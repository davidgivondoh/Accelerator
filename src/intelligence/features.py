"""
Feature Engineering for ML Scoring.

Extracts structured features from opportunities and profiles
for use in the ML scoring model.

Features include:
- Semantic similarity scores
- Skill match percentages
- Experience level alignment
- Deadline urgency
- Organization prestige signals
- Historical success patterns
"""

from datetime import datetime, timedelta
from typing import Any

import numpy as np


class FeatureExtractor:
    """
    Extracts ML features from opportunities and profiles.
    
    Features are designed to capture fit signals that predict
    application success.
    """
    
    # Prestige indicators (expandable)
    PRESTIGE_KEYWORDS = {
        "high": [
            "google", "meta", "apple", "amazon", "microsoft", "openai",
            "anthropic", "deepmind", "stanford", "mit", "harvard", "berkeley",
            "ycombinator", "y combinator", "sequoia", "andreessen", "techstars",
            "rhodes", "fulbright", "marshall", "gates cambridge",
        ],
        "medium": [
            "series b", "series c", "unicorn", "top tier", "leading",
            "prestigious", "renowned", "elite", "selective",
        ],
    }
    
    def __init__(self):
        """Initialize the feature extractor."""
        self._skill_cache: dict[str, set[str]] = {}
    
    def extract_features(
        self,
        opportunity: dict[str, Any],
        profile: dict[str, Any],
        semantic_score: float | None = None,
    ) -> dict[str, float]:
        """
        Extract all features for an opportunity-profile pair.
        
        Args:
            opportunity: Opportunity dictionary
            profile: Profile dictionary
            semantic_score: Pre-computed semantic similarity (optional)
            
        Returns:
            Dictionary of feature names to values
        """
        features = {}
        
        # Semantic features
        features["semantic_score"] = semantic_score or 0.5
        
        # Skill match features
        skill_features = self._extract_skill_features(opportunity, profile)
        features.update(skill_features)
        
        # Experience features
        exp_features = self._extract_experience_features(opportunity, profile)
        features.update(exp_features)
        
        # Deadline features
        deadline_features = self._extract_deadline_features(opportunity)
        features.update(deadline_features)
        
        # Organization features
        org_features = self._extract_organization_features(opportunity)
        features.update(org_features)
        
        # Opportunity type features
        type_features = self._extract_type_features(opportunity)
        features.update(type_features)
        
        # Compensation features
        comp_features = self._extract_compensation_features(opportunity, profile)
        features.update(comp_features)
        
        return features
    
    def _extract_skill_features(
        self,
        opportunity: dict[str, Any],
        profile: dict[str, Any],
    ) -> dict[str, float]:
        """Extract skill-related features."""
        features = {}
        
        # Get required skills from opportunity
        required_skills = set()
        if opportunity.get("requirements"):
            reqs = opportunity["requirements"]
            if isinstance(reqs, dict) and reqs.get("skills_required"):
                required_skills = {s.lower() for s in reqs["skills_required"]}
        
        # Get user skills
        user_skills = set()
        if profile.get("skills"):
            skills = profile["skills"]
            if isinstance(skills, list):
                user_skills = {s.lower() if isinstance(s, str) else s.get("name", "").lower() for s in skills}
        
        # Calculate overlap
        if required_skills:
            overlap = required_skills & user_skills
            features["skill_match_ratio"] = len(overlap) / len(required_skills)
            features["skill_match_count"] = float(len(overlap))
            features["missing_skills_count"] = float(len(required_skills - user_skills))
        else:
            features["skill_match_ratio"] = 0.5  # Neutral if no skills specified
            features["skill_match_count"] = 0.0
            features["missing_skills_count"] = 0.0
        
        features["user_skill_count"] = float(len(user_skills))
        
        return features
    
    def _extract_experience_features(
        self,
        opportunity: dict[str, Any],
        profile: dict[str, Any],
    ) -> dict[str, float]:
        """Extract experience-related features."""
        features = {}
        
        # Get required experience
        required_years = 0
        if opportunity.get("requirements"):
            reqs = opportunity["requirements"]
            if isinstance(reqs, dict):
                required_years = reqs.get("experience_years", 0) or 0
        
        # Calculate user experience
        user_years = 0
        if profile.get("experience"):
            for exp in profile["experience"]:
                if isinstance(exp, dict):
                    # Try to calculate duration
                    start = exp.get("start_date")
                    end = exp.get("end_date") or datetime.now().strftime("%Y-%m")
                    if start:
                        try:
                            start_year = int(start.split("-")[0])
                            end_year = int(end.split("-")[0])
                            user_years += max(0, end_year - start_year)
                        except (ValueError, IndexError):
                            user_years += 1  # Assume 1 year if can't parse
        
        features["required_experience_years"] = float(required_years)
        features["user_experience_years"] = float(user_years)
        
        if required_years > 0:
            features["experience_ratio"] = min(2.0, user_years / required_years)
            features["experience_gap"] = float(max(0, required_years - user_years))
        else:
            features["experience_ratio"] = 1.0
            features["experience_gap"] = 0.0
        
        return features
    
    def _extract_deadline_features(
        self,
        opportunity: dict[str, Any],
    ) -> dict[str, float]:
        """Extract deadline-related features."""
        features = {}
        
        deadline = opportunity.get("deadline")
        if deadline:
            if isinstance(deadline, str):
                try:
                    deadline = datetime.fromisoformat(deadline.replace("Z", "+00:00"))
                except ValueError:
                    deadline = None
            
            if isinstance(deadline, datetime):
                now = datetime.now(deadline.tzinfo) if deadline.tzinfo else datetime.now()
                days_until = (deadline - now).days
                
                features["days_until_deadline"] = float(max(0, days_until))
                features["deadline_urgency"] = self._calculate_urgency(days_until)
                features["has_deadline"] = 1.0
            else:
                features["days_until_deadline"] = 30.0  # Default
                features["deadline_urgency"] = 0.3
                features["has_deadline"] = 0.0
        else:
            features["days_until_deadline"] = 30.0
            features["deadline_urgency"] = 0.3
            features["has_deadline"] = 0.0
        
        return features
    
    def _calculate_urgency(self, days: int) -> float:
        """Calculate urgency score (0-1) based on days until deadline."""
        if days <= 0:
            return 0.0  # Expired
        elif days <= 3:
            return 1.0  # Critical
        elif days <= 7:
            return 0.9  # Very urgent
        elif days <= 14:
            return 0.7  # Urgent
        elif days <= 30:
            return 0.5  # Moderate
        elif days <= 60:
            return 0.3  # Low
        else:
            return 0.2  # Not urgent
    
    def _extract_organization_features(
        self,
        opportunity: dict[str, Any],
    ) -> dict[str, float]:
        """Extract organization-related features."""
        features = {}
        
        org_name = opportunity.get("organization", "").lower()
        description = opportunity.get("description", "").lower()
        combined = f"{org_name} {description}"
        
        # Check prestige indicators
        high_prestige = any(kw in combined for kw in self.PRESTIGE_KEYWORDS["high"])
        medium_prestige = any(kw in combined for kw in self.PRESTIGE_KEYWORDS["medium"])
        
        if high_prestige:
            features["prestige_score"] = 1.0
        elif medium_prestige:
            features["prestige_score"] = 0.7
        else:
            features["prestige_score"] = 0.5
        
        features["is_high_prestige"] = 1.0 if high_prestige else 0.0
        
        return features
    
    def _extract_type_features(
        self,
        opportunity: dict[str, Any],
    ) -> dict[str, float]:
        """Extract opportunity type features (one-hot encoded)."""
        features = {}
        
        opp_type = opportunity.get("opportunity_type", "OTHER").upper()
        
        # One-hot encoding for common types
        types = ["JOB", "FELLOWSHIP", "GRANT", "SCHOLARSHIP", "ACCELERATOR", "RESEARCH"]
        for t in types:
            features[f"type_is_{t.lower()}"] = 1.0 if opp_type == t else 0.0
        
        return features
    
    def _extract_compensation_features(
        self,
        opportunity: dict[str, Any],
        profile: dict[str, Any],
    ) -> dict[str, float]:
        """Extract compensation-related features."""
        features = {}
        
        comp = opportunity.get("compensation", {})
        if isinstance(comp, dict):
            amount = comp.get("amount", 0) or 0
            features["has_compensation"] = 1.0 if amount > 0 else 0.0
            features["compensation_amount"] = float(amount)
            
            # Normalize to rough salary scale
            features["compensation_normalized"] = min(1.0, amount / 200000) if amount else 0.5
        else:
            features["has_compensation"] = 0.0
            features["compensation_amount"] = 0.0
            features["compensation_normalized"] = 0.5
        
        return features
    
    def get_feature_names(self) -> list[str]:
        """Get list of all feature names in order."""
        return [
            # Semantic
            "semantic_score",
            # Skills
            "skill_match_ratio",
            "skill_match_count",
            "missing_skills_count",
            "user_skill_count",
            # Experience
            "required_experience_years",
            "user_experience_years",
            "experience_ratio",
            "experience_gap",
            # Deadline
            "days_until_deadline",
            "deadline_urgency",
            "has_deadline",
            # Organization
            "prestige_score",
            "is_high_prestige",
            # Type (one-hot)
            "type_is_job",
            "type_is_fellowship",
            "type_is_grant",
            "type_is_scholarship",
            "type_is_accelerator",
            "type_is_research",
            # Compensation
            "has_compensation",
            "compensation_amount",
            "compensation_normalized",
        ]
    
    def features_to_array(self, features: dict[str, float]) -> np.ndarray:
        """Convert feature dict to numpy array in consistent order."""
        return np.array([features.get(name, 0.0) for name in self.get_feature_names()])


# Global feature extractor instance
_extractor: FeatureExtractor | None = None


def get_feature_extractor() -> FeatureExtractor:
    """Get or create the global feature extractor."""
    global _extractor
    if _extractor is None:
        _extractor = FeatureExtractor()
    return _extractor
