"""
Authentication Controller for PlacementIQ
Manages user authentication, student registration, and session state.
"""
from typing import Optional, Tuple
from database.db_manager import DBManager
from models.user_model import User
from models.student_model import Student
from utils.constants import ROLE_STUDENT, ROLE_ADMIN
from utils.validator import Validator

class AuthController:
    _current_user: Optional[User] = None

    @classmethod
    def get_current_user(cls) -> Optional[User]:
        return cls._current_user

    @classmethod
    def set_current_user(cls, user: Optional[User]):
        cls._current_user = user

    @classmethod
    def logout(cls):
        cls._current_user = None

    @classmethod
    def login(cls, username: str, password: str, db_manager: Optional[DBManager] = None) -> Tuple[bool, str, Optional[User]]:
        if not username or not username.strip():
            return False, "Username is required.", None
        if not password:
            return False, "Password is required.", None

        user = User.authenticate(username, password, db_manager)
        if not user:
            return False, "Invalid username or password.", None

        cls.set_current_user(user)
        return True, f"Welcome back, {user.full_name}!", user

    @classmethod
    def register_student(
        cls,
        username: str,
        password: str,
        full_name: str,
        email: str,
        register_no: str,
        department: str,
        academic_year: str,
        cgpa: float,
        technical_skills: list[str],
        soft_skills: list[str],
        db_manager: Optional[DBManager] = None
    ) -> Tuple[bool, str, Optional[User]]:
        db = db_manager or DBManager.get_instance()

        # Validation
        if not username or len(username.strip()) < 3:
            return False, "Username must be at least 3 characters long.", None
        
        ok, msg = Validator.is_valid_password(password)
        if not ok:
            return False, msg, None

        if not full_name or len(full_name.strip()) < 2:
            return False, "Full name is required.", None

        if not Validator.is_valid_email(email):
            return False, "Please enter a valid email address.", None

        ok, msg = Validator.is_valid_reg_no(register_no)
        if not ok:
            return False, msg, None

        ok, msg = Validator.is_valid_cgpa(cgpa)
        if not ok:
            return False, msg, None

        # Check existing username
        with db.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT id FROM users WHERE LOWER(username) = LOWER(?);", (username.strip(),))
            if cur.fetchone():
                return False, f"Username '{username}' is already taken.", None

            cur.execute("SELECT id FROM students WHERE LOWER(register_no) = LOWER(?);", (register_no.strip(),))
            if cur.fetchone():
                return False, f"Register number '{register_no}' is already registered.", None

        # Create user & student profile
        try:
            user = User.create_user(
                username=username,
                password=password,
                role=ROLE_STUDENT,
                full_name=full_name,
                email=email,
                db_manager=db
            )

            Student.create(
                user_id=user.id,
                register_no=register_no,
                department=department,
                academic_year=academic_year,
                cgpa=float(cgpa),
                technical_skills=technical_skills,
                soft_skills=soft_skills,
                projects_count=1,
                certifications_count=0,
                projects_description="Academic project",
                aptitude_score=75.0,
                communication_score=75.0,
                resume_path="",
                db_manager=db
            )
            return True, "Registration successful! You may now log in.", user
        except Exception as e:
            return False, f"Registration failed: {str(e)}", None
