"""
Proposal Templates for Grant and Research Applications.

Provides templates for:
- Research proposals
- Grant applications
- Project proposals
- Budget narratives
"""

from typing import Any

from src.templates.base import render_template

# =============================================================================
# PROPOSAL TEMPLATES
# =============================================================================

PROPOSAL_TEMPLATES = {
    # Research Proposal
    "research_proposal": """
You are writing a research proposal for {{ profile.name }}.

## RESEARCHER PROFILE
Principal Investigator: {{ profile.name }}
Affiliation: {{ profile.current_organization | default(profile.current_role) }}
Email: {{ profile.email }}

### Research Background
{{ profile.summary }}

### Relevant Publications
{% for pub in profile.publications[:5] %}
- {{ pub.title }} ({{ pub.venue }}, {{ pub.year }})
{% endfor %}

### Previous Funding
{% for grant in profile.grants if profile.grants %}
- {{ grant.title }}: {{ grant.amount }} from {{ grant.funder }} ({{ grant.year }})
{% endfor %}

## FUNDING OPPORTUNITY
Funder: {{ opportunity.organization }}
Program: {{ opportunity.title }}
Award Amount: {{ opportunity.compensation.amount | default("Not specified") }}
Duration: {{ opportunity.duration | default("1-3 years") }}

### Focus Areas
{% if opportunity.requirements and opportunity.requirements.focus_areas %}
{% for area in opportunity.requirements.focus_areas %}
- {{ area }}
{% endfor %}
{% endif %}

### Description
{{ opportunity.description[:1500] }}

## PROPOSAL INSTRUCTIONS

Write a {{ word_count | default(2000) }}-word research proposal following this structure:

### 1. Executive Summary (150 words)
- Problem statement in one sentence
- Proposed solution/approach
- Expected outcomes and impact
- Funding request and timeline

### 2. Problem Statement & Significance (300 words)
- What is the problem?
- Why does it matter?
- What are the gaps in current solutions?
- Who benefits from solving this?

### 3. Research Objectives (200 words)
- Primary research question
- 3-4 specific aims/objectives
- Hypotheses to test (if applicable)
- Success metrics

### 4. Methodology (500 words)
- Research design and approach
- Data collection methods
- Analysis techniques
- Timeline and milestones
- Risk mitigation strategies

### 5. Preliminary Results (200 words)
- Relevant prior work
- Pilot data or proof of concept
- Why you're positioned to succeed

### 6. Expected Outcomes & Impact (250 words)
- Tangible deliverables
- Broader impacts (societal, scientific, economic)
- Dissemination plan
- Sustainability beyond grant period

### 7. Team & Resources (200 words)
- Key personnel and roles
- Available resources/facilities
- Collaborations and partnerships

### 8. Budget Justification (200 words)
- Personnel costs
- Equipment and supplies
- Travel and conferences
- Indirect costs
- Why each expense is necessary

### Style Guidelines
- Clear, jargon-free writing
- Quantified goals where possible
- Address funder's priorities explicitly
- Be ambitious but realistic
""",

    # Grant Application (Shorter Form)
    "grant_application": """
You are writing a grant application for {{ profile.name }}.

## APPLICANT PROFILE
{{ profile.name }}
{{ profile.current_role }}
{{ profile.summary[:500] }}

### Qualifications
{% for achievement in profile.achievements[:4] %}
- {{ achievement | format_achievement }}
{% endfor %}

## GRANT DETAILS
Funder: {{ opportunity.organization }}
Program: {{ opportunity.title }}
Amount: {{ opportunity.compensation.amount | default("Varies") }}

{{ opportunity.description[:1000] }}

## APPLICATION INSTRUCTIONS

Write a {{ word_count | default(1000) }}-word grant application:

### Project Title
[Generate a compelling, specific title]

### Abstract (150 words)
- Problem, approach, expected outcomes in brief

### Project Description (500 words)
- What you'll do
- How you'll do it
- Timeline and milestones
- Why you're the right person/team

### Budget Overview (150 words)
- Breakdown of funding use
- Justification for major items

### Impact Statement (200 words)
- Who benefits and how
- Metrics for success
- Long-term sustainability

### Tips
- Match the funder's language and priorities
- Be specific about deliverables
- Show you understand the field
- Include preliminary work if available
""",

    # Project Proposal (Business/Innovation)
    "project_proposal": """
You are writing a project proposal for {{ profile.name }}.

## PROPOSER PROFILE
{{ profile.name }}
{{ profile.current_role }}
{% if profile.startup %}
Company: {{ profile.startup.name }}
Stage: {{ profile.startup.stage }}
{% endif %}

### Background
{{ profile.summary }}

### Relevant Experience
{% for exp in profile.experience[:3] %}
- {{ exp.title }} at {{ exp.organization }}
{% endfor %}

## OPPORTUNITY
Program: {{ opportunity.title }}
Organization: {{ opportunity.organization }}
Type: {{ opportunity.opportunity_type }}

{{ opportunity.description[:800] }}

## PROPOSAL INSTRUCTIONS

Write a {{ word_count | default(1500) }}-word project proposal:

### 1. Executive Summary (200 words)
- The problem you're solving
- Your unique solution
- Market opportunity / impact potential
- What you're asking for

### 2. Problem Analysis (250 words)
- Problem description with specifics
- Who experiences this problem
- Current solutions and their limitations
- Market size or scope of impact

### 3. Proposed Solution (300 words)
- Your approach/product/innovation
- How it addresses the problem
- Unique value proposition
- Competitive advantages

### 4. Implementation Plan (300 words)
- Key milestones and timeline
- Required resources
- Team and capabilities
- Risk factors and mitigation

### 5. Impact & Metrics (200 words)
- Success metrics
- Expected outcomes
- Scalability potential
- Long-term vision

### 6. Team (150 words)
- Key team members and roles
- Relevant experience
- Advisory support

### 7. Ask & Use of Funds (100 words)
- Specific funding request
- Allocation breakdown
- Expected ROI or outcomes

### Tone
- Confident and ambitious
- Data-driven where possible
- Clear business/impact case
- Urgency without desperation
"""
}

# =============================================================================
# RENDERING FUNCTIONS
# =============================================================================


def render_proposal_prompt(
    proposal_type: str,
    profile: dict[str, Any],
    opportunity: dict[str, Any],
    word_count: int = 1500,
    **extra_context: Any,
) -> str:
    """
    Render a proposal prompt template with context.
    
    Args:
        proposal_type: Type of proposal (research_proposal, grant_application, etc.)
        profile: User profile data
        opportunity: Opportunity details
        word_count: Target word count
        **extra_context: Additional context variables
        
    Returns:
        Rendered prompt ready for LLM
    """
    if proposal_type not in PROPOSAL_TEMPLATES:
        available = ", ".join(PROPOSAL_TEMPLATES.keys())
        raise KeyError(f"Unknown proposal type: {proposal_type}. Available: {available}")
    
    template = PROPOSAL_TEMPLATES[proposal_type]
    
    context = {
        "profile": profile,
        "opportunity": opportunity,
        "word_count": word_count,
        **extra_context,
    }
    
    return render_template(template, context)


def get_available_proposal_types() -> list[str]:
    """Return list of available proposal template types."""
    return list(PROPOSAL_TEMPLATES.keys())
