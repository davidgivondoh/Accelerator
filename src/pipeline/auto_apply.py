"""
Auto-Apply Pipeline

Automated application system that:
- Generates personalized applications
- Tracks application status
- Manages follow-ups
- Optimizes based on success rates
"""

import asyncio
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum


class ApplicationStatus(Enum):
    """Status of an application"""
    DRAFT = "draft"
    READY = "ready"
    SUBMITTED = "submitted"
    VIEWED = "viewed"
    SHORTLISTED = "shortlisted"
    INTERVIEW = "interview"
    OFFER = "offer"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"


@dataclass
class Application:
    """Application tracking model"""
    id: str
    opportunity_id: str
    opportunity_title: str
    company: str
    status: ApplicationStatus
    created_at: datetime
    submitted_at: Optional[datetime] = None
    last_updated: datetime = field(default_factory=datetime.now)
    cover_letter: Optional[str] = None
    resume_version: Optional[str] = None
    custom_responses: Dict[str, str] = field(default_factory=dict)
    notes: str = ""
    follow_up_date: Optional[datetime] = None
    response_received: bool = False
    score: float = 0.0


@dataclass
class UserProfile:
    """User profile for personalized applications"""
    name: str
    email: str
    phone: Optional[str] = None
    location: str = ""
    title: str = ""
    summary: str = ""
    skills: List[str] = field(default_factory=list)
    experience: List[Dict[str, Any]] = field(default_factory=list)
    education: List[Dict[str, Any]] = field(default_factory=list)
    projects: List[Dict[str, Any]] = field(default_factory=list)
    links: Dict[str, str] = field(default_factory=dict)
    preferences: Dict[str, Any] = field(default_factory=dict)


class AutoApplyPipeline:
    """
    Automated application pipeline that manages the entire 
    application lifecycle from discovery to follow-up.
    """
    
    def __init__(self, user_profile: Optional[UserProfile] = None):
        self.user_profile = user_profile or self._create_demo_profile()
        self.applications: Dict[str, Application] = {}
        self.templates: Dict[str, str] = self._load_templates()
        self.success_rate = 0.0
        self.total_applied = 0
        self.total_responses = 0
        
    def _create_demo_profile(self) -> UserProfile:
        """Create a demo user profile"""
        return UserProfile(
            name="Demo User",
            email="demo@accelerator.io",
            phone="+1 (555) 123-4567",
            location="San Francisco, CA",
            title="Full Stack Developer",
            summary="Passionate developer with 5+ years of experience building scalable web applications. "
                   "Focused on React, Python, and cloud technologies. Love working on impactful projects.",
            skills=[
                "Python", "JavaScript", "TypeScript", "React", "Node.js",
                "PostgreSQL", "MongoDB", "AWS", "Docker", "Kubernetes",
                "GraphQL", "REST APIs", "CI/CD", "Agile/Scrum"
            ],
            experience=[
                {
                    "title": "Senior Developer",
                    "company": "Tech Startup",
                    "duration": "2021 - Present",
                    "highlights": [
                        "Led development of microservices architecture",
                        "Reduced API latency by 60%",
                        "Mentored junior developers"
                    ]
                },
                {
                    "title": "Software Engineer",
                    "company": "Enterprise Corp",
                    "duration": "2019 - 2021",
                    "highlights": [
                        "Built customer-facing dashboard",
                        "Implemented real-time analytics",
                        "Automated deployment pipelines"
                    ]
                }
            ],
            education=[
                {
                    "degree": "B.S. Computer Science",
                    "school": "State University",
                    "year": "2019"
                }
            ],
            projects=[
                {
                    "name": "Open Source Contribution",
                    "description": "Major contributor to popular React library",
                    "link": "https://github.com/example"
                }
            ],
            links={
                "linkedin": "https://linkedin.com/in/example",
                "github": "https://github.com/example",
                "portfolio": "https://example.dev"
            },
            preferences={
                "remote_only": True,
                "min_salary": 120000,
                "preferred_roles": ["Senior Developer", "Tech Lead", "Full Stack"],
                "avoid_industries": []
            }
        )
    
    def _load_templates(self) -> Dict[str, str]:
        """Load application templates"""
        return {
            "cover_letter_startup": """
Dear {hiring_manager},

I am excited to apply for the {position} role at {company}. As someone who thrives in fast-paced, innovative environments, I believe my skills in {relevant_skills} make me an excellent fit for your team.

{personalized_paragraph}

My experience at {recent_company} has prepared me well for this opportunity. I've {achievement_1}, and I'm eager to bring this same drive to {company}.

What excites me most about {company} is {company_interest}. I would love the opportunity to contribute to your mission.

Best regards,
{name}
""",
            "cover_letter_corporate": """
Dear Hiring Manager,

I am writing to express my strong interest in the {position} position at {company}. With {years_exp} years of experience in {field}, I am confident in my ability to contribute effectively to your team.

Throughout my career, I have demonstrated expertise in {relevant_skills}. At {recent_company}, I {achievement_1}.

{personalized_paragraph}

I am particularly drawn to {company}'s commitment to {company_value}. I believe my background aligns well with your requirements and company culture.

Thank you for considering my application. I look forward to discussing how I can contribute to {company}'s continued success.

Sincerely,
{name}
""",
            "follow_up_email": """
Dear {hiring_manager},

I hope this email finds you well. I wanted to follow up on my application for the {position} role at {company}, submitted on {submit_date}.

I remain very enthusiastic about the opportunity to join your team and contribute to {company_goal}.

If you need any additional information, please don't hesitate to reach out. I'm happy to provide further details about my qualifications.

Thank you for your time and consideration.

Best regards,
{name}
""",
            "thank_you_interview": """
Dear {interviewer_name},

Thank you for taking the time to speak with me about the {position} role at {company}. I enjoyed learning more about {discussion_topic} and am even more excited about the possibility of joining your team.

Our conversation reinforced my belief that my experience in {relevant_skill} would allow me to make meaningful contributions to {team_project}.

I look forward to hearing about the next steps in the process.

Best regards,
{name}
"""
        }
    
    async def analyze_opportunity(self, opportunity: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze an opportunity for application strategy"""
        
        # Extract key information
        title = opportunity.get("title", "")
        company = opportunity.get("company", opportunity.get("source", ""))
        description = opportunity.get("description", "")
        requirements = opportunity.get("requirements", [])
        
        # Match skills
        matched_skills = []
        for skill in self.user_profile.skills:
            if skill.lower() in description.lower() or skill.lower() in title.lower():
                matched_skills.append(skill)
        
        # Calculate match score
        skill_match = len(matched_skills) / max(len(self.user_profile.skills), 1) * 100
        
        # Determine application strategy
        if skill_match >= 70:
            strategy = "strong_match"
            priority = "high"
            template = "cover_letter_startup" if "startup" in company.lower() else "cover_letter_corporate"
        elif skill_match >= 50:
            strategy = "good_match"
            priority = "medium"
            template = "cover_letter_corporate"
        else:
            strategy = "stretch_opportunity"
            priority = "low"
            template = "cover_letter_corporate"
        
        return {
            "opportunity_id": opportunity.get("id", str(hash(title))),
            "match_score": skill_match,
            "matched_skills": matched_skills,
            "strategy": strategy,
            "priority": priority,
            "recommended_template": template,
            "personalization_tips": self._get_personalization_tips(opportunity, matched_skills),
            "estimated_success_rate": min(skill_match * 0.8, 75)
        }
    
    def _get_personalization_tips(self, opportunity: Dict, matched_skills: List[str]) -> List[str]:
        """Generate personalization tips for the application"""
        tips = []
        
        company = opportunity.get("company", opportunity.get("source", ""))
        
        # Skill-based tips
        if matched_skills:
            tips.append(f"Emphasize your expertise in {', '.join(matched_skills[:3])}")
        
        # Company-specific tips
        if "startup" in company.lower() or "vc" in company.lower():
            tips.append("Highlight entrepreneurial mindset and adaptability")
            tips.append("Mention any experience with rapid iteration")
        
        if "remote" in opportunity.get("title", "").lower():
            tips.append("Emphasize remote work experience and self-management")
        
        # General tips
        tips.append("Research recent company news and mention specific initiatives")
        tips.append("Quantify achievements with specific metrics")
        
        return tips
    
    async def generate_application(self, 
                                   opportunity: Dict[str, Any],
                                   analysis: Optional[Dict] = None) -> Application:
        """Generate a complete application for an opportunity"""
        
        if not analysis:
            analysis = await self.analyze_opportunity(opportunity)
        
        # Generate cover letter
        template_name = analysis.get("recommended_template", "cover_letter_corporate")
        template = self.templates.get(template_name, self.templates["cover_letter_corporate"])
        
        cover_letter = self._fill_template(template, {
            "hiring_manager": "Hiring Manager",
            "position": opportunity.get("title", "Position"),
            "company": opportunity.get("company", opportunity.get("source", "Company")),
            "relevant_skills": ", ".join(analysis.get("matched_skills", self.user_profile.skills[:3])),
            "personalized_paragraph": self._generate_personalized_paragraph(opportunity, analysis),
            "recent_company": self.user_profile.experience[0]["company"] if self.user_profile.experience else "my current role",
            "achievement_1": self.user_profile.experience[0]["highlights"][0] if self.user_profile.experience else "delivered impactful results",
            "company_interest": self._extract_company_interest(opportunity),
            "name": self.user_profile.name,
            "years_exp": "5+",
            "field": "software development",
            "company_value": "innovation and excellence"
        })
        
        # Create application object
        app_id = f"app_{datetime.now().strftime('%Y%m%d%H%M%S')}_{random.randint(1000, 9999)}"
        
        application = Application(
            id=app_id,
            opportunity_id=analysis.get("opportunity_id", ""),
            opportunity_title=opportunity.get("title", "Unknown"),
            company=opportunity.get("company", opportunity.get("source", "Unknown")),
            status=ApplicationStatus.DRAFT,
            created_at=datetime.now(),
            cover_letter=cover_letter,
            score=analysis.get("match_score", 0)
        )
        
        self.applications[app_id] = application
        
        return application
    
    def _fill_template(self, template: str, values: Dict[str, str]) -> str:
        """Fill in template placeholders"""
        result = template
        for key, value in values.items():
            result = result.replace(f"{{{key}}}", str(value))
        return result.strip()
    
    def _generate_personalized_paragraph(self, opportunity: Dict, analysis: Dict) -> str:
        """Generate a personalized paragraph for the cover letter"""
        matched_skills = analysis.get("matched_skills", [])
        
        if len(matched_skills) >= 3:
            return f"My strong background in {matched_skills[0]} and {matched_skills[1]}, combined with my experience in {matched_skills[2]}, positions me well to make immediate contributions to your team."
        elif matched_skills:
            return f"My expertise in {', '.join(matched_skills)} directly aligns with the requirements of this role, and I'm excited about the opportunity to apply these skills in a new context."
        else:
            return "I am a quick learner who is passionate about taking on new challenges and expanding my skill set to meet the needs of dynamic teams."
    
    def _extract_company_interest(self, opportunity: Dict) -> str:
        """Extract what's interesting about the company"""
        description = opportunity.get("description", "")
        
        if "mission" in description.lower():
            return "your mission-driven approach"
        elif "growth" in description.lower():
            return "your rapid growth and innovation"
        elif "remote" in description.lower():
            return "your commitment to remote-first culture"
        else:
            return "your innovative approach to solving complex problems"
    
    async def submit_application(self, app_id: str) -> Dict[str, Any]:
        """Submit an application (simulation)"""
        
        if app_id not in self.applications:
            return {"success": False, "error": "Application not found"}
        
        application = self.applications[app_id]
        application.status = ApplicationStatus.SUBMITTED
        application.submitted_at = datetime.now()
        application.follow_up_date = datetime.now() + timedelta(days=7)
        application.last_updated = datetime.now()
        
        self.total_applied += 1
        
        return {
            "success": True,
            "application_id": app_id,
            "status": application.status.value,
            "submitted_at": application.submitted_at.isoformat(),
            "follow_up_date": application.follow_up_date.isoformat(),
            "message": f"Application submitted to {application.company} for {application.opportunity_title}"
        }
    
    async def bulk_apply(self, opportunities: List[Dict[str, Any]], 
                         max_applications: int = 10) -> Dict[str, Any]:
        """Apply to multiple opportunities at once"""
        
        results = {
            "submitted": [],
            "skipped": [],
            "errors": []
        }
        
        # Analyze and sort by match score
        analyzed = []
        for opp in opportunities[:max_applications * 2]:  # Analyze more than needed
            analysis = await self.analyze_opportunity(opp)
            analyzed.append((opp, analysis))
        
        # Sort by match score
        analyzed.sort(key=lambda x: x[1].get("match_score", 0), reverse=True)
        
        # Apply to top matches
        for opp, analysis in analyzed[:max_applications]:
            try:
                if analysis.get("match_score", 0) < 30:
                    results["skipped"].append({
                        "title": opp.get("title", ""),
                        "reason": "Low match score"
                    })
                    continue
                
                application = await self.generate_application(opp, analysis)
                submit_result = await self.submit_application(application.id)
                
                if submit_result.get("success"):
                    results["submitted"].append({
                        "application_id": application.id,
                        "title": opp.get("title", ""),
                        "company": opp.get("company", opp.get("source", "")),
                        "match_score": analysis.get("match_score", 0)
                    })
                else:
                    results["errors"].append({
                        "title": opp.get("title", ""),
                        "error": submit_result.get("error", "Unknown error")
                    })
                    
            except Exception as e:
                results["errors"].append({
                    "title": opp.get("title", ""),
                    "error": str(e)
                })
        
        return {
            "success": True,
            "total_submitted": len(results["submitted"]),
            "total_skipped": len(results["skipped"]),
            "total_errors": len(results["errors"]),
            "results": results
        }
    
    def get_application_status(self, app_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific application"""
        
        if app_id not in self.applications:
            return None
        
        app = self.applications[app_id]
        
        return {
            "id": app.id,
            "opportunity_title": app.opportunity_title,
            "company": app.company,
            "status": app.status.value,
            "created_at": app.created_at.isoformat(),
            "submitted_at": app.submitted_at.isoformat() if app.submitted_at else None,
            "follow_up_date": app.follow_up_date.isoformat() if app.follow_up_date else None,
            "match_score": app.score,
            "response_received": app.response_received
        }
    
    def get_all_applications(self) -> List[Dict[str, Any]]:
        """Get all applications with their status"""
        return [self.get_application_status(app_id) for app_id in self.applications]
    
    def get_pipeline_stats(self) -> Dict[str, Any]:
        """Get overall pipeline statistics"""
        
        status_counts = {}
        for app in self.applications.values():
            status = app.status.value
            status_counts[status] = status_counts.get(status, 0) + 1
        
        return {
            "total_applications": len(self.applications),
            "total_submitted": self.total_applied,
            "total_responses": self.total_responses,
            "response_rate": (self.total_responses / max(self.total_applied, 1)) * 100,
            "status_breakdown": status_counts,
            "pending_follow_ups": sum(
                1 for app in self.applications.values()
                if app.follow_up_date and app.follow_up_date <= datetime.now()
                and app.status == ApplicationStatus.SUBMITTED
            )
        }
    
    async def generate_follow_up(self, app_id: str) -> Dict[str, Any]:
        """Generate a follow-up email for an application"""
        
        if app_id not in self.applications:
            return {"success": False, "error": "Application not found"}
        
        app = self.applications[app_id]
        
        if app.status != ApplicationStatus.SUBMITTED:
            return {"success": False, "error": "Can only follow up on submitted applications"}
        
        template = self.templates["follow_up_email"]
        
        follow_up = self._fill_template(template, {
            "hiring_manager": "Hiring Manager",
            "position": app.opportunity_title,
            "company": app.company,
            "submit_date": app.submitted_at.strftime("%B %d, %Y") if app.submitted_at else "recently",
            "company_goal": "your team's important work",
            "name": self.user_profile.name
        })
        
        return {
            "success": True,
            "application_id": app_id,
            "follow_up_email": follow_up,
            "recommended_send_date": (datetime.now() + timedelta(days=1)).isoformat()
        }


# Singleton instance
_pipeline: Optional[AutoApplyPipeline] = None


def get_pipeline() -> AutoApplyPipeline:
    """Get or create the auto-apply pipeline singleton"""
    global _pipeline
    if _pipeline is None:
        _pipeline = AutoApplyPipeline()
    return _pipeline


# Convenience functions
async def analyze_and_apply(opportunity: Dict[str, Any]) -> Dict[str, Any]:
    """Convenience function to analyze and apply to an opportunity"""
    pipeline = get_pipeline()
    analysis = await pipeline.analyze_opportunity(opportunity)
    application = await pipeline.generate_application(opportunity, analysis)
    result = await pipeline.submit_application(application.id)
    
    return {
        **result,
        "analysis": analysis,
        "cover_letter_preview": application.cover_letter[:500] + "..." if application.cover_letter else None
    }
