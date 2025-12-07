"""
Multi-User Support
==================

Authentication, authorization, and team management for Growth Engine.

Features:
- JWT-based authentication
- Role-based access control (RBAC)
- Team/organization support
- User profile management
- Session management
- API key management
"""

import asyncio
import hashlib
import hmac
import secrets
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Optional
from functools import wraps

from pydantic import BaseModel, Field, EmailStr


# =============================================================================
# ENUMS & CONSTANTS
# =============================================================================

class UserRole(Enum):
    """User roles for RBAC."""
    ADMIN = "admin"           # Full system access
    OWNER = "owner"           # Organization owner
    MANAGER = "manager"       # Can manage team members
    MEMBER = "member"         # Standard user
    VIEWER = "viewer"         # Read-only access
    API_USER = "api_user"     # API-only access


class Permission(Enum):
    """Granular permissions."""
    # Opportunities
    VIEW_OPPORTUNITIES = "view_opportunities"
    CREATE_OPPORTUNITIES = "create_opportunities"
    EDIT_OPPORTUNITIES = "edit_opportunities"
    DELETE_OPPORTUNITIES = "delete_opportunities"
    
    # Applications
    VIEW_APPLICATIONS = "view_applications"
    CREATE_APPLICATIONS = "create_applications"
    EDIT_APPLICATIONS = "edit_applications"
    DELETE_APPLICATIONS = "delete_applications"
    SUBMIT_APPLICATIONS = "submit_applications"
    
    # Profile
    VIEW_PROFILE = "view_profile"
    EDIT_PROFILE = "edit_profile"
    
    # Templates
    VIEW_TEMPLATES = "view_templates"
    CREATE_TEMPLATES = "create_templates"
    EDIT_TEMPLATES = "edit_templates"
    DELETE_TEMPLATES = "delete_templates"
    
    # Analytics
    VIEW_ANALYTICS = "view_analytics"
    EXPORT_DATA = "export_data"
    
    # Team
    VIEW_TEAM = "view_team"
    MANAGE_TEAM = "manage_team"
    INVITE_MEMBERS = "invite_members"
    REMOVE_MEMBERS = "remove_members"
    
    # Settings
    VIEW_SETTINGS = "view_settings"
    EDIT_SETTINGS = "edit_settings"
    MANAGE_INTEGRATIONS = "manage_integrations"
    
    # API
    MANAGE_API_KEYS = "manage_api_keys"
    
    # Admin
    ADMIN_ACCESS = "admin_access"
    VIEW_AUDIT_LOG = "view_audit_log"


# Role-Permission mapping
ROLE_PERMISSIONS: dict[UserRole, set[Permission]] = {
    UserRole.ADMIN: set(Permission),  # All permissions
    
    UserRole.OWNER: {
        Permission.VIEW_OPPORTUNITIES, Permission.CREATE_OPPORTUNITIES,
        Permission.EDIT_OPPORTUNITIES, Permission.DELETE_OPPORTUNITIES,
        Permission.VIEW_APPLICATIONS, Permission.CREATE_APPLICATIONS,
        Permission.EDIT_APPLICATIONS, Permission.DELETE_APPLICATIONS,
        Permission.SUBMIT_APPLICATIONS,
        Permission.VIEW_PROFILE, Permission.EDIT_PROFILE,
        Permission.VIEW_TEMPLATES, Permission.CREATE_TEMPLATES,
        Permission.EDIT_TEMPLATES, Permission.DELETE_TEMPLATES,
        Permission.VIEW_ANALYTICS, Permission.EXPORT_DATA,
        Permission.VIEW_TEAM, Permission.MANAGE_TEAM,
        Permission.INVITE_MEMBERS, Permission.REMOVE_MEMBERS,
        Permission.VIEW_SETTINGS, Permission.EDIT_SETTINGS,
        Permission.MANAGE_INTEGRATIONS, Permission.MANAGE_API_KEYS,
        Permission.VIEW_AUDIT_LOG,
    },
    
    UserRole.MANAGER: {
        Permission.VIEW_OPPORTUNITIES, Permission.CREATE_OPPORTUNITIES,
        Permission.EDIT_OPPORTUNITIES,
        Permission.VIEW_APPLICATIONS, Permission.CREATE_APPLICATIONS,
        Permission.EDIT_APPLICATIONS, Permission.SUBMIT_APPLICATIONS,
        Permission.VIEW_PROFILE, Permission.EDIT_PROFILE,
        Permission.VIEW_TEMPLATES, Permission.CREATE_TEMPLATES,
        Permission.EDIT_TEMPLATES,
        Permission.VIEW_ANALYTICS,
        Permission.VIEW_TEAM, Permission.INVITE_MEMBERS,
        Permission.VIEW_SETTINGS,
    },
    
    UserRole.MEMBER: {
        Permission.VIEW_OPPORTUNITIES, Permission.CREATE_OPPORTUNITIES,
        Permission.EDIT_OPPORTUNITIES,
        Permission.VIEW_APPLICATIONS, Permission.CREATE_APPLICATIONS,
        Permission.EDIT_APPLICATIONS, Permission.SUBMIT_APPLICATIONS,
        Permission.VIEW_PROFILE, Permission.EDIT_PROFILE,
        Permission.VIEW_TEMPLATES, Permission.CREATE_TEMPLATES,
        Permission.VIEW_ANALYTICS,
        Permission.VIEW_TEAM,
    },
    
    UserRole.VIEWER: {
        Permission.VIEW_OPPORTUNITIES,
        Permission.VIEW_APPLICATIONS,
        Permission.VIEW_PROFILE,
        Permission.VIEW_TEMPLATES,
        Permission.VIEW_ANALYTICS,
        Permission.VIEW_TEAM,
    },
    
    UserRole.API_USER: {
        Permission.VIEW_OPPORTUNITIES, Permission.CREATE_OPPORTUNITIES,
        Permission.VIEW_APPLICATIONS, Permission.CREATE_APPLICATIONS,
        Permission.VIEW_PROFILE,
        Permission.VIEW_ANALYTICS,
    },
}


# =============================================================================
# MODELS
# =============================================================================

class User(BaseModel):
    """User model."""
    id: str
    email: EmailStr
    username: str
    password_hash: str = Field(exclude=True)
    
    # Profile
    full_name: str = ""
    avatar_url: Optional[str] = None
    timezone: str = "UTC"
    
    # Role
    role: UserRole = UserRole.MEMBER
    custom_permissions: set[Permission] = Field(default_factory=set)
    
    # Organization
    organization_id: Optional[str] = None
    
    # Status
    is_active: bool = True
    is_verified: bool = False
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    
    def has_permission(self, permission: Permission) -> bool:
        """Check if user has a specific permission."""
        if not self.is_active:
            return False
        
        # Check custom permissions first
        if permission in self.custom_permissions:
            return True
        
        # Then check role permissions
        return permission in ROLE_PERMISSIONS.get(self.role, set())
    
    def has_any_permission(self, permissions: list[Permission]) -> bool:
        """Check if user has any of the specified permissions."""
        return any(self.has_permission(p) for p in permissions)
    
    def has_all_permissions(self, permissions: list[Permission]) -> bool:
        """Check if user has all specified permissions."""
        return all(self.has_permission(p) for p in permissions)


class UserSession(BaseModel):
    """User session model."""
    id: str
    user_id: str
    token_hash: str = Field(exclude=True)
    
    # Session info
    device_info: str = ""
    ip_address: str = ""
    user_agent: str = ""
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime
    last_activity: datetime = Field(default_factory=datetime.utcnow)
    
    # Status
    is_active: bool = True
    
    @property
    def is_expired(self) -> bool:
        """Check if session is expired."""
        return datetime.utcnow() > self.expires_at


class APIKey(BaseModel):
    """API key model."""
    id: str
    user_id: str
    name: str
    key_prefix: str  # First 8 chars for identification
    key_hash: str = Field(exclude=True)
    
    # Permissions
    scopes: list[Permission] = Field(default_factory=list)
    
    # Limits
    rate_limit: int = 1000  # Requests per hour
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    last_used: Optional[datetime] = None
    
    # Status
    is_active: bool = True
    
    @property
    def is_expired(self) -> bool:
        """Check if API key is expired."""
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at


class Organization(BaseModel):
    """Organization/team model."""
    id: str
    name: str
    slug: str
    
    # Owner
    owner_id: str
    
    # Settings
    settings: dict[str, Any] = Field(default_factory=dict)
    
    # Plan/subscription
    plan: str = "free"
    max_members: int = 5
    max_applications: int = 100
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Status
    is_active: bool = True


class OrganizationMember(BaseModel):
    """Organization membership model."""
    id: str
    organization_id: str
    user_id: str
    
    # Role within organization
    role: UserRole = UserRole.MEMBER
    
    # Timestamps
    joined_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Status
    is_active: bool = True


class Invitation(BaseModel):
    """Team invitation model."""
    id: str
    organization_id: str
    email: EmailStr
    role: UserRole = UserRole.MEMBER
    
    # Tokens
    token_hash: str = Field(exclude=True)
    
    # Inviter
    invited_by: str
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime
    accepted_at: Optional[datetime] = None
    
    @property
    def is_expired(self) -> bool:
        """Check if invitation is expired."""
        return datetime.utcnow() > self.expires_at


class AuthToken(BaseModel):
    """Authentication token response."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    refresh_token: Optional[str] = None


class AuditLogEntry(BaseModel):
    """Audit log entry."""
    id: str
    user_id: str
    action: str
    resource_type: str
    resource_id: Optional[str] = None
    
    # Details
    details: dict[str, Any] = Field(default_factory=dict)
    ip_address: str = ""
    user_agent: str = ""
    
    # Timestamp
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# =============================================================================
# AUTHENTICATION SERVICE
# =============================================================================

class PasswordHasher:
    """Password hashing utility."""
    
    @staticmethod
    def hash(password: str) -> str:
        """Hash a password."""
        salt = secrets.token_hex(16)
        hash_obj = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode(),
            salt.encode(),
            100000
        )
        return f"{salt}:{hash_obj.hex()}"
    
    @staticmethod
    def verify(password: str, hash_string: str) -> bool:
        """Verify a password against a hash."""
        try:
            salt, stored_hash = hash_string.split(':')
            hash_obj = hashlib.pbkdf2_hmac(
                'sha256',
                password.encode(),
                salt.encode(),
                100000
            )
            return hmac.compare_digest(hash_obj.hex(), stored_hash)
        except (ValueError, AttributeError):
            return False


class TokenGenerator:
    """Token generation utility."""
    
    @staticmethod
    def generate_token(length: int = 32) -> str:
        """Generate a random token."""
        return secrets.token_urlsafe(length)
    
    @staticmethod
    def generate_api_key() -> tuple[str, str]:
        """Generate an API key and return (key, prefix)."""
        key = f"ge_{secrets.token_urlsafe(32)}"
        prefix = key[:10]
        return key, prefix
    
    @staticmethod
    def hash_token(token: str) -> str:
        """Hash a token for storage."""
        return hashlib.sha256(token.encode()).hexdigest()


class AuthenticationService:
    """
    Authentication service handling user authentication.
    """
    
    def __init__(
        self,
        secret_key: str,
        access_token_ttl: int = 3600,      # 1 hour
        refresh_token_ttl: int = 604800,   # 7 days
    ):
        """Initialize authentication service."""
        self.secret_key = secret_key
        self.access_token_ttl = access_token_ttl
        self.refresh_token_ttl = refresh_token_ttl
        
        # In-memory stores (use database in production)
        self._users: dict[str, User] = {}
        self._sessions: dict[str, UserSession] = {}
        self._api_keys: dict[str, APIKey] = {}
        self._refresh_tokens: dict[str, str] = {}  # token_hash -> user_id
    
    async def register(
        self,
        email: str,
        username: str,
        password: str,
        full_name: str = "",
        role: UserRole = UserRole.MEMBER
    ) -> User:
        """Register a new user."""
        # Check if email exists
        for user in self._users.values():
            if user.email == email:
                raise ValueError("Email already registered")
            if user.username == username:
                raise ValueError("Username already taken")
        
        # Create user
        user_id = secrets.token_hex(12)
        user = User(
            id=user_id,
            email=email,
            username=username,
            password_hash=PasswordHasher.hash(password),
            full_name=full_name,
            role=role,
        )
        
        self._users[user_id] = user
        return user
    
    async def authenticate(
        self,
        email_or_username: str,
        password: str,
        device_info: str = "",
        ip_address: str = "",
        user_agent: str = ""
    ) -> tuple[User, AuthToken]:
        """Authenticate a user and return tokens."""
        # Find user
        user = None
        for u in self._users.values():
            if u.email == email_or_username or u.username == email_or_username:
                user = u
                break
        
        if not user:
            raise ValueError("Invalid credentials")
        
        # Verify password
        if not PasswordHasher.verify(password, user.password_hash):
            raise ValueError("Invalid credentials")
        
        if not user.is_active:
            raise ValueError("Account is disabled")
        
        # Update last login
        user.last_login = datetime.utcnow()
        
        # Create session
        session = await self._create_session(
            user.id, device_info, ip_address, user_agent
        )
        
        # Generate tokens
        access_token = TokenGenerator.generate_token()
        refresh_token = TokenGenerator.generate_token()
        
        # Store refresh token
        self._refresh_tokens[TokenGenerator.hash_token(refresh_token)] = user.id
        
        # Update session with access token hash
        session.token_hash = TokenGenerator.hash_token(access_token)
        
        return user, AuthToken(
            access_token=access_token,
            expires_in=self.access_token_ttl,
            refresh_token=refresh_token,
        )
    
    async def _create_session(
        self,
        user_id: str,
        device_info: str,
        ip_address: str,
        user_agent: str
    ) -> UserSession:
        """Create a new session."""
        session_id = secrets.token_hex(12)
        session = UserSession(
            id=session_id,
            user_id=user_id,
            token_hash="",
            device_info=device_info,
            ip_address=ip_address,
            user_agent=user_agent,
            expires_at=datetime.utcnow() + timedelta(seconds=self.access_token_ttl),
        )
        self._sessions[session_id] = session
        return session
    
    async def validate_token(self, token: str) -> Optional[User]:
        """Validate an access token and return the user."""
        token_hash = TokenGenerator.hash_token(token)
        
        # Find session with this token
        for session in self._sessions.values():
            if session.token_hash == token_hash:
                if session.is_expired or not session.is_active:
                    return None
                
                # Update last activity
                session.last_activity = datetime.utcnow()
                
                # Return user
                return self._users.get(session.user_id)
        
        return None
    
    async def refresh_access_token(
        self,
        refresh_token: str
    ) -> Optional[AuthToken]:
        """Refresh an access token."""
        token_hash = TokenGenerator.hash_token(refresh_token)
        user_id = self._refresh_tokens.get(token_hash)
        
        if not user_id:
            return None
        
        user = self._users.get(user_id)
        if not user or not user.is_active:
            return None
        
        # Generate new access token
        access_token = TokenGenerator.generate_token()
        
        # Find and update session
        for session in self._sessions.values():
            if session.user_id == user_id and session.is_active:
                session.token_hash = TokenGenerator.hash_token(access_token)
                session.expires_at = datetime.utcnow() + timedelta(
                    seconds=self.access_token_ttl
                )
                break
        
        return AuthToken(
            access_token=access_token,
            expires_in=self.access_token_ttl,
        )
    
    async def logout(self, token: str) -> bool:
        """Logout by invalidating the session."""
        token_hash = TokenGenerator.hash_token(token)
        
        for session in self._sessions.values():
            if session.token_hash == token_hash:
                session.is_active = False
                return True
        
        return False
    
    async def logout_all(self, user_id: str) -> int:
        """Logout all sessions for a user."""
        count = 0
        for session in self._sessions.values():
            if session.user_id == user_id and session.is_active:
                session.is_active = False
                count += 1
        return count
    
    # API Key Management
    async def create_api_key(
        self,
        user_id: str,
        name: str,
        scopes: list[Permission],
        expires_in_days: Optional[int] = None
    ) -> tuple[APIKey, str]:
        """Create a new API key. Returns (APIKey, raw_key)."""
        key, prefix = TokenGenerator.generate_api_key()
        key_id = secrets.token_hex(12)
        
        api_key = APIKey(
            id=key_id,
            user_id=user_id,
            name=name,
            key_prefix=prefix,
            key_hash=TokenGenerator.hash_token(key),
            scopes=scopes,
            expires_at=(
                datetime.utcnow() + timedelta(days=expires_in_days)
                if expires_in_days else None
            ),
        )
        
        self._api_keys[key_id] = api_key
        return api_key, key
    
    async def validate_api_key(self, key: str) -> Optional[tuple[User, APIKey]]:
        """Validate an API key and return user and key info."""
        key_hash = TokenGenerator.hash_token(key)
        
        for api_key in self._api_keys.values():
            if api_key.key_hash == key_hash:
                if api_key.is_expired or not api_key.is_active:
                    return None
                
                user = self._users.get(api_key.user_id)
                if not user or not user.is_active:
                    return None
                
                # Update last used
                api_key.last_used = datetime.utcnow()
                
                return user, api_key
        
        return None
    
    async def revoke_api_key(self, key_id: str, user_id: str) -> bool:
        """Revoke an API key."""
        api_key = self._api_keys.get(key_id)
        if api_key and api_key.user_id == user_id:
            api_key.is_active = False
            return True
        return False
    
    def get_user_api_keys(self, user_id: str) -> list[APIKey]:
        """Get all API keys for a user."""
        return [
            key for key in self._api_keys.values()
            if key.user_id == user_id and key.is_active
        ]


# =============================================================================
# ORGANIZATION SERVICE
# =============================================================================

class OrganizationService:
    """
    Organization and team management service.
    """
    
    def __init__(self, auth_service: AuthenticationService):
        """Initialize organization service."""
        self.auth_service = auth_service
        
        # In-memory stores
        self._organizations: dict[str, Organization] = {}
        self._memberships: dict[str, OrganizationMember] = {}
        self._invitations: dict[str, Invitation] = {}
    
    async def create_organization(
        self,
        name: str,
        owner_id: str,
        plan: str = "free"
    ) -> Organization:
        """Create a new organization."""
        org_id = secrets.token_hex(12)
        slug = name.lower().replace(' ', '-')
        
        # Check if slug exists
        for org in self._organizations.values():
            if org.slug == slug:
                slug = f"{slug}-{secrets.token_hex(4)}"
                break
        
        org = Organization(
            id=org_id,
            name=name,
            slug=slug,
            owner_id=owner_id,
            plan=plan,
        )
        
        self._organizations[org_id] = org
        
        # Add owner as member with OWNER role
        await self.add_member(org_id, owner_id, UserRole.OWNER)
        
        # Update user's organization_id
        user = self.auth_service._users.get(owner_id)
        if user:
            user.organization_id = org_id
            user.role = UserRole.OWNER
        
        return org
    
    async def get_organization(self, org_id: str) -> Optional[Organization]:
        """Get organization by ID."""
        return self._organizations.get(org_id)
    
    async def get_organization_by_slug(self, slug: str) -> Optional[Organization]:
        """Get organization by slug."""
        for org in self._organizations.values():
            if org.slug == slug:
                return org
        return None
    
    async def update_organization(
        self,
        org_id: str,
        updates: dict[str, Any]
    ) -> Optional[Organization]:
        """Update organization settings."""
        org = self._organizations.get(org_id)
        if not org:
            return None
        
        for key, value in updates.items():
            if hasattr(org, key):
                setattr(org, key, value)
        
        org.updated_at = datetime.utcnow()
        return org
    
    async def add_member(
        self,
        org_id: str,
        user_id: str,
        role: UserRole = UserRole.MEMBER
    ) -> OrganizationMember:
        """Add a member to an organization."""
        member_id = secrets.token_hex(12)
        
        member = OrganizationMember(
            id=member_id,
            organization_id=org_id,
            user_id=user_id,
            role=role,
        )
        
        self._memberships[member_id] = member
        
        # Update user
        user = self.auth_service._users.get(user_id)
        if user:
            user.organization_id = org_id
            if user.role not in [UserRole.ADMIN, UserRole.OWNER]:
                user.role = role
        
        return member
    
    async def remove_member(
        self,
        org_id: str,
        user_id: str
    ) -> bool:
        """Remove a member from an organization."""
        for member_id, member in list(self._memberships.items()):
            if member.organization_id == org_id and member.user_id == user_id:
                member.is_active = False
                
                # Update user
                user = self.auth_service._users.get(user_id)
                if user:
                    user.organization_id = None
                
                return True
        
        return False
    
    async def get_members(self, org_id: str) -> list[tuple[OrganizationMember, User]]:
        """Get all members of an organization."""
        members = []
        for member in self._memberships.values():
            if member.organization_id == org_id and member.is_active:
                user = self.auth_service._users.get(member.user_id)
                if user:
                    members.append((member, user))
        return members
    
    async def update_member_role(
        self,
        org_id: str,
        user_id: str,
        new_role: UserRole
    ) -> bool:
        """Update a member's role."""
        for member in self._memberships.values():
            if (member.organization_id == org_id and 
                member.user_id == user_id and 
                member.is_active):
                member.role = new_role
                
                # Update user role
                user = self.auth_service._users.get(user_id)
                if user:
                    user.role = new_role
                
                return True
        
        return False
    
    # Invitations
    async def create_invitation(
        self,
        org_id: str,
        email: str,
        role: UserRole,
        invited_by: str,
        expires_in_days: int = 7
    ) -> tuple[Invitation, str]:
        """Create an invitation. Returns (Invitation, token)."""
        invitation_id = secrets.token_hex(12)
        token = TokenGenerator.generate_token()
        
        invitation = Invitation(
            id=invitation_id,
            organization_id=org_id,
            email=email,
            role=role,
            token_hash=TokenGenerator.hash_token(token),
            invited_by=invited_by,
            expires_at=datetime.utcnow() + timedelta(days=expires_in_days),
        )
        
        self._invitations[invitation_id] = invitation
        return invitation, token
    
    async def accept_invitation(
        self,
        token: str,
        user_id: str
    ) -> Optional[Organization]:
        """Accept an invitation."""
        token_hash = TokenGenerator.hash_token(token)
        
        for invitation in self._invitations.values():
            if invitation.token_hash == token_hash:
                if invitation.is_expired or invitation.accepted_at:
                    return None
                
                # Mark as accepted
                invitation.accepted_at = datetime.utcnow()
                
                # Add user to organization
                await self.add_member(
                    invitation.organization_id,
                    user_id,
                    invitation.role
                )
                
                return self._organizations.get(invitation.organization_id)
        
        return None
    
    async def get_pending_invitations(self, org_id: str) -> list[Invitation]:
        """Get pending invitations for an organization."""
        return [
            inv for inv in self._invitations.values()
            if (inv.organization_id == org_id and 
                not inv.is_expired and 
                inv.accepted_at is None)
        ]


# =============================================================================
# AUTHORIZATION DECORATORS
# =============================================================================

def require_auth(func):
    """Decorator to require authentication."""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Get user from context (would be set by middleware)
        user = kwargs.get('current_user')
        if not user:
            raise PermissionError("Authentication required")
        return await func(*args, **kwargs)
    return wrapper


def require_permission(*permissions: Permission):
    """Decorator to require specific permissions."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            user = kwargs.get('current_user')
            if not user:
                raise PermissionError("Authentication required")
            
            if not user.has_any_permission(list(permissions)):
                raise PermissionError(f"Missing required permissions: {permissions}")
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def require_role(*roles: UserRole):
    """Decorator to require specific roles."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            user = kwargs.get('current_user')
            if not user:
                raise PermissionError("Authentication required")
            
            if user.role not in roles:
                raise PermissionError(f"Required role: {roles}")
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


# =============================================================================
# AUDIT LOGGING
# =============================================================================

class AuditLogger:
    """Audit logging service."""
    
    def __init__(self):
        """Initialize audit logger."""
        self._entries: list[AuditLogEntry] = []
    
    async def log(
        self,
        user_id: str,
        action: str,
        resource_type: str,
        resource_id: Optional[str] = None,
        details: Optional[dict] = None,
        ip_address: str = "",
        user_agent: str = ""
    ) -> AuditLogEntry:
        """Log an audit entry."""
        entry = AuditLogEntry(
            id=secrets.token_hex(12),
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details or {},
            ip_address=ip_address,
            user_agent=user_agent,
        )
        
        self._entries.append(entry)
        
        # Keep only last 10000 entries
        if len(self._entries) > 10000:
            self._entries = self._entries[-10000:]
        
        return entry
    
    def get_entries(
        self,
        user_id: Optional[str] = None,
        action: Optional[str] = None,
        resource_type: Optional[str] = None,
        since: Optional[datetime] = None,
        limit: int = 100
    ) -> list[AuditLogEntry]:
        """Get audit log entries with filters."""
        entries = self._entries
        
        if user_id:
            entries = [e for e in entries if e.user_id == user_id]
        
        if action:
            entries = [e for e in entries if e.action == action]
        
        if resource_type:
            entries = [e for e in entries if e.resource_type == resource_type]
        
        if since:
            entries = [e for e in entries if e.timestamp >= since]
        
        return sorted(
            entries,
            key=lambda e: e.timestamp,
            reverse=True
        )[:limit]


# =============================================================================
# USER MANAGEMENT SERVICE
# =============================================================================

class UserManagementService:
    """
    High-level user management service combining auth and org services.
    """
    
    def __init__(
        self,
        secret_key: str = "your-secret-key-here"
    ):
        """Initialize user management service."""
        self.auth_service = AuthenticationService(secret_key)
        self.org_service = OrganizationService(self.auth_service)
        self.audit_logger = AuditLogger()
    
    async def register_user(
        self,
        email: str,
        username: str,
        password: str,
        full_name: str = ""
    ) -> User:
        """Register a new user."""
        user = await self.auth_service.register(
            email=email,
            username=username,
            password=password,
            full_name=full_name,
        )
        
        await self.audit_logger.log(
            user_id=user.id,
            action="register",
            resource_type="user",
            resource_id=user.id,
        )
        
        return user
    
    async def login(
        self,
        email_or_username: str,
        password: str,
        device_info: str = "",
        ip_address: str = ""
    ) -> tuple[User, AuthToken]:
        """Login a user."""
        user, tokens = await self.auth_service.authenticate(
            email_or_username=email_or_username,
            password=password,
            device_info=device_info,
            ip_address=ip_address,
        )
        
        await self.audit_logger.log(
            user_id=user.id,
            action="login",
            resource_type="session",
            ip_address=ip_address,
        )
        
        return user, tokens
    
    async def create_team(
        self,
        user_id: str,
        name: str
    ) -> Organization:
        """Create a new team/organization."""
        org = await self.org_service.create_organization(
            name=name,
            owner_id=user_id,
        )
        
        await self.audit_logger.log(
            user_id=user_id,
            action="create",
            resource_type="organization",
            resource_id=org.id,
            details={"name": name},
        )
        
        return org
    
    async def invite_team_member(
        self,
        inviter_id: str,
        org_id: str,
        email: str,
        role: UserRole = UserRole.MEMBER
    ) -> tuple[Invitation, str]:
        """Invite a member to the team."""
        invitation, token = await self.org_service.create_invitation(
            org_id=org_id,
            email=email,
            role=role,
            invited_by=inviter_id,
        )
        
        await self.audit_logger.log(
            user_id=inviter_id,
            action="invite",
            resource_type="organization_member",
            details={"email": email, "role": role.value},
        )
        
        return invitation, token
    
    async def get_user_context(
        self,
        user_id: str
    ) -> dict[str, Any]:
        """Get full user context including org and permissions."""
        user = self.auth_service._users.get(user_id)
        if not user:
            return {}
        
        org = None
        members = []
        if user.organization_id:
            org = await self.org_service.get_organization(user.organization_id)
            members = await self.org_service.get_members(user.organization_id)
        
        return {
            "user": user,
            "organization": org,
            "team_members": [(m, u.full_name) for m, u in members],
            "permissions": list(ROLE_PERMISSIONS.get(user.role, set())),
            "api_keys": self.auth_service.get_user_api_keys(user_id),
        }


# =============================================================================
# FACTORY FUNCTION
# =============================================================================

def create_user_management_service(
    secret_key: Optional[str] = None
) -> UserManagementService:
    """Create a configured user management service."""
    import os
    key = secret_key or os.getenv("SECRET_KEY", "development-secret-key")
    return UserManagementService(secret_key=key)


# =============================================================================
# MODULE EXPORTS
# =============================================================================

__all__ = [
    # Enums
    'UserRole',
    'Permission',
    'ROLE_PERMISSIONS',
    
    # Models
    'User',
    'UserSession',
    'APIKey',
    'Organization',
    'OrganizationMember',
    'Invitation',
    'AuthToken',
    'AuditLogEntry',
    
    # Utilities
    'PasswordHasher',
    'TokenGenerator',
    
    # Services
    'AuthenticationService',
    'OrganizationService',
    'AuditLogger',
    'UserManagementService',
    
    # Decorators
    'require_auth',
    'require_permission',
    'require_role',
    
    # Factory
    'create_user_management_service',
]
