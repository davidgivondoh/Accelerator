"""
Mega Scraping Engine
=====================
Comprehensive scraping engine that aggregates 1000+ opportunities per day
from all sources: jobs, scholarships, fellowships, grants, conferences,
VC/startup programs, and African opportunities.
"""

import asyncio
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import json

# Import all scrapers
from .linkedin_scraper import scrape_linkedin_jobs
from .indeed_scraper import scrape_indeed_jobs
from .remoteok_scraper import scrape_remoteok_jobs
from .wellfound_scraper import scrape_wellfound_jobs
from .grants_scraper import scrape_grants_gov

# New comprehensive scrapers
from .african_opportunities_scraper import (
    scrape_all_african_opportunities,
    scrape_opportunities_for_africans,
    scrape_vc4africa,
    scrape_african_leadership
)
from .vc_startup_scraper import (
    scrape_all_vc_opportunities,
    scrape_yc,
    scrape_techstars,
    scrape_vc_funds,
    scrape_angellist
)
from .scholarship_fellowship_scraper import (
    scrape_all_scholarships_and_fellowships,
    scrape_scholarships_com,
    scrape_fastweb,
    scrape_fellowships,
    scrape_international_scholarships
)
from .conference_event_scraper import (
    scrape_all_events_and_conferences,
    scrape_conferences,
    scrape_meetups,
    scrape_eventbrite,
    scrape_hackathons
)

logger = logging.getLogger(__name__)


@dataclass
class ScanConfig:
    """Configuration for mega scanning"""
    # Job sources
    enable_linkedin: bool = True
    enable_indeed: bool = True
    enable_remoteok: bool = True
    enable_wellfound: bool = True
    
    # Government/Grants
    enable_grants: bool = True
    
    # African opportunities
    enable_african: bool = True
    enable_ofa: bool = True
    enable_vc4africa: bool = True
    
    # VC/Startup
    enable_vc: bool = True
    enable_yc: bool = True
    enable_techstars: bool = True
    
    # Scholarships/Fellowships
    enable_scholarships: bool = True
    enable_fellowships: bool = True
    
    # Events
    enable_conferences: bool = True
    enable_hackathons: bool = True
    enable_meetups: bool = True
    
    # Limits
    jobs_per_source: int = 50
    max_pages_per_source: int = 30
    
    # Search keywords (expanded for maximum coverage)
    keywords: List[str] = None
    
    def __post_init__(self):
        if self.keywords is None:
            self.keywords = [
                "software engineer", "developer", "data scientist",
                "machine learning", "product manager", "designer",
                "analyst", "researcher", "founder", "entrepreneur"
            ]


class MegaScrapingEngine:
    """
    Mega scraping engine for 1000+ opportunities per day.
    Aggregates from all available sources globally.
    """
    
    def __init__(self, config: Optional[ScanConfig] = None):
        self.config = config or ScanConfig()
        self.all_opportunities: List[Dict] = []
        self.seen_ids: set = set()
        self.stats = {
            "total": 0,
            "by_category": {},
            "by_source": {},
            "by_type": {},
            "scan_started": None,
            "scan_completed": None,
            "errors": []
        }
    
    async def mega_scan(self) -> Dict[str, Any]:
        """
        Execute comprehensive scan across all sources.
        Target: 1000+ opportunities per scan.
        
        Returns:
            Dict with opportunities and detailed stats
        """
        self.stats["scan_started"] = datetime.utcnow().isoformat()
        logger.info("🚀 Starting MEGA SCAN - Target: 1000+ opportunities")
        
        # Organize tasks by category for parallel execution
        tasks = []
        
        # ============ JOBS ============
        if self.config.enable_linkedin or self.config.enable_indeed or \
           self.config.enable_remoteok or self.config.enable_wellfound:
            tasks.append(("jobs", self._scan_jobs()))
        
        # ============ AFRICAN OPPORTUNITIES ============
        if self.config.enable_african:
            tasks.append(("african", self._scan_african()))
        
        # ============ VC & STARTUP ============
        if self.config.enable_vc:
            tasks.append(("vc_startup", self._scan_vc_startup()))
        
        # ============ SCHOLARSHIPS & FELLOWSHIPS ============
        if self.config.enable_scholarships or self.config.enable_fellowships:
            tasks.append(("education", self._scan_scholarships_fellowships()))
        
        # ============ EVENTS & CONFERENCES ============
        if self.config.enable_conferences or self.config.enable_hackathons:
            tasks.append(("events", self._scan_events()))
        
        # ============ GRANTS ============
        if self.config.enable_grants:
            tasks.append(("grants", self._scan_grants()))
        
        # Execute all categories in parallel
        logger.info(f"📡 Launching {len(tasks)} parallel scan categories...")
        
        async_tasks = [task[1] for task in tasks]
        task_names = [task[0] for task in tasks]
        
        results = await asyncio.gather(*async_tasks, return_exceptions=True)
        
        # Process results
        for i, (name, result) in enumerate(zip(task_names, results)):
            if isinstance(result, Exception):
                logger.error(f"❌ {name} scan failed: {result}")
                self.stats["errors"].append(f"{name}: {str(result)}")
                self.stats["by_category"][name] = 0
            else:
                opportunities = result
                self.stats["by_category"][name] = len(opportunities)
                
                # Add unique opportunities
                for opp in opportunities:
                    opp_id = opp.get("id", str(hash(json.dumps(opp, sort_keys=True, default=str))))
                    if opp_id not in self.seen_ids:
                        self.seen_ids.add(opp_id)
                        self.all_opportunities.append(opp)
                        
                        # Track by source and type
                        source = opp.get("source", "unknown")
                        opp_type = opp.get("opportunity_type", "unknown")
                        
                        self.stats["by_source"][source] = self.stats["by_source"].get(source, 0) + 1
                        self.stats["by_type"][opp_type] = self.stats["by_type"].get(opp_type, 0) + 1
                
                logger.info(f"✅ {name}: {len(opportunities)} opportunities")
        
        # Final stats
        self.stats["total"] = len(self.all_opportunities)
        self.stats["scan_completed"] = datetime.utcnow().isoformat()
        
        logger.info(f"\n{'='*60}")
        logger.info(f"🎯 MEGA SCAN COMPLETE: {self.stats['total']} total opportunities")
        logger.info(f"{'='*60}")
        
        return {
            "opportunities": self.all_opportunities,
            "stats": self.stats,
            "target_reached": self.stats["total"] >= 1000
        }
    
    async def _scan_jobs(self) -> List[Dict]:
        """Scan all job sources"""
        logger.info("📋 Scanning job sources...")
        all_jobs = []
        
        tasks = []
        keywords = " ".join(self.config.keywords[:3])
        limit = self.config.jobs_per_source
        
        if self.config.enable_linkedin:
            for kw in self.config.keywords[:5]:
                tasks.append(scrape_linkedin_jobs(keywords=kw, location="remote", limit=limit//2))
        
        if self.config.enable_indeed:
            for kw in self.config.keywords[:5]:
                tasks.append(scrape_indeed_jobs(query=kw, location="remote", limit=limit//2))
        
        if self.config.enable_remoteok:
            tasks.append(scrape_remoteok_jobs(tags=self.config.keywords[:5], limit=limit))
        
        if self.config.enable_wellfound:
            for kw in self.config.keywords[:3]:
                tasks.append(scrape_wellfound_jobs(role=kw, limit=limit//2))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, list):
                all_jobs.extend(result)
        
        return all_jobs
    
    async def _scan_african(self) -> List[Dict]:
        """Scan African opportunity sources"""
        logger.info("🌍 Scanning African opportunities...")
        return await scrape_all_african_opportunities()
    
    async def _scan_vc_startup(self) -> List[Dict]:
        """Scan VC and startup sources"""
        logger.info("🚀 Scanning VC & startup opportunities...")
        return await scrape_all_vc_opportunities()
    
    async def _scan_scholarships_fellowships(self) -> List[Dict]:
        """Scan scholarship and fellowship sources"""
        logger.info("🎓 Scanning scholarships & fellowships...")
        return await scrape_all_scholarships_and_fellowships()
    
    async def _scan_events(self) -> List[Dict]:
        """Scan events and conferences"""
        logger.info("📅 Scanning events & conferences...")
        return await scrape_all_events_and_conferences()
    
    async def _scan_grants(self) -> List[Dict]:
        """Scan government grants"""
        logger.info("💰 Scanning grants...")
        return await scrape_grants_gov(keywords=self.config.keywords[:5], limit=100)
    
    def get_by_type(self, opportunity_type: str) -> List[Dict]:
        """Get opportunities by type"""
        return [opp for opp in self.all_opportunities 
                if opp.get("opportunity_type") == opportunity_type]
    
    def get_by_source(self, source: str) -> List[Dict]:
        """Get opportunities by source"""
        return [opp for opp in self.all_opportunities 
                if opp.get("source") == source]
    
    def get_scholarships(self) -> List[Dict]:
        """Get all scholarships"""
        return self.get_by_type("scholarship")
    
    def get_fellowships(self) -> List[Dict]:
        """Get all fellowships"""
        return self.get_by_type("fellowship")
    
    def get_grants(self) -> List[Dict]:
        """Get all grants"""
        return self.get_by_type("grant")
    
    def get_jobs(self) -> List[Dict]:
        """Get all jobs"""
        return self.get_by_type("job")
    
    def get_conferences(self) -> List[Dict]:
        """Get all conferences"""
        return self.get_by_type("conference")
    
    def get_hackathons(self) -> List[Dict]:
        """Get all hackathons"""
        return self.get_by_type("hackathon")
    
    def get_african_opportunities(self) -> List[Dict]:
        """Get African-focused opportunities"""
        african_sources = ["OpportunitiesForAfricans", "VC4Africa", "AfricanLeadership"]
        return [opp for opp in self.all_opportunities 
                if opp.get("source") in african_sources or 
                "africa" in str(opp.get("tags", [])).lower()]
    
    def export_to_json(self, filepath: str):
        """Export all opportunities to JSON"""
        with open(filepath, "w") as f:
            json.dump({
                "opportunities": self.all_opportunities,
                "stats": self.stats,
                "exported_at": datetime.utcnow().isoformat()
            }, f, indent=2, default=str)


# Quick scan function for API
async def mega_scan_opportunities(
    keywords: List[str] = None,
    include_jobs: bool = True,
    include_african: bool = True,
    include_scholarships: bool = True,
    include_fellowships: bool = True,
    include_grants: bool = True,
    include_conferences: bool = True,
    include_vc: bool = True
) -> Dict[str, Any]:
    """
    Quick mega scan function.
    
    Args:
        keywords: Search keywords
        include_*: Enable/disable categories
        
    Returns:
        Dict with opportunities and stats
    """
    config = ScanConfig(
        enable_linkedin=include_jobs,
        enable_indeed=include_jobs,
        enable_remoteok=include_jobs,
        enable_wellfound=include_jobs,
        enable_grants=include_grants,
        enable_african=include_african,
        enable_scholarships=include_scholarships,
        enable_fellowships=include_fellowships,
        enable_conferences=include_conferences,
        enable_vc=include_vc,
        keywords=keywords or [
            "software engineer", "data scientist", "product manager",
            "machine learning", "developer", "designer", "analyst"
        ]
    )
    
    engine = MegaScrapingEngine(config)
    return await engine.mega_scan()


# Category-specific scan functions
async def scan_all_scholarships() -> Dict[str, Any]:
    """Scan only scholarships"""
    config = ScanConfig(
        enable_linkedin=False,
        enable_indeed=False,
        enable_remoteok=False,
        enable_wellfound=False,
        enable_grants=False,
        enable_african=True,  # African scholarships
        enable_scholarships=True,
        enable_fellowships=True,
        enable_conferences=False,
        enable_vc=False
    )
    engine = MegaScrapingEngine(config)
    return await engine.mega_scan()


async def scan_all_grants() -> Dict[str, Any]:
    """Scan only grants"""
    config = ScanConfig(
        enable_linkedin=False,
        enable_indeed=False,
        enable_remoteok=False,
        enable_wellfound=False,
        enable_grants=True,
        enable_african=True,  # African grants
        enable_scholarships=False,
        enable_fellowships=False,
        enable_conferences=False,
        enable_vc=True  # VC funding
    )
    engine = MegaScrapingEngine(config)
    return await engine.mega_scan()


async def scan_all_jobs() -> Dict[str, Any]:
    """Scan only jobs"""
    config = ScanConfig(
        enable_linkedin=True,
        enable_indeed=True,
        enable_remoteok=True,
        enable_wellfound=True,
        enable_grants=False,
        enable_african=False,
        enable_scholarships=False,
        enable_fellowships=False,
        enable_conferences=False,
        enable_vc=True  # YC startup jobs
    )
    engine = MegaScrapingEngine(config)
    return await engine.mega_scan()


if __name__ == "__main__":
    async def test_mega_scan():
        """Test the mega scanning engine"""
        print("\n" + "="*70)
        print("🚀 MEGA SCAN TEST")
        print("="*70)
        
        result = await mega_scan_opportunities()
        
        print(f"\n📊 RESULTS:")
        print(f"  Total opportunities: {result['stats']['total']}")
        print(f"  Target (1000+): {'✅ REACHED' if result['target_reached'] else '❌ NOT REACHED'}")
        
        print(f"\n📁 BY CATEGORY:")
        for cat, count in result['stats']['by_category'].items():
            print(f"  {cat}: {count}")
        
        print(f"\n🏷️ BY TYPE:")
        for type_name, count in sorted(result['stats']['by_type'].items(), key=lambda x: -x[1])[:10]:
            print(f"  {type_name}: {count}")
        
        print(f"\n🌐 BY SOURCE (Top 15):")
        for source, count in sorted(result['stats']['by_source'].items(), key=lambda x: -x[1])[:15]:
            print(f"  {source}: {count}")
        
        if result['stats']['errors']:
            print(f"\n⚠️ ERRORS:")
            for error in result['stats']['errors']:
                print(f"  {error}")
        
        # Sample opportunities
        print(f"\n📋 SAMPLE OPPORTUNITIES:")
        for opp in result['opportunities'][:5]:
            print(f"\n  📌 {opp.get('title', 'N/A')}")
            print(f"     Company: {opp.get('company', 'N/A')}")
            print(f"     Type: {opp.get('opportunity_type', 'N/A')}")
            print(f"     Source: {opp.get('source', 'N/A')}")
            print(f"     URL: {opp.get('apply_url', 'N/A')[:60]}...")
    
    asyncio.run(test_mega_scan())
