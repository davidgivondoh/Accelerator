"""
Safety Guardrails & Human-in-the-Loop Approval System
======================================================

This module implements comprehensive safety mechanisms:
1. Content filtering and validation
2. Rate limiting and abuse prevention
3. Human approval workflows
4. Audit logging and compliance
5. ADK callback integration

Built for the Google ADK framework with enterprise-grade safety.
"""

import asyncio
import hashlib
import json
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum, auto
from typing import Any, Callable, Optional, Awaitable
from collections import defaultdict

from pydantic import BaseModel, Field
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.table import Table
from rich.syntax import Syntax

console = Console()


# =============================================================================
# ENUMS AND TYPES
# =============================================================================

class ContentCategory(Enum):
    """Categories of content for filtering."""
    SAFE = auto()
    PII_DETECTED = auto()
    SENSITIVE_INFO = auto()
    OFFENSIVE = auto()
    SPAM_LIKE = auto()
    MANIPULATION = auto()
    EXTERNAL_LINKS = auto()
    RATE_LIMITED = auto()


class ApprovalStatus(Enum):
    """Status of an approval request."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    AUTO_APPROVED = "auto_approved"
    EXPIRED = "expired"
    MODIFIED = "modified"


class RiskLevel(Enum):
    """Risk levels for content and actions."""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


class ActionType(Enum):
    """Types of actions requiring approval."""
    SEND_EMAIL = "send_email"
    SUBMIT_APPLICATION = "submit_application"
    EXTERNAL_API_CALL = "external_api_call"
    DATA_EXPORT = "data_export"
    PROFILE_UPDATE = "profile_update"
    BULK_OPERATION = "bulk_operation"


# =============================================================================
# DATA MODELS
# =============================================================================

class ContentFilter(BaseModel):
    """Configuration for content filtering."""
    block_pii: bool = True
    block_offensive: bool = True
    block_external_links: bool = False
    max_length: int = 50000
    require_professional_tone: bool = True
    allowed_domains: list[str] = Field(default_factory=list)
    blocked_patterns: list[str] = Field(default_factory=list)


class ApprovalRequest(BaseModel):
    """A request requiring human approval."""
    id: str
    action_type: ActionType
    risk_level: RiskLevel
    summary: str
    details: dict[str, Any]
    content_preview: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    status: ApprovalStatus = ApprovalStatus.PENDING
    approved_by: Optional[str] = None
    rejection_reason: Optional[str] = None
    modifications: Optional[dict[str, Any]] = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class SafetyViolation(BaseModel):
    """Record of a safety violation."""
    id: str
    category: ContentCategory
    severity: RiskLevel
    description: str
    content_hash: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    resolved: bool = False
    resolution_notes: Optional[str] = None


class AuditEntry(BaseModel):
    """Audit log entry for compliance."""
    id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    action: str
    actor: str
    target: Optional[str] = None
    details: dict[str, Any] = Field(default_factory=dict)
    outcome: str
    risk_level: RiskLevel = RiskLevel.LOW


# =============================================================================
# CONTENT SAFETY
# =============================================================================

class ContentSafetyChecker:
    """
    Validates content for safety and compliance.
    
    Checks for:
    - PII (emails, phones, SSN, etc.)
    - Offensive language
    - Spam patterns
    - Manipulation attempts
    - External links
    """
    
    # PII patterns
    PII_PATTERNS = {
        'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        'phone': r'\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b',
        'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
        'credit_card': r'\b(?:\d{4}[-\s]?){3}\d{4}\b',
        'address': r'\b\d+\s+[\w\s]+(?:street|st|avenue|ave|road|rd|boulevard|blvd|drive|dr|lane|ln|court|ct|way|place|pl)\b',
    }
    
    # Offensive patterns (simplified - would use ML model in production)
    OFFENSIVE_PATTERNS = [
        r'\b(?:stupid|idiot|dumb|hate)\b',
        # Add more patterns as needed
    ]
    
    # Spam indicators
    SPAM_PATTERNS = [
        r'(?:click here|act now|limited time|free money|guaranteed)',
        r'(?:!!!|\$\$\$|[A-Z]{10,})',  # Excessive punctuation/caps
    ]
    
    def __init__(self, config: Optional[ContentFilter] = None):
        """Initialize with optional custom configuration."""
        self.config = config or ContentFilter()
        self.violations: list[SafetyViolation] = []
        
    def check_content(self, content: str, context: Optional[dict] = None) -> tuple[bool, list[ContentCategory], str]:
        """
        Check content for safety issues.
        
        Returns:
            Tuple of (is_safe, categories_found, explanation)
        """
        issues: list[ContentCategory] = []
        explanations: list[str] = []
        
        # Length check
        if len(content) > self.config.max_length:
            issues.append(ContentCategory.SPAM_LIKE)
            explanations.append(f"Content exceeds maximum length ({len(content)} > {self.config.max_length})")
        
        # PII detection
        if self.config.block_pii:
            pii_found = self._detect_pii(content)
            if pii_found:
                issues.append(ContentCategory.PII_DETECTED)
                explanations.append(f"PII detected: {', '.join(pii_found)}")
        
        # Offensive content
        if self.config.block_offensive:
            if self._detect_offensive(content):
                issues.append(ContentCategory.OFFENSIVE)
                explanations.append("Potentially offensive content detected")
        
        # Spam patterns
        if self._detect_spam(content):
            issues.append(ContentCategory.SPAM_LIKE)
            explanations.append("Spam-like patterns detected")
        
        # External links
        if self.config.block_external_links:
            links = self._detect_external_links(content)
            if links:
                issues.append(ContentCategory.EXTERNAL_LINKS)
                explanations.append(f"External links found: {len(links)}")
        
        # Custom blocked patterns
        for pattern in self.config.blocked_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                issues.append(ContentCategory.MANIPULATION)
                explanations.append(f"Blocked pattern matched: {pattern[:30]}...")
        
        is_safe = len(issues) == 0
        explanation = "; ".join(explanations) if explanations else "Content passed all safety checks"
        
        return is_safe, issues, explanation
    
    def _detect_pii(self, content: str) -> list[str]:
        """Detect PII in content."""
        found = []
        for pii_type, pattern in self.PII_PATTERNS.items():
            if re.search(pattern, content, re.IGNORECASE):
                found.append(pii_type)
        return found
    
    def _detect_offensive(self, content: str) -> bool:
        """Check for offensive content."""
        content_lower = content.lower()
        for pattern in self.OFFENSIVE_PATTERNS:
            if re.search(pattern, content_lower):
                return True
        return False
    
    def _detect_spam(self, content: str) -> bool:
        """Check for spam patterns."""
        for pattern in self.SPAM_PATTERNS:
            if re.search(pattern, content, re.IGNORECASE):
                return True
        return False
    
    def _detect_external_links(self, content: str) -> list[str]:
        """Find external links in content."""
        url_pattern = r'https?://(?:www\.)?([a-zA-Z0-9-]+(?:\.[a-zA-Z]{2,})+)'
        matches = re.findall(url_pattern, content)
        
        # Filter out allowed domains
        external = [m for m in matches if m not in self.config.allowed_domains]
        return external
    
    def sanitize_content(self, content: str) -> str:
        """
        Sanitize content by redacting PII.
        
        Returns sanitized content with PII replaced by placeholders.
        """
        sanitized = content
        
        for pii_type, pattern in self.PII_PATTERNS.items():
            sanitized = re.sub(pattern, f'[{pii_type.upper()}_REDACTED]', sanitized, flags=re.IGNORECASE)
        
        return sanitized
    
    def log_violation(
        self,
        category: ContentCategory,
        severity: RiskLevel,
        description: str,
        content: str
    ) -> SafetyViolation:
        """Log a safety violation."""
        content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
        
        violation = SafetyViolation(
            id=f"viol_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{content_hash[:8]}",
            category=category,
            severity=severity,
            description=description,
            content_hash=content_hash
        )
        
        self.violations.append(violation)
        return violation


# =============================================================================
# RATE LIMITING
# =============================================================================

@dataclass
class RateLimitConfig:
    """Configuration for rate limiting."""
    max_requests: int = 100
    window_seconds: int = 3600
    burst_limit: int = 10
    burst_window_seconds: int = 60


class RateLimiter:
    """
    Rate limiter with sliding window and burst protection.
    """
    
    def __init__(self, config: Optional[RateLimitConfig] = None):
        """Initialize rate limiter."""
        self.config = config or RateLimitConfig()
        self.requests: dict[str, list[datetime]] = defaultdict(list)
        self.lock = asyncio.Lock()
    
    async def check_limit(self, key: str) -> tuple[bool, str]:
        """
        Check if request is within rate limits.
        
        Returns:
            Tuple of (is_allowed, reason)
        """
        async with self.lock:
            now = datetime.utcnow()
            
            # Clean old requests
            self._clean_old_requests(key, now)
            
            requests = self.requests[key]
            
            # Check burst limit
            burst_cutoff = now - timedelta(seconds=self.config.burst_window_seconds)
            burst_count = sum(1 for r in requests if r > burst_cutoff)
            
            if burst_count >= self.config.burst_limit:
                return False, f"Burst limit exceeded ({burst_count}/{self.config.burst_limit})"
            
            # Check window limit
            if len(requests) >= self.config.max_requests:
                return False, f"Rate limit exceeded ({len(requests)}/{self.config.max_requests})"
            
            # Record request
            requests.append(now)
            
            return True, "Request allowed"
    
    def _clean_old_requests(self, key: str, now: datetime) -> None:
        """Remove requests outside the window."""
        cutoff = now - timedelta(seconds=self.config.window_seconds)
        self.requests[key] = [r for r in self.requests[key] if r > cutoff]
    
    def get_status(self, key: str) -> dict[str, Any]:
        """Get rate limit status for a key."""
        now = datetime.utcnow()
        self._clean_old_requests(key, now)
        
        requests = self.requests[key]
        burst_cutoff = now - timedelta(seconds=self.config.burst_window_seconds)
        burst_count = sum(1 for r in requests if r > burst_cutoff)
        
        return {
            "key": key,
            "requests_in_window": len(requests),
            "max_requests": self.config.max_requests,
            "burst_count": burst_count,
            "burst_limit": self.config.burst_limit,
            "window_seconds": self.config.window_seconds,
        }


# =============================================================================
# HUMAN-IN-THE-LOOP APPROVAL
# =============================================================================

class ApprovalWorkflow:
    """
    Human-in-the-loop approval workflow.
    
    Manages approval requests, notifications, and decision tracking.
    """
    
    # Actions that always require approval
    ALWAYS_REQUIRE_APPROVAL = {ActionType.SUBMIT_APPLICATION, ActionType.BULK_OPERATION}
    
    # Risk thresholds for auto-approval
    AUTO_APPROVE_THRESHOLD = RiskLevel.LOW
    
    def __init__(
        self,
        auto_approve_low_risk: bool = True,
        approval_timeout_hours: int = 24,
        notify_callback: Optional[Callable[[ApprovalRequest], Awaitable[None]]] = None
    ):
        """
        Initialize approval workflow.
        
        Args:
            auto_approve_low_risk: Whether to auto-approve low-risk actions
            approval_timeout_hours: Hours before pending requests expire
            notify_callback: Async callback for notifications
        """
        self.auto_approve_low_risk = auto_approve_low_risk
        self.approval_timeout = timedelta(hours=approval_timeout_hours)
        self.notify_callback = notify_callback
        
        self.pending_requests: dict[str, ApprovalRequest] = {}
        self.completed_requests: list[ApprovalRequest] = []
        self.audit_log: list[AuditEntry] = []
    
    async def request_approval(
        self,
        action_type: ActionType,
        summary: str,
        details: dict[str, Any],
        content_preview: Optional[str] = None,
        risk_level: Optional[RiskLevel] = None,
        metadata: Optional[dict[str, Any]] = None
    ) -> ApprovalRequest:
        """
        Create an approval request.
        
        Args:
            action_type: Type of action requiring approval
            summary: Brief description
            details: Full action details
            content_preview: Preview of content (for review)
            risk_level: Override calculated risk level
            metadata: Additional metadata
            
        Returns:
            ApprovalRequest with status
        """
        # Calculate risk if not provided
        if risk_level is None:
            risk_level = self._calculate_risk(action_type, details)
        
        # Create request
        request_id = f"apr_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{hashlib.md5(summary.encode()).hexdigest()[:8]}"
        
        request = ApprovalRequest(
            id=request_id,
            action_type=action_type,
            risk_level=risk_level,
            summary=summary,
            details=details,
            content_preview=content_preview,
            expires_at=datetime.utcnow() + self.approval_timeout,
            metadata=metadata or {}
        )
        
        # Check for auto-approval
        if self._can_auto_approve(request):
            request.status = ApprovalStatus.AUTO_APPROVED
            self._log_decision(request, "system", "Auto-approved (low risk)")
            self.completed_requests.append(request)
        else:
            # Needs human approval
            self.pending_requests[request_id] = request
            
            # Send notification
            if self.notify_callback:
                await self.notify_callback(request)
        
        return request
    
    def _calculate_risk(self, action_type: ActionType, details: dict[str, Any]) -> RiskLevel:
        """Calculate risk level based on action type and details."""
        # Base risk by action type
        base_risk = {
            ActionType.SEND_EMAIL: RiskLevel.MEDIUM,
            ActionType.SUBMIT_APPLICATION: RiskLevel.HIGH,
            ActionType.EXTERNAL_API_CALL: RiskLevel.MEDIUM,
            ActionType.DATA_EXPORT: RiskLevel.HIGH,
            ActionType.PROFILE_UPDATE: RiskLevel.LOW,
            ActionType.BULK_OPERATION: RiskLevel.CRITICAL,
        }
        
        risk = base_risk.get(action_type, RiskLevel.MEDIUM)
        
        # Adjust based on details
        if details.get("recipient_count", 0) > 10:
            risk = RiskLevel(min(risk.value + 1, RiskLevel.CRITICAL.value))
        
        if details.get("external_service"):
            risk = RiskLevel(min(risk.value + 1, RiskLevel.CRITICAL.value))
        
        return risk
    
    def _can_auto_approve(self, request: ApprovalRequest) -> bool:
        """Check if request can be auto-approved."""
        if not self.auto_approve_low_risk:
            return False
        
        if request.action_type in self.ALWAYS_REQUIRE_APPROVAL:
            return False
        
        return request.risk_level.value <= self.AUTO_APPROVE_THRESHOLD.value
    
    async def approve(
        self,
        request_id: str,
        approver: str,
        modifications: Optional[dict[str, Any]] = None,
        notes: Optional[str] = None
    ) -> bool:
        """
        Approve a pending request.
        
        Args:
            request_id: ID of request to approve
            approver: Identity of approver
            modifications: Optional modifications to the action
            notes: Approval notes
            
        Returns:
            True if approved successfully
        """
        request = self.pending_requests.get(request_id)
        if not request:
            return False
        
        # Check expiration
        if request.expires_at and datetime.utcnow() > request.expires_at:
            request.status = ApprovalStatus.EXPIRED
            self._log_decision(request, "system", "Request expired")
            self.completed_requests.append(request)
            del self.pending_requests[request_id]
            return False
        
        # Apply approval
        if modifications:
            request.status = ApprovalStatus.MODIFIED
            request.modifications = modifications
        else:
            request.status = ApprovalStatus.APPROVED
        
        request.approved_by = approver
        
        self._log_decision(request, approver, notes or "Approved")
        self.completed_requests.append(request)
        del self.pending_requests[request_id]
        
        return True
    
    async def reject(
        self,
        request_id: str,
        rejector: str,
        reason: str
    ) -> bool:
        """
        Reject a pending request.
        
        Args:
            request_id: ID of request to reject
            rejector: Identity of rejector
            reason: Rejection reason
            
        Returns:
            True if rejected successfully
        """
        request = self.pending_requests.get(request_id)
        if not request:
            return False
        
        request.status = ApprovalStatus.REJECTED
        request.approved_by = rejector
        request.rejection_reason = reason
        
        self._log_decision(request, rejector, f"Rejected: {reason}")
        self.completed_requests.append(request)
        del self.pending_requests[request_id]
        
        return True
    
    def _log_decision(self, request: ApprovalRequest, actor: str, notes: str) -> None:
        """Log an approval decision."""
        entry = AuditEntry(
            id=f"audit_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            action=f"approval_{request.status.value}",
            actor=actor,
            target=request.id,
            details={
                "action_type": request.action_type.value,
                "summary": request.summary,
                "notes": notes,
            },
            outcome=request.status.value,
            risk_level=request.risk_level
        )
        self.audit_log.append(entry)
    
    def get_pending_requests(self) -> list[ApprovalRequest]:
        """Get all pending approval requests."""
        # Clean expired requests
        now = datetime.utcnow()
        expired = [
            rid for rid, req in self.pending_requests.items()
            if req.expires_at and now > req.expires_at
        ]
        
        for rid in expired:
            req = self.pending_requests[rid]
            req.status = ApprovalStatus.EXPIRED
            self.completed_requests.append(req)
            del self.pending_requests[rid]
        
        return list(self.pending_requests.values())
    
    def get_statistics(self) -> dict[str, Any]:
        """Get approval workflow statistics."""
        completed = self.completed_requests
        
        return {
            "pending_count": len(self.pending_requests),
            "total_completed": len(completed),
            "approved": sum(1 for r in completed if r.status in {ApprovalStatus.APPROVED, ApprovalStatus.AUTO_APPROVED, ApprovalStatus.MODIFIED}),
            "rejected": sum(1 for r in completed if r.status == ApprovalStatus.REJECTED),
            "expired": sum(1 for r in completed if r.status == ApprovalStatus.EXPIRED),
            "auto_approved": sum(1 for r in completed if r.status == ApprovalStatus.AUTO_APPROVED),
            "average_risk": sum(r.risk_level.value for r in completed) / len(completed) if completed else 0,
        }


# =============================================================================
# ADK CALLBACK INTEGRATION
# =============================================================================

class ADKGuardrails:
    """
    Google ADK callback integration for safety guardrails.
    
    Provides before_agent_callback and after_agent_callback for the ADK.
    """
    
    def __init__(
        self,
        content_checker: Optional[ContentSafetyChecker] = None,
        rate_limiter: Optional[RateLimiter] = None,
        approval_workflow: Optional[ApprovalWorkflow] = None
    ):
        """Initialize ADK guardrails."""
        self.content_checker = content_checker or ContentSafetyChecker()
        self.rate_limiter = rate_limiter or RateLimiter()
        self.approval_workflow = approval_workflow or ApprovalWorkflow()
        
        self.blocked_actions: list[dict[str, Any]] = []
        self.audit_log: list[AuditEntry] = []
    
    async def before_agent_callback(
        self,
        agent_name: str,
        action: str,
        parameters: dict[str, Any]
    ) -> tuple[bool, Optional[str], Optional[dict[str, Any]]]:
        """
        Callback executed before an agent action.
        
        This is called by the ADK before executing any agent action.
        
        Args:
            agent_name: Name of the agent
            action: Action being performed
            parameters: Action parameters
            
        Returns:
            Tuple of (allow_action, block_reason, modified_parameters)
        """
        # Rate limiting
        rate_key = f"{agent_name}:{action}"
        allowed, reason = await self.rate_limiter.check_limit(rate_key)
        
        if not allowed:
            self._log_blocked_action(agent_name, action, f"Rate limited: {reason}")
            return False, f"Rate limited: {reason}", None
        
        # Content safety check
        content_fields = ['content', 'message', 'body', 'text', 'description']
        for field in content_fields:
            if field in parameters and isinstance(parameters[field], str):
                is_safe, issues, explanation = self.content_checker.check_content(parameters[field])
                
                if not is_safe:
                    # Log violation
                    for issue in issues:
                        self.content_checker.log_violation(
                            category=issue,
                            severity=RiskLevel.HIGH,
                            description=explanation,
                            content=parameters[field]
                        )
                    
                    self._log_blocked_action(agent_name, action, f"Content safety: {explanation}")
                    return False, f"Content blocked: {explanation}", None
        
        # Check for high-risk actions requiring approval
        if self._requires_approval(action, parameters):
            request = await self.approval_workflow.request_approval(
                action_type=self._get_action_type(action),
                summary=f"{agent_name}: {action}",
                details=parameters,
                content_preview=str(parameters)[:500]
            )
            
            if request.status == ApprovalStatus.PENDING:
                self._log_blocked_action(agent_name, action, "Awaiting human approval")
                return False, f"Action requires human approval. Request ID: {request.id}", None
            elif request.status == ApprovalStatus.REJECTED:
                return False, f"Action was rejected: {request.rejection_reason}", None
            elif request.status == ApprovalStatus.MODIFIED and request.modifications:
                # Return modified parameters
                return True, None, {**parameters, **request.modifications}
        
        # Action allowed
        self._log_audit(agent_name, action, "allowed", parameters)
        return True, None, None
    
    async def after_agent_callback(
        self,
        agent_name: str,
        action: str,
        result: Any,
        error: Optional[Exception] = None
    ) -> None:
        """
        Callback executed after an agent action.
        
        Args:
            agent_name: Name of the agent
            action: Action that was performed
            result: Result of the action
            error: Exception if action failed
        """
        outcome = "error" if error else "success"
        
        self._log_audit(
            agent_name=agent_name,
            action=action,
            outcome=outcome,
            details={
                "result_type": type(result).__name__ if result else None,
                "error": str(error) if error else None
            }
        )
    
    def _requires_approval(self, action: str, parameters: dict[str, Any]) -> bool:
        """Check if action requires human approval."""
        approval_actions = {
            'send_email', 'submit_application', 'post_message',
            'update_profile', 'bulk_action', 'external_api'
        }
        
        if any(a in action.lower() for a in approval_actions):
            return True
        
        # Check for high-value actions
        if parameters.get('recipient_count', 0) > 5:
            return True
        
        return False
    
    def _get_action_type(self, action: str) -> ActionType:
        """Map action string to ActionType enum."""
        action_lower = action.lower()
        
        if 'email' in action_lower:
            return ActionType.SEND_EMAIL
        elif 'application' in action_lower or 'submit' in action_lower:
            return ActionType.SUBMIT_APPLICATION
        elif 'api' in action_lower or 'external' in action_lower:
            return ActionType.EXTERNAL_API_CALL
        elif 'export' in action_lower:
            return ActionType.DATA_EXPORT
        elif 'profile' in action_lower:
            return ActionType.PROFILE_UPDATE
        elif 'bulk' in action_lower:
            return ActionType.BULK_OPERATION
        
        return ActionType.EXTERNAL_API_CALL
    
    def _log_blocked_action(self, agent_name: str, action: str, reason: str) -> None:
        """Log a blocked action."""
        self.blocked_actions.append({
            "timestamp": datetime.utcnow().isoformat(),
            "agent": agent_name,
            "action": action,
            "reason": reason
        })
    
    def _log_audit(
        self,
        agent_name: str,
        action: str,
        outcome: str,
        details: Optional[dict] = None
    ) -> None:
        """Add audit log entry."""
        entry = AuditEntry(
            id=f"audit_{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}",
            action=action,
            actor=agent_name,
            details=details or {},
            outcome=outcome
        )
        self.audit_log.append(entry)


# =============================================================================
# INTERACTIVE APPROVAL CLI
# =============================================================================

class InteractiveApprovalCLI:
    """
    Interactive CLI for reviewing and approving requests.
    
    Provides a rich terminal interface for human-in-the-loop approval.
    """
    
    def __init__(self, workflow: ApprovalWorkflow):
        """Initialize interactive CLI."""
        self.workflow = workflow
    
    async def review_pending(self) -> None:
        """Review all pending approval requests."""
        pending = self.workflow.get_pending_requests()
        
        if not pending:
            console.print("[green]✓ No pending approval requests[/green]")
            return
        
        console.print(f"\n[bold cyan]📋 {len(pending)} Pending Approval Requests[/bold cyan]\n")
        
        for request in pending:
            await self._review_request(request)
    
    async def _review_request(self, request: ApprovalRequest) -> None:
        """Review a single approval request."""
        # Display request details
        risk_colors = {
            RiskLevel.LOW: "green",
            RiskLevel.MEDIUM: "yellow",
            RiskLevel.HIGH: "red",
            RiskLevel.CRITICAL: "bold red"
        }
        
        risk_color = risk_colors.get(request.risk_level, "white")
        
        table = Table(title=f"Approval Request: {request.id}", show_header=False)
        table.add_column("Field", style="cyan")
        table.add_column("Value")
        
        table.add_row("Action Type", request.action_type.value)
        table.add_row("Risk Level", f"[{risk_color}]{request.risk_level.name}[/{risk_color}]")
        table.add_row("Summary", request.summary)
        table.add_row("Created", request.created_at.strftime("%Y-%m-%d %H:%M:%S"))
        
        if request.expires_at:
            remaining = request.expires_at - datetime.utcnow()
            table.add_row("Expires In", f"{remaining.total_seconds() / 3600:.1f} hours")
        
        console.print(table)
        
        # Show content preview
        if request.content_preview:
            console.print("\n[bold]Content Preview:[/bold]")
            console.print(Panel(
                request.content_preview[:1000] + ("..." if len(request.content_preview) > 1000 else ""),
                title="Preview",
                border_style="dim"
            ))
        
        # Show details
        if request.details:
            console.print("\n[bold]Details:[/bold]")
            console.print(Syntax(
                json.dumps(request.details, indent=2, default=str),
                "json",
                theme="monokai"
            ))
        
        # Get user decision
        console.print()
        action = Prompt.ask(
            "Action",
            choices=["approve", "reject", "skip", "modify"],
            default="skip"
        )
        
        if action == "approve":
            await self.workflow.approve(
                request.id,
                approver="cli_user",
                notes=Prompt.ask("Notes (optional)", default="")
            )
            console.print(f"[green]✓ Request {request.id} approved[/green]")
            
        elif action == "reject":
            reason = Prompt.ask("Rejection reason")
            await self.workflow.reject(
                request.id,
                rejector="cli_user",
                reason=reason
            )
            console.print(f"[red]✗ Request {request.id} rejected[/red]")
            
        elif action == "modify":
            console.print("[yellow]Modify parameters (JSON format):[/yellow]")
            mod_str = Prompt.ask("Modifications")
            try:
                modifications = json.loads(mod_str)
                await self.workflow.approve(
                    request.id,
                    approver="cli_user",
                    modifications=modifications,
                    notes="Approved with modifications"
                )
                console.print(f"[green]✓ Request {request.id} approved with modifications[/green]")
            except json.JSONDecodeError:
                console.print("[red]Invalid JSON, skipping[/red]")
        
        console.print()
    
    def show_statistics(self) -> None:
        """Display approval workflow statistics."""
        stats = self.workflow.get_statistics()
        
        console.print("\n[bold cyan]📊 Approval Workflow Statistics[/bold cyan]\n")
        
        table = Table(show_header=False)
        table.add_column("Metric", style="cyan")
        table.add_column("Value", justify="right")
        
        table.add_row("Pending Requests", str(stats["pending_count"]))
        table.add_row("Total Completed", str(stats["total_completed"]))
        table.add_row("Approved", f"[green]{stats['approved']}[/green]")
        table.add_row("Rejected", f"[red]{stats['rejected']}[/red]")
        table.add_row("Expired", f"[yellow]{stats['expired']}[/yellow]")
        table.add_row("Auto-Approved", str(stats["auto_approved"]))
        table.add_row("Avg Risk Level", f"{stats['average_risk']:.2f}")
        
        console.print(table)


# =============================================================================
# GUARDRAILS SYSTEM FACADE
# =============================================================================

class GuardrailsSystem:
    """
    Unified facade for all safety guardrails.
    
    Provides a single interface for content safety, rate limiting,
    and human-in-the-loop approval.
    """
    
    def __init__(
        self,
        content_config: Optional[ContentFilter] = None,
        rate_config: Optional[RateLimitConfig] = None,
        auto_approve_low_risk: bool = True,
        approval_timeout_hours: int = 24
    ):
        """
        Initialize the guardrails system.
        
        Args:
            content_config: Content filtering configuration
            rate_config: Rate limiting configuration
            auto_approve_low_risk: Auto-approve low-risk actions
            approval_timeout_hours: Hours before approval requests expire
        """
        self.content_checker = ContentSafetyChecker(content_config)
        self.rate_limiter = RateLimiter(rate_config)
        self.approval_workflow = ApprovalWorkflow(
            auto_approve_low_risk=auto_approve_low_risk,
            approval_timeout_hours=approval_timeout_hours
        )
        
        self.adk_guardrails = ADKGuardrails(
            content_checker=self.content_checker,
            rate_limiter=self.rate_limiter,
            approval_workflow=self.approval_workflow
        )
        
        self.interactive_cli = InteractiveApprovalCLI(self.approval_workflow)
    
    async def check_content(self, content: str) -> tuple[bool, str]:
        """
        Quick content safety check.
        
        Returns:
            Tuple of (is_safe, explanation)
        """
        is_safe, _, explanation = self.content_checker.check_content(content)
        return is_safe, explanation
    
    async def request_approval(
        self,
        action_type: ActionType,
        summary: str,
        details: dict[str, Any],
        content_preview: Optional[str] = None
    ) -> ApprovalRequest:
        """Request human approval for an action."""
        return await self.approval_workflow.request_approval(
            action_type=action_type,
            summary=summary,
            details=details,
            content_preview=content_preview
        )
    
    async def check_rate_limit(self, key: str) -> bool:
        """Check if request is within rate limits."""
        allowed, _ = await self.rate_limiter.check_limit(key)
        return allowed
    
    def get_adk_callbacks(self) -> tuple[Callable, Callable]:
        """
        Get ADK callback functions.
        
        Returns:
            Tuple of (before_callback, after_callback)
        """
        return (
            self.adk_guardrails.before_agent_callback,
            self.adk_guardrails.after_agent_callback
        )
    
    async def review_approvals(self) -> None:
        """Start interactive approval review."""
        await self.interactive_cli.review_pending()
    
    def get_statistics(self) -> dict[str, Any]:
        """Get comprehensive statistics."""
        return {
            "approval_stats": self.approval_workflow.get_statistics(),
            "content_violations": len(self.content_checker.violations),
            "blocked_actions": len(self.adk_guardrails.blocked_actions),
            "audit_entries": len(self.adk_guardrails.audit_log),
        }


# =============================================================================
# FACTORY FUNCTION
# =============================================================================

def create_guardrails_system(
    strict_mode: bool = False,
    auto_approve: bool = True
) -> GuardrailsSystem:
    """
    Create a configured guardrails system.
    
    Args:
        strict_mode: Enable strict content filtering
        auto_approve: Enable auto-approval for low-risk actions
        
    Returns:
        Configured GuardrailsSystem
    """
    content_config = ContentFilter(
        block_pii=True,
        block_offensive=True,
        block_external_links=strict_mode,
        require_professional_tone=strict_mode,
    )
    
    rate_config = RateLimitConfig(
        max_requests=50 if strict_mode else 100,
        burst_limit=5 if strict_mode else 10,
    )
    
    return GuardrailsSystem(
        content_config=content_config,
        rate_config=rate_config,
        auto_approve_low_risk=auto_approve,
        approval_timeout_hours=12 if strict_mode else 24
    )


# =============================================================================
# MODULE EXPORTS
# =============================================================================

__all__ = [
    # Enums
    'ContentCategory',
    'ApprovalStatus',
    'RiskLevel',
    'ActionType',
    
    # Models
    'ContentFilter',
    'ApprovalRequest',
    'SafetyViolation',
    'AuditEntry',
    'RateLimitConfig',
    
    # Core classes
    'ContentSafetyChecker',
    'RateLimiter',
    'ApprovalWorkflow',
    'ADKGuardrails',
    'InteractiveApprovalCLI',
    'GuardrailsSystem',
    
    # Factory
    'create_guardrails_system',
]
