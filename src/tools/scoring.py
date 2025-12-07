"""
ADK Tools for opportunity scoring.

Contains FunctionTools for scoring and prioritizing opportunities.
"""

from datetime import datetime
from typing import Any

from google.adk.tools import FunctionTool

from src.scoring.calculator import scoring_engine
from src.models import OpportunityTier


async def score_opportunity(
    opportunity: dict[str, Any],
    profile: dict[str, Any],
) -> dict[str, Any]:
    """
    Score a single opportunity for profile fit.
    
    Args:
        opportunity: Opportunity data to score
        profile: User profile to match against
        
    Returns:
        Scoring result with fit score, component scores, and tier
    """
    score = scoring_engine.score_opportunity(opportunity, profile)
    tier = scoring_engine.assign_tier(score)
    
    return {
        "success": True,
        "opportunity_title": opportunity.get("title", "Unknown"),
        "fit_score": score.fit_score,
        "tier": tier.value,
        "scores": {
            "skill_match": score.skill_match,
            "experience_match": score.experience_match,
            "interest_match": score.interest_match,
            "prestige_score": score.prestige_score,
            "urgency_score": score.urgency_score,
        },
        "confidence": score.confidence,
        "reasoning": score.reasoning,
        "timestamp": datetime.utcnow().isoformat(),
    }


async def score_batch(
    opportunities: list[dict[str, Any]],
    profile: dict[str, Any],
) -> dict[str, Any]:
    """
    Score a batch of opportunities and rank them.
    
    Args:
        opportunities: List of opportunities to score
        profile: User profile to match against
        
    Returns:
        Scored and ranked opportunities with summary statistics
    """
    scored = scoring_engine.score_batch(opportunities, profile)
    
    # Calculate tier distribution
    tier_counts = {
        OpportunityTier.TIER_1.value: 0,
        OpportunityTier.TIER_2.value: 0,
        OpportunityTier.TIER_3.value: 0,
    }
    
    for opp in scored:
        tier = opp.get("tier", OpportunityTier.TIER_3.value)
        if tier in tier_counts:
            tier_counts[tier] += 1
    
    # Calculate average scores
    avg_fit = sum(o["score"]["fit_score"] for o in scored) / len(scored) if scored else 0
    
    return {
        "success": True,
        "total_scored": len(scored),
        "tier_distribution": tier_counts,
        "average_fit_score": round(avg_fit, 3),
        "top_opportunities": scored[:10],  # Top 10
        "all_scored": scored,
        "timestamp": datetime.utcnow().isoformat(),
    }


async def get_tier_1_opportunities(
    opportunities: list[dict[str, Any]],
    profile: dict[str, Any],
    limit: int = 20,
) -> dict[str, Any]:
    """
    Get only Tier 1 (highest priority) opportunities.
    
    Args:
        opportunities: List of opportunities to filter
        profile: User profile for scoring
        limit: Maximum number to return
        
    Returns:
        Tier 1 opportunities only
    """
    scored = scoring_engine.score_batch(opportunities, profile)
    tier_1 = [o for o in scored if o.get("tier") == OpportunityTier.TIER_1.value]
    
    return {
        "success": True,
        "tier_1_count": len(tier_1),
        "opportunities": tier_1[:limit],
        "message": f"Found {len(tier_1)} Tier 1 opportunities" + (
            f" (showing top {limit})" if len(tier_1) > limit else ""
        ),
    }


async def explain_score(
    opportunity: dict[str, Any],
    profile: dict[str, Any],
) -> dict[str, Any]:
    """
    Get a detailed explanation of why an opportunity scored as it did.
    
    Args:
        opportunity: Opportunity to explain
        profile: User profile used for scoring
        
    Returns:
        Detailed score breakdown with explanations
    """
    score = scoring_engine.score_opportunity(opportunity, profile)
    tier = scoring_engine.assign_tier(score)
    
    # Build detailed explanation
    explanations = []
    
    # Skill analysis
    req_skills = opportunity.get("requirements", {}).get("skills", [])
    profile_skills = [s.get("name", s) if isinstance(s, dict) else s for s in profile.get("skills", [])]
    
    if req_skills:
        matched = [s for s in req_skills if s.lower() in [ps.lower() for ps in profile_skills]]
        missing = [s for s in req_skills if s not in matched]
        explanations.append(f"Skills: {len(matched)}/{len(req_skills)} required skills matched")
        if missing:
            explanations.append(f"Missing skills: {', '.join(missing[:5])}")
    
    # Experience analysis
    req_years = opportunity.get("requirements", {}).get("experience_years")
    profile_years = len(profile.get("experience", [])) * 2
    if req_years:
        explanations.append(f"Experience: {profile_years} years vs {req_years} required")
    
    # Tier explanation
    tier_reasons = {
        OpportunityTier.TIER_1.value: "High priority - strong fit, consider applying immediately",
        OpportunityTier.TIER_2.value: "Medium priority - good fit, queue for review",
        OpportunityTier.TIER_3.value: "Lower priority - partial fit, consider if time permits",
    }
    
    return {
        "success": True,
        "opportunity_title": opportunity.get("title", "Unknown"),
        "organization": opportunity.get("organization", "Unknown"),
        "fit_score": score.fit_score,
        "tier": tier.value,
        "tier_explanation": tier_reasons.get(tier.value, "Unknown tier"),
        "score_breakdown": {
            "skill_match": {
                "score": score.skill_match,
                "weight": "30%",
                "description": "How well your skills match requirements",
            },
            "experience_match": {
                "score": score.experience_match,
                "weight": "20%",
                "description": "Experience level and role similarity",
            },
            "interest_match": {
                "score": score.interest_match,
                "weight": "20%",
                "description": "Alignment with your interests and goals",
            },
            "prestige_score": {
                "score": score.prestige_score,
                "weight": "15%",
                "description": "Organization reputation",
            },
            "urgency_score": {
                "score": score.urgency_score,
                "weight": "10%",
                "description": "Deadline urgency",
            },
        },
        "detailed_analysis": explanations,
        "recommendation": score.reasoning,
    }


async def adjust_weights(
    new_weights: dict[str, float],
) -> dict[str, Any]:
    """
    Temporarily adjust scoring weights for experimentation.
    
    Args:
        new_weights: Dictionary of weight names to new values
        
    Returns:
        Confirmation of weight changes
    """
    # Note: In production, this would persist to config
    valid_weights = [
        "skill_match_weight",
        "experience_match_weight",
        "interest_match_weight",
        "prestige_weight",
        "urgency_weight",
        "compensation_weight",
    ]
    
    updated = {}
    errors = []
    
    for key, value in new_weights.items():
        if key in valid_weights:
            if 0 <= value <= 1:
                setattr(scoring_engine.weights, key, value)
                updated[key] = value
            else:
                errors.append(f"{key}: value must be between 0 and 1")
        else:
            errors.append(f"{key}: unknown weight")
    
    # Validate weights sum to 1
    weights_valid = scoring_engine.weights.validate_weights()
    
    return {
        "success": len(errors) == 0 and weights_valid,
        "updated_weights": updated,
        "errors": errors,
        "weights_sum_valid": weights_valid,
        "message": "Weights updated" if len(errors) == 0 else "Some weights could not be updated",
    }


# Create ADK FunctionTools
score_opportunity_tool = FunctionTool(func=score_opportunity)
score_batch_tool = FunctionTool(func=score_batch)
get_tier_1_tool = FunctionTool(func=get_tier_1_opportunities)
explain_score_tool = FunctionTool(func=explain_score)
adjust_weights_tool = FunctionTool(func=adjust_weights)

# Export all scoring tools
scoring_tools = [
    score_opportunity_tool,
    score_batch_tool,
    get_tier_1_tool,
    explain_score_tool,
    adjust_weights_tool,
]
