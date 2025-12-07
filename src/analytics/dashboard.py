"""
Analytics Dashboard System

Comprehensive dashboard for visualizing performance metrics, tracking success rates,
and providing actionable insights across all Growth Engine activities.
"""

import asyncio
import json
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)


class DashboardMetricType(Enum):
    """Types of metrics tracked in dashboard"""
    SUCCESS_RATE = "success_rate"
    RESPONSE_RATE = "response_rate"
    CONVERSION_RATE = "conversion_rate"
    TIME_TO_RESPONSE = "time_to_response"
    APPLICATION_VOLUME = "application_volume"
    PLATFORM_PERFORMANCE = "platform_performance"
    TEMPLATE_EFFECTIVENESS = "template_effectiveness"
    FOLLOW_UP_SUCCESS = "follow_up_success"
    SKILL_MATCH_SCORE = "skill_match_score"
    COMPANY_RESPONSE_RATE = "company_response_rate"


class TimeRange(Enum):
    """Time ranges for dashboard views"""
    LAST_7_DAYS = "7d"
    LAST_30_DAYS = "30d"
    LAST_90_DAYS = "90d"
    LAST_6_MONTHS = "6m"
    LAST_YEAR = "1y"
    ALL_TIME = "all"


@dataclass
class MetricValue:
    """Individual metric value with metadata"""
    value: Union[float, int]
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'value': self.value,
            'timestamp': self.timestamp.isoformat(),
            'metadata': self.metadata
        }


@dataclass
class DashboardWidget:
    """Individual dashboard widget configuration"""
    widget_id: str
    title: str
    metric_type: DashboardMetricType
    chart_type: str  # line, bar, pie, gauge, number, table
    time_range: TimeRange
    filters: Dict[str, Any] = field(default_factory=dict)
    position: Tuple[int, int] = (0, 0)
    size: Tuple[int, int] = (12, 6)  # grid units
    refreshRate: int = 300  # seconds
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'widget_id': self.widget_id,
            'title': self.title,
            'metric_type': self.metric_type.value,
            'chart_type': self.chart_type,
            'time_range': self.time_range.value,
            'filters': self.filters,
            'position': self.position,
            'size': self.size,
            'refreshRate': self.refreshRate
        }


@dataclass
class DashboardLayout:
    """Dashboard layout configuration"""
    layout_id: str
    name: str
    description: str
    widgets: List[DashboardWidget] = field(default_factory=list)
    created_by: str = "system"
    created_at: datetime = field(default_factory=datetime.utcnow)
    is_default: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'layout_id': self.layout_id,
            'name': self.name,
            'description': self.description,
            'widgets': [widget.to_dict() for widget in self.widgets],
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat(),
            'is_default': self.is_default
        }


class MetricCalculator:
    """Calculates various dashboard metrics"""
    
    def __init__(self):
        self.data_cache: Dict[str, Any] = {}
        self.cache_ttl = 300  # 5 minutes
        self.last_cache_update = {}
    
    async def calculate_success_rate(
        self,
        user_id: str,
        time_range: TimeRange,
        filters: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Calculate application success rate"""
        
        # Get applications data
        from ..pipeline.status_tracking import global_application_tracker
        applications = global_application_tracker.get_user_applications(user_id)
        
        # Apply time filter
        applications = self._filter_by_time(applications, time_range)
        
        # Apply additional filters
        if filters:
            applications = self._apply_filters(applications, filters)
        
        if not applications:
            return {'value': 0.0, 'total_applications': 0, 'successful_applications': 0}
        
        # Count successful applications
        successful_stages = ['offer_accepted', 'offer_extended']
        successful = [app for app in applications if app.get('current_stage') in successful_stages]
        
        success_rate = len(successful) / len(applications)
        
        return {
            'value': success_rate,
            'total_applications': len(applications),
            'successful_applications': len(successful),
            'success_rate_percentage': success_rate * 100,
            'stage_breakdown': self._get_stage_breakdown(applications)
        }
    
    async def calculate_response_rate(
        self,
        user_id: str,
        time_range: TimeRange,
        filters: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Calculate response rate from companies"""
        
        from ..pipeline.status_tracking import global_application_tracker
        applications = global_application_tracker.get_user_applications(user_id)
        
        applications = self._filter_by_time(applications, time_range)
        if filters:
            applications = self._apply_filters(applications, filters)
        
        if not applications:
            return {'value': 0.0, 'total_applications': 0, 'responses': 0}
        
        # Count applications with responses (beyond submitted stage)
        response_stages = [
            'under_review', 'screening', 'first_interview', 'technical_interview',
            'final_interview', 'reference_check', 'offer_extended', 'offer_accepted',
            'rejected'
        ]
        
        responded = [app for app in applications if app.get('current_stage') in response_stages]
        response_rate = len(responded) / len(applications)
        
        return {
            'value': response_rate,
            'total_applications': len(applications),
            'responses': len(responded),
            'response_rate_percentage': response_rate * 100,
            'average_response_time_days': self._calculate_average_response_time(applications)
        }
    
    async def calculate_conversion_rates(
        self,
        user_id: str,
        time_range: TimeRange,
        filters: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Calculate conversion rates between stages"""
        
        from ..pipeline.status_tracking import global_application_tracker
        applications = global_application_tracker.get_user_applications(user_id)
        
        applications = self._filter_by_time(applications, time_range)
        if filters:
            applications = self._apply_filters(applications, filters)
        
        # Define conversion funnel stages
        stages = [
            'submitted', 'under_review', 'screening', 'first_interview',
            'technical_interview', 'final_interview', 'offer_extended'
        ]
        
        # Count applications at each stage and beyond
        stage_counts = {}
        for stage in stages:
            stage_counts[stage] = len([
                app for app in applications 
                if self._is_stage_reached(app.get('current_stage', ''), stage)
            ])
        
        # Calculate conversion rates
        conversions = {}
        for i in range(len(stages) - 1):
            current_stage = stages[i]
            next_stage = stages[i + 1]
            
            if stage_counts[current_stage] > 0:
                conversion_rate = stage_counts[next_stage] / stage_counts[current_stage]
            else:
                conversion_rate = 0.0
            
            conversions[f"{current_stage}_to_{next_stage}"] = {
                'rate': conversion_rate,
                'rate_percentage': conversion_rate * 100,
                'current_count': stage_counts[current_stage],
                'next_count': stage_counts[next_stage]
            }
        
        return {
            'stage_counts': stage_counts,
            'conversions': conversions,
            'overall_funnel_efficiency': stage_counts.get('offer_extended', 0) / max(stage_counts.get('submitted', 1), 1)
        }
    
    async def calculate_platform_performance(
        self,
        user_id: str,
        time_range: TimeRange,
        filters: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Calculate performance by platform"""
        
        from ..pipeline.status_tracking import global_application_tracker
        applications = global_application_tracker.get_user_applications(user_id)
        
        applications = self._filter_by_time(applications, time_range)
        if filters:
            applications = self._apply_filters(applications, filters)
        
        platform_stats = defaultdict(lambda: {
            'total_applications': 0,
            'responses': 0,
            'successful': 0,
            'average_response_time': 0
        })
        
        for app in applications:
            # Extract platform from events or metadata
            platform = self._extract_platform(app)
            
            platform_stats[platform]['total_applications'] += 1
            
            # Check for response
            if app.get('current_stage') not in ['submitted', 'draft']:
                platform_stats[platform]['responses'] += 1
            
            # Check for success
            if app.get('current_stage') in ['offer_extended', 'offer_accepted']:
                platform_stats[platform]['successful'] += 1
        
        # Calculate rates
        platform_metrics = {}
        for platform, stats in platform_stats.items():
            total = stats['total_applications']
            platform_metrics[platform] = {
                'total_applications': total,
                'response_rate': (stats['responses'] / total) if total > 0 else 0,
                'success_rate': (stats['successful'] / total) if total > 0 else 0,
                'response_count': stats['responses'],
                'success_count': stats['successful']
            }
        
        return platform_metrics
    
    async def calculate_template_effectiveness(
        self,
        user_id: str,
        time_range: TimeRange,
        filters: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Calculate effectiveness of different templates"""
        
        from ..pipeline.status_tracking import global_application_tracker
        applications = global_application_tracker.get_user_applications(user_id)
        
        applications = self._filter_by_time(applications, time_range)
        if filters:
            applications = self._apply_filters(applications, filters)
        
        template_stats = defaultdict(lambda: {
            'usage_count': 0,
            'response_count': 0,
            'success_count': 0
        })
        
        for app in applications:
            # Extract template type from events or metadata
            template_type = self._extract_template_type(app)
            
            template_stats[template_type]['usage_count'] += 1
            
            if app.get('current_stage') not in ['submitted', 'draft']:
                template_stats[template_type]['response_count'] += 1
            
            if app.get('current_stage') in ['offer_extended', 'offer_accepted']:
                template_stats[template_type]['success_count'] += 1
        
        # Calculate effectiveness metrics
        template_metrics = {}
        for template, stats in template_stats.items():
            usage = stats['usage_count']
            template_metrics[template] = {
                'usage_count': usage,
                'response_rate': (stats['response_count'] / usage) if usage > 0 else 0,
                'success_rate': (stats['success_count'] / usage) if usage > 0 else 0,
                'effectiveness_score': self._calculate_template_effectiveness_score(stats)
            }
        
        return template_metrics
    
    def _filter_by_time(self, applications: List[Dict], time_range: TimeRange) -> List[Dict]:
        """Filter applications by time range"""
        
        if time_range == TimeRange.ALL_TIME:
            return applications
        
        # Define time deltas
        time_deltas = {
            TimeRange.LAST_7_DAYS: timedelta(days=7),
            TimeRange.LAST_30_DAYS: timedelta(days=30),
            TimeRange.LAST_90_DAYS: timedelta(days=90),
            TimeRange.LAST_6_MONTHS: timedelta(days=180),
            TimeRange.LAST_YEAR: timedelta(days=365)
        }
        
        cutoff_date = datetime.utcnow() - time_deltas.get(time_range, timedelta(days=30))
        
        return [
            app for app in applications
            if datetime.fromisoformat(app.get('submitted_date', '').replace('Z', '+00:00')) >= cutoff_date
        ]
    
    def _apply_filters(self, applications: List[Dict], filters: Dict[str, Any]) -> List[Dict]:
        """Apply additional filters to applications"""
        
        filtered = applications
        
        if 'company' in filters:
            company_filter = filters['company'].lower()
            filtered = [app for app in filtered if company_filter in app.get('company_name', '').lower()]
        
        if 'priority' in filters:
            priority_filter = filters['priority']
            filtered = [app for app in filtered if app.get('priority') == priority_filter]
        
        if 'stage' in filters:
            stage_filter = filters['stage']
            filtered = [app for app in filtered if app.get('current_stage') == stage_filter]
        
        return filtered
    
    def _get_stage_breakdown(self, applications: List[Dict]) -> Dict[str, int]:
        """Get breakdown of applications by stage"""
        
        breakdown = defaultdict(int)
        for app in applications:
            stage = app.get('current_stage', 'unknown')
            breakdown[stage] += 1
        
        return dict(breakdown)
    
    def _calculate_average_response_time(self, applications: List[Dict]) -> float:
        """Calculate average time to first response"""
        
        response_times = []
        
        for app in applications:
            if app.get('current_stage') not in ['submitted', 'draft']:
                # Find first response event
                events = app.get('events', [])
                submitted_time = None
                first_response_time = None
                
                for event in sorted(events, key=lambda x: x.get('timestamp', '')):
                    if event.get('event_type') == 'application_submitted':
                        submitted_time = datetime.fromisoformat(event.get('timestamp', '').replace('Z', '+00:00'))
                    elif 'response' in event.get('event_type', '').lower() and submitted_time:
                        first_response_time = datetime.fromisoformat(event.get('timestamp', '').replace('Z', '+00:00'))
                        break
                
                if submitted_time and first_response_time:
                    response_time = (first_response_time - submitted_time).days
                    response_times.append(response_time)
        
        return sum(response_times) / len(response_times) if response_times else 0
    
    def _is_stage_reached(self, current_stage: str, target_stage: str) -> bool:
        """Check if target stage has been reached"""
        
        stage_order = [
            'draft', 'submitted', 'under_review', 'screening', 'first_interview',
            'technical_interview', 'final_interview', 'reference_check',
            'offer_extended', 'offer_accepted', 'rejected', 'withdrawn'
        ]
        
        try:
            current_idx = stage_order.index(current_stage)
            target_idx = stage_order.index(target_stage)
            return current_idx >= target_idx
        except ValueError:
            return False
    
    def _extract_platform(self, application: Dict) -> str:
        """Extract platform from application data"""
        
        # Check events for submission method
        events = application.get('events', [])
        for event in events:
            if event.get('event_type') == 'application_submitted':
                return event.get('metadata', {}).get('submission_method', 'unknown')
        
        return 'unknown'
    
    def _extract_template_type(self, application: Dict) -> str:
        """Extract template type from application data"""
        
        # Check events for template usage
        events = application.get('events', [])
        for event in events:
            if 'template' in event.get('event_type', '').lower():
                return event.get('metadata', {}).get('template_type', 'default')
        
        return 'default'
    
    def _calculate_template_effectiveness_score(self, stats: Dict) -> float:
        """Calculate overall template effectiveness score"""
        
        usage = stats['usage_count']
        if usage == 0:
            return 0.0
        
        response_rate = stats['response_count'] / usage
        success_rate = stats['success_count'] / usage
        
        # Weighted score: 30% response rate, 70% success rate
        effectiveness = (0.3 * response_rate) + (0.7 * success_rate)
        
        return effectiveness


class DashboardManager:
    """Main dashboard management system"""
    
    def __init__(self):
        self.layouts: Dict[str, DashboardLayout] = {}
        self.metric_calculator = MetricCalculator()
        self.default_layouts_initialized = False
        
        # Initialize default layouts
        asyncio.create_task(self._initialize_default_layouts())
    
    async def _initialize_default_layouts(self):
        """Initialize default dashboard layouts"""
        
        if self.default_layouts_initialized:
            return
        
        # Executive Overview Layout
        executive_layout = DashboardLayout(
            layout_id="executive_overview",
            name="Executive Overview",
            description="High-level metrics for leadership visibility",
            is_default=True
        )
        
        executive_layout.widgets = [
            DashboardWidget(
                widget_id="success_rate_gauge",
                title="Overall Success Rate",
                metric_type=DashboardMetricType.SUCCESS_RATE,
                chart_type="gauge",
                time_range=TimeRange.LAST_30_DAYS,
                position=(0, 0),
                size=(6, 4)
            ),
            DashboardWidget(
                widget_id="application_volume_line",
                title="Application Volume Trend",
                metric_type=DashboardMetricType.APPLICATION_VOLUME,
                chart_type="line",
                time_range=TimeRange.LAST_90_DAYS,
                position=(6, 0),
                size=(6, 4)
            ),
            DashboardWidget(
                widget_id="response_rate_bar",
                title="Response Rate by Platform",
                metric_type=DashboardMetricType.PLATFORM_PERFORMANCE,
                chart_type="bar",
                time_range=TimeRange.LAST_30_DAYS,
                position=(0, 4),
                size=(12, 4)
            ),
            DashboardWidget(
                widget_id="conversion_funnel",
                title="Application Funnel",
                metric_type=DashboardMetricType.CONVERSION_RATE,
                chart_type="funnel",
                time_range=TimeRange.LAST_30_DAYS,
                position=(0, 8),
                size=(12, 6)
            )
        ]
        
        self.layouts["executive_overview"] = executive_layout
        
        # Operational Dashboard Layout
        operational_layout = DashboardLayout(
            layout_id="operational_dashboard",
            name="Operational Dashboard",
            description="Detailed operational metrics and performance tracking"
        )
        
        operational_layout.widgets = [
            DashboardWidget(
                widget_id="template_effectiveness",
                title="Template Effectiveness",
                metric_type=DashboardMetricType.TEMPLATE_EFFECTIVENESS,
                chart_type="table",
                time_range=TimeRange.LAST_30_DAYS,
                position=(0, 0),
                size=(6, 6)
            ),
            DashboardWidget(
                widget_id="response_time_trend",
                title="Average Response Time",
                metric_type=DashboardMetricType.TIME_TO_RESPONSE,
                chart_type="line",
                time_range=TimeRange.LAST_90_DAYS,
                position=(6, 0),
                size=(6, 6)
            ),
            DashboardWidget(
                widget_id="follow_up_success",
                title="Follow-up Success Rates",
                metric_type=DashboardMetricType.FOLLOW_UP_SUCCESS,
                chart_type="pie",
                time_range=TimeRange.LAST_30_DAYS,
                position=(0, 6),
                size=(6, 6)
            ),
            DashboardWidget(
                widget_id="skill_match_scores",
                title="Skill Match Distribution",
                metric_type=DashboardMetricType.SKILL_MATCH_SCORE,
                chart_type="histogram",
                time_range=TimeRange.LAST_30_DAYS,
                position=(6, 6),
                size=(6, 6)
            )
        ]
        
        self.layouts["operational_dashboard"] = operational_layout
        
        self.default_layouts_initialized = True
        logger.info("Initialized default dashboard layouts")
    
    async def get_dashboard_data(
        self,
        layout_id: str,
        user_id: str,
        time_range: Optional[TimeRange] = None,
        filters: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Get complete dashboard data for a layout"""
        
        if layout_id not in self.layouts:
            raise ValueError(f"Layout {layout_id} not found")
        
        layout = self.layouts[layout_id]
        dashboard_data = {
            'layout': layout.to_dict(),
            'widgets': {},
            'last_updated': datetime.utcnow().isoformat()
        }
        
        # Get data for each widget
        for widget in layout.widgets:
            widget_time_range = time_range or widget.time_range
            widget_filters = {**(filters or {}), **widget.filters}
            
            try:
                widget_data = await self._get_widget_data(
                    widget,
                    user_id,
                    widget_time_range,
                    widget_filters
                )
                dashboard_data['widgets'][widget.widget_id] = widget_data
            except Exception as e:
                logger.error(f"Error loading widget {widget.widget_id}: {str(e)}")
                dashboard_data['widgets'][widget.widget_id] = {
                    'error': str(e),
                    'data': None
                }
        
        return dashboard_data
    
    async def _get_widget_data(
        self,
        widget: DashboardWidget,
        user_id: str,
        time_range: TimeRange,
        filters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Get data for a specific widget"""
        
        metric_type = widget.metric_type
        
        if metric_type == DashboardMetricType.SUCCESS_RATE:
            data = await self.metric_calculator.calculate_success_rate(user_id, time_range, filters)
        elif metric_type == DashboardMetricType.RESPONSE_RATE:
            data = await self.metric_calculator.calculate_response_rate(user_id, time_range, filters)
        elif metric_type == DashboardMetricType.CONVERSION_RATE:
            data = await self.metric_calculator.calculate_conversion_rates(user_id, time_range, filters)
        elif metric_type == DashboardMetricType.PLATFORM_PERFORMANCE:
            data = await self.metric_calculator.calculate_platform_performance(user_id, time_range, filters)
        elif metric_type == DashboardMetricType.TEMPLATE_EFFECTIVENESS:
            data = await self.metric_calculator.calculate_template_effectiveness(user_id, time_range, filters)
        else:
            data = {'message': f'Metric type {metric_type.value} not yet implemented'}
        
        return {
            'widget_config': widget.to_dict(),
            'data': data,
            'chart_type': widget.chart_type,
            'last_updated': datetime.utcnow().isoformat()
        }
    
    def create_custom_layout(
        self,
        layout_id: str,
        name: str,
        description: str,
        widgets: List[DashboardWidget],
        created_by: str
    ) -> DashboardLayout:
        """Create a custom dashboard layout"""
        
        layout = DashboardLayout(
            layout_id=layout_id,
            name=name,
            description=description,
            widgets=widgets,
            created_by=created_by
        )
        
        self.layouts[layout_id] = layout
        logger.info(f"Created custom layout: {layout_id}")
        
        return layout
    
    def get_available_layouts(self) -> List[Dict[str, Any]]:
        """Get list of available dashboard layouts"""
        
        return [layout.to_dict() for layout in self.layouts.values()]
    
    def clone_layout(self, source_layout_id: str, new_layout_id: str, new_name: str) -> DashboardLayout:
        """Clone an existing layout"""
        
        if source_layout_id not in self.layouts:
            raise ValueError(f"Source layout {source_layout_id} not found")
        
        source = self.layouts[source_layout_id]
        
        cloned_layout = DashboardLayout(
            layout_id=new_layout_id,
            name=new_name,
            description=f"Cloned from {source.name}",
            widgets=source.widgets.copy()
        )
        
        self.layouts[new_layout_id] = cloned_layout
        return cloned_layout


# Global dashboard manager
global_dashboard_manager = DashboardManager()