"""
African Opportunities Scraper
=============================
Scrapes opportunities from OpportunitiesForAfricans.com, VC4Africa, 
and other African-focused platforms.
"""

import asyncio
import httpx
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging
import re
import json

from .base_scraper import BaseScraper, Opportunity

logger = logging.getLogger(__name__)


class OpportunitiesForAfricansScraper(BaseScraper):
    """Scraper for OpportunitiesForAfricans.com - largest African opportunity aggregator"""
    
    def __init__(self):
        super().__init__(
            name="OpportunitiesForAfricans",
            base_url="https://www.opportunitiesforafricans.com",
            rate_limit=0.5,  # Respectful rate
            timeout=45.0
        )
        self.categories = [
            "scholarships",
            "fellowships", 
            "grants",
            "internships",
            "jobs",
            "competitions",
            "conferences",
            "workshops",
            "entrepreneurship",
            "awards",
            "training-programs",
            "phd-scholarships",
            "masters-scholarships",
            "undergraduate-scholarships",
            "postdoctoral-fellowships",
            "research-grants",
            "business-grants",
            "women-opportunities",
            "youth-opportunities",
            "stem-opportunities",
        ]
    
    async def scrape(self, max_pages: int = 50) -> List[Opportunity]:
        """Scrape opportunities from all categories"""
        opportunities = []
        
        async with httpx.AsyncClient(timeout=self.timeout, headers=self.default_headers) as client:
            for category in self.categories:
                try:
                    cat_opps = await self._scrape_category(client, category, max_pages // len(self.categories) + 1)
                    opportunities.extend(cat_opps)
                    logger.info(f"OFA: Scraped {len(cat_opps)} from {category}")
                except Exception as e:
                    logger.error(f"OFA: Error scraping {category}: {e}")
                await asyncio.sleep(2)  # Rate limit between categories
        
        return opportunities
    
    async def _scrape_category(self, client: httpx.AsyncClient, category: str, max_pages: int) -> List[Opportunity]:
        """Scrape a specific category"""
        opportunities = []
        
        for page in range(1, max_pages + 1):
            try:
                await self._wait_for_rate_limit()
                url = f"{self.base_url}/category/{category}/page/{page}/"
                response = await client.get(url)
                
                if response.status_code != 200:
                    break
                    
                soup = BeautifulSoup(response.text, 'lxml')
                articles = soup.find_all('article', class_='post')
                
                if not articles:
                    break
                
                for article in articles:
                    opp = self._parse_article(article, category)
                    if opp:
                        opportunities.append(opp)
                        
            except Exception as e:
                logger.error(f"OFA: Error on page {page} of {category}: {e}")
                break
                
        return opportunities
    
    def _parse_article(self, article, category: str) -> Optional[Opportunity]:
        """Parse article into opportunity"""
        try:
            title_elem = article.find('h2', class_='entry-title')
            if not title_elem or not title_elem.find('a'):
                return None
                
            title = title_elem.get_text(strip=True)
            link = title_elem.find('a')['href']
            
            # Extract deadline if present
            deadline = None
            content = article.get_text()
            deadline_match = re.search(r'deadline[:\s]*(\w+\s+\d{1,2},?\s+\d{4})', content, re.I)
            if deadline_match:
                try:
                    deadline = datetime.strptime(deadline_match.group(1).replace(',', ''), '%B %d %Y')
                except:
                    pass
            
            # Map category to opportunity type
            type_map = {
                'scholarships': 'scholarship',
                'fellowships': 'fellowship',
                'grants': 'grant',
                'internships': 'internship',
                'jobs': 'job',
                'competitions': 'competition',
                'conferences': 'conference',
                'workshops': 'workshop',
                'awards': 'award',
            }
            opp_type = type_map.get(category.split('-')[0], 'opportunity')
            
            return Opportunity(
                id=Opportunity.generate_id("ofa", link),
                title=title,
                company="Various",
                location="Africa / Global",
                description=content[:500] if content else "",
                apply_url=link,
                source="OpportunitiesForAfricans",
                source_id=link,
                deadline=deadline,
                opportunity_type=opp_type,
                remote=True,
                tags=[category, "africa", opp_type],
                metadata={"category": category}
            )
        except Exception as e:
            logger.error(f"OFA: Error parsing article: {e}")
            return None
    
    async def search(self, query: str, **kwargs) -> List[Opportunity]:
        """Search for opportunities"""
        opportunities = []
        
        async with httpx.AsyncClient(timeout=self.timeout, headers=self.default_headers) as client:
            await self._wait_for_rate_limit()
            url = f"{self.base_url}/?s={query.replace(' ', '+')}"
            response = await client.get(url)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'lxml')
                articles = soup.find_all('article', class_='post')
                
                for article in articles:
                    opp = self._parse_article(article, "search")
                    if opp:
                        opportunities.append(opp)
        
        return opportunities


class VC4AfricaScraper(BaseScraper):
    """Scraper for VC4Africa - African startup and venture capital platform"""
    
    def __init__(self):
        super().__init__(
            name="VC4Africa",
            base_url="https://vc4a.com",
            rate_limit=0.5,
            timeout=45.0
        )
    
    async def scrape(self, max_pages: int = 20) -> List[Opportunity]:
        """Scrape funding opportunities and programs"""
        opportunities = []
        
        async with httpx.AsyncClient(timeout=self.timeout, headers=self.default_headers) as client:
            # Scrape funding opportunities
            try:
                opps = await self._scrape_funding(client, max_pages)
                opportunities.extend(opps)
            except Exception as e:
                logger.error(f"VC4A: Error scraping funding: {e}")
            
            # Scrape accelerator programs
            try:
                programs = await self._scrape_programs(client)
                opportunities.extend(programs)
            except Exception as e:
                logger.error(f"VC4A: Error scraping programs: {e}")
        
        return opportunities
    
    async def _scrape_funding(self, client: httpx.AsyncClient, max_pages: int) -> List[Opportunity]:
        """Scrape funding opportunities"""
        opportunities = []
        
        for page in range(1, max_pages + 1):
            try:
                await self._wait_for_rate_limit()
                url = f"{self.base_url}/funding/page/{page}/"
                response = await client.get(url)
                
                if response.status_code != 200:
                    break
                    
                soup = BeautifulSoup(response.text, 'lxml')
                items = soup.find_all('div', class_='funding-item') or soup.find_all('article')
                
                if not items:
                    break
                
                for item in items:
                    opp = self._parse_funding_item(item)
                    if opp:
                        opportunities.append(opp)
                        
            except Exception as e:
                logger.error(f"VC4A: Error on funding page {page}: {e}")
                break
                
        return opportunities
    
    async def _scrape_programs(self, client: httpx.AsyncClient) -> List[Opportunity]:
        """Scrape accelerator and incubator programs"""
        opportunities = []
        
        try:
            await self._wait_for_rate_limit()
            url = f"{self.base_url}/programs/"
            response = await client.get(url)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'lxml')
                programs = soup.find_all('div', class_='program-item') or soup.find_all('article')
                
                for program in programs:
                    title_elem = program.find(['h2', 'h3', 'a'])
                    if title_elem:
                        title = title_elem.get_text(strip=True)
                        link = title_elem.get('href', '') if title_elem.name == 'a' else program.find('a', href=True)
                        if isinstance(link, dict):
                            link = link.get('href', '')
                        elif hasattr(link, 'get'):
                            link = link.get('href', '')
                        
                        if link and not link.startswith('http'):
                            link = f"{self.base_url}{link}"
                        
                        opportunities.append(Opportunity(
                            id=Opportunity.generate_id("vc4a", str(link)),
                            title=title,
                            company="VC4Africa",
                            location="Africa",
                            description=program.get_text()[:500],
                            apply_url=str(link) if link else self.base_url,
                            source="VC4Africa",
                            source_id=str(link),
                            opportunity_type="accelerator",
                            remote=True,
                            tags=["africa", "startup", "funding", "accelerator"]
                        ))
        except Exception as e:
            logger.error(f"VC4A: Error scraping programs: {e}")
            
        return opportunities
    
    def _parse_funding_item(self, item) -> Optional[Opportunity]:
        """Parse funding item"""
        try:
            title_elem = item.find(['h2', 'h3', 'a'])
            if not title_elem:
                return None
                
            title = title_elem.get_text(strip=True)
            link = item.find('a', href=True)
            url = link['href'] if link else ""
            
            if url and not url.startswith('http'):
                url = f"{self.base_url}{url}"
            
            return Opportunity(
                id=Opportunity.generate_id("vc4a", url),
                title=title,
                company="Various",
                location="Africa",
                description=item.get_text()[:500],
                apply_url=url,
                source="VC4Africa",
                source_id=url,
                opportunity_type="funding",
                remote=True,
                tags=["africa", "funding", "startup", "venture"]
            )
        except Exception as e:
            logger.error(f"VC4A: Error parsing item: {e}")
            return None
    
    async def search(self, query: str, **kwargs) -> List[Opportunity]:
        """Search VC4Africa"""
        return await self.scrape(max_pages=5)


class AfricanLeadershipScraper(BaseScraper):
    """Scraper for African Leadership Academy and related programs"""
    
    def __init__(self):
        super().__init__(
            name="AfricanLeadership",
            base_url="https://www.africanleadershipacademy.org",
            rate_limit=0.5,
            timeout=45.0
        )
    
    async def scrape(self, max_pages: int = 10) -> List[Opportunity]:
        """Scrape leadership programs and scholarships"""
        opportunities = []
        
        # Pre-defined African leadership opportunities (these are well-known programs)
        programs = [
            {
                "title": "African Leadership Academy - 2-Year Pre-University Program",
                "url": "https://www.africanleadershipacademy.org/apply/",
                "type": "scholarship",
                "description": "Full scholarship for young African leaders ages 15-19"
            },
            {
                "title": "African Leadership University Scholarship",
                "url": "https://www.alueducation.com/scholarships/",
                "type": "scholarship",
                "description": "University scholarships for African students"
            },
            {
                "title": "Anzisha Prize for Young African Entrepreneurs",
                "url": "https://anzishaprize.org/",
                "type": "competition",
                "description": "$100,000 prize pool for African entrepreneurs under 22"
            },
            {
                "title": "African Leadership Network Fellowship",
                "url": "https://africanleadershipnetwork.com/",
                "type": "fellowship",
                "description": "Fellowship for emerging African leaders"
            },
            {
                "title": "Tony Elumelu Foundation Entrepreneurship Programme",
                "url": "https://www.tonyelumelufoundation.org/",
                "type": "grant",
                "description": "$5,000 seed funding + mentorship for African entrepreneurs"
            },
            {
                "title": "MasterCard Foundation Scholars Program",
                "url": "https://mastercardfdn.org/all/scholars/",
                "type": "scholarship",
                "description": "Full scholarships for talented African students"
            },
        ]
        
        for prog in programs:
            opportunities.append(Opportunity(
                id=Opportunity.generate_id("african_leadership", prog["url"]),
                title=prog["title"],
                company="African Leadership Programs",
                location="Africa / Global",
                description=prog["description"],
                apply_url=prog["url"],
                source="AfricanLeadership",
                source_id=prog["url"],
                opportunity_type=prog["type"],
                remote=True,
                tags=["africa", "leadership", prog["type"]]
            ))
        
        return opportunities
    
    async def search(self, query: str, **kwargs) -> List[Opportunity]:
        return await self.scrape()


# Convenience functions
async def scrape_opportunities_for_africans(max_pages: int = 50) -> List[Dict]:
    """Scrape OpportunitiesForAfricans.com"""
    scraper = OpportunitiesForAfricansScraper()
    opportunities = await scraper.scrape(max_pages)
    return [opp.to_dict() for opp in opportunities]


async def scrape_vc4africa(max_pages: int = 20) -> List[Dict]:
    """Scrape VC4Africa"""
    scraper = VC4AfricaScraper()
    opportunities = await scraper.scrape(max_pages)
    return [opp.to_dict() for opp in opportunities]


async def scrape_african_leadership() -> List[Dict]:
    """Scrape African Leadership programs"""
    scraper = AfricanLeadershipScraper()
    opportunities = await scraper.scrape()
    return [opp.to_dict() for opp in opportunities]


async def scrape_all_african_opportunities() -> List[Dict]:
    """Scrape all African opportunity sources"""
    all_opportunities = []
    
    scrapers = [
        scrape_opportunities_for_africans(50),
        scrape_vc4africa(20),
        scrape_african_leadership(),
    ]
    
    results = await asyncio.gather(*scrapers, return_exceptions=True)
    
    for result in results:
        if isinstance(result, list):
            all_opportunities.extend(result)
        elif isinstance(result, Exception):
            logger.error(f"African scraper error: {result}")
    
    return all_opportunities
