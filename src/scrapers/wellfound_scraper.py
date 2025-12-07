"""
Wellfound (AngelList) Scraper
=============================
Scrapes startup jobs from Wellfound's job listings.
"""

import asyncio
import httpx
import re
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
from bs4 import BeautifulSoup
import hashlib
import json

logger = logging.getLogger(__name__)


class WellfoundScraper:
    """
    Wellfound (formerly AngelList Talent) Scraper.
    Scrapes startup jobs from their public pages.
    """
    
    BASE_URL = "https://wellfound.com"
    JOBS_URL = "https://wellfound.com/jobs"
    
    def __init__(self, rate_limit: float = 0.5):
        self.rate_limit = rate_limit
        self.last_request = datetime.min
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        }
    
    async def _wait_rate_limit(self):
        elapsed = (datetime.now() - self.last_request).total_seconds()
        if elapsed < (1 / self.rate_limit):
            await asyncio.sleep((1 / self.rate_limit) - elapsed)
        self.last_request = datetime.now()
    
    async def search_jobs(
        self,
        keywords: str = "",
        role: str = "engineering",  # engineering, design, marketing, sales, etc.
        location: str = "",
        remote: bool = False,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Search Wellfound startup jobs.
        
        Args:
            keywords: Job search keywords
            role: Role category (engineering, design, marketing, sales, product, operations)
            location: Location filter
            remote: Filter for remote jobs
            limit: Max results
            
        Returns:
            List of job dictionaries
        """
        await self._wait_rate_limit()
        
        jobs = []
        
        # Build URL
        url = f"{self.JOBS_URL}"
        params = {}
        
        if keywords:
            params["q"] = keywords
        if role:
            params["role"] = role
        if location:
            params["location"] = location
        if remote:
            params["remote"] = "true"
        
        try:
            async with httpx.AsyncClient(headers=self.headers, follow_redirects=True, timeout=30) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, "html.parser")
                
                # Find job listings
                # Wellfound uses React, so we need to find the data in script tags
                scripts = soup.find_all("script", type="application/json")
                
                for script in scripts:
                    try:
                        data = json.loads(script.string)
                        # Look for job data in the JSON
                        extracted_jobs = self._extract_jobs_from_json(data)
                        jobs.extend(extracted_jobs)
                    except:
                        continue
                
                # Also try parsing visible job cards
                job_cards = soup.find_all("div", class_=re.compile(r"styles_jobCard|job-listing"))
                for card in job_cards:
                    job = self._parse_job_card(card)
                    if job and job["id"] not in [j["id"] for j in jobs]:
                        jobs.append(job)
                
                logger.info(f"Wellfound: Found {len(jobs)} startup jobs")
                
        except Exception as e:
            logger.error(f"Wellfound scraper error: {e}")
        
        return jobs[:limit]
    
    def _extract_jobs_from_json(self, data: Any, jobs: List = None) -> List[Dict]:
        """Recursively extract job data from JSON structure"""
        if jobs is None:
            jobs = []
        
        if isinstance(data, dict):
            # Check if this looks like a job listing
            if "title" in data and ("company" in data or "startup" in data):
                job = self._normalize_job(data)
                if job:
                    jobs.append(job)
            else:
                for value in data.values():
                    self._extract_jobs_from_json(value, jobs)
        elif isinstance(data, list):
            for item in data:
                self._extract_jobs_from_json(item, jobs)
        
        return jobs
    
    def _normalize_job(self, data: Dict) -> Optional[Dict]:
        """Normalize job data from various formats"""
        try:
            job_id = str(data.get("id", data.get("slug", "")))
            if not job_id:
                return None
            
            unique_id = hashlib.md5(f"wellfound:{job_id}".encode()).hexdigest()[:16]
            
            # Get company info
            company = data.get("company", data.get("startup", {}))
            if isinstance(company, dict):
                company_name = company.get("name", "Startup")
            else:
                company_name = str(company) if company else "Startup"
            
            # Get salary
            salary_min = data.get("salary_min") or data.get("compensation", {}).get("min")
            salary_max = data.get("salary_max") or data.get("compensation", {}).get("max")
            
            # Get equity
            equity_min = data.get("equity_min") or data.get("equity", {}).get("min")
            equity_max = data.get("equity_max") or data.get("equity", {}).get("max")
            
            # Location
            location = data.get("location", "Remote")
            if isinstance(location, dict):
                location = location.get("name", "Remote")
            
            remote = data.get("remote", False) or "remote" in str(location).lower()
            
            return {
                "id": unique_id,
                "title": data.get("title", "Unknown Position"),
                "company": company_name,
                "location": location,
                "salary_min": salary_min,
                "salary_max": salary_max,
                "equity_min": equity_min,
                "equity_max": equity_max,
                "description": data.get("description", ""),
                "apply_url": data.get("url", f"https://wellfound.com/jobs/{job_id}"),
                "source": "wellfound",
                "source_id": job_id,
                "remote": remote,
                "job_type": data.get("job_type", "full-time"),
                "tags": data.get("tags", []),
                "match_score": 0.0,
                "scraped_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error normalizing Wellfound job: {e}")
            return None
    
    def _parse_job_card(self, card) -> Optional[Dict]:
        """Parse HTML job card"""
        try:
            # Title
            title_elem = card.find(["h2", "h3", "a"], class_=re.compile(r"title|name"))
            title = title_elem.get_text(strip=True) if title_elem else None
            if not title:
                return None
            
            # Company
            company_elem = card.find("span", class_=re.compile(r"company|startup"))
            company = company_elem.get_text(strip=True) if company_elem else "Startup"
            
            # Link
            link_elem = card.find("a", href=True)
            job_url = ""
            job_id = ""
            if link_elem:
                href = link_elem.get("href", "")
                if href.startswith("/"):
                    job_url = f"{self.BASE_URL}{href}"
                else:
                    job_url = href
                job_id = href.split("/")[-1] if href else hashlib.md5(title.encode()).hexdigest()[:12]
            
            unique_id = hashlib.md5(f"wellfound:{job_id}".encode()).hexdigest()[:16]
            
            # Location
            location_elem = card.find("span", class_=re.compile(r"location"))
            location = location_elem.get_text(strip=True) if location_elem else "Remote"
            
            return {
                "id": unique_id,
                "title": title,
                "company": company,
                "location": location,
                "apply_url": job_url,
                "source": "wellfound",
                "source_id": job_id,
                "remote": "remote" in location.lower(),
                "scraped_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error parsing Wellfound card: {e}")
            return None


async def scrape_wellfound_jobs(
    keywords: str = "",
    role: str = "engineering",
    remote: bool = False,
    limit: int = 50
) -> List[Dict]:
    """
    Convenience function to scrape Wellfound startup jobs.
    """
    scraper = WellfoundScraper()
    return await scraper.search_jobs(
        keywords=keywords,
        role=role,
        remote=remote,
        limit=limit
    )


if __name__ == "__main__":
    async def test():
        jobs = await scrape_wellfound_jobs(keywords="python", limit=10)
        print(f"Found {len(jobs)} startup jobs\n")
        
        for job in jobs:
            print(f"{job['title']} at {job['company']}")
            print(f"  Location: {job.get('location', 'N/A')}")
            print(f"  URL: {job['apply_url']}")
            print()
    
    asyncio.run(test())
