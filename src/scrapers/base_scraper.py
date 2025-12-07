"""
Base Scraper Class
==================
Foundation for all opportunity scrapers with rate limiting,
proxy rotation, error handling, and health checks.

Phase 1 Improvements:
- Enhanced retry logic with exponential backoff
- Circuit breaker pattern for failing scrapers
- Comprehensive health checks
- Improved error categorization
- Request/response metrics
"""

import asyncio
import httpx
import logging
import random
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import json
import hashlib
from collections import deque

logger = logging.getLogger(__name__)


class ScraperStatus(Enum):
    """Scraper health status"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    CIRCUIT_OPEN = "circuit_open"


@dataclass
class ScraperMetrics:
    """Track scraper performance metrics"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_opportunities: int = 0
    avg_response_time: float = 0.0
    last_success: Optional[datetime] = None
    last_failure: Optional[datetime] = None
    last_error: Optional[str] = None
    consecutive_failures: int = 0
    circuit_open_until: Optional[datetime] = None
    
    @property
    def success_rate(self) -> float:
        if self.total_requests == 0:
            return 1.0
        return self.successful_requests / self.total_requests
    
    @property
    def status(self) -> ScraperStatus:
        # Check if circuit breaker is open
        if self.circuit_open_until and datetime.now() < self.circuit_open_until:
            return ScraperStatus.CIRCUIT_OPEN
        
        if self.consecutive_failures >= 5:
            return ScraperStatus.UNHEALTHY
        elif self.consecutive_failures >= 2 or self.success_rate < 0.8:
            return ScraperStatus.DEGRADED
        return ScraperStatus.HEALTHY
    
    def record_success(self, response_time: float, opportunities_count: int = 0):
        self.total_requests += 1
        self.successful_requests += 1
        self.total_opportunities += opportunities_count
        self.last_success = datetime.now()
        self.consecutive_failures = 0
        self.circuit_open_until = None
        
        # Update rolling average response time
        if self.avg_response_time == 0:
            self.avg_response_time = response_time
        else:
            self.avg_response_time = (self.avg_response_time * 0.9) + (response_time * 0.1)
    
    def record_failure(self, error: str):
        self.total_requests += 1
        self.failed_requests += 1
        self.last_failure = datetime.now()
        self.last_error = error
        self.consecutive_failures += 1
        
        # Open circuit breaker after 5 consecutive failures
        if self.consecutive_failures >= 5:
            # Exponential backoff for circuit breaker
            backoff_minutes = min(2 ** (self.consecutive_failures - 5), 60)
            self.circuit_open_until = datetime.now() + timedelta(minutes=backoff_minutes)
            logger.warning(f"Circuit breaker opened for {backoff_minutes} minutes")
    
    def to_dict(self) -> Dict:
        return {
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
            "success_rate": round(self.success_rate * 100, 1),
            "total_opportunities": self.total_opportunities,
            "avg_response_time_ms": round(self.avg_response_time * 1000, 1),
            "status": self.status.value,
            "consecutive_failures": self.consecutive_failures,
            "last_success": self.last_success.isoformat() if self.last_success else None,
            "last_failure": self.last_failure.isoformat() if self.last_failure else None,
            "last_error": self.last_error,
        }


# Global metrics registry
_scraper_metrics: Dict[str, ScraperMetrics] = {}


def get_scraper_metrics(name: str) -> ScraperMetrics:
    """Get or create metrics for a scraper"""
    if name not in _scraper_metrics:
        _scraper_metrics[name] = ScraperMetrics()
    return _scraper_metrics[name]


def get_all_scraper_health() -> Dict[str, Any]:
    """Get health status of all scrapers"""
    return {
        name: metrics.to_dict() 
        for name, metrics in _scraper_metrics.items()
    }


@dataclass
class Opportunity:
    """Standardized opportunity data structure"""
    id: str
    title: str
    company: str
    location: str
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    description: str = ""
    requirements: List[str] = field(default_factory=list)
    apply_url: str = ""
    source: str = ""
    source_id: str = ""
    posted_date: Optional[datetime] = None
    deadline: Optional[datetime] = None
    opportunity_type: str = "job"  # job, grant, fellowship, competition, etc.
    remote: bool = False
    match_score: float = 0.0
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    scraped_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "title": self.title,
            "company": self.company,
            "location": self.location,
            "salary_min": self.salary_min,
            "salary_max": self.salary_max,
            "description": self.description,
            "requirements": self.requirements,
            "apply_url": self.apply_url,
            "source": self.source,
            "source_id": self.source_id,
            "posted_date": self.posted_date.isoformat() if self.posted_date else None,
            "deadline": self.deadline.isoformat() if self.deadline else None,
            "opportunity_type": self.opportunity_type,
            "remote": self.remote,
            "match_score": self.match_score,
            "tags": self.tags,
            "metadata": self.metadata,
            "scraped_at": self.scraped_at.isoformat()
        }
    
    @staticmethod
    def generate_id(source: str, source_id: str) -> str:
        """Generate unique opportunity ID"""
        return hashlib.md5(f"{source}:{source_id}".encode()).hexdigest()[:16]


class BaseScraper(ABC):
    """
    Base class for all opportunity scrapers.
    Implements common functionality like rate limiting, retries, caching,
    circuit breaker pattern, and health monitoring.
    """
    
    # Retry configuration
    RETRY_STATUS_CODES = {429, 500, 502, 503, 504}
    RETRY_EXCEPTIONS = (httpx.RequestError, httpx.TimeoutException, asyncio.TimeoutError)
    
    def __init__(
        self,
        name: str,
        base_url: str,
        rate_limit: float = 1.0,  # requests per second
        max_retries: int = 3,
        timeout: float = 30.0,
        headers: Optional[Dict[str, str]] = None,
        jitter: bool = True,  # Add randomness to delays
    ):
        self.name = name
        self.base_url = base_url
        self.rate_limit = rate_limit
        self.max_retries = max_retries
        self.timeout = timeout
        self.jitter = jitter
        self.last_request_time = datetime.min
        self.request_interval = timedelta(seconds=1.0 / rate_limit)
        
        # Get or create metrics for this scraper
        self.metrics = get_scraper_metrics(name)
        
        self.default_headers = {
            "User-Agent": self._get_random_user_agent(),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
        }
        if headers:
            self.default_headers.update(headers)
        
        self._client: Optional[httpx.AsyncClient] = None
        self._cache: Dict[str, Any] = {}
        self._cache_ttl = timedelta(minutes=15)
        self._recent_response_times: deque = deque(maxlen=100)
    
    @staticmethod
    def _get_random_user_agent() -> str:
        """Return a random user agent to avoid detection"""
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        ]
        return random.choice(user_agents)
    
    async def __aenter__(self):
        self._client = httpx.AsyncClient(
            timeout=self.timeout,
            headers=self.default_headers,
            follow_redirects=True
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._client:
            await self._client.aclose()
    
    async def _wait_for_rate_limit(self):
        """Enforce rate limiting between requests with optional jitter"""
        now = datetime.now()
        elapsed = now - self.last_request_time
        if elapsed < self.request_interval:
            wait_time = (self.request_interval - elapsed).total_seconds()
            # Add jitter (0-50% random variance) to avoid thundering herd
            if self.jitter:
                wait_time *= (1 + random.random() * 0.5)
            await asyncio.sleep(wait_time)
        self.last_request_time = datetime.now()
    
    def _calculate_backoff(self, attempt: int, base_delay: float = 1.0) -> float:
        """Calculate exponential backoff with jitter"""
        # Exponential backoff: 1s, 2s, 4s, 8s, ...
        delay = base_delay * (2 ** attempt)
        # Cap at 60 seconds
        delay = min(delay, 60.0)
        # Add jitter (±25%)
        if self.jitter:
            delay *= (0.75 + random.random() * 0.5)
        return delay
    
    def _is_circuit_open(self) -> bool:
        """Check if circuit breaker is open"""
        if self.metrics.circuit_open_until:
            if datetime.now() < self.metrics.circuit_open_until:
                return True
            # Circuit breaker timeout expired, allow retry
            self.metrics.circuit_open_until = None
        return False
    
    async def _make_request(
        self,
        method: str,
        url: str,
        **kwargs
    ) -> Optional[httpx.Response]:
        """Make HTTP request with enhanced retry logic and circuit breaker"""
        
        # Check circuit breaker
        if self._is_circuit_open():
            logger.warning(f"{self.name}: Circuit breaker open, skipping request to {url}")
            return None
        
        await self._wait_for_rate_limit()
        start_time = datetime.now()
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                if not self._client:
                    raise RuntimeError("Client not initialized. Use 'async with' context manager.")
                
                response = await self._client.request(method, url, **kwargs)
                response_time = (datetime.now() - start_time).total_seconds()
                
                # Check for retryable status codes
                if response.status_code in self.RETRY_STATUS_CODES:
                    if response.status_code == 429:  # Too Many Requests
                        wait_time = int(response.headers.get("Retry-After", 60))
                        logger.info(f"{self.name}: Rate limited, waiting {wait_time}s")
                        await asyncio.sleep(wait_time)
                    else:
                        # Server error - use exponential backoff
                        backoff = self._calculate_backoff(attempt)
                        logger.warning(f"{self.name}: HTTP {response.status_code}, retry in {backoff:.1f}s (attempt {attempt + 1}/{self.max_retries})")
                        await asyncio.sleep(backoff)
                    continue
                
                response.raise_for_status()
                
                # Success - record metrics
                self.metrics.record_success(response_time)
                logger.debug(f"{self.name}: Request successful ({response_time*1000:.0f}ms)")
                return response
                
            except httpx.HTTPStatusError as e:
                last_error = f"HTTP {e.response.status_code}"
                logger.warning(f"{self.name}: {last_error} for {url}")
                
                if e.response.status_code == 429:
                    wait_time = int(e.response.headers.get("Retry-After", 60))
                    logger.info(f"{self.name}: Rate limited, waiting {wait_time}s")
                    await asyncio.sleep(wait_time)
                elif e.response.status_code >= 500:
                    backoff = self._calculate_backoff(attempt)
                    await asyncio.sleep(backoff)
                else:
                    # Client error (4xx) - don't retry except 429
                    break
                    
            except self.RETRY_EXCEPTIONS as e:
                last_error = str(e)
                backoff = self._calculate_backoff(attempt)
                logger.warning(f"{self.name}: Request error ({type(e).__name__}), retry in {backoff:.1f}s (attempt {attempt + 1}/{self.max_retries})")
                await asyncio.sleep(backoff)
                
            except Exception as e:
                last_error = f"Unexpected error: {e}"
                logger.error(f"{self.name}: {last_error}")
                break
        
        # All retries exhausted - record failure
        self.metrics.record_failure(last_error or "Unknown error")
        logger.error(f"{self.name}: Request failed after {self.max_retries} attempts: {last_error}")
        return None
    
    async def get(self, url: str, **kwargs) -> Optional[httpx.Response]:
        """GET request"""
        return await self._make_request("GET", url, **kwargs)
    
    async def post(self, url: str, **kwargs) -> Optional[httpx.Response]:
        """POST request"""
        return await self._make_request("POST", url, **kwargs)
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform a health check on this scraper.
        Returns status and metrics.
        """
        health = {
            "name": self.name,
            "base_url": self.base_url,
            "status": self.metrics.status.value,
            "metrics": self.metrics.to_dict(),
            "circuit_breaker_open": self._is_circuit_open(),
        }
        
        # Try a simple request to verify connectivity
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.head(self.base_url)
                health["reachable"] = response.status_code < 500
                health["response_code"] = response.status_code
        except Exception as e:
            health["reachable"] = False
            health["connectivity_error"] = str(e)
        
        return health
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics for this scraper"""
        return self.metrics.to_dict()
    
    def _get_cache_key(self, *args) -> str:
        """Generate cache key from arguments"""
        return hashlib.md5(json.dumps(args, default=str).encode()).hexdigest()
    
    def _get_from_cache(self, key: str) -> Optional[Any]:
        """Get value from cache if not expired"""
        if key in self._cache:
            value, timestamp = self._cache[key]
            if datetime.now() - timestamp < self._cache_ttl:
                return value
            del self._cache[key]
        return None
    
    def _set_cache(self, key: str, value: Any):
        """Set value in cache"""
        self._cache[key] = (value, datetime.now())
    
    @abstractmethod
    async def search(
        self,
        query: str,
        location: Optional[str] = None,
        page: int = 1,
        **filters
    ) -> List[Opportunity]:
        """
        Search for opportunities.
        Must be implemented by each specific scraper.
        """
        pass
    
    @abstractmethod
    async def get_details(self, opportunity_id: str) -> Optional[Opportunity]:
        """
        Get detailed information about a specific opportunity.
        Must be implemented by each specific scraper.
        """
        pass
    
    async def get_latest(self, limit: int = 50) -> List[Opportunity]:
        """Get latest opportunities (default implementation)"""
        return await self.search("", page=1)[:limit]


class LinkedInScraper(BaseScraper):
    """LinkedIn Jobs Scraper"""
    
    def __init__(self):
        super().__init__(
            name="LinkedIn",
            base_url="https://www.linkedin.com",
            rate_limit=0.5  # Be conservative with LinkedIn
        )
    
    async def search(
        self,
        query: str,
        location: Optional[str] = None,
        page: int = 1,
        **filters
    ) -> List[Opportunity]:
        opportunities = []
        
        params = {
            "keywords": query,
            "location": location or "United States",
            "start": (page - 1) * 25,
            "f_TPR": "r86400",  # Last 24 hours
        }
        
        if filters.get("remote"):
            params["f_WT"] = "2"  # Remote
        
        url = f"{self.base_url}/jobs-guest/jobs/api/seeMoreJobPostings/search"
        response = await self.get(url, params=params)
        
        if response:
            # Parse HTML response and extract jobs
            # This is a simplified example - real implementation would use BeautifulSoup
            html = response.text
            # ... parsing logic here ...
            
            # Example opportunity
            opp = Opportunity(
                id=Opportunity.generate_id("linkedin", "123456"),
                title="Software Engineer",
                company="Example Corp",
                location="San Francisco, CA",
                apply_url="https://linkedin.com/jobs/view/123456",
                source="LinkedIn",
                source_id="123456",
                opportunity_type="job"
            )
            opportunities.append(opp)
        
        return opportunities
    
    async def get_details(self, opportunity_id: str) -> Optional[Opportunity]:
        url = f"{self.base_url}/jobs/view/{opportunity_id}"
        response = await self.get(url)
        
        if response:
            # Parse and return detailed opportunity
            pass
        
        return None


class RemoteOKScraper(BaseScraper):
    """Remote OK API Scraper - Has public JSON API"""
    
    def __init__(self):
        super().__init__(
            name="RemoteOK",
            base_url="https://remoteok.com",
            rate_limit=1.0
        )
    
    async def search(
        self,
        query: str,
        location: Optional[str] = None,
        page: int = 1,
        **filters
    ) -> List[Opportunity]:
        opportunities = []
        
        # RemoteOK has a public JSON API
        url = f"{self.base_url}/api"
        response = await self.get(url)
        
        if response:
            try:
                data = response.json()
                # First item is metadata, skip it
                jobs = data[1:] if len(data) > 1 else []
                
                for job in jobs:
                    if query.lower() in job.get("position", "").lower() or not query:
                        opp = Opportunity(
                            id=Opportunity.generate_id("remoteok", str(job.get("id", ""))),
                            title=job.get("position", ""),
                            company=job.get("company", ""),
                            location="Remote",
                            salary_min=job.get("salary_min"),
                            salary_max=job.get("salary_max"),
                            description=job.get("description", ""),
                            apply_url=job.get("url", ""),
                            source="RemoteOK",
                            source_id=str(job.get("id", "")),
                            opportunity_type="job",
                            remote=True,
                            tags=job.get("tags", [])
                        )
                        opportunities.append(opp)
            except Exception as e:
                logger.error(f"RemoteOK parse error: {e}")
        
        return opportunities
    
    async def get_details(self, opportunity_id: str) -> Optional[Opportunity]:
        # RemoteOK API returns all jobs, filter by ID
        opportunities = await self.search("")
        for opp in opportunities:
            if opp.source_id == opportunity_id:
                return opp
        return None


# Scraper registry
SCRAPERS = {
    "linkedin": LinkedInScraper,
    "remoteok": RemoteOKScraper,
}


async def run_all_scrapers(query: str = "", limit: int = 100) -> List[Opportunity]:
    """Run all scrapers concurrently and aggregate results"""
    all_opportunities = []
    
    async def run_scraper(scraper_class):
        try:
            async with scraper_class() as scraper:
                return await scraper.search(query)
        except Exception as e:
            logger.error(f"Scraper {scraper_class.__name__} failed: {e}")
            return []
    
    tasks = [run_scraper(scraper) for scraper in SCRAPERS.values()]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    for result in results:
        if isinstance(result, list):
            all_opportunities.extend(result)
    
    # Deduplicate and sort by match score
    seen = set()
    unique = []
    for opp in all_opportunities:
        if opp.id not in seen:
            seen.add(opp.id)
            unique.append(opp)
    
    return sorted(unique, key=lambda x: x.match_score, reverse=True)[:limit]
