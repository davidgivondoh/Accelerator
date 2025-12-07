"""
Interview Preparation Agent
===========================

AI-powered interview preparation and practice system.

Features:
- Interview question generation based on opportunity/role
- Mock interview sessions with AI interviewer
- Response coaching and feedback
- Behavioral question preparation (STAR method)
- Technical question practice
- Company-specific research and insights
- Confidence scoring and improvement tracking
"""

import asyncio
import json
import random
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional
import hashlib

from pydantic import BaseModel, Field


# =============================================================================
# ENUMS & TYPES
# =============================================================================

class InterviewType(Enum):
    """Types of interviews."""
    BEHAVIORAL = "behavioral"
    TECHNICAL = "technical"
    CASE_STUDY = "case_study"
    COMPETENCY = "competency"
    SITUATIONAL = "situational"
    PANEL = "panel"
    PHONE_SCREEN = "phone_screen"
    FINAL_ROUND = "final_round"


class QuestionCategory(Enum):
    """Question categories."""
    # Behavioral
    LEADERSHIP = "leadership"
    TEAMWORK = "teamwork"
    CONFLICT = "conflict"
    FAILURE = "failure"
    SUCCESS = "success"
    CHALLENGE = "challenge"
    MOTIVATION = "motivation"
    ADAPTABILITY = "adaptability"
    
    # Technical
    TECHNICAL_SKILLS = "technical_skills"
    PROBLEM_SOLVING = "problem_solving"
    SYSTEM_DESIGN = "system_design"
    CODING = "coding"
    
    # Role-specific
    ROLE_SPECIFIC = "role_specific"
    COMPANY_SPECIFIC = "company_specific"
    INDUSTRY_KNOWLEDGE = "industry_knowledge"
    
    # General
    INTRODUCTION = "introduction"
    CAREER_GOALS = "career_goals"
    QUESTIONS_FOR_INTERVIEWER = "questions_for_interviewer"


class DifficultyLevel(Enum):
    """Question difficulty levels."""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    EXPERT = "expert"


class FeedbackType(Enum):
    """Types of feedback."""
    CONTENT = "content"          # What you said
    STRUCTURE = "structure"      # How you organized
    DELIVERY = "delivery"        # How you said it
    RELEVANCE = "relevance"      # How relevant to question
    DEPTH = "depth"              # Level of detail
    EXAMPLES = "examples"        # Quality of examples


# =============================================================================
# MODELS
# =============================================================================

class InterviewQuestion(BaseModel):
    """An interview question."""
    id: str = Field(default_factory=lambda: hashlib.md5(
        f"{datetime.utcnow().isoformat()}".encode()
    ).hexdigest()[:12])
    
    # Question details
    question: str
    category: QuestionCategory
    difficulty: DifficultyLevel = DifficultyLevel.MEDIUM
    interview_type: InterviewType = InterviewType.BEHAVIORAL
    
    # Guidance
    what_they_assess: str = ""
    tips: list[str] = Field(default_factory=list)
    sample_structure: str = ""
    
    # Follow-ups
    follow_up_questions: list[str] = Field(default_factory=list)
    
    # Context
    role_specific: bool = False
    company_specific: bool = False
    
    # Metadata
    tags: list[str] = Field(default_factory=list)


class STARResponse(BaseModel):
    """STAR method response structure."""
    situation: str = ""
    task: str = ""
    action: str = ""
    result: str = ""
    
    # Analysis
    is_complete: bool = False
    missing_elements: list[str] = Field(default_factory=list)
    
    def analyze(self) -> None:
        """Analyze response completeness."""
        self.missing_elements = []
        
        if not self.situation or len(self.situation) < 50:
            self.missing_elements.append("situation")
        if not self.task or len(self.task) < 30:
            self.missing_elements.append("task")
        if not self.action or len(self.action) < 100:
            self.missing_elements.append("action")
        if not self.result or len(self.result) < 50:
            self.missing_elements.append("result")
        
        self.is_complete = len(self.missing_elements) == 0


class ResponseFeedback(BaseModel):
    """Feedback on an interview response."""
    # Scores (0-100)
    overall_score: float = 0.0
    content_score: float = 0.0
    structure_score: float = 0.0
    relevance_score: float = 0.0
    depth_score: float = 0.0
    
    # Detailed feedback
    strengths: list[str] = Field(default_factory=list)
    areas_to_improve: list[str] = Field(default_factory=list)
    specific_suggestions: list[str] = Field(default_factory=list)
    
    # STAR analysis (for behavioral)
    star_analysis: Optional[STARResponse] = None
    
    # Example improvements
    improved_response_snippet: str = ""


class MockInterviewResponse(BaseModel):
    """A response in a mock interview."""
    question_id: str
    question_text: str
    response_text: str
    
    # Timing
    think_time_seconds: float = 0.0
    response_time_seconds: float = 0.0
    
    # Feedback
    feedback: Optional[ResponseFeedback] = None
    
    # Timestamp
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class MockInterviewSession(BaseModel):
    """A mock interview session."""
    id: str = Field(default_factory=lambda: hashlib.md5(
        f"{datetime.utcnow().isoformat()}".encode()
    ).hexdigest()[:12])
    
    # Context
    user_id: str
    opportunity_id: Optional[str] = None
    role_title: str = ""
    company_name: str = ""
    
    # Session config
    interview_type: InterviewType = InterviewType.BEHAVIORAL
    difficulty: DifficultyLevel = DifficultyLevel.MEDIUM
    num_questions: int = 5
    
    # Questions and responses
    questions: list[InterviewQuestion] = Field(default_factory=list)
    responses: list[MockInterviewResponse] = Field(default_factory=list)
    
    # Progress
    current_question_index: int = 0
    is_complete: bool = False
    
    # Timestamps
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    
    # Overall scores
    overall_score: float = 0.0
    confidence_score: float = 0.0
    
    def calculate_overall_score(self) -> None:
        """Calculate overall session score."""
        if not self.responses:
            return
        
        scores = [r.feedback.overall_score for r in self.responses if r.feedback]
        if scores:
            self.overall_score = sum(scores) / len(scores)


class CompanyInsights(BaseModel):
    """Research insights about a company for interview prep."""
    company_name: str
    
    # Company info
    mission: str = ""
    values: list[str] = Field(default_factory=list)
    culture_highlights: list[str] = Field(default_factory=list)
    recent_news: list[str] = Field(default_factory=list)
    
    # Interview-specific
    interview_process: str = ""
    common_questions: list[str] = Field(default_factory=list)
    tips_from_reviews: list[str] = Field(default_factory=list)
    
    # Questions to ask
    suggested_questions: list[str] = Field(default_factory=list)
    
    # Last updated
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class InterviewPrepPlan(BaseModel):
    """Personalized interview preparation plan."""
    id: str = Field(default_factory=lambda: hashlib.md5(
        f"{datetime.utcnow().isoformat()}".encode()
    ).hexdigest()[:12])
    
    user_id: str
    opportunity_id: Optional[str] = None
    
    # Target
    role_title: str
    company_name: str
    interview_date: Optional[datetime] = None
    
    # Plan details
    focus_areas: list[QuestionCategory] = Field(default_factory=list)
    daily_tasks: list[dict[str, Any]] = Field(default_factory=list)
    
    # Resources
    company_insights: Optional[CompanyInsights] = None
    practice_questions: list[InterviewQuestion] = Field(default_factory=list)
    
    # Progress
    completed_tasks: list[str] = Field(default_factory=list)
    practice_sessions: list[str] = Field(default_factory=list)  # Session IDs
    
    # Created
    created_at: datetime = Field(default_factory=datetime.utcnow)


# =============================================================================
# QUESTION BANK
# =============================================================================

class QuestionBank:
    """Repository of interview questions."""
    
    def __init__(self):
        """Initialize question bank with common questions."""
        self._questions: list[InterviewQuestion] = []
        self._load_default_questions()
    
    def _load_default_questions(self) -> None:
        """Load default interview questions."""
        # Behavioral - Leadership
        self._questions.extend([
            InterviewQuestion(
                question="Tell me about a time when you had to lead a team through a difficult project.",
                category=QuestionCategory.LEADERSHIP,
                what_they_assess="Leadership skills, problem-solving under pressure, team management",
                tips=[
                    "Choose a specific, challenging situation",
                    "Highlight your decision-making process",
                    "Show how you motivated the team",
                    "Quantify the results if possible"
                ],
                sample_structure="STAR: Situation (project context, challenges), Task (your responsibility), Action (specific leadership actions), Result (measurable outcomes)",
                follow_up_questions=[
                    "What would you do differently?",
                    "How did you handle team members who disagreed?",
                    "What did you learn from this experience?"
                ]
            ),
            InterviewQuestion(
                question="Describe a situation where you had to make an unpopular decision.",
                category=QuestionCategory.LEADERSHIP,
                what_they_assess="Decision-making, integrity, handling pushback",
                tips=[
                    "Show you can make tough calls",
                    "Explain your reasoning clearly",
                    "Demonstrate empathy for those affected",
                    "Focus on the positive outcome"
                ],
                follow_up_questions=[
                    "How did people react initially?",
                    "Did you gain their support eventually?",
                ]
            ),
        ])
        
        # Behavioral - Teamwork
        self._questions.extend([
            InterviewQuestion(
                question="Tell me about a time when you had to work with someone difficult.",
                category=QuestionCategory.TEAMWORK,
                what_they_assess="Interpersonal skills, conflict resolution, emotional intelligence",
                tips=[
                    "Don't badmouth the other person",
                    "Focus on your actions and approach",
                    "Show empathy and understanding",
                    "Highlight the resolution"
                ],
                follow_up_questions=[
                    "What did you learn about yourself?",
                    "Would you approach it differently now?",
                ]
            ),
            InterviewQuestion(
                question="Describe a successful team project you were part of. What was your role?",
                category=QuestionCategory.TEAMWORK,
                what_they_assess="Collaboration, role clarity, contribution to team success",
                tips=[
                    "Be specific about YOUR contribution",
                    "Acknowledge teammates' contributions",
                    "Show how you collaborated effectively",
                ]
            ),
        ])
        
        # Behavioral - Conflict
        self._questions.extend([
            InterviewQuestion(
                question="Tell me about a conflict you had with a coworker and how you resolved it.",
                category=QuestionCategory.CONFLICT,
                what_they_assess="Conflict resolution, communication, professionalism",
                tips=[
                    "Stay professional, no blame",
                    "Focus on the resolution process",
                    "Show you can disagree constructively",
                    "Emphasize the positive outcome"
                ],
                follow_up_questions=[
                    "What triggered the conflict?",
                    "How is your relationship now?",
                ]
            ),
        ])
        
        # Behavioral - Failure
        self._questions.extend([
            InterviewQuestion(
                question="Tell me about a time you failed. What did you learn?",
                category=QuestionCategory.FAILURE,
                difficulty=DifficultyLevel.HARD,
                what_they_assess="Self-awareness, accountability, growth mindset, resilience",
                tips=[
                    "Choose a real failure, not a humble brag",
                    "Take ownership, don't blame others",
                    "Focus heavily on what you learned",
                    "Show how you applied the lesson"
                ],
                follow_up_questions=[
                    "How did it affect your confidence?",
                    "Have you faced a similar situation since?",
                ]
            ),
            InterviewQuestion(
                question="Describe a project that didn't go as planned. What happened?",
                category=QuestionCategory.FAILURE,
                what_they_assess="Problem-solving, adaptability, learning from mistakes",
                tips=[
                    "Be honest about what went wrong",
                    "Show your problem-solving approach",
                    "Highlight lessons learned",
                ]
            ),
        ])
        
        # Behavioral - Success
        self._questions.extend([
            InterviewQuestion(
                question="What's your greatest professional achievement?",
                category=QuestionCategory.SUCCESS,
                what_they_assess="Values, impact, ability to articulate accomplishments",
                tips=[
                    "Choose something relevant to the role",
                    "Quantify impact if possible",
                    "Show passion and pride appropriately",
                    "Connect to your career trajectory"
                ],
                follow_up_questions=[
                    "Why does this achievement matter to you?",
                    "What made you successful?",
                ]
            ),
        ])
        
        # Behavioral - Challenge
        self._questions.extend([
            InterviewQuestion(
                question="Tell me about the most challenging situation you've faced at work.",
                category=QuestionCategory.CHALLENGE,
                what_they_assess="Resilience, problem-solving, handling pressure",
                tips=[
                    "Choose a genuinely difficult situation",
                    "Walk through your thought process",
                    "Show resourcefulness",
                    "End with a positive resolution"
                ],
                follow_up_questions=[
                    "How did you stay motivated?",
                    "Who did you turn to for support?",
                ]
            ),
        ])
        
        # Behavioral - Motivation
        self._questions.extend([
            InterviewQuestion(
                question="What motivates you in your work?",
                category=QuestionCategory.MOTIVATION,
                what_they_assess="Self-awareness, cultural fit, intrinsic motivation",
                tips=[
                    "Be authentic",
                    "Connect to the role/company",
                    "Show passion",
                    "Avoid mentioning money as primary motivator"
                ],
            ),
            InterviewQuestion(
                question="Why are you interested in this role/company?",
                category=QuestionCategory.MOTIVATION,
                what_they_assess="Research, genuine interest, cultural fit",
                tips=[
                    "Show you've researched the company",
                    "Connect your background to the role",
                    "Express genuine enthusiasm",
                    "Be specific, not generic"
                ],
            ),
        ])
        
        # Introduction
        self._questions.extend([
            InterviewQuestion(
                question="Tell me about yourself.",
                category=QuestionCategory.INTRODUCTION,
                difficulty=DifficultyLevel.EASY,
                what_they_assess="Communication, relevance, self-awareness",
                tips=[
                    "Keep it to 2-3 minutes",
                    "Structure: Present → Past → Future",
                    "Tailor to the role",
                    "End with why you're excited about this opportunity"
                ],
                sample_structure="Present (current role/situation) → Past (relevant experience) → Future (why this role)",
            ),
            InterviewQuestion(
                question="Walk me through your resume.",
                category=QuestionCategory.INTRODUCTION,
                what_they_assess="Career narrative, transitions, growth",
                tips=[
                    "Prepare a coherent career story",
                    "Explain transitions meaningfully",
                    "Highlight growth and progression",
                    "Connect to the current opportunity"
                ],
            ),
        ])
        
        # Career Goals
        self._questions.extend([
            InterviewQuestion(
                question="Where do you see yourself in 5 years?",
                category=QuestionCategory.CAREER_GOALS,
                what_they_assess="Ambition, planning, commitment",
                tips=[
                    "Show ambition but be realistic",
                    "Align with company's growth trajectory",
                    "Focus on skills and impact, not just titles",
                ],
            ),
            InterviewQuestion(
                question="What are your career goals?",
                category=QuestionCategory.CAREER_GOALS,
                what_they_assess="Direction, ambition, self-awareness",
                tips=[
                    "Be specific but flexible",
                    "Show how this role fits your goals",
                    "Demonstrate long-term thinking",
                ],
            ),
        ])
        
        # Technical/Problem-Solving
        self._questions.extend([
            InterviewQuestion(
                question="Describe a complex problem you solved. Walk me through your approach.",
                category=QuestionCategory.PROBLEM_SOLVING,
                interview_type=InterviewType.TECHNICAL,
                what_they_assess="Analytical thinking, methodology, communication",
                tips=[
                    "Structure your approach clearly",
                    "Show systematic thinking",
                    "Explain your reasoning",
                    "Discuss alternatives considered"
                ],
            ),
            InterviewQuestion(
                question="How do you approach learning a new technology or skill?",
                category=QuestionCategory.PROBLEM_SOLVING,
                interview_type=InterviewType.TECHNICAL,
                what_they_assess="Learning ability, adaptability, self-improvement",
                tips=[
                    "Show a structured approach",
                    "Give specific examples",
                    "Mention resources you use",
                ],
            ),
        ])
        
        # Questions for Interviewer
        self._questions.extend([
            InterviewQuestion(
                question="[Prep] Questions to ask the interviewer",
                category=QuestionCategory.QUESTIONS_FOR_INTERVIEWER,
                difficulty=DifficultyLevel.EASY,
                what_they_assess="Preparation, genuine interest, critical thinking",
                tips=[
                    "Prepare 3-5 thoughtful questions",
                    "Ask about the role, team, culture",
                    "Show you've researched the company",
                    "Avoid questions about salary/benefits initially"
                ],
                sample_structure="""Examples:
- What does success look like in this role?
- Can you tell me about the team I'd be working with?
- What are the biggest challenges facing the team right now?
- How would you describe the company culture?
- What do you enjoy most about working here?
- What's the typical career path for someone in this role?"""
            ),
        ])
    
    def get_questions(
        self,
        category: Optional[QuestionCategory] = None,
        difficulty: Optional[DifficultyLevel] = None,
        interview_type: Optional[InterviewType] = None,
        limit: Optional[int] = None
    ) -> list[InterviewQuestion]:
        """Get questions with optional filters."""
        questions = self._questions
        
        if category:
            questions = [q for q in questions if q.category == category]
        
        if difficulty:
            questions = [q for q in questions if q.difficulty == difficulty]
        
        if interview_type:
            questions = [q for q in questions if q.interview_type == interview_type]
        
        if limit:
            questions = questions[:limit]
        
        return questions
    
    def get_random_questions(
        self,
        num_questions: int,
        categories: Optional[list[QuestionCategory]] = None,
        difficulty: Optional[DifficultyLevel] = None
    ) -> list[InterviewQuestion]:
        """Get random questions for a practice session."""
        pool = self._questions
        
        if categories:
            pool = [q for q in pool if q.category in categories]
        
        if difficulty:
            pool = [q for q in pool if q.difficulty == difficulty]
        
        return random.sample(pool, min(num_questions, len(pool)))
    
    def add_question(self, question: InterviewQuestion) -> None:
        """Add a question to the bank."""
        self._questions.append(question)
    
    def add_role_specific_questions(
        self,
        role_title: str,
        questions: list[dict[str, Any]]
    ) -> None:
        """Add role-specific questions."""
        for q_data in questions:
            question = InterviewQuestion(
                **q_data,
                role_specific=True,
                tags=[role_title.lower()]
            )
            self._questions.append(question)


# =============================================================================
# RESPONSE ANALYZER
# =============================================================================

class ResponseAnalyzer:
    """Analyzes interview responses and provides feedback."""
    
    def __init__(self):
        """Initialize analyzer."""
        self.star_keywords = {
            "situation": ["when", "context", "background", "situation", "scenario", "at my", "in my"],
            "task": ["responsible", "task", "goal", "objective", "needed to", "had to", "challenge"],
            "action": ["i did", "i decided", "i implemented", "i created", "i led", "i spoke", "i initiated"],
            "result": ["result", "outcome", "achieved", "improved", "increased", "decreased", "saved", "learned"]
        }
    
    async def analyze_response(
        self,
        question: InterviewQuestion,
        response: str,
        is_behavioral: bool = True
    ) -> ResponseFeedback:
        """Analyze an interview response."""
        feedback = ResponseFeedback()
        
        # Basic metrics
        word_count = len(response.split())
        sentence_count = response.count('.') + response.count('!') + response.count('?')
        
        # Analyze STAR for behavioral questions
        if is_behavioral or question.category in [
            QuestionCategory.LEADERSHIP, QuestionCategory.TEAMWORK,
            QuestionCategory.CONFLICT, QuestionCategory.FAILURE,
            QuestionCategory.SUCCESS, QuestionCategory.CHALLENGE
        ]:
            star_analysis = self._analyze_star(response)
            feedback.star_analysis = star_analysis
        
        # Calculate scores
        feedback.content_score = self._score_content(response, question)
        feedback.structure_score = self._score_structure(response, word_count, sentence_count)
        feedback.relevance_score = self._score_relevance(response, question)
        feedback.depth_score = self._score_depth(response, word_count)
        
        # Overall score
        feedback.overall_score = (
            feedback.content_score * 0.3 +
            feedback.structure_score * 0.2 +
            feedback.relevance_score * 0.3 +
            feedback.depth_score * 0.2
        )
        
        # Generate feedback
        self._generate_feedback(feedback, response, question, word_count)
        
        return feedback
    
    def _analyze_star(self, response: str) -> STARResponse:
        """Analyze response for STAR components."""
        response_lower = response.lower()
        star = STARResponse()
        
        # Try to identify each component
        sentences = response.split('.')
        
        current_component = "situation"
        for sentence in sentences:
            sentence_lower = sentence.lower()
            
            # Check for component transitions
            if any(kw in sentence_lower for kw in self.star_keywords["result"]):
                current_component = "result"
            elif any(kw in sentence_lower for kw in self.star_keywords["action"]):
                current_component = "action"
            elif any(kw in sentence_lower for kw in self.star_keywords["task"]):
                current_component = "task"
            
            # Add to appropriate component
            if current_component == "situation":
                star.situation += sentence + "."
            elif current_component == "task":
                star.task += sentence + "."
            elif current_component == "action":
                star.action += sentence + "."
            elif current_component == "result":
                star.result += sentence + "."
        
        star.analyze()
        return star
    
    def _score_content(
        self,
        response: str,
        question: InterviewQuestion
    ) -> float:
        """Score the content quality."""
        score = 50.0  # Base score
        
        # Check for specific examples
        if any(word in response.lower() for word in ["for example", "specifically", "instance"]):
            score += 15
        
        # Check for quantifiable results
        if any(char.isdigit() for char in response):
            score += 10
        
        # Check for action verbs
        action_verbs = ["led", "created", "improved", "managed", "developed", "implemented", "achieved"]
        if any(verb in response.lower() for verb in action_verbs):
            score += 15
        
        # Penalize vague language
        vague_words = ["stuff", "things", "like", "kind of", "sort of", "maybe"]
        vague_count = sum(1 for word in vague_words if word in response.lower())
        score -= vague_count * 5
        
        return max(0, min(100, score))
    
    def _score_structure(
        self,
        response: str,
        word_count: int,
        sentence_count: int
    ) -> float:
        """Score the response structure."""
        score = 50.0
        
        # Check length (ideal: 150-300 words for behavioral)
        if 150 <= word_count <= 300:
            score += 20
        elif 100 <= word_count < 150 or 300 < word_count <= 400:
            score += 10
        elif word_count < 50:
            score -= 20
        elif word_count > 500:
            score -= 10
        
        # Check sentence variety
        if sentence_count >= 3:
            avg_sentence_length = word_count / sentence_count
            if 10 <= avg_sentence_length <= 25:
                score += 15
        
        # Check for clear transitions
        transitions = ["first", "then", "after", "finally", "as a result", "consequently"]
        if any(t in response.lower() for t in transitions):
            score += 15
        
        return max(0, min(100, score))
    
    def _score_relevance(
        self,
        response: str,
        question: InterviewQuestion
    ) -> float:
        """Score relevance to the question."""
        score = 60.0
        
        # Check if response addresses the question type
        response_lower = response.lower()
        
        if question.category == QuestionCategory.LEADERSHIP:
            if any(word in response_lower for word in ["team", "led", "leadership", "guide", "mentor"]):
                score += 20
        elif question.category == QuestionCategory.TEAMWORK:
            if any(word in response_lower for word in ["team", "collaborate", "together", "group"]):
                score += 20
        elif question.category == QuestionCategory.CONFLICT:
            if any(word in response_lower for word in ["resolved", "conflict", "disagreed", "compromise"]):
                score += 20
        elif question.category == QuestionCategory.FAILURE:
            if any(word in response_lower for word in ["learned", "mistake", "failed", "wrong"]):
                score += 20
        
        # Penalize off-topic responses
        off_topic_indicators = ["i don't know", "i can't think of", "not sure"]
        if any(indicator in response_lower for indicator in off_topic_indicators):
            score -= 30
        
        return max(0, min(100, score))
    
    def _score_depth(
        self,
        response: str,
        word_count: int
    ) -> float:
        """Score the depth of the response."""
        score = 50.0
        
        # Check for detail
        if word_count >= 150:
            score += 15
        
        # Check for reflection/learning
        reflection_words = ["learned", "realized", "understood", "insight", "takeaway"]
        if any(word in response.lower() for word in reflection_words):
            score += 20
        
        # Check for specific details
        specific_indicators = ["specifically", "in particular", "exactly", "precisely"]
        if any(indicator in response.lower() for indicator in specific_indicators):
            score += 15
        
        return max(0, min(100, score))
    
    def _generate_feedback(
        self,
        feedback: ResponseFeedback,
        response: str,
        question: InterviewQuestion,
        word_count: int
    ) -> None:
        """Generate detailed feedback."""
        # Strengths
        if feedback.content_score >= 70:
            feedback.strengths.append("Good use of specific examples and details")
        if feedback.structure_score >= 70:
            feedback.strengths.append("Well-structured response with clear flow")
        if feedback.relevance_score >= 70:
            feedback.strengths.append("Response directly addresses the question")
        if feedback.depth_score >= 70:
            feedback.strengths.append("Good depth and reflection in your answer")
        
        # Areas to improve
        if feedback.star_analysis and feedback.star_analysis.missing_elements:
            for element in feedback.star_analysis.missing_elements:
                if element == "result":
                    feedback.areas_to_improve.append("Include more about the outcome and results")
                elif element == "action":
                    feedback.areas_to_improve.append("Be more specific about YOUR actions and contributions")
                elif element == "situation":
                    feedback.areas_to_improve.append("Provide more context about the situation")
        
        if word_count < 100:
            feedback.areas_to_improve.append("Response could be more detailed")
        elif word_count > 400:
            feedback.areas_to_improve.append("Consider being more concise")
        
        if feedback.content_score < 60:
            feedback.specific_suggestions.append(
                "Use more action verbs and quantify your achievements when possible"
            )
        
        if feedback.structure_score < 60:
            feedback.specific_suggestions.append(
                "Use the STAR method: clearly state the Situation, Task, your Actions, and the Result"
            )


# =============================================================================
# INTERVIEW PREP AGENT
# =============================================================================

class InterviewPrepAgent:
    """
    AI-powered interview preparation agent.
    
    Provides personalized interview preparation including
    question practice, feedback, and coaching.
    """
    
    def __init__(self):
        """Initialize the interview prep agent."""
        self.question_bank = QuestionBank()
        self.response_analyzer = ResponseAnalyzer()
        
        # Session storage
        self._sessions: dict[str, MockInterviewSession] = {}
        self._prep_plans: dict[str, InterviewPrepPlan] = {}
    
    async def create_prep_plan(
        self,
        user_id: str,
        role_title: str,
        company_name: str,
        interview_date: Optional[datetime] = None,
        focus_areas: Optional[list[QuestionCategory]] = None
    ) -> InterviewPrepPlan:
        """Create a personalized interview prep plan."""
        # Default focus areas
        if not focus_areas:
            focus_areas = [
                QuestionCategory.INTRODUCTION,
                QuestionCategory.LEADERSHIP,
                QuestionCategory.TEAMWORK,
                QuestionCategory.CHALLENGE,
                QuestionCategory.MOTIVATION,
            ]
        
        # Generate daily tasks
        daily_tasks = self._generate_daily_tasks(focus_areas, interview_date)
        
        # Get practice questions
        practice_questions = []
        for category in focus_areas:
            questions = self.question_bank.get_questions(category=category, limit=3)
            practice_questions.extend(questions)
        
        plan = InterviewPrepPlan(
            user_id=user_id,
            role_title=role_title,
            company_name=company_name,
            interview_date=interview_date,
            focus_areas=focus_areas,
            daily_tasks=daily_tasks,
            practice_questions=practice_questions,
        )
        
        self._prep_plans[plan.id] = plan
        return plan
    
    def _generate_daily_tasks(
        self,
        focus_areas: list[QuestionCategory],
        interview_date: Optional[datetime]
    ) -> list[dict[str, Any]]:
        """Generate daily preparation tasks."""
        tasks = [
            {
                "day": 1,
                "title": "Research & Setup",
                "tasks": [
                    "Research the company thoroughly",
                    "Review the job description",
                    "Prepare your 'Tell me about yourself' pitch",
                    "Set up your interview practice schedule"
                ]
            },
            {
                "day": 2,
                "title": "Behavioral Prep - Part 1",
                "tasks": [
                    "Prepare 3 STAR stories about leadership",
                    "Practice 'Why this company?' answer",
                    "Review your resume for talking points"
                ]
            },
            {
                "day": 3,
                "title": "Behavioral Prep - Part 2",
                "tasks": [
                    "Prepare STAR stories about teamwork",
                    "Prepare a story about handling conflict",
                    "Practice a story about failure and learning"
                ]
            },
            {
                "day": 4,
                "title": "Technical/Role Prep",
                "tasks": [
                    "Review technical skills relevant to the role",
                    "Prepare examples of relevant projects",
                    "Practice problem-solving questions"
                ]
            },
            {
                "day": 5,
                "title": "Mock Interview",
                "tasks": [
                    "Complete a full mock interview session",
                    "Review feedback and improve weak areas",
                    "Prepare questions for the interviewer"
                ]
            },
            {
                "day": 6,
                "title": "Final Preparation",
                "tasks": [
                    "Review all your prepared stories",
                    "Practice out loud one more time",
                    "Prepare your outfit and materials",
                    "Get a good night's sleep!"
                ]
            }
        ]
        
        return tasks
    
    async def start_mock_interview(
        self,
        user_id: str,
        interview_type: InterviewType = InterviewType.BEHAVIORAL,
        difficulty: DifficultyLevel = DifficultyLevel.MEDIUM,
        num_questions: int = 5,
        categories: Optional[list[QuestionCategory]] = None,
        role_title: str = "",
        company_name: str = ""
    ) -> MockInterviewSession:
        """Start a new mock interview session."""
        # Select questions
        if categories:
            questions = self.question_bank.get_random_questions(
                num_questions=num_questions,
                categories=categories,
                difficulty=difficulty
            )
        else:
            # Default mix of behavioral questions
            default_categories = [
                QuestionCategory.INTRODUCTION,
                QuestionCategory.LEADERSHIP,
                QuestionCategory.TEAMWORK,
                QuestionCategory.CHALLENGE,
                QuestionCategory.CAREER_GOALS,
            ]
            questions = self.question_bank.get_random_questions(
                num_questions=num_questions,
                categories=default_categories,
                difficulty=difficulty
            )
        
        session = MockInterviewSession(
            user_id=user_id,
            role_title=role_title,
            company_name=company_name,
            interview_type=interview_type,
            difficulty=difficulty,
            num_questions=num_questions,
            questions=questions,
        )
        
        self._sessions[session.id] = session
        return session
    
    def get_current_question(
        self,
        session_id: str
    ) -> Optional[InterviewQuestion]:
        """Get the current question in a session."""
        session = self._sessions.get(session_id)
        if not session or session.is_complete:
            return None
        
        if session.current_question_index >= len(session.questions):
            return None
        
        return session.questions[session.current_question_index]
    
    async def submit_response(
        self,
        session_id: str,
        response_text: str,
        think_time: float = 0.0,
        response_time: float = 0.0
    ) -> ResponseFeedback:
        """Submit a response to the current question and get feedback."""
        session = self._sessions.get(session_id)
        if not session:
            raise ValueError("Session not found")
        
        if session.is_complete:
            raise ValueError("Session already complete")
        
        current_question = self.get_current_question(session_id)
        if not current_question:
            raise ValueError("No current question")
        
        # Analyze response
        feedback = await self.response_analyzer.analyze_response(
            current_question,
            response_text,
            is_behavioral=session.interview_type == InterviewType.BEHAVIORAL
        )
        
        # Create response record
        mock_response = MockInterviewResponse(
            question_id=current_question.id,
            question_text=current_question.question,
            response_text=response_text,
            think_time_seconds=think_time,
            response_time_seconds=response_time,
            feedback=feedback,
        )
        
        session.responses.append(mock_response)
        session.current_question_index += 1
        
        # Check if session is complete
        if session.current_question_index >= len(session.questions):
            session.is_complete = True
            session.completed_at = datetime.utcnow()
            session.calculate_overall_score()
        
        return feedback
    
    def get_session_summary(
        self,
        session_id: str
    ) -> dict[str, Any]:
        """Get a summary of a completed session."""
        session = self._sessions.get(session_id)
        if not session:
            return {}
        
        # Calculate category scores
        category_scores: dict[str, list[float]] = {}
        for response in session.responses:
            if response.feedback:
                for q in session.questions:
                    if q.id == response.question_id:
                        category = q.category.value
                        if category not in category_scores:
                            category_scores[category] = []
                        category_scores[category].append(response.feedback.overall_score)
        
        avg_category_scores = {
            cat: sum(scores) / len(scores)
            for cat, scores in category_scores.items()
        }
        
        # Identify strengths and weaknesses
        all_strengths = []
        all_improvements = []
        for response in session.responses:
            if response.feedback:
                all_strengths.extend(response.feedback.strengths)
                all_improvements.extend(response.feedback.areas_to_improve)
        
        return {
            "session_id": session.id,
            "overall_score": session.overall_score,
            "questions_answered": len(session.responses),
            "total_questions": len(session.questions),
            "category_scores": avg_category_scores,
            "top_strengths": list(set(all_strengths))[:3],
            "areas_to_improve": list(set(all_improvements))[:3],
            "duration_minutes": (
                (session.completed_at - session.started_at).total_seconds() / 60
                if session.completed_at else 0
            ),
        }
    
    async def get_question_tips(
        self,
        question_id: str
    ) -> dict[str, Any]:
        """Get tips and guidance for a specific question."""
        for question in self.question_bank._questions:
            if question.id == question_id:
                return {
                    "question": question.question,
                    "what_they_assess": question.what_they_assess,
                    "tips": question.tips,
                    "sample_structure": question.sample_structure,
                    "follow_ups": question.follow_up_questions,
                }
        return {}
    
    async def generate_improved_response(
        self,
        original_response: str,
        feedback: ResponseFeedback,
        question: InterviewQuestion
    ) -> str:
        """Generate suggestions for improving a response."""
        suggestions = []
        
        if feedback.star_analysis and feedback.star_analysis.missing_elements:
            if "result" in feedback.star_analysis.missing_elements:
                suggestions.append(
                    "Add a clear result: 'As a result, [specific outcome with numbers if possible]'"
                )
            if "action" in feedback.star_analysis.missing_elements:
                suggestions.append(
                    "Be more specific about YOUR actions: 'I specifically [action verb] by [how]'"
                )
        
        if feedback.content_score < 70:
            suggestions.append(
                "Add quantifiable achievements: numbers, percentages, or specific metrics"
            )
        
        if feedback.structure_score < 70:
            suggestions.append(
                "Structure with: 'First... Then... As a result...'"
            )
        
        return "\n".join([f"• {s}" for s in suggestions])


# =============================================================================
# FACTORY FUNCTION
# =============================================================================

def create_interview_prep_agent() -> InterviewPrepAgent:
    """Create an interview preparation agent."""
    return InterviewPrepAgent()


# =============================================================================
# MODULE EXPORTS
# =============================================================================

__all__ = [
    # Enums
    'InterviewType',
    'QuestionCategory',
    'DifficultyLevel',
    'FeedbackType',
    
    # Models
    'InterviewQuestion',
    'STARResponse',
    'ResponseFeedback',
    'MockInterviewResponse',
    'MockInterviewSession',
    'CompanyInsights',
    'InterviewPrepPlan',
    
    # Services
    'QuestionBank',
    'ResponseAnalyzer',
    'InterviewPrepAgent',
    
    # Factory
    'create_interview_prep_agent',
]
