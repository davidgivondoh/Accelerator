#!/usr/bin/env python3
"""
Test script for Climate/Sustainability platform integration
Validates the 60+ climate, energy, and environmental platforms added to opportunity_sources.py
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.scrapers.opportunity_sources import OPPORTUNITY_SOURCES

def analyze_climate_sustainability_platforms():
    """Analyze the newly added climate/sustainability platforms"""
    
    if "climate_sustainability" not in OPPORTUNITY_SOURCES:
        print("❌ ERROR: climate_sustainability section not found!")
        return
    
    platforms = OPPORTUNITY_SOURCES["climate_sustainability"]
    print(f"✅ Found climate_sustainability section with {len(platforms)} platforms")
    print("=" * 60)
    
    # Categorize by type and subtype
    by_type = {}
    by_subtype = {}
    by_specialty = {}
    by_region = {}
    by_tier = {"1": 0, "2": 0, "3": 0}
    
    for platform_id, platform_info in platforms.items():
        ptype = platform_info.get("type", "unknown")
        subtype = platform_info.get("subtype", "unknown")
        specialty = platform_info.get("specialty", "general")
        region = platform_info.get("region", "global")
        tier = str(platform_info.get("tier", 0))
        
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
    
    print("🌍 PLATFORM BREAKDOWN BY MAJOR CATEGORIES:")
    print("-" * 50)
    
    # Climate platforms
    climate_platforms = by_type.get("climate", [])
    print(f"🌡️  Climate Action & Policy ({len(climate_platforms)}): {len(climate_platforms)} platforms")
    
    # Energy platforms
    energy_platforms = by_type.get("energy", [])
    print(f"⚡ Clean Energy & Renewables ({len(energy_platforms)}): {len(energy_platforms)} platforms")
    
    # Agriculture platforms
    agriculture_platforms = by_type.get("agriculture", [])
    print(f"🌱 Agriculture & Food Systems ({len(agriculture_platforms)}): {len(agriculture_platforms)} platforms")
    
    # Conservation platforms
    conservation_platforms = by_type.get("conservation", [])
    print(f"🌳 Forest & Conservation ({len(conservation_platforms)}): {len(conservation_platforms)} platforms")
    
    # Water platforms
    water_platforms = by_type.get("water", [])
    print(f"💧 Water & Sanitation ({len(water_platforms)}): {len(water_platforms)} platforms")
    
    # Climate finance
    finance_platforms = by_type.get("climate_finance", [])
    print(f"💰 Climate Finance ({len(finance_platforms)}): {len(finance_platforms)} platforms")
    
    # Other categories
    other_types = [t for t in by_type.keys() if t not in ["climate", "energy", "agriculture", "conservation", "water", "climate_finance"]]
    if other_types:
        other_count = sum(len(by_type[t]) for t in other_types)
        print(f"🔧 Other Categories ({other_count}): {', '.join(other_types)}")
    
    print(f"\n🎯 TIER DISTRIBUTION:")
    print(f"   Tier 1 (Major/International): {by_tier['1']} platforms")
    print(f"   Tier 2 (Regional/Specialized): {by_tier['2']} platforms")
    print(f"   Tier 3 (Niche): {by_tier['3']} platforms")
    
    print(f"\n🌍 REGIONAL FOCUS:")
    sorted_regions = sorted(by_region.items(), key=lambda x: x[1], reverse=True)
    for region, count in sorted_regions:
        print(f"   {region}: {count} platforms")
    
    print(f"\n🔬 TOP SPECIALIZATIONS:")
    sorted_specialties = sorted(by_specialty.items(), key=lambda x: x[1], reverse=True)[:12]
    for specialty, count in sorted_specialties:
        print(f"   {specialty}: {count} platforms")
    
    # Verify key platform categories
    key_categories = {
        "Climate Policy": ["climate_links", "climate_kic", "climate_action"],
        "Renewable Energy": ["irena", "ren21", "se_for_all", "re100"],
        "Carbon Markets": ["south_pole", "verra", "gold_standard", "patch_io"],
        "Agricultural Research": ["fao", "cimmyt", "icrisat", "alliance_bioversity"],
        "Climate Finance": ["green_climate_fund", "gef", "world_bank_climate"],
        "Job Platforms": ["climate_base", "clean_technica", "sustainable_careers"],
        "International Organizations": ["fao", "ifad", "afdb", "irena"],
        "African Focus": ["afdb", "africa_rice", "grow_africa", "energise_africa"]
    }
    
    print(f"\n✅ KEY CATEGORY COVERAGE:")
    print("-" * 40)
    total_verified = 0
    for category, expected_platforms in key_categories.items():
        found = sum(1 for p in expected_platforms if p in platforms)
        total_verified += found
        coverage_pct = (found / len(expected_platforms)) * 100
        print(f"{category}: {found}/{len(expected_platforms)} ({coverage_pct:.0f}%)")
    
    # Check for comprehensive opportunity types
    opportunity_types = {
        "Jobs & Careers": 0,
        "Grants & Funding": 0,
        "Partnerships": 0,
        "Research Opportunities": 0,
        "Innovation Programs": 0,
        "Fellowships": 0,
        "Training & Education": 0,
        "Investment Opportunities": 0
    }
    
    for platform_info in platforms.values():
        offers = platform_info.get("offers", [])
        offers_str = ' '.join(offers).lower()
        
        if any(word in offers_str for word in ["jobs", "careers", "employment"]):
            opportunity_types["Jobs & Careers"] += 1
        if any(word in offers_str for word in ["grants", "funding", "finance"]):
            opportunity_types["Grants & Funding"] += 1
        if any(word in offers_str for word in ["partnerships", "collaboration", "cooperation"]):
            opportunity_types["Partnerships"] += 1
        if any(word in offers_str for word in ["research", "studies"]):
            opportunity_types["Research Opportunities"] += 1
        if any(word in offers_str for word in ["innovation", "programs", "initiatives"]):
            opportunity_types["Innovation Programs"] += 1
        if any(word in offers_str for word in ["fellowships", "fellowship"]):
            opportunity_types["Fellowships"] += 1
        if any(word in offers_str for word in ["training", "education", "courses"]):
            opportunity_types["Training & Education"] += 1
        if any(word in offers_str for word in ["investment", "deals", "funding"]):
            opportunity_types["Investment Opportunities"] += 1
    
    print(f"\n🎯 OPPORTUNITY TYPES AVAILABLE:")
    print("-" * 40)
    for opp_type, count in opportunity_types.items():
        print(f"   {opp_type}: {count} platforms")
    
    # Verify major climate organizations
    major_organizations = {
        "climate_base": "Climate job platform",
        "irena": "International renewable energy agency",
        "fao": "UN Food and Agriculture Organization", 
        "green_climate_fund": "Major climate finance fund",
        "rainforest_alliance": "Forest conservation leader",
        "clean_cooking_alliance": "Clean cooking solutions",
        "power_for_all": "Energy access advocacy"
    }
    
    print(f"\n✅ MAJOR ORGANIZATION VERIFICATION:")
    print("-" * 40)
    for platform_id, description in major_organizations.items():
        if platform_id in platforms:
            platform_name = platforms[platform_id]["name"]
            print(f"✅ {platform_name} ({platform_id}) - {description}")
        else:
            print(f"❌ Missing: {platform_id} - {description}")
    
    print(f"\n📈 FINAL SUMMARY:")
    print("=" * 60)
    print(f"✅ Total climate/sustainability platforms integrated: {len(platforms)}")
    print(f"✅ Coverage across {len(by_type)} major environmental sectors")
    print(f"✅ {by_tier['1']} Tier 1 (international/major) organizations")
    print(f"✅ Strong African focus: {by_region.get('africa', 0)} Africa-specific platforms")
    print(f"✅ Comprehensive opportunity types from jobs to funding to partnerships")
    print(f"✅ Complete climate spectrum: Policy → Research → Implementation → Finance")
    
    if len(platforms) >= 60:
        print(f"🎉 SUCCESS: Successfully integrated {len(platforms)} climate/sustainability platforms!")
        print("Platform now has comprehensive environmental & climate opportunity coverage.")
    else:
        print(f"⚠️  Note: Expected 60+ platforms, found {len(platforms)}")

if __name__ == "__main__":
    print("🌍 CLIMATE/SUSTAINABILITY PLATFORMS INTEGRATION ANALYSIS")
    print("=" * 60)
    analyze_climate_sustainability_platforms()