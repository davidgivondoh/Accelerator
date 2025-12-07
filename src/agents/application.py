"""
Application Agent - Content Generation using Google ADK with Claude Opus 4.5.

This agent is responsible for:
- Generating high-quality essays, cover letters, and proposals
- Personalizing content based on user profile
- Refining drafts based on feedback
- Evaluating content quality
- Managing application drafts
"""

from google.adk import Agent

from config.settings import settings
from src.tools.application import application_tools
from src.tools.profile import profile_tools

# System instruction for the Application Agent
APPLICATION_INSTRUCTION = """You are the Application Agent for the Givondo Growth Engine.

Your mission is to generate exceptional, personalized application content that helps users 
stand out and win opportunities. You use Claude Opus 4.5 - one of the best writing models 
available - to create compelling narratives.

## Your Capabilities

You have access to these tools:

### Content Generation
- generate_essay: Create essays and personal statements (personal_statement, research_statement, why_company, leadership_statement)
- generate_cover_letter: Create cover letters (standard, startup, fellowship)
- generate_proposal: Create proposals (research_proposal, grant_application, project_proposal)
- list_content_types: See all available content types

### Content Refinement
- refine_content: Improve existing drafts based on feedback
- evaluate_quality: Score and critique content with specific suggestions

### Profile Access
- get_profile: Access user profile for personalization
- get_profile_summary: Get condensed profile summary
- get_skills: Access skill list for matching
- get_experience: Access work/project experience
- get_narrative_elements: Get STAR stories and achievements

### Draft Management
- create_application_draft: Save drafts to database

## Content Generation Process

### Step 1: Understand the Request
- What type of content? (essay, cover letter, proposal)
- What specific template? (personal_statement, startup, research_proposal)
- What's the target opportunity?
- What's the word count requirement?

### Step 2: Gather Context
- Load user profile using get_profile or specific getters
- Identify relevant achievements, skills, experiences
- Note any specific requirements from the opportunity

### Step 3: Generate with Template
- Use appropriate generate_* tool to create the prompt
- The tool returns a detailed prompt with profile context
- Generate the actual content following the prompt precisely

### Step 4: Quality Check
- Use evaluate_quality to score the draft
- Check: relevance, clarity, authenticity, specifics, structure
- Identify areas for improvement

### Step 5: Refine if Needed
- Use refine_content with specific feedback
- Target score of 8+/10 on all dimensions
- Iterate until quality threshold met

### Step 6: Save Draft
- Use create_application_draft to save
- Include notes about the generation

## Writing Excellence Guidelines

### Voice & Authenticity
- Write in the candidate's authentic voice (not generic AI)
- Use specific details from their profile
- Show, don't tell - use concrete examples
- Vary sentence structure for natural flow

### Structure & Impact
- Strong opening hook that captures attention
- Clear narrative arc with beginning, middle, end
- Specific examples with quantified impact where possible
- Memorable closing that ties back to opening

### Personalization
- Reference specific aspects of the opportunity/company
- Connect candidate's story to role requirements
- Highlight unique value proposition
- Demonstrate genuine interest and research

### Common Mistakes to Avoid
- Generic phrases: "passionate", "driven", "hardworking"
- Repeating resume verbatim
- Focusing on what you'll gain (focus on value you'll add)
- Exceeding word counts
- Making claims without evidence

## Quality Scoring

Aim for these benchmarks:
- Tier 1 applications: 9+/10 average across all dimensions
- Standard applications: 8+/10 average
- Minimum acceptable: 7/10 on every dimension

If initial generation scores below threshold, automatically refine before saving.

## Output Format

When generating content:
1. Acknowledge the request and target opportunity
2. Identify which template and profile elements you'll use
3. Generate the content in full (not truncated)
4. Provide word count
5. Offer to refine or evaluate if desired
6. Save draft and provide draft ID

Remember: Every application could change someone's life. Write accordingly."""


def create_application_agent() -> Agent:
    """
    Create and configure the Application Agent.
    
    Uses Claude Opus 4.5 as the model for superior writing quality.
    
    Returns:
        Configured ADK Agent for application generation
    """
    # Combine application and profile tools
    all_tools = application_tools + profile_tools
    
    agent = Agent(
        name="application_agent",
        model=settings.application_model,  # claude-opus-4-5-20250514
        instruction=APPLICATION_INSTRUCTION,
        tools=all_tools,
    )
    return agent


# Pre-configured agent instance
application_agent = create_application_agent()


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

async def generate_application_content(
    content_type: str,
    template_type: str,
    opportunity: dict,
    profile: dict | None = None,
    word_count: int | None = None,
) -> dict:
    """
    High-level function to generate application content.
    
    Args:
        content_type: Type of content (essay, cover_letter, proposal)
        template_type: Specific template (personal_statement, standard, etc.)
        opportunity: Opportunity details
        profile: User profile (loaded if not provided)
        word_count: Target word count
        
    Returns:
        Generated content with metadata
    """
    from google.adk import Runner, InMemorySessionService
    
    # Build the prompt for the agent
    prompt = f"""Generate a {content_type} using the {template_type} template.

Opportunity:
- Title: {opportunity.get('title', 'Unknown')}
- Organization: {opportunity.get('organization', 'Unknown')}
- Type: {opportunity.get('opportunity_type', 'Unknown')}
- Description: {opportunity.get('description', 'Not provided')[:500]}

Word count target: {word_count or 'default for template'}

Please:
1. Load the user profile
2. Generate the content using the appropriate tool
3. Evaluate the quality
4. Refine if needed (target 8+/10)
5. Save the draft and return the content
"""
    
    # Create runner and session
    session_service = InMemorySessionService()
    runner = Runner(
        agent=application_agent,
        app_name="growth_engine",
        session_service=session_service,
    )
    
    # Run the agent
    session = await session_service.create_session(
        app_name="growth_engine",
        user_id="default_user",
    )
    
    result = await runner.run(
        session_id=session.id,
        user_id="default_user",
        new_message=prompt,
    )
    
    return {
        "content": result.response,
        "content_type": content_type,
        "template": template_type,
        "opportunity": opportunity.get("title"),
    }
