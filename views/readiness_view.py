"""
Smart Placement Readiness and Skill Gap Analysis View
The flagship analytical module of PlacementIQ.
Features transparent rule-based scoring, category progress rings,
real-time missing skill gap identification across campus drives,
and explainable career recommendations.
"""
import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional, List, Dict, Any
from utils.theme import Theme
from utils.components import (
    ModernCard, NeonButton, PillBadge, ConcentricGauge,
    ScrollableFrame
)
from models.user_model import User
from models.student_model import Student
from controllers.student_controller import StudentController
from controllers.admin_controller import AdminController

class ReadinessView(tk.Frame):
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

        # Determine target student
        if self.current_user.is_student:
            self.selected_student = self.student_controller.get_student_by_user_id(current_user.id)
        else:
            all_s = self.admin_controller.get_all_students()
            self.selected_student = all_s[0] if all_s else None

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

        tk.Label(
            title_box,
            text="Smart Placement Readiness & Skill Gap Analysis",
            font=Theme.FONT_TITLE_LARGE,
            fg=Theme.TEXT_WHITE,
            bg=Theme.BG_DARK
        ).pack(anchor="w")
        tk.Label(
            title_box,
            text="Explainable, rule-based readiness calculation and market demand gap detection",
            font=Theme.FONT_SMALL,
            fg=Theme.TEXT_MUTED,
            bg=Theme.BG_DARK
        ).pack(anchor="w")

        # If Admin, show student selector dropdown
        if self.current_user.is_admin:
            sel_box = tk.Frame(head_f, bg=Theme.BG_DARK)
            sel_box.pack(side="right")
            tk.Label(sel_box, text="Evaluate Student:", font=Theme.FONT_SMALL_BOLD, fg=Theme.TEXT_LIGHT, bg=Theme.BG_DARK).pack(side="left", padx=6)
            all_students = self.admin_controller.get_all_students()
            self.student_map = {f"{s.register_no} - {s.full_name}": s for s in all_students}
            self.sel_var = tk.StringVar(value=list(self.student_map.keys())[0] if self.student_map else "")
            cb = ttk.Combobox(sel_box, textvariable=self.sel_var, values=list(self.student_map.keys()), state="readonly", width=28)
            cb.pack(side="left")
            cb.bind("<<ComboboxSelected>>", self._on_student_change)

        if not self.selected_student:
            tk.Label(container, text="No student records available.", font=Theme.FONT_TITLE_MED, fg=Theme.TEXT_MUTED, bg=Theme.BG_DARK).pack(pady=40)
            return

        self.analysis_container = tk.Frame(container, bg=Theme.BG_DARK)
        self.analysis_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        self._render_analysis()

    def _on_student_change(self, event):
        val = self.sel_var.get()
        if val in self.student_map:
            self.selected_student = self.student_map[val]
            self._render_analysis()

    def _render_analysis(self):
        for child in self.analysis_container.winfo_children():
            child.destroy()

        s = self.selected_student
        res = self.student_controller.get_readiness_analysis(s)

        # 1. Top Readiness Summary Card (Score + Concentric Gauge + Progress Bars)
        top_card = ModernCard(self.analysis_container, padding=18)
        top_card.pack(fill="x", pady=(0, 16))

        top_grid = tk.Frame(top_card.inner, bg=Theme.CARD_BG)
        top_grid.pack(fill="x")
        top_grid.columnconfigure(0, weight=3) # Score & Level
        top_grid.columnconfigure(1, weight=4) # Concentric Gauge
        top_grid.columnconfigure(2, weight=5) # 5 Category Progress Bars

        # Col 0: Overall Score Badge
        score_col = tk.Frame(top_grid, bg=Theme.CARD_BG)
        score_col.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        tk.Label(score_col, text="OVERALL READINESS", font=Theme.FONT_TINY, fg=Theme.TEXT_MUTED, bg=Theme.CARD_BG).pack(anchor="w")
        tk.Label(score_col, text=f"{res.overall_score:.0f}", font=("Segoe UI", 36, "bold"), fg=Theme.ACCENT_PINK, bg=Theme.CARD_BG).pack(anchor="w")
        tk.Label(score_col, text="out of 100 points", font=Theme.FONT_SMALL, fg=Theme.TEXT_SUBTLE, bg=Theme.CARD_BG).pack(anchor="w", pady=(0, 8))

        badge_status = "Good Fit" if res.overall_score >= 80 else "Assessment" if res.overall_score >= 60 else "Ineligible"
        PillBadge(score_col, text=res.readiness_level, status=badge_status, width=150, height=26).pack(anchor="w", pady=(0, 10))

        tk.Label(score_col, text=f"Student: {s.full_name}", font=Theme.FONT_BODY_BOLD, fg=Theme.TEXT_WHITE, bg=Theme.CARD_BG).pack(anchor="w")
        tk.Label(score_col, text=f"Reg No: {s.register_no} • CGPA: {s.cgpa:.2f}", font=Theme.FONT_SMALL, fg=Theme.TEXT_LIGHT, bg=Theme.CARD_BG).pack(anchor="w")
        tk.Label(score_col, text=f"{s.department}", font=Theme.FONT_TINY, fg=Theme.TEXT_MUTED, bg=Theme.CARD_BG).pack(anchor="w")

        # Col 1: Concentric Circular Arcs
        gauge_col = tk.Frame(top_grid, bg=Theme.CARD_BG)
        gauge_col.grid(row=0, column=1, sticky="nsew", padx=10)

        cat_scores = {
            "Academics": res.academic_score,
            "Technical Skills": res.technical_score,
            "Aptitude": res.aptitude_score,
            "Communication": res.communication_score,
            "Projects": res.project_score
        }
        ConcentricGauge(
            gauge_col,
            category_scores=cat_scores,
            overall_score=res.overall_score,
            height=160
        ).pack(fill="both", expand=True)

        # Col 2: Category Breakdown Bars
        bars_col = tk.Frame(top_grid, bg=Theme.CARD_BG)
        bars_col.grid(row=0, column=2, sticky="nsew", padx=(10, 0))

        tk.Label(bars_col, text="EVALUATION PILLARS (100 TOTAL)", font=Theme.FONT_TINY, fg=Theme.TEXT_MUTED, bg=Theme.CARD_BG).pack(anchor="w", pady=(0, 4))

        categories = [
            ("Academics (CGPA)", res.academic_score, 25.0, Theme.ACCENT_ORANGE),
            ("Technical Skills", res.technical_score, 25.0, Theme.ACCENT_PINK),
            ("Aptitude & Reasoning", res.aptitude_score, 20.0, Theme.ACCENT_PURPLE),
            ("Soft Skills & Comm.", res.communication_score, 15.0, Theme.COLOR_SUCCESS),
            ("Projects & Practical", res.project_score, 15.0, Theme.ACCENT_CYAN),
        ]

        for cat_name, sc, max_sc, col in categories:
            self._render_category_bar(bars_col, cat_name, sc, max_sc, col)

        # 2. Middle Row: Missing Skill Gap Matrix (Left) + Explainable Recommendations (Right)
        mid_row = tk.Frame(self.analysis_container, bg=Theme.BG_DARK)
        mid_row.pack(fill="x", pady=(0, 16))
        mid_row.columnconfigure(0, weight=6)
        mid_row.columnconfigure(1, weight=5)

        # Left Card: Live Skill Gap Matrix
        gap_card = ModernCard(mid_row, padding=16)
        gap_card.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        tk.Label(gap_card.inner, text="Campus Drive Skill Gap Analysis", font=Theme.FONT_TITLE_MED, fg=Theme.TEXT_WHITE, bg=Theme.CARD_BG).pack(anchor="w")
        tk.Label(gap_card.inner, text="Missing technical skills demanded by active campus recruiters", font=Theme.FONT_TINY, fg=Theme.TEXT_MUTED, bg=Theme.CARD_BG).pack(anchor="w", pady=(0, 12))

        if not res.missing_skills:
            tk.Label(gap_card.inner, text="🎉 Outstanding! You possess all required technical skills for active drives.", font=Theme.FONT_BODY, fg=Theme.COLOR_SUCCESS, bg=Theme.CARD_BG).pack(pady=20)
        else:
            for item in res.missing_skills[:5]:
                skill_row = tk.Frame(gap_card.inner, bg=Theme.CARD_BG_ALT, bd=1, relief="solid")
                skill_row.pack(fill="x", pady=3, ipady=4, ipadx=6)

                left_info = tk.Frame(skill_row, bg=Theme.CARD_BG_ALT)
                left_info.pack(side="left")

                tk.Label(left_info, text=f"• {item['skill']}", font=Theme.FONT_BODY_BOLD, fg=Theme.ACCENT_PINK, bg=Theme.CARD_BG_ALT).pack(anchor="w")
                comps = ", ".join(item["required_by"][:3])
                tk.Label(left_info, text=f"Demanded by: {comps}", font=Theme.FONT_TINY, fg=Theme.TEXT_MUTED, bg=Theme.CARD_BG_ALT).pack(anchor="w")

                PillBadge(skill_row, text=f"{item['demand_count']} Drives Demand", status="Assessment", width=120, height=22).pack(side="right")

        # Right Card: Actionable Recommendations
        rec_card = ModernCard(mid_row, padding=16)
        rec_card.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

        tk.Label(rec_card.inner, text="Targeted Recommendations", font=Theme.FONT_TITLE_MED, fg=Theme.TEXT_WHITE, bg=Theme.CARD_BG).pack(anchor="w")
        tk.Label(rec_card.inner, text="Rule-based actions to maximize placement probability", font=Theme.FONT_TINY, fg=Theme.TEXT_MUTED, bg=Theme.CARD_BG).pack(anchor="w", pady=(0, 10))

        for rec in res.recommendations[:4]:
            rec_box = tk.Frame(rec_card.inner, bg=Theme.CARD_BG_ALT, bd=1, relief="solid")
            rec_box.pack(fill="x", pady=4, ipady=6, ipadx=8)

            top_r = tk.Frame(rec_box, bg=Theme.CARD_BG_ALT)
            top_r.pack(fill="x")

            prio_color = Theme.COLOR_DANGER if rec["priority"] == "High" else Theme.ACCENT_ORANGE
            tk.Label(top_r, text=f"[{rec['priority']} Priority] {rec['category']}", font=Theme.FONT_TINY, fg=prio_color, bg=Theme.CARD_BG_ALT).pack(side="left")

            tk.Label(rec_box, text=rec["title"], font=Theme.FONT_SMALL_BOLD, fg=Theme.TEXT_WHITE, bg=Theme.CARD_BG_ALT).pack(anchor="w", pady=(2, 1))
            tk.Label(rec_box, text=rec["impact"], font=Theme.FONT_TINY, fg=Theme.TEXT_MUTED, bg=Theme.CARD_BG_ALT, wraplength=340, justify="left").pack(anchor="w")

        # 3. Bottom Card: Current Profile Inventory
        inv_card = ModernCard(self.analysis_container, padding=16)
        inv_card.pack(fill="x")

        tk.Label(inv_card.inner, text="Verified Profile Inventory & Portfolio Strengths", font=Theme.FONT_TITLE_MED, fg=Theme.TEXT_WHITE, bg=Theme.CARD_BG).pack(anchor="w")

        tags_f = tk.Frame(inv_card.inner, bg=Theme.CARD_BG)
        tags_f.pack(fill="x", pady=(10, 0))

        tk.Label(tags_f, text="Technical Skills:", font=Theme.FONT_SMALL_BOLD, fg=Theme.TEXT_MUTED, bg=Theme.CARD_BG).pack(anchor="w")
        t_box = tk.Frame(tags_f, bg=Theme.CARD_BG)
        t_box.pack(fill="x", pady=(3, 8))
        for t in s.technical_skills:
            PillBadge(t_box, text=t, status="Active", width=max(60, len(t)*8 + 16), height=22).pack(side="left", padx=3, pady=2)

        tk.Label(tags_f, text="Soft Skills:", font=Theme.FONT_SMALL_BOLD, fg=Theme.TEXT_MUTED, bg=Theme.CARD_BG).pack(anchor="w")
        s_box = tk.Frame(tags_f, bg=Theme.CARD_BG)
        s_box.pack(fill="x", pady=(3, 0))
        for sf in s.soft_skills:
            PillBadge(s_box, text=sf, status="Interview", width=max(70, len(sf)*8 + 16), height=22).pack(side="left", padx=3, pady=2)

    def _render_category_bar(self, parent, label: str, score: float, max_score: float, color: str):
        row = tk.Frame(parent, bg=Theme.CARD_BG)
        row.pack(fill="x", pady=2)

        head = tk.Frame(row, bg=Theme.CARD_BG)
        head.pack(fill="x")
        tk.Label(head, text=label, font=Theme.FONT_TINY, fg=Theme.TEXT_LIGHT, bg=Theme.CARD_BG).pack(side="left")
        tk.Label(head, text=f"{score:.1f}/{max_score:.0f}", font=Theme.FONT_TINY, fg=color, bg=Theme.CARD_BG).pack(side="right")

        pct = min(1.0, max(0.0, score / max_score))
        c = tk.Canvas(row, height=6, bg=Theme.CARD_BG, highlightthickness=0)
        c.pack(fill="x", pady=(2, 2))

        def draw_bar(event):
            w = event.width
            c.delete("all")
            # Track
            c.create_rectangle(0, 0, w, 6, fill=Theme.CARD_BORDER, outline="")
            # Active
            fill_w = int(w * pct)
            if fill_w > 0:
                c.create_rectangle(0, 0, fill_w, 6, fill=color, outline="")

        c.bind("<Configure>", draw_bar)
