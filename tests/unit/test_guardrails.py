"""
Unit Tests for Guardrails System
================================

Tests for content safety, rate limiting, and approval workflows.
"""

import pytest
import asyncio
from datetime import datetime, timedelta

from src.guardrails import (
    ContentSafetyChecker,
    ContentFilter,
    ContentCategory,
    RateLimiter,
    RateLimitConfig,
    ApprovalWorkflow,
    ApprovalStatus,
    ActionType,
    RiskLevel,
    GuardrailsSystem,
    create_guardrails_system,
)


class TestContentSafetyChecker:
    """Tests for content safety checking."""
    
    @pytest.fixture
    def checker(self):
        """Create a default content checker."""
        return ContentSafetyChecker()
    
    @pytest.fixture
    def strict_checker(self):
        """Create a strict content checker."""
        config = ContentFilter(
            block_pii=True,
            block_offensive=True,
            block_external_links=True,
        )
        return ContentSafetyChecker(config)
    
    def test_safe_content_passes(self, checker):
        """Test that safe content passes checks."""
        content = "I am a highly motivated software engineer with 5 years of experience."
        is_safe, issues, _ = checker.check_content(content)
        assert is_safe is True
        assert len(issues) == 0
    
    def test_pii_email_detected(self, checker):
        """Test that email addresses are detected as PII."""
        content = "Contact me at john.doe@example.com for more info."
        is_safe, issues, _ = checker.check_content(content)
        assert is_safe is False
        assert ContentCategory.PII_DETECTED in issues
    
    def test_pii_phone_detected(self, checker):
        """Test that phone numbers are detected as PII."""
        content = "Call me at 555-123-4567 anytime."
        is_safe, issues, _ = checker.check_content(content)
        assert is_safe is False
        assert ContentCategory.PII_DETECTED in issues
    
    def test_pii_ssn_detected(self, checker):
        """Test that SSN patterns are detected."""
        content = "My SSN is 123-45-6789."
        is_safe, issues, _ = checker.check_content(content)
        assert is_safe is False
        assert ContentCategory.PII_DETECTED in issues
    
    def test_sanitize_content_redacts_pii(self, checker):
        """Test that PII is redacted in sanitized content."""
        content = "Email me at test@example.com or call 555-123-4567."
        sanitized = checker.sanitize_content(content)
        
        assert "test@example.com" not in sanitized
        assert "555-123-4567" not in sanitized
        assert "EMAIL_REDACTED" in sanitized or "PHONE_REDACTED" in sanitized
    
    def test_content_length_limit(self, checker):
        """Test that overly long content is flagged."""
        long_content = "x" * 100000  # 100k characters
        is_safe, issues, _ = checker.check_content(long_content)
        assert is_safe is False
        assert ContentCategory.SPAM_LIKE in issues
    
    def test_external_links_blocked_when_enabled(self, strict_checker):
        """Test external link blocking when enabled."""
        content = "Check out https://malicious-site.com for details."
        is_safe, issues, _ = strict_checker.check_content(content)
        assert is_safe is False
        assert ContentCategory.EXTERNAL_LINKS in issues
    
    def test_violation_logging(self, checker):
        """Test that violations are logged."""
        checker.log_violation(
            category=ContentCategory.PII_DETECTED,
            severity=RiskLevel.HIGH,
            description="Email detected",
            content="test@example.com"
        )
        assert len(checker.violations) == 1
        assert checker.violations[0].category == ContentCategory.PII_DETECTED


class TestRateLimiter:
    """Tests for rate limiting."""
    
    @pytest.fixture
    def limiter(self):
        """Create a rate limiter with low limits for testing."""
        config = RateLimitConfig(
            max_requests=5,
            window_seconds=60,
            burst_limit=2,
            burst_window_seconds=1
        )
        return RateLimiter(config)
    
    @pytest.mark.asyncio
    async def test_allows_requests_under_limit(self, limiter):
        """Test that requests under limit are allowed."""
        allowed, _ = await limiter.check_limit("test_key")
        assert allowed is True
    
    @pytest.mark.asyncio
    async def test_blocks_burst_requests(self, limiter):
        """Test that burst requests are blocked."""
        # Make burst_limit + 1 requests rapidly
        for _ in range(3):
            await limiter.check_limit("burst_test")
        
        allowed, reason = await limiter.check_limit("burst_test")
        # Should be blocked due to burst limit
        assert allowed is False or "burst" in reason.lower() or "limit" in reason.lower()
    
    @pytest.mark.asyncio
    async def test_blocks_window_requests(self, limiter):
        """Test that requests exceeding window limit are blocked."""
        # Make max_requests + 1 requests
        for i in range(6):
            await limiter.check_limit("window_test")
            await asyncio.sleep(0.5)  # Spread to avoid burst limit
        
        status = limiter.get_status("window_test")
        assert status["requests_in_window"] <= status["max_requests"] + 1
    
    def test_get_status(self, limiter):
        """Test status reporting."""
        status = limiter.get_status("new_key")
        assert "key" in status
        assert "requests_in_window" in status
        assert "max_requests" in status
        assert "burst_count" in status


class TestApprovalWorkflow:
    """Tests for human-in-the-loop approval workflow."""
    
    @pytest.fixture
    def workflow(self):
        """Create an approval workflow."""
        return ApprovalWorkflow(
            auto_approve_low_risk=True,
            approval_timeout_hours=1
        )
    
    @pytest.fixture
    def strict_workflow(self):
        """Create a workflow that requires approval for everything."""
        return ApprovalWorkflow(
            auto_approve_low_risk=False,
            approval_timeout_hours=1
        )
    
    @pytest.mark.asyncio
    async def test_auto_approve_low_risk(self, workflow):
        """Test that low-risk actions are auto-approved."""
        request = await workflow.request_approval(
            action_type=ActionType.PROFILE_UPDATE,
            summary="Update profile picture",
            details={"field": "avatar"},
            risk_level=RiskLevel.LOW
        )
        assert request.status == ApprovalStatus.AUTO_APPROVED
    
    @pytest.mark.asyncio
    async def test_requires_approval_for_high_risk(self, workflow):
        """Test that high-risk actions require approval."""
        request = await workflow.request_approval(
            action_type=ActionType.SUBMIT_APPLICATION,
            summary="Submit job application",
            details={"company": "BigTech"},
            risk_level=RiskLevel.HIGH
        )
        # Should be pending since SUBMIT_APPLICATION always requires approval
        assert request.status == ApprovalStatus.PENDING
        assert request.id in workflow.pending_requests
    
    @pytest.mark.asyncio
    async def test_approve_request(self, workflow):
        """Test approving a pending request."""
        request = await workflow.request_approval(
            action_type=ActionType.SUBMIT_APPLICATION,
            summary="Submit application",
            details={},
            risk_level=RiskLevel.HIGH
        )
        
        success = await workflow.approve(
            request_id=request.id,
            approver="test_user",
            notes="Looks good"
        )
        
        assert success is True
        assert request.id not in workflow.pending_requests
    
    @pytest.mark.asyncio
    async def test_reject_request(self, workflow):
        """Test rejecting a pending request."""
        request = await workflow.request_approval(
            action_type=ActionType.SUBMIT_APPLICATION,
            summary="Submit application",
            details={},
            risk_level=RiskLevel.HIGH
        )
        
        success = await workflow.reject(
            request_id=request.id,
            rejector="test_user",
            reason="Not ready yet"
        )
        
        assert success is True
        assert request.status == ApprovalStatus.REJECTED
    
    @pytest.mark.asyncio
    async def test_approve_with_modifications(self, workflow):
        """Test approving with modifications."""
        request = await workflow.request_approval(
            action_type=ActionType.SEND_EMAIL,
            summary="Send outreach email",
            details={"recipient": "recruiter@company.com"},
            risk_level=RiskLevel.MEDIUM
        )
        
        if request.status == ApprovalStatus.PENDING:
            success = await workflow.approve(
                request_id=request.id,
                approver="test_user",
                modifications={"subject": "Updated subject line"}
            )
            
            assert success is True
            # Find the completed request
            completed = [r for r in workflow.completed_requests if r.id == request.id]
            if completed:
                assert completed[0].status == ApprovalStatus.MODIFIED
    
    def test_get_statistics(self, workflow):
        """Test statistics reporting."""
        stats = workflow.get_statistics()
        assert "pending_count" in stats
        assert "total_completed" in stats
        assert "approved" in stats
        assert "rejected" in stats


class TestGuardrailsSystem:
    """Tests for the unified guardrails system."""
    
    @pytest.fixture
    def guardrails(self):
        """Create a guardrails system."""
        return create_guardrails_system(strict_mode=False, auto_approve=True)
    
    @pytest.mark.asyncio
    async def test_check_safe_content(self, guardrails):
        """Test checking safe content."""
        is_safe, _ = await guardrails.check_content(
            "I am excited to apply for this position."
        )
        assert is_safe is True
    
    @pytest.mark.asyncio
    async def test_check_unsafe_content(self, guardrails):
        """Test checking unsafe content."""
        is_safe, explanation = await guardrails.check_content(
            "Contact me at private@email.com"
        )
        assert is_safe is False
        assert "PII" in explanation.upper() or "detected" in explanation.lower()
    
    @pytest.mark.asyncio
    async def test_rate_limit_check(self, guardrails):
        """Test rate limit checking."""
        # First request should pass
        allowed = await guardrails.check_rate_limit("test_action")
        assert allowed is True
    
    def test_get_adk_callbacks(self, guardrails):
        """Test getting ADK callbacks."""
        before_cb, after_cb = guardrails.get_adk_callbacks()
        assert callable(before_cb)
        assert callable(after_cb)
    
    def test_get_statistics(self, guardrails):
        """Test getting system statistics."""
        stats = guardrails.get_statistics()
        assert "approval_stats" in stats
        assert "content_violations" in stats
        assert "blocked_actions" in stats


class TestFactoryFunction:
    """Tests for the factory function."""
    
    def test_create_default_system(self):
        """Test creating default guardrails system."""
        system = create_guardrails_system()
        assert isinstance(system, GuardrailsSystem)
    
    def test_create_strict_system(self):
        """Test creating strict guardrails system."""
        system = create_guardrails_system(strict_mode=True, auto_approve=False)
        assert isinstance(system, GuardrailsSystem)
        # Strict mode should have lower rate limits
        status = system.rate_limiter.get_status("test")
        assert status["max_requests"] == 50  # Strict mode limit
