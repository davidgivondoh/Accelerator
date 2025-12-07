"""
Reporting & Insights System

Comprehensive reporting system that generates automated insights, executive reports,
and actionable intelligence from all Growth Engine analytics data.
"""

import asyncio
import json
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from collections import defaultdict
import logging
from jinja2 import Environment, BaseLoader

logger = logging.getLogger(__name__)


class ReportType(Enum):
    """Types of reports available"""
    EXECUTIVE_SUMMARY = "executive_summary"         # High-level overview
    PERFORMANCE_DEEP_DIVE = "performance_deep_dive" # Detailed performance analysis
    OPTIMIZATION_REPORT = "optimization_report"     # Optimization recommendations
    SUCCESS_PATTERNS = "success_patterns"           # Pattern analysis report
    AB_TEST_RESULTS = "ab_test_results"             # A/B testing insights
    COMPETITIVE_ANALYSIS = "competitive_analysis"   # Market positioning
    TREND_ANALYSIS = "trend_analysis"               # Time-based trends
    CUSTOM_REPORT = "custom_report"                 # User-defined reports


class ReportFormat(Enum):
    """Report output formats"""
    HTML = "html"
    JSON = "json"
    MARKDOWN = "markdown"
    PDF = "pdf"
    CSV = "csv"


class InsightCategory(Enum):
    """Categories of insights"""
    PERFORMANCE = "performance"
    OPTIMIZATION = "optimization"
    TRENDS = "trends"
    PATTERNS = "patterns"
    RECOMMENDATIONS = "recommendations"
    ALERTS = "alerts"


class InsightSeverity(Enum):
    """Severity levels for insights"""
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class Insight:
    """Individual actionable insight"""
    insight_id: str
    category: InsightCategory
    severity: InsightSeverity
    title: str
    description: str
    recommendation: str
    supporting_data: Dict[str, Any]
    confidence: float  # 0-1 confidence score
    impact_score: float  # 0-1 potential impact
    created_at: datetime
    expires_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'insight_id': self.insight_id,
            'category': self.category.value,
            'severity': self.severity.value,
            'title': self.title,
            'description': self.description,
            'recommendation': self.recommendation,
            'supporting_data': self.supporting_data,
            'confidence': self.confidence,
            'impact_score': self.impact_score,
            'created_at': self.created_at.isoformat(),
            'expires_at': self.expires_at.isoformat() if self.expires_at else None
        }


@dataclass
class Report:
    """Complete report structure"""
    report_id: str
    report_type: ReportType
    title: str
    user_id: str
    generated_at: datetime
    time_period: Dict[str, datetime]
    insights: List[Insight]
    data_summary: Dict[str, Any]
    visualizations: List[Dict[str, Any]]
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'report_id': self.report_id,
            'report_type': self.report_type.value,
            'title': self.title,
            'user_id': self.user_id,
            'generated_at': self.generated_at.isoformat(),
            'time_period': {k: v.isoformat() for k, v in self.time_period.items()},
            'insights': [insight.to_dict() for insight in self.insights],
            'data_summary': self.data_summary,
            'visualizations': self.visualizations,
            'metadata': self.metadata
        }


class InsightGenerator:
    """Generates actionable insights from analytics data"""
    
    def __init__(self):
        self.insight_templates = self._load_insight_templates()
    
    def _load_insight_templates(self) -> Dict[str, Dict]:
        """Load insight generation templates"""
        return {
            'low_success_rate': {
                'category': InsightCategory.PERFORMANCE,
                'severity': InsightSeverity.HIGH,
                'title_template': 'Success Rate Below Benchmark',
                'description_template': 'Your success rate of {success_rate:.1%} is {diff:.1%} below the recommended benchmark',
                'recommendation_template': 'Focus on template optimization and timing improvements to boost success rates'
            },
            'declining_response_rate': {
                'category': InsightCategory.TRENDS,
                'severity': InsightSeverity.MEDIUM,
                'title_template': 'Response Rate Declining',
                'description_template': 'Response rate has declined {decline:.1%} over the past {period} days',
                'recommendation_template': 'Review and refresh your application templates and content strategy'
            },
            'platform_underperformance': {
                'category': InsightCategory.OPTIMIZATION,
                'severity': InsightSeverity.MEDIUM,
                'title_template': 'Platform {platform} Underperforming',
                'description_template': '{platform} shows {performance:.1%} lower success rate than other platforms',
                'recommendation_template': 'Consider reallocating efforts to higher-performing platforms or optimize {platform} strategy'
            },
            'timing_opportunity': {
                'category': InsightCategory.PATTERNS,
                'severity': InsightSeverity.LOW,
                'title_template': 'Optimal Timing Opportunity',
                'description_template': 'Applications submitted on {best_day} at {best_time} show {improvement:.1%} better performance',
                'recommendation_template': 'Schedule more applications for {best_day} at {best_time} for improved results'
            },
            'content_pattern_found': {
                'category': InsightCategory.PATTERNS,
                'severity': InsightSeverity.MEDIUM,
                'title_template': 'Successful Content Pattern Identified',
                'description_template': 'Content featuring "{theme}" shows {success_rate:.1%} success rate',
                'recommendation_template': 'Incorporate "{theme}" themes more frequently in your applications'
            },
            'automation_efficiency_low': {
                'category': InsightCategory.OPTIMIZATION,
                'severity': InsightSeverity.MEDIUM,
                'title_template': 'Low Automation Utilization',
                'description_template': 'Only {automation_rate:.1%} of tasks are automated, below the {benchmark:.1%} benchmark',
                'recommendation_template': 'Enable more automation features to improve efficiency and consistency'
            }
        }
    
    async def generate_insights(
        self,
        user_id: str,
        time_period: Dict[str, datetime]
    ) -> List[Insight]:
        """Generate insights for a user within a time period"""
        
        insights = []
        
        # Get analytics data
        from ..analytics.performance_metrics import global_metrics_engine
        from ..analytics.pattern_recognition import global_pattern_engine
        from ..pipeline.status_tracking import global_application_tracker
        
        # Get user applications
        applications = global_application_tracker.get_user_applications(user_id)
        
        # Filter by time period
        if time_period:
            start_date = time_period.get('start', datetime.utcnow() - timedelta(days=30))
            end_date = time_period.get('end', datetime.utcnow())
            
            applications = [
                app for app in applications
                if start_date <= datetime.fromisoformat(app.get('submitted_date', '').replace('Z', '+00:00')) <= end_date
            ]
        
        if len(applications) < 5:
            return insights
        
        # Generate performance insights
        performance_insights = await self._generate_performance_insights(user_id, applications)
        insights.extend(performance_insights)
        
        # Generate trend insights
        trend_insights = await self._generate_trend_insights(user_id, applications)
        insights.extend(trend_insights)
        
        # Generate pattern insights
        pattern_insights = await self._generate_pattern_insights(user_id, applications)
        insights.extend(pattern_insights)
        
        # Generate optimization insights
        optimization_insights = await self._generate_optimization_insights(user_id, applications)
        insights.extend(optimization_insights)
        
        return insights
    
    async def _generate_performance_insights(
        self,
        user_id: str,
        applications: List[Dict[str, Any]]
    ) -> List[Insight]:
        """Generate performance-related insights"""
        
        insights = []
        
        # Calculate success rate
        successful_apps = len([app for app in applications if app.get('current_stage') in ['offer_extended', 'offer_accepted']])
        success_rate = successful_apps / len(applications) if applications else 0
        
        benchmark_success_rate = 0.15  # 15% benchmark
        
        if success_rate < benchmark_success_rate:
            template = self.insight_templates['low_success_rate']
            
            insight = Insight(
                insight_id=f"perf_success_rate_{user_id}_{int(datetime.utcnow().timestamp())}",
                category=InsightCategory(template['category']),
                severity=InsightSeverity(template['severity']),
                title=template['title_template'],
                description=template['description_template'].format(
                    success_rate=success_rate,
                    diff=benchmark_success_rate - success_rate
                ),
                recommendation=template['recommendation_template'],
                supporting_data={
                    'current_success_rate': success_rate,
                    'benchmark': benchmark_success_rate,
                    'total_applications': len(applications),
                    'successful_applications': successful_apps
                },
                confidence=0.9,
                impact_score=0.8,
                created_at=datetime.utcnow()
            )
            insights.append(insight)
        
        # Calculate response rate
        responded_apps = len([app for app in applications if app.get('current_stage') not in ['submitted', 'draft']])
        response_rate = responded_apps / len(applications) if applications else 0
        
        benchmark_response_rate = 0.4  # 40% benchmark
        
        if response_rate < benchmark_response_rate:
            insight = Insight(
                insight_id=f"perf_response_rate_{user_id}_{int(datetime.utcnow().timestamp())}",
                category=InsightCategory.PERFORMANCE,
                severity=InsightSeverity.MEDIUM,
                title='Response Rate Below Benchmark',
                description=f'Your response rate of {response_rate:.1%} is {benchmark_response_rate - response_rate:.1%} below the recommended benchmark',
                recommendation='Review and optimize your application templates and outreach strategy',
                supporting_data={
                    'current_response_rate': response_rate,
                    'benchmark': benchmark_response_rate,
                    'total_applications': len(applications),
                    'responded_applications': responded_apps
                },
                confidence=0.85,
                impact_score=0.7,
                created_at=datetime.utcnow()
            )
            insights.append(insight)
        
        return insights
    
    async def _generate_trend_insights(
        self,
        user_id: str,
        applications: List[Dict[str, Any]]
    ) -> List[Insight]:
        """Generate trend-related insights"""
        
        insights = []
        
        if len(applications) < 10:
            return insights
        
        # Sort applications by date
        sorted_apps = sorted(applications, key=lambda x: x.get('submitted_date', ''))
        
        # Split into two periods for comparison
        mid_point = len(sorted_apps) // 2
        early_apps = sorted_apps[:mid_point]
        recent_apps = sorted_apps[mid_point:]
        
        # Calculate response rates for both periods
        early_responses = len([app for app in early_apps if app.get('current_stage') not in ['submitted', 'draft']])
        recent_responses = len([app for app in recent_apps if app.get('current_stage') not in ['submitted', 'draft']])
        
        early_rate = early_responses / len(early_apps) if early_apps else 0
        recent_rate = recent_responses / len(recent_apps) if recent_apps else 0
        
        if early_rate > 0 and recent_rate < early_rate * 0.8:  # 20% decline
            decline = early_rate - recent_rate
            
            template = self.insight_templates['declining_response_rate']
            
            insight = Insight(
                insight_id=f"trend_response_decline_{user_id}_{int(datetime.utcnow().timestamp())}",
                category=InsightCategory(template['category']),
                severity=InsightSeverity(template['severity']),
                title=template['title_template'],
                description=template['description_template'].format(
                    decline=decline,
                    period=30  # Approximate period
                ),
                recommendation=template['recommendation_template'],
                supporting_data={
                    'early_response_rate': early_rate,
                    'recent_response_rate': recent_rate,
                    'decline': decline,
                    'early_period_apps': len(early_apps),
                    'recent_period_apps': len(recent_apps)
                },
                confidence=0.75,
                impact_score=0.6,
                created_at=datetime.utcnow()
            )
            insights.append(insight)
        
        return insights
    
    async def _generate_pattern_insights(
        self,
        user_id: str,
        applications: List[Dict[str, Any]]
    ) -> List[Insight]:
        """Generate pattern-related insights"""
        
        insights = []
        
        # Analyze timing patterns
        day_performance = defaultdict(list)
        hour_performance = defaultdict(list)
        
        for app in applications:
            submitted_date = datetime.fromisoformat(app.get('submitted_date', '').replace('Z', '+00:00'))
            is_successful = app.get('current_stage') in ['offer_extended', 'offer_accepted']
            
            day_performance[submitted_date.strftime('%A')].append(is_successful)
            hour_performance[submitted_date.hour].append(is_successful)
        
        # Find best day
        best_day_performance = 0
        best_day = None
        
        for day, results in day_performance.items():
            if len(results) >= 3:
                performance = sum(results) / len(results)
                if performance > best_day_performance:
                    best_day_performance = performance
                    best_day = day
        
        # Find best hour
        best_hour_performance = 0
        best_hour = None
        
        for hour, results in hour_performance.items():
            if len(results) >= 2:
                performance = sum(results) / len(results)
                if performance > best_hour_performance:
                    best_hour_performance = performance
                    best_hour = hour
        
        # Generate timing insight if patterns are strong enough
        if best_day and best_day_performance > 0.2:  # At least 20% success rate
            avg_performance = sum(sum(results) for results in day_performance.values()) / sum(len(results) for results in day_performance.values())
            improvement = best_day_performance - avg_performance
            
            if improvement > 0.1:  # At least 10% improvement
                time_str = f"{best_hour}:00" if best_hour and best_hour < 12 else f"{best_hour-12}:00 PM" if best_hour and best_hour > 12 else "noon" if best_hour == 12 else "morning"
                
                template = self.insight_templates['timing_opportunity']
                
                insight = Insight(
                    insight_id=f"pattern_timing_{user_id}_{int(datetime.utcnow().timestamp())}",
                    category=InsightCategory(template['category']),
                    severity=InsightSeverity(template['severity']),
                    title=template['title_template'],
                    description=template['description_template'].format(
                        best_day=best_day,
                        best_time=time_str,
                        improvement=improvement
                    ),
                    recommendation=template['recommendation_template'].format(
                        best_day=best_day,
                        best_time=time_str
                    ),
                    supporting_data={
                        'best_day': best_day,
                        'best_day_performance': best_day_performance,
                        'best_hour': best_hour,
                        'improvement': improvement,
                        'sample_size': len(day_performance[best_day])
                    },
                    confidence=min(0.8, len(day_performance[best_day]) / 10),
                    impact_score=improvement,
                    created_at=datetime.utcnow()
                )
                insights.append(insight)
        
        return insights
    
    async def _generate_optimization_insights(
        self,
        user_id: str,
        applications: List[Dict[str, Any]]
    ) -> List[Insight]:
        """Generate optimization-related insights"""
        
        insights = []
        
        # Calculate automation rate (simplified)
        automated_tasks = 0
        total_tasks = len(applications) * 3  # Assume 3 tasks per application
        
        # Count automated events
        for app in applications:
            events = app.get('events', [])
            automated_events = [e for e in events if e.get('metadata', {}).get('automated', False)]
            automated_tasks += len(automated_events)
        
        automation_rate = automated_tasks / max(total_tasks, 1)
        benchmark_automation = 0.6  # 60% benchmark
        
        if automation_rate < benchmark_automation:
            template = self.insight_templates['automation_efficiency_low']
            
            insight = Insight(
                insight_id=f"opt_automation_{user_id}_{int(datetime.utcnow().timestamp())}",
                category=InsightCategory(template['category']),
                severity=InsightSeverity(template['severity']),
                title=template['title_template'],
                description=template['description_template'].format(
                    automation_rate=automation_rate,
                    benchmark=benchmark_automation
                ),
                recommendation=template['recommendation_template'],
                supporting_data={
                    'current_automation_rate': automation_rate,
                    'benchmark': benchmark_automation,
                    'automated_tasks': automated_tasks,
                    'total_tasks': total_tasks
                },
                confidence=0.7,
                impact_score=0.5,
                created_at=datetime.utcnow()
            )
            insights.append(insight)
        
        return insights


class ReportGenerator:
    """Generates comprehensive reports from analytics data"""
    
    def __init__(self):
        self.insight_generator = InsightGenerator()
        self.template_env = Environment(loader=BaseLoader())
        self._load_report_templates()
    
    def _load_report_templates(self):
        """Load report templates"""
        self.templates = {
            ReportType.EXECUTIVE_SUMMARY: """
# Executive Summary Report

**Report Period:** {{ time_period.start.strftime('%B %d, %Y') }} - {{ time_period.end.strftime('%B %d, %Y') }}
**Generated:** {{ generated_at.strftime('%B %d, %Y at %I:%M %p') }}

## Key Metrics

- **Total Applications:** {{ data_summary.total_applications }}
- **Success Rate:** {{ "%.1f%%" | format(data_summary.success_rate * 100) }}
- **Response Rate:** {{ "%.1f%%" | format(data_summary.response_rate * 100) }}
- **Average Time to Response:** {{ data_summary.avg_response_time_days }} days

## Critical Insights

{% for insight in insights[:3] %}
### {{ insight.title }}
**Severity:** {{ insight.severity.value.title() }}

{{ insight.description }}

**Recommendation:** {{ insight.recommendation }}

{% endfor %}

## Performance Trends

{% if visualizations %}
{% for viz in visualizations %}
- {{ viz.title }}: {{ viz.summary }}
{% endfor %}
{% endif %}

---
*This report was automatically generated by the Growth Engine Analytics System.*
            """,
            
            ReportType.PERFORMANCE_DEEP_DIVE: """
# Performance Deep Dive Report

**Analysis Period:** {{ time_period.start.strftime('%B %d, %Y') }} - {{ time_period.end.strftime('%B %d, %Y') }}

## Application Performance Analysis

### Overall Metrics
- **Applications Submitted:** {{ data_summary.total_applications }}
- **Success Rate:** {{ "%.1f%%" | format(data_summary.success_rate * 100) }}
- **Response Rate:** {{ "%.1f%%" | format(data_summary.response_rate * 100) }}
- **Interview Rate:** {{ "%.1f%%" | format(data_summary.interview_rate * 100) }}

### Stage Breakdown
{% for stage, count in data_summary.stage_distribution.items() %}
- **{{ stage.replace('_', ' ').title() }}:** {{ count }} applications
{% endfor %}

## Detailed Insights

{% for insight in insights %}
### {{ insight.title }}
**Category:** {{ insight.category.value.title() }} | **Confidence:** {{ "%.0f%%" | format(insight.confidence * 100) }}

{{ insight.description }}

**Recommendation:** {{ insight.recommendation }}

**Supporting Data:**
{% for key, value in insight.supporting_data.items() %}
- {{ key.replace('_', ' ').title() }}: {{ value }}
{% endfor %}

---
{% endfor %}

## Performance Visualizations

{% for viz in visualizations %}
### {{ viz.title }}
{{ viz.description }}
{% endfor %}
            """
        }
    
    async def generate_report(
        self,
        report_type: ReportType,
        user_id: str,
        time_period: Dict[str, datetime],
        format: ReportFormat = ReportFormat.MARKDOWN
    ) -> Report:
        """Generate a comprehensive report"""
        
        # Generate insights
        insights = await self.insight_generator.generate_insights(user_id, time_period)
        
        # Gather data summary
        data_summary = await self._gather_data_summary(user_id, time_period)
        
        # Generate visualizations
        visualizations = await self._generate_visualizations(user_id, time_period, data_summary)
        
        # Create report
        report_id = f"report_{report_type.value}_{user_id}_{int(datetime.utcnow().timestamp())}"
        
        report = Report(
            report_id=report_id,
            report_type=report_type,
            title=self._generate_report_title(report_type, time_period),
            user_id=user_id,
            generated_at=datetime.utcnow(),
            time_period=time_period,
            insights=insights,
            data_summary=data_summary,
            visualizations=visualizations
        )
        
        return report
    
    async def _gather_data_summary(
        self,
        user_id: str,
        time_period: Dict[str, datetime]
    ) -> Dict[str, Any]:
        """Gather summary data for the report"""
        
        from ..pipeline.status_tracking import global_application_tracker
        
        applications = global_application_tracker.get_user_applications(user_id)
        
        # Filter by time period
        if time_period:
            start_date = time_period.get('start', datetime.utcnow() - timedelta(days=30))
            end_date = time_period.get('end', datetime.utcnow())
            
            applications = [
                app for app in applications
                if start_date <= datetime.fromisoformat(app.get('submitted_date', '').replace('Z', '+00:00')) <= end_date
            ]
        
        if not applications:
            return {
                'total_applications': 0,
                'success_rate': 0.0,
                'response_rate': 0.0,
                'interview_rate': 0.0,
                'avg_response_time_days': 0,
                'stage_distribution': {}
            }
        
        # Calculate metrics
        total_apps = len(applications)
        successful_apps = len([app for app in applications if app.get('current_stage') in ['offer_extended', 'offer_accepted']])
        responded_apps = len([app for app in applications if app.get('current_stage') not in ['submitted', 'draft']])
        interview_apps = len([app for app in applications if 'interview' in app.get('current_stage', '')])
        
        # Stage distribution
        stage_distribution = defaultdict(int)
        for app in applications:
            stage = app.get('current_stage', 'unknown')
            stage_distribution[stage] += 1
        
        # Average response time (simplified)
        response_times = []
        for app in applications:
            if app.get('current_stage') not in ['submitted', 'draft']:
                submitted_date = datetime.fromisoformat(app.get('submitted_date', '').replace('Z', '+00:00'))
                # Estimate response time based on stage progression
                days_since_submission = (datetime.utcnow() - submitted_date).days
                response_times.append(min(days_since_submission, 30))  # Cap at 30 days
        
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        return {
            'total_applications': total_apps,
            'success_rate': successful_apps / total_apps,
            'response_rate': responded_apps / total_apps,
            'interview_rate': interview_apps / total_apps,
            'avg_response_time_days': avg_response_time,
            'stage_distribution': dict(stage_distribution),
            'successful_applications': successful_apps,
            'responded_applications': responded_apps,
            'interview_applications': interview_apps
        }
    
    async def _generate_visualizations(
        self,
        user_id: str,
        time_period: Dict[str, datetime],
        data_summary: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate visualization specifications for the report"""
        
        visualizations = []
        
        # Success rate trend visualization
        visualizations.append({
            'type': 'line_chart',
            'title': 'Success Rate Trend',
            'description': 'Application success rate over time',
            'data_source': 'application_success_trend',
            'summary': f"Current success rate: {data_summary['success_rate']:.1%}"
        })
        
        # Stage distribution pie chart
        visualizations.append({
            'type': 'pie_chart',
            'title': 'Application Stage Distribution',
            'description': 'Current distribution of applications across stages',
            'data_source': 'stage_distribution',
            'summary': f"Most applications in: {max(data_summary['stage_distribution'], key=data_summary['stage_distribution'].get) if data_summary['stage_distribution'] else 'N/A'}"
        })
        
        # Platform performance comparison
        visualizations.append({
            'type': 'bar_chart',
            'title': 'Platform Performance Comparison',
            'description': 'Success rates by application platform',
            'data_source': 'platform_performance',
            'summary': 'Platform performance analysis'
        })
        
        return visualizations
    
    def _generate_report_title(self, report_type: ReportType, time_period: Dict[str, datetime]) -> str:
        """Generate appropriate title for the report"""
        
        start = time_period.get('start', datetime.utcnow() - timedelta(days=30))
        end = time_period.get('end', datetime.utcnow())
        
        period_str = f"{start.strftime('%b %d')} - {end.strftime('%b %d, %Y')}"
        
        title_map = {
            ReportType.EXECUTIVE_SUMMARY: f"Executive Summary Report ({period_str})",
            ReportType.PERFORMANCE_DEEP_DIVE: f"Performance Analysis ({period_str})",
            ReportType.OPTIMIZATION_REPORT: f"Optimization Recommendations ({period_str})",
            ReportType.SUCCESS_PATTERNS: f"Success Pattern Analysis ({period_str})",
            ReportType.AB_TEST_RESULTS: f"A/B Test Results ({period_str})",
            ReportType.TREND_ANALYSIS: f"Trend Analysis ({period_str})"
        }
        
        return title_map.get(report_type, f"Growth Engine Report ({period_str})")
    
    def render_report(self, report: Report, format: ReportFormat = ReportFormat.MARKDOWN) -> str:
        """Render report in specified format"""
        
        if format == ReportFormat.JSON:
            return json.dumps(report.to_dict(), indent=2)
        
        elif format == ReportFormat.MARKDOWN:
            template_str = self.templates.get(report.report_type, "# Report\n\nReport content not available.")
            template = self.template_env.from_string(template_str)
            
            return template.render(
                report_type=report.report_type,
                title=report.title,
                generated_at=report.generated_at,
                time_period=report.time_period,
                insights=report.insights,
                data_summary=report.data_summary,
                visualizations=report.visualizations
            )
        
        elif format == ReportFormat.HTML:
            # Convert markdown to HTML (simplified)
            markdown_content = self.render_report(report, ReportFormat.MARKDOWN)
            html_content = f"""
            <html>
            <head><title>{report.title}</title></head>
            <body>
                <div style="font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px;">
                    <pre style="white-space: pre-wrap;">{markdown_content}</pre>
                </div>
            </body>
            </html>
            """
            return html_content
        
        else:
            return f"Unsupported format: {format}"


class ReportingSystem:
    """Main reporting and insights system"""
    
    def __init__(self):
        self.report_generator = ReportGenerator()
        self.insight_generator = InsightGenerator()
        self.reports: Dict[str, Report] = {}
        self.scheduled_reports: Dict[str, Dict[str, Any]] = {}
        
        # Start background report generation
        asyncio.create_task(self._generate_scheduled_reports())
    
    async def generate_report(
        self,
        report_type: ReportType,
        user_id: str,
        time_period: Optional[Dict[str, datetime]] = None,
        format: ReportFormat = ReportFormat.MARKDOWN
    ) -> Report:
        """Generate a report for a user"""
        
        if not time_period:
            time_period = {
                'start': datetime.utcnow() - timedelta(days=30),
                'end': datetime.utcnow()
            }
        
        report = await self.report_generator.generate_report(report_type, user_id, time_period, format)
        self.reports[report.report_id] = report
        
        logger.info(f"Generated {report_type.value} report for user {user_id}")
        
        return report
    
    def schedule_report(
        self,
        report_type: ReportType,
        user_id: str,
        frequency_days: int,
        format: ReportFormat = ReportFormat.MARKDOWN
    ):
        """Schedule recurring report generation"""
        
        schedule_id = f"schedule_{report_type.value}_{user_id}_{frequency_days}"
        
        self.scheduled_reports[schedule_id] = {
            'report_type': report_type,
            'user_id': user_id,
            'frequency_days': frequency_days,
            'format': format,
            'last_generated': None,
            'next_due': datetime.utcnow() + timedelta(days=frequency_days)
        }
        
        logger.info(f"Scheduled {report_type.value} report for user {user_id} every {frequency_days} days")
    
    async def get_user_insights(self, user_id: str, severity_filter: Optional[InsightSeverity] = None) -> List[Insight]:
        """Get current insights for a user"""
        
        time_period = {
            'start': datetime.utcnow() - timedelta(days=30),
            'end': datetime.utcnow()
        }
        
        insights = await self.insight_generator.generate_insights(user_id, time_period)
        
        # Filter by severity if specified
        if severity_filter:
            severity_order = [InsightSeverity.INFO, InsightSeverity.LOW, InsightSeverity.MEDIUM, InsightSeverity.HIGH, InsightSeverity.CRITICAL]
            min_index = severity_order.index(severity_filter)
            
            insights = [
                insight for insight in insights
                if severity_order.index(insight.severity) >= min_index
            ]
        
        return insights
    
    def get_report_summary(self, user_id: str) -> Dict[str, Any]:
        """Get summary of reports for a user"""
        
        user_reports = [report for report in self.reports.values() if report.user_id == user_id]
        
        return {
            'total_reports': len(user_reports),
            'report_types': list(set([report.report_type.value for report in user_reports])),
            'latest_report': max([report.generated_at for report in user_reports]).isoformat() if user_reports else None,
            'scheduled_reports': len([s for s in self.scheduled_reports.values() if s['user_id'] == user_id])
        }
    
    async def _generate_scheduled_reports(self):
        """Background task to generate scheduled reports"""
        
        while True:
            try:
                current_time = datetime.utcnow()
                
                for schedule_id, schedule in list(self.scheduled_reports.items()):
                    if current_time >= schedule['next_due']:
                        # Generate the report
                        await self.generate_report(
                            schedule['report_type'],
                            schedule['user_id'],
                            format=schedule['format']
                        )
                        
                        # Update schedule
                        schedule['last_generated'] = current_time
                        schedule['next_due'] = current_time + timedelta(days=schedule['frequency_days'])
                
                await asyncio.sleep(3600)  # Check every hour
                
            except Exception as e:
                logger.error(f"Error in scheduled report generation: {str(e)}")
                await asyncio.sleep(300)  # Retry in 5 minutes


# Global reporting system
global_reporting_system = ReportingSystem()