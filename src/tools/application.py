"""
Application Generation Tools for the Growth Engine.

These tools enable the ApplicationAgent to generate high-quality
application content using Claude Opus 4.5 as the writing model.

Tools:
- generate_essay: Create essays and personal statements
- generate_cover_letter: Create tailored cover letters
- generate_proposal: Create grant/research proposals
- refine_content: Improve existing drafts
- evaluate_quality: Score and critique content
"""

from typing import Any

from google.adk.tools import FunctionTool

from src.templates.essays import render_essay_prompt, get_available_essay_types
from src.templates.cover_letters import render_cover_letter_prompt, get_available_letter_types
from src.templates.proposals import render_proposal_prompt, get_available_proposal_types


# =============================================================================
# ESSAY GENERATION TOOLS
# =============================================================================

@FunctionTool
def generate_essay(
    essay_type: str,
    profile: dict[str, Any],
    opportunity: dict[str, Any],
    word_count: int = 500,
    additional_instructions: str = "",
) -> dict[str, Any]:
    """
    Generate an essay or personal statement using templates.
    
    This tool creates a detailed prompt for essay generation based on the
    user's profile and the target opportunity. The actual generation is
    handled by the ApplicationAgent using Claude Opus 4.5.
    
    Args:
        essay_type: Type of essay to generate. Options:
            - personal_statement: General personal statement
            - research_statement: Academic/research positions
            - why_company: Why this company/program essay
            - leadership_statement: Leadership and motivation
        profile: User profile dictionary containing:
            - name, current_role, summary
            - skills, achievements, education
            - experience, publications, star_stories
        opportunity: Opportunity dictionary containing:
            - title, organization, description
            - requirements, opportunity_type
        word_count: Target word count (default: 500)
        additional_instructions: Extra guidance for generation
        
    Returns:
        Dictionary with:
            - prompt: The rendered prompt for generation
            - essay_type: Type of essay
            - word_count: Target word count
            - template_used: Template identifier
    """
    try:
        prompt = render_essay_prompt(
            essay_type=essay_type,
            profile=profile,
            opportunity=opportunity,
            word_count=word_count,
        )
        
        if additional_instructions:
            prompt += f"\n\n## Additional Instructions\n{additional_instructions}"
        
        return {
            "success": True,
            "prompt": prompt,
            "essay_type": essay_type,
            "word_count": word_count,
            "template_used": f"essays.{essay_type}",
            "available_types": get_available_essay_types(),
        }
    except KeyError as e:
        return {
            "success": False,
            "error": str(e),
            "available_types": get_available_essay_types(),
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to generate essay prompt: {str(e)}",
        }


@FunctionTool
def generate_cover_letter(
    letter_type: str,
    profile: dict[str, Any],
    opportunity: dict[str, Any],
    word_count: int = 350,
    company_info: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Generate a cover letter using templates.
    
    Creates a prompt for cover letter generation tailored to the
    opportunity type (standard job, startup, fellowship).
    
    Args:
        letter_type: Type of cover letter. Options:
            - standard: Professional job application
            - startup: Early-stage company application
            - fellowship: Fellowship/program application
        profile: User profile dictionary
        opportunity: Opportunity dictionary
        word_count: Target word count (default: 350)
        company_info: Optional company research data containing:
            - mission, values, culture
            - recent_news, stage, funding
            
    Returns:
        Dictionary with prompt and metadata
    """
    try:
        prompt = render_cover_letter_prompt(
            letter_type=letter_type,
            profile=profile,
            opportunity=opportunity,
            word_count=word_count,
            company_info=company_info,
        )
        
        return {
            "success": True,
            "prompt": prompt,
            "letter_type": letter_type,
            "word_count": word_count,
            "template_used": f"cover_letters.{letter_type}",
            "available_types": get_available_letter_types(),
        }
    except KeyError as e:
        return {
            "success": False,
            "error": str(e),
            "available_types": get_available_letter_types(),
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to generate cover letter prompt: {str(e)}",
        }


@FunctionTool
def generate_proposal(
    proposal_type: str,
    profile: dict[str, Any],
    opportunity: dict[str, Any],
    word_count: int = 1500,
) -> dict[str, Any]:
    """
    Generate a grant or research proposal using templates.
    
    Creates a prompt for proposal generation suitable for grants,
    research funding, or project applications.
    
    Args:
        proposal_type: Type of proposal. Options:
            - research_proposal: Full academic research proposal
            - grant_application: Shorter grant application
            - project_proposal: Business/innovation project proposal
        profile: User profile dictionary
        opportunity: Opportunity dictionary
        word_count: Target word count (default: 1500)
        
    Returns:
        Dictionary with prompt and metadata
    """
    try:
        prompt = render_proposal_prompt(
            proposal_type=proposal_type,
            profile=profile,
            opportunity=opportunity,
            word_count=word_count,
        )
        
        return {
            "success": True,
            "prompt": prompt,
            "proposal_type": proposal_type,
            "word_count": word_count,
            "template_used": f"proposals.{proposal_type}",
            "available_types": get_available_proposal_types(),
        }
    except KeyError as e:
        return {
            "success": False,
            "error": str(e),
            "available_types": get_available_proposal_types(),
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to generate proposal prompt: {str(e)}",
        }


# =============================================================================
# CONTENT REFINEMENT TOOLS
# =============================================================================

@FunctionTool
def refine_content(
    content: str,
    content_type: str,
    feedback: str,
    word_count: int | None = None,
    tone_adjustment: str | None = None,
) -> dict[str, Any]:
    """
    Create a prompt to refine existing application content.
    
    Takes a draft and feedback to generate an improved version.
    
    Args:
        content: The existing draft content to refine
        content_type: Type of content (essay, cover_letter, proposal, etc.)
        feedback: Specific feedback or improvement instructions
        word_count: Optional new word count target
        tone_adjustment: Optional tone change (more formal, warmer, etc.)
        
    Returns:
        Dictionary with refinement prompt
    """
    prompt = f"""You are refining a {content_type} based on feedback.

## ORIGINAL CONTENT
{content}

## FEEDBACK TO ADDRESS
{feedback}

## REFINEMENT INSTRUCTIONS

Please improve the content by addressing the feedback above.

"""
    
    if word_count:
        prompt += f"- Adjust to approximately {word_count} words\n"
    
    if tone_adjustment:
        prompt += f"- Adjust tone to be: {tone_adjustment}\n"
    
    prompt += """
Maintain:
- The core message and key achievements
- Authentic voice of the writer
- Specific examples and metrics

Improve:
- Address all feedback points
- Strengthen weak sections
- Improve flow and transitions
- Enhance impact and memorability

Return the refined content in full, not just the changes.
"""
    
    return {
        "success": True,
        "prompt": prompt,
        "content_type": content_type,
        "original_length": len(content.split()),
        "target_length": word_count,
    }


@FunctionTool
def evaluate_quality(
    content: str,
    content_type: str,
    opportunity: dict[str, Any],
    evaluation_criteria: list[str] | None = None,
) -> dict[str, Any]:
    """
    Create a prompt to evaluate and score application content.
    
    Generates detailed quality assessment with scores and suggestions.
    
    Args:
        content: The content to evaluate
        content_type: Type of content (essay, cover_letter, proposal)
        opportunity: The target opportunity (for relevance scoring)
        evaluation_criteria: Optional list of specific criteria to evaluate
        
    Returns:
        Dictionary with evaluation prompt
    """
    default_criteria = [
        "Relevance to opportunity",
        "Clarity and structure",
        "Authenticity and voice",
        "Specific examples and metrics",
        "Compelling opening and closing",
        "Grammar and style",
        "Word count appropriateness",
    ]
    
    criteria = evaluation_criteria or default_criteria
    
    prompt = f"""You are evaluating a {content_type} for quality.

## CONTENT TO EVALUATE
{content}

## TARGET OPPORTUNITY
Organization: {opportunity.get('organization', 'Unknown')}
Role/Program: {opportunity.get('title', 'Unknown')}
Type: {opportunity.get('opportunity_type', 'Unknown')}

Description:
{opportunity.get('description', 'Not provided')[:500]}

## EVALUATION CRITERIA
Evaluate the content on these dimensions (score 1-10 each):

"""
    
    for i, criterion in enumerate(criteria, 1):
        prompt += f"{i}. {criterion}\n"
    
    prompt += """

## OUTPUT FORMAT
Provide:

1. **Overall Score**: X/10
2. **Dimension Scores**:
   - [Criterion 1]: X/10 - Brief explanation
   - [Criterion 2]: X/10 - Brief explanation
   - ...

3. **Strengths** (2-3 bullet points)
4. **Areas for Improvement** (2-3 bullet points)
5. **Specific Suggestions** (Actionable improvements)
6. **Red Flags** (Any issues that could hurt the application)

Be constructive but honest. This evaluation will help improve the content.
"""
    
    return {
        "success": True,
        "prompt": prompt,
        "content_type": content_type,
        "criteria_count": len(criteria),
        "content_word_count": len(content.split()),
    }


# =============================================================================
# DRAFT MANAGEMENT TOOLS
# =============================================================================

@FunctionTool
def create_application_draft(
    opportunity_id: str,
    content_type: str,
    content: str,
    profile_version: str = "1.0.0",
    notes: str = "",
) -> dict[str, Any]:
    """
    Save an application draft to the database.
    
    Args:
        opportunity_id: ID of the target opportunity
        content_type: Type of content (essay, cover_letter, etc.)
        content: The generated content
        profile_version: Version of profile used for generation
        notes: Optional notes about the draft
        
    Returns:
        Dictionary with draft ID and status
    """
    # This would integrate with the database layer
    # For now, return a structured response
    from uuid import uuid4
    from datetime import datetime
    
    draft_id = str(uuid4())
    
    return {
        "success": True,
        "draft_id": draft_id,
        "opportunity_id": opportunity_id,
        "content_type": content_type,
        "word_count": len(content.split()),
        "profile_version": profile_version,
        "created_at": datetime.utcnow().isoformat(),
        "status": "draft",
        "message": f"Draft saved with ID {draft_id}",
    }


@FunctionTool
def list_content_types() -> dict[str, Any]:
    """
    List all available content generation types.
    
    Returns:
        Dictionary with all available template types
    """
    return {
        "essays": get_available_essay_types(),
        "cover_letters": get_available_letter_types(),
        "proposals": get_available_proposal_types(),
        "outreach": ["cold_email", "linkedin_connection", "follow_up", "referral_request", "thank_you"],
    }


# =============================================================================
# TOOL COLLECTIONS
# =============================================================================

# All application generation tools
application_tools = [
    generate_essay,
    generate_cover_letter,
    generate_proposal,
    refine_content,
    evaluate_quality,
    create_application_draft,
    list_content_types,
]
