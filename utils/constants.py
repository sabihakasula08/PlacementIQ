"""
PlacementIQ Constants & Configuration
"""

APP_NAME = "PlacementIQ"
APP_SUBTITLE = "Smart Campus Placement Management System"
APP_VERSION = "2.0.0"

# User Roles
ROLE_STUDENT = "student"
ROLE_ADMIN = "admin"

# Application Statuses
STATUS_APPLIED = "Applied"
STATUS_SHORTLISTED = "Shortlisted"
STATUS_ASSESSMENT = "Assessment"
STATUS_INTERVIEW = "Interview"
STATUS_SELECTED = "Selected"
STATUS_REJECTED = "Rejected"

APPLICATION_STATUSES = [
    STATUS_APPLIED,
    STATUS_SHORTLISTED,
    STATUS_ASSESSMENT,
    STATUS_INTERVIEW,
    STATUS_SELECTED,
    STATUS_REJECTED,
]

# Academic Departments
DEPARTMENTS = [
    "Computer Science & Engineering",
    "Information Technology",
    "Artificial Intelligence & Data Science",
    "Electronics & Communication Engineering",
    "Electrical & Electronics Engineering",
    "Mechanical Engineering",
    "Civil Engineering",
]

# Academic Years
ACADEMIC_YEARS = [
    "2023 - 2027 (2nd Year)",
    "2022 - 2026 (3rd Year)",
    "2021 - 2025 (Final Year / Passing Out)",
]

# Standard Skills Directory
COMMON_SKILLS = [
    "Python", "Java", "C++", "C", "JavaScript", "TypeScript",
    "React", "Node.js", "Django", "FastAPI", "Spring Boot",
    "SQL", "MySQL", "PostgreSQL", "MongoDB",
    "Data Structures & Algorithms", "System Design",
    "Machine Learning", "Deep Learning", "Data Analysis",
    "Docker", "Kubernetes", "AWS", "Git & GitHub",
    "Linux", "Cybersecurity", "REST APIs"
]

COMMON_SOFT_SKILLS = [
    "Communication",
    "Problem Solving",
    "Team Collaboration",
    "Leadership",
    "Adaptability",
    "Critical Thinking",
    "Presentation Skills",
    "Time Management"
]

# Readiness Score Weights (Total = 100)
READINESS_WEIGHTS = {
    "academics": 25,       # CGPA performance
    "technical_skills": 25,# Technical skills vs industry benchmark
    "aptitude": 20,        # Aptitude & logical reasoning test
    "communication": 15,   # Communication & soft skills
    "projects": 15         # Projects, certifications, github/practical
}

# Demo Credentials
DEMO_USERS = [
    {
        "role": ROLE_ADMIN,
        "username": "admin",
        "password": "admin123",
        "full_name": "Dr. Sarah Jenkins",
        "email": "sarah.jenkins@campus.edu",
        "department": "Placement Directorate",
    },
    {
        "role": ROLE_STUDENT,
        "username": "student1",
        "password": "password123",
        "register_no": "21CS042",
        "full_name": "Rahul Sharma",
        "email": "rahul.21cs@campus.edu",
        "department": "Computer Science & Engineering",
        "cgpa": 8.75,
        "academic_year": "2021 - 2025 (Final Year / Passing Out)",
        "technical_skills": ["Python", "Java", "SQL", "Data Structures & Algorithms", "React", "Git & GitHub"],
        "soft_skills": ["Communication", "Problem Solving", "Team Collaboration"],
        "projects_count": 3,
        "certifications_count": 2,
        "aptitude_score": 85,
        "communication_score": 80,
    },
    {
        "role": ROLE_STUDENT,
        "username": "student2",
        "password": "password123",
        "register_no": "21IT019",
        "full_name": "Priya Patel",
        "email": "priya.21it@campus.edu",
        "department": "Information Technology",
        "cgpa": 7.40,
        "academic_year": "2021 - 2025 (Final Year / Passing Out)",
        "technical_skills": ["Java", "SQL", "HTML/CSS", "JavaScript"],
        "soft_skills": ["Team Collaboration", "Time Management"],
        "projects_count": 1,
        "certifications_count": 1,
        "aptitude_score": 68,
        "communication_score": 70,
    },
    {
        "role": ROLE_STUDENT,
        "username": "student3",
        "password": "password123",
        "register_no": "22AI005",
        "full_name": "Ananya Verma",
        "email": "ananya.22ai@campus.edu",
        "department": "Artificial Intelligence & Data Science",
        "cgpa": 9.45,
        "academic_year": "2022 - 2026 (3rd Year)",
        "technical_skills": ["Python", "Machine Learning", "Deep Learning", "SQL", "Data Structures & Algorithms", "Docker", "Git & GitHub"],
        "soft_skills": ["Communication", "Leadership", "Critical Thinking", "Problem Solving"],
        "projects_count": 4,
        "certifications_count": 3,
        "aptitude_score": 92,
        "communication_score": 90,
    },
    {
        "role": ROLE_STUDENT,
        "username": "student4",
        "password": "password123",
        "register_no": "21EC088",
        "full_name": "Karan Singh",
        "email": "karan.21ec@campus.edu",
        "department": "Electronics & Communication Engineering",
        "cgpa": 6.80,
        "academic_year": "2021 - 2025 (Final Year / Passing Out)",
        "technical_skills": ["C", "C++", "Linux", "Git & GitHub"],
        "soft_skills": ["Team Collaboration"],
        "projects_count": 1,
        "certifications_count": 0,
        "aptitude_score": 60,
        "communication_score": 65,
    }
]
