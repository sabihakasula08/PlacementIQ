"""
Automated Test Suite for PlacementIQ
Covers authentication, student registration, profile updates, company CRUD,
drive campaigns, smart eligibility checks, application lifecycle,
duplicate application prevention, and database persistence.
"""
import os
import sys
import unittest

# Ensure project root in sys.path
TEST_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(TEST_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from database.db_manager import DBManager
from models.user_model import User
from models.student_model import Student
from models.company_model import Company
from models.drive_model import PlacementDrive
from models.application_model import Application
from models.readiness_model import ReadinessEngine
from controllers.auth_controller import AuthController
from controllers.student_controller import StudentController
from controllers.admin_controller import AdminController
from controllers.analytics_controller import AnalyticsController
from utils.constants import ROLE_STUDENT, ROLE_ADMIN, STATUS_APPLIED, STATUS_SELECTED, STATUS_INTERVIEW

TEST_DB_PATH = os.path.join(TEST_DIR, "test_suite.db")


class TestPlacementIQ(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Remove old test DB if exists
        if os.path.exists(TEST_DB_PATH):
            os.remove(TEST_DB_PATH)
        cls.db = DBManager(TEST_DB_PATH)
        cls.auth_ctrl = AuthController()
        cls.student_ctrl = StudentController(cls.db)
        cls.admin_ctrl = AdminController(cls.db)
        cls.analytics_ctrl = AnalyticsController(cls.db)

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(TEST_DB_PATH):
            try:
                os.remove(TEST_DB_PATH)
            except Exception:
                pass

    def test_01_seed_and_auth(self):
        """Test default demo authentication for admin and student accounts."""
        # Admin login
        ok, msg, admin_user = self.auth_ctrl.login("admin", "admin123", self.db)
        self.assertTrue(ok)
        self.assertIsNotNone(admin_user)
        self.assertTrue(admin_user.is_admin)

        # Student login
        ok, msg, student_user = self.auth_ctrl.login("student1", "password123", self.db)
        self.assertTrue(ok)
        self.assertIsNotNone(student_user)
        self.assertTrue(student_user.is_student)

        # Invalid password
        ok, msg, fail_user = self.auth_ctrl.login("admin", "wrongpass", self.db)
        self.assertFalse(ok)
        self.assertIsNone(fail_user)

    def test_02_student_registration(self):
        """Test registration of a new student with validation and profile creation."""
        ok, msg, new_user = self.auth_ctrl.register_student(
            username="newstudent99",
            password="securepassword123",
            full_name="Deepak Joshi",
            email="deepak.joshi@campus.edu",
            register_no="22CS999",
            department="Computer Science & Engineering",
            academic_year="2022 - 2026 (3rd Year)",
            cgpa=8.40,
            technical_skills=["Python", "SQL", "Git & GitHub"],
            soft_skills=["Problem Solving", "Communication"],
            db_manager=self.db
        )
        self.assertTrue(ok, f"Registration failed: {msg}")
        self.assertIsNotNone(new_user)

        # Verify Student row
        student = self.student_ctrl.get_student_by_user_id(new_user.id)
        self.assertIsNotNone(student)
        self.assertEqual(student.register_no, "22CS999")
        self.assertEqual(student.cgpa, 8.40)
        self.assertIn("Python", student.technical_skills)

        # Verify duplicate register number rejection
        dup_ok, dup_msg, _ = self.auth_ctrl.register_student(
            username="different_user",
            password="password123",
            full_name="Another Person",
            email="another@campus.edu",
            register_no="22CS999", # Same register no!
            department="Information Technology",
            academic_year="2022 - 2026 (3rd Year)",
            cgpa=7.5,
            technical_skills=["Java"],
            soft_skills=["Team Collaboration"],
            db_manager=self.db
        )
        self.assertFalse(dup_ok)
        self.assertIn("already registered", dup_msg.lower())

    def test_03_profile_update(self):
        """Test updating student academic metrics, skills, and portfolio."""
        student = Student.get_by_reg_no("22CS999", self.db)
        self.assertIsNotNone(student)

        ok, msg = self.student_ctrl.update_profile(
            student=student,
            full_name="Deepak Joshi (Updated)",
            email="deepak.updated@campus.edu",
            department="Computer Science & Engineering",
            academic_year="2022 - 2026 (3rd Year)",
            cgpa=8.95,
            technical_skills=["Python", "SQL", "Docker", "FastAPI"],
            soft_skills=["Problem Solving", "Leadership"],
            projects_count=3,
            certifications_count=2,
            projects_description="Microservices with Docker and FastAPI",
            aptitude_score=88.0,
            communication_score=82.0,
            resume_path="C:/resumes/22CS999_Resume.pdf"
        )
        self.assertTrue(ok)

        # Re-fetch from DB to verify persistence
        reloaded = Student.get_by_reg_no("22CS999", self.db)
        self.assertEqual(reloaded.cgpa, 8.95)
        self.assertEqual(reloaded.full_name, "Deepak Joshi (Updated)")
        self.assertIn("Docker", reloaded.technical_skills)
        self.assertEqual(reloaded.projects_count, 3)

    def test_04_company_crud(self):
        """Test company creation, update, and deletion."""
        # Create
        ok, msg, comp = self.admin_ctrl.add_company(
            name="NVIDIA Corporation",
            industry="GPU & AI Computing",
            website="https://nvidia.com",
            contact_email="university-recruiting@nvidia.com",
            location="Bengaluru / Pune",
            description="World pioneer in GPU accelerated computing and AI superclusters."
        )
        self.assertTrue(ok)
        self.assertIsNotNone(comp)

        # Update
        ok, msg = self.admin_ctrl.update_company(
            company_id=comp.id,
            name="NVIDIA AI Systems",
            industry="Accelerated Computing",
            website="https://nvidia.com",
            contact_email="careers@nvidia.com",
            location="Bengaluru",
            description="Updated description."
        )
        self.assertTrue(ok)

        reloaded = Company.get_by_id(comp.id, self.db)
        self.assertEqual(reloaded.name, "NVIDIA AI Systems")

        # Delete
        del_ok, del_msg = self.admin_ctrl.delete_company(comp.id)
        self.assertTrue(del_ok)
        self.assertIsNone(Company.get_by_id(comp.id, self.db))

    def test_05_placement_drive_crud(self):
        """Test creating, querying, and updating a placement drive."""
        comps = self.admin_ctrl.get_all_companies()
        self.assertTrue(len(comps) > 0)
        target_company = comps[0]

        ok, msg, drive = self.admin_ctrl.add_drive(
            company_id=target_company.id,
            title="Backend Systems Engineer",
            job_role="Software Engineer - Core Services",
            package_lpa=16.5,
            min_cgpa=7.5,
            eligible_departments=["Computer Science & Engineering", "Information Technology"],
            eligible_years=["2022 - 2026 (3rd Year)", "2021 - 2025 (Final Year / Passing Out)"],
            required_skills=["Python", "SQL", "Docker"],
            application_deadline="2026-12-15",
            drive_date="2026-12-20",
            venue_or_link="Auditorium Lab 1",
            status="Active"
        )
        self.assertTrue(ok)
        self.assertIsNotNone(drive)
        self.assertEqual(drive.package_lpa, 16.5)

        # Update drive
        up_ok, up_msg = self.admin_ctrl.update_drive(
            drive_id=drive.id,
            company_id=target_company.id,
            title="Backend Systems Engineer (Senior)",
            job_role="Senior Core Engineer",
            package_lpa=19.0,
            min_cgpa=8.0,
            eligible_departments=["Computer Science & Engineering"],
            eligible_years=["2022 - 2026 (3rd Year)"],
            required_skills=["Python", "SQL", "Docker", "Kubernetes"],
            application_deadline="2026-12-25"
        )
        self.assertTrue(up_ok)

        reloaded_drive = PlacementDrive.get_by_id(drive.id, self.db)
        self.assertEqual(reloaded_drive.package_lpa, 19.0)
        self.assertEqual(reloaded_drive.min_cgpa, 8.0)

    def test_06_smart_readiness_and_skill_gap(self):
        """Test rule-based scoring formula and missing-skill gap engine."""
        student = Student.get_by_reg_no("22CS999", self.db)
        self.assertIsNotNone(student)

        res = ReadinessEngine.calculate_readiness(student, self.db)

        # Verify transparent score boundary (0 to 100)
        self.assertGreaterEqual(res.overall_score, 0.0)
        self.assertLessEqual(res.overall_score, 100.0)

        # Verify category weights sum to 100
        self.assertEqual(sum(res.category_max.values()), 100)

        # Verify individual category scores are bounded by category max
        self.assertLessEqual(res.academic_score, res.category_max["academics"])
        self.assertLessEqual(res.technical_score, res.category_max["technical_skills"])
        self.assertLessEqual(res.aptitude_score, res.category_max["aptitude"])
        self.assertLessEqual(res.communication_score, res.category_max["communication"])
        self.assertLessEqual(res.project_score, res.category_max["projects"])

        # Verify missing skills list is populated from active placement drives
        self.assertIsInstance(res.missing_skills, list)
        self.assertIsInstance(res.recommendations, list)
        self.assertGreater(len(res.recommendations), 0)

    def test_07_automated_eligibility_checking(self):
        """Test comparing student against placement drive criteria."""
        student = Student.get_by_reg_no("22CS999", self.db) # CGPA 8.95, CS, 3rd Year

        drives = PlacementDrive.get_active(self.db)
        self.assertTrue(len(drives) > 0)

        # Find drive where student qualifies
        for drive in drives:
            elig = ReadinessEngine.check_drive_eligibility(student, drive)
            self.assertIsInstance(elig.is_eligible, bool)
            self.assertIsInstance(elig.satisfied_criteria, list)
            self.assertIsInstance(elig.missing_criteria, list)

            # Verification of criteria consistency
            if student.cgpa >= drive.min_cgpa:
                self.assertTrue(elig.cgpa_passed)
            else:
                self.assertFalse(elig.cgpa_passed)
                self.assertFalse(elig.is_eligible)

    def test_08_application_submission_and_duplicate_prevention(self):
        """Test student application lifecycle and duplicate prevention constraint."""
        student = Student.get_by_reg_no("22CS999", self.db)
        drives = PlacementDrive.get_active(self.db)
        drive_to_apply = drives[0]

        # First application -> Should succeed
        ok, msg, app = Application.apply(student.id, drive_to_apply.id, self.db)
        self.assertTrue(ok)
        self.assertIsNotNone(app)
        self.assertEqual(app.status, STATUS_APPLIED)

        # Duplicate application -> MUST fail
        dup_ok, dup_msg, dup_app = Application.apply(student.id, drive_to_apply.id, self.db)
        self.assertFalse(dup_ok)
        self.assertIn("already submitted", dup_msg.lower())
        self.assertIsNone(dup_app)

    def test_09_application_status_update(self):
        """Test advancing an application through recruitment pipeline stages."""
        student = Student.get_by_reg_no("22CS999", self.db)
        apps = Application.get_by_student(student.id, self.db)
        self.assertTrue(len(apps) > 0)
        target_app = apps[0]

        # Update to Interview
        ok = Application.update_status(target_app.id, STATUS_INTERVIEW, "Scheduled for Technical Round 2", self.db)
        self.assertTrue(ok)

        # Reload and verify
        reloaded = Application.get_by_id(target_app.id, self.db)
        self.assertEqual(reloaded.status, STATUS_INTERVIEW)
        self.assertIn("Round 2", reloaded.feedback)

        # Update to Selected
        ok = Application.update_status(target_app.id, STATUS_SELECTED, "Offered position!", self.db)
        self.assertTrue(ok)
        reloaded_final = Application.get_by_id(target_app.id, self.db)
        self.assertEqual(reloaded_final.status, STATUS_SELECTED)

    def test_10_database_persistence(self):
        """Simulate closing DB and opening a new connection to verify persistent storage."""
        # Open completely fresh instance pointing to same file
        fresh_db = DBManager(TEST_DB_PATH)
        with fresh_db.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM users;")
            users_count = cur.fetchone()[0]
            self.assertGreaterEqual(users_count, 6)

            cur.execute("SELECT COUNT(*) FROM students;")
            students_count = cur.fetchone()[0]
            self.assertGreaterEqual(students_count, 5)

            cur.execute("SELECT COUNT(*) FROM placement_drives;")
            drives_count = cur.fetchone()[0]
            self.assertGreaterEqual(drives_count, 6)

            cur.execute("SELECT COUNT(*) FROM applications;")
            apps_count = cur.fetchone()[0]
            self.assertGreaterEqual(apps_count, 8)


if __name__ == "__main__":
    unittest.main()
