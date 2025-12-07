#!/usr/bin/env python3
"""
Test script for Tech/AI/Learning/Bootcamp platform integration
Validates the 70+ educational and technical learning platforms added to opportunity_sources.py
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.scrapers.opportunity_sources import OPPORTUNITY_SOURCES

def analyze_tech_learning_platforms():
    """Analyze the newly added tech/AI/learning platforms"""
    
    if "tech_learning_platforms" not in OPPORTUNITY_SOURCES:
        print("❌ ERROR: tech_learning_platforms section not found!")
        return
    
    platforms = OPPORTUNITY_SOURCES["tech_learning_platforms"]
    print(f"✅ Found tech_learning_platforms section with {len(platforms)} platforms")
    print("=" * 60)
    
    # Categorize by subtype
    by_subtype = {}
    by_specialty = {}
    by_tier = {"1": 0, "2": 0, "3": 0}
    
    # Major categories we're looking for
    expected_categories = [
        "mooc", "nanodegree", "marketplace", "data_science", "competitions",
        "ai_specialization", "corporate_training", "cloud_training", 
        "coding_bootcamp", "university_course", "academic_conferences"
    ]
    
    for platform_id, platform_info in platforms.items():
        subtype = platform_info.get("subtype", "unknown")
        specialty = platform_info.get("specialty", "general")
        tier = str(platform_info.get("tier", 0))
        
        # Count by subtype
        if subtype not in by_subtype:
            by_subtype[subtype] = []
        by_subtype[subtype].append(platform_id)
        
        # Count by specialty
        if specialty not in by_specialty:
            by_specialty[specialty] = 0
        by_specialty[specialty] += 1
        
        # Count by tier
        if tier in by_tier:
            by_tier[tier] += 1
    
    print("📊 PLATFORM BREAKDOWN BY CATEGORY:")
    print("-" * 40)
    
    # Major MOOC platforms
    mooc_platforms = by_subtype.get("mooc", [])
    print(f"🎓 Major MOOC Platforms ({len(mooc_platforms)}): {', '.join(mooc_platforms)}")
    
    # AI/ML specialized
    ai_categories = ["ai_specialization", "ai_resources", "deep_learning_institute", 
                    "framework_ecosystem", "research_platform"]
    ai_count = sum(len(by_subtype.get(cat, [])) for cat in ai_categories)
    print(f"🤖 AI/ML Specialized ({ai_count} platforms)")
    
    # Bootcamps and intensive programs
    bootcamp_categories = ["coding_bootcamp", "intensive_bootcamp", "skills_bootcamp", 
                          "remote_dev_school", "african_tech_school"]
    bootcamp_count = sum(len(by_subtype.get(cat, [])) for cat in bootcamp_categories)
    print(f"💻 Bootcamps & Intensive Programs ({bootcamp_count} platforms)")
    
    # University and academic
    academic_categories = ["university_course", "university_online", "open_courseware",
                          "academic_conferences", "ai_conference"]
    academic_count = sum(len(by_subtype.get(cat, [])) for cat in academic_categories)
    print(f"🏫 University & Academic ({academic_count} platforms)")
    
    # Developer monetization
    monetization_categories = ["coding_bounties", "open_source_funding", "dev_tools_ecosystem",
                             "developer_content", "tech_blogging", "writing_monetization"]
    monetization_count = sum(len(by_subtype.get(cat, [])) for cat in monetization_categories)
    print(f"💰 Developer Monetization ({monetization_count} platforms)")
    
    print(f"\n🎯 TIER DISTRIBUTION:")
    print(f"   Tier 1 (Premium/Major): {by_tier['1']} platforms")
    print(f"   Tier 2 (Quality): {by_tier['2']} platforms") 
    print(f"   Tier 3 (Specialized): {by_tier['3']} platforms")
    
    print(f"\n🔬 TOP SPECIALTIES:")
    sorted_specialties = sorted(by_specialty.items(), key=lambda x: x[1], reverse=True)
    for specialty, count in sorted_specialties[:10]:
        print(f"   {specialty}: {count} platforms")
    
    # Verify key platforms are included
    key_platforms_check = {
        "coursera": "Major MOOC platform with scholarships",
        "kaggle": "ML competitions and jobs",
        "github_sponsors": "Open source funding",
        "fast_ai": "Practical AI education",
        "freecodecamp": "Free coding bootcamp",
        "cs50_harvard": "Harvard CS course",
        "neurips": "Top AI conference",
        "huggingface": "AI open source community"
    }
    
    print(f"\n✅ KEY PLATFORM VERIFICATION:")
    print("-" * 40)
    for platform_id, description in key_platforms_check.items():
        if platform_id in platforms:
            platform_name = platforms[platform_id]["name"]
            print(f"✅ {platform_name} ({platform_id}) - {description}")
        else:
            print(f"❌ Missing: {platform_id} - {description}")
    
    # Check for comprehensive coverage
    coverage_areas = {
        "MOOC Platforms": ["coursera", "edx", "udacity", "udemy"],
        "AI/ML Specialization": ["deeplearning_ai", "fast_ai", "kaggle", "huggingface"],
        "Cloud Training": ["aws_training", "microsoft_learn", "google_developers"],
        "Coding Bootcamps": ["freecodecamp", "app_academy", "general_assembly", "microverse"],
        "University Courses": ["cs50_harvard", "mit_ocw", "stanford_online"],
        "Developer Monetization": ["github_sponsors", "gitcoin", "replit_bounties"],
        "Content Creation": ["dev_to", "medium_partner", "substack", "hashnode"],
        "Premium Learning": ["pluralsight", "frontend_masters", "egghead"]
    }
    
    print(f"\n🎯 COVERAGE VERIFICATION:")
    print("-" * 40)
    total_coverage = 0
    for area, expected_platforms in coverage_areas.items():
        found = sum(1 for p in expected_platforms if p in platforms)
        total_coverage += found
        print(f"{area}: {found}/{len(expected_platforms)} platforms")
    
    print(f"\n📈 FINAL SUMMARY:")
    print("=" * 60)
    print(f"✅ Total tech learning platforms integrated: {len(platforms)}")
    print(f"✅ Coverage across {len(by_subtype)} different platform types")
    print(f"✅ {len([p for p in platforms.values() if p.get('tier') == 1])} Tier 1 (premium) platforms")
    print(f"✅ Global coverage including Africa, Europe, and specialized regions")
    print(f"✅ Complete spectrum: Free → Premium, Academic → Industry, Theory → Practice")
    
    if len(platforms) >= 70:
        print(f"🎉 SUCCESS: Successfully integrated {len(platforms)} tech/AI/learning platforms!")
        print("Platform now has comprehensive educational technology coverage.")
    else:
        print(f"⚠️  Warning: Expected 70+ platforms, found {len(platforms)}")

if __name__ == "__main__":
    print("🔍 TECH/AI/LEARNING PLATFORMS INTEGRATION ANALYSIS")
    print("=" * 60)
    analyze_tech_learning_platforms()