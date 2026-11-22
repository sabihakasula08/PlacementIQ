"""
Main Window Shell for PlacementIQ
Hosts the modern matte black sidebar navigation matching the reference design,
dynamic breadcrumb bar, and content switching container.
"""
import tkinter as tk
from datetime import datetime
from typing import Optional, Dict
from utils.theme import Theme
from utils.constants import APP_NAME, APP_SUBTITLE
from utils.components import PillBadge, NeonButton
from models.user_model import User
from controllers.auth_controller import AuthController
from controllers.student_controller import StudentController
from controllers.admin_controller import AdminController
from controllers.analytics_controller import AnalyticsController

from views.student_dashboard import StudentDashboardView
from views.admin_dashboard import AdminDashboardView
from views.student_profile import StudentProfileView
from views.readiness_view import ReadinessView
from views.companies_view import CompaniesView
from views.drives_view import DrivesView
from views.applications_view import ApplicationsView
from views.analytics_view import AnalyticsView
from views.system_info_view import SystemInfoView

class MainWindow(tk.Frame):
    def __init__(self, parent, current_user: User, on_logout):
        super().__init__(parent, bg=Theme.BG_DARK)
        self.parent = parent
        self.current_user = current_user
        self.on_logout = on_logout

        # Initialize controllers
        self.auth_controller = AuthController()
        self.student_controller = StudentController()
        self.admin_controller = AdminController()
        self.analytics_controller = AnalyticsController()

        self.current_nav = "dashboard"
        self.nav_buttons: Dict[str, tk.Frame] = {}

        self._build_layout()
        self.navigate_to("dashboard")

    def _build_layout(self):
        # Left Sidebar (Matte Black matching screenshot)
        self.sidebar = tk.Frame(self, bg=Theme.SIDEBAR_BG, width=250)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Right Main Workspace
        self.workspace = tk.Frame(self, bg=Theme.BG_DARK)
        self.workspace.pack(side="right", fill="both", expand=True)

        self._build_sidebar()
        self._build_top_navbar()

        # Dynamic Content View Area
        self.content_area = tk.Frame(self.workspace, bg=Theme.BG_DARK)
        self.content_area.pack(fill="both", expand=True)

    def _build_sidebar(self):
        sb = self.sidebar

        # 1. Brand Logo Header (Matches screenshot "ZENTRA" style)
        brand_f = tk.Frame(sb, bg=Theme.SIDEBAR_BG)
        brand_f.pack(fill="x", padx=16, pady=(18, 14))

        # Brand Icon
        icon_cv = tk.Canvas(brand_f, width=32, height=32, bg=Theme.SIDEBAR_BG, highlightthickness=0)
        icon_cv.pack(side="left", padx=(0, 8))
        icon_cv.create_oval(1, 1, 31, 31, fill=Theme.ACCENT_PINK, outline=Theme.GRADIENT_HERO_START, width=1.5)
        icon_cv.create_text(16, 16, text="IQ", font=Theme.FONT_SMALL_BOLD, fill=Theme.TEXT_WHITE)

        brand_txt = tk.Frame(brand_f, bg=Theme.SIDEBAR_BG)
        brand_txt.pack(side="left")
        tk.Label(brand_txt, text=APP_NAME.upper(), font=Theme.FONT_TITLE_MED, fg=Theme.TEXT_WHITE, bg=Theme.SIDEBAR_BG).pack(anchor="w")
        tk.Label(brand_txt, text="Campus SaaS", font=Theme.FONT_TINY, fg=Theme.ACCENT_LAVENDER, bg=Theme.SIDEBAR_BG).pack(anchor="w")

        # 2. Search Capsule (Matches screenshot `Search... ⌘+F`)
        search_f = tk.Frame(sb, bg=Theme.CARD_BG, bd=1, relief="solid")
        search_f.pack(fill="x", padx=14, pady=(0, 14), ipady=3, ipadx=6)
        tk.Label(search_f, text="🔍 Search...", font=Theme.FONT_TINY, fg=Theme.TEXT_MUTED, bg=Theme.CARD_BG).pack(side="left")
        tk.Label(search_f, text="Ctrl+F", font=Theme.FONT_TINY, fg=Theme.TEXT_SUBTLE, bg=Theme.CARD_BG).pack(side="right")

        # 3. Main Menu Section Header
        tk.Label(sb, text="MAIN MENU", font=Theme.FONT_TINY, fg=Theme.TEXT_SUBTLE, bg=Theme.SIDEBAR_BG).pack(anchor="w", padx=18, pady=(4, 4))

        # Navigation items
        nav_items = [
            ("dashboard", "⚡ Dashboard", "2"),
            ("profile", "👤 My Profile" if self.current_user.is_student else "👥 Student Directory", None),
            ("readiness", "🎯 Placement Readiness", "★"),
            ("drives", "💼 Placement Drives", "6"),
            ("applications", "📋 Applications Pipeline", None),
            ("companies", "🏢 Partner Companies", None),
            ("analytics", "📊 Placement Analytics", None),
            ("sysinfo", "ℹ System Info & Viva", None),
        ]

        self.nav_container = tk.Frame(sb, bg=Theme.SIDEBAR_BG)
        self.nav_container.pack(fill="x", padx=10)

        for key, label, badge in nav_items:
            self._create_nav_button(self.nav_container, key, label, badge)

        # 4. Starred Section (Matches screenshot "Starred" section)
        tk.Label(sb, text="STARRED", font=Theme.FONT_TINY, fg=Theme.TEXT_SUBTLE, bg=Theme.SIDEBAR_BG).pack(anchor="w", padx=18, pady=(12, 4))

        quick_links = [
            ("drives", "🌸 Dream Offers (>15 LPA)", None),
            ("readiness", "🔥 Skill Gap Analysis", "99"),
            ("analytics", "💎 Campus Placement 2026", None)
        ]
        for key, label, badge in quick_links:
            self._create_nav_button(sb, f"star_{key}", label, badge, target_key=key)

        # 5. Bottom Section: Upgrade/Readiness Promo Card + User Profile Pill
        bot_f = tk.Frame(sb, bg=Theme.SIDEBAR_BG)
        bot_f.pack(side="bottom", fill="x", padx=12, pady=12)

        # Gradient Card (Matches screenshot bottom gradient card)
        promo_card = tk.Canvas(bot_f, height=88, bg=Theme.SIDEBAR_BG, highlightthickness=0)
        promo_card.pack(fill="x", pady=(0, 10))

        def draw_promo(event):
            w = event.width
            h = event.height
            promo_card.delete("all")
            # Draw gradient
            steps = 30
            for i in range(steps):
                t = i / steps
                col = Theme.GRADIENT_PURPLE_START if t < 0.5 else Theme.ACCENT_PINK
                x1 = i * (w / steps)
                x2 = (i + 1) * (w / steps) + 1
                promo_card.create_rectangle(x1, 0, x2, h, fill=col, outline="")
            # Text
            promo_card.create_text(12, 18, text="Placement Readiness", font=Theme.FONT_SMALL_BOLD, fill=Theme.TEXT_WHITE, anchor="w")
            promo_card.create_text(12, 34, text="Boost score & unlock drives", font=Theme.FONT_TINY, fill="#F2E6FC", anchor="w")
            # Pill button inside
            promo_card.create_rectangle(12, 52, w - 12, 76, fill="#FFFFFF", outline="", width=0)
            promo_card.create_text(w // 2, 64, text="↑ Calculate Now", font=Theme.FONT_SMALL_BOLD, fill=Theme.TEXT_DARK)

        promo_card.bind("<Configure>", draw_promo)
        promo_card.bind("<Button-1>", lambda e: self.navigate_to("readiness"))

        # User Profile Pill & Logout (Matches screenshot bottom avatar)
        user_pill = tk.Frame(bot_f, bg=Theme.CARD_BG_ALT, bd=1, relief="solid")
        user_pill.pack(fill="x", ipady=4, ipadx=6)

        av_c = tk.Canvas(user_pill, width=28, height=28, bg=Theme.CARD_BG_ALT, highlightthickness=0)
        av_c.pack(side="left", padx=(2, 6))
        av_c.create_oval(1, 1, 27, 27, fill=Theme.ACCENT_PINK, outline=Theme.TEXT_WHITE)
        initials = "".join([w[0] for w in self.current_user.full_name.split()[:2]]).upper()
        av_c.create_text(14, 14, text=initials, font=Theme.FONT_TINY, fill=Theme.TEXT_WHITE)

        u_info = tk.Frame(user_pill, bg=Theme.CARD_BG_ALT)
        u_info.pack(side="left", fill="both", expand=True)
        tk.Label(u_info, text=self.current_user.full_name, font=Theme.FONT_TINY, fg=Theme.TEXT_WHITE, bg=Theme.CARD_BG_ALT).pack(anchor="w")
        role_title = "Student" if self.current_user.is_student else "Placement Head"
        tk.Label(u_info, text=role_title, font=Theme.FONT_TINY, fg=Theme.TEXT_MUTED, bg=Theme.CARD_BG_ALT).pack(anchor="w")

        # Logout Button
        logout_btn = tk.Button(
            user_pill, text="⎋", font=("Segoe UI", 11, "bold"),
            bg=Theme.CARD_BG_ALT, fg=Theme.COLOR_DANGER,
            activebackground=Theme.CARD_BG, activeforeground=Theme.COLOR_DANGER,
            bd=0, relief="flat", cursor="hand2", command=self.on_logout
        )
        logout_btn.pack(side="right", padx=2)

    def _create_nav_button(self, parent, key: str, label: str, badge: Optional[str] = None, target_key: Optional[str] = None):
        action_key = target_key or key
        btn_frame = tk.Frame(parent, bg=Theme.SIDEBAR_BG, cursor="hand2")
        btn_frame.pack(fill="x", pady=2, ipady=4, ipadx=8)

        lbl = tk.Label(btn_frame, text=label, font=Theme.FONT_SMALL, fg=Theme.TEXT_MUTED, bg=Theme.SIDEBAR_BG, cursor="hand2")
        lbl.pack(side="left")

        if badge:
            badge_lbl = tk.Label(
                btn_frame, text=badge, font=Theme.FONT_TINY,
                fg=Theme.TEXT_WHITE, bg=Theme.ACCENT_PINK,
                padx=5, pady=0
            )
            badge_lbl.pack(side="right")

        def on_click(e):
            self.navigate_to(action_key)

        btn_frame.bind("<Button-1>", on_click)
        lbl.bind("<Button-1>", on_click)

        self.nav_buttons[key] = btn_frame

    def _build_top_navbar(self):
        # Top breadcrumb bar (Matches screenshot top navbar)
        self.top_bar = tk.Frame(self.workspace, bg=Theme.BG_DARK, height=44)
        self.top_bar.pack(fill="x", padx=20, pady=(10, 0))

        self.breadcrumb_lbl = tk.Label(
            self.top_bar, text="Dashboard / Overview",
            font=Theme.FONT_SMALL, fg=Theme.TEXT_MUTED, bg=Theme.BG_DARK
        )
        self.breadcrumb_lbl.pack(side="left")

        right_top = tk.Frame(self.top_bar, bg=Theme.BG_DARK)
        right_top.pack(side="right")

        tk.Label(right_top, text="☆", font=("Segoe UI", 12), fg=Theme.TEXT_MUTED, bg=Theme.BG_DARK, cursor="hand2").pack(side="left", padx=8)
        tk.Label(right_top, text="🔗 Share", font=Theme.FONT_SMALL, fg=Theme.TEXT_LIGHT, bg=Theme.CARD_BG_ALT, cursor="hand2").pack(side="left", padx=8, ipady=3, ipadx=8)

    def navigate_to(self, view_name: str):
        self.current_nav = view_name

        # Update sidebar active styling
        for k, f in self.nav_buttons.items():
            is_active = (k == view_name or (k.startswith("star_") and k[5:] == view_name))
            f.configure(bg=Theme.CARD_BG_ALT if is_active else Theme.SIDEBAR_BG)
            for child in f.winfo_children():
                if isinstance(child, tk.Label) and child.cget("text") not in ("2", "★", "6", "99"):
                    child.configure(
                        bg=Theme.CARD_BG_ALT if is_active else Theme.SIDEBAR_BG,
                        fg=Theme.TEXT_WHITE if is_active else Theme.TEXT_MUTED,
                        font=Theme.FONT_SMALL_BOLD if is_active else Theme.FONT_SMALL
                    )

        # Clear workspace
        for child in self.content_area.winfo_children():
            child.destroy()

        # Update Breadcrumb
        titles = {
            "dashboard": "Dashboard / Overview",
            "profile": "Student Portal / My Profile",
            "readiness": "Analytics / Smart Placement Readiness & Skill Gap",
            "drives": "Recruitment / Placement Drives",
            "applications": "Recruitment / Application Pipeline",
            "companies": "Directory / Partner Companies",
            "analytics": "Executive / Placement Analytics",
            "sysinfo": "System / Architecture & Viva Guide",
        }
        self.breadcrumb_lbl.configure(text=titles.get(view_name, "Dashboard / Overview"))

        # Render corresponding view
        if view_name == "dashboard":
            if self.current_user.is_student:
                view = StudentDashboardView(self.content_area, self.current_user, self.student_controller, self.navigate_to)
            else:
                view = AdminDashboardView(self.content_area, self.current_user, self.admin_controller, self.analytics_controller, self.navigate_to)
        elif view_name == "profile":
            view = StudentProfileView(self.content_area, self.current_user, self.student_controller, self.navigate_to)
        elif view_name == "readiness":
            view = ReadinessView(self.content_area, self.current_user, self.student_controller, self.admin_controller, self.navigate_to)
        elif view_name == "drives":
            view = DrivesView(self.content_area, self.current_user, self.admin_controller, self.student_controller, self.navigate_to)
        elif view_name == "applications":
            view = ApplicationsView(self.content_area, self.current_user, self.student_controller, self.admin_controller, self.navigate_to)
        elif view_name == "companies":
            view = CompaniesView(self.content_area, self.current_user, self.admin_controller, self.navigate_to)
        elif view_name == "analytics":
            view = AnalyticsView(self.content_area, self.current_user, self.analytics_controller, self.navigate_to)
        elif view_name == "sysinfo":
            view = SystemInfoView(self.content_area, self.navigate_to)
        else:
            view = tk.Label(self.content_area, text=f"View '{view_name}' under construction.", fg=Theme.TEXT_MUTED, bg=Theme.BG_DARK)

        view.pack(fill="both", expand=True)
