"""
User Model for PlacementIQ
Handles authentication, user entities, and secure password checks.
"""
from typing import Optional, Dict, Any
from database.db_manager import DBManager
from utils.constants import ROLE_STUDENT, ROLE_ADMIN

class User:
    def __init__(self, id: int, username: str, role: str, full_name: str, email: str):
        self.id = id
        self.username = username
        self.role = role
        self.full_name = full_name
        self.email = email

    @property
    def is_admin(self) -> bool:
        return self.role == ROLE_ADMIN

    @property
    def is_student(self) -> bool:
        return self.role == ROLE_STUDENT

    @classmethod
    def authenticate(cls, username: str, password: str, db_manager: Optional[DBManager] = None) -> Optional["User"]:
        db = db_manager or DBManager.get_instance()
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT id, username, password_hash, salt, role, full_name, email
            FROM users WHERE LOWER(username) = LOWER(?);
            """, (username.strip(),))
            row = cursor.fetchone()
            if not row:
                return None

            if db.verify_password(password, row["password_hash"], row["salt"]):
                return cls(
                    id=row["id"],
                    username=row["username"],
                    role=row["role"],
                    full_name=row["full_name"],
                    email=row["email"]
                )
        return None

    @classmethod
    def get_by_id(cls, user_id: int, db_manager: Optional[DBManager] = None) -> Optional["User"]:
        db = db_manager or DBManager.get_instance()
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT id, username, role, full_name, email
            FROM users WHERE id = ?;
            """, (user_id,))
            row = cursor.fetchone()
            if row:
                return cls(
                    id=row["id"],
                    username=row["username"],
                    role=row["role"],
                    full_name=row["full_name"],
                    email=row["email"]
                )
        return None

    @classmethod
    def create_user(
        cls,
        username: str,
        password: str,
        role: str,
        full_name: str,
        email: str,
        db_manager: Optional[DBManager] = None
    ) -> "User":
        db = db_manager or DBManager.get_instance()
        pw_hash, salt = db.hash_password(password)
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO users (username, password_hash, salt, role, full_name, email)
            VALUES (?, ?, ?, ?, ?, ?);
            """, (username.strip(), pw_hash, salt, role, full_name.strip(), email.strip()))
            user_id = cursor.lastrowid
            conn.commit()

        return cls(id=user_id, username=username, role=role, full_name=full_name, email=email)
