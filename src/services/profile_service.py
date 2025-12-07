"""
Profile Service - Manages user profiles for opportunity matching.

Stores profiles in JSON files for simplicity (can be upgraded to database).
Provides CRUD operations and profile-based scoring.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List
import hashlib

from src.models.profile import Profile, Preferences, Skill, Experience, Education, Project


# Profile storage directory
PROFILES_DIR = Path(__file__).parent.parent.parent / "data" / "profiles"
PROFILES_DIR.mkdir(parents=True, exist_ok=True)

# Default profile path
DEFAULT_PROFILE_PATH = PROFILES_DIR / "default_profile.json"


def get_profile_path(profile_id: str = "default") -> Path:
    """Get the path to a profile file."""
    return PROFILES_DIR / f"{profile_id}_profile.json"


def generate_profile_id(email: str) -> str:
    """Generate a unique profile ID from email."""
    return hashlib.md5(email.lower().encode()).hexdigest()[:12]


def load_profile(profile_id: str = "default") -> Optional[Profile]:
    """Load a profile from storage."""
    profile_path = get_profile_path(profile_id)
    
    if not profile_path.exists():
        return None
    
    try:
        with open(profile_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return Profile(**data)
    except Exception as e:
        print(f"Error loading profile: {e}")
        return None


def save_profile(profile: Profile, profile_id: str = "default") -> bool:
    """Save a profile to storage."""
    profile_path = get_profile_path(profile_id)
    
    try:
        # Update timestamp
        profile.updated_at = datetime.utcnow()
        
        # Convert to dict and save
        data = profile.model_dump(mode="json")
        
        with open(profile_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, default=str)
        
        return True
    except Exception as e:
        print(f"Error saving profile: {e}")
        return False


def delete_profile(profile_id: str) -> bool:
    """Delete a profile from storage."""
    profile_path = get_profile_path(profile_id)
    
    if profile_path.exists():
        os.remove(profile_path)
        return True
    return False


def list_profiles() -> List[Dict[str, Any]]:
    """List all saved profiles."""
    profiles = []
    
    for file in PROFILES_DIR.glob("*_profile.json"):
        try:
            with open(file, "r", encoding="utf-8") as f:
                data = json.load(f)
            profiles.append({
                "id": file.stem.replace("_profile", ""),
                "name": data.get("full_name", "Unknown"),
                "email": data.get("email", ""),
                "headline": data.get("headline", ""),
                "updated_at": data.get("updated_at", "")
            })
        except:
            continue
    
    return profiles


def create_default_profile() -> Profile:
    """Create a default empty profile template."""
    return Profile(
        full_name="",
        email="",
        headline="",
        summary="",
        preferences=Preferences(
            open_to_remote=True,
            interested_in_jobs=True,
            interested_in_fellowships=True,
            interested_in_grants=True,
            interested_in_accelerators=True,
            interested_in_research=True,
        )
    )


def calculate_opportunity_match_score(
    profile: Profile,
    opportunity: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Calculate how well an opportunity matches a profile.
    
    Returns a score from 0-100 with breakdown.
    """
    scores = {
        "skills_match": 0,
        "location_match": 0,
        "type_match": 0,
        "preferences_match": 0,
        "experience_match": 0,
    }
    weights = {
        "skills_match": 0.35,
        "location_match": 0.15,
        "type_match": 0.20,
        "preferences_match": 0.15,
        "experience_match": 0.15,
    }
    
    opp_type = opportunity.get("opportunity_type", "").lower()
    opp_title = opportunity.get("title", "").lower()
    opp_desc = opportunity.get("description", "").lower()
    opp_location = opportunity.get("location", "").lower()
    opp_tags = [t.lower() for t in opportunity.get("tags", [])]
    is_remote = opportunity.get("remote", False)
    
    # 1. Skills Match (35%)
    profile_skills = [s.name.lower() for s in profile.skills]
    skill_matches = 0
    total_checks = len(profile_skills) if profile_skills else 1
    
    for skill in profile_skills:
        if skill in opp_title or skill in opp_desc or skill in opp_tags:
            skill_matches += 1
    
    scores["skills_match"] = min(100, (skill_matches / total_checks) * 150) if profile_skills else 50
    
    # 2. Location Match (15%)
    if is_remote and profile.preferences.open_to_remote:
        scores["location_match"] = 100
    elif profile.preferences.preferred_locations:
        for loc in profile.preferences.preferred_locations:
            if loc.lower() in opp_location:
                scores["location_match"] = 100
                break
        if scores["location_match"] == 0 and profile.preferences.open_to_relocation:
            scores["location_match"] = 60
    else:
        scores["location_match"] = 70  # No preference = neutral
    
    # 3. Type Match (20%)
    type_prefs = {
        "job": profile.preferences.interested_in_jobs,
        "fellowship": profile.preferences.interested_in_fellowships,
        "scholarship": profile.preferences.interested_in_fellowships,
        "grant": profile.preferences.interested_in_grants,
        "accelerator": profile.preferences.interested_in_accelerators,
        "hackathon": profile.preferences.interested_in_accelerators,
        "research": profile.preferences.interested_in_research,
    }
    
    if opp_type in type_prefs:
        scores["type_match"] = 100 if type_prefs.get(opp_type, True) else 20
    else:
        scores["type_match"] = 70  # Unknown type
    
    # 4. Preferences Match (15%)
    pref_score = 50
    
    # Target roles
    if profile.preferences.target_roles:
        for role in profile.preferences.target_roles:
            if role.lower() in opp_title:
                pref_score += 30
                break
    
    # Target companies
    opp_company = opportunity.get("company", "").lower()
    if profile.preferences.target_companies:
        for company in profile.preferences.target_companies:
            if company.lower() in opp_company:
                pref_score += 40
                break
    
    # Avoid companies
    if profile.preferences.avoid_companies:
        for company in profile.preferences.avoid_companies:
            if company.lower() in opp_company:
                pref_score -= 50
                break
    
    scores["preferences_match"] = max(0, min(100, pref_score))
    
    # 5. Experience Match (15%)
    years_exp = len(profile.experience)
    
    # Check if opportunity seems entry-level or senior
    if any(word in opp_title for word in ["senior", "lead", "principal", "staff", "director"]):
        scores["experience_match"] = min(100, years_exp * 20)
    elif any(word in opp_title for word in ["junior", "entry", "intern", "associate"]):
        scores["experience_match"] = 100 if years_exp <= 3 else 60
    else:
        scores["experience_match"] = 70  # Mid-level default
    
    # Calculate weighted total
    total_score = sum(scores[k] * weights[k] for k in scores)
    
    return {
        "total_score": round(total_score),
        "breakdown": scores,
        "weights": weights,
        "match_reasons": generate_match_reasons(profile, opportunity, scores)
    }


def generate_match_reasons(
    profile: Profile,
    opportunity: Dict[str, Any],
    scores: Dict[str, float]
) -> List[str]:
    """Generate human-readable reasons for the match."""
    reasons = []
    
    if scores["skills_match"] >= 70:
        reasons.append("Strong skills alignment")
    
    if scores["location_match"] >= 90:
        if opportunity.get("remote"):
            reasons.append("Remote friendly - matches your preference")
        else:
            reasons.append("Location matches your preferences")
    
    if scores["type_match"] >= 90:
        reasons.append(f"Matches your interest in {opportunity.get('opportunity_type', 'this type')}")
    
    if scores["preferences_match"] >= 80:
        if profile.preferences.target_companies:
            opp_company = opportunity.get("company", "")
            for tc in profile.preferences.target_companies:
                if tc.lower() in opp_company.lower():
                    reasons.append(f"Target company: {opp_company}")
                    break
    
    if not reasons:
        reasons.append("General opportunity match")
    
    return reasons


def get_profile_completeness(profile: Profile) -> Dict[str, Any]:
    """Calculate how complete a profile is."""
    sections = {
        "basic_info": {
            "filled": bool(profile.full_name and profile.email),
            "weight": 15,
            "items": ["full_name", "email", "phone", "location"]
        },
        "professional_summary": {
            "filled": bool(profile.headline and profile.summary),
            "weight": 20,
            "items": ["headline", "summary"]
        },
        "experience": {
            "filled": len(profile.experience) > 0,
            "weight": 20,
            "items": ["work history", "roles", "achievements"]
        },
        "education": {
            "filled": len(profile.education) > 0,
            "weight": 10,
            "items": ["degrees", "institutions"]
        },
        "skills": {
            "filled": len(profile.skills) >= 5,
            "weight": 15,
            "items": ["technical skills", "soft skills"]
        },
        "preferences": {
            "filled": bool(profile.preferences.target_roles or profile.preferences.preferred_locations),
            "weight": 10,
            "items": ["target roles", "locations", "salary"]
        },
        "narrative": {
            "filled": bool(profile.origin_story or profile.career_goals),
            "weight": 10,
            "items": ["origin story", "career goals", "unique value"]
        }
    }
    
    total_score = sum(
        s["weight"] if s["filled"] else 0
        for s in sections.values()
    )
    
    missing = [
        name for name, s in sections.items()
        if not s["filled"]
    ]
    
    return {
        "completeness_score": total_score,
        "sections": sections,
        "missing_sections": missing,
        "is_complete": total_score >= 80
    }


# Quick access functions
def get_current_profile() -> Optional[Profile]:
    """Get the current/default profile."""
    return load_profile("default")


def save_current_profile(profile: Profile) -> bool:
    """Save as the current/default profile."""
    return save_profile(profile, "default")
