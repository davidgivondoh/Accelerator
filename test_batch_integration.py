"""
Test live_scrapers batch integration including scholarships
"""
import asyncio
import sys
import os

# Add the project root to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

async def test_batch_integration():
    """Test the batch system that includes scholarships"""
    print("🎯 Testing Live Scrapers Batch Integration")
    print("=" * 60)
    
    try:
        from src.scrapers.live_scrapers import SCRAPER_BATCHES
        
        # Find the batch that contains scholarships
        scholarship_batch = None
        for batch_id, batch_info in SCRAPER_BATCHES.items():
            scrapers = batch_info.get("scrapers", [])
            for scraper_name, scraper_func in scrapers:
                if "Scholarships" in scraper_name:
                    scholarship_batch = (batch_id, batch_info)
                    break
            if scholarship_batch:
                break
        
        if scholarship_batch:
            batch_id, batch_info = scholarship_batch
            print(f"✅ Found scholarships in batch {batch_id}: {batch_info['name']}")
            print(f"📝 Description: {batch_info['description']}")
            print(f"📊 Category: {batch_info['category']}")
            print(f"🔢 Sources: {batch_info['estimated_sources']}")
            
            print(f"\n📋 Scrapers in this batch:")
            for i, (scraper_name, scraper_func) in enumerate(batch_info["scrapers"]):
                print(f"   {i+1}. {scraper_name}")
            
            # Test just the scholarship scraper function
            print(f"\n🧪 Testing Scholarship scraper function...")
            scholarship_func = None
            for scraper_name, scraper_func in batch_info["scrapers"]:
                if "Scholarships" in scraper_name:
                    scholarship_func = scraper_func
                    break
            
            if scholarship_func:
                try:
                    results = await scholarship_func()
                    print(f"✅ Scholarship function returned {len(results)} opportunities")
                    
                    if results:
                        print(f"📋 Sample scholarship opportunities:")
                        for i, opp in enumerate(results[:3]):
                            title = opp.get('title', 'Unknown')
                            company = opp.get('company', 'Unknown')
                            region = opp.get('region', 'global')
                            print(f"   {i+1}. {title} ({company}) - {region}")
                except Exception as e:
                    print(f"❌ Error testing scholarship function: {e}")
            
        else:
            print("❌ Could not find scholarships in any batch")
        
        print(f"\n🎯 Batch integration test completed!")
        
    except Exception as e:
        print(f"❌ Batch test error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_batch_integration())