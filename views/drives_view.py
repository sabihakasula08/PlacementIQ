"""
Placement Drives Management and Smart Eligibility View
Supports recruitment drive publishing, multi-criteria filtering,
automated profile vs requirement eligibility evaluation, and single-click application.
"""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Optional, List
from utils.theme import Theme
from utils.constants import DEPARTMENTS, ACADEMIC_YEARS
from utils.components import ModernCard, NeonButton, PillBadge, ScrollableFrame, SegmentedToggle
from models.user_model import User
from models.student_model import Student
from models.drive_model import PlacementDrive
from controllers.admin_controller import AdminController
from controllers.student_controller import StudentController

class DrivesView(tk.Frame):
    def __init__(
        self,
        parent,
        current_user: User,
        admin_controller: AdminController,
        student_controller: StudentController,
        nav_callback: Callable[[str], None]
    ):
        super().__init__(parent, bg=Theme.BG_DARK)
        self.current_user = current_user
        self.admin_controller = admin_controller
        self.student_controller = student_controller
        self.nav_callback = nav_callback

        self.student = self.student_controller.get_student_by_user_id(current_user.id) if current_user.is_student else None
        self.filter_mode = "All Drives"
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

        tk.Label(title_box, text="Campus Placement Drives", font=Theme.FONT_TITLE_LARGE, fg=Theme.TEXT_WHITE, bg=Theme.BG_DARK).pack(anchor="w")
        tk.Label(title_box, text="Active recruitment opportunities, smart eligibility criteria, and candidate applications", font=Theme.FONT_SMALL, fg=Theme.TEXT_MUTED, bg=Theme.BG_DARK).pack(anchor="w")

        # Admin Action: Publish New Drive Button
        if self.current_user.is_admin:
            NeonButton(
                head_f, text="+ Publish Placement Drive",
                command=self._open_add_drive_dialog,
                style="primary", width=190, height=36
            ).pack(side="right")

        # Filter & Toggle Bar Card
        bar_card = ModernCard(container, padding=12)
        bar_card.pack(fill="x", padx=20, pady=(0, 16))

        # Search box
        tk.Label(bar_card.inner, text="🔍 Search Drives:", font=Theme.FONT_SMALL_BOLD, fg=Theme.TEXT_LIGHT, bg=Theme.CARD_BG).pack(side="left", padx=(0, 8))
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *args: self._filter_and_render())

        search_entry = tk.Entry(
            bar_card.inner, textvariable=self.search_var, font=Theme.FONT_SMALL,
            bg=Theme.INPUT_BG, fg=Theme.TEXT_LIGHT, insertbackground=Theme.ACCENT_PINK,
            bd=1, relief="solid", highlightthickness=1, highlightcolor=Theme.ACCENT_PINK,
            highlightbackground=Theme.INPUT_BORDER, width=28
        )
        search_entry.pack(side="left", fill="x", expand=True, ipady=4, padx=(0, 14))

        # If student: Toggle [All Drives] [Eligible Only] [Applied Only]
        if self.current_user.is_student:
            SegmentedToggle(
                bar_card.inner,
                options=["All Drives", "Eligible Only", "My Applied"],
                default_index=0,
                on_change=self._on_filter_toggle,
                height=32,
                pill_width=95
            ).pack(side="right")

        # Drives List Container
        self.drives_container = tk.Frame(container, bg=Theme.BG_DARK)
        self.drives_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        self._load_drives()

    def _on_filter_toggle(self, opt: str):
        self.filter_mode = opt
        self._filter_and_render()

    def _load_drives(self):
        self.all_drives = self.admin_controller.get_all_drives()
        self._filter_and_render()

    def _filter_and_render(self):
        for c in self.drives_container.winfo_children():
            c.destroy()

        query = self.search_var.get().strip().lower()

        # If student, compute eligibility for each drive
        if self.student:
            drives_with_elig = self.student_controller.get_drives_with_eligibility(self.student)
            # Filter by search
            filtered = [
                item for item in drives_with_elig
                if query in item[0].title.lower() or query in item[0].company_name.lower() or query in item[0].job_role.lower()
            ]

            # Filter by toggle mode
            if self.filter_mode == "Eligible Only":
                filtered = [item for item in filtered if item[1].is_eligible]
            elif self.filter_mode == "My Applied":
                filtered = [item for item in filtered if item[2]]

            if not filtered:
                tk.Label(
                    self.drives_container,
                    text="No placement drives found matching criteria.",
                    font=Theme.FONT_BODY, fg=Theme.TEXT_MUTED, bg=Theme.BG_DARK
                ).pack(pady=40)
                return

            for drive, el, has_applied in filtered:
                self._render_student_drive_card(self.drives_container, drive, el, has_applied)

        else: # Admin view
            filtered = [
                d for d in self.all_drives
                if query in d.title.lower() or query in d.company_name.lower() or query in d.job_role.lower()
            ]
            if not filtered:
                tk.Label(
                    self.drives_container,
                    text="No placement drives created yet.",
                    font=Theme.FONT_BODY, fg=Theme.TEXT_MUTED, bg=Theme.BG_DARK
                ).pack(pady=40)
                return

            for drive in filtered:
                self._render_admin_drive_card(self.drives_container, drive)

    def _render_student_drive_card(self, parent, drive: PlacementDrive, el, has_applied: bool):
        card = ModernCard(parent, padding=18)
        card.pack(fill="x", pady=8)
        f = card.inner

        # Top line: Company + Package badge + Eligibility Pill + Apply Button
        top_r = tk.Frame(f, bg=Theme.CARD_BG)
        top_r.pack(fill="x")

        title_box = tk.Frame(top_r, bg=Theme.CARD_BG)
        title_box.pack(side="left", fill="both", expand=True)

        h_row = tk.Frame(title_box, bg=Theme.CARD_BG)
        h_row.pack(anchor="w")

        tk.Label(h_row, text=f"{drive.company_name} — {drive.title}", font=Theme.FONT_TITLE_MED, fg=Theme.TEXT_WHITE, bg=Theme.CARD_BG).pack(side="left")

        # Package Pill
        PillBadge(h_row, text=f"INR {drive.package_lpa:.1f} LPA", status="Good Fit", width=110, height=24).pack(side="left", padx=8)

        tk.Label(title_box, text=f"Role: {drive.job_role} • Min CGPA: {drive.min_cgpa:.1f} • Deadline: {drive.application_deadline}", font=Theme.FONT_SMALL, fg=Theme.ACCENT_LAVENDER, bg=Theme.CARD_BG).pack(anchor="w", pady=(2, 0))

        # Right side: Eligibility Status + Apply Action
        action_box = tk.Frame(top_r, bg=Theme.CARD_BG)
        action_box.pack(side="right")

        if has_applied:
            PillBadge(action_box, text="Applied ✓", status="Applied", width=95, height=28).pack(side="right")
        elif el.is_eligible:
            PillBadge(action_box, text="Eligible", status="Good Fit", width=80, height=28).pack(side="left", padx=6)
            NeonButton(
                action_box, text="Apply Now  →",
                command=lambda: self._apply_drive(drive.id),
                style="primary", width=115, height=32
            ).pack(side="right")
        else:
            PillBadge(action_box, text="Ineligible", status="Ineligible", width=85, height=28).pack(side="right")

        # Smart Eligibility Checker Breakdown (Transparency Box)
        eval_box = tk.Frame(f, bg=Theme.CARD_BG_ALT, bd=1, relief="solid")
        eval_box.pack(fill="x", pady=(12, 4), ipady=6, ipadx=8)

        eval_head = tk.Frame(eval_box, bg=Theme.CARD_BG_ALT)
        eval_head.pack(fill="x")

        tk.Label(eval_head, text="Automated Eligibility Evaluation:", font=Theme.FONT_TINY, fg=Theme.TEXT_MUTED, bg=Theme.CARD_BG_ALT).pack(side="left")
        match_color = Theme.COLOR_SUCCESS if el.skills_match_pct >= 70 else Theme.ACCENT_ORANGE
        tk.Label(eval_head, text=f"Skill Match: {el.skills_match_pct:.0f}%", font=Theme.FONT_SMALL_BOLD, fg=match_color, bg=Theme.CARD_BG_ALT).pack(side="right")

        # Satisfied Criteria (Green ticks)
        for sat in el.satisfied_criteria:
            tk.Label(eval_box, text=f"  ✓ {sat}", font=Theme.FONT_TINY, fg=Theme.BADGE_TEXT_GREEN, bg=Theme.CARD_BG_ALT).pack(anchor="w")

        # Missing Criteria (Red warnings)
        for mis in el.missing_criteria:
            tk.Label(eval_box, text=f"  ✗ {mis}", font=Theme.FONT_TINY, fg=Theme.COLOR_DANGER, bg=Theme.CARD_BG_ALT).pack(anchor="w")

        # Skills and Batch summary
        meta_box = tk.Frame(f, bg=Theme.CARD_BG)
        meta_box.pack(fill="x", pady=(6, 0))
        tk.Label(meta_box, text=f"Required Skills: {drive.skills_str}", font=Theme.FONT_TINY, fg=Theme.TEXT_MUTED, bg=Theme.CARD_BG).pack(anchor="w")
        tk.Label(meta_box, text=f"Eligible Departments: {drive.depts_str}", font=Theme.FONT_TINY, fg=Theme.TEXT_SUBTLE, bg=Theme.CARD_BG).pack(anchor="w")

    def _render_admin_drive_card(self, parent, drive: PlacementDrive):
        card = ModernCard(parent, padding=18)
        card.pack(fill="x", pady=8)
        f = card.inner

        top_r = tk.Frame(f, bg=Theme.CARD_BG)
        top_r.pack(fill="x")

        title_box = tk.Frame(top_r, bg=Theme.CARD_BG)
        title_box.pack(side="left", fill="both", expand=True)

        h_row = tk.Frame(title_box, bg=Theme.CARD_BG)
        h_row.pack(anchor="w")
        tk.Label(h_row, text=f"{drive.company_name} — {drive.title}", font=Theme.FONT_TITLE_MED, fg=Theme.TEXT_WHITE, bg=Theme.CARD_BG).pack(side="left")
        PillBadge(h_row, text=f"INR {drive.package_lpa:.1f} LPA", status="Good Fit", width=110, height=24).pack(side="left", padx=8)

        tk.Label(title_box, text=f"Role: {drive.job_role} • Min CGPA: {drive.min_cgpa:.1f} • Deadline: {drive.application_deadline}", font=Theme.FONT_SMALL, fg=Theme.ACCENT_LAVENDER, bg=Theme.CARD_BG).pack(anchor="w", pady=(2, 0))

        # Right side: Applicants count + Actions
        right_box = tk.Frame(top_r, bg=Theme.CARD_BG)
        right_box.pack(side="right")

        PillBadge(right_box, text=f"{drive.applicant_count} Applicants", status="Shortlisted", width=110, height=24).pack(side="left", padx=6)

        NeonButton(
            right_box, text="Edit",
            command=lambda: self._open_edit_drive_dialog(drive),
            style="secondary", width=65, height=28, font=Theme.FONT_SMALL
        ).pack(side="left", padx=3)

        NeonButton(
            right_box, text="Delete",
            command=lambda: self._delete_drive(drive),
            style="danger", width=65, height=28, font=Theme.FONT_SMALL
        ).pack(side="left", padx=3)

        # Meta info
        meta_box = tk.Frame(f, bg=Theme.CARD_BG)
        meta_box.pack(fill="x", pady=(10, 0))
        tk.Label(meta_box, text=f"Required Skills: {drive.skills_str}", font=Theme.FONT_TINY, fg=Theme.TEXT_LIGHT, bg=Theme.CARD_BG).pack(anchor="w")
        tk.Label(meta_box, text=f"Eligible Departments: {drive.depts_str}", font=Theme.FONT_TINY, fg=Theme.TEXT_MUTED, bg=Theme.CARD_BG).pack(anchor="w")
        tk.Label(meta_box, text=f"Eligible Batches: {drive.years_str} • Test Venue: {drive.venue_or_link}", font=Theme.FONT_TINY, fg=Theme.TEXT_SUBTLE, bg=Theme.CARD_BG).pack(anchor="w")

    def _apply_drive(self, drive_id: int):
        if not self.student:
            return
        if messagebox.askyesno("Confirm Application", "Are you sure you want to apply for this campus placement drive?"):
            ok, msg = self.student_controller.apply_for_drive(self.student.id, drive_id)
            if ok:
                messagebox.showinfo("Application Submitted", msg)
                self._filter_and_render()
            else:
                messagebox.showerror("Error", msg)

    def _open_add_drive_dialog(self):
        self._show_drive_dialog(title="Publish Placement Drive", drive=None)

    def _open_edit_drive_dialog(self, drive: PlacementDrive):
        self._show_drive_dialog(title=f"Edit Drive: {drive.title}", drive=drive)

    def _show_drive_dialog(self, title: str, drive: Optional[PlacementDrive]):
        dlg = tk.Toplevel(self)
        dlg.title(title)
        dlg.geometry("580x560")
        dlg.configure(bg=Theme.BG_DARK)
        dlg.transient(self)
        dlg.grab_set()

        card = ModernCard(dlg, padding=20)
        card.pack(fill="both", expand=True, padx=16, pady=16)
        f = card.inner

        tk.Label(f, text=title, font=Theme.FONT_TITLE_MED, fg=Theme.TEXT_WHITE, bg=Theme.CARD_BG).pack(anchor="w", pady=(0, 10))

        # Company Selector
        companies = self.admin_controller.get_all_companies()
        if not companies:
            messagebox.showerror("No Companies", "Please add at least one recruiting company first.")
            dlg.destroy()
            return

        comp_map = {c.name: c.id for c in companies}
        tk.Label(f, text="RECRUITING COMPANY", font=Theme.FONT_TINY, fg=Theme.TEXT_MUTED, bg=Theme.CARD_BG).pack(anchor="w")
        comp_var = tk.StringVar(value=drive.company_name if drive and drive.company_name in comp_map else list(comp_map.keys())[0])
        comp_cb = ttk.Combobox(f, textvariable=comp_var, values=list(comp_map.keys()), state="readonly")
        comp_cb.pack(fill="x", ipady=4, pady=(2, 6))

        def add_field(label, val=""):
            tk.Label(f, text=label, font=Theme.FONT_TINY, fg=Theme.TEXT_MUTED, bg=Theme.CARD_BG).pack(anchor="w", pady=(2, 1))
            e = tk.Entry(
                f, font=Theme.FONT_SMALL, bg=Theme.INPUT_BG, fg=Theme.TEXT_LIGHT,
                insertbackground=Theme.ACCENT_PINK, bd=1, relief="solid", highlightthickness=1,
                highlightcolor=Theme.ACCENT_PINK, highlightbackground=Theme.INPUT_BORDER
            )
            e.pack(fill="x", ipady=4, pady=(0, 6))
            if val:
                e.insert(0, val)
            return e

        ent_title = add_field("DRIVE TITLE (e.g. Software Engineer 2026)", drive.title if drive else "")
        ent_role = add_field("JOB ROLE / DESIGNATION", drive.job_role if drive else "")

        # Row for Package, Min CGPA, Deadline
        row_num = tk.Frame(f, bg=Theme.CARD_BG)
        row_num.pack(fill="x", pady=2)
        row_num.columnconfigure(0, weight=1)
        row_num.columnconfigure(1, weight=1)
        row_num.columnconfigure(2, weight=1)

        c0 = tk.Frame(row_num, bg=Theme.CARD_BG)
        c0.grid(row=0, column=0, sticky="ew", padx=(0, 4))
        tk.Label(c0, text="PACKAGE (LPA)", font=Theme.FONT_TINY, fg=Theme.TEXT_MUTED, bg=Theme.CARD_BG).pack(anchor="w")
        ent_pkg = tk.Entry(c0, font=Theme.FONT_SMALL, bg=Theme.INPUT_BG, fg=Theme.TEXT_LIGHT, insertbackground=Theme.ACCENT_PINK)
        ent_pkg.pack(fill="x", ipady=4)
        ent_pkg.insert(0, f"{drive.package_lpa:.1f}" if drive else "12.0")

        c1 = tk.Frame(row_num, bg=Theme.CARD_BG)
        c1.grid(row=0, column=1, sticky="ew", padx=4)
        tk.Label(c1, text="MIN CGPA CUTOFF", font=Theme.FONT_TINY, fg=Theme.TEXT_MUTED, bg=Theme.CARD_BG).pack(anchor="w")
        ent_cgpa = tk.Entry(c1, font=Theme.FONT_SMALL, bg=Theme.INPUT_BG, fg=Theme.TEXT_LIGHT, insertbackground=Theme.ACCENT_PINK)
        ent_cgpa.pack(fill="x", ipady=4)
        ent_cgpa.insert(0, f"{drive.min_cgpa:.1f}" if drive else "7.5")

        c2 = tk.Frame(row_num, bg=Theme.CARD_BG)
        c2.grid(row=0, column=2, sticky="ew", padx=(4, 0))
        tk.Label(c2, text="DEADLINE (YYYY-MM-DD)", font=Theme.FONT_TINY, fg=Theme.TEXT_MUTED, bg=Theme.CARD_BG).pack(anchor="w")
        ent_dead = tk.Entry(c2, font=Theme.FONT_SMALL, bg=Theme.INPUT_BG, fg=Theme.TEXT_LIGHT, insertbackground=Theme.ACCENT_PINK)
        ent_dead.pack(fill="x", ipady=4)
        ent_dead.insert(0, drive.application_deadline if drive else "2026-12-30")

        ent_skills = add_field("REQUIRED TECHNICAL SKILLS (comma-separated)", drive.skills_str if drive else "Python, SQL, Data Structures")
        ent_depts = add_field("ELIGIBLE DEPARTMENTS (comma-separated or 'All Departments')", drive.depts_str if drive else "Computer Science & Engineering, Information Technology")
        ent_years = add_field("ELIGIBLE BATCH YEARS (comma-separated)", drive.years_str if drive else "2021 - 2025 (Final Year / Passing Out)")

        def save():
            cid = comp_map[comp_var.get()]
            t = ent_title.get().strip()
            r = ent_role.get().strip()
            dl = ent_dead.get().strip()
            skills = [s.strip() for s in ent_skills.get().split(",") if s.strip()]
            depts = [d.strip() for d in ent_depts.get().split(",") if d.strip()]
            years = [y.strip() for y in ent_years.get().split(",") if y.strip()]

            try:
                pkg = float(ent_pkg.get().strip())
                mcgpa = float(ent_cgpa.get().strip())
            except ValueError:
                messagebox.showerror("Validation Error", "Package and CGPA must be numeric.")
                return

            if not drive:
                ok, msg, _ = self.admin_controller.add_drive(
                    company_id=cid, title=t, job_role=r, package_lpa=pkg,
                    min_cgpa=mcgpa, eligible_departments=depts, eligible_years=years,
                    required_skills=skills, application_deadline=dl
                )
            else:
                ok, msg = self.admin_controller.update_drive(
                    drive_id=drive.id, company_id=cid, title=t, job_role=r, package_lpa=pkg,
                    min_cgpa=mcgpa, eligible_departments=depts, eligible_years=years,
                    required_skills=skills, application_deadline=dl
                )

            if ok:
                messagebox.showinfo("Success", msg)
                dlg.destroy()
                self._load_drives()
            else:
                messagebox.showerror("Error", msg)

        NeonButton(
            f, text="Save Placement Drive  ✓",
            command=save,
            style="primary", width=240, height=36
        ).pack(pady=(12, 0))

    def _delete_drive(self, drive: PlacementDrive):
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete drive '{drive.title}'?"):
            ok, msg = self.admin_controller.delete_drive(drive.id)
            if ok:
                messagebox.showinfo("Deleted", msg)
                self._load_drives()
            else:
                messagebox.showerror("Error", msg)
