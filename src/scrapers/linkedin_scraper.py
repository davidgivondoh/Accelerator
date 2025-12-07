"""
LinkedIn Jobs Scraper
=====================
Scrapes job listings from LinkedIn's public job search.
"""

import asyncio
import httpx
import re
import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from bs4 import BeautifulSoup
from dataclasses import dataclass, field
import hashlib
import json

logger = logging.getLogger(__name__)


@dataclass
class JobListing:
    """Standardized job listing structure"""
    id: str
    title: str
    company: str
    location: str
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    description: str = ""
    requirements: List[str] = field(default_factory=list)
    apply_url: str = ""
    source: str = "linkedin"
    source_id: str = ""
    posted_date: Optional[datetime] = None
    job_type: str = "full-time"
    remote: bool = False
    easy_apply: bool = False
    match_score: float = 0.0
    scraped_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "company": self.company,
            "location": self.location,
            "salary_min": self.salary_min,
            "salary_max": self.salary_max,
            "description": self.description[:500] + "..." if len(self.description) > 500 else self.description,
            "apply_url": self.apply_url,
            "source": self.source,
            "source_id": self.source_id,
            "posted_date": self.posted_date.isoformat() if self.posted_date else None,
            "job_type": self.job_type,
            "remote": self.remote,
            "easy_apply": self.easy_apply,
            "match_score": self.match_score,
            "scraped_at": self.scraped_at.isoformat()
        }


class LinkedInScraper:
    """
    LinkedIn Jobs Scraper using public guest API.
    No authentication required - uses public job listings.
    """
    
    BASE_URL = "https://www.linkedin.com"
    JOBS_API = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
    JOB_DETAIL_URL = "https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{job_id}"
    
    def __init__(self, rate_limit: float = 0.5):
        self.rate_limit = rate_limit
        self.last_request = datetime.min
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }
    
    async def _wait_rate_limit(self):
        """Enforce rate limiting"""
        elapsed = (datetime.now() - self.last_request).total_seconds()
        if elapsed < (1 / self.rate_limit):
            await asyncio.sleep((1 / self.rate_limit) - elapsed)
        self.last_request = datetime.now()
    
    async def search_jobs(
        self,
        keywords: str,
        location: str = "United States",
        job_type: Optional[str] = None,  # F=Full-time, P=Part-time, C=Contract
        remote: bool = False,
        experience_level: Optional[str] = None,  # 1=Intern, 2=Entry, 3=Associate, 4=Mid-Senior, 5=Director, 6=Executive
        posted_within: str = "day",  # day, week, month
        start: int = 0,
        limit: int = 25
    ) -> List[JobListing]:
        """
        Search LinkedIn jobs with filters.
        
        Args:
            keywords: Job search keywords
            location: Location filter
            job_type: F=Full-time, P=Part-time, C=Contract, T=Temporary, I=Internship
            remote: Filter for remote jobs
            experience_level: 1-6 for different experience levels
            posted_within: day, week, month
            start: Pagination offset
            limit: Number of results
            
        Returns:
            List of JobListing objects
        """
        await self._wait_rate_limit()
        
        # Build params
        params = {
            "keywords": keywords,
            "location": location,
            "start": start,
        }
        
        # Time filter
        time_filters = {
            "day": "r86400",      # Last 24 hours
            "week": "r604800",    # Last week
            "month": "r2592000",  # Last month
        }
        if posted_within in time_filters:
            params["f_TPR"] = time_filters[posted_within]
        
        # Remote filter
        if remote:
            params["f_WT"] = "2"  # Remote
        
        # Job type filter
        if job_type:
            params["f_JT"] = job_type
        
        # Experience level
        if experience_level:
            params["f_E"] = experience_level
        
        jobs = []
        
        try:
            async with httpx.AsyncClient(headers=self.headers, follow_redirects=True, timeout=30) as client:
                response = await client.get(self.JOBS_API, params=params)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, "html.parser")
                job_cards = soup.find_all("div", class_="base-card")
                
                for card in job_cards[:limit]:
                    try:
                        job = self._parse_job_card(card)
                        if job:
                            jobs.append(job)
                    except Exception as e:
                        logger.warning(f"Failed to parse job card: {e}")
                        continue
                
                logger.info(f"LinkedIn: Found {len(jobs)} jobs for '{keywords}'")
                
        except httpx.HTTPStatusError as e:
            logger.error(f"LinkedIn HTTP error: {e.response.status_code}")
        except Exception as e:
            logger.error(f"LinkedIn scraper error: {e}")
        
        return jobs
    
    def _parse_job_card(self, card) -> Optional[JobListing]:
        """Parse a job card HTML element into a JobListing"""
        try:
            # Extract job ID from data attribute or link
            job_link = card.find("a", class_="base-card__full-link")
            if not job_link:
                return None
            
            job_url = job_link.get("href", "")
            job_id_match = re.search(r'/jobs/view/(\d+)', job_url)
            job_id = job_id_match.group(1) if job_id_match else hashlib.md5(job_url.encode()).hexdigest()[:12]
            
            # Title
            title_elem = card.find("h3", class_="base-search-card__title")
            title = title_elem.get_text(strip=True) if title_elem else "Unknown Title"
            
            # Company
            company_elem = card.find("h4", class_="base-search-card__subtitle")
            company = company_elem.get_text(strip=True) if company_elem else "Unknown Company"
            
            # Location
            location_elem = card.find("span", class_="job-search-card__location")
            location = location_elem.get_text(strip=True) if location_elem else "Unknown Location"
            
            # Posted date
            date_elem = card.find("time", class_="job-search-card__listdate")
            posted_date = None
            if date_elem:
                date_str = date_elem.get("datetime", "")
                try:
                    posted_date = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                except:
                    pass
            
            # Check for Easy Apply
            easy_apply = card.find("span", string=re.compile("Easy Apply", re.I)) is not None
            
            # Check for remote
            remote = "remote" in location.lower()
            
            # Generate unique ID
            unique_id = hashlib.md5(f"linkedin:{job_id}".encode()).hexdigest()[:16]
            
            return JobListing(
                id=unique_id,
                title=title,
                company=company,
                location=location,
                apply_url=job_url.split("?")[0] if job_url else "",
                source="linkedin",
                source_id=job_id,
                posted_date=posted_date,
                remote=remote,
                easy_apply=easy_apply
            )
            
        except Exception as e:
            logger.error(f"Error parsing job card: {e}")
            return None
    
    async def get_job_details(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific job"""
        await self._wait_rate_limit()
        
        try:
            url = self.JOB_DETAIL_URL.format(job_id=job_id)
            
            async with httpx.AsyncClient(headers=self.headers, follow_redirects=True, timeout=30) as client:
                response = await client.get(url)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, "html.parser")
                
                # Extract description
                desc_elem = soup.find("div", class_="description__text")
                description = desc_elem.get_text(strip=True) if desc_elem else ""
                
                # Extract salary if available
                salary_elem = soup.find("div", class_="salary-main-rail__salary-range")
                salary_text = salary_elem.get_text(strip=True) if salary_elem else ""
                
                # Parse salary
                salary_min, salary_max = self._parse_salary(salary_text)
                
                return {
                    "description": description,
                    "salary_min": salary_min,
                    "salary_max": salary_max,
                    "salary_text": salary_text
                }
                
        except Exception as e:
            logger.error(f"Error fetching job details: {e}")
            return None
    
    def _parse_salary(self, salary_text: str) -> tuple:
        """Parse salary string into min/max values"""
        if not salary_text:
            return None, None
        
        # Find all numbers in the salary text
        numbers = re.findall(r'\$?([\d,]+)', salary_text)
        numbers = [int(n.replace(',', '')) for n in numbers]
        
        # Handle different formats
        if len(numbers) >= 2:
            # If numbers are hourly (typically < 500), convert to annual
            if numbers[0] < 500:
                numbers = [n * 2080 for n in numbers]  # 40 hrs/week * 52 weeks
            return min(numbers), max(numbers)
        elif len(numbers) == 1:
            if numbers[0] < 500:
                numbers[0] = numbers[0] * 2080
            return numbers[0], numbers[0]
        
        return None, None


async def scrape_linkedin_jobs(
    keywords: str,
    location: str = "United States",
    remote: bool = False,
    limit: int = 50
) -> List[Dict]:
    """
    Convenience function to scrape LinkedIn jobs.
    
    Args:
        keywords: Search keywords
        location: Location filter
        remote: Remote jobs only
        limit: Max results
        
    Returns:
        List of job dictionaries
    """
    scraper = LinkedInScraper()
    jobs = await scraper.search_jobs(
        keywords=keywords,
        location=location,
        remote=remote,
        limit=limit
    )
    return [job.to_dict() for job in jobs]


# For testing
if __name__ == "__main__":
    async def test():
        jobs = await scrape_linkedin_jobs("software engineer", limit=10)
        for job in jobs:
            print(f"{job['title']} at {job['company']} - {job['location']}")
            print(f"  URL: {job['apply_url']}")
            print()
    
    asyncio.run(test())
