"""
Test specific accelerator scraping
"""
import asyncio
import sys
import os

# Add the project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

async def test_specific_accelerator():
    try:
        from src.scrapers.accelerator_scraper import AcceleratorScraper
        from src.scrapers.opportunity_sources import OPPORTUNITY_SOURCES
        
        # Get Y Combinator config
        ycombinator_config = OPPORTUNITY_SOURCES['accelerators']['ycombinator']
        print(f"Testing scraper with Y Combinator: {ycombinator_config['name']}")
        print(f"URL: {ycombinator_config['url']}")
        print(f"Type: {ycombinator_config['type']}")
        
        # Use the scraper as an async context manager
        async with AcceleratorScraper() as scraper:
            # Test scraping Y Combinator
            opportunities = await scraper.scrape_single_accelerator(ycombinator_config)
        
        print(f"Found {len(opportunities)} opportunities")
        
        if opportunities:
            for opp in opportunities:
                print(f"- {opp.title}")
                print(f"  Company: {opp.company}")
                print(f"  Location: {opp.location}")
                print(f"  Type: {opp.opportunity_type}")
                print(f"  URL: {opp.url}")
                print()
        else:
            print("No opportunities found (this might be expected for live scraping)")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_specific_accelerator())