"""
Indeed Jobs Scraper
===================
Scrapes job listings from Indeed's public search.
"""

import asyncio
import httpx
import re
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
from bs4 import BeautifulSoup
from dataclasses import dataclass, field
import hashlib
import json

logger = logging.getLogger(__name__)


@dataclass 
class IndeedJob:
    """Indeed job listing structure"""
    id: str
    title: str
    company: str
    location: str
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    description: str = ""
    apply_url: str = ""
    source: str = "indeed"
    source_id: str = ""
    posted_date: Optional[str] = None
    job_type: str = "full-time"
    remote: bool = False
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
            "posted_date": self.posted_date,
            "job_type": self.job_type,
            "remote": self.remote,
            "match_score": self.match_score,
            "scraped_at": self.scraped_at.isoformat()
        }


class IndeedScraper:
    """
    Indeed Jobs Scraper.
    Uses Indeed's public search pages.
    """
    
    BASE_URL = "https://www.indeed.com"
    SEARCH_URL = "https://www.indeed.com/jobs"
    
    def __init__(self, rate_limit: float = 0.5):
        self.rate_limit = rate_limit
        self.last_request = datetime.min
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
        }
    
    async def _wait_rate_limit(self):
        elapsed = (datetime.now() - self.last_request).total_seconds()
        if elapsed < (1 / self.rate_limit):
            await asyncio.sleep((1 / self.rate_limit) - elapsed)
        self.last_request = datetime.now()
    
    async def search_jobs(
        self,
        keywords: str,
        location: str = "",
        job_type: Optional[str] = None,
        remote: bool = False,
        salary_min: Optional[int] = None,
        posted_within: int = 1,  # Days
        start: int = 0,
        limit: int = 25
    ) -> List[IndeedJob]:
        """
        Search Indeed jobs with filters.
        
        Args:
            keywords: Job search keywords
            location: Location filter
            job_type: fulltime, parttime, contract, temporary, internship
            remote: Filter for remote jobs
            salary_min: Minimum salary filter
            posted_within: Posted within X days
            start: Pagination offset (multiples of 10)
            limit: Number of results
            
        Returns:
            List of IndeedJob objects
        """
        await self._wait_rate_limit()
        
        # Build params
        params = {
            "q": keywords,
            "l": location,
            "start": start,
            "fromage": posted_within,  # Posted within X days
        }
        
        # Job type filter
        if job_type:
            params["jt"] = job_type
        
        # Remote filter
        if remote:
            params["remotejob"] = "1"
        
        # Salary filter
        if salary_min:
            params["salary"] = f"${salary_min}"
        
        jobs = []
        
        try:
            async with httpx.AsyncClient(headers=self.headers, follow_redirects=True, timeout=30) as client:
                response = await client.get(self.SEARCH_URL, params=params)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, "html.parser")
                
                # Find job cards - Indeed uses various selectors
                job_cards = soup.find_all("div", class_=re.compile(r"job_seen_beacon|cardOutline|jobsearch-SerpJobCard"))
                
                if not job_cards:
                    # Try alternative selector
                    job_cards = soup.find_all("td", class_="resultContent")
                
                for card in job_cards[:limit]:
                    try:
                        job = self._parse_job_card(card)
                        if job:
                            jobs.append(job)
                    except Exception as e:
                        logger.warning(f"Failed to parse Indeed job card: {e}")
                        continue
                
                logger.info(f"Indeed: Found {len(jobs)} jobs for '{keywords}'")
                
        except httpx.HTTPStatusError as e:
            logger.error(f"Indeed HTTP error: {e.response.status_code}")
        except Exception as e:
            logger.error(f"Indeed scraper error: {e}")
        
        return jobs
    
    def _parse_job_card(self, card) -> Optional[IndeedJob]:
        """Parse an Indeed job card"""
        try:
            # Title and link
            title_elem = card.find("h2", class_=re.compile(r"jobTitle|title"))
            if not title_elem:
                title_elem = card.find("a", class_=re.compile(r"jobtitle|title"))
            
            if not title_elem:
                return None
            
            title = title_elem.get_text(strip=True)
            
            # Get job link
            link_elem = title_elem.find("a") if title_elem.name != "a" else title_elem
            if not link_elem:
                link_elem = card.find("a", href=re.compile(r"/rc/clk|/viewjob"))
            
            job_url = ""
            job_id = ""
            if link_elem:
                href = link_elem.get("href", "")
                if href.startswith("/"):
                    job_url = f"{self.BASE_URL}{href}"
                else:
                    job_url = href
                
                # Extract job ID
                jk_match = re.search(r'jk=([a-f0-9]+)', href)
                if jk_match:
                    job_id = jk_match.group(1)
                else:
                    job_id = hashlib.md5(href.encode()).hexdigest()[:12]
            
            # Company
            company_elem = card.find("span", class_=re.compile(r"companyName|company"))
            if not company_elem:
                company_elem = card.find("span", {"data-testid": "company-name"})
            company = company_elem.get_text(strip=True) if company_elem else "Unknown Company"
            
            # Location
            location_elem = card.find("div", class_=re.compile(r"companyLocation|location"))
            if not location_elem:
                location_elem = card.find("span", {"data-testid": "text-location"})
            location = location_elem.get_text(strip=True) if location_elem else "Unknown Location"
            
            # Salary
            salary_elem = card.find("div", class_=re.compile(r"salary-snippet|salaryText|metadata salary-snippet-container"))
            salary_text = salary_elem.get_text(strip=True) if salary_elem else ""
            salary_min, salary_max = self._parse_salary(salary_text)
            
            # Posted date
            date_elem = card.find("span", class_=re.compile(r"date|posted"))
            posted_date = date_elem.get_text(strip=True) if date_elem else None
            
            # Remote check
            remote = "remote" in location.lower() or card.find(string=re.compile(r"remote", re.I)) is not None
            
            # Generate unique ID
            unique_id = hashlib.md5(f"indeed:{job_id}".encode()).hexdigest()[:16]
            
            return IndeedJob(
                id=unique_id,
                title=title,
                company=company,
                location=location,
                salary_min=salary_min,
                salary_max=salary_max,
                apply_url=job_url,
                source="indeed",
                source_id=job_id,
                posted_date=posted_date,
                remote=remote
            )
            
        except Exception as e:
            logger.error(f"Error parsing Indeed job card: {e}")
            return None
    
    def _parse_salary(self, salary_text: str) -> tuple:
        """Parse salary string into min/max values"""
        if not salary_text:
            return None, None
        
        # Find all numbers
        numbers = re.findall(r'\$?([\d,]+)', salary_text)
        numbers = [int(n.replace(',', '')) for n in numbers]
        
        if not numbers:
            return None, None
        
        # Determine if hourly, monthly, or yearly
        is_hourly = "hour" in salary_text.lower() or "hr" in salary_text.lower()
        is_monthly = "month" in salary_text.lower()
        
        # Convert to annual
        if is_hourly:
            numbers = [n * 2080 for n in numbers]  # 40 hrs * 52 weeks
        elif is_monthly:
            numbers = [n * 12 for n in numbers]
        
        if len(numbers) >= 2:
            return min(numbers), max(numbers)
        elif len(numbers) == 1:
            return numbers[0], numbers[0]
        
        return None, None


async def scrape_indeed_jobs(
    keywords: str,
    location: str = "",
    remote: bool = False,
    limit: int = 50
) -> List[Dict]:
    """
    Convenience function to scrape Indeed jobs.
    """
    scraper = IndeedScraper()
    jobs = await scraper.search_jobs(
        keywords=keywords,
        location=location,
        remote=remote,
        limit=limit
    )
    return [job.to_dict() for job in jobs]


if __name__ == "__main__":
    async def test():
        jobs = await scrape_indeed_jobs("python developer", location="New York", limit=10)
        for job in jobs:
            print(f"{job['title']} at {job['company']} - {job['location']}")
            print(f"  Salary: {job.get('salary_min', 'N/A')} - {job.get('salary_max', 'N/A')}")
            print(f"  URL: {job['apply_url']}")
            print()
    
    asyncio.run(test())
