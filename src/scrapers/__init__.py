# Web Scrapers Module
# Mega Opportunity Engine - 1000+ opportunities/day
# Supports: Jobs, Scholarships, Fellowships, Grants, Conferences, VC/Startup, African Opportunities

from .opportunity_sources import OPPORTUNITY_SOURCES
from .base_scraper import BaseScraper, Opportunity

# Job Scrapers
from .linkedin_scraper import LinkedInScraper, scrape_linkedin_jobs
from .indeed_scraper import IndeedScraper, scrape_indeed_jobs
from .remoteok_scraper import RemoteOKScraper, scrape_remoteok_jobs
from .wellfound_scraper import WellfoundScraper, scrape_wellfound_jobs
from .grants_scraper import GrantsGovScraper, scrape_grants_gov

# African Opportunity Scrapers
from .african_opportunities_scraper import (
    OpportunitiesForAfricansScraper,
    VC4AfricaScraper,
    AfricanLeadershipScraper,
    scrape_all_african_opportunities,
    scrape_opportunities_for_africans,
    scrape_vc4africa,
    scrape_african_leadership,
)

# VC & Startup Scrapers
from .vc_startup_scraper import (
    YCombinatorScraper,
    TechstarsScraper,
    VCFundsScraper,
    AngelListScraper,
    scrape_all_vc_opportunities,
    scrape_yc,
    scrape_techstars,
    scrape_vc_funds,
    scrape_angellist,
)

# Scholarship & Fellowship Scrapers
from .scholarship_fellowship_scraper import (
    ScholarshipsComScraper,
    FastwedScraper,
    FellowshipsScraper,
    InternationalScholarshipsScraper,
    scrape_all_scholarships_and_fellowships,
    scrape_scholarships_com,
    scrape_fastweb,
    scrape_fellowships,
    scrape_international_scholarships,
)

# Conference & Event Scrapers
from .conference_event_scraper import (
    ConferenceScraper,
    MeetupScraper,
    EventbriteScraper,
    HackathonScraper,
    scrape_all_events_and_conferences,
    scrape_conferences,
    scrape_meetups,
    scrape_eventbrite,
    scrape_hackathons,
)

# Scraping Engines
from .scraping_engine import ScrapingEngine, scan_opportunities
from .mega_scraping_engine import (
    MegaScrapingEngine,
    ScanConfig,
    mega_scan_opportunities,
    scan_all_scholarships,
    scan_all_grants,
    scan_all_jobs,
)

# Fast Demo Engine for instant results
from .fast_demo_engine import fast_demo_scan, demo_mega_scan

# Utilities and health monitoring
from .utils import (
    safe_request,
    safe_json_request,
    retry_on_failure,
    RateLimiter,
    run_scrapers_safely,
)
from .base_scraper import (
    get_scraper_metrics,
    get_all_scraper_health,
    ScraperStatus,
    ScraperMetrics,
)

__all__ = [
    # Base
    "OPPORTUNITY_SOURCES",
    "BaseScraper",
    "Opportunity",
    
    # Job Scrapers
    "LinkedInScraper",
    "IndeedScraper",
    "RemoteOKScraper",
    "WellfoundScraper",
    "GrantsGovScraper",
    "scrape_linkedin_jobs",
    "scrape_indeed_jobs",
    "scrape_remoteok_jobs",
    "scrape_wellfound_jobs",
    "scrape_grants_gov",
    
    # African Scrapers
    "OpportunitiesForAfricansScraper",
    "VC4AfricaScraper",
    "AfricanLeadershipScraper",
    "scrape_all_african_opportunities",
    "scrape_opportunities_for_africans",
    "scrape_vc4africa",
    "scrape_african_leadership",
    
    # VC & Startup Scrapers
    "YCombinatorScraper",
    "TechstarsScraper",
    "VCFundsScraper",
    "AngelListScraper",
    "scrape_all_vc_opportunities",
    "scrape_yc",
    "scrape_techstars",
    "scrape_vc_funds",
    "scrape_angellist",
    
    # Scholarship & Fellowship Scrapers
    "ScholarshipsComScraper",
    "FastwedScraper",
    "FellowshipsScraper",
    "InternationalScholarshipsScraper",
    "scrape_all_scholarships_and_fellowships",
    "scrape_scholarships_com",
    "scrape_fastweb",
    "scrape_fellowships",
    "scrape_international_scholarships",
    
    # Conference & Event Scrapers
    "ConferenceScraper",
    "MeetupScraper",
    "EventbriteScraper",
    "HackathonScraper",
    "scrape_all_events_and_conferences",
    "scrape_conferences",
    "scrape_meetups",
    "scrape_eventbrite",
    "scrape_hackathons",
    
    # Engines
    "ScrapingEngine",
    "MegaScrapingEngine",
    "ScanConfig",
    "scan_opportunities",
    "mega_scan_opportunities",
    "scan_all_scholarships",
    "scan_all_grants",
    "scan_all_jobs",
    
    # Fast Demo Engine
    "fast_demo_scan",
    "demo_mega_scan",
    
    # Utilities & Health Monitoring
    "safe_request",
    "safe_json_request",
    "retry_on_failure",
    "RateLimiter",
    "run_scrapers_safely",
    "get_scraper_metrics",
    "get_all_scraper_health",
    "ScraperStatus",
    "ScraperMetrics",
]
