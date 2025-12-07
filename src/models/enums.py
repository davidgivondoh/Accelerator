"""
Shared enumerations for the Growth Engine.
"""

from enum import Enum


class OpportunityType(str, Enum):
    """Types of opportunities the system discovers."""
    
    JOB = "job"
    SCHOLARSHIP = "scholarship"
    FELLOWSHIP = "fellowship"
    ACCELERATOR = "accelerator"
    GRANT = "grant"
    RESEARCH = "research"
    EVENT = "event"
    STARTUP_PROGRAM = "startup_program"
    FUNDING = "funding"
    COMPETITION = "competition"
    OTHER = "other"


class OpportunityTier(str, Enum):
    """Priority tiers for opportunities."""
    
    TIER_1 = "tier_1"  # High priority - immediate action
    TIER_2 = "tier_2"  # Medium priority - queue for review
    TIER_3 = "tier_3"  # Low priority - archive
    UNSCORED = "unscored"  # Not yet scored


class ApplicationStatus(str, Enum):
    """Status of an application draft."""
    
    DRAFT = "draft"
    REVIEW = "review"
    APPROVED = "approved"
    SUBMITTED = "submitted"
    REJECTED = "rejected"
    ACCEPTED = "accepted"
    WITHDRAWN = "withdrawn"


class OutcomeType(str, Enum):
    """Outcome types for learning."""
    
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    INTERVIEW = "interview"
    NO_RESPONSE = "no_response"
    WAITLISTED = "waitlisted"
    WITHDRAWN = "withdrawn"


# Alias for backward compatibility
ApplicationOutcome = OutcomeType


class ContentType(str, Enum):
    """Types of generated content."""
    
    ESSAY = "essay"
    COVER_LETTER = "cover_letter"
    RESEARCH_STATEMENT = "research_statement"
    MOTIVATION_STATEMENT = "motivation_statement"
    LEADERSHIP_STATEMENT = "leadership_statement"
    PROPOSAL = "proposal"
    EMAIL = "email"
    LINKEDIN_MESSAGE = "linkedin_message"


class SourceType(str, Enum):
    """Sources where opportunities are discovered."""
    
    LINKEDIN = "linkedin"
    INDEED = "indeed"
    GLASSDOOR = "glassdoor"
    GOOGLE_JOBS = "google_jobs"
    GREENHOUSE = "greenhouse"
    LEVER = "lever"
    WORKDAY = "workday"
    GRANTS_GOV = "grants_gov"
    FASTLANE = "fastlane"
    PIVOT = "pivot"
    YCOMBINATOR = "ycombinator"
    TECHSTARS = "techstars"
    ANGELLIST = "angellist"
    ACCELERATOR_SCRAPER = "accelerator_scraper"
    SCHOLARSHIP_SCRAPER = "scholarship_scraper"
    CUSTOM = "custom"
    MANUAL = "manual"
