"""
Fast Demo Scraping Engine
=========================
Generates realistic opportunities from our 1,337 sources database
for instant UI response while real scrapers run in background.
"""

import asyncio
import random
import hashlib
from datetime import datetime, timedelta
from typing import List, Dict, Any
import logging

# Import source databases
from .sources import (
    JOB_BOARDS, COMPANY_CAREER_PAGES,
    SCHOLARSHIPS, FELLOWSHIPS,
    ACCELERATORS, VC_FUNDS, ANGEL_NETWORKS, STARTUP_COMPETITIONS,
    GOVERNMENT_GRANTS, FOUNDATION_GRANTS, CORPORATE_GRANTS,
    TECH_CONFERENCES, ACADEMIC_CONFERENCES, HACKATHONS, PROFESSIONAL_EVENTS,
    AFRICAN_OPPORTUNITIES, GLOBAL_SOUTH_OPPORTUNITIES, INTERNATIONAL_DEVELOPMENT_ORGS,
    get_total_source_count
)

logger = logging.getLogger(__name__)

# Job titles by industry
JOB_TITLES = {
    "tech": [
        "Senior Software Engineer", "Staff Engineer", "Principal Engineer",
        "Machine Learning Engineer", "Data Scientist", "AI Research Scientist",
        "Full Stack Developer", "Backend Engineer", "Frontend Developer",
        "DevOps Engineer", "Site Reliability Engineer", "Cloud Architect",
        "Product Manager", "Technical Product Manager", "Engineering Manager",
        "VP of Engineering", "CTO", "Director of Engineering",
        "Security Engineer", "Blockchain Developer", "Mobile Developer",
        "iOS Developer", "Android Developer", "React Native Developer",
    ],
    "startup": [
        "Founding Engineer", "Head of Engineering", "First Engineer",
        "Co-Founder (Technical)", "Startup CTO", "Growth Engineer",
    ],
    "research": [
        "Research Scientist", "Research Engineer", "Applied Scientist",
        "PhD Researcher", "Postdoctoral Fellow", "Research Intern",
    ],
}

SCHOLARSHIP_TITLES = [
    "Full Scholarship for Master's Degree",
    "PhD Fellowship - Full Funding",
    "Undergraduate Scholarship",
    "STEM Excellence Award",
    "Women in Tech Scholarship",
    "Emerging Leaders Fellowship",
    "International Student Grant",
    "Research Excellence Award",
    "Innovation Scholarship",
    "Future Leaders Program",
    "Academic Merit Scholarship",
    "Graduate Research Fellowship",
    "Doctoral Research Grant",
    "Professional Development Award",
    "Leadership Development Fellowship",
]

GRANT_TITLES = [
    "Research Innovation Grant",
    "Small Business Development Grant",
    "Technology Commercialization Grant",
    "Scientific Research Funding",
    "Innovation Challenge Grant",
    "Community Development Grant",
    "Entrepreneurship Support Grant",
    "Clean Technology Grant",
    "AI/ML Research Grant",
    "Healthcare Innovation Grant",
    "Education Technology Grant",
    "Social Impact Grant",
]

CONFERENCE_TITLES = [
    "Annual Tech Summit",
    "Developer Conference",
    "AI & ML Conference",
    "Startup Week",
    "Innovation Forum",
    "Tech Meetup",
    "Industry Summit",
    "Professional Conference",
    "Research Symposium",
    "Global Tech Week",
]

LOCATIONS = [
    "Remote", "San Francisco, CA", "New York, NY", "Austin, TX",
    "Seattle, WA", "Boston, MA", "Los Angeles, CA", "Chicago, IL",
    "London, UK", "Berlin, Germany", "Amsterdam, Netherlands",
    "Singapore", "Sydney, Australia", "Toronto, Canada",
    "Nairobi, Kenya", "Lagos, Nigeria", "Cape Town, South Africa",
    "Dubai, UAE", "Tel Aviv, Israel", "Bangalore, India",
]

SALARIES = [
    "$80,000 - $120,000", "$100,000 - $150,000", "$120,000 - $180,000",
    "$150,000 - $220,000", "$180,000 - $280,000", "$200,000 - $350,000",
    "Competitive", "Equity + Salary", "Market Rate",
]

FUNDING_AMOUNTS = [
    "$5,000", "$10,000", "$25,000", "$50,000", "$75,000",
    "$100,000", "$150,000", "$250,000", "$500,000", "$1,000,000",
    "Full Tuition", "Full Funding + Stipend", "Variable",
]


def generate_id(source: str, title: str) -> str:
    """Generate unique ID"""
    content = f"{source}_{title}_{datetime.utcnow().isoformat()}"
    return hashlib.md5(content.encode()).hexdigest()[:16]


def random_deadline() -> datetime:
    """Generate random deadline within next 3 months"""
    days = random.randint(7, 90)
    return datetime.utcnow() + timedelta(days=days)


def generate_job_opportunity(source_name: str, source_data: dict) -> Dict[str, Any]:
    """Generate a job opportunity from a source"""
    title = random.choice(JOB_TITLES["tech"] + JOB_TITLES["startup"])
    location = random.choice(LOCATIONS)
    
    return {
        "id": generate_id(source_name, title),
        "title": title,
        "company": source_data.get("name", source_name),
        "location": location,
        "description": source_data.get("description", f"Exciting opportunity at {source_name}"),
        "apply_url": source_data.get("url", f"https://{source_name.lower().replace(' ', '')}.com/careers"),
        "source": source_name,
        "opportunity_type": "job",
        "salary": random.choice(SALARIES),
        "remote": "Remote" in location,
        "deadline": random_deadline().isoformat(),
        "tags": source_data.get("categories", ["technology", "engineering"]),
        "match_score": random.randint(70, 99),
        "scraped_at": datetime.utcnow().isoformat(),
    }


def generate_scholarship_opportunity(source_name: str, source_data: dict) -> Dict[str, Any]:
    """Generate a scholarship/fellowship opportunity"""
    title = random.choice(SCHOLARSHIP_TITLES)
    
    return {
        "id": generate_id(source_name, title),
        "title": f"{source_name} - {title}",
        "company": source_data.get("name", source_name),
        "location": "International",
        "description": source_data.get("description", f"Prestigious scholarship program from {source_name}"),
        "apply_url": source_data.get("url", f"https://{source_name.lower().replace(' ', '')}.org"),
        "source": source_name,
        "opportunity_type": "scholarship" if "Fellowship" not in title else "fellowship",
        "funding": random.choice(FUNDING_AMOUNTS),
        "remote": True,
        "deadline": random_deadline().isoformat(),
        "tags": source_data.get("categories", ["education", "scholarship"]),
        "match_score": random.randint(65, 95),
        "scraped_at": datetime.utcnow().isoformat(),
    }


def generate_grant_opportunity(source_name: str, source_data: dict) -> Dict[str, Any]:
    """Generate a grant opportunity"""
    title = random.choice(GRANT_TITLES)
    
    return {
        "id": generate_id(source_name, title),
        "title": f"{source_name} - {title}",
        "company": source_data.get("name", source_name),
        "location": "Various",
        "description": source_data.get("description", f"Funding opportunity from {source_name}"),
        "apply_url": source_data.get("url", f"https://{source_name.lower().replace(' ', '')}.gov"),
        "source": source_name,
        "opportunity_type": "grant",
        "funding": random.choice(FUNDING_AMOUNTS),
        "remote": True,
        "deadline": random_deadline().isoformat(),
        "tags": source_data.get("categories", ["funding", "grants"]),
        "match_score": random.randint(60, 90),
        "scraped_at": datetime.utcnow().isoformat(),
    }


def generate_vc_opportunity(source_name: str, source_data: dict) -> Dict[str, Any]:
    """Generate a VC/accelerator opportunity"""
    opp_types = ["accelerator", "funding", "program", "competition"]
    opp_type = random.choice(opp_types)
    
    titles = {
        "accelerator": f"{source_name} Accelerator Program",
        "funding": f"{source_name} Seed Funding",
        "program": f"{source_name} Startup Program",
        "competition": f"{source_name} Pitch Competition",
    }
    
    return {
        "id": generate_id(source_name, titles[opp_type]),
        "title": titles[opp_type],
        "company": source_data.get("name", source_name),
        "location": random.choice(LOCATIONS[:10]),
        "description": source_data.get("description", f"Startup opportunity from {source_name}"),
        "apply_url": source_data.get("url", f"https://{source_name.lower().replace(' ', '')}.com"),
        "source": source_name,
        "opportunity_type": opp_type,
        "funding": random.choice(["$50K - $150K", "$100K - $500K", "$500K - $2M", "Up to $1M"]),
        "remote": random.choice([True, False]),
        "deadline": random_deadline().isoformat(),
        "tags": source_data.get("categories", ["startup", "funding", "accelerator"]),
        "match_score": random.randint(70, 98),
        "scraped_at": datetime.utcnow().isoformat(),
    }


def generate_event_opportunity(source_name: str, source_data: dict) -> Dict[str, Any]:
    """Generate a conference/event opportunity"""
    title = random.choice(CONFERENCE_TITLES)
    event_type = random.choice(["conference", "hackathon", "meetup", "workshop"])
    
    return {
        "id": generate_id(source_name, title),
        "title": f"{source_name} {title}",
        "company": source_data.get("name", source_name),
        "location": random.choice(LOCATIONS),
        "description": source_data.get("description", f"Event from {source_name}"),
        "apply_url": source_data.get("url", f"https://{source_name.lower().replace(' ', '')}.com"),
        "source": source_name,
        "opportunity_type": event_type,
        "remote": random.choice([True, False]),
        "deadline": random_deadline().isoformat(),
        "tags": source_data.get("categories", ["events", event_type]),
        "match_score": random.randint(60, 95),
        "scraped_at": datetime.utcnow().isoformat(),
    }


def generate_african_opportunity(source_name: str, source_data: dict) -> Dict[str, Any]:
    """Generate an African-focused opportunity"""
    opp_types = ["scholarship", "fellowship", "grant", "job", "accelerator", "competition"]
    opp_type = random.choice(opp_types)
    
    african_locations = [
        "Africa-wide", "Kenya", "Nigeria", "South Africa", "Ghana",
        "Rwanda", "Egypt", "Morocco", "Ethiopia", "Tanzania"
    ]
    
    return {
        "id": generate_id(source_name, f"African {opp_type}"),
        "title": f"{source_name} - {opp_type.title()} for Africans",
        "company": source_data.get("name", source_name),
        "location": random.choice(african_locations),
        "description": source_data.get("description", f"Opportunity for Africans from {source_name}"),
        "apply_url": source_data.get("url", f"https://{source_name.lower().replace(' ', '')}.org"),
        "source": source_name,
        "opportunity_type": opp_type,
        "funding": random.choice(FUNDING_AMOUNTS) if opp_type in ["scholarship", "fellowship", "grant"] else None,
        "remote": True,
        "deadline": random_deadline().isoformat(),
        "tags": ["africa", opp_type] + source_data.get("categories", []),
        "match_score": random.randint(75, 99),
        "scraped_at": datetime.utcnow().isoformat(),
    }


async def fast_demo_scan(
    limit_per_category: int = 100,
    include_jobs: bool = True,
    include_scholarships: bool = True,
    include_grants: bool = True,
    include_vc: bool = True,
    include_events: bool = True,
    include_african: bool = True,
) -> Dict[str, Any]:
    """
    Fast demo scan that instantly generates opportunities from all 1,337 sources.
    
    Returns immediately with realistic data for UI demonstration.
    """
    logger.info("🚀 Starting FAST DEMO SCAN from 1,337 sources...")
    
    start_time = datetime.utcnow()
    opportunities = []
    stats = {
        "total": 0,
        "by_category": {},
        "by_type": {},
        "by_source": {},
        "scan_started": start_time.isoformat(),
        "scan_completed": None,
        "errors": []
    }
    
    # Generate from each source category
    if include_jobs:
        job_opps = []
        all_job_sources = {**JOB_BOARDS, **COMPANY_CAREER_PAGES}
        for source_name, source_data in list(all_job_sources.items())[:limit_per_category]:
            try:
                opp = generate_job_opportunity(source_name, source_data)
                job_opps.append(opp)
            except Exception as e:
                logger.error(f"Error generating job from {source_name}: {e}")
        
        opportunities.extend(job_opps)
        stats["by_category"]["jobs"] = len(job_opps)
        logger.info(f"✅ Jobs: {len(job_opps)} opportunities")
    
    if include_scholarships:
        edu_opps = []
        all_edu_sources = {**SCHOLARSHIPS, **FELLOWSHIPS}
        for source_name, source_data in list(all_edu_sources.items())[:limit_per_category]:
            try:
                opp = generate_scholarship_opportunity(source_name, source_data)
                edu_opps.append(opp)
            except Exception as e:
                logger.error(f"Error generating scholarship from {source_name}: {e}")
        
        opportunities.extend(edu_opps)
        stats["by_category"]["education"] = len(edu_opps)
        logger.info(f"✅ Scholarships/Fellowships: {len(edu_opps)} opportunities")
    
    if include_grants:
        grant_opps = []
        all_grant_sources = {**GOVERNMENT_GRANTS, **FOUNDATION_GRANTS, **CORPORATE_GRANTS}
        for source_name, source_data in list(all_grant_sources.items())[:limit_per_category]:
            try:
                opp = generate_grant_opportunity(source_name, source_data)
                grant_opps.append(opp)
            except Exception as e:
                logger.error(f"Error generating grant from {source_name}: {e}")
        
        opportunities.extend(grant_opps)
        stats["by_category"]["grants"] = len(grant_opps)
        logger.info(f"✅ Grants: {len(grant_opps)} opportunities")
    
    if include_vc:
        vc_opps = []
        all_vc_sources = {**ACCELERATORS, **VC_FUNDS, **ANGEL_NETWORKS, **STARTUP_COMPETITIONS}
        for source_name, source_data in list(all_vc_sources.items())[:limit_per_category]:
            try:
                opp = generate_vc_opportunity(source_name, source_data)
                vc_opps.append(opp)
            except Exception as e:
                logger.error(f"Error generating VC opp from {source_name}: {e}")
        
        opportunities.extend(vc_opps)
        stats["by_category"]["vc_startup"] = len(vc_opps)
        logger.info(f"✅ VC/Startups: {len(vc_opps)} opportunities")
    
    if include_events:
        event_opps = []
        all_event_sources = {**TECH_CONFERENCES, **ACADEMIC_CONFERENCES, **HACKATHONS, **PROFESSIONAL_EVENTS}
        for source_name, source_data in list(all_event_sources.items())[:limit_per_category]:
            try:
                opp = generate_event_opportunity(source_name, source_data)
                event_opps.append(opp)
            except Exception as e:
                logger.error(f"Error generating event from {source_name}: {e}")
        
        opportunities.extend(event_opps)
        stats["by_category"]["events"] = len(event_opps)
        logger.info(f"✅ Events: {len(event_opps)} opportunities")
    
    if include_african:
        african_opps = []
        all_african_sources = {**AFRICAN_OPPORTUNITIES, **GLOBAL_SOUTH_OPPORTUNITIES, **INTERNATIONAL_DEVELOPMENT_ORGS}
        for source_name, source_data in list(all_african_sources.items())[:limit_per_category]:
            try:
                opp = generate_african_opportunity(source_name, source_data)
                african_opps.append(opp)
            except Exception as e:
                logger.error(f"Error generating African opp from {source_name}: {e}")
        
        opportunities.extend(african_opps)
        stats["by_category"]["african"] = len(african_opps)
        logger.info(f"✅ African/Global South: {len(african_opps)} opportunities")
    
    # Aggregate stats
    for opp in opportunities:
        opp_type = opp.get("opportunity_type", "unknown")
        source = opp.get("source", "unknown")
        
        stats["by_type"][opp_type] = stats["by_type"].get(opp_type, 0) + 1
        stats["by_source"][source] = stats["by_source"].get(source, 0) + 1
    
    stats["total"] = len(opportunities)
    stats["scan_completed"] = datetime.utcnow().isoformat()
    
    # Add source count info
    source_counts = get_total_source_count()
    
    logger.info(f"\n{'='*60}")
    logger.info(f"🎯 FAST DEMO SCAN COMPLETE: {stats['total']} opportunities generated")
    logger.info(f"📊 From {source_counts['GRAND_TOTAL']} total sources")
    logger.info(f"{'='*60}")
    
    # Sort by match score
    opportunities.sort(key=lambda x: x.get("match_score", 0), reverse=True)
    
    return {
        "opportunities": opportunities,
        "stats": stats,
        "source_counts": source_counts,
        "target_reached": stats["total"] >= 100
    }


# Quick async wrapper for API
async def demo_mega_scan(**kwargs) -> Dict[str, Any]:
    """Wrapper for fast demo scan"""
    return await fast_demo_scan(**kwargs)
