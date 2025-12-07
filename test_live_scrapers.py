"""Test live scrapers"""
import asyncio
import sys
sys.path.insert(0, 'C:/Users/san/Desktop/Accelerator')

from src.scrapers.live_scrapers import (
    scrape_remoteok_live,
    scrape_hackernews_hiring,
    scrape_yc_companies,
    scrape_devpost_hackathons,
    live_mega_scan
)

async def test_individual():
    print("=" * 60)
    print("TESTING INDIVIDUAL SCRAPERS")
    print("=" * 60)
    
    # Test RemoteOK
    print("\n1. Testing RemoteOK...")
    jobs = await scrape_remoteok_live(5)
    print(f"   ✅ RemoteOK: {len(jobs)} jobs")
    if jobs:
        print(f"   Sample: {jobs[0]['title']} at {jobs[0]['company']}")
    
    # Test YC
    print("\n2. Testing Y Combinator...")
    yc = await scrape_yc_companies(5)
    print(f"   ✅ YC: {len(yc)} companies")
    if yc:
        print(f"   Sample: {yc[0]['title']}")
    
    # Test Devpost
    print("\n3. Testing Devpost Hackathons...")
    hacks = await scrape_devpost_hackathons(5)
    print(f"   ✅ Devpost: {len(hacks)} hackathons")
    if hacks:
        print(f"   Sample: {hacks[0]['title']}")
    
    print("\n" + "=" * 60)
    print("INDIVIDUAL TESTS COMPLETE")
    print("=" * 60)

async def test_mega():
    print("\n" + "=" * 60)
    print("TESTING FULL LIVE MEGA SCAN")
    print("=" * 60)
    
    result = await live_mega_scan()
    
    print(f"\n📊 RESULTS:")
    print(f"   Total: {result['stats']['total']} opportunities")
    print(f"   Duration: {result.get('duration_seconds', 0):.1f}s")
    print(f"\n   By Source:")
    for source, count in result['stats']['by_source'].items():
        print(f"     - {source}: {count}")
    print(f"\n   By Type:")
    for type_name, count in result['stats']['by_type'].items():
        print(f"     - {type_name}: {count}")
    
    if result['stats'].get('errors'):
        print(f"\n   Errors:")
        for err in result['stats']['errors']:
            print(f"     ⚠️ {err}")
    
    print("\n   Sample Opportunities:")
    for opp in result['opportunities'][:3]:
        print(f"     📌 {opp['title']}")
        print(f"        Company: {opp['company']}")
        print(f"        Source: {opp['source']}")
        print(f"        URL: {opp['apply_url'][:60]}...")
        print()

if __name__ == "__main__":
    print("🚀 Starting Live Scraper Tests\n")
    asyncio.run(test_individual())
    asyncio.run(test_mega())
    print("\n✅ All tests complete!")
