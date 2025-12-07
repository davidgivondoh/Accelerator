"""
Prompt Templates Module for the Growth Engine.

Provides Jinja2-based templates for generating various application content:
- Essays and personal statements
- Cover letters
- Research proposals
- Grant applications
- Outreach messages

Templates support dynamic context injection from user profiles
and opportunity details.
"""

from src.templates.base import TemplateEngine, render_template
from src.templates.essays import (
    ESSAY_TEMPLATES,
    render_essay_prompt,
)
from src.templates.cover_letters import (
    COVER_LETTER_TEMPLATES,
    render_cover_letter_prompt,
)
from src.templates.proposals import (
    PROPOSAL_TEMPLATES,
    render_proposal_prompt,
)
from src.templates.outreach import (
    OUTREACH_TEMPLATES,
    render_outreach_prompt,
)

__all__ = [
    # Core
    "TemplateEngine",
    "render_template",
    # Essays
    "ESSAY_TEMPLATES",
    "render_essay_prompt",
    # Cover Letters
    "COVER_LETTER_TEMPLATES",
    "render_cover_letter_prompt",
    # Proposals
    "PROPOSAL_TEMPLATES",
    "render_proposal_prompt",
    # Outreach
    "OUTREACH_TEMPLATES",
    "render_outreach_prompt",
]
