"""
Growth Engine - Root Orchestrator Agent.

The main orchestrator that coordinates all sub-agents to run the
full opportunity discovery and application pipeline.

Now with Intelligence Layer integration for:
- ML-powered scoring with embeddings
- Outcome tracking and learning
- Adaptive weight optimization
- Performance analytics
"""

from datetime import datetime
from typing import Any, Optional

from google.adk import Agent, InMemorySessionService, Runner

from config.settings import settings
from src.agents.discovery import discovery_agent
from src.agents.profile import profile_agent
from src.agents.scoring import scoring_agent
from src.agents.application import application_agent
from src.agents.outreach import outreach_agent

# Intelligence layer imports
from src.intelligence import (
    EmbeddingPipeline,
    FeatureEngineer,
    MLScoringModel,
    LearningAgent,
    AnalyticsEngine,
    get_dashboard,
    record_outcome,
    run_weekly_learning,
)


# System instruction for the Root Orchestrator
ORCHESTRATOR_INSTRUCTION = """You are the Growth Engine Orchestrator - the brain coordinating an autonomous opportunity discovery and application system.

## Your Mission
Coordinate specialized sub-agents to:
1. Discover 500+ opportunities daily
2. Score and prioritize them for fit
3. Generate 100+ polished applications
4. Send strategic outreach to key contacts
5. Learn and improve from outcomes

## Your Sub-Agents

You can delegate to these specialized agents:

### 1. Discovery Agent
- Searches for opportunities across sources
- Scrapes and parses opportunity details
- Filters duplicates and expired listings
- Use for: Finding new opportunities

### 2. Profile Agent  
- Manages user profile data
- Provides skills, experience, preferences
- Maintains narrative consistency
- Use for: Getting profile context for matching

### 3. Scoring Agent
- Calculates fit scores for opportunities
- Assigns Tier 1/2/3 priorities
- Explains scoring decisions
- Use for: Prioritizing what to apply to

### 4. Application Agent (NEW - Claude Opus 4.5)
- Generates essays, cover letters, proposals
- Personalizes content from profile
- Refines drafts to high quality
- Use for: Creating application materials

### 5. Outreach Agent (NEW)
- Generates cold emails and LinkedIn messages
- Creates follow-up sequences
- Writes referral requests and thank you notes
- Use for: Networking and building connections

## Full Pipeline Workflow

### Daily Discovery Loop
1. **Profile Check** - Get current profile summary
2. **Discovery Phase** - Search for 500+ opportunities
3. **Scoring Phase** - Score and tier all opportunities (using ML model)
4. **Summary Generation** - Report findings

### Intelligence Layer (NEW)
1. **ML Scoring**: Use trained XGBoost model for fit prediction
2. **Embeddings**: Generate semantic embeddings for matching
3. **Learning**: Track outcomes and adjust weights automatically
4. **Analytics**: Monitor performance and ROI metrics

### Application Generation (On Demand)
1. Receive Tier 1 opportunity
2. Generate appropriate content (essay, cover letter, etc.)
3. Evaluate quality (target 8+/10)
4. Refine until quality threshold met
5. Save draft for review

### Outreach Campaigns
1. Identify key contacts for target opportunities
2. Generate personalized cold emails
3. Create follow-up sequences
4. Track and manage responses

## Coordination Guidelines

1. **Delegate Appropriately**: Use the right sub-agent for each task
2. **Share Context**: Pass relevant information between agents
3. **Track Progress**: Monitor quotas and completion
4. **Handle Errors**: Gracefully handle failures, continue processing
5. **Report Clearly**: Provide structured summaries
6. **Learn Continuously**: Track outcomes and adapt scoring weights

## Output Format

Always provide status updates:
```
📊 Daily Summary - {date}
━━━━━━━━━━━━━━━━━━━━━
Discovered: {count} opportunities
Scored: {count} opportunities
Tier 1: {count} | Tier 2: {count} | Tier 3: {count}

🏆 Top Opportunities:
1. {title} at {org} - Score: {score}
...

📝 Applications Generated: {count}
📧 Outreach Sent: {count}

⏰ Upcoming Deadlines:
- {title}: {days} days
...

📋 Recommendations:
- {action items}
```

Be proactive, efficient, and thorough."""


class GrowthEngine:
    """
    Main Growth Engine orchestrator.
    
    Coordinates all sub-agents to run the opportunity discovery
    and application pipeline, enhanced with intelligence layer.
    """
    
    def __init__(self):
        """Initialize the Growth Engine with all sub-agents and intelligence."""
        # Create the root orchestrator agent with sub-agents
        self.orchestrator = Agent(
            name="growth_engine",
            model=settings.orchestrator_model,
            instruction=ORCHESTRATOR_INSTRUCTION,
            sub_agents=[
                discovery_agent,
                profile_agent,
                scoring_agent,
                application_agent,
                outreach_agent,
            ],
        )
        
        # Session management
        self.session_service = InMemorySessionService()
        
        # Create runner
        self.runner = Runner(
            agent=self.orchestrator,
            session_service=self.session_service,
        )
        
        # Intelligence layer components
        self.embedding_pipeline = EmbeddingPipeline()
        self.feature_engineer = FeatureEngineer()
        self.ml_model: Optional[MLScoringModel] = None
        self.learning_agent = LearningAgent()
        self.analytics = AnalyticsEngine()
        
        # State tracking
        self.current_session_id: str | None = None
        self.daily_stats: dict[str, Any] = {}
        
    async def initialize_ml_model(self, model_path: str = "models/fit_scorer.json"):
        """Initialize or load the ML scoring model."""
        from pathlib import Path
        
        self.ml_model = MLScoringModel()
        model_file = Path(model_path)
        
        if model_file.exists():
            self.ml_model.load(model_path)
        else:
            # Train with synthetic data initially
            await self.ml_model.train_initial_model()
    
    async def run(
        self,
        message: str,
        user_id: str = "default_user",
        session_id: str | None = None,
    ) -> str:
        """
        Run the orchestrator with a message.
        
        Args:
            message: User message or command
            user_id: User identifier
            session_id: Session identifier (auto-generated if not provided)
            
        Returns:
            Agent response
        """
        if session_id is None:
            session_id = f"session_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        self.current_session_id = session_id
        
        response_text = ""
        async for event in self.runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=message,
        ):
            if event.is_final_response():
                response_text = event.content
        
        return response_text
    
    async def run_daily_loop(
        self,
        user_id: str = "default_user",
    ) -> dict[str, Any]:
        """
        Run the full daily discovery and scoring loop.
        
        Args:
            user_id: User identifier
            
        Returns:
            Daily summary with statistics
        """
        session_id = f"daily_{datetime.utcnow().strftime('%Y%m%d')}"
        
        # Run the daily loop command
        response = await self.run(
            message="""Execute the full daily loop:
            
            1. First, get my profile summary to understand what opportunities I'm looking for
            2. Then search for opportunities across all categories (jobs, fellowships, grants, accelerators)
            3. Score all discovered opportunities against my profile
            4. Provide a comprehensive summary with:
               - Total counts by type and tier
               - Top 10 opportunities
               - Urgent deadlines (within 7 days)
               - Recommendations for next steps
            
            Target: Discover and score 50+ opportunities.""",
            user_id=user_id,
            session_id=session_id,
        )
        
        return {
            "date": datetime.utcnow().isoformat(),
            "session_id": session_id,
            "summary": response,
            "status": "completed",
        }
    
    async def discover_opportunities(
        self,
        query: str,
        opportunity_type: str = "job",
        user_id: str = "default_user",
    ) -> str:
        """
        Discover opportunities for a specific query.
        
        Args:
            query: Search query
            opportunity_type: Type of opportunity
            user_id: User identifier
            
        Returns:
            Discovery results
        """
        return await self.run(
            message=f"Search for {opportunity_type} opportunities matching: {query}",
            user_id=user_id,
        )
    
    async def get_top_opportunities(
        self,
        limit: int = 10,
        user_id: str = "default_user",
    ) -> str:
        """
        Get top-scored opportunities.
        
        Args:
            limit: Maximum number to return
            user_id: User identifier
            
        Returns:
            Top opportunities summary
        """
        return await self.run(
            message=f"Show me the top {limit} Tier 1 opportunities with the highest fit scores.",
            user_id=user_id,
        )
    
    async def generate_application(
        self,
        opportunity_id: str,
        content_type: str = "cover_letter",
        user_id: str = "default_user",
    ) -> str:
        """
        Generate application content for an opportunity.
        
        Args:
            opportunity_id: ID of the target opportunity
            content_type: Type of content (essay, cover_letter, proposal)
            user_id: User identifier
            
        Returns:
            Generated application content
        """
        return await self.run(
            message=f"""Generate a {content_type} for opportunity ID: {opportunity_id}
            
            Please:
            1. Get my profile context
            2. Look up the opportunity details
            3. Generate high-quality content using the ApplicationAgent
            4. Evaluate the quality (target 8+/10)
            5. Refine if needed
            6. Save the draft and return the content""",
            user_id=user_id,
        )
    
    async def create_outreach(
        self,
        recipient_name: str,
        recipient_title: str,
        company: str,
        opportunity_title: str,
        outreach_type: str = "cold_email",
        user_id: str = "default_user",
    ) -> str:
        """
        Create outreach message for a contact.
        
        Args:
            recipient_name: Name of the recipient
            recipient_title: Their job title
            company: Their company
            opportunity_title: Related opportunity
            outreach_type: Type of message (cold_email, linkedin_connection)
            user_id: User identifier
            
        Returns:
            Generated outreach message
        """
        return await self.run(
            message=f"""Create a {outreach_type} for:
            
            Recipient: {recipient_name}, {recipient_title} at {company}
            Related to: {opportunity_title}
            
            Please:
            1. Get my profile for personalization
            2. Generate the outreach using the OutreachAgent
            3. Provide subject line options (for email)
            4. Include optimal send timing
            5. Offer to create a follow-up sequence""",
            user_id=user_id,
        )
    
    # ==================== Intelligence Layer Methods ====================
    
    async def score_with_ml(
        self,
        opportunity_data: dict,
        profile_data: dict,
    ) -> dict[str, Any]:
        """
        Score an opportunity using the ML model.
        
        Args:
            opportunity_data: Opportunity details
            profile_data: User profile data
            
        Returns:
            Score prediction with confidence and explanation
        """
        if self.ml_model is None:
            await self.initialize_ml_model()
        
        # Generate embeddings
        opp_embedding = await self.embedding_pipeline.generate_opportunity_embedding(
            opportunity_data
        )
        profile_embedding = await self.embedding_pipeline.generate_profile_embedding(
            profile_data
        )
        
        # Extract features
        features = await self.feature_engineer.build_feature_vector(
            opportunity=opportunity_data,
            profile=profile_data,
            opportunity_embedding=opp_embedding.embedding,
            profile_embedding=profile_embedding.embedding,
        )
        
        # Get prediction with confidence
        prediction = self.ml_model.predict_with_confidence(features.to_numpy())
        
        # Get explanation
        explanation = self.ml_model.explain_prediction(features.to_numpy())
        
        return {
            "fit_score": prediction.prediction,
            "confidence": prediction.confidence,
            "confidence_interval": prediction.confidence_interval,
            "explanation": explanation,
            "features_used": list(features.feature_names),
        }
    
    async def record_application_outcome(
        self,
        opportunity_id: str,
        outcome: str,
        feedback: Optional[str] = None,
        response_time_days: Optional[int] = None,
        compensation_offered: Optional[float] = None,
    ) -> dict:
        """
        Record the outcome of an application for learning.
        
        Args:
            opportunity_id: The opportunity identifier
            outcome: The outcome (accepted, rejected, interview, no_response)
            feedback: Any feedback received
            response_time_days: Days between application and response
            compensation_offered: Final compensation if accepted
            
        Returns:
            Recorded outcome data
        """
        outcome_data = await self.learning_agent.record_outcome(
            opportunity_id=opportunity_id,
            outcome=outcome,
            feedback=feedback,
            response_time_days=response_time_days,
            compensation_offered=compensation_offered,
        )
        
        return outcome_data.to_dict()
    
    async def run_learning_cycle(
        self,
        auto_adjust_weights: bool = True,
    ) -> dict[str, Any]:
        """
        Run a learning cycle to optimize the system.
        
        Analyzes recent outcomes, identifies patterns, and
        optionally adjusts scoring weights.
        
        Args:
            auto_adjust_weights: Whether to auto-apply weight adjustments
            
        Returns:
            Performance report with insights
        """
        # Generate performance report
        report = await self.learning_agent.generate_performance_report(days=90)
        
        # Optimize weights if enabled
        adjustments = []
        if auto_adjust_weights:
            adjustments = await self.learning_agent.optimize_weights(
                auto_apply=True,
                confidence_threshold=0.75,
            )
        
        return {
            "period": f"{report.period_start.isoformat()} to {report.period_end.isoformat()}",
            "outcomes_analyzed": report.outcomes_tracked,
            "acceptance_rate": report.acceptance_rate,
            "interview_rate": report.interview_rate,
            "trend": report.trend_direction,
            "patterns_found": len(report.success_patterns),
            "insights": [i.model_dump() for i in report.insights],
            "weight_adjustments": [a.model_dump() for a in adjustments],
        }
    
    async def get_analytics_dashboard(
        self,
        period_days: int = 30,
    ) -> dict[str, Any]:
        """
        Get comprehensive analytics dashboard.
        
        Args:
            period_days: Number of days to analyze
            
        Returns:
            Dashboard data with all metrics
        """
        dashboard = await self.analytics.generate_dashboard(period_days)
        return dashboard.model_dump()
    
    async def run_full_pipeline(
        self,
        user_id: str = "default_user",
        include_learning: bool = True,
    ) -> dict[str, Any]:
        """
        Run the complete pipeline including intelligence.
        
        This enhanced pipeline:
        1. Runs discovery and scoring
        2. Uses ML model for refined scoring
        3. Tracks outcomes for learning
        4. Provides analytics insights
        
        Args:
            user_id: User identifier
            include_learning: Whether to run learning cycle
            
        Returns:
            Comprehensive pipeline results
        """
        # Initialize ML model if needed
        if self.ml_model is None:
            await self.initialize_ml_model()
        
        # Run daily discovery loop
        daily_results = await self.run_daily_loop(user_id)
        
        # Run learning cycle
        learning_results = {}
        if include_learning:
            learning_results = await self.run_learning_cycle(auto_adjust_weights=True)
        
        # Get analytics snapshot
        analytics = await self.get_analytics_dashboard(period_days=30)
        
        return {
            "daily_summary": daily_results,
            "learning_insights": learning_results,
            "analytics_snapshot": {
                "acceptance_rate": analytics.get("summary", {}).get("acceptance_rate", 0),
                "response_rate": analytics.get("summary", {}).get("response_rate", 0),
                "total_opportunities": analytics.get("summary", {}).get("total_opportunities_discovered", 0),
            },
            "status": "completed",
            "timestamp": datetime.utcnow().isoformat(),
        }


def create_growth_engine() -> GrowthEngine:
    """Create and return a GrowthEngine instance."""
    return GrowthEngine()


# Default instance
growth_engine = create_growth_engine()
