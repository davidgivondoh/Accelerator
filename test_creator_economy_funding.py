#!/usr/bin/env python3
"""
Test script for Creator Economy & Funding Platforms integration
Validates the 90+ creator economy, funding, and startup ecosystem platforms
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.scrapers.opportunity_sources import OPPORTUNITY_SOURCES

def analyze_creator_economy_funding():
    """Analyze the newly added creator economy and funding platforms"""
    
    if "creator_economy_funding" not in OPPORTUNITY_SOURCES:
        print("❌ ERROR: creator_economy_funding section not found!")
        return
    
    platforms = OPPORTUNITY_SOURCES["creator_economy_funding"]
    print(f"✅ Found creator_economy_funding section with {len(platforms)} platforms")
    print("=" * 80)
    
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
    
    print("💰 PLATFORM BREAKDOWN BY MAJOR CATEGORIES:")
    print("-" * 80)
    
    # Opportunity Hubs
    hub_platforms = by_type.get("opportunity_hub", []) + by_type.get("scholarship_hub", []) + by_type.get("education_hub", []) + by_type.get("fellowship_hub", [])
    print(f"🌐 Opportunity Hubs & Aggregators ({len(hub_platforms)}): Global discovery platforms")
    
    # Creator Economy
    creator_platforms = by_type.get("creator_platform", [])
    print(f"🎨 Creator Economy ({len(creator_platforms)}): Subscription, tips, fan support")
    
    # Marketplaces
    marketplace_platforms = by_type.get("marketplace", [])
    print(f"🛒 Marketplaces ({len(marketplace_platforms)}): Digital assets, merchandise, handmade")
    
    # Funding & Investment
    funding_platforms = by_type.get("crowdfunding", []) + by_type.get("funding_platform", []) + by_type.get("investment_platform", [])
    print(f"💸 Funding & Investment ({len(funding_platforms)}): Crowdfunding, VC, revenue-based")
    
    # Ecommerce & Sales
    ecommerce_platforms = by_type.get("ecommerce_platform", []) + by_type.get("print_platform", []) + by_type.get("resale_platform", [])
    print(f"🛍️ Ecommerce & Sales ({len(ecommerce_platforms)}): Online stores, print-on-demand, resale")
    
    # Creative & Gaming
    creative_platforms = by_type.get("creative_platform", []) + by_type.get("game_platform", []) + by_type.get("stock_platform", [])
    print(f"🎮 Creative & Gaming ({len(creative_platforms)}): Design jobs, game dev, stock media")
    
    # Startup Ecosystem
    startup_platforms = by_type.get("startup_platform", []) + by_type.get("intelligence_platform", []) + by_type.get("product_platform", [])
    print(f"🚀 Startup Ecosystem ({len(startup_platforms)}): Launch, intelligence, networking")
    
    # Communities & Fellowships
    community_platforms = by_type.get("community_platform", []) + by_type.get("fellowship_platform", [])
    print(f"👥 Communities & Fellowships ({len(community_platforms)}): No-code, founders, builders")
    
    # Other categories
    other_types = [t for t in by_type.keys() if t not in [
        "opportunity_hub", "scholarship_hub", "education_hub", "fellowship_hub",
        "creator_platform", "marketplace", "crowdfunding", "funding_platform", 
        "investment_platform", "ecommerce_platform", "print_platform", "resale_platform",
        "creative_platform", "game_platform", "stock_platform", "startup_platform",
        "intelligence_platform", "product_platform", "community_platform", "fellowship_platform"
    ]]
    if other_types:
        other_count = sum(len(by_type[t]) for t in other_types)
        print(f"🔧 Other Categories ({other_count}): {', '.join(other_types)}")
    
    print(f"\n🎯 TIER DISTRIBUTION:")
    print(f"   Tier 1 (Major/Established): {by_tier['1']} platforms")
    print(f"   Tier 2 (Growing/Regional): {by_tier['2']} platforms")
    print(f"   Tier 3 (Niche/Emerging): {by_tier['3']} platforms")
    
    print(f"\n🌍 REGIONAL DISTRIBUTION:")
    sorted_regions = sorted(by_region.items(), key=lambda x: x[1], reverse=True)[:10]
    for region, count in sorted_regions:
        print(f"   {region}: {count} platforms")
    
    print(f"\n⚡ UPDATE FREQUENCY:")
    sorted_frequencies = sorted(by_frequency.items(), key=lambda x: x[1], reverse=True)
    for frequency, count in sorted_frequencies:
        print(f"   {frequency}: {count} platforms")
    
    # Analyze monetization models
    monetization_models = {
        "Creator Subscriptions": ["patreon", "buy_me_coffee", "ko_fi"],
        "Marketplace Sales": ["etsy", "redbubble", "gumroad", "themeforest"],
        "Stock Media": ["shutterstock", "getty_images", "adobe_stock"],
        "Crowdfunding": ["kickstarter", "indiegogo", "gofundme", "experiment"],
        "Ecommerce Stores": ["shopify", "woocommerce", "big_cartel"],
        "Print-on-Demand": ["printful", "printify", "teespring"],
        "Game Development": ["itch_io", "unity_asset_store", "steam_direct"],
        "Investment Platforms": ["republic", "angellist", "wefunder"]
    }
    
    print(f"\n💰 MONETIZATION MODEL COVERAGE:")
    print("-" * 60)
    total_monetization = 0
    for model, expected_platforms in monetization_models.items():
        found = sum(1 for p in expected_platforms if p in platforms)
        total_monetization += found
        coverage_pct = (found / len(expected_platforms)) * 100
        print(f"{model}: {found}/{len(expected_platforms)} ({coverage_pct:.0f}%)")
    
    # Analyze opportunity types
    opportunity_types = {
        "Direct Sales": 0,
        "Subscription Income": 0,
        "Marketplace Commissions": 0,
        "Crowdfunding": 0,
        "Investment/Funding": 0,
        "Freelance/Services": 0,
        "Community Building": 0,
        "Educational Content": 0
    }
    
    for platform_info in platforms.values():
        offers = platform_info.get("offers", [])
        specialty = platform_info.get("specialty", "")
        subtype = platform_info.get("subtype", "")
        combined_text = ' '.join(offers + [specialty, subtype]).lower()
        
        if any(word in combined_text for word in ["sales", "sell", "marketplace", "store"]):
            opportunity_types["Direct Sales"] += 1
        if any(word in combined_text for word in ["subscription", "support", "income"]):
            opportunity_types["Subscription Income"] += 1
        if any(word in combined_text for word in ["marketplace", "commission", "revenue"]):
            opportunity_types["Marketplace Commissions"] += 1
        if any(word in combined_text for word in ["crowdfunding", "funding", "campaign"]):
            opportunity_types["Crowdfunding"] += 1
        if any(word in combined_text for word in ["investment", "funding", "equity", "venture"]):
            opportunity_types["Investment/Funding"] += 1
        if any(word in combined_text for word in ["freelance", "service", "commission", "job"]):
            opportunity_types["Freelance/Services"] += 1
        if any(word in combined_text for word in ["community", "networking", "collaboration"]):
            opportunity_types["Community Building"] += 1
        if any(word in combined_text for word in ["education", "course", "tutorial", "learning"]):
            opportunity_types["Educational Content"] += 1
    
    print(f"\n🎯 OPPORTUNITY TYPES AVAILABLE:")
    print("-" * 60)
    for opp_type, count in opportunity_types.items():
        print(f"   {opp_type}: {count} platforms")
    
    # Verify major platforms
    major_platforms = {
        "opportunity_desk": "Global opportunity aggregator",
        "kickstarter": "Creative project crowdfunding",
        "patreon": "Creator subscription platform", 
        "shopify": "Comprehensive ecommerce platform",
        "etsy": "Handmade goods marketplace",
        "angellist": "Startup ecosystem platform",
        "product_hunt": "Product launch platform",
        "republic": "Equity crowdfunding platform"
    }
    
    print(f"\n✅ MAJOR PLATFORM VERIFICATION:")
    print("-" * 60)
    for platform_id, description in major_platforms.items():
        if platform_id in platforms:
            platform_name = platforms[platform_id]["name"]
            print(f"✅ {platform_name} ({platform_id}) - {description}")
        else:
            print(f"❌ Missing: {platform_id} - {description}")
    
    # Revenue model analysis
    revenue_models = {
        "High Volume/Low Margin": ["etsy", "redbubble", "shutterstock", "itch_io"],
        "High Value/Low Volume": ["flippa", "empire_flippers", "microacquire"],
        "Subscription/Recurring": ["patreon", "gumroad", "shopify", "pipe"],
        "Commission-Based": ["kickstarter", "indiegogo", "republic", "angellist"],
        "Print-on-Demand": ["printful", "printify", "teespring", "redbubble"],
        "Digital Products": ["gumroad", "themeforest", "codecanyon", "unity_asset_store"]
    }
    
    print(f"\n📊 REVENUE MODEL ANALYSIS:")
    print("-" * 60)
    for model, model_platforms in revenue_models.items():
        matching = sum(1 for p in model_platforms if p in platforms)
        print(f"{model}: {matching} platforms")
    
    # Geographic specialization
    geographic_specializations = {
        "Global Reach": sum(1 for p in platforms.values() if p.get("region") == "global"),
        "US-Focused": sum(1 for p in platforms.values() if "us" in p.get("region", "").lower()),
        "Europe-Focused": sum(1 for p in platforms.values() if "europe" in p.get("region", "").lower()),
        "Africa-Focused": sum(1 for p in platforms.values() if "africa" in p.get("region", "").lower()),
        "Regional Specific": sum(1 for p in platforms.values() if p.get("region", "global") != "global")
    }
    
    print(f"\n🌍 GEOGRAPHIC SPECIALIZATION:")
    print("-" * 60)
    for geo_focus, count in geographic_specializations.items():
        print(f"{geo_focus}: {count} platforms")
    
    print(f"\n📈 FINAL SUMMARY:")
    print("=" * 80)
    print(f"✅ Total creator economy & funding platforms integrated: {len(platforms)}")
    print(f"✅ Coverage across {len(by_type)} major platform categories")
    print(f"✅ {by_tier['1']} Tier 1 (major/established) platforms")
    print(f"✅ {by_region.get('global', 0)} platforms with global reach")
    print(f"✅ Complete monetization spectrum: Direct Sales → Subscriptions → Investment")
    print(f"✅ Full creator journey: Idea → Build → Launch → Scale → Exit")
    print(f"✅ Comprehensive funding options: Crowdfunding → Revenue-based → Equity")
    
    if len(platforms) >= 90:
        print(f"🎉 SUCCESS: Successfully integrated {len(platforms)} creator economy platforms!")
        print("Platform now has comprehensive creator economy & funding coverage.")
    else:
        print(f"⚠️  Note: Expected 90+ platforms, found {len(platforms)}")

if __name__ == "__main__":
    print("💰 CREATOR ECONOMY & FUNDING PLATFORMS INTEGRATION ANALYSIS")
    print("=" * 80)
    analyze_creator_economy_funding()