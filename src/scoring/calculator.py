"""
Scoring calculator for opportunities.

Calculates fit scores based on profile matching and configurable weights.
"""

from datetime import datetime
from typing import Any

from src.models import (
    Opportunity,
    OpportunityScore,
    OpportunityTier,
    Profile,
)
from src.scoring.weights import ScoringWeights, default_weights


class ScoringEngine:
    """
    Engine for scoring opportunities based on profile fit.
    
    Uses configurable weights to calculate a fit score (0-1) and assign tiers.
    """
    
    def __init__(self, weights: ScoringWeights | None = None):
        """
        Initialize the scoring engine.
        
        Args:
            weights: Custom scoring weights, or use defaults
        """
        self.weights = weights or default_weights
    
    def calculate_skill_match(
        self,
        required_skills: list[str],
        profile_skills: list[str],
    ) -> float:
        """
        Calculate skill match score.
        
        Args:
            required_skills: Skills required by opportunity
            profile_skills: Skills in user profile
            
        Returns:
            Skill match score (0-1)
        """
        if not required_skills:
            return 1.0  # No requirements = perfect match
        
        # Normalize skill names for comparison
        required_lower = [s.lower().strip() for s in required_skills]
        profile_lower = [s.lower().strip() for s in profile_skills]
        
        matched = 0
        partial = 0
        
        for req in required_lower:
            if req in profile_lower:
                matched += 1
            else:
                # Check for partial matches (e.g., "Python" matches "Python 3")
                for profile_skill in profile_lower:
                    if req in profile_skill or profile_skill in req:
                        partial += 1
                        break
        
        exact_score = (matched / len(required_skills)) * self.weights.exact_skill_match
        partial_score = (partial / len(required_skills)) * self.weights.partial_skill_match
        
        # Penalty for missing critical skills
        missing = len(required_skills) - matched - partial
        penalty = missing * self.weights.missing_skill_penalty / len(required_skills)
        
        score = exact_score + partial_score - penalty
        return max(0.0, min(1.0, score))
    
    def calculate_experience_match(
        self,
        required_years: int | None,
        profile_years: int,
        required_role_keywords: list[str] | None = None,
        profile_roles: list[str] | None = None,
    ) -> float:
        """
        Calculate experience match score.
        
        Args:
            required_years: Years of experience required
            profile_years: User's years of experience
            required_role_keywords: Keywords from required role
            profile_roles: User's past role titles
            
        Returns:
            Experience match score (0-1)
        """
        years_score = 1.0
        role_score = 1.0
        
        # Years matching
        if required_years is not None and required_years > 0:
            if profile_years >= required_years:
                years_score = 1.0
            elif profile_years >= required_years * 0.7:
                years_score = 0.8  # Close enough
            elif profile_years >= required_years * 0.5:
                years_score = 0.5
            else:
                years_score = 0.3
        
        # Role similarity
        if required_role_keywords and profile_roles:
            req_lower = [k.lower() for k in required_role_keywords]
            matches = sum(
                1 for role in profile_roles
                for keyword in req_lower
                if keyword in role.lower()
            )
            role_score = min(1.0, matches / len(required_role_keywords))
        
        # Combine with sub-weights
        combined = (
            years_score * self.weights.experience_years_importance +
            role_score * self.weights.role_similarity_importance
        )
        
        return combined
    
    def calculate_interest_match(
        self,
        opportunity_tags: list[str],
        profile_interests: list[str],
        career_goals: str | None = None,
        opportunity_description: str = "",
    ) -> float:
        """
        Calculate interest/goal alignment score.
        
        Args:
            opportunity_tags: Tags/categories of the opportunity
            profile_interests: User's stated interests
            career_goals: User's career goals text
            opportunity_description: Full opportunity description
            
        Returns:
            Interest match score (0-1)
        """
        if not opportunity_tags and not profile_interests:
            return 0.5  # Neutral score if no data
        
        # Tag matching
        tag_score = 0.0
        if opportunity_tags and profile_interests:
            opp_lower = [t.lower() for t in opportunity_tags]
            int_lower = [i.lower() for i in profile_interests]
            matches = sum(1 for t in opp_lower if any(i in t or t in i for i in int_lower))
            tag_score = min(1.0, matches / max(len(opportunity_tags), 1))
        
        # Goal alignment (simple keyword matching for now)
        # In production, use embeddings for semantic matching
        goal_score = 0.5
        if career_goals and opportunity_description:
            goal_keywords = career_goals.lower().split()
            desc_lower = opportunity_description.lower()
            matches = sum(1 for kw in goal_keywords if len(kw) > 4 and kw in desc_lower)
            goal_score = min(1.0, 0.5 + matches * 0.1)
        
        return (tag_score + goal_score) / 2
    
    def calculate_prestige_score(
        self,
        organization: str,
        opportunity_type: str,
    ) -> float:
        """
        Calculate organization/program prestige score.
        
        Args:
            organization: Organization name
            opportunity_type: Type of opportunity
            
        Returns:
            Prestige score (0-1)
        """
        # High-prestige organizations (simplified - could use a database)
        top_companies = {
            "google", "deepmind", "anthropic", "openai", "meta", "apple",
            "microsoft", "amazon", "nvidia", "tesla", "spacex",
            "stanford", "mit", "berkeley", "harvard", "cambridge", "oxford",
        }
        
        top_programs = {
            "y combinator", "techstars", "sequoia", "a16z", "founders fund",
            "thiel fellowship", "rhodes", "fulbright", "marshall",
        }
        
        org_lower = organization.lower()
        
        # Check against known prestigious organizations
        for top in top_companies:
            if top in org_lower:
                return 0.95
        
        for prog in top_programs:
            if prog in org_lower:
                return 0.90
        
        # Default to moderate prestige
        return 0.5
    
    def calculate_urgency_score(
        self,
        deadline: datetime | None,
    ) -> float:
        """
        Calculate deadline urgency score.
        
        Args:
            deadline: Application deadline
            
        Returns:
            Urgency score (0-1), higher = more urgent
        """
        if deadline is None:
            return 0.3  # Low urgency if no deadline
        
        now = datetime.utcnow()
        days_until = (deadline - now).days
        
        if days_until < 0:
            return 0.0  # Expired
        elif days_until <= 3:
            return 1.0  # Critical
        elif days_until <= 7:
            return 0.9  # Urgent
        elif days_until <= 14:
            return 0.7  # Soon
        elif days_until <= 30:
            return 0.5  # Normal
        else:
            return 0.3  # Plenty of time
    
    def calculate_compensation_score(
        self,
        salary_min: float | None,
        salary_max: float | None,
        min_acceptable: float | None,
    ) -> float:
        """
        Calculate compensation match score.
        
        Args:
            salary_min: Minimum offered salary
            salary_max: Maximum offered salary
            min_acceptable: User's minimum acceptable salary
            
        Returns:
            Compensation score (0-1)
        """
        if salary_max is None or min_acceptable is None:
            return 0.5  # Neutral if unknown
        
        if salary_max >= min_acceptable * 1.2:
            return 1.0  # Excellent
        elif salary_max >= min_acceptable:
            return 0.8  # Good
        elif salary_max >= min_acceptable * 0.9:
            return 0.5  # Acceptable
        else:
            return 0.3  # Below expectations
    
    def score_opportunity(
        self,
        opportunity: Opportunity | dict[str, Any],
        profile: Profile | dict[str, Any],
    ) -> OpportunityScore:
        """
        Calculate comprehensive fit score for an opportunity.
        
        Args:
            opportunity: Opportunity to score
            profile: User profile to match against
            
        Returns:
            OpportunityScore with detailed breakdown
        """
        # Handle dict inputs
        if isinstance(opportunity, dict):
            opp = opportunity
        else:
            opp = opportunity.model_dump()
        
        if isinstance(profile, dict):
            prof = profile
        else:
            prof = profile.model_dump()
        
        # Extract profile data
        profile_skills = [s.get("name", s) if isinstance(s, dict) else s for s in prof.get("skills", [])]
        profile_roles = [e.get("role", "") for e in prof.get("experience", [])]
        profile_years = len(prof.get("experience", [])) * 2
        profile_interests = prof.get("preferences", {}).get("target_roles", [])
        career_goals = prof.get("career_goals", "")
        min_salary = prof.get("preferences", {}).get("min_salary")
        
        # Extract opportunity data
        requirements = opp.get("requirements", {})
        required_skills = requirements.get("skills", [])
        required_years = requirements.get("experience_years")
        compensation = opp.get("compensation", {})
        
        # Calculate component scores
        skill_match = self.calculate_skill_match(required_skills, profile_skills)
        
        experience_match = self.calculate_experience_match(
            required_years,
            profile_years,
            required_role_keywords=opp.get("title", "").split(),
            profile_roles=profile_roles,
        )
        
        interest_match = self.calculate_interest_match(
            opp.get("tags", []),
            profile_interests,
            career_goals,
            opp.get("description", ""),
        )
        
        prestige_score = self.calculate_prestige_score(
            opp.get("organization", ""),
            opp.get("opportunity_type", "job"),
        )
        
        urgency_score = self.calculate_urgency_score(
            opp.get("deadline"),
        )
        
        compensation_score = self.calculate_compensation_score(
            compensation.get("salary_min"),
            compensation.get("salary_max"),
            min_salary,
        )
        
        # Calculate weighted fit score
        fit_score = (
            skill_match * self.weights.skill_match_weight +
            experience_match * self.weights.experience_match_weight +
            interest_match * self.weights.interest_match_weight +
            prestige_score * self.weights.prestige_weight +
            urgency_score * self.weights.urgency_weight +
            compensation_score * self.weights.compensation_weight
        )
        
        # Generate reasoning
        reasoning_parts = []
        if skill_match >= 0.8:
            reasoning_parts.append("Strong skill match")
        elif skill_match < 0.5:
            reasoning_parts.append("Skills gap identified")
        
        if experience_match >= 0.8:
            reasoning_parts.append("Experience aligns well")
        
        if prestige_score >= 0.9:
            reasoning_parts.append("Top-tier organization")
        
        if urgency_score >= 0.9:
            reasoning_parts.append("Urgent deadline")
        
        return OpportunityScore(
            fit_score=round(fit_score, 3),
            skill_match=round(skill_match, 3),
            experience_match=round(experience_match, 3),
            interest_match=round(interest_match, 3),
            prestige_score=round(prestige_score, 3),
            urgency_score=round(urgency_score, 3),
            confidence=0.75,  # Fixed confidence for rule-based scoring
            reasoning="; ".join(reasoning_parts) if reasoning_parts else "Standard match",
        )
    
    def assign_tier(self, score: OpportunityScore) -> OpportunityTier:
        """
        Assign a tier based on the fit score.
        
        Args:
            score: Calculated opportunity score
            
        Returns:
            OpportunityTier (TIER_1, TIER_2, or TIER_3)
        """
        if score.fit_score >= self.weights.tier_1_threshold:
            return OpportunityTier.TIER_1
        elif score.fit_score >= self.weights.tier_2_threshold:
            return OpportunityTier.TIER_2
        else:
            return OpportunityTier.TIER_3
    
    def score_batch(
        self,
        opportunities: list[Opportunity | dict[str, Any]],
        profile: Profile | dict[str, Any],
    ) -> list[dict[str, Any]]:
        """
        Score a batch of opportunities.
        
        Args:
            opportunities: List of opportunities to score
            profile: User profile
            
        Returns:
            List of opportunities with scores and tiers added
        """
        results = []
        
        for opp in opportunities:
            score = self.score_opportunity(opp, profile)
            tier = self.assign_tier(score)
            
            # Add score and tier to opportunity
            if isinstance(opp, dict):
                opp_result = opp.copy()
            else:
                opp_result = opp.model_dump()
            
            opp_result["score"] = score.model_dump()
            opp_result["tier"] = tier.value
            results.append(opp_result)
        
        # Sort by fit score descending
        results.sort(key=lambda x: x["score"]["fit_score"], reverse=True)
        
        return results


# Default scoring engine instance
scoring_engine = ScoringEngine()
