"""
AI-Powered Cover Letter Template System

Creates highly personalized, contextually-aware cover letters using
intelligent templates, dynamic content generation, and quality optimization.
"""

from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime

from .base import BaseTemplate, TemplateEngine


class CoverLetterTemplate(BaseTemplate):
    """Advanced cover letter template with AI-powered personalization"""
    
    def __init__(self):
        self.template_engine = TemplateEngine()
        self.templates = self._load_advanced_templates()
    
    def get_template_type(self) -> str:
        return "cover_letter"
    
    def validate_context(self, context: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate required context for cover letter generation"""
        errors = []
        
        required_fields = ['company_name', 'position_title']
        for field in required_fields:
            if not context.get(field):
                errors.append(f"Missing required field: {field}")
        
        return len(errors) == 0, errors
    
    def generate(self, context: Dict[str, Any]) -> str:
        """Generate personalized cover letter"""
        
        # Validate context
        is_valid, errors = self.validate_context(context)
        if not is_valid:
            return f"Error: {'; '.join(errors)}"
        
        # Determine best template based on context
        template_type = self._select_template_type(context)
        template = self.templates[template_type]
        
        # Enhance context with dynamic content
        enhanced_context = self._enhance_context(context)
        
        # Render template
        jinja_template = self.template_engine.env.from_string(template)
        content = jinja_template.render(**enhanced_context)
        
        # Apply post-processing enhancements
        content = self._post_process_content(content, context)
        
        return content.strip()
    
    def _load_advanced_templates(self) -> Dict[str, str]:
        """Load advanced cover letter templates"""
        return {
            'professional': self._get_professional_template(),
            'startup': self._get_startup_template(),
            'academic': self._get_academic_template(),
            'creative': self._get_creative_template(),
            'technical': self._get_technical_template()
        }
    
    def _select_template_type(self, context: Dict[str, Any]) -> str:
        """Select best template type based on context"""
        
        company = context.get('company_name', '').lower()
        position = context.get('position_title', '').lower()
        tone = context.get('tone', 'professional').lower()
        
        # Check for specific industries/contexts
        if any(word in company + position for word in ['startup', 'tech startup', 'early stage']):
            return 'startup'
        elif any(word in position for word in ['research', 'professor', 'academic', 'phd', 'postdoc']):
            return 'academic'
        elif any(word in position for word in ['engineer', 'developer', 'software', 'technical', 'architect']):
            return 'technical'
        elif tone == 'creative' or any(word in position for word in ['creative', 'design', 'marketing', 'content']):
            return 'creative'
        else:
            return 'professional'
    
    def _enhance_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance context with dynamic content generation"""
        enhanced = context.copy()
        
        # Generate dynamic opening
        enhanced['dynamic_opening'] = self.template_engine._generate_opening(context)
        
        # Generate dynamic closing
        enhanced['dynamic_closing'] = self.template_engine._generate_closing(context)
        
        # Match skills to opportunity
        user_skills = context.get('user_skills', [])
        if user_skills:
            enhanced['matched_skills'] = self.template_engine._match_skills_to_opportunity(
                user_skills, context
            )
        else:
            enhanced['matched_skills'] = ['problem-solving', 'communication', 'teamwork']
        
        # Add formatted date
        enhanced['current_date'] = self.template_engine._format_date()
        
        # Add skill connectors for variety
        enhanced['skill_connector'] = self.template_engine.content_library['skill_connectors'][0]
        
        return enhanced
    
    def _post_process_content(self, content: str, context: Dict[str, Any]) -> str:
        """Apply post-processing enhancements to generated content"""
        
        tone = context.get('tone', 'professional')
        length = context.get('length', 'medium')
        
        # Apply tone adaptation
        content = self.template_engine._adapt_tone(content, tone)
        
        # Optimize length
        content = self.template_engine._optimize_content_length(content, length)
        
        # Enhance vocabulary
        content = self.template_engine._enhance_vocabulary(content, tone)
        
        # Add smooth transitions
        content = self.template_engine._add_smooth_transitions(content)
        
        # Personalize final content
        content = self.template_engine._personalize_content(content, context)
        
        return content
    
    def _get_professional_template(self) -> str:
        \"\"\"Professional cover letter template\"\"\"\n        return \"\"\"\n{{ current_date }}\n\nDear Hiring Manager,\n\n{{ dynamic_opening | adapt_tone('professional') }}\n\nWith my background in {{ matched_skills[0] }} and proven experience in {{ matched_skills[1] }}, I am confident I would be a valuable addition to your team. My experience has {{ skill_connector }} {{ matched_skills[2] }}, making me well-positioned to contribute to {{ company_name }}'s objectives.\n\n{% if user_skills|length > 3 %}\nThroughout my career, I have consistently demonstrated {{ matched_skills[0] }} while developing strong capabilities in {{ matched_skills[1] }}. This combination of skills, {{ skill_connector }} {{ matched_skills[2] }}, has enabled me to deliver exceptional results in challenging environments.\n{% endif %}\n\nI am particularly drawn to {{ company_name }} because of its reputation for innovation and excellence. The {{ position_title }} role aligns perfectly with my career goals and would allow me to leverage my expertise while contributing to your organization's continued success.\n\n{{ dynamic_closing | adapt_tone('professional') }} I would welcome the opportunity to discuss how my qualifications align with your needs.\n\nSincerely,\n[Your Name]\n\"\"\""
    
    def _get_startup_template(self) -> str:
        """Startup-focused cover letter template"""
        return """
{{ current_date }}

Hi {{ company_name }} Team,

{{ dynamic_opening | adapt_tone('casual') }}

I'm excited about the opportunity to join {{ company_name }} as {{ position_title }}. As someone passionate about {{ matched_skills[0] }} and experienced in {{ matched_skills[1] }}, I believe I can make an immediate impact on your growing team.

What attracts me most to {{ company_name }} is your innovative approach and rapid growth potential. My experience in {{ matched_skills[2] }} and ability to work in fast-paced environments makes me a great fit for your startup culture.

I thrive in environments where I can wear multiple hats, contribute to strategic decisions, and help scale operations. My background in {{ matched_skills[0] }} combined with my entrepreneurial mindset would be valuable as {{ company_name }} continues to expand.

{{ dynamic_closing | adapt_tone('casual') }} I'd love to discuss how I can contribute to {{ company_name }}'s mission and growth.

Best regards,
[Your Name]
"""
    
    def _get_academic_template(self) -> str:
        """Academic cover letter template"""
        return """
{{ current_date }}

Dear Search Committee,

{{ dynamic_opening | adapt_tone('academic') }}

My research expertise in {{ matched_skills[0] }} and extensive background in {{ matched_skills[1] }} position me well for the {{ position_title }} role at {{ company_name }}. My scholarly work has consistently demonstrated {{ matched_skills[2] }}, resulting in meaningful contributions to the field.

My research methodology emphasizes {{ matched_skills[0] }}, and I have successfully {{ skill_connector }} {{ matched_skills[1] }} throughout my academic career. This interdisciplinary approach has enabled me to address complex research questions and contribute to knowledge advancement.

I am particularly impressed by {{ company_name }}'s commitment to scholarly excellence and research innovation. The {{ position_title }} position would provide an ideal platform to further my research agenda while contributing to the institution's academic mission.

{{ dynamic_closing | adapt_tone('academic') }} I look forward to the opportunity to discuss my research vision and potential contributions to {{ company_name }}.

Respectfully yours,
[Your Name]
"""
    
    def _get_creative_template(self) -> str:
        """Creative industry cover letter template"""
        return """
{{ current_date }}

Hello {{ company_name }} Team,

{{ dynamic_opening | adapt_tone('creative') }}

As a creative professional with expertise in {{ matched_skills[0] }} and a passion for {{ matched_skills[1] }}, I'm thrilled about the {{ position_title }} opportunity at {{ company_name }}. My portfolio demonstrates {{ matched_skills[2] }} and reflects my commitment to innovative, impactful work.

What excites me about {{ company_name }} is your reputation for pushing creative boundaries and delivering exceptional results. My experience in {{ matched_skills[0] }} and collaborative approach to {{ matched_skills[1] }} would contribute to your team's continued creative success.

I believe great work comes from the intersection of creativity and strategy. My background has taught me to {{ skill_connector }} {{ matched_skills[2] }}, ensuring that creative solutions also drive business results.

{{ dynamic_closing | adapt_tone('creative') }} I'd love to share my portfolio and discuss how my creative vision aligns with {{ company_name }}'s goals.

Looking forward to connecting,
[Your Name]
"""
    
    def _get_technical_template(self) -> str:
        """Technical role cover letter template"""
        return """
{{ current_date }}

Dear Hiring Team,

{{ dynamic_opening | adapt_tone('professional') }}

With my technical expertise in {{ matched_skills[0] }} and hands-on experience with {{ matched_skills[1] }}, I am well-positioned to contribute to {{ company_name }}'s technology initiatives. My background has {{ skill_connector }} {{ matched_skills[2] }}, enabling me to tackle complex technical challenges effectively.

In my experience, successful technical solutions require both deep technical knowledge and strong problem-solving abilities. My proficiency in {{ matched_skills[0] }} combined with my experience in {{ matched_skills[1] }} has enabled me to design scalable, efficient systems that meet business objectives.

{{ company_name }}'s reputation for technical innovation and engineering excellence makes this {{ position_title }} role particularly appealing. I am excited about the opportunity to contribute to your technical team while continuing to grow my expertise in cutting-edge technologies.

{{ dynamic_closing | adapt_tone('professional') }} I would welcome the chance to discuss how my technical background aligns with your engineering needs.

Best regards,
[Your Name]
"""

# Legacy template support for backward compatibility
from src.templates.base import render_template

# =============================================================================
# LEGACY COVER LETTER TEMPLATES (for backward compatibility)
# =============================================================================

COVER_LETTER_TEMPLATES = {
    # Standard Professional Cover Letter
    "standard": """
You are writing a cover letter for {{ profile.name }} applying to {{ opportunity.title }} at {{ opportunity.organization }}.

## CANDIDATE PROFILE
Name: {{ profile.name }}
Current Role: {{ profile.current_role }}
Email: {{ profile.email }}
Location: {{ profile.location }}

### Professional Summary
{{ profile.summary }}

### Key Skills (Relevant to Role)
{{ profile.skills | highlight_skills(7) }}

### Top Achievements
{% for achievement in profile.achievements[:3] %}
- {{ achievement | format_achievement }}
{% endfor %}

### Relevant Experience
{% for exp in profile.experience[:2] %}
**{{ exp.title }}** at {{ exp.organization }} ({{ exp.start_date }} - {{ exp.end_date | default("Present") }})
{{ exp.description[:300] }}
{% endfor %}

## OPPORTUNITY DETAILS
Company: {{ opportunity.organization }}
Position: {{ opportunity.title }}
Location: {{ opportunity.location | default("Not specified") }}
Type: {{ opportunity.opportunity_type }}

### Job Description
{{ opportunity.description[:1000] }}

### Required Skills
{% if opportunity.requirements and opportunity.requirements.skills_required %}
{% for skill in opportunity.requirements.skills_required[:8] %}
- {{ skill }}
{% endfor %}
{% endif %}

## COVER LETTER INSTRUCTIONS

Write a {{ word_count | default(350) }}-word cover letter that follows this structure:

### Opening Paragraph (2-3 sentences)
- Hook with a specific, relevant accomplishment
- State the position and how you learned about it
- Express genuine enthusiasm (without being generic)

### Body Paragraph 1: Skill Match (4-5 sentences)
- Address 2-3 key requirements from the job description
- Provide specific evidence from your experience
- Quantify impact where possible

### Body Paragraph 2: Value Proposition (3-4 sentences)
- What unique perspective/skill you bring
- How you'll contribute beyond the basic requirements
- Show understanding of company challenges/goals

### Closing Paragraph (2-3 sentences)
- Reiterate interest and fit
- Call to action (interview request)
- Professional sign-off

### Formatting
- Professional but warm tone
- Active voice
- Specific examples, not generic claims
- Match the company's communication style

### DO NOT
- Start with "I am writing to apply..."
- Use "passionate" or overused buzzwords
- Repeat your resume verbatim
- Make it longer than requested
- Include salary expectations unless asked
""",

    # Startup/Early-Stage Cover Letter
    "startup": """
You are writing a startup-focused cover letter for {{ profile.name }}.

## CANDIDATE PROFILE
{{ profile.name }} - {{ profile.current_role }}
{{ profile.summary }}

### Entrepreneurial/Startup Experience
{% for exp in profile.experience if "startup" in exp.organization.lower() or "founder" in exp.title.lower() %}
- {{ exp.title }} at {{ exp.organization }}: {{ exp.description[:200] }}
{% endfor %}

### Technical Skills
{{ profile.skills | highlight_skills(10) }}

## STARTUP
Company: {{ opportunity.organization }}
Role: {{ opportunity.title }}
Stage: {{ company_info.stage | default("Startup") }}
{% if company_info %}
Funding: {{ company_info.funding | default("Not disclosed") }}
Mission: {{ company_info.mission }}
{% endif %}

## COVER LETTER INSTRUCTIONS

Write a {{ word_count | default(300) }}-word cover letter optimized for startups:

### Key Differences for Startups
- Shorter and more direct
- Emphasize versatility and ownership mentality
- Show you can handle ambiguity
- Demonstrate you've researched the specific problem they're solving

### Structure
1. **Opening Hook** - Something that shows you "get" their mission/product
2. **Relevant Experience** - Focus on impact, not titles
3. **Why This Stage** - Why you want startup vs. big company
4. **Founder Mindset Evidence** - Times you went beyond your job description
5. **Close** - Direct ask, show urgency

### Tone
- Conversational but professional
- High energy without being cringey
- Specific product/company knowledge
- Builder mentality

### Example Opening Hooks (adapt, don't copy)
- "I've been using [product] since [date] and noticed [specific observation]..."
- "Your recent [blog post/tweet/announcement] about [topic] resonated because..."
- "As someone who's [relevant experience], the problem you're solving is personal to me..."
""",

    # Fellowship/Program Application Letter
    "fellowship": """
You are writing a fellowship/program application letter for {{ profile.name }}.

## CANDIDATE PROFILE
{{ profile.name }}
{{ profile.current_role }}
{{ profile.summary }}

### Academic Background
{% for edu in profile.education %}
- {{ edu.degree }} in {{ edu.field }}, {{ edu.institution }} ({{ edu.year }})
  {% if edu.honors %}Honors: {{ edu.honors }}{% endif %}
{% endfor %}

### Research/Project Experience
{% for exp in profile.experience[:3] %}
- {{ exp.title }} at {{ exp.organization }}
{% endfor %}

### Achievements
{% for achievement in profile.achievements[:4] %}
- {{ achievement | format_achievement }}
{% endfor %}

## FELLOWSHIP DETAILS
Program: {{ opportunity.title }}
Organization: {{ opportunity.organization }}
Duration: {{ opportunity.duration | default("Not specified") }}
Focus Areas: {{ opportunity.requirements.focus_areas | join(", ") if opportunity.requirements and opportunity.requirements.focus_areas else "Various" }}

{{ opportunity.description[:800] }}

## LETTER INSTRUCTIONS

Write a {{ word_count | default(500) }}-word application letter that:

### Opening (100 words)
- State the specific fellowship and cohort/year
- Brief positioning statement (who you are in relation to program)
- Why this program specifically (not generically)

### Background & Qualifications (150 words)
- Relevant experience that qualifies you
- Key achievements that demonstrate readiness
- Skills that align with program goals

### Project/Goal Statement (150 words)
- What you plan to accomplish during the fellowship
- How it connects to your longer-term vision
- Why this program is essential to achieving it

### Community Contribution (100 words)
- What you'll contribute to the cohort
- Perspective/experience you bring
- How you'll stay engaged after the program

### Fellowship-Specific Notes
- Emphasize intellectual curiosity
- Show awareness of program alumni/outcomes
- Demonstrate fit with program values
- Be specific about what you'll do with the opportunity
"""
}

# =============================================================================
# RENDERING FUNCTIONS
# =============================================================================


def render_cover_letter_prompt(
    letter_type: str,
    profile: dict[str, Any],
    opportunity: dict[str, Any],
    word_count: int = 350,
    company_info: dict[str, Any] | None = None,
    **extra_context: Any,
) -> str:
    """
    Render a cover letter prompt template with context.
    
    Args:
        letter_type: Type of cover letter (standard, startup, fellowship)
        profile: User profile data
        opportunity: Opportunity details
        word_count: Target word count
        company_info: Optional company research data
        **extra_context: Additional context variables
        
    Returns:
        Rendered prompt ready for LLM
    """
    if letter_type not in COVER_LETTER_TEMPLATES:
        available = ", ".join(COVER_LETTER_TEMPLATES.keys())
        raise KeyError(f"Unknown letter type: {letter_type}. Available: {available}")
    
    template = COVER_LETTER_TEMPLATES[letter_type]
    
    context = {
        "profile": profile,
        "opportunity": opportunity,
        "word_count": word_count,
        "company_info": company_info,
        **extra_context,
    }
    
    return render_template(template, context)


def get_available_letter_types() -> list[str]:
    """Return list of available cover letter template types."""
    return list(COVER_LETTER_TEMPLATES.keys())
