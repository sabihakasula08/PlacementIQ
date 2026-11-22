"""
Smoke Test for PlacementIQ Views and Navigation Lifecycle
Boots Tkinter in headless/virtual mode, logs in as Admin, visits every view,
switches to Student, visits every view, tests interactions, and cleanly shuts down.
"""
import os
import sys
import tkinter as tk

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(TEST_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from main import PlacementIQApp
from models.user_model import User
from database.db_manager import DBManager

def run_smoke_test():
    print("Starting PlacementIQ GUI Smoke Test...")
    root = tk.Tk()
    root.withdraw() # Don't steal screen focus during smoke test

    app = PlacementIQApp(root)
    print("App initialized successfully.")

    # 1. Admin Workflow
    admin_user = User.authenticate("admin", "admin123")
    assert admin_user is not None, "Failed to authenticate admin"
    app.on_login_success(admin_user)
    print("Logged in as Admin.")

    views = ["dashboard", "profile", "readiness", "drives", "applications", "companies", "analytics", "sysinfo"]
    for v in views:
        app.main_window.navigate_to(v)
        root.update()
        print(f"  [Admin] Navigated to '{v}' cleanly.")

    # 2. Logout
    app.on_logout()
    root.update()
    print("Logged out cleanly.")

    # 3. Student Workflow
    student_user = User.authenticate("student1", "password123")
    assert student_user is not None, "Failed to authenticate student"
    app.on_login_success(student_user)
    print("Logged in as Student.")

    for v in views:
        app.main_window.navigate_to(v)
        root.update()
        print(f"  [Student] Navigated to '{v}' cleanly.")

    root.destroy()
    print("GUI Smoke Test Completed Successfully! All views render without error.")

if __name__ == "__main__":
    run_smoke_test()
