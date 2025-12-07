"""
Test the expanded freelance and remote job platform integration
"""
import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from src.scrapers.opportunity_sources import OPPORTUNITY_SOURCES

def analyze_job_platforms():
    """Analyze the expanded job platforms"""
    print("💼 JOB & FREELANCE PLATFORM ANALYSIS")
    print("=" * 50)
    
    # Count platforms in each category
    job_boards = OPPORTUNITY_SOURCES.get("job_boards", {})
    tech_startup = OPPORTUNITY_SOURCES.get("tech_startup", {})
    freelance_platforms = OPPORTUNITY_SOURCES.get("freelance_platforms", {})
    
    print(f"📊 Job Boards: {len(job_boards)} platforms")
    print(f"🚀 Tech & Startup: {len(tech_startup)} platforms")  
    print(f"💻 Freelance Platforms: {len(freelance_platforms)} platforms")
    
    total = len(job_boards) + len(tech_startup) + len(freelance_platforms)
    print(f"📈 Total Job/Freelance Sources: {total}")
    
    # Show sample freelance platforms
    print(f"\n💻 Sample Freelance Platforms:")
    for i, (key, config) in enumerate(list(freelance_platforms.items())[:8]):
        name = config.get("name", "Unknown")
        platform_type = config.get("type", "unknown")
        volume = config.get("volume", "medium")
        print(f"   {i+1}. {name} - {platform_type} - {volume} volume")
    
    # Show remote job platforms
    remote_jobs = [(key, config) for key, config in tech_startup.items() 
                  if config.get("type") == "remote_jobs"]
    print(f"\n🌍 Remote Job Platforms ({len(remote_jobs)}):")
    for i, (key, config) in enumerate(remote_jobs[:8]):
        name = config.get("name", "Unknown")
        region = config.get("region", "global")
        print(f"   {i+1}. {name} - {region}")
    
    # Show AI/Tech specialized platforms
    ai_tech_jobs = [(key, config) for key, config in tech_startup.items() 
                   if config.get("type") in ["ai_jobs", "freelance_dev", "tech_jobs"]]
    print(f"\n🤖 AI & Tech Specialized ({len(ai_tech_jobs)}):")
    for i, (key, config) in enumerate(ai_tech_jobs[:6]):
        name = config.get("name", "Unknown")
        specialty = config.get("specialty", "tech")
        print(f"   {i+1}. {name} - {specialty}")
    
    print(f"\n🎯 Analysis complete!")

if __name__ == "__main__":
    analyze_job_platforms()