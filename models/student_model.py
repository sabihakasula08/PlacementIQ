"""
Student Model for PlacementIQ
Manages student profiles, academic metrics, skills, and portfolio attributes.
"""
from typing import Optional, List, Dict, Any
from database.db_manager import DBManager

class Student:
    def __init__(
        self,
        id: int,
        user_id: int,
        register_no: str,
        department: str,
        academic_year: str,
        cgpa: float,
        technical_skills: List[str],
        soft_skills: List[str],
        projects_count: int = 0,
        certifications_count: int = 0,
        projects_description: str = "",
        aptitude_score: float = 70.0,
        communication_score: float = 70.0,
        resume_path: str = "",
        full_name: str = "",
        email: str = "",
        username: str = ""
    ):
        self.id = id
        self.user_id = user_id
        self.register_no = register_no
        self.department = department
        self.academic_year = academic_year
        self.cgpa = float(cgpa)
        self.technical_skills = [s.strip() for s in technical_skills if s.strip()]
        self.soft_skills = [s.strip() for s in soft_skills if s.strip()]
        self.projects_count = int(projects_count)
        self.certifications_count = int(certifications_count)
        self.projects_description = projects_description
        self.aptitude_score = float(aptitude_score)
        self.communication_score = float(communication_score)
        self.resume_path = resume_path
        self.full_name = full_name
        self.email = email
        self.username = username

    @property
    def tech_skills_str(self) -> str:
        return ", ".join(self.technical_skills)

    @property
    def soft_skills_str(self) -> str:
        return ", ".join(self.soft_skills)

    @classmethod
    def from_row(cls, row: Any) -> "Student":
        tech_raw = row["technical_skills"] or ""
        soft_raw = row["soft_skills"] or ""
        tech_list = [s.strip() for s in tech_raw.split(",") if s.strip()]
        soft_list = [s.strip() for s in soft_raw.split(",") if s.strip()]

        full_name = row["full_name"] if "full_name" in row.keys() else ""
        email = row["email"] if "email" in row.keys() else ""
        username = row["username"] if "username" in row.keys() else ""

        return cls(
            id=row["id"],
            user_id=row["user_id"],
            register_no=row["register_no"],
            department=row["department"],
            academic_year=row["academic_year"],
            cgpa=row["cgpa"],
            technical_skills=tech_list,
            soft_skills=soft_list,
            projects_count=row["projects_count"] or 0,
            certifications_count=row["certifications_count"] or 0,
            projects_description=row["projects_description"] or "",
            aptitude_score=row["aptitude_score"] or 0.0,
            communication_score=row["communication_score"] or 0.0,
            resume_path=row["resume_path"] or "",
            full_name=full_name,
            email=email,
            username=username
        )

    @classmethod
    def get_by_user_id(cls, user_id: int, db_manager: Optional[DBManager] = None) -> Optional["Student"]:
        db = db_manager or DBManager.get_instance()
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT s.*, u.full_name, u.email, u.username
            FROM students s
            JOIN users u ON s.user_id = u.id
            WHERE s.user_id = ?;
            """, (user_id,))
            row = cursor.fetchone()
            if row:
                return cls.from_row(row)
        return None

    @classmethod
    def get_by_id(cls, student_id: int, db_manager: Optional[DBManager] = None) -> Optional["Student"]:
        db = db_manager or DBManager.get_instance()
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT s.*, u.full_name, u.email, u.username
            FROM students s
            JOIN users u ON s.user_id = u.id
            WHERE s.id = ?;
            """, (student_id,))
            row = cursor.fetchone()
            if row:
                return cls.from_row(row)
        return None

    @classmethod
    def get_by_reg_no(cls, register_no: str, db_manager: Optional[DBManager] = None) -> Optional["Student"]:
        db = db_manager or DBManager.get_instance()
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT s.*, u.full_name, u.email, u.username
            FROM students s
            JOIN users u ON s.user_id = u.id
            WHERE LOWER(s.register_no) = LOWER(?);
            """, (register_no.strip(),))
            row = cursor.fetchone()
            if row:
                return cls.from_row(row)
        return None

    @classmethod
    def get_all(cls, db_manager: Optional[DBManager] = None) -> List["Student"]:
        db = db_manager or DBManager.get_instance()
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT s.*, u.full_name, u.email, u.username
            FROM students s
            JOIN users u ON s.user_id = u.id
            ORDER BY s.register_no ASC;
            """)
            return [cls.from_row(row) for row in cursor.fetchall()]

    @classmethod
    def create(
        cls,
        user_id: int,
        register_no: str,
        department: str,
        academic_year: str,
        cgpa: float,
        technical_skills: List[str],
        soft_skills: List[str],
        projects_count: int = 0,
        certifications_count: int = 0,
        projects_description: str = "",
        aptitude_score: float = 75.0,
        communication_score: float = 75.0,
        resume_path: str = "",
        db_manager: Optional[DBManager] = None
    ) -> "Student":
        db = db_manager or DBManager.get_instance()
        tech_str = ", ".join(technical_skills)
        soft_str = ", ".join(soft_skills)
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO students (
                user_id, register_no, department, academic_year, cgpa,
                technical_skills, soft_skills, projects_count, certifications_count,
                projects_description, aptitude_score, communication_score, resume_path
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, (
                user_id, register_no.strip().upper(), department.strip(),
                academic_year.strip(), cgpa, tech_str, soft_str,
                projects_count, certifications_count, projects_description.strip(),
                aptitude_score, communication_score, resume_path.strip()
            ))
            student_id = cursor.lastrowid
            conn.commit()

        return cls.get_by_id(student_id, db)

    def update(
        self,
        full_name: Optional[str] = None,
        email: Optional[str] = None,
        department: Optional[str] = None,
        academic_year: Optional[str] = None,
        cgpa: Optional[float] = None,
        technical_skills: Optional[List[str]] = None,
        soft_skills: Optional[List[str]] = None,
        projects_count: Optional[int] = None,
        certifications_count: Optional[int] = None,
        projects_description: Optional[str] = None,
        aptitude_score: Optional[float] = None,
        communication_score: Optional[float] = None,
        resume_path: Optional[str] = None,
        db_manager: Optional[DBManager] = None
    ) -> bool:
        db = db_manager or DBManager.get_instance()
        with db.get_connection() as conn:
            cursor = conn.cursor()

            # Update User table if full_name or email changed
            if full_name is not None or email is not None:
                new_name = full_name if full_name is not None else self.full_name
                new_email = email if email is not None else self.email
                cursor.execute("""
                UPDATE users SET full_name = ?, email = ? WHERE id = ?;
                """, (new_name.strip(), new_email.strip(), self.user_id))
                self.full_name = new_name
                self.email = new_email

            # Update Students table
            if department is not None: self.department = department
            if academic_year is not None: self.academic_year = academic_year
            if cgpa is not None: self.cgpa = float(cgpa)
            if technical_skills is not None: self.technical_skills = [s.strip() for s in technical_skills if s.strip()]
            if soft_skills is not None: self.soft_skills = [s.strip() for s in soft_skills if s.strip()]
            if projects_count is not None: self.projects_count = int(projects_count)
            if certifications_count is not None: self.certifications_count = int(certifications_count)
            if projects_description is not None: self.projects_description = projects_description
            if aptitude_score is not None: self.aptitude_score = float(aptitude_score)
            if communication_score is not None: self.communication_score = float(communication_score)
            if resume_path is not None: self.resume_path = resume_path

            cursor.execute("""
            UPDATE students SET
                department = ?, academic_year = ?, cgpa = ?,
                technical_skills = ?, soft_skills = ?,
                projects_count = ?, certifications_count = ?,
                projects_description = ?, aptitude_score = ?,
                communication_score = ?, resume_path = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?;
            """, (
                self.department, self.academic_year, self.cgpa,
                self.tech_skills_str, self.soft_skills_str,
                self.projects_count, self.certifications_count,
                self.projects_description, self.aptitude_score,
                self.communication_score, self.resume_path,
                self.id
            ))
            conn.commit()
            return True
