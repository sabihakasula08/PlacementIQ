"""
System Information & APP Viva Evaluation Guide View
Provides comprehensive technical documentation, MVC architecture breakdown,
database schema overview, and sample Viva questions and answers.
"""
import tkinter as tk
from typing import Callable
from utils.theme import Theme
from utils.constants import APP_NAME, APP_SUBTITLE, APP_VERSION
from utils.components import ModernCard, NeonButton, PillBadge, ScrollableFrame

class SystemInfoView(tk.Frame):
    def __init__(self, parent, nav_callback: Callable[[str], None]):
        super().__init__(parent, bg=Theme.BG_DARK)
        self.nav_callback = nav_callback
        self._build_ui()

    def _build_ui(self):
        self.scroll = ScrollableFrame(self, bg=Theme.BG_DARK)
        self.scroll.pack(fill="both", expand=True)
        container = self.scroll.scrollable_content

        # Header Title
        head_f = tk.Frame(container, bg=Theme.BG_DARK)
        head_f.pack(fill="x", padx=20, pady=(18, 12))

        tk.Label(head_f, text=f"{APP_NAME} — System Architecture & Viva Guide", font=Theme.FONT_TITLE_LARGE, fg=Theme.TEXT_WHITE, bg=Theme.BG_DARK).pack(anchor="w")
        tk.Label(head_f, text="Advanced Programming Practices (APP) Project Documentation & Evaluation Reference", font=Theme.FONT_SMALL, fg=Theme.TEXT_MUTED, bg=Theme.BG_DARK).pack(anchor="w")

        # 1. Project Overview Card
        c1 = ModernCard(container, padding=18)
        c1.pack(fill="x", padx=20, pady=(0, 14))

        tk.Label(c1.inner, text="1. Project Synopsis & Core Innovation", font=Theme.FONT_TITLE_MED, fg=Theme.TEXT_WHITE, bg=Theme.CARD_BG).pack(anchor="w")
        synopsis = (
            "PlacementIQ is an offline-first, enterprise-grade desktop placement management system built in Python "
            "using Tkinter and SQLite. Unlike basic CRUD student record systems, PlacementIQ's defining innovation is "
            "its Smart Placement Readiness and Skill Gap Analysis engine. It calculates transparent rule-based scores (out of 100) "
            "across academics, technical skills, aptitude, communication, and projects. It compares each student's profile "
            "against active campus recruiter demands, automatically identifies high-priority missing skills, and explains "
            "exact eligibility reasons for every placement drive."
        )
        tk.Label(c1.inner, text=synopsis, font=Theme.FONT_BODY, fg=Theme.TEXT_LIGHT, bg=Theme.CARD_BG, wraplength=760, justify="left").pack(anchor="w", pady=(8, 10))

        # Badges row
        b_row = tk.Frame(c1.inner, bg=Theme.CARD_BG)
        b_row.pack(fill="x")
        PillBadge(b_row, text="100% Offline Python 3", status="Good Fit", width=150, height=24).pack(side="left", padx=4)
        PillBadge(b_row, text="MVC Architecture", status="Shortlisted", width=130, height=24).pack(side="left", padx=4)
        PillBadge(b_row, text="Salted SHA-256 Auth", status="Interview", width=140, height=24).pack(side="left", padx=4)
        PillBadge(b_row, text="SQLite Relational DB", status="Active", width=140, height=24).pack(side="left", padx=4)

        # 2. Technology Stack & MVC Architecture
        c2 = ModernCard(container, padding=18)
        c2.pack(fill="x", padx=20, pady=(0, 14))

        tk.Label(c2.inner, text="2. Technology Stack & MVC Design Pattern", font=Theme.FONT_TITLE_MED, fg=Theme.TEXT_WHITE, bg=Theme.CARD_BG).pack(anchor="w")

        tech_text = (
            "• Programming Language: Python 3.10+ (Standard Library only — zero fragile external pip dependencies)\n"
            "• GUI Framework: Tkinter & TTK with custom Canvas component engine (Dark Neon SaaS Aesthetic)\n"
            "• Database: SQLite3 with foreign keys enabled, cascading deletes, and ACID transactions\n"
            "• Security: Salted password hashing via hashlib.sha256 and secrets token generation\n\n"
            "Architecture Flow (Model-View-Controller):\n"
            "• Models (models/): Encapsulate data schemas and business rules (User, Student, Company, Drive, Application, ReadinessEngine).\n"
            "• Views (views/): Presentation layer rendering screens, cards, charts, and handling user inputs.\n"
            "• Controllers (controllers/): Coordinate actions, validate inputs, interact with models, and return data to views.\n"
            "• Database Manager (database/db_manager.py): Singleton connection manager, schema migrations, and demo data seeder."
        )
        tk.Label(c2.inner, text=tech_text, font=Theme.FONT_BODY, fg=Theme.TEXT_LIGHT, bg=Theme.CARD_BG, wraplength=760, justify="left").pack(anchor="w", pady=(8, 0))

        # 3. Viva Evaluation Quick Q&A Card
        c3 = ModernCard(container, padding=18)
        c3.pack(fill="x", padx=20, pady=(0, 20))

        tk.Label(c3.inner, text="3. Key Viva Questions & Explanations for APP Examiners", font=Theme.FONT_TITLE_MED, fg=Theme.TEXT_WHITE, bg=Theme.CARD_BG).pack(anchor="w", pady=(0, 10))

        qa_list = [
            (
                "Q1: How is the Smart Readiness Score calculated?",
                "Answer: It uses a transparent 100-point formula: Academics (25 pts based on CGPA/10), Technical Skills (25 pts based on breadth + market alignment with active campus drives), Aptitude (20 pts), Communication & Soft Skills (15 pts), and Practical Projects & Certifications (15 pts). It is completely deterministic and explainable without black-box AI."
            ),
            (
                "Q2: How does the Skill Gap Analysis work?",
                "Answer: The system dynamically queries all active placement drives, aggregates required skills, and compares them against the student's technical skills. Missing skills are ranked by market demand frequency, and targeted learning recommendations are generated."
            ),
            (
                "Q3: How is duplicate application prevention enforced?",
                "Answer: Enforced at both the database level via a UNIQUE(student_id, drive_id) constraint in SQLite and at the controller level before database execution."
            ),
            (
                "Q4: How are passwords stored securely?",
                "Answer: Passwords are never stored in plain text. A cryptographic 32-character hexadecimal salt is generated using secrets.token_hex(16), combined with the password, and hashed using SHA-256. Verification uses constant-time comparison (secrets.compare_digest) to prevent timing attacks."
            ),
            (
                "Q5: Why use Tkinter Canvas components instead of default Tkinter widgets?",
                "Answer: Standard Tkinter widgets look dated and lack modern SaaS visual hierarchy. By creating custom Canvas-rendered widgets (ModernCard, GradientBanner, ConcentricGauge, InteractiveLineChart), PlacementIQ achieves a stunning, modern dark neon UI while remaining 100% portable and dependency-free."
            )
        ]

        for q, a in qa_list:
            box = tk.Frame(c3.inner, bg=Theme.CARD_BG_ALT, bd=1, relief="solid")
            box.pack(fill="x", pady=4, ipady=6, ipadx=8)
            tk.Label(box, text=q, font=Theme.FONT_SMALL_BOLD, fg=Theme.ACCENT_PINK, bg=Theme.CARD_BG_ALT).pack(anchor="w")
            tk.Label(box, text=a, font=Theme.FONT_TINY, fg=Theme.TEXT_LIGHT, bg=Theme.CARD_BG_ALT, wraplength=730, justify="left").pack(anchor="w", pady=(2, 0))
