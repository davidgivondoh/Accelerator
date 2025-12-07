"""
Application Status Tracking System

Comprehensive tracking and monitoring of application lifecycle,
from submission through final outcome, with intelligent status updates
and automated follow-up management.
"""

import asyncio
import json
from typing import Dict, List, Optional, Any, Tuple, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import logging

from ..models.application import ApplicationRecord
from ..intelligence.user_profiles import global_profile_engine, InteractionType

logger = logging.getLogger(__name__)


class ApplicationStage(Enum):
    """Stages in the application process"""
    DRAFT = "draft"                    # Application being prepared
    SUBMITTED = "submitted"            # Application submitted
    UNDER_REVIEW = "under_review"      # Application being reviewed
    SCREENING = "screening"            # Initial screening phase
    FIRST_INTERVIEW = "first_interview"  # First round interview
    TECHNICAL_INTERVIEW = "technical_interview"  # Technical assessment
    FINAL_INTERVIEW = "final_interview"  # Final interview round
    REFERENCE_CHECK = "reference_check"  # Reference verification
    OFFER_EXTENDED = "offer_extended"   # Job offer made
    OFFER_ACCEPTED = "offer_accepted"   # Offer accepted
    OFFER_DECLINED = "offer_declined"   # Offer declined
    REJECTED = "rejected"              # Application rejected
    WITHDRAWN = "withdrawn"            # Application withdrawn
    EXPIRED = "expired"                # Application expired


class ApplicationPriority(Enum):
    """Priority levels for applications"""
    HIGH = "high"        # Dream opportunity
    MEDIUM = "medium"    # Good fit
    LOW = "low"         # Backup option


class FollowUpType(Enum):
    """Types of follow-up actions"""
    THANK_YOU = "thank_you"
    STATUS_CHECK = "status_check"
    ADDITIONAL_INFO = "additional_info"
    INTERVIEW_CONFIRMATION = "interview_confirmation"
    OFFER_RESPONSE = "offer_response"
    WITHDRAWAL = "withdrawal"


@dataclass
class ApplicationEvent:
    """Individual event in application timeline"""
    event_id: str
    application_id: str
    event_type: str
    stage: ApplicationStage
    timestamp: datetime
    description: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    source: str = "system"  # system, user, external
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'event_id': self.event_id,
            'application_id': self.application_id,
            'event_type': self.event_type,
            'stage': self.stage.value,
            'timestamp': self.timestamp.isoformat(),
            'description': self.description,
            'metadata': self.metadata,
            'source': self.source
        }


@dataclass
class FollowUpAction:
    """Follow-up action to be taken"""
    action_id: str
    application_id: str
    follow_up_type: FollowUpType
    scheduled_date: datetime
    description: str
    completed: bool = False
    completed_date: Optional[datetime] = None
    notes: str = ""
    auto_generated: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'action_id': self.action_id,
            'application_id': self.application_id,
            'follow_up_type': self.follow_up_type.value,
            'scheduled_date': self.scheduled_date.isoformat(),
            'description': self.description,
            'completed': self.completed,
            'completed_date': self.completed_date.isoformat() if self.completed_date else None,
            'notes': self.notes,
            'auto_generated': self.auto_generated,
            'days_until_due': (self.scheduled_date - datetime.utcnow()).days if not self.completed else None
        }


@dataclass
class ApplicationMetrics:
    """Metrics for application performance"""
    application_id: str
    time_in_current_stage: timedelta
    total_process_time: timedelta
    response_rate: float  # How quickly they respond
    interview_success_rate: float
    estimated_decision_date: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'application_id': self.application_id,
            'time_in_current_stage_days': self.time_in_current_stage.days,
            'total_process_time_days': self.total_process_time.days,
            'response_rate': self.response_rate,
            'interview_success_rate': self.interview_success_rate,
            'estimated_decision_date': self.estimated_decision_date.isoformat() if self.estimated_decision_date else None
        }


@dataclass
class TrackedApplication:
    """Comprehensive tracked application with full lifecycle data"""
    application_id: str
    user_id: str
    opportunity_id: str
    opportunity_title: str
    company_name: str
    current_stage: ApplicationStage
    priority: ApplicationPriority
    submitted_date: datetime
    last_updated: datetime
    events: List[ApplicationEvent] = field(default_factory=list)
    follow_up_actions: List[FollowUpAction] = field(default_factory=list)
    metrics: Optional[ApplicationMetrics] = None
    notes: str = ""
    tags: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'application_id': self.application_id,
            'user_id': self.user_id,
            'opportunity_id': self.opportunity_id,
            'opportunity_title': self.opportunity_title,
            'company_name': self.company_name,
            'current_stage': self.current_stage.value,
            'priority': self.priority.value,
            'submitted_date': self.submitted_date.isoformat(),
            'last_updated': self.last_updated.isoformat(),
            'events': [event.to_dict() for event in self.events],
            'follow_up_actions': [action.to_dict() for action in self.follow_up_actions],
            'metrics': self.metrics.to_dict() if self.metrics else None,
            'notes': self.notes,
            'tags': self.tags,
            'days_since_submission': (datetime.utcnow() - self.submitted_date).days,
            'pending_follow_ups': len([a for a in self.follow_up_actions if not a.completed])
        }


class StageTransitionRules:
    """Rules for automatic stage transitions and follow-up scheduling"""
    
    def __init__(self):
        self.transition_rules = self._load_transition_rules()
        self.follow_up_rules = self._load_follow_up_rules()
    
    def _load_transition_rules(self) -> Dict[str, Dict]:
        """Load rules for automatic stage transitions"""
        return {
            ApplicationStage.SUBMITTED.value: {
                'auto_transition_after_days': 7,
                'next_stage': ApplicationStage.UNDER_REVIEW.value,
                'conditions': ['no_response_received']
            },
            ApplicationStage.UNDER_REVIEW.value: {
                'auto_transition_after_days': 14,
                'next_stage': ApplicationStage.SCREENING.value,
                'conditions': ['typical_review_period']
            },
            ApplicationStage.FIRST_INTERVIEW.value: {
                'auto_transition_after_days': 3,
                'next_stage': ApplicationStage.TECHNICAL_INTERVIEW.value,
                'conditions': ['interview_completed', 'positive_feedback']
            }
        }
    
    def _load_follow_up_rules(self) -> Dict[str, List[Dict]]:
        """Load rules for automatic follow-up scheduling"""
        return {
            ApplicationStage.SUBMITTED.value: [
                {
                    'type': FollowUpType.STATUS_CHECK.value,
                    'days_after': 7,
                    'description': 'Follow up on application status'
                }
            ],
            ApplicationStage.UNDER_REVIEW.value: [
                {
                    'type': FollowUpType.STATUS_CHECK.value,
                    'days_after': 14,
                    'description': 'Check on review progress'
                }
            ],
            ApplicationStage.FIRST_INTERVIEW.value: [
                {
                    'type': FollowUpType.THANK_YOU.value,
                    'days_after': 1,
                    'description': 'Send thank you note after interview'
                },
                {
                    'type': FollowUpType.STATUS_CHECK.value,
                    'days_after': 7,
                    'description': 'Follow up on interview outcome'
                }
            ],
            ApplicationStage.OFFER_EXTENDED.value: [
                {
                    'type': FollowUpType.OFFER_RESPONSE.value,
                    'days_after': 3,
                    'description': 'Respond to job offer'
                }
            ]
        }
    
    def should_auto_transition(self, application: TrackedApplication) -> Tuple[bool, Optional[ApplicationStage]]:
        """Check if application should automatically transition to next stage"""
        
        current_stage = application.current_stage.value
        rules = self.transition_rules.get(current_stage)
        
        if not rules:
            return False, None
        
        # Check time condition
        days_in_stage = (datetime.utcnow() - application.last_updated).days
        if days_in_stage >= rules['auto_transition_after_days']:
            next_stage = ApplicationStage(rules['next_stage'])
            return True, next_stage
        
        return False, None
    
    def get_follow_up_actions(self, application: TrackedApplication) -> List[FollowUpAction]:
        """Generate follow-up actions for current stage"""
        
        current_stage = application.current_stage.value
        rules = self.follow_up_rules.get(current_stage, [])
        
        actions = []
        for rule in rules:
            # Check if this follow-up already exists
            existing = any(
                action.follow_up_type.value == rule['type'] and not action.completed
                for action in application.follow_up_actions
            )
            
            if not existing:
                scheduled_date = application.last_updated + timedelta(days=rule['days_after'])
                
                action = FollowUpAction(
                    action_id=f"{application.application_id}_{rule['type']}_{int(datetime.utcnow().timestamp())}",
                    application_id=application.application_id,
                    follow_up_type=FollowUpType(rule['type']),
                    scheduled_date=scheduled_date,
                    description=rule['description'],
                    auto_generated=True
                )
                actions.append(action)
        
        return actions


class ApplicationStatusTracker:
    """Main application status tracking system"""
    
    def __init__(self):
        self.tracked_applications: Dict[str, TrackedApplication] = {}
        self.transition_rules = StageTransitionRules()
        self.event_listeners: List[Callable] = []
        
        # Start background tasks
        asyncio.create_task(self._background_monitor())
    
    def create_application_tracking(
        self,
        application_id: str,
        user_id: str,
        opportunity: Dict[str, Any],
        priority: ApplicationPriority = ApplicationPriority.MEDIUM
    ) -> TrackedApplication:
        """Create new application tracking"""
        
        tracked_app = TrackedApplication(
            application_id=application_id,
            user_id=user_id,
            opportunity_id=opportunity.get('id', ''),
            opportunity_title=opportunity.get('title', 'Unknown'),
            company_name=opportunity.get('company', 'Unknown Company'),
            current_stage=ApplicationStage.SUBMITTED,
            priority=priority,
            submitted_date=datetime.utcnow(),
            last_updated=datetime.utcnow()
        )
        
        # Add initial submission event
        self.add_event(
            tracked_app,
            'application_submitted',
            'Application submitted successfully',
            {'submission_method': 'automated'}
        )
        
        # Schedule initial follow-up actions
        follow_ups = self.transition_rules.get_follow_up_actions(tracked_app)
        tracked_app.follow_up_actions.extend(follow_ups)
        
        # Calculate initial metrics
        tracked_app.metrics = self._calculate_metrics(tracked_app)
        
        self.tracked_applications[application_id] = tracked_app
        
        # Track interaction
        global_profile_engine.track_interaction(
            user_id,
            opportunity.get('id', ''),
            InteractionType.APPLY,
            {'application_tracking_started': True}
        )
        
        logger.info(f"Started tracking application {application_id}")
        return tracked_app
    
    def update_application_stage(
        self,
        application_id: str,
        new_stage: ApplicationStage,
        description: str = "",
        metadata: Dict[str, Any] = None
    ) -> bool:
        """Update application to new stage"""
        
        if application_id not in self.tracked_applications:
            return False
        
        app = self.tracked_applications[application_id]
        old_stage = app.current_stage
        
        # Update stage
        app.current_stage = new_stage
        app.last_updated = datetime.utcnow()
        
        # Add stage transition event
        self.add_event(
            app,
            'stage_transition',
            description or f"Moved from {old_stage.value} to {new_stage.value}",
            metadata or {'old_stage': old_stage.value, 'new_stage': new_stage.value}
        )
        
        # Generate new follow-up actions for new stage
        new_follow_ups = self.transition_rules.get_follow_up_actions(app)
        app.follow_up_actions.extend(new_follow_ups)
        
        # Update metrics
        app.metrics = self._calculate_metrics(app)
        
        # Notify listeners
        self._notify_stage_change(app, old_stage, new_stage)
        
        logger.info(f"Updated application {application_id} to stage {new_stage.value}")
        return True
    
    def add_event(
        self,
        application: TrackedApplication,
        event_type: str,
        description: str,
        metadata: Dict[str, Any] = None,
        source: str = "system"
    ):
        """Add event to application timeline"""
        
        event = ApplicationEvent(
            event_id=f"{application.application_id}_{event_type}_{int(datetime.utcnow().timestamp())}",
            application_id=application.application_id,
            event_type=event_type,
            stage=application.current_stage,
            timestamp=datetime.utcnow(),
            description=description,
            metadata=metadata or {},
            source=source
        )
        
        application.events.append(event)
        application.last_updated = datetime.utcnow()
        
        # Update metrics
        application.metrics = self._calculate_metrics(application)
    
    def complete_follow_up(self, application_id: str, action_id: str, notes: str = "") -> bool:
        """Mark follow-up action as completed"""
        
        if application_id not in self.tracked_applications:
            return False
        
        app = self.tracked_applications[application_id]
        
        for action in app.follow_up_actions:
            if action.action_id == action_id:
                action.completed = True
                action.completed_date = datetime.utcnow()
                action.notes = notes
                
                # Add completion event
                self.add_event(
                    app,
                    'follow_up_completed',
                    f"Completed follow-up: {action.description}",
                    {'follow_up_type': action.follow_up_type.value}
                )
                
                logger.info(f"Completed follow-up {action_id} for application {application_id}")
                return True
        
        return False
    
    def get_application_status(self, application_id: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive status of an application"""
        
        if application_id not in self.tracked_applications:
            return None
        
        return self.tracked_applications[application_id].to_dict()
    
    def get_user_applications(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all applications for a user"""
        
        user_apps = [
            app for app in self.tracked_applications.values()
            if app.user_id == user_id
        ]
        
        # Sort by last updated (most recent first)
        user_apps.sort(key=lambda x: x.last_updated, reverse=True)
        
        return [app.to_dict() for app in user_apps]
    
    def get_pending_follow_ups(self, user_id: str = None) -> List[Dict[str, Any]]:
        """Get pending follow-up actions"""
        
        pending = []
        
        for app in self.tracked_applications.values():
            if user_id and app.user_id != user_id:
                continue
            
            for action in app.follow_up_actions:
                if not action.completed and action.scheduled_date <= datetime.utcnow():
                    pending.append({
                        'action': action.to_dict(),
                        'application': {
                            'id': app.application_id,
                            'title': app.opportunity_title,
                            'company': app.company_name,
                            'stage': app.current_stage.value
                        }
                    })
        
        # Sort by scheduled date
        pending.sort(key=lambda x: x['action']['scheduled_date'])
        
        return pending
    
    def get_application_statistics(self, user_id: str) -> Dict[str, Any]:
        """Get application statistics for a user"""
        
        user_apps = [
            app for app in self.tracked_applications.values()
            if app.user_id == user_id
        ]
        
        if not user_apps:
            return {
                'total_applications': 0,
                'stage_distribution': {},
                'average_process_time': 0,
                'success_rate': 0.0
            }
        
        # Stage distribution
        stage_counts = {}
        for app in user_apps:
            stage = app.current_stage.value
            stage_counts[stage] = stage_counts.get(stage, 0) + 1
        
        # Success metrics
        successful_stages = {
            ApplicationStage.OFFER_ACCEPTED.value,
            ApplicationStage.OFFER_EXTENDED.value
        }
        successful_apps = [app for app in user_apps if app.current_stage.value in successful_stages]
        success_rate = len(successful_apps) / len(user_apps) if user_apps else 0.0
        
        # Average process time
        completed_apps = [
            app for app in user_apps 
            if app.current_stage in [ApplicationStage.OFFER_ACCEPTED, ApplicationStage.REJECTED, ApplicationStage.WITHDRAWN]
        ]
        
        if completed_apps:
            avg_process_time = sum(
                (datetime.utcnow() - app.submitted_date).days 
                for app in completed_apps
            ) / len(completed_apps)
        else:
            avg_process_time = 0
        
        return {
            'total_applications': len(user_apps),
            'active_applications': len([app for app in user_apps if app.current_stage not in [ApplicationStage.REJECTED, ApplicationStage.WITHDRAWN, ApplicationStage.OFFER_ACCEPTED]]),
            'stage_distribution': stage_counts,
            'average_process_time_days': avg_process_time,
            'success_rate': success_rate,
            'pending_follow_ups': len(self.get_pending_follow_ups(user_id))
        }
    
    def _calculate_metrics(self, application: TrackedApplication) -> ApplicationMetrics:
        """Calculate metrics for application"""
        
        now = datetime.utcnow()
        
        # Time in current stage
        stage_events = [e for e in application.events if e.event_type == 'stage_transition']
        if stage_events:
            last_transition = max(stage_events, key=lambda x: x.timestamp)
            time_in_stage = now - last_transition.timestamp
        else:
            time_in_stage = now - application.submitted_date
        
        # Total process time
        total_time = now - application.submitted_date
        
        # Response rate (simplified)
        response_events = [e for e in application.events if 'response' in e.event_type.lower()]
        response_rate = min(len(response_events) / max(total_time.days, 1), 1.0)
        
        # Interview success rate (placeholder)
        interview_events = [e for e in application.events if 'interview' in e.event_type.lower()]
        interview_success_rate = 0.5 if interview_events else 0.0
        
        # Estimated decision date
        estimated_decision = None
        if application.current_stage in [ApplicationStage.FINAL_INTERVIEW, ApplicationStage.REFERENCE_CHECK]:
            estimated_decision = now + timedelta(days=7)
        elif application.current_stage == ApplicationStage.OFFER_EXTENDED:
            estimated_decision = now + timedelta(days=3)
        
        return ApplicationMetrics(
            application_id=application.application_id,
            time_in_current_stage=time_in_stage,
            total_process_time=total_time,
            response_rate=response_rate,
            interview_success_rate=interview_success_rate,
            estimated_decision_date=estimated_decision
        )
    
    async def _background_monitor(self):
        """Background task to monitor applications and trigger updates"""
        
        while True:
            try:
                await self._check_for_auto_transitions()
                await self._check_for_stale_applications()
                await asyncio.sleep(3600)  # Check every hour
            except Exception as e:
                logger.error(f"Background monitor error: {str(e)}")
                await asyncio.sleep(300)  # Retry in 5 minutes on error
    
    async def _check_for_auto_transitions(self):
        """Check for applications that should auto-transition"""
        
        for app in self.tracked_applications.values():
            should_transition, next_stage = self.transition_rules.should_auto_transition(app)
            
            if should_transition:
                self.update_application_stage(
                    app.application_id,
                    next_stage,
                    f"Auto-transitioned to {next_stage.value} after timeout",
                    {'auto_transition': True}
                )
    
    async def _check_for_stale_applications(self):
        """Check for applications with no recent activity"""
        
        stale_threshold = timedelta(days=30)
        now = datetime.utcnow()
        
        for app in self.tracked_applications.values():
            if (now - app.last_updated) > stale_threshold:
                if app.current_stage not in [ApplicationStage.REJECTED, ApplicationStage.WITHDRAWN, ApplicationStage.OFFER_ACCEPTED]:
                    # Mark as potentially expired
                    self.add_event(
                        app,
                        'stale_application_detected',
                        'Application has been inactive for 30+ days',
                        {'stale_threshold_days': 30}
                    )
    
    def _notify_stage_change(self, application: TrackedApplication, old_stage: ApplicationStage, new_stage: ApplicationStage):
        """Notify listeners about stage changes"""
        
        for listener in self.event_listeners:
            try:
                listener(application, old_stage, new_stage)
            except Exception as e:
                logger.error(f"Event listener error: {str(e)}")
    
    def add_event_listener(self, listener: Callable):
        """Add event listener for stage changes"""
        self.event_listeners.append(listener)


# Global application status tracker
global_application_tracker = ApplicationStatusTracker()