"""
Student Controller for PlacementIQ
Bridges student views to student profile updates, readiness calculations,
drive eligibility status checks, and job applications.
"""
from typing import Optional, List, Dict, Any, Tuple
from database.db_manager import DBManager
from models.student_model import Student
from models.drive_model import PlacementDrive
from models.application_model import Application
from models.readiness_model import ReadinessEngine, ReadinessResult, EligibilityResult
from utils.validator import Validator

class StudentController:
    def __init__(self, db_manager: Optional[DBManager] = None):
        self.db = db_manager or DBManager.get_instance()

    def get_student_by_user_id(self, user_id: int) -> Optional[Student]:
        return Student.get_by_user_id(user_id, self.db)

    def get_student_by_id(self, student_id: int) -> Optional[Student]:
        return Student.get_by_id(student_id, self.db)

    def update_profile(
        self,
        student: Student,
        full_name: str,
        email: str,
        department: str,
        academic_year: str,
        cgpa: float,
        technical_skills: List[str],
        soft_skills: List[str],
        projects_count: int,
        certifications_count: int,
        projects_description: str,
        aptitude_score: float,
        communication_score: float,
        resume_path: str = ""
    ) -> Tuple[bool, str]:
        if not full_name or len(full_name.strip()) < 2:
            return False, "Full name cannot be empty."

        if not Validator.is_valid_email(email):
            return False, "Please enter a valid email address."

        ok, msg = Validator.is_valid_cgpa(cgpa)
        if not ok:
            return False, msg

        try:
            student.update(
                full_name=full_name,
                email=email,
                department=department,
                academic_year=academic_year,
                cgpa=cgpa,
                technical_skills=technical_skills,
                soft_skills=soft_skills,
                projects_count=projects_count,
                certifications_count=certifications_count,
                projects_description=projects_description,
                aptitude_score=aptitude_score,
                communication_score=communication_score,
                resume_path=resume_path,
                db_manager=self.db
            )
            return True, "Profile updated successfully!"
        except Exception as e:
            return False, f"Failed to update profile: {str(e)}"

    def get_readiness_analysis(self, student: Student) -> ReadinessResult:
        return ReadinessEngine.calculate_readiness(student, self.db)

    def get_drives_with_eligibility(self, student: Student) -> List[Tuple[PlacementDrive, EligibilityResult, bool]]:
        """
        Returns list of tuples: (PlacementDrive, EligibilityResult, has_already_applied)
        Sorted so eligible drives appear first, followed by deadline.
        """
        drives = PlacementDrive.get_active(self.db)
        results = []
        for drive in drives:
            eligibility = ReadinessEngine.check_drive_eligibility(student, drive)
            has_applied = Application.has_applied(student.id, drive.id, self.db)
            results.append((drive, eligibility, has_applied))

        # Sort: eligible first, then already applied, then deadline
        results.sort(key=lambda item: (not item[1].is_eligible, item[2], item[0].application_deadline))
        return results

    def apply_for_drive(self, student_id: int, drive_id: int) -> Tuple[bool, str]:
        # Pre-check drive exists and active
        drive = PlacementDrive.get_by_id(drive_id, self.db)
        if not drive:
            return False, "Placement drive not found."
        if drive.status != "Active":
            return False, "This placement drive is closed for applications."

        # Check eligibility
        student = Student.get_by_id(student_id, self.db)
        if not student:
            return False, "Student record not found."

        eligibility = ReadinessEngine.check_drive_eligibility(student, drive)
        if not eligibility.is_eligible:
            reasons = "; ".join(eligibility.missing_criteria)
            return False, f"You are not eligible for this drive: {reasons}"

        success, msg, app = Application.apply(student_id, drive_id, self.db)
        return success, msg

    def get_student_applications(self, student_id: int) -> List[Application]:
        return Application.get_by_student(student_id, self.db)
