"""
Remote OK Scraper
=================
Scrapes remote job listings from RemoteOK's public API.
This is one of the easiest sources - they have a public JSON API!
"""

import asyncio
import httpx
import logging
from datetime import datetime
from typing import List, Dict, Any
import hashlib

logger = logging.getLogger(__name__)


class RemoteOKScraper:
    """
    RemoteOK Scraper - Uses their public JSON API.
    No rate limiting needed, but we'll be respectful.
    """
    
    API_URL = "https://remoteok.com/api"
    
    def __init__(self):
        self.headers = {
            "User-Agent": "GrowthEngine/1.0 (Job Aggregator)",
            "Accept": "application/json",
        }
    
    async def get_jobs(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Fetch all remote jobs from RemoteOK.
        
        Args:
            limit: Maximum number of jobs to return
            
        Returns:
            List of job dictionaries
        """
        jobs = []
        
        try:
            async with httpx.AsyncClient(headers=self.headers, timeout=30) as client:
                response = await client.get(self.API_URL)
                response.raise_for_status()
                
                data = response.json()
                
                # First element is metadata/legal notice, skip it
                job_list = data[1:] if len(data) > 1 else []
                
                for job_data in job_list[:limit]:
                    job = self._parse_job(job_data)
                    if job:
                        jobs.append(job)
                
                logger.info(f"RemoteOK: Fetched {len(jobs)} remote jobs")
                
        except Exception as e:
            logger.error(f"RemoteOK scraper error: {e}")
        
        return jobs
    
    async def search_jobs(
        self,
        keywords: str = "",
        tags: List[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Search/filter RemoteOK jobs.
        
        Args:
            keywords: Search keywords to filter by title/company
            tags: Filter by tags (e.g., ["python", "react", "senior"])
            limit: Maximum results
            
        Returns:
            Filtered list of jobs
        """
        all_jobs = await self.get_jobs(limit=500)  # Get more to filter
        
        filtered = []
        keywords_lower = keywords.lower() if keywords else ""
        tags_lower = [t.lower() for t in (tags or [])]
        
        for job in all_jobs:
            # Keyword match
            if keywords_lower:
                title = job.get("title", "").lower()
                company = job.get("company", "").lower()
                description = job.get("description", "").lower()
                
                if keywords_lower not in title and keywords_lower not in company and keywords_lower not in description:
                    continue
            
            # Tag match
            if tags_lower:
                job_tags = [t.lower() for t in job.get("tags", [])]
                if not any(t in job_tags for t in tags_lower):
                    continue
            
            filtered.append(job)
            
            if len(filtered) >= limit:
                break
        
        return filtered
    
    def _parse_job(self, job_data: Dict) -> Dict[str, Any]:
        """Parse RemoteOK job data into standard format"""
        try:
            job_id = str(job_data.get("id", ""))
            unique_id = hashlib.md5(f"remoteok:{job_id}".encode()).hexdigest()[:16]
            
            # Parse salary
            salary_min = job_data.get("salary_min")
            salary_max = job_data.get("salary_max")
            
            # Convert to integers if strings
            if salary_min and isinstance(salary_min, str):
                salary_min = int(salary_min.replace(",", "").replace("$", ""))
            if salary_max and isinstance(salary_max, str):
                salary_max = int(salary_max.replace(",", "").replace("$", ""))
            
            # Parse date
            posted_date = None
            if job_data.get("date"):
                try:
                    posted_date = datetime.fromisoformat(job_data["date"].replace("Z", "+00:00"))
                except:
                    posted_date = None
            
            return {
                "id": unique_id,
                "title": job_data.get("position", "Unknown Position"),
                "company": job_data.get("company", "Unknown Company"),
                "company_logo": job_data.get("company_logo", ""),
                "location": job_data.get("location", "Remote"),
                "salary_min": salary_min,
                "salary_max": salary_max,
                "description": job_data.get("description", ""),
                "apply_url": job_data.get("url", f"https://remoteok.com/remote-jobs/{job_id}"),
                "source": "remoteok",
                "source_id": job_id,
                "posted_date": posted_date.isoformat() if posted_date else None,
                "tags": job_data.get("tags", []),
                "remote": True,
                "job_type": "full-time",
                "match_score": 0.0,
                "scraped_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error parsing RemoteOK job: {e}")
            return None


async def scrape_remoteok_jobs(
    keywords: str = "",
    tags: List[str] = None,
    limit: int = 50
) -> List[Dict]:
    """
    Convenience function to scrape RemoteOK jobs.
    """
    scraper = RemoteOKScraper()
    return await scraper.search_jobs(keywords=keywords, tags=tags, limit=limit)


if __name__ == "__main__":
    async def test():
        # Get all jobs
        jobs = await scrape_remoteok_jobs(limit=10)
        print(f"Found {len(jobs)} jobs\n")
        
        for job in jobs:
            salary = ""
            if job.get("salary_min") and job.get("salary_max"):
                salary = f"${job['salary_min']:,} - ${job['salary_max']:,}"
            
            print(f"{job['title']} at {job['company']}")
            print(f"  Tags: {', '.join(job.get('tags', []))}")
            print(f"  Salary: {salary or 'Not specified'}")
            print(f"  URL: {job['apply_url']}")
            print()
    
    asyncio.run(test())
