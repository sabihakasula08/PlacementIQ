"""
Student Profile View for PlacementIQ
Allows students to view and update their academic credentials, technical skills,
soft skills, practical projects, certifications, and resume path.
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Callable, Optional
from utils.theme import Theme
from utils.constants import DEPARTMENTS, ACADEMIC_YEARS, COMMON_SKILLS, COMMON_SOFT_SKILLS
from utils.components import ModernCard, NeonButton, PillBadge, ScrollableFrame
from models.user_model import User
from models.student_model import Student
from controllers.student_controller import StudentController

class StudentProfileView(tk.Frame):
    def __init__(
        self,
        parent,
        current_user: User,
        student_controller: StudentController,
        nav_callback: Callable[[str], None]
    ):
        super().__init__(parent, bg=Theme.BG_DARK)
        self.current_user = current_user
        self.student_controller = student_controller
        self.nav_callback = nav_callback

        self.student = self.student_controller.get_student_by_user_id(current_user.id)
        self._build_ui()

    def _build_ui(self):
        self.scroll = ScrollableFrame(self, bg=Theme.BG_DARK)
        self.scroll.pack(fill="both", expand=True)
        container = self.scroll.scrollable_content

        # Header Title Row
        head_f = tk.Frame(container, bg=Theme.BG_DARK)
        head_f.pack(fill="x", padx=20, pady=(18, 12))

        tk.Label(
            head_f,
            text="Student Profile & Placement Portfolio",
            font=Theme.FONT_TITLE_LARGE,
            fg=Theme.TEXT_WHITE,
            bg=Theme.BG_DARK
        ).pack(anchor="w")
        tk.Label(
            head_f,
            text="Keep your academic credentials and verified skill stack updated for eligibility matching",
            font=Theme.FONT_SMALL,
            fg=Theme.TEXT_MUTED,
            bg=Theme.BG_DARK
        ).pack(anchor="w")

        if not self.student:
            tk.Label(container, text="No student profile linked to this user account.", fg=Theme.COLOR_DANGER, bg=Theme.BG_DARK).pack(pady=40)
            return

        s = self.student

        # Main Layout Grid: Left Details Form + Right Quick Skills Selector
        main_grid = tk.Frame(container, bg=Theme.BG_DARK)
        main_grid.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        main_grid.columnconfigure(0, weight=6) # 60% Form
        main_grid.columnconfigure(1, weight=4) # 40% Quick Skills palette

        # Left Card: Profile Information Form
        card = ModernCard(main_grid, padding=20)
        card.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        f = card.inner

        # Register No. (Read-only badge)
        reg_box = tk.Frame(f, bg=Theme.CARD_BG)
        reg_box.pack(fill="x", pady=(0, 10))
        tk.Label(reg_box, text=f"REGISTER NUMBER: {s.register_no}", font=Theme.FONT_BODY_BOLD, fg=Theme.ACCENT_PINK, bg=Theme.CARD_BG).pack(side="left")
        PillBadge(reg_box, text="Verified Student", status="Good Fit", width=110, height=22).pack(side="right")

        # Full Name & Email
        row1 = tk.Frame(f, bg=Theme.CARD_BG)
        row1.pack(fill="x", pady=4)
        row1.columnconfigure(0, weight=1)
        row1.columnconfigure(1, weight=1)

        c0 = tk.Frame(row1, bg=Theme.CARD_BG)
        c0.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        tk.Label(c0, text="FULL NAME", font=Theme.FONT_TINY, fg=Theme.TEXT_MUTED, bg=Theme.CARD_BG).pack(anchor="w")
        self.ent_name = self._make_entry(c0, s.full_name)

        c1 = tk.Frame(row1, bg=Theme.CARD_BG)
        c1.grid(row=0, column=1, sticky="ew", padx=(6, 0))
        tk.Label(c1, text="CAMPUS EMAIL", font=Theme.FONT_TINY, fg=Theme.TEXT_MUTED, bg=Theme.CARD_BG).pack(anchor="w")
        self.ent_email = self._make_entry(c1, s.email)

        # Department & Batch Year
        row2 = tk.Frame(f, bg=Theme.CARD_BG)
        row2.pack(fill="x", pady=4)
        row2.columnconfigure(0, weight=1)
        row2.columnconfigure(1, weight=1)

        d0 = tk.Frame(row2, bg=Theme.CARD_BG)
        d0.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        tk.Label(d0, text="ACADEMIC DEPARTMENT", font=Theme.FONT_TINY, fg=Theme.TEXT_MUTED, bg=Theme.CARD_BG).pack(anchor="w")
        self.dept_var = tk.StringVar(value=s.department)
        self.dept_cb = ttk.Combobox(d0, textvariable=self.dept_var, values=DEPARTMENTS, state="readonly")
        self.dept_cb.pack(fill="x", ipady=4, pady=(2, 6))

        d1 = tk.Frame(row2, bg=Theme.CARD_BG)
        d1.grid(row=0, column=1, sticky="ew", padx=(6, 0))
        tk.Label(d1, text="GRADUATION BATCH", font=Theme.FONT_TINY, fg=Theme.TEXT_MUTED, bg=Theme.CARD_BG).pack(anchor="w")
        self.year_var = tk.StringVar(value=s.academic_year)
        self.year_cb = ttk.Combobox(d1, textvariable=self.year_var, values=ACADEMIC_YEARS, state="readonly")
        self.year_cb.pack(fill="x", ipady=4, pady=(2, 6))

        # CGPA, Aptitude Score, Communication Score
        row3 = tk.Frame(f, bg=Theme.CARD_BG)
        row3.pack(fill="x", pady=4)
        row3.columnconfigure(0, weight=1)
        row3.columnconfigure(1, weight=1)
        row3.columnconfigure(2, weight=1)

        e0 = tk.Frame(row3, bg=Theme.CARD_BG)
        e0.grid(row=0, column=0, sticky="ew", padx=(0, 4))
        tk.Label(e0, text="CGPA (0 - 10.0)", font=Theme.FONT_TINY, fg=Theme.TEXT_MUTED, bg=Theme.CARD_BG).pack(anchor="w")
        self.ent_cgpa = self._make_entry(e0, f"{s.cgpa:.2f}")

        e1 = tk.Frame(row3, bg=Theme.CARD_BG)
        e1.grid(row=0, column=1, sticky="ew", padx=4)
        tk.Label(e1, text="APTITUDE SCORE (0-100)", font=Theme.FONT_TINY, fg=Theme.TEXT_MUTED, bg=Theme.CARD_BG).pack(anchor="w")
        self.ent_apt = self._make_entry(e1, f"{s.aptitude_score:.0f}")

        e2 = tk.Frame(row3, bg=Theme.CARD_BG)
        e2.grid(row=0, column=2, sticky="ew", padx=(4, 0))
        tk.Label(e2, text="COMMUNICATION (0-100)", font=Theme.FONT_TINY, fg=Theme.TEXT_MUTED, bg=Theme.CARD_BG).pack(anchor="w")
        self.ent_comm = self._make_entry(e2, f"{s.communication_score:.0f}")

        # Projects & Certifications
        row4 = tk.Frame(f, bg=Theme.CARD_BG)
        row4.pack(fill="x", pady=4)
        row4.columnconfigure(0, weight=1)
        row4.columnconfigure(1, weight=1)

        p0 = tk.Frame(row4, bg=Theme.CARD_BG)
        p0.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        tk.Label(p0, text="COMPLETED PROJECTS COUNT", font=Theme.FONT_TINY, fg=Theme.TEXT_MUTED, bg=Theme.CARD_BG).pack(anchor="w")
        self.ent_proj_cnt = self._make_entry(p0, str(s.projects_count))

        p1 = tk.Frame(row4, bg=Theme.CARD_BG)
        p1.grid(row=0, column=1, sticky="ew", padx=(6, 0))
        tk.Label(p1, text="CERTIFICATIONS COUNT", font=Theme.FONT_TINY, fg=Theme.TEXT_MUTED, bg=Theme.CARD_BG).pack(anchor="w")
        self.ent_cert_cnt = self._make_entry(p1, str(s.certifications_count))

        # Technical Skills (Comma separated text entry)
        tk.Label(f, text="TECHNICAL SKILLS (comma-separated)", font=Theme.FONT_TINY, fg=Theme.TEXT_MUTED, bg=Theme.CARD_BG).pack(anchor="w", pady=(6, 1))
        self.ent_tech = self._make_entry(f, s.tech_skills_str)

        # Soft Skills
        tk.Label(f, text="SOFT SKILLS (comma-separated)", font=Theme.FONT_TINY, fg=Theme.TEXT_MUTED, bg=Theme.CARD_BG).pack(anchor="w", pady=(6, 1))
        self.ent_soft = self._make_entry(f, s.soft_skills_str)

        # Project Description / GitHub summary
        tk.Label(f, text="PORTFOLIO & PROJECT HIGHLIGHTS", font=Theme.FONT_TINY, fg=Theme.TEXT_MUTED, bg=Theme.CARD_BG).pack(anchor="w", pady=(6, 1))
        self.ent_desc = self._make_entry(f, s.projects_description or "Capstone & GitHub repositories")

        # Resume Path with Browse button
        tk.Label(f, text="RESUME FILE PATH", font=Theme.FONT_TINY, fg=Theme.TEXT_MUTED, bg=Theme.CARD_BG).pack(anchor="w", pady=(6, 1))
        res_row = tk.Frame(f, bg=Theme.CARD_BG)
        res_row.pack(fill="x", pady=(0, 14))

        self.ent_resume = tk.Entry(
            res_row, font=Theme.FONT_SMALL, bg=Theme.INPUT_BG, fg=Theme.TEXT_LIGHT,
            insertbackground=Theme.ACCENT_PINK, bd=1, relief="solid", highlightthickness=1,
            highlightcolor=Theme.ACCENT_PINK, highlightbackground=Theme.INPUT_BORDER
        )
        self.ent_resume.pack(side="left", fill="x", expand=True, ipady=4)
        self.ent_resume.insert(0, s.resume_path or f"C:/resumes/{s.register_no}_Resume.pdf")

        NeonButton(
            res_row, text="Browse...",
            command=self._browse_resume,
            style="secondary", width=90, height=30, font=Theme.FONT_SMALL
        ).pack(side="right", padx=(8, 0))

        # Save Button
        NeonButton(
            f, text="Save Profile Changes  ✓",
            command=self._handle_save,
            style="primary", width=260, height=38
        ).pack(pady=(10, 0))

        # Right Card: Quick Common Skills Checklist (Click to add to skills!)
        right_card = ModernCard(main_grid, padding=16)
        right_card.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        rf = right_card.inner

        tk.Label(rf, text="Quick Skills Add Palette", font=Theme.FONT_TITLE_MED, fg=Theme.TEXT_WHITE, bg=Theme.CARD_BG).pack(anchor="w")
        tk.Label(rf, text="Click any chip below to instantly add it to your technical skills list:", font=Theme.FONT_TINY, fg=Theme.TEXT_MUTED, bg=Theme.CARD_BG, wraplength=250, justify="left").pack(anchor="w", pady=(0, 10))

        # Grid of skill badges that can be clicked
        chips_frame = tk.Frame(rf, bg=Theme.CARD_BG)
        chips_frame.pack(fill="both", expand=True)

        for skill_name in COMMON_SKILLS:
            btn = tk.Button(
                chips_frame, text=f"+ {skill_name}",
                font=Theme.FONT_TINY,
                bg=Theme.CARD_BG_ALT, fg=Theme.ACCENT_LAVENDER,
                activebackground=Theme.ACCENT_PINK, activeforeground=Theme.TEXT_WHITE,
                bd=1, relief="flat", padx=6, pady=3,
                command=lambda sn=skill_name: self._quick_add_skill(sn)
            )
            btn.pack(side="top", anchor="w", pady=2, fill="x")

    def _make_entry(self, parent, val: str) -> tk.Entry:
        ent = tk.Entry(
            parent, font=Theme.FONT_SMALL, bg=Theme.INPUT_BG, fg=Theme.TEXT_LIGHT,
            insertbackground=Theme.ACCENT_PINK, bd=1, relief="solid", highlightthickness=1,
            highlightcolor=Theme.ACCENT_PINK, highlightbackground=Theme.INPUT_BORDER
        )
        ent.pack(fill="x", ipady=4, pady=(2, 6))
        ent.insert(0, val)
        return ent

    def _browse_resume(self):
        f = filedialog.askopenfilename(
            title="Select Student Resume",
            filetypes=[("PDF Documents", "*.pdf"), ("Word Documents", "*.docx"), ("All Files", "*.*")]
        )
        if f:
            self.ent_resume.delete(0, tk.END)
            self.ent_resume.insert(0, f)

    def _quick_add_skill(self, skill_name: str):
        current_skills = [s.strip() for s in self.ent_tech.get().split(",") if s.strip()]
        if skill_name not in current_skills:
            current_skills.append(skill_name)
            self.ent_tech.delete(0, tk.END)
            self.ent_tech.insert(0, ", ".join(current_skills))

    def _handle_save(self):
        try:
            cgpa = float(self.ent_cgpa.get().strip())
            apt = float(self.ent_apt.get().strip())
            comm = float(self.ent_comm.get().strip())
            proj = int(self.ent_proj_cnt.get().strip())
            cert = int(self.ent_cert_cnt.get().strip())
        except ValueError:
            messagebox.showerror("Validation Error", "Please ensure CGPA, aptitude, and counts are valid numbers.")
            return

        tech_list = [s.strip() for s in self.ent_tech.get().split(",") if s.strip()]
        soft_list = [s.strip() for s in self.ent_soft.get().split(",") if s.strip()]

        ok, msg = self.student_controller.update_profile(
            student=self.student,
            full_name=self.ent_name.get().strip(),
            email=self.ent_email.get().strip(),
            department=self.dept_var.get(),
            academic_year=self.year_var.get(),
            cgpa=cgpa,
            technical_skills=tech_list,
            soft_skills=soft_list,
            projects_count=proj,
            certifications_count=cert,
            projects_description=self.ent_desc.get().strip(),
            aptitude_score=apt,
            communication_score=comm,
            resume_path=self.ent_resume.get().strip()
        )

        if ok:
            messagebox.showinfo("Profile Updated", "Your student profile has been updated and your readiness score recalculated!")
            self.nav_callback("readiness")
        else:
            messagebox.showerror("Error", msg)
