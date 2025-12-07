"""
Test comprehensive scholarship scraping within the proper package structure
"""
import asyncio
import sys
import os

# Add the project root to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

async def test_in_package():
    """Test the scholarship scraper within proper package structure"""
    print("🎓 Testing Scholarship Integration in Package")
    print("=" * 60)
    
    try:
        # Test importing the components
        from src.scrapers.opportunity_sources import OPPORTUNITY_SOURCES
        from src.scrapers.scholarship_fellowship_scraper import ScholarshipScraper
        
        print("✅ Successfully imported scholarship components")
        
        # Check scholarship sources
        scholarships = OPPORTUNITY_SOURCES.get("scholarships", {})
        print(f"📊 Found {len(scholarships)} scholarship sources configured")
        
        # Show some tier 1 scholarships
        tier1_scholarships = [(name, config) for name, config in scholarships.items() 
                            if config.get('tier') == 'tier1']
        print(f"🏆 Tier 1 scholarships: {len(tier1_scholarships)}")
        
        # Show sample tier 1 scholarships
        for i, (name, config) in enumerate(tier1_scholarships[:5]):
            print(f"   {i+1}. {config['name']} - {config.get('region', 'global')} - {config.get('award', 'varies')}")
        
        # Show platform sources
        platform_scholarships = [(name, config) for name, config in scholarships.items() 
                                if config.get('tier') == 'platform']
        print(f"🌐 Platform sources: {len(platform_scholarships)}")
        
        for i, (name, config) in enumerate(platform_scholarships[:3]):
            print(f"   {i+1}. {config['name']} - {config.get('volume', 'medium')} volume")
        
        # Test scraper initialization (without async context)
        scraper = ScholarshipScraper()
        print("✅ ScholarshipScraper initialized successfully")
        
        print(f"\n🎯 Package integration test completed successfully!")
        
    except Exception as e:
        print(f"❌ Package test error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_in_package())