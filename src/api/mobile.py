"""
Mobile API Extensions
=====================

Mobile-optimized API endpoints for the Growth Engine mobile application.

Features:
- Optimized payloads for mobile bandwidth
- Push notification registration
- Offline-first data sync
- Mobile-specific authentication
- Biometric auth support
- Location-based features
"""

from datetime import datetime
from enum import Enum
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Header, Query, status
from fastapi.security import HTTPBearer
from pydantic import BaseModel, Field


# =============================================================================
# MOBILE API ROUTER
# =============================================================================

mobile_router = APIRouter(prefix="/api/mobile/v1", tags=["mobile"])
security = HTTPBearer()


# =============================================================================
# MOBILE-SPECIFIC MODELS
# =============================================================================

class DevicePlatform(Enum):
    """Supported mobile platforms."""
    IOS = "ios"
    ANDROID = "android"
    WEB = "web"


class DeviceInfo(BaseModel):
    """Device information for mobile clients."""
    device_id: str
    platform: DevicePlatform
    os_version: str
    app_version: str
    device_model: str = ""
    push_token: Optional[str] = None


class PushTokenRegistration(BaseModel):
    """Push notification token registration."""
    device_id: str
    platform: DevicePlatform
    push_token: str
    topics: list[str] = Field(default_factory=lambda: ["all"])


class SyncRequest(BaseModel):
    """Data sync request for offline-first support."""
    device_id: str
    last_sync_timestamp: Optional[datetime] = None
    pending_changes: list[dict[str, Any]] = Field(default_factory=list)


class SyncResponse(BaseModel):
    """Data sync response."""
    sync_timestamp: datetime
    opportunities: list[dict[str, Any]] = Field(default_factory=list)
    applications: list[dict[str, Any]] = Field(default_factory=list)
    notifications: list[dict[str, Any]] = Field(default_factory=list)
    deleted_ids: list[str] = Field(default_factory=list)
    has_more: bool = False


# Mobile-optimized opportunity
class MobileOpportunity(BaseModel):
    """Lightweight opportunity model for mobile."""
    id: str
    title: str
    organization: str
    deadline: Optional[datetime] = None
    fit_score: float = 0.0
    status: str = "discovered"
    is_bookmarked: bool = False
    
    # Truncated fields for mobile
    description_preview: str = ""  # First 200 chars
    
    # Timestamps
    created_at: datetime
    updated_at: datetime


class MobileOpportunityDetail(MobileOpportunity):
    """Full opportunity details for mobile."""
    description: str = ""
    requirements: list[str] = Field(default_factory=list)
    url: str = ""
    location: str = ""
    compensation: str = ""
    
    # Application status
    application_id: Optional[str] = None
    application_status: Optional[str] = None


class MobileApplication(BaseModel):
    """Lightweight application model for mobile."""
    id: str
    opportunity_id: str
    opportunity_title: str
    organization: str
    status: str
    submitted_at: Optional[datetime] = None
    deadline: Optional[datetime] = None
    
    # Progress
    completion_percentage: int = 0
    
    # Timestamps
    created_at: datetime
    updated_at: datetime


class MobileNotification(BaseModel):
    """Mobile notification model."""
    id: str
    type: str
    title: str
    message: str
    action_url: Optional[str] = None
    is_read: bool = False
    created_at: datetime


class MobileDashboard(BaseModel):
    """Mobile dashboard summary."""
    # Stats
    opportunities_discovered: int = 0
    high_fit_opportunities: int = 0
    applications_in_progress: int = 0
    applications_submitted: int = 0
    
    # Alerts
    deadlines_this_week: int = 0
    unread_notifications: int = 0
    
    # Quick access
    recent_opportunities: list[MobileOpportunity] = Field(default_factory=list)
    pending_applications: list[MobileApplication] = Field(default_factory=list)
    
    # Last sync
    last_sync: Optional[datetime] = None


class QuickAction(BaseModel):
    """Quick action for mobile shortcuts."""
    id: str
    type: str  # "apply", "bookmark", "dismiss", "remind"
    opportunity_id: str


class BiometricAuthRequest(BaseModel):
    """Biometric authentication request."""
    device_id: str
    platform: DevicePlatform
    biometric_token: str
    user_id: str


class LocationData(BaseModel):
    """Location data for location-based features."""
    latitude: float
    longitude: float
    accuracy: float = 0.0
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# =============================================================================
# MOBILE API ENDPOINTS
# =============================================================================

# ----- Device Management -----

@mobile_router.post("/devices/register")
async def register_device(
    device_info: DeviceInfo,
    authorization: str = Header(...)
) -> dict[str, Any]:
    """
    Register a mobile device.
    
    Called on app launch to register the device and enable
    push notifications.
    """
    # In production, validate auth token and store device info
    return {
        "success": True,
        "device_id": device_info.device_id,
        "registered_at": datetime.utcnow().isoformat(),
        "features_enabled": {
            "push_notifications": device_info.push_token is not None,
            "biometric_auth": True,
            "offline_mode": True,
        }
    }


@mobile_router.post("/devices/push-token")
async def register_push_token(
    registration: PushTokenRegistration,
    authorization: str = Header(...)
) -> dict[str, Any]:
    """
    Register or update push notification token.
    
    Called when push token changes or topics are updated.
    """
    return {
        "success": True,
        "device_id": registration.device_id,
        "topics_subscribed": registration.topics,
    }


@mobile_router.delete("/devices/{device_id}")
async def unregister_device(
    device_id: str,
    authorization: str = Header(...)
) -> dict[str, Any]:
    """
    Unregister a device (logout).
    
    Removes push token and clears device-specific data.
    """
    return {
        "success": True,
        "device_id": device_id,
        "unregistered_at": datetime.utcnow().isoformat(),
    }


# ----- Authentication -----

@mobile_router.post("/auth/biometric")
async def biometric_auth(
    request: BiometricAuthRequest
) -> dict[str, Any]:
    """
    Authenticate using biometrics (Face ID, Touch ID, fingerprint).
    
    Returns new access tokens on successful biometric verification.
    """
    # In production, verify biometric token against stored credentials
    return {
        "success": True,
        "access_token": "mock_access_token",
        "refresh_token": "mock_refresh_token",
        "expires_in": 3600,
    }


@mobile_router.post("/auth/refresh")
async def refresh_mobile_token(
    refresh_token: str = Header(...),
    device_id: str = Header(...)
) -> dict[str, Any]:
    """
    Refresh access token for mobile client.
    
    Extended TTL for mobile to reduce auth frequency.
    """
    return {
        "access_token": "new_mock_access_token",
        "expires_in": 86400,  # 24 hours for mobile
    }


# ----- Data Sync -----

@mobile_router.post("/sync")
async def sync_data(
    sync_request: SyncRequest,
    authorization: str = Header(...)
) -> SyncResponse:
    """
    Sync data for offline-first support.
    
    - Sends pending local changes to server
    - Receives changes since last sync
    - Supports delta sync for efficiency
    """
    # Process pending changes
    # In production, apply changes to database
    
    # Return changes since last sync
    return SyncResponse(
        sync_timestamp=datetime.utcnow(),
        opportunities=[],  # Would contain changes since last_sync_timestamp
        applications=[],
        notifications=[],
        deleted_ids=[],
        has_more=False,
    )


@mobile_router.get("/sync/status")
async def get_sync_status(
    device_id: str = Query(...),
    authorization: str = Header(...)
) -> dict[str, Any]:
    """
    Get current sync status for device.
    
    Used to check if sync is needed on app launch.
    """
    return {
        "device_id": device_id,
        "last_sync": datetime.utcnow().isoformat(),
        "pending_server_changes": 0,
        "sync_required": False,
    }


# ----- Dashboard -----

@mobile_router.get("/dashboard")
async def get_mobile_dashboard(
    authorization: str = Header(...)
) -> MobileDashboard:
    """
    Get mobile dashboard summary.
    
    Optimized single endpoint for dashboard data.
    """
    # In production, aggregate from database
    return MobileDashboard(
        opportunities_discovered=42,
        high_fit_opportunities=8,
        applications_in_progress=3,
        applications_submitted=12,
        deadlines_this_week=2,
        unread_notifications=5,
        recent_opportunities=[],
        pending_applications=[],
        last_sync=datetime.utcnow(),
    )


# ----- Opportunities -----

@mobile_router.get("/opportunities")
async def list_mobile_opportunities(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=50),
    status: Optional[str] = None,
    min_fit_score: Optional[float] = None,
    bookmarked_only: bool = False,
    authorization: str = Header(...)
) -> dict[str, Any]:
    """
    List opportunities optimized for mobile.
    
    - Lightweight payload with preview text
    - Pagination for infinite scroll
    - Filter support
    """
    # In production, query database with filters
    opportunities: list[MobileOpportunity] = []
    
    return {
        "opportunities": opportunities,
        "page": page,
        "limit": limit,
        "total": 0,
        "has_more": False,
    }


@mobile_router.get("/opportunities/{opportunity_id}")
async def get_mobile_opportunity(
    opportunity_id: str,
    authorization: str = Header(...)
) -> MobileOpportunityDetail:
    """
    Get full opportunity details for mobile.
    
    Includes full description and application status.
    """
    # In production, fetch from database
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Opportunity not found"
    )


@mobile_router.post("/opportunities/{opportunity_id}/bookmark")
async def bookmark_opportunity(
    opportunity_id: str,
    authorization: str = Header(...)
) -> dict[str, Any]:
    """
    Bookmark an opportunity.
    
    Optimistic update supported - returns quickly.
    """
    return {
        "success": True,
        "opportunity_id": opportunity_id,
        "is_bookmarked": True,
    }


@mobile_router.delete("/opportunities/{opportunity_id}/bookmark")
async def remove_bookmark(
    opportunity_id: str,
    authorization: str = Header(...)
) -> dict[str, Any]:
    """
    Remove bookmark from opportunity.
    """
    return {
        "success": True,
        "opportunity_id": opportunity_id,
        "is_bookmarked": False,
    }


@mobile_router.post("/opportunities/{opportunity_id}/dismiss")
async def dismiss_opportunity(
    opportunity_id: str,
    reason: Optional[str] = None,
    authorization: str = Header(...)
) -> dict[str, Any]:
    """
    Dismiss an opportunity (hide from feed).
    
    Used for swipe-to-dismiss gestures.
    """
    return {
        "success": True,
        "opportunity_id": opportunity_id,
        "dismissed": True,
    }


# ----- Applications -----

@mobile_router.get("/applications")
async def list_mobile_applications(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=50),
    status: Optional[str] = None,
    authorization: str = Header(...)
) -> dict[str, Any]:
    """
    List applications for mobile.
    
    Lightweight payload with key status info.
    """
    applications: list[MobileApplication] = []
    
    return {
        "applications": applications,
        "page": page,
        "limit": limit,
        "total": 0,
        "has_more": False,
    }


@mobile_router.get("/applications/{application_id}")
async def get_mobile_application(
    application_id: str,
    authorization: str = Header(...)
) -> dict[str, Any]:
    """
    Get full application details for mobile.
    """
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Application not found"
    )


@mobile_router.post("/applications/{application_id}/quick-update")
async def quick_update_application(
    application_id: str,
    status: str,
    authorization: str = Header(...)
) -> dict[str, Any]:
    """
    Quick status update for application.
    
    Used for quick actions like marking as submitted.
    """
    return {
        "success": True,
        "application_id": application_id,
        "status": status,
        "updated_at": datetime.utcnow().isoformat(),
    }


# ----- Quick Actions -----

@mobile_router.post("/quick-actions")
async def process_quick_actions(
    actions: list[QuickAction],
    authorization: str = Header(...)
) -> dict[str, Any]:
    """
    Process batch of quick actions.
    
    Allows processing multiple actions in one request
    for better mobile performance.
    """
    results = []
    for action in actions:
        results.append({
            "action_id": action.id,
            "success": True,
            "type": action.type,
        })
    
    return {
        "processed": len(actions),
        "results": results,
    }


# ----- Notifications -----

@mobile_router.get("/notifications")
async def list_mobile_notifications(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=50),
    unread_only: bool = False,
    authorization: str = Header(...)
) -> dict[str, Any]:
    """
    List notifications for mobile.
    """
    notifications: list[MobileNotification] = []
    
    return {
        "notifications": notifications,
        "page": page,
        "limit": limit,
        "unread_count": 0,
        "has_more": False,
    }


@mobile_router.post("/notifications/mark-read")
async def mark_notifications_read(
    notification_ids: list[str],
    authorization: str = Header(...)
) -> dict[str, Any]:
    """
    Mark notifications as read.
    
    Supports batch marking for efficiency.
    """
    return {
        "success": True,
        "marked_count": len(notification_ids),
    }


@mobile_router.post("/notifications/mark-all-read")
async def mark_all_notifications_read(
    authorization: str = Header(...)
) -> dict[str, Any]:
    """
    Mark all notifications as read.
    """
    return {
        "success": True,
        "marked_count": 0,  # Would return actual count
    }


# ----- Interview Prep (Mobile) -----

@mobile_router.get("/interview-prep/questions")
async def get_interview_questions(
    category: Optional[str] = None,
    limit: int = Query(10, ge=1, le=50),
    authorization: str = Header(...)
) -> dict[str, Any]:
    """
    Get interview prep questions for mobile flashcard mode.
    """
    return {
        "questions": [],
        "total": 0,
        "category": category,
    }


@mobile_router.post("/interview-prep/practice")
async def submit_practice_response(
    question_id: str,
    response: str,
    audio_url: Optional[str] = None,
    authorization: str = Header(...)
) -> dict[str, Any]:
    """
    Submit practice interview response.
    
    Supports text and audio responses.
    """
    return {
        "success": True,
        "question_id": question_id,
        "feedback": {
            "score": 75,
            "strengths": ["Good structure"],
            "improvements": ["Add more specifics"],
        }
    }


# ----- Location Features -----

@mobile_router.post("/location/update")
async def update_location(
    location: LocationData,
    authorization: str = Header(...)
) -> dict[str, Any]:
    """
    Update user location for location-based features.
    
    Used for finding nearby opportunities, events, etc.
    """
    return {
        "success": True,
        "nearby_opportunities": 0,
        "nearby_events": 0,
    }


@mobile_router.get("/opportunities/nearby")
async def get_nearby_opportunities(
    latitude: float = Query(...),
    longitude: float = Query(...),
    radius_km: float = Query(50, ge=1, le=500),
    authorization: str = Header(...)
) -> dict[str, Any]:
    """
    Get opportunities near a location.
    """
    return {
        "opportunities": [],
        "center": {"lat": latitude, "lng": longitude},
        "radius_km": radius_km,
    }


# ----- Search -----

@mobile_router.get("/search")
async def mobile_search(
    q: str = Query(..., min_length=2),
    type: str = Query("all"),  # "all", "opportunities", "applications"
    limit: int = Query(20, ge=1, le=50),
    authorization: str = Header(...)
) -> dict[str, Any]:
    """
    Global search optimized for mobile.
    
    Searches across opportunities, applications, etc.
    """
    return {
        "query": q,
        "type": type,
        "results": {
            "opportunities": [],
            "applications": [],
        },
        "total": 0,
    }


@mobile_router.get("/search/suggestions")
async def search_suggestions(
    q: str = Query(..., min_length=1),
    authorization: str = Header(...)
) -> dict[str, Any]:
    """
    Get search suggestions for autocomplete.
    """
    return {
        "query": q,
        "suggestions": [],
    }


# ----- Settings -----

@mobile_router.get("/settings")
async def get_mobile_settings(
    authorization: str = Header(...)
) -> dict[str, Any]:
    """
    Get mobile app settings.
    """
    return {
        "notifications": {
            "push_enabled": True,
            "email_enabled": True,
            "new_opportunities": True,
            "deadlines": True,
            "application_updates": True,
        },
        "preferences": {
            "auto_sync": True,
            "data_saver_mode": False,
            "biometric_enabled": False,
        },
        "sync": {
            "wifi_only": False,
            "background_sync": True,
        }
    }


@mobile_router.patch("/settings")
async def update_mobile_settings(
    settings: dict[str, Any],
    authorization: str = Header(...)
) -> dict[str, Any]:
    """
    Update mobile app settings.
    """
    return {
        "success": True,
        "updated_settings": settings,
    }


# ----- Health Check -----

@mobile_router.get("/health")
async def mobile_health_check() -> dict[str, Any]:
    """
    Health check endpoint for mobile.
    
    Returns API status and version info.
    """
    return {
        "status": "healthy",
        "api_version": "1.0.0",
        "min_app_version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
    }


@mobile_router.get("/config")
async def get_mobile_config() -> dict[str, Any]:
    """
    Get mobile app configuration.
    
    Returns feature flags, limits, and configuration.
    """
    return {
        "features": {
            "voice_search": True,
            "interview_prep": True,
            "location_features": True,
            "biometric_auth": True,
        },
        "limits": {
            "max_sync_items": 100,
            "max_offline_days": 7,
            "max_bookmarks": 50,
        },
        "urls": {
            "terms": "https://example.com/terms",
            "privacy": "https://example.com/privacy",
            "support": "https://example.com/support",
        }
    }


# =============================================================================
# MODULE EXPORTS
# =============================================================================

__all__ = [
    # Router
    'mobile_router',
    
    # Models
    'DevicePlatform',
    'DeviceInfo',
    'PushTokenRegistration',
    'SyncRequest',
    'SyncResponse',
    'MobileOpportunity',
    'MobileOpportunityDetail',
    'MobileApplication',
    'MobileNotification',
    'MobileDashboard',
    'QuickAction',
    'BiometricAuthRequest',
    'LocationData',
]
