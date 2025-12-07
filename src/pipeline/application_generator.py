"""
Automated Application Generation System

Generates personalized applications, cover letters, essays, and other application
materials based on user profile, opportunity requirements, and AI templates.
"""

import json
import re
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod

from ..intelligence.user_profiles import global_profile_engine, UserProfile
from ..intelligence.nlp_processor import global_processor
from ..intelligence.success_prediction import global_success_predictor
from ..templates.base import BaseTemplate
from ..templates.cover_letters import CoverLetterTemplate
from ..templates.essays import EssayTemplate
from ..templates.proposals import ProposalTemplate


class ApplicationType(Enum):
    """Types of applications that can be generated"""
    JOB_APPLICATION = "job_application"
    GRANT_APPLICATION = "grant_application"
    SCHOLARSHIP_APPLICATION = "scholarship_application"
    FELLOWSHIP_APPLICATION = "fellowship_application"
    INTERNSHIP_APPLICATION = "internship_application"
    PROPOSAL_SUBMISSION = "proposal_submission"
    CONFERENCE_SUBMISSION = "conference_submission"


class DocumentType(Enum):
    """Types of documents that can be generated"""
    COVER_LETTER = "cover_letter"
    PERSONAL_STATEMENT = "personal_statement"
    RESEARCH_PROPOSAL = "research_proposal"
    PROJECT_DESCRIPTION = "project_description"
    MOTIVATION_LETTER = "motivation_letter"
    RESUME_SUMMARY = "resume_summary"
    PORTFOLIO_DESCRIPTION = "portfolio_description"


class GenerationMode(Enum):
    """Generation modes for different levels of automation"""
    FULLY_AUTOMATED = "fully_automated"    # Complete automation
    ASSISTED = "assisted"                  # Human review required
    TEMPLATE_BASED = "template_based"      # Use predefined templates
    CUSTOM = "custom"                      # Custom generation rules


@dataclass
class GenerationRequest:
    """Request for generating application materials"""
    user_id: str
    opportunity: Dict[str, Any]
    application_type: ApplicationType
    documents_needed: List[DocumentType]
    generation_mode: GenerationMode = GenerationMode.ASSISTED
    custom_requirements: Dict[str, Any] = field(default_factory=dict)
    tone: str = "professional"  # professional, casual, academic, creative
    length: str = "medium"      # short, medium, long, custom
    deadline: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'user_id': self.user_id,
            'opportunity_id': self.opportunity.get('id', ''),
            'application_type': self.application_type.value,
            'documents_needed': [doc.value for doc in self.documents_needed],
            'generation_mode': self.generation_mode.value,
            'custom_requirements': self.custom_requirements,
            'tone': self.tone,
            'length': self.length,
            'deadline': self.deadline.isoformat() if self.deadline else None
        }


@dataclass
class GeneratedDocument:
    """A generated document with metadata"""
    document_type: DocumentType
    title: str
    content: str
    word_count: int
    generation_metadata: Dict[str, Any]
    quality_score: float
    suggestions: List[str] = field(default_factory=list)
    generated_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'document_type': self.document_type.value,
            'title': self.title,
            'content': self.content,
            'word_count': self.word_count,
            'generation_metadata': self.generation_metadata,
            'quality_score': self.quality_score,
            'suggestions': self.suggestions,
            'generated_at': self.generated_at.isoformat()
        }


@dataclass
class ApplicationPackage:
    """Complete application package with all generated documents"""
    request: GenerationRequest
    documents: List[GeneratedDocument]
    overall_quality_score: float
    generation_summary: str
    recommendations: List[str]
    estimated_success_probability: float
    generated_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'request': self.request.to_dict(),
            'documents': [doc.to_dict() for doc in self.documents],
            'overall_quality_score': self.overall_quality_score,
            'generation_summary': self.generation_summary,
            'recommendations': self.recommendations,
            'estimated_success_probability': self.estimated_success_probability,
            'total_documents': len(self.documents),
            'total_word_count': sum(doc.word_count for doc in self.documents),
            'generated_at': self.generated_at.isoformat()
        }


class ContentGenerator(ABC):
    """Abstract base class for content generators"""
    
    @abstractmethod
    def generate_content(
        self, 
        user_profile: UserProfile, 
        opportunity: Dict[str, Any],
        requirements: Dict[str, Any]
    ) -> str:
        pass
    
    @abstractmethod
    def calculate_quality_score(self, content: str, requirements: Dict[str, Any]) -> float:
        pass


class CoverLetterGenerator(ContentGenerator):
    """Generates personalized cover letters"""
    
    def __init__(self):
        self.template = CoverLetterTemplate()
    
    def generate_content(
        self, 
        user_profile: UserProfile, 
        opportunity: Dict[str, Any],
        requirements: Dict[str, Any]
    ) -> str:
        """Generate a personalized cover letter"""
        
        # Extract opportunity details
        company_name = opportunity.get('company', 'the company')
        position_title = opportunity.get('title', 'this position')
        job_description = opportunity.get('description', '')
        
        # Get user's relevant experience and skills
        user_skills = user_profile.skills if user_profile.skills else ['problem-solving', 'communication', 'teamwork']
        
        # Extract key requirements from job description
        opportunity_intel = opportunity.get('intelligence', {})
        if not opportunity_intel:
            opportunity_intel = global_processor.classify_opportunity(job_description)
        
        required_skills = opportunity_intel.get('skills', [])
        opportunity_type = opportunity_intel.get('opportunity_type', 'position')
        
        # Find skill overlaps
        matching_skills = [skill for skill in user_skills if any(req_skill.lower() in skill.lower() for req_skill in required_skills)]
        if not matching_skills:
            matching_skills = user_skills[:3]  # Use top 3 user skills
        
        # Generate personalized content
        context = {
            'company_name': company_name,
            'position_title': position_title,
            'user_skills': matching_skills,
            'opportunity_type': opportunity_type,
            'tone': requirements.get('tone', 'professional'),
            'length': requirements.get('length', 'medium')
        }
        
        return self.template.generate(context)
    
    def calculate_quality_score(self, content: str, requirements: Dict[str, Any]) -> float:
        """Calculate quality score for cover letter"""
        
        score = 0.0
        
        # Length check
        word_count = len(content.split())
        target_length = requirements.get('length', 'medium')
        
        if target_length == 'short' and 150 <= word_count <= 250:
            score += 0.2
        elif target_length == 'medium' and 250 <= word_count <= 400:
            score += 0.2
        elif target_length == 'long' and 400 <= word_count <= 600:
            score += 0.2
        
        # Structure check
        paragraphs = content.split('\n\n')
        if len(paragraphs) >= 3:  # Introduction, body, conclusion
            score += 0.2
        
        # Professional tone check
        professional_indicators = [
            'sincerely', 'dear', 'thank you', 'opportunity', 'experience',
            'skills', 'contribute', 'team', 'company', 'position'
        ]
        found_indicators = sum(1 for indicator in professional_indicators if indicator in content.lower())
        score += min(found_indicators / len(professional_indicators), 0.3)
        
        # Personalization check
        if requirements.get('company_name', '').lower() in content.lower():
            score += 0.15
        
        if requirements.get('position_title', '').lower() in content.lower():
            score += 0.15
        
        return min(score, 1.0)


class PersonalStatementGenerator(ContentGenerator):
    """Generates personal statements and motivation letters"""
    
    def __init__(self):
        self.template = EssayTemplate()
    
    def generate_content(
        self, 
        user_profile: UserProfile, 
        opportunity: Dict[str, Any],
        requirements: Dict[str, Any]
    ) -> str:
        """Generate a personal statement"""
        
        # Determine the type of personal statement needed
        statement_type = requirements.get('statement_type', 'motivation')
        
        # Extract user background
        user_background = self._extract_user_background(user_profile)
        
        # Extract opportunity focus
        opportunity_focus = self._extract_opportunity_focus(opportunity)
        
        # Generate content based on type
        context = {
            'statement_type': statement_type,
            'user_background': user_background,
            'opportunity_focus': opportunity_focus,
            'tone': requirements.get('tone', 'professional'),
            'length': requirements.get('length', 'medium')
        }
        
        return self.template.generate(context)
    
    def _extract_user_background(self, user_profile: UserProfile) -> Dict[str, Any]:
        """Extract relevant background from user profile"""
        
        # Analyze user's interaction history for interests
        interests = []
        if user_profile.interaction_history:
            # Extract common opportunity types from interactions
            opp_types = [i.context.get('opportunity_type', '') for i in user_profile.interaction_history]
            interest_counts = {}
            for opp_type in opp_types:
                if opp_type:
                    interest_counts[opp_type] = interest_counts.get(opp_type, 0) + 1
            
            interests = sorted(interest_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        
        return {
            'skills': user_profile.skills if user_profile.skills else ['problem-solving', 'leadership'],
            'interests': [interest[0] for interest in interests],
            'experience_indicators': len(user_profile.interaction_history) > 20,
            'preferences': user_profile.preferences or {}
        }
    
    def _extract_opportunity_focus(self, opportunity: Dict[str, Any]) -> Dict[str, Any]:
        """Extract key focus areas from opportunity"""
        
        opportunity_intel = opportunity.get('intelligence', {})
        if not opportunity_intel:
            description = opportunity.get('description', '')
            opportunity_intel = global_processor.classify_opportunity(description)
        
        return {
            'type': opportunity_intel.get('opportunity_type', 'opportunity'),
            'skills_needed': opportunity_intel.get('skills', []),
            'focus_areas': opportunity_intel.get('categories', []),
            'organization': opportunity.get('company', opportunity.get('organization', 'organization'))
        }
    
    def calculate_quality_score(self, content: str, requirements: Dict[str, Any]) -> float:
        """Calculate quality score for personal statement"""
        
        score = 0.0
        
        # Length appropriateness
        word_count = len(content.split())
        target_length = requirements.get('length', 'medium')
        
        if target_length == 'short' and 200 <= word_count <= 350:
            score += 0.25
        elif target_length == 'medium' and 350 <= word_count <= 600:
            score += 0.25
        elif target_length == 'long' and 600 <= word_count <= 1000:
            score += 0.25
        
        # Narrative structure
        first_person_count = len(re.findall(r'\bI\b', content))
        if first_person_count >= 3:  # Should be personal
            score += 0.2
        
        # Goal-oriented content
        goal_indicators = ['goal', 'aspiration', 'aim', 'objective', 'vision', 'future', 'career']
        found_goals = sum(1 for goal in goal_indicators if goal in content.lower())
        score += min(found_goals / len(goal_indicators), 0.25)
        
        # Specific examples and experiences
        experience_indicators = ['experience', 'project', 'worked', 'developed', 'led', 'achieved']
        found_experiences = sum(1 for exp in experience_indicators if exp in content.lower())
        score += min(found_experiences / len(experience_indicators), 0.3)
        
        return min(score, 1.0)


class ProposalGenerator(ContentGenerator):
    """Generates research proposals and project descriptions"""
    
    def __init__(self):
        self.template = ProposalTemplate()
    
    def generate_content(
        self, 
        user_profile: UserProfile, 
        opportunity: Dict[str, Any],
        requirements: Dict[str, Any]
    ) -> str:
        """Generate a research/project proposal"""
        
        # Extract proposal requirements
        proposal_type = requirements.get('proposal_type', 'research')
        
        # Analyze opportunity for research areas
        opportunity_intel = opportunity.get('intelligence', {})
        if not opportunity_intel:
            description = opportunity.get('description', '')
            opportunity_intel = global_processor.classify_opportunity(description)
        
        # Generate proposal context
        context = {
            'proposal_type': proposal_type,
            'research_area': opportunity_intel.get('opportunity_type', 'research'),
            'skills_available': user_profile.skills if user_profile.skills else ['research', 'analysis'],
            'opportunity_focus': opportunity_intel.get('categories', []),
            'organization': opportunity.get('company', opportunity.get('organization', 'institution')),
            'tone': requirements.get('tone', 'academic'),
            'length': requirements.get('length', 'long')
        }
        
        return self.template.generate(context)
    
    def calculate_quality_score(self, content: str, requirements: Dict[str, Any]) -> float:
        """Calculate quality score for proposals"""
        
        score = 0.0
        
        # Academic structure check
        sections = content.split('\n\n')
        if len(sections) >= 4:  # Should have multiple clear sections
            score += 0.3
        
        # Technical content indicators
        technical_terms = ['methodology', 'approach', 'framework', 'analysis', 'implementation', 'evaluation']
        found_technical = sum(1 for term in technical_terms if term in content.lower())
        score += min(found_technical / len(technical_terms), 0.4)
        
        # Objective and measurable language
        objective_indicators = ['will', 'shall', 'objective', 'goal', 'measure', 'evaluate', 'assess']
        found_objectives = sum(1 for obj in objective_indicators if obj in content.lower())
        score += min(found_objectives / len(objective_indicators), 0.3)
        
        return min(score, 1.0)


class ApplicationGenerator:
    """Main application generation engine"""
    
    def __init__(self):
        self.generators = {
            DocumentType.COVER_LETTER: CoverLetterGenerator(),
            DocumentType.PERSONAL_STATEMENT: PersonalStatementGenerator(),
            DocumentType.MOTIVATION_LETTER: PersonalStatementGenerator(),
            DocumentType.RESEARCH_PROPOSAL: ProposalGenerator(),
            DocumentType.PROJECT_DESCRIPTION: ProposalGenerator(),
        }
    
    def generate_application_package(self, request: GenerationRequest) -> ApplicationPackage:
        """Generate complete application package"""
        
        # Get user profile
        user_profile = global_profile_engine.get_profile(request.user_id)
        if not user_profile:
            raise ValueError(f"User profile not found: {request.user_id}")
        
        # Generate each requested document
        generated_documents = []
        
        for document_type in request.documents_needed:
            try:
                document = self.generate_document(
                    document_type, user_profile, request.opportunity, request
                )
                generated_documents.append(document)
            except Exception as e:
                # Create placeholder document for failed generations
                error_doc = GeneratedDocument(
                    document_type=document_type,
                    title=f"Error generating {document_type.value}",
                    content=f"Failed to generate document: {str(e)}",
                    word_count=0,
                    generation_metadata={'error': str(e)},
                    quality_score=0.0,
                    suggestions=[f"Manual creation required for {document_type.value}"]
                )
                generated_documents.append(error_doc)
        
        # Calculate overall quality
        quality_scores = [doc.quality_score for doc in generated_documents if doc.quality_score > 0]
        overall_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0.0
        
        # Get success prediction
        success_prediction = 0.5  # Default
        try:
            prediction_result = global_success_predictor.predict_application_success(
                request.user_id, request.opportunity
            )
            success_prediction = prediction_result.success_probability
        except:
            pass
        
        # Generate summary and recommendations
        summary = self._generate_summary(generated_documents, overall_quality)
        recommendations = self._generate_recommendations(generated_documents, request)
        
        return ApplicationPackage(
            request=request,
            documents=generated_documents,
            overall_quality_score=overall_quality,
            generation_summary=summary,
            recommendations=recommendations,
            estimated_success_probability=success_prediction
        )
    
    def generate_document(
        self, 
        document_type: DocumentType, 
        user_profile: UserProfile,
        opportunity: Dict[str, Any],
        request: GenerationRequest
    ) -> GeneratedDocument:
        """Generate a single document"""
        
        if document_type not in self.generators:
            raise ValueError(f"No generator available for {document_type.value}")
        
        generator = self.generators[document_type]
        
        # Prepare requirements for generator
        requirements = {
            'tone': request.tone,
            'length': request.length,
            'company_name': opportunity.get('company', ''),
            'position_title': opportunity.get('title', ''),
            **request.custom_requirements
        }
        
        # Generate content
        content = generator.generate_content(user_profile, opportunity, requirements)
        
        # Calculate quality score
        quality_score = generator.calculate_quality_score(content, requirements)
        
        # Generate suggestions for improvement
        suggestions = self._generate_improvement_suggestions(content, quality_score, document_type)
        
        # Create title
        title = self._generate_document_title(document_type, opportunity)
        
        return GeneratedDocument(
            document_type=document_type,
            title=title,
            content=content,
            word_count=len(content.split()),
            generation_metadata={
                'generator_type': generator.__class__.__name__,
                'requirements': requirements,
                'generation_mode': request.generation_mode.value
            },
            quality_score=quality_score,
            suggestions=suggestions
        )
    
    def _generate_document_title(self, document_type: DocumentType, opportunity: Dict[str, Any]) -> str:
        """Generate appropriate title for document"""
        
        company = opportunity.get('company', 'Company')
        position = opportunity.get('title', 'Position')
        
        title_templates = {
            DocumentType.COVER_LETTER: f"Cover Letter - {position} at {company}",
            DocumentType.PERSONAL_STATEMENT: f"Personal Statement - {position}",
            DocumentType.MOTIVATION_LETTER: f"Motivation Letter - {position}",
            DocumentType.RESEARCH_PROPOSAL: f"Research Proposal - {position}",
            DocumentType.PROJECT_DESCRIPTION: f"Project Description - {position}",
            DocumentType.RESUME_SUMMARY: f"Resume Summary - {position}",
            DocumentType.PORTFOLIO_DESCRIPTION: f"Portfolio Description - {position}"
        }
        
        return title_templates.get(document_type, f"{document_type.value.replace('_', ' ').title()} - {position}")
    
    def _generate_improvement_suggestions(
        self, 
        content: str, 
        quality_score: float, 
        document_type: DocumentType
    ) -> List[str]:
        """Generate suggestions for improving the document"""
        
        suggestions = []
        
        # General quality suggestions
        if quality_score < 0.6:
            suggestions.append("Consider reviewing and enhancing the content for better quality")
        
        # Length-based suggestions
        word_count = len(content.split())
        if word_count < 150:
            suggestions.append("Content might be too brief - consider adding more details")
        elif word_count > 800:
            suggestions.append("Content might be too lengthy - consider condensing key points")
        
        # Document-specific suggestions
        if document_type == DocumentType.COVER_LETTER:
            if 'sincerely' not in content.lower() and 'best regards' not in content.lower():
                suggestions.append("Add a professional closing (e.g., 'Sincerely' or 'Best regards')")
        
        elif document_type in [DocumentType.PERSONAL_STATEMENT, DocumentType.MOTIVATION_LETTER]:
            if len(re.findall(r'\bI\b', content)) < 3:
                suggestions.append("Make the statement more personal by using 'I' statements")
        
        elif document_type == DocumentType.RESEARCH_PROPOSAL:
            if 'methodology' not in content.lower():
                suggestions.append("Include a clear methodology section")
        
        # If no specific suggestions, add encouragement
        if not suggestions and quality_score > 0.7:
            suggestions.append("Great work! The document looks well-structured and professional")
        
        return suggestions
    
    def _generate_summary(self, documents: List[GeneratedDocument], overall_quality: float) -> str:
        """Generate summary of the application package"""
        
        doc_count = len(documents)
        total_words = sum(doc.word_count for doc in documents)
        
        quality_description = (
            "excellent" if overall_quality > 0.8 else
            "good" if overall_quality > 0.6 else
            "acceptable" if overall_quality > 0.4 else
            "needs improvement"
        )
        
        return (
            f"Generated {doc_count} documents with {total_words} total words. "
            f"Overall quality assessment: {quality_description} ({overall_quality:.1%}). "
            f"Package ready for review and submission."
        )
    
    def _generate_recommendations(
        self, 
        documents: List[GeneratedDocument], 
        request: GenerationRequest
    ) -> List[str]:
        """Generate recommendations for the application package"""
        
        recommendations = []
        
        # Quality-based recommendations
        low_quality_docs = [doc for doc in documents if doc.quality_score < 0.5]
        if low_quality_docs:
            recommendations.append(f"Review and improve {len(low_quality_docs)} documents with lower quality scores")
        
        # Deadline-based recommendations
        if request.deadline:
            time_until_deadline = request.deadline - datetime.utcnow()
            if time_until_deadline.days < 1:
                recommendations.append("URGENT: Deadline is within 24 hours - prioritize final review")
            elif time_until_deadline.days < 3:
                recommendations.append("Deadline approaching - schedule final review session")
        
        # Mode-based recommendations
        if request.generation_mode == GenerationMode.FULLY_AUTOMATED:
            recommendations.append("Review automated content for accuracy and personalization")
        
        # General recommendations
        recommendations.extend([
            "Proofread all documents for grammar and spelling",
            "Customize content further based on specific opportunity requirements",
            "Get feedback from a mentor or colleague before submitting"
        ])
        
        return recommendations[:5]  # Limit to top 5 recommendations


# Global application generator
global_application_generator = ApplicationGenerator()