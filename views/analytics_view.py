"""
Placement Analytics Dashboard View for PlacementIQ
Provides real-time recruitment metrics, interactive department-wise placement charts,
recruitment funnel conversion, company selections, and readiness distribution.
"""
import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional, List, Dict, Any
from utils.theme import Theme
from utils.components import (
    ModernCard, NeonButton, PillBadge, InteractiveLineChart,
    ConcentricGauge, MiniSparkline, ScrollableFrame
)
from models.user_model import User
from controllers.analytics_controller import AnalyticsController

class AnalyticsView(tk.Frame):
    def __init__(
        self,
        parent,
        current_user: User,
        analytics_controller: AnalyticsController,
        nav_callback: Callable[[str], None]
    ):
        super().__init__(parent, bg=Theme.BG_DARK)
        self.current_user = current_user
        self.analytics_controller = analytics_controller
        self.nav_callback = nav_callback

        self._build_ui()

    def _build_ui(self):
        self.scroll = ScrollableFrame(self, bg=Theme.BG_DARK)
        self.scroll.pack(fill="both", expand=True)
        container = self.scroll.scrollable_content

        # Header Title Row
        head_f = tk.Frame(container, bg=Theme.BG_DARK)
        head_f.pack(fill="x", padx=20, pady=(18, 12))

        tk.Label(head_f, text="Campus Placement Analytics & Executive Insights", font=Theme.FONT_TITLE_LARGE, fg=Theme.TEXT_WHITE, bg=Theme.BG_DARK).pack(anchor="w")
        tk.Label(head_f, text="Real-time SQLite database metrics, department placements, package statistics, and readiness distributions", font=Theme.FONT_SMALL, fg=Theme.TEXT_MUTED, bg=Theme.BG_DARK).pack(anchor="w")

        # Fetch Data
        kpi = self.analytics_controller.get_kpi_summary()
        dept_stats = self.analytics_controller.get_department_stats()
        funnel = self.analytics_controller.get_application_funnel()
        company_sels = self.analytics_controller.get_company_selections()
        readiness_dist = self.analytics_controller.get_readiness_distribution()

        # 1. KPI Cards Row (4 Cards)
        kpi_row = tk.Frame(container, bg=Theme.BG_DARK)
        kpi_row.pack(fill="x", padx=20, pady=(0, 16))
        for i in range(4):
            kpi_row.columnconfigure(i, weight=1)

        # KPI 1: Placed Students & Placement Rate
        c1 = ModernCard(kpi_row, padding=14)
        c1.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        self._build_kpi(c1.inner, "Placed Students", f"{kpi['placed_students']}", f"{kpi['placement_pct']}% Placement", "Good Fit", Theme.COLOR_SUCCESS, [1, 1, 2, 2, kpi['placed_students']])

        # KPI 2: Total Applications
        c2 = ModernCard(kpi_row, padding=14)
        c2.grid(row=0, column=1, sticky="nsew", padx=6)
        self._build_kpi(c2.inner, "Total Applications", f"{kpi['total_applications']}", "Active Pipeline", "Assessment", Theme.ACCENT_PURPLE, [4, 6, 8, 12, kpi['total_applications']])

        # KPI 3: Highest Package
        c3 = ModernCard(kpi_row, padding=14)
        c3.grid(row=0, column=2, sticky="nsew", padx=6)
        self._build_kpi(c3.inner, "Highest Package", f"{kpi['highest_lpa']} LPA", "Super Dream Offer", "Active", Theme.ACCENT_PINK, [12, 14, 18, 21, int(kpi['highest_lpa'])])

        # KPI 4: Average Package
        c4 = ModernCard(kpi_row, padding=14)
        c4.grid(row=0, column=3, sticky="nsew", padx=(6, 0))
        self._build_kpi(c4.inner, "Average Package", f"{kpi['avg_lpa']} LPA", "Campus Average", "Interview", Theme.ACCENT_ORANGE, [5, 6, 7, int(kpi['avg_lpa'])])

        # 2. Middle Row: Department-wise Placement Horizontal Bar Chart (Left) + Recruitment Funnel (Right)
        mid_row = tk.Frame(container, bg=Theme.BG_DARK)
        mid_row.pack(fill="x", padx=20, pady=(0, 16))
        mid_row.columnconfigure(0, weight=6)
        mid_row.columnconfigure(1, weight=4)

        # Left Card: Department-wise Placement Statistics
        dept_card = ModernCard(mid_row, padding=18)
        dept_card.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        tk.Label(dept_card.inner, text="Department-Wise Placement Statistics", font=Theme.FONT_TITLE_MED, fg=Theme.TEXT_WHITE, bg=Theme.CARD_BG).pack(anchor="w")
        tk.Label(dept_card.inner, text="Total registered students vs candidates placed by department", font=Theme.FONT_TINY, fg=Theme.TEXT_MUTED, bg=Theme.CARD_BG).pack(anchor="w", pady=(0, 12))

        for item in dept_stats:
            self._render_dept_bar(dept_card.inner, item["department"], item["placed"], item["total"], item["percentage"])

        # Right Card: Recruitment Funnel Breakdown
        funnel_card = ModernCard(mid_row, padding=18)
        funnel_card.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

        tk.Label(funnel_card.inner, text="Recruitment Conversion Funnel", font=Theme.FONT_TITLE_MED, fg=Theme.TEXT_WHITE, bg=Theme.CARD_BG).pack(anchor="w")
        tk.Label(funnel_card.inner, text="Candidate drop-off and conversion by stage", font=Theme.FONT_TINY, fg=Theme.TEXT_MUTED, bg=Theme.CARD_BG).pack(anchor="w", pady=(0, 12))

        tot_apps = max(1, kpi["total_applications"])
        for stage, count in funnel.items():
            pct = (count / tot_apps) * 100.0
            color = Theme.COLOR_SUCCESS if stage == "Selected" else Theme.COLOR_DANGER if stage == "Rejected" else Theme.ACCENT_PINK if stage == "Interview" else Theme.ACCENT_PURPLE
            self._render_funnel_bar(funnel_card.inner, stage, count, pct, color)

        # 3. Bottom Row: Company Selections Table (Left) + Cohort Readiness Distribution (Right)
        bot_row = tk.Frame(container, bg=Theme.BG_DARK)
        bot_row.pack(fill="x", padx=20, pady=(0, 20))
        bot_row.columnconfigure(0, weight=6)
        bot_row.columnconfigure(1, weight=4)

        # Left Card: Company Selections
        comp_card = ModernCard(bot_row, padding=18)
        comp_card.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        tk.Label(comp_card.inner, text="Recruiter Selections & Offers Made", font=Theme.FONT_TITLE_MED, fg=Theme.TEXT_WHITE, bg=Theme.CARD_BG).pack(anchor="w")
        tk.Label(comp_card.inner, text="Candidate offers extended per corporate recruiting partner", font=Theme.FONT_TINY, fg=Theme.TEXT_MUTED, bg=Theme.CARD_BG).pack(anchor="w", pady=(0, 10))

        for cs in company_sels[:5]:
            row = tk.Frame(comp_card.inner, bg=Theme.CARD_BG_ALT, bd=1, relief="solid")
            row.pack(fill="x", pady=3, ipady=4, ipadx=8)

            tk.Label(row, text=cs["company"], font=Theme.FONT_SMALL_BOLD, fg=Theme.TEXT_WHITE, bg=Theme.CARD_BG_ALT).pack(side="left")
            PillBadge(row, text=f"{cs['selected']} Selected", status="Selected" if cs["selected"] > 0 else "Assessment", width=100, height=22).pack(side="right")
            tk.Label(row, text=f"{cs['applicants']} Applicants", font=Theme.FONT_TINY, fg=Theme.TEXT_MUTED, bg=Theme.CARD_BG_ALT).pack(side="right", padx=10)

        # Right Card: Cohort Readiness Breakdown
        read_card = ModernCard(bot_row, padding=18)
        read_card.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

        tk.Label(read_card.inner, text="Cohort Readiness Distribution", font=Theme.FONT_TITLE_MED, fg=Theme.TEXT_WHITE, bg=Theme.CARD_BG).pack(anchor="w")
        tk.Label(read_card.inner, text="Student count across 4 readiness tiers", font=Theme.FONT_TINY, fg=Theme.TEXT_MUTED, bg=Theme.CARD_BG).pack(anchor="w", pady=(0, 10))

        for tier, count in readiness_dist.items():
            t_row = tk.Frame(read_card.inner, bg=Theme.CARD_BG_ALT, bd=1, relief="solid")
            t_row.pack(fill="x", pady=3, ipady=4, ipadx=8)

            tk.Label(t_row, text=tier, font=Theme.FONT_SMALL_BOLD, fg=Theme.TEXT_WHITE, bg=Theme.CARD_BG_ALT).pack(side="left")
            PillBadge(t_row, text=f"{count} Students", status="Good Fit" if "Elite" in tier or "Job" in tier else "Assessment", width=100, height=22).pack(side="right")

    def _build_kpi(self, parent, label: str, value: str, badge_text: str, badge_status: str, sparkline_color: str, spark_data: list):
        tk.Label(parent, text=label, font=Theme.FONT_TINY, fg=Theme.TEXT_MUTED, bg=Theme.CARD_BG).pack(anchor="w")
        tk.Label(parent, text=value, font=Theme.FONT_NUMBER_HERO, fg=Theme.TEXT_WHITE, bg=Theme.CARD_BG).pack(anchor="w", pady=(2, 4))

        bot = tk.Frame(parent, bg=Theme.CARD_BG)
        bot.pack(fill="x")
        PillBadge(bot, text=badge_text, status=badge_status, width=110, height=20).pack(side="left")
        MiniSparkline(bot, values=spark_data, color=sparkline_color, width=65, height=24).pack(side="right")

    def _render_dept_bar(self, parent, dept: str, placed: int, total: int, pct: float):
        row = tk.Frame(parent, bg=Theme.CARD_BG)
        row.pack(fill="x", pady=3)

        head = tk.Frame(row, bg=Theme.CARD_BG)
        head.pack(fill="x")
        tk.Label(head, text=dept, font=Theme.FONT_TINY, fg=Theme.TEXT_LIGHT, bg=Theme.CARD_BG).pack(side="left")
        tk.Label(head, text=f"{placed}/{total} Placed ({pct:.1f}%)", font=Theme.FONT_TINY, fg=Theme.ACCENT_PINK, bg=Theme.CARD_BG).pack(side="right")

        ratio = min(1.0, max(0.0, pct / 100.0))
        c = tk.Canvas(row, height=6, bg=Theme.CARD_BG, highlightthickness=0)
        c.pack(fill="x", pady=(2, 2))

        def draw(event):
            w = event.width
            c.delete("all")
            c.create_rectangle(0, 0, w, 6, fill=Theme.CARD_BORDER, outline="")
            fill_w = int(w * ratio)
            if fill_w > 0:
                c.create_rectangle(0, 0, fill_w, 6, fill=Theme.ACCENT_PINK, outline="")

        c.bind("<Configure>", draw)

    def _render_funnel_bar(self, parent, stage: str, count: int, pct: float, color: str):
        row = tk.Frame(parent, bg=Theme.CARD_BG)
        row.pack(fill="x", pady=3)

        head = tk.Frame(row, bg=Theme.CARD_BG)
        head.pack(fill="x")
        tk.Label(head, text=stage, font=Theme.FONT_TINY, fg=Theme.TEXT_LIGHT, bg=Theme.CARD_BG).pack(side="left")
        tk.Label(head, text=f"{count} ({pct:.0f}%)", font=Theme.FONT_TINY, fg=color, bg=Theme.CARD_BG).pack(side="right")

        ratio = min(1.0, max(0.0, pct / 100.0))
        c = tk.Canvas(row, height=6, bg=Theme.CARD_BG, highlightthickness=0)
        c.pack(fill="x", pady=(2, 2))

        def draw(event):
            w = event.width
            c.delete("all")
            c.create_rectangle(0, 0, w, 6, fill=Theme.CARD_BORDER, outline="")
            fill_w = int(w * ratio)
            if fill_w > 0:
                c.create_rectangle(0, 0, fill_w, 6, fill=color, outline="")

        c.bind("<Configure>", draw)
