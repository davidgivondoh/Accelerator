"""
ADK Tools module.

Contains all FunctionTools for the Growth Engine agents.
"""

from src.tools.search import (
    discovery_tools,
    filter_opportunities_tool,
    parse_opportunity_tool,
    scrape_opportunity_tool,
    search_opportunities_tool,
    store_opportunities_tool,
)
from src.tools.profile import (
    profile_tools,
    get_profile_tool,
    get_profile_summary_tool,
    get_skills_tool,
    get_experience_tool,
    get_preferences_tool,
    update_profile_tool,
    add_skill_tool,
    get_narrative_elements_tool,
)
from src.tools.scoring import (
    scoring_tools,
    score_opportunity_tool,
    score_batch_tool,
    get_tier_1_tool,
    explain_score_tool,
    adjust_weights_tool,
)
from src.tools.application import (
    application_tools,
    generate_essay,
    generate_cover_letter,
    generate_proposal,
    refine_content,
    evaluate_quality,
    create_application_draft,
    list_content_types,
)
from src.tools.outreach import (
    outreach_tools,
    generate_cold_email,
    generate_linkedin_message,
    generate_follow_up,
    generate_referral_request,
    generate_thank_you,
    create_outreach_sequence,
    get_outreach_types,
)

__all__ = [
    # Discovery tools
    "discovery_tools",
    "search_opportunities_tool",
    "scrape_opportunity_tool",
    "parse_opportunity_tool",
    "filter_opportunities_tool",
    "store_opportunities_tool",
    # Profile tools
    "profile_tools",
    "get_profile_tool",
    "get_profile_summary_tool",
    "get_skills_tool",
    "get_experience_tool",
    "get_preferences_tool",
    "update_profile_tool",
    "add_skill_tool",
    "get_narrative_elements_tool",
    # Scoring tools
    "scoring_tools",
    "score_opportunity_tool",
    "score_batch_tool",
    "get_tier_1_tool",
    "explain_score_tool",
    "adjust_weights_tool",
    # Application tools
    "application_tools",
    "generate_essay",
    "generate_cover_letter",
    "generate_proposal",
    "refine_content",
    "evaluate_quality",
    "create_application_draft",
    "list_content_types",
    # Outreach tools
    "outreach_tools",
    "generate_cold_email",
    "generate_linkedin_message",
    "generate_follow_up",
    "generate_referral_request",
    "generate_thank_you",
    "create_outreach_sequence",
    "get_outreach_types",
]
