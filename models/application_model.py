"""
Application Model for PlacementIQ
Tracks student recruitment pipeline stages and enforces single-application constraints.
"""
from typing import Optional, List, Dict, Any, Tuple
from database.db_manager import DBManager
from utils.constants import (
    STATUS_APPLIED, STATUS_SHORTLISTED, STATUS_ASSESSMENT,
    STATUS_INTERVIEW, STATUS_SELECTED, STATUS_REJECTED
)

class Application:
    def __init__(
        self,
        id: int,
        student_id: int,
        drive_id: int,
        applied_date: str,
        status: str = STATUS_APPLIED,
        feedback: str = "",
        stage_updated_at: str = "",
        drive_title: str = "",
        job_role: str = "",
        company_name: str = "",
        package_lpa: float = 0.0,
        student_name: str = "",
        register_no: str = "",
        student_cgpa: float = 0.0,
        student_dept: str = ""
    ):
        self.id = id
        self.student_id = student_id
        self.drive_id = drive_id
        self.applied_date = applied_date
        self.status = status
        self.feedback = feedback
        self.stage_updated_at = stage_updated_at
        self.drive_title = drive_title
        self.job_role = job_role
        self.company_name = company_name
        self.package_lpa = float(package_lpa)
        self.student_name = student_name
        self.register_no = register_no
        self.student_cgpa = float(student_cgpa)
        self.student_dept = student_dept

    @classmethod
    def from_row(cls, row: Any) -> "Application":
        return cls(
            id=row["id"],
            student_id=row["student_id"],
            drive_id=row["drive_id"],
            applied_date=str(row["applied_date"]),
            status=row["status"],
            feedback=row["feedback"] or "",
            stage_updated_at=str(row["stage_updated_at"]) if "stage_updated_at" in row.keys() else "",
            drive_title=row["drive_title"] if "drive_title" in row.keys() else "",
            job_role=row["job_role"] if "job_role" in row.keys() else "",
            company_name=row["company_name"] if "company_name" in row.keys() else "",
            package_lpa=row["package_lpa"] if "package_lpa" in row.keys() else 0.0,
            student_name=row["student_name"] if "student_name" in row.keys() else "",
            register_no=row["register_no"] if "register_no" in row.keys() else "",
            student_cgpa=row["student_cgpa"] if "student_cgpa" in row.keys() else 0.0,
            student_dept=row["student_dept"] if "student_dept" in row.keys() else ""
        )

    @classmethod
    def has_applied(cls, student_id: int, drive_id: int, db_manager: Optional[DBManager] = None) -> bool:
        db = db_manager or DBManager.get_instance()
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT id FROM applications WHERE student_id = ? AND drive_id = ?;
            """, (student_id, drive_id))
            return cursor.fetchone() is not None

    @classmethod
    def apply(cls, student_id: int, drive_id: int, db_manager: Optional[DBManager] = None) -> Tuple[bool, str, Optional["Application"]]:
        db = db_manager or DBManager.get_instance()
        if cls.has_applied(student_id, drive_id, db):
            return False, "You have already submitted an application to this placement drive.", None

        with db.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("""
                INSERT INTO applications (student_id, drive_id, status, feedback)
                VALUES (?, ?, ?, ?);
                """, (student_id, drive_id, STATUS_APPLIED, "Application submitted successfully."))
                app_id = cursor.lastrowid
                conn.commit()
            except Exception as e:
                return False, f"Failed to submit application: {str(e)}", None

        app = cls.get_by_id(app_id, db)
        return True, "Application successfully submitted!", app

    @classmethod
    def get_by_id(cls, app_id: int, db_manager: Optional[DBManager] = None) -> Optional["Application"]:
        db = db_manager or DBManager.get_instance()
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT a.*, pd.title AS drive_title, pd.job_role, pd.package_lpa,
                   c.name AS company_name, u.full_name AS student_name, s.register_no,
                   s.cgpa AS student_cgpa, s.department AS student_dept
            FROM applications a
            JOIN placement_drives pd ON a.drive_id = pd.id
            JOIN companies c ON pd.company_id = c.id
            JOIN students s ON a.student_id = s.id
            JOIN users u ON s.user_id = u.id
            WHERE a.id = ?;
            """, (app_id,))
            row = cursor.fetchone()
            if row:
                return cls.from_row(row)
        return None

    @classmethod
    def get_by_student(cls, student_id: int, db_manager: Optional[DBManager] = None) -> List["Application"]:
        db = db_manager or DBManager.get_instance()
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT a.*, pd.title AS drive_title, pd.job_role, pd.package_lpa,
                   c.name AS company_name, u.full_name AS student_name, s.register_no,
                   s.cgpa AS student_cgpa, s.department AS student_dept
            FROM applications a
            JOIN placement_drives pd ON a.drive_id = pd.id
            JOIN companies c ON pd.company_id = c.id
            JOIN students s ON a.student_id = s.id
            JOIN users u ON s.user_id = u.id
            WHERE a.student_id = ?
            ORDER BY a.applied_date DESC;
            """, (student_id,))
            return [cls.from_row(row) for row in cursor.fetchall()]

    @classmethod
    def get_all(cls, db_manager: Optional[DBManager] = None) -> List["Application"]:
        db = db_manager or DBManager.get_instance()
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT a.*, pd.title AS drive_title, pd.job_role, pd.package_lpa,
                   c.name AS company_name, u.full_name AS student_name, s.register_no,
                   s.cgpa AS student_cgpa, s.department AS student_dept
            FROM applications a
            JOIN placement_drives pd ON a.drive_id = pd.id
            JOIN companies c ON pd.company_id = c.id
            JOIN students s ON a.student_id = s.id
            JOIN users u ON s.user_id = u.id
            ORDER BY a.applied_date DESC;
            """)
            return [cls.from_row(row) for row in cursor.fetchall()]

    @classmethod
    def get_by_drive(cls, drive_id: int, db_manager: Optional[DBManager] = None) -> List["Application"]:
        db = db_manager or DBManager.get_instance()
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT a.*, pd.title AS drive_title, pd.job_role, pd.package_lpa,
                   c.name AS company_name, u.full_name AS student_name, s.register_no,
                   s.cgpa AS student_cgpa, s.department AS student_dept
            FROM applications a
            JOIN placement_drives pd ON a.drive_id = pd.id
            JOIN companies c ON pd.company_id = c.id
            JOIN students s ON a.student_id = s.id
            JOIN users u ON s.user_id = u.id
            WHERE a.drive_id = ?
            ORDER BY a.applied_date DESC;
            """, (drive_id,))
            return [cls.from_row(row) for row in cursor.fetchall()]

    @classmethod
    def update_status(cls, app_id: int, status: str, feedback: str = "", db_manager: Optional[DBManager] = None) -> bool:
        db = db_manager or DBManager.get_instance()
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            UPDATE applications
            SET status = ?, feedback = ?, stage_updated_at = CURRENT_TIMESTAMP
            WHERE id = ?;
            """, (status, feedback, app_id))
            conn.commit()
            return cursor.rowcount > 0
