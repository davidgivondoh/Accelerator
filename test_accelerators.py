"""
Test the accelerator scraper integration
"""
import asyncio
import sys
import os

# Add the project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

async def test_accelerator_scraper():
    try:
        # Test the comprehensive accelerator scraper
        from src.scrapers.live_scrapers import scrape_startup_accelerators_comprehensive
        
        print("Testing comprehensive accelerator scraper...")
        opportunities = await scrape_startup_accelerators_comprehensive(limit=10)
        
        print(f"Found {len(opportunities)} opportunities")
        
        if opportunities:
            print("\nSample opportunities:")
            for i, opp in enumerate(opportunities[:3]):
                title = opp.get('title', 'No title')
                company = opp.get('company', 'No company')
                tier = opp.get('tier', 'unknown')
                opportunity_type = opp.get('opportunity_type', 'unknown')
                print(f"{i+1}. {title}")
                print(f"   Company: {company}")
                print(f"   Type: {opportunity_type}")
                print(f"   Tier: {tier}")
                print()
        else:
            print("No opportunities found")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_accelerator_scraper())