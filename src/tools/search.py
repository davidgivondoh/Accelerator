"""
ADK Tools for opportunity discovery.

Contains FunctionTools for searching and scraping opportunities.
"""

import json
from datetime import datetime
from typing import Any

from google.adk.tools import FunctionTool

from src.models import Opportunity, OpportunityCreate, OpportunityType, SourceType


async def search_opportunities(
    query: str,
    opportunity_type: str = "job",
    location: str | None = None,
    remote_only: bool = False,
    max_results: int = 20,
) -> dict[str, Any]:
    """
    Search for opportunities using Google Search.
    
    Args:
        query: Search query (e.g., "AI Research Scientist", "climate tech grants")
        opportunity_type: Type of opportunity (job, fellowship, grant, accelerator, scholarship, research)
        location: Location filter (e.g., "San Francisco", "Remote")
        remote_only: Only return remote opportunities
        max_results: Maximum number of results to return
        
    Returns:
        Dictionary with search results containing opportunities
    """
    # Build search query
    search_parts = [query]
    
    # Add opportunity type context
    type_keywords = {
        "job": "job posting careers hiring",
        "fellowship": "fellowship program application",
        "grant": "grant funding application deadline",
        "accelerator": "accelerator program startup application",
        "scholarship": "scholarship application deadline",
        "research": "research position postdoc lab",
    }
    search_parts.append(type_keywords.get(opportunity_type, ""))
    
    if location:
        search_parts.append(location)
    if remote_only:
        search_parts.append("remote")
    
    full_query = " ".join(search_parts)
    
    # NOTE: In production, this would call google_search or brave_search
    # For now, return mock structure that shows expected output format
    return {
        "query": full_query,
        "opportunity_type": opportunity_type,
        "results_count": 0,
        "results": [],
        "message": "Search executed. In production, integrate with google_search tool or web scraping.",
        "timestamp": datetime.utcnow().isoformat(),
    }


async def scrape_opportunity_page(
    url: str,
    opportunity_type: str = "job",
) -> dict[str, Any]:
    """
    Scrape detailed information from an opportunity page.
    
    Args:
        url: URL of the opportunity posting to scrape
        opportunity_type: Expected type of opportunity
        
    Returns:
        Structured opportunity data extracted from the page
    """
    # NOTE: In production, use Playwright or BeautifulSoup
    # This is the expected output structure
    return {
        "url": url,
        "opportunity_type": opportunity_type,
        "extracted": False,
        "data": None,
        "message": "Scraping not yet implemented. Use Playwright for dynamic pages.",
        "timestamp": datetime.utcnow().isoformat(),
    }


async def parse_opportunity(
    raw_data: dict[str, Any],
    source: str = "manual",
) -> dict[str, Any]:
    """
    Parse raw opportunity data into structured format.
    
    Args:
        raw_data: Raw data from search or scraping
        source: Source of the opportunity
        
    Returns:
        Parsed opportunity in standard format
    """
    # Extract and normalize fields
    title = raw_data.get("title", "Unknown Title")
    organization = raw_data.get("company") or raw_data.get("organization", "Unknown")
    description = raw_data.get("description", "")
    url = raw_data.get("url", "")
    
    # Determine opportunity type from content
    opp_type = raw_data.get("opportunity_type", "job")
    
    # Parse deadline if present
    deadline = raw_data.get("deadline")
    if deadline and isinstance(deadline, str):
        try:
            deadline = datetime.fromisoformat(deadline)
        except ValueError:
            deadline = None
    
    opportunity = OpportunityCreate(
        title=title,
        organization=organization,
        description=description,
        opportunity_type=OpportunityType(opp_type) if opp_type in OpportunityType.__members__.values() else OpportunityType.OTHER,
        url=url,
        source=SourceType(source) if source in SourceType.__members__.values() else SourceType.CUSTOM,
        location=raw_data.get("location"),
        is_remote=raw_data.get("remote", False),
        deadline=deadline,
        raw_data=raw_data,
    )
    
    return opportunity.model_dump(mode="json")


async def filter_opportunities(
    opportunities: list[dict[str, Any]],
    min_match_score: float = 0.5,
    exclude_expired: bool = True,
    exclude_duplicates: bool = True,
) -> dict[str, Any]:
    """
    Filter a list of opportunities based on criteria.
    
    Args:
        opportunities: List of opportunity dictionaries
        min_match_score: Minimum match score to include (0-1)
        exclude_expired: Remove opportunities past deadline
        exclude_duplicates: Remove duplicate opportunities
        
    Returns:
        Filtered list of opportunities with stats
    """
    filtered = []
    removed_expired = 0
    removed_duplicates = 0
    removed_low_score = 0
    
    seen_urls = set()
    now = datetime.utcnow()
    
    for opp in opportunities:
        # Check expiration
        if exclude_expired:
            deadline = opp.get("deadline")
            if deadline:
                try:
                    if isinstance(deadline, str):
                        deadline = datetime.fromisoformat(deadline)
                    if deadline < now:
                        removed_expired += 1
                        continue
                except (ValueError, TypeError):
                    pass
        
        # Check duplicates
        if exclude_duplicates:
            url = opp.get("url", "")
            if url in seen_urls:
                removed_duplicates += 1
                continue
            seen_urls.add(url)
        
        # Check match score
        score = opp.get("fit_score") or opp.get("score", {}).get("fit_score", 1.0)
        if score < min_match_score:
            removed_low_score += 1
            continue
        
        filtered.append(opp)
    
    return {
        "original_count": len(opportunities),
        "filtered_count": len(filtered),
        "removed_expired": removed_expired,
        "removed_duplicates": removed_duplicates,
        "removed_low_score": removed_low_score,
        "opportunities": filtered,
    }


async def store_opportunities(
    opportunities: list[dict[str, Any]],
    batch_id: str | None = None,
) -> dict[str, Any]:
    """
    Store opportunities to the database.
    
    Args:
        opportunities: List of opportunities to store
        batch_id: Optional batch identifier for grouping
        
    Returns:
        Storage result with counts and IDs
    """
    # NOTE: In production, this would insert into Supabase
    stored_ids = []
    
    for i, opp in enumerate(opportunities):
        # Generate a mock ID
        opp_id = f"opp_{batch_id or 'manual'}_{i}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        stored_ids.append(opp_id)
    
    return {
        "success": True,
        "batch_id": batch_id,
        "stored_count": len(opportunities),
        "opportunity_ids": stored_ids,
        "message": "Storage simulated. Connect Supabase for persistence.",
        "timestamp": datetime.utcnow().isoformat(),
    }


# Create ADK FunctionTools
search_opportunities_tool = FunctionTool(func=search_opportunities)
scrape_opportunity_tool = FunctionTool(func=scrape_opportunity_page)
parse_opportunity_tool = FunctionTool(func=parse_opportunity)
filter_opportunities_tool = FunctionTool(func=filter_opportunities)
store_opportunities_tool = FunctionTool(func=store_opportunities)

# Export all tools
discovery_tools = [
    search_opportunities_tool,
    scrape_opportunity_tool,
    parse_opportunity_tool,
    filter_opportunities_tool,
    store_opportunities_tool,
]
