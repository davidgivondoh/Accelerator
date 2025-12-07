"""
External Integrations
=====================

MCP tools, browser extension support, voice interface, notifications,
multi-user support, and third-party service integrations.
"""

from src.integrations.mcp_tools import (
    MCPTool,
    MCPToolRegistry,
    MCPServer,
    create_mcp_server,
)
from src.integrations.browser_extension import (
    BrowserExtensionAPI,
    CapturedOpportunity,
    CaptureQueue,
    SmartCapture,
)
from src.integrations.voice import (
    VoiceInterface,
    VoiceConfig,
    SpeechRecognizer,
    TextToSpeech,
    VoiceCommandProcessor,
)
from src.integrations.notifications import (
    NotificationService,
    NotificationChannel,
    NotificationType,
    NotificationPriority,
    Notification,
    NotificationPreferences,
    create_notification_service,
)
from src.integrations.multi_user import (
    UserManagementService,
    AuthenticationService,
    OrganizationService,
    User,
    UserRole,
    Permission,
    Organization,
    APIKey,
    create_user_management_service,
)

__all__ = [
    # MCP
    'MCPTool',
    'MCPToolRegistry',
    'MCPServer',
    'create_mcp_server',
    
    # Browser Extension
    'BrowserExtensionAPI',
    'CapturedOpportunity',
    'CaptureQueue',
    'SmartCapture',
    
    # Voice
    'VoiceInterface',
    'VoiceConfig',
    'SpeechRecognizer',
    'TextToSpeech',
    'VoiceCommandProcessor',
    
    # Notifications
    'NotificationService',
    'NotificationChannel',
    'NotificationType',
    'NotificationPriority',
    'Notification',
    'NotificationPreferences',
    'create_notification_service',
    
    # Multi-User
    'UserManagementService',
    'AuthenticationService',
    'OrganizationService',
    'User',
    'UserRole',
    'Permission',
    'Organization',
    'APIKey',
    'create_user_management_service',
]
