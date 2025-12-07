"""
Test scholarship scraper integration
Test script to verify the comprehensive scholarship implementation
"""
import asyncio
import sys
import os

# Add the project root to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from src.scrapers.live_scrapers import scrape_scholarships_comprehensive, scrape_scholarships_basic

async def test_scholarship_scrapers():
    """Test both comprehensive and basic scholarship scrapers"""
    print("🎓 Testing Scholarship Scrapers")
    print("=" * 50)
    
    # Test basic scraper first (should always work)
    print("\n1. Testing Basic Scholarship Scraper...")
    try:
        basic_results = await scrape_scholarships_basic(limit=10)
        print(f"   ✅ Basic scraper: {len(basic_results)} scholarships")
        
        if basic_results:
            print("   📋 Sample scholarships:")
            for i, scholarship in enumerate(basic_results[:3]):
                print(f"      {i+1}. {scholarship['title']} - {scholarship['award_amount']}")
        
    except Exception as e:
        print(f"   ❌ Basic scraper error: {e}")
    
    # Test comprehensive scraper
    print("\n2. Testing Comprehensive Scholarship Scraper...")
    try:
        comprehensive_results = await scrape_scholarships_comprehensive(limit=15)
        print(f"   ✅ Comprehensive scraper: {len(comprehensive_results)} scholarships")
        
        if comprehensive_results:
            print("   📋 Sample scholarships:")
            for i, scholarship in enumerate(comprehensive_results[:5]):
                title = scholarship.get('title', 'Unknown')
                company = scholarship.get('company', 'Unknown')
                tier = scholarship.get('tier', 'unknown')
                region = scholarship.get('region', 'global')
                print(f"      {i+1}. {title} ({company}) - {tier} - {region}")
        
    except Exception as e:
        print(f"   ❌ Comprehensive scraper error: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"\n🎯 Test completed!")

if __name__ == "__main__":
    asyncio.run(test_scholarship_scrapers())