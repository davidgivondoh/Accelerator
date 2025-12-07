"""
Outreach Tools for the Growth Engine.

These tools enable the OutreachAgent to generate and manage
networking communications including cold emails, LinkedIn messages,
and follow-up sequences.

Tools:
- generate_cold_email: Create personalized cold outreach emails
- generate_linkedin_message: Create LinkedIn connection requests
- generate_follow_up: Create follow-up messages
- generate_referral_request: Create referral request emails
- generate_thank_you: Create post-interview thank you notes
- schedule_outreach: Schedule outreach sequences
"""

from typing import Any
from datetime import datetime, timedelta

from google.adk.tools import FunctionTool

from src.templates.outreach import render_outreach_prompt, get_available_outreach_types


# =============================================================================
# OUTREACH GENERATION TOOLS
# =============================================================================

@FunctionTool
def generate_cold_email(
    profile: dict[str, Any],
    opportunity: dict[str, Any],
    recipient: dict[str, Any],
    word_count: int = 150,
) -> dict[str, Any]:
    """
    Generate a cold outreach email to a hiring manager or contact.
    
    Creates a concise, personalized email designed to get responses.
    Best practices: under 150 words, specific hook, clear ask.
    
    Args:
        profile: User profile dictionary
        opportunity: Target opportunity dictionary
        recipient: Recipient information containing:
            - name: Recipient's name
            - title: Their job title
            - company: Their company (if different from opportunity)
        word_count: Target word count (default: 150, max recommended)
        
    Returns:
        Dictionary with email prompt and metadata
    """
    try:
        prompt = render_outreach_prompt(
            outreach_type="cold_email",
            profile=profile,
            opportunity=opportunity,
            recipient=recipient,
            word_count=min(word_count, 200),  # Cap at 200 for cold emails
        )
        
        return {
            "success": True,
            "prompt": prompt,
            "outreach_type": "cold_email",
            "recipient": recipient.get("name", "Unknown"),
            "word_count": word_count,
            "tips": [
                "Send Tuesday-Thursday, 8-10 AM recipient's timezone",
                "Subject line should be specific and intriguing",
                "Follow up if no response in 5-7 days",
            ],
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to generate cold email: {str(e)}",
        }


@FunctionTool
def generate_linkedin_message(
    profile: dict[str, Any],
    opportunity: dict[str, Any],
    recipient: dict[str, Any],
    connection_reason: str = "",
) -> dict[str, Any]:
    """
    Generate a LinkedIn connection request message.
    
    Creates a brief, personalized message within LinkedIn's 280 character limit.
    
    Args:
        profile: User profile dictionary
        opportunity: Target opportunity dictionary
        recipient: Recipient information
        connection_reason: Why you want to connect (shared interest, mutual connection, etc.)
        
    Returns:
        Dictionary with message prompt and metadata
    """
    try:
        prompt = render_outreach_prompt(
            outreach_type="linkedin_connection",
            profile=profile,
            opportunity=opportunity,
            recipient=recipient,
            word_count=280,  # LinkedIn character limit
            connection_reason=connection_reason,
        )
        
        return {
            "success": True,
            "prompt": prompt,
            "outreach_type": "linkedin_connection",
            "recipient": recipient.get("name", "Unknown"),
            "character_limit": 280,
            "tips": [
                "Personalize based on their recent posts or activity",
                "Mention mutual connections if available",
                "Don't ask for anything in the connection request",
            ],
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to generate LinkedIn message: {str(e)}",
        }


@FunctionTool
def generate_follow_up(
    profile: dict[str, Any],
    opportunity: dict[str, Any],
    recipient: dict[str, Any],
    original_date: str,
    original_summary: str,
    follow_up_number: int = 1,
) -> dict[str, Any]:
    """
    Generate a follow-up email after no response.
    
    Creates a brief follow-up that adds new value rather than just "bumping."
    
    Args:
        profile: User profile dictionary
        opportunity: Target opportunity dictionary
        recipient: Recipient information
        original_date: When the original email was sent
        original_summary: Brief summary of the original email
        follow_up_number: Which follow-up this is (1, 2, or 3)
        
    Returns:
        Dictionary with follow-up prompt and timing advice
    """
    # Calculate recommended send time
    original = datetime.fromisoformat(original_date) if original_date else datetime.utcnow()
    
    follow_up_delays = {
        1: 5,   # 5 days for first follow-up
        2: 10,  # 10 days for second
        3: 14,  # 14 days for final
    }
    
    delay_days = follow_up_delays.get(follow_up_number, 7)
    recommended_send = original + timedelta(days=delay_days)
    
    try:
        prompt = render_outreach_prompt(
            outreach_type="follow_up",
            profile=profile,
            opportunity=opportunity,
            recipient=recipient,
            word_count=75,  # Follow-ups should be short
            original_date=original_date,
            original_summary=original_summary,
            follow_up_number=follow_up_number,
        )
        
        return {
            "success": True,
            "prompt": prompt,
            "outreach_type": "follow_up",
            "follow_up_number": follow_up_number,
            "max_follow_ups": 3,
            "recommended_send_date": recommended_send.isoformat(),
            "word_count": 75,
            "tips": [
                "Add new value - don't just bump",
                "Keep it shorter than the original",
                "Provide an easy exit if not interested",
            ],
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to generate follow-up: {str(e)}",
        }


@FunctionTool
def generate_referral_request(
    profile: dict[str, Any],
    opportunity: dict[str, Any],
    contact: dict[str, Any],
) -> dict[str, Any]:
    """
    Generate a referral request email to a professional contact.
    
    Creates a message asking for a referral or introduction.
    
    Args:
        profile: User profile dictionary
        opportunity: Target opportunity dictionary
        contact: Contact information containing:
            - name: Contact's name
            - relationship: How you know them (former colleague, etc.)
            - company: Where they work (if relevant)
            
    Returns:
        Dictionary with referral request prompt
    """
    try:
        prompt = render_outreach_prompt(
            outreach_type="referral_request",
            profile=profile,
            opportunity=opportunity,
            recipient=contact,  # Using contact as recipient
            word_count=200,
            contact=contact,
        )
        
        return {
            "success": True,
            "prompt": prompt,
            "outreach_type": "referral_request",
            "contact": contact.get("name", "Unknown"),
            "relationship": contact.get("relationship", "Professional connection"),
            "tips": [
                "Make it easy for them to say yes",
                "Offer to provide a blurb they can forward",
                "Express willingness to reciprocate",
            ],
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to generate referral request: {str(e)}",
        }


@FunctionTool
def generate_thank_you(
    profile: dict[str, Any],
    opportunity: dict[str, Any],
    interviewer: dict[str, Any],
    interview_type: str = "Interview",
    interview_notes: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Generate a post-interview thank you email.
    
    Creates a personalized thank you note referencing specific
    discussion points from the interview.
    
    Args:
        profile: User profile dictionary
        opportunity: Target opportunity dictionary
        interviewer: Interviewer information containing:
            - name: Interviewer's name
            - title: Their job title
        interview_type: Type of interview (Phone, Video, Onsite, etc.)
        interview_notes: Optional notes from the interview containing:
            - topics: List of topics discussed
            - key_moments: Notable moments to reference
            
    Returns:
        Dictionary with thank you email prompt
    """
    try:
        prompt = render_outreach_prompt(
            outreach_type="thank_you",
            profile=profile,
            opportunity=opportunity,
            recipient=interviewer,
            word_count=150,
            interviewer=interviewer,
            interview_type=interview_type,
            interview_notes=interview_notes,
        )
        
        return {
            "success": True,
            "prompt": prompt,
            "outreach_type": "thank_you",
            "interviewer": interviewer.get("name", "Unknown"),
            "interview_type": interview_type,
            "timing": "Send within 24 hours of interview",
            "tips": [
                "Reference a specific moment from the conversation",
                "Add value - answer a question better or share a resource",
                "If multiple interviewers, personalize each email",
            ],
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to generate thank you note: {str(e)}",
        }


# =============================================================================
# OUTREACH MANAGEMENT TOOLS
# =============================================================================

@FunctionTool
def create_outreach_sequence(
    profile: dict[str, Any],
    opportunity: dict[str, Any],
    recipient: dict[str, Any],
    sequence_type: str = "cold_outreach",
) -> dict[str, Any]:
    """
    Create a full outreach sequence with initial email and follow-ups.
    
    Generates a coordinated sequence of messages with optimal timing.
    
    Args:
        profile: User profile dictionary
        opportunity: Target opportunity dictionary
        recipient: Recipient information
        sequence_type: Type of sequence:
            - cold_outreach: Cold email + 2-3 follow-ups
            - warm_intro: Introduction request + follow-up
            - post_interview: Thank you + check-in
            
    Returns:
        Dictionary with sequence steps and timing
    """
    sequences = {
        "cold_outreach": [
            {"day": 0, "type": "cold_email", "description": "Initial cold email"},
            {"day": 5, "type": "follow_up", "number": 1, "description": "First follow-up with new value"},
            {"day": 12, "type": "follow_up", "number": 2, "description": "Second follow-up"},
            {"day": 20, "type": "follow_up", "number": 3, "description": "Final follow-up with graceful exit"},
        ],
        "warm_intro": [
            {"day": 0, "type": "referral_request", "description": "Ask for introduction"},
            {"day": 7, "type": "follow_up", "number": 1, "description": "Follow-up on intro request"},
        ],
        "post_interview": [
            {"day": 0, "type": "thank_you", "description": "Thank you email"},
            {"day": 7, "type": "follow_up", "number": 1, "description": "Check-in if no response"},
        ],
    }
    
    if sequence_type not in sequences:
        return {
            "success": False,
            "error": f"Unknown sequence type: {sequence_type}",
            "available_types": list(sequences.keys()),
        }
    
    sequence = sequences[sequence_type]
    start_date = datetime.utcnow()
    
    steps = []
    for step in sequence:
        send_date = start_date + timedelta(days=step["day"])
        steps.append({
            **step,
            "send_date": send_date.isoformat(),
            "status": "pending",
        })
    
    return {
        "success": True,
        "sequence_type": sequence_type,
        "recipient": recipient.get("name", "Unknown"),
        "opportunity": opportunity.get("title", "Unknown"),
        "steps": steps,
        "total_touchpoints": len(steps),
        "sequence_duration_days": max(step["day"] for step in sequence),
    }


@FunctionTool
def get_outreach_types() -> dict[str, Any]:
    """
    List all available outreach message types.
    
    Returns:
        Dictionary with available outreach types and their use cases
    """
    return {
        "success": True,
        "types": get_available_outreach_types(),
        "use_cases": {
            "cold_email": "Initial outreach to someone you don't know",
            "linkedin_connection": "LinkedIn connection request (280 char limit)",
            "follow_up": "Follow-up after no response (1-3 in a sequence)",
            "referral_request": "Asking a contact for a referral or introduction",
            "thank_you": "Post-interview thank you note",
        },
        "sequences": {
            "cold_outreach": "Full cold email sequence with follow-ups",
            "warm_intro": "Request for introduction from contact",
            "post_interview": "Thank you and follow-up after interview",
        },
    }


# =============================================================================
# TOOL COLLECTIONS
# =============================================================================

# All outreach tools
outreach_tools = [
    generate_cold_email,
    generate_linkedin_message,
    generate_follow_up,
    generate_referral_request,
    generate_thank_you,
    create_outreach_sequence,
    get_outreach_types,
]
