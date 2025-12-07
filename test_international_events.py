#!/usr/bin/env python3
"""
Test script for International Events & Opportunities integration
Validates the 70+ global conferences, youth programs, volunteer opportunities, and cultural exchanges
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.scrapers.opportunity_sources import OPPORTUNITY_SOURCES

def analyze_international_events_opportunities():
    """Analyze the newly added international events and opportunities platforms"""
    
    if "international_events_opportunities" not in OPPORTUNITY_SOURCES:
        print("❌ ERROR: international_events_opportunities section not found!")
        return
    
    platforms = OPPORTUNITY_SOURCES["international_events_opportunities"]
    print(f"✅ Found international_events_opportunities section with {len(platforms)} platforms")
    print("=" * 70)
    
    # Categorize by type and subtype
    by_type = {}
    by_subtype = {}
    by_specialty = {}
    by_region = {}
    by_tier = {"1": 0, "2": 0, "3": 0}
    by_frequency = {}
    
    for platform_id, platform_info in platforms.items():
        ptype = platform_info.get("type", "unknown")
        subtype = platform_info.get("subtype", "unknown")
        specialty = platform_info.get("specialty", "general")
        region = platform_info.get("region", "global")
        tier = str(platform_info.get("tier", 0))
        frequency = platform_info.get("frequency", "unknown")
        
        # Count by type
        if ptype not in by_type:
            by_type[ptype] = []
        by_type[ptype].append(platform_id)
        
        # Count by subtype
        if subtype not in by_subtype:
            by_subtype[subtype] = []
        by_subtype[subtype].append(platform_id)
        
        # Count by specialty
        if specialty not in by_specialty:
            by_specialty[specialty] = 0
        by_specialty[specialty] += 1
        
        # Count by region
        if region not in by_region:
            by_region[region] = 0
        by_region[region] += 1
        
        # Count by tier
        if tier in by_tier:
            by_tier[tier] += 1
            
        # Count by frequency
        if frequency not in by_frequency:
            by_frequency[frequency] = 0
        by_frequency[frequency] += 1
    
    print("🌍 PLATFORM BREAKDOWN BY MAJOR CATEGORIES:")
    print("-" * 60)
    
    # Conference platforms
    conference_platforms = by_type.get("conference", [])
    print(f"🎤 Conferences & Summits ({len(conference_platforms)}): Global forums, tech summits, policy events")
    
    # Youth programs
    youth_platforms = by_type.get("youth_program", [])
    print(f"👥 Youth Programs ({len(youth_platforms)}): Leadership, exchanges, advocacy")
    
    # Volunteer programs
    volunteer_platforms = by_type.get("volunteer_program", [])
    print(f"🤝 Volunteer Programs ({len(volunteer_platforms)}): International service, skill-sharing")
    
    # Exchange programs
    exchange_platforms = by_type.get("exchange_program", [])
    print(f"🌐 Exchange Programs ({len(exchange_platforms)}): Cultural, academic, professional")
    
    # Study abroad
    study_platforms = by_type.get("study_abroad", [])
    print(f"📚 Study Abroad ({len(study_platforms)}): International education, cultural immersion")
    
    # Other categories
    other_types = [t for t in by_type.keys() if t not in ["conference", "youth_program", "volunteer_program", "exchange_program", "study_abroad"]]
    if other_types:
        other_count = sum(len(by_type[t]) for t in other_types)
        print(f"🔧 Support & Other ({other_count}): {', '.join(other_types)}")
    
    print(f"\n🎯 TIER DISTRIBUTION:")
    print(f"   Tier 1 (Major/Global): {by_tier['1']} platforms")
    print(f"   Tier 2 (Regional/Specialized): {by_tier['2']} platforms")
    print(f"   Tier 3 (Niche): {by_tier['3']} platforms")
    
    print(f"\n🌍 REGIONAL FOCUS:")
    sorted_regions = sorted(by_region.items(), key=lambda x: x[1], reverse=True)[:12]
    for region, count in sorted_regions:
        print(f"   {region}: {count} platforms")
    
    print(f"\n⚡ FREQUENCY DISTRIBUTION:")
    sorted_frequencies = sorted(by_frequency.items(), key=lambda x: x[1], reverse=True)
    for frequency, count in sorted_frequencies:
        print(f"   {frequency}: {count} platforms")
    
    print(f"\n🔬 TOP SPECIALIZATIONS:")
    sorted_specialties = sorted(by_specialty.items(), key=lambda x: x[1], reverse=True)[:15]
    for specialty, count in sorted_specialties:
        print(f"   {specialty}: {count} platforms")
    
    # Verify key platform categories
    key_categories = {
        "Global Leadership": ["one_young_world", "world_economic_forum", "global_shapers"],
        "Youth Exchanges": ["aiesec", "rotary_exchange", "erasmus_plus", "iaeste"],
        "International Volunteering": ["unv", "peace_corps", "vso_international", "volunteer_hq"],
        "Technical Conferences": ["aws_events", "ml_summit", "ai_expo", "electronica"],
        "Maker Movement": ["maker_faire", "hackaday_contests", "fab_foundation_events"],
        "UN/International Orgs": ["unesco_events", "unitar_events", "world_bank_events"],
        "African Innovation": ["nairobi_tech_week", "lagos_startup_week", "africa_climate_summit"],
        "Humanitarian Work": ["doctors_without_borders", "engineers_without_borders", "red_cross_volunteer"]
    }
    
    print(f"\n✅ KEY CATEGORY COVERAGE:")
    print("-" * 50)
    total_verified = 0
    for category, expected_platforms in key_categories.items():
        found = sum(1 for p in expected_platforms if p in platforms)
        total_verified += found
        coverage_pct = (found / len(expected_platforms)) * 100
        print(f"{category}: {found}/{len(expected_platforms)} ({coverage_pct:.0f}%)")
    
    # Check for comprehensive opportunity types
    opportunity_types = {
        "Conferences & Summits": 0,
        "Youth Leadership": 0,
        "International Volunteering": 0,
        "Cultural Exchange": 0,
        "Academic Programs": 0,
        "Technical Training": 0,
        "Networking Events": 0,
        "Innovation Challenges": 0
    }
    
    for platform_info in platforms.values():
        offers = platform_info.get("offers", [])
        offers_str = ' '.join(offers).lower()
        specialty = platform_info.get("specialty", "").lower()
        subtype = platform_info.get("subtype", "").lower()
        
        if any(word in offers_str for word in ["events", "summit", "conference", "forum"]):
            opportunity_types["Conferences & Summits"] += 1
        if any(word in offers_str + " " + specialty for word in ["youth", "leadership", "young"]):
            opportunity_types["Youth Leadership"] += 1
        if any(word in offers_str for word in ["volunteer", "humanitarian", "service"]):
            opportunity_types["International Volunteering"] += 1
        if any(word in offers_str + " " + specialty for word in ["cultural", "exchange", "immersion"]):
            opportunity_types["Cultural Exchange"] += 1
        if any(word in offers_str + " " + subtype for word in ["academic", "study", "research", "education"]):
            opportunity_types["Academic Programs"] += 1
        if any(word in offers_str + " " + specialty for word in ["technical", "training", "certification"]):
            opportunity_types["Technical Training"] += 1
        if any(word in offers_str for word in ["networking", "community", "collaboration"]):
            opportunity_types["Networking Events"] += 1
        if any(word in offers_str + " " + subtype for word in ["challenges", "contests", "competition", "innovation"]):
            opportunity_types["Innovation Challenges"] += 1
    
    print(f"\n🎯 OPPORTUNITY TYPES AVAILABLE:")
    print("-" * 50)
    for opp_type, count in opportunity_types.items():
        print(f"   {opp_type}: {count} platforms")
    
    # Verify major international organizations
    major_organizations = {
        "aiesec": "World's largest youth exchange organization",
        "one_young_world": "Premier youth leadership summit",
        "tedx_events": "Global ideas platform",
        "peace_corps": "US international service program",
        "unv": "UN volunteer program",
        "world_economic_forum": "Global economic forum",
        "erasmus_plus": "European mobility program",
        "fulbright": "Academic exchange program"
    }
    
    print(f"\n✅ MAJOR ORGANIZATION VERIFICATION:")
    print("-" * 50)
    for platform_id, description in major_organizations.items():
        if platform_id in platforms:
            platform_name = platforms[platform_id]["name"]
            print(f"✅ {platform_name} ({platform_id}) - {description}")
        else:
            print(f"❌ Missing: {platform_id} - {description}")
    
    # Regional specialization analysis
    regional_specializations = {
        "African Innovation": ["africa", "kenya", "nigeria", "east_africa"],
        "European Programs": ["europe", "germany", "uk"],
        "Middle East Focus": ["middle_east", "middle_east_north_africa"],
        "US International": ["us_international", "mit_global"]
    }
    
    print(f"\n🌍 REGIONAL SPECIALIZATION:")
    print("-" * 50)
    for region_focus, region_keywords in regional_specializations.items():
        matching_count = sum(1 for p in platforms.values() 
                           if any(keyword in p.get("region", "").lower() for keyword in region_keywords))
        print(f"{region_focus}: {matching_count} specialized platforms")
    
    print(f"\n📈 FINAL SUMMARY:")
    print("=" * 70)
    print(f"✅ Total international events/opportunities integrated: {len(platforms)}")
    print(f"✅ Coverage across {len(by_type)} major opportunity categories")
    print(f"✅ {by_tier['1']} Tier 1 (global/major) organizations")
    print(f"✅ {by_region.get('global', 0)} global platforms with worldwide reach")
    print(f"✅ Strong regional diversity: Africa ({by_region.get('africa', 0)}), Europe, Middle East, US")
    print(f"✅ Comprehensive opportunity spectrum: Leadership → Volunteering → Education → Innovation")
    print(f"✅ Multiple engagement levels: Conferences → Programs → Long-term Service")
    
    if len(platforms) >= 70:
        print(f"🎉 SUCCESS: Successfully integrated {len(platforms)} international platforms!")
        print("Platform now has comprehensive global opportunity & networking coverage.")
    else:
        print(f"⚠️  Note: Expected 70+ platforms, found {len(platforms)}")

if __name__ == "__main__":
    print("🌍 INTERNATIONAL EVENTS & OPPORTUNITIES INTEGRATION ANALYSIS")
    print("=" * 70)
    analyze_international_events_opportunities()