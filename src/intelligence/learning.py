"""
Learning Agent - Adaptive Intelligence for Continuous Improvement

This module implements an outcome-aware learning system that:
1. Tracks application outcomes (accepted/rejected/no response)
2. Analyzes success patterns across opportunities
3. Adjusts scoring weights based on historical performance
4. Provides actionable insights for strategy optimization
"""

import asyncio
import json
import logging
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Optional

import numpy as np
from pydantic import BaseModel, Field
from sqlalchemy import select, update, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.data.database import get_db_session
from src.data.models import (
    OutcomeRecord, 
    ApplicationDraft, 
    OpportunityRecord, 
    ScoringWeightRecord,
    ProfileRecord,
)
from src.models.enums import ApplicationOutcome, OpportunityType

logger = logging.getLogger(__name__)


class OutcomeType(str, Enum):
    """Application outcome categories"""
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    INTERVIEW = "interview"
    WAITLISTED = "waitlisted"
    NO_RESPONSE = "no_response"
    WITHDRAWN = "withdrawn"


@dataclass
class OutcomeData:
    """Data structure for outcome tracking"""
    opportunity_id: str
    outcome: OutcomeType
    response_time_days: Optional[int] = None
    feedback: Optional[str] = None
    interview_rounds: int = 0
    final_stage_reached: Optional[str] = None
    compensation_offered: Optional[float] = None
    recorded_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> dict:
        return {
            "opportunity_id": self.opportunity_id,
            "outcome": self.outcome.value,
            "response_time_days": self.response_time_days,
            "feedback": self.feedback,
            "interview_rounds": self.interview_rounds,
            "final_stage_reached": self.final_stage_reached,
            "compensation_offered": self.compensation_offered,
            "recorded_at": self.recorded_at.isoformat()
        }


class SuccessPattern(BaseModel):
    """Identified pattern leading to success"""
    pattern_name: str
    confidence: float = Field(ge=0, le=1)
    sample_size: int
    success_rate: float = Field(ge=0, le=1)
    key_factors: list[str] = []
    recommendations: list[str] = []
    discovered_at: datetime = Field(default_factory=datetime.utcnow)


class WeightAdjustment(BaseModel):
    """Proposed adjustment to scoring weights"""
    weight_name: str
    current_value: float
    proposed_value: float
    change_percent: float
    rationale: str
    confidence: float = Field(ge=0, le=1)
    based_on_outcomes: int


class LearningInsight(BaseModel):
    """Actionable insight from learning analysis"""
    category: str  # "strategy", "timing", "targeting", "content"
    insight: str
    impact_score: float = Field(ge=0, le=1)
    evidence: list[str] = []
    suggested_actions: list[str] = []


class PerformanceReport(BaseModel):
    """Comprehensive performance analysis"""
    period_start: datetime
    period_end: datetime
    total_applications: int
    outcomes_tracked: int
    
    # Success metrics
    acceptance_rate: float
    interview_rate: float
    response_rate: float
    
    # Breakdown by type
    outcomes_by_type: dict[str, dict[str, int]] = {}
    
    # Patterns and insights
    success_patterns: list[SuccessPattern] = []
    insights: list[LearningInsight] = []
    
    # Weight recommendations
    weight_adjustments: list[WeightAdjustment] = []
    
    # Trend analysis
    trend_direction: str  # "improving", "declining", "stable"
    trend_confidence: float = Field(ge=0, le=1)


class OutcomeTracker:
    """
    Tracks and records application outcomes for learning.
    """
    
    def __init__(self):
        self.pending_followups: dict[str, datetime] = {}
        self.outcome_buffer: list[OutcomeData] = []
    
    async def record_outcome(
        self,
        opportunity_id: str,
        outcome: OutcomeType,
        feedback: Optional[str] = None,
        response_time_days: Optional[int] = None,
        interview_rounds: int = 0,
        compensation_offered: Optional[float] = None
    ) -> OutcomeData:
        """
        Record an application outcome.
        
        Args:
            opportunity_id: The opportunity identifier
            outcome: The outcome type
            feedback: Any feedback received
            response_time_days: Days between application and response
            interview_rounds: Number of interview rounds completed
            compensation_offered: Final compensation if accepted
        
        Returns:
            The recorded outcome data
        """
        outcome_data = OutcomeData(
            opportunity_id=opportunity_id,
            outcome=outcome,
            feedback=feedback,
            response_time_days=response_time_days,
            interview_rounds=interview_rounds,
            compensation_offered=compensation_offered
        )
        
        # Store in database
        async with get_db_session() as session:
            try:
                # Create outcome record
                record = OutcomeRecord(
                    opportunity_id=opportunity_id,
                    outcome=outcome.value,
                    feedback=feedback,
                    response_time_days=response_time_days,
                    interview_rounds=interview_rounds,
                    compensation_offered=compensation_offered,
                    recorded_at=outcome_data.recorded_at
                )
                session.add(record)
                await session.commit()
                
                logger.info(f"Recorded outcome for {opportunity_id}: {outcome.value}")
                
            except Exception as e:
                logger.error(f"Failed to record outcome: {e}")
                await session.rollback()
                # Still add to buffer for later retry
                self.outcome_buffer.append(outcome_data)
        
        # Remove from pending followups
        if opportunity_id in self.pending_followups:
            del self.pending_followups[opportunity_id]
        
        return outcome_data
    
    async def schedule_followup(
        self,
        opportunity_id: str,
        followup_date: datetime
    ) -> None:
        """Schedule a followup reminder for an application."""
        self.pending_followups[opportunity_id] = followup_date
        logger.info(f"Scheduled followup for {opportunity_id} on {followup_date}")
    
    async def get_pending_followups(self) -> list[tuple[str, datetime]]:
        """Get all pending followups that are due."""
        now = datetime.utcnow()
        due_followups = [
            (opp_id, date)
            for opp_id, date in self.pending_followups.items()
            if date <= now
        ]
        return due_followups
    
    async def get_outcomes_for_period(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> list[OutcomeData]:
        """Retrieve all outcomes for a given period."""
        outcomes = []
        
        async with get_db_session() as session:
            try:
                result = await session.execute(
                    select(OutcomeRecord).where(
                        and_(
                            OutcomeRecord.recorded_at >= start_date,
                            OutcomeRecord.recorded_at <= end_date
                        )
                    )
                )
                records = result.scalars().all()
                
                for record in records:
                    outcomes.append(OutcomeData(
                        opportunity_id=record.opportunity_id,
                        outcome=OutcomeType(record.outcome),
                        feedback=record.feedback,
                        response_time_days=record.response_time_days,
                        interview_rounds=record.interview_rounds,
                        compensation_offered=record.compensation_offered,
                        recorded_at=record.recorded_at
                    ))
                    
            except Exception as e:
                logger.error(f"Failed to retrieve outcomes: {e}")
        
        return outcomes


class PatternAnalyzer:
    """
    Analyzes success patterns from historical outcomes.
    """
    
    def __init__(self, min_sample_size: int = 5):
        self.min_sample_size = min_sample_size
    
    async def analyze_patterns(
        self,
        outcomes: list[OutcomeData],
        opportunities: dict[str, dict]
    ) -> list[SuccessPattern]:
        """
        Identify success patterns from outcome data.
        
        Args:
            outcomes: List of outcome data
            opportunities: Mapping of opportunity IDs to opportunity details
        
        Returns:
            List of identified success patterns
        """
        patterns = []
        
        # Group outcomes by success
        successful = [o for o in outcomes if o.outcome in [OutcomeType.ACCEPTED, OutcomeType.INTERVIEW]]
        unsuccessful = [o for o in outcomes if o.outcome in [OutcomeType.REJECTED, OutcomeType.NO_RESPONSE]]
        
        if len(successful) < self.min_sample_size:
            logger.info("Insufficient successful outcomes for pattern analysis")
            return patterns
        
        # Analyze by opportunity type
        patterns.extend(await self._analyze_by_type(outcomes, opportunities))
        
        # Analyze by timing
        patterns.extend(await self._analyze_by_timing(outcomes, opportunities))
        
        # Analyze by compensation range
        patterns.extend(await self._analyze_by_compensation(outcomes, opportunities))
        
        # Analyze by requirements match
        patterns.extend(await self._analyze_by_requirements(outcomes, opportunities))
        
        return patterns
    
    async def _analyze_by_type(
        self,
        outcomes: list[OutcomeData],
        opportunities: dict[str, dict]
    ) -> list[SuccessPattern]:
        """Analyze patterns by opportunity type."""
        patterns = []
        type_outcomes: dict[str, list[OutcomeData]] = defaultdict(list)
        
        for outcome in outcomes:
            opp = opportunities.get(outcome.opportunity_id, {})
            opp_type = opp.get("type", "unknown")
            type_outcomes[opp_type].append(outcome)
        
        for opp_type, type_data in type_outcomes.items():
            if len(type_data) < self.min_sample_size:
                continue
            
            success_count = sum(
                1 for o in type_data 
                if o.outcome in [OutcomeType.ACCEPTED, OutcomeType.INTERVIEW]
            )
            success_rate = success_count / len(type_data)
            
            if success_rate > 0.3:  # Notable success rate
                patterns.append(SuccessPattern(
                    pattern_name=f"high_success_{opp_type}",
                    confidence=min(0.9, len(type_data) / 20),  # More data = more confidence
                    sample_size=len(type_data),
                    success_rate=success_rate,
                    key_factors=[
                        f"Opportunity type: {opp_type}",
                        f"Sample size: {len(type_data)}",
                        f"Success count: {success_count}"
                    ],
                    recommendations=[
                        f"Prioritize {opp_type} opportunities",
                        f"Expected success rate: {success_rate:.1%}"
                    ]
                ))
        
        return patterns
    
    async def _analyze_by_timing(
        self,
        outcomes: list[OutcomeData],
        opportunities: dict[str, dict]
    ) -> list[SuccessPattern]:
        """Analyze patterns by application timing."""
        patterns = []
        
        # Group by response time
        quick_response = [o for o in outcomes if o.response_time_days and o.response_time_days <= 14]
        slow_response = [o for o in outcomes if o.response_time_days and o.response_time_days > 14]
        
        if len(quick_response) >= self.min_sample_size:
            success_rate = sum(
                1 for o in quick_response 
                if o.outcome in [OutcomeType.ACCEPTED, OutcomeType.INTERVIEW]
            ) / len(quick_response)
            
            if success_rate > 0.4:
                patterns.append(SuccessPattern(
                    pattern_name="quick_response_correlation",
                    confidence=0.7,
                    sample_size=len(quick_response),
                    success_rate=success_rate,
                    key_factors=[
                        "Response within 14 days",
                        "Quick responses correlate with interest"
                    ],
                    recommendations=[
                        "Prioritize opportunities that respond quickly",
                        "Follow up on slow responses after 2 weeks"
                    ]
                ))
        
        return patterns
    
    async def _analyze_by_compensation(
        self,
        outcomes: list[OutcomeData],
        opportunities: dict[str, dict]
    ) -> list[SuccessPattern]:
        """Analyze patterns by compensation range."""
        patterns = []
        
        # Group outcomes by compensation bands
        comp_bands = defaultdict(list)
        for outcome in outcomes:
            opp = opportunities.get(outcome.opportunity_id, {})
            comp = opp.get("compensation", {})
            
            if isinstance(comp, dict):
                max_comp = comp.get("max", 0)
            else:
                max_comp = comp or 0
            
            if max_comp < 50000:
                band = "entry"
            elif max_comp < 100000:
                band = "mid"
            elif max_comp < 200000:
                band = "senior"
            else:
                band = "executive"
            
            comp_bands[band].append(outcome)
        
        for band, band_outcomes in comp_bands.items():
            if len(band_outcomes) >= self.min_sample_size:
                success_rate = sum(
                    1 for o in band_outcomes 
                    if o.outcome in [OutcomeType.ACCEPTED, OutcomeType.INTERVIEW]
                ) / len(band_outcomes)
                
                if success_rate > 0.25:
                    patterns.append(SuccessPattern(
                        pattern_name=f"{band}_compensation_success",
                        confidence=min(0.85, len(band_outcomes) / 15),
                        sample_size=len(band_outcomes),
                        success_rate=success_rate,
                        key_factors=[
                            f"Compensation band: {band}",
                            f"Success rate: {success_rate:.1%}"
                        ],
                        recommendations=[
                            f"Continue targeting {band}-level positions",
                            f"Current success rate justifies this strategy"
                        ]
                    ))
        
        return patterns
    
    async def _analyze_by_requirements(
        self,
        outcomes: list[OutcomeData],
        opportunities: dict[str, dict]
    ) -> list[SuccessPattern]:
        """Analyze patterns by requirements match."""
        patterns = []
        
        # This would integrate with profile matching data
        # For now, return empty - would be expanded with actual requirement analysis
        
        return patterns


class WeightOptimizer:
    """
    Optimizes scoring weights based on outcome data.
    """
    
    def __init__(
        self,
        learning_rate: float = 0.1,
        min_outcomes_for_adjustment: int = 10
    ):
        self.learning_rate = learning_rate
        self.min_outcomes = min_outcomes_for_adjustment
    
    async def calculate_adjustments(
        self,
        outcomes: list[OutcomeData],
        opportunities: dict[str, dict],
        current_weights: dict[str, float]
    ) -> list[WeightAdjustment]:
        """
        Calculate recommended weight adjustments.
        
        Uses gradient-like approach to adjust weights toward
        configurations that historically led to success.
        """
        if len(outcomes) < self.min_outcomes:
            logger.info(f"Insufficient outcomes ({len(outcomes)}) for weight adjustment")
            return []
        
        adjustments = []
        
        # Calculate success correlation for each weight dimension
        success_outcomes = [
            o for o in outcomes 
            if o.outcome in [OutcomeType.ACCEPTED, OutcomeType.INTERVIEW]
        ]
        failure_outcomes = [
            o for o in outcomes 
            if o.outcome in [OutcomeType.REJECTED, OutcomeType.NO_RESPONSE]
        ]
        
        # Analyze skill match weight
        skill_adj = await self._analyze_skill_weight(
            success_outcomes, failure_outcomes, opportunities, current_weights
        )
        if skill_adj:
            adjustments.append(skill_adj)
        
        # Analyze compensation weight
        comp_adj = await self._analyze_compensation_weight(
            success_outcomes, failure_outcomes, opportunities, current_weights
        )
        if comp_adj:
            adjustments.append(comp_adj)
        
        # Analyze deadline urgency weight
        deadline_adj = await self._analyze_deadline_weight(
            success_outcomes, failure_outcomes, opportunities, current_weights
        )
        if deadline_adj:
            adjustments.append(deadline_adj)
        
        return adjustments
    
    async def _analyze_skill_weight(
        self,
        successes: list[OutcomeData],
        failures: list[OutcomeData],
        opportunities: dict[str, dict],
        current_weights: dict[str, float]
    ) -> Optional[WeightAdjustment]:
        """Analyze if skill match weight should be adjusted."""
        current = current_weights.get("skill_match", 0.35)
        
        # Calculate average skill match for successes vs failures
        success_skill_scores = []
        for outcome in successes:
            opp = opportunities.get(outcome.opportunity_id, {})
            score = opp.get("skill_match_score", 0)
            if score > 0:
                success_skill_scores.append(score)
        
        failure_skill_scores = []
        for outcome in failures:
            opp = opportunities.get(outcome.opportunity_id, {})
            score = opp.get("skill_match_score", 0)
            if score > 0:
                failure_skill_scores.append(score)
        
        if not success_skill_scores or not failure_skill_scores:
            return None
        
        success_avg = np.mean(success_skill_scores)
        failure_avg = np.mean(failure_skill_scores)
        
        # If successful applications had higher skill match, increase weight
        if success_avg > failure_avg * 1.1:  # 10% higher
            proposed = min(0.5, current * (1 + self.learning_rate))
            return WeightAdjustment(
                weight_name="skill_match",
                current_value=current,
                proposed_value=proposed,
                change_percent=((proposed - current) / current) * 100,
                rationale=f"Successful apps had {success_avg:.0%} avg skill match vs {failure_avg:.0%} for failures",
                confidence=0.75,
                based_on_outcomes=len(successes) + len(failures)
            )
        elif failure_avg > success_avg * 1.1:  # Failures had higher skill match
            proposed = max(0.2, current * (1 - self.learning_rate * 0.5))
            return WeightAdjustment(
                weight_name="skill_match",
                current_value=current,
                proposed_value=proposed,
                change_percent=((proposed - current) / current) * 100,
                rationale="Skill match may be over-weighted - consider other factors",
                confidence=0.6,
                based_on_outcomes=len(successes) + len(failures)
            )
        
        return None
    
    async def _analyze_compensation_weight(
        self,
        successes: list[OutcomeData],
        failures: list[OutcomeData],
        opportunities: dict[str, dict],
        current_weights: dict[str, float]
    ) -> Optional[WeightAdjustment]:
        """Analyze compensation weight adjustment."""
        current = current_weights.get("compensation_alignment", 0.20)
        
        # Check if compensation targeting is effective
        success_in_range = 0
        for outcome in successes:
            if outcome.compensation_offered:
                success_in_range += 1
        
        success_rate_with_comp = success_in_range / max(len(successes), 1)
        
        if success_rate_with_comp > 0.7:
            proposed = min(0.35, current * (1 + self.learning_rate))
            return WeightAdjustment(
                weight_name="compensation_alignment",
                current_value=current,
                proposed_value=proposed,
                change_percent=((proposed - current) / current) * 100,
                rationale=f"{success_rate_with_comp:.0%} of acceptances included compensation offers",
                confidence=0.7,
                based_on_outcomes=len(successes)
            )
        
        return None
    
    async def _analyze_deadline_weight(
        self,
        successes: list[OutcomeData],
        failures: list[OutcomeData],
        opportunities: dict[str, dict],
        current_weights: dict[str, float]
    ) -> Optional[WeightAdjustment]:
        """Analyze deadline urgency weight."""
        current = current_weights.get("deadline_urgency", 0.10)
        
        # Check response times
        success_response_times = [
            o.response_time_days for o in successes 
            if o.response_time_days is not None
        ]
        
        if not success_response_times:
            return None
        
        avg_response = np.mean(success_response_times)
        
        # Fast responses suggest timing matters
        if avg_response < 14:
            proposed = min(0.20, current * (1 + self.learning_rate))
            return WeightAdjustment(
                weight_name="deadline_urgency",
                current_value=current,
                proposed_value=proposed,
                change_percent=((proposed - current) / current) * 100,
                rationale=f"Avg response time of {avg_response:.0f} days suggests timing is important",
                confidence=0.65,
                based_on_outcomes=len(success_response_times)
            )
        
        return None
    
    async def apply_adjustments(
        self,
        adjustments: list[WeightAdjustment],
        auto_apply_threshold: float = 0.7
    ) -> dict[str, float]:
        """
        Apply weight adjustments to the database.
        
        Only auto-applies adjustments with confidence above threshold.
        """
        applied_weights = {}
        
        async with get_db_session() as session:
            # Get or create the active weight configuration
            result = await session.execute(
                select(ScoringWeightRecord).where(
                    ScoringWeightRecord.is_active == True
                )
            )
            active_config = result.scalar_one_or_none()
            
            if active_config is None:
                # Create default configuration
                active_config = ScoringWeightRecord(
                    name="adaptive_weights",
                    is_active=True,
                    weights={
                        "skill_match": 0.35,
                        "compensation_alignment": 0.20,
                        "growth_potential": 0.20,
                        "deadline_urgency": 0.10,
                        "organization_fit": 0.15
                    }
                )
                session.add(active_config)
                await session.commit()
                await session.refresh(active_config)
            
            current_weights = active_config.weights.copy()
            
            for adj in adjustments:
                if adj.confidence >= auto_apply_threshold:
                    try:
                        # Update the weight in the JSON
                        current_weights[adj.weight_name] = adj.proposed_value
                        applied_weights[adj.weight_name] = adj.proposed_value
                        
                        logger.info(
                            f"Applied weight adjustment: {adj.weight_name} "
                            f"{adj.current_value:.3f} -> {adj.proposed_value:.3f}"
                        )
                        
                    except Exception as e:
                        logger.error(f"Failed to apply weight adjustment: {e}")
            
            # Update the database with new weights
            if applied_weights:
                try:
                    active_config.weights = current_weights
                    active_config.samples_evaluated = active_config.samples_evaluated + len(adjustments)
                    await session.commit()
                except Exception as e:
                    logger.error(f"Failed to save weight adjustments: {e}")
                    await session.rollback()
        
        return applied_weights


class LearningAgent:
    """
    Main learning agent that coordinates outcome tracking,
    pattern analysis, and weight optimization.
    
    This agent continuously improves the system's ability to
    identify high-potential opportunities based on historical outcomes.
    """
    
    def __init__(
        self,
        learning_rate: float = 0.1,
        min_sample_size: int = 5,
        analysis_window_days: int = 90
    ):
        self.outcome_tracker = OutcomeTracker()
        self.pattern_analyzer = PatternAnalyzer(min_sample_size=min_sample_size)
        self.weight_optimizer = WeightOptimizer(
            learning_rate=learning_rate,
            min_outcomes_for_adjustment=min_sample_size * 2
        )
        self.analysis_window_days = analysis_window_days
    
    async def record_outcome(
        self,
        opportunity_id: str,
        outcome: str | OutcomeType,
        **kwargs
    ) -> OutcomeData:
        """
        Record an application outcome.
        
        Args:
            opportunity_id: The opportunity identifier
            outcome: The outcome (string or OutcomeType)
            **kwargs: Additional outcome data
        
        Returns:
            The recorded outcome data
        """
        if isinstance(outcome, str):
            outcome = OutcomeType(outcome)
        
        return await self.outcome_tracker.record_outcome(
            opportunity_id=opportunity_id,
            outcome=outcome,
            **kwargs
        )
    
    async def generate_performance_report(
        self,
        days: int = None
    ) -> PerformanceReport:
        """
        Generate a comprehensive performance report.
        
        Args:
            days: Number of days to analyze (default: analysis_window_days)
        
        Returns:
            Complete performance report with insights
        """
        days = days or self.analysis_window_days
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Get outcomes for period
        outcomes = await self.outcome_tracker.get_outcomes_for_period(
            start_date, end_date
        )
        
        if not outcomes:
            return PerformanceReport(
                period_start=start_date,
                period_end=end_date,
                total_applications=0,
                outcomes_tracked=0,
                acceptance_rate=0.0,
                interview_rate=0.0,
                response_rate=0.0,
                trend_direction="stable",
                trend_confidence=0.0
            )
        
        # Load opportunity data
        opportunities = await self._load_opportunities(
            [o.opportunity_id for o in outcomes]
        )
        
        # Calculate metrics
        total = len(outcomes)
        accepted = sum(1 for o in outcomes if o.outcome == OutcomeType.ACCEPTED)
        interviews = sum(1 for o in outcomes if o.outcome == OutcomeType.INTERVIEW)
        no_response = sum(1 for o in outcomes if o.outcome == OutcomeType.NO_RESPONSE)
        
        acceptance_rate = accepted / total
        interview_rate = interviews / total
        response_rate = 1 - (no_response / total)
        
        # Group by opportunity type
        outcomes_by_type = defaultdict(lambda: defaultdict(int))
        for outcome in outcomes:
            opp = opportunities.get(outcome.opportunity_id, {})
            opp_type = opp.get("type", "unknown")
            outcomes_by_type[opp_type][outcome.outcome.value] += 1
        
        # Analyze patterns
        success_patterns = await self.pattern_analyzer.analyze_patterns(
            outcomes, opportunities
        )
        
        # Get current weights
        current_weights = await self._get_current_weights()
        
        # Calculate weight adjustments
        weight_adjustments = await self.weight_optimizer.calculate_adjustments(
            outcomes, opportunities, current_weights
        )
        
        # Generate insights
        insights = await self._generate_insights(
            outcomes, opportunities, success_patterns
        )
        
        # Calculate trend
        trend_direction, trend_confidence = await self._calculate_trend(outcomes)
        
        # Count total applications (would come from database)
        total_applications = await self._count_total_applications(start_date, end_date)
        
        return PerformanceReport(
            period_start=start_date,
            period_end=end_date,
            total_applications=total_applications,
            outcomes_tracked=total,
            acceptance_rate=acceptance_rate,
            interview_rate=interview_rate,
            response_rate=response_rate,
            outcomes_by_type=dict(outcomes_by_type),
            success_patterns=success_patterns,
            insights=insights,
            weight_adjustments=weight_adjustments,
            trend_direction=trend_direction,
            trend_confidence=trend_confidence
        )
    
    async def optimize_weights(
        self,
        auto_apply: bool = True,
        confidence_threshold: float = 0.7
    ) -> list[WeightAdjustment]:
        """
        Analyze outcomes and optimize scoring weights.
        
        Args:
            auto_apply: Whether to automatically apply high-confidence adjustments
            confidence_threshold: Minimum confidence for auto-apply
        
        Returns:
            List of weight adjustments (applied and proposed)
        """
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=self.analysis_window_days)
        
        outcomes = await self.outcome_tracker.get_outcomes_for_period(
            start_date, end_date
        )
        
        if not outcomes:
            logger.info("No outcomes available for weight optimization")
            return []
        
        opportunities = await self._load_opportunities(
            [o.opportunity_id for o in outcomes]
        )
        
        current_weights = await self._get_current_weights()
        
        adjustments = await self.weight_optimizer.calculate_adjustments(
            outcomes, opportunities, current_weights
        )
        
        if auto_apply and adjustments:
            await self.weight_optimizer.apply_adjustments(
                adjustments, 
                auto_apply_threshold=confidence_threshold
            )
        
        return adjustments
    
    async def get_pending_followups(self) -> list[dict]:
        """Get applications that need follow-up."""
        followups = await self.outcome_tracker.get_pending_followups()
        
        result = []
        for opp_id, due_date in followups:
            result.append({
                "opportunity_id": opp_id,
                "due_date": due_date.isoformat(),
                "overdue_days": (datetime.utcnow() - due_date).days
            })
        
        return result
    
    async def _load_opportunities(
        self,
        opportunity_ids: list[str]
    ) -> dict[str, dict]:
        """Load opportunity details from database."""
        opportunities = {}
        
        async with get_db_session() as session:
            try:
                result = await session.execute(
                    select(OpportunityRecord).where(
                        OpportunityRecord.id.in_(opportunity_ids)
                    )
                )
                records = result.scalars().all()
                
                for record in records:
                    # Extract compensation from JSON field
                    comp = record.compensation or {}
                    opportunities[str(record.id)] = {
                        "type": record.opportunity_type,
                        "title": record.title,
                        "organization": record.organization,
                        "compensation": {
                            "min": comp.get("min", 0),
                            "max": comp.get("max", 0)
                        },
                        "skill_match_score": record.fit_score or 0,
                        "deadline": record.deadline.isoformat() if record.deadline else None
                    }
                    
            except Exception as e:
                logger.error(f"Failed to load opportunities: {e}")
        
        return opportunities
    
    async def _get_current_weights(self) -> dict[str, float]:
        """Get current scoring weights from database."""
        # Default weights
        weights = {
            "skill_match": 0.35,
            "compensation_alignment": 0.20,
            "growth_potential": 0.20,
            "deadline_urgency": 0.10,
            "organization_fit": 0.15
        }
        
        async with get_db_session() as session:
            try:
                # Get active weight configuration
                result = await session.execute(
                    select(ScoringWeightRecord).where(
                        ScoringWeightRecord.is_active == True
                    )
                )
                active_config = result.scalar_one_or_none()
                
                if active_config and active_config.weights:
                    weights.update(active_config.weights)
                    
            except Exception as e:
                logger.error(f"Failed to load weights: {e}")
        
        return weights
    
    async def _generate_insights(
        self,
        outcomes: list[OutcomeData],
        opportunities: dict[str, dict],
        patterns: list[SuccessPattern]
    ) -> list[LearningInsight]:
        """Generate actionable insights from analysis."""
        insights = []
        
        # Timing insight
        response_times = [
            o.response_time_days for o in outcomes 
            if o.response_time_days is not None
        ]
        if response_times:
            avg_response = np.mean(response_times)
            insights.append(LearningInsight(
                category="timing",
                insight=f"Average response time is {avg_response:.0f} days",
                impact_score=0.6,
                evidence=[f"Based on {len(response_times)} tracked responses"],
                suggested_actions=[
                    f"Follow up on applications after {max(14, int(avg_response))} days",
                    "Quick responses often indicate strong interest"
                ]
            ))
        
        # Pattern-based insights
        for pattern in patterns:
            if pattern.success_rate > 0.4:
                insights.append(LearningInsight(
                    category="targeting",
                    insight=f"Pattern '{pattern.pattern_name}' shows {pattern.success_rate:.0%} success rate",
                    impact_score=pattern.confidence,
                    evidence=pattern.key_factors,
                    suggested_actions=pattern.recommendations
                ))
        
        # Success rate insight
        acceptance_count = sum(1 for o in outcomes if o.outcome == OutcomeType.ACCEPTED)
        if len(outcomes) > 10:
            rate = acceptance_count / len(outcomes)
            if rate > 0.3:
                insights.append(LearningInsight(
                    category="strategy",
                    insight=f"Strong acceptance rate of {rate:.0%}",
                    impact_score=0.8,
                    evidence=[f"Accepted: {acceptance_count}/{len(outcomes)}"],
                    suggested_actions=[
                        "Current targeting strategy is effective",
                        "Consider increasing application volume"
                    ]
                ))
            elif rate < 0.1:
                insights.append(LearningInsight(
                    category="strategy",
                    insight=f"Low acceptance rate of {rate:.0%} needs attention",
                    impact_score=0.9,
                    evidence=[f"Accepted: {acceptance_count}/{len(outcomes)}"],
                    suggested_actions=[
                        "Review application quality",
                        "Consider adjusting target criteria",
                        "Analyze rejected applications for patterns"
                    ]
                ))
        
        return insights
    
    async def _calculate_trend(
        self,
        outcomes: list[OutcomeData]
    ) -> tuple[str, float]:
        """Calculate performance trend direction."""
        if len(outcomes) < 10:
            return "stable", 0.3
        
        # Sort by date
        sorted_outcomes = sorted(outcomes, key=lambda o: o.recorded_at)
        
        # Split into halves
        mid = len(sorted_outcomes) // 2
        first_half = sorted_outcomes[:mid]
        second_half = sorted_outcomes[mid:]
        
        # Calculate success rates
        first_success = sum(
            1 for o in first_half 
            if o.outcome in [OutcomeType.ACCEPTED, OutcomeType.INTERVIEW]
        ) / len(first_half)
        
        second_success = sum(
            1 for o in second_half 
            if o.outcome in [OutcomeType.ACCEPTED, OutcomeType.INTERVIEW]
        ) / len(second_half)
        
        diff = second_success - first_success
        
        if diff > 0.1:
            return "improving", min(0.9, abs(diff) * 5)
        elif diff < -0.1:
            return "declining", min(0.9, abs(diff) * 5)
        else:
            return "stable", 0.7
    
    async def _count_total_applications(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> int:
        """Count total applications in period."""
        async with get_db_session() as session:
            try:
                result = await session.execute(
                    select(func.count(ApplicationDraft.id)).where(
                        and_(
                            ApplicationDraft.created_at >= start_date,
                            ApplicationDraft.created_at <= end_date
                        )
                    )
                )
                return result.scalar() or 0
            except Exception:
                return 0


# Convenience function for quick outcome recording
async def record_outcome(
    opportunity_id: str,
    outcome: str,
    **kwargs
) -> OutcomeData:
    """Quick function to record an outcome."""
    agent = LearningAgent()
    return await agent.record_outcome(opportunity_id, outcome, **kwargs)


# Weekly learning task
async def run_weekly_learning() -> PerformanceReport:
    """
    Run weekly learning analysis and optimization.
    
    This should be scheduled to run weekly to:
    1. Generate performance report
    2. Identify success patterns
    3. Optimize scoring weights
    4. Generate actionable insights
    """
    agent = LearningAgent(analysis_window_days=90)
    
    # Generate comprehensive report
    report = await agent.generate_performance_report()
    
    # Auto-optimize weights with high confidence threshold
    await agent.optimize_weights(
        auto_apply=True,
        confidence_threshold=0.75
    )
    
    logger.info(
        f"Weekly learning complete: {report.outcomes_tracked} outcomes analyzed, "
        f"{len(report.success_patterns)} patterns found, "
        f"{len(report.weight_adjustments)} weight adjustments proposed"
    )
    
    return report
