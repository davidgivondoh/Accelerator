"""
Performance Metrics Engine

Advanced performance tracking and metrics calculation system that provides
deep insights into application success patterns, user behavior, and optimization opportunities.
"""

import asyncio
import json
import numpy as np
from typing import Dict, List, Optional, Any, Tuple, Callable, Set
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from collections import defaultdict, deque
import logging
import statistics

logger = logging.getLogger(__name__)


class MetricCategory(Enum):
    """Categories of performance metrics"""
    EFFICIENCY = "efficiency"           # Speed and throughput metrics
    EFFECTIVENESS = "effectiveness"     # Success and quality metrics  
    ENGAGEMENT = "engagement"          # User interaction metrics
    CONVERSION = "conversion"          # Stage-to-stage conversion metrics
    QUALITY = "quality"               # Content and output quality metrics
    BEHAVIORAL = "behavioral"         # User behavior pattern metrics
    PREDICTIVE = "predictive"         # Forward-looking metrics


class MetricAggregationType(Enum):
    """Types of metric aggregation"""
    SUM = "sum"
    AVERAGE = "average"
    MEDIAN = "median"
    MIN = "min"
    MAX = "max"
    COUNT = "count"
    PERCENTILE_95 = "p95"
    PERCENTILE_99 = "p99"
    STANDARD_DEVIATION = "stddev"
    VARIANCE = "variance"


@dataclass
class MetricDefinition:
    """Definition of a performance metric"""
    metric_id: str
    name: str
    description: str
    category: MetricCategory
    unit: str  # percentage, count, seconds, score, etc.
    aggregation_type: MetricAggregationType
    calculation_function: Callable
    dependencies: List[str] = field(default_factory=list)  # Other metrics needed
    tags: List[str] = field(default_factory=list)
    is_kpi: bool = False  # Key Performance Indicator
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'metric_id': self.metric_id,
            'name': self.name,
            'description': self.description,
            'category': self.category.value,
            'unit': self.unit,
            'aggregation_type': self.aggregation_type.value,
            'dependencies': self.dependencies,
            'tags': self.tags,
            'is_kpi': self.is_kpi
        }


@dataclass
class MetricResult:
    """Result of a metric calculation"""
    metric_id: str
    value: float
    timestamp: datetime
    period: str  # daily, weekly, monthly
    metadata: Dict[str, Any] = field(default_factory=dict)
    confidence_score: float = 1.0  # 0-1 confidence in the result
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'metric_id': self.metric_id,
            'value': self.value,
            'timestamp': self.timestamp.isoformat(),
            'period': self.period,
            'metadata': self.metadata,
            'confidence_score': self.confidence_score
        }


@dataclass
class MetricTrend:
    """Trend analysis for a metric over time"""
    metric_id: str
    current_value: float
    previous_value: float
    change_percentage: float
    trend_direction: str  # up, down, stable
    significance: str  # significant, minor, insignificant
    period_comparison: str  # week-over-week, month-over-month, etc.
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'metric_id': self.metric_id,
            'current_value': self.current_value,
            'previous_value': self.previous_value,
            'change_percentage': self.change_percentage,
            'trend_direction': self.trend_direction,
            'significance': self.significance,
            'period_comparison': self.period_comparison
        }


class MetricCalculations:
    """Collection of metric calculation functions"""
    
    @staticmethod
    async def application_success_rate(data: Dict[str, Any]) -> float:
        """Calculate application success rate"""
        applications = data.get('applications', [])
        if not applications:
            return 0.0
        
        successful = len([
            app for app in applications 
            if app.get('current_stage') in ['offer_extended', 'offer_accepted']
        ])
        
        return successful / len(applications)
    
    @staticmethod
    async def average_time_to_response(data: Dict[str, Any]) -> float:
        """Calculate average time to first response"""
        applications = data.get('applications', [])
        response_times = []
        
        for app in applications:
            events = app.get('events', [])
            submitted_time = None
            response_time = None
            
            for event in sorted(events, key=lambda x: x.get('timestamp', '')):
                if event.get('event_type') == 'application_submitted':
                    submitted_time = datetime.fromisoformat(event.get('timestamp', '').replace('Z', '+00:00'))
                elif submitted_time and 'response' in event.get('event_type', '').lower():
                    response_time = datetime.fromisoformat(event.get('timestamp', '').replace('Z', '+00:00'))
                    break
            
            if submitted_time and response_time:
                hours_diff = (response_time - submitted_time).total_seconds() / 3600
                response_times.append(hours_diff)
        
        return statistics.mean(response_times) if response_times else 0.0
    
    @staticmethod
    async def interview_conversion_rate(data: Dict[str, Any]) -> float:
        """Calculate interview invitation rate"""
        applications = data.get('applications', [])
        if not applications:
            return 0.0
        
        interview_stages = ['first_interview', 'technical_interview', 'final_interview']
        interviews = len([
            app for app in applications 
            if app.get('current_stage') in interview_stages
        ])
        
        return interviews / len(applications)
    
    @staticmethod
    async def template_effectiveness_score(data: Dict[str, Any]) -> float:
        """Calculate weighted template effectiveness"""
        template_stats = data.get('template_performance', {})
        if not template_stats:
            return 0.0
        
        total_score = 0.0
        total_weight = 0.0
        
        for template, stats in template_stats.items():
            usage_count = stats.get('usage_count', 0)
            response_rate = stats.get('response_rate', 0)
            success_rate = stats.get('success_rate', 0)
            
            # Weight by usage
            weight = usage_count
            score = (0.3 * response_rate) + (0.7 * success_rate)
            
            total_score += score * weight
            total_weight += weight
        
        return total_score / total_weight if total_weight > 0 else 0.0
    
    @staticmethod
    async def user_engagement_score(data: Dict[str, Any]) -> float:
        """Calculate user engagement with the system"""
        user_sessions = data.get('user_sessions', [])
        if not user_sessions:
            return 0.0
        
        # Calculate engagement factors
        session_frequency = len(user_sessions) / 30  # sessions per day
        avg_session_duration = statistics.mean([
            session.get('duration_minutes', 0) for session in user_sessions
        ]) if user_sessions else 0
        
        feature_usage = len(set([
            action.get('feature') for session in user_sessions
            for action in session.get('actions', [])
        ]))
        
        # Weighted engagement score
        engagement = (
            min(session_frequency * 10, 100) * 0.4 +  # Frequency (capped)
            min(avg_session_duration * 2, 100) * 0.3 +  # Duration
            min(feature_usage * 5, 100) * 0.3  # Feature diversity
        ) / 100
        
        return min(engagement, 1.0)
    
    @staticmethod
    async def automation_efficiency(data: Dict[str, Any]) -> float:
        """Calculate automation efficiency ratio"""
        automated_tasks = data.get('automated_task_count', 0)
        manual_tasks = data.get('manual_task_count', 0)
        total_tasks = automated_tasks + manual_tasks
        
        return automated_tasks / total_tasks if total_tasks > 0 else 0.0
    
    @staticmethod
    async def quality_consistency_score(data: Dict[str, Any]) -> float:
        """Calculate consistency of output quality"""
        quality_scores = data.get('quality_scores', [])
        if len(quality_scores) < 2:
            return 1.0  # Perfect consistency if too few samples
        
        # Calculate coefficient of variation (lower = more consistent)
        mean_quality = statistics.mean(quality_scores)
        std_dev = statistics.stdev(quality_scores)
        
        if mean_quality == 0:
            return 0.0
        
        cv = std_dev / mean_quality
        # Convert to consistency score (higher = more consistent)
        consistency = max(0, 1 - cv)
        
        return consistency
    
    @staticmethod
    async def predictive_success_probability(data: Dict[str, Any]) -> float:
        """Predict success probability for current pipeline"""
        # Simplified predictive model based on historical patterns
        current_applications = data.get('current_applications', [])
        historical_success_rate = data.get('historical_success_rate', 0.0)
        
        if not current_applications:
            return historical_success_rate
        
        # Adjust based on current application quality indicators
        quality_indicators = []
        for app in current_applications:
            # Factors that predict success
            skill_match = app.get('skill_match_score', 0.5)
            company_fit = app.get('company_fit_score', 0.5)
            application_quality = app.get('quality_score', 0.5)
            
            combined_score = (skill_match + company_fit + application_quality) / 3
            quality_indicators.append(combined_score)
        
        avg_quality = statistics.mean(quality_indicators) if quality_indicators else 0.5
        
        # Adjust historical rate by current quality
        predicted_rate = historical_success_rate * (0.5 + avg_quality)
        
        return min(predicted_rate, 1.0)


class PerformanceMetricsEngine:
    """Main performance metrics calculation and tracking engine"""
    
    def __init__(self):
        self.metric_definitions: Dict[str, MetricDefinition] = {}
        self.metric_results: Dict[str, List[MetricResult]] = defaultdict(list)
        self.calculation_cache: Dict[str, Any] = {}
        self.cache_ttl = 300  # 5 minutes
        
        # Initialize standard metrics
        self._initialize_standard_metrics()
    
    def _initialize_standard_metrics(self):
        """Initialize standard performance metrics"""
        
        # Effectiveness Metrics
        self.register_metric(MetricDefinition(
            metric_id="application_success_rate",
            name="Application Success Rate",
            description="Percentage of applications resulting in offers",
            category=MetricCategory.EFFECTIVENESS,
            unit="percentage",
            aggregation_type=MetricAggregationType.AVERAGE,
            calculation_function=MetricCalculations.application_success_rate,
            is_kpi=True,
            tags=["applications", "success", "kpi"]
        ))
        
        self.register_metric(MetricDefinition(
            metric_id="interview_conversion_rate",
            name="Interview Conversion Rate",
            description="Percentage of applications leading to interviews",
            category=MetricCategory.CONVERSION,
            unit="percentage",
            aggregation_type=MetricAggregationType.AVERAGE,
            calculation_function=MetricCalculations.interview_conversion_rate,
            is_kpi=True,
            tags=["interviews", "conversion", "kpi"]
        ))
        
        # Efficiency Metrics
        self.register_metric(MetricDefinition(
            metric_id="avg_time_to_response",
            name="Average Time to Response",
            description="Average time from application to first response",
            category=MetricCategory.EFFICIENCY,
            unit="hours",
            aggregation_type=MetricAggregationType.AVERAGE,
            calculation_function=MetricCalculations.average_time_to_response,
            tags=["response_time", "efficiency"]
        ))
        
        self.register_metric(MetricDefinition(
            metric_id="automation_efficiency",
            name="Automation Efficiency",
            description="Ratio of automated vs manual tasks",
            category=MetricCategory.EFFICIENCY,
            unit="percentage",
            aggregation_type=MetricAggregationType.AVERAGE,
            calculation_function=MetricCalculations.automation_efficiency,
            tags=["automation", "efficiency"]
        ))
        
        # Quality Metrics
        self.register_metric(MetricDefinition(
            metric_id="template_effectiveness",
            name="Template Effectiveness Score",
            description="Weighted effectiveness of all templates",
            category=MetricCategory.QUALITY,
            unit="score",
            aggregation_type=MetricAggregationType.AVERAGE,
            calculation_function=MetricCalculations.template_effectiveness_score,
            tags=["templates", "quality"]
        ))
        
        self.register_metric(MetricDefinition(
            metric_id="quality_consistency",
            name="Quality Consistency Score",
            description="Consistency of output quality across applications",
            category=MetricCategory.QUALITY,
            unit="score",
            aggregation_type=MetricAggregationType.AVERAGE,
            calculation_function=MetricCalculations.quality_consistency_score,
            tags=["quality", "consistency"]
        ))
        
        # Engagement Metrics
        self.register_metric(MetricDefinition(
            metric_id="user_engagement",
            name="User Engagement Score",
            description="Overall user engagement with the platform",
            category=MetricCategory.ENGAGEMENT,
            unit="score",
            aggregation_type=MetricAggregationType.AVERAGE,
            calculation_function=MetricCalculations.user_engagement_score,
            tags=["engagement", "usage"]
        ))
        
        # Predictive Metrics
        self.register_metric(MetricDefinition(
            metric_id="predicted_success_rate",
            name="Predicted Success Rate",
            description="AI-predicted success rate for current applications",
            category=MetricCategory.PREDICTIVE,
            unit="percentage",
            aggregation_type=MetricAggregationType.AVERAGE,
            calculation_function=MetricCalculations.predictive_success_probability,
            tags=["prediction", "ai", "forecast"]
        ))
    
    def register_metric(self, metric_definition: MetricDefinition):
        """Register a new metric definition"""
        self.metric_definitions[metric_definition.metric_id] = metric_definition
        logger.info(f"Registered metric: {metric_definition.metric_id}")
    
    async def calculate_metric(
        self,
        metric_id: str,
        data: Dict[str, Any],
        period: str = "daily",
        force_recalculate: bool = False
    ) -> MetricResult:
        """Calculate a specific metric"""
        
        if metric_id not in self.metric_definitions:
            raise ValueError(f"Unknown metric: {metric_id}")
        
        # Check cache
        cache_key = f"{metric_id}_{period}_{hash(str(data))}"
        if not force_recalculate and cache_key in self.calculation_cache:
            cached_result, cache_time = self.calculation_cache[cache_key]
            if (datetime.utcnow() - cache_time).seconds < self.cache_ttl:
                return cached_result
        
        metric_def = self.metric_definitions[metric_id]
        
        # Calculate dependencies first
        dependency_results = {}
        for dep_metric_id in metric_def.dependencies:
            dep_result = await self.calculate_metric(dep_metric_id, data, period)
            dependency_results[dep_metric_id] = dep_result.value
        
        # Add dependency results to data
        enhanced_data = {**data, 'dependency_results': dependency_results}
        
        # Calculate the metric
        try:
            value = await metric_def.calculation_function(enhanced_data)
            confidence = self._calculate_confidence(metric_id, data)
            
            result = MetricResult(
                metric_id=metric_id,
                value=value,
                timestamp=datetime.utcnow(),
                period=period,
                confidence_score=confidence,
                metadata={
                    'data_points': len(data.get('applications', [])),
                    'calculation_method': metric_def.calculation_function.__name__
                }
            )
            
            # Cache result
            self.calculation_cache[cache_key] = (result, datetime.utcnow())
            
            # Store result
            self.metric_results[metric_id].append(result)
            
            return result
            
        except Exception as e:
            logger.error(f"Error calculating metric {metric_id}: {str(e)}")
            raise
    
    async def calculate_all_metrics(
        self,
        data: Dict[str, Any],
        period: str = "daily",
        categories: List[MetricCategory] = None
    ) -> Dict[str, MetricResult]:
        """Calculate all registered metrics"""
        
        results = {}
        
        # Filter metrics by categories if specified
        metrics_to_calculate = self.metric_definitions
        if categories:
            category_values = [cat.value for cat in categories]
            metrics_to_calculate = {
                metric_id: metric_def
                for metric_id, metric_def in self.metric_definitions.items()
                if metric_def.category.value in category_values
            }
        
        # Calculate metrics in dependency order
        calculated = set()
        while len(calculated) < len(metrics_to_calculate):
            for metric_id, metric_def in metrics_to_calculate.items():
                if metric_id in calculated:
                    continue
                
                # Check if all dependencies are calculated
                deps_ready = all(dep in calculated for dep in metric_def.dependencies)
                if deps_ready:
                    try:
                        result = await self.calculate_metric(metric_id, data, period)
                        results[metric_id] = result
                        calculated.add(metric_id)
                    except Exception as e:
                        logger.error(f"Failed to calculate {metric_id}: {str(e)}")
                        calculated.add(metric_id)  # Skip this metric
        
        return results
    
    def get_metric_trends(
        self,
        metric_id: str,
        periods: int = 7,
        period_type: str = "daily"
    ) -> List[MetricTrend]:
        """Calculate trends for a metric over time"""
        
        if metric_id not in self.metric_results:
            return []
        
        results = self.metric_results[metric_id]
        if len(results) < 2:
            return []
        
        # Sort by timestamp
        results = sorted(results, key=lambda x: x.timestamp)
        
        trends = []
        for i in range(1, min(len(results), periods + 1)):
            current = results[-i]
            previous = results[-i-1] if i < len(results) else results[0]
            
            if previous.value == 0:
                change_pct = 100.0 if current.value > 0 else 0.0
            else:
                change_pct = ((current.value - previous.value) / previous.value) * 100
            
            # Determine trend direction and significance
            if abs(change_pct) < 5:
                direction = "stable"
                significance = "insignificant"
            elif change_pct > 0:
                direction = "up"
                significance = "significant" if abs(change_pct) > 15 else "minor"
            else:
                direction = "down"
                significance = "significant" if abs(change_pct) > 15 else "minor"
            
            trend = MetricTrend(
                metric_id=metric_id,
                current_value=current.value,
                previous_value=previous.value,
                change_percentage=change_pct,
                trend_direction=direction,
                significance=significance,
                period_comparison=f"{period_type}-over-{period_type}"
            )
            
            trends.append(trend)
        
        return trends
    
    def get_kpi_summary(self, period: str = "monthly") -> Dict[str, Any]:
        """Get summary of Key Performance Indicators"""
        
        kpi_metrics = {
            metric_id: metric_def
            for metric_id, metric_def in self.metric_definitions.items()
            if metric_def.is_kpi
        }
        
        kpi_summary = {
            'period': period,
            'timestamp': datetime.utcnow().isoformat(),
            'kpis': {},
            'overall_score': 0.0
        }
        
        total_score = 0.0
        valid_kpis = 0
        
        for metric_id, metric_def in kpi_metrics.items():
            if metric_id in self.metric_results and self.metric_results[metric_id]:
                latest_result = self.metric_results[metric_id][-1]
                trend = self.get_metric_trends(metric_id, periods=2)
                
                kpi_summary['kpis'][metric_id] = {
                    'name': metric_def.name,
                    'current_value': latest_result.value,
                    'unit': metric_def.unit,
                    'confidence': latest_result.confidence_score,
                    'trend': trend[0].to_dict() if trend else None
                }
                
                # Add to overall score (normalized)
                normalized_value = min(latest_result.value, 1.0) if metric_def.unit == "percentage" else latest_result.value
                total_score += normalized_value
                valid_kpis += 1
        
        kpi_summary['overall_score'] = total_score / valid_kpis if valid_kpis > 0 else 0.0
        
        return kpi_summary
    
    def _calculate_confidence(self, metric_id: str, data: Dict[str, Any]) -> float:
        """Calculate confidence score for a metric based on data quality"""
        
        # Base confidence on data completeness and sample size
        applications = data.get('applications', [])
        data_points = len(applications)
        
        if data_points == 0:
            return 0.0
        elif data_points < 10:
            return 0.5
        elif data_points < 50:
            return 0.7
        elif data_points < 100:
            return 0.85
        else:
            return 0.95
    
    def get_metric_definition(self, metric_id: str) -> Optional[MetricDefinition]:
        """Get definition for a specific metric"""
        return self.metric_definitions.get(metric_id)
    
    def get_all_metric_definitions(self) -> List[MetricDefinition]:
        """Get all registered metric definitions"""
        return list(self.metric_definitions.values())
    
    def get_metrics_by_category(self, category: MetricCategory) -> List[MetricDefinition]:
        """Get all metrics in a specific category"""
        return [
            metric_def for metric_def in self.metric_definitions.values()
            if metric_def.category == category
        ]


# Global performance metrics engine
global_metrics_engine = PerformanceMetricsEngine()