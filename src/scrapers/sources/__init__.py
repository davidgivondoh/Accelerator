"""
Master Sources Database - 1000+ Opportunity Sources Combined
"""

from .job_boards import JOB_BOARDS, COMPANY_CAREER_PAGES, get_all_job_sources
from .scholarships import SCHOLARSHIPS, FELLOWSHIPS, get_all_scholarship_sources
from .vc_startups import ACCELERATORS, VC_FUNDS, ANGEL_NETWORKS, STARTUP_COMPETITIONS, get_all_vc_sources
from .grants import GOVERNMENT_GRANTS, FOUNDATION_GRANTS, CORPORATE_GRANTS, get_all_grant_sources
from .conferences import TECH_CONFERENCES, ACADEMIC_CONFERENCES, HACKATHONS, PROFESSIONAL_EVENTS, get_all_event_sources
from .african_opportunities import AFRICAN_OPPORTUNITIES, GLOBAL_SOUTH_OPPORTUNITIES, INTERNATIONAL_DEVELOPMENT_ORGS, get_all_african_sources


def get_total_source_count():
    """Get total number of opportunity sources"""
    jobs = get_all_job_sources()
    scholarships = get_all_scholarship_sources()
    vc = get_all_vc_sources()
    grants = get_all_grant_sources()
    events = get_all_event_sources()
    african = get_all_african_sources()
    
    return {
        "jobs": jobs["total"],
        "scholarships": scholarships["total"],
        "vc_startups": vc["total"],
        "grants": grants["total"],
        "events": events["total"],
        "african_global_south": african["total"],
        "GRAND_TOTAL": (
            jobs["total"] + 
            scholarships["total"] + 
            vc["total"] + 
            grants["total"] + 
            events["total"] + 
            african["total"]
        )
    }


def get_all_sources():
    """Get all sources combined"""
    return {
        "jobs": {
            "job_boards": JOB_BOARDS,
            "company_careers": COMPANY_CAREER_PAGES,
        },
        "scholarships": {
            "scholarships": SCHOLARSHIPS,
            "fellowships": FELLOWSHIPS,
        },
        "vc_startups": {
            "accelerators": ACCELERATORS,
            "vc_funds": VC_FUNDS,
            "angel_networks": ANGEL_NETWORKS,
            "competitions": STARTUP_COMPETITIONS,
        },
        "grants": {
            "government": GOVERNMENT_GRANTS,
            "foundations": FOUNDATION_GRANTS,
            "corporate": CORPORATE_GRANTS,
        },
        "events": {
            "tech_conferences": TECH_CONFERENCES,
            "academic_conferences": ACADEMIC_CONFERENCES,
            "hackathons": HACKATHONS,
            "professional_events": PROFESSIONAL_EVENTS,
        },
        "african_global_south": {
            "african": AFRICAN_OPPORTUNITIES,
            "global_south": GLOBAL_SOUTH_OPPORTUNITIES,
            "development_orgs": INTERNATIONAL_DEVELOPMENT_ORGS,
        }
    }


# Quick access to all sources as flat list
ALL_SOURCES = {}
ALL_SOURCES.update(JOB_BOARDS)
ALL_SOURCES.update(COMPANY_CAREER_PAGES)
ALL_SOURCES.update(SCHOLARSHIPS)
ALL_SOURCES.update(FELLOWSHIPS)
ALL_SOURCES.update(ACCELERATORS)
ALL_SOURCES.update(VC_FUNDS)
ALL_SOURCES.update(ANGEL_NETWORKS)
ALL_SOURCES.update(STARTUP_COMPETITIONS)
ALL_SOURCES.update(GOVERNMENT_GRANTS)
ALL_SOURCES.update(FOUNDATION_GRANTS)
ALL_SOURCES.update(CORPORATE_GRANTS)
ALL_SOURCES.update(TECH_CONFERENCES)
ALL_SOURCES.update(ACADEMIC_CONFERENCES)
ALL_SOURCES.update(HACKATHONS)
ALL_SOURCES.update(PROFESSIONAL_EVENTS)
ALL_SOURCES.update(AFRICAN_OPPORTUNITIES)
ALL_SOURCES.update(GLOBAL_SOUTH_OPPORTUNITIES)
ALL_SOURCES.update(INTERNATIONAL_DEVELOPMENT_ORGS)


__all__ = [
    # Job sources
    "JOB_BOARDS",
    "COMPANY_CAREER_PAGES",
    "get_all_job_sources",
    
    # Scholarship sources
    "SCHOLARSHIPS",
    "FELLOWSHIPS",
    "get_all_scholarship_sources",
    
    # VC/Startup sources
    "ACCELERATORS",
    "VC_FUNDS",
    "ANGEL_NETWORKS",
    "STARTUP_COMPETITIONS",
    "get_all_vc_sources",
    
    # Grant sources
    "GOVERNMENT_GRANTS",
    "FOUNDATION_GRANTS",
    "CORPORATE_GRANTS",
    "get_all_grant_sources",
    
    # Event sources
    "TECH_CONFERENCES",
    "ACADEMIC_CONFERENCES",
    "HACKATHONS",
    "PROFESSIONAL_EVENTS",
    "get_all_event_sources",
    
    # African/Global South sources
    "AFRICAN_OPPORTUNITIES",
    "GLOBAL_SOUTH_OPPORTUNITIES",
    "INTERNATIONAL_DEVELOPMENT_ORGS",
    "get_all_african_sources",
    
    # Combined
    "get_total_source_count",
    "get_all_sources",
    "ALL_SOURCES",
]
