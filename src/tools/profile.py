"""
ADK Tools for profile management.

Contains FunctionTools for reading and updating user profile data.
"""

from datetime import datetime
from pathlib import Path
from typing import Any

import yaml
from google.adk.tools import FunctionTool

from src.models import Profile, Skill, Experience, Education, Preferences


# Default profile path
PROFILE_PATH = Path("config/profile_data.yaml")


def _load_profile_from_yaml() -> dict[str, Any] | None:
    """Load profile from YAML file."""
    if PROFILE_PATH.exists():
        with open(PROFILE_PATH, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    return None


def _save_profile_to_yaml(profile_data: dict[str, Any]) -> None:
    """Save profile to YAML file."""
    PROFILE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(PROFILE_PATH, "w", encoding="utf-8") as f:
        yaml.dump(profile_data, f, default_flow_style=False, allow_unicode=True)


async def get_profile() -> dict[str, Any]:
    """
    Get the current user profile.
    
    Returns:
        Complete user profile data including skills, experience, and preferences.
    """
    profile_data = _load_profile_from_yaml()
    
    if profile_data is None:
        return {
            "success": False,
            "message": "Profile not found. Please create a profile first.",
            "profile": None,
        }
    
    return {
        "success": True,
        "profile": profile_data,
        "timestamp": datetime.utcnow().isoformat(),
    }


async def get_profile_summary() -> dict[str, Any]:
    """
    Get a summary of the user profile for quick context.
    
    Returns:
        Condensed profile summary with key information.
    """
    profile_data = _load_profile_from_yaml()
    
    if profile_data is None:
        return {
            "success": False,
            "message": "Profile not found.",
            "summary": None,
        }
    
    # Extract key summary fields
    summary = {
        "name": profile_data.get("full_name", "Unknown"),
        "headline": profile_data.get("headline", ""),
        "location": profile_data.get("location", ""),
        "top_skills": [s.get("name") for s in profile_data.get("skills", [])[:10]],
        "years_experience": len(profile_data.get("experience", [])) * 2,  # Rough estimate
        "education_count": len(profile_data.get("education", [])),
        "target_roles": profile_data.get("preferences", {}).get("target_roles", []),
        "open_to_remote": profile_data.get("preferences", {}).get("open_to_remote", True),
    }
    
    return {
        "success": True,
        "summary": summary,
        "timestamp": datetime.utcnow().isoformat(),
    }


async def get_skills(category: str | None = None) -> dict[str, Any]:
    """
    Get skills from the user profile.
    
    Args:
        category: Optional category filter (e.g., "Programming", "ML/AI")
        
    Returns:
        List of skills, optionally filtered by category.
    """
    profile_data = _load_profile_from_yaml()
    
    if profile_data is None:
        return {"success": False, "message": "Profile not found.", "skills": []}
    
    skills = profile_data.get("skills", [])
    
    if category:
        skills = [s for s in skills if s.get("category", "").lower() == category.lower()]
    
    return {
        "success": True,
        "skills": skills,
        "count": len(skills),
        "categories": list(set(s.get("category", "Other") for s in profile_data.get("skills", []))),
    }


async def get_experience() -> dict[str, Any]:
    """
    Get work/research experience from the user profile.
    
    Returns:
        List of experience entries with details.
    """
    profile_data = _load_profile_from_yaml()
    
    if profile_data is None:
        return {"success": False, "message": "Profile not found.", "experience": []}
    
    experience = profile_data.get("experience", [])
    
    return {
        "success": True,
        "experience": experience,
        "count": len(experience),
        "current_role": next((e for e in experience if e.get("is_current")), None),
    }


async def get_preferences() -> dict[str, Any]:
    """
    Get user preferences for opportunity matching.
    
    Returns:
        User preferences including target roles, locations, and interests.
    """
    profile_data = _load_profile_from_yaml()
    
    if profile_data is None:
        return {"success": False, "message": "Profile not found.", "preferences": None}
    
    preferences = profile_data.get("preferences", {})
    
    return {
        "success": True,
        "preferences": preferences,
    }


async def update_profile(
    field: str,
    value: Any,
) -> dict[str, Any]:
    """
    Update a specific field in the user profile.
    
    Args:
        field: Field name to update (e.g., "headline", "summary", "career_goals")
        value: New value for the field
        
    Returns:
        Update result with success status.
    """
    profile_data = _load_profile_from_yaml()
    
    if profile_data is None:
        profile_data = {}
    
    # Update the field
    profile_data[field] = value
    profile_data["updated_at"] = datetime.utcnow().isoformat()
    
    # Save back
    _save_profile_to_yaml(profile_data)
    
    return {
        "success": True,
        "message": f"Updated {field} successfully.",
        "timestamp": datetime.utcnow().isoformat(),
    }


async def add_skill(
    name: str,
    category: str,
    proficiency: str = "Intermediate",
    years: int | None = None,
) -> dict[str, Any]:
    """
    Add a new skill to the profile.
    
    Args:
        name: Skill name (e.g., "Python", "Machine Learning")
        category: Skill category (e.g., "Programming", "ML/AI", "Soft Skills")
        proficiency: Proficiency level (Expert, Advanced, Intermediate, Beginner)
        years: Years of experience with this skill
        
    Returns:
        Result with updated skills list.
    """
    profile_data = _load_profile_from_yaml()
    
    if profile_data is None:
        profile_data = {"skills": []}
    
    if "skills" not in profile_data:
        profile_data["skills"] = []
    
    # Check if skill already exists
    existing = next((s for s in profile_data["skills"] if s.get("name", "").lower() == name.lower()), None)
    
    if existing:
        # Update existing skill
        existing["proficiency"] = proficiency
        if years:
            existing["years"] = years
        message = f"Updated existing skill: {name}"
    else:
        # Add new skill
        new_skill = {
            "name": name,
            "category": category,
            "proficiency": proficiency,
        }
        if years:
            new_skill["years"] = years
        profile_data["skills"].append(new_skill)
        message = f"Added new skill: {name}"
    
    profile_data["updated_at"] = datetime.utcnow().isoformat()
    _save_profile_to_yaml(profile_data)
    
    return {
        "success": True,
        "message": message,
        "skill_count": len(profile_data["skills"]),
    }


async def get_narrative_elements() -> dict[str, Any]:
    """
    Get narrative elements for consistent storytelling across applications.
    
    Returns:
        Origin story, key achievements, unique value proposition, and career goals.
    """
    profile_data = _load_profile_from_yaml()
    
    if profile_data is None:
        return {"success": False, "message": "Profile not found.", "narrative": None}
    
    narrative = {
        "origin_story": profile_data.get("origin_story"),
        "key_achievements": profile_data.get("key_achievements", []),
        "unique_value_proposition": profile_data.get("unique_value_proposition"),
        "career_goals": profile_data.get("career_goals"),
        "summary": profile_data.get("summary"),
    }
    
    return {
        "success": True,
        "narrative": narrative,
    }


# Create ADK FunctionTools
get_profile_tool = FunctionTool(func=get_profile)
get_profile_summary_tool = FunctionTool(func=get_profile_summary)
get_skills_tool = FunctionTool(func=get_skills)
get_experience_tool = FunctionTool(func=get_experience)
get_preferences_tool = FunctionTool(func=get_preferences)
update_profile_tool = FunctionTool(func=update_profile)
add_skill_tool = FunctionTool(func=add_skill)
get_narrative_elements_tool = FunctionTool(func=get_narrative_elements)

# Export all profile tools
profile_tools = [
    get_profile_tool,
    get_profile_summary_tool,
    get_skills_tool,
    get_experience_tool,
    get_preferences_tool,
    update_profile_tool,
    add_skill_tool,
    get_narrative_elements_tool,
]
