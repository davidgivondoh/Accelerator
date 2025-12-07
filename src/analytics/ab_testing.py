"""
A/B Testing Framework

Comprehensive framework for running controlled experiments to optimize
application success rates, content effectiveness, and user experience.
"""

import asyncio
import json
import numpy as np
import hashlib
from typing import Dict, List, Optional, Any, Tuple, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from collections import defaultdict
import logging
import random

# Optional scipy import - provides statistical tests
try:
    from scipy import stats
    SCIPY_AVAILABLE = True
except ImportError:
    stats = None
    SCIPY_AVAILABLE = False

logger = logging.getLogger(__name__)


class ExperimentType(Enum):
    """Types of A/B experiments"""
    TEMPLATE_COMPARISON = "template_comparison"           # Compare different templates
    TIMING_OPTIMIZATION = "timing_optimization"         # Test different submission times
    CONTENT_VARIATION = "content_variation"             # Test content variations
    SUBJECT_LINE_TEST = "subject_line_test"             # Email subject line testing
    PLATFORM_STRATEGY = "platform_strategy"            # Compare platform strategies
    FOLLOW_UP_TIMING = "follow_up_timing"               # Test follow-up schedules
    PERSONALIZATION_LEVEL = "personalization_level"    # Test personalization depth


class ExperimentStatus(Enum):
    """Experiment lifecycle status"""
    DRAFT = "draft"                    # Being designed
    ACTIVE = "active"                  # Currently running
    PAUSED = "paused"                  # Temporarily stopped
    COMPLETED = "completed"            # Finished successfully
    STOPPED = "stopped"                # Stopped early
    FAILED = "failed"                  # Failed to complete


class StatisticalSignificance(Enum):
    """Statistical significance levels"""
    NOT_SIGNIFICANT = "not_significant"     # p > 0.05
    MARGINALLY_SIGNIFICANT = "marginal"     # 0.01 < p <= 0.05  
    SIGNIFICANT = "significant"             # 0.001 < p <= 0.01
    HIGHLY_SIGNIFICANT = "highly_significant"  # p <= 0.001


@dataclass
class ExperimentVariant:
    """Individual variant in an A/B test"""
    variant_id: str
    name: str
    description: str
    configuration: Dict[str, Any]
    allocation_percentage: float  # 0-100
    is_control: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'variant_id': self.variant_id,
            'name': self.name,
            'description': self.description,
            'configuration': self.configuration,
            'allocation_percentage': self.allocation_percentage,
            'is_control': self.is_control
        }


@dataclass
class ExperimentMetric:
    """Metric to be measured in the experiment"""
    metric_id: str
    name: str
    description: str
    metric_type: str  # conversion_rate, average_value, count
    is_primary: bool = False  # Primary metric for decision making
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'metric_id': self.metric_id,
            'name': self.name,
            'description': self.description,
            'metric_type': self.metric_type,
            'is_primary': self.is_primary
        }


@dataclass
class ExperimentResult:
    """Results for a specific variant and metric"""
    variant_id: str
    metric_id: str
    sample_size: int
    value: float
    confidence_interval: Tuple[float, float]
    standard_error: float
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'variant_id': self.variant_id,
            'metric_id': self.metric_id,
            'sample_size': self.sample_size,
            'value': self.value,
            'confidence_interval': list(self.confidence_interval),
            'standard_error': self.standard_error
        }


@dataclass
class ExperimentComparison:
    """Statistical comparison between variants"""
    variant_a_id: str
    variant_b_id: str
    metric_id: str
    lift: float  # Percentage improvement of B over A
    p_value: float
    significance: StatisticalSignificance
    confidence_level: float
    is_winner: Optional[str] = None  # variant_id of winner, if any
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'variant_a_id': self.variant_a_id,
            'variant_b_id': self.variant_b_id,
            'metric_id': self.metric_id,
            'lift': self.lift,
            'p_value': self.p_value,
            'significance': self.significance.value,
            'confidence_level': self.confidence_level,
            'is_winner': self.is_winner
        }


@dataclass
class Experiment:
    """Complete A/B test experiment"""
    experiment_id: str
    name: str
    description: str
    experiment_type: ExperimentType
    variants: List[ExperimentVariant]
    metrics: List[ExperimentMetric]
    target_users: Dict[str, Any]  # User targeting criteria
    start_date: datetime
    end_date: Optional[datetime]
    status: ExperimentStatus
    created_by: str
    min_sample_size: int = 100
    confidence_level: float = 0.95
    max_duration_days: int = 30
    results: List[ExperimentResult] = field(default_factory=list)
    comparisons: List[ExperimentComparison] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'experiment_id': self.experiment_id,
            'name': self.name,
            'description': self.description,
            'experiment_type': self.experiment_type.value,
            'variants': [v.to_dict() for v in self.variants],
            'metrics': [m.to_dict() for m in self.metrics],
            'target_users': self.target_users,
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'status': self.status.value,
            'created_by': self.created_by,
            'min_sample_size': self.min_sample_size,
            'confidence_level': self.confidence_level,
            'max_duration_days': self.max_duration_days,
            'results': [r.to_dict() for r in self.results],
            'comparisons': [c.to_dict() for c in self.comparisons],
            'metadata': self.metadata
        }


class UserAssignment:
    """Handles user assignment to experiment variants"""
    
    def __init__(self):
        self.assignments: Dict[str, Dict[str, str]] = {}  # user_id -> {experiment_id: variant_id}
    
    def assign_user_to_variant(self, user_id: str, experiment: Experiment) -> str:
        """Assign user to a variant using consistent hashing"""
        
        # Check if user already assigned
        if user_id in self.assignments and experiment.experiment_id in self.assignments[user_id]:
            return self.assignments[user_id][experiment.experiment_id]
        
        # Use consistent hashing for deterministic assignment
        hash_input = f"{user_id}:{experiment.experiment_id}"
        hash_value = int(hashlib.md5(hash_input.encode()).hexdigest(), 16)
        
        # Convert to percentage (0-100)
        percentage = (hash_value % 10000) / 100
        
        # Find variant based on allocation
        cumulative_allocation = 0
        for variant in experiment.variants:
            cumulative_allocation += variant.allocation_percentage
            if percentage <= cumulative_allocation:
                # Store assignment
                if user_id not in self.assignments:
                    self.assignments[user_id] = {}
                self.assignments[user_id][experiment.experiment_id] = variant.variant_id
                
                return variant.variant_id
        
        # Fallback to control variant
        control_variant = next((v for v in experiment.variants if v.is_control), experiment.variants[0])
        self.assignments[user_id][experiment.experiment_id] = control_variant.variant_id
        
        return control_variant.variant_id
    
    def get_user_variant(self, user_id: str, experiment_id: str) -> Optional[str]:
        """Get user's assigned variant for an experiment"""
        return self.assignments.get(user_id, {}).get(experiment_id)


class ExperimentDataCollector:
    """Collects and stores experiment data"""
    
    def __init__(self):
        self.experiment_data: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    
    def record_event(
        self,
        experiment_id: str,
        user_id: str,
        variant_id: str,
        event_type: str,
        event_data: Dict[str, Any]
    ):
        """Record an experiment event"""
        
        event = {
            'experiment_id': experiment_id,
            'user_id': user_id,
            'variant_id': variant_id,
            'event_type': event_type,
            'event_data': event_data,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        self.experiment_data[experiment_id].append(event)
        
        logger.debug(f"Recorded experiment event: {experiment_id}:{variant_id}:{event_type}")
    
    def get_experiment_events(
        self,
        experiment_id: str,
        variant_id: Optional[str] = None,
        event_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get events for an experiment"""
        
        events = self.experiment_data.get(experiment_id, [])
        
        if variant_id:
            events = [e for e in events if e['variant_id'] == variant_id]
        
        if event_type:
            events = [e for e in events if e['event_type'] == event_type]
        
        return events
    
    def calculate_metric_value(
        self,
        experiment_id: str,
        variant_id: str,
        metric: ExperimentMetric
    ) -> Tuple[float, int]:
        """Calculate metric value for a variant"""
        
        events = self.get_experiment_events(experiment_id, variant_id)
        
        if metric.metric_type == "conversion_rate":
            # Count conversion events
            conversion_events = [e for e in events if e['event_type'] == 'conversion']
            total_users = len(set(e['user_id'] for e in events))
            
            if total_users == 0:
                return 0.0, 0
            
            conversion_rate = len(conversion_events) / total_users
            return conversion_rate, total_users
        
        elif metric.metric_type == "average_value":
            # Calculate average of numeric values
            value_events = [e for e in events if e['event_type'] == 'value' and 'value' in e['event_data']]
            
            if not value_events:
                return 0.0, 0
            
            values = [e['event_data']['value'] for e in value_events]
            avg_value = np.mean(values)
            return avg_value, len(value_events)
        
        elif metric.metric_type == "count":
            # Count specific events
            target_events = [e for e in events if e['event_type'] == metric.metric_id]
            return len(target_events), len(events)
        
        return 0.0, 0


class StatisticalAnalyzer:
    """Performs statistical analysis on experiment results"""
    
    @staticmethod
    def calculate_confidence_interval(
        data: List[float],
        confidence_level: float = 0.95
    ) -> Tuple[float, float]:
        """Calculate confidence interval for a dataset"""
        
        if len(data) < 2:
            return (0.0, 0.0)
        
        mean = np.mean(data)
        sem = stats.sem(data)  # Standard error of mean
        
        # Calculate confidence interval
        h = sem * stats.t.ppf((1 + confidence_level) / 2, len(data) - 1)
        
        return (mean - h, mean + h)
    
    @staticmethod
    def compare_variants(
        variant_a_data: List[float],
        variant_b_data: List[float],
        confidence_level: float = 0.95
    ) -> ExperimentComparison:
        """Compare two variants statistically"""
        
        if len(variant_a_data) < 2 or len(variant_b_data) < 2:
            return None
        
        # Perform t-test
        t_stat, p_value = stats.ttest_ind(variant_b_data, variant_a_data)
        
        # Calculate means
        mean_a = np.mean(variant_a_data)
        mean_b = np.mean(variant_b_data)
        
        # Calculate lift (percentage improvement)
        lift = 0.0
        if mean_a != 0:
            lift = ((mean_b - mean_a) / mean_a) * 100
        
        # Determine significance
        if p_value <= 0.001:
            significance = StatisticalSignificance.HIGHLY_SIGNIFICANT
        elif p_value <= 0.01:
            significance = StatisticalSignificance.SIGNIFICANT
        elif p_value <= 0.05:
            significance = StatisticalSignificance.MARGINALLY_SIGNIFICANT
        else:
            significance = StatisticalSignificance.NOT_SIGNIFICANT
        
        # Determine winner
        winner = None
        if significance != StatisticalSignificance.NOT_SIGNIFICANT:
            winner = "variant_b" if mean_b > mean_a else "variant_a"
        
        return {
            'lift': lift,
            'p_value': p_value,
            'significance': significance,
            'confidence_level': confidence_level,
            'winner': winner
        }
    
    @staticmethod
    def calculate_required_sample_size(
        baseline_rate: float,
        minimum_effect: float,
        power: float = 0.8,
        alpha: float = 0.05
    ) -> int:
        """Calculate required sample size for experiment"""
        
        # Using formula for comparing two proportions
        z_alpha = stats.norm.ppf(1 - alpha / 2)
        z_beta = stats.norm.ppf(power)
        
        p1 = baseline_rate
        p2 = baseline_rate * (1 + minimum_effect)
        
        p_pooled = (p1 + p2) / 2
        
        numerator = (z_alpha * np.sqrt(2 * p_pooled * (1 - p_pooled)) + 
                    z_beta * np.sqrt(p1 * (1 - p1) + p2 * (1 - p2)))**2
        
        denominator = (p2 - p1)**2
        
        sample_size = int(np.ceil(numerator / denominator))
        
        return max(sample_size, 50)  # Minimum 50 per variant


class ABTestingFramework:
    """Main A/B testing framework"""
    
    def __init__(self):
        self.experiments: Dict[str, Experiment] = {}
        self.user_assignment = UserAssignment()
        self.data_collector = ExperimentDataCollector()
        self.analyzer = StatisticalAnalyzer()
        
        # Background task for monitoring experiments
        asyncio.create_task(self._monitor_experiments())
    
    def create_experiment(
        self,
        name: str,
        description: str,
        experiment_type: ExperimentType,
        variants: List[ExperimentVariant],
        metrics: List[ExperimentMetric],
        created_by: str,
        target_users: Dict[str, Any] = None,
        min_sample_size: int = 100,
        confidence_level: float = 0.95,
        max_duration_days: int = 30
    ) -> Experiment:
        """Create a new A/B test experiment"""
        
        # Validate variants
        total_allocation = sum(v.allocation_percentage for v in variants)
        if abs(total_allocation - 100.0) > 0.01:
            raise ValueError(f"Variant allocations must sum to 100%, got {total_allocation}")
        
        # Ensure at least one control variant
        if not any(v.is_control for v in variants):
            variants[0].is_control = True
        
        experiment_id = f"exp_{int(datetime.utcnow().timestamp())}_{hash(name) % 1000}"
        
        experiment = Experiment(
            experiment_id=experiment_id,
            name=name,
            description=description,
            experiment_type=experiment_type,
            variants=variants,
            metrics=metrics,
            target_users=target_users or {},
            start_date=datetime.utcnow(),
            end_date=None,
            status=ExperimentStatus.DRAFT,
            created_by=created_by,
            min_sample_size=min_sample_size,
            confidence_level=confidence_level,
            max_duration_days=max_duration_days
        )
        
        self.experiments[experiment_id] = experiment
        
        logger.info(f"Created experiment: {experiment_id}")
        return experiment
    
    def start_experiment(self, experiment_id: str) -> bool:
        """Start an experiment"""
        
        if experiment_id not in self.experiments:
            return False
        
        experiment = self.experiments[experiment_id]
        
        if experiment.status != ExperimentStatus.DRAFT:
            return False
        
        experiment.status = ExperimentStatus.ACTIVE
        experiment.start_date = datetime.utcnow()
        
        logger.info(f"Started experiment: {experiment_id}")
        return True
    
    def stop_experiment(self, experiment_id: str, reason: str = "manual_stop") -> bool:
        """Stop an experiment"""
        
        if experiment_id not in self.experiments:
            return False
        
        experiment = self.experiments[experiment_id]
        
        if experiment.status != ExperimentStatus.ACTIVE:
            return False
        
        experiment.status = ExperimentStatus.STOPPED
        experiment.end_date = datetime.utcnow()
        experiment.metadata['stop_reason'] = reason
        
        # Perform final analysis
        self._analyze_experiment(experiment_id)
        
        logger.info(f"Stopped experiment: {experiment_id}")
        return True
    
    def get_user_variant(self, user_id: str, experiment_id: str) -> Optional[ExperimentVariant]:
        """Get the variant assigned to a user"""
        
        if experiment_id not in self.experiments:
            return None
        
        experiment = self.experiments[experiment_id]
        
        if experiment.status != ExperimentStatus.ACTIVE:
            return None
        
        # Check if user matches targeting criteria
        if not self._user_matches_targeting(user_id, experiment.target_users):
            return None
        
        variant_id = self.user_assignment.assign_user_to_variant(user_id, experiment)
        
        return next((v for v in experiment.variants if v.variant_id == variant_id), None)
    
    def record_event(
        self,
        experiment_id: str,
        user_id: str,
        event_type: str,
        event_data: Dict[str, Any] = None
    ):
        """Record an event for an experiment"""
        
        if experiment_id not in self.experiments:
            return
        
        experiment = self.experiments[experiment_id]
        
        if experiment.status != ExperimentStatus.ACTIVE:
            return
        
        variant_id = self.user_assignment.get_user_variant(user_id, experiment_id)
        if not variant_id:
            return
        
        self.data_collector.record_event(
            experiment_id,
            user_id,
            variant_id,
            event_type,
            event_data or {}
        )
    
    def get_experiment_results(self, experiment_id: str) -> Optional[Dict[str, Any]]:
        """Get current results for an experiment"""
        
        if experiment_id not in self.experiments:
            return None
        
        experiment = self.experiments[experiment_id]
        
        # Calculate results for each variant and metric
        results = []
        
        for variant in experiment.variants:
            for metric in experiment.metrics:
                # Get raw data for statistical analysis
                events = self.data_collector.get_experiment_events(experiment_id, variant.variant_id)
                
                if metric.metric_type == "conversion_rate":
                    conversions = [1 if e['event_type'] == 'conversion' else 0 for e in events]
                    data = conversions
                elif metric.metric_type == "average_value":
                    value_events = [e for e in events if e['event_type'] == 'value' and 'value' in e['event_data']]
                    data = [e['event_data']['value'] for e in value_events]
                else:
                    data = [1] * len(events)  # Count data
                
                if data:
                    value = np.mean(data)
                    ci = self.analyzer.calculate_confidence_interval(data, experiment.confidence_level)
                    se = np.std(data) / np.sqrt(len(data)) if len(data) > 1 else 0
                    
                    result = ExperimentResult(
                        variant_id=variant.variant_id,
                        metric_id=metric.metric_id,
                        sample_size=len(data),
                        value=value,
                        confidence_interval=ci,
                        standard_error=se
                    )
                    results.append(result)
        
        # Perform comparisons between variants
        comparisons = self._calculate_comparisons(experiment, results)
        
        return {
            'experiment': experiment.to_dict(),
            'results': [r.to_dict() for r in results],
            'comparisons': [c.to_dict() for c in comparisons],
            'recommendations': self._generate_recommendations(experiment, results, comparisons)
        }
    
    def _calculate_comparisons(self, experiment: Experiment, results: List[ExperimentResult]) -> List[ExperimentComparison]:
        """Calculate statistical comparisons between variants"""
        
        comparisons = []
        control_variant = next((v for v in experiment.variants if v.is_control), experiment.variants[0])
        
        for metric in experiment.metrics:
            # Get control results for this metric
            control_results = [r for r in results if r.variant_id == control_variant.variant_id and r.metric_id == metric.metric_id]
            
            if not control_results:
                continue
            
            control_result = control_results[0]
            
            # Compare each variant to control
            for variant in experiment.variants:
                if variant.variant_id == control_variant.variant_id:
                    continue
                
                variant_results = [r for r in results if r.variant_id == variant.variant_id and r.metric_id == metric.metric_id]
                
                if not variant_results:
                    continue
                
                variant_result = variant_results[0]
                
                # Get raw data for statistical test
                control_events = self.data_collector.get_experiment_events(experiment.experiment_id, control_variant.variant_id)
                variant_events = self.data_collector.get_experiment_events(experiment.experiment_id, variant.variant_id)
                
                # Extract metric values
                control_data = self._extract_metric_data(control_events, metric)
                variant_data = self._extract_metric_data(variant_events, metric)
                
                if len(control_data) >= 10 and len(variant_data) >= 10:  # Minimum sample size
                    comparison_stats = self.analyzer.compare_variants(
                        control_data, variant_data, experiment.confidence_level
                    )
                    
                    if comparison_stats:
                        comparison = ExperimentComparison(
                            variant_a_id=control_variant.variant_id,
                            variant_b_id=variant.variant_id,
                            metric_id=metric.metric_id,
                            lift=comparison_stats['lift'],
                            p_value=comparison_stats['p_value'],
                            significance=comparison_stats['significance'],
                            confidence_level=experiment.confidence_level,
                            is_winner=comparison_stats['winner']
                        )
                        comparisons.append(comparison)
        
        return comparisons
    
    def _extract_metric_data(self, events: List[Dict[str, Any]], metric: ExperimentMetric) -> List[float]:
        """Extract metric data from events for statistical analysis"""
        
        if metric.metric_type == "conversion_rate":
            # Create binary data (1 for conversion, 0 for non-conversion)
            users = set(e['user_id'] for e in events)
            converting_users = set(e['user_id'] for e in events if e['event_type'] == 'conversion')
            
            data = []
            for user in users:
                data.append(1.0 if user in converting_users else 0.0)
            
            return data
        
        elif metric.metric_type == "average_value":
            value_events = [e for e in events if e['event_type'] == 'value' and 'value' in e['event_data']]
            return [float(e['event_data']['value']) for e in value_events]
        
        elif metric.metric_type == "count":
            target_events = [e for e in events if e['event_type'] == metric.metric_id]
            return [1.0] * len(target_events)
        
        return []
    
    def _user_matches_targeting(self, user_id: str, target_criteria: Dict[str, Any]) -> bool:
        """Check if user matches experiment targeting criteria"""
        
        if not target_criteria:
            return True
        
        # Implement targeting logic based on user attributes
        # This would integrate with user profile system
        
        return True  # Simplified - include all users
    
    def _generate_recommendations(
        self,
        experiment: Experiment,
        results: List[ExperimentResult],
        comparisons: List[ExperimentComparison]
    ) -> List[str]:
        """Generate recommendations based on experiment results"""
        
        recommendations = []
        
        # Check for statistical significance
        significant_wins = [c for c in comparisons if c.significance in [
            StatisticalSignificance.SIGNIFICANT,
            StatisticalSignificance.HIGHLY_SIGNIFICANT
        ]]
        
        if significant_wins:
            best_variant = max(significant_wins, key=lambda x: x.lift)
            recommendations.append(
                f"Variant {best_variant.variant_b_id} shows statistically significant improvement "
                f"of {best_variant.lift:.1f}% (p={best_variant.p_value:.4f})"
            )
        else:
            recommendations.append("No statistically significant differences detected yet")
        
        # Sample size recommendations
        min_sample_per_variant = experiment.min_sample_size
        for variant in experiment.variants:
            variant_results = [r for r in results if r.variant_id == variant.variant_id]
            if variant_results:
                sample_size = min(r.sample_size for r in variant_results)
                if sample_size < min_sample_per_variant:
                    recommendations.append(
                        f"Variant {variant.variant_id} needs more data "
                        f"({sample_size}/{min_sample_per_variant} samples)"
                    )
        
        # Duration recommendations
        days_running = (datetime.utcnow() - experiment.start_date).days
        if days_running < 7:
            recommendations.append("Experiment should run for at least 1 week for reliable results")
        elif days_running >= experiment.max_duration_days:
            recommendations.append("Experiment has reached maximum duration - consider stopping")
        
        return recommendations
    
    async def _monitor_experiments(self):
        """Background task to monitor experiment health"""
        
        while True:
            try:
                for experiment_id, experiment in self.experiments.items():
                    if experiment.status == ExperimentStatus.ACTIVE:
                        await self._check_experiment_health(experiment_id)
                
                await asyncio.sleep(3600)  # Check every hour
                
            except Exception as e:
                logger.error(f"Error in experiment monitoring: {str(e)}")
                await asyncio.sleep(300)  # Retry in 5 minutes
    
    async def _check_experiment_health(self, experiment_id: str):
        """Check health of running experiment"""
        
        experiment = self.experiments[experiment_id]
        
        # Auto-stop if maximum duration reached
        if experiment.max_duration_days > 0:
            days_running = (datetime.utcnow() - experiment.start_date).days
            if days_running >= experiment.max_duration_days:
                self.stop_experiment(experiment_id, "max_duration_reached")
                return
        
        # Check for early stopping based on statistical significance
        results = self.get_experiment_results(experiment_id)
        if results and results.get('comparisons'):
            highly_significant = [
                c for c in results['comparisons']
                if c['significance'] == StatisticalSignificance.HIGHLY_SIGNIFICANT.value
            ]
            
            if highly_significant and all(c['sample_size'] >= experiment.min_sample_size for c in results['results']):
                # Can stop early with high confidence
                self.stop_experiment(experiment_id, "early_stopping_significant_result")
    
    def _analyze_experiment(self, experiment_id: str):
        """Perform final analysis when experiment completes"""
        
        experiment = self.experiments[experiment_id]
        experiment.status = ExperimentStatus.COMPLETED
        
        # Store final results
        results = self.get_experiment_results(experiment_id)
        if results:
            experiment.results = [ExperimentResult(**r) for r in results['results']]
            experiment.comparisons = [ExperimentComparison(**c) for c in results['comparisons']]
        
        logger.info(f"Completed analysis for experiment: {experiment_id}")
    
    def get_active_experiments(self) -> List[Experiment]:
        """Get all active experiments"""
        return [e for e in self.experiments.values() if e.status == ExperimentStatus.ACTIVE]
    
    def get_experiment_summary(self) -> Dict[str, Any]:
        """Get summary of all experiments"""
        
        total_experiments = len(self.experiments)
        active_experiments = len(self.get_active_experiments())
        completed_experiments = len([e for e in self.experiments.values() if e.status == ExperimentStatus.COMPLETED])
        
        return {
            'total_experiments': total_experiments,
            'active_experiments': active_experiments,
            'completed_experiments': completed_experiments,
            'experiment_types': list(set(e.experiment_type.value for e in self.experiments.values())),
            'last_experiment_date': max([e.start_date for e in self.experiments.values()]).isoformat() if self.experiments else None
        }


# Global A/B testing framework
global_ab_testing_framework = ABTestingFramework()