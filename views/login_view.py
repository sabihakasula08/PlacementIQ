"""
Login and Registration View for PlacementIQ
Provides a futuristic dark SaaS login card with quick demo fill buttons,
show/hide password toggle, and full vertical scrolling on any laptop or desktop resolution.
"""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Optional
from utils.theme import Theme
from utils.constants import DEPARTMENTS, ACADEMIC_YEARS, ROLE_ADMIN, ROLE_STUDENT
from utils.components import ModernCard, NeonButton, SegmentedToggle, ScrollableFrame
from controllers.auth_controller import AuthController

class LoginView(tk.Frame):
    def __init__(self, parent, on_login_success: Callable):
        super().__init__(parent, bg=Theme.BG_DARK)
        self.on_login_success = on_login_success
        self.auth_controller = AuthController()

        self._build_ui()

    def _build_ui(self):
        # 1. Full page scrollable container so users can ALWAYS scroll on smaller screens or high scaling
        self.scroll = ScrollableFrame(self, bg=Theme.BG_DARK)
        self.scroll.pack(fill="both", expand=True)
        container = self.scroll.scrollable_content

        # Outer centering frame packed with vertical breathing room
        self.center_wrapper = tk.Frame(container, bg=Theme.BG_DARK)
        self.center_wrapper.pack(fill="x", expand=True, pady=(20, 30))

        self.center_box = tk.Frame(self.center_wrapper, bg=Theme.BG_DARK)
        self.center_box.pack(anchor="center")

        # 2. Top Brand Header
        brand_frame = tk.Frame(self.center_box, bg=Theme.BG_DARK)
        brand_frame.pack(pady=(0, 16))

        # Brand Icon + Text
        canvas_icon = tk.Canvas(brand_frame, width=42, height=42, bg=Theme.BG_DARK, highlightthickness=0)
        canvas_icon.pack(side="left", padx=(0, 12))
        canvas_icon.create_oval(2, 2, 40, 40, fill=Theme.ACCENT_PINK, outline=Theme.GRADIENT_HERO_START, width=2)
        canvas_icon.create_text(21, 21, text="IQ", font=("Segoe UI", 13, "bold"), fill=Theme.TEXT_WHITE)

        title_box = tk.Frame(brand_frame, bg=Theme.BG_DARK)
        title_box.pack(side="left")
        tk.Label(
            title_box,
            text="PLACEMENT IQ",
            font=("Segoe UI", 20, "bold"),
            fg=Theme.TEXT_WHITE,
            bg=Theme.BG_DARK
        ).pack(anchor="w")
        tk.Label(
            title_box,
            text="Smart Campus Placement Management System",
            font=Theme.FONT_SMALL,
            fg=Theme.ACCENT_LAVENDER,
            bg=Theme.BG_DARK
        ).pack(anchor="w")

        # 3. Main Login Card Container
        self.card_wrapper = tk.Frame(self.center_box, bg=Theme.BG_DARK, width=500)
        self.card_wrapper.pack()

        self.card = ModernCard(self.card_wrapper, padding=22, width=480, height=430)
        self.card.pack(fill="x", expand=True)

        # Tab Segmented Switch: [Sign In] [New Student Registration]
        self.mode_toggle = SegmentedToggle(
            self.card.inner,
            options=["Sign In", "New Student Registration"],
            default_index=0,
            on_change=self._on_mode_change,
            height=34,
            pill_width=175
        )
        self.mode_toggle.pack(pady=(0, 16))

        # Dynamic Content Container
        self.form_container = tk.Frame(self.card.inner, bg=Theme.CARD_BG)
        self.form_container.pack(fill="both", expand=True)

        self._show_login_form()

        # Ensure mousewheel scrolling works seamlessly across all child widgets
        self.scroll.bind_mousewheel(self)

    def _on_mode_change(self, mode: str):
        for child in self.form_container.winfo_children():
            child.destroy()
        if mode == "Sign In":
            self.card.set_card_height(430)
            self._show_login_form()
        else:
            self.card.set_card_height(740)
            self._show_register_form()
        self.scroll.bind_mousewheel(self)
        self.after(50, lambda: self.scroll.canvas.configure(scrollregion=self.scroll.canvas.bbox("all")))

    # ---------------- LOGIN FORM ----------------
    def _show_login_form(self):
        f = self.form_container

        tk.Label(
            f, text="Welcome Back", font=Theme.FONT_TITLE_LARGE,
            fg=Theme.TEXT_WHITE, bg=Theme.CARD_BG
        ).pack(anchor="w", pady=(0, 2))

        tk.Label(
            f, text="Sign in to your student portal or coordinator dashboard",
            font=Theme.FONT_SMALL, fg=Theme.TEXT_MUTED, bg=Theme.CARD_BG
        ).pack(anchor="w", pady=(0, 14))

        # Username field
        tk.Label(f, text="USERNAME", font=Theme.FONT_TINY, fg=Theme.TEXT_MUTED, bg=Theme.CARD_BG).pack(anchor="w")
        self.ent_username = tk.Entry(
            f, font=Theme.FONT_BODY, bg=Theme.INPUT_BG, fg=Theme.TEXT_LIGHT,
            insertbackground=Theme.ACCENT_PINK, bd=1, relief="solid", highlightthickness=1,
            highlightcolor=Theme.ACCENT_PINK, highlightbackground=Theme.INPUT_BORDER
        )
        self.ent_username.pack(fill="x", ipady=6, pady=(3, 12))
        self.ent_username.bind("<Return>", lambda e: self.ent_password.focus_set())

        # Password field with Show/Hide toggle button
        tk.Label(f, text="PASSWORD", font=Theme.FONT_TINY, fg=Theme.TEXT_MUTED, bg=Theme.CARD_BG).pack(anchor="w")
        
        pwd_row = tk.Frame(f, bg=Theme.INPUT_BG, bd=1, relief="solid", highlightthickness=1,
                           highlightcolor=Theme.ACCENT_PINK, highlightbackground=Theme.INPUT_BORDER)
        pwd_row.pack(fill="x", pady=(3, 16))

        self.pwd_hidden = True
        self.ent_password = tk.Entry(
            pwd_row, font=Theme.FONT_BODY, bg=Theme.INPUT_BG, fg=Theme.TEXT_LIGHT,
            insertbackground=Theme.ACCENT_PINK, show="•", bd=0, highlightthickness=0
        )
        self.ent_password.pack(side="left", fill="x", expand=True, ipady=6, padx=(8, 4))
        self.ent_password.bind("<Return>", lambda e: self._handle_login())

        self.btn_toggle_pwd = tk.Button(
            pwd_row, text="👁", font=("Segoe UI", 10),
            bg=Theme.INPUT_BG, fg=Theme.TEXT_MUTED, activebackground=Theme.INPUT_BG,
            activeforeground=Theme.ACCENT_PINK, bd=0, relief="flat", cursor="hand2",
            command=self._toggle_pwd_visibility
        )
        self.btn_toggle_pwd.pack(side="right", padx=6)

        # Sign In Button
        NeonButton(
            f, text="Sign In to Portal  →",
            command=self._handle_login,
            style="primary",
            width=380,
            height=38
        ).pack(fill="x", pady=(0, 14))

        # Quick Demo Login Section
        demo_box = tk.LabelFrame(
            f, text=" ⚡ Quick Demo Logins (1-Click Viva Demo) ",
            font=Theme.FONT_TINY, fg=Theme.TEXT_SUBTLE, bg=Theme.CARD_BG,
            bd=1, relief="solid"
        )
        demo_box.pack(fill="x", pady=(4, 6))

        demo_btns = tk.Frame(demo_box, bg=Theme.CARD_BG)
        demo_btns.pack(fill="x", padx=6, pady=6)
        demo_btns.columnconfigure(0, weight=1)
        demo_btns.columnconfigure(1, weight=1)
        demo_btns.columnconfigure(2, weight=1)

        NeonButton(
            demo_btns, text="👑 Admin Demo",
            command=lambda: self._fill_demo("admin", "admin123"),
            style="secondary", width=110, height=28, font=Theme.FONT_SMALL
        ).grid(row=0, column=0, padx=2, sticky="ew")

        NeonButton(
            demo_btns, text="🎓 Rahul (CS 8.75)",
            command=lambda: self._fill_demo("student1", "password123"),
            style="secondary", width=120, height=28, font=Theme.FONT_SMALL
        ).grid(row=0, column=1, padx=2, sticky="ew")

        NeonButton(
            demo_btns, text="🎓 Priya (IT 7.40)",
            command=lambda: self._fill_demo("student2", "password123"),
            style="secondary", width=110, height=28, font=Theme.FONT_SMALL
        ).grid(row=0, column=2, padx=2, sticky="ew")

    def _toggle_pwd_visibility(self):
        if self.pwd_hidden:
            self.ent_password.configure(show="")
            self.btn_toggle_pwd.configure(text="🔒")
            self.pwd_hidden = False
        else:
            self.ent_password.configure(show="•")
            self.btn_toggle_pwd.configure(text="👁")
            self.pwd_hidden = True

    def _fill_demo(self, u: str, p: str):
        self.ent_username.delete(0, tk.END)
        self.ent_username.insert(0, u)
        self.ent_password.delete(0, tk.END)
        self.ent_password.insert(0, p)
        self._handle_login()

    def _handle_login(self):
        u = self.ent_username.get().strip()
        p = self.ent_password.get()
        ok, msg, user = self.auth_controller.login(u, p)
        if ok and user:
            self.on_login_success(user)
        else:
            messagebox.showerror("Authentication Failed", msg)

    # ---------------- REGISTER FORM ----------------
    def _show_register_form(self):
        f = self.form_container

        tk.Label(
            f, text="Student Registration", font=Theme.FONT_TITLE_MED,
            fg=Theme.TEXT_WHITE, bg=Theme.CARD_BG
        ).pack(anchor="w", pady=(0, 2))

        tk.Label(
            f, text="Create a verified student placement profile",
            font=Theme.FONT_SMALL, fg=Theme.TEXT_MUTED, bg=Theme.CARD_BG
        ).pack(anchor="w", pady=(0, 10))

        def make_entry(lbl_text, show=None):
            tk.Label(f, text=lbl_text, font=Theme.FONT_TINY, fg=Theme.TEXT_MUTED, bg=Theme.CARD_BG).pack(anchor="w", pady=(3, 1))
            ent = tk.Entry(
                f, font=Theme.FONT_SMALL, bg=Theme.INPUT_BG, fg=Theme.TEXT_LIGHT,
                insertbackground=Theme.ACCENT_PINK, show=show, bd=1, relief="solid",
                highlightthickness=1, highlightcolor=Theme.ACCENT_PINK, highlightbackground=Theme.INPUT_BORDER
            )
            ent.pack(fill="x", ipady=4, pady=(0, 4))
            return ent

        self.reg_fullname = make_entry("FULL NAME")
        self.reg_username = make_entry("USERNAME")
        self.reg_email = make_entry("CAMPUS EMAIL")
        self.reg_password = make_entry("PASSWORD", show="•")
        self.reg_regno = make_entry("REGISTER NO. (e.g. 22CS105)")
        self.reg_cgpa = make_entry("CGPA (0.00 - 10.00)")

        # Department Dropdown
        tk.Label(f, text="DEPARTMENT", font=Theme.FONT_TINY, fg=Theme.TEXT_MUTED, bg=Theme.CARD_BG).pack(anchor="w", pady=(3, 1))
        self.reg_dept_var = tk.StringVar(value=DEPARTMENTS[0])
        dept_menu = ttk.Combobox(f, textvariable=self.reg_dept_var, values=DEPARTMENTS, state="readonly")
        dept_menu.pack(fill="x", ipady=3, pady=(0, 4))

        # Academic Year Dropdown
        tk.Label(f, text="ACADEMIC BATCH / YEAR", font=Theme.FONT_TINY, fg=Theme.TEXT_MUTED, bg=Theme.CARD_BG).pack(anchor="w", pady=(3, 1))
        self.reg_year_var = tk.StringVar(value=ACADEMIC_YEARS[0])
        year_menu = ttk.Combobox(f, textvariable=self.reg_year_var, values=ACADEMIC_YEARS, state="readonly")
        year_menu.pack(fill="x", ipady=3, pady=(0, 4))

        self.reg_skills = make_entry("TECHNICAL SKILLS (comma-separated, e.g. Python, SQL, React)")
        self.reg_soft_skills = make_entry("SOFT SKILLS (e.g. Problem Solving, Communication)")

        NeonButton(
            f, text="Complete Registration  ✓",
            command=self._handle_register,
            style="primary", width=380, height=36
        ).pack(fill="x", pady=(10, 8))

    def _handle_register(self):
        full_name = self.reg_fullname.get().strip()
        username = self.reg_username.get().strip()
        email = self.reg_email.get().strip()
        password = self.reg_password.get()
        reg_no = self.reg_regno.get().strip().upper()
        cgpa_str = self.reg_cgpa.get().strip()
        dept = self.reg_dept_var.get()
        year = self.reg_year_var.get()
        skills = [s.strip() for s in self.reg_skills.get().split(",") if s.strip()]
        soft_skills = [s.strip() for s in self.reg_soft_skills.get().split(",") if s.strip()]

        try:
            cgpa = float(cgpa_str)
        except ValueError:
            messagebox.showerror("Input Error", "Please enter a valid numeric CGPA (e.g. 8.25)")
            return

        ok, msg, user = self.auth_controller.register_student(
            username=username,
            password=password,
            full_name=full_name,
            email=email,
            register_no=reg_no,
            department=dept,
            academic_year=year,
            cgpa=cgpa,
            technical_skills=skills,
            soft_skills=soft_skills
        )

        if ok and user:
            messagebox.showinfo("Success", "Account created successfully! Logging you in now...")
            self.auth_controller.set_current_user(user)
            self.on_login_success(user)
        else:
            messagebox.showerror("Registration Error", msg)
