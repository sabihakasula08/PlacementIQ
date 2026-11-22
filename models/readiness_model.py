"""
Placement Readiness & Skill Gap Analysis Engine
Computes transparent rule-based readiness scores, identifies missing skills across
live placement drives, and powers the automated drive eligibility checker.
"""
from typing import Optional, List, Dict, Any, Tuple
from database.db_manager import DBManager
from models.student_model import Student
from models.drive_model import PlacementDrive
from utils.constants import READINESS_WEIGHTS

class ReadinessResult:
    def __init__(
        self,
        overall_score: float,
        academic_score: float,
        technical_score: float,
        aptitude_score: float,
        communication_score: float,
        project_score: float,
        category_max: Dict[str, float],
        missing_skills: List[Dict[str, Any]],
        recommendations: List[Dict[str, str]],
        readiness_level: str
    ):
        self.overall_score = round(overall_score, 1)
        self.academic_score = round(academic_score, 1)
        self.technical_score = round(technical_score, 1)
        self.aptitude_score = round(aptitude_score, 1)
        self.communication_score = round(communication_score, 1)
        self.project_score = round(project_score, 1)
        self.category_max = category_max
        self.missing_skills = missing_skills
        self.recommendations = recommendations
        self.readiness_level = readiness_level

    def to_dict(self) -> Dict[str, Any]:
        return {
            "overall_score": self.overall_score,
            "academic_score": self.academic_score,
            "technical_score": self.technical_score,
            "aptitude_score": self.aptitude_score,
            "communication_score": self.communication_score,
            "project_score": self.project_score,
            "category_max": self.category_max,
            "missing_skills": self.missing_skills,
            "recommendations": self.recommendations,
            "readiness_level": self.readiness_level,
        }


class EligibilityResult:
    def __init__(
        self,
        drive_id: int,
        drive_title: str,
        company_name: str,
        is_eligible: bool,
        cgpa_passed: bool,
        dept_passed: bool,
        year_passed: bool,
        skills_match_pct: float,
        satisfied_criteria: List[str],
        missing_criteria: List[str],
        matching_skills: List[str],
        missing_skills: List[str]
    ):
        self.drive_id = drive_id
        self.drive_title = drive_title
        self.company_name = company_name
        self.is_eligible = is_eligible
        self.cgpa_passed = cgpa_passed
        self.dept_passed = dept_passed
        self.year_passed = year_passed
        self.skills_match_pct = round(skills_match_pct, 1)
        self.satisfied_criteria = satisfied_criteria
        self.missing_criteria = missing_criteria
        self.matching_skills = matching_skills
        self.missing_skills = missing_skills


class ReadinessEngine:
    @staticmethod
    def calculate_readiness(student: Student, db_manager: Optional[DBManager] = None) -> ReadinessResult:
        """
        Calculates a 100-point transparent rule-based score:
        - Academics (25 pts): Based on CGPA out of 10.
        - Technical Skills (25 pts): Breadth and alignment with active campus recruitment requirements.
        - Aptitude (20 pts): Logical reasoning & aptitude test score (out of 100).
        - Communication & Soft Skills (15 pts): Verbal/soft skill proficiency (10 pts) + registered soft skills count (5 pts).
        - Projects & Certifications (15 pts): Projects (up to 10 pts) + Certifications (up to 5 pts).
        """
        # 1. Academic Performance (max 25)
        cgpa_clamped = min(10.0, max(0.0, student.cgpa))
        academic_score = (cgpa_clamped / 10.0) * READINESS_WEIGHTS["academics"]

        # 2. Technical Skills (max 25)
        # Check student skills against skills demanded by active campus drives
        all_drives = PlacementDrive.get_active(db_manager)
        drive_skills_demanded: Dict[str, int] = {}
        for d in all_drives:
            for s in d.required_skills:
                norm = s.strip().lower()
                drive_skills_demanded[norm] = drive_skills_demanded.get(norm, 0) + 1

        student_tech_normalized = {s.strip().lower() for s in student.technical_skills}
        
        # Skill breadth score: 3 points per unique relevant tech skill (up to 15)
        breadth_points = min(15.0, len(student.technical_skills) * 3.0)
        
        # Alignment with active placement drives: (up to 10)
        if drive_skills_demanded:
            total_matches = sum(count for s, count in drive_skills_demanded.items() if s in student_tech_normalized)
            total_demanded = sum(drive_skills_demanded.values())
            alignment_ratio = total_matches / max(1, total_demanded)
            alignment_points = min(10.0, alignment_ratio * 12.0)
        else:
            alignment_points = min(10.0, len(student.technical_skills) * 2.0)

        technical_score = min(float(READINESS_WEIGHTS["technical_skills"]), breadth_points + alignment_points)

        # 3. Aptitude & Problem Solving (max 20)
        apt_clamped = min(100.0, max(0.0, student.aptitude_score))
        aptitude_score = (apt_clamped / 100.0) * READINESS_WEIGHTS["aptitude"]

        # 4. Soft Skills & Communication (max 15)
        comm_clamped = min(100.0, max(0.0, student.communication_score))
        comm_pts = (comm_clamped / 100.0) * 10.0
        soft_skills_pts = min(5.0, len(student.soft_skills) * 1.5)
        communication_score = min(float(READINESS_WEIGHTS["communication"]), comm_pts + soft_skills_pts)

        # 5. Practical Projects & Experience (max 15)
        proj_pts = min(10.0, student.projects_count * 2.5)
        cert_pts = min(5.0, student.certifications_count * 2.5)
        project_score = min(float(READINESS_WEIGHTS["projects"]), proj_pts + cert_pts)

        # Total score
        overall_score = academic_score + technical_score + aptitude_score + communication_score + project_score
        overall_score = min(100.0, max(0.0, overall_score))

        # Readiness Level
        if overall_score >= 85:
            level = "Elite Placement Ready"
        elif overall_score >= 70:
            level = "Job Ready (High Match)"
        elif overall_score >= 55:
            level = "Moderate Readiness (Skill Gaps)"
        else:
            level = "Needs Preparation"

        # Missing Skills Identification
        missing_skills_map: Dict[str, Dict[str, Any]] = {}
        for d in all_drives:
            for s in d.required_skills:
                s_clean = s.strip()
                if s_clean.lower() not in student_tech_normalized:
                    if s_clean not in missing_skills_map:
                        missing_skills_map[s_clean] = {
                            "skill": s_clean,
                            "demand_count": 0,
                            "required_by": []
                        }
                    missing_skills_map[s_clean]["demand_count"] += 1
                    if d.company_name not in missing_skills_map[s_clean]["required_by"]:
                        missing_skills_map[s_clean]["required_by"].append(d.company_name)

        sorted_missing = sorted(
            missing_skills_map.values(),
            key=lambda x: x["demand_count"],
            reverse=True
        )

        # Explainable Recommendations
        recommendations = []
        if sorted_missing:
            top_skills = [item["skill"] for item in sorted_missing[:3]]
            companies_unlocked = list({comp for item in sorted_missing[:3] for comp in item["required_by"]})[:3]
            recommendations.append({
                "category": "Technical Skill Gap",
                "title": f"Acquire high-demand skills: {', '.join(top_skills)}",
                "impact": f"Targeting these will unlock eligibility for {', '.join(companies_unlocked)} and improve technical readiness by ~10 points.",
                "priority": "High"
            })

        if student.cgpa < 7.5:
            recommendations.append({
                "category": "Academic Threshold",
                "title": f"Target CGPA > 7.50 (Current: {student.cgpa:.2f})",
                "impact": "Tier-1 recruiters (Google, Microsoft, Amazon) require minimum 7.5 - 8.2 CGPA cutoffs.",
                "priority": "High"
            })
        elif student.cgpa < 8.2:
            recommendations.append({
                "category": "Academic Target",
                "title": f"Elevate CGPA to 8.20+ for Super Dream Offers",
                "impact": "Unlocks top-tier cloud & systems engineering roles (packages 20+ LPA).",
                "priority": "Medium"
            })

        if student.projects_count < 2:
            recommendations.append({
                "category": "Portfolio Experience",
                "title": "Build and deploy 1 full-stack or system project on GitHub",
                "impact": "Projects boost interview shortlisting rates by 40% and add practical experience points.",
                "priority": "High"
            })

        if student.aptitude_score < 75:
            recommendations.append({
                "category": "Aptitude Preparation",
                "title": "Practice Quantitative Aptitude & Data Interpretation tests",
                "impact": f"Score currently at {student.aptitude_score:.0f}%. Most campus screening filters require 75%+.",
                "priority": "Medium"
            })

        if student.communication_score < 75 or len(student.soft_skills) < 2:
            recommendations.append({
                "category": "Soft Skills",
                "title": "Engage in mock technical interviews and presentation workshops",
                "impact": "HR and managerial evaluation rounds heavily test structured problem articulation.",
                "priority": "Low"
            })

        return ReadinessResult(
            overall_score=overall_score,
            academic_score=academic_score,
            technical_score=technical_score,
            aptitude_score=aptitude_score,
            communication_score=communication_score,
            project_score=project_score,
            category_max=READINESS_WEIGHTS,
            missing_skills=sorted_missing,
            recommendations=recommendations,
            readiness_level=level
        )

    @staticmethod
    def check_drive_eligibility(student: Student, drive: PlacementDrive) -> EligibilityResult:
        """
        Deep rule-based check between student and placement drive.
        Evaluates CGPA, Department, Passing Year, and Skills.
        """
        satisfied = []
        missing = []
        matching_skills = []
        missing_skills = []

        # 1. CGPA check
        cgpa_passed = student.cgpa >= drive.min_cgpa
        if cgpa_passed:
            satisfied.append(f"CGPA Requirement: Met ({student.cgpa:.2f} >= {drive.min_cgpa:.2f})")
        else:
            missing.append(f"CGPA Requirement: Not met (Student CGPA {student.cgpa:.2f} < Min Cutoff {drive.min_cgpa:.2f})")

        # 2. Department check
        dept_passed = False
        drive_depts_lower = [d.strip().lower() for d in drive.eligible_departments]
        student_dept_lower = student.department.strip().lower()

        # Check if student dept is explicitly in list or "all"
        for d in drive_depts_lower:
            if "all" in d or d in student_dept_lower or student_dept_lower in d:
                dept_passed = True
                break

        if dept_passed:
            satisfied.append(f"Department: Eligible ({student.department})")
        else:
            missing.append(f"Department: Ineligible ({student.department} is not listed in {drive.depts_str})")

        # 3. Academic Year check
        year_passed = False
        drive_years_lower = [y.strip().lower() for y in drive.eligible_years]
        student_year_lower = student.academic_year.strip().lower()
        for y in drive_years_lower:
            if y in student_year_lower or student_year_lower in y or "all" in y:
                year_passed = True
                break

        if year_passed:
            satisfied.append(f"Graduation Batch: Eligible ({student.academic_year})")
        else:
            missing.append(f"Graduation Batch: Ineligible ({student.academic_year} not in {drive.years_str})")

        # 4. Skills match
        student_skills_lower = {s.strip().lower() for s in student.technical_skills}
        for req_skill in drive.required_skills:
            if req_skill.strip().lower() in student_skills_lower:
                matching_skills.append(req_skill.strip())
            else:
                missing_skills.append(req_skill.strip())

        total_req_skills = len(drive.required_skills)
        if total_req_skills > 0:
            match_pct = (len(matching_skills) / total_req_skills) * 100.0
        else:
            match_pct = 100.0

        if match_pct >= 60.0:
            satisfied.append(f"Technical Skills: {len(matching_skills)}/{total_req_skills} matched ({match_pct:.0f}%)")
        else:
            missing.append(f"Technical Skills: Missing required core competencies ({', '.join(missing_skills)})")

        # Core eligibility rule: CGPA, Department, and Academic Year must be satisfied.
        # Technical skills match is also evaluated and factored into recommendations.
        is_eligible = cgpa_passed and dept_passed and year_passed

        return EligibilityResult(
            drive_id=drive.id,
            drive_title=drive.title,
            company_name=drive.company_name,
            is_eligible=is_eligible,
            cgpa_passed=cgpa_passed,
            dept_passed=dept_passed,
            year_passed=year_passed,
            skills_match_pct=match_pct,
            satisfied_criteria=satisfied,
            missing_criteria=missing,
            matching_skills=matching_skills,
            missing_skills=missing_skills
        )
