"""
Profile data model.

Represents the user's profile, skills, experience, and preferences.
This is the "source of truth" for personalization.
"""

from datetime import datetime

from pydantic import BaseModel, Field


class Education(BaseModel):
    """Educational background entry."""
    
    institution: str = Field(description="University/school name")
    degree: str = Field(description="Degree type (BS, MS, PhD, etc.)")
    field: str = Field(description="Field of study")
    graduation_year: int | None = Field(default=None, description="Graduation year")
    gpa: float | None = Field(default=None, description="GPA if available")
    honors: list[str] = Field(default_factory=list, description="Honors received")
    relevant_coursework: list[str] = Field(default_factory=list)


class Experience(BaseModel):
    """Work/research experience entry."""
    
    organization: str = Field(description="Company/lab/organization name")
    role: str = Field(description="Job title or role")
    description: str = Field(description="Description of responsibilities and achievements")
    start_date: str = Field(description="Start date (YYYY-MM or YYYY)")
    end_date: str | None = Field(default=None, description="End date or 'Present'")
    location: str | None = Field(default=None, description="Location")
    skills_used: list[str] = Field(default_factory=list, description="Skills used in this role")
    achievements: list[str] = Field(default_factory=list, description="Key achievements")
    is_current: bool = Field(default=False, description="Currently in this role")


class Project(BaseModel):
    """Project entry."""
    
    name: str = Field(description="Project name")
    description: str = Field(description="Project description")
    role: str | None = Field(default=None, description="Your role in the project")
    technologies: list[str] = Field(default_factory=list, description="Technologies used")
    url: str | None = Field(default=None, description="Project URL")
    highlights: list[str] = Field(default_factory=list, description="Key highlights")


class Publication(BaseModel):
    """Publication or paper entry."""
    
    title: str = Field(description="Publication title")
    authors: list[str] = Field(description="List of authors")
    venue: str = Field(description="Journal, conference, or venue")
    year: int = Field(description="Publication year")
    url: str | None = Field(default=None, description="URL to paper")
    doi: str | None = Field(default=None, description="DOI if available")
    abstract: str | None = Field(default=None, description="Abstract")


class Skill(BaseModel):
    """Skill with proficiency level."""
    
    name: str = Field(description="Skill name")
    category: str = Field(description="Category (e.g., 'Programming', 'ML/AI', 'Soft Skills')")
    proficiency: str = Field(description="Proficiency level (Expert, Advanced, Intermediate, Beginner)")
    years: int | None = Field(default=None, description="Years of experience")


class Preferences(BaseModel):
    """User preferences for opportunity matching."""
    
    # Job preferences
    target_roles: list[str] = Field(default_factory=list, description="Target job titles")
    target_companies: list[str] = Field(default_factory=list, description="Dream companies")
    avoid_companies: list[str] = Field(default_factory=list, description="Companies to avoid")
    
    # Location preferences
    preferred_locations: list[str] = Field(default_factory=list, description="Preferred locations")
    open_to_remote: bool = Field(default=True, description="Open to remote work")
    open_to_relocation: bool = Field(default=True, description="Willing to relocate")
    visa_required: bool = Field(default=False, description="Needs visa sponsorship")
    
    # Compensation preferences
    min_salary: float | None = Field(default=None, description="Minimum acceptable salary")
    preferred_currency: str = Field(default="USD")
    
    # Opportunity type preferences
    interested_in_jobs: bool = Field(default=True)
    interested_in_fellowships: bool = Field(default=True)
    interested_in_grants: bool = Field(default=True)
    interested_in_accelerators: bool = Field(default=True)
    interested_in_research: bool = Field(default=True)
    
    # Work preferences
    preferred_company_size: list[str] = Field(
        default_factory=list,
        description="Startup, Small, Medium, Large, Enterprise"
    )
    preferred_industries: list[str] = Field(default_factory=list)


class Profile(BaseModel):
    """
    Complete user profile.
    
    This is the source of truth for all personalization in the system.
    Used to:
    - Score opportunities for fit
    - Generate personalized applications
    - Maintain consistent narrative across applications
    """
    
    # Identity
    id: str | None = Field(default=None, description="Unique identifier")
    version: str = Field(default="1.0.0", description="Profile version for tracking changes")
    
    # Basic info
    full_name: str = Field(description="Full name")
    email: str = Field(description="Email address")
    phone: str | None = Field(default=None, description="Phone number")
    location: str | None = Field(default=None, description="Current location")
    
    # Online presence
    linkedin_url: str | None = Field(default=None, description="LinkedIn profile URL")
    github_url: str | None = Field(default=None, description="GitHub profile URL")
    portfolio_url: str | None = Field(default=None, description="Personal website/portfolio")
    twitter_url: str | None = Field(default=None, description="Twitter/X profile URL")
    
    # Professional summary
    headline: str = Field(description="Professional headline (1-2 sentences)")
    summary: str = Field(description="Professional summary (2-3 paragraphs)")
    
    # Background
    education: list[Education] = Field(default_factory=list)
    experience: list[Experience] = Field(default_factory=list)
    projects: list[Project] = Field(default_factory=list)
    publications: list[Publication] = Field(default_factory=list)
    
    # Skills
    skills: list[Skill] = Field(default_factory=list)
    languages: list[str] = Field(default_factory=list, description="Languages spoken")
    certifications: list[str] = Field(default_factory=list)
    
    # Awards & achievements
    awards: list[str] = Field(default_factory=list)
    
    # Personal narrative elements (for consistent storytelling)
    origin_story: str | None = Field(
        default=None,
        description="Your journey and what drives you"
    )
    key_achievements: list[str] = Field(
        default_factory=list,
        description="Top 3-5 achievements to highlight"
    )
    unique_value_proposition: str | None = Field(
        default=None,
        description="What makes you uniquely valuable"
    )
    career_goals: str | None = Field(
        default=None,
        description="Short and long-term career goals"
    )
    
    # Preferences
    preferences: Preferences = Field(default_factory=Preferences)
    
    # Embeddings (for semantic matching)
    summary_embedding: list[float] | None = Field(default=None)
    skills_embedding: list[float] | None = Field(default=None)
    experience_embedding: list[float] | None = Field(default=None)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    @property
    def years_of_experience(self) -> int:
        """Calculate total years of experience."""
        if not self.experience:
            return 0
        # Simple calculation - could be more sophisticated
        return len(self.experience) * 2  # Rough estimate
    
    @property
    def skill_names(self) -> list[str]:
        """Get list of all skill names."""
        return [s.name for s in self.skills]
    
    @property
    def expert_skills(self) -> list[str]:
        """Get skills marked as Expert or Advanced."""
        return [s.name for s in self.skills if s.proficiency in ("Expert", "Advanced")]
    
    def get_skills_by_category(self, category: str) -> list[Skill]:
        """Get skills filtered by category."""
        return [s for s in self.skills if s.category.lower() == category.lower()]


class ProfileUpdate(BaseModel):
    """Schema for partial profile updates."""
    
    headline: str | None = None
    summary: str | None = None
    skills: list[Skill] | None = None
    experience: list[Experience] | None = None
    preferences: Preferences | None = None
    origin_story: str | None = None
    key_achievements: list[str] | None = None
    career_goals: str | None = None
