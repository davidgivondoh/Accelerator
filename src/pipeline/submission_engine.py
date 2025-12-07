"""
Smart Application Submission System

Handles automated submission of applications across different platforms,
manages submission workflows, and tracks application status.
"""

import asyncio
import json
import hashlib
from typing import Dict, List, Optional, Any, Tuple, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
import logging

from ..models.application import ApplicationRecord
from ..intelligence.user_profiles import global_profile_engine
from .application_generator import ApplicationPackage, DocumentType

logger = logging.getLogger(__name__)


class SubmissionPlatform(Enum):
    """Supported submission platforms"""
    EMAIL = "email"
    LINKEDIN = "linkedin"
    INDEED = "indeed"
    GLASSDOOR = "glassdoor"
    COMPANY_WEBSITE = "company_website"
    UNIVERSITY_PORTAL = "university_portal"
    GRANT_PORTAL = "grant_portal"
    CUSTOM_API = "custom_api"
    MANUAL_REVIEW = "manual_review"


class SubmissionStatus(Enum):
    """Status of submission attempts"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUBMITTED = "submitted"
    FAILED = "failed"
    REQUIRES_MANUAL = "requires_manual"
    CANCELLED = "cancelled"


class SubmissionMethod(Enum):
    """Methods for submission"""
    AUTOMATED = "automated"      # Fully automated via API/scraping
    SEMI_AUTOMATED = "semi_automated"  # Automated with human confirmation
    MANUAL = "manual"           # Requires human intervention
    SCHEDULED = "scheduled"     # Scheduled for later submission


@dataclass
class SubmissionConfig:
    """Configuration for submission behavior"""
    platform: SubmissionPlatform
    method: SubmissionMethod
    auto_submit: bool = False
    require_confirmation: bool = True
    max_retries: int = 3
    retry_delay_minutes: int = 30
    custom_fields: Dict[str, Any] = field(default_factory=dict)
    submission_deadline: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'platform': self.platform.value,
            'method': self.method.value,
            'auto_submit': self.auto_submit,
            'require_confirmation': self.require_confirmation,
            'max_retries': self.max_retries,
            'retry_delay_minutes': self.retry_delay_minutes,
            'custom_fields': self.custom_fields,
            'submission_deadline': self.submission_deadline.isoformat() if self.submission_deadline else None
        }


@dataclass
class SubmissionAttempt:
    """Record of a submission attempt"""
    attempt_id: str
    timestamp: datetime
    platform: SubmissionPlatform
    method: SubmissionMethod
    status: SubmissionStatus
    response_data: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None
    submission_url: Optional[str] = None
    confirmation_code: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'attempt_id': self.attempt_id,
            'timestamp': self.timestamp.isoformat(),
            'platform': self.platform.value,
            'method': self.method.value,
            'status': self.status.value,
            'response_data': self.response_data,
            'error_message': self.error_message,
            'submission_url': self.submission_url,
            'confirmation_code': self.confirmation_code
        }


@dataclass
class SubmissionRequest:
    """Request to submit an application package"""
    user_id: str
    opportunity_id: str
    application_package: ApplicationPackage
    submission_config: SubmissionConfig
    priority: int = 1  # 1 = high, 2 = medium, 3 = low
    notes: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def generate_id(self) -> str:
        """Generate unique ID for submission request"""
        content = f"{self.user_id}{self.opportunity_id}{self.created_at.isoformat()}"
        return hashlib.md5(content.encode()).hexdigest()[:16]


@dataclass
class SubmissionResult:
    """Result of a submission operation"""
    submission_id: str
    request: SubmissionRequest
    attempts: List[SubmissionAttempt]
    final_status: SubmissionStatus
    success: bool
    submission_url: Optional[str] = None
    confirmation_details: Dict[str, Any] = field(default_factory=dict)
    next_steps: List[str] = field(default_factory=list)
    estimated_response_time: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'submission_id': self.submission_id,
            'opportunity_id': self.request.opportunity_id,
            'attempts': [attempt.to_dict() for attempt in self.attempts],
            'final_status': self.final_status.value,
            'success': self.success,
            'submission_url': self.submission_url,
            'confirmation_details': self.confirmation_details,
            'next_steps': self.next_steps,
            'estimated_response_time': self.estimated_response_time,
            'total_attempts': len(self.attempts)
        }


class SubmissionHandler(ABC):
    """Abstract base class for platform-specific submission handlers"""
    
    @abstractmethod
    async def can_handle(self, platform: SubmissionPlatform) -> bool:
        """Check if handler can handle the given platform"""
        pass
    
    @abstractmethod
    async def submit_application(
        self, 
        request: SubmissionRequest
    ) -> SubmissionAttempt:
        """Submit application to the platform"""
        pass
    
    @abstractmethod
    async def validate_submission_data(
        self, 
        application_package: ApplicationPackage,
        config: SubmissionConfig
    ) -> Tuple[bool, List[str]]:
        """Validate that submission data is complete and correct"""
        pass


class EmailSubmissionHandler(SubmissionHandler):
    """Handles email-based application submissions"""
    
    async def can_handle(self, platform: SubmissionPlatform) -> bool:
        return platform == SubmissionPlatform.EMAIL
    
    async def validate_submission_data(
        self, 
        application_package: ApplicationPackage,
        config: SubmissionConfig
    ) -> Tuple[bool, List[str]]:
        """Validate email submission data"""
        
        errors = []
        
        # Check for required email fields
        custom_fields = config.custom_fields
        
        if not custom_fields.get('recipient_email'):
            errors.append("Recipient email address is required")
        
        if not custom_fields.get('subject'):
            errors.append("Email subject is required")
        
        # Check for email body content
        if not application_package.documents:
            errors.append("No documents to send")
        
        # Validate email format
        recipient = custom_fields.get('recipient_email', '')
        if recipient and '@' not in recipient:
            errors.append("Invalid recipient email format")
        
        return len(errors) == 0, errors
    
    async def submit_application(self, request: SubmissionRequest) -> SubmissionAttempt:
        """Submit application via email"""
        
        attempt_id = self._generate_attempt_id()
        
        try:
            # Validate submission data
            is_valid, validation_errors = await self.validate_submission_data(
                request.application_package, request.submission_config
            )
            
            if not is_valid:
                return SubmissionAttempt(
                    attempt_id=attempt_id,
                    timestamp=datetime.utcnow(),
                    platform=SubmissionPlatform.EMAIL,
                    method=request.submission_config.method,
                    status=SubmissionStatus.FAILED,
                    error_message=f"Validation failed: {'; '.join(validation_errors)}"
                )
            
            # Prepare email content
            email_data = self._prepare_email_data(request)
            
            # In a real implementation, this would use an email service
            # For now, we'll simulate the email submission
            await self._simulate_email_submission(email_data)
            
            return SubmissionAttempt(
                attempt_id=attempt_id,
                timestamp=datetime.utcnow(),
                platform=SubmissionPlatform.EMAIL,
                method=request.submission_config.method,
                status=SubmissionStatus.SUBMITTED,
                response_data={'email_sent': True, 'message_id': f"email_{attempt_id}"},
                confirmation_code=f"EMAIL_{attempt_id[:8].upper()}"
            )
            
        except Exception as e:
            logger.error(f"Email submission failed: {str(e)}")
            return SubmissionAttempt(
                attempt_id=attempt_id,
                timestamp=datetime.utcnow(),
                platform=SubmissionPlatform.EMAIL,
                method=request.submission_config.method,
                status=SubmissionStatus.FAILED,
                error_message=str(e)
            )
    
    def _prepare_email_data(self, request: SubmissionRequest) -> Dict[str, Any]:
        """Prepare email data for submission"""
        
        config = request.submission_config
        package = request.application_package
        
        # Build email body
        body_parts = []
        
        # Add introduction
        body_parts.append("Dear Hiring Manager,")
        body_parts.append("")
        body_parts.append("Please find attached my application materials for the position.")
        body_parts.append("")
        
        # Add document list
        body_parts.append("Attached documents:")
        for doc in package.documents:
            body_parts.append(f"- {doc.title}")
        
        body_parts.append("")
        body_parts.append("Thank you for your consideration.")
        body_parts.append("")
        body_parts.append("Best regards")
        
        return {
            'to': config.custom_fields.get('recipient_email'),
            'subject': config.custom_fields.get('subject', 'Application Submission'),
            'body': '\n'.join(body_parts),
            'attachments': [
                {'filename': f"{doc.title}.txt", 'content': doc.content}
                for doc in package.documents
            ]
        }
    
    async def _simulate_email_submission(self, email_data: Dict[str, Any]):
        """Simulate email submission (replace with real email service)"""
        
        # Simulate processing time
        await asyncio.sleep(1)
        
        # In production, this would integrate with:
        # - SendGrid, Mailgun, SES, etc.
        logger.info(f"Email sent to {email_data['to']} with subject '{email_data['subject']}'")
    
    def _generate_attempt_id(self) -> str:
        """Generate unique attempt ID"""
        return hashlib.md5(f"{datetime.utcnow().isoformat()}".encode()).hexdigest()[:16]


class LinkedInSubmissionHandler(SubmissionHandler):
    """Handles LinkedIn-based application submissions"""
    
    async def can_handle(self, platform: SubmissionPlatform) -> bool:
        return platform == SubmissionPlatform.LINKEDIN
    
    async def validate_submission_data(
        self, 
        application_package: ApplicationPackage,
        config: SubmissionConfig
    ) -> Tuple[bool, List[str]]:
        """Validate LinkedIn submission data"""
        
        errors = []
        
        # LinkedIn typically requires cover letter content
        has_cover_letter = any(
            doc.document_type == DocumentType.COVER_LETTER 
            for doc in application_package.documents
        )
        
        if not has_cover_letter:
            errors.append("Cover letter is typically required for LinkedIn applications")
        
        # Check for job URL
        if not config.custom_fields.get('job_url'):
            errors.append("LinkedIn job URL is required")
        
        return len(errors) == 0, errors
    
    async def submit_application(self, request: SubmissionRequest) -> SubmissionAttempt:
        """Submit application via LinkedIn"""
        
        attempt_id = self._generate_attempt_id()
        
        try:
            # In production, this would:
            # 1. Use LinkedIn API or automation
            # 2. Navigate to job posting
            # 3. Fill in application form
            # 4. Upload documents
            # 5. Submit application
            
            # For now, simulate the process
            await self._simulate_linkedin_submission(request)
            
            return SubmissionAttempt(
                attempt_id=attempt_id,
                timestamp=datetime.utcnow(),
                platform=SubmissionPlatform.LINKEDIN,
                method=SubmissionMethod.SEMI_AUTOMATED,  # LinkedIn typically requires human confirmation
                status=SubmissionStatus.REQUIRES_MANUAL,
                response_data={'prepared_for_submission': True},
                confirmation_code=f"LINKEDIN_{attempt_id[:8].upper()}"
            )
            
        except Exception as e:
            logger.error(f"LinkedIn submission preparation failed: {str(e)}")
            return SubmissionAttempt(
                attempt_id=attempt_id,
                timestamp=datetime.utcnow(),
                platform=SubmissionPlatform.LINKEDIN,
                method=request.submission_config.method,
                status=SubmissionStatus.FAILED,
                error_message=str(e)
            )
    
    async def _simulate_linkedin_submission(self, request: SubmissionRequest):
        """Simulate LinkedIn submission preparation"""
        await asyncio.sleep(2)  # Simulate processing time
        logger.info(f"LinkedIn application prepared for manual submission")
    
    def _generate_attempt_id(self) -> str:
        return hashlib.md5(f"linkedin_{datetime.utcnow().isoformat()}".encode()).hexdigest()[:16]


class CompanyWebsiteHandler(SubmissionHandler):
    """Handles company website application submissions"""
    
    async def can_handle(self, platform: SubmissionPlatform) -> bool:
        return platform == SubmissionPlatform.COMPANY_WEBSITE
    
    async def validate_submission_data(
        self, 
        application_package: ApplicationPackage,
        config: SubmissionConfig
    ) -> Tuple[bool, List[str]]:
        """Validate company website submission data"""
        
        errors = []
        
        if not config.custom_fields.get('application_url'):
            errors.append("Company application URL is required")
        
        # Most company websites require resume/CV
        has_resume_content = any(
            doc.document_type in [DocumentType.COVER_LETTER, DocumentType.RESUME_SUMMARY]
            for doc in application_package.documents
        )
        
        if not has_resume_content:
            errors.append("Resume or cover letter content is required")
        
        return len(errors) == 0, errors
    
    async def submit_application(self, request: SubmissionRequest) -> SubmissionAttempt:
        """Submit application to company website"""
        
        attempt_id = self._generate_attempt_id()
        
        try:
            # Company websites typically require manual submission
            # We prepare the data and provide instructions
            
            instructions = self._generate_submission_instructions(request)
            
            return SubmissionAttempt(
                attempt_id=attempt_id,
                timestamp=datetime.utcnow(),
                platform=SubmissionPlatform.COMPANY_WEBSITE,
                method=SubmissionMethod.MANUAL,
                status=SubmissionStatus.REQUIRES_MANUAL,
                response_data={
                    'instructions': instructions,
                    'application_url': request.submission_config.custom_fields.get('application_url')
                },
                submission_url=request.submission_config.custom_fields.get('application_url'),
                confirmation_code=f"WEBSITE_{attempt_id[:8].upper()}"
            )
            
        except Exception as e:
            logger.error(f"Website submission preparation failed: {str(e)}")
            return SubmissionAttempt(
                attempt_id=attempt_id,
                timestamp=datetime.utcnow(),
                platform=SubmissionPlatform.COMPANY_WEBSITE,
                method=request.submission_config.method,
                status=SubmissionStatus.FAILED,
                error_message=str(e)
            )
    
    def _generate_submission_instructions(self, request: SubmissionRequest) -> List[str]:
        """Generate manual submission instructions"""
        
        instructions = []
        instructions.append("1. Navigate to the company application portal")
        instructions.append("2. Create account or log in if required")
        instructions.append("3. Fill in personal information")
        
        # Add document-specific instructions
        for doc in request.application_package.documents:
            if doc.document_type == DocumentType.COVER_LETTER:
                instructions.append("4. Copy and paste cover letter content into application form")
            elif doc.document_type == DocumentType.RESUME_SUMMARY:
                instructions.append("5. Upload resume file or fill in resume sections")
        
        instructions.append("6. Review all information for accuracy")
        instructions.append("7. Submit application")
        instructions.append("8. Save confirmation number/email")
        
        return instructions
    
    def _generate_attempt_id(self) -> str:
        return hashlib.md5(f"website_{datetime.utcnow().isoformat()}".encode()).hexdigest()[:16]


class SubmissionQueue:
    """Queue for managing submission requests"""
    
    def __init__(self):
        self.pending_submissions: List[SubmissionRequest] = []
        self.in_progress_submissions: Dict[str, SubmissionRequest] = {}
        self.completed_submissions: Dict[str, SubmissionResult] = {}
    
    def add_submission(self, request: SubmissionRequest) -> str:
        """Add submission request to queue"""
        submission_id = request.generate_id()
        self.pending_submissions.append(request)
        
        # Sort by priority (lower number = higher priority)
        self.pending_submissions.sort(key=lambda x: (x.priority, x.created_at))
        
        logger.info(f"Added submission {submission_id} to queue (priority {request.priority})")
        return submission_id
    
    def get_next_submission(self) -> Optional[SubmissionRequest]:
        """Get next submission request from queue"""
        if self.pending_submissions:
            return self.pending_submissions.pop(0)
        return None
    
    def mark_in_progress(self, submission_id: str, request: SubmissionRequest):
        """Mark submission as in progress"""
        self.in_progress_submissions[submission_id] = request
    
    def complete_submission(self, submission_id: str, result: SubmissionResult):
        """Mark submission as completed"""
        if submission_id in self.in_progress_submissions:
            del self.in_progress_submissions[submission_id]
        self.completed_submissions[submission_id] = result
    
    def get_queue_status(self) -> Dict[str, Any]:
        """Get current queue status"""
        return {
            'pending': len(self.pending_submissions),
            'in_progress': len(self.in_progress_submissions),
            'completed': len(self.completed_submissions),
            'total_processed': len(self.completed_submissions)
        }


class SmartSubmissionEngine:
    """Main engine for handling smart application submissions"""
    
    def __init__(self):
        self.handlers = {
            SubmissionPlatform.EMAIL: EmailSubmissionHandler(),
            SubmissionPlatform.LINKEDIN: LinkedInSubmissionHandler(),
            SubmissionPlatform.COMPANY_WEBSITE: CompanyWebsiteHandler(),
        }
        self.submission_queue = SubmissionQueue()
        self.is_processing = False
    
    async def submit_application(
        self, 
        user_id: str,
        opportunity: Dict[str, Any],
        application_package: ApplicationPackage,
        submission_config: SubmissionConfig
    ) -> str:
        """Submit application package"""
        
        # Create submission request
        request = SubmissionRequest(
            user_id=user_id,
            opportunity_id=opportunity.get('id', ''),
            application_package=application_package,
            submission_config=submission_config
        )
        
        # Add to queue
        submission_id = self.submission_queue.add_submission(request)
        
        # Start processing if not already running
        if not self.is_processing:
            asyncio.create_task(self._process_submissions())
        
        return submission_id
    
    async def _process_submissions(self):
        """Process submissions from queue"""
        
        self.is_processing = True
        
        try:
            while True:
                # Get next submission
                request = self.submission_queue.get_next_submission()
                if not request:
                    break
                
                submission_id = request.generate_id()
                self.submission_queue.mark_in_progress(submission_id, request)
                
                try:
                    # Process submission
                    result = await self._process_single_submission(submission_id, request)
                    self.submission_queue.complete_submission(submission_id, result)
                    
                    logger.info(f"Completed submission {submission_id}: {result.final_status.value}")
                    
                except Exception as e:
                    logger.error(f"Failed to process submission {submission_id}: {str(e)}")
                    
                    # Create error result
                    error_result = SubmissionResult(
                        submission_id=submission_id,
                        request=request,
                        attempts=[],
                        final_status=SubmissionStatus.FAILED,
                        success=False,
                        next_steps=[f"Manual intervention required: {str(e)}"]
                    )
                    self.submission_queue.complete_submission(submission_id, error_result)
                
                # Small delay between submissions
                await asyncio.sleep(1)
                
        finally:
            self.is_processing = False
    
    async def _process_single_submission(
        self, 
        submission_id: str, 
        request: SubmissionRequest
    ) -> SubmissionResult:
        """Process a single submission request"""
        
        platform = request.submission_config.platform
        handler = self.handlers.get(platform)
        
        if not handler:
            # Create manual submission result for unsupported platforms
            return SubmissionResult(
                submission_id=submission_id,
                request=request,
                attempts=[],
                final_status=SubmissionStatus.REQUIRES_MANUAL,
                success=False,
                next_steps=[f"Manual submission required for platform: {platform.value}"]
            )
        
        attempts = []
        max_retries = request.submission_config.max_retries
        
        for attempt_num in range(max_retries + 1):
            try:
                attempt = await handler.submit_application(request)
                attempts.append(attempt)
                
                # Check if submission was successful
                if attempt.status == SubmissionStatus.SUBMITTED:
                    return SubmissionResult(
                        submission_id=submission_id,
                        request=request,
                        attempts=attempts,
                        final_status=SubmissionStatus.SUBMITTED,
                        success=True,
                        submission_url=attempt.submission_url,
                        confirmation_details={
                            'confirmation_code': attempt.confirmation_code,
                            'submitted_at': attempt.timestamp.isoformat()
                        },
                        next_steps=["Application submitted successfully", "Wait for response from employer"],
                        estimated_response_time="1-2 weeks"
                    )
                
                elif attempt.status == SubmissionStatus.REQUIRES_MANUAL:
                    return SubmissionResult(
                        submission_id=submission_id,
                        request=request,
                        attempts=attempts,
                        final_status=SubmissionStatus.REQUIRES_MANUAL,
                        success=False,
                        submission_url=attempt.submission_url,
                        next_steps=["Complete manual submission following provided instructions"],
                        confirmation_details=attempt.response_data
                    )
                
                # If failed and we have retries left, wait and retry
                if attempt_num < max_retries:
                    retry_delay = request.submission_config.retry_delay_minutes
                    logger.info(f"Submission attempt {attempt_num + 1} failed, retrying in {retry_delay} minutes")
                    await asyncio.sleep(retry_delay * 60)
                
            except Exception as e:
                logger.error(f"Submission attempt {attempt_num + 1} error: {str(e)}")
                
                error_attempt = SubmissionAttempt(
                    attempt_id=f"{submission_id}_attempt_{attempt_num}",
                    timestamp=datetime.utcnow(),
                    platform=platform,
                    method=request.submission_config.method,
                    status=SubmissionStatus.FAILED,
                    error_message=str(e)
                )
                attempts.append(error_attempt)
        
        # All attempts failed
        return SubmissionResult(
            submission_id=submission_id,
            request=request,
            attempts=attempts,
            final_status=SubmissionStatus.FAILED,
            success=False,
            next_steps=[
                "All automated submission attempts failed",
                "Review error messages and try manual submission",
                "Contact support if issues persist"
            ]
        )
    
    def get_submission_status(self, submission_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific submission"""
        
        # Check completed submissions
        if submission_id in self.submission_queue.completed_submissions:
            result = self.submission_queue.completed_submissions[submission_id]
            return result.to_dict()
        
        # Check in-progress submissions
        if submission_id in self.submission_queue.in_progress_submissions:
            return {
                'submission_id': submission_id,
                'status': 'in_progress',
                'message': 'Submission is currently being processed'
            }
        
        # Check pending submissions
        for request in self.submission_queue.pending_submissions:
            if request.generate_id() == submission_id:
                return {
                    'submission_id': submission_id,
                    'status': 'pending',
                    'message': 'Submission is queued for processing'
                }
        
        return None
    
    def get_queue_status(self) -> Dict[str, Any]:
        """Get overall queue status"""
        return self.submission_queue.get_queue_status()
    
    def get_supported_platforms(self) -> List[str]:
        """Get list of supported submission platforms"""
        return [platform.value for platform in self.handlers.keys()]


# Global submission engine
global_submission_engine = SmartSubmissionEngine()