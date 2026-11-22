"""
Admin Dashboard View for PlacementIQ
Faithfully mirrors the uploaded SaaS interface with welcome gradient banner,
applicant & open roles KPI cards, candidate applied trend line chart,
recruitment candidate pipeline cards (Andi Sanjaya style), concentric statistics gauge,
and today's schedule timeline.
"""
import tkinter as tk
from datetime import datetime
from typing import Callable, Optional
from utils.theme import Theme
from utils.components import (
    ModernCard, GradientBanner, NeonButton, PillBadge,
    SegmentedToggle, InteractiveLineChart, ConcentricGauge,
    MiniSparkline, ScheduleTimelineWidget, ScrollableFrame
)
from models.user_model import User
from controllers.admin_controller import AdminController
from controllers.analytics_controller import AnalyticsController

class AdminDashboardView(tk.Frame):
    def __init__(
        self,
        parent,
        current_user: User,
        admin_controller: AdminController,
        analytics_controller: AnalyticsController,
        nav_callback: Callable[[str], None]
    ):
        super().__init__(parent, bg=Theme.BG_DARK)
        self.current_user = current_user
        self.admin_controller = admin_controller
        self.analytics_controller = analytics_controller
        self.nav_callback = nav_callback

        self._build_ui()

    def _build_ui(self):
        # Scrollable container for laptop & desktop resolutions
        self.scroll = ScrollableFrame(self, bg=Theme.BG_DARK)
        self.scroll.pack(fill="both", expand=True)
        container = self.scroll.scrollable_content

        # Fetch KPIs
        kpi = self.analytics_controller.get_kpi_summary()
        all_apps = self.admin_controller.get_all_applications()

        # 1. Top Hero Gradient Banner (Matches Reference Image)
        now_str = datetime.now().strftime("%d %b %Y, %I:%M %p")
        self.banner = GradientBanner(
            container,
            title=f"Welcome Back, {self.current_user.full_name}",
            subtitle=f"Placement Operations Command Center • {kpi['active_drives']} Active Drives",
            action_text="+ Add Jobs",
            action_callback=lambda: self.nav_callback("drives"),
            date_text=now_str,
            height=110
        )
        self.banner.pack(fill="x", padx=18, pady=(16, 14))

        # 2. Top KPI Cards Row: Total Applicant, Open Roles, Placed Students
        kpi_row = tk.Frame(container, bg=Theme.BG_DARK)
        kpi_row.pack(fill="x", padx=18, pady=(0, 14))
        kpi_row.columnconfigure(0, weight=1)
        kpi_row.columnconfigure(1, weight=1)
        kpi_row.columnconfigure(2, weight=1)

        # KPI Card 1: Total Applicant (Matches Reference Screenshot)
        card1 = ModernCard(kpi_row, padding=14)
        card1.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        self._build_kpi_card(
            card1.inner,
            label="Total Applicant",
            value=f"{kpi['total_applications']:,}",
            badge_text="↗ 10% +142",
            badge_status="Good Fit",
            sparkline_color=Theme.ACCENT_PURPLE,
            spark_data=[14, 18, 25, 32, 28, 45, 42, 60]
        )

        # KPI Card 2: Open Roles (Matches Reference Screenshot)
        card2 = ModernCard(kpi_row, padding=14)
        card2.grid(row=0, column=1, sticky="nsew", padx=4)
        self._build_kpi_card(
            card2.inner,
            label="Open Roles",
            value=f"{kpi['active_drives']}",
            badge_text="↗ 10% +142",
            badge_status="Good Fit",
            sparkline_color=Theme.ACCENT_ORANGE,
            spark_data=[3, 4, 4, 5, 5, 6, 6]
        )

        # KPI Card 3: Placed / Selections
        card3 = ModernCard(kpi_row, padding=14)
        card3.grid(row=0, column=2, sticky="nsew", padx=(8, 0))
        self._build_kpi_card(
            card3.inner,
            label="Students Placed",
            value=f"{kpi['placed_students']}",
            badge_text=f"{kpi['placement_pct']}% Rate",
            badge_status="Selected",
            sparkline_color=Theme.COLOR_SUCCESS,
            spark_data=[0, 1, 1, 2, 2, kpi['placed_students']]
        )

        # 3. Middle Row: Left Big Line Chart ("Candidate Applied") + Right Recruitment Pipeline Card
        mid_row = tk.Frame(container, bg=Theme.BG_DARK)
        mid_row.pack(fill="x", padx=18, pady=(0, 14))
        mid_row.columnconfigure(0, weight=6)
        mid_row.columnconfigure(1, weight=4)

        # Left: "Candidate Applied" Line Chart Card (Matches Screenshot)
        chart_card = ModernCard(mid_row, padding=16)
        chart_card.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        chart_head = tk.Frame(chart_card.inner, bg=Theme.CARD_BG)
        chart_head.pack(fill="x", pady=(0, 10))

        title_sub = tk.Frame(chart_head, bg=Theme.CARD_BG)
        title_sub.pack(side="left")
        tk.Label(title_sub, text="Candidate Applied", font=Theme.FONT_TITLE_MED, fg=Theme.TEXT_WHITE, bg=Theme.CARD_BG).pack(anchor="w")
        tk.Label(title_sub, text="Recruitment application volume & interview trends", font=Theme.FONT_TINY, fg=Theme.TEXT_MUTED, bg=Theme.CARD_BG).pack(anchor="w")

        SegmentedToggle(
            chart_head,
            options=["Daily", "Weekly", "Monthly"],
            default_index=2,
            height=28,
            pill_width=60
        ).pack(side="right")

        self.chart = InteractiveLineChart(
            chart_card.inner,
            data_points=[220, 240, 310, 480, 460, 680, 520, 580, 610, 490, 470, 540],
            labels=["Lbl", "Lbl", "Lbl", "Lbl", "Lbl", "Lbl", "Lbl", "Lbl", "Lbl", "Lbl", "Lbl", "Lbl"],
            height=195
        )
        self.chart.pack(fill="both", expand=True)

        # Right: "Recruitment" Candidate Stream Card (Matches Andi Sanjaya layout in Screenshot)
        right_card = ModernCard(mid_row, padding=16)
        right_card.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

        r_head = tk.Frame(right_card.inner, bg=Theme.CARD_BG)
        r_head.pack(fill="x", pady=(0, 8))

        r_title = tk.Frame(r_head, bg=Theme.CARD_BG)
        r_title.pack(side="left")
        tk.Label(r_title, text="Recruitment", font=Theme.FONT_TITLE_MED, fg=Theme.TEXT_WHITE, bg=Theme.CARD_BG).pack(anchor="w")
        tk.Label(r_title, text="Active candidate pipeline & screening", font=Theme.FONT_TINY, fg=Theme.TEXT_MUTED, bg=Theme.CARD_BG).pack(anchor="w")

        # [Positions] [Candidate] toggle switch
        SegmentedToggle(
            right_card.inner,
            options=["Positions", "Candidate"],
            default_index=1,
            height=30,
            pill_width=110
        ).pack(pady=(0, 10))

        # Candidate Stream Items (Andi Sanjaya style)
        stream_box = tk.Frame(right_card.inner, bg=Theme.CARD_BG)
        stream_box.pack(fill="both", expand=True)

        # Display top 2 applications
        top_apps = all_apps[:2]
        if top_apps:
            for app in top_apps:
                self._build_candidate_item(stream_box, app)
        else:
            tk.Label(stream_box, text="No candidate applications yet.", fg=Theme.TEXT_MUTED, bg=Theme.CARD_BG).pack(pady=20)

        # See All Button at bottom of card
        NeonButton(
            right_card.inner,
            text="See All",
            command=lambda: self.nav_callback("applications"),
            style="secondary",
            width=280,
            height=32
        ).pack(fill="x", pady=(10, 0))

        # 4. Bottom Row: Left "Statistic" Multi-Ring + Right "Today's schedule" Timeline (Matches Screenshot)
        bottom_row = tk.Frame(container, bg=Theme.BG_DARK)
        bottom_row.pack(fill="x", padx=18, pady=(0, 20))
        bottom_row.columnconfigure(0, weight=5)
        bottom_row.columnconfigure(1, weight=5)

        # Bottom Left: "Statistic" Concentric Gauge Card
        stat_card = ModernCard(bottom_row, padding=16)
        stat_card.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        stat_head = tk.Frame(stat_card.inner, bg=Theme.CARD_BG)
        stat_head.pack(fill="x", pady=(0, 6))

        stat_title = tk.Frame(stat_head, bg=Theme.CARD_BG)
        stat_title.pack(side="left")
        tk.Label(stat_title, text="Statistic", font=Theme.FONT_TITLE_MED, fg=Theme.TEXT_WHITE, bg=Theme.CARD_BG).pack(anchor="w")
        tk.Label(stat_title, text="Applicant statistic & readiness breakdown", font=Theme.FONT_TINY, fg=Theme.TEXT_MUTED, bg=Theme.CARD_BG).pack(anchor="w")

        # Type / Ages / Gender toggle from screenshot
        SegmentedToggle(
            stat_card.inner,
            options=["Type", "Ages", "Gender"],
            default_index=0,
            height=26,
            pill_width=65
        ).pack(anchor="w", pady=(2, 6))

        readiness_dist = self.analytics_controller.get_readiness_distribution()
        ConcentricGauge(
            stat_card.inner,
            category_scores={
                "Academics": 22.0,
                "Technical Skills": 21.5,
                "Aptitude": 17.5,
                "Communication": 13.0,
                "Projects": 12.0
            },
            overall_score=86.0,
            height=145
        ).pack(fill="both", expand=True)

        # Bottom Right: "Today's schedule" Card (Matches Screenshot)
        sched_card = ModernCard(bottom_row, padding=16)
        sched_card.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

        s_head = tk.Frame(sched_card.inner, bg=Theme.CARD_BG)
        s_head.pack(fill="x", pady=(0, 6))

        tk.Label(s_head, text="Today's schedule", font=Theme.FONT_TITLE_MED, fg=Theme.TEXT_WHITE, bg=Theme.CARD_BG).pack(side="left")

        # Date header + Selected filter badge
        s_sub = tk.Frame(sched_card.inner, bg=Theme.CARD_BG)
        s_sub.pack(fill="x", pady=(0, 4))
        tk.Label(s_sub, text="📅 12 April 2026", font=Theme.FONT_SMALL_BOLD, fg=Theme.TEXT_LIGHT, bg=Theme.CARD_BG_ALT).pack(side="left", ipady=3, ipadx=8)
        tk.Label(s_sub, text="⚙ Selected", font=Theme.FONT_TINY, fg=Theme.TEXT_MUTED, bg=Theme.CARD_BG).pack(side="right")

        ScheduleTimelineWidget(
            sched_card.inner,
            events=[
                {"time_idx": 1, "title": "Candidate Screening Round", "subtitle": "Google Cloud • Room 3", "color": Theme.GRADIENT_PURPLE_START},
                {"time_idx": 4, "title": "Technical SDE Assessment", "subtitle": "Microsoft • Lab 1", "color": Theme.ACCENT_PINK}
            ],
            height=125
        ).pack(fill="both", expand=True)

    def _build_kpi_card(self, parent, label: str, value: str, badge_text: str, badge_status: str, sparkline_color: str, spark_data: list):
        top_f = tk.Frame(parent, bg=Theme.CARD_BG)
        top_f.pack(fill="x")
        tk.Label(top_f, text=label, font=Theme.FONT_SMALL, fg=Theme.TEXT_MUTED, bg=Theme.CARD_BG).pack(side="left")

        bot_f = tk.Frame(parent, bg=Theme.CARD_BG)
        bot_f.pack(fill="x", pady=(8, 0))

        val_col = tk.Frame(bot_f, bg=Theme.CARD_BG)
        val_col.pack(side="left")

        tk.Label(val_col, text=value, font=Theme.FONT_NUMBER_HERO, fg=Theme.TEXT_WHITE, bg=Theme.CARD_BG).pack(anchor="w")

        PillBadge(val_col, text=badge_text, status=badge_status, width=105, height=22).pack(anchor="w", pady=(4, 0))

        MiniSparkline(bot_f, values=spark_data, color=sparkline_color, width=95, height=36).pack(side="right")

    def _build_candidate_item(self, parent, app):
        card = tk.Frame(parent, bg=Theme.CARD_BG_ALT, bd=1, relief="solid")
        card.pack(fill="x", pady=4, ipady=6, ipadx=8)

        # Header row: Avatar + Name/Role + ellipsis
        top_r = tk.Frame(card, bg=Theme.CARD_BG_ALT)
        top_r.pack(fill="x")

        # Avatar circle
        av = tk.Canvas(top_r, width=32, height=32, bg=Theme.CARD_BG_ALT, highlightthickness=0)
        av.pack(side="left", padx=(0, 8))
        av.create_oval(1, 1, 31, 31, fill=Theme.CARD_BG, outline=Theme.ACCENT_PINK, width=1.5)
        initials = "".join([w[0] for w in app.student_name.split()[:2]]).upper()
        av.create_text(16, 16, text=initials, font=Theme.FONT_TINY, fill=Theme.TEXT_WHITE)

        name_box = tk.Frame(top_r, bg=Theme.CARD_BG_ALT)
        name_box.pack(side="left", fill="both", expand=True)

        tk.Label(name_box, text=app.student_name, font=Theme.FONT_SMALL_BOLD, fg=Theme.TEXT_WHITE, bg=Theme.CARD_BG_ALT).pack(anchor="w")
        tk.Label(name_box, text=f"{app.drive_title} ({app.company_name})", font=Theme.FONT_TINY, fg=Theme.TEXT_MUTED, bg=Theme.CARD_BG_ALT).pack(anchor="w")

        tk.Label(top_r, text="⋮", font=Theme.FONT_HEADING, fg=Theme.TEXT_MUTED, bg=Theme.CARD_BG_ALT).pack(side="right")

        # Step & Date row
        meta_r = tk.Frame(card, bg=Theme.CARD_BG_ALT)
        meta_r.pack(fill="x", pady=(6, 2))

        step_col = tk.Frame(meta_r, bg=Theme.CARD_BG_ALT)
        step_col.pack(side="left")
        tk.Label(step_col, text="Step", font=Theme.FONT_TINY, fg=Theme.TEXT_SUBTLE, bg=Theme.CARD_BG_ALT).pack(anchor="w")
        tk.Label(step_col, text=f"{app.status} Round", font=Theme.FONT_SMALL_BOLD, fg=Theme.TEXT_LIGHT, bg=Theme.CARD_BG_ALT).pack(anchor="w")

        date_col = tk.Frame(meta_r, bg=Theme.CARD_BG_ALT)
        date_col.pack(side="right")
        tk.Label(date_col, text="Applied", font=Theme.FONT_TINY, fg=Theme.TEXT_SUBTLE, bg=Theme.CARD_BG_ALT).pack(anchor="e")
        tk.Label(date_col, text=app.applied_date[:10], font=Theme.FONT_SMALL_BOLD, fg=Theme.TEXT_LIGHT, bg=Theme.CARD_BG_ALT).pack(anchor="e")

        # Bottom row: Sparkle + "Good Fit" pill badge (Matches Screenshot)
        bot_r = tk.Frame(card, bg=Theme.CARD_BG_ALT)
        bot_r.pack(fill="x", pady=(6, 2))
        tk.Label(bot_r, text="✦", font=Theme.FONT_BODY_BOLD, fg=Theme.ACCENT_PINK, bg=Theme.CARD_BG_ALT).pack(side="left")

        badge_status = "Good Fit" if app.status in ("Selected", "Interview", "Shortlisted") else app.status
        PillBadge(bot_r, text=app.status, status=badge_status, width=80, height=22).pack(side="right")
