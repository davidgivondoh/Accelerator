"""
Compare the new accelerator list with existing configuration
"""
import sys
import os
import re
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from src.scrapers.opportunity_sources import OPPORTUNITY_SOURCES

# Your new list from the request
new_accelerators = [
    "ycombinator.com", "seedstars.com", "techstars.com", "500.co", "foundersfactory.com",
    "entrepreneurfirst.com", "antler.co", "plugandplaytechcenter.com", "masschallenge.org",
    "startupbootcamp.org", "villageglobal.vc", "onedevcamp.com", "googleforstartups.com",
    "awsstartups.com", "microsoftfoundershub.com", "nvidia-inception-program.com",
    "intel-ignited.com", "IBM Hyper Protect Accelerator", "Apple Entrepreneur Camp",
    "MIT Sandbox", "MIT delta v", "Harvard iLab", "Stanford StartX", "Berkeley SkyDeck",
    "Alchemist Accelerator", "SOSV", "IndieBio", "HAX Hardware Accelerator",
    "Climate-KIC Accelerator", "Greentown Labs", "Elemental Excelerator",
    "Clean Energy Trust", "Africa's Talking AT Labs", "Antler Nairobi",
    "Founders Factory Africa", "AfriLabs", "MEST Africa", "CcHub", "iHub",
    "Gearbox Nairobi", "Nailab", "Villgro Africa", "Savanna Circuits",
    "Safaricom Spark Fund", "Blue Moon Ethiopia", "Tony Elumelu Foundation",
    "Orange Fab", "Huawei Cloud Startup Program", "Stripe Atlas", "Paystack Startup Program",
    "Flutterwave Startup Fund", "FoundersForge", "Google Black Founders Fund",
    "GSMA Innovation Fund", "Mastercard Start Path", "Visa Everywhere Initiative",
    "IFC Startup Catalyst", "UNDP Innovation Challenge", "UNICEF Venture Fund",
    "UNIDO ITPO", "WFP Innovation Accelerator", "Africa Prize for Engineering Innovation",
    "MIT Solve", "XPRIZE competitions", "ASME ISHOW", "Autodesk Technology Impact Program",
    "OpenAI Startup Fund", "Frontier AI Grants", "Nvidia grants", "Replit Launchpad",
    "Figma Creator Fund", "Notion Startup Program", "HubSpot for Startups",
    "Twilio Startups", "DigitalOcean Hatch", "Oracle for Startups",
    "OVHcloud Startup Program", "IBM Startup Program", "Cloudflare Startup Program",
    "Supabase Startup Program", "Render Startup Program", "Vercel Startup Program",
    "GitHub Startup Program", "Stripe Climate", "YC Startup School",
    "Founder Institute", "Starta Accelerator", "Bolt Accelerator", "BlueYard Capital",
    "First Round Capital", "Lux Capital", "A16z START program", "Neo Scholars",
    "Lightspeed Extreme Startups", "TechCrunch Startup Battlefield", "Africa Tech Summit",
    "Future Africa", "LoftyInc Capital", "Ingressive Capital", "Saviu Ventures",
    "Novastar Ventures", "TLcom Capital", "Partech Africa", "Chandaria Capital",
    "Enza Capital", "Kepple Africa Ventures", "Goodwell Investments", "Algebra Ventures",
    "EchoVC", "Founders Factory Climate Tech", "MIT ClimateTech", "GSMA AgriTech",
    "GSMA Digital Utilities", "Katapult VC", "Blue Impact Fund", "Acumen Fund",
    "Seed Transformation Program (Stanford)", "Young African Leaders Initiative (YALI)",
    "Obama Africa Leaders", "Mandela Washington Fellowship"
]

def analyze_coverage():
    """Analyze coverage of new accelerators in existing config"""
    current_accelerators = OPPORTUNITY_SOURCES.get("accelerators", {})
    
    print("🔍 ACCELERATOR COVERAGE ANALYSIS")
    print("=" * 50)
    print(f"📊 Current configuration: {len(current_accelerators)} accelerators")
    print(f"📋 New list provided: {len(new_accelerators)} accelerators")
    
    # Extract names and URLs from current config
    current_names = []
    current_urls = []
    
    for key, config in current_accelerators.items():
        name = config.get("name", "").lower()
        url = config.get("url", "").lower()
        current_names.append(name)
        current_urls.append(url)
    
    # Check coverage
    covered = 0
    missing = []
    
    for new_accel in new_accelerators:
        new_accel_clean = new_accel.lower().strip()
        
        # Check if it's covered by name matching
        is_covered = False
        
        # Check by URL/domain
        if new_accel_clean.endswith('.com') or new_accel_clean.endswith('.co') or new_accel_clean.endswith('.org'):
            domain_check = new_accel_clean.replace('.com', '').replace('.co', '').replace('.org', '')
            for url in current_urls:
                if domain_check in url:
                    is_covered = True
                    break
        
        # Check by name matching
        if not is_covered:
            for name in current_names:
                if any(word in name for word in new_accel_clean.split()) or any(word in new_accel_clean for word in name.split()):
                    is_covered = True
                    break
        
        if is_covered:
            covered += 1
        else:
            missing.append(new_accel)
    
    coverage_rate = (covered / len(new_accelerators)) * 100
    
    print(f"\n✅ Coverage: {covered}/{len(new_accelerators)} ({coverage_rate:.1f}%)")
    
    if missing:
        print(f"\n❓ Potentially missing accelerators ({len(missing)}):")
        for i, miss in enumerate(missing[:15]):  # Show first 15
            print(f"  {i+1}. {miss}")
        if len(missing) > 15:
            print(f"  ... and {len(missing) - 15} more")
    
    print(f"\n🎯 Analysis complete!")
    return coverage_rate, missing

if __name__ == "__main__":
    analyze_coverage()