"""
Test comprehensive accelerator scraper
"""
import asyncio
import sys
sys.path.append('src')

from scrapers.live_scrapers import scrape_startup_accelerators_comprehensive

async def test_accelerators():
    print("🚀 Testing Comprehensive Accelerator Scraper")
    print("=" * 50)
    
    try:
        result = await scrape_startup_accelerators_comprehensive(15)
        print(f"✅ Scraper working: {len(result)} opportunities")
        
        if result:
            print("\n📋 Sample accelerator opportunities:")
            for i, opp in enumerate(result[:5]):
                title = opp.get('title', 'Unknown')
                tier = opp.get('tier', 'unknown')
                funding = opp.get('funding', 'varies')
                print(f"  {i+1}. {title} - {tier} - {funding}")
        
        print(f"\n🎯 Test completed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_accelerators())