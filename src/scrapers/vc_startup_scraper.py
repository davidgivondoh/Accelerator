"""
Venture Capital & Startup Scrapers
===================================
Scrapes opportunities from YCombinator, major VC firms, 
accelerators, and startup platforms.
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


class YCombinatorScraper(BaseScraper):
    """Scraper for Y Combinator jobs, startup school, and programs"""
    
    def __init__(self):
        super().__init__(
            name="YCombinator",
            base_url="https://www.ycombinator.com",
            rate_limit=0.5,
            timeout=45.0
        )
        self.workatastartup_url = "https://www.workatastartup.com"
    
    async def scrape(self, max_pages: int = 50) -> List[Opportunity]:
        """Scrape YC jobs and programs"""
        opportunities = []
        
        async with httpx.AsyncClient(timeout=self.timeout, headers=self.default_headers) as client:
            # YC startup jobs
            try:
                jobs = await self._scrape_startup_jobs(client, max_pages)
                opportunities.extend(jobs)
            except Exception as e:
                logger.error(f"YC: Error scraping jobs: {e}")
            
            # YC programs
            programs = self._get_yc_programs()
            opportunities.extend(programs)
        
        return opportunities
    
    async def _scrape_startup_jobs(self, client: httpx.AsyncClient, max_pages: int) -> List[Opportunity]:
        """Scrape Work at a Startup jobs"""
        opportunities = []
        
        # YC company jobs API endpoint
        roles = [
            "software-engineer", "machine-learning", "data-scientist",
            "product-manager", "designer", "founder", "operations",
            "marketing", "sales", "finance", "legal"
        ]
        
        for role in roles:
            try:
                await self._wait_for_rate_limit()
                url = f"{self.workatastartup_url}/companies?role={role}"
                response = await client.get(url)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'lxml')
                    job_cards = soup.find_all('div', class_='company-card') or soup.find_all('a', class_='job')
                    
                    for card in job_cards[:20]:  # Limit per role
                        opp = self._parse_job_card(card, role)
                        if opp:
                            opportunities.append(opp)
                            
            except Exception as e:
                logger.error(f"YC: Error scraping {role}: {e}")
                
        return opportunities
    
    def _parse_job_card(self, card, role: str) -> Optional[Opportunity]:
        """Parse job card"""
        try:
            title_elem = card.find(['h2', 'h3', 'span']) or card
            title = title_elem.get_text(strip=True) if title_elem else "YC Startup Role"
            
            link = card.get('href', '') if card.name == 'a' else card.find('a', href=True)
            if isinstance(link, dict):
                link = link.get('href', '')
            elif hasattr(link, 'get'):
                link = link.get('href', '')
            
            if link and not link.startswith('http'):
                link = f"{self.workatastartup_url}{link}"
            
            return Opportunity(
                id=Opportunity.generate_id("yc", str(link) + title),
                title=title,
                company="YC Startup",
                location="Remote / San Francisco",
                description=f"Role at Y Combinator backed startup - {role}",
                apply_url=str(link) if link else self.workatastartup_url,
                source="YCombinator",
                source_id=str(link),
                opportunity_type="job",
                remote=True,
                tags=["yc", "startup", role, "silicon-valley"]
            )
        except Exception as e:
            logger.error(f"YC: Error parsing card: {e}")
            return None
    
    def _get_yc_programs(self) -> List[Opportunity]:
        """Get YC programs and funding opportunities"""
        programs = [
            {
                "title": "Y Combinator Core Batch (W2025/S2025)",
                "description": "YC invests $500k in startups. Get funding, mentorship, and access to the YC network.",
                "url": "https://www.ycombinator.com/apply/",
                "type": "accelerator",
                "funding": "$500,000"
            },
            {
                "title": "Y Combinator Startup School",
                "description": "Free 8-week program for aspiring founders. Learn how to build a startup.",
                "url": "https://www.startupschool.org/",
                "type": "program",
                "funding": "Free"
            },
            {
                "title": "YC Open Requests for Startups",
                "description": "Ideas YC wants to fund - AI, biotech, climate, etc.",
                "url": "https://www.ycombinator.com/rfs",
                "type": "funding",
                "funding": "$500,000"
            },
            {
                "title": "YC Co-founder Matching",
                "description": "Find a co-founder for your startup through YC's matching platform",
                "url": "https://www.ycombinator.com/cofounder-matching",
                "type": "program",
                "funding": "N/A"
            },
        ]
        
        return [
            Opportunity(
                id=Opportunity.generate_id("yc", prog["url"]),
                title=prog["title"],
                company="Y Combinator",
                location="San Francisco / Remote",
                description=prog["description"],
                apply_url=prog["url"],
                source="YCombinator",
                source_id=prog["url"],
                opportunity_type=prog["type"],
                remote=True,
                tags=["yc", "startup", "funding", "silicon-valley"],
                metadata={"funding": prog.get("funding")}
            )
            for prog in programs
        ]
    
    async def search(self, query: str, **kwargs) -> List[Opportunity]:
        return await self.scrape(max_pages=10)


class TechstarsScraper(BaseScraper):
    """Scraper for Techstars accelerator programs"""
    
    def __init__(self):
        super().__init__(
            name="Techstars",
            base_url="https://www.techstars.com",
            rate_limit=0.5,
            timeout=45.0
        )
    
    async def scrape(self, max_pages: int = 10) -> List[Opportunity]:
        """Scrape Techstars programs"""
        opportunities = []
        
        async with httpx.AsyncClient(timeout=self.timeout, headers=self.default_headers) as client:
            try:
                await self._wait_for_rate_limit()
                url = f"{self.base_url}/accelerators/"
                response = await client.get(url)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'lxml')
                    programs = soup.find_all('div', class_='accelerator') or soup.find_all('article')
                    
                    for prog in programs:
                        opp = self._parse_program(prog)
                        if opp:
                            opportunities.append(opp)
            except Exception as e:
                logger.error(f"Techstars: Error: {e}")
        
        # Add known Techstars programs
        opportunities.extend(self._get_known_programs())
        
        return opportunities
    
    def _parse_program(self, prog) -> Optional[Opportunity]:
        """Parse program"""
        try:
            title_elem = prog.find(['h2', 'h3', 'a'])
            if not title_elem:
                return None
            
            title = title_elem.get_text(strip=True)
            link = prog.find('a', href=True)
            url = link['href'] if link else self.base_url
            
            if not url.startswith('http'):
                url = f"{self.base_url}{url}"
            
            return Opportunity(
                id=Opportunity.generate_id("techstars", url),
                title=f"Techstars {title}",
                company="Techstars",
                location="Various",
                description=prog.get_text()[:500],
                apply_url=url,
                source="Techstars",
                source_id=url,
                opportunity_type="accelerator",
                remote=True,
                tags=["techstars", "accelerator", "startup", "funding"]
            )
        except Exception as e:
            return None
    
    def _get_known_programs(self) -> List[Opportunity]:
        """Known Techstars programs"""
        programs = [
            ("Techstars NYC", "New York"),
            ("Techstars LA", "Los Angeles"),
            ("Techstars Boston", "Boston"),
            ("Techstars Seattle", "Seattle"),
            ("Techstars Austin", "Austin"),
            ("Techstars Toronto", "Toronto"),
            ("Techstars London", "London"),
            ("Techstars Berlin", "Berlin"),
            ("Techstars AI", "Remote"),
            ("Techstars Climate", "Remote"),
            ("Techstars Fintech", "New York"),
            ("Techstars Healthcare", "Boston"),
        ]
        
        return [
            Opportunity(
                id=Opportunity.generate_id("techstars", name),
                title=name,
                company="Techstars",
                location=location,
                description=f"{name} accelerator program - $120k investment, 3-month program",
                apply_url="https://www.techstars.com/accelerators",
                source="Techstars",
                source_id=name,
                opportunity_type="accelerator",
                remote=True,
                tags=["techstars", "accelerator", "startup"],
                metadata={"funding": "$120,000"}
            )
            for name, location in programs
        ]
    
    async def search(self, query: str, **kwargs) -> List[Opportunity]:
        return await self.scrape()


class VCFundsScraper(BaseScraper):
    """Scraper for major VC firm opportunities and programs"""
    
    def __init__(self):
        super().__init__(
            name="VCFunds",
            base_url="https://www.vcfunds.com",
            rate_limit=0.5,
            timeout=45.0
        )
    
    async def scrape(self, max_pages: int = 10) -> List[Opportunity]:
        """Get VC programs and funding opportunities"""
        opportunities = []
        
        # Major VC programs and opportunities
        vc_programs = [
            # a16z
            {
                "title": "a16z Crypto Startup School",
                "company": "Andreessen Horowitz",
                "url": "https://a16z.com/crypto-startup-school/",
                "description": "Free 12-week program for crypto founders",
                "type": "program",
                "tags": ["a16z", "crypto", "web3"]
            },
            {
                "title": "a16z Cultural Leadership Fund",
                "company": "Andreessen Horowitz",
                "url": "https://a16z.com/cultural-leadership-fund/",
                "description": "Investment fund supporting underrepresented founders",
                "type": "funding",
                "tags": ["a16z", "diversity"]
            },
            # Sequoia
            {
                "title": "Sequoia Arc",
                "company": "Sequoia Capital",
                "url": "https://www.sequoiacap.com/arc/",
                "description": "Program for founders at the earliest stages",
                "type": "accelerator",
                "tags": ["sequoia", "early-stage"]
            },
            {
                "title": "Sequoia Scout Program",
                "company": "Sequoia Capital",
                "url": "https://www.sequoiacap.com/",
                "description": "Scout program for identifying exceptional founders",
                "type": "program",
                "tags": ["sequoia", "scout"]
            },
            # First Round
            {
                "title": "First Round Capital - Fast Track Application",
                "company": "First Round Capital",
                "url": "https://firstround.com/",
                "description": "Early-stage funding for pre-seed and seed startups",
                "type": "funding",
                "tags": ["firstround", "seed"]
            },
            # Founders Fund
            {
                "title": "Founders Fund - Pitch",
                "company": "Founders Fund",
                "url": "https://foundersfund.com/",
                "description": "Funding for bold ideas and contrarian startups",
                "type": "funding",
                "tags": ["foundersfund", "contrarian"]
            },
            # Greylock
            {
                "title": "Greylock Partners",
                "company": "Greylock Partners",
                "url": "https://greylock.com/",
                "description": "Early-stage enterprise and consumer investments",
                "type": "funding",
                "tags": ["greylock", "enterprise"]
            },
            # Benchmark
            {
                "title": "Benchmark Capital",
                "company": "Benchmark",
                "url": "https://www.benchmark.com/",
                "description": "Early-stage venture capital",
                "type": "funding",
                "tags": ["benchmark", "early-stage"]
            },
            # Accel
            {
                "title": "Accel Partners",
                "company": "Accel",
                "url": "https://www.accel.com/",
                "description": "Global venture capital at every stage",
                "type": "funding",
                "tags": ["accel", "global"]
            },
            # Kleiner Perkins
            {
                "title": "Kleiner Perkins Fellows",
                "company": "Kleiner Perkins",
                "url": "https://fellows.kleinerperkins.com/",
                "description": "Fellowship program for students and recent grads",
                "type": "fellowship",
                "tags": ["kp", "fellowship", "student"]
            },
            # General Catalyst
            {
                "title": "General Catalyst",
                "company": "General Catalyst",
                "url": "https://www.generalcatalyst.com/",
                "description": "Venture capital for transformative companies",
                "type": "funding",
                "tags": ["gc", "transformative"]
            },
            # Index Ventures
            {
                "title": "Index Ventures",
                "company": "Index Ventures",
                "url": "https://www.indexventures.com/",
                "description": "European and US venture capital",
                "type": "funding",
                "tags": ["index", "europe", "us"]
            },
            # Lightspeed
            {
                "title": "Lightspeed Venture Partners",
                "company": "Lightspeed",
                "url": "https://lsvp.com/",
                "description": "Multi-stage venture capital",
                "type": "funding",
                "tags": ["lightspeed", "multi-stage"]
            },
            # NEA
            {
                "title": "New Enterprise Associates",
                "company": "NEA",
                "url": "https://www.nea.com/",
                "description": "One of the largest VC funds globally",
                "type": "funding",
                "tags": ["nea", "large-fund"]
            },
            # Bessemer
            {
                "title": "Bessemer Venture Partners",
                "company": "Bessemer",
                "url": "https://www.bvp.com/",
                "description": "Pioneer in venture capital since 1911",
                "type": "funding",
                "tags": ["bessemer", "pioneer"]
            },
            # Tiger Global
            {
                "title": "Tiger Global Management",
                "company": "Tiger Global",
                "url": "https://www.tigerglobal.com/",
                "description": "Growth-stage technology investments",
                "type": "funding",
                "tags": ["tiger", "growth"]
            },
            # SoftBank
            {
                "title": "SoftBank Vision Fund",
                "company": "SoftBank",
                "url": "https://visionfund.com/",
                "description": "Large-scale technology investments",
                "type": "funding",
                "tags": ["softbank", "vision-fund"]
            },
            # Insight Partners
            {
                "title": "Insight Partners",
                "company": "Insight Partners",
                "url": "https://www.insightpartners.com/",
                "description": "Software and tech growth investments",
                "type": "funding",
                "tags": ["insight", "software"]
            },
            # 500 Global
            {
                "title": "500 Global Accelerator",
                "company": "500 Global",
                "url": "https://500.co/accelerators",
                "description": "Global accelerator program with $150k investment",
                "type": "accelerator",
                "tags": ["500", "global", "accelerator"]
            },
            # Plug and Play
            {
                "title": "Plug and Play Tech Center",
                "company": "Plug and Play",
                "url": "https://www.plugandplaytechcenter.com/",
                "description": "Innovation platform and accelerator",
                "type": "accelerator",
                "tags": ["plugandplay", "innovation"]
            },
        ]
        
        for prog in vc_programs:
            opportunities.append(Opportunity(
                id=Opportunity.generate_id("vc", prog["url"]),
                title=prog["title"],
                company=prog["company"],
                location="Global",
                description=prog["description"],
                apply_url=prog["url"],
                source="VCFunds",
                source_id=prog["url"],
                opportunity_type=prog["type"],
                remote=True,
                tags=prog["tags"] + ["venture-capital", "funding"]
            ))
        
        return opportunities
    
    async def search(self, query: str, **kwargs) -> List[Opportunity]:
        return await self.scrape()


class AngelListScraper(BaseScraper):
    """Scraper for AngelList/Wellfound jobs and investments"""
    
    def __init__(self):
        super().__init__(
            name="AngelList",
            base_url="https://angel.co",
            rate_limit=0.5,
            timeout=45.0
        )
    
    async def scrape(self, max_pages: int = 20) -> List[Opportunity]:
        """Scrape AngelList jobs and syndicates"""
        opportunities = []
        
        # AngelList investing opportunities
        invest_opps = [
            {
                "title": "AngelList Rolling Funds",
                "url": "https://angel.co/rolling-funds",
                "description": "Access to top angel investor portfolios through rolling funds",
                "type": "investment"
            },
            {
                "title": "AngelList Syndicates",
                "url": "https://angel.co/syndicates",
                "description": "Co-invest alongside experienced angels in startups",
                "type": "investment"
            },
            {
                "title": "AngelList Venture - Start a Fund",
                "url": "https://www.angellist.com/venture",
                "description": "Launch and manage your own venture fund",
                "type": "program"
            },
        ]
        
        for opp in invest_opps:
            opportunities.append(Opportunity(
                id=Opportunity.generate_id("angellist", opp["url"]),
                title=opp["title"],
                company="AngelList",
                location="Global",
                description=opp["description"],
                apply_url=opp["url"],
                source="AngelList",
                source_id=opp["url"],
                opportunity_type=opp["type"],
                remote=True,
                tags=["angellist", "startup", "investing"]
            ))
        
        return opportunities
    
    async def search(self, query: str, **kwargs) -> List[Opportunity]:
        return await self.scrape()


# Convenience functions
async def scrape_yc(max_pages: int = 50) -> List[Dict]:
    """Scrape Y Combinator"""
    scraper = YCombinatorScraper()
    opportunities = await scraper.scrape(max_pages)
    return [opp.to_dict() for opp in opportunities]


async def scrape_techstars() -> List[Dict]:
    """Scrape Techstars"""
    scraper = TechstarsScraper()
    opportunities = await scraper.scrape()
    return [opp.to_dict() for opp in opportunities]


async def scrape_vc_funds() -> List[Dict]:
    """Scrape VC fund opportunities"""
    scraper = VCFundsScraper()
    opportunities = await scraper.scrape()
    return [opp.to_dict() for opp in opportunities]


async def scrape_angellist() -> List[Dict]:
    """Scrape AngelList"""
    scraper = AngelListScraper()
    opportunities = await scraper.scrape()
    return [opp.to_dict() for opp in opportunities]


async def scrape_all_vc_opportunities() -> List[Dict]:
    """Scrape all VC and startup opportunities"""
    all_opportunities = []
    
    scrapers = [
        scrape_yc(50),
        scrape_techstars(),
        scrape_vc_funds(),
        scrape_angellist(),
    ]
    
    results = await asyncio.gather(*scrapers, return_exceptions=True)
    
    for result in results:
        if isinstance(result, list):
            all_opportunities.extend(result)
        elif isinstance(result, Exception):
            logger.error(f"VC scraper error: {result}")
    
    return all_opportunities
