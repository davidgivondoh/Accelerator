"""
SQLAlchemy ORM models for the Growth Engine.

These map to PostgreSQL tables and provide type-safe database operations.
"""

from datetime import datetime
from typing import Any
from uuid import uuid4

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.data.database import Base
from src.models.enums import (
    ApplicationStatus,
    ContentType,
    OpportunityTier,
    OpportunityType,
    OutcomeType,
    SourceType,
)


class OpportunityORM(Base):
    """SQLAlchemy model for opportunities."""
    
    __tablename__ = "opportunities"
    
    # Primary key
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4())
    )
    
    # External reference
    external_id: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    
    # Core info
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    organization: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # Classification
    opportunity_type: Mapped[str] = mapped_column(
        Enum(OpportunityType, name="opportunity_type"),
        nullable=False,
        index=True
    )
    tier: Mapped[str] = mapped_column(
        Enum(OpportunityTier, name="opportunity_tier"),
        default=OpportunityTier.UNSCORED,
        index=True
    )
    tags: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    
    # Location
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_remote: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # URLs
    url: Mapped[str] = mapped_column(String(2048), nullable=False, unique=True)
    application_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    
    # Dates
    posted_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    deadline: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, index=True)
    start_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    
    # Requirements (JSON for flexibility)
    requirements: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    
    # Compensation (JSON)
    compensation: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    
    # Scoring (JSON)
    score: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    fit_score: Mapped[float | None] = mapped_column(Float, nullable=True, index=True)
    
    # Source tracking
    source: Mapped[str] = mapped_column(
        Enum(SourceType, name="source_type"),
        nullable=False
    )
    source_query: Mapped[str | None] = mapped_column(String(500), nullable=True)
    
    # Raw data backup
    raw_data: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    
    # Timestamps
    discovered_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    
    # Relationships
    applications: Mapped[list["ApplicationDraftORM"]] = relationship(
        back_populates="opportunity",
        cascade="all, delete-orphan"
    )


class ApplicationDraftORM(Base):
    """SQLAlchemy model for application drafts."""
    
    __tablename__ = "application_drafts"
    
    # Primary key
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4())
    )
    
    # Foreign key to opportunity
    opportunity_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("opportunities.id"),
        nullable=False,
        index=True
    )
    
    # Status
    status: Mapped[str] = mapped_column(
        Enum(ApplicationStatus, name="application_status"),
        default=ApplicationStatus.DRAFT,
        index=True
    )
    
    # Content pieces (JSON array)
    content_pieces: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list)
    
    # Metadata
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    feedback: Mapped[str | None] = mapped_column(Text, nullable=True)
    overall_quality_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    
    # Profile version used
    profile_version: Mapped[str | None] = mapped_column(String(50), nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    
    # Relationships
    opportunity: Mapped["OpportunityORM"] = relationship(back_populates="applications")
    outcomes: Mapped[list["OutcomeORM"]] = relationship(
        back_populates="application",
        cascade="all, delete-orphan"
    )


class OutcomeORM(Base):
    """SQLAlchemy model for tracking application outcomes."""
    
    __tablename__ = "outcomes"
    
    # Primary key
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4())
    )
    
    # Foreign key to application
    application_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("application_drafts.id"),
        nullable=False,
        index=True
    )
    
    # Outcome details
    outcome_type: Mapped[str] = mapped_column(
        Enum(OutcomeType, name="outcome_type"),
        nullable=False,
        index=True
    )
    
    # Additional info
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    feedback_received: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # For learning system
    score_at_submission: Mapped[float | None] = mapped_column(Float, nullable=True)
    features_snapshot: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    
    # Timestamps
    recorded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    outcome_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    
    # Relationships
    application: Mapped["ApplicationDraftORM"] = relationship(back_populates="outcomes")


class ProfileORM(Base):
    """SQLAlchemy model for user profiles."""
    
    __tablename__ = "profiles"
    
    # Primary key
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4())
    )
    
    # User identifier
    user_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    
    # Version tracking
    version: Mapped[str] = mapped_column(String(50), default="1.0.0")
    
    # Profile data (stored as JSON for flexibility)
    profile_data: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    
    # Embeddings (stored separately for vector operations)
    summary_embedding: Mapped[list[float] | None] = mapped_column(ARRAY(Float), nullable=True)
    skills_embedding: Mapped[list[float] | None] = mapped_column(ARRAY(Float), nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )


class ScoringWeightsORM(Base):
    """SQLAlchemy model for scoring weight configurations."""
    
    __tablename__ = "scoring_weights"
    
    # Primary key
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4())
    )
    
    # Weight configuration name
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    
    # Weights (JSON for flexibility)
    weights: Mapped[dict[str, float]] = mapped_column(JSON, nullable=False)
    
    # Performance metrics
    accuracy: Mapped[float | None] = mapped_column(Float, nullable=True)
    samples_evaluated: Mapped[int] = mapped_column(Integer, default=0)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )


# Aliases for the intelligence layer
# These provide compatibility with the learning agent's expected model names
OpportunityRecord = OpportunityORM
ApplicationDraft = ApplicationDraftORM
OutcomeRecord = OutcomeORM
ProfileRecord = ProfileORM
ScoringWeightRecord = ScoringWeightsORM
