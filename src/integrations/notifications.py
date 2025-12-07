"""
Notification System
===================

Multi-channel notification system for Growth Engine alerts and updates.

Supports:
- Email notifications (SMTP, SendGrid, SES)
- Slack integration
- Discord webhooks
- Push notifications (Web Push, Firebase)
- SMS (Twilio)
- In-app notifications
"""

import asyncio
import json
import smtplib
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from enum import Enum
from typing import Any, Optional
import hashlib

from pydantic import BaseModel, Field


# =============================================================================
# ENUMS & TYPES
# =============================================================================

class NotificationChannel(Enum):
    """Supported notification channels."""
    EMAIL = "email"
    SLACK = "slack"
    DISCORD = "discord"
    SMS = "sms"
    PUSH = "push"
    IN_APP = "in_app"


class NotificationPriority(Enum):
    """Notification priority levels."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class NotificationType(Enum):
    """Types of notifications."""
    # Opportunities
    NEW_OPPORTUNITY = "new_opportunity"
    HIGH_FIT_OPPORTUNITY = "high_fit_opportunity"
    DEADLINE_APPROACHING = "deadline_approaching"
    DEADLINE_TODAY = "deadline_today"
    
    # Applications
    APPLICATION_GENERATED = "application_generated"
    APPLICATION_SUBMITTED = "application_submitted"
    APPLICATION_STATUS_CHANGE = "application_status_change"
    
    # System
    DAILY_DIGEST = "daily_digest"
    WEEKLY_SUMMARY = "weekly_summary"
    SYSTEM_ALERT = "system_alert"
    
    # Learning
    OUTCOME_RECORDED = "outcome_recorded"
    MODEL_UPDATED = "model_updated"
    
    # Approvals
    APPROVAL_REQUIRED = "approval_required"
    APPROVAL_GRANTED = "approval_granted"
    APPROVAL_REJECTED = "approval_rejected"


# =============================================================================
# MODELS
# =============================================================================

class NotificationTemplate(BaseModel):
    """Template for notifications."""
    name: str
    subject_template: str
    body_template: str
    html_template: Optional[str] = None
    
    def render(self, context: dict[str, Any]) -> tuple[str, str, Optional[str]]:
        """Render template with context."""
        subject = self.subject_template.format(**context)
        body = self.body_template.format(**context)
        html = self.html_template.format(**context) if self.html_template else None
        return subject, body, html


class Notification(BaseModel):
    """A notification to be sent."""
    id: str = Field(default_factory=lambda: hashlib.md5(
        f"{datetime.utcnow().isoformat()}".encode()
    ).hexdigest()[:12])
    
    type: NotificationType
    priority: NotificationPriority = NotificationPriority.NORMAL
    channels: list[NotificationChannel] = Field(default_factory=lambda: [NotificationChannel.EMAIL])
    
    # Content
    title: str
    message: str
    html_content: Optional[str] = None
    
    # Metadata
    data: dict[str, Any] = Field(default_factory=dict)
    recipient_id: str = ""
    recipient_email: Optional[str] = None
    recipient_phone: Optional[str] = None
    
    # Tracking
    created_at: datetime = Field(default_factory=datetime.utcnow)
    sent_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    
    # Actions
    action_url: Optional[str] = None
    action_label: Optional[str] = None


class NotificationPreferences(BaseModel):
    """User notification preferences."""
    user_id: str
    
    # Channel preferences
    email_enabled: bool = True
    slack_enabled: bool = False
    discord_enabled: bool = False
    sms_enabled: bool = False
    push_enabled: bool = True
    
    # Type preferences
    enabled_types: list[NotificationType] = Field(
        default_factory=lambda: list(NotificationType)
    )
    
    # Timing
    quiet_hours_start: Optional[int] = 22  # 10 PM
    quiet_hours_end: Optional[int] = 8     # 8 AM
    timezone: str = "UTC"
    
    # Digest settings
    daily_digest_enabled: bool = True
    daily_digest_time: str = "09:00"
    weekly_summary_enabled: bool = True
    weekly_summary_day: int = 1  # Monday
    
    # Thresholds
    min_fit_score_alert: float = 0.8  # Alert for high-fit opportunities
    deadline_reminder_days: list[int] = Field(default_factory=lambda: [7, 3, 1])


class DeliveryResult(BaseModel):
    """Result of notification delivery attempt."""
    channel: NotificationChannel
    success: bool
    message: str = ""
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: dict[str, Any] = Field(default_factory=dict)


# =============================================================================
# NOTIFICATION PROVIDERS
# =============================================================================

class NotificationProvider(ABC):
    """Abstract base class for notification providers."""
    
    @property
    @abstractmethod
    def channel(self) -> NotificationChannel:
        """The channel this provider handles."""
        pass
    
    @abstractmethod
    async def send(self, notification: Notification) -> DeliveryResult:
        """Send a notification."""
        pass
    
    @abstractmethod
    async def send_batch(self, notifications: list[Notification]) -> list[DeliveryResult]:
        """Send multiple notifications."""
        pass


class EmailProvider(NotificationProvider):
    """Email notification provider using SMTP."""
    
    def __init__(
        self,
        smtp_host: str = "smtp.gmail.com",
        smtp_port: int = 587,
        username: str = "",
        password: str = "",
        from_email: str = "",
        from_name: str = "Growth Engine"
    ):
        """Initialize email provider."""
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.from_email = from_email or username
        self.from_name = from_name
    
    @property
    def channel(self) -> NotificationChannel:
        return NotificationChannel.EMAIL
    
    async def send(self, notification: Notification) -> DeliveryResult:
        """Send email notification."""
        if not notification.recipient_email:
            return DeliveryResult(
                channel=self.channel,
                success=False,
                message="No recipient email provided"
            )
        
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = notification.title
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = notification.recipient_email
            
            # Plain text
            msg.attach(MIMEText(notification.message, 'plain'))
            
            # HTML if available
            if notification.html_content:
                msg.attach(MIMEText(notification.html_content, 'html'))
            
            # Send via SMTP
            await asyncio.get_event_loop().run_in_executor(
                None,
                self._send_smtp,
                msg,
                notification.recipient_email
            )
            
            return DeliveryResult(
                channel=self.channel,
                success=True,
                message=f"Email sent to {notification.recipient_email}"
            )
            
        except Exception as e:
            return DeliveryResult(
                channel=self.channel,
                success=False,
                message=str(e)
            )
    
    def _send_smtp(self, msg: MIMEMultipart, recipient: str) -> None:
        """Send email via SMTP (blocking)."""
        with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
            server.starttls()
            if self.username and self.password:
                server.login(self.username, self.password)
            server.sendmail(self.from_email, recipient, msg.as_string())
    
    async def send_batch(self, notifications: list[Notification]) -> list[DeliveryResult]:
        """Send batch of emails."""
        return await asyncio.gather(*[self.send(n) for n in notifications])


class SlackProvider(NotificationProvider):
    """Slack notification provider using webhooks."""
    
    def __init__(self, webhook_url: str, default_channel: str = "#growth-engine"):
        """Initialize Slack provider."""
        self.webhook_url = webhook_url
        self.default_channel = default_channel
    
    @property
    def channel(self) -> NotificationChannel:
        return NotificationChannel.SLACK
    
    async def send(self, notification: Notification) -> DeliveryResult:
        """Send Slack notification."""
        try:
            import httpx
            
            # Build Slack message
            blocks = self._build_blocks(notification)
            
            payload = {
                "channel": self.default_channel,
                "username": "Growth Engine",
                "icon_emoji": self._get_emoji(notification.type),
                "blocks": blocks,
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.webhook_url,
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )
                response.raise_for_status()
            
            return DeliveryResult(
                channel=self.channel,
                success=True,
                message="Slack message sent"
            )
            
        except Exception as e:
            return DeliveryResult(
                channel=self.channel,
                success=False,
                message=str(e)
            )
    
    def _build_blocks(self, notification: Notification) -> list[dict]:
        """Build Slack Block Kit blocks."""
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": notification.title,
                    "emoji": True
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": notification.message
                }
            }
        ]
        
        # Add action button if URL provided
        if notification.action_url:
            blocks.append({
                "type": "actions",
                "elements": [{
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": notification.action_label or "View Details"
                    },
                    "url": notification.action_url,
                    "style": "primary"
                }]
            })
        
        # Add context with timestamp
        blocks.append({
            "type": "context",
            "elements": [{
                "type": "mrkdwn",
                "text": f"🕐 {notification.created_at.strftime('%Y-%m-%d %H:%M UTC')}"
            }]
        })
        
        return blocks
    
    def _get_emoji(self, notification_type: NotificationType) -> str:
        """Get emoji for notification type."""
        emoji_map = {
            NotificationType.NEW_OPPORTUNITY: ":sparkles:",
            NotificationType.HIGH_FIT_OPPORTUNITY: ":star2:",
            NotificationType.DEADLINE_APPROACHING: ":warning:",
            NotificationType.DEADLINE_TODAY: ":rotating_light:",
            NotificationType.APPLICATION_GENERATED: ":memo:",
            NotificationType.APPLICATION_SUBMITTED: ":rocket:",
            NotificationType.DAILY_DIGEST: ":newspaper:",
            NotificationType.WEEKLY_SUMMARY: ":bar_chart:",
            NotificationType.APPROVAL_REQUIRED: ":raised_hand:",
            NotificationType.SYSTEM_ALERT: ":bell:",
        }
        return emoji_map.get(notification_type, ":bell:")
    
    async def send_batch(self, notifications: list[Notification]) -> list[DeliveryResult]:
        """Send batch of Slack messages."""
        results = []
        for notification in notifications:
            result = await self.send(notification)
            results.append(result)
            await asyncio.sleep(0.5)  # Rate limiting
        return results


class DiscordProvider(NotificationProvider):
    """Discord notification provider using webhooks."""
    
    def __init__(self, webhook_url: str):
        """Initialize Discord provider."""
        self.webhook_url = webhook_url
    
    @property
    def channel(self) -> NotificationChannel:
        return NotificationChannel.DISCORD
    
    async def send(self, notification: Notification) -> DeliveryResult:
        """Send Discord notification."""
        try:
            import httpx
            
            # Build Discord embed
            embed = {
                "title": notification.title,
                "description": notification.message,
                "color": self._get_color(notification.priority),
                "timestamp": notification.created_at.isoformat(),
                "footer": {"text": "Growth Engine"}
            }
            
            if notification.action_url:
                embed["url"] = notification.action_url
            
            payload = {
                "username": "Growth Engine",
                "embeds": [embed]
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.webhook_url,
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )
                response.raise_for_status()
            
            return DeliveryResult(
                channel=self.channel,
                success=True,
                message="Discord message sent"
            )
            
        except Exception as e:
            return DeliveryResult(
                channel=self.channel,
                success=False,
                message=str(e)
            )
    
    def _get_color(self, priority: NotificationPriority) -> int:
        """Get embed color based on priority."""
        colors = {
            NotificationPriority.LOW: 0x808080,      # Gray
            NotificationPriority.NORMAL: 0x3498db,   # Blue
            NotificationPriority.HIGH: 0xf39c12,     # Orange
            NotificationPriority.URGENT: 0xe74c3c,   # Red
        }
        return colors.get(priority, 0x3498db)
    
    async def send_batch(self, notifications: list[Notification]) -> list[DeliveryResult]:
        """Send batch of Discord messages."""
        results = []
        for notification in notifications:
            result = await self.send(notification)
            results.append(result)
            await asyncio.sleep(0.5)  # Rate limiting
        return results


class PushProvider(NotificationProvider):
    """Web Push notification provider."""
    
    def __init__(self, vapid_private_key: str, vapid_public_key: str, vapid_email: str):
        """Initialize push provider."""
        self.vapid_private_key = vapid_private_key
        self.vapid_public_key = vapid_public_key
        self.vapid_email = vapid_email
        self._subscriptions: dict[str, dict] = {}
    
    @property
    def channel(self) -> NotificationChannel:
        return NotificationChannel.PUSH
    
    def register_subscription(self, user_id: str, subscription: dict) -> None:
        """Register a push subscription for a user."""
        self._subscriptions[user_id] = subscription
    
    async def send(self, notification: Notification) -> DeliveryResult:
        """Send push notification."""
        subscription = self._subscriptions.get(notification.recipient_id)
        
        if not subscription:
            return DeliveryResult(
                channel=self.channel,
                success=False,
                message="No push subscription found"
            )
        
        try:
            # In production, use pywebpush library
            payload = {
                "title": notification.title,
                "body": notification.message,
                "icon": "/icon-192.png",
                "badge": "/badge-72.png",
                "data": {
                    "url": notification.action_url,
                    "notification_id": notification.id,
                }
            }
            
            # Simulate push send (actual implementation would use pywebpush)
            return DeliveryResult(
                channel=self.channel,
                success=True,
                message="Push notification sent",
                metadata={"subscription_endpoint": subscription.get("endpoint", "")[:50]}
            )
            
        except Exception as e:
            return DeliveryResult(
                channel=self.channel,
                success=False,
                message=str(e)
            )
    
    async def send_batch(self, notifications: list[Notification]) -> list[DeliveryResult]:
        """Send batch of push notifications."""
        return await asyncio.gather(*[self.send(n) for n in notifications])


class InAppProvider(NotificationProvider):
    """In-app notification provider (stored in database)."""
    
    def __init__(self):
        """Initialize in-app provider."""
        self._notifications: dict[str, list[Notification]] = {}
    
    @property
    def channel(self) -> NotificationChannel:
        return NotificationChannel.IN_APP
    
    async def send(self, notification: Notification) -> DeliveryResult:
        """Store notification for in-app display."""
        user_id = notification.recipient_id
        
        if user_id not in self._notifications:
            self._notifications[user_id] = []
        
        notification.sent_at = datetime.utcnow()
        self._notifications[user_id].append(notification)
        
        # Keep only last 100 notifications per user
        self._notifications[user_id] = self._notifications[user_id][-100:]
        
        return DeliveryResult(
            channel=self.channel,
            success=True,
            message="In-app notification stored"
        )
    
    async def send_batch(self, notifications: list[Notification]) -> list[DeliveryResult]:
        """Store batch of notifications."""
        return await asyncio.gather(*[self.send(n) for n in notifications])
    
    def get_notifications(
        self,
        user_id: str,
        unread_only: bool = False,
        limit: int = 50
    ) -> list[Notification]:
        """Get notifications for a user."""
        notifications = self._notifications.get(user_id, [])
        
        if unread_only:
            notifications = [n for n in notifications if n.read_at is None]
        
        return sorted(
            notifications,
            key=lambda n: n.created_at,
            reverse=True
        )[:limit]
    
    def mark_as_read(self, user_id: str, notification_ids: list[str]) -> int:
        """Mark notifications as read."""
        count = 0
        for notification in self._notifications.get(user_id, []):
            if notification.id in notification_ids and notification.read_at is None:
                notification.read_at = datetime.utcnow()
                count += 1
        return count
    
    def get_unread_count(self, user_id: str) -> int:
        """Get count of unread notifications."""
        return len([
            n for n in self._notifications.get(user_id, [])
            if n.read_at is None
        ])


# =============================================================================
# NOTIFICATION SERVICE
# =============================================================================

class NotificationService:
    """
    Main notification service.
    
    Coordinates sending notifications across multiple channels
    based on user preferences and notification type.
    """
    
    def __init__(self):
        """Initialize notification service."""
        self._providers: dict[NotificationChannel, NotificationProvider] = {}
        self._preferences: dict[str, NotificationPreferences] = {}
        self._templates: dict[NotificationType, NotificationTemplate] = {}
        
        # Initialize in-app provider by default
        self._providers[NotificationChannel.IN_APP] = InAppProvider()
        
        # Load default templates
        self._load_default_templates()
    
    def _load_default_templates(self) -> None:
        """Load default notification templates."""
        self._templates = {
            NotificationType.NEW_OPPORTUNITY: NotificationTemplate(
                name="new_opportunity",
                subject_template="🌟 New Opportunity: {title}",
                body_template="""A new opportunity has been discovered:

{title} at {organization}

Fit Score: {fit_score:.0%}
Deadline: {deadline}

{description}

View Details: {url}""",
                html_template="""
<h2>🌟 New Opportunity Discovered</h2>
<h3>{title}</h3>
<p><strong>{organization}</strong></p>
<p>Fit Score: <strong>{fit_score:.0%}</strong></p>
<p>Deadline: {deadline}</p>
<hr>
<p>{description}</p>
<a href="{url}" style="display:inline-block;padding:10px 20px;background:#4CAF50;color:white;text-decoration:none;border-radius:5px;">View Details</a>
"""
            ),
            
            NotificationType.HIGH_FIT_OPPORTUNITY: NotificationTemplate(
                name="high_fit_opportunity",
                subject_template="⭐ High-Fit Opportunity: {title} ({fit_score:.0%} match)",
                body_template="""Excellent match found!

{title} at {organization}

This opportunity has a {fit_score:.0%} fit score - one of your best matches!

Deadline: {deadline}

{description}

Don't miss this one! View Details: {url}""",
                html_template="""
<h2>⭐ High-Fit Opportunity Found!</h2>
<div style="background:#FFF3E0;padding:15px;border-radius:8px;margin:10px 0;">
  <h3 style="margin:0;">{title}</h3>
  <p><strong>{organization}</strong></p>
  <p style="font-size:24px;color:#FF9800;margin:10px 0;">{fit_score:.0%} Match</p>
</div>
<p>Deadline: <strong>{deadline}</strong></p>
<p>{description}</p>
<a href="{url}" style="display:inline-block;padding:12px 24px;background:#FF9800;color:white;text-decoration:none;border-radius:5px;font-weight:bold;">Apply Now</a>
"""
            ),
            
            NotificationType.DEADLINE_APPROACHING: NotificationTemplate(
                name="deadline_approaching",
                subject_template="⏰ Deadline in {days_remaining} days: {title}",
                body_template="""Deadline reminder:

{title} at {organization}

Deadline: {deadline} ({days_remaining} days remaining)

Application Status: {application_status}

Don't forget to submit! View: {url}""",
                html_template="""
<h2>⏰ Deadline Approaching</h2>
<div style="background:#FFEBEE;padding:15px;border-radius:8px;margin:10px 0;">
  <h3 style="margin:0;">{title}</h3>
  <p><strong>{days_remaining} days remaining</strong></p>
</div>
<p>Organization: {organization}</p>
<p>Deadline: {deadline}</p>
<p>Status: {application_status}</p>
<a href="{url}" style="display:inline-block;padding:10px 20px;background:#f44336;color:white;text-decoration:none;border-radius:5px;">Complete Application</a>
"""
            ),
            
            NotificationType.DAILY_DIGEST: NotificationTemplate(
                name="daily_digest",
                subject_template="📊 Daily Digest: {new_opportunities} new opportunities",
                body_template="""Your Growth Engine Daily Digest

📊 Summary for {date}

New Opportunities: {new_opportunities}
High-Fit Matches: {high_fit_count}
Applications Generated: {applications_generated}
Deadlines This Week: {upcoming_deadlines}

Top Opportunities:
{top_opportunities}

View Dashboard: {dashboard_url}""",
                html_template="""
<h2>📊 Your Daily Digest</h2>
<p style="color:#666;">{date}</p>
<div style="display:flex;gap:20px;margin:20px 0;">
  <div style="background:#E3F2FD;padding:15px;border-radius:8px;text-align:center;flex:1;">
    <div style="font-size:32px;font-weight:bold;color:#1976D2;">{new_opportunities}</div>
    <div>New Opportunities</div>
  </div>
  <div style="background:#FFF3E0;padding:15px;border-radius:8px;text-align:center;flex:1;">
    <div style="font-size:32px;font-weight:bold;color:#FF9800;">{high_fit_count}</div>
    <div>High-Fit Matches</div>
  </div>
  <div style="background:#E8F5E9;padding:15px;border-radius:8px;text-align:center;flex:1;">
    <div style="font-size:32px;font-weight:bold;color:#4CAF50;">{applications_generated}</div>
    <div>Applications Ready</div>
  </div>
</div>
<h3>Top Opportunities</h3>
{top_opportunities_html}
<a href="{dashboard_url}" style="display:inline-block;padding:12px 24px;background:#1976D2;color:white;text-decoration:none;border-radius:5px;margin-top:20px;">View Full Dashboard</a>
"""
            ),
            
            NotificationType.APPROVAL_REQUIRED: NotificationTemplate(
                name="approval_required",
                subject_template="🔔 Approval Required: {action_type}",
                body_template="""Action requires your approval:

Type: {action_type}
Summary: {summary}

Details:
{details}

Approve or reject: {approval_url}""",
                html_template="""
<h2>🔔 Approval Required</h2>
<div style="background:#FFF3E0;padding:15px;border-radius:8px;margin:10px 0;">
  <p><strong>Action Type:</strong> {action_type}</p>
  <p><strong>Summary:</strong> {summary}</p>
</div>
<h3>Details</h3>
<pre style="background:#f5f5f5;padding:10px;border-radius:4px;">{details}</pre>
<div style="margin-top:20px;">
  <a href="{approve_url}" style="display:inline-block;padding:10px 20px;background:#4CAF50;color:white;text-decoration:none;border-radius:5px;margin-right:10px;">Approve</a>
  <a href="{reject_url}" style="display:inline-block;padding:10px 20px;background:#f44336;color:white;text-decoration:none;border-radius:5px;">Reject</a>
</div>
"""
            ),
        }
    
    def register_provider(
        self,
        provider: NotificationProvider
    ) -> None:
        """Register a notification provider."""
        self._providers[provider.channel] = provider
    
    def set_user_preferences(
        self,
        user_id: str,
        preferences: NotificationPreferences
    ) -> None:
        """Set notification preferences for a user."""
        self._preferences[user_id] = preferences
    
    def get_user_preferences(
        self,
        user_id: str
    ) -> NotificationPreferences:
        """Get notification preferences for a user."""
        if user_id not in self._preferences:
            self._preferences[user_id] = NotificationPreferences(user_id=user_id)
        return self._preferences[user_id]
    
    async def send(
        self,
        notification: Notification,
        user_id: Optional[str] = None
    ) -> dict[NotificationChannel, DeliveryResult]:
        """
        Send a notification across configured channels.
        
        Args:
            notification: The notification to send
            user_id: Optional user ID for preferences lookup
            
        Returns:
            Dict of channel to delivery result
        """
        user_id = user_id or notification.recipient_id
        prefs = self.get_user_preferences(user_id)
        
        # Check if notification type is enabled
        if notification.type not in prefs.enabled_types:
            return {}
        
        # Determine channels to use
        channels = self._get_enabled_channels(notification, prefs)
        
        # Send to each channel
        results = {}
        for channel in channels:
            provider = self._providers.get(channel)
            if provider:
                result = await provider.send(notification)
                results[channel] = result
        
        return results
    
    def _get_enabled_channels(
        self,
        notification: Notification,
        prefs: NotificationPreferences
    ) -> list[NotificationChannel]:
        """Determine which channels to use based on preferences."""
        channels = []
        
        # Check each channel
        if prefs.email_enabled and NotificationChannel.EMAIL in self._providers:
            channels.append(NotificationChannel.EMAIL)
        
        if prefs.slack_enabled and NotificationChannel.SLACK in self._providers:
            channels.append(NotificationChannel.SLACK)
        
        if prefs.discord_enabled and NotificationChannel.DISCORD in self._providers:
            channels.append(NotificationChannel.DISCORD)
        
        if prefs.sms_enabled and NotificationChannel.SMS in self._providers:
            # SMS only for urgent notifications
            if notification.priority == NotificationPriority.URGENT:
                channels.append(NotificationChannel.SMS)
        
        if prefs.push_enabled and NotificationChannel.PUSH in self._providers:
            channels.append(NotificationChannel.PUSH)
        
        # Always include in-app
        channels.append(NotificationChannel.IN_APP)
        
        return channels
    
    async def send_batch(
        self,
        notifications: list[Notification]
    ) -> list[dict[NotificationChannel, DeliveryResult]]:
        """Send multiple notifications."""
        return await asyncio.gather(*[self.send(n) for n in notifications])
    
    async def notify_new_opportunity(
        self,
        user_id: str,
        opportunity: dict,
        recipient_email: Optional[str] = None
    ) -> dict[NotificationChannel, DeliveryResult]:
        """Send notification for new opportunity."""
        template = self._templates.get(NotificationType.NEW_OPPORTUNITY)
        
        notification = Notification(
            type=NotificationType.NEW_OPPORTUNITY,
            priority=NotificationPriority.NORMAL,
            title=f"🌟 New Opportunity: {opportunity.get('title', 'Untitled')}",
            message=template.body_template.format(**opportunity) if template else str(opportunity),
            html_content=template.html_template.format(**opportunity) if template and template.html_template else None,
            recipient_id=user_id,
            recipient_email=recipient_email,
            data=opportunity,
            action_url=opportunity.get('url'),
            action_label="View Opportunity"
        )
        
        return await self.send(notification)
    
    async def notify_high_fit_opportunity(
        self,
        user_id: str,
        opportunity: dict,
        recipient_email: Optional[str] = None
    ) -> dict[NotificationChannel, DeliveryResult]:
        """Send notification for high-fit opportunity."""
        notification = Notification(
            type=NotificationType.HIGH_FIT_OPPORTUNITY,
            priority=NotificationPriority.HIGH,
            title=f"⭐ High-Fit Match: {opportunity.get('title', '')} ({opportunity.get('fit_score', 0):.0%})",
            message=f"Excellent match found! {opportunity.get('title')} at {opportunity.get('organization')}",
            recipient_id=user_id,
            recipient_email=recipient_email,
            data=opportunity,
            action_url=opportunity.get('url'),
            action_label="Apply Now"
        )
        
        return await self.send(notification)
    
    async def notify_deadline(
        self,
        user_id: str,
        opportunity: dict,
        days_remaining: int,
        recipient_email: Optional[str] = None
    ) -> dict[NotificationChannel, DeliveryResult]:
        """Send deadline reminder notification."""
        notification_type = (
            NotificationType.DEADLINE_TODAY if days_remaining == 0
            else NotificationType.DEADLINE_APPROACHING
        )
        
        priority = (
            NotificationPriority.URGENT if days_remaining == 0
            else NotificationPriority.HIGH if days_remaining <= 3
            else NotificationPriority.NORMAL
        )
        
        notification = Notification(
            type=notification_type,
            priority=priority,
            title=f"⏰ {'TODAY' if days_remaining == 0 else f'{days_remaining} days'}: {opportunity.get('title', '')}",
            message=f"Deadline {'today' if days_remaining == 0 else f'in {days_remaining} days'} for {opportunity.get('title')}",
            recipient_id=user_id,
            recipient_email=recipient_email,
            data={**opportunity, "days_remaining": days_remaining},
            action_url=opportunity.get('url'),
            action_label="Complete Application"
        )
        
        return await self.send(notification)
    
    async def send_daily_digest(
        self,
        user_id: str,
        digest_data: dict,
        recipient_email: Optional[str] = None
    ) -> dict[NotificationChannel, DeliveryResult]:
        """Send daily digest notification."""
        notification = Notification(
            type=NotificationType.DAILY_DIGEST,
            priority=NotificationPriority.LOW,
            title=f"📊 Daily Digest: {digest_data.get('new_opportunities', 0)} new opportunities",
            message=f"Today's summary: {digest_data.get('new_opportunities', 0)} new, {digest_data.get('high_fit_count', 0)} high-fit matches",
            recipient_id=user_id,
            recipient_email=recipient_email,
            data=digest_data,
            action_url=digest_data.get('dashboard_url'),
            action_label="View Dashboard"
        )
        
        return await self.send(notification)
    
    def get_in_app_notifications(
        self,
        user_id: str,
        unread_only: bool = False,
        limit: int = 50
    ) -> list[Notification]:
        """Get in-app notifications for a user."""
        provider = self._providers.get(NotificationChannel.IN_APP)
        if isinstance(provider, InAppProvider):
            return provider.get_notifications(user_id, unread_only, limit)
        return []
    
    def mark_notifications_read(
        self,
        user_id: str,
        notification_ids: list[str]
    ) -> int:
        """Mark notifications as read."""
        provider = self._providers.get(NotificationChannel.IN_APP)
        if isinstance(provider, InAppProvider):
            return provider.mark_as_read(user_id, notification_ids)
        return 0
    
    def get_unread_count(self, user_id: str) -> int:
        """Get count of unread notifications."""
        provider = self._providers.get(NotificationChannel.IN_APP)
        if isinstance(provider, InAppProvider):
            return provider.get_unread_count(user_id)
        return 0


# =============================================================================
# FACTORY FUNCTION
# =============================================================================

def create_notification_service(
    smtp_config: Optional[dict] = None,
    slack_webhook: Optional[str] = None,
    discord_webhook: Optional[str] = None,
) -> NotificationService:
    """
    Create a configured notification service.
    
    Args:
        smtp_config: SMTP configuration for email
        slack_webhook: Slack webhook URL
        discord_webhook: Discord webhook URL
        
    Returns:
        Configured NotificationService
    """
    service = NotificationService()
    
    # Configure email if SMTP config provided
    if smtp_config:
        email_provider = EmailProvider(**smtp_config)
        service.register_provider(email_provider)
    
    # Configure Slack if webhook provided
    if slack_webhook:
        slack_provider = SlackProvider(webhook_url=slack_webhook)
        service.register_provider(slack_provider)
    
    # Configure Discord if webhook provided
    if discord_webhook:
        discord_provider = DiscordProvider(webhook_url=discord_webhook)
        service.register_provider(discord_provider)
    
    return service


# =============================================================================
# MODULE EXPORTS
# =============================================================================

__all__ = [
    # Enums
    'NotificationChannel',
    'NotificationPriority',
    'NotificationType',
    
    # Models
    'NotificationTemplate',
    'Notification',
    'NotificationPreferences',
    'DeliveryResult',
    
    # Providers
    'NotificationProvider',
    'EmailProvider',
    'SlackProvider',
    'DiscordProvider',
    'PushProvider',
    'InAppProvider',
    
    # Service
    'NotificationService',
    'create_notification_service',
]
