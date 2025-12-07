"""
Comprehensive Scholarship & Fellowship Scraper
Handles 120+ scholarship sources including government, university, foundation, and corporate programs
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Union
from urllib.parse import urljoin, urlparse
import re

from bs4 import BeautifulSoup
import httpx

from .base_scraper import BaseScraper
from src.models.opportunity import Opportunity
from src.models.enums import OpportunityType, SourceType, ApplicationStatus
from .utils import clean_text, extract_dates, normalize_url

logger = logging.getLogger(__name__)

class ScholarshipScraper(BaseScraper):
    """
    Comprehensive scraper for scholarship and fellowship opportunities
    Supports multiple scholarship types: government, university, foundation, corporate, research
    """
    
    def __init__(self, timeout: int = 30, max_retries: int = 3):
        super().__init__(
            name="ScholarshipScraper",
            base_url="https://scholarships.com",
            timeout=timeout,
            max_retries=max_retries
        )
        self.source_type = SourceType.SCHOLARSHIP_SCRAPER
        
        # Scholarship-specific keywords for opportunity detection
        self.scholarship_keywords = {
            'titles': [
                'scholarship', 'fellowship', 'grant', 'award', 'bursary', 'stipend',
                'financial aid', 'funding', 'assistantship', 'studentship', 'prize'
            ],
            'amounts': [
                'full funding', 'partial funding', 'tuition waiver', 'living allowance',
                'research funding', 'travel grant', 'stipend'
            ],
            'levels': [
                'undergraduate', 'graduate', 'postgraduate', 'doctoral', 'phd',
                'masters', 'bachelor', 'postdoc', 'research'
            ],
            'regions': [
                'international', 'global', 'developing countries', 'africa', 'asia',
                'europe', 'americas', 'commonwealth', 'francophone'
            ]
        }
        
        # Common date patterns for scholarship deadlines
        self.date_patterns = [
            r'deadline[:\s]*([^<\n]+)',
            r'apply by[:\s]*([^<\n]+)',
            r'due[:\s]*([^<\n]+)',
            r'closes?[:\s]*([^<\n]+)',
            r'applications? close[:\s]*([^<\n]+)'
        ]
        
        # Award amount extraction patterns
        self.amount_patterns = [
            r'\$[\d,]+(?:\.\d{2})?',
            r'€[\d,]+(?:\.\d{2})?', 
            r'£[\d,]+(?:\.\d{2})?',
            r'¥[\d,]+',
            r'CHF\s*[\d,]+',
            r'full funding',
            r'tuition\s+waiver',
            r'living\s+allowance'
        ]

    async def scrape_opportunities(self, source_config: Dict[str, Any]) -> List[Opportunity]:
        """
        Main scraping method for scholarship opportunities
        Adapts to different scholarship source types and structures
        """
        opportunities = []
        
        try:
            # Get source metadata
            source_name = source_config.get('name', 'Unknown Scholarship')
            source_url = source_config.get('url', '')
            scholarship_type = source_config.get('type', 'scholarship')
            tier = source_config.get('tier', 'tier2')
            region = source_config.get('region', 'global')
            specialty = source_config.get('specialty', None)
            
            logger.info(f"Scraping scholarship source: {source_name}")
            
            # Fetch the main page
            html_content = await self._fetch_page(source_url)
            if not html_content:
                logger.warning(f"Failed to fetch content from {source_url}")
                return opportunities
            
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Try different scraping strategies based on source type
            if scholarship_type == 'scholarship_platform':
                opportunities = await self._scrape_platform(soup, source_config)
            elif scholarship_type in ['government_scholarship', 'university_scholarship']:
                opportunities = await self._scrape_institutional(soup, source_config)
            elif scholarship_type == 'foundation_scholarship':
                opportunities = await self._scrape_foundation(soup, source_config)
            elif scholarship_type == 'corporate_scholarship':
                opportunities = await self._scrape_corporate(soup, source_config)
            elif scholarship_type in ['research_grant', 'research_fellowship']:
                opportunities = await self._scrape_research(soup, source_config)
            else:
                # Generic scholarship scraping
                opportunities = await self._scrape_generic(soup, source_config)
            
            # Enhance opportunities with source metadata
            for opp in opportunities:
                opp.tags.extend([tier, region])
                if specialty:
                    opp.tags.append(specialty)
                opp.source_url = source_url
            
            logger.info(f"Successfully scraped {len(opportunities)} opportunities from {source_name}")
            
        except Exception as e:
            logger.error(f"Error scraping {source_config.get('name', 'Unknown')}: {str(e)}")
        
        return opportunities

    async def _scrape_platform(self, soup: BeautifulSoup, source_config: Dict[str, Any]) -> List[Opportunity]:
        """Scrape scholarship platforms and databases"""
        opportunities = []
        
        # Look for scholarship listings on platform pages
        scholarship_selectors = [
            '.scholarship-item', '.scholarship-card', '.opportunity-item',
            '.listing-item', '.search-result', '.scholarship-listing',
            'article', '.post', '.entry'
        ]
        
        for selector in scholarship_selectors:
            items = soup.select(selector)
            if items:
                for item in items[:20]:  # Limit to avoid overwhelming
                    opp = await self._extract_opportunity_from_element(item, source_config)
                    if opp:
                        opportunities.append(opp)
                break
        
        return opportunities

    async def _scrape_institutional(self, soup: BeautifulSoup, source_config: Dict[str, Any]) -> List[Opportunity]:
        """Scrape government and university scholarship pages"""
        opportunities = []
        
        # Look for scholarship program sections
        program_selectors = [
            '.program', '.scholarship', '.funding-opportunity',
            '.award', '.fellowship', '.grant-program'
        ]
        
        # Also check for links to detailed scholarship pages
        scholarship_links = soup.find_all('a', href=True)
        relevant_links = []
        
        for link in scholarship_links[:15]:  # Limit link following
            href = link.get('href', '')
            link_text = clean_text(link.get_text())
            
            if any(keyword in link_text.lower() for keyword in self.scholarship_keywords['titles']):
                full_url = urljoin(source_config['url'], href)
                relevant_links.append((full_url, link_text))
        
        # Scrape linked pages
        for url, title in relevant_links:
            try:
                linked_content = await self._fetch_page(url)
                if linked_content:
                    linked_soup = BeautifulSoup(linked_content, 'html.parser')
                    opp = await self._extract_detailed_opportunity(linked_soup, source_config, url, title)
                    if opp:
                        opportunities.append(opp)
            except Exception as e:
                logger.debug(f"Error fetching linked page {url}: {e}")
        
        # Also try to extract from main page
        main_opp = await self._extract_opportunity_from_page(soup, source_config)
        if main_opp:
            opportunities.append(main_opp)
        
        return opportunities

    async def _scrape_foundation(self, soup: BeautifulSoup, source_config: Dict[str, Any]) -> List[Opportunity]:
        """Scrape foundation and private scholarship pages"""
        return await self._scrape_generic(soup, source_config)

    async def _scrape_corporate(self, soup: BeautifulSoup, source_config: Dict[str, Any]) -> List[Opportunity]:
        """Scrape corporate scholarship programs"""
        opportunities = []
        
        # Corporate scholarships often have dedicated sections
        program_selectors = [
            '.scholarship-program', '.student-program', '.education-program',
            '.diversity-program', '.internship', '.fellowship'
        ]
        
        for selector in program_selectors:
            items = soup.select(selector)
            if items:
                for item in items:
                    opp = await self._extract_opportunity_from_element(item, source_config)
                    if opp:
                        opportunities.append(opp)
        
        # If no specific sections found, try generic extraction
        if not opportunities:
            main_opp = await self._extract_opportunity_from_page(soup, source_config)
            if main_opp:
                opportunities.append(main_opp)
        
        return opportunities

    async def _scrape_research(self, soup: BeautifulSoup, source_config: Dict[str, Any]) -> List[Opportunity]:
        """Scrape research grants and fellowship opportunities"""
        opportunities = []
        
        # Research opportunities often have specific structures
        research_selectors = [
            '.grant', '.fellowship', '.funding-opportunity',
            '.research-program', '.call-for-proposals'
        ]
        
        for selector in research_selectors:
            items = soup.select(selector)
            if items:
                for item in items[:10]:  # Research grants are usually fewer
                    opp = await self._extract_opportunity_from_element(item, source_config)
                    if opp:
                        # Research opportunities are typically grants
                        opp.opportunity_type = OpportunityType.GRANT
                        opportunities.append(opp)
        
        return opportunities

    async def _scrape_generic(self, soup: BeautifulSoup, source_config: Dict[str, Any]) -> List[Opportunity]:
        """Generic scholarship scraping for unknown structures"""
        opportunities = []
        
        # Try to extract main opportunity from page
        main_opp = await self._extract_opportunity_from_page(soup, source_config)
        if main_opp:
            opportunities.append(main_opp)
        
        return opportunities

    async def _extract_opportunity_from_element(self, element, source_config: Dict[str, Any]) -> Optional[Opportunity]:
        """Extract opportunity data from a DOM element"""
        try:
            # Extract title
            title_selectors = ['h1', 'h2', 'h3', '.title', '.name', '.heading', 'a']
            title = None
            for selector in title_selectors:
                title_elem = element.select_one(selector)
                if title_elem:
                    title = clean_text(title_elem.get_text())
                    break
            
            if not title or len(title) < 10:
                title = source_config.get('name', 'Scholarship Opportunity')
            
            # Extract description
            desc_selectors = ['.description', '.summary', '.excerpt', 'p', '.content']
            description = ""
            for selector in desc_selectors:
                desc_elem = element.select_one(selector)
                if desc_elem:
                    description = clean_text(desc_elem.get_text())[:500]
                    break
            
            if not description:
                description = f"Scholarship opportunity from {source_config.get('name', 'Unknown Source')}"
            
            # Extract URL if available
            url_elem = element.select_one('a')
            opportunity_url = source_config['url']
            if url_elem and url_elem.get('href'):
                opportunity_url = urljoin(source_config['url'], url_elem['href'])
            
            # Determine opportunity type
            opp_type = self._determine_opportunity_type(title, description, source_config)
            
            # Extract deadline
            deadline = self._extract_deadline(element.get_text())
            
            # Extract award amount
            award_amount = self._extract_award_amount(element.get_text())
            
            # Create opportunity
            opportunity = Opportunity(
                title=title,
                organization=source_config.get('name', 'Unknown Organization'),
                description=description,
                opportunity_type=opp_type,
                application_url=opportunity_url,
                deadline=deadline,
                award_amount=award_amount,
                location=source_config.get('region', 'Global'),
                tags=[
                    source_config.get('type', 'scholarship'),
                    source_config.get('tier', 'tier2'),
                    source_config.get('specialty', 'general')
                ],
                source_url=source_config['url'],
                application_status=ApplicationStatus.NOT_APPLIED,
                created_at=datetime.now()
            )
            
            return opportunity
            
        except Exception as e:
            logger.debug(f"Error extracting opportunity from element: {e}")
            return None

    async def _extract_opportunity_from_page(self, soup: BeautifulSoup, source_config: Dict[str, Any]) -> Optional[Opportunity]:
        """Extract single opportunity from entire page"""
        try:
            # Extract title from page
            title_selectors = ['h1', 'title', '.page-title', '.main-title']
            title = None
            for selector in title_selectors:
                title_elem = soup.select_one(selector)
                if title_elem:
                    title = clean_text(title_elem.get_text())
                    if len(title) > 10:
                        break
            
            if not title or len(title) < 10:
                title = source_config.get('name', 'Scholarship Opportunity')
            
            # Extract description from main content
            content_selectors = [
                '.main-content', '.content', '.description', 
                '.about', '.program-details', 'main'
            ]
            description = ""
            for selector in content_selectors:
                content_elem = soup.select_one(selector)
                if content_elem:
                    paragraphs = content_elem.find_all('p')
                    desc_parts = [clean_text(p.get_text()) for p in paragraphs[:3]]
                    description = ' '.join(desc_parts)[:500]
                    break
            
            if not description:
                # Fallback to meta description
                meta_desc = soup.find('meta', attrs={'name': 'description'})
                if meta_desc:
                    description = meta_desc.get('content', '')[:500]
                else:
                    description = f"Scholarship opportunity from {source_config.get('name', 'Unknown Source')}"
            
            # Determine opportunity type
            opp_type = self._determine_opportunity_type(title, description, source_config)
            
            # Extract deadline from page content
            page_text = soup.get_text()
            deadline = self._extract_deadline(page_text)
            
            # Extract award amount
            award_amount = self._extract_award_amount(page_text)
            
            # Create opportunity
            opportunity = Opportunity(
                title=title,
                organization=source_config.get('name', 'Unknown Organization'),
                description=description,
                opportunity_type=opp_type,
                application_url=source_config['url'],
                deadline=deadline,
                award_amount=award_amount,
                location=source_config.get('region', 'Global'),
                tags=[
                    source_config.get('type', 'scholarship'),
                    source_config.get('tier', 'tier2'),
                    source_config.get('specialty', 'general')
                ],
                source_url=source_config['url'],
                application_status=ApplicationStatus.NOT_APPLIED,
                created_at=datetime.now()
            )
            
            return opportunity
            
        except Exception as e:
            logger.debug(f"Error extracting opportunity from page: {e}")
            return None

    async def _extract_detailed_opportunity(self, soup: BeautifulSoup, source_config: Dict[str, Any], 
                                          url: str, title: str) -> Optional[Opportunity]:
        """Extract opportunity from a detailed linked page"""
        try:
            # Use provided title or extract from page
            if not title or len(title) < 10:
                title_elem = soup.select_one('h1')
                if title_elem:
                    title = clean_text(title_elem.get_text())
                else:
                    title = source_config.get('name', 'Scholarship Opportunity')
            
            # Extract detailed description
            content_selectors = [
                '.content', '.main-content', '.description',
                '.program-description', '.opportunity-details'
            ]
            description = ""
            for selector in content_selectors:
                content_elem = soup.select_one(selector)
                if content_elem:
                    paragraphs = content_elem.find_all('p')
                    desc_parts = [clean_text(p.get_text()) for p in paragraphs[:5]]
                    description = ' '.join(desc_parts)[:800]
                    break
            
            if not description:
                description = f"Detailed scholarship opportunity from {source_config.get('name')}"
            
            # Determine opportunity type
            opp_type = self._determine_opportunity_type(title, description, source_config)
            
            # Extract deadline
            page_text = soup.get_text()
            deadline = self._extract_deadline(page_text)
            
            # Extract award amount
            award_amount = self._extract_award_amount(page_text)
            
            # Create opportunity
            opportunity = Opportunity(
                title=title,
                organization=source_config.get('name', 'Unknown Organization'),
                description=description,
                opportunity_type=opp_type,
                application_url=url,
                deadline=deadline,
                award_amount=award_amount,
                location=source_config.get('region', 'Global'),
                tags=[
                    source_config.get('type', 'scholarship'),
                    source_config.get('tier', 'tier2'),
                    source_config.get('specialty', 'general'),
                    'detailed'
                ],
                source_url=source_config['url'],
                application_status=ApplicationStatus.NOT_APPLIED,
                created_at=datetime.now()
            )
            
            return opportunity
            
        except Exception as e:
            logger.debug(f"Error extracting detailed opportunity: {e}")
            return None

    def _determine_opportunity_type(self, title: str, description: str, source_config: Dict[str, Any]) -> OpportunityType:
        """Determine the appropriate OpportunityType for a scholarship"""
        text = f"{title} {description}".lower()
        source_type = source_config.get('type', '').lower()
        
        # Check for specific types
        if any(word in text for word in ['fellowship', 'research fellow', 'postdoc']):
            return OpportunityType.FELLOWSHIP
        elif any(word in text for word in ['grant', 'research grant', 'funding']):
            return OpportunityType.GRANT
        elif any(word in text for word in ['internship', 'intern program']):
            return OpportunityType.INTERNSHIP
        elif 'competition' in text or 'contest' in text:
            return OpportunityType.COMPETITION
        elif source_type in ['research_grant', 'research_fellowship']:
            return OpportunityType.GRANT
        elif source_type == 'fellowship':
            return OpportunityType.FELLOWSHIP
        else:
            return OpportunityType.SCHOLARSHIP

    def _extract_deadline(self, text: str) -> Optional[datetime]:
        """Extract deadline from text content"""
        try:
            dates = extract_dates(text)
            if dates:
                # Return the earliest future date
                future_dates = [d for d in dates if d > datetime.now()]
                if future_dates:
                    return min(future_dates)
        except Exception as e:
            logger.debug(f"Error extracting deadline: {e}")
        return None

    def _extract_award_amount(self, text: str) -> Optional[str]:
        """Extract award amount from text"""
        try:
            for pattern in self.amount_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                if matches:
                    return matches[0]
        except Exception as e:
            logger.debug(f"Error extracting award amount: {e}")
        return None

    async def _fetch_page(self, url: str) -> Optional[str]:
        """Fetch page content with error handling"""
        try:
            response = await self.session.get(
                url,
                timeout=self.timeout,
                follow_redirects=True,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
            )
            if response.status_code == 200:
                return response.text
        except Exception as e:
            logger.debug(f"Error fetching {url}: {e}")
        return None

    # Abstract method implementations required by BaseScraper
    async def search(
        self,
        query: str,
        location: Optional[str] = None,
        page: int = 1,
        **filters
    ) -> List[Opportunity]:
        """
        Search for scholarship opportunities based on query
        This method fulfills the BaseScraper abstract method requirement
        """
        # For scholarships, we use our source-based scraping approach
        # Could be enhanced to filter by query/location in the future
        try:
            from .opportunity_sources import OPPORTUNITY_SOURCES
            scholarship_sources = OPPORTUNITY_SOURCES.get("scholarships", {})
            
            # Select a few sources for search
            selected_sources = list(scholarship_sources.items())[:5]
            opportunities = []
            
            for source_name, source_config in selected_sources:
                source_opps = await self.scrape_opportunities(source_config)
                opportunities.extend(source_opps[:10])  # Limit per source
                
                if len(opportunities) >= 20:  # Total limit
                    break
            
            return opportunities
            
        except Exception as e:
            logger.error(f"Error in scholarship search: {e}")
            return []

    async def get_details(self, opportunity_id: str) -> Optional[Opportunity]:
        """
        Get detailed information about a specific scholarship opportunity
        This method fulfills the BaseScraper abstract method requirement
        """
        # For now, return None as we don't have opportunity ID tracking
        # This could be enhanced to fetch detailed information from cached opportunities
        logger.debug(f"Detailed scholarship lookup not implemented for ID: {opportunity_id}")
        return None

# Helper function to create scraper instance
async def create_scholarship_scraper() -> ScholarshipScraper:
    """Create and initialize scholarship scraper"""
    scraper = ScholarshipScraper()
    await scraper.__aenter__()
    return scraper