"""
Unit Tests for Core Models
==========================

Tests for Pydantic models, enums, and data structures.
"""

import pytest
from datetime import datetime, timedelta
from decimal import Decimal

from src.models import (
    Opportunity,
    OpportunityType,
    OpportunityTier,
    ApplicationDraft,
    Profile,
)


class TestOpportunityType:
    """Tests for OpportunityType enum."""
    
    def test_all_types_exist(self):
        """Verify all opportunity types are defined."""
        expected_types = {'JOB', 'SCHOLARSHIP', 'FELLOWSHIP', 'GRANT', 
                         'ACCELERATOR', 'RESEARCH', 'EVENT'}
        actual_types = {t.name for t in OpportunityType}
        assert expected_types.issubset(actual_types)
    
    def test_type_values(self):
        """Verify type values are correct."""
        assert OpportunityType.JOB.value == "job"
        assert OpportunityType.GRANT.value == "grant"


class TestOpportunityTier:
    """Tests for OpportunityTier enum."""
    
    def test_tier_ordering(self):
        """Verify tiers are ordered by priority."""
        assert OpportunityTier.TIER_1.value < OpportunityTier.TIER_2.value
        assert OpportunityTier.TIER_2.value < OpportunityTier.TIER_3.value
    
    def test_tier_names(self):
        """Verify tier names are descriptive."""
        assert "1" in OpportunityTier.TIER_1.name
        assert "2" in OpportunityTier.TIER_2.name
        assert "3" in OpportunityTier.TIER_3.name


class TestOpportunityModel:
    """Tests for the Opportunity model."""
    
    @pytest.fixture
    def valid_opportunity_data(self):
        """Valid opportunity data for testing."""
        return {
            "title": "Senior AI Engineer",
            "organization": "TechCorp",
            "type": OpportunityType.JOB,
            "source_url": "https://example.com/job/123",
            "description": "We're looking for an experienced AI engineer...",
            "requirements": ["5+ years experience", "PhD preferred"],
            "deadline": datetime.utcnow() + timedelta(days=30),
            "fit_score": 0.85,
            "tier": OpportunityTier.TIER_1,
        }
    
    def test_create_valid_opportunity(self, valid_opportunity_data):
        """Test creating a valid opportunity."""
        opp = Opportunity(**valid_opportunity_data)
        assert opp.title == "Senior AI Engineer"
        assert opp.organization == "TechCorp"
        assert opp.fit_score == 0.85
    
    def test_fit_score_bounds(self, valid_opportunity_data):
        """Test fit score must be between 0 and 1."""
        # Valid scores
        valid_opportunity_data["fit_score"] = 0.0
        opp = Opportunity(**valid_opportunity_data)
        assert opp.fit_score == 0.0
        
        valid_opportunity_data["fit_score"] = 1.0
        opp = Opportunity(**valid_opportunity_data)
        assert opp.fit_score == 1.0
    
    def test_auto_tier_assignment(self, valid_opportunity_data):
        """Test tier is auto-assigned based on fit score."""
        # High score = Tier 1
        valid_opportunity_data["fit_score"] = 0.9
        valid_opportunity_data["tier"] = None
        opp = Opportunity(**valid_opportunity_data)
        # Tier should be assigned based on score
        assert opp.tier is not None


class TestApplicationDraft:
    """Tests for the ApplicationDraft model."""
    
    @pytest.fixture
    def valid_draft_data(self):
        """Valid application draft data."""
        return {
            "opportunity_id": "opp_123",
            "content_type": "cover_letter",
            "content": "Dear Hiring Manager...",
            "version": 1,
            "quality_score": 0.88,
        }
    
    def test_create_valid_draft(self, valid_draft_data):
        """Test creating a valid draft."""
        draft = ApplicationDraft(**valid_draft_data)
        assert draft.content_type == "cover_letter"
        assert draft.version == 1
    
    def test_draft_versioning(self, valid_draft_data):
        """Test draft version incrementing."""
        draft1 = ApplicationDraft(**valid_draft_data)
        valid_draft_data["version"] = 2
        valid_draft_data["content"] = "Dear Hiring Manager (revised)..."
        draft2 = ApplicationDraft(**valid_draft_data)
        
        assert draft2.version > draft1.version


class TestProfile:
    """Tests for the Profile model."""
    
    @pytest.fixture
    def valid_profile_data(self):
        """Valid profile data."""
        return {
            "name": "John Doe",
            "email": "john@example.com",
            "headline": "AI Researcher & Engineer",
            "skills": ["Python", "Machine Learning", "NLP"],
            "experience_years": 5,
        }
    
    def test_create_valid_profile(self, valid_profile_data):
        """Test creating a valid profile."""
        profile = Profile(**valid_profile_data)
        assert profile.name == "John Doe"
        assert len(profile.skills) == 3
    
    def test_profile_skills_list(self, valid_profile_data):
        """Test profile skills are stored as list."""
        profile = Profile(**valid_profile_data)
        assert isinstance(profile.skills, list)
        assert "Python" in profile.skills


class TestModelSerialization:
    """Tests for model serialization/deserialization."""
    
    def test_opportunity_to_dict(self):
        """Test opportunity can be serialized to dict."""
        opp = Opportunity(
            title="Test Job",
            organization="Test Org",
            type=OpportunityType.JOB,
            source_url="https://example.com",
            fit_score=0.75,
        )
        data = opp.model_dump()
        assert isinstance(data, dict)
        assert data["title"] == "Test Job"
    
    def test_opportunity_from_dict(self):
        """Test opportunity can be deserialized from dict."""
        data = {
            "title": "Test Job",
            "organization": "Test Org",
            "type": "job",
            "source_url": "https://example.com",
            "fit_score": 0.75,
        }
        opp = Opportunity.model_validate(data)
        assert opp.title == "Test Job"
        assert opp.type == OpportunityType.JOB
