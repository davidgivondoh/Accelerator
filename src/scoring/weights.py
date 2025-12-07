"""
Scoring weights configuration.

Defines the weights used to score opportunities for fit.
These can be adjusted through the learning system.
"""

from pydantic import BaseModel, Field


class ScoringWeights(BaseModel):
    """Weights for opportunity scoring."""
    
    # Skill matching weights
    skill_match_weight: float = Field(default=0.30, description="Weight for skill match score")
    experience_match_weight: float = Field(default=0.20, description="Weight for experience match")
    interest_match_weight: float = Field(default=0.20, description="Weight for interest/goal alignment")
    
    # External factors
    prestige_weight: float = Field(default=0.15, description="Weight for company/program prestige")
    urgency_weight: float = Field(default=0.10, description="Weight for deadline urgency")
    compensation_weight: float = Field(default=0.05, description="Weight for compensation")
    
    # Skill match sub-weights
    exact_skill_match: float = Field(default=1.0, description="Score for exact skill match")
    partial_skill_match: float = Field(default=0.5, description="Score for partial skill match")
    missing_skill_penalty: float = Field(default=0.2, description="Penalty per missing required skill")
    
    # Experience sub-weights
    experience_years_importance: float = Field(default=0.7, description="Importance of years of experience")
    role_similarity_importance: float = Field(default=0.3, description="Importance of similar role titles")
    
    # Tier thresholds
    tier_1_threshold: float = Field(default=0.80, description="Minimum score for Tier 1")
    tier_2_threshold: float = Field(default=0.60, description="Minimum score for Tier 2")
    # Below tier_2_threshold = Tier 3
    
    def validate_weights(self) -> bool:
        """Ensure main weights sum to 1.0."""
        total = (
            self.skill_match_weight +
            self.experience_match_weight +
            self.interest_match_weight +
            self.prestige_weight +
            self.urgency_weight +
            self.compensation_weight
        )
        return abs(total - 1.0) < 0.01


# Default weights instance
default_weights = ScoringWeights()
