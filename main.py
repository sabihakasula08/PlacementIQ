"""
PlacementIQ – Smart Campus Placement Management System
Main Entry Point
"""
import sys
import os
import tkinter as tk
from tkinter import ttk

# Ensure project root is in python path
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from utils.theme import Theme
from utils.constants import APP_NAME, APP_SUBTITLE, APP_VERSION
from database.db_manager import DBManager
from models.user_model import User
from controllers.auth_controller import AuthController
from views.login_view import LoginView
from views.main_window import MainWindow

class PlacementIQApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title(f"{APP_NAME} – {APP_SUBTITLE} v{APP_VERSION}")
        self.root.minsize(980, 580)
        self.root.configure(bg=Theme.BG_DARK)

        # Center window on screen adaptively
        self._center_window(1240, 740)

        # Configure ttk dark styling
        self._configure_styles()

        # Initialize SQLite database
        self.db = DBManager.get_instance()

        self.current_user: User = None
        self.current_container: tk.Widget = None

        # Start with Login screen
        self.show_login()

    def _center_window(self, width: int, height: int):
        self.root.update_idletasks()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        target_w = min(width, max(980, screen_width - 60))
        target_h = min(height, max(580, screen_height - 90))
        x = max(0, (screen_width - target_w) // 2)
        y = max(0, (screen_height - target_h) // 2)
        self.root.geometry(f"{target_w}x{target_h}+{x}+{y}")
        y = max(0, (screen_height - height) // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def _configure_styles(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except Exception:
            pass

        # Dark Combobox styling
        style.configure(
            "TCombobox",
            fieldbackground=Theme.INPUT_BG,
            background=Theme.CARD_BG_ALT,
            foreground=Theme.TEXT_WHITE,
            arrowcolor=Theme.ACCENT_PINK,
            darkcolor=Theme.INPUT_BORDER,
            lightcolor=Theme.INPUT_BORDER,
            bordercolor=Theme.INPUT_BORDER,
            insertcolor=Theme.ACCENT_PINK
        )
        style.map(
            "TCombobox",
            fieldbackground=[("readonly", Theme.INPUT_BG)],
            foreground=[("readonly", Theme.TEXT_WHITE)],
            selectbackground=[("readonly", Theme.INPUT_BG)],
            selectforeground=[("readonly", Theme.TEXT_WHITE)]
        )

        # Dark Scrollbar styling
        style.configure(
            "Vertical.TScrollbar",
            background=Theme.CARD_BG_ALT,
            troughcolor=Theme.BG_DARK,
            bordercolor=Theme.BG_DARK,
            arrowcolor=Theme.TEXT_MUTED
        )

    def show_login(self):
        if self.current_container:
            self.current_container.destroy()

        self.login_view = LoginView(self.root, on_login_success=self.on_login_success)
        self.login_view.pack(fill="both", expand=True)
        self.current_container = self.login_view

    def on_login_success(self, user: User):
        self.current_user = user
        if self.current_container:
            self.current_container.destroy()

        self.main_window = MainWindow(self.root, current_user=user, on_logout=self.on_logout)
        self.main_window.pack(fill="both", expand=True)
        self.current_container = self.main_window

    def on_logout(self):
        AuthController.logout()
        self.current_user = None
        self.show_login()


def main():
    root = tk.Tk()
    app = PlacementIQApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
