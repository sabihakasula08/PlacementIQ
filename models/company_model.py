"""
Company Model for PlacementIQ
Manages corporate recruiters, industries, profiles, and placement history.
"""
from typing import Optional, List, Dict, Any
from database.db_manager import DBManager

class Company:
    def __init__(
        self,
        id: int,
        name: str,
        industry: str,
        website: str = "",
        contact_email: str = "",
        location: str = "",
        description: str = "",
        created_at: str = "",
        active_drives_count: int = 0
    ):
        self.id = id
        self.name = name
        self.industry = industry
        self.website = website
        self.contact_email = contact_email
        self.location = location
        self.description = description
        self.created_at = created_at
        self.active_drives_count = active_drives_count

    @classmethod
    def from_row(cls, row: Any) -> "Company":
        active_drives = row["active_drives_count"] if "active_drives_count" in row.keys() else 0
        return cls(
            id=row["id"],
            name=row["name"],
            industry=row["industry"],
            website=row["website"] or "",
            contact_email=row["contact_email"] or "",
            location=row["location"] or "",
            description=row["description"] or "",
            created_at=str(row["created_at"]) if "created_at" in row.keys() else "",
            active_drives_count=active_drives
        )

    @classmethod
    def get_all(cls, db_manager: Optional[DBManager] = None) -> List["Company"]:
        db = db_manager or DBManager.get_instance()
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT c.*,
                   (SELECT COUNT(*) FROM placement_drives pd WHERE pd.company_id = c.id AND pd.status = 'Active') AS active_drives_count
            FROM companies c
            ORDER BY c.name ASC;
            """)
            return [cls.from_row(row) for row in cursor.fetchall()]

    @classmethod
    def get_by_id(cls, company_id: int, db_manager: Optional[DBManager] = None) -> Optional["Company"]:
        db = db_manager or DBManager.get_instance()
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT c.*,
                   (SELECT COUNT(*) FROM placement_drives pd WHERE pd.company_id = c.id AND pd.status = 'Active') AS active_drives_count
            FROM companies c
            WHERE c.id = ?;
            """, (company_id,))
            row = cursor.fetchone()
            if row:
                return cls.from_row(row)
        return None

    @classmethod
    def create(
        cls,
        name: str,
        industry: str,
        website: str = "",
        contact_email: str = "",
        location: str = "",
        description: str = "",
        db_manager: Optional[DBManager] = None
    ) -> "Company":
        db = db_manager or DBManager.get_instance()
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO companies (name, industry, website, contact_email, location, description)
            VALUES (?, ?, ?, ?, ?, ?);
            """, (name.strip(), industry.strip(), website.strip(), contact_email.strip(), location.strip(), description.strip()))
            cid = cursor.lastrowid
            conn.commit()
        return cls.get_by_id(cid, db)

    def update(
        self,
        name: str,
        industry: str,
        website: str = "",
        contact_email: str = "",
        location: str = "",
        description: str = "",
        db_manager: Optional[DBManager] = None
    ) -> bool:
        db = db_manager or DBManager.get_instance()
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            UPDATE companies
            SET name = ?, industry = ?, website = ?, contact_email = ?, location = ?, description = ?
            WHERE id = ?;
            """, (name.strip(), industry.strip(), website.strip(), contact_email.strip(), location.strip(), description.strip(), self.id))
            conn.commit()
            self.name = name
            self.industry = industry
            self.website = website
            self.contact_email = contact_email
            self.location = location
            self.description = description
            return True

    @classmethod
    def delete(cls, company_id: int, db_manager: Optional[DBManager] = None) -> bool:
        db = db_manager or DBManager.get_instance()
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM companies WHERE id = ?;", (company_id,))
            conn.commit()
            return cursor.rowcount > 0
