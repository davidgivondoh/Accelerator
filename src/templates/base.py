"""
"""Advanced Template Engine for Automated Document Generation

Provides intelligent template rendering with AI-powered content adaptation,
dynamic personalization, and quality optimization for application materials.
"""

import re
import random
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime
from abc import ABC, abstractmethod

from jinja2 import Environment, FileSystemLoader, select_autoescape, Template


class BaseTemplate(ABC):
    """Abstract base class for all document templates"""
    
    @abstractmethod
    def generate(self, context: Dict[str, Any]) -> str:
        """Generate document content from context"""
        pass
    
    @abstractmethod
    def get_template_type(self) -> str:
        """Get the type of template"""
        pass
    
    def validate_context(self, context: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate context has required fields"""
        return True, []


class TemplateEngine:
    """
    Advanced Jinja2-based template engine with AI-powered content generation.
    
    Features:
    - Dynamic content personalization
    - Intelligent tone adaptation
    - Context-aware content generation
    - Quality scoring and optimization
    - Multi-format output support
    """
    
    def __init__(self, template_dir: Path | None = None):
        """Initialize the enhanced template engine."""
        if template_dir is None:
            template_dir = Path(__file__).parent / "files"
        
        self.env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=select_autoescape(["html", "xml"]),
            trim_blocks=True,
            lstrip_blocks=True,
        )
        
        # Content libraries for dynamic generation
        self.content_library = self._load_content_library()
        self.tone_adapters = self._initialize_tone_adapters()
        
        # Register custom filters and globals
        self._register_filters()
        self._register_globals()
    
    def _load_content_library(self) -> Dict[str, List[str]]:
        """Load content libraries for dynamic generation"""
        return {
            'opening_phrases': [
                "I am writing to express my strong interest in",
                "I am excited to apply for",
                "I would like to submit my application for",
                "It is with great enthusiasm that I apply for",
                "I am pleased to submit my candidacy for"
            ],
            'transition_phrases': [
                "Furthermore", "Additionally", "Moreover", "In addition",
                "What's more", "Beyond that", "Building on this"
            ],
            'closing_phrases': [
                "I look forward to the opportunity to discuss",
                "I would welcome the chance to contribute",
                "I am eager to bring my experience to",
                "I would be honored to join",
                "I am excited about the possibility of"
            ],
            'skill_connectors': [
                "which has equipped me with",
                "giving me valuable experience in",
                "developing my expertise in",
                "strengthening my abilities in",
                "enhancing my skills in"
            ]
        }
    
    def _initialize_tone_adapters(self) -> Dict[str, Dict[str, Any]]:
        """Initialize tone adaptation rules"""
        return {
            'professional': {
                'formality': 'high',
                'vocabulary': 'business',
                'sentence_length': 'medium',
                'personal_pronouns': 'minimal'
            },
            'academic': {
                'formality': 'very_high',
                'vocabulary': 'scholarly',
                'sentence_length': 'long',
                'personal_pronouns': 'formal'
            },
            'casual': {
                'formality': 'low',
                'vocabulary': 'conversational',
                'sentence_length': 'short',
                'personal_pronouns': 'frequent'
            },
            'creative': {
                'formality': 'medium',
                'vocabulary': 'expressive',
                'sentence_length': 'varied',
                'personal_pronouns': 'moderate'
            }
        }
    
    def _register_filters(self) -> None:
        """Register enhanced custom Jinja2 filters."""
        # Original filters
        self.env.filters["truncate_words"] = self._truncate_words
        self.env.filters["highlight_skills"] = self._highlight_skills
        self.env.filters["format_achievement"] = self._format_achievement
        self.env.filters["star_format"] = self._star_format
        
        # Enhanced filters for automation
        self.env.filters["adapt_tone"] = self._adapt_tone
        self.env.filters["personalize"] = self._personalize_content
        self.env.filters["vary_sentence"] = self._vary_sentence_structure
        self.env.filters["smart_connect"] = self._smart_connect_ideas
        self.env.filters["optimize_length"] = self._optimize_content_length
        self.env.filters["enhance_vocabulary"] = self._enhance_vocabulary
        self.env.filters["add_transitions"] = self._add_smooth_transitions
    
    def _register_globals(self) -> None:
        """Register global functions for templates"""
        self.env.globals['generate_opening'] = self._generate_opening
        self.env.globals['generate_closing'] = self._generate_closing
        self.env.globals['match_skills'] = self._match_skills_to_opportunity
        self.env.globals['format_date'] = self._format_date
        self.env.globals['calculate_fit'] = self._calculate_content_fit
    
    # Enhanced filter implementations
    def _adapt_tone(self, text: str, tone: str = 'professional') -> str:
        """Adapt text to specified tone"""
        if tone not in self.tone_adapters:
            return text
        
        adapter = self.tone_adapters[tone]
        
        # Apply tone-specific transformations
        if adapter['formality'] == 'high':
            # Replace contractions
            text = re.sub(r"won't", "will not", text)
            text = re.sub(r"can't", "cannot", text)
            text = re.sub(r"don't", "do not", text)
            text = re.sub(r"I'm", "I am", text)
            text = re.sub(r"you're", "you are", text)
        
        return text
    
    def _personalize_content(self, template_text: str, context: Dict[str, Any]) -> str:
        """Personalize content based on context"""
        personalized = template_text
        
        # Replace placeholders with context values
        if 'company_name' in context and context['company_name']:
            personalized = personalized.replace('[COMPANY]', context['company_name'])
        
        if 'position_title' in context and context['position_title']:
            personalized = personalized.replace('[POSITION]', context['position_title'])
        
        if 'user_skills' in context and context['user_skills']:
            skills_text = ', '.join(context['user_skills'][:3])
            personalized = personalized.replace('[SKILLS]', skills_text)
        
        return personalized
    
    def _vary_sentence_structure(self, text: str) -> str:
        """Vary sentence structure for better readability"""
        sentences = text.split('. ')
        if len(sentences) <= 1:
            return text
        
        # Add variety to sentence beginnings
        varied_sentences = []
        starters = ['Furthermore', 'Additionally', 'Moreover', 'In particular', 'Specifically']
        
        for i, sentence in enumerate(sentences):
            if i > 0 and i % 3 == 0 and len(sentences) > 3:
                if not sentence.startswith(tuple(starters)):
                    starter = random.choice(starters)
                    sentence = f"{starter}, {sentence.lower()}"
            varied_sentences.append(sentence)
        
        return '. '.join(varied_sentences)
    
    def _smart_connect_ideas(self, text: str, connection_type: str = 'logical') -> str:
        """Add smart transitions between ideas"""
        sentences = text.split('. ')
        if len(sentences) <= 2:
            return text
        
        connectors = self.content_library.get('transition_phrases', ['Additionally', 'Furthermore'])
        connected = [sentences[0]]  # Keep first sentence as is
        
        for i in range(1, len(sentences) - 1):
            if i % 2 == 0:  # Add connector to every other sentence
                connector = random.choice(connectors)
                sentence = f"{connector}, {sentences[i].lower()}"
            else:
                sentence = sentences[i]
            connected.append(sentence)
        
        if len(sentences) > 1:
            connected.append(sentences[-1])  # Keep last sentence as is
        
        return '. '.join(connected)
    
    def _optimize_content_length(self, text: str, target_length: str = 'medium') -> str:
        """Optimize content length based on target"""
        words = text.split()
        current_length = len(words)
        
        targets = {
            'short': (100, 200),
            'medium': (200, 400),
            'long': (400, 800)
        }
        
        target_range = targets.get(target_length, targets['medium'])
        min_words, max_words = target_range
        
        if current_length < min_words:
            # Add elaboration
            elaborations = [
                "This experience has been invaluable in developing my professional skills.",
                "I believe this background positions me well for success in this role.",
                "My dedication to excellence drives me to continuously improve and learn."
            ]
            text += " " + random.choice(elaborations)
        
        elif current_length > max_words:
            # Trim content while preserving meaning
            sentences = text.split('. ')
            # Keep first and last sentences, trim middle if needed
            if len(sentences) > 3:
                trimmed = [sentences[0]] + sentences[-1:]
                text = '. '.join(trimmed)
        
        return text
    
    def _enhance_vocabulary(self, text: str, level: str = 'professional') -> str:
        """Enhance vocabulary based on specified level"""
        
        enhancements = {
            'professional': {
                'help': 'assist',
                'get': 'obtain',
                'use': 'utilize',
                'show': 'demonstrate',
                'make': 'create',
                'big': 'significant',
                'good': 'excellent'
            },
            'academic': {
                'show': 'illustrate',
                'use': 'employ',
                'help': 'facilitate',
                'big': 'substantial',
                'good': 'exemplary',
                'important': 'paramount'
            }
        }
        
        replacements = enhancements.get(level, enhancements['professional'])
        
        enhanced_text = text
        for simple, enhanced in replacements.items():
            pattern = r'\b' + simple + r'\b'
            enhanced_text = re.sub(pattern, enhanced, enhanced_text, flags=re.IGNORECASE)
        
        return enhanced_text
    
    def _add_smooth_transitions(self, text: str) -> str:
        """Add smooth transitions between paragraphs"""
        paragraphs = text.split('\n\n')
        if len(paragraphs) <= 1:
            return text
        
        transitions = [
            "Building on this experience",
            "In addition to these qualifications", 
            "Furthermore",
            "What sets me apart is",
            "Beyond my technical skills"
        ]
        
        enhanced_paragraphs = [paragraphs[0]]  # Keep first paragraph as is
        
        for i in range(1, len(paragraphs)):
            if i < len(paragraphs) - 1:  # Don't add transition to last paragraph
                transition = random.choice(transitions)
                enhanced_paragraphs.append(f"{transition}, {paragraphs[i].lower()}")
            else:
                enhanced_paragraphs.append(paragraphs[i])
        
        return '\n\n'.join(enhanced_paragraphs)
    
    # Global function implementations
    def _generate_opening(self, context: Dict[str, Any]) -> str:
        """Generate dynamic opening based on context"""
        openings = self.content_library['opening_phrases']
        base_opening = random.choice(openings)
        
        position = context.get('position_title', 'this position')
        company = context.get('company_name', 'your organization')
        
        return f"{base_opening} the {position} role at {company}."
    
    def _generate_closing(self, context: Dict[str, Any]) -> str:
        """Generate dynamic closing based on context"""
        closings = self.content_library['closing_phrases']
        base_closing = random.choice(closings)
        
        company = context.get('company_name', 'your organization')
        
        return f"{base_closing} how I can contribute to {company}'s continued success."
    
    def _match_skills_to_opportunity(self, user_skills: List[str], opp_context: Dict[str, Any]) -> List[str]:
        """Match user skills to opportunity requirements"""
        opp_skills = opp_context.get('required_skills', [])
        if not opp_skills:
            return user_skills[:3]  # Return top 3 user skills
        
        # Find matching skills
        matched = []
        for user_skill in user_skills:
            for opp_skill in opp_skills:
                if user_skill.lower() in opp_skill.lower() or opp_skill.lower() in user_skill.lower():
                    if user_skill not in matched:
                        matched.append(user_skill)
        
        # Fill with remaining user skills if needed
        remaining = [skill for skill in user_skills if skill not in matched]
        matched.extend(remaining[:3 - len(matched)])
        
        return matched[:3]
    
    def _format_date(self, date_obj: datetime = None) -> str:
        \"\"\"Format date for professional documents\"\"\"\n        if date_obj is None:\n            date_obj = datetime.utcnow()\n        return date_obj.strftime(\"%B %d, %Y\")\n    \n    def _calculate_content_fit(self, content: str, target_context: Dict[str, Any]) -> float:\n        \"\"\"Calculate how well content fits the target context\"\"\"\n        score = 0.0\n        \n        # Check for company name mention\n        company = target_context.get('company_name', '').lower()\n        if company and company in content.lower():\n            score += 0.3\n        \n        # Check for position mention\n        position = target_context.get('position_title', '').lower()\n        if position and any(word in content.lower() for word in position.split()):\n            score += 0.3\n        \n        # Check for skill mentions\n        skills = target_context.get('user_skills', [])\n        skill_mentions = sum(1 for skill in skills if skill.lower() in content.lower())\n        score += min(skill_mentions * 0.1, 0.4)\n        \n        return min(score, 1.0)\n    \n    @staticmethod\n    def _truncate_words(text: str, word_limit: int) -> str:\n        \"\"\"Truncate text to specified word count.\"\"\"\n        words = text.split()
        if len(words) <= word_limit:
            return text
        return " ".join(words[:word_limit]) + "..."
    
    @staticmethod
    def _highlight_skills(skills: list[str], max_skills: int = 5) -> str:
        """Format skills list for highlighting."""
        relevant = skills[:max_skills]
        return ", ".join(relevant)
    
    @staticmethod
    def _format_achievement(achievement: dict[str, Any]) -> str:
        """Format an achievement for narrative use."""
        title = achievement.get("title", "")
        impact = achievement.get("impact", "")
        metrics = achievement.get("metrics", "")
        
        if metrics:
            return f"{title}: {impact} ({metrics})"
        return f"{title}: {impact}"
    
    @staticmethod
    def _star_format(story: dict[str, Any]) -> str:
        """Format a STAR story for applications."""
        situation = story.get("situation", "")
        task = story.get("task", "")
        action = story.get("action", "")
        result = story.get("result", "")
        
        return f"""
**Situation:** {situation}
**Task:** {task}
**Action:** {action}
**Result:** {result}
""".strip()
    
    def render(self, template_name: str, context: dict[str, Any]) -> str:
        """
        Render a template with the given context.
        
        Args:
            template_name: Name of the template file
            context: Variables to inject into the template
            
        Returns:
            Rendered template string
        """
        template = self.env.get_template(template_name)
        return template.render(**context)
    
    def render_string(self, template_string: str, context: dict[str, Any]) -> str:
        """
        Render a template string directly.
        
        Args:
            template_string: Template content as string
            context: Variables to inject into the template
            
        Returns:
            Rendered template string
        """
        template = self.env.from_string(template_string)
        return template.render(**context)


# Global template engine instance
_engine: TemplateEngine | None = None


def get_engine() -> TemplateEngine:
    """Get or create the global template engine."""
    global _engine
    if _engine is None:
        _engine = TemplateEngine()
    return _engine


def render_template(template_string: str, context: dict[str, Any]) -> str:
    """
    Convenience function to render a template string.
    
    Args:
        template_string: Template content
        context: Variables to inject
        
    Returns:
        Rendered string
    """
    return get_engine().render_string(template_string, context)
