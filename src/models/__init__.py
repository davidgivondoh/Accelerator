"""
Data models for the Growth Engine.

This module exports all Pydantic models for:
- Opportunities (jobs, grants, fellowships, etc.)
- Applications (drafts, content pieces)
- Profiles (user data, skills, preferences)
- Enums (types, statuses, tiers)
"""

from src.models.application import (
    ApplicationDraft,
    ApplicationDraftCreate,
    ApplicationDraftUpdate,
    ContentPiece,
)
from src.models.enums import (
    ApplicationStatus,
    ContentType,
    OpportunityTier,
    OpportunityType,
    OutcomeType,
    SourceType,
)
from src.models.opportunity import (
    Opportunity,
    OpportunityCompensation,
    OpportunityCreate,
    OpportunityRequirements,
    OpportunityScore,
    OpportunityUpdate,
)
from src.models.profile import (
    Education,
    Experience,
    Preferences,
    Profile,
    ProfileUpdate,
    Project,
    Publication,
    Skill,
)

__all__ = [
    # Enums
    "OpportunityType",
    "OpportunityTier",
    "ApplicationStatus",
    "OutcomeType",
    "ContentType",
    "SourceType",
    # Opportunity
    "Opportunity",
    "OpportunityCreate",
    "OpportunityUpdate",
    "OpportunityRequirements",
    "OpportunityCompensation",
    "OpportunityScore",
    # Application
    "ApplicationDraft",
    "ApplicationDraftCreate",
    "ApplicationDraftUpdate",
    "ContentPiece",
    # Profile
    "Profile",
    "ProfileUpdate",
    "Education",
    "Experience",
    "Project",
    "Publication",
    "Skill",
    "Preferences",
]
