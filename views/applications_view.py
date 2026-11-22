"""
Applications Tracking & Pipeline View for PlacementIQ
Provides transparent stage tracking across recruitment workflows:
Applied -> Shortlisted -> Assessment -> Interview -> Selected / Rejected.
"""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Optional, List
from utils.theme import Theme
from utils.constants import APPLICATION_STATUSES, STATUS_SELECTED, STATUS_REJECTED
from utils.components import ModernCard, NeonButton, PillBadge, ScrollableFrame, SegmentedToggle
from models.user_model import User
from models.application_model import Application
from controllers.student_controller import StudentController
from controllers.admin_controller import AdminController

class ApplicationsView(tk.Frame):
    def __init__(
        self,
        parent,
        current_user: User,
        student_controller: StudentController,
        admin_controller: AdminController,
        nav_callback: Callable[[str], None]
    ):
        super().__init__(parent, bg=Theme.BG_DARK)
        self.current_user = current_user
        self.student_controller = student_controller
        self.admin_controller = admin_controller
        self.nav_callback = nav_callback

        self.student = self.student_controller.get_student_by_user_id(current_user.id) if current_user.is_student else None
        self.status_filter = "All"
        self._build_ui()

    def _build_ui(self):
        self.scroll = ScrollableFrame(self, bg=Theme.BG_DARK)
        self.scroll.pack(fill="both", expand=True)
        container = self.scroll.scrollable_content

        # Header Title Row
        head_f = tk.Frame(container, bg=Theme.BG_DARK)
        head_f.pack(fill="x", padx=20, pady=(18, 12))

        title_box = tk.Frame(head_f, bg=Theme.BG_DARK)
        title_box.pack(side="left")

        tk.Label(title_box, text="Application Tracking & Recruitment Pipeline", font=Theme.FONT_TITLE_LARGE, fg=Theme.TEXT_WHITE, bg=Theme.BG_DARK).pack(anchor="w")
        subtitle_txt = "Track your live recruitment progress, interview rounds, and selection offers" if self.current_user.is_student else "Manage candidate screening rounds, interview schedules, and offer letters"
        tk.Label(title_box, text=subtitle_txt, font=Theme.FONT_SMALL, fg=Theme.TEXT_MUTED, bg=Theme.BG_DARK).pack(anchor="w")

        # Filter & Search Bar
        bar_card = ModernCard(container, padding=12)
        bar_card.pack(fill="x", padx=20, pady=(0, 16))

        tk.Label(bar_card.inner, text="🔍 Search Applications:", font=Theme.FONT_SMALL_BOLD, fg=Theme.TEXT_LIGHT, bg=Theme.CARD_BG).pack(side="left", padx=(0, 8))
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *args: self._filter_and_render())

        search_entry = tk.Entry(
            bar_card.inner, textvariable=self.search_var, font=Theme.FONT_SMALL,
            bg=Theme.INPUT_BG, fg=Theme.TEXT_LIGHT, insertbackground=Theme.ACCENT_PINK,
            bd=1, relief="solid", highlightthickness=1, highlightcolor=Theme.ACCENT_PINK,
            highlightbackground=Theme.INPUT_BORDER, width=28
        )
        search_entry.pack(side="left", fill="x", expand=True, ipady=4, padx=(0, 14))

        # Status Stage filter dropdown
        tk.Label(bar_card.inner, text="Stage Filter:", font=Theme.FONT_SMALL_BOLD, fg=Theme.TEXT_MUTED, bg=Theme.CARD_BG).pack(side="left", padx=(0, 6))
        self.stage_filter_var = tk.StringVar(value="All Stages")
        filter_opts = ["All Stages"] + APPLICATION_STATUSES
        stage_cb = ttk.Combobox(bar_card.inner, textvariable=self.stage_filter_var, values=filter_opts, state="readonly", width=14)
        stage_cb.pack(side="left")
        stage_cb.bind("<<ComboboxSelected>>", lambda e: self._filter_and_render())

        # Applications List Container
        self.apps_container = tk.Frame(container, bg=Theme.BG_DARK)
        self.apps_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        self._load_applications()

    def _load_applications(self):
        if self.current_user.is_student and self.student:
            self.all_apps = self.student_controller.get_student_applications(self.student.id)
        else:
            self.all_apps = self.admin_controller.get_all_applications()
        self._filter_and_render()

    def _filter_and_render(self):
        for c in self.apps_container.winfo_children():
            c.destroy()

        query = self.search_var.get().strip().lower()
        selected_stage = self.stage_filter_var.get()

        filtered = []
        for app in self.all_apps:
            # Query match on student name, register no, company, title
            match_query = (
                query in app.company_name.lower() or
                query in app.drive_title.lower() or
                query in app.student_name.lower() or
                query in app.register_no.lower()
            )
            # Stage match
            match_stage = (selected_stage == "All Stages" or app.status == selected_stage)

            if match_query and match_stage:
                filtered.append(app)

        if not filtered:
            tk.Label(
                self.apps_container,
                text="No applications found matching the selected filters.",
                font=Theme.FONT_BODY, fg=Theme.TEXT_MUTED, bg=Theme.BG_DARK
            ).pack(pady=40)
            return

        for app in filtered:
            if self.current_user.is_student:
                self._render_student_app_card(self.apps_container, app)
            else:
                self._render_admin_app_card(self.apps_container, app)

    def _render_student_app_card(self, parent, app: Application):
        card = ModernCard(parent, padding=16)
        card.pack(fill="x", pady=6)
        f = card.inner

        top_r = tk.Frame(f, bg=Theme.CARD_BG)
        top_r.pack(fill="x")

        title_box = tk.Frame(top_r, bg=Theme.CARD_BG)
        title_box.pack(side="left")

        h_row = tk.Frame(title_box, bg=Theme.CARD_BG)
        h_row.pack(anchor="w")
        tk.Label(h_row, text=f"{app.company_name} — {app.drive_title}", font=Theme.FONT_TITLE_MED, fg=Theme.TEXT_WHITE, bg=Theme.CARD_BG).pack(side="left")
        PillBadge(h_row, text=f"INR {app.package_lpa:.1f} LPA", status="Good Fit", width=110, height=22).pack(side="left", padx=8)

        tk.Label(title_box, text=f"Role: {app.job_role} • Applied On: {app.applied_date[:10]}", font=Theme.FONT_SMALL, fg=Theme.TEXT_MUTED, bg=Theme.CARD_BG).pack(anchor="w", pady=(2, 0))

        # Right Status Badge
        badge_status = "Good Fit" if app.status == STATUS_SELECTED else "Assessment" if app.status in ("Assessment", "Interview") else app.status
        PillBadge(top_r, text=app.status, status=badge_status, width=110, height=26).pack(side="right")

        # Pipeline Visual Stepper
        self._render_pipeline_stepper(f, app.status)

        # Recruiter Feedback note
        if app.feedback:
            feed_box = tk.Frame(f, bg=Theme.CARD_BG_ALT, bd=1, relief="solid")
            feed_box.pack(fill="x", pady=(8, 0), ipady=4, ipadx=8)
            tk.Label(feed_box, text=f"💬 Recruiter Remarks: {app.feedback}", font=Theme.FONT_TINY, fg=Theme.TEXT_LIGHT, bg=Theme.CARD_BG_ALT).pack(anchor="w")

    def _render_admin_app_card(self, parent, app: Application):
        card = ModernCard(parent, padding=16)
        card.pack(fill="x", pady=6)
        f = card.inner

        top_r = tk.Frame(f, bg=Theme.CARD_BG)
        top_r.pack(fill="x")

        # Student info + Company info
        info_col = tk.Frame(top_r, bg=Theme.CARD_BG)
        info_col.pack(side="left", fill="both", expand=True)

        h_row = tk.Frame(info_col, bg=Theme.CARD_BG)
        h_row.pack(anchor="w")
        tk.Label(h_row, text=f"{app.student_name} ({app.register_no})", font=Theme.FONT_TITLE_MED, fg=Theme.TEXT_WHITE, bg=Theme.CARD_BG).pack(side="left")
        tk.Label(h_row, text=f"CGPA: {app.student_cgpa:.2f} • {app.student_dept}", font=Theme.FONT_SMALL_BOLD, fg=Theme.ACCENT_PINK, bg=Theme.CARD_BG).pack(side="left", padx=10)

        tk.Label(info_col, text=f"Applied For: {app.company_name} — {app.drive_title} ({app.package_lpa:.1f} LPA) • {app.applied_date[:10]}", font=Theme.FONT_SMALL, fg=Theme.TEXT_LIGHT, bg=Theme.CARD_BG).pack(anchor="w", pady=(2, 0))

        # Status Update Controls on Right
        action_col = tk.Frame(top_r, bg=Theme.CARD_BG)
        action_col.pack(side="right")

        status_var = tk.StringVar(value=app.status)
        status_cb = ttk.Combobox(action_col, textvariable=status_var, values=APPLICATION_STATUSES, state="readonly", width=12)
        status_cb.pack(side="left", padx=6)

        NeonButton(
            action_col, text="Update Stage",
            command=lambda: self._update_stage(app, status_var.get()),
            style="primary", width=110, height=30, font=Theme.FONT_SMALL
        ).pack(side="left")

        # Visual Stepper
        self._render_pipeline_stepper(f, app.status)

        # Feedback row with quick edit
        feed_r = tk.Frame(f, bg=Theme.CARD_BG)
        feed_r.pack(fill="x", pady=(6, 0))
        tk.Label(feed_r, text=f"Remarks: {app.feedback or 'No remarks entered'}", font=Theme.FONT_TINY, fg=Theme.TEXT_MUTED, bg=Theme.CARD_BG).pack(side="left")

    def _render_pipeline_stepper(self, parent, current_status: str):
        steps = ["Applied", "Shortlisted", "Assessment", "Interview", "Selected"]
        stepper = tk.Frame(parent, bg=Theme.CARD_BG)
        stepper.pack(fill="x", pady=(8, 4))

        is_rejected = (current_status == STATUS_REJECTED)
        try:
            curr_idx = steps.index(current_status) if not is_rejected else -1
        except ValueError:
            curr_idx = 0

        for i, step in enumerate(steps):
            col = tk.Frame(stepper, bg=Theme.CARD_BG)
            col.pack(side="left", fill="x", expand=True)

            if is_rejected:
                color = Theme.COLOR_DANGER
                icon = "✗" if i == 0 else "•"
            elif i < curr_idx:
                color = Theme.COLOR_SUCCESS
                icon = "✓"
            elif i == curr_idx:
                color = Theme.ACCENT_PINK
                icon = "●"
            else:
                color = Theme.CARD_BORDER
                icon = "○"

            lbl_step = tk.Label(col, text=f"{icon} {step}", font=Theme.FONT_TINY, fg=color, bg=Theme.CARD_BG)
            lbl_step.pack(anchor="center")

            # Mini progress bar
            pb = tk.Canvas(col, height=3, bg=Theme.CARD_BG, highlightthickness=0)
            pb.pack(fill="x", pady=(2, 0))
            bar_color = color if (i <= curr_idx and not is_rejected) else Theme.CARD_BORDER
            pb.create_rectangle(0, 0, 500, 3, fill=bar_color, outline="")

    def _update_stage(self, app: Application, new_status: str):
        # Prompt for optional remarks
        dlg = tk.Toplevel(self)
        dlg.title("Update Application Stage")
        dlg.geometry("420x220")
        dlg.configure(bg=Theme.BG_DARK)
        dlg.transient(self)
        dlg.grab_set()

        card = ModernCard(dlg, padding=16)
        card.pack(fill="both", expand=True, padx=12, pady=12)
        f = card.inner

        tk.Label(f, text=f"Update Stage: {app.student_name}", font=Theme.FONT_TITLE_MED, fg=Theme.TEXT_WHITE, bg=Theme.CARD_BG).pack(anchor="w")
        tk.Label(f, text=f"New Stage: {new_status}", font=Theme.FONT_BODY_BOLD, fg=Theme.ACCENT_PINK, bg=Theme.CARD_BG).pack(anchor="w", pady=(2, 8))

        tk.Label(f, text="REMARKS / FEEDBACK NOTE", font=Theme.FONT_TINY, fg=Theme.TEXT_MUTED, bg=Theme.CARD_BG).pack(anchor="w")
        ent_fb = tk.Entry(
            f, font=Theme.FONT_SMALL, bg=Theme.INPUT_BG, fg=Theme.TEXT_LIGHT,
            insertbackground=Theme.ACCENT_PINK, bd=1, relief="solid", highlightthickness=1,
            highlightcolor=Theme.ACCENT_PINK, highlightbackground=Theme.INPUT_BORDER
        )
        ent_fb.pack(fill="x", ipady=4, pady=(2, 12))
        ent_fb.insert(0, app.feedback or f"Updated status to {new_status}")

        def confirm():
            fb = ent_fb.get().strip()
            ok, msg = self.admin_controller.update_application_status(app.id, new_status, fb)
            if ok:
                messagebox.showinfo("Success", msg)
                dlg.destroy()
                self._load_applications()
            else:
                messagebox.showerror("Error", msg)

        NeonButton(f, text="Confirm & Save Stage  ✓", command=confirm, style="primary", width=220, height=34).pack()
