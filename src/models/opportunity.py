"""
Opportunity data model.

Represents discovered opportunities (jobs, grants, fellowships, etc.)
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, HttpUrl, computed_field

from src.models.enums import OpportunityTier, OpportunityType, SourceType


class OpportunityRequirements(BaseModel):
    """Requirements for an opportunity."""
    
    education: list[str] = Field(default_factory=list, description="Required education levels")
    experience_years: int | None = Field(default=None, description="Years of experience required")
    skills: list[str] = Field(default_factory=list, description="Required skills")
    languages: list[str] = Field(default_factory=list, description="Required languages")
    location_requirements: str | None = Field(default=None, description="Location/visa requirements")
    other: list[str] = Field(default_factory=list, description="Other requirements")


class OpportunityCompensation(BaseModel):
    """Compensation details for an opportunity."""
    
    salary_min: float | None = Field(default=None, description="Minimum salary")
    salary_max: float | None = Field(default=None, description="Maximum salary")
    currency: str = Field(default="USD", description="Currency code")
    equity: str | None = Field(default=None, description="Equity details")
    benefits: list[str] = Field(default_factory=list, description="Benefits offered")
    funding_amount: float | None = Field(default=None, description="Grant/scholarship amount")


class OpportunityScore(BaseModel):
    """Scoring details for an opportunity."""
    
    fit_score: float = Field(ge=0.0, le=1.0, description="Overall fit score (0-1)")
    skill_match: float = Field(ge=0.0, le=1.0, description="Skill match score")
    experience_match: float = Field(ge=0.0, le=1.0, description="Experience match score")
    interest_match: float = Field(ge=0.0, le=1.0, description="Interest/goal alignment")
    prestige_score: float = Field(ge=0.0, le=1.0, description="Company/program prestige")
    urgency_score: float = Field(ge=0.0, le=1.0, description="Deadline urgency")
    confidence: float = Field(ge=0.0, le=1.0, description="Scoring confidence")
    reasoning: str | None = Field(default=None, description="Explanation for score")


class Opportunity(BaseModel):
    """
    Core opportunity model.
    
    Represents any type of opportunity discovered by the system:
    jobs, scholarships, fellowships, grants, accelerators, etc.
    """
    
    # Identity
    id: str | None = Field(default=None, description="Unique identifier (UUID)")
    external_id: str | None = Field(default=None, description="ID from source platform")
    
    # Core info
    title: str = Field(description="Opportunity title")
    organization: str = Field(description="Company, university, or organization name")
    description: str = Field(description="Full description text")
    summary: str | None = Field(default=None, description="AI-generated summary")
    
    # Classification
    opportunity_type: OpportunityType = Field(description="Type of opportunity")
    tier: OpportunityTier = Field(default=OpportunityTier.UNSCORED, description="Priority tier")
    tags: list[str] = Field(default_factory=list, description="Categorization tags")
    
    # Location
    location: str | None = Field(default=None, description="Location (city, country, or 'Remote')")
    is_remote: bool = Field(default=False, description="Whether remote work is available")
    
    # Links
    url: HttpUrl = Field(description="Original posting URL")
    application_url: HttpUrl | None = Field(default=None, description="Direct application URL")
    
    # Dates
    posted_date: datetime | None = Field(default=None, description="When the opportunity was posted")
    deadline: datetime | None = Field(default=None, description="Application deadline")
    start_date: datetime | None = Field(default=None, description="Position/program start date")
    
    # Details
    requirements: OpportunityRequirements = Field(
        default_factory=OpportunityRequirements,
        description="Requirements for the opportunity"
    )
    compensation: OpportunityCompensation = Field(
        default_factory=OpportunityCompensation,
        description="Compensation details"
    )
    
    # Scoring
    score: OpportunityScore | None = Field(default=None, description="Scoring details")
    
    # Source tracking
    source: SourceType = Field(description="Where this opportunity was discovered")
    source_query: str | None = Field(default=None, description="Search query that found this")
    
    # Metadata
    raw_data: dict[str, Any] | None = Field(default=None, description="Original raw data")
    embedding: list[float] | None = Field(default=None, description="Vector embedding")
    
    # Timestamps
    discovered_at: datetime = Field(default_factory=datetime.utcnow, description="When discovered")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update time")

    @computed_field
    @property
    def days_until_deadline(self) -> int | None:
        """Calculate days until deadline."""
        if self.deadline is None:
            return None
        delta = self.deadline - datetime.utcnow()
        return max(0, delta.days)

    @computed_field
    @property
    def is_urgent(self) -> bool:
        """Check if deadline is within 7 days."""
        days = self.days_until_deadline
        return days is not None and days <= 7

    @computed_field
    @property
    def fit_score(self) -> float | None:
        """Get the fit score if scored."""
        return self.score.fit_score if self.score else None


class OpportunityCreate(BaseModel):
    """Schema for creating a new opportunity."""
    
    title: str
    organization: str
    description: str
    opportunity_type: OpportunityType
    url: HttpUrl
    source: SourceType
    
    # Optional fields
    summary: str | None = None
    location: str | None = None
    is_remote: bool = False
    application_url: HttpUrl | None = None
    posted_date: datetime | None = None
    deadline: datetime | None = None
    requirements: OpportunityRequirements | None = None
    compensation: OpportunityCompensation | None = None
    tags: list[str] = Field(default_factory=list)
    source_query: str | None = None
    raw_data: dict[str, Any] | None = None


class OpportunityUpdate(BaseModel):
    """Schema for updating an opportunity."""
    
    title: str | None = None
    description: str | None = None
    summary: str | None = None
    tier: OpportunityTier | None = None
    score: OpportunityScore | None = None
    tags: list[str] | None = None
    deadline: datetime | None = None
    embedding: list[float] | None = None
