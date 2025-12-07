"""
Outreach Templates for Networking and Cold Emails.

Provides templates for:
- Cold emails to hiring managers
- LinkedIn connection messages
- Follow-up sequences
- Referral requests
- Thank you notes
"""

from typing import Any

from src.templates.base import render_template

# =============================================================================
# OUTREACH TEMPLATES
# =============================================================================

OUTREACH_TEMPLATES = {
    # Cold Email to Hiring Manager
    "cold_email": """
You are writing a cold email for {{ profile.name }} to reach out about an opportunity.

## SENDER PROFILE
{{ profile.name }}
{{ profile.current_role }}
{{ profile.email }}

### Key Credentials
{% for achievement in profile.achievements[:2] %}
- {{ achievement | format_achievement }}
{% endfor %}

### Relevant Experience
{{ profile.summary[:300] }}

## TARGET
Recipient: {{ recipient.name | default("Hiring Manager") }}
Title: {{ recipient.title | default("") }}
Company: {{ opportunity.organization }}
Role of Interest: {{ opportunity.title }}

## EMAIL INSTRUCTIONS

Write a {{ word_count | default(150) }}-word cold email that:

### Subject Line Options (provide 3)
- Specific and intriguing
- Reference a mutual connection, shared interest, or specific achievement
- Avoid spam triggers

### Email Structure

**Opening (1-2 sentences)**
- Establish relevance immediately
- Why you're reaching out to THEM specifically
- Optional: Mutual connection or shared context

**Value Hook (2-3 sentences)**
- One specific, impressive credential
- How it relates to their company/role
- What you bring that's unique

**Ask (1-2 sentences)**
- Specific, low-commitment request
- 15-minute call, coffee, or quick question
- Make it easy to say yes

**Closing (1 sentence)**
- Brief, professional
- Include availability

### Tone Guidelines
- Respectful of their time
- Confident but not arrogant
- Specific, not generic
- Human and genuine

### DO NOT
- Open with "I hope this email finds you well"
- Make it about you (make it about them)
- Ask for a job directly
- Write more than 150 words
- Attach your resume (unless requested)

### Example Openers (adapt, don't copy)
- "Your talk at [event] on [topic] changed how I think about [X]..."
- "I noticed [company] just [specific news] - congrats! I've been working on [related thing]..."
- "[Mutual connection] suggested I reach out about [specific topic]..."
""",

    # LinkedIn Connection Request
    "linkedin_connection": """
You are writing a LinkedIn connection request for {{ profile.name }}.

## SENDER
{{ profile.name }}
{{ profile.current_role }}

## RECIPIENT
{{ recipient.name | default("Professional") }}
{{ recipient.title | default("") }}
{{ recipient.company | default(opportunity.organization) }}

## CONNECTION CONTEXT
Reason: {{ connection_reason | default("shared interest in " + opportunity.organization) }}

## MESSAGE INSTRUCTIONS

Write a {{ word_count | default(280) }}-character LinkedIn connection message.

### Structure
1. **Personalized opener** (why them specifically)
2. **Common ground** (shared connection, interest, or background)
3. **Value statement** (what you bring to the connection)
4. **Soft ask** (connect and potentially chat)

### Character Limit: 280 characters for connection requests!

### Good Examples
- "Hi [Name], I loved your post on [topic]. As a fellow [shared background], I'd love to connect and learn more about your work at [company]."
- "Hi [Name], [Mutual connection] speaks highly of you. I'm exploring [area] and would value connecting with someone who's done [specific thing]."

### Avoid
- Generic "I'd like to add you to my network"
- Immediately asking for something
- Making it about you, not them
- Sales pitches
""",

    # Follow-up Email (After No Response)
    "follow_up": """
You are writing a follow-up email for {{ profile.name }}.

## CONTEXT
Original Email Sent: {{ original_date | default("1 week ago") }}
Recipient: {{ recipient.name | default("Hiring Manager") }}
Company: {{ opportunity.organization }}
Role: {{ opportunity.title }}

Original email summary: {{ original_summary | default("Cold outreach about the role") }}

## FOLLOW-UP INSTRUCTIONS

Write a {{ word_count | default(75) }}-word follow-up email.

### Timing Rules
- First follow-up: 5-7 days after original
- Second follow-up: 7-10 days after first
- Third follow-up: Final, 10-14 days later

### This is Follow-up #{{ follow_up_number | default(1) }}

### Structure
**Subject Line:** Re: [Original subject] OR "Quick follow-up"

**Body:**
1. Brief reference to previous email (1 sentence)
2. Add NEW value - news, insight, or update (1-2 sentences)  
3. Restate ask with easy out (1 sentence)

### Key Principles
- Add new value, don't just "bump"
- Keep it shorter than original
- Make it easy to respond
- Provide graceful exit ("if timing isn't right...")
- Stay positive, no guilt-tripping

### New Value Ideas
- Relevant news about their company
- New achievement or update from you
- Insight related to their work
- Shared article or resource
""",

    # Referral Request
    "referral_request": """
You are writing a referral request for {{ profile.name }}.

## SENDER
{{ profile.name }}
{{ profile.current_role }}

## CONTACT
{{ contact.name }}
Relationship: {{ contact.relationship | default("Professional connection") }}
Works at: {{ contact.company | default("") }}

## TARGET OPPORTUNITY
Company: {{ opportunity.organization }}
Role: {{ opportunity.title }}

## REQUEST INSTRUCTIONS

Write a {{ word_count | default(200) }}-word referral request email.

### Structure

**Opening**
- Personal greeting appropriate to relationship
- Brief catch-up or acknowledgment

**Context**
- What you're looking for
- Why this specific company/role
- Brief reminder of your relevant background

**The Ask**
- Specific request: referral, introduction, or advice
- Make it easy (offer to send materials)
- No pressure clause

**Closing**
- Gratitude
- Offer reciprocity
- Easy next step

### Making it Easy for Them
- Include a short blurb they can forward
- Attach resume or LinkedIn link
- Suggest what they could say

### Relationship-Appropriate Tone
- Close friend: Casual, direct
- Former colleague: Warm professional
- Acquaintance: Respectful, provide more context
- LinkedIn connection: Most formal, more explanation
""",

    # Thank You Note (After Interview)
    "thank_you": """
You are writing a post-interview thank you note for {{ profile.name }}.

## CONTEXT
Interviewer: {{ interviewer.name }}
Role: {{ interviewer.title | default("Interviewer") }}
Company: {{ opportunity.organization }}
Position: {{ opportunity.title }}
Interview Type: {{ interview_type | default("Interview") }}

### Interview Notes
{% if interview_notes %}
Topics Discussed:
{% for topic in interview_notes.topics %}
- {{ topic }}
{% endfor %}

Key Moments:
{% for moment in interview_notes.key_moments %}
- {{ moment }}
{% endfor %}
{% endif %}

## THANK YOU INSTRUCTIONS

Write a {{ word_count | default(150) }}-word thank you email.

### Timing
- Send within 24 hours of interview
- Evening of interview day is ideal

### Structure

**Subject Line**
"Thank you - {{ opportunity.title }} conversation" or similar

**Opening (1 sentence)**
- Express gratitude for their time
- Mention specific thing you enjoyed

**Substance (2-3 sentences)**
- Reference specific discussion point
- Reinforce your fit for a key requirement
- Add value: answer a question better, share relevant resource

**Closing (1-2 sentences)**
- Reaffirm interest and enthusiasm
- Look forward to next steps

### Key Principles
- Personalize to the specific interview
- Add new value, don't just repeat yourself
- Keep it concise and genuine
- Proofread carefully!

### If Multiple Interviewers
- Send individual emails to each
- Personalize each one differently
- Same-day timing for all
"""
}

# =============================================================================
# RENDERING FUNCTIONS
# =============================================================================


def render_outreach_prompt(
    outreach_type: str,
    profile: dict[str, Any],
    opportunity: dict[str, Any],
    recipient: dict[str, Any] | None = None,
    word_count: int = 150,
    **extra_context: Any,
) -> str:
    """
    Render an outreach prompt template with context.
    
    Args:
        outreach_type: Type of outreach (cold_email, linkedin_connection, etc.)
        profile: User profile data
        opportunity: Opportunity details
        recipient: Recipient information
        word_count: Target word count
        **extra_context: Additional context variables
        
    Returns:
        Rendered prompt ready for LLM
    """
    if outreach_type not in OUTREACH_TEMPLATES:
        available = ", ".join(OUTREACH_TEMPLATES.keys())
        raise KeyError(f"Unknown outreach type: {outreach_type}. Available: {available}")
    
    template = OUTREACH_TEMPLATES[outreach_type]
    
    context = {
        "profile": profile,
        "opportunity": opportunity,
        "recipient": recipient or {},
        "word_count": word_count,
        **extra_context,
    }
    
    return render_template(template, context)


def get_available_outreach_types() -> list[str]:
    """Return list of available outreach template types."""
    return list(OUTREACH_TEMPLATES.keys())
