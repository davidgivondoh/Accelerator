"""
Optimization Engine

AI-powered optimization system that automatically improves application success rates
by learning from patterns, A/B test results, and continuous performance monitoring.
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
import warnings
warnings.filterwarnings('ignore')

# Optional sklearn imports - provides ML optimization
try:
    from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
    from sklearn.model_selection import cross_val_score
    from sklearn.preprocessing import StandardScaler
    SKLEARN_AVAILABLE = True
except ImportError:
    RandomForestRegressor = None
    GradientBoostingRegressor = None
    cross_val_score = None
    StandardScaler = None
    SKLEARN_AVAILABLE = False

logger = logging.getLogger(__name__)


class OptimizationType(Enum):
    """Types of optimizations available"""
    TEMPLATE_SELECTION = "template_selection"           # Choose best templates
    TIMING_OPTIMIZATION = "timing_optimization"        # Optimize submission timing  
    CONTENT_PERSONALIZATION = "content_personalization" # Personalize content
    PLATFORM_ALLOCATION = "platform_allocation"        # Allocate across platforms
    FOLLOW_UP_SCHEDULING = "follow_up_scheduling"       # Optimize follow-up timing
    APPLICATION_PRIORITIZATION = "application_prioritization"  # Prioritize opportunities
    AUTOMATION_TUNING = "automation_tuning"            # Tune automation parameters


class OptimizationStrategy(Enum):
    """Optimization strategies"""
    CONSERVATIVE = "conservative"       # Slow, safe improvements
    BALANCED = "balanced"              # Moderate risk/reward
    AGGRESSIVE = "aggressive"          # Fast, higher-risk improvements
    EXPERIMENTAL = "experimental"     # Maximum experimentation


class OptimizationStatus(Enum):
    """Status of optimization processes"""
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class OptimizationRecommendation:
    """Individual optimization recommendation"""
    recommendation_id: str
    optimization_type: OptimizationType
    title: str
    description: str
    current_value: Any
    recommended_value: Any
    expected_improvement: float  # Expected % improvement
    confidence: float  # 0-1 confidence score
    implementation_effort: str  # low, medium, high
    risk_level: str  # low, medium, high
    supporting_evidence: List[str]
    created_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'recommendation_id': self.recommendation_id,
            'optimization_type': self.optimization_type.value,
            'title': self.title,
            'description': self.description,
            'current_value': self.current_value,
            'recommended_value': self.recommended_value,
            'expected_improvement': self.expected_improvement,
            'confidence': self.confidence,
            'implementation_effort': self.implementation_effort,
            'risk_level': self.risk_level,
            'supporting_evidence': self.supporting_evidence,
            'created_at': self.created_at.isoformat()
        }


@dataclass
class OptimizationPlan:
    """Comprehensive optimization plan"""
    plan_id: str
    name: str
    strategy: OptimizationStrategy
    recommendations: List[OptimizationRecommendation]
    priority_order: List[str]  # Recommendation IDs in priority order
    total_expected_improvement: float
    implementation_timeline_days: int
    created_at: datetime
    status: OptimizationStatus = OptimizationStatus.ACTIVE
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'plan_id': self.plan_id,
            'name': self.name,
            'strategy': self.strategy.value,
            'recommendations': [r.to_dict() for r in self.recommendations],
            'priority_order': self.priority_order,
            'total_expected_improvement': self.total_expected_improvement,
            'implementation_timeline_days': self.implementation_timeline_days,
            'created_at': self.created_at.isoformat(),
            'status': self.status.value
        }


class PerformancePredictor:
    """ML model for predicting performance improvements"""
    
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.feature_names = []
        self.is_trained = False
    
    def prepare_features(self, applications: List[Dict[str, Any]]) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare features for ML model"""
        
        features = []
        targets = []
        
        for app in applications:
            # Extract features
            feature_vector = []
            
            # Timing features
            submitted_date = datetime.fromisoformat(app.get('submitted_date', '').replace('Z', '+00:00'))
            feature_vector.extend([
                submitted_date.hour,  # Hour of day
                submitted_date.weekday(),  # Day of week
                submitted_date.day,  # Day of month
            ])
            
            # Application features
            feature_vector.extend([
                len(app.get('opportunity_title', '')),  # Title length
                app.get('skill_match_score', 0.5),  # Skill match
                len(app.get('notes', '')),  # Notes length
                1 if app.get('priority') == 'high' else 0,  # High priority
            ])
            
            # Company features
            company_name = app.get('company_name', '').lower()
            feature_vector.extend([
                len(company_name),  # Company name length
                1 if 'tech' in company_name else 0,  # Tech company
                1 if any(keyword in company_name for keyword in ['startup', 'inc', 'llc']) else 0,  # Startup indicators
            ])
            
            # Template features (if available)
            events = app.get('events', [])
            template_events = [e for e in events if 'template' in e.get('event_type', '').lower()]
            if template_events:
                template_type = template_events[0].get('metadata', {}).get('template_type', 'default')
                feature_vector.append(1 if template_type == 'professional' else 0)
                feature_vector.append(1 if template_type == 'creative' else 0)
            else:
                feature_vector.extend([0, 0])
            
            features.append(feature_vector)
            
            # Target: success score (0-1)
            if app.get('current_stage') in ['offer_accepted']:
                target = 1.0
            elif app.get('current_stage') in ['offer_extended']:
                target = 0.8
            elif app.get('current_stage') in ['final_interview', 'reference_check']:
                target = 0.6
            elif app.get('current_stage') in ['first_interview', 'technical_interview']:
                target = 0.4
            elif app.get('current_stage') in ['under_review', 'screening']:
                target = 0.2
            else:
                target = 0.0
            
            targets.append(target)
        
        if not features:
            return np.array([]), np.array([])
        
        # Store feature names for interpretation
        if not self.feature_names:
            self.feature_names = [
                'hour', 'weekday', 'day_of_month',
                'title_length', 'skill_match', 'notes_length', 'high_priority',
                'company_name_length', 'is_tech', 'is_startup',
                'template_professional', 'template_creative'
            ]
        
        return np.array(features), np.array(targets)
    
    def train(self, applications: List[Dict[str, Any]]) -> bool:
        """Train the performance prediction model"""
        
        if len(applications) < 50:
            logger.warning("Insufficient data to train performance predictor")
            return False
        
        try:
            X, y = self.prepare_features(applications)
            
            if len(X) < 20:
                return False
            
            # Scale features
            X_scaled = self.scaler.fit_transform(X)
            
            # Train ensemble model
            self.model = GradientBoostingRegressor(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=4,
                random_state=42
            )
            
            self.model.fit(X_scaled, y)
            
            # Validate model
            scores = cross_val_score(self.model, X_scaled, y, cv=5)
            avg_score = np.mean(scores)
            
            if avg_score > 0.1:  # Minimum acceptable performance
                self.is_trained = True
                logger.info(f"Trained performance predictor with score: {avg_score:.3f}")
                return True
            else:
                logger.warning(f"Performance predictor training failed with low score: {avg_score:.3f}")
                return False
                
        except Exception as e:
            logger.error(f"Error training performance predictor: {str(e)}")
            return False
    
    def predict_improvement(
        self,
        current_config: Dict[str, Any],
        proposed_config: Dict[str, Any]
    ) -> float:
        """Predict performance improvement from configuration change"""
        
        if not self.is_trained:
            return 0.0
        
        try:
            # Create feature vectors for both configurations
            current_features = self._config_to_features(current_config)
            proposed_features = self._config_to_features(proposed_config)
            
            # Scale features
            current_scaled = self.scaler.transform([current_features])
            proposed_scaled = self.scaler.transform([proposed_features])
            
            # Predict performance
            current_score = self.model.predict(current_scaled)[0]
            proposed_score = self.model.predict(proposed_scaled)[0]
            
            # Calculate improvement
            improvement = (proposed_score - current_score) / max(current_score, 0.01)
            
            return max(0.0, improvement)  # Only positive improvements
            
        except Exception as e:
            logger.error(f"Error predicting improvement: {str(e)}")
            return 0.0
    
    def _config_to_features(self, config: Dict[str, Any]) -> List[float]:
        """Convert configuration to feature vector"""
        
        # Default feature vector
        features = [0.0] * len(self.feature_names)
        
        # Map configuration to features
        if 'timing' in config:
            timing = config['timing']
            features[0] = timing.get('hour', 10)  # Default 10 AM
            features[1] = timing.get('weekday', 1)  # Default Tuesday
        
        if 'content' in config:
            content = config['content']
            features[3] = len(content.get('title', ''))
            features[5] = len(content.get('notes', ''))
        
        if 'template' in config:
            template_type = config['template'].get('type', 'default')
            features[10] = 1.0 if template_type == 'professional' else 0.0
            features[11] = 1.0 if template_type == 'creative' else 0.0
        
        return features
    
    def get_feature_importance(self) -> Dict[str, float]:
        """Get feature importance from trained model"""
        
        if not self.is_trained or not hasattr(self.model, 'feature_importances_'):
            return {}
        
        importance_dict = {}
        for name, importance in zip(self.feature_names, self.model.feature_importances_):
            importance_dict[name] = float(importance)
        
        return importance_dict


class OptimizationRecommender:
    """Generates optimization recommendations"""
    
    def __init__(self):
        self.predictor = PerformancePredictor()
        self.recommendation_history: Dict[str, List[OptimizationRecommendation]] = defaultdict(list)
    
    async def generate_recommendations(
        self,
        user_id: str,
        strategy: OptimizationStrategy = OptimizationStrategy.BALANCED
    ) -> List[OptimizationRecommendation]:
        """Generate personalized optimization recommendations"""
        
        # Get user data
        from ..pipeline.status_tracking import global_application_tracker
        from ..analytics.pattern_recognition import global_pattern_engine
        from ..analytics.performance_metrics import global_metrics_engine
        
        applications = global_application_tracker.get_user_applications(user_id)
        
        if len(applications) < 10:
            logger.info(f"Insufficient data for optimization recommendations: {len(applications)} applications")
            return []
        
        # Train predictor if not already trained
        if not self.predictor.is_trained:
            self.predictor.train(applications)
        
        recommendations = []
        
        # Template optimization recommendations
        template_recs = await self._generate_template_recommendations(user_id, applications, strategy)
        recommendations.extend(template_recs)
        
        # Timing optimization recommendations
        timing_recs = await self._generate_timing_recommendations(user_id, applications, strategy)
        recommendations.extend(timing_recs)
        
        # Content optimization recommendations
        content_recs = await self._generate_content_recommendations(user_id, applications, strategy)
        recommendations.extend(content_recs)
        
        # Platform optimization recommendations
        platform_recs = await self._generate_platform_recommendations(user_id, applications, strategy)
        recommendations.extend(platform_recs)
        
        # Sort by expected improvement
        recommendations.sort(key=lambda x: x.expected_improvement, reverse=True)
        
        # Store recommendations
        self.recommendation_history[user_id].extend(recommendations)
        
        return recommendations
    
    async def _generate_template_recommendations(
        self,
        user_id: str,
        applications: List[Dict[str, Any]],
        strategy: OptimizationStrategy
    ) -> List[OptimizationRecommendation]:
        """Generate template optimization recommendations"""
        
        recommendations = []
        
        # Analyze template performance
        template_performance = defaultdict(list)
        
        for app in applications:
            # Extract template type from events
            events = app.get('events', [])
            template_events = [e for e in events if 'template' in e.get('event_type', '').lower()]
            
            template_type = 'default'
            if template_events:
                template_type = template_events[0].get('metadata', {}).get('template_type', 'default')
            
            # Calculate success score
            success_score = self._calculate_success_score(app)
            template_performance[template_type].append(success_score)
        
        # Find best performing template
        template_averages = {}
        for template, scores in template_performance.items():
            if len(scores) >= 3:  # Minimum sample size
                template_averages[template] = np.mean(scores)
        
        if len(template_averages) >= 2:
            best_template = max(template_averages.keys(), key=lambda x: template_averages[x])
            current_template = max(template_performance.keys(), key=lambda x: len(template_performance[x]))
            
            if best_template != current_template:
                improvement = (template_averages[best_template] - template_averages.get(current_template, 0)) / max(template_averages.get(current_template, 0.01), 0.01)
                
                if improvement > 0.1:  # Minimum 10% improvement
                    recommendation = OptimizationRecommendation(
                        recommendation_id=f"template_{user_id}_{int(datetime.utcnow().timestamp())}",
                        optimization_type=OptimizationType.TEMPLATE_SELECTION,
                        title=f"Switch to {best_template} template",
                        description=f"Using {best_template} template shows {improvement*100:.1f}% better performance than your current {current_template} template",
                        current_value=current_template,
                        recommended_value=best_template,
                        expected_improvement=improvement * 100,
                        confidence=min(0.9, len(template_performance[best_template]) / 20),
                        implementation_effort="low",
                        risk_level="low",
                        supporting_evidence=[
                            f"{best_template} template: {template_averages[best_template]:.2f} avg success",
                            f"{current_template} template: {template_averages.get(current_template, 0):.2f} avg success",
                            f"Based on {len(template_performance[best_template])} {best_template} applications"
                        ],
                        created_at=datetime.utcnow()
                    )
                    recommendations.append(recommendation)
        
        return recommendations
    
    async def _generate_timing_recommendations(
        self,
        user_id: str,
        applications: List[Dict[str, Any]],
        strategy: OptimizationStrategy
    ) -> List[OptimizationRecommendation]:
        """Generate timing optimization recommendations"""
        
        recommendations = []
        
        # Analyze timing patterns
        hour_performance = defaultdict(list)
        day_performance = defaultdict(list)
        
        for app in applications:
            submitted_date = datetime.fromisoformat(app.get('submitted_date', '').replace('Z', '+00:00'))
            success_score = self._calculate_success_score(app)
            
            hour_performance[submitted_date.hour].append(success_score)
            day_performance[submitted_date.strftime('%A')].append(success_score)
        
        # Find best timing
        best_hours = self._find_best_timing_windows(hour_performance, min_samples=3)
        best_days = self._find_best_timing_windows(day_performance, min_samples=5)
        
        # Generate hour recommendation
        if best_hours:
            best_hour, best_score = best_hours[0]
            current_hours = [h for h, scores in hour_performance.items() if len(scores) >= 2]
            
            if current_hours:
                current_hour = max(current_hours, key=lambda x: len(hour_performance[x]))
                current_score = np.mean(hour_performance[current_hour])
                
                if best_hour != current_hour and best_score > current_score:
                    improvement = (best_score - current_score) / max(current_score, 0.01)
                    
                    if improvement > 0.15:  # 15% improvement threshold
                        time_str = f"{best_hour}:00" if best_hour < 12 else f"{best_hour-12}:00 PM" if best_hour > 12 else "12:00 PM"
                        
                        recommendation = OptimizationRecommendation(
                            recommendation_id=f"timing_hour_{user_id}_{int(datetime.utcnow().timestamp())}",
                            optimization_type=OptimizationType.TIMING_OPTIMIZATION,
                            title=f"Submit applications at {time_str}",
                            description=f"Applications submitted at {time_str} show {improvement*100:.1f}% better performance",
                            current_value=f"{current_hour}:00",
                            recommended_value=time_str,
                            expected_improvement=improvement * 100,
                            confidence=min(0.8, len(hour_performance[best_hour]) / 10),
                            implementation_effort="low",
                            risk_level="low",
                            supporting_evidence=[
                                f"Best time ({time_str}): {best_score:.2f} avg success",
                                f"Current time: {current_score:.2f} avg success",
                                f"Based on {len(hour_performance[best_hour])} applications"
                            ],
                            created_at=datetime.utcnow()
                        )
                        recommendations.append(recommendation)
        
        return recommendations
    
    async def _generate_content_recommendations(
        self,
        user_id: str,
        applications: List[Dict[str, Any]],
        strategy: OptimizationStrategy
    ) -> List[OptimizationRecommendation]:
        """Generate content optimization recommendations"""
        
        recommendations = []
        
        # Analyze content patterns using pattern recognition results
        from ..analytics.pattern_recognition import global_pattern_engine
        
        patterns = await global_pattern_engine.discover_patterns(user_id, time_window_days=180, min_applications=10)
        content_patterns = patterns.get('content', [])
        
        if content_patterns:
            # Find highest impact content patterns
            high_impact_patterns = [p for p in content_patterns if p.success_rate > 0.4 and p.sample_size >= 3]
            
            if high_impact_patterns:
                best_pattern = max(high_impact_patterns, key=lambda x: x.success_rate)
                
                recommendation = OptimizationRecommendation(
                    recommendation_id=f"content_{user_id}_{int(datetime.utcnow().timestamp())}",
                    optimization_type=OptimizationType.CONTENT_PERSONALIZATION,
                    title=f"Emphasize {best_pattern.conditions.get('content_theme', 'key themes')}",
                    description=best_pattern.description,
                    current_value="generic_content",
                    recommended_value=best_pattern.conditions.get('content_theme', 'optimized_content'),
                    expected_improvement=(best_pattern.success_rate - 0.3) * 100,  # Compared to baseline
                    confidence=best_pattern.confidence,
                    implementation_effort="medium",
                    risk_level="low",
                    supporting_evidence=[
                        f"Success rate: {best_pattern.success_rate*100:.1f}%",
                        f"Sample size: {best_pattern.sample_size} applications",
                        f"Pattern strength: {best_pattern.strength.value}"
                    ],
                    created_at=datetime.utcnow()
                )
                recommendations.append(recommendation)
        
        return recommendations
    
    async def _generate_platform_recommendations(
        self,
        user_id: str,
        applications: List[Dict[str, Any]],
        strategy: OptimizationStrategy
    ) -> List[OptimizationRecommendation]:
        """Generate platform allocation recommendations"""
        
        recommendations = []
        
        # Analyze platform performance
        platform_performance = defaultdict(list)
        
        for app in applications:
            # Extract platform from events
            events = app.get('events', [])
            platform = 'unknown'
            
            for event in events:
                if event.get('event_type') == 'application_submitted':
                    platform = event.get('metadata', {}).get('submission_method', 'unknown')
                    break
            
            success_score = self._calculate_success_score(app)
            platform_performance[platform].append(success_score)
        
        # Find best platform
        platform_averages = {}
        for platform, scores in platform_performance.items():
            if len(scores) >= 5:  # Minimum sample size
                platform_averages[platform] = np.mean(scores)
        
        if len(platform_averages) >= 2:
            best_platform = max(platform_averages.keys(), key=lambda x: platform_averages[x])
            current_distribution = {platform: len(scores) for platform, scores in platform_performance.items()}
            total_apps = sum(current_distribution.values())
            
            # Check if best platform is underutilized
            best_platform_usage = current_distribution.get(best_platform, 0) / total_apps
            
            if best_platform_usage < 0.4:  # Less than 40% usage
                improvement = platform_averages[best_platform] - np.mean(list(platform_averages.values()))
                
                if improvement > 0.1:  # 10% better than average
                    recommendation = OptimizationRecommendation(
                        recommendation_id=f"platform_{user_id}_{int(datetime.utcnow().timestamp())}",
                        optimization_type=OptimizationType.PLATFORM_ALLOCATION,
                        title=f"Increase usage of {best_platform}",
                        description=f"Allocate more applications to {best_platform} which shows {improvement*100:.1f}% better performance",
                        current_value=f"{best_platform_usage*100:.1f}%",
                        recommended_value="60%",
                        expected_improvement=improvement * 100,
                        confidence=min(0.8, len(platform_performance[best_platform]) / 20),
                        implementation_effort="medium",
                        risk_level="medium",
                        supporting_evidence=[
                            f"{best_platform} success rate: {platform_averages[best_platform]:.2f}",
                            f"Current usage: {best_platform_usage*100:.1f}%",
                            f"Based on {len(platform_performance[best_platform])} applications"
                        ],
                        created_at=datetime.utcnow()
                    )
                    recommendations.append(recommendation)
        
        return recommendations
    
    def _calculate_success_score(self, application: Dict[str, Any]) -> float:
        """Calculate success score for an application (0-1)"""
        
        stage = application.get('current_stage', 'submitted')
        
        stage_scores = {
            'offer_accepted': 1.0,
            'offer_extended': 0.8,
            'final_interview': 0.6,
            'technical_interview': 0.5,
            'first_interview': 0.4,
            'screening': 0.3,
            'under_review': 0.2,
            'submitted': 0.1,
            'rejected': 0.0,
            'withdrawn': 0.0
        }
        
        return stage_scores.get(stage, 0.1)
    
    def _find_best_timing_windows(self, timing_data: Dict, min_samples: int = 3) -> List[Tuple[Any, float]]:
        """Find best performing timing windows"""
        
        timing_averages = []
        
        for timing, scores in timing_data.items():
            if len(scores) >= min_samples:
                avg_score = np.mean(scores)
                timing_averages.append((timing, avg_score))
        
        # Sort by average score
        timing_averages.sort(key=lambda x: x[1], reverse=True)
        
        return timing_averages


class OptimizationPlanGenerator:
    """Generates comprehensive optimization plans"""
    
    def __init__(self):
        self.recommender = OptimizationRecommender()
    
    async def generate_plan(
        self,
        user_id: str,
        strategy: OptimizationStrategy = OptimizationStrategy.BALANCED,
        max_recommendations: int = 10,
        timeline_days: int = 30
    ) -> OptimizationPlan:
        """Generate comprehensive optimization plan"""
        
        # Generate recommendations
        recommendations = await self.recommender.generate_recommendations(user_id, strategy)
        
        # Limit number of recommendations
        recommendations = recommendations[:max_recommendations]
        
        # Prioritize recommendations
        priority_order = self._prioritize_recommendations(recommendations, strategy)
        
        # Calculate total expected improvement
        total_improvement = self._calculate_total_improvement(recommendations)
        
        plan_id = f"plan_{user_id}_{int(datetime.utcnow().timestamp())}"
        
        plan = OptimizationPlan(
            plan_id=plan_id,
            name=f"{strategy.value.title()} Optimization Plan",
            strategy=strategy,
            recommendations=recommendations,
            priority_order=priority_order,
            total_expected_improvement=total_improvement,
            implementation_timeline_days=timeline_days,
            created_at=datetime.utcnow()
        )
        
        return plan
    
    def _prioritize_recommendations(
        self,
        recommendations: List[OptimizationRecommendation],
        strategy: OptimizationStrategy
    ) -> List[str]:
        """Prioritize recommendations based on strategy"""
        
        if strategy == OptimizationStrategy.CONSERVATIVE:
            # Prioritize low-risk, high-confidence recommendations
            sorted_recs = sorted(
                recommendations,
                key=lambda x: (
                    -self._risk_to_score(x.risk_level),
                    -x.confidence,
                    -x.expected_improvement
                )
            )
        elif strategy == OptimizationStrategy.AGGRESSIVE:
            # Prioritize high-impact recommendations
            sorted_recs = sorted(
                recommendations,
                key=lambda x: (
                    -x.expected_improvement,
                    -x.confidence,
                    -self._effort_to_score(x.implementation_effort)
                )
            )
        elif strategy == OptimizationStrategy.EXPERIMENTAL:
            # Prioritize novel/experimental recommendations
            sorted_recs = sorted(
                recommendations,
                key=lambda x: (
                    self._risk_to_score(x.risk_level),  # Higher risk first
                    -x.expected_improvement,
                    -x.confidence
                )
            )
        else:  # BALANCED
            # Balance impact, confidence, and risk
            sorted_recs = sorted(
                recommendations,
                key=lambda x: (
                    -(x.expected_improvement * x.confidence / max(self._risk_to_score(x.risk_level), 1)),
                    -x.expected_improvement,
                    -x.confidence
                )
            )
        
        return [rec.recommendation_id for rec in sorted_recs]
    
    def _calculate_total_improvement(self, recommendations: List[OptimizationRecommendation]) -> float:
        """Calculate total expected improvement (not simply additive)"""
        
        if not recommendations:
            return 0.0
        
        # Use compound improvement formula (assumes some overlap)
        total = 0.0
        for rec in recommendations:
            # Weight by confidence and reduce for interaction effects
            weighted_improvement = rec.expected_improvement * rec.confidence * 0.7
            total += weighted_improvement
        
        # Cap at reasonable maximum
        return min(total, 100.0)
    
    def _risk_to_score(self, risk_level: str) -> int:
        """Convert risk level to numeric score"""
        return {'low': 1, 'medium': 2, 'high': 3}.get(risk_level, 2)
    
    def _effort_to_score(self, effort_level: str) -> int:
        """Convert effort level to numeric score"""
        return {'low': 1, 'medium': 2, 'high': 3}.get(effort_level, 2)


class OptimizationEngine:
    """Main optimization engine"""
    
    def __init__(self):
        self.plan_generator = OptimizationPlanGenerator()
        self.active_plans: Dict[str, OptimizationPlan] = {}
        self.optimization_history: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        
        # Start background optimization monitoring
        asyncio.create_task(self._monitor_optimizations())
    
    async def create_optimization_plan(
        self,
        user_id: str,
        strategy: OptimizationStrategy = OptimizationStrategy.BALANCED,
        auto_implement: bool = False
    ) -> OptimizationPlan:
        """Create a new optimization plan for user"""
        
        plan = await self.plan_generator.generate_plan(user_id, strategy)
        self.active_plans[plan.plan_id] = plan
        
        logger.info(f"Created optimization plan {plan.plan_id} for user {user_id}")
        
        if auto_implement:
            await self._implement_plan(plan.plan_id, user_id)
        
        return plan
    
    async def implement_recommendation(
        self,
        recommendation_id: str,
        user_id: str
    ) -> bool:
        """Implement a specific recommendation"""
        
        # Find the recommendation
        recommendation = None
        for plan in self.active_plans.values():
            for rec in plan.recommendations:
                if rec.recommendation_id == recommendation_id:
                    recommendation = rec
                    break
        
        if not recommendation:
            return False
        
        try:
            success = await self._apply_recommendation(recommendation, user_id)
            
            # Record implementation
            self.optimization_history[user_id].append({
                'recommendation_id': recommendation_id,
                'optimization_type': recommendation.optimization_type.value,
                'implemented_at': datetime.utcnow().isoformat(),
                'success': success,
                'expected_improvement': recommendation.expected_improvement
            })
            
            return success
            
        except Exception as e:
            logger.error(f"Error implementing recommendation {recommendation_id}: {str(e)}")
            return False
    
    async def _apply_recommendation(
        self,
        recommendation: OptimizationRecommendation,
        user_id: str
    ) -> bool:
        """Apply a specific recommendation"""
        
        opt_type = recommendation.optimization_type
        
        if opt_type == OptimizationType.TEMPLATE_SELECTION:
            # Update user's default template preference
            await self._update_template_preference(user_id, recommendation.recommended_value)
            return True
        
        elif opt_type == OptimizationType.TIMING_OPTIMIZATION:
            # Update timing preferences
            await self._update_timing_preference(user_id, recommendation.recommended_value)
            return True
        
        elif opt_type == OptimizationType.CONTENT_PERSONALIZATION:
            # Update content preferences
            await self._update_content_preferences(user_id, recommendation.recommended_value)
            return True
        
        elif opt_type == OptimizationType.PLATFORM_ALLOCATION:
            # Update platform allocation
            await self._update_platform_allocation(user_id, recommendation.recommended_value)
            return True
        
        else:
            logger.warning(f"Unimplemented optimization type: {opt_type}")
            return False
    
    async def _update_template_preference(self, user_id: str, template_type: str):
        """Update user's template preference"""
        # This would integrate with the template system
        from ..intelligence.user_profiles import global_profile_engine
        
        profile = global_profile_engine.get_user_profile(user_id)
        if profile:
            if 'preferences' not in profile.metadata:
                profile.metadata['preferences'] = {}
            profile.metadata['preferences']['default_template'] = template_type
            logger.info(f"Updated template preference for {user_id}: {template_type}")
    
    async def _update_timing_preference(self, user_id: str, timing_config: str):
        """Update user's timing preference"""
        from ..intelligence.user_profiles import global_profile_engine
        
        profile = global_profile_engine.get_user_profile(user_id)
        if profile:
            if 'preferences' not in profile.metadata:
                profile.metadata['preferences'] = {}
            profile.metadata['preferences']['optimal_timing'] = timing_config
            logger.info(f"Updated timing preference for {user_id}: {timing_config}")
    
    async def _update_content_preferences(self, user_id: str, content_theme: str):
        """Update user's content preferences"""
        from ..intelligence.user_profiles import global_profile_engine
        
        profile = global_profile_engine.get_user_profile(user_id)
        if profile:
            if 'preferences' not in profile.metadata:
                profile.metadata['preferences'] = {}
            profile.metadata['preferences']['content_emphasis'] = content_theme
            logger.info(f"Updated content preference for {user_id}: {content_theme}")
    
    async def _update_platform_allocation(self, user_id: str, allocation_strategy: str):
        """Update user's platform allocation strategy"""
        from ..intelligence.user_profiles import global_profile_engine
        
        profile = global_profile_engine.get_user_profile(user_id)
        if profile:
            if 'preferences' not in profile.metadata:
                profile.metadata['preferences'] = {}
            profile.metadata['preferences']['platform_allocation'] = allocation_strategy
            logger.info(f"Updated platform allocation for {user_id}: {allocation_strategy}")
    
    async def _implement_plan(self, plan_id: str, user_id: str):
        """Implement an entire optimization plan"""
        
        if plan_id not in self.active_plans:
            return
        
        plan = self.active_plans[plan_id]
        
        # Implement recommendations in priority order
        for rec_id in plan.priority_order[:5]:  # Limit to top 5 for safety
            recommendation = next((r for r in plan.recommendations if r.recommendation_id == rec_id), None)
            
            if recommendation and recommendation.implementation_effort == "low":
                # Only auto-implement low-effort recommendations
                await self.implement_recommendation(rec_id, user_id)
                await asyncio.sleep(1)  # Brief delay between implementations
    
    def get_optimization_status(self, user_id: str) -> Dict[str, Any]:
        """Get optimization status for user"""
        
        user_plans = [plan for plan in self.active_plans.values() if user_id in plan.plan_id]
        history = self.optimization_history.get(user_id, [])
        
        implemented_count = len([h for h in history if h['success']])
        total_expected_improvement = sum([h['expected_improvement'] for h in history if h['success']])
        
        return {
            'active_plans': len(user_plans),
            'total_recommendations': sum(len(plan.recommendations) for plan in user_plans),
            'implemented_optimizations': implemented_count,
            'total_expected_improvement': total_expected_improvement,
            'last_optimization': max([datetime.fromisoformat(h['implemented_at']) for h in history]).isoformat() if history else None,
            'optimization_types': list(set([h['optimization_type'] for h in history]))
        }
    
    async def _monitor_optimizations(self):
        """Background task to monitor optimization effectiveness"""
        
        while True:
            try:
                await self._evaluate_optimization_effectiveness()
                await asyncio.sleep(86400)  # Check daily
                
            except Exception as e:
                logger.error(f"Error in optimization monitoring: {str(e)}")
                await asyncio.sleep(3600)  # Retry in 1 hour
    
    async def _evaluate_optimization_effectiveness(self):
        """Evaluate how well optimizations are performing"""
        
        for user_id, history in self.optimization_history.items():
            if len(history) >= 3:  # Need some history
                # Get recent applications to measure improvement
                from ..pipeline.status_tracking import global_application_tracker
                recent_apps = global_application_tracker.get_user_applications(user_id)
                
                # Calculate recent performance
                cutoff_date = datetime.utcnow() - timedelta(days=30)
                recent_apps = [
                    app for app in recent_apps
                    if datetime.fromisoformat(app.get('submitted_date', '').replace('Z', '+00:00')) >= cutoff_date
                ]
                
                if recent_apps:
                    avg_success = np.mean([
                        self.plan_generator.recommender._calculate_success_score(app) 
                        for app in recent_apps
                    ])
                    
                    logger.info(f"User {user_id} recent performance: {avg_success:.2f} "
                              f"({len(history)} optimizations applied)")


# Global optimization engine
global_optimization_engine = OptimizationEngine()