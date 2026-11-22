"""
Admin Controller for PlacementIQ
Handles company management, drive campaigns, student oversight, and pipeline progress.
"""
from typing import Optional, List, Dict, Any, Tuple
from database.db_manager import DBManager
from models.company_model import Company
from models.drive_model import PlacementDrive
from models.student_model import Student
from models.application_model import Application
from utils.validator import Validator

class AdminController:
    def __init__(self, db_manager: Optional[DBManager] = None):
        self.db = db_manager or DBManager.get_instance()

    # ---------------- Company Management ----------------
    def get_all_companies(self) -> List[Company]:
        return Company.get_all(self.db)

    def add_company(
        self,
        name: str,
        industry: str,
        website: str = "",
        contact_email: str = "",
        location: str = "",
        description: str = ""
    ) -> Tuple[bool, str, Optional[Company]]:
        if not name or len(name.strip()) < 2:
            return False, "Company name cannot be empty.", None
        if not industry or len(industry.strip()) < 2:
            return False, "Industry cannot be empty.", None

        try:
            comp = Company.create(name, industry, website, contact_email, location, description, self.db)
            return True, f"Company '{name}' registered successfully!", comp
        except Exception as e:
            return False, f"Failed to add company: {str(e)}", None

    def update_company(
        self,
        company_id: int,
        name: str,
        industry: str,
        website: str = "",
        contact_email: str = "",
        location: str = "",
        description: str = ""
    ) -> Tuple[bool, str]:
        comp = Company.get_by_id(company_id, self.db)
        if not comp:
            return False, "Company not found."
        try:
            comp.update(name, industry, website, contact_email, location, description, self.db)
            return True, "Company profile updated successfully!"
        except Exception as e:
            return False, f"Update failed: {str(e)}"

    def delete_company(self, company_id: int) -> Tuple[bool, str]:
        try:
            success = Company.delete(company_id, self.db)
            if success:
                return True, "Company and associated placement drives deleted."
            return False, "Company not found."
        except Exception as e:
            return False, f"Failed to delete company: {str(e)}"

    # ---------------- Drive Management ----------------
    def get_all_drives(self) -> List[PlacementDrive]:
        return PlacementDrive.get_all(self.db)

    def add_drive(
        self,
        company_id: int,
        title: str,
        job_role: str,
        package_lpa: float,
        min_cgpa: float,
        eligible_departments: List[str],
        eligible_years: List[str],
        required_skills: List[str],
        application_deadline: str,
        drive_date: str = "",
        venue_or_link: str = "",
        status: str = "Active"
    ) -> Tuple[bool, str, Optional[PlacementDrive]]:
        if not title or len(title.strip()) < 2:
            return False, "Drive title is required.", None
        if not job_role or len(job_role.strip()) < 2:
            return False, "Job role is required.", None

        ok, msg = Validator.is_valid_package(package_lpa)
        if not ok:
            return False, msg, None

        ok, msg = Validator.is_valid_cgpa(min_cgpa)
        if not ok:
            return False, msg, None

        ok, msg = Validator.is_valid_date(application_deadline)
        if not ok:
            return False, msg, None

        if not eligible_departments:
            return False, "Please specify at least one eligible department.", None
        if not eligible_years:
            return False, "Please specify at least one eligible batch year.", None
        if not required_skills:
            return False, "Please specify required skills.", None

        try:
            drive = PlacementDrive.create(
                company_id=company_id,
                title=title,
                job_role=job_role,
                package_lpa=float(package_lpa),
                min_cgpa=float(min_cgpa),
                eligible_departments=eligible_departments,
                eligible_years=eligible_years,
                required_skills=required_skills,
                application_deadline=application_deadline,
                drive_date=drive_date,
                venue_or_link=venue_or_link,
                status=status,
                db_manager=self.db
            )
            return True, "Placement drive published successfully!", drive
        except Exception as e:
            return False, f"Failed to create drive: {str(e)}", None

    def update_drive(
        self,
        drive_id: int,
        company_id: int,
        title: str,
        job_role: str,
        package_lpa: float,
        min_cgpa: float,
        eligible_departments: List[str],
        eligible_years: List[str],
        required_skills: List[str],
        application_deadline: str,
        drive_date: str = "",
        venue_or_link: str = "",
        status: str = "Active"
    ) -> Tuple[bool, str]:
        drive = PlacementDrive.get_by_id(drive_id, self.db)
        if not drive:
            return False, "Placement drive not found."

        try:
            drive.update(
                title=title,
                job_role=job_role,
                package_lpa=float(package_lpa),
                min_cgpa=float(min_cgpa),
                eligible_departments=eligible_departments,
                eligible_years=eligible_years,
                required_skills=required_skills,
                application_deadline=application_deadline,
                drive_date=drive_date,
                venue_or_link=venue_or_link,
                status=status,
                company_id=company_id,
                db_manager=self.db
            )
            return True, "Placement drive updated successfully!"
        except Exception as e:
            return False, f"Failed to update drive: {str(e)}"

    def delete_drive(self, drive_id: int) -> Tuple[bool, str]:
        try:
            success = PlacementDrive.delete(drive_id, self.db)
            if success:
                return True, "Placement drive deleted successfully."
            return False, "Drive not found."
        except Exception as e:
            return False, f"Failed to delete drive: {str(e)}"

    # ---------------- Application Pipeline ----------------
    def get_all_applications(self) -> List[Application]:
        return Application.get_all(self.db)

    def update_application_status(self, app_id: int, new_status: str, feedback: str = "") -> Tuple[bool, str]:
        success = Application.update_status(app_id, new_status, feedback, self.db)
        if success:
            return True, f"Application moved to '{new_status}' successfully!"
        return False, "Application record not found."

    # ---------------- Student Directory ----------------
    def get_all_students(self) -> List[Student]:
        return Student.get_all(self.db)
