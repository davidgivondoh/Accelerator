"""
Massive African & Global South Opportunities Database - 150+ Sources
"""

AFRICAN_OPPORTUNITIES = {
    # === MAJOR AFRICAN OPPORTUNITY PLATFORMS ===
    "opportunities_for_africans": {"url": "https://www.opportunitiesforafricans.com", "type": "aggregator", "region": "africa"},
    "opportunity_desk": {"url": "https://opportunitydesk.org", "type": "aggregator", "region": "global"},
    "after_school_africa": {"url": "https://www.afterschool.africa", "type": "aggregator", "region": "africa"},
    "opportunity_desk_africa": {"url": "https://opportunitydesk.org/category/africa", "type": "aggregator", "region": "africa"},
    "youthop": {"url": "https://youthop.com", "type": "aggregator", "region": "global"},
    "youth_opportunities": {"url": "https://www.youthopportunities.org", "type": "aggregator", "region": "global"},
    "opportunities_planet": {"url": "https://opportunitiesplanet.com", "type": "aggregator", "region": "global"},
    "opportunity_portal": {"url": "https://opportunityportal.org", "type": "aggregator", "region": "global"},
    "africa_grant_maker": {"url": "https://africagrantmaker.com", "type": "grants", "region": "africa"},
    "fundsforngos_africa": {"url": "https://www2.fundsforngos.org/category/africa", "type": "grants", "region": "africa"},
    
    # === AFRICAN VC & STARTUP ECOSYSTEM ===
    "vc4africa": {"url": "https://vc4a.com/ventures", "type": "vc", "region": "africa"},
    "afrilab": {"url": "https://afrilabs.com/programs", "type": "incubator", "region": "africa"},
    "disrupt_africa": {"url": "https://disrupt-africa.com/funding", "type": "news", "region": "africa"},
    "weetrack": {"url": "https://weetracker.com/deals", "type": "news", "region": "africa"},
    "techcabal": {"url": "https://techcabal.com/category/funding", "type": "news", "region": "africa"},
    "techpoint_africa": {"url": "https://techpoint.africa/category/funding", "type": "news", "region": "africa"},
    "benjamindada": {"url": "https://www.benjamindada.com/category/funding", "type": "news", "region": "africa"},
    "techcrunch_africa": {"url": "https://techcrunch.com/tag/africa", "type": "news", "region": "africa"},
    "quartz_africa": {"url": "https://qz.com/africa", "type": "news", "region": "africa"},
    "african_business": {"url": "https://african.business", "type": "news", "region": "africa"},
    
    # === AFRICAN ACCELERATORS & INCUBATORS ===
    "mest": {"url": "https://meltwater.org/apply", "location": "Ghana", "type": "accelerator"},
    "cchub": {"url": "https://cchubnigeria.com/programs", "location": "Nigeria", "type": "incubator"},
    "andela": {"url": "https://andela.com/careers", "location": "Pan-African", "type": "talent"},
    "startupbootcamp": {"url": "https://www.startupbootcamp.org/accelerator/afritech", "location": "South Africa", "type": "accelerator"},
    "google_africa": {"url": "https://startup.google.com/accelerator/africa", "location": "Pan-African", "type": "accelerator"},
    "seedstars_africa": {"url": "https://www.seedstars.com/world/africa", "location": "Pan-African", "type": "accelerator"},
    "founders_factory_africa": {"url": "https://foundersfactory.africa/apply", "location": "South Africa", "type": "accelerator"},
    "villgro_africa": {"url": "https://villgroafrica.org/apply", "location": "Kenya", "type": "incubator"},
    "grindstone": {"url": "https://grindstone.co.za/apply", "location": "South Africa", "type": "accelerator"},
    "savannah_fund": {"url": "https://savannah.vc/apply", "location": "Kenya", "type": "vc"},
    "catalyst_fund_africa": {"url": "https://bfrancais.com/catalyst-fund", "location": "Pan-African", "type": "accelerator"},
    "eneza_labs": {"url": "https://eneza.com/labs", "location": "Kenya", "type": "incubator"},
    "wennovation": {"url": "https://wennovationhub.org/apply", "location": "Nigeria", "type": "incubator"},
    "techstars_lagos": {"url": "https://www.techstars.com/accelerators/lagos", "location": "Nigeria", "type": "accelerator"},
    "flat6labs_africa": {"url": "https://www.flat6labs.com/apply", "location": "North Africa", "type": "accelerator"},
    "seedspace_africa": {"url": "https://www.seedspace.co/apply", "location": "Pan-African", "type": "incubator"},
    "launch_africa": {"url": "https://launchafricaventures.com/apply", "location": "Pan-African", "type": "vc"},
    "goodwell_investments": {"url": "https://goodwellinvestments.com/apply", "location": "Pan-African", "type": "vc"},
    "novastar_ventures": {"url": "https://novastarventures.com/contact", "location": "East Africa", "type": "vc"},
    "tlcom_capital": {"url": "https://www.tlcomcapital.com/contact", "location": "Pan-African", "type": "vc"},
    "partech_africa": {"url": "https://partechpartners.com/africa", "location": "Pan-African", "type": "vc"},
    "4dx_ventures": {"url": "https://www.4dxventures.com/contact", "location": "Pan-African", "type": "vc"},
    "enza_capital": {"url": "https://www.enzacapital.com", "location": "East Africa", "type": "vc"},
    "knife_capital": {"url": "https://www.knifecap.com", "location": "South Africa", "type": "vc"},
    "algebra_ventures": {"url": "https://www.algebraventures.com/apply", "location": "Egypt", "type": "vc"},
    "sawari_ventures": {"url": "https://sawariventures.com/contact", "location": "Egypt", "type": "vc"},
    
    # === AFRICAN FOUNDATIONS & FELLOWSHIPS ===
    "tony_elumelu": {"url": "https://www.tonyelumelufoundation.org/programme", "type": "fellowship", "funding": "$5000"},
    "mastercard_foundation": {"url": "https://mastercardfdn.org/our-work/scholars-program", "type": "scholarship", "funding": "full"},
    "african_leadership": {"url": "https://www.africanleadershipacademy.org/apply", "type": "education", "funding": "varies"},
    "anzisha_prize": {"url": "https://anzishaprize.org/apply", "type": "prize", "funding": "$25000"},
    "queen_elizabeth": {"url": "https://www.queenelizabethscholars.ca/apply", "type": "scholarship", "funding": "full"},
    "mandela_rhodes": {"url": "https://www.mandelarhodes.org/apply", "type": "scholarship", "funding": "full"},
    "mo_ibrahim": {"url": "https://mo.ibrahim.foundation/fellowships", "type": "fellowship", "funding": "full"},
    "canon_collins": {"url": "https://canoncollins.org.uk/apply", "type": "scholarship", "funding": "full"},
    "africa_oxford": {"url": "https://www.afriox.org/apply", "type": "research", "funding": "full"},
    "aga_khan_africa": {"url": "https://www.akdn.org/our-agencies/aga-khan-foundation/international-scholarship-programme", "type": "scholarship", "funding": "loan"},
    "chevening_africa": {"url": "https://www.chevening.org/scholarships", "type": "scholarship", "funding": "full"},
    "commonwealth_africa": {"url": "https://cscuk.fcdo.gov.uk/scholarships", "type": "scholarship", "funding": "full"},
    "daad_africa": {"url": "https://www.daad.de/en/study-and-research-in-germany/scholarships", "type": "scholarship", "funding": "full"},
    "fulbright_africa": {"url": "https://eca.state.gov/fulbright/about-fulbright/participating-countries", "type": "scholarship", "funding": "full"},
    "gates_cambridge_africa": {"url": "https://www.gatescambridge.org/apply", "type": "scholarship", "funding": "full"},
    "rhodesscholarship_africa": {"url": "https://www.rhodeshouse.ox.ac.uk/scholarships/apply", "type": "scholarship", "funding": "full"},
    "wellcome_africa": {"url": "https://wellcome.org/grant-funding/schemes/africa-and-asia-programmes", "type": "research", "funding": "varies"},
    "african_union_scholarships": {"url": "https://au.int/en/scholarships", "type": "scholarship", "funding": "varies"},
    "afdb_scholarships": {"url": "https://www.afdb.org/en/about-us/careers/japan-africa-dream-scholarship-program", "type": "scholarship", "funding": "full"},
    
    # === AFRICAN GRANTS & FUNDING ===
    "usaid_africa": {"url": "https://www.usaid.gov/africa", "type": "grants", "region": "africa"},
    "dfid_africa": {"url": "https://www.gov.uk/government/organisations/foreign-commonwealth-development-office", "type": "grants", "region": "africa"},
    "giz_africa": {"url": "https://www.giz.de/en/worldwide/africa.html", "type": "development", "region": "africa"},
    "afdb_grants": {"url": "https://www.afdb.org/en/projects-and-operations", "type": "grants", "region": "africa"},
    "world_bank_africa": {"url": "https://www.worldbank.org/en/region/afr/projects", "type": "grants", "region": "africa"},
    "bill_melinda_gates_africa": {"url": "https://www.gatesfoundation.org/our-work/places/africa", "type": "grants", "region": "africa"},
    "ford_foundation_africa": {"url": "https://www.fordfoundation.org/regions/africa", "type": "grants", "region": "africa"},
    "rockefeller_africa": {"url": "https://www.rockefellerfoundation.org/africa-initiative", "type": "grants", "region": "africa"},
    "hewlett_africa": {"url": "https://hewlett.org/strategy/sub-saharan-africa", "type": "grants", "region": "africa"},
    "skoll_africa": {"url": "https://skoll.org/organization-type/africa", "type": "social_enterprise", "region": "africa"},
    "open_society_africa": {"url": "https://www.opensocietyfoundations.org/grants", "type": "grants", "region": "africa"},
    
    # === AFRICAN COMPETITIONS & CHALLENGES ===
    "africa_prize": {"url": "https://www.raeng.org.uk/grants-prizes/prizes/international-prizes/africa-prize", "type": "prize", "funding": "£25000"},
    "rlabs_africa": {"url": "https://rlabs.org/programs", "type": "training", "region": "africa"},
    "african_entrepreneurship_award": {"url": "https://africanentrepreneurshipaward.com", "type": "prize", "funding": "$1M"},
    "africa_netpreneur": {"url": "https://africabusinessheroes.org", "type": "prize", "funding": "$1.5M"},
    "seedstars_africa_competition": {"url": "https://www.seedstars.com/world", "type": "competition", "funding": "$500k"},
    
    # === AFRICAN JOB BOARDS ===
    "jobberman": {"url": "https://www.jobberman.com", "location": "Nigeria", "type": "jobs"},
    "myjobmag": {"url": "https://www.myjobmag.com", "location": "Pan-African", "type": "jobs"},
    "brightermonday": {"url": "https://www.brightermonday.com", "location": "East Africa", "type": "jobs"},
    "careers24": {"url": "https://www.careers24.com", "location": "South Africa", "type": "jobs"},
    "pnet": {"url": "https://www.pnet.co.za", "location": "South Africa", "type": "jobs"},
    "indeed_africa": {"url": "https://ng.indeed.com", "location": "Nigeria", "type": "jobs"},
    "linkedin_africa": {"url": "https://www.linkedin.com/jobs/africa-jobs", "location": "Pan-African", "type": "jobs"},
    "ngcareers": {"url": "https://ngcareers.com", "location": "Nigeria", "type": "jobs"},
    "jobweb_ghana": {"url": "https://www.jobwebghana.com", "location": "Ghana", "type": "jobs"},
    "fuzu": {"url": "https://www.fuzu.com", "location": "East Africa", "type": "jobs"},
    "recruit_africa": {"url": "https://recruit.africa", "location": "Pan-African", "type": "jobs"},
}

GLOBAL_SOUTH_OPPORTUNITIES = {
    # === LATIN AMERICA ===
    "startup_chile": {"url": "https://www.startupchile.org/apply", "location": "Chile", "type": "accelerator"},
    "start_up_brasil": {"url": "https://www.startupbrasil.org.br", "location": "Brazil", "type": "accelerator"},
    "wayra": {"url": "https://www.wayra.com/apply", "location": "LATAM", "type": "accelerator"},
    "kaszek": {"url": "https://www.kaszek.com/apply", "location": "LATAM", "type": "vc"},
    "valor_latam": {"url": "https://valorcapitalgroup.com/contact", "location": "LATAM", "type": "vc"},
    "ignia": {"url": "https://ignia.com.mx/en/contact", "location": "Mexico", "type": "vc"},
    "magma_latam": {"url": "https://www.magmapartners.com/apply", "location": "LATAM", "type": "vc"},
    "softbank_latam": {"url": "https://www.softbank.com/en/corp/portfolio", "location": "LATAM", "type": "vc"},
    "iadb_lab": {"url": "https://bidlab.org/en/home", "location": "LATAM", "type": "grants"},
    "caf_latam": {"url": "https://www.caf.com/en/topics/entrepreneurship", "location": "LATAM", "type": "development"},
    
    # === SOUTHEAST ASIA ===
    "500_sea": {"url": "https://500.co/southeast-asia", "location": "SEA", "type": "vc"},
    "jungle_ventures": {"url": "https://www.jungle-ventures.com/contact", "location": "SEA", "type": "vc"},
    "golden_gate_sea": {"url": "https://www.goldengate.vc/apply", "location": "SEA", "type": "vc"},
    "east_ventures": {"url": "https://east.vc/contact", "location": "SEA", "type": "vc"},
    "vertex_sea": {"url": "https://www.vertexventures.com/sea", "location": "SEA", "type": "vc"},
    "wavemaker": {"url": "https://wavemaker.vc/contact", "location": "SEA", "type": "vc"},
    "openspace_ventures": {"url": "https://www.openspace.vc/contact", "location": "SEA", "type": "vc"},
    "seedplus": {"url": "https://seedplus.com/contact", "location": "SEA", "type": "vc"},
    "endeavor_sea": {"url": "https://endeavor.org/network/southeast-asia", "location": "SEA", "type": "network"},
    "echelon_asia": {"url": "https://e27.co/echelon", "location": "SEA", "type": "conference"},
    
    # === SOUTH ASIA (INDIA) ===
    "sequoia_india": {"url": "https://www.sequoiacap.com/india", "location": "India", "type": "vc"},
    "accel_india": {"url": "https://www.accel.com/india", "location": "India", "type": "vc"},
    "elevation_india": {"url": "https://www.elevationcapital.com/contact", "location": "India", "type": "vc"},
    "lightspeed_india": {"url": "https://lsindia.vc/contact", "location": "India", "type": "vc"},
    "matrix_india": {"url": "https://www.matrixpartners.in/contact", "location": "India", "type": "vc"},
    "blume_ventures": {"url": "https://blume.vc/contact", "location": "India", "type": "vc"},
    "chiratae_ventures": {"url": "https://www.chiratae.com/contact", "location": "India", "type": "vc"},
    "kalaari": {"url": "https://www.kalaari.com/contact", "location": "India", "type": "vc"},
    "startup_india": {"url": "https://www.startupindia.gov.in", "location": "India", "type": "government"},
    "nasscom_india": {"url": "https://nasscom.in/programs", "location": "India", "type": "network"},
    "t_hub": {"url": "https://t-hub.co/programs", "location": "India", "type": "incubator"},
    "nasscom_10000": {"url": "https://10000startups.com/apply", "location": "India", "type": "accelerator"},
    
    # === MIDDLE EAST/MENA ===
    "flat6labs": {"url": "https://www.flat6labs.com/apply", "location": "MENA", "type": "accelerator"},
    "500_mena": {"url": "https://500.co/mena", "location": "MENA", "type": "vc"},
    "mevp": {"url": "https://www.mevp.com/contact", "location": "MENA", "type": "vc"},
    "wamda": {"url": "https://www.wamda.com", "location": "MENA", "type": "ecosystem"},
    "beco_capital": {"url": "https://www.bfrancais.com/beco-capital", "location": "UAE", "type": "vc"},
    "shorooq_partners": {"url": "https://www.shorooq.ae/contact", "location": "UAE", "type": "vc"},
    "raed_ventures": {"url": "https://www.raed.vc/contact", "location": "Saudi", "type": "vc"},
    "saudi_venture": {"url": "https://svc.com.sa/en/contact", "location": "Saudi", "type": "vc"},
    "hub71": {"url": "https://hub71.com/apply", "location": "UAE", "type": "accelerator"},
    "dtec": {"url": "https://dtec.ae/apply", "location": "UAE", "type": "incubator"},
    "astrolabs": {"url": "https://astrolabs.com/apply", "location": "MENA", "type": "accelerator"},
    "oasis500": {"url": "https://www.oasis500.com/apply", "location": "Jordan", "type": "accelerator"},
}

INTERNATIONAL_DEVELOPMENT_ORGS = {
    # === MULTILATERAL ORGANIZATIONS ===
    "world_bank_youth": {"url": "https://www.worldbank.org/en/topic/youth", "type": "development"},
    "undp_youth": {"url": "https://www.undp.org/youth", "type": "development"},
    "unicef_youth": {"url": "https://www.unicef.org/partnerships/youth", "type": "development"},
    "ilo_youth": {"url": "https://www.ilo.org/global/topics/youth-employment/lang--en/index.htm", "type": "employment"},
    "unido": {"url": "https://www.unido.org/our-focus-priority-areas-youth-employment", "type": "industry"},
    "fao_youth": {"url": "https://www.fao.org/rural-employment/work-areas/youth-employment/en", "type": "agriculture"},
    "ifad_youth": {"url": "https://www.ifad.org/en/youth", "type": "rural"},
    "ifc_ventures": {"url": "https://www.ifc.org/wps/wcm/connect/Topics_Ext_Content/IFC_External_Corporate_Site/Venture+Capital", "type": "investment"},
    "afd": {"url": "https://www.afd.fr/en/page-thematique-axe/entrepreneurship-and-innovation", "type": "development"},
    "jica": {"url": "https://www.jica.go.jp/english/our_work/types_of_assistance/tech/training/index.html", "type": "development"},
    "koica": {"url": "https://www.koica.go.kr/koica_en/index.do", "type": "development"},
    "sida": {"url": "https://www.sida.se/en/for-partners/funding", "type": "development"},
    "norad": {"url": "https://norad.no/en/front/funding", "type": "development"},
    "danida": {"url": "https://um.dk/en/danida/partners", "type": "development"},
}

def get_all_african_sources():
    """Return total count and all African/Global South sources"""
    total = len(AFRICAN_OPPORTUNITIES) + len(GLOBAL_SOUTH_OPPORTUNITIES) + len(INTERNATIONAL_DEVELOPMENT_ORGS)
    return {
        "total": total,
        "african": AFRICAN_OPPORTUNITIES,
        "global_south": GLOBAL_SOUTH_OPPORTUNITIES,
        "development_orgs": INTERNATIONAL_DEVELOPMENT_ORGS
    }
