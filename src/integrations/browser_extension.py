"""
Browser Extension API
=====================

Backend API for the Growth Engine browser extension.
Enables one-click opportunity capture from any website.

Features:
- Capture opportunities from job boards
- Extract structured data from pages
- Auto-score captured opportunities
- Sync with main Growth Engine database
"""

import asyncio
import hashlib
import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional
from urllib.parse import urlparse

from pydantic import BaseModel, Field, HttpUrl
from fastapi import APIRouter, HTTPException, BackgroundTasks, Header
from fastapi.responses import JSONResponse


# =============================================================================
# MODELS
# =============================================================================

class CaptureSource(Enum):
    """Source of captured opportunity."""
    LINKEDIN = "linkedin"
    INDEED = "indeed"
    GLASSDOOR = "glassdoor"
    ANGELLIST = "angellist"
    WELLFOUND = "wellfound"
    YCOMBINATOR = "ycombinator"
    GREENHOUSE = "greenhouse"
    LEVER = "lever"
    WORKDAY = "workday"
    CUSTOM = "custom"


class CapturedOpportunity(BaseModel):
    """Data captured from browser extension."""
    url: str
    title: str
    organization: Optional[str] = None
    description: Optional[str] = None
    requirements: list[str] = Field(default_factory=list)
    salary_range: Optional[str] = None
    location: Optional[str] = None
    deadline: Optional[str] = None
    opportunity_type: str = "job"
    
    # Metadata
    source: CaptureSource = CaptureSource.CUSTOM
    captured_at: datetime = Field(default_factory=datetime.utcnow)
    page_html: Optional[str] = None
    screenshot_base64: Optional[str] = None
    
    # User context
    user_notes: Optional[str] = None
    priority: int = Field(default=0, ge=0, le=5)
    tags: list[str] = Field(default_factory=list)


class CaptureResponse(BaseModel):
    """Response after capturing an opportunity."""
    success: bool
    opportunity_id: Optional[str] = None
    fit_score: Optional[float] = None
    tier: Optional[str] = None
    message: str
    duplicate: bool = False
    existing_id: Optional[str] = None


class ExtensionAuth(BaseModel):
    """Authentication for browser extension."""
    user_id: str
    api_key: str
    device_id: Optional[str] = None


class SyncStatus(BaseModel):
    """Sync status for extension."""
    last_sync: Optional[datetime] = None
    pending_captures: int = 0
    total_captured: int = 0
    storage_used_bytes: int = 0


class ExtensionSettings(BaseModel):
    """User settings for browser extension."""
    auto_capture: bool = True
    auto_score: bool = True
    show_notifications: bool = True
    capture_screenshots: bool = False
    supported_sites: list[str] = Field(default_factory=lambda: [
        "linkedin.com", "indeed.com", "glassdoor.com",
        "wellfound.com", "ycombinator.com", "greenhouse.io",
        "lever.co", "workday.com"
    ])
    min_auto_score: float = 0.0
    default_tags: list[str] = Field(default_factory=list)


# =============================================================================
# URL PARSERS
# =============================================================================

class URLParser:
    """Parse and extract data from job board URLs."""
    
    PATTERNS = {
        CaptureSource.LINKEDIN: [
            r"linkedin\.com/jobs/view/(\d+)",
            r"linkedin\.com/jobs/.*?currentJobId=(\d+)",
        ],
        CaptureSource.INDEED: [
            r"indeed\.com/viewjob\?jk=([a-f0-9]+)",
            r"indeed\.com/.*?vjk=([a-f0-9]+)",
        ],
        CaptureSource.GLASSDOOR: [
            r"glassdoor\.com/job-listing/.*?jobListingId=(\d+)",
        ],
        CaptureSource.ANGELLIST: [
            r"angel\.co/company/([^/]+)/jobs/(\d+)",
        ],
        CaptureSource.WELLFOUND: [
            r"wellfound\.com/company/([^/]+)/jobs/(\d+)",
        ],
        CaptureSource.YCOMBINATOR: [
            r"ycombinator\.com/companies/([^/]+)/jobs/([^/]+)",
            r"workatastartup\.com/jobs/(\d+)",
        ],
        CaptureSource.GREENHOUSE: [
            r"boards\.greenhouse\.io/([^/]+)/jobs/(\d+)",
        ],
        CaptureSource.LEVER: [
            r"jobs\.lever\.co/([^/]+)/([a-f0-9-]+)",
        ],
        CaptureSource.WORKDAY: [
            r"([^.]+)\.wd\d+\.myworkdayjobs\.com/.*?/job/([^/]+)/([^/]+)",
        ],
    }
    
    @classmethod
    def detect_source(cls, url: str) -> CaptureSource:
        """Detect the source from URL."""
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        
        for source, patterns in cls.PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, url, re.IGNORECASE):
                    return source
        
        # Check domain directly
        domain_mapping = {
            "linkedin.com": CaptureSource.LINKEDIN,
            "indeed.com": CaptureSource.INDEED,
            "glassdoor.com": CaptureSource.GLASSDOOR,
            "angel.co": CaptureSource.ANGELLIST,
            "wellfound.com": CaptureSource.WELLFOUND,
            "ycombinator.com": CaptureSource.YCOMBINATOR,
            "workatastartup.com": CaptureSource.YCOMBINATOR,
        }
        
        for key, source in domain_mapping.items():
            if key in domain:
                return source
        
        return CaptureSource.CUSTOM
    
    @classmethod
    def extract_job_id(cls, url: str, source: CaptureSource) -> Optional[str]:
        """Extract job ID from URL."""
        patterns = cls.PATTERNS.get(source, [])
        
        for pattern in patterns:
            match = re.search(pattern, url, re.IGNORECASE)
            if match:
                groups = match.groups()
                return "_".join(groups) if len(groups) > 1 else groups[0]
        
        return None


# =============================================================================
# CONTENT EXTRACTOR
# =============================================================================

class ContentExtractor:
    """Extract structured data from page HTML."""
    
    @staticmethod
    async def extract_from_html(
        html: str,
        url: str,
        source: CaptureSource
    ) -> dict[str, Any]:
        """
        Extract job details from HTML.
        
        Args:
            html: Page HTML content
            url: Page URL
            source: Detected source
            
        Returns:
            Extracted structured data
        """
        from bs4 import BeautifulSoup
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remove scripts and styles
        for tag in soup(['script', 'style', 'nav', 'footer', 'header']):
            tag.decompose()
        
        extracted = {
            "title": None,
            "organization": None,
            "description": None,
            "requirements": [],
            "location": None,
            "salary_range": None,
        }
        
        # Source-specific extraction
        extractors = {
            CaptureSource.LINKEDIN: ContentExtractor._extract_linkedin,
            CaptureSource.GREENHOUSE: ContentExtractor._extract_greenhouse,
            CaptureSource.LEVER: ContentExtractor._extract_lever,
        }
        
        extractor = extractors.get(source, ContentExtractor._extract_generic)
        extracted.update(extractor(soup))
        
        return extracted
    
    @staticmethod
    def _extract_linkedin(soup) -> dict:
        """Extract from LinkedIn job page."""
        data = {}
        
        # Title
        title_elem = soup.find('h1', class_='top-card-layout__title')
        if title_elem:
            data["title"] = title_elem.get_text(strip=True)
        
        # Company
        company_elem = soup.find('a', class_='topcard__org-name-link')
        if company_elem:
            data["organization"] = company_elem.get_text(strip=True)
        
        # Description
        desc_elem = soup.find('div', class_='description__text')
        if desc_elem:
            data["description"] = desc_elem.get_text(strip=True)
        
        # Location
        loc_elem = soup.find('span', class_='topcard__flavor--bullet')
        if loc_elem:
            data["location"] = loc_elem.get_text(strip=True)
        
        return data
    
    @staticmethod
    def _extract_greenhouse(soup) -> dict:
        """Extract from Greenhouse job page."""
        data = {}
        
        title_elem = soup.find('h1', class_='app-title')
        if title_elem:
            data["title"] = title_elem.get_text(strip=True)
        
        company_elem = soup.find('span', class_='company-name')
        if company_elem:
            data["organization"] = company_elem.get_text(strip=True)
        
        content_elem = soup.find('div', id='content')
        if content_elem:
            data["description"] = content_elem.get_text(strip=True)[:5000]
        
        return data
    
    @staticmethod
    def _extract_lever(soup) -> dict:
        """Extract from Lever job page."""
        data = {}
        
        title_elem = soup.find('h2', class_='posting-headline')
        if title_elem:
            h2 = title_elem.find('h2')
            if h2:
                data["title"] = h2.get_text(strip=True)
        
        location_elem = soup.find('div', class_='location')
        if location_elem:
            data["location"] = location_elem.get_text(strip=True)
        
        return data
    
    @staticmethod
    def _extract_generic(soup) -> dict:
        """Generic extraction for unknown sources."""
        data = {}
        
        # Try common patterns
        # Title from h1
        h1 = soup.find('h1')
        if h1:
            data["title"] = h1.get_text(strip=True)
        
        # Try to find job description
        for selector in ['[class*="description"]', '[class*="job-content"]', 
                         '[id*="description"]', 'article', 'main']:
            elem = soup.select_one(selector)
            if elem:
                text = elem.get_text(strip=True)
                if len(text) > 100:
                    data["description"] = text[:5000]
                    break
        
        # Try to find requirements
        for keyword in ['requirements', 'qualifications', 'skills']:
            elems = soup.find_all(string=re.compile(keyword, re.I))
            for elem in elems:
                parent = elem.find_parent(['div', 'section', 'ul'])
                if parent:
                    items = parent.find_all('li')
                    if items:
                        data["requirements"] = [li.get_text(strip=True) for li in items[:20]]
                        break
        
        return data


# =============================================================================
# EXTENSION API SERVICE
# =============================================================================

class ExtensionAPI:
    """
    Backend service for browser extension.
    
    Handles capture requests, scoring, and sync.
    """
    
    def __init__(self):
        """Initialize extension API."""
        self._captured: dict[str, CapturedOpportunity] = {}
        self._user_settings: dict[str, ExtensionSettings] = {}
    
    async def capture_opportunity(
        self,
        data: CapturedOpportunity,
        user_id: str
    ) -> CaptureResponse:
        """
        Capture an opportunity from the browser extension.
        
        Args:
            data: Captured opportunity data
            user_id: User ID
            
        Returns:
            Capture response with score and status
        """
        # Detect source if not provided
        if data.source == CaptureSource.CUSTOM:
            data.source = URLParser.detect_source(data.url)
        
        # Generate opportunity ID
        url_hash = hashlib.md5(data.url.encode()).hexdigest()[:12]
        opportunity_id = f"cap_{data.source.value}_{url_hash}"
        
        # Check for duplicates
        existing = await self._check_duplicate(data.url, user_id)
        if existing:
            return CaptureResponse(
                success=True,
                opportunity_id=existing,
                message="Opportunity already captured",
                duplicate=True,
                existing_id=existing
            )
        
        # Extract additional data from HTML if provided
        if data.page_html:
            extracted = await ContentExtractor.extract_from_html(
                data.page_html,
                data.url,
                data.source
            )
            
            # Fill in missing fields
            if not data.title and extracted.get("title"):
                data.title = extracted["title"]
            if not data.organization and extracted.get("organization"):
                data.organization = extracted["organization"]
            if not data.description and extracted.get("description"):
                data.description = extracted["description"]
            if not data.requirements and extracted.get("requirements"):
                data.requirements = extracted["requirements"]
            if not data.location and extracted.get("location"):
                data.location = extracted["location"]
        
        # Score the opportunity
        fit_score, tier = await self._score_opportunity(data)
        
        # Store captured opportunity
        self._captured[opportunity_id] = data
        
        # Save to database
        await self._save_to_database(opportunity_id, data, user_id, fit_score, tier)
        
        return CaptureResponse(
            success=True,
            opportunity_id=opportunity_id,
            fit_score=fit_score,
            tier=tier,
            message=f"Captured: {data.title or 'Opportunity'}"
        )
    
    async def _check_duplicate(self, url: str, user_id: str) -> Optional[str]:
        """Check if opportunity already exists."""
        url_hash = hashlib.md5(url.encode()).hexdigest()[:12]
        
        # Check in-memory cache
        for opp_id, opp in self._captured.items():
            if url_hash in opp_id:
                return opp_id
        
        # Check database
        try:
            from src.data.database import async_session
            from src.data.models import Opportunity
            from sqlalchemy import select
            
            async with async_session() as session:
                result = await session.execute(
                    select(Opportunity).where(Opportunity.source_url == url)
                )
                existing = result.scalar_one_or_none()
                if existing:
                    return str(existing.id)
        except Exception:
            pass
        
        return None
    
    async def _score_opportunity(
        self,
        data: CapturedOpportunity
    ) -> tuple[float, str]:
        """Score the captured opportunity."""
        try:
            from src.scoring import ScoringEngine
            
            engine = ScoringEngine()
            result = await engine.score_opportunity({
                "title": data.title,
                "organization": data.organization,
                "description": data.description,
                "requirements": data.requirements,
                "location": data.location,
                "type": data.opportunity_type,
            })
            
            return result.get("fit_score", 0.5), result.get("tier", "TIER_2")
        except Exception:
            return 0.5, "TIER_2"
    
    async def _save_to_database(
        self,
        opportunity_id: str,
        data: CapturedOpportunity,
        user_id: str,
        fit_score: float,
        tier: str
    ) -> None:
        """Save captured opportunity to database."""
        try:
            from src.data.database import async_session
            from src.data.models import Opportunity
            from src.models import OpportunityType, OpportunityTier
            
            async with async_session() as session:
                opp = Opportunity(
                    id=opportunity_id,
                    title=data.title,
                    organization=data.organization,
                    description=data.description,
                    requirements=data.requirements,
                    source_url=data.url,
                    source=data.source.value,
                    type=OpportunityType(data.opportunity_type),
                    fit_score=fit_score,
                    tier=OpportunityTier[tier],
                    location=data.location,
                    deadline=data.deadline,
                    discovered_at=data.captured_at,
                    user_id=user_id,
                )
                session.add(opp)
                await session.commit()
        except Exception as e:
            # Log but don't fail - opportunity is still in memory
            print(f"Failed to save to database: {e}")
    
    async def get_user_settings(self, user_id: str) -> ExtensionSettings:
        """Get user's extension settings."""
        if user_id not in self._user_settings:
            self._user_settings[user_id] = ExtensionSettings()
        return self._user_settings[user_id]
    
    async def update_user_settings(
        self,
        user_id: str,
        settings: ExtensionSettings
    ) -> ExtensionSettings:
        """Update user's extension settings."""
        self._user_settings[user_id] = settings
        return settings
    
    async def get_sync_status(self, user_id: str) -> SyncStatus:
        """Get sync status for user."""
        user_captures = [
            opp for opp_id, opp in self._captured.items()
        ]
        
        return SyncStatus(
            last_sync=datetime.utcnow(),
            pending_captures=0,
            total_captured=len(user_captures),
            storage_used_bytes=sum(
                len(str(opp.model_dump()).encode()) 
                for opp in user_captures
            )
        )
    
    async def get_recent_captures(
        self,
        user_id: str,
        limit: int = 20
    ) -> list[dict]:
        """Get recent captures for user."""
        captures = list(self._captured.items())[-limit:]
        return [
            {
                "id": opp_id,
                "title": opp.title,
                "organization": opp.organization,
                "url": opp.url,
                "captured_at": opp.captured_at.isoformat(),
                "source": opp.source.value,
            }
            for opp_id, opp in captures
        ]


# =============================================================================
# FASTAPI ROUTER
# =============================================================================

def create_extension_router() -> APIRouter:
    """Create FastAPI router for extension endpoints."""
    router = APIRouter(prefix="/extension", tags=["Browser Extension"])
    api = ExtensionAPI()
    
    @router.post("/capture", response_model=CaptureResponse)
    async def capture_opportunity(
        data: CapturedOpportunity,
        background_tasks: BackgroundTasks,
        x_user_id: str = Header(..., alias="X-User-ID"),
        x_api_key: str = Header(..., alias="X-API-Key"),
    ):
        """
        Capture an opportunity from the browser extension.
        
        Send the page URL and any extracted data to create a new opportunity.
        """
        # TODO: Validate API key
        return await api.capture_opportunity(data, x_user_id)
    
    @router.get("/settings", response_model=ExtensionSettings)
    async def get_settings(
        x_user_id: str = Header(..., alias="X-User-ID"),
    ):
        """Get user's extension settings."""
        return await api.get_user_settings(x_user_id)
    
    @router.put("/settings", response_model=ExtensionSettings)
    async def update_settings(
        settings: ExtensionSettings,
        x_user_id: str = Header(..., alias="X-User-ID"),
    ):
        """Update user's extension settings."""
        return await api.update_user_settings(x_user_id, settings)
    
    @router.get("/sync/status", response_model=SyncStatus)
    async def sync_status(
        x_user_id: str = Header(..., alias="X-User-ID"),
    ):
        """Get sync status for the extension."""
        return await api.get_sync_status(x_user_id)
    
    @router.get("/captures/recent")
    async def recent_captures(
        limit: int = 20,
        x_user_id: str = Header(..., alias="X-User-ID"),
    ):
        """Get recent captures."""
        return await api.get_recent_captures(x_user_id, limit)
    
    @router.post("/parse-url")
    async def parse_url(url: str):
        """Parse a URL to detect source and extract job ID."""
        source = URLParser.detect_source(url)
        job_id = URLParser.extract_job_id(url, source)
        
        return {
            "url": url,
            "source": source.value,
            "job_id": job_id,
            "supported": source != CaptureSource.CUSTOM,
        }
    
    return router


# =============================================================================
# MODULE EXPORTS
# =============================================================================

__all__ = [
    'CaptureSource',
    'CapturedOpportunity',
    'CaptureResponse',
    'ExtensionAuth',
    'SyncStatus',
    'ExtensionSettings',
    'URLParser',
    'ContentExtractor',
    'ExtensionAPI',
    'create_extension_router',
]
