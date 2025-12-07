"""
Application draft data model.

Represents generated application content (essays, cover letters, etc.)
"""

from datetime import datetime

from pydantic import BaseModel, Field

from src.models.enums import ApplicationStatus, ContentType


class ContentPiece(BaseModel):
    """A single piece of generated content."""
    
    content_type: ContentType = Field(description="Type of content")
    prompt_used: str | None = Field(default=None, description="Prompt that generated this")
    content: str = Field(description="The generated content")
    word_count: int = Field(description="Word count")
    quality_score: float | None = Field(default=None, ge=0.0, le=1.0, description="Self-evaluated quality")
    version: int = Field(default=1, description="Content version number")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    @classmethod
    def from_text(cls, content: str, content_type: ContentType, prompt: str | None = None) -> "ContentPiece":
        """Create a ContentPiece from raw text."""
        return cls(
            content_type=content_type,
            prompt_used=prompt,
            content=content,
            word_count=len(content.split()),
        )


class ApplicationDraft(BaseModel):
    """
    Application draft model.
    
    Contains all generated content for a single opportunity application.
    """
    
    # Identity
    id: str | None = Field(default=None, description="Unique identifier (UUID)")
    opportunity_id: str = Field(description="ID of the associated opportunity")
    
    # Status
    status: ApplicationStatus = Field(default=ApplicationStatus.DRAFT)
    
    # Generated content pieces
    content_pieces: list[ContentPiece] = Field(
        default_factory=list,
        description="All generated content pieces"
    )
    
    # Metadata
    notes: str | None = Field(default=None, description="User notes on this draft")
    feedback: str | None = Field(default=None, description="Review feedback")
    
    # Quality metrics
    overall_quality_score: float | None = Field(
        default=None, ge=0.0, le=1.0,
        description="Overall quality score across all content"
    )
    
    # Profile snapshot (what profile data was used)
    profile_version: str | None = Field(default=None, description="Profile version used")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    submitted_at: datetime | None = Field(default=None, description="When application was submitted")
    
    def get_content_by_type(self, content_type: ContentType) -> ContentPiece | None:
        """Get the latest content piece of a specific type."""
        matching = [c for c in self.content_pieces if c.content_type == content_type]
        return max(matching, key=lambda x: x.version, default=None)
    
    def add_content(self, content: ContentPiece) -> None:
        """Add a new content piece, incrementing version if type exists."""
        existing = self.get_content_by_type(content.content_type)
        if existing:
            content.version = existing.version + 1
        self.content_pieces.append(content)
        self.updated_at = datetime.utcnow()
    
    @property
    def has_essay(self) -> bool:
        """Check if draft has an essay."""
        return self.get_content_by_type(ContentType.ESSAY) is not None
    
    @property
    def has_cover_letter(self) -> bool:
        """Check if draft has a cover letter."""
        return self.get_content_by_type(ContentType.COVER_LETTER) is not None
    
    @property
    def total_word_count(self) -> int:
        """Get total word count across all content."""
        return sum(c.word_count for c in self.content_pieces)


class ApplicationDraftCreate(BaseModel):
    """Schema for creating a new application draft."""
    
    opportunity_id: str
    content_pieces: list[ContentPiece] = Field(default_factory=list)
    notes: str | None = None


class ApplicationDraftUpdate(BaseModel):
    """Schema for updating an application draft."""
    
    status: ApplicationStatus | None = None
    content_pieces: list[ContentPiece] | None = None
    notes: str | None = None
    feedback: str | None = None
    overall_quality_score: float | None = None
