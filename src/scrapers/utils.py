"""
Scraper Utilities
=================
Common utilities for web scraping with improved reliability.
"""

import asyncio
import httpx
import logging
from datetime import datetime
from typing import List, Dict, Any, Callable, TypeVar, Optional
from functools import wraps

logger = logging.getLogger(__name__)

T = TypeVar('T')


# Common headers to avoid blocks
DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "DNT": "1",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}


async def safe_request(
    url: str,
    method: str = "GET",
    timeout: float = 30.0,
    retries: int = 3,
    headers: Optional[Dict[str, str]] = None,
    **kwargs
) -> Optional[httpx.Response]:
    """
    Make an HTTP request with automatic retries and error handling.
    
    Args:
        url: The URL to request
        method: HTTP method (GET, POST, etc.)
        timeout: Request timeout in seconds
        retries: Number of retry attempts
        headers: Optional additional headers
        **kwargs: Additional arguments to pass to httpx
        
    Returns:
        Response object or None if all retries failed
    """
    request_headers = {**DEFAULT_HEADERS}
    if headers:
        request_headers.update(headers)
    
    last_error = None
    
    for attempt in range(retries):
        try:
            async with httpx.AsyncClient(
                timeout=timeout,
                headers=request_headers,
                follow_redirects=True
            ) as client:
                response = await client.request(method, url, **kwargs)
                
                # Handle rate limiting
                if response.status_code == 429:
                    wait_time = int(response.headers.get("Retry-After", 30))
                    logger.warning(f"Rate limited on {url}, waiting {wait_time}s")
                    await asyncio.sleep(wait_time)
                    continue
                
                # Success
                if response.status_code < 400:
                    return response
                
                # Server errors - retry with backoff
                if response.status_code >= 500:
                    backoff = 2 ** attempt
                    logger.warning(f"Server error {response.status_code} on {url}, retry in {backoff}s")
                    await asyncio.sleep(backoff)
                    continue
                
                # Client errors - log and return None
                logger.warning(f"Client error {response.status_code} on {url}")
                return None
                
        except httpx.TimeoutException:
            last_error = "Timeout"
            backoff = 2 ** attempt
            logger.warning(f"Timeout on {url}, retry in {backoff}s (attempt {attempt + 1}/{retries})")
            await asyncio.sleep(backoff)
            
        except httpx.RequestError as e:
            last_error = str(e)
            backoff = 2 ** attempt
            logger.warning(f"Request error on {url}: {e}, retry in {backoff}s")
            await asyncio.sleep(backoff)
            
        except Exception as e:
            last_error = str(e)
            logger.error(f"Unexpected error on {url}: {e}")
            break
    
    logger.error(f"All {retries} retries failed for {url}: {last_error}")
    return None


async def safe_json_request(
    url: str,
    method: str = "GET",
    timeout: float = 30.0,
    retries: int = 3,
    headers: Optional[Dict[str, str]] = None,
    **kwargs
) -> Optional[Dict[str, Any]]:
    """
    Make a request and parse JSON response safely.
    
    Returns:
        Parsed JSON dict or None if request/parsing failed
    """
    response = await safe_request(url, method, timeout, retries, headers, **kwargs)
    
    if response is None:
        return None
    
    try:
        return response.json()
    except Exception as e:
        logger.error(f"JSON parse error for {url}: {e}")
        return None


async def run_scrapers_safely(
    scraper_tasks: List[tuple],
    max_concurrent: int = 10
) -> Dict[str, Any]:
    """
    Run multiple scraper tasks with error handling and concurrency control.
    
    Args:
        scraper_tasks: List of (name, coroutine) tuples
        max_concurrent: Maximum concurrent scrapers
        
    Returns:
        Dict with results, stats, and errors
    """
    semaphore = asyncio.Semaphore(max_concurrent)
    results = {}
    errors = []
    stats = {
        "total_tasks": len(scraper_tasks),
        "successful": 0,
        "failed": 0,
        "total_items": 0,
        "start_time": datetime.utcnow().isoformat()
    }
    
    async def run_with_semaphore(name: str, coro):
        async with semaphore:
            try:
                start = datetime.utcnow()
                result = await coro
                duration = (datetime.utcnow() - start).total_seconds()
                
                count = len(result) if isinstance(result, list) else 0
                logger.info(f"✅ {name}: {count} items in {duration:.1f}s")
                
                return name, result, None
            except Exception as e:
                logger.error(f"❌ {name} failed: {e}")
                return name, [], str(e)
    
    # Run all scrapers
    tasks = [run_with_semaphore(name, coro) for name, coro in scraper_tasks]
    completed = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Process results
    for item in completed:
        if isinstance(item, Exception):
            errors.append(str(item))
            stats["failed"] += 1
        else:
            name, result, error = item
            if error:
                errors.append(f"{name}: {error}")
                stats["failed"] += 1
            else:
                results[name] = result
                stats["successful"] += 1
                stats["total_items"] += len(result) if isinstance(result, list) else 0
    
    stats["end_time"] = datetime.utcnow().isoformat()
    
    return {
        "results": results,
        "stats": stats,
        "errors": errors
    }


def retry_on_failure(
    retries: int = 3,
    delay: float = 1.0,
    exceptions: tuple = (Exception,)
):
    """
    Decorator to retry a function on failure with exponential backoff.
    
    Usage:
        @retry_on_failure(retries=3, delay=1.0)
        async def my_scraper():
            ...
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            last_error = None
            for attempt in range(retries):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_error = e
                    if attempt < retries - 1:
                        wait_time = delay * (2 ** attempt)
                        logger.warning(
                            f"{func.__name__} failed (attempt {attempt + 1}/{retries}): {e}. "
                            f"Retrying in {wait_time:.1f}s"
                        )
                        await asyncio.sleep(wait_time)
            
            logger.error(f"{func.__name__} failed after {retries} attempts: {last_error}")
            return []  # Return empty list for scrapers
        
        return wrapper
    return decorator


class RateLimiter:
    """
    Token bucket rate limiter for controlling request rates.
    
    Usage:
        limiter = RateLimiter(rate=1.0)  # 1 request per second
        await limiter.acquire()
        # make request
    """
    
    def __init__(self, rate: float = 1.0, burst: int = 1):
        """
        Args:
            rate: Requests per second
            burst: Maximum burst size
        """
        self.rate = rate
        self.burst = burst
        self.tokens = burst
        self.last_update = datetime.now()
        self._lock = asyncio.Lock()
    
    async def acquire(self):
        """Wait until a request can be made."""
        async with self._lock:
            now = datetime.now()
            elapsed = (now - self.last_update).total_seconds()
            
            # Refill tokens
            self.tokens = min(self.burst, self.tokens + elapsed * self.rate)
            self.last_update = now
            
            if self.tokens < 1:
                # Wait for token
                wait_time = (1 - self.tokens) / self.rate
                await asyncio.sleep(wait_time)
                self.tokens = 0
            else:
                self.tokens -= 1


# Additional utility functions for accelerator scraper
def clean_text(text: str) -> str:
    """Clean and normalize text content"""
    if not text:
        return ""
    
    import re
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Remove common unwanted characters
    text = re.sub(r'[^\w\s\.\,\!\?\-\(\)\/\:\;]', '', text)
    
    return text


def extract_dates(text: str) -> List[datetime]:
    """Extract dates from text content"""
    if not text:
        return []
    
    import re
    
    dates = []
    
    try:
        # Try to use dateutil if available
        from dateutil import parser
        
        # Common date patterns
        patterns = [
            r'\b\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4}\b',  # MM/DD/YYYY or MM-DD-YYYY
            r'\b\d{4}[\/\-]\d{1,2}[\/\-]\d{1,2}\b',    # YYYY/MM/DD or YYYY-MM-DD
            r'\b[A-Za-z]+ \d{1,2},? \d{4}\b',          # Month DD, YYYY
            r'\b\d{1,2} [A-Za-z]+ \d{4}\b',            # DD Month YYYY
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                try:
                    date_obj = parser.parse(match)
                    dates.append(date_obj)
                except:
                    continue
        
        return sorted(list(set(dates)))
        
    except ImportError:
        # Fallback to basic pattern matching without parsing
        from datetime import datetime
        
        # Look for YYYY-MM-DD pattern
        pattern = r'\b(\d{4})[\/\-](\d{1,2})[\/\-](\d{1,2})\b'
        matches = re.findall(pattern, text)
        
        for match in matches:
            try:
                year, month, day = int(match[0]), int(match[1]), int(match[2])
                if 1 <= month <= 12 and 1 <= day <= 31:
                    date_obj = datetime(year, month, day)
                    dates.append(date_obj)
            except:
                continue
        
        return dates


def normalize_url(url: str, base_url: str = "") -> str:
    """Normalize and resolve URLs"""
    if not url:
        return ""
    
    from urllib.parse import urljoin, urlparse
    
    # If URL is already absolute, return as is
    if url.startswith(('http://', 'https://')):
        return url
    
    # If it's a relative URL and we have a base, join them
    if base_url:
        return urljoin(base_url, url)
    
    # If URL starts with //, add https:
    if url.startswith('//'):
        return 'https:' + url
    
    return url
