"""
Analytics Engine for Growth Engine

Provides comprehensive analytics and insights including user behavior analysis,
opportunity trends, performance metrics, and market intelligence.
"""

import json
from typing import Dict, List, Optional, Tuple, Any, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from collections import defaultdict, Counter
from pathlib import Path
import math
from enum import Enum

import numpy as np
from pydantic import BaseModel, Field

from .user_profiles import global_profile_engine, InteractionType, UserProfile
from .data_enrichment import global_enrichment_service


class MetricType(Enum):
    """Types of metrics tracked"""
    USER_ENGAGEMENT = "user_engagement"
    OPPORTUNITY_PERFORMANCE = "opportunity_performance"
    SEARCH_ANALYTICS = "search_analytics"
    CONVERSION_METRICS = "conversion_metrics"
    MARKET_TRENDS = "market_trends"
    SYSTEM_PERFORMANCE = "system_performance"


class MetricPeriod(Enum):
    """Time periods for metric aggregation"""
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class FunnelStage(Enum):
    """Stages in the opportunity funnel"""
    DISCOVERED = "discovered"
    SCORED = "scored"
    APPLIED = "applied"
    RESPONDED = "responded"
    INTERVIEWED = "interviewed"
    ACCEPTED = "accepted"


@dataclass
class AnalyticsMetric:
    """Individual analytics metric"""
    metric_type: MetricType
    name: str
    value: float
    unit: str
    timestamp: datetime
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'metric_type': self.metric_type.value,
            'name': self.name,
            'value': self.value,
            'unit': self.unit,
            'timestamp': self.timestamp.isoformat(),
            'metadata': self.metadata
        }


@dataclass
class AnalyticsReport:
    """Comprehensive analytics report"""
    report_type: str
    time_period: str
    metrics: List[AnalyticsMetric]
    insights: List[str]
    recommendations: List[str]
    generated_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'report_type': self.report_type,
            'time_period': self.time_period,
            'metrics': [m.to_dict() for m in self.metrics],
            'insights': self.insights,
            'recommendations': self.recommendations,
            'generated_at': self.generated_at.isoformat(),
            'total_metrics': len(self.metrics)
        }


class UserEngagementAnalyzer:
    """Analyzes user engagement patterns and behaviors"""
    
    def __init__(self):
        self.engagement_thresholds = {
            'high': 50,      # interactions per week
            'medium': 20,    # interactions per week
            'low': 5         # interactions per week
        }
    
    def analyze_user_engagement(
        self, 
        time_window_days: int = 30
    ) -> Dict[str, Any]:
        """Analyze overall user engagement metrics"""
        
        cutoff_date = datetime.utcnow() - timedelta(days=time_window_days)
        all_profiles = global_profile_engine.profiles
        
        if not all_profiles:
            return {
                'total_users': 0,
                'active_users': 0,
                'engagement_distribution': {},
                'average_interactions_per_user': 0.0
            }
        
        # Analyze user activity
        user_stats = {}
        total_interactions = 0
        active_users = 0
        
        for user_id, profile in all_profiles.items():
            recent_interactions = [
                i for i in profile.interaction_history
                if i.timestamp > cutoff_date
            ]
            
            interaction_count = len(recent_interactions)
            total_interactions += interaction_count
            
            if interaction_count > 0:
                active_users += 1
            
            # Categorize engagement level
            weekly_interactions = (interaction_count * 7) / time_window_days
            
            if weekly_interactions >= self.engagement_thresholds['high']:
                engagement_level = 'high'
            elif weekly_interactions >= self.engagement_thresholds['medium']:
                engagement_level = 'medium'
            elif weekly_interactions >= self.engagement_thresholds['low']:
                engagement_level = 'low'
            else:
                engagement_level = 'inactive'
            
            user_stats[user_id] = {
                'total_interactions': interaction_count,
                'weekly_interactions': weekly_interactions,
                'engagement_level': engagement_level,
                'last_activity': max([i.timestamp for i in recent_interactions]) if recent_interactions else None
            }
        
        # Calculate engagement distribution
        engagement_distribution = Counter(
            stats['engagement_level'] for stats in user_stats.values()
        )
        
        # Calculate averages
        avg_interactions = total_interactions / len(all_profiles) if all_profiles else 0
        
        return {
            'total_users': len(all_profiles),
            'active_users': active_users,
            'inactive_users': len(all_profiles) - active_users,
            'engagement_distribution': dict(engagement_distribution),
            'average_interactions_per_user': avg_interactions,
            'total_interactions': total_interactions,
            'user_retention_rate': (active_users / len(all_profiles)) * 100 if all_profiles else 0,
            'time_window_days': time_window_days
        }
    
    def analyze_interaction_patterns(
        self, 
        time_window_days: int = 30
    ) -> Dict[str, Any]:
        """Analyze user interaction patterns and types"""
        
        cutoff_date = datetime.utcnow() - timedelta(days=time_window_days)
        all_profiles = global_profile_engine.profiles
        
        # Collect all recent interactions
        all_interactions = []
        for profile in all_profiles.values():
            recent_interactions = [
                i for i in profile.interaction_history
                if i.timestamp > cutoff_date
            ]
            all_interactions.extend(recent_interactions)
        
        if not all_interactions:
            return {
                'total_interactions': 0,
                'interaction_type_distribution': {},
                'daily_activity_pattern': {},
                'hourly_activity_pattern': {}
            }
        
        # Analyze interaction types
        interaction_types = Counter(i.interaction_type.value for i in all_interactions)
        
        # Analyze daily patterns
        daily_activity = defaultdict(int)
        for interaction in all_interactions:
            day_name = interaction.timestamp.strftime('%A')
            daily_activity[day_name] += 1
        
        # Analyze hourly patterns
        hourly_activity = defaultdict(int)
        for interaction in all_interactions:
            hour = interaction.timestamp.hour
            hourly_activity[hour] += 1
        
        return {
            'total_interactions': len(all_interactions),
            'interaction_type_distribution': dict(interaction_types),
            'daily_activity_pattern': dict(daily_activity),
            'hourly_activity_pattern': dict(hourly_activity),
            'most_active_day': max(daily_activity.items(), key=lambda x: x[1])[0] if daily_activity else None,
            'peak_hour': max(hourly_activity.items(), key=lambda x: x[1])[0] if hourly_activity else None,
            'time_window_days': time_window_days
        }
    
    def calculate_user_cohort_retention(
        self, 
        cohort_period_days: int = 7
    ) -> Dict[str, Any]:
        """Calculate user retention by cohorts"""
        
        all_profiles = global_profile_engine.profiles
        
        if not all_profiles:
            return {'cohorts': {}, 'overall_retention': 0.0}
        
        # Group users by creation week
        cohorts = defaultdict(list)
        for profile in all_profiles.values():
            # Week of user creation
            week_start = profile.created_at - timedelta(days=profile.created_at.weekday())
            week_key = week_start.strftime('%Y-W%U')
            cohorts[week_key].append(profile)
        
        # Calculate retention for each cohort
        cohort_retention = {}
        
        for week_key, profiles in cohorts.items():
            cohort_size = len(profiles)
            if cohort_size == 0:
                continue
            
            # Calculate retention at different periods
            retention_periods = [7, 14, 30, 90]  # days
            retention_data = {'cohort_size': cohort_size}
            
            for period_days in retention_periods:
                retained_users = 0
                cutoff_date = datetime.utcnow() - timedelta(days=period_days)
                
                for profile in profiles:
                    # Check if user was active in the retention period
                    if profile.created_at < cutoff_date:
                        recent_activity = any(
                            i.timestamp > cutoff_date
                            for i in profile.interaction_history
                        )
                        if recent_activity:
                            retained_users += 1
                
                retention_rate = (retained_users / cohort_size) * 100
                retention_data[f'retention_{period_days}d'] = retention_rate
            
            cohort_retention[week_key] = retention_data
        
        # Calculate overall retention rates
        if cohort_retention:
            overall_retention = {}
            for period in ['retention_7d', 'retention_14d', 'retention_30d', 'retention_90d']:
                period_rates = [data.get(period, 0) for data in cohort_retention.values() if period in data]
                overall_retention[period] = sum(period_rates) / len(period_rates) if period_rates else 0.0
        else:
            overall_retention = {}
        
        return {
            'cohorts': cohort_retention,
            'overall_retention': overall_retention,
            'total_cohorts': len(cohort_retention)
        }


class OpportunityAnalyzer:
    """Analyzes opportunity performance and trends"""
    
    def analyze_opportunity_performance(
        self, 
        opportunities: List[Dict[str, Any]], 
        time_window_days: int = 30
    ) -> Dict[str, Any]:
        """Analyze how opportunities are performing"""
        
        cutoff_date = datetime.utcnow() - timedelta(days=time_window_days)
        all_profiles = global_profile_engine.profiles
        
        # Collect interactions for each opportunity
        opp_interactions = defaultdict(list)
        
        for profile in all_profiles.values():
            for interaction in profile.interaction_history:
                if interaction.timestamp > cutoff_date:
                    opp_interactions[interaction.opportunity_id].append(interaction)
        
        # Analyze each opportunity
        opp_performance = {}
        
        for opp in opportunities:
            opp_id = opp.get('id', '')
            interactions = opp_interactions.get(opp_id, [])
            
            if not interactions:
                continue
            
            # Calculate performance metrics
            total_interactions = len(interactions)
            unique_users = len(set(i.user_id for i in interactions))
            
            interaction_breakdown = Counter(i.interaction_type.value for i in interactions)
            
            # Calculate conversion metrics
            views = interaction_breakdown.get('view', 0)
            applies = interaction_breakdown.get('apply', 0)
            saves = interaction_breakdown.get('save', 0)
            dismissals = interaction_breakdown.get('dismiss', 0)
            
            # Conversion rates
            apply_rate = (applies / views) * 100 if views > 0 else 0
            save_rate = (saves / views) * 100 if views > 0 else 0
            dismissal_rate = (dismissals / views) * 100 if views > 0 else 0
            
            # Engagement score (weighted by interaction importance)
            engagement_score = (
                views * 1.0 +
                interaction_breakdown.get('click', 0) * 2.0 +
                saves * 5.0 +
                applies * 10.0 +
                dismissals * -2.0
            )
            
            opp_performance[opp_id] = {
                'opportunity_title': opp.get('title', 'Unknown'),
                'total_interactions': total_interactions,
                'unique_users': unique_users,
                'interaction_breakdown': dict(interaction_breakdown),
                'conversion_metrics': {
                    'apply_rate': apply_rate,
                    'save_rate': save_rate,
                    'dismissal_rate': dismissal_rate
                },
                'engagement_score': engagement_score,
                'performance_tier': (
                    'high' if engagement_score > 50 else
                    'medium' if engagement_score > 20 else
                    'low'
                )
            }
        
        # Sort opportunities by performance
        top_performers = sorted(
            opp_performance.items(),
            key=lambda x: x[1]['engagement_score'],
            reverse=True
        )[:10]
        
        return {
            'total_opportunities_analyzed': len(opp_performance),
            'top_performers': [
                {'opportunity_id': opp_id, **metrics}
                for opp_id, metrics in top_performers
            ],
            'performance_distribution': {
                'high': len([p for p in opp_performance.values() if p['performance_tier'] == 'high']),
                'medium': len([p for p in opp_performance.values() if p['performance_tier'] == 'medium']),
                'low': len([p for p in opp_performance.values() if p['performance_tier'] == 'low'])
            },
            'average_engagement_score': sum(p['engagement_score'] for p in opp_performance.values()) / len(opp_performance) if opp_performance else 0,
            'time_window_days': time_window_days
        }
    
    def analyze_market_trends(
        self, 
        opportunities: List[Dict[str, Any]], 
        time_window_days: int = 90
    ) -> Dict[str, Any]:
        """Analyze market trends from opportunity data"""
        
        # Opportunity type distribution
        opp_types = Counter(opp.get('type', 'unknown') for opp in opportunities)
        
        # Industry distribution
        industries = []
        for opp in opportunities:
            company_data = opp.get('company_data', {})
            industry = company_data.get('industry')
            if industry:
                industries.append(industry)
        
        industry_distribution = Counter(industries)
        
        # Location trends
        locations = []
        remote_count = 0
        
        for opp in opportunities:
            location_data = opp.get('location_data', {})
            if location_data.get('is_remote'):
                remote_count += 1
            else:
                country = location_data.get('country')
                if country:
                    locations.append(country)
        
        location_distribution = Counter(locations)
        remote_percentage = (remote_count / len(opportunities)) * 100 if opportunities else 0
        
        # Salary trends
        salaries = []
        for opp in opportunities:
            salary_data = opp.get('salary_data', {})
            if salary_data and salary_data.get('min_amount'):
                salaries.append(salary_data['min_amount'])
        
        salary_stats = {}
        if salaries:
            salaries.sort()
            salary_stats = {
                'median': salaries[len(salaries) // 2],
                'q25': salaries[len(salaries) // 4],
                'q75': salaries[(3 * len(salaries)) // 4],
                'min': min(salaries),
                'max': max(salaries),
                'average': sum(salaries) / len(salaries)
            }
        
        return {
            'opportunity_type_trends': dict(opp_types),
            'industry_trends': dict(industry_distribution.most_common(10)),
            'location_trends': {
                'top_countries': dict(location_distribution.most_common(10)),
                'remote_percentage': remote_percentage
            },
            'salary_trends': salary_stats,
            'total_opportunities_analyzed': len(opportunities),
            'time_window_days': time_window_days,
            'trending_insights': self._generate_trend_insights(
                opp_types, industry_distribution, location_distribution, remote_percentage
            )
        }
    
    def _generate_trend_insights(
        self, 
        opp_types: Counter, 
        industries: Counter, 
        locations: Counter, 
        remote_percentage: float
    ) -> List[str]:
        """Generate textual insights from trend data"""
        
        insights = []
        
        # Opportunity type insights
        if opp_types:
            top_type = opp_types.most_common(1)[0]
            insights.append(f"Most popular opportunity type: {top_type[0]} ({top_type[1]} opportunities)")
        
        # Industry insights
        if industries:
            top_industry = industries.most_common(1)[0]
            insights.append(f"Leading industry: {top_industry[0]} with {top_industry[1]} opportunities")
        
        # Remote work insights
        if remote_percentage > 50:
            insights.append(f"Remote work is dominant: {remote_percentage:.1f}% of opportunities are remote")
        elif remote_percentage > 25:
            insights.append(f"Hybrid work model emerging: {remote_percentage:.1f}% remote opportunities")
        else:
            insights.append(f"Traditional on-site work prevalent: Only {remote_percentage:.1f}% remote opportunities")
        
        # Location insights
        if locations:
            top_location = locations.most_common(1)[0]
            insights.append(f"Top location for opportunities: {top_location[0]} ({top_location[1]} opportunities)")
        
        return insights


class SearchAnalyzer:
    """Analyzes search patterns and query performance"""
    
    def analyze_search_patterns(
        self, 
        time_window_days: int = 30
    ) -> Dict[str, Any]:
        """Analyze user search behavior and patterns"""
        
        cutoff_date = datetime.utcnow() - timedelta(days=time_window_days)
        all_profiles = global_profile_engine.profiles
        
        # Collect search interactions
        search_interactions = []
        
        for profile in all_profiles.values():
            searches = [
                i for i in profile.interaction_history
                if (i.interaction_type == InteractionType.SEARCH and 
                    i.timestamp > cutoff_date)
            ]
            search_interactions.extend(searches)
        
        if not search_interactions:
            return {
                'total_searches': 0,
                'unique_searchers': 0,
                'search_patterns': {}
            }
        
        # Analyze search queries
        search_queries = []
        search_contexts = []
        
        for interaction in search_interactions:
            context = interaction.context
            if 'query' in context:
                search_queries.append(context['query'])
            search_contexts.append(context)
        
        # Most common search terms
        all_terms = []
        for query in search_queries:
            terms = query.lower().split()
            all_terms.extend(terms)
        
        common_terms = Counter(all_terms).most_common(20)
        
        # Search frequency analysis
        unique_searchers = len(set(i.user_id for i in search_interactions))
        searches_per_user = len(search_interactions) / unique_searchers if unique_searchers > 0 else 0
        
        # Daily search pattern
        daily_searches = defaultdict(int)
        for interaction in search_interactions:
            day = interaction.timestamp.strftime('%A')
            daily_searches[day] += 1
        
        return {
            'total_searches': len(search_interactions),
            'unique_searchers': unique_searchers,
            'average_searches_per_user': searches_per_user,
            'most_common_terms': dict(common_terms),
            'daily_search_pattern': dict(daily_searches),
            'search_volume_trend': 'stable',  # Would calculate actual trend from historical data
            'time_window_days': time_window_days
        }


class AnalyticsEngine:
    """Main analytics engine combining all analysis components"""
    
    def __init__(self):
        self.user_analyzer = UserEngagementAnalyzer()
        self.opportunity_analyzer = OpportunityAnalyzer()
        self.search_analyzer = SearchAnalyzer()
    
    def generate_comprehensive_report(
        self, 
        opportunities: List[Dict[str, Any]] = None,
        time_window_days: int = 30
    ) -> AnalyticsReport:
        """Generate comprehensive analytics report"""
        
        start_time = datetime.utcnow()
        
        # Collect all analytics
        metrics = []
        insights = []
        recommendations = []
        
        # User engagement analysis
        user_engagement = self.user_analyzer.analyze_user_engagement(time_window_days)
        interaction_patterns = self.user_analyzer.analyze_interaction_patterns(time_window_days)
        cohort_retention = self.user_analyzer.calculate_user_cohort_retention()
        
        # Add user metrics
        metrics.append(AnalyticsMetric(
            metric_type=MetricType.USER_ENGAGEMENT,
            name="Total Active Users",
            value=user_engagement['active_users'],
            unit="users",
            timestamp=start_time,
            metadata=user_engagement
        ))
        
        metrics.append(AnalyticsMetric(
            metric_type=MetricType.USER_ENGAGEMENT,
            name="User Retention Rate",
            value=user_engagement['user_retention_rate'],
            unit="percentage",
            timestamp=start_time,
            metadata=cohort_retention
        ))
        
        # Opportunity analysis (if opportunities provided)
        if opportunities:
            opp_performance = self.opportunity_analyzer.analyze_opportunity_performance(
                opportunities, time_window_days
            )
            market_trends = self.opportunity_analyzer.analyze_market_trends(
                opportunities, time_window_days
            )
            
            metrics.append(AnalyticsMetric(
                metric_type=MetricType.OPPORTUNITY_PERFORMANCE,
                name="Average Opportunity Engagement Score",
                value=opp_performance['average_engagement_score'],
                unit="score",
                timestamp=start_time,
                metadata=opp_performance
            ))
            
            # Add market trend insights
            insights.extend(market_trends['trending_insights'])
        
        # Search analysis
        search_patterns = self.search_analyzer.analyze_search_patterns(time_window_days)
        
        metrics.append(AnalyticsMetric(
            metric_type=MetricType.SEARCH_ANALYTICS,
            name="Total Searches",
            value=search_patterns['total_searches'],
            unit="searches",
            timestamp=start_time,
            metadata=search_patterns
        ))
        
        # Generate insights based on data
        insights.extend(self._generate_insights(user_engagement, interaction_patterns, search_patterns))
        
        # Generate recommendations
        recommendations.extend(self._generate_recommendations(user_engagement, search_patterns))
        
        return AnalyticsReport(
            report_type="comprehensive",
            time_period=f"{time_window_days} days",
            metrics=metrics,
            insights=insights,
            recommendations=recommendations,
            generated_at=start_time
        )
    
    def _generate_insights(
        self, 
        user_engagement: Dict[str, Any], 
        interaction_patterns: Dict[str, Any], 
        search_patterns: Dict[str, Any]
    ) -> List[str]:
        """Generate actionable insights from analytics data"""
        
        insights = []
        
        # User engagement insights
        retention_rate = user_engagement.get('user_retention_rate', 0)
        if retention_rate < 30:
            insights.append(f"Low user retention ({retention_rate:.1f}%) indicates need for improved onboarding")
        elif retention_rate > 70:
            insights.append(f"Strong user retention ({retention_rate:.1f}%) shows good product-market fit")
        
        # Interaction pattern insights
        if interaction_patterns.get('most_active_day'):
            most_active_day = interaction_patterns['most_active_day']
            insights.append(f"Peak user activity on {most_active_day} - optimize content releases")
        
        # Search insights
        if search_patterns['total_searches'] > 0:
            searches_per_user = search_patterns.get('average_searches_per_user', 0)
            if searches_per_user > 5:
                insights.append("High search activity suggests users are actively exploring opportunities")
            elif searches_per_user < 2:
                insights.append("Low search activity may indicate poor search discoverability")
        
        return insights
    
    def _generate_recommendations(
        self, 
        user_engagement: Dict[str, Any], 
        search_patterns: Dict[str, Any]
    ) -> List[str]:
        """Generate actionable recommendations"""
        
        recommendations = []
        
        # User engagement recommendations
        engagement_dist = user_engagement.get('engagement_distribution', {})
        inactive_users = engagement_dist.get('inactive', 0)
        
        if inactive_users > 0:
            recommendations.append(f"Re-engage {inactive_users} inactive users with personalized email campaigns")
        
        # Search recommendations
        if search_patterns['total_searches'] > 0:
            common_terms = search_patterns.get('most_common_terms', {})
            if common_terms:
                top_term = list(common_terms.keys())[0]
                recommendations.append(f"Optimize content for popular search term: '{top_term}'")
        
        # General recommendations
        recommendations.append("Implement A/B testing for recommendation algorithms")
        recommendations.append("Add more detailed user preference collection during onboarding")
        
        return recommendations
    
    def get_real_time_metrics(self) -> Dict[str, Any]:
        """Get real-time system metrics"""
        
        all_profiles = global_profile_engine.profiles
        
        # Current active users (active in last hour)
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)
        active_now = 0
        
        for profile in all_profiles.values():
            if profile.interaction_history:
                last_interaction = max(i.timestamp for i in profile.interaction_history)
                if last_interaction > one_hour_ago:
                    active_now += 1
        
        return {
            'active_users_now': active_now,
            'total_registered_users': len(all_profiles),
            'system_load': 'normal',  # Would calculate from actual system metrics
            'cache_hit_rate': 85.5,   # Would get from cache system
            'average_response_time_ms': 145,  # Would get from monitoring
            'timestamp': datetime.utcnow().isoformat()
        }


# Global analytics engine
global_analytics_engine = AnalyticsEngine()


@dataclass
class MetricPoint:
    """Single metric data point"""
    timestamp: datetime
    value: float
    metadata: dict = field(default_factory=dict)


class TimeSeriesMetric(BaseModel):
    """Time series of a metric"""
    name: str
    unit: str
    data_points: list[dict] = []  # List of {timestamp, value}
    aggregation: str = "sum"  # sum, avg, max, min, count
    
    def add_point(self, timestamp: datetime, value: float):
        self.data_points.append({
            "timestamp": timestamp.isoformat(),
            "value": value
        })
    
    def get_trend(self) -> float:
        """Calculate trend direction (-1 to 1)"""
        if len(self.data_points) < 2:
            return 0.0
        
        values = [p["value"] for p in self.data_points]
        x = np.arange(len(values))
        
        # Linear regression slope
        if np.std(x) == 0:
            return 0.0
        
        slope = np.corrcoef(x, values)[0, 1]
        return slope if not np.isnan(slope) else 0.0


class FunnelMetrics(BaseModel):
    """Funnel conversion metrics"""
    stage: str
    count: int
    conversion_rate: float = Field(ge=0, le=1)
    avg_time_in_stage_days: float = 0.0
    drop_off_reasons: dict[str, int] = {}


class CohortAnalysis(BaseModel):
    """Cohort-based analysis results"""
    cohort_name: str
    cohort_criteria: dict
    size: int
    metrics: dict[str, float]
    comparison_to_baseline: dict[str, float] = {}


class ROIMetrics(BaseModel):
    """Return on Investment calculations"""
    period_start: datetime
    period_end: datetime
    
    # Time investment
    total_hours_invested: float
    hours_per_application: float
    hours_in_interviews: float
    
    # Outcomes
    applications_submitted: int
    interviews_secured: int
    offers_received: int
    
    # Financial
    total_compensation_offered: float
    avg_compensation_per_offer: float
    compensation_per_hour_invested: float
    
    # Efficiency
    application_to_interview_rate: float
    interview_to_offer_rate: float
    overall_success_rate: float


class DashboardData(BaseModel):
    """Complete dashboard data structure"""
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    period: str
    
    # Summary metrics
    summary: dict[str, Any] = {}
    
    # Time series
    time_series: dict[str, TimeSeriesMetric] = {}
    
    # Funnel
    funnel: list[FunnelMetrics] = []
    
    # Cohorts
    cohorts: list[CohortAnalysis] = []
    
    # ROI
    roi: Optional[ROIMetrics] = None
    
    # Top performers
    top_opportunities: list[dict] = []
    top_organizations: list[dict] = []


class AnalyticsEngine:
    """
    Core analytics engine for tracking and analyzing performance.
    """
    
    def __init__(self, default_period_days: int = 30):
        self.default_period_days = default_period_days
        self._cache: dict[str, Any] = {}
        self._cache_ttl = timedelta(minutes=15)
        self._cache_timestamps: dict[str, datetime] = {}
    
    async def get_summary_metrics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> dict[str, Any]:
        """
        Get summary metrics for a period.
        
        Returns:
            Dictionary with key metrics
        """
        end_date = end_date or datetime.utcnow()
        start_date = start_date or (end_date - timedelta(days=self.default_period_days))
        
        async with get_db_session() as session:
            # Total opportunities discovered
            opp_count = await session.execute(
                select(func.count(OpportunityRecord.id)).where(
                    and_(
                        OpportunityRecord.discovered_at >= start_date,
                        OpportunityRecord.discovered_at <= end_date
                    )
                )
            )
            total_opportunities = opp_count.scalar() or 0
            
            # Applications submitted
            app_count = await session.execute(
                select(func.count(ApplicationDraft.id)).where(
                    and_(
                        ApplicationDraft.created_at >= start_date,
                        ApplicationDraft.created_at <= end_date,
                        ApplicationDraft.status == "submitted"
                    )
                )
            )
            applications_submitted = app_count.scalar() or 0
            
            # Outcomes
            outcome_counts = await session.execute(
                select(
                    OutcomeRecord.outcome,
                    func.count(OutcomeRecord.id)
                ).where(
                    and_(
                        OutcomeRecord.recorded_at >= start_date,
                        OutcomeRecord.recorded_at <= end_date
                    )
                ).group_by(OutcomeRecord.outcome)
            )
            outcomes = dict(outcome_counts.all())
            
            # Average fit score
            avg_score = await session.execute(
                select(func.avg(OpportunityRecord.fit_score)).where(
                    and_(
                        OpportunityRecord.discovered_at >= start_date,
                        OpportunityRecord.discovered_at <= end_date,
                        OpportunityRecord.fit_score.isnot(None)
                    )
                )
            )
            average_fit_score = avg_score.scalar() or 0.0
            
            # Response rate
            total_outcomes = sum(outcomes.values()) if outcomes else 0
            no_response = outcomes.get("no_response", 0)
            response_rate = 1 - (no_response / total_outcomes) if total_outcomes > 0 else 0
            
            # Acceptance rate
            accepted = outcomes.get("accepted", 0)
            acceptance_rate = accepted / total_outcomes if total_outcomes > 0 else 0
        
        return {
            "period_start": start_date.isoformat(),
            "period_end": end_date.isoformat(),
            "total_opportunities_discovered": total_opportunities,
            "applications_submitted": applications_submitted,
            "outcomes_tracked": total_outcomes,
            "outcomes_by_type": outcomes,
            "average_fit_score": round(average_fit_score, 3),
            "response_rate": round(response_rate, 3),
            "acceptance_rate": round(acceptance_rate, 3),
            "interviews": outcomes.get("interview", 0),
            "accepted": accepted,
            "rejected": outcomes.get("rejected", 0)
        }
    
    async def get_time_series(
        self,
        metric_name: str,
        period: MetricPeriod = MetricPeriod.DAILY,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> TimeSeriesMetric:
        """
        Get time series data for a specific metric.
        
        Args:
            metric_name: Name of metric (applications, opportunities, outcomes, etc.)
            period: Aggregation period
            start_date: Start of time range
            end_date: End of time range
        
        Returns:
            TimeSeriesMetric with data points
        """
        end_date = end_date or datetime.utcnow()
        start_date = start_date or (end_date - timedelta(days=90))
        
        metric = TimeSeriesMetric(
            name=metric_name,
            unit="count",
            aggregation="sum"
        )
        
        # Determine date truncation based on period
        if period == MetricPeriod.DAILY:
            interval_days = 1
        elif period == MetricPeriod.WEEKLY:
            interval_days = 7
        elif period == MetricPeriod.MONTHLY:
            interval_days = 30
        else:
            interval_days = 90
        
        async with get_db_session() as session:
            current = start_date
            
            while current <= end_date:
                next_period = current + timedelta(days=interval_days)
                
                if metric_name == "applications":
                    result = await session.execute(
                        select(func.count(ApplicationDraft.id)).where(
                            and_(
                                ApplicationDraft.created_at >= current,
                                ApplicationDraft.created_at < next_period
                            )
                        )
                    )
                elif metric_name == "opportunities":
                    result = await session.execute(
                        select(func.count(OpportunityRecord.id)).where(
                            and_(
                                OpportunityRecord.discovered_at >= current,
                                OpportunityRecord.discovered_at < next_period
                            )
                        )
                    )
                elif metric_name == "outcomes":
                    result = await session.execute(
                        select(func.count(OutcomeRecord.id)).where(
                            and_(
                                OutcomeRecord.recorded_at >= current,
                                OutcomeRecord.recorded_at < next_period
                            )
                        )
                    )
                elif metric_name == "success_rate":
                    # Calculate success rate for period
                    total = await session.execute(
                        select(func.count(OutcomeRecord.id)).where(
                            and_(
                                OutcomeRecord.recorded_at >= current,
                                OutcomeRecord.recorded_at < next_period
                            )
                        )
                    )
                    successful = await session.execute(
                        select(func.count(OutcomeRecord.id)).where(
                            and_(
                                OutcomeRecord.recorded_at >= current,
                                OutcomeRecord.recorded_at < next_period,
                                OutcomeRecord.outcome.in_(["accepted", "interview"])
                            )
                        )
                    )
                    total_count = total.scalar() or 0
                    success_count = successful.scalar() or 0
                    value = success_count / total_count if total_count > 0 else 0
                    metric.add_point(current, value)
                    current = next_period
                    continue
                else:
                    result = await session.execute(
                        select(func.count(OpportunityRecord.id)).where(
                            and_(
                                OpportunityRecord.discovered_at >= current,
                                OpportunityRecord.discovered_at < next_period
                            )
                        )
                    )
                
                value = result.scalar() or 0
                metric.add_point(current, value)
                current = next_period
        
        return metric
    
    async def get_funnel_metrics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> list[FunnelMetrics]:
        """
        Calculate funnel conversion metrics.
        
        Returns:
            List of FunnelMetrics for each stage
        """
        end_date = end_date or datetime.utcnow()
        start_date = start_date or (end_date - timedelta(days=self.default_period_days))
        
        funnel = []
        
        async with get_db_session() as session:
            # Stage 1: Discovered
            discovered = await session.execute(
                select(func.count(OpportunityRecord.id)).where(
                    and_(
                        OpportunityRecord.discovered_at >= start_date,
                        OpportunityRecord.discovered_at <= end_date
                    )
                )
            )
            discovered_count = discovered.scalar() or 0
            
            # Stage 2: Scored (has fit_score)
            scored = await session.execute(
                select(func.count(OpportunityRecord.id)).where(
                    and_(
                        OpportunityRecord.discovered_at >= start_date,
                        OpportunityRecord.discovered_at <= end_date,
                        OpportunityRecord.fit_score.isnot(None)
                    )
                )
            )
            scored_count = scored.scalar() or 0
            
            # Stage 3: Applied
            applied = await session.execute(
                select(func.count(ApplicationDraft.id)).where(
                    and_(
                        ApplicationDraft.created_at >= start_date,
                        ApplicationDraft.created_at <= end_date,
                        ApplicationDraft.status == "submitted"
                    )
                )
            )
            applied_count = applied.scalar() or 0
            
            # Stage 4: Responded (has outcome)
            responded = await session.execute(
                select(func.count(OutcomeRecord.id)).where(
                    and_(
                        OutcomeRecord.recorded_at >= start_date,
                        OutcomeRecord.recorded_at <= end_date,
                        OutcomeRecord.outcome != "no_response"
                    )
                )
            )
            responded_count = responded.scalar() or 0
            
            # Stage 5: Interviewed
            interviewed = await session.execute(
                select(func.count(OutcomeRecord.id)).where(
                    and_(
                        OutcomeRecord.recorded_at >= start_date,
                        OutcomeRecord.recorded_at <= end_date,
                        OutcomeRecord.outcome.in_(["interview", "accepted"])
                    )
                )
            )
            interviewed_count = interviewed.scalar() or 0
            
            # Stage 6: Accepted
            accepted = await session.execute(
                select(func.count(OutcomeRecord.id)).where(
                    and_(
                        OutcomeRecord.recorded_at >= start_date,
                        OutcomeRecord.recorded_at <= end_date,
                        OutcomeRecord.outcome == "accepted"
                    )
                )
            )
            accepted_count = accepted.scalar() or 0
        
        # Build funnel stages
        stages = [
            (FunnelStage.DISCOVERED, discovered_count),
            (FunnelStage.SCORED, scored_count),
            (FunnelStage.APPLIED, applied_count),
            (FunnelStage.RESPONDED, responded_count),
            (FunnelStage.INTERVIEWED, interviewed_count),
            (FunnelStage.ACCEPTED, accepted_count),
        ]
        
        for i, (stage, count) in enumerate(stages):
            prev_count = stages[i-1][1] if i > 0 else count
            conversion = count / prev_count if prev_count > 0 else 0
            
            funnel.append(FunnelMetrics(
                stage=stage.value,
                count=count,
                conversion_rate=round(conversion, 3)
            ))
        
        return funnel
    
    async def get_cohort_analysis(
        self,
        cohort_by: str = "opportunity_type",
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> list[CohortAnalysis]:
        """
        Perform cohort analysis.
        
        Args:
            cohort_by: Field to cohort by (opportunity_type, organization, etc.)
            start_date: Start of analysis period
            end_date: End of analysis period
        
        Returns:
            List of CohortAnalysis results
        """
        end_date = end_date or datetime.utcnow()
        start_date = start_date or (end_date - timedelta(days=90))
        
        cohorts = []
        
        async with get_db_session() as session:
            # Get unique cohort values
            if cohort_by == "opportunity_type":
                cohort_field = OpportunityRecord.opportunity_type
            elif cohort_by == "organization":
                cohort_field = OpportunityRecord.organization
            else:
                cohort_field = OpportunityRecord.opportunity_type
            
            # Get all opportunities with outcomes
            result = await session.execute(
                select(
                    cohort_field,
                    func.count(OpportunityRecord.id).label("total"),
                    func.avg(OpportunityRecord.fit_score).label("avg_score"),
                ).where(
                    and_(
                        OpportunityRecord.discovered_at >= start_date,
                        OpportunityRecord.discovered_at <= end_date
                    )
                ).group_by(cohort_field)
            )
            
            rows = result.all()
            
            # Calculate baseline metrics
            total_all = sum(r.total for r in rows)
            avg_score_all = np.mean([r.avg_score for r in rows if r.avg_score]) if rows else 0
            
            for row in rows:
                if row.total < 3:  # Skip small cohorts
                    continue
                
                cohorts.append(CohortAnalysis(
                    cohort_name=str(row[0]) if row[0] else "unknown",
                    cohort_criteria={cohort_by: row[0]},
                    size=row.total,
                    metrics={
                        "average_fit_score": round(row.avg_score or 0, 3),
                        "percentage_of_total": round(row.total / total_all, 3) if total_all > 0 else 0
                    },
                    comparison_to_baseline={
                        "fit_score_diff": round((row.avg_score or 0) - avg_score_all, 3)
                    }
                ))
        
        return sorted(cohorts, key=lambda c: c.size, reverse=True)
    
    async def calculate_roi(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        hours_per_application: float = 2.0,
        hours_per_interview: float = 3.0
    ) -> ROIMetrics:
        """
        Calculate ROI metrics for time invested.
        
        Args:
            start_date: Start of period
            end_date: End of period
            hours_per_application: Estimated hours per application
            hours_per_interview: Estimated hours per interview
        
        Returns:
            ROIMetrics with calculated values
        """
        end_date = end_date or datetime.utcnow()
        start_date = start_date or (end_date - timedelta(days=self.default_period_days))
        
        async with get_db_session() as session:
            # Get application count
            app_count = await session.execute(
                select(func.count(ApplicationDraft.id)).where(
                    and_(
                        ApplicationDraft.created_at >= start_date,
                        ApplicationDraft.created_at <= end_date,
                        ApplicationDraft.status == "submitted"
                    )
                )
            )
            applications = app_count.scalar() or 0
            
            # Get interview count
            interview_count = await session.execute(
                select(func.count(OutcomeRecord.id)).where(
                    and_(
                        OutcomeRecord.recorded_at >= start_date,
                        OutcomeRecord.recorded_at <= end_date,
                        OutcomeRecord.outcome.in_(["interview", "accepted"])
                    )
                )
            )
            interviews = interview_count.scalar() or 0
            
            # Get total interview rounds
            interview_rounds = await session.execute(
                select(func.sum(OutcomeRecord.interview_rounds)).where(
                    and_(
                        OutcomeRecord.recorded_at >= start_date,
                        OutcomeRecord.recorded_at <= end_date,
                        OutcomeRecord.interview_rounds.isnot(None)
                    )
                )
            )
            total_rounds = interview_rounds.scalar() or 0
            
            # Get offers and compensation
            offers = await session.execute(
                select(
                    func.count(OutcomeRecord.id),
                    func.sum(OutcomeRecord.compensation_offered),
                    func.avg(OutcomeRecord.compensation_offered)
                ).where(
                    and_(
                        OutcomeRecord.recorded_at >= start_date,
                        OutcomeRecord.recorded_at <= end_date,
                        OutcomeRecord.outcome == "accepted",
                        OutcomeRecord.compensation_offered.isnot(None)
                    )
                )
            )
            offer_data = offers.first()
            offer_count = offer_data[0] or 0
            total_compensation = offer_data[1] or 0
            avg_compensation = offer_data[2] or 0
        
        # Calculate time investment
        hours_applications = applications * hours_per_application
        hours_interviews = total_rounds * hours_per_interview
        total_hours = hours_applications + hours_interviews
        
        # Calculate rates
        app_to_interview = interviews / applications if applications > 0 else 0
        interview_to_offer = offer_count / interviews if interviews > 0 else 0
        overall_success = offer_count / applications if applications > 0 else 0
        
        # Compensation per hour
        comp_per_hour = total_compensation / total_hours if total_hours > 0 else 0
        
        return ROIMetrics(
            period_start=start_date,
            period_end=end_date,
            total_hours_invested=round(total_hours, 1),
            hours_per_application=hours_per_application,
            hours_in_interviews=round(hours_interviews, 1),
            applications_submitted=applications,
            interviews_secured=interviews,
            offers_received=offer_count,
            total_compensation_offered=total_compensation,
            avg_compensation_per_offer=round(avg_compensation, 2),
            compensation_per_hour_invested=round(comp_per_hour, 2),
            application_to_interview_rate=round(app_to_interview, 3),
            interview_to_offer_rate=round(interview_to_offer, 3),
            overall_success_rate=round(overall_success, 3)
        )
    
    async def get_top_performers(
        self,
        category: str = "opportunities",
        limit: int = 10,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> list[dict]:
        """
        Get top performing items in a category.
        
        Args:
            category: "opportunities" or "organizations"
            limit: Number of results
            start_date: Start of period
            end_date: End of period
        
        Returns:
            List of top performers with metrics
        """
        end_date = end_date or datetime.utcnow()
        start_date = start_date or (end_date - timedelta(days=90))
        
        results = []
        
        async with get_db_session() as session:
            if category == "opportunities":
                # Top opportunities by fit score
                query = await session.execute(
                    select(OpportunityRecord).where(
                        and_(
                            OpportunityRecord.discovered_at >= start_date,
                            OpportunityRecord.discovered_at <= end_date,
                            OpportunityRecord.fit_score.isnot(None)
                        )
                    ).order_by(OpportunityRecord.fit_score.desc()).limit(limit)
                )
                opportunities = query.scalars().all()
                
                for opp in opportunities:
                    results.append({
                        "id": str(opp.id),
                        "title": opp.title,
                        "organization": opp.organization,
                        "fit_score": opp.fit_score,
                        "type": opp.opportunity_type,
                        "discovered_at": opp.discovered_at.isoformat() if opp.discovered_at else None
                    })
            
            elif category == "organizations":
                # Top organizations by success rate
                query = await session.execute(
                    select(
                        OpportunityRecord.organization,
                        func.count(OpportunityRecord.id).label("total"),
                        func.avg(OpportunityRecord.fit_score).label("avg_score")
                    ).where(
                        and_(
                            OpportunityRecord.discovered_at >= start_date,
                            OpportunityRecord.discovered_at <= end_date,
                            OpportunityRecord.organization.isnot(None)
                        )
                    ).group_by(
                        OpportunityRecord.organization
                    ).having(
                        func.count(OpportunityRecord.id) >= 2
                    ).order_by(
                        func.avg(OpportunityRecord.fit_score).desc()
                    ).limit(limit)
                )
                
                for row in query:
                    results.append({
                        "organization": row.organization,
                        "opportunity_count": row.total,
                        "average_fit_score": round(row.avg_score or 0, 3)
                    })
        
        return results
    
    async def generate_dashboard(
        self,
        period_days: int = 30
    ) -> DashboardData:
        """
        Generate complete dashboard data.
        
        Args:
            period_days: Number of days to analyze
        
        Returns:
            Complete DashboardData object
        """
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=period_days)
        
        # Gather all data in parallel
        summary = await self.get_summary_metrics(start_date, end_date)
        funnel = await self.get_funnel_metrics(start_date, end_date)
        cohorts = await self.get_cohort_analysis("opportunity_type", start_date, end_date)
        roi = await self.calculate_roi(start_date, end_date)
        top_opportunities = await self.get_top_performers("opportunities", 10, start_date, end_date)
        top_organizations = await self.get_top_performers("organizations", 10, start_date, end_date)
        
        # Time series
        time_series = {
            "applications": await self.get_time_series("applications", MetricPeriod.DAILY, start_date, end_date),
            "opportunities": await self.get_time_series("opportunities", MetricPeriod.DAILY, start_date, end_date),
            "success_rate": await self.get_time_series("success_rate", MetricPeriod.WEEKLY, start_date, end_date)
        }
        
        return DashboardData(
            period=f"{period_days} days",
            summary=summary,
            time_series=time_series,
            funnel=funnel,
            cohorts=cohorts,
            roi=roi,
            top_opportunities=top_opportunities,
            top_organizations=top_organizations
        )


class AnalyticsExporter:
    """
    Export analytics data to various formats.
    """
    
    def __init__(self, analytics: AnalyticsEngine):
        self.analytics = analytics
    
    async def export_to_json(
        self,
        output_path: Path,
        period_days: int = 30
    ) -> Path:
        """Export dashboard data to JSON file."""
        dashboard = await self.analytics.generate_dashboard(period_days)
        
        with open(output_path, "w") as f:
            json.dump(dashboard.model_dump(), f, indent=2, default=str)
        
        logger.info(f"Exported analytics to {output_path}")
        return output_path
    
    async def export_to_csv(
        self,
        output_dir: Path,
        period_days: int = 30
    ) -> list[Path]:
        """Export analytics data to multiple CSV files."""
        output_dir.mkdir(parents=True, exist_ok=True)
        dashboard = await self.analytics.generate_dashboard(period_days)
        files = []
        
        # Export summary
        summary_path = output_dir / "summary.csv"
        with open(summary_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Metric", "Value"])
            for key, value in dashboard.summary.items():
                writer.writerow([key, value])
        files.append(summary_path)
        
        # Export funnel
        funnel_path = output_dir / "funnel.csv"
        with open(funnel_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["stage", "count", "conversion_rate"])
            writer.writeheader()
            for stage in dashboard.funnel:
                writer.writerow(stage.model_dump())
        files.append(funnel_path)
        
        # Export cohorts
        cohorts_path = output_dir / "cohorts.csv"
        with open(cohorts_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Cohort", "Size", "Avg Fit Score"])
            for cohort in dashboard.cohorts:
                writer.writerow([
                    cohort.cohort_name,
                    cohort.size,
                    cohort.metrics.get("average_fit_score", 0)
                ])
        files.append(cohorts_path)
        
        logger.info(f"Exported {len(files)} CSV files to {output_dir}")
        return files
    
    def format_for_display(self, dashboard: DashboardData) -> str:
        """Format dashboard data for terminal display."""
        lines = [
            "=" * 60,
            f"📊 ANALYTICS DASHBOARD - {dashboard.period}",
            f"Generated: {dashboard.generated_at.strftime('%Y-%m-%d %H:%M')}",
            "=" * 60,
            "",
            "📈 SUMMARY METRICS",
            "-" * 40,
        ]
        
        summary = dashboard.summary
        lines.extend([
            f"  Opportunities Discovered: {summary.get('total_opportunities_discovered', 0)}",
            f"  Applications Submitted:   {summary.get('applications_submitted', 0)}",
            f"  Outcomes Tracked:         {summary.get('outcomes_tracked', 0)}",
            f"  Average Fit Score:        {summary.get('average_fit_score', 0):.1%}",
            f"  Response Rate:            {summary.get('response_rate', 0):.1%}",
            f"  Acceptance Rate:          {summary.get('acceptance_rate', 0):.1%}",
            "",
            "🔄 CONVERSION FUNNEL",
            "-" * 40,
        ])
        
        for stage in dashboard.funnel:
            bar = "█" * int(stage.conversion_rate * 20)
            lines.append(f"  {stage.stage:<15} {stage.count:>5}  {bar} {stage.conversion_rate:.0%}")
        
        if dashboard.roi:
            lines.extend([
                "",
                "💰 ROI METRICS",
                "-" * 40,
                f"  Total Hours Invested:     {dashboard.roi.total_hours_invested:.1f}h",
                f"  Applications:             {dashboard.roi.applications_submitted}",
                f"  Interviews:               {dashboard.roi.interviews_secured}",
                f"  Offers:                   {dashboard.roi.offers_received}",
                f"  Application→Interview:    {dashboard.roi.application_to_interview_rate:.1%}",
                f"  Interview→Offer:          {dashboard.roi.interview_to_offer_rate:.1%}",
            ])
        
        if dashboard.top_opportunities:
            lines.extend([
                "",
                "🏆 TOP OPPORTUNITIES",
                "-" * 40,
            ])
            for i, opp in enumerate(dashboard.top_opportunities[:5], 1):
                lines.append(f"  {i}. {opp.get('title', 'Unknown')[:35]} ({opp.get('fit_score', 0):.0%})")
        
        lines.append("")
        lines.append("=" * 60)
        
        return "\n".join(lines)


# Convenience functions
async def get_dashboard(period_days: int = 30) -> DashboardData:
    """Quick function to get dashboard data."""
    engine = AnalyticsEngine(default_period_days=period_days)
    return await engine.generate_dashboard(period_days)


async def print_dashboard(period_days: int = 30) -> None:
    """Print formatted dashboard to console."""
    engine = AnalyticsEngine(default_period_days=period_days)
    dashboard = await engine.generate_dashboard(period_days)
    exporter = AnalyticsExporter(engine)
    print(exporter.format_for_display(dashboard))


async def export_analytics(
    output_path: str = "analytics_export",
    format: str = "json",
    period_days: int = 30
) -> None:
    """Export analytics to file."""
    engine = AnalyticsEngine(default_period_days=period_days)
    exporter = AnalyticsExporter(engine)
    
    if format == "json":
        await exporter.export_to_json(Path(f"{output_path}.json"), period_days)
    elif format == "csv":
        await exporter.export_to_csv(Path(output_path), period_days)
    else:
        raise ValueError(f"Unsupported format: {format}")
