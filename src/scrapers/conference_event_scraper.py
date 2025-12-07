"""
Conference & Event Scrapers
============================
Scrapes conferences, summits, workshops, and networking events
from tech, business, and academic platforms.
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


class ConferenceScraper(BaseScraper):
    """Scraper for major tech and business conferences"""
    
    def __init__(self):
        super().__init__(
            name="Conferences",
            base_url="https://confs.tech",
            rate_limit=0.5,
            timeout=45.0
        )
    
    async def scrape(self, max_pages: int = 20) -> List[Opportunity]:
        """Scrape tech conferences"""
        opportunities = []
        
        # Major tech conferences (well-known, recurring)
        conferences = [
            # AI/ML Conferences
            {
                "title": "NeurIPS - Conference on Neural Information Processing Systems",
                "company": "NeurIPS Foundation",
                "url": "https://neurips.cc/",
                "description": "Premier AI/ML research conference. Call for papers and workshops.",
                "location": "Various",
                "tags": ["ai", "ml", "research", "academic"]
            },
            {
                "title": "ICML - International Conference on Machine Learning",
                "company": "ICML",
                "url": "https://icml.cc/",
                "description": "Leading machine learning research conference.",
                "location": "Various",
                "tags": ["ml", "research", "academic"]
            },
            {
                "title": "CVPR - Computer Vision and Pattern Recognition",
                "company": "IEEE",
                "url": "https://cvpr.thecvf.com/",
                "description": "Top computer vision conference.",
                "location": "Various",
                "tags": ["cv", "ai", "research"]
            },
            {
                "title": "ACL - Association for Computational Linguistics",
                "company": "ACL",
                "url": "https://www.aclweb.org/",
                "description": "Premier NLP research conference.",
                "location": "Various",
                "tags": ["nlp", "ai", "research"]
            },
            # Tech Industry Conferences
            {
                "title": "Google I/O",
                "company": "Google",
                "url": "https://io.google/",
                "description": "Google's annual developer conference. Free online.",
                "location": "Mountain View / Online",
                "tags": ["google", "developer", "tech"]
            },
            {
                "title": "Apple WWDC",
                "company": "Apple",
                "url": "https://developer.apple.com/wwdc/",
                "description": "Apple's Worldwide Developers Conference.",
                "location": "Cupertino / Online",
                "tags": ["apple", "developer", "ios", "macos"]
            },
            {
                "title": "Microsoft Build",
                "company": "Microsoft",
                "url": "https://build.microsoft.com/",
                "description": "Microsoft's annual developer conference.",
                "location": "Seattle / Online",
                "tags": ["microsoft", "developer", "azure"]
            },
            {
                "title": "AWS re:Invent",
                "company": "Amazon Web Services",
                "url": "https://reinvent.awsevents.com/",
                "description": "AWS's premier cloud computing event.",
                "location": "Las Vegas",
                "tags": ["aws", "cloud", "devops"]
            },
            {
                "title": "Meta Connect",
                "company": "Meta",
                "url": "https://www.metaconnect.com/",
                "description": "Meta's annual VR/AR and metaverse conference.",
                "location": "Online",
                "tags": ["meta", "vr", "ar", "metaverse"]
            },
            {
                "title": "GitHub Universe",
                "company": "GitHub",
                "url": "https://githubuniverse.com/",
                "description": "GitHub's annual developer conference.",
                "location": "San Francisco / Online",
                "tags": ["github", "developer", "opensource"]
            },
            # Startup & Business Conferences
            {
                "title": "TechCrunch Disrupt",
                "company": "TechCrunch",
                "url": "https://techcrunch.com/events/",
                "description": "Premier startup conference with Startup Battlefield competition.",
                "location": "San Francisco",
                "tags": ["startup", "pitch", "techcrunch"]
            },
            {
                "title": "Web Summit",
                "company": "Web Summit",
                "url": "https://websummit.com/",
                "description": "One of the world's largest tech conferences.",
                "location": "Lisbon",
                "tags": ["startup", "tech", "networking"]
            },
            {
                "title": "Collision Conference",
                "company": "Web Summit",
                "url": "https://collisionconf.com/",
                "description": "North America's fastest-growing tech conference.",
                "location": "Toronto",
                "tags": ["startup", "tech", "canada"]
            },
            {
                "title": "SXSW - South by Southwest",
                "company": "SXSW",
                "url": "https://www.sxsw.com/",
                "description": "Convergence of tech, film, and music industries.",
                "location": "Austin",
                "tags": ["tech", "creative", "startup"]
            },
            {
                "title": "CES - Consumer Electronics Show",
                "company": "CTA",
                "url": "https://www.ces.tech/",
                "description": "World's largest consumer technology trade show.",
                "location": "Las Vegas",
                "tags": ["hardware", "consumer", "tech"]
            },
            {
                "title": "Money20/20",
                "company": "Money20/20",
                "url": "https://www.money2020.com/",
                "description": "Premier fintech and payments conference.",
                "location": "Las Vegas / Amsterdam",
                "tags": ["fintech", "payments", "banking"]
            },
            # Developer Conferences
            {
                "title": "PyCon US",
                "company": "Python Software Foundation",
                "url": "https://pycon.org/",
                "description": "The largest annual gathering for the Python community.",
                "location": "Various US",
                "tags": ["python", "developer", "opensource"]
            },
            {
                "title": "JSConf",
                "company": "JSConf",
                "url": "https://jsconf.com/",
                "description": "JavaScript developer conferences worldwide.",
                "location": "Global",
                "tags": ["javascript", "developer", "web"]
            },
            {
                "title": "GopherCon",
                "company": "GopherCon",
                "url": "https://www.gophercon.com/",
                "description": "The largest Go conference.",
                "location": "Various",
                "tags": ["golang", "developer"]
            },
            {
                "title": "RustConf",
                "company": "Rust Foundation",
                "url": "https://rustconf.com/",
                "description": "Annual Rust programming language conference.",
                "location": "Various",
                "tags": ["rust", "developer", "systems"]
            },
            {
                "title": "KubeCon + CloudNativeCon",
                "company": "CNCF",
                "url": "https://events.linuxfoundation.org/kubecon-cloudnativecon/",
                "description": "Cloud native and Kubernetes conference.",
                "location": "Global",
                "tags": ["kubernetes", "cloud", "devops"]
            },
            # Design Conferences
            {
                "title": "Figma Config",
                "company": "Figma",
                "url": "https://config.figma.com/",
                "description": "Figma's annual design conference.",
                "location": "San Francisco / Online",
                "tags": ["design", "figma", "ux"]
            },
            {
                "title": "Adobe MAX",
                "company": "Adobe",
                "url": "https://max.adobe.com/",
                "description": "Adobe's creativity conference.",
                "location": "Los Angeles / Online",
                "tags": ["design", "creative", "adobe"]
            },
            # Data & Analytics
            {
                "title": "Strata Data Conference",
                "company": "O'Reilly",
                "url": "https://www.oreilly.com/conferences/",
                "description": "Data science and analytics conference.",
                "location": "Various",
                "tags": ["data", "analytics", "bigdata"]
            },
            {
                "title": "Spark + AI Summit",
                "company": "Databricks",
                "url": "https://www.databricks.com/dataaisummit/",
                "description": "Premier data and AI conference.",
                "location": "San Francisco",
                "tags": ["data", "ai", "spark"]
            },
            # Security
            {
                "title": "DEF CON",
                "company": "DEF CON",
                "url": "https://defcon.org/",
                "description": "World's largest hacker convention.",
                "location": "Las Vegas",
                "tags": ["security", "hacking", "infosec"]
            },
            {
                "title": "Black Hat",
                "company": "Black Hat",
                "url": "https://www.blackhat.com/",
                "description": "Information security conferences and training.",
                "location": "Las Vegas / Global",
                "tags": ["security", "infosec", "training"]
            },
            {
                "title": "RSA Conference",
                "company": "RSA",
                "url": "https://www.rsaconference.com/",
                "description": "Cybersecurity conference and expo.",
                "location": "San Francisco",
                "tags": ["security", "cybersecurity", "enterprise"]
            },
            # African Tech Conferences
            {
                "title": "AfricArena Summit",
                "company": "AfricArena",
                "url": "https://www.africarena.com/",
                "description": "Premier African tech and VC summit.",
                "location": "Cape Town / Virtual",
                "tags": ["africa", "startup", "venture"]
            },
            {
                "title": "Africa Tech Summit",
                "company": "Africa Tech Summit",
                "url": "https://www.africatechsummit.com/",
                "description": "Leading African tech conference.",
                "location": "Nairobi / London",
                "tags": ["africa", "tech", "startup"]
            },
            {
                "title": "Lagos Startup Week",
                "company": "Lagos Startup Week",
                "url": "https://lagosstartupweek.com/",
                "description": "Nigeria's largest startup event.",
                "location": "Lagos",
                "tags": ["africa", "nigeria", "startup"]
            },
            # Entrepreneur Conferences
            {
                "title": "Startup Grind Global Conference",
                "company": "Startup Grind",
                "url": "https://www.startupgrind.com/conference/",
                "description": "Global startup community conference.",
                "location": "Silicon Valley",
                "tags": ["startup", "networking", "entrepreneur"]
            },
            {
                "title": "Slush",
                "company": "Slush",
                "url": "https://www.slush.org/",
                "description": "World's leading startup event.",
                "location": "Helsinki",
                "tags": ["startup", "europe", "nordic"]
            },
            {
                "title": "4YFN - 4 Years From Now",
                "company": "Mobile World Congress",
                "url": "https://www.4yfn.com/",
                "description": "Startup event alongside MWC.",
                "location": "Barcelona",
                "tags": ["startup", "mobile", "europe"]
            },
        ]
        
        for conf in conferences:
            opportunities.append(Opportunity(
                id=Opportunity.generate_id("conference", conf["url"]),
                title=conf["title"],
                company=conf["company"],
                location=conf["location"],
                description=conf["description"],
                apply_url=conf["url"],
                source="Conferences",
                source_id=conf["url"],
                opportunity_type="conference",
                remote="Online" in conf["location"] or "Virtual" in conf["location"],
                tags=conf["tags"] + ["conference", "event", "networking"]
            ))
        
        # Scrape confs.tech for more
        async with httpx.AsyncClient(timeout=self.timeout, headers=self.default_headers) as client:
            tech_categories = ["javascript", "python", "data", "devops", "ux", "ruby", "ios", "android", "security"]
            
            for category in tech_categories:
                try:
                    await self._wait_for_rate_limit()
                    url = f"{self.base_url}/{category}"
                    response = await client.get(url)
                    
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.text, 'lxml')
                        conf_items = soup.find_all(['div', 'article'], class_=re.compile('conf|event'))
                        
                        for item in conf_items[:15]:
                            opp = self._parse_conference(item, category)
                            if opp:
                                opportunities.append(opp)
                except Exception as e:
                    logger.error(f"Confs.tech: Error scraping {category}: {e}")
        
        return opportunities
    
    def _parse_conference(self, item, category: str) -> Optional[Opportunity]:
        """Parse conference item"""
        try:
            title_elem = item.find(['h2', 'h3', 'a', 'span'])
            if not title_elem:
                return None
            
            title = title_elem.get_text(strip=True)
            link = item.find('a', href=True)
            url = link['href'] if link else ""
            
            if url and not url.startswith('http'):
                url = f"{self.base_url}{url}"
            
            return Opportunity(
                id=Opportunity.generate_id("confstech", url + title),
                title=title,
                company="Various",
                location="Various",
                description=item.get_text()[:500],
                apply_url=url or self.base_url,
                source="Confs.tech",
                source_id=url,
                opportunity_type="conference",
                remote=True,
                tags=[category, "conference", "tech", "developer"]
            )
        except:
            return None
    
    async def search(self, query: str, **kwargs) -> List[Opportunity]:
        return await self.scrape()


class MeetupScraper(BaseScraper):
    """Scraper for Meetup events and groups"""
    
    def __init__(self):
        super().__init__(
            name="Meetup",
            base_url="https://www.meetup.com",
            rate_limit=0.5,
            timeout=45.0
        )
    
    async def scrape(self, max_pages: int = 20) -> List[Opportunity]:
        """Scrape Meetup events"""
        opportunities = []
        
        categories = [
            "tech-talks", "startup-businesses", "software-development",
            "artificial-intelligence", "data-science", "cloud-computing",
            "blockchain", "fintech", "entrepreneurship", "venture-capital"
        ]
        
        async with httpx.AsyncClient(timeout=self.timeout, headers=self.default_headers) as client:
            for category in categories:
                try:
                    await self._wait_for_rate_limit()
                    url = f"{self.base_url}/find/?keywords={category}&source=EVENTS"
                    response = await client.get(url)
                    
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.text, 'lxml')
                        events = soup.find_all(['div', 'article'], class_=re.compile('event|card'))
                        
                        for event in events[:20]:
                            opp = self._parse_event(event, category)
                            if opp:
                                opportunities.append(opp)
                except Exception as e:
                    logger.error(f"Meetup: Error scraping {category}: {e}")
        
        return opportunities
    
    def _parse_event(self, event, category: str) -> Optional[Opportunity]:
        """Parse Meetup event"""
        try:
            title_elem = event.find(['h2', 'h3', 'a', 'span'])
            if not title_elem:
                return None
            
            title = title_elem.get_text(strip=True)
            link = event.find('a', href=True)
            url = link['href'] if link else ""
            
            if url and not url.startswith('http'):
                url = f"{self.base_url}{url}"
            
            return Opportunity(
                id=Opportunity.generate_id("meetup", url + title),
                title=title,
                company="Meetup Group",
                location="Various",
                description=event.get_text()[:500],
                apply_url=url or self.base_url,
                source="Meetup",
                source_id=url,
                opportunity_type="event",
                remote=True,
                tags=[category, "meetup", "networking", "community"]
            )
        except:
            return None
    
    async def search(self, query: str, **kwargs) -> List[Opportunity]:
        return await self.scrape()


class EventbriteScraper(BaseScraper):
    """Scraper for Eventbrite business and tech events"""
    
    def __init__(self):
        super().__init__(
            name="Eventbrite",
            base_url="https://www.eventbrite.com",
            rate_limit=0.5,
            timeout=45.0
        )
    
    async def scrape(self, max_pages: int = 20) -> List[Opportunity]:
        """Scrape Eventbrite events"""
        opportunities = []
        
        search_terms = [
            "startup+pitch", "tech+conference", "AI+summit",
            "entrepreneurship+workshop", "venture+capital", "hackathon",
            "data+science", "machine+learning", "blockchain+summit",
            "fintech+conference", "developer+conference"
        ]
        
        async with httpx.AsyncClient(timeout=self.timeout, headers=self.default_headers) as client:
            for term in search_terms:
                try:
                    await self._wait_for_rate_limit()
                    url = f"{self.base_url}/d/online/{term}/"
                    response = await client.get(url)
                    
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.text, 'lxml')
                        events = soup.find_all(['div', 'article'], class_=re.compile('event|card'))
                        
                        for event in events[:15]:
                            opp = self._parse_event(event, term)
                            if opp:
                                opportunities.append(opp)
                except Exception as e:
                    logger.error(f"Eventbrite: Error scraping {term}: {e}")
        
        return opportunities
    
    def _parse_event(self, event, search_term: str) -> Optional[Opportunity]:
        """Parse Eventbrite event"""
        try:
            title_elem = event.find(['h2', 'h3', 'a'])
            if not title_elem:
                return None
            
            title = title_elem.get_text(strip=True)
            link = event.find('a', href=True)
            url = link['href'] if link else ""
            
            if url and not url.startswith('http'):
                url = f"{self.base_url}{url}"
            
            return Opportunity(
                id=Opportunity.generate_id("eventbrite", url + title),
                title=title,
                company="Event Organizer",
                location="Online / Various",
                description=event.get_text()[:500],
                apply_url=url or self.base_url,
                source="Eventbrite",
                source_id=url,
                opportunity_type="event",
                remote=True,
                tags=[search_term.replace("+", "-"), "event", "workshop"]
            )
        except:
            return None
    
    async def search(self, query: str, **kwargs) -> List[Opportunity]:
        return await self.scrape()


class HackathonScraper(BaseScraper):
    """Scraper for hackathons and coding competitions"""
    
    def __init__(self):
        super().__init__(
            name="Hackathons",
            base_url="https://devpost.com",
            rate_limit=0.5,
            timeout=45.0
        )
    
    async def scrape(self, max_pages: int = 10) -> List[Opportunity]:
        """Scrape hackathons"""
        opportunities = []
        
        async with httpx.AsyncClient(timeout=self.timeout, headers=self.default_headers) as client:
            try:
                # Devpost hackathons
                await self._wait_for_rate_limit()
                url = f"{self.base_url}/hackathons?status[]=upcoming&status[]=open"
                response = await client.get(url)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'lxml')
                    hackathons = soup.find_all(['div', 'article'], class_=re.compile('hackathon|challenge'))
                    
                    for hack in hackathons[:50]:
                        opp = self._parse_hackathon(hack)
                        if opp:
                            opportunities.append(opp)
            except Exception as e:
                logger.error(f"Devpost: Error: {e}")
        
        # Add well-known recurring hackathons
        known_hackathons = [
            {
                "title": "MLH (Major League Hacking) Hackathons",
                "url": "https://mlh.io/seasons/2025/events",
                "description": "Student hackathons organized by Major League Hacking worldwide.",
                "prize": "Various"
            },
            {
                "title": "Google Solution Challenge",
                "url": "https://developers.google.com/community/gdsc-solution-challenge",
                "description": "Build solutions for UN's SDGs using Google technologies.",
                "prize": "$10,000+"
            },
            {
                "title": "HackMIT",
                "url": "https://hackmit.org/",
                "description": "MIT's premier hackathon.",
                "prize": "Various"
            },
            {
                "title": "PennApps",
                "url": "https://pennapps.com/",
                "description": "UPenn's flagship hackathon.",
                "prize": "Various"
            },
            {
                "title": "TreeHacks (Stanford)",
                "url": "https://www.treehacks.com/",
                "description": "Stanford's flagship hackathon.",
                "prize": "Various"
            },
            {
                "title": "ETHGlobal Hackathons",
                "url": "https://ethglobal.com/",
                "description": "Ethereum and Web3 hackathons worldwide.",
                "prize": "$100,000+"
            },
            {
                "title": "NASA Space Apps Challenge",
                "url": "https://www.spaceappschallenge.org/",
                "description": "World's largest annual hackathon using NASA data.",
                "prize": "Various"
            },
        ]
        
        for hack in known_hackathons:
            opportunities.append(Opportunity(
                id=Opportunity.generate_id("hackathon", hack["url"]),
                title=hack["title"],
                company="Hackathon Organizer",
                location="Global / Online",
                description=hack["description"],
                apply_url=hack["url"],
                source="Hackathons",
                source_id=hack["url"],
                opportunity_type="hackathon",
                remote=True,
                tags=["hackathon", "competition", "coding", "prize"],
                metadata={"prize": hack.get("prize")}
            ))
        
        return opportunities
    
    def _parse_hackathon(self, hack) -> Optional[Opportunity]:
        """Parse hackathon"""
        try:
            title_elem = hack.find(['h2', 'h3', 'a'])
            if not title_elem:
                return None
            
            title = title_elem.get_text(strip=True)
            link = hack.find('a', href=True)
            url = link['href'] if link else ""
            
            if url and not url.startswith('http'):
                url = f"{self.base_url}{url}"
            
            # Extract prize if present
            prize_match = re.search(r'\$[\d,]+', hack.get_text())
            prize = prize_match.group(0) if prize_match else None
            
            return Opportunity(
                id=Opportunity.generate_id("devpost", url + title),
                title=title,
                company="Hackathon",
                location="Online / Various",
                description=hack.get_text()[:500],
                apply_url=url or self.base_url,
                source="Devpost",
                source_id=url,
                opportunity_type="hackathon",
                remote=True,
                tags=["hackathon", "competition", "coding"],
                metadata={"prize": prize} if prize else {}
            )
        except:
            return None
    
    async def search(self, query: str, **kwargs) -> List[Opportunity]:
        return await self.scrape()


# Convenience functions
async def scrape_conferences() -> List[Dict]:
    """Scrape tech conferences"""
    scraper = ConferenceScraper()
    opportunities = await scraper.scrape()
    return [opp.to_dict() for opp in opportunities]


async def scrape_meetups() -> List[Dict]:
    """Scrape Meetup events"""
    scraper = MeetupScraper()
    opportunities = await scraper.scrape()
    return [opp.to_dict() for opp in opportunities]


async def scrape_eventbrite() -> List[Dict]:
    """Scrape Eventbrite events"""
    scraper = EventbriteScraper()
    opportunities = await scraper.scrape()
    return [opp.to_dict() for opp in opportunities]


async def scrape_hackathons() -> List[Dict]:
    """Scrape hackathons"""
    scraper = HackathonScraper()
    opportunities = await scraper.scrape()
    return [opp.to_dict() for opp in opportunities]


async def scrape_all_events_and_conferences() -> List[Dict]:
    """Scrape all event and conference sources"""
    all_opportunities = []
    
    scrapers = [
        scrape_conferences(),
        scrape_meetups(),
        scrape_eventbrite(),
        scrape_hackathons(),
    ]
    
    results = await asyncio.gather(*scrapers, return_exceptions=True)
    
    for result in results:
        if isinstance(result, list):
            all_opportunities.extend(result)
        elif isinstance(result, Exception):
            logger.error(f"Event scraper error: {result}")
    
    return all_opportunities
