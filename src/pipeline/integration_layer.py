"""
Integration Layer for Application Automation

Provides unified interfaces and adapters for connecting with external platforms,
APIs, and services. Handles authentication, rate limiting, data transformation,
and error handling for seamless external integrations.
"""

import asyncio
import aiohttp
import json
from typing import Dict, List, Optional, Any, Callable, Type
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class IntegrationType(Enum):
    """Types of external integrations"""
    JOB_BOARD = "job_board"          # LinkedIn, Indeed, etc.
    ATS = "ats"                      # Applicant Tracking Systems
    EMAIL = "email"                  # Email providers
    CALENDAR = "calendar"            # Calendar systems
    SOCIAL = "social"                # Social media platforms
    DOCUMENT = "document"            # Document storage/sharing
    ANALYTICS = "analytics"          # Analytics platforms
    CRM = "crm"                      # Customer Relationship Management
    WEBHOOK = "webhook"              # Webhook endpoints


class IntegrationStatus(Enum):
    """Status of integration connections"""
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    AUTHENTICATION_REQUIRED = "auth_required"
    ERROR = "error"
    RATE_LIMITED = "rate_limited"
    MAINTENANCE = "maintenance"


@dataclass
class APICredentials:
    """API credentials for external services"""
    service_name: str
    api_key: Optional[str] = None
    secret_key: Optional[str] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    expires_at: Optional[datetime] = None
    additional_params: Dict[str, Any] = field(default_factory=dict)
    
    def is_expired(self) -> bool:
        """Check if credentials are expired"""
        if not self.expires_at:
            return False
        return datetime.utcnow() >= self.expires_at
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'service_name': self.service_name,
            'has_api_key': bool(self.api_key),
            'has_access_token': bool(self.access_token),
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'is_expired': self.is_expired()
        }


@dataclass
class IntegrationConfig:
    """Configuration for external integration"""
    service_name: str
    integration_type: IntegrationType
    base_url: str
    api_version: str = "v1"
    rate_limit_requests: int = 100
    rate_limit_period: int = 3600  # seconds
    timeout: int = 30
    retry_attempts: int = 3
    retry_delay: int = 5
    authentication_method: str = "api_key"  # api_key, oauth, bearer_token
    required_scopes: List[str] = field(default_factory=list)
    custom_headers: Dict[str, str] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'service_name': self.service_name,
            'integration_type': self.integration_type.value,
            'base_url': self.base_url,
            'api_version': self.api_version,
            'rate_limit_requests': self.rate_limit_requests,
            'rate_limit_period': self.rate_limit_period,
            'authentication_method': self.authentication_method,
            'required_scopes': self.required_scopes
        }


class RateLimiter:
    """Rate limiting for API calls"""
    
    def __init__(self, requests_per_period: int, period_seconds: int):
        self.requests_per_period = requests_per_period
        self.period_seconds = period_seconds
        self.requests = []
        self.lock = asyncio.Lock()
    
    async def acquire(self) -> bool:
        """Acquire rate limit slot"""
        async with self.lock:
            now = datetime.utcnow()
            
            # Remove old requests outside the period
            cutoff = now - timedelta(seconds=self.period_seconds)
            self.requests = [req_time for req_time in self.requests if req_time > cutoff]
            
            # Check if we can make a new request
            if len(self.requests) < self.requests_per_period:
                self.requests.append(now)
                return True
            
            return False
    
    def time_until_next_slot(self) -> Optional[int]:
        """Get seconds until next rate limit slot is available"""
        if not self.requests:
            return 0
        
        oldest_request = min(self.requests)
        next_slot = oldest_request + timedelta(seconds=self.period_seconds)
        wait_time = (next_slot - datetime.utcnow()).total_seconds()
        
        return max(0, int(wait_time))


class BaseIntegrationAdapter:
    """Base class for external service integrations"""
    
    def __init__(self, config: IntegrationConfig, credentials: APICredentials):
        self.config = config
        self.credentials = credentials
        self.status = IntegrationStatus.DISCONNECTED
        self.rate_limiter = RateLimiter(
            config.rate_limit_requests,
            config.rate_limit_period
        )
        self.session: Optional[aiohttp.ClientSession] = None
        self.last_error: Optional[str] = None
        self.connection_time: Optional[datetime] = None
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.disconnect()
    
    async def connect(self) -> bool:
        """Establish connection to the external service"""
        try:
            if not self.session:
                timeout = aiohttp.ClientTimeout(total=self.config.timeout)
                self.session = aiohttp.ClientSession(timeout=timeout)
            
            # Test connection
            if await self._test_connection():
                self.status = IntegrationStatus.CONNECTED
                self.connection_time = datetime.utcnow()
                logger.info(f"Connected to {self.config.service_name}")
                return True
            else:
                self.status = IntegrationStatus.ERROR
                return False
                
        except Exception as e:
            self.status = IntegrationStatus.ERROR
            self.last_error = str(e)
            logger.error(f"Failed to connect to {self.config.service_name}: {str(e)}")
            return False
    
    async def disconnect(self):
        """Close connection to external service"""
        if self.session:
            await self.session.close()
            self.session = None
        
        self.status = IntegrationStatus.DISCONNECTED
        logger.info(f"Disconnected from {self.config.service_name}")
    
    async def _test_connection(self) -> bool:
        """Test connection to service (override in subclasses)"""
        return True
    
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Dict[str, Any] = None,
        params: Dict[str, Any] = None,
        headers: Dict[str, str] = None
    ) -> Dict[str, Any]:
        """Make authenticated API request with rate limiting"""
        
        # Wait for rate limit
        while not await self.rate_limiter.acquire():
            wait_time = self.rate_limiter.time_until_next_slot()
            if wait_time > 0:
                await asyncio.sleep(wait_time)
        
        # Prepare request
        url = f"{self.config.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        request_headers = self._build_headers(headers)
        
        # Make request with retries
        for attempt in range(self.config.retry_attempts):
            try:
                async with self.session.request(
                    method,
                    url,
                    json=data,
                    params=params,
                    headers=request_headers
                ) as response:
                    
                    if response.status == 429:  # Rate limited
                        self.status = IntegrationStatus.RATE_LIMITED
                        retry_after = int(response.headers.get('Retry-After', self.config.retry_delay))
                        await asyncio.sleep(retry_after)
                        continue
                    
                    if response.status == 401:  # Unauthorized
                        self.status = IntegrationStatus.AUTHENTICATION_REQUIRED
                        raise Exception("Authentication required")
                    
                    response.raise_for_status()
                    
                    # Parse response
                    content_type = response.headers.get('Content-Type', '')
                    if 'application/json' in content_type:
                        return await response.json()
                    else:
                        return {'content': await response.text()}
                        
            except aiohttp.ClientError as e:
                if attempt == self.config.retry_attempts - 1:
                    self.status = IntegrationStatus.ERROR
                    self.last_error = str(e)
                    raise
                await asyncio.sleep(self.config.retry_delay)
        
        raise Exception(f"Failed after {self.config.retry_attempts} attempts")
    
    def _build_headers(self, additional_headers: Dict[str, str] = None) -> Dict[str, str]:
        """Build headers with authentication"""
        headers = {
            'User-Agent': 'Growth-Engine-Integration/1.0',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        
        # Add custom headers from config
        headers.update(self.config.custom_headers)
        
        # Add authentication headers
        if self.config.authentication_method == "api_key" and self.credentials.api_key:
            headers['Authorization'] = f'Bearer {self.credentials.api_key}'
        elif self.config.authentication_method == "bearer_token" and self.credentials.access_token:
            headers['Authorization'] = f'Bearer {self.credentials.access_token}'
        
        # Add additional headers
        if additional_headers:
            headers.update(additional_headers)
        
        return headers
    
    def get_status(self) -> Dict[str, Any]:
        """Get integration status"""
        return {
            'service_name': self.config.service_name,
            'integration_type': self.config.integration_type.value,
            'status': self.status.value,
            'connected_at': self.connection_time.isoformat() if self.connection_time else None,
            'last_error': self.last_error,
            'credentials_valid': not self.credentials.is_expired() if self.credentials.expires_at else True
        }


class LinkedInIntegrationAdapter(BaseIntegrationAdapter):
    """LinkedIn API integration"""
    
    async def _test_connection(self) -> bool:
        """Test LinkedIn API connection"""
        try:
            response = await self._make_request('GET', '/v2/me')
            return 'id' in response
        except:
            return False
    
    async def get_profile(self) -> Dict[str, Any]:
        """Get user profile from LinkedIn"""
        return await self._make_request('GET', '/v2/me')
    
    async def search_jobs(self, query: str, location: str = None, limit: int = 25) -> List[Dict[str, Any]]:
        """Search for jobs on LinkedIn"""
        params = {
            'keywords': query,
            'count': limit
        }
        if location:
            params['location'] = location
        
        response = await self._make_request('GET', '/v2/jobSearch', params=params)
        return response.get('elements', [])
    
    async def submit_application(self, job_id: str, application_data: Dict[str, Any]) -> Dict[str, Any]:
        """Submit job application via LinkedIn"""
        data = {
            'jobId': job_id,
            **application_data
        }
        return await self._make_request('POST', '/v2/applications', data=data)


class EmailIntegrationAdapter(BaseIntegrationAdapter):
    """Email service integration (Generic SMTP/API)"""
    
    async def _test_connection(self) -> bool:
        """Test email service connection"""
        # Simplified test - would implement actual email service test
        return True
    
    async def send_email(
        self,
        to_address: str,
        subject: str,
        content: str,
        content_type: str = 'text/html',
        attachments: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Send email through the service"""
        data = {
            'to': to_address,
            'subject': subject,
            'content': content,
            'content_type': content_type,
            'attachments': attachments or []
        }
        return await self._make_request('POST', '/send', data=data)


class WebhookIntegrationAdapter(BaseIntegrationAdapter):
    """Webhook integration for receiving external events"""
    
    async def _test_connection(self) -> bool:
        """Test webhook endpoint"""
        # Would implement webhook verification
        return True
    
    async def register_webhook(self, url: str, events: List[str]) -> Dict[str, Any]:
        """Register webhook for events"""
        data = {
            'url': url,
            'events': events
        }
        return await self._make_request('POST', '/webhooks', data=data)
    
    async def process_webhook_event(self, event_data: Dict[str, Any]) -> bool:
        """Process incoming webhook event"""
        # Override in specific implementations
        logger.info(f"Received webhook event: {event_data.get('type', 'unknown')}")
        return True


class IntegrationManager:
    """Main manager for all external integrations"""
    
    def __init__(self):
        self.adapters: Dict[str, BaseIntegrationAdapter] = {}
        self.configs: Dict[str, IntegrationConfig] = {}
        self.credentials_store: Dict[str, APICredentials] = {}
        self.adapter_classes: Dict[IntegrationType, Type[BaseIntegrationAdapter]] = {
            IntegrationType.JOB_BOARD: LinkedInIntegrationAdapter,
            IntegrationType.EMAIL: EmailIntegrationAdapter,
            IntegrationType.WEBHOOK: WebhookIntegrationAdapter,
        }
        
        # Load default configurations
        self._load_default_configs()
    
    def _load_default_configs(self):
        """Load default integration configurations"""
        
        # LinkedIn
        self.configs['linkedin'] = IntegrationConfig(
            service_name='linkedin',
            integration_type=IntegrationType.JOB_BOARD,
            base_url='https://api.linkedin.com',
            api_version='v2',
            rate_limit_requests=100,
            rate_limit_period=3600,
            authentication_method='oauth',
            required_scopes=['r_liteprofile', 'r_emailaddress', 'w_member_social']
        )
        
        # Email (Generic)
        self.configs['email'] = IntegrationConfig(
            service_name='email',
            integration_type=IntegrationType.EMAIL,
            base_url='https://api.emailservice.com',
            api_version='v1',
            rate_limit_requests=1000,
            rate_limit_period=3600,
            authentication_method='api_key'
        )
        
        # Webhook
        self.configs['webhook'] = IntegrationConfig(
            service_name='webhook',
            integration_type=IntegrationType.WEBHOOK,
            base_url='https://api.webhookservice.com',
            api_version='v1',
            rate_limit_requests=500,
            rate_limit_period=3600,
            authentication_method='api_key'
        )
    
    def add_credentials(self, service_name: str, credentials: APICredentials):
        """Add credentials for a service"""
        self.credentials_store[service_name] = credentials
        logger.info(f"Added credentials for {service_name}")
    
    def add_config(self, config: IntegrationConfig):
        """Add integration configuration"""
        self.configs[config.service_name] = config
        logger.info(f"Added configuration for {config.service_name}")
    
    async def connect_service(self, service_name: str) -> bool:
        """Connect to a specific service"""
        
        if service_name not in self.configs:
            logger.error(f"No configuration found for {service_name}")
            return False
        
        if service_name not in self.credentials_store:
            logger.error(f"No credentials found for {service_name}")
            return False
        
        config = self.configs[service_name]
        credentials = self.credentials_store[service_name]
        
        # Get adapter class
        adapter_class = self.adapter_classes.get(config.integration_type, BaseIntegrationAdapter)
        
        # Create and connect adapter
        adapter = adapter_class(config, credentials)
        
        if await adapter.connect():
            self.adapters[service_name] = adapter
            return True
        
        return False
    
    async def disconnect_service(self, service_name: str):
        """Disconnect from a service"""
        if service_name in self.adapters:
            await self.adapters[service_name].disconnect()
            del self.adapters[service_name]
    
    def get_adapter(self, service_name: str) -> Optional[BaseIntegrationAdapter]:
        """Get adapter for a service"""
        return self.adapters.get(service_name)
    
    def is_connected(self, service_name: str) -> bool:
        """Check if service is connected"""
        adapter = self.adapters.get(service_name)
        return adapter and adapter.status == IntegrationStatus.CONNECTED
    
    def get_all_statuses(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all integrations"""
        statuses = {}
        
        for service_name, config in self.configs.items():
            if service_name in self.adapters:
                statuses[service_name] = self.adapters[service_name].get_status()
            else:
                statuses[service_name] = {
                    'service_name': service_name,
                    'integration_type': config.integration_type.value,
                    'status': IntegrationStatus.DISCONNECTED.value,
                    'connected_at': None,
                    'last_error': None,
                    'credentials_valid': service_name in self.credentials_store
                }
        
        return statuses
    
    async def test_all_connections(self) -> Dict[str, bool]:
        """Test all configured connections"""
        results = {}
        
        for service_name in self.configs.keys():
            try:
                if service_name in self.adapters:
                    # Test existing connection
                    adapter = self.adapters[service_name]
                    results[service_name] = await adapter._test_connection()
                else:
                    # Try to connect and test
                    results[service_name] = await self.connect_service(service_name)
            except Exception as e:
                logger.error(f"Connection test failed for {service_name}: {str(e)}")
                results[service_name] = False
        
        return results
    
    async def cleanup(self):
        """Clean up all connections"""
        for service_name in list(self.adapters.keys()):
            await self.disconnect_service(service_name)


# Global integration manager
global_integration_manager = IntegrationManager()