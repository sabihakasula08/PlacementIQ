"""
Placement Drive Model for PlacementIQ
Handles recruitment drive campaigns, role parameters, criteria, and deadlines.
"""
from typing import Optional, List, Dict, Any
from database.db_manager import DBManager

class PlacementDrive:
    def __init__(
        self,
        id: int,
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
        status: str = "Active",
        company_name: str = "",
        applicant_count: int = 0,
        created_at: str = ""
    ):
        self.id = id
        self.company_id = company_id
        self.title = title
        self.job_role = job_role
        self.package_lpa = float(package_lpa)
        self.min_cgpa = float(min_cgpa)
        self.eligible_departments = [d.strip() for d in eligible_departments if d.strip()]
        self.eligible_years = [y.strip() for y in eligible_years if y.strip()]
        self.required_skills = [s.strip() for s in required_skills if s.strip()]
        self.application_deadline = application_deadline
        self.drive_date = drive_date
        self.venue_or_link = venue_or_link
        self.status = status
        self.company_name = company_name
        self.applicant_count = applicant_count
        self.created_at = created_at

    @property
    def depts_str(self) -> str:
        return ", ".join(self.eligible_departments)

    @property
    def years_str(self) -> str:
        return ", ".join(self.eligible_years)

    @property
    def skills_str(self) -> str:
        return ", ".join(self.required_skills)

    @classmethod
    def from_row(cls, row: Any) -> "PlacementDrive":
        depts_raw = row["eligible_departments"] or ""
        years_raw = row["eligible_years"] or ""
        skills_raw = row["required_skills"] or ""

        depts = [d.strip() for d in depts_raw.split(",") if d.strip()]
        years = [y.strip() for y in years_raw.split(",") if y.strip()]
        skills = [s.strip() for s in skills_raw.split(",") if s.strip()]

        company_name = row["company_name"] if "company_name" in row.keys() else ""
        applicant_count = row["applicant_count"] if "applicant_count" in row.keys() else 0

        return cls(
            id=row["id"],
            company_id=row["company_id"],
            title=row["title"],
            job_role=row["job_role"],
            package_lpa=row["package_lpa"],
            min_cgpa=row["min_cgpa"],
            eligible_departments=depts,
            eligible_years=years,
            required_skills=skills,
            application_deadline=row["application_deadline"],
            drive_date=row["drive_date"] or "",
            venue_or_link=row["venue_or_link"] or "",
            status=row["status"] or "Active",
            company_name=company_name,
            applicant_count=applicant_count,
            created_at=str(row["created_at"]) if "created_at" in row.keys() else ""
        )

    @classmethod
    def get_all(cls, db_manager: Optional[DBManager] = None) -> List["PlacementDrive"]:
        db = db_manager or DBManager.get_instance()
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT pd.*, c.name AS company_name,
                   (SELECT COUNT(*) FROM applications a WHERE a.drive_id = pd.id) AS applicant_count
            FROM placement_drives pd
            JOIN companies c ON pd.company_id = c.id
            ORDER BY pd.created_at DESC;
            """)
            return [cls.from_row(row) for row in cursor.fetchall()]

    @classmethod
    def get_active(cls, db_manager: Optional[DBManager] = None) -> List["PlacementDrive"]:
        db = db_manager or DBManager.get_instance()
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT pd.*, c.name AS company_name,
                   (SELECT COUNT(*) FROM applications a WHERE a.drive_id = pd.id) AS applicant_count
            FROM placement_drives pd
            JOIN companies c ON pd.company_id = c.id
            WHERE pd.status = 'Active'
            ORDER BY pd.application_deadline ASC;
            """)
            return [cls.from_row(row) for row in cursor.fetchall()]

    @classmethod
    def get_by_id(cls, drive_id: int, db_manager: Optional[DBManager] = None) -> Optional["PlacementDrive"]:
        db = db_manager or DBManager.get_instance()
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT pd.*, c.name AS company_name,
                   (SELECT COUNT(*) FROM applications a WHERE a.drive_id = pd.id) AS applicant_count
            FROM placement_drives pd
            JOIN companies c ON pd.company_id = c.id
            WHERE pd.id = ?;
            """, (drive_id,))
            row = cursor.fetchone()
            if row:
                return cls.from_row(row)
        return None

    @classmethod
    def create(
        cls,
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
        status: str = "Active",
        db_manager: Optional[DBManager] = None
    ) -> "PlacementDrive":
        db = db_manager or DBManager.get_instance()
        depts_str = ", ".join(eligible_departments)
        years_str = ", ".join(eligible_years)
        skills_str = ", ".join(required_skills)
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO placement_drives (
                company_id, title, job_role, package_lpa, min_cgpa, eligible_departments,
                eligible_years, required_skills, application_deadline, drive_date, venue_or_link, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, (
                company_id, title.strip(), job_role.strip(), package_lpa, min_cgpa,
                depts_str, years_str, skills_str, application_deadline.strip(),
                drive_date.strip(), venue_or_link.strip(), status
            ))
            drive_id = cursor.lastrowid
            conn.commit()
        return cls.get_by_id(drive_id, db)

    def update(
        self,
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
        status: str = "Active",
        company_id: Optional[int] = None,
        db_manager: Optional[DBManager] = None
    ) -> bool:
        db = db_manager or DBManager.get_instance()
        cid = company_id if company_id is not None else self.company_id
        depts_str = ", ".join(eligible_departments)
        years_str = ", ".join(eligible_years)
        skills_str = ", ".join(required_skills)
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            UPDATE placement_drives SET
                company_id = ?, title = ?, job_role = ?, package_lpa = ?, min_cgpa = ?,
                eligible_departments = ?, eligible_years = ?, required_skills = ?,
                application_deadline = ?, drive_date = ?, venue_or_link = ?, status = ?
            WHERE id = ?;
            """, (
                cid, title.strip(), job_role.strip(), package_lpa, min_cgpa,
                depts_str, years_str, skills_str, application_deadline.strip(),
                drive_date.strip(), venue_or_link.strip(), status, self.id
            ))
            conn.commit()
            self.company_id = cid
            self.title = title
            self.job_role = job_role
            self.package_lpa = package_lpa
            self.min_cgpa = min_cgpa
            self.eligible_departments = eligible_departments
            self.eligible_years = eligible_years
            self.required_skills = required_skills
            self.application_deadline = application_deadline
            self.drive_date = drive_date
            self.venue_or_link = venue_or_link
            self.status = status
            return True

    @classmethod
    def delete(cls, drive_id: int, db_manager: Optional[DBManager] = None) -> bool:
        db = db_manager or DBManager.get_instance()
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM placement_drives WHERE id = ?;", (drive_id,))
            conn.commit()
            return cursor.rowcount > 0
