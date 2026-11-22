"""
Input Validation Utilities for PlacementIQ
"""
import re
from datetime import datetime

class Validator:
    @staticmethod
    def is_valid_email(email: str) -> bool:
        if not email or not isinstance(email, str):
            return False
        pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        return bool(re.match(pattern, email.strip()))

    @staticmethod
    def is_valid_cgpa(cgpa_val) -> tuple[bool, str]:
        try:
            val = float(cgpa_val)
            if 0.0 <= val <= 10.0:
                return True, ""
            return False, "CGPA must be between 0.00 and 10.00"
        except (ValueError, TypeError):
            return False, "CGPA must be a valid numeric decimal (e.g. 8.5)"

    @staticmethod
    def is_valid_reg_no(reg_no: str) -> tuple[bool, str]:
        if not reg_no or not reg_no.strip():
            return False, "Register number cannot be empty"
        cleaned = reg_no.strip()
        if len(cleaned) < 3 or len(cleaned) > 20:
            return False, "Register number must be between 3 and 20 characters"
        if not re.match(r"^[A-Za-z0-9\-_]+$", cleaned):
            return False, "Register number can only contain letters, numbers, hyphens, and underscores"
        return True, ""

    @staticmethod
    def is_valid_package(package_val) -> tuple[bool, str]:
        try:
            val = float(package_val)
            if val > 0:
                return True, ""
            return False, "Package (LPA) must be greater than 0"
        except (ValueError, TypeError):
            return False, "Package must be a valid number (e.g. 12.5)"

    @staticmethod
    def is_valid_date(date_str: str) -> tuple[bool, str]:
        if not date_str or not date_str.strip():
            return False, "Date cannot be empty"
        for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%Y/%m/%d"):
            try:
                datetime.strptime(date_str.strip(), fmt)
                return True, ""
            except ValueError:
                continue
        return False, "Date must be in format YYYY-MM-DD"

    @staticmethod
    def is_valid_password(pwd: str) -> tuple[bool, str]:
        if not pwd or len(pwd) < 4:
            return False, "Password must be at least 4 characters long"
        return True, ""
