"""
Unified Scraping Engine
=======================
Orchestrates all scrapers to aggregate opportunities from 100+ sources.
Implements parallel scraping, deduplication, and scoring.
"""

import asyncio
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import hashlib
import json

# Import scrapers
from .linkedin_scraper import LinkedInScraper, scrape_linkedin_jobs
from .indeed_scraper import IndeedScraper, scrape_indeed_jobs
from .remoteok_scraper import RemoteOKScraper, scrape_remoteok_jobs
from .wellfound_scraper import WellfoundScraper, scrape_wellfound_jobs
from .grants_scraper import GrantsGovScraper, scrape_grants_gov
from .opportunity_sources import OPPORTUNITY_SOURCES

logger = logging.getLogger(__name__)


@dataclass
class UserProfile:
    """User profile for opportunity matching"""
    skills: List[str]
    experience_years: int
    desired_roles: List[str]
    desired_locations: List[str]
    min_salary: Optional[int]
    remote_preferred: bool
    industries: List[str]
    keywords: List[str]


# Expanded keyword sets for comprehensive scanning
EXPANDED_KEYWORDS = {
    "tech": [
        "software engineer", "developer", "programmer", "coder",
        "full stack", "backend", "frontend", "web developer",
        "mobile developer", "ios developer", "android developer",
        "devops", "sre", "platform engineer", "infrastructure",
        "cloud engineer", "aws", "azure", "gcp",
        "data engineer", "etl", "data pipeline",
    ],
    "ai_ml": [
        "machine learning", "ml engineer", "ai engineer",
        "data scientist", "deep learning", "nlp", "computer vision",
        "ai research", "research scientist", "applied scientist",
        "llm", "generative ai", "prompt engineer",
    ],
    "product": [
        "product manager", "product owner", "program manager",
        "technical program manager", "project manager",
        "product designer", "ux designer", "ui designer",
    ],
    "leadership": [
        "engineering manager", "tech lead", "team lead",
        "director of engineering", "vp engineering", "cto",
        "principal engineer", "staff engineer", "architect",
    ],
    "data": [
        "data analyst", "business analyst", "analytics",
        "business intelligence", "tableau", "power bi",
        "sql", "python", "r programmer",
    ],
    "security": [
        "security engineer", "cybersecurity", "infosec",
        "penetration tester", "security analyst",
    ],
    "other": [
        "consultant", "solutions architect", "technical writer",
        "developer advocate", "developer relations",
        "qa engineer", "test engineer", "automation engineer",
    ]
}

ALL_KEYWORDS = []
for category in EXPANDED_KEYWORDS.values():
    ALL_KEYWORDS.extend(category)


class OpportunityScorer:
    """Scores opportunities based on user profile match"""
    
    def __init__(self, profile: UserProfile):
        self.profile = profile
    
    def score(self, opportunity: Dict) -> float:
        """
        Calculate match score (0-100) for an opportunity.
        
        Scoring factors:
        - Skill match: 30%
        - Role match: 25%
        - Salary match: 20%
        - Location/Remote match: 15%
        - Keywords match: 10%
        """
        score = 0.0
        
        title = opportunity.get("title", "").lower()
        description = opportunity.get("description", "").lower()
        location = opportunity.get("location", "").lower()
        
        # Skill match (30%)
        skill_matches = sum(1 for skill in self.profile.skills 
                          if skill.lower() in title or skill.lower() in description)
        skill_score = min(skill_matches / max(len(self.profile.skills), 1), 1.0) * 30
        score += skill_score
        
        # Role match (25%)
        role_matches = sum(1 for role in self.profile.desired_roles 
                         if role.lower() in title)
        role_score = min(role_matches, 1.0) * 25
        score += role_score
        
        # Salary match (20%)
        salary_min = opportunity.get("salary_min")
        if salary_min and self.profile.min_salary:
            if salary_min >= self.profile.min_salary:
                score += 20
            elif salary_min >= self.profile.min_salary * 0.8:
                score += 10
        else:
            score += 10  # Neutral if no salary info
        
        # Location/Remote match (15%)
        is_remote = opportunity.get("remote", False) or "remote" in location
        if is_remote and self.profile.remote_preferred:
            score += 15
        elif any(loc.lower() in location for loc in self.profile.desired_locations):
            score += 15
        elif is_remote:
            score += 10
        
        # Keywords match (10%)
        keyword_matches = sum(1 for kw in self.profile.keywords 
                            if kw.lower() in title or kw.lower() in description)
        keyword_score = min(keyword_matches / max(len(self.profile.keywords), 1), 1.0) * 10
        score += keyword_score
        
        return round(score, 1)


class ScrapingEngine:
    """
    Main scraping engine that orchestrates all scrapers.
    """
    
    def __init__(self, profile: Optional[UserProfile] = None):
        self.profile = profile or self._default_profile()
        self.scorer = OpportunityScorer(self.profile)
        self.scraped_opportunities: List[Dict] = []
        self.seen_ids: set = set()
        self.stats = {
            "total_scraped": 0,
            "by_source": {},
            "last_scan": None,
            "errors": []
        }
    
    def _default_profile(self) -> UserProfile:
        """Default user profile for scoring - expanded for broad matching"""
        return UserProfile(
            skills=[
                "python", "javascript", "typescript", "react", "node", "sql", 
                "aws", "gcp", "azure", "docker", "kubernetes",
                "machine learning", "ai", "data science", "analytics",
                "java", "go", "rust", "c++", "swift", "kotlin",
                "graphql", "rest", "microservices", "distributed systems"
            ],
            experience_years=5,
            desired_roles=[
                "engineer", "developer", "architect", "lead", "manager",
                "scientist", "analyst", "designer", "product", "consultant"
            ],
            desired_locations=[
                "remote", "san francisco", "new york", "austin", "seattle",
                "los angeles", "boston", "chicago", "denver", "miami",
                "worldwide", "anywhere", "usa", "united states"
            ],
            min_salary=80000,
            remote_preferred=True,
            industries=[
                "tech", "startup", "ai", "fintech", "healthtech", "edtech",
                "saas", "enterprise", "consumer", "b2b", "b2c",
                "crypto", "web3", "gaming", "media", "ecommerce"
            ],
            keywords=[
                "growth", "scale", "innovative", "ai", "ml", "startup",
                "remote-first", "equity", "series", "funded", "fast-paced",
                "cutting-edge", "impact", "mission-driven"
            ]
        )
    
    async def scrape_all_sources(
        self,
        keywords: List[str] = None,
        location: str = "remote",
        limit_per_source: int = 25,
        enabled_sources: List[str] = None
    ) -> List[Dict]:
        """
        Scan all available sources in parallel.
        
        Args:
            keywords: List of search keywords
            location: Location preference
            limit_per_source: Max results per source
            enabled_sources: List of source names to scan
            
        Returns:
            List of opportunities
        """
        keywords = keywords or ["software engineer", "developer"]
        enabled_sources = enabled_sources or ["linkedin", "indeed", "remoteok", "wellfound", "grants"]
        keyword_str = " ".join(keywords)
        
        logger.info(f"Starting scan with keywords: '{keyword_str}', sources: {enabled_sources}")
        self.stats["last_scan"] = datetime.utcnow().isoformat()
        
        # Define scraping tasks based on enabled sources
        tasks = []
        if "linkedin" in enabled_sources:
            tasks.append(self._scrape_with_error_handling("linkedin", self._scrape_linkedin, keyword_str, location, limit_per_source))
        if "indeed" in enabled_sources:
            tasks.append(self._scrape_with_error_handling("indeed", self._scrape_indeed, keyword_str, location, limit_per_source))
        if "remoteok" in enabled_sources:
            tasks.append(self._scrape_with_error_handling("remoteok", self._scrape_remoteok, keywords, limit_per_source))
        if "wellfound" in enabled_sources:
            tasks.append(self._scrape_with_error_handling("wellfound", self._scrape_wellfound, keyword_str, location, limit_per_source))
        if "grants" in enabled_sources:
            tasks.append(self._scrape_with_error_handling("grants", self._scrape_grants, keywords, limit_per_source))
        
        # Run all scrapers in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        all_opportunities = []
        for source_name, opportunities in results:
            if isinstance(opportunities, Exception):
                self.stats["errors"].append(f"{source_name}: {str(opportunities)}")
                continue
            
            # Score and add opportunities
            for opp in opportunities:
                if opp["id"] not in self.seen_ids:
                    opp["match_score"] = self.scorer.score(opp)
                    all_opportunities.append(opp)
                    self.seen_ids.add(opp["id"])
            
            self.stats["by_source"][source_name] = len(opportunities)
        
        # Sort by match score
        all_opportunities.sort(key=lambda x: x.get("match_score", 0), reverse=True)
        
        self.scraped_opportunities = all_opportunities
        self.stats["total_scraped"] = len(all_opportunities)
        
        logger.info(f"Scan complete: {len(all_opportunities)} total opportunities")
        
        return all_opportunities
    
    async def _scrape_with_error_handling(
        self,
        source_name: str,
        scraper_func,
        keywords,
        location_or_limit,
        limit: int = None
    ):
        """Wrap scraper with error handling"""
        try:
            if limit is not None:
                opportunities = await scraper_func(keywords, location_or_limit, limit)
            else:
                opportunities = await scraper_func(keywords, location_or_limit)
            return (source_name, opportunities)
        except Exception as e:
            logger.error(f"Error scraping {source_name}: {e}")
            return (source_name, [])
    
    async def _scrape_linkedin(self, keywords: str, location: str, limit: int) -> List[Dict]:
        """Scrape LinkedIn jobs"""
        return await scrape_linkedin_jobs(keywords=keywords, location=location, limit=limit)
    
    async def _scrape_indeed(self, keywords: str, location: str, limit: int) -> List[Dict]:
        """Scrape Indeed jobs"""
        return await scrape_indeed_jobs(query=keywords, location=location, limit=limit)
    
    async def _scrape_remoteok(self, keywords: List[str], limit: int) -> List[Dict]:
        """Scrape RemoteOK jobs"""
        return await scrape_remoteok_jobs(tags=keywords, limit=limit)
    
    async def _scrape_wellfound(self, keywords: str, location: str, limit: int) -> List[Dict]:
        """Scrape Wellfound startup jobs"""
        return await scrape_wellfound_jobs(role=keywords, location=location, limit=limit)
    
    async def _scrape_grants(self, keywords: List[str], limit: int) -> List[Dict]:
        """Scrape Grants.gov"""
        return await scrape_grants_gov(keywords=keywords, limit=limit)
    
    def get_high_match_opportunities(self, min_score: float = 70) -> List[Dict]:
        """Get opportunities with high match scores"""
        return [opp for opp in self.scraped_opportunities 
                if opp.get("match_score", 0) >= min_score]
    
    def get_opportunities_by_source(self, source: str) -> List[Dict]:
        """Get opportunities from a specific source"""
        return [opp for opp in self.scraped_opportunities 
                if opp.get("source") == source]
    
    def get_remote_opportunities(self) -> List[Dict]:
        """Get only remote opportunities"""
        return [opp for opp in self.scraped_opportunities 
                if opp.get("remote", False)]
    
    def export_to_json(self, filepath: str):
        """Export opportunities to JSON file"""
        with open(filepath, "w") as f:
            json.dump({
                "opportunities": self.scraped_opportunities,
                "stats": self.stats,
                "exported_at": datetime.utcnow().isoformat()
            }, f, indent=2)


# Convenience function for API
async def scan_opportunities(
    keywords: str = "software engineer",
    limit_per_source: int = 25,
    profile: Optional[Dict] = None
) -> Dict[str, Any]:
    """
    Main entry point for scanning opportunities.
    
    Args:
        keywords: Search keywords
        limit_per_source: Max results per source
        profile: Optional user profile dict for matching
        
    Returns:
        Dict with opportunities and stats
    """
    user_profile = None
    if profile:
        user_profile = UserProfile(**profile)
    
    engine = ScrapingEngine(profile=user_profile)
    return await engine.scan_all_sources(keywords=keywords, limit_per_source=limit_per_source)


if __name__ == "__main__":
    async def test():
        result = await scan_opportunities(
            keywords="python developer",
            limit_per_source=10
        )
        
        print(f"\n{'='*60}")
        print(f"SCAN RESULTS")
        print(f"{'='*60}")
        print(f"Total opportunities: {result['stats']['total_scraped']}")
        print(f"\nBy source:")
        for source, count in result['stats']['by_source'].items():
            print(f"  {source}: {count}")
        
        print(f"\n{'='*60}")
        print(f"TOP 10 MATCHES")
        print(f"{'='*60}")
        for opp in result['opportunities'][:10]:
            print(f"\n{opp['title']} at {opp['company']}")
            print(f"  Match: {opp['match_score']}%")
            print(f"  Source: {opp['source']}")
            print(f"  URL: {opp['apply_url']}")
    
    asyncio.run(test())
