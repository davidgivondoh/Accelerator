"""
Scholarship & Fellowship Scrapers
==================================
Scrapes scholarships, fellowships, and educational opportunities
from major platforms worldwide.
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


class ScholarshipsComScraper(BaseScraper):
    """Scraper for Scholarships.com"""
    
    def __init__(self):
        super().__init__(
            name="ScholarshipsCom",
            base_url="https://www.scholarships.com",
            rate_limit=0.5,
            timeout=45.0
        )
        self.categories = [
            "college-scholarships",
            "graduate-scholarships",
            "minority-scholarships",
            "women-scholarships",
            "stem-scholarships",
            "international-student-scholarships",
            "undergraduate-scholarships",
            "doctoral-scholarships",
        ]
    
    async def scrape(self, max_pages: int = 30) -> List[Opportunity]:
        """Scrape scholarships"""
        opportunities = []
        
        async with httpx.AsyncClient(timeout=self.timeout, headers=self.default_headers) as client:
            for category in self.categories:
                try:
                    await self._wait_for_rate_limit()
                    url = f"{self.base_url}/financial-aid/{category}/"
                    response = await client.get(url)
                    
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.text, 'lxml')
                        items = soup.find_all(['div', 'article'], class_=re.compile('scholarship'))
                        
                        for item in items[:50]:
                            opp = self._parse_scholarship(item, category)
                            if opp:
                                opportunities.append(opp)
                except Exception as e:
                    logger.error(f"Scholarships.com: Error scraping {category}: {e}")
        
        return opportunities
    
    def _parse_scholarship(self, item, category: str) -> Optional[Opportunity]:
        """Parse scholarship item"""
        try:
            title_elem = item.find(['h2', 'h3', 'a', 'span'])
            if not title_elem:
                return None
            
            title = title_elem.get_text(strip=True)
            link = item.find('a', href=True)
            url = link['href'] if link else ""
            
            if url and not url.startswith('http'):
                url = f"{self.base_url}{url}"
            
            # Extract amount if present
            amount_match = re.search(r'\$[\d,]+', item.get_text())
            amount = amount_match.group(0) if amount_match else None
            
            return Opportunity(
                id=Opportunity.generate_id("scholarshipscom", url + title),
                title=title,
                company="Various",
                location="USA",
                description=item.get_text()[:500],
                apply_url=url or self.base_url,
                source="Scholarships.com",
                source_id=url,
                opportunity_type="scholarship",
                remote=True,
                tags=[category, "scholarship", "education"],
                metadata={"amount": amount} if amount else {}
            )
        except Exception as e:
            logger.error(f"Scholarships.com: Parse error: {e}")
            return None
    
    async def search(self, query: str, **kwargs) -> List[Opportunity]:
        return await self.scrape()


class FastwedScraper(BaseScraper):
    """Scraper for Fastweb scholarships"""
    
    def __init__(self):
        super().__init__(
            name="Fastweb",
            base_url="https://www.fastweb.com",
            rate_limit=0.5,
            timeout=45.0
        )
    
    async def scrape(self, max_pages: int = 20) -> List[Opportunity]:
        """Scrape Fastweb scholarships"""
        opportunities = []
        
        async with httpx.AsyncClient(timeout=self.timeout, headers=self.default_headers) as client:
            categories = [
                "scholarships-by-type",
                "scholarships-by-major",
                "scholarships-for-minorities",
                "scholarships-for-women",
            ]
            
            for category in categories:
                try:
                    await self._wait_for_rate_limit()
                    url = f"{self.base_url}/directory/{category}"
                    response = await client.get(url)
                    
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.text, 'lxml')
                        items = soup.find_all(['div', 'li'], class_=re.compile('scholarship|award'))
                        
                        for item in items[:30]:
                            opp = self._parse_item(item)
                            if opp:
                                opportunities.append(opp)
                except Exception as e:
                    logger.error(f"Fastweb: Error: {e}")
        
        return opportunities
    
    def _parse_item(self, item) -> Optional[Opportunity]:
        """Parse Fastweb item"""
        try:
            title_elem = item.find(['h2', 'h3', 'a'])
            if not title_elem:
                return None
            
            title = title_elem.get_text(strip=True)
            link = item.find('a', href=True)
            url = link['href'] if link else self.base_url
            
            if not url.startswith('http'):
                url = f"{self.base_url}{url}"
            
            return Opportunity(
                id=Opportunity.generate_id("fastweb", url),
                title=title,
                company="Various",
                location="USA",
                description=item.get_text()[:500],
                apply_url=url,
                source="Fastweb",
                source_id=url,
                opportunity_type="scholarship",
                remote=True,
                tags=["scholarship", "education", "usa"]
            )
        except:
            return None
    
    async def search(self, query: str, **kwargs) -> List[Opportunity]:
        return await self.scrape()


class FellowshipsScraper(BaseScraper):
    """Scraper for major fellowship programs"""
    
    def __init__(self):
        super().__init__(
            name="Fellowships",
            base_url="https://www.profellow.com",
            rate_limit=0.5,
            timeout=45.0
        )
    
    async def scrape(self, max_pages: int = 20) -> List[Opportunity]:
        """Get major fellowship opportunities"""
        opportunities = []
        
        # Major fellowship programs (well-known, prestigious)
        fellowships = [
            # Rhodes Scholar
            {
                "title": "Rhodes Scholarship",
                "company": "Rhodes Trust",
                "url": "https://www.rhodeshouse.ox.ac.uk/scholarships/",
                "description": "Full funding for postgraduate study at Oxford University. One of the world's most prestigious scholarships.",
                "location": "Oxford, UK",
                "amount": "Full funding"
            },
            # Fulbright
            {
                "title": "Fulbright Scholarship Program",
                "company": "US Department of State",
                "url": "https://us.fulbrightonline.org/",
                "description": "International educational exchange program for students, scholars, and professionals.",
                "location": "Global",
                "amount": "Full funding"
            },
            # Marshall
            {
                "title": "Marshall Scholarship",
                "company": "Marshall Aid Commemoration Commission",
                "url": "https://www.marshallscholarship.org/",
                "description": "Funding for Americans to study at any UK university.",
                "location": "UK",
                "amount": "Full funding"
            },
            # Gates Cambridge
            {
                "title": "Gates Cambridge Scholarship",
                "company": "Gates Cambridge Trust",
                "url": "https://www.gatescambridge.org/",
                "description": "Full-cost scholarship to study at Cambridge University.",
                "location": "Cambridge, UK",
                "amount": "Full funding"
            },
            # Chevening
            {
                "title": "Chevening Scholarship",
                "company": "UK Government",
                "url": "https://www.chevening.org/",
                "description": "UK government's global scholarship programme for future leaders.",
                "location": "UK",
                "amount": "Full funding"
            },
            # Schwarzman
            {
                "title": "Schwarzman Scholars",
                "company": "Schwarzman Scholars",
                "url": "https://www.schwarzmanscholars.org/",
                "description": "One-year Master's degree at Tsinghua University in Beijing.",
                "location": "Beijing, China",
                "amount": "Full funding"
            },
            # Knight-Hennessy
            {
                "title": "Knight-Hennessy Scholars",
                "company": "Stanford University",
                "url": "https://knight-hennessy.stanford.edu/",
                "description": "Full funding for graduate study at Stanford University.",
                "location": "Stanford, USA",
                "amount": "Full funding"
            },
            # Rotary Peace Fellowship
            {
                "title": "Rotary Peace Fellowship",
                "company": "Rotary International",
                "url": "https://www.rotary.org/en/our-programs/peace-fellowships",
                "description": "Fellowship for peace and conflict resolution studies.",
                "location": "Global",
                "amount": "Full funding"
            },
            # DAAD
            {
                "title": "DAAD Scholarship",
                "company": "German Academic Exchange Service",
                "url": "https://www.daad.de/en/",
                "description": "Scholarships for studying in Germany.",
                "location": "Germany",
                "amount": "Full funding"
            },
            # Erasmus Mundus
            {
                "title": "Erasmus Mundus Joint Masters",
                "company": "European Commission",
                "url": "https://erasmus-plus.ec.europa.eu/",
                "description": "Joint Master's degrees at multiple European universities.",
                "location": "Europe",
                "amount": "Full funding"
            },
            # Commonwealth Scholarship
            {
                "title": "Commonwealth Scholarship",
                "company": "Commonwealth Scholarship Commission",
                "url": "https://cscuk.fcdo.gov.uk/",
                "description": "Scholarships for Commonwealth country citizens to study in the UK.",
                "location": "UK",
                "amount": "Full funding"
            },
            # Mandela Washington Fellowship
            {
                "title": "Mandela Washington Fellowship (YALI)",
                "company": "US Department of State",
                "url": "https://yali.state.gov/washington-fellowship/",
                "description": "Leadership program for young African leaders.",
                "location": "USA",
                "amount": "Fully funded"
            },
            # Australia Awards
            {
                "title": "Australia Awards Scholarships",
                "company": "Australian Government",
                "url": "https://www.dfat.gov.au/people-to-people/australia-awards",
                "description": "Scholarships for study in Australia.",
                "location": "Australia",
                "amount": "Full funding"
            },
            # Japanese Government (MEXT)
            {
                "title": "MEXT Scholarship (Japan)",
                "company": "Japanese Government",
                "url": "https://www.studyinjapan.go.jp/en/smap_stopj-applications_scholarship.html",
                "description": "Japanese government scholarship for international students.",
                "location": "Japan",
                "amount": "Full funding"
            },
            # Korea Foundation
            {
                "title": "Korean Government Scholarship (KGSP)",
                "company": "Korean Government",
                "url": "https://www.studyinkorea.go.kr/",
                "description": "Korean government scholarship for graduate studies.",
                "location": "South Korea",
                "amount": "Full funding"
            },
            # Chinese Government Scholarship
            {
                "title": "Chinese Government Scholarship",
                "company": "China Scholarship Council",
                "url": "https://www.campuschina.org/",
                "description": "Full scholarship to study in China.",
                "location": "China",
                "amount": "Full funding"
            },
            # Swiss Government Excellence
            {
                "title": "Swiss Government Excellence Scholarships",
                "company": "Swiss Government",
                "url": "https://www.sbfi.admin.ch/sbfi/en/home/education/scholarships-and-grants.html",
                "description": "Scholarships for research and study in Switzerland.",
                "location": "Switzerland",
                "amount": "Full funding"
            },
            # Mitchell Scholarship
            {
                "title": "Mitchell Scholarship",
                "company": "US-Ireland Alliance",
                "url": "https://www.us-irelandalliance.org/mitchellscholarship",
                "description": "One year of graduate study in Ireland.",
                "location": "Ireland",
                "amount": "Full funding"
            },
            # Truman Scholarship
            {
                "title": "Truman Scholarship",
                "company": "Truman Foundation",
                "url": "https://www.truman.gov/",
                "description": "Scholarship for future public service leaders.",
                "location": "USA",
                "amount": "$30,000"
            },
            # Goldwater Scholarship
            {
                "title": "Goldwater Scholarship",
                "company": "Goldwater Foundation",
                "url": "https://goldwaterscholarship.gov/",
                "description": "Scholarship for STEM undergraduates.",
                "location": "USA",
                "amount": "$7,500/year"
            },
            # Boren Fellowship
            {
                "title": "Boren Fellowship",
                "company": "National Security Education Program",
                "url": "https://www.borenawards.org/",
                "description": "Funding for international study in critical languages.",
                "location": "Global",
                "amount": "$25,000"
            },
            # Ford Foundation Fellowship
            {
                "title": "Ford Foundation Fellowship",
                "company": "Ford Foundation",
                "url": "https://sites.nationalacademies.org/pga/fordfellowships/",
                "description": "Fellowship for diverse PhD students and scholars.",
                "location": "USA",
                "amount": "$28,000/year"
            },
            # Hertz Fellowship
            {
                "title": "Hertz Fellowship",
                "company": "Fannie and John Hertz Foundation",
                "url": "https://www.hertzfoundation.org/",
                "description": "Fellowship for applied physical sciences PhD students.",
                "location": "USA",
                "amount": "$250,000+"
            },
            # NSF Graduate Research Fellowship
            {
                "title": "NSF Graduate Research Fellowship",
                "company": "National Science Foundation",
                "url": "https://www.nsfgrfp.org/",
                "description": "Fellowship for STEM graduate students.",
                "location": "USA",
                "amount": "$147,000 total"
            },
            # Paul & Daisy Soros Fellowship
            {
                "title": "Paul & Daisy Soros Fellowship for New Americans",
                "company": "Soros Foundation",
                "url": "https://www.pdsoros.org/",
                "description": "Fellowship for immigrants and children of immigrants.",
                "location": "USA",
                "amount": "$90,000"
            },
        ]
        
        for fellowship in fellowships:
            opportunities.append(Opportunity(
                id=Opportunity.generate_id("fellowship", fellowship["url"]),
                title=fellowship["title"],
                company=fellowship["company"],
                location=fellowship["location"],
                description=fellowship["description"],
                apply_url=fellowship["url"],
                source="Fellowships",
                source_id=fellowship["url"],
                opportunity_type="fellowship",
                remote=False,
                tags=["fellowship", "scholarship", "education", "prestigious"],
                metadata={"amount": fellowship.get("amount")}
            ))
        
        # Scrape ProFellow for more
        async with httpx.AsyncClient(timeout=self.timeout, headers=self.default_headers) as client:
            try:
                await self._wait_for_rate_limit()
                url = f"{self.base_url}/fellowships/"
                response = await client.get(url)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'lxml')
                    items = soup.find_all(['div', 'article'], class_=re.compile('fellowship|post'))
                    
                    for item in items[:50]:
                        title_elem = item.find(['h2', 'h3', 'a'])
                        if title_elem:
                            title = title_elem.get_text(strip=True)
                            link = item.find('a', href=True)
                            url = link['href'] if link else ""
                            
                            if url and not url.startswith('http'):
                                url = f"{self.base_url}{url}"
                            
                            opportunities.append(Opportunity(
                                id=Opportunity.generate_id("profellow", url + title),
                                title=title,
                                company="Various",
                                location="Global",
                                description=item.get_text()[:500],
                                apply_url=url or self.base_url,
                                source="ProFellow",
                                source_id=url,
                                opportunity_type="fellowship",
                                remote=True,
                                tags=["fellowship", "education"]
                            ))
            except Exception as e:
                logger.error(f"ProFellow: Error: {e}")
        
        return opportunities
    
    async def search(self, query: str, **kwargs) -> List[Opportunity]:
        return await self.scrape()


class InternationalScholarshipsScraper(BaseScraper):
    """Scraper for international scholarships from various countries"""
    
    def __init__(self):
        super().__init__(
            name="InternationalScholarships",
            base_url="https://www.scholars4dev.com",
            rate_limit=0.5,
            timeout=45.0
        )
    
    async def scrape(self, max_pages: int = 20) -> List[Opportunity]:
        """Scrape international scholarships"""
        opportunities = []
        
        categories = [
            "scholarships-in-usa",
            "scholarships-in-uk",
            "scholarships-in-canada",
            "scholarships-in-australia",
            "scholarships-in-germany",
            "scholarships-in-netherlands",
            "scholarships-in-sweden",
            "scholarships-in-japan",
            "scholarships-in-korea",
            "scholarships-for-africans",
            "scholarships-for-asians",
            "fully-funded-scholarships",
        ]
        
        async with httpx.AsyncClient(timeout=self.timeout, headers=self.default_headers) as client:
            for category in categories:
                try:
                    await self._wait_for_rate_limit()
                    url = f"{self.base_url}/{category}/"
                    response = await client.get(url)
                    
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.text, 'lxml')
                        items = soup.find_all(['article', 'div'], class_=re.compile('post|entry'))
                        
                        for item in items[:20]:
                            opp = self._parse_item(item, category)
                            if opp:
                                opportunities.append(opp)
                except Exception as e:
                    logger.error(f"Scholars4dev: Error scraping {category}: {e}")
        
        return opportunities
    
    def _parse_item(self, item, category: str) -> Optional[Opportunity]:
        """Parse scholarship item"""
        try:
            title_elem = item.find(['h2', 'h3', 'a'])
            if not title_elem:
                return None
            
            title = title_elem.get_text(strip=True)
            link = item.find('a', href=True)
            url = link['href'] if link else ""
            
            if url and not url.startswith('http'):
                url = f"{self.base_url}{url}"
            
            # Extract location from category
            location_map = {
                "usa": "USA",
                "uk": "UK", 
                "canada": "Canada",
                "australia": "Australia",
                "germany": "Germany",
                "netherlands": "Netherlands",
                "sweden": "Sweden",
                "japan": "Japan",
                "korea": "South Korea",
            }
            
            location = "Global"
            for key, loc in location_map.items():
                if key in category:
                    location = loc
                    break
            
            return Opportunity(
                id=Opportunity.generate_id("scholars4dev", url + title),
                title=title,
                company="Various",
                location=location,
                description=item.get_text()[:500],
                apply_url=url or self.base_url,
                source="Scholars4Dev",
                source_id=url,
                opportunity_type="scholarship",
                remote=False,
                tags=[category, "scholarship", "international", "education"]
            )
        except:
            return None
    
    async def search(self, query: str, **kwargs) -> List[Opportunity]:
        return await self.scrape()


# Convenience functions
async def scrape_scholarships_com() -> List[Dict]:
    """Scrape Scholarships.com"""
    scraper = ScholarshipsComScraper()
    opportunities = await scraper.scrape()
    return [opp.to_dict() for opp in opportunities]


async def scrape_fastweb() -> List[Dict]:
    """Scrape Fastweb"""
    scraper = FastwedScraper()
    opportunities = await scraper.scrape()
    return [opp.to_dict() for opp in opportunities]


async def scrape_fellowships() -> List[Dict]:
    """Scrape fellowship programs"""
    scraper = FellowshipsScraper()
    opportunities = await scraper.scrape()
    return [opp.to_dict() for opp in opportunities]


async def scrape_international_scholarships() -> List[Dict]:
    """Scrape international scholarships"""
    scraper = InternationalScholarshipsScraper()
    opportunities = await scraper.scrape()
    return [opp.to_dict() for opp in opportunities]


async def scrape_all_scholarships_and_fellowships() -> List[Dict]:
    """Scrape all scholarship and fellowship sources"""
    all_opportunities = []
    
    scrapers = [
        scrape_scholarships_com(),
        scrape_fastweb(),
        scrape_fellowships(),
        scrape_international_scholarships(),
    ]
    
    results = await asyncio.gather(*scrapers, return_exceptions=True)
    
    for result in results:
        if isinstance(result, list):
            all_opportunities.extend(result)
        elif isinstance(result, Exception):
            logger.error(f"Scholarship scraper error: {result}")
    
    return all_opportunities
