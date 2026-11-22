"""
Student Dashboard View for PlacementIQ
Faithfully mirrors the dark neon SaaS reference design with welcome gradient banner,
sparkline KPI cards, interactive trend line chart, concentric readiness arcs,
eligible drive quick cards, and today's schedule timeline.
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
from models.student_model import Student
from controllers.student_controller import StudentController

class StudentDashboardView(tk.Frame):
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
        # Scrollable container for flexible resolution
        self.scroll = ScrollableFrame(self, bg=Theme.BG_DARK)
        self.scroll.pack(fill="both", expand=True)
        container = self.scroll.scrollable_content

        # 1. Top Hero Gradient Banner
        now_str = datetime.now().strftime("%d %b %Y, %I:%M %p")
        dept_str = self.student.department if self.student else "Student Portal"
        reg_str = f"Reg: {self.student.register_no} • " if self.student else ""

        self.banner = GradientBanner(
            container,
            title=f"Welcome Back, {self.current_user.full_name}",
            subtitle=f"{reg_str}{dept_str} • Ready for Campus Placement",
            action_text="+ View Eligible",
            action_callback=lambda: self.nav_callback("drives"),
            date_text=now_str,
            height=110
        )
        self.banner.pack(fill="x", padx=18, pady=(16, 14))

        # 2. Top KPI Cards Row (Total Readiness, Eligible Drives, Placed/Status)
        kpi_row = tk.Frame(container, bg=Theme.BG_DARK)
        kpi_row.pack(fill="x", padx=18, pady=(0, 14))
        kpi_row.columnconfigure(0, weight=1)
        kpi_row.columnconfigure(1, weight=1)
        kpi_row.columnconfigure(2, weight=1)

        # Calculate student readiness
        if self.student:
            readiness = self.student_controller.get_readiness_analysis(self.student)
            score_val = readiness.overall_score
            level_str = readiness.readiness_level
            drives_with_elig = self.student_controller.get_drives_with_eligibility(self.student)
            eligible_count = sum(1 for d, el, app in drives_with_elig if el.is_eligible)
            apps = self.student_controller.get_student_applications(self.student.id)
            applied_count = len(apps)
            selected_count = sum(1 for a in apps if a.status == "Selected")
        else:
            score_val = 0.0
            level_str = "N/A"
            eligible_count = 0
            applied_count = 0
            selected_count = 0

        # KPI Card 1: Readiness Score
        card1 = ModernCard(kpi_row, padding=14)
        card1.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        self._build_kpi_card(
            card1.inner,
            label="Placement Readiness",
            value=f"{score_val:.0f}/100",
            badge_text=level_str,
            badge_status="Good Fit" if score_val >= 70 else "Assessment",
            sparkline_color=Theme.ACCENT_PINK,
            spark_data=[55, 60, 68, 72, 75, int(score_val)]
        )

        # KPI Card 2: Eligible Drives
        card2 = ModernCard(kpi_row, padding=14)
        card2.grid(row=0, column=1, sticky="nsew", padx=4)
        self._build_kpi_card(
            card2.inner,
            label="Eligible Campus Drives",
            value=f"{eligible_count} Open",
            badge_text=f"{eligible_count} Active" if eligible_count > 0 else "Review Gaps",
            badge_status="Active" if eligible_count > 0 else "Ineligible",
            sparkline_color=Theme.ACCENT_PURPLE,
            spark_data=[2, 3, 4, 5, 5, eligible_count]
        )

        # KPI Card 3: Applications & Placement Status
        card3 = ModernCard(kpi_row, padding=14)
        card3.grid(row=0, column=2, sticky="nsew", padx=(8, 0))
        status_lbl = "Selected" if selected_count > 0 else f"{applied_count} Active"
        status_badge = "Selected" if selected_count > 0 else "Shortlisted"
        self._build_kpi_card(
            card3.inner,
            label="Application Pipeline",
            value=f"{applied_count} Applied",
            badge_text=status_lbl,
            badge_status=status_badge,
            sparkline_color=Theme.COLOR_SUCCESS,
            spark_data=[1, 1, 2, 2, 3, applied_count]
        )

        # 3. Middle Row: Left Big Line Chart + Right Recruitment Activity List
        mid_row = tk.Frame(container, bg=Theme.BG_DARK)
        mid_row.pack(fill="x", padx=18, pady=(0, 14))
        mid_row.columnconfigure(0, weight=6) # 60% width
        mid_row.columnconfigure(1, weight=4) # 40% width

        # Left: Interactive Trend Chart Card
        chart_card = ModernCard(mid_row, padding=16)
        chart_card.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        chart_head = tk.Frame(chart_card.inner, bg=Theme.CARD_BG)
        chart_head.pack(fill="x", pady=(0, 10))

        title_sub = tk.Frame(chart_head, bg=Theme.CARD_BG)
        title_sub.pack(side="left")
        tk.Label(title_sub, text="Preparation & Drive Activity", font=Theme.FONT_TITLE_MED, fg=Theme.TEXT_WHITE, bg=Theme.CARD_BG).pack(anchor="w")
        tk.Label(title_sub, text="Application progression and campus recruitment benchmarks", font=Theme.FONT_TINY, fg=Theme.TEXT_MUTED, bg=Theme.CARD_BG).pack(anchor="w")

        SegmentedToggle(
            chart_head,
            options=["Daily", "Weekly", "Monthly"],
            default_index=2,
            height=28,
            pill_width=60
        ).pack(side="right")

        self.chart = InteractiveLineChart(chart_card.inner, height=195)
        self.chart.pack(fill="both", expand=True)

        # Right: Live Eligible Drives / Recruitment Card (like Andi Sanjaya UI in screenshot)
        right_card = ModernCard(mid_row, padding=16)
        right_card.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

        r_head = tk.Frame(right_card.inner, bg=Theme.CARD_BG)
        r_head.pack(fill="x", pady=(0, 10))

        r_title = tk.Frame(r_head, bg=Theme.CARD_BG)
        r_title.pack(side="left")
        tk.Label(r_title, text="Eligible Campus Drives", font=Theme.FONT_TITLE_MED, fg=Theme.TEXT_WHITE, bg=Theme.CARD_BG).pack(anchor="w")
        tk.Label(r_title, text="Top matching recruitment drives", font=Theme.FONT_TINY, fg=Theme.TEXT_MUTED, bg=Theme.CARD_BG).pack(anchor="w")

        # Top 2 Eligible Drive Items
        drives_box = tk.Frame(right_card.inner, bg=Theme.CARD_BG)
        drives_box.pack(fill="both", expand=True)

        if self.student:
            eligible_drives = [item for item in drives_with_elig if item[1].is_eligible][:2]
            if not eligible_drives:
                eligible_drives = drives_with_elig[:2]

            for drive, el, has_applied in eligible_drives:
                self._build_drive_list_item(drives_box, drive, el, has_applied)

        # See All Button at bottom of card
        NeonButton(
            right_card.inner,
            text="See All Drives  →",
            command=lambda: self.nav_callback("drives"),
            style="secondary",
            width=280,
            height=32
        ).pack(fill="x", pady=(10, 0))

        # 4. Bottom Row: Concentric Gauge Card + Today's Schedule Timeline Card
        bottom_row = tk.Frame(container, bg=Theme.BG_DARK)
        bottom_row.pack(fill="x", padx=18, pady=(0, 20))
        bottom_row.columnconfigure(0, weight=5)
        bottom_row.columnconfigure(1, weight=5)

        # Bottom Left: Readiness Concentric Rings
        gauge_card = ModernCard(bottom_row, padding=16)
        gauge_card.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        g_head = tk.Frame(gauge_card.inner, bg=Theme.CARD_BG)
        g_head.pack(fill="x", pady=(0, 6))

        g_title = tk.Frame(g_head, bg=Theme.CARD_BG)
        g_title.pack(side="left")
        tk.Label(g_title, text="Readiness Category Breakdown", font=Theme.FONT_TITLE_MED, fg=Theme.TEXT_WHITE, bg=Theme.CARD_BG).pack(anchor="w")
        tk.Label(g_title, text="Concentric skill scoring across evaluation pillars", font=Theme.FONT_TINY, fg=Theme.TEXT_MUTED, bg=Theme.CARD_BG).pack(anchor="w")

        if self.student:
            category_scores = {
                "Academics": readiness.academic_score,
                "Technical Skills": readiness.technical_score,
                "Aptitude": readiness.aptitude_score,
                "Communication": readiness.communication_score,
                "Projects": readiness.project_score
            }
        else:
            category_scores = {"Academics": 20, "Technical Skills": 20, "Aptitude": 15, "Communication": 10, "Projects": 10}

        ConcentricGauge(
            gauge_card.inner,
            category_scores=category_scores,
            overall_score=score_val,
            height=160
        ).pack(fill="both", expand=True)

        # Bottom Right: Today's Schedule Card
        sched_card = ModernCard(bottom_row, padding=16)
        sched_card.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

        s_head = tk.Frame(sched_card.inner, bg=Theme.CARD_BG)
        s_head.pack(fill="x", pady=(0, 6))

        s_title = tk.Frame(s_head, bg=Theme.CARD_BG)
        s_title.pack(side="left")
        tk.Label(s_title, text="Today's Schedule & Deadlines", font=Theme.FONT_TITLE_MED, fg=Theme.TEXT_WHITE, bg=Theme.CARD_BG).pack(anchor="w")
        tk.Label(s_title, text="Upcoming online assessments, tests & interviews", font=Theme.FONT_TINY, fg=Theme.TEXT_MUTED, bg=Theme.CARD_BG).pack(anchor="w")

        ScheduleTimelineWidget(
            sched_card.inner,
            events=[
                {"time_idx": 1, "title": "Google Cloud Online Test", "subtitle": "Auditorium Lab 3 • 10:00 AM", "color": Theme.GRADIENT_PURPLE_START},
                {"time_idx": 4, "title": "Microsoft SDE Tech Interview", "subtitle": "Teams Room 2 • 02:00 PM", "color": Theme.ACCENT_PINK}
            ],
            height=140
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

        PillBadge(val_col, text=badge_text, status=badge_status, width=110, height=22).pack(anchor="w", pady=(4, 0))

        # Mini Sparkline on right
        MiniSparkline(bot_f, values=spark_data, color=sparkline_color, width=95, height=36).pack(side="right")

    def _build_drive_list_item(self, parent, drive, el, has_applied: bool):
        row = tk.Frame(parent, bg=Theme.CARD_BG_ALT, bd=1, relief="solid")
        row.pack(fill="x", pady=4, ipady=6, ipadx=8)

        # Company Icon/Avatar Circle
        av_canvas = tk.Canvas(row, width=36, height=36, bg=Theme.CARD_BG_ALT, highlightthickness=0)
        av_canvas.pack(side="left", padx=(4, 10))
        av_canvas.create_oval(2, 2, 34, 34, fill=Theme.CARD_BG, outline=Theme.ACCENT_PINK, width=1.5)
        initials = "".join([w[0] for w in drive.company_name.split()[:2]]).upper()
        av_canvas.create_text(18, 18, text=initials, font=Theme.FONT_SMALL_BOLD, fill=Theme.TEXT_WHITE)

        # Details
        info = tk.Frame(row, bg=Theme.CARD_BG_ALT)
        info.pack(side="left", fill="both", expand=True)

        tk.Label(info, text=f"{drive.company_name} • {drive.title}", font=Theme.FONT_BODY_BOLD, fg=Theme.TEXT_WHITE, bg=Theme.CARD_BG_ALT).pack(anchor="w")
        tk.Label(info, text=f"Package: {drive.package_lpa:.1f} LPA • Min CGPA: {drive.min_cgpa:.1f}", font=Theme.FONT_TINY, fg=Theme.TEXT_MUTED, bg=Theme.CARD_BG_ALT).pack(anchor="w")

        # Status badge or Apply button
        if has_applied:
            PillBadge(row, text="Applied", status="Applied", width=70, height=24).pack(side="right", padx=6)
        elif el.is_eligible:
            PillBadge(row, text=f"{el.skills_match_pct:.0f}% Match", status="Good Fit", width=85, height=24).pack(side="right", padx=6)
        else:
            PillBadge(row, text="Skill Gap", status="Ineligible", width=70, height=24).pack(side="right", padx=6)
