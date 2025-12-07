"""
Agents module for the Growth Engine.

Contains all ADK agents:
- DiscoveryAgent: Finds opportunities across multiple sources
- ProfileAgent: Manages user profile and narrative elements
- ScoringAgent: Scores and prioritizes opportunities
- ApplicationAgent: Generates high-quality applications (Claude Opus 4.5)
- OutreachAgent: Handles networking and cold outreach
"""

from src.agents.discovery import create_discovery_agent, discovery_agent
from src.agents.profile import create_profile_agent, profile_agent
from src.agents.scoring import create_scoring_agent, scoring_agent
from src.agents.application import (
    create_application_agent,
    application_agent,
    generate_application_content,
)
from src.agents.outreach import (
    create_outreach_agent,
    outreach_agent,
    create_outreach_campaign,
)

__all__ = [
    # Discovery
    "create_discovery_agent",
    "discovery_agent",
    # Profile
    "create_profile_agent",
    "profile_agent",
    # Scoring
    "create_scoring_agent",
    "scoring_agent",
    # Application (Phase 2)
    "create_application_agent",
    "application_agent",
    "generate_application_content",
    # Outreach (Phase 2)
    "create_outreach_agent",
    "outreach_agent",
    "create_outreach_campaign",
]
