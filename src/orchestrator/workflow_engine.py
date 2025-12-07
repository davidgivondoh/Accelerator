"""
Workflow Orchestration Engine

Manages end-to-end application workflows, coordinates between different
pipeline components, and handles complex multi-step automation processes.
"""

import asyncio
import json
from typing import Dict, List, Optional, Any, Callable, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
import logging

from ..intelligence.user_profiles import global_profile_engine, InteractionType
from ..intelligence.success_prediction import global_success_predictor

# Stub classes for optional modules
class ApplicationType(Enum):
    """Stub ApplicationType enum"""
    JOB_APPLICATION = "job_application"
    GRANT_APPLICATION = "grant_application"
    SCHOLARSHIP_APPLICATION = "scholarship_application"
    INTERNSHIP_APPLICATION = "internship_application"
    CONFERENCE_SUBMISSION = "conference_submission"

class DocumentType(Enum):
    """Stub DocumentType enum"""
    COVER_LETTER = "cover_letter"
    RESUME_SUMMARY = "resume_summary"
    RESEARCH_PROPOSAL = "research_proposal"
    PROJECT_DESCRIPTION = "project_description"
    PERSONAL_STATEMENT = "personal_statement"
    MOTIVATION_LETTER = "motivation_letter"

class GenerationMode(Enum):
    """Stub GenerationMode enum"""
    STANDARD = "standard"
    PERSONALIZED = "personalized"

class SubmissionPlatform(Enum):
    """Stub SubmissionPlatform enum"""
    WEB_FORM = "web_form"
    EMAIL = "email"
    API = "api"

class SubmissionMethod(Enum):
    """Stub SubmissionMethod enum"""
    AUTOMATIC = "automatic"
    MANUAL = "manual"

class SubmissionStatus(Enum):
    """Stub SubmissionStatus enum"""
    PENDING = "pending"
    SUBMITTED = "submitted"
    FAILED = "failed"

# Optional imports for application generation and submission
# These modules may not exist yet - use stubs if missing
global_application_generator = None
GenerationRequest = None
ApplicationPackage = None
global_submission_engine = None
SubmissionConfig = None

# Note: application_generator and submission_engine modules are not yet implemented
# The stub classes defined above provide the necessary types for workflow operation

logger = logging.getLogger(__name__)


class WorkflowStage(Enum):
    """Stages in the application workflow"""
    DISCOVERY = "discovery"
    ANALYSIS = "analysis" 
    GENERATION = "generation"
    REVIEW = "review"
    SUBMISSION = "submission"
    TRACKING = "tracking"
    COMPLETED = "completed"
    FAILED = "failed"


class WorkflowStatus(Enum):
    """Status of workflow execution"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    PAUSED = "paused"
    WAITING_FOR_APPROVAL = "waiting_for_approval"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AutomationLevel(Enum):
    """Levels of automation for workflows"""
    FULLY_AUTOMATED = "fully_automated"      # No human intervention
    SEMI_AUTOMATED = "semi_automated"        # Human approval at key stages
    ASSISTED = "assisted"                    # Human guidance throughout
    MANUAL = "manual"                        # Human-driven with tool support


class WorkflowTrigger(Enum):
    """What triggers a workflow"""
    USER_REQUEST = "user_request"
    SCHEDULED = "scheduled"
    OPPORTUNITY_MATCH = "opportunity_match"
    DEADLINE_APPROACHING = "deadline_approaching"
    SUCCESS_PREDICTION_HIGH = "success_prediction_high"


@dataclass
class WorkflowConfig:
    """Configuration for workflow behavior"""
    automation_level: AutomationLevel = AutomationLevel.SEMI_AUTOMATED
    require_review: bool = True
    auto_submit: bool = False
    max_concurrent_applications: int = 3
    success_probability_threshold: float = 0.6
    priority_weights: Dict[str, float] = field(default_factory=lambda: {
        'deadline_urgency': 0.3,
        'success_probability': 0.4,
        'user_interest': 0.3
    })
    retry_failed_stages: bool = True
    max_retries_per_stage: int = 2
    notification_preferences: Dict[str, bool] = field(default_factory=lambda: {
        'stage_completion': True,
        'approval_needed': True,
        'errors': True,
        'final_results': True
    })


@dataclass
class WorkflowStep:
    """Individual step in a workflow"""
    step_id: str
    stage: WorkflowStage
    name: str
    description: str
    status: WorkflowStatus = WorkflowStatus.PENDING
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result_data: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None
    requires_approval: bool = False
    approved: bool = False
    retry_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'step_id': self.step_id,
            'stage': self.stage.value,
            'name': self.name,
            'description': self.description,
            'status': self.status.value,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'result_data': self.result_data,
            'error_message': self.error_message,
            'requires_approval': self.requires_approval,
            'approved': self.approved,
            'retry_count': self.retry_count,
            'duration_seconds': (
                (self.completed_at - self.started_at).total_seconds() 
                if self.started_at and self.completed_at else None
            )
        }


@dataclass
class WorkflowInstance:
    """Instance of a running workflow"""
    workflow_id: str
    user_id: str
    opportunity_id: str
    opportunity_data: Dict[str, Any]
    trigger: WorkflowTrigger
    config: WorkflowConfig
    steps: List[WorkflowStep] = field(default_factory=list)
    overall_status: WorkflowStatus = WorkflowStatus.PENDING
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    final_results: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'workflow_id': self.workflow_id,
            'user_id': self.user_id,
            'opportunity_id': self.opportunity_id,
            'opportunity_title': self.opportunity_data.get('title', 'Unknown'),
            'trigger': self.trigger.value,
            'overall_status': self.overall_status.value,
            'steps': [step.to_dict() for step in self.steps],
            'created_at': self.created_at.isoformat(),
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'total_steps': len(self.steps),
            'completed_steps': len([s for s in self.steps if s.status == WorkflowStatus.COMPLETED]),
            'failed_steps': len([s for s in self.steps if s.status == WorkflowStatus.FAILED]),
            'final_results': self.final_results,
            'duration_minutes': (
                (self.completed_at - self.started_at).total_seconds() / 60
                if self.started_at and self.completed_at else None
            )
        }


class WorkflowStepExecutor(ABC):
    """Abstract base class for step executors"""
    
    @abstractmethod
    async def execute(self, workflow: WorkflowInstance, step: WorkflowStep) -> bool:
        """Execute the workflow step. Returns True if successful."""
        pass
    
    @abstractmethod
    def get_stage(self) -> WorkflowStage:
        """Get the stage this executor handles"""
        pass


class DiscoveryStepExecutor(WorkflowStepExecutor):
    """Executes opportunity discovery and initial analysis"""
    
    def get_stage(self) -> WorkflowStage:
        return WorkflowStage.DISCOVERY
    
    async def execute(self, workflow: WorkflowInstance, step: WorkflowStep) -> bool:
        """Execute discovery step"""
        
        try:
            step.started_at = datetime.utcnow()
            step.status = WorkflowStatus.IN_PROGRESS
            
            # Track user interaction for discovery
            global_profile_engine.track_interaction(
                workflow.user_id,
                workflow.opportunity_id,
                InteractionType.VIEW,
                {'workflow_discovery': True, 'trigger': workflow.trigger.value}
            )
            
            # Simulate opportunity analysis
            await asyncio.sleep(1)
            
            step.result_data = {
                'opportunity_discovered': True,
                'initial_analysis_completed': True,
                'discovery_method': workflow.trigger.value
            }
            
            step.status = WorkflowStatus.COMPLETED
            step.completed_at = datetime.utcnow()
            
            logger.info(f"Discovery step completed for workflow {workflow.workflow_id}")
            return True
            
        except Exception as e:
            step.status = WorkflowStatus.FAILED
            step.error_message = str(e)
            logger.error(f"Discovery step failed for workflow {workflow.workflow_id}: {str(e)}")
            return False


class AnalysisStepExecutor(WorkflowStepExecutor):
    """Executes opportunity analysis and success prediction"""
    
    def get_stage(self) -> WorkflowStage:
        return WorkflowStage.ANALYSIS
    
    async def execute(self, workflow: WorkflowInstance, step: WorkflowStep) -> bool:
        """Execute analysis step"""
        
        try:
            step.started_at = datetime.utcnow()
            step.status = WorkflowStatus.IN_PROGRESS
            
            # Get success prediction
            prediction = global_success_predictor.generate_comprehensive_prediction(
                workflow.user_id, workflow.opportunity_data
            )
            
            # Check if opportunity meets success threshold
            success_threshold = workflow.config.success_probability_threshold
            meets_threshold = prediction.overall_score >= success_threshold
            
            step.result_data = {
                'success_prediction': prediction.to_dict(),
                'meets_threshold': meets_threshold,
                'success_threshold': success_threshold,
                'recommendation': (
                    'proceed' if meets_threshold else 'review_carefully'
                )
            }
            
            # If automation level is high and doesn't meet threshold, consider stopping
            if (workflow.config.automation_level == AutomationLevel.FULLY_AUTOMATED and 
                not meets_threshold):
                step.result_data['auto_stop_recommended'] = True
            
            step.status = WorkflowStatus.COMPLETED
            step.completed_at = datetime.utcnow()
            
            logger.info(f"Analysis step completed for workflow {workflow.workflow_id}: {prediction.overall_score:.2f}")
            return True
            
        except Exception as e:
            step.status = WorkflowStatus.FAILED
            step.error_message = str(e)
            logger.error(f"Analysis step failed for workflow {workflow.workflow_id}: {str(e)}")
            return False


class GenerationStepExecutor(WorkflowStepExecutor):
    """Executes application document generation"""
    
    def get_stage(self) -> WorkflowStage:
        return WorkflowStage.GENERATION
    
    async def execute(self, workflow: WorkflowInstance, step: WorkflowStep) -> bool:
        """Execute generation step"""
        
        try:
            step.started_at = datetime.utcnow()
            step.status = WorkflowStatus.IN_PROGRESS
            
            # Determine application type based on opportunity
            app_type = self._determine_application_type(workflow.opportunity_data)
            
            # Determine documents needed
            docs_needed = self._determine_documents_needed(app_type)
            
            # Create generation request
            generation_request = GenerationRequest(
                user_id=workflow.user_id,
                opportunity=workflow.opportunity_data,
                application_type=app_type,
                documents_needed=docs_needed,
                generation_mode=(
                    GenerationMode.FULLY_AUTOMATED 
                    if workflow.config.automation_level == AutomationLevel.FULLY_AUTOMATED
                    else GenerationMode.ASSISTED
                )
            )
            
            # Generate application package
            application_package = global_application_generator.generate_application_package(
                generation_request
            )
            
            step.result_data = {
                'application_package': application_package.to_dict(),
                'generation_successful': True,
                'documents_generated': len(application_package.documents),
                'overall_quality': application_package.overall_quality_score
            }
            
            # Store package for next step
            workflow.final_results['application_package'] = application_package
            
            step.status = WorkflowStatus.COMPLETED
            step.completed_at = datetime.utcnow()
            
            logger.info(f"Generation step completed for workflow {workflow.workflow_id}")
            return True
            
        except Exception as e:
            step.status = WorkflowStatus.FAILED
            step.error_message = str(e)
            logger.error(f"Generation step failed for workflow {workflow.workflow_id}: {str(e)}")
            return False
    
    def _determine_application_type(self, opportunity: Dict[str, Any]) -> ApplicationType:
        """Determine application type based on opportunity"""
        
        title = opportunity.get('title', '').lower()
        description = opportunity.get('description', '').lower()
        
        if any(word in title + description for word in ['grant', 'funding', 'research']):
            return ApplicationType.GRANT_APPLICATION
        elif any(word in title + description for word in ['scholarship', 'fellowship']):
            return ApplicationType.SCHOLARSHIP_APPLICATION
        elif any(word in title + description for word in ['intern', 'internship']):
            return ApplicationType.INTERNSHIP_APPLICATION
        elif any(word in title + description for word in ['conference', 'paper', 'submission']):
            return ApplicationType.CONFERENCE_SUBMISSION
        else:
            return ApplicationType.JOB_APPLICATION
    
    def _determine_documents_needed(self, app_type: ApplicationType) -> List[DocumentType]:
        """Determine which documents are needed for application type"""
        
        document_map = {
            ApplicationType.JOB_APPLICATION: [
                DocumentType.COVER_LETTER,
                DocumentType.RESUME_SUMMARY
            ],
            ApplicationType.GRANT_APPLICATION: [
                DocumentType.RESEARCH_PROPOSAL,
                DocumentType.PROJECT_DESCRIPTION
            ],
            ApplicationType.SCHOLARSHIP_APPLICATION: [
                DocumentType.PERSONAL_STATEMENT,
                DocumentType.MOTIVATION_LETTER
            ],
            ApplicationType.INTERNSHIP_APPLICATION: [
                DocumentType.COVER_LETTER,
                DocumentType.MOTIVATION_LETTER
            ],
            ApplicationType.CONFERENCE_SUBMISSION: [
                DocumentType.RESEARCH_PROPOSAL
            ]
        }
        
        return document_map.get(app_type, [DocumentType.COVER_LETTER])


class ReviewStepExecutor(WorkflowStepExecutor):
    """Executes review and approval process"""
    
    def get_stage(self) -> WorkflowStage:
        return WorkflowStage.REVIEW
    
    async def execute(self, workflow: WorkflowInstance, step: WorkflowStep) -> bool:
        """Execute review step"""
        
        try:
            step.started_at = datetime.utcnow()
            
            # Check if review is required
            if not workflow.config.require_review:
                step.status = WorkflowStatus.COMPLETED
                step.completed_at = datetime.utcnow()
                step.result_data = {'review_skipped': True, 'auto_approved': True}
                return True
            
            # For automation purposes, simulate review
            if workflow.config.automation_level == AutomationLevel.FULLY_AUTOMATED:
                step.status = WorkflowStatus.IN_PROGRESS
                await asyncio.sleep(2)  # Simulate review time
                
                # Auto-approve based on quality scores
                app_package = workflow.final_results.get('application_package')
                if app_package and app_package.overall_quality_score > 0.7:
                    step.approved = True
                    step.status = WorkflowStatus.COMPLETED
                    step.result_data = {'auto_approved': True, 'quality_check_passed': True}
                else:
                    step.status = WorkflowStatus.WAITING_FOR_APPROVAL
                    step.requires_approval = True
                    step.result_data = {'manual_review_required': True, 'quality_concerns': True}
            else:
                # Require manual approval
                step.status = WorkflowStatus.WAITING_FOR_APPROVAL
                step.requires_approval = True
                step.result_data = {'awaiting_user_approval': True}
            
            step.completed_at = datetime.utcnow()
            
            logger.info(f"Review step processed for workflow {workflow.workflow_id}")
            return step.status == WorkflowStatus.COMPLETED
            
        except Exception as e:
            step.status = WorkflowStatus.FAILED
            step.error_message = str(e)
            logger.error(f"Review step failed for workflow {workflow.workflow_id}: {str(e)}")
            return False


class SubmissionStepExecutor(WorkflowStepExecutor):
    """Executes application submission"""
    
    def get_stage(self) -> WorkflowStage:
        return WorkflowStage.SUBMISSION
    
    async def execute(self, workflow: WorkflowInstance, step: WorkflowStep) -> bool:
        """Execute submission step"""
        
        try:
            step.started_at = datetime.utcnow()
            step.status = WorkflowStatus.IN_PROGRESS
            
            # Get application package from previous steps
            app_package = workflow.final_results.get('application_package')
            if not app_package:
                raise ValueError("No application package available for submission")
            
            # Determine submission platform and method
            platform, method = self._determine_submission_method(workflow.opportunity_data)
            
            # Create submission config
            submission_config = SubmissionConfig(
                platform=platform,
                method=method,
                auto_submit=workflow.config.auto_submit,
                require_confirmation=(
                    not workflow.config.auto_submit or 
                    workflow.config.automation_level != AutomationLevel.FULLY_AUTOMATED
                ),
                custom_fields=self._extract_submission_fields(workflow.opportunity_data)
            )
            
            # Submit application
            submission_id = await global_submission_engine.submit_application(
                workflow.user_id,
                workflow.opportunity_data,
                app_package,
                submission_config
            )
            
            # Track submission interaction
            global_profile_engine.track_interaction(
                workflow.user_id,
                workflow.opportunity_id,
                InteractionType.APPLY,
                {
                    'workflow_submission': True,
                    'submission_id': submission_id,
                    'platform': platform.value
                }
            )
            
            step.result_data = {
                'submission_id': submission_id,
                'platform': platform.value,
                'method': method.value,
                'submission_initiated': True
            }
            
            step.status = WorkflowStatus.COMPLETED
            step.completed_at = datetime.utcnow()
            
            logger.info(f"Submission step completed for workflow {workflow.workflow_id}")
            return True
            
        except Exception as e:
            step.status = WorkflowStatus.FAILED
            step.error_message = str(e)
            logger.error(f"Submission step failed for workflow {workflow.workflow_id}: {str(e)}")
            return False
    
    def _determine_submission_method(self, opportunity: Dict[str, Any]) -> tuple:
        """Determine best submission platform and method"""
        
        # Check for specific submission instructions
        description = opportunity.get('description', '').lower()
        
        if 'email' in description or '@' in description:
            return SubmissionPlatform.EMAIL, SubmissionMethod.AUTOMATED
        elif 'linkedin' in description:
            return SubmissionPlatform.LINKEDIN, SubmissionMethod.SEMI_AUTOMATED
        elif opportunity.get('apply_url') or opportunity.get('application_url'):
            return SubmissionPlatform.COMPANY_WEBSITE, SubmissionMethod.MANUAL
        else:
            return SubmissionPlatform.MANUAL_REVIEW, SubmissionMethod.MANUAL
    
    def _extract_submission_fields(self, opportunity: Dict[str, Any]) -> Dict[str, Any]:
        """Extract submission-specific fields from opportunity"""
        
        fields = {}
        
        # Extract email if present
        description = opportunity.get('description', '')
        import re
        email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', description)
        if email_match:
            fields['recipient_email'] = email_match.group()
        
        # Extract URLs
        if opportunity.get('apply_url'):
            fields['application_url'] = opportunity['apply_url']
        elif opportunity.get('url'):
            fields['job_url'] = opportunity['url']
        
        # Generate email subject
        company = opportunity.get('company', 'Company')
        title = opportunity.get('title', 'Position')
        fields['subject'] = f"Application for {title} at {company}"
        
        return fields


class WorkflowOrchestrator:
    """Main orchestrator for managing application workflows"""
    
    def __init__(self):
        self.executors = {
            WorkflowStage.DISCOVERY: DiscoveryStepExecutor(),
            WorkflowStage.ANALYSIS: AnalysisStepExecutor(),
            WorkflowStage.GENERATION: GenerationStepExecutor(),
            WorkflowStage.REVIEW: ReviewStepExecutor(),
            WorkflowStage.SUBMISSION: SubmissionStepExecutor()
        }
        self.active_workflows: Dict[str, WorkflowInstance] = {}
        self.completed_workflows: Dict[str, WorkflowInstance] = {}
    
    async def create_workflow(
        self,
        user_id: str,
        opportunity: Dict[str, Any],
        trigger: WorkflowTrigger,
        config: WorkflowConfig = None
    ) -> str:
        """Create and start a new workflow"""
        
        if config is None:
            config = WorkflowConfig()
        
        # Generate workflow ID
        workflow_id = f"wf_{user_id}_{opportunity.get('id', 'unknown')}_{int(datetime.utcnow().timestamp())}"
        
        # Create workflow instance
        workflow = WorkflowInstance(
            workflow_id=workflow_id,
            user_id=user_id,
            opportunity_id=opportunity.get('id', ''),
            opportunity_data=opportunity,
            trigger=trigger,
            config=config
        )
        
        # Create workflow steps
        workflow.steps = self._create_workflow_steps(workflow)
        
        # Add to active workflows
        self.active_workflows[workflow_id] = workflow
        
        # Start workflow execution
        asyncio.create_task(self._execute_workflow(workflow))
        
        logger.info(f"Created workflow {workflow_id} for user {user_id}")
        return workflow_id
    
    def _create_workflow_steps(self, workflow: WorkflowInstance) -> List[WorkflowStep]:
        """Create the sequence of steps for a workflow"""
        
        steps = []
        
        # Discovery step
        steps.append(WorkflowStep(
            step_id=f"{workflow.workflow_id}_discovery",
            stage=WorkflowStage.DISCOVERY,
            name="Opportunity Discovery",
            description="Initial opportunity analysis and data collection"
        ))
        
        # Analysis step
        steps.append(WorkflowStep(
            step_id=f"{workflow.workflow_id}_analysis",
            stage=WorkflowStage.ANALYSIS,
            name="Success Analysis",
            description="Predict success probability and analyze fit"
        ))
        
        # Generation step
        steps.append(WorkflowStep(
            step_id=f"{workflow.workflow_id}_generation",
            stage=WorkflowStage.GENERATION,
            name="Document Generation",
            description="Generate application documents and materials"
        ))
        
        # Review step
        if workflow.config.require_review:
            steps.append(WorkflowStep(
                step_id=f"{workflow.workflow_id}_review",
                stage=WorkflowStage.REVIEW,
                name="Application Review",
                description="Review generated materials for quality and accuracy",
                requires_approval=workflow.config.automation_level != AutomationLevel.FULLY_AUTOMATED
            ))
        
        # Submission step
        steps.append(WorkflowStep(
            step_id=f"{workflow.workflow_id}_submission",
            stage=WorkflowStage.SUBMISSION,
            name="Application Submission",
            description="Submit application to target platform"
        ))
        
        return steps
    
    async def _execute_workflow(self, workflow: WorkflowInstance):
        """Execute a workflow end-to-end"""
        
        workflow.started_at = datetime.utcnow()
        workflow.overall_status = WorkflowStatus.IN_PROGRESS
        
        try:
            for step in workflow.steps:
                # Check if workflow was cancelled
                if workflow.overall_status == WorkflowStatus.CANCELLED:
                    break
                
                # Wait for approval if required
                if step.requires_approval and not step.approved:
                    step.status = WorkflowStatus.WAITING_FOR_APPROVAL
                    workflow.overall_status = WorkflowStatus.WAITING_FOR_APPROVAL
                    logger.info(f"Workflow {workflow.workflow_id} waiting for approval at step {step.name}")
                    
                    # Wait for approval (in production, this would be event-driven)
                    while not step.approved and workflow.overall_status != WorkflowStatus.CANCELLED:
                        await asyncio.sleep(10)  # Check every 10 seconds
                    
                    if workflow.overall_status == WorkflowStatus.CANCELLED:
                        break
                
                # Execute step
                executor = self.executors.get(step.stage)
                if not executor:
                    step.status = WorkflowStatus.FAILED
                    step.error_message = f"No executor found for stage {step.stage.value}"
                    continue
                
                # Retry logic
                max_retries = workflow.config.max_retries_per_stage
                for retry in range(max_retries + 1):
                    step.retry_count = retry
                    
                    success = await executor.execute(workflow, step)
                    
                    if success:
                        break
                    elif retry < max_retries and workflow.config.retry_failed_stages:
                        logger.info(f"Retrying step {step.name} (attempt {retry + 2})")
                        await asyncio.sleep(30)  # Wait before retry
                    else:
                        logger.error(f"Step {step.name} failed after {retry + 1} attempts")
                        break
                
                # Check if step failed
                if step.status == WorkflowStatus.FAILED:
                    workflow.overall_status = WorkflowStatus.FAILED
                    logger.error(f"Workflow {workflow.workflow_id} failed at step {step.name}")
                    break
            
            # Check final status
            if workflow.overall_status != WorkflowStatus.FAILED:
                completed_steps = [s for s in workflow.steps if s.status == WorkflowStatus.COMPLETED]
                if len(completed_steps) == len(workflow.steps):
                    workflow.overall_status = WorkflowStatus.COMPLETED
                    logger.info(f"Workflow {workflow.workflow_id} completed successfully")
        
        except Exception as e:
            workflow.overall_status = WorkflowStatus.FAILED
            logger.error(f"Workflow {workflow.workflow_id} failed with exception: {str(e)}")
        
        finally:
            workflow.completed_at = datetime.utcnow()
            
            # Move to completed workflows
            self.completed_workflows[workflow.workflow_id] = workflow
            if workflow.workflow_id in self.active_workflows:
                del self.active_workflows[workflow.workflow_id]
    
    def approve_step(self, workflow_id: str, step_id: str) -> bool:
        """Approve a workflow step that requires approval"""
        
        workflow = self.active_workflows.get(workflow_id)
        if not workflow:
            return False
        
        for step in workflow.steps:
            if step.step_id == step_id and step.requires_approval:
                step.approved = True
                step.status = WorkflowStatus.COMPLETED
                
                # Resume workflow if it was waiting
                if workflow.overall_status == WorkflowStatus.WAITING_FOR_APPROVAL:
                    workflow.overall_status = WorkflowStatus.IN_PROGRESS
                
                logger.info(f"Approved step {step_id} in workflow {workflow_id}")
                return True
        
        return False
    
    def cancel_workflow(self, workflow_id: str) -> bool:
        """Cancel an active workflow"""
        
        workflow = self.active_workflows.get(workflow_id)
        if workflow:
            workflow.overall_status = WorkflowStatus.CANCELLED
            workflow.completed_at = datetime.utcnow()
            logger.info(f"Cancelled workflow {workflow_id}")
            return True
        
        return False
    
    def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific workflow"""
        
        # Check active workflows
        if workflow_id in self.active_workflows:
            return self.active_workflows[workflow_id].to_dict()
        
        # Check completed workflows
        if workflow_id in self.completed_workflows:
            return self.completed_workflows[workflow_id].to_dict()
        
        return None
    
    def get_user_workflows(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all workflows for a specific user"""
        
        workflows = []
        
        # Add active workflows
        for workflow in self.active_workflows.values():
            if workflow.user_id == user_id:
                workflows.append(workflow.to_dict())
        
        # Add completed workflows
        for workflow in self.completed_workflows.values():
            if workflow.user_id == user_id:
                workflows.append(workflow.to_dict())
        
        # Sort by creation time (newest first)
        workflows.sort(key=lambda x: x['created_at'], reverse=True)
        
        return workflows
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status"""
        
        total_active = len(self.active_workflows)
        total_completed = len(self.completed_workflows)
        
        # Count workflows by status
        status_counts = {}
        for workflow in self.active_workflows.values():
            status = workflow.overall_status.value
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Count workflows by stage
        stage_counts = {}
        for workflow in self.active_workflows.values():
            current_step = next(
                (step for step in workflow.steps if step.status == WorkflowStatus.IN_PROGRESS),
                None
            )
            if current_step:
                stage = current_step.stage.value
                stage_counts[stage] = stage_counts.get(stage, 0) + 1
        
        return {
            'total_active_workflows': total_active,
            'total_completed_workflows': total_completed,
            'status_distribution': status_counts,
            'current_stage_distribution': stage_counts,
            'system_health': 'healthy' if total_active < 100 else 'high_load'
        }


# Global workflow orchestrator
global_workflow_orchestrator = WorkflowOrchestrator()