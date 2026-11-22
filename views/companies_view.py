"""
Companies Directory View for PlacementIQ
Enables company discovery, industry categorization, and full CRUD operations for administrators.
"""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Optional, List
from utils.theme import Theme
from utils.components import ModernCard, NeonButton, PillBadge, ScrollableFrame
from models.user_model import User
from models.company_model import Company
from controllers.admin_controller import AdminController

class CompaniesView(tk.Frame):
    def __init__(
        self,
        parent,
        current_user: User,
        admin_controller: AdminController,
        nav_callback: Callable[[str], None]
    ):
        super().__init__(parent, bg=Theme.BG_DARK)
        self.current_user = current_user
        self.admin_controller = admin_controller
        self.nav_callback = nav_callback

        self._build_ui()

    def _build_ui(self):
        self.scroll = ScrollableFrame(self, bg=Theme.BG_DARK)
        self.scroll.pack(fill="both", expand=True)
        container = self.scroll.scrollable_content

        # Header Row
        head_f = tk.Frame(container, bg=Theme.BG_DARK)
        head_f.pack(fill="x", padx=20, pady=(18, 12))

        title_box = tk.Frame(head_f, bg=Theme.BG_DARK)
        title_box.pack(side="left")

        tk.Label(title_box, text="Recruiting Partner Companies", font=Theme.FONT_TITLE_LARGE, fg=Theme.TEXT_WHITE, bg=Theme.BG_DARK).pack(anchor="w")
        tk.Label(title_box, text="Verified campus recruiting companies, industry domains, and drive history", font=Theme.FONT_SMALL, fg=Theme.TEXT_MUTED, bg=Theme.BG_DARK).pack(anchor="w")

        # Admin Action: Add Company Button
        if self.current_user.is_admin:
            NeonButton(
                head_f, text="+ Add Company",
                command=self._open_add_dialog,
                style="primary", width=140, height=36
            ).pack(side="right")

        # Search Bar Filter Row
        filter_card = ModernCard(container, padding=12)
        filter_card.pack(fill="x", padx=20, pady=(0, 16))

        tk.Label(filter_card.inner, text="🔍 Search Companies:", font=Theme.FONT_SMALL_BOLD, fg=Theme.TEXT_LIGHT, bg=Theme.CARD_BG).pack(side="left", padx=(0, 10))
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *args: self._filter_companies())

        search_entry = tk.Entry(
            filter_card.inner, textvariable=self.search_var, font=Theme.FONT_SMALL,
            bg=Theme.INPUT_BG, fg=Theme.TEXT_LIGHT, insertbackground=Theme.ACCENT_PINK,
            bd=1, relief="solid", highlightthickness=1, highlightcolor=Theme.ACCENT_PINK,
            highlightbackground=Theme.INPUT_BORDER, width=40
        )
        search_entry.pack(side="left", fill="x", expand=True, ipady=4)

        # Company List Grid Container
        self.list_container = tk.Frame(container, bg=Theme.BG_DARK)
        self.list_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        self._load_companies()

    def _load_companies(self):
        self.all_companies = self.admin_controller.get_all_companies()
        self._filter_companies()

    def _filter_companies(self):
        query = self.search_var.get().strip().lower()
        for c in self.list_container.winfo_children():
            c.destroy()

        filtered = [
            c for c in self.all_companies
            if query in c.name.lower() or query in c.industry.lower() or query in c.location.lower()
        ]

        if not filtered:
            tk.Label(
                self.list_container,
                text="No companies matching your search query.",
                font=Theme.FONT_BODY, fg=Theme.TEXT_MUTED, bg=Theme.BG_DARK
            ).pack(pady=40)
            return

        for comp in filtered:
            self._render_company_card(self.list_container, comp)

    def _render_company_card(self, parent, comp: Company):
        card = ModernCard(parent, padding=16)
        card.pack(fill="x", pady=6)
        f = card.inner

        # Top row: Logo Circle + Name & Industry + Badges + Action Buttons
        top_r = tk.Frame(f, bg=Theme.CARD_BG)
        top_r.pack(fill="x")

        # Avatar circle
        av = tk.Canvas(top_r, width=44, height=44, bg=Theme.CARD_BG, highlightthickness=0)
        av.pack(side="left", padx=(0, 12))
        av.create_oval(2, 2, 42, 42, fill=Theme.CARD_BG_ALT, outline=Theme.ACCENT_PINK, width=1.5)
        initials = "".join([w[0] for w in comp.name.split()[:2]]).upper()
        av.create_text(22, 22, text=initials, font=Theme.FONT_BODY_BOLD, fill=Theme.TEXT_WHITE)

        name_box = tk.Frame(top_r, bg=Theme.CARD_BG)
        name_box.pack(side="left", fill="both", expand=True)

        tk.Label(name_box, text=comp.name, font=Theme.FONT_TITLE_MED, fg=Theme.TEXT_WHITE, bg=Theme.CARD_BG).pack(anchor="w")
        tk.Label(name_box, text=f"{comp.industry} • {comp.location or 'Multiple Locations'}", font=Theme.FONT_SMALL, fg=Theme.ACCENT_LAVENDER, bg=Theme.CARD_BG).pack(anchor="w")

        # Right side: Drives badge and Admin actions
        right_box = tk.Frame(top_r, bg=Theme.CARD_BG)
        right_box.pack(side="right")

        PillBadge(right_box, text=f"{comp.active_drives_count} Active Drives", status="Active" if comp.active_drives_count > 0 else "Assessment", width=120, height=24).pack(side="left", padx=8)

        if self.current_user.is_admin:
            NeonButton(
                right_box, text="Edit",
                command=lambda: self._open_edit_dialog(comp),
                style="secondary", width=70, height=28, font=Theme.FONT_SMALL
            ).pack(side="left", padx=4)

            NeonButton(
                right_box, text="Delete",
                command=lambda: self._delete_company(comp),
                style="danger", width=70, height=28, font=Theme.FONT_SMALL
            ).pack(side="left", padx=4)

        # Description
        if comp.description:
            tk.Label(
                f, text=comp.description,
                font=Theme.FONT_SMALL, fg=Theme.TEXT_LIGHT, bg=Theme.CARD_BG,
                wraplength=700, justify="left"
            ).pack(anchor="w", pady=(8, 4))

        # Bottom info row: Website & Email
        bot_r = tk.Frame(f, bg=Theme.CARD_BG)
        bot_r.pack(fill="x", pady=(4, 0))
        tk.Label(bot_r, text=f"🌐 Website: {comp.website or 'N/A'}", font=Theme.FONT_TINY, fg=Theme.TEXT_MUTED, bg=Theme.CARD_BG).pack(side="left", padx=(0, 16))
        tk.Label(bot_r, text=f"✉ Contact: {comp.contact_email or 'careers@campus.edu'}", font=Theme.FONT_TINY, fg=Theme.TEXT_MUTED, bg=Theme.CARD_BG).pack(side="left")

    def _open_add_dialog(self):
        self._show_company_dialog(title="Register New Company", comp=None)

    def _open_edit_dialog(self, comp: Company):
        self._show_company_dialog(title=f"Edit {comp.name}", comp=comp)

    def _show_company_dialog(self, title: str, comp: Optional[Company]):
        dlg = tk.Toplevel(self)
        dlg.title(title)
        dlg.geometry("520x480")
        dlg.configure(bg=Theme.BG_DARK)
        dlg.transient(self)
        dlg.grab_set()

        card = ModernCard(dlg, padding=20)
        card.pack(fill="both", expand=True, padx=16, pady=16)
        f = card.inner

        tk.Label(f, text=title, font=Theme.FONT_TITLE_MED, fg=Theme.TEXT_WHITE, bg=Theme.CARD_BG).pack(anchor="w", pady=(0, 12))

        def add_field(label, val=""):
            tk.Label(f, text=label, font=Theme.FONT_TINY, fg=Theme.TEXT_MUTED, bg=Theme.CARD_BG).pack(anchor="w", pady=(4, 1))
            e = tk.Entry(
                f, font=Theme.FONT_SMALL, bg=Theme.INPUT_BG, fg=Theme.TEXT_LIGHT,
                insertbackground=Theme.ACCENT_PINK, bd=1, relief="solid", highlightthickness=1,
                highlightcolor=Theme.ACCENT_PINK, highlightbackground=Theme.INPUT_BORDER
            )
            e.pack(fill="x", ipady=4, pady=(0, 6))
            if val:
                e.insert(0, val)
            return e

        ent_name = add_field("COMPANY NAME", comp.name if comp else "")
        ent_ind = add_field("INDUSTRY DOMAIN (e.g. Cloud Computing, FinTech)", comp.industry if comp else "")
        ent_loc = add_field("HEADQUARTERS / LOCATIONS", comp.location if comp else "")
        ent_web = add_field("WEBSITE URL", comp.website if comp else "")
        ent_email = add_field("RECRUITER CONTACT EMAIL", comp.contact_email if comp else "")
        ent_desc = add_field("BRIEF COMPANY OVERVIEW", comp.description if comp else "")

        def save():
            name = ent_name.get().strip()
            ind = ent_ind.get().strip()
            loc = ent_loc.get().strip()
            web = ent_web.get().strip()
            email = ent_email.get().strip()
            desc = ent_desc.get().strip()

            if not comp:
                ok, msg, _ = self.admin_controller.add_company(name, ind, web, email, loc, desc)
            else:
                ok, msg = self.admin_controller.update_company(comp.id, name, ind, web, email, loc, desc)

            if ok:
                messagebox.showinfo("Success", msg)
                dlg.destroy()
                self._load_companies()
            else:
                messagebox.showerror("Error", msg)

        NeonButton(
            f, text="Save Company  ✓",
            command=save,
            style="primary", width=220, height=36
        ).pack(pady=(12, 0))

    def _delete_company(self, comp: Company):
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{comp.name}' and all associated drives?"):
            ok, msg = self.admin_controller.delete_company(comp.id)
            if ok:
                messagebox.showinfo("Deleted", msg)
                self._load_companies()
            else:
                messagebox.showerror("Error", msg)
