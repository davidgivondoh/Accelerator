"""
Essay Templates for Application Generation.

Provides templates for:
- Personal statements
- Motivation essays
- Research statements
- Leadership narratives
- Why [Company/Program] essays
"""

from typing import Any

from src.templates.base import render_template

# =============================================================================
# ESSAY TEMPLATES
# =============================================================================

ESSAY_TEMPLATES = {
    # Personal Statement - General purpose
    "personal_statement": """
You are writing a compelling personal statement for {{ profile.name }}.

## CANDIDATE PROFILE
Name: {{ profile.name }}
Current Role: {{ profile.current_role }}
Target: {{ opportunity.title }} at {{ opportunity.organization }}

### Professional Summary
{{ profile.summary }}

### Key Skills
{{ profile.skills | highlight_skills }}

### Notable Achievements
{% for achievement in profile.achievements[:3] %}
- {{ achievement | format_achievement }}
{% endfor %}

### Education
{% for edu in profile.education %}
- {{ edu.degree }} in {{ edu.field }} from {{ edu.institution }} ({{ edu.year }})
{% endfor %}

## OPPORTUNITY DETAILS
Organization: {{ opportunity.organization }}
Role/Program: {{ opportunity.title }}
Description: {{ opportunity.description }}

{% if opportunity.requirements %}
### Requirements
{% for req in opportunity.requirements.skills_required[:5] %}
- {{ req }}
{% endfor %}
{% endif %}

## WRITING INSTRUCTIONS

Write a {{ word_count | default(500) }}-word personal statement that:

1. **Opens with a hook** - A compelling anecdote or insight that captures attention
2. **Establishes motivation** - Why this specific opportunity excites the candidate
3. **Demonstrates fit** - Connects the candidate's experience to the role requirements
4. **Shows growth** - Highlights a transformation or key learning moment
5. **Projects vision** - What the candidate will contribute and achieve
6. **Closes memorably** - Ties back to the opening with forward momentum

### Tone Guidelines
- Professional yet personable
- Confident but not arrogant
- Specific with concrete examples
- Authentic to the candidate's voice

### Must Include
- At least 2 specific achievements with metrics
- Connection to {{ opportunity.organization }}'s mission/values
- Clear articulation of career goals
- Evidence of relevant skills

DO NOT:
- Use clichés like "passionate" or "driven"
- Make generic statements that could apply to anyone
- Exceed the word count by more than 10%
- Include information not provided in the profile
""",

    # Research Statement
    "research_statement": """
You are writing a research statement for {{ profile.name }}.

## RESEARCHER PROFILE
Name: {{ profile.name }}
Current Position: {{ profile.current_role }}
Research Focus: {{ profile.research_interests | join(", ") if profile.research_interests else "AI/ML" }}

### Publications
{% for pub in profile.publications[:5] %}
- {{ pub.title }} ({{ pub.venue }}, {{ pub.year }})
{% endfor %}

### Research Experience
{% for exp in profile.experience[:3] if "research" in exp.title.lower() or "scientist" in exp.title.lower() %}
- {{ exp.title }} at {{ exp.organization }}: {{ exp.description[:200] }}...
{% endfor %}

## TARGET POSITION
Institution: {{ opportunity.organization }}
Position: {{ opportunity.title }}
Research Areas: {{ opportunity.requirements.research_areas | join(", ") if opportunity.requirements and opportunity.requirements.research_areas else "Open" }}

## WRITING INSTRUCTIONS

Write a {{ word_count | default(1000) }}-word research statement that:

1. **Research Vision** (200 words)
   - Articulate a compelling research agenda
   - Situate within the broader field
   - Explain the significance and potential impact

2. **Past Research** (300 words)
   - Highlight 2-3 key research contributions
   - Explain methodology and findings
   - Quantify impact where possible (citations, adoption, etc.)

3. **Future Directions** (300 words)
   - Propose specific research projects
   - Connect to the target institution's strengths
   - Identify potential collaborations

4. **Fit & Contribution** (200 words)
   - Explain why this institution specifically
   - What unique perspectives you bring
   - Teaching and mentorship plans

### Style Guidelines
- Technical but accessible
- Evidence-based claims
- Forward-looking vision
- Collaborative tone
""",

    # Why This Company/Program
    "why_company": """
You are writing a "Why {{ opportunity.organization }}?" essay for {{ profile.name }}.

## CANDIDATE PROFILE
{{ profile.name }} - {{ profile.current_role }}
{{ profile.summary }}

## TARGET
Company/Program: {{ opportunity.organization }}
Role: {{ opportunity.title }}
Type: {{ opportunity.opportunity_type }}

## COMPANY RESEARCH
{% if company_info %}
Mission: {{ company_info.mission }}
Values: {{ company_info.values | join(", ") }}
Recent News: {{ company_info.recent_news[:3] | join("; ") }}
Culture: {{ company_info.culture }}
{% else %}
[Research {{ opportunity.organization }} to add specific details]
{% endif %}

## WRITING INSTRUCTIONS

Write a {{ word_count | default(300) }}-word essay explaining why {{ profile.name }} is 
specifically interested in {{ opportunity.organization }}.

Structure:
1. **Specific Interest** (1 paragraph)
   - Name a specific project, product, paper, or initiative
   - Explain why it resonates personally

2. **Values Alignment** (1 paragraph)
   - Connect personal values to company values
   - Give an example of living those values

3. **Mutual Value** (1 paragraph)
   - What unique value you'll add
   - How you'll grow from this opportunity

Key Rules:
- Be SPECIFIC - generic answers are instantly rejected
- Show you've done research
- Connect your story to their story
- Avoid flattery without substance
""",

    # Leadership/Motivation Statement
    "leadership_statement": """
You are writing a leadership statement for {{ profile.name }}.

## PROFILE
{{ profile.name }} - {{ profile.current_role }}

### Leadership Experience
{% for exp in profile.experience if exp.leadership_examples %}
{{ exp.title }} at {{ exp.organization }}:
{% for example in exp.leadership_examples[:2] %}
- {{ example }}
{% endfor %}
{% endfor %}

### STAR Stories (Leadership)
{% for story in profile.star_stories if story.category == "leadership" %}
{{ story | star_format }}
---
{% endfor %}

## OPPORTUNITY
{{ opportunity.title }} at {{ opportunity.organization }}
{{ opportunity.description[:500] }}

## WRITING INSTRUCTIONS

Write a {{ word_count | default(500) }}-word leadership statement that:

1. **Define your leadership philosophy** (100 words)
   - What does leadership mean to you?
   - How has it evolved?

2. **Demonstrate with a story** (200 words)
   - Use the STAR format
   - Show impact on team/org
   - Include specific metrics

3. **Growth & Learning** (100 words)
   - A leadership challenge you faced
   - What you learned

4. **Future Vision** (100 words)
   - How you'll lead at {{ opportunity.organization }}
   - What impact you'll create

Avoid:
- Vague claims without evidence
- Focusing only on authority
- Ignoring collaboration and empathy
"""
}

# =============================================================================
# RENDERING FUNCTIONS
# =============================================================================


def render_essay_prompt(
    essay_type: str,
    profile: dict[str, Any],
    opportunity: dict[str, Any],
    word_count: int = 500,
    company_info: dict[str, Any] | None = None,
    **extra_context: Any,
) -> str:
    """
    Render an essay prompt template with context.
    
    Args:
        essay_type: Type of essay (personal_statement, research_statement, etc.)
        profile: User profile data
        opportunity: Opportunity details
        word_count: Target word count
        company_info: Optional company research data
        **extra_context: Additional context variables
        
    Returns:
        Rendered prompt ready for LLM
        
    Raises:
        KeyError: If essay_type is not found
    """
    if essay_type not in ESSAY_TEMPLATES:
        available = ", ".join(ESSAY_TEMPLATES.keys())
        raise KeyError(f"Unknown essay type: {essay_type}. Available: {available}")
    
    template = ESSAY_TEMPLATES[essay_type]
    
    context = {
        "profile": profile,
        "opportunity": opportunity,
        "word_count": word_count,
        "company_info": company_info,
        **extra_context,
    }
    
    return render_template(template, context)


def get_available_essay_types() -> list[str]:
    """Return list of available essay template types."""
    return list(ESSAY_TEMPLATES.keys())
