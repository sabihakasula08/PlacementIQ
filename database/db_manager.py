"""
Database Manager for PlacementIQ
Handles SQLite schema, connection lifecycle, transactions, and realistic seeding.
"""
import os
import sqlite3
import hashlib
import secrets
from contextlib import contextmanager
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Tuple
from utils.constants import (
    ROLE_ADMIN, ROLE_STUDENT, STATUS_APPLIED, STATUS_SHORTLISTED,
    STATUS_ASSESSMENT, STATUS_INTERVIEW, STATUS_SELECTED, STATUS_REJECTED,
    DEMO_USERS
)

DEFAULT_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "placementiq.db")


class DBManager:
    _instance = None

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or DEFAULT_DB_PATH
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.init_db()

    @classmethod
    def get_instance(cls, db_path: Optional[str] = None):
        if cls._instance is None:
            cls._instance = DBManager(db_path)
        return cls._instance

    @contextmanager
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        try:
            yield conn
        finally:
            conn.close()

    # ---------------- Password Hashing & Security ----------------
    @staticmethod
    def hash_password(password: str, salt: Optional[str] = None) -> Tuple[str, str]:
        """Returns (password_hash, salt) using SHA-256 with cryptographically strong salt."""
        if salt is None:
            salt = secrets.token_hex(16)
        salted = f"{salt}:{password}".encode("utf-8")
        hashed = hashlib.sha256(salted).hexdigest()
        return hashed, salt

    @staticmethod
    def verify_password(password: str, password_hash: str, salt: str) -> bool:
        check_hash, _ = DBManager.hash_password(password, salt)
        return secrets.compare_digest(check_hash, password_hash)

    # ---------------- Schema Initialization ----------------
    def init_db(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # 1. Users Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('admin', 'student')),
                full_name TEXT NOT NULL,
                email TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)

            # 2. Students Profile Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE NOT NULL,
                register_no TEXT UNIQUE NOT NULL,
                department TEXT NOT NULL,
                academic_year TEXT NOT NULL,
                cgpa REAL NOT NULL DEFAULT 0.0,
                technical_skills TEXT DEFAULT '',
                soft_skills TEXT DEFAULT '',
                projects_count INTEGER DEFAULT 0,
                certifications_count INTEGER DEFAULT 0,
                projects_description TEXT DEFAULT '',
                aptitude_score REAL DEFAULT 0.0,
                communication_score REAL DEFAULT 0.0,
                resume_path TEXT DEFAULT '',
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );
            """)

            # 3. Companies Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS companies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                industry TEXT NOT NULL,
                website TEXT,
                contact_email TEXT,
                location TEXT,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)

            # 4. Placement Drives Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS placement_drives (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                job_role TEXT NOT NULL,
                package_lpa REAL NOT NULL,
                min_cgpa REAL NOT NULL DEFAULT 6.0,
                eligible_departments TEXT NOT NULL,
                eligible_years TEXT NOT NULL,
                required_skills TEXT NOT NULL,
                application_deadline TEXT NOT NULL,
                drive_date TEXT,
                venue_or_link TEXT DEFAULT 'Campus Auditorium & Virtual Test',
                status TEXT DEFAULT 'Active' CHECK(status IN ('Active', 'Closed', 'Upcoming')),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE
            );
            """)

            # 5. Applications Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                drive_id INTEGER NOT NULL,
                applied_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT NOT NULL DEFAULT 'Applied' CHECK(status IN ('Applied', 'Shortlisted', 'Assessment', 'Interview', 'Selected', 'Rejected')),
                feedback TEXT DEFAULT '',
                stage_updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE (student_id, drive_id),
                FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
                FOREIGN KEY (drive_id) REFERENCES placement_drives(id) ON DELETE CASCADE
            );
            """)

            # 6. Readiness Cache / Breakdown Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS readiness_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER UNIQUE NOT NULL,
                overall_score REAL NOT NULL,
                academic_score REAL NOT NULL,
                technical_score REAL NOT NULL,
                aptitude_score REAL NOT NULL,
                communication_score REAL NOT NULL,
                project_score REAL NOT NULL,
                missing_skills TEXT,
                recommendations TEXT,
                last_calculated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
            );
            """)

            conn.commit()

        # Seed initial demo data if empty
        self.seed_demo_data_if_needed()

    # ---------------- Data Seeding ----------------
    def seed_demo_data_if_needed(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM users;")
            count = cursor.fetchone()[0]
            if count > 0:
                return  # Database is already seeded

        self.seed_demo_data()

    def seed_demo_data(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # 1. Seed Users and Students
            for u in DEMO_USERS:
                pw_hash, salt = self.hash_password(u["password"])
                cursor.execute("""
                INSERT INTO users (username, password_hash, salt, role, full_name, email)
                VALUES (?, ?, ?, ?, ?, ?);
                """, (u["username"], pw_hash, salt, u["role"], u["full_name"], u["email"]))
                user_id = cursor.lastrowid

                if u["role"] == ROLE_STUDENT:
                    tech_skills_str = ", ".join(u.get("technical_skills", []))
                    soft_skills_str = ", ".join(u.get("soft_skills", []))
                    cursor.execute("""
                    INSERT INTO students (
                        user_id, register_no, department, academic_year, cgpa,
                        technical_skills, soft_skills, projects_count, certifications_count,
                        projects_description, aptitude_score, communication_score, resume_path
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                    """, (
                        user_id,
                        u["register_no"],
                        u["department"],
                        u["academic_year"],
                        u["cgpa"],
                        tech_skills_str,
                        soft_skills_str,
                        u.get("projects_count", 2),
                        u.get("certifications_count", 1),
                        f"Final year capstone on AI & Cloud Computing; Microservices project using {tech_skills_str}",
                        u.get("aptitude_score", 75),
                        u.get("communication_score", 80),
                        f"C:/resumes/{u['register_no']}_Resume.pdf"
                    ))

            # 2. Seed Companies
            companies = [
                ("Google Cloud", "Cloud Computing & AI", "https://cloud.google.com", "careers@google.com", "Bengaluru / Hyderabad", "Global leader in hyperscale cloud infrastructure, enterprise AI models, and scalable distributed systems."),
                ("Microsoft", "Enterprise Software & OS", "https://microsoft.com", "campus-india@microsoft.com", "Bengaluru / Hyderabad / Noida", "World leader in software products, Azure cloud platform, AI copilot services, and hardware engineering."),
                ("Amazon AWS", "E-Commerce & Cloud Services", "https://aws.amazon.com", "university-hiring@amazon.com", "Bengaluru / Chennai", "Leading global cloud platform delivering over 200 fully featured services from data centers globally."),
                ("Cisco Systems", "Networking & Cybersecurity", "https://cisco.com", "campus-recruitment@cisco.com", "Bengaluru", "Global technology pioneer that connects people, computing, and devices securely via advanced networking."),
                ("TCS Digital", "IT Services & Consulting", "https://tcs.com", "careers.digital@tcs.com", "Pan India", "Tata Consultancy Services Digital practice focusing on advanced analytics, cloud migration, and IoT solutions."),
                ("Deloitte USI", "Management & Technology Consulting", "https://deloitte.com", "talent@deloitte.com", "Hyderabad / Bengaluru", "Professional services firm driving digital transformation, cloud architecture, and cybersecurity analytics.")
            ]

            cursor.executemany("""
            INSERT INTO companies (name, industry, website, contact_email, location, description)
            VALUES (?, ?, ?, ?, ?, ?);
            """, companies)

            # Get company IDs
            cursor.execute("SELECT id, name FROM companies;")
            company_map = {row["name"]: row["id"] for row in cursor.fetchall()}

            # 3. Seed Placement Drives
            today = datetime.now()
            drives = [
                (
                    company_map["Google Cloud"],
                    "Cloud Platform Engineer",
                    "Software Engineer - Cloud Systems",
                    24.5,
                    8.2,
                    "Computer Science & Engineering, Information Technology, Artificial Intelligence & Data Science",
                    "2021 - 2025 (Final Year / Passing Out)",
                    "Python, Docker, Kubernetes, Linux, Data Structures & Algorithms, System Design",
                    (today + timedelta(days=14)).strftime("%Y-%m-%d"),
                    (today + timedelta(days=21)).strftime("%Y-%m-%d"),
                    "Main Campus Auditorium & Google Meet Virtual Round",
                    "Active"
                ),
                (
                    company_map["Microsoft"],
                    "Software Development Engineer (SDE-1)",
                    "Core SDE - Azure Services",
                    21.0,
                    8.0,
                    "Computer Science & Engineering, Information Technology, Artificial Intelligence & Data Science, Electronics & Communication Engineering",
                    "2021 - 2025 (Final Year / Passing Out), 2022 - 2026 (3rd Year)",
                    "Java, C++, Data Structures & Algorithms, System Design, SQL",
                    (today + timedelta(days=10)).strftime("%Y-%m-%d"),
                    (today + timedelta(days=18)).strftime("%Y-%m-%d"),
                    "Virtual Assessment on Codility + Microsoft Teams Interviews",
                    "Active"
                ),
                (
                    company_map["Amazon AWS"],
                    "Associate Cloud Support Engineer",
                    "Solutions Architect & Cloud DevOps",
                    18.0,
                    7.5,
                    "Computer Science & Engineering, Information Technology, Artificial Intelligence & Data Science, Electronics & Communication Engineering, Electrical & Electronics Engineering",
                    "2021 - 2025 (Final Year / Passing Out)",
                    "Python, AWS, SQL, Linux, Git & GitHub",
                    (today + timedelta(days=7)).strftime("%Y-%m-%d"),
                    (today + timedelta(days=15)).strftime("%Y-%m-%d"),
                    "AWS Online Assessment + Chime Video Round",
                    "Active"
                ),
                (
                    company_map["Cisco Systems"],
                    "Network Software Engineer",
                    "Core Network Protocols & Embedded C",
                    14.5,
                    7.0,
                    "Computer Science & Engineering, Information Technology, Electronics & Communication Engineering, Electrical & Electronics Engineering",
                    "2021 - 2025 (Final Year / Passing Out)",
                    "C, C++, Linux, Git & GitHub, Problem Solving",
                    (today + timedelta(days=20)).strftime("%Y-%m-%d"),
                    (today + timedelta(days=28)).strftime("%Y-%m-%d"),
                    "Campus Lab 4 & Webex Conference",
                    "Active"
                ),
                (
                    company_map["TCS Digital"],
                    "Systems Engineer - Digital",
                    "Full Stack Web & Enterprise Java",
                    7.5,
                    6.5,
                    "Computer Science & Engineering, Information Technology, Artificial Intelligence & Data Science, Electronics & Communication Engineering, Electrical & Electronics Engineering, Mechanical Engineering, Civil Engineering",
                    "2021 - 2025 (Final Year / Passing Out)",
                    "Java, SQL, React, Git & GitHub",
                    (today + timedelta(days=5)).strftime("%Y-%m-%d"),
                    (today + timedelta(days=12)).strftime("%Y-%m-%d"),
                    "TCS iON Center & Campus Placement Cell",
                    "Active"
                ),
                (
                    company_map["Deloitte USI"],
                    "Analyst - Technology Consulting",
                    "Data Analytics & ERP Engineering",
                    9.0,
                    6.8,
                    "Computer Science & Engineering, Information Technology, Artificial Intelligence & Data Science, Electronics & Communication Engineering, Electrical & Electronics Engineering",
                    "2021 - 2025 (Final Year / Passing Out)",
                    "SQL, Python, Communication, Problem Solving",
                    (today + timedelta(days=25)).strftime("%Y-%m-%d"),
                    (today + timedelta(days=32)).strftime("%Y-%m-%d"),
                    "Deloitte Virtual Portal",
                    "Active"
                )
            ]

            cursor.executemany("""
            INSERT INTO placement_drives (
                company_id, title, job_role, package_lpa, min_cgpa, eligible_departments,
                eligible_years, required_skills, application_deadline, drive_date, venue_or_link, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, drives)

            # 4. Seed Applications for existing students
            cursor.execute("SELECT id, register_no FROM students;")
            students = {row["register_no"]: row["id"] for row in cursor.fetchall()}

            cursor.execute("SELECT id, title FROM placement_drives;")
            drive_list = cursor.fetchall()
            drive_ids = [d["id"] for d in drive_list]

            # Realistic pipeline applications
            s1_id = students.get("21CS042") # Rahul Sharma
            s2_id = students.get("21IT019") # Priya Patel
            s3_id = students.get("22AI005") # Ananya Verma
            s4_id = students.get("21EC088") # Karan Singh

            applications = []
            if s1_id and len(drive_ids) >= 5:
                # Rahul has applied to Google, Microsoft, TCS
                applications.append((s1_id, drive_ids[0], "Interview", "Cleared Codility Round with 95% test score."))
                applications.append((s1_id, drive_ids[1], "Assessment", "Scheduled for Technical Assessment next Tuesday."))
                applications.append((s1_id, drive_ids[4], "Selected", "Offer letter issued: INR 7.5 LPA Digital Cadre."))

            if s2_id and len(drive_ids) >= 5:
                # Priya applied to TCS, Deloitte
                applications.append((s2_id, drive_ids[4], "Shortlisted", "Resume screened and approved for online test."))
                applications.append((s2_id, drive_ids[5], "Applied", "Application submitted; awaiting preliminary screening."))

            if s3_id and len(drive_ids) >= 2:
                # Ananya applied to Microsoft (eligible 3rd year)
                applications.append((s3_id, drive_ids[1], "Shortlisted", "Top 5% in algorithm ranking."))

            if s4_id and len(drive_ids) >= 4:
                # Karan applied to Cisco
                applications.append((s4_id, drive_ids[3], "Assessment", "Cleared Round 1 network quiz."))

            for sid, did, stat, feedb in applications:
                cursor.execute("""
                INSERT INTO applications (student_id, drive_id, status, feedback)
                VALUES (?, ?, ?, ?);
                """, (sid, did, stat, feedb))

            conn.commit()
