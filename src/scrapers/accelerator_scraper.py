"""
Accelerator & Startup Program Scraper
=====================================
Comprehensive scraper for 120+ accelerators, incubators, and startup programs
"""

import asyncio
import aiohttp
from bs4 import BeautifulSoup
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import re
import json

from .base_scraper import BaseScraper
from .utils import clean_text, extract_dates, normalize_url
from ..models.opportunity import Opportunity, OpportunityRequirements
from ..models.enums import OpportunityType, SourceType


class AcceleratorScraper(BaseScraper):
    """Scraper for accelerators, incubators, and startup programs"""
    
    def __init__(self):
        super().__init__("AcceleratorScraper", "")
        self.opportunities = []
        self.logger = logging.getLogger(__name__)
        
        # Common selectors for different types of accelerator sites
        self.selectors = {
            "program_cards": [
                ".program-card", ".accelerator-card", ".cohort-card",
                ".opportunity-card", ".application-card", "[data-program]",
                ".grid-item", ".program-item", ".cohort-item"
            ],
            "titles": [
                "h1", "h2", "h3", ".title", ".program-title", 
                ".accelerator-name", ".cohort-name", "[data-title]"
            ],
            "descriptions": [
                ".description", ".program-description", ".cohort-description",
                ".overview", ".summary", "p", ".content", "[data-description]"
            ],
            "dates": [
                ".date", ".deadline", ".application-date", ".cohort-date",
                ".program-date", "[data-date]", ".timeline", ".schedule"
            ],
            "links": [
                "a[href*='apply']", "a[href*='application']", "a[href*='program']",
                ".apply-link", ".application-link", ".program-link"
            ],
            "funding": [
                ".funding", ".investment", ".equity", ".amount",
                "[data-funding]", ".financial-terms"
            ],
            "location": [
                ".location", ".city", ".country", "[data-location]",
                ".program-location", ".accelerator-location"
            ],
            "duration": [
                ".duration", ".program-length", ".cohort-duration",
                "[data-duration]", ".timeline"
            ]
        }
    
    async def search(
        self,
        query: str,
        location: Optional[str] = None,
        page: int = 1,
        **filters
    ) -> List[Opportunity]:
        """Search accelerator opportunities (required by BaseScraper)"""
        # For accelerator scraper, we don't really use search - we scrape all
        return await self.scrape_all_accelerators(limit=50)
    
    async def get_details(self, opportunity_id: str) -> Optional[Opportunity]:
        """Get details for a specific opportunity (required by BaseScraper)"""
        # For now, return None as we don't have individual opportunity detail pages
        return None
    
    async def fetch_html(self, url: str) -> Optional[str]:
        """Fetch HTML content from URL using base scraper's HTTP methods"""
        try:
            response = await self.get(url)
            if response and response.status_code == 200:
                return response.text
        except Exception as e:
            self.logger.error(f"Error fetching HTML from {url}: {e}")
        return None
    
    async def scrape_single_accelerator(self, accelerator_config: Dict[str, Any]) -> List[Opportunity]:
        """Scrape a single accelerator/startup program"""
        opportunities = []
        
        try:
            url = accelerator_config.get('url', '')
            if not url:
                return opportunities
            
            self.logger.info(f"Scraping {accelerator_config.get('name', url)}")
            
            # Handle different accelerator types with specialized parsing
            accelerator_type = accelerator_config.get('type', 'accelerator')
            tier = accelerator_config.get('tier', 'unknown')
            
            if accelerator_type == 'startup_program':
                opportunities.extend(await self._scrape_startup_program(accelerator_config))
            elif accelerator_type == 'corporate_accelerator':
                opportunities.extend(await self._scrape_corporate_accelerator(accelerator_config))
            elif accelerator_type == 'university_accelerator':
                opportunities.extend(await self._scrape_university_accelerator(accelerator_config))
            elif accelerator_type in ['accelerator', 'incubator']:
                opportunities.extend(await self._scrape_traditional_accelerator(accelerator_config))
            elif accelerator_type == 'vc_program':
                opportunities.extend(await self._scrape_vc_program(accelerator_config))
            elif accelerator_type in ['competition', 'prize_competition', 'innovation_challenge']:
                opportunities.extend(await self._scrape_competition(accelerator_config))
            else:
                # Generic fallback scraping
                opportunities.extend(await self._scrape_generic_accelerator(accelerator_config))
            
            self.logger.info(f"Found {len(opportunities)} opportunities from {accelerator_config.get('name', url)}")
            
        except Exception as e:
            self.logger.error(f"Error scraping {accelerator_config.get('name', url)}: {e}")
        
        return opportunities
    
    async def _scrape_startup_program(self, config: Dict[str, Any]) -> List[Opportunity]:
        """Scrape startup programs (usually ongoing/rolling applications)"""
        opportunities = []
        
        try:
            html = await self.fetch_html(config['url'])
            if not html:
                return opportunities
            
            soup = BeautifulSoup(html, 'html.parser')
            
            # For startup programs, often there's just one main program
            opportunity = Opportunity(
                title=f"{config['name']} - Startup Program",
                description=await self._extract_program_description(soup),
                organization=config['name'],
                location=await self._extract_location(soup, config),
                url=config['url'],
                application_url=config.get('apply_url', config['url']),
                opportunity_type=OpportunityType.STARTUP_PROGRAM,
                deadline=await self._extract_deadline(soup, config),
                requirements=OpportunityRequirements(other=[await self._extract_requirements(soup)]),
                source=SourceType.ACCELERATOR_SCRAPER
            )
            
            opportunities.append(opportunity)
            
        except Exception as e:
            self.logger.error(f"Error scraping startup program {config.get('name', '')}: {e}")
        
        return opportunities
    
    async def _scrape_traditional_accelerator(self, config: Dict[str, Any]) -> List[Opportunity]:
        """Scrape traditional accelerators with cohort-based programs"""
        opportunities = []
        
        try:
            html = await self.fetch_html(config['url'])
            if not html:
                return opportunities
            
            soup = BeautifulSoup(html, 'html.parser')
            
            # Look for multiple cohorts or programs
            program_elements = []
            for selector in self.selectors["program_cards"]:
                program_elements.extend(soup.select(selector))
            
            if not program_elements:
                # If no program cards found, create one main opportunity
                opportunity = await self._create_accelerator_opportunity(soup, config)
                if opportunity:
                    opportunities.append(opportunity)
            else:
                # Process each program/cohort
                for element in program_elements[:10]:  # Limit to prevent too many results
                    opportunity = await self._create_accelerator_opportunity_from_element(element, config)
                    if opportunity:
                        opportunities.append(opportunity)
            
        except Exception as e:
            self.logger.error(f"Error scraping traditional accelerator {config.get('name', '')}: {e}")
        
        return opportunities
    
    async def _scrape_corporate_accelerator(self, config: Dict[str, Any]) -> List[Opportunity]:
        """Scrape corporate accelerators"""
        return await self._scrape_traditional_accelerator(config)
    
    async def _scrape_university_accelerator(self, config: Dict[str, Any]) -> List[Opportunity]:
        """Scrape university-based accelerators"""
        return await self._scrape_traditional_accelerator(config)
    
    async def _scrape_vc_program(self, config: Dict[str, Any]) -> List[Opportunity]:
        """Scrape VC programs and investment opportunities"""
        opportunities = []
        
        try:
            html = await self.fetch_html(config['url'])
            if not html:
                return opportunities
            
            soup = BeautifulSoup(html, 'html.parser')
            
            opportunity = Opportunity(
                title=f"{config['name']} - Investment Program",
                description=await self._extract_program_description(soup),
                company=config['name'],
                location=await self._extract_location(soup, config),
                url=config['url'],
                apply_url=config.get('apply_url', config['url']),
                opportunity_type=OpportunityType.FUNDING,
                deadline=await self._extract_deadline(soup, config),
                salary_range=config.get('funding', ''),
                requirements=await self._extract_requirements(soup),
                source="accelerator_scraper",
                scraped_at=datetime.now(),
                metadata={
                    'tier': config.get('tier', ''),
                    'frequency': config.get('frequency', ''),
                    'specialty': config.get('specialty', ''),
                    'region': config.get('region', ''),
                    'apply_method': config.get('apply_method', ''),
                    'accelerator_type': config.get('type', '')
                }
            )
            
            opportunities.append(opportunity)
            
        except Exception as e:
            self.logger.error(f"Error scraping VC program {config.get('name', '')}: {e}")
        
        return opportunities
    
    async def _scrape_competition(self, config: Dict[str, Any]) -> List[Opportunity]:
        """Scrape competitions and challenges"""
        opportunities = []
        
        try:
            html = await self.fetch_html(config['url'])
            if not html:
                return opportunities
            
            soup = BeautifulSoup(html, 'html.parser')
            
            opportunity = Opportunity(
                title=f"{config['name']} - Competition",
                description=await self._extract_program_description(soup),
                company=config['name'],
                location=await self._extract_location(soup, config),
                url=config['url'],
                apply_url=config.get('apply_url', config['url']),
                opportunity_type=OpportunityType.COMPETITION,
                deadline=await self._extract_deadline(soup, config),
                salary_range=config.get('prize_amount', ''),
                requirements=await self._extract_requirements(soup),
                source="accelerator_scraper",
                scraped_at=datetime.now(),
                metadata={
                    'tier': config.get('tier', ''),
                    'frequency': config.get('frequency', ''),
                    'specialty': config.get('specialty', ''),
                    'region': config.get('region', ''),
                    'apply_method': config.get('apply_method', ''),
                    'accelerator_type': config.get('type', '')
                }
            )
            
            opportunities.append(opportunity)
            
        except Exception as e:
            self.logger.error(f"Error scraping competition {config.get('name', '')}: {e}")
        
        return opportunities
    
    async def _scrape_generic_accelerator(self, config: Dict[str, Any]) -> List[Opportunity]:
        """Generic fallback scraping for unknown accelerator types"""
        return await self._scrape_traditional_accelerator(config)
    
    async def _create_accelerator_opportunity(self, soup: BeautifulSoup, config: Dict[str, Any]) -> Optional[Opportunity]:
        """Create an opportunity from the main page content"""
        try:
            title = f"{config['name']} - {config.get('type', 'Program').title()}"
            
            opportunity = Opportunity(
                title=title,
                description=await self._extract_program_description(soup),
                company=config['name'],
                location=await self._extract_location(soup, config),
                url=config['url'],
                apply_url=config.get('apply_url', config['url']),
                opportunity_type=self._map_opportunity_type(config.get('type', 'accelerator')),
                deadline=await self._extract_deadline(soup, config),
                salary_range=config.get('funding', ''),
                requirements=await self._extract_requirements(soup),
                source="accelerator_scraper",
                scraped_at=datetime.now(),
                metadata={
                    'tier': config.get('tier', ''),
                    'frequency': config.get('frequency', ''),
                    'specialty': config.get('specialty', ''),
                    'region': config.get('region', ''),
                    'apply_method': config.get('apply_method', ''),
                    'accelerator_type': config.get('type', '')
                }
            )
            
            return opportunity
            
        except Exception as e:
            self.logger.error(f"Error creating accelerator opportunity: {e}")
            return None
    
    async def _create_accelerator_opportunity_from_element(self, element, config: Dict[str, Any]) -> Optional[Opportunity]:
        """Create an opportunity from a specific HTML element"""
        try:
            title_element = None
            for selector in self.selectors["titles"]:
                title_element = element.select_one(selector)
                if title_element:
                    break
            
            title = clean_text(title_element.get_text()) if title_element else f"{config['name']} Program"
            
            desc_element = None
            for selector in self.selectors["descriptions"]:
                desc_element = element.select_one(selector)
                if desc_element:
                    break
            
            description = clean_text(desc_element.get_text()) if desc_element else ""
            
            # Extract apply link
            apply_link = config.get('apply_url', config['url'])
            link_element = None
            for selector in self.selectors["links"]:
                link_element = element.select_one(selector)
                if link_element and link_element.get('href'):
                    apply_link = normalize_url(link_element.get('href'), config['url'])
                    break
            
            opportunity = Opportunity(
                title=title,
                description=description,
                company=config['name'],
                location=await self._extract_location_from_element(element, config),
                url=config['url'],
                apply_url=apply_link,
                opportunity_type=self._map_opportunity_type(config.get('type', 'accelerator')),
                deadline=await self._extract_deadline_from_element(element, config),
                salary_range=config.get('funding', ''),
                requirements="",
                source="accelerator_scraper",
                scraped_at=datetime.now(),
                metadata={
                    'tier': config.get('tier', ''),
                    'frequency': config.get('frequency', ''),
                    'specialty': config.get('specialty', ''),
                    'region': config.get('region', ''),
                    'apply_method': config.get('apply_method', ''),
                    'accelerator_type': config.get('type', '')
                }
            )
            
            return opportunity
            
        except Exception as e:
            self.logger.error(f"Error creating opportunity from element: {e}")
            return None
    
    async def _extract_program_description(self, soup: BeautifulSoup) -> str:
        """Extract program description from page"""
        try:
            for selector in self.selectors["descriptions"]:
                elements = soup.select(selector)
                if elements:
                    descriptions = []
                    for elem in elements[:3]:  # Take first 3 description elements
                        text = clean_text(elem.get_text())
                        if len(text) > 50:  # Only include substantial descriptions
                            descriptions.append(text)
                    
                    if descriptions:
                        return " ".join(descriptions)[:1000]  # Limit length
            
            # Fallback: try meta description
            meta_desc = soup.select_one('meta[name="description"]')
            if meta_desc and meta_desc.get('content'):
                return clean_text(meta_desc.get('content'))
            
            return "Accelerator/startup program - visit website for details"
            
        except Exception as e:
            self.logger.error(f"Error extracting program description: {e}")
            return ""
    
    async def _extract_location(self, soup: BeautifulSoup, config: Dict[str, Any]) -> str:
        """Extract location information"""
        try:
            # First check config for region info
            if config.get('region'):
                return config['region'].title()
            
            # Then try to extract from page
            for selector in self.selectors["location"]:
                location_element = soup.select_one(selector)
                if location_element:
                    location = clean_text(location_element.get_text())
                    if location and len(location) < 100:
                        return location
            
            # Fallback based on accelerator name patterns
            name = config.get('name', '').lower()
            if 'africa' in name:
                return "Africa"
            elif 'nairobi' in name:
                return "Nairobi, Kenya"
            elif 'silicon valley' in name or 'san francisco' in name:
                return "San Francisco, CA"
            elif 'boston' in name:
                return "Boston, MA"
            elif 'london' in name:
                return "London, UK"
            
            return "Global/Remote"
            
        except Exception as e:
            self.logger.error(f"Error extracting location: {e}")
            return "Unknown"
    
    async def _extract_location_from_element(self, element, config: Dict[str, Any]) -> str:
        """Extract location from specific element"""
        try:
            for selector in self.selectors["location"]:
                location_element = element.select_one(selector)
                if location_element:
                    location = clean_text(location_element.get_text())
                    if location and len(location) < 100:
                        return location
            
            return await self._extract_location(element, config)
            
        except Exception as e:
            return "Unknown"
    
    async def _extract_deadline(self, soup: BeautifulSoup, config: Dict[str, Any]) -> Optional[datetime]:
        """Extract application deadline"""
        try:
            # Check frequency to estimate deadlines
            frequency = config.get('frequency', 'rolling')
            
            if frequency == 'rolling':
                # Rolling applications - no specific deadline
                return None
            elif frequency == 'biannual':
                # Estimate next biannual deadline
                now = datetime.now()
                if now.month <= 6:
                    return datetime(now.year, 6, 30)  # June deadline
                else:
                    return datetime(now.year + 1, 1, 31)  # January deadline
            elif frequency == 'quarterly':
                # Estimate next quarterly deadline
                now = datetime.now()
                next_quarter_month = ((now.month - 1) // 3 + 1) * 3 + 1
                if next_quarter_month > 12:
                    return datetime(now.year + 1, 1, 31)
                else:
                    return datetime(now.year, next_quarter_month, 1)
            elif frequency == 'yearly':
                # Estimate next yearly deadline
                now = datetime.now()
                return datetime(now.year + 1, 3, 31)  # Common application deadline
            
            # Try to extract from page content
            for selector in self.selectors["dates"]:
                date_elements = soup.select(selector)
                for elem in date_elements:
                    date_text = clean_text(elem.get_text())
                    extracted_date = extract_dates(date_text)
                    if extracted_date:
                        return extracted_date[0]
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error extracting deadline: {e}")
            return None
    
    async def _extract_deadline_from_element(self, element, config: Dict[str, Any]) -> Optional[datetime]:
        """Extract deadline from specific element"""
        try:
            for selector in self.selectors["dates"]:
                date_element = element.select_one(selector)
                if date_element:
                    date_text = clean_text(date_element.get_text())
                    extracted_date = extract_dates(date_text)
                    if extracted_date:
                        return extracted_date[0]
            
            return await self._extract_deadline(element, config)
            
        except Exception as e:
            return None
    
    async def _extract_requirements(self, soup: BeautifulSoup) -> str:
        """Extract program requirements"""
        try:
            requirement_keywords = [
                'requirements', 'eligibility', 'criteria', 'qualifications',
                'who can apply', 'application requirements'
            ]
            
            for keyword in requirement_keywords:
                # Look for headers containing requirement keywords
                headers = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
                for header in headers:
                    if keyword.lower() in header.get_text().lower():
                        # Get the next element(s) after the header
                        next_elem = header.find_next_sibling()
                        if next_elem:
                            requirements = clean_text(next_elem.get_text())
                            if len(requirements) > 50:
                                return requirements[:500]
            
            return ""
            
        except Exception as e:
            self.logger.error(f"Error extracting requirements: {e}")
            return ""
    
    def _map_opportunity_type(self, accelerator_type: str) -> OpportunityType:
        """Map accelerator type to OpportunityType enum"""
        type_mapping = {
            'accelerator': OpportunityType.ACCELERATOR,
            'incubator': OpportunityType.ACCELERATOR,
            'startup_program': OpportunityType.STARTUP_PROGRAM,
            'corporate_accelerator': OpportunityType.ACCELERATOR,
            'university_accelerator': OpportunityType.ACCELERATOR,
            'vc_program': OpportunityType.FUNDING,
            'competition': OpportunityType.COMPETITION,
            'prize_competition': OpportunityType.COMPETITION,
            'innovation_challenge': OpportunityType.COMPETITION,
            'fellowship_program': OpportunityType.FELLOWSHIP,
            'grant_program': OpportunityType.GRANT,
            'innovation_fund': OpportunityType.FUNDING
        }
        
        return type_mapping.get(accelerator_type, OpportunityType.OTHER)
    
    async def scrape_all_accelerators(self, limit: Optional[int] = None) -> List[Opportunity]:
        """Scrape all accelerators from the configuration"""
        from .opportunity_sources import OPPORTUNITY_SOURCES
        
        all_opportunities = []
        accelerators = OPPORTUNITY_SOURCES.get('accelerators', {})
        
        # Sort accelerators by tier for priority scraping
        tier_priority = {
            'tier1': 1,
            'corporate': 2,
            'university': 3,
            'tier2': 4,
            'specialty': 5,
            'regional': 6,
            'vc': 7,
            'startup_program': 8,
            'unknown': 9
        }
        
        sorted_accelerators = sorted(
            accelerators.items(),
            key=lambda x: tier_priority.get(x[1].get('tier', 'unknown'), 9)
        )
        
        if limit:
            sorted_accelerators = sorted_accelerators[:limit]
        
        # Process accelerators in batches to avoid overwhelming servers
        batch_size = 5
        for i in range(0, len(sorted_accelerators), batch_size):
            batch = sorted_accelerators[i:i + batch_size]
            
            tasks = []
            for acc_id, acc_config in batch:
                task = self.scrape_single_accelerator(acc_config)
                tasks.append(task)
            
            try:
                batch_results = await asyncio.gather(*tasks, return_exceptions=True)
                
                for result in batch_results:
                    if isinstance(result, list):
                        all_opportunities.extend(result)
                    elif isinstance(result, Exception):
                        self.logger.error(f"Batch processing error: {result}")
                
                # Add delay between batches to be respectful
                await asyncio.sleep(2)
                
            except Exception as e:
                self.logger.error(f"Error processing batch: {e}")
        
        self.logger.info(f"Total accelerator opportunities scraped: {len(all_opportunities)}")
        return all_opportunities


# Async function for external use
async def scrape_accelerators(limit: Optional[int] = None) -> List[Opportunity]:
    """Main function to scrape all accelerator opportunities"""
    scraper = AcceleratorScraper()
    return await scraper.scrape_all_accelerators(limit=limit)


# For testing individual accelerators
async def test_single_accelerator(accelerator_name: str) -> List[Opportunity]:
    """Test scraping a single accelerator by name"""
    from .opportunity_sources import OPPORTUNITY_SOURCES
    
    accelerators = OPPORTUNITY_SOURCES.get('accelerators', {})
    
    if accelerator_name not in accelerators:
        print(f"Accelerator '{accelerator_name}' not found in configuration")
        return []
    
    scraper = AcceleratorScraper()
    return await scraper.scrape_single_accelerator(accelerators[accelerator_name])


if __name__ == "__main__":
    # Test the scraper
    async def main():
        # Test with a few tier 1 accelerators
        opportunities = await scrape_accelerators(limit=10)
        
        print(f"Found {len(opportunities)} opportunities:")
        for opp in opportunities:
            print(f"- {opp.title} at {opp.company} ({opp.location})")
    
    asyncio.run(main())