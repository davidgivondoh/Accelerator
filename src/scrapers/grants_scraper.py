"""
Grants.gov Scraper
==================
Scrapes federal grant opportunities from Grants.gov API.
"""

import asyncio
import httpx
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
import hashlib

logger = logging.getLogger(__name__)


class GrantsGovScraper:
    """
    Grants.gov API Scraper.
    Uses their official REST API for searching federal grants.
    """
    
    BASE_URL = "https://www.grants.gov"
    SEARCH_API = "https://www.grants.gov/grantsws/rest/opportunities/search"
    DETAIL_API = "https://www.grants.gov/grantsws/rest/opportunity/details"
    
    def __init__(self):
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "GrowthEngine/1.0 (Grant Aggregator)",
        }
    
    async def search_grants(
        self,
        keywords: str = "",
        funding_categories: List[str] = None,
        eligibility: List[str] = None,
        agency: str = "",
        posted_within_days: int = 30,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Search Grants.gov for opportunities.
        
        Args:
            keywords: Search keywords
            funding_categories: List of funding category codes
                - ST: Science and Technology
                - ED: Education
                - HL: Health
                - EN: Energy
                - ENV: Environment
                - AG: Agriculture
                - etc.
            eligibility: List of eligibility codes
                - 00: State governments
                - 01: County governments
                - 02: City or township governments
                - 04: Special district governments
                - 05: Independent school districts
                - 06: Public/State controlled institutions of higher education
                - 07: Native American tribal governments
                - 08: Public housing authorities
                - 11: Native American tribal organizations
                - 12: Nonprofits having 501(c)(3) status
                - 13: Nonprofits without 501(c)(3) status
                - 20: Private institutions of higher education
                - 21: Individuals
                - 22: For-profit organizations
                - 23: Small businesses
                - 25: Others
            agency: Agency code (e.g., "NSF", "NIH", "DOE")
            posted_within_days: Only grants posted within X days
            limit: Maximum results
            
        Returns:
            List of grant dictionaries
        """
        grants = []
        
        # Build search request
        search_params = {
            "keyword": keywords,
            "rows": min(limit, 100),  # API max is typically 100
            "sortBy": "openDate|desc",
        }
        
        # Add filters
        if funding_categories:
            search_params["fundingCategories"] = ",".join(funding_categories)
        if eligibility:
            search_params["eligibilities"] = ",".join(eligibility)
        if agency:
            search_params["agency"] = agency
        
        try:
            async with httpx.AsyncClient(headers=self.headers, timeout=60) as client:
                # Grants.gov uses POST for search
                response = await client.post(
                    self.SEARCH_API,
                    json=search_params
                )
                
                if response.status_code == 200:
                    data = response.json()
                    opportunities = data.get("oppHits", [])
                    
                    for opp in opportunities[:limit]:
                        grant = self._parse_grant(opp)
                        if grant:
                            grants.append(grant)
                    
                    logger.info(f"Grants.gov: Found {len(grants)} grants for '{keywords}'")
                else:
                    logger.warning(f"Grants.gov API returned status {response.status_code}")
                    
        except Exception as e:
            logger.error(f"Grants.gov scraper error: {e}")
        
        return grants
    
    def _parse_grant(self, data: Dict) -> Optional[Dict[str, Any]]:
        """Parse grant data from API response"""
        try:
            opp_id = str(data.get("id", data.get("opportunityId", "")))
            opp_number = data.get("number", data.get("opportunityNumber", ""))
            
            if not opp_id:
                return None
            
            unique_id = hashlib.md5(f"grants_gov:{opp_id}".encode()).hexdigest()[:16]
            
            # Parse dates
            close_date = None
            if data.get("closeDate"):
                try:
                    close_date = datetime.strptime(data["closeDate"], "%m/%d/%Y")
                except:
                    pass
            
            open_date = None
            if data.get("openDate"):
                try:
                    open_date = datetime.strptime(data["openDate"], "%m/%d/%Y")
                except:
                    pass
            
            # Parse award info
            award_ceiling = data.get("awardCeiling")
            award_floor = data.get("awardFloor")
            
            if award_ceiling and isinstance(award_ceiling, str):
                award_ceiling = int(award_ceiling.replace(",", "").replace("$", ""))
            if award_floor and isinstance(award_floor, str):
                award_floor = int(award_floor.replace(",", "").replace("$", ""))
            
            # Calculate urgency based on deadline
            urgency = "normal"
            if close_date:
                days_left = (close_date - datetime.now()).days
                if days_left <= 7:
                    urgency = "urgent"
                elif days_left <= 14:
                    urgency = "soon"
            
            return {
                "id": unique_id,
                "title": data.get("title", data.get("opportunityTitle", "Unknown Grant")),
                "agency": data.get("agency", data.get("agencyName", "")),
                "agency_code": data.get("agencyCode", ""),
                "opportunity_number": opp_number,
                "description": data.get("description", data.get("synopsis", "")),
                "award_floor": award_floor,
                "award_ceiling": award_ceiling,
                "estimated_funding": data.get("estimatedFunding"),
                "expected_awards": data.get("numberOfAwards"),
                "open_date": open_date.isoformat() if open_date else None,
                "close_date": close_date.isoformat() if close_date else None,
                "urgency": urgency,
                "eligibility": data.get("eligibility", []),
                "funding_category": data.get("fundingCategory", ""),
                "apply_url": f"https://www.grants.gov/web/grants/view-opportunity.html?oppId={opp_id}",
                "source": "grants_gov",
                "source_id": opp_id,
                "opportunity_type": "grant",
                "match_score": 0.0,
                "scraped_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error parsing grant: {e}")
            return None
    
    async def get_grant_details(self, opportunity_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific grant"""
        try:
            async with httpx.AsyncClient(headers=self.headers, timeout=30) as client:
                response = await client.get(
                    f"{self.DETAIL_API}/{opportunity_id}"
                )
                
                if response.status_code == 200:
                    return response.json()
                    
        except Exception as e:
            logger.error(f"Error fetching grant details: {e}")
        
        return None


# Specialized grant searches
async def search_tech_grants(limit: int = 50) -> List[Dict]:
    """Search for technology and science grants"""
    scraper = GrantsGovScraper()
    return await scraper.search_grants(
        keywords="technology research innovation",
        funding_categories=["ST", "O"],  # Science & Tech, Other
        eligibility=["12", "21", "22", "23"],  # Nonprofits, Individuals, For-profit, Small biz
        limit=limit
    )


async def search_ai_grants(limit: int = 50) -> List[Dict]:
    """Search for AI and ML related grants"""
    scraper = GrantsGovScraper()
    return await scraper.search_grants(
        keywords="artificial intelligence machine learning AI",
        limit=limit
    )


async def search_small_business_grants(limit: int = 50) -> List[Dict]:
    """Search for small business grants (SBIR/STTR)"""
    scraper = GrantsGovScraper()
    return await scraper.search_grants(
        keywords="SBIR STTR small business innovation",
        eligibility=["23"],  # Small businesses
        limit=limit
    )


async def scrape_grants_gov(
    keywords: str = "",
    limit: int = 50
) -> List[Dict]:
    """
    Convenience function to scrape Grants.gov.
    """
    scraper = GrantsGovScraper()
    return await scraper.search_grants(keywords=keywords, limit=limit)


if __name__ == "__main__":
    async def test():
        # Search for AI grants
        grants = await search_ai_grants(limit=10)
        print(f"Found {len(grants)} AI-related grants\n")
        
        for grant in grants:
            print(f"{grant['title']}")
            print(f"  Agency: {grant['agency']}")
            print(f"  Award: ${grant.get('award_floor', 0):,} - ${grant.get('award_ceiling', 0):,}")
            print(f"  Deadline: {grant.get('close_date', 'N/A')}")
            print(f"  URL: {grant['apply_url']}")
            print()
    
    asyncio.run(test())
