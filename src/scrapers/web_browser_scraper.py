"""
Web Browser Scraper
===================
Advanced web browsing capabilities for dynamic opportunity discovery.
Uses search engines and web crawling to find opportunities beyond static APIs.

Features:
- Google/Bing search for opportunities
- Dynamic website scraping with BeautifulSoup
- JavaScript rendering support (optional)
- Intelligent content extraction
- Multi-source aggregation
"""

import asyncio
import httpx
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Set
import logging
import re
import json
import hashlib
from urllib.parse import urljoin, urlparse, quote_plus
import random

from .utils import safe_request, retry_on_failure, RateLimiter
from .base_scraper import get_scraper_metrics

logger = logging.getLogger(__name__)

# Rate limiters for search engines (be very conservative)
SEARCH_RATE_LIMITER = RateLimiter(rate=0.2, burst=1)  # 1 request per 5 seconds


def generate_id(source: str, title: str, url: str) -> str:
    """Generate unique opportunity ID"""
    content = f"{source}_{title}_{url}"
    return hashlib.md5(content.encode()).hexdigest()[:16]


# User agents for rotation
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
]


# =============================================================================
# SEARCH ENGINE SCRAPING
# =============================================================================
@retry_on_failure(retries=2, delay=5.0)
async def search_google_for_opportunities(
    query: str,
    site: Optional[str] = None,
    num_results: int = 20,
) -> List[Dict]:
    """
    Search Google for opportunities using their search.
    Note: Uses DuckDuckGo HTML as it's more scraping-friendly.
    """
    opportunities = []
    metrics = get_scraper_metrics("WebSearch")
    start_time = datetime.now()
    
    try:
        await SEARCH_RATE_LIMITER.acquire()
        
        # Build search query
        search_query = query
        if site:
            search_query = f"site:{site} {query}"
        
        # Use DuckDuckGo HTML (more reliable for scraping)
        encoded_query = quote_plus(search_query)
        url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
        
        headers = {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        }
        
        async with httpx.AsyncClient(timeout=30.0, headers=headers, follow_redirects=True) as client:
            response = await client.get(url)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'lxml')
                
                # Parse DuckDuckGo results
                results = soup.find_all('div', class_='result')[:num_results]
                
                for result in results:
                    try:
                        title_elem = result.find('a', class_='result__a')
                        snippet_elem = result.find('a', class_='result__snippet')
                        
                        if title_elem:
                            title = title_elem.get_text(strip=True)
                            link = title_elem.get('href', '')
                            snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""
                            
                            # Extract actual URL from DuckDuckGo redirect
                            if 'uddg=' in link:
                                import urllib.parse
                                parsed = urllib.parse.parse_qs(urllib.parse.urlparse(link).query)
                                link = parsed.get('uddg', [link])[0]
                            
                            opp = {
                                "id": generate_id("websearch", title, link),
                                "title": title[:200],
                                "company": urlparse(link).netloc.replace('www.', ''),
                                "location": "Various",
                                "description": snippet[:500],
                                "apply_url": link,
                                "source": "Web Search",
                                "opportunity_type": _classify_opportunity(title, snippet),
                                "remote": "remote" in (title + snippet).lower(),
                                "tags": ["web_search", query.split()[0] if query else ""],
                                "match_score": 70,
                                "scraped_at": datetime.utcnow().isoformat(),
                            }
                            opportunities.append(opp)
                    except Exception as e:
                        logger.debug(f"Error parsing search result: {e}")
                
                duration = (datetime.now() - start_time).total_seconds()
                metrics.record_success(duration, len(opportunities))
                logger.info(f"✅ Web Search: Found {len(opportunities)} results for '{query}'")
                
    except Exception as e:
        metrics.record_failure(str(e))
        logger.error(f"❌ Web Search failed: {e}")
    
    return opportunities


def _classify_opportunity(title: str, description: str) -> str:
    """Classify opportunity type from title and description"""
    text = (title + " " + description).lower()
    
    if any(w in text for w in ["scholarship", "fellowship", "funding", "stipend"]):
        return "scholarship"
    elif any(w in text for w in ["grant", "funding opportunity", "rfp"]):
        return "grant"
    elif any(w in text for w in ["hackathon", "competition", "challenge", "contest"]):
        return "hackathon"
    elif any(w in text for w in ["accelerator", "incubator", "startup program"]):
        return "accelerator"
    elif any(w in text for w in ["conference", "summit", "event", "meetup"]):
        return "event"
    elif any(w in text for w in ["internship", "intern "]):
        return "internship"
    else:
        return "job"


# =============================================================================
# DYNAMIC WEBSITE SCRAPER
# =============================================================================
class DynamicScraper:
    """
    Scrapes opportunities from any website by detecting common patterns.
    """
    
    # Common job listing selectors
    JOB_SELECTORS = [
        # Class patterns
        ('div', {'class_': re.compile(r'job[-_]?(listing|card|item|post)', re.I)}),
        ('article', {'class_': re.compile(r'job', re.I)}),
        ('li', {'class_': re.compile(r'job[-_]?(listing|item)', re.I)}),
        ('div', {'class_': re.compile(r'(position|vacancy|opening|career)', re.I)}),
        # Data attributes
        ('div', {'data-job': True}),
        ('div', {'data-position': True}),
        # Schema.org
        ('script', {'type': 'application/ld+json'}),
    ]
    
    # Common title selectors
    TITLE_SELECTORS = [
        'h1', 'h2', 'h3',
        '.job-title', '.position-title', '.title',
        '[class*="title"]', '[class*="position"]',
        'a[href*="job"]', 'a[href*="career"]',
    ]
    
    def __init__(self):
        self.rate_limiter = RateLimiter(rate=0.5, burst=2)
    
    async def scrape_website(
        self,
        url: str,
        source_name: str,
        opportunity_type: str = "job",
        limit: int = 50,
    ) -> List[Dict]:
        """
        Dynamically scrape a website for opportunities.
        """
        opportunities = []
        metrics = get_scraper_metrics(f"Dynamic_{source_name}")
        start_time = datetime.now()
        
        try:
            await self.rate_limiter.acquire()
            
            headers = {
                "User-Agent": random.choice(USER_AGENTS),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
            }
            
            async with httpx.AsyncClient(timeout=30.0, headers=headers, follow_redirects=True) as client:
                response = await client.get(url)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'lxml')
                    
                    # Try to find JSON-LD structured data first
                    opportunities.extend(await self._extract_json_ld(soup, source_name, url))
                    
                    # Try common selectors
                    if len(opportunities) < limit:
                        opportunities.extend(await self._extract_by_selectors(
                            soup, source_name, url, opportunity_type, limit
                        ))
                    
                    # Try extracting links that look like job postings
                    if len(opportunities) < limit:
                        opportunities.extend(await self._extract_job_links(
                            soup, source_name, url, limit - len(opportunities)
                        ))
                    
                    duration = (datetime.now() - start_time).total_seconds()
                    metrics.record_success(duration, len(opportunities))
                    logger.info(f"✅ {source_name}: Scraped {len(opportunities)} opportunities")
                else:
                    metrics.record_failure(f"HTTP {response.status_code}")
                    
        except Exception as e:
            metrics.record_failure(str(e))
            logger.error(f"❌ {source_name} scrape failed: {e}")
        
        return opportunities[:limit]
    
    async def _extract_json_ld(self, soup: BeautifulSoup, source: str, base_url: str) -> List[Dict]:
        """Extract opportunities from JSON-LD structured data"""
        opportunities = []
        
        for script in soup.find_all('script', type='application/ld+json'):
            try:
                data = json.loads(script.string)
                
                # Handle different JSON-LD formats
                items = []
                if isinstance(data, list):
                    items = data
                elif isinstance(data, dict):
                    if '@graph' in data:
                        items = data['@graph']
                    else:
                        items = [data]
                
                for item in items:
                    if item.get('@type') in ['JobPosting', 'Job', 'Position']:
                        opp = {
                            "id": generate_id(source, item.get('title', ''), item.get('url', base_url)),
                            "title": item.get('title', item.get('name', 'Position')),
                            "company": item.get('hiringOrganization', {}).get('name', source),
                            "location": self._extract_location(item),
                            "description": item.get('description', '')[:500],
                            "apply_url": item.get('url', base_url),
                            "source": source,
                            "opportunity_type": "job",
                            "salary": item.get('baseSalary', {}).get('value', ''),
                            "remote": 'remote' in str(item).lower(),
                            "posted_date": item.get('datePosted', ''),
                            "deadline": item.get('validThrough', ''),
                            "tags": ["structured_data"],
                            "match_score": 80,
                            "scraped_at": datetime.utcnow().isoformat(),
                        }
                        opportunities.append(opp)
            except:
                continue
        
        return opportunities
    
    def _extract_location(self, item: Dict) -> str:
        """Extract location from JSON-LD item"""
        loc = item.get('jobLocation', {})
        if isinstance(loc, dict):
            address = loc.get('address', {})
            if isinstance(address, dict):
                city = address.get('addressLocality', '')
                region = address.get('addressRegion', '')
                country = address.get('addressCountry', '')
                return ', '.join(filter(None, [city, region, country])) or 'Various'
        return 'Various'
    
    async def _extract_by_selectors(
        self,
        soup: BeautifulSoup,
        source: str,
        base_url: str,
        opportunity_type: str,
        limit: int
    ) -> List[Dict]:
        """Extract opportunities using common CSS selectors"""
        opportunities = []
        
        for tag, attrs in self.JOB_SELECTORS:
            items = soup.find_all(tag, attrs)[:limit]
            
            for item in items:
                try:
                    # Find title
                    title = None
                    for sel in self.TITLE_SELECTORS:
                        title_elem = item.select_one(sel) if '.' in sel or '[' in sel else item.find(sel)
                        if title_elem:
                            title = title_elem.get_text(strip=True)
                            break
                    
                    if not title:
                        title = item.get_text(strip=True)[:100]
                    
                    if not title or len(title) < 5:
                        continue
                    
                    # Find link
                    link_elem = item.find('a', href=True)
                    link = urljoin(base_url, link_elem['href']) if link_elem else base_url
                    
                    # Find company
                    company_elem = item.find(class_=re.compile(r'company|employer|org', re.I))
                    company = company_elem.get_text(strip=True) if company_elem else source
                    
                    # Find location
                    loc_elem = item.find(class_=re.compile(r'location|place|city', re.I))
                    location = loc_elem.get_text(strip=True) if loc_elem else "Various"
                    
                    opp = {
                        "id": generate_id(source, title, link),
                        "title": title[:200],
                        "company": company[:100],
                        "location": location[:100],
                        "description": item.get_text(strip=True)[:500],
                        "apply_url": link,
                        "source": source,
                        "opportunity_type": opportunity_type,
                        "remote": "remote" in item.get_text().lower(),
                        "tags": ["dynamic_scrape"],
                        "match_score": 75,
                        "scraped_at": datetime.utcnow().isoformat(),
                    }
                    opportunities.append(opp)
                    
                except Exception as e:
                    continue
            
            if opportunities:
                break  # Found items with this selector
        
        return opportunities
    
    async def _extract_job_links(
        self,
        soup: BeautifulSoup,
        source: str,
        base_url: str,
        limit: int
    ) -> List[Dict]:
        """Extract links that look like job postings"""
        opportunities = []
        seen_urls = set()
        
        # Patterns that indicate job links
        job_patterns = [
            r'/jobs?/',
            r'/careers?/',
            r'/positions?/',
            r'/openings?/',
            r'/vacancies?/',
            r'/apply',
            r'/job[-_]',
            r'jobId=',
            r'positionId=',
        ]
        
        for link in soup.find_all('a', href=True):
            href = link['href']
            full_url = urljoin(base_url, href)
            
            # Skip if already seen
            if full_url in seen_urls:
                continue
            
            # Check if URL matches job patterns
            if any(re.search(p, href, re.I) for p in job_patterns):
                title = link.get_text(strip=True)
                
                # Skip navigation links
                if not title or len(title) < 10 or len(title) > 200:
                    continue
                if title.lower() in ['jobs', 'careers', 'apply now', 'view all']:
                    continue
                
                seen_urls.add(full_url)
                
                opp = {
                    "id": generate_id(source, title, full_url),
                    "title": title,
                    "company": source,
                    "location": "Various",
                    "description": "",
                    "apply_url": full_url,
                    "source": source,
                    "opportunity_type": "job",
                    "remote": "remote" in title.lower(),
                    "tags": ["link_extraction"],
                    "match_score": 65,
                    "scraped_at": datetime.utcnow().isoformat(),
                }
                opportunities.append(opp)
                
                if len(opportunities) >= limit:
                    break
        
        return opportunities


# =============================================================================
# MULTI-SOURCE WEB SCRAPER
# =============================================================================
async def scrape_multiple_job_boards(
    sources: Dict[str, Dict],
    limit_per_source: int = 20,
    max_concurrent: int = 3,
) -> List[Dict]:
    """
    Scrape multiple job boards in parallel.
    
    Args:
        sources: Dict of source_name -> {url, type, ...}
        limit_per_source: Max items per source
        max_concurrent: Max parallel requests
    """
    all_opportunities = []
    scraper = DynamicScraper()
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def scrape_source(name: str, config: Dict):
        async with semaphore:
            try:
                url = config.get('url', '')
                opp_type = config.get('type', 'job')
                
                # Use careers/jobs page if available
                careers_url = config.get('careers_url', url)
                
                return await scraper.scrape_website(
                    url=careers_url,
                    source_name=name,
                    opportunity_type=opp_type,
                    limit=limit_per_source
                )
            except Exception as e:
                logger.error(f"Failed to scrape {name}: {e}")
                return []
    
    # Run all scrapers
    tasks = [scrape_source(name, config) for name, config in sources.items()]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    for result in results:
        if isinstance(result, list):
            all_opportunities.extend(result)
    
    return all_opportunities


# =============================================================================
# SEARCH-BASED OPPORTUNITY DISCOVERY
# =============================================================================
async def discover_opportunities_via_search(
    queries: List[str] = None,
    sites: List[str] = None,
    limit: int = 100,
) -> List[Dict]:
    """
    Discover opportunities by searching the web.
    
    Args:
        queries: List of search queries
        sites: Optional list of sites to search within
        limit: Max total results
    """
    if queries is None:
        queries = [
            "remote software engineer jobs 2024",
            "tech startup jobs hiring now",
            "machine learning engineer remote",
            "developer grants funding",
            "tech fellowships 2024",
            "hackathon prizes 2024",
            "startup accelerator applications open",
        ]
    
    all_opportunities = []
    seen_urls = set()
    
    for query in queries:
        if len(all_opportunities) >= limit:
            break
        
        if sites:
            for site in sites:
                results = await search_google_for_opportunities(query, site=site)
                for opp in results:
                    if opp['apply_url'] not in seen_urls:
                        seen_urls.add(opp['apply_url'])
                        all_opportunities.append(opp)
        else:
            results = await search_google_for_opportunities(query)
            for opp in results:
                if opp['apply_url'] not in seen_urls:
                    seen_urls.add(opp['apply_url'])
                    all_opportunities.append(opp)
        
        # Rate limit between queries
        await asyncio.sleep(2)
    
    return all_opportunities[:limit]


# =============================================================================
# ENHANCED LIVE SCRAPER WITH WEB BROWSING
# =============================================================================
async def browse_and_scrape(
    include_search: bool = True,
    include_dynamic: bool = True,
    search_queries: List[str] = None,
    additional_sites: Dict[str, str] = None,
    limit: int = 200,
) -> Dict[str, Any]:
    """
    Comprehensive web browsing and scraping.
    
    Combines:
    - Search engine discovery
    - Dynamic website scraping
    - Known job board APIs
    """
    logger.info("🌐 Starting WEB BROWSING scan...")
    start_time = datetime.utcnow()
    
    all_opportunities = []
    stats = {
        "total": 0,
        "by_source": {},
        "by_method": {"search": 0, "dynamic": 0, "api": 0},
        "errors": []
    }
    
    # Default additional sites to scrape dynamically
    if additional_sites is None:
        additional_sites = {
            "Lever": "https://jobs.lever.co/",
            "Greenhouse": "https://boards.greenhouse.io/",
            "Workable": "https://apply.workable.com/",
            "BambooHR": "https://careers.bamboohr.com/",
            "Otta": "https://otta.com/",
            "Cord": "https://cord.co/",
            "TrueUp": "https://www.trueup.io/jobs",
            "Techjobs": "https://www.techjobsforgood.com/",
            "Climatebase": "https://climatebase.org/jobs",
            "80000Hours": "https://80000hours.org/job-board/",
        }
    
    tasks = []
    
    # 1. Search-based discovery
    if include_search:
        if search_queries is None:
            search_queries = [
                "software engineer remote jobs apply now",
                "machine learning engineer hiring 2024",
                "startup grants applications open",
                "tech fellowship deadline 2024",
            ]
        tasks.append(("Web Search", discover_opportunities_via_search(search_queries, limit=50)))
    
    # 2. Dynamic website scraping
    if include_dynamic:
        scraper = DynamicScraper()
        for name, url in additional_sites.items():
            tasks.append((name, scraper.scrape_website(url, name, limit=20)))
    
    # Execute with concurrency limit
    semaphore = asyncio.Semaphore(3)
    
    async def run_with_limit(name, coro):
        async with semaphore:
            try:
                result = await asyncio.wait_for(coro, timeout=60.0)
                return name, result, None
            except Exception as e:
                return name, [], str(e)
    
    wrapped = [run_with_limit(name, coro) for name, coro in tasks]
    results = await asyncio.gather(*wrapped)
    
    # Process results
    for name, opps, error in results:
        if error:
            stats["errors"].append(f"{name}: {error}")
        else:
            all_opportunities.extend(opps)
            stats["by_source"][name] = len(opps)
            
            # Track method
            if name == "Web Search":
                stats["by_method"]["search"] += len(opps)
            else:
                stats["by_method"]["dynamic"] += len(opps)
    
    # Deduplicate by URL
    seen_urls = set()
    unique_opps = []
    for opp in all_opportunities:
        url = opp.get('apply_url', '')
        if url and url not in seen_urls:
            seen_urls.add(url)
            unique_opps.append(opp)
    
    unique_opps.sort(key=lambda x: x.get('match_score', 0), reverse=True)
    
    stats["total"] = len(unique_opps)
    duration = (datetime.utcnow() - start_time).total_seconds()
    
    logger.info(f"\n{'='*60}")
    logger.info(f"🔍 WEB BROWSING COMPLETE: {stats['total']} opportunities")
    logger.info(f"⏱️ Duration: {duration:.1f}s")
    logger.info(f"📊 By method: {stats['by_method']}")
    logger.info(f"{'='*60}")
    
    return {
        "opportunities": unique_opps[:limit],
        "stats": stats,
        "duration_seconds": duration,
        "is_web_browsing": True,
    }


# Quick test
if __name__ == "__main__":
    async def test():
        result = await browse_and_scrape(limit=50)
        print(f"Total: {result['stats']['total']}")
        print(f"By source: {result['stats']['by_source']}")
        for opp in result['opportunities'][:5]:
            print(f"  - {opp['title']} ({opp['source']})")
    
    asyncio.run(test())
