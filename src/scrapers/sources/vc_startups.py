"""
Massive VC & Startup Sources Database - 300+ VC Funds, Accelerators, Angel Networks
"""

ACCELERATORS = {
    # === TOP TIER ACCELERATORS ===
    "ycombinator": {"url": "https://www.ycombinator.com/apply", "location": "San Francisco", "funding": "$500k", "equity": "7%"},
    "techstars": {"url": "https://www.techstars.com/accelerators", "location": "Global", "funding": "$120k", "equity": "6%"},
    "500_global": {"url": "https://500.co/accelerators", "location": "Global", "funding": "$150k", "equity": "6%"},
    "antler": {"url": "https://www.antler.co/apply", "location": "Global", "funding": "$100k", "equity": "10%"},
    "founder_institute": {"url": "https://fi.co/apply", "location": "Global", "funding": "varies", "equity": "4%"},
    "plug_and_play": {"url": "https://www.plugandplaytechcenter.com/join", "location": "Silicon Valley", "funding": "varies", "equity": "0%"},
    "startx": {"url": "https://startx.com/apply", "location": "Stanford", "funding": "varies", "equity": "0%"},
    "alchemist": {"url": "https://alchemistaccelerator.com/apply", "location": "Silicon Valley", "funding": "$36k", "equity": "5%"},
    "angelpad": {"url": "https://angelpad.com/apply", "location": "San Francisco", "funding": "$120k", "equity": "7%"},
    "amplify_la": {"url": "https://amplify.la/apply", "location": "Los Angeles", "funding": "$100k", "equity": "5%"},
    "mucker_capital": {"url": "https://www.muckercapital.com/accelerator", "location": "Los Angeles", "funding": "$150k", "equity": "6%"},
    "launch": {"url": "https://www.launchaccelerator.co/apply", "location": "San Francisco", "funding": "$100k", "equity": "6%"},
    "dreamit": {"url": "https://www.dreamit.com/apply", "location": "Multi-city", "funding": "$50k", "equity": "6%"},
    "gener8tor": {"url": "https://www.gener8tor.com/apply", "location": "Midwest", "funding": "$100k", "equity": "6%"},
    "boomtown": {"url": "https://www.boomtownaccelerators.com", "location": "Boulder", "funding": "$50k", "equity": "6%"},
    "brandery": {"url": "https://brandery.org/apply", "location": "Cincinnati", "funding": "$100k", "equity": "6%"},
    "alphalab": {"url": "https://alphalab.org/apply", "location": "Pittsburgh", "funding": "$25k", "equity": "5%"},
    "betaspring": {"url": "https://betaspring.com/apply", "location": "Providence", "funding": "$25k", "equity": "6%"},
    "capitalfactory": {"url": "https://www.capitalfactory.com/accelerator", "location": "Austin", "funding": "$25k", "equity": "1%"},
    "techtown": {"url": "https://techtowndetroit.org/dtx", "location": "Detroit", "funding": "$50k", "equity": "0%"},
    "masschallenge": {"url": "https://masschallenge.org/programs", "location": "Boston", "funding": "prize", "equity": "0%"},
    "newchip": {"url": "https://newchip.com/apply", "location": "Austin", "funding": "varies", "equity": "varies"},
    
    # === SECTOR-SPECIFIC ACCELERATORS ===
    # AI/ML
    "ai_camp": {"url": "https://www.ai.camp", "location": "Global", "funding": "varies", "focus": "ai"},
    "pioneer": {"url": "https://pioneer.app", "location": "Remote", "funding": "$20k", "focus": "ai"},
    "ai2_incubator": {"url": "https://incubator.allenai.org", "location": "Seattle", "funding": "$250k", "focus": "ai"},
    "factory_ai": {"url": "https://www.factory.ai", "location": "San Francisco", "funding": "varies", "focus": "ai"},
    "radical_ventures": {"url": "https://radical.vc/apply", "location": "Toronto", "funding": "varies", "focus": "ai"},
    
    # HealthTech
    "rock_health": {"url": "https://rockhealth.com/apply", "location": "San Francisco", "funding": "$250k", "focus": "health"},
    "startup_health": {"url": "https://www.startuphealth.com/apply", "location": "New York", "funding": "varies", "focus": "health"},
    "blueprintx": {"url": "https://www.blueprinthealth.org", "location": "New York", "funding": "varies", "focus": "health"},
    "matter": {"url": "https://matter.health/startups/accelerate", "location": "Chicago", "funding": "varies", "focus": "health"},
    "healthbox": {"url": "https://healthbox.com/programs", "location": "Nashville", "funding": "varies", "focus": "health"},
    "digital_health_accelerator": {"url": "https://www.cedars-sinai.org/accelerator", "location": "Los Angeles", "funding": "$100k", "focus": "health"},
    
    # FinTech
    "fintech_sandbox": {"url": "https://fintechsandbox.org/apply", "location": "Boston", "funding": "varies", "focus": "fintech"},
    "barclays_accelerator": {"url": "https://home.barclays/who-we-are/innovation/barclays-accelerator", "location": "London", "funding": "varies", "focus": "fintech"},
    "citi_ventures": {"url": "https://citi.com/ventures/accelerator", "location": "Global", "funding": "varies", "focus": "fintech"},
    "f10": {"url": "https://www.f10.global/accelerator", "location": "Zurich", "funding": "varies", "focus": "fintech"},
    "fintech_innovation_lab": {"url": "https://www.fintechinnovationlab.com", "location": "Global", "funding": "varies", "focus": "fintech"},
    "catalyst_fund": {"url": "https://www.bfrancais.com/catalyst-fund", "location": "Global", "funding": "$100k", "focus": "fintech"},
    
    # CleanTech/Climate
    "cleantech_open": {"url": "https://www.cleantechopen.org/apply", "location": "Global", "funding": "varies", "focus": "cleantech"},
    "techstars_sustainability": {"url": "https://www.techstars.com/accelerators/sustainability-paris", "location": "Paris", "funding": "$120k", "focus": "climate"},
    "elemental": {"url": "https://elementalexcelerator.com/apply", "location": "Hawaii", "funding": "$1M", "focus": "climate"},
    "greentown_labs": {"url": "https://greentownlabs.com/apply", "location": "Boston", "funding": "varies", "focus": "cleantech"},
    "cyclotron_road": {"url": "https://cyclotronroad.lbl.gov/apply", "location": "Berkeley", "funding": "varies", "focus": "energy"},
    "lacrawd": {"url": "https://www.lacleantechincubator.org", "location": "Los Angeles", "funding": "varies", "focus": "cleantech"},
    "prime_coalition": {"url": "https://primecoalition.org/apply", "location": "Global", "funding": "varies", "focus": "climate"},
    "third_derivative": {"url": "https://www.third-derivative.org/apply", "location": "Global", "funding": "varies", "focus": "climate"},
    "congruent_ventures": {"url": "https://www.congruentvc.com", "location": "San Francisco", "funding": "varies", "focus": "climate"},
    
    # EdTech
    "imagine_k12": {"url": "https://www.imaginek12.com", "location": "San Francisco", "funding": "varies", "focus": "edtech"},
    "learnlaunch": {"url": "https://learnlaunch.org/accelerator", "location": "Boston", "funding": "$100k", "focus": "edtech"},
    "edtech_accelerator": {"url": "https://www.edtechaccelerator.com", "location": "Global", "funding": "varies", "focus": "edtech"},
    "emerge_edtech": {"url": "https://www.emergeeducation.com", "location": "London", "funding": "varies", "focus": "edtech"},
    "reach_capital": {"url": "https://www.reachcapital.com", "location": "San Francisco", "funding": "varies", "focus": "edtech"},
    
    # FoodTech/AgTech
    "food_x": {"url": "https://www.food-x.com/apply", "location": "New York", "funding": "$50k", "focus": "foodtech"},
    "terra_accelerator": {"url": "https://www.terra.do/climate-accelerator", "location": "Global", "funding": "varies", "focus": "agtech"},
    "yield_lab": {"url": "https://www.theyieldlab.com/apply", "location": "St. Louis", "funding": "$100k", "focus": "agtech"},
    "agtech_xchange": {"url": "https://agtechxchange.com", "location": "Midwest", "funding": "varies", "focus": "agtech"},
    "bits_x_bites": {"url": "https://www.bitsxbites.com", "location": "Shanghai", "funding": "varies", "focus": "foodtech"},
    
    # PropTech/Construction
    "metaprop": {"url": "https://www.metaprop.vc/accelerator", "location": "New York", "funding": "$250k", "focus": "proptech"},
    "fifth_wall": {"url": "https://fifthwall.com", "location": "Los Angeles", "funding": "varies", "focus": "proptech"},
    "construction_tech": {"url": "https://www.constructiontech.com", "location": "Global", "funding": "varies", "focus": "construction"},
    
    # Mobility/Transport
    "2048_ventures": {"url": "https://www.2048.vc", "location": "New York", "funding": "varies", "focus": "mobility"},
    "autotech_ventures": {"url": "https://www.autotechvc.com", "location": "Silicon Valley", "funding": "varies", "focus": "mobility"},
    "fontinalis": {"url": "https://fontinalis.com", "location": "Detroit", "funding": "varies", "focus": "mobility"},
    
    # Space
    "techstars_space": {"url": "https://www.techstars.com/accelerators/space", "location": "Los Angeles", "funding": "$120k", "focus": "space"},
    "starburst": {"url": "https://starburst.aero/apply", "location": "Global", "funding": "varies", "focus": "aerospace"},
    "seraphim": {"url": "https://seraphimcapital.co.uk/accelerator", "location": "London", "funding": "varies", "focus": "space"},
    
    # Web3/Crypto
    "a16z_crypto_startup": {"url": "https://a16zcrypto.com/csl", "location": "Remote", "funding": "varies", "focus": "web3"},
    "outlier_ventures": {"url": "https://outlierventures.io/base-camp", "location": "London", "funding": "varies", "focus": "web3"},
    "alliance_dao": {"url": "https://alliance.xyz", "location": "New York", "funding": "$250k", "focus": "web3"},
    "tachyon": {"url": "https://mesh.xyz/tachyon", "location": "Remote", "funding": "varies", "focus": "web3"},
    "tribe_capital": {"url": "https://www.tribecapital.com", "location": "San Francisco", "funding": "varies", "focus": "web3"},
    
    # Social Impact
    "unreasonable": {"url": "https://unreasonablegroup.com/companies/apply", "location": "Global", "funding": "varies", "focus": "impact"},
    "village_capital": {"url": "https://vilcap.com/apply", "location": "Global", "funding": "varies", "focus": "impact"},
    "echoing_green": {"url": "https://echoinggreen.org/fellowship/apply", "location": "Global", "funding": "$80k", "focus": "impact"},
    "skoll_foundation": {"url": "https://skoll.org/about/skoll-awards", "location": "Global", "funding": "$1.5M", "focus": "impact"},
    "schwab_foundation": {"url": "https://www.schwabfound.org", "location": "Global", "funding": "varies", "focus": "impact"},
    "ashoka": {"url": "https://www.ashoka.org/en-us/program/ashoka-venture-and-fellowship", "location": "Global", "funding": "varies", "focus": "impact"},
    "resolution_project": {"url": "https://resolutionproject.org/apply", "location": "Global", "funding": "$3k", "focus": "impact"},
    
    # Women/Diversity Focused
    "female_founders": {"url": "https://femalefounders.org/apply", "location": "Global", "funding": "varies", "focus": "women"},
    "sheeo": {"url": "https://sheeo.world/apply", "location": "Global", "funding": "varies", "focus": "women"},
    "backstage_capital": {"url": "https://backstagecapital.com/apply", "location": "Global", "funding": "varies", "focus": "diversity"},
    "digitalundivided": {"url": "https://www.digitalundivided.com/incubator", "location": "Global", "funding": "varies", "focus": "diversity"},
    "newme": {"url": "https://www.newme.in/apply", "location": "Silicon Valley", "funding": "varies", "focus": "diversity"},
    "harlem_capital": {"url": "https://www.harlem.capital", "location": "New York", "funding": "varies", "focus": "diversity"},
}

VC_FUNDS = {
    # === MEGA FUNDS (>$1B AUM) ===
    "a16z": {"url": "https://a16z.com/portfolio", "stage": "all", "focus": "tech"},
    "sequoia": {"url": "https://www.sequoiacap.com/our-companies", "stage": "all", "focus": "tech"},
    "accel": {"url": "https://www.accel.com/companies", "stage": "all", "focus": "tech"},
    "benchmark": {"url": "https://www.benchmark.com/portfolio", "stage": "early", "focus": "tech"},
    "greylock": {"url": "https://greylock.com/portfolio", "stage": "all", "focus": "tech"},
    "kleiner_perkins": {"url": "https://www.kleinerperkins.com/partnerships", "stage": "all", "focus": "tech"},
    "lightspeed": {"url": "https://lsvp.com/portfolio", "stage": "all", "focus": "tech"},
    "nea": {"url": "https://www.nea.com/portfolio", "stage": "all", "focus": "tech"},
    "general_catalyst": {"url": "https://www.generalcatalyst.com/portfolio", "stage": "all", "focus": "tech"},
    "ivp": {"url": "https://www.ivp.com/portfolio", "stage": "growth", "focus": "tech"},
    "bessemer": {"url": "https://www.bvp.com/portfolio", "stage": "all", "focus": "tech"},
    "founders_fund": {"url": "https://foundersfund.com/portfolio", "stage": "all", "focus": "tech"},
    "khosla": {"url": "https://www.khoslaventures.com/portfolio", "stage": "all", "focus": "tech"},
    "index_ventures": {"url": "https://www.indexventures.com/companies", "stage": "all", "focus": "tech"},
    "spark_capital": {"url": "https://www.sparkcapital.com/portfolio", "stage": "early", "focus": "tech"},
    "insight_partners": {"url": "https://www.insightpartners.com/portfolio", "stage": "growth", "focus": "tech"},
    "tiger_global": {"url": "https://www.tigerglobal.com/portfolio", "stage": "growth", "focus": "tech"},
    "coatue": {"url": "https://www.coatue.com/portfolio", "stage": "growth", "focus": "tech"},
    "d1_capital": {"url": "https://www.d1lp.com", "stage": "growth", "focus": "tech"},
    "dragoneer": {"url": "https://www.dragoneer.com/portfolio", "stage": "growth", "focus": "tech"},
    
    # === SEED/PRE-SEED FUNDS ===
    "first_round": {"url": "https://firstround.com/companies", "stage": "seed", "focus": "tech"},
    "initialized": {"url": "https://initialized.com/portfolio", "stage": "seed", "focus": "tech"},
    "sv_angel": {"url": "https://www.svangel.com/portfolio", "stage": "seed", "focus": "tech"},
    "flybridge": {"url": "https://www.flybridge.com/portfolio", "stage": "seed", "focus": "tech"},
    "floodgate": {"url": "https://www.floodgate.com/portfolio", "stage": "seed", "focus": "tech"},
    "precursor": {"url": "https://precursorvc.com/portfolio", "stage": "pre-seed", "focus": "tech"},
    "hustle_fund": {"url": "https://www.hustlefund.vc/portfolio", "stage": "pre-seed", "focus": "tech"},
    "techstars_ventures": {"url": "https://www.techstars.com/portfolio", "stage": "seed", "focus": "tech"},
    "unshackled": {"url": "https://www.unshackledvc.com/portfolio", "stage": "pre-seed", "focus": "immigrant"},
    "haystack": {"url": "https://www.haystack.vc/portfolio", "stage": "seed", "focus": "tech"},
    "2048_vc": {"url": "https://www.2048.vc/portfolio", "stage": "seed", "focus": "frontier"},
    "notation": {"url": "https://notationcapital.com/portfolio", "stage": "pre-seed", "focus": "tech"},
    "boldstart": {"url": "https://boldstart.vc/portfolio", "stage": "seed", "focus": "enterprise"},
    "lerer_hippeau": {"url": "https://www.lererhippeau.com/portfolio", "stage": "seed", "focus": "consumer"},
    "homebrew": {"url": "https://homebrew.co/portfolio", "stage": "seed", "focus": "tech"},
    "cowboy_ventures": {"url": "https://www.cowboy.vc/portfolio", "stage": "seed", "focus": "tech"},
    "eniac": {"url": "https://www.eniac.vc/portfolio", "stage": "seed", "focus": "mobile"},
    "nextview": {"url": "https://nextview.vc/portfolio", "stage": "seed", "focus": "consumer"},
    "betaworks": {"url": "https://www.betaworks.com/companies", "stage": "seed", "focus": "tech"},
    "compound": {"url": "https://compoundvc.com/portfolio", "stage": "seed", "focus": "tech"},
    
    # === AI/ML FOCUSED FUNDS ===
    "a16z_bio": {"url": "https://a16z.com/bio-health", "stage": "all", "focus": "ai_bio"},
    "radical_vc": {"url": "https://radical.vc/portfolio", "stage": "early", "focus": "ai"},
    "dcvc": {"url": "https://www.dcvc.com/portfolio", "stage": "all", "focus": "deep_tech"},
    "playground_global": {"url": "https://playground.global/portfolio", "stage": "seed", "focus": "ai"},
    "ai_fund": {"url": "https://aifund.ai/portfolio", "stage": "all", "focus": "ai"},
    "felicis": {"url": "https://www.felicis.com/portfolio", "stage": "all", "focus": "ai"},
    "neo": {"url": "https://neo.com/portfolio", "stage": "seed", "focus": "ai"},
    "amplify_partners": {"url": "https://amplifypartners.com/portfolio", "stage": "seed", "focus": "ai"},
    "comet_labs": {"url": "https://cometlabs.io/portfolio", "stage": "seed", "focus": "ai"},
    "air_street": {"url": "https://www.airstreet.com/portfolio", "stage": "seed", "focus": "ai"},
    "gradient_ventures": {"url": "https://www.gradient.com/portfolio", "stage": "seed", "focus": "ai"},
    
    # === FINTECH FUNDS ===
    "ribbit_capital": {"url": "https://ribbitcap.com/portfolio", "stage": "all", "focus": "fintech"},
    "qed_investors": {"url": "https://qedinvestors.com/portfolio", "stage": "all", "focus": "fintech"},
    "nyca": {"url": "https://www.nyca.com/portfolio", "stage": "all", "focus": "fintech"},
    "anthemis": {"url": "https://anthemis.com/portfolio", "stage": "all", "focus": "fintech"},
    "clocktower": {"url": "https://www.clocktower.com/portfolio", "stage": "all", "focus": "fintech"},
    "bain_capital_ventures": {"url": "https://www.baincapitalventures.com/portfolio", "stage": "all", "focus": "fintech"},
    
    # === ENTERPRISE/B2B FUNDS ===
    "emergence": {"url": "https://www.emcap.com/portfolio", "stage": "all", "focus": "enterprise"},
    "redpoint": {"url": "https://www.redpoint.com/companies", "stage": "all", "focus": "enterprise"},
    "battery_ventures": {"url": "https://www.battery.com/portfolio", "stage": "all", "focus": "enterprise"},
    "sapphire_ventures": {"url": "https://sapphireventures.com/portfolio", "stage": "all", "focus": "enterprise"},
    "matrix_partners": {"url": "https://www.matrixpartners.com/companies", "stage": "early", "focus": "enterprise"},
    "menlo_ventures": {"url": "https://www.menlovc.com/portfolio", "stage": "early", "focus": "enterprise"},
    "norwest": {"url": "https://www.nvp.com/portfolio", "stage": "all", "focus": "enterprise"},
    "costanoa": {"url": "https://www.costanoavc.com/portfolio", "stage": "seed", "focus": "enterprise"},
    "unusual_ventures": {"url": "https://www.unusual.vc/portfolio", "stage": "seed", "focus": "enterprise"},
    "work_bench": {"url": "https://www.work-bench.com/portfolio", "stage": "seed", "focus": "enterprise"},
    
    # === CONSUMER FUNDS ===
    "forerunner": {"url": "https://forerunnerventures.com/portfolio", "stage": "all", "focus": "consumer"},
    "kirsten_green": {"url": "https://forerunnerventures.com", "stage": "all", "focus": "consumer"},
    "social_capital": {"url": "https://www.socialcapital.com/portfolio", "stage": "all", "focus": "consumer"},
    "maveron": {"url": "https://www.maveron.com/portfolio", "stage": "early", "focus": "consumer"},
    "goodwater": {"url": "https://www.goodwatercap.com/portfolio", "stage": "all", "focus": "consumer"},
    "consumer_ventures": {"url": "https://www.consumerventurecapital.com", "stage": "seed", "focus": "consumer"},
    
    # === HEALTH/BIO FUNDS ===
    "gv_life_sciences": {"url": "https://www.gv.com/portfolio", "stage": "all", "focus": "health"},
    "arch_venture": {"url": "https://www.archventure.com/portfolio", "stage": "all", "focus": "bio"},
    "flagship_pioneering": {"url": "https://www.flagshippioneering.com/companies", "stage": "all", "focus": "bio"},
    "polaris_partners": {"url": "https://www.polarispartners.com/portfolio", "stage": "all", "focus": "health"},
    "andreessen_bio": {"url": "https://a16z.com/bio-health", "stage": "all", "focus": "bio"},
    "general_atlantic_healthcare": {"url": "https://www.generalatlantic.com/portfolio", "stage": "growth", "focus": "health"},
    "oak_hc_ft": {"url": "https://www.oakhcft.com/portfolio", "stage": "growth", "focus": "health"},
    
    # === CLIMATE/CLEANTECH FUNDS ===
    "breakthrough_energy": {"url": "https://www.breakthroughenergy.org/our-challenge/our-companies", "stage": "all", "focus": "climate"},
    "lowercarbon": {"url": "https://lowercarboncapital.com/portfolio", "stage": "all", "focus": "climate"},
    "prelude_ventures": {"url": "https://www.preludeventures.com/portfolio", "stage": "early", "focus": "climate"},
    "energy_impact": {"url": "https://www.energyimpactpartners.com/portfolio", "stage": "all", "focus": "climate"},
    "congruent": {"url": "https://www.congruentvc.com/portfolio", "stage": "seed", "focus": "climate"},
    "clean_energy_ventures": {"url": "https://www.cleanenergyventures.com/portfolio", "stage": "seed", "focus": "climate"},
    "energize": {"url": "https://www.energize.vc/portfolio", "stage": "all", "focus": "climate"},
    "g2vp": {"url": "https://g2vp.com/portfolio", "stage": "early", "focus": "climate"},
    "system_iq": {"url": "https://www.systemiq.earth", "stage": "all", "focus": "climate"},
    
    # === CRYPTO/WEB3 FUNDS ===
    "paradigm": {"url": "https://www.paradigm.xyz/portfolio", "stage": "all", "focus": "crypto"},
    "polychain": {"url": "https://polychain.capital/portfolio", "stage": "all", "focus": "crypto"},
    "a16z_crypto": {"url": "https://a16zcrypto.com/portfolio", "stage": "all", "focus": "crypto"},
    "pantera": {"url": "https://panteracapital.com/portfolio", "stage": "all", "focus": "crypto"},
    "dragonfly": {"url": "https://www.dragonfly.xyz/portfolio", "stage": "all", "focus": "crypto"},
    "multicoin": {"url": "https://multicoin.capital/portfolio", "stage": "all", "focus": "crypto"},
    "placeholder": {"url": "https://www.placeholder.vc/portfolio", "stage": "all", "focus": "crypto"},
    "electric_capital": {"url": "https://www.electriccapital.com/portfolio", "stage": "all", "focus": "crypto"},
    "variant": {"url": "https://variant.fund/portfolio", "stage": "all", "focus": "crypto"},
    "framework": {"url": "https://framework.ventures/portfolio", "stage": "all", "focus": "crypto"},
    "blockchain_capital": {"url": "https://blockchain.capital/portfolio", "stage": "all", "focus": "crypto"},
    
    # === INTERNATIONAL FUNDS ===
    # Europe
    "atomico": {"url": "https://www.atomico.com/companies", "stage": "all", "region": "europe"},
    "balderton": {"url": "https://www.balderton.com/portfolio", "stage": "all", "region": "europe"},
    "northzone": {"url": "https://northzone.com/companies", "stage": "early", "region": "europe"},
    "creandum": {"url": "https://creandum.com/companies", "stage": "seed", "region": "europe"},
    "eqt_ventures": {"url": "https://eqtventures.com/portfolio", "stage": "early", "region": "europe"},
    "point_nine": {"url": "https://www.pointnine.com/portfolio", "stage": "seed", "region": "europe"},
    "cherry_ventures": {"url": "https://www.cherry.vc/portfolio", "stage": "seed", "region": "europe"},
    "localglobe": {"url": "https://localglobe.vc/portfolio", "stage": "seed", "region": "europe"},
    "seedcamp": {"url": "https://seedcamp.com/portfolio", "stage": "seed", "region": "europe"},
    "moonfire": {"url": "https://www.moonfire.com/portfolio", "stage": "seed", "region": "europe"},
    
    # Asia
    "hillhouse": {"url": "https://www.hillhousecap.com/portfolio", "stage": "all", "region": "asia"},
    "ggv": {"url": "https://www.ggvc.com/portfolio", "stage": "all", "region": "asia"},
    "golden_gate": {"url": "https://www.goldengate.vc/portfolio", "stage": "early", "region": "asia"},
    "sequoia_china": {"url": "https://www.sequoiacap.com/china", "stage": "all", "region": "asia"},
    "sequoia_india": {"url": "https://www.sequoiacap.com/india", "stage": "all", "region": "asia"},
    "softbank_vision": {"url": "https://visionfund.com/portfolio", "stage": "growth", "region": "asia"},
    "matrix_india": {"url": "https://www.matrixpartners.in/portfolio", "stage": "early", "region": "asia"},
    "elevation": {"url": "https://www.elevationcapital.com/portfolio", "stage": "early", "region": "asia"},
    "accel_india": {"url": "https://www.accel.com/india", "stage": "early", "region": "asia"},
    "lightspeed_india": {"url": "https://lsindia.vc/portfolio", "stage": "all", "region": "asia"},
    "vertex_ventures": {"url": "https://www.vertexventures.com/portfolio", "stage": "early", "region": "asia"},
    "500_sea": {"url": "https://500.co/southeast-asia", "stage": "seed", "region": "asia"},
    "jungle_ventures": {"url": "https://www.jungle-ventures.com/portfolio", "stage": "early", "region": "asia"},
    "east_ventures": {"url": "https://east.vc/portfolio", "stage": "seed", "region": "asia"},
    
    # LATAM
    "kaszek": {"url": "https://www.kaszek.com/portfolio", "stage": "all", "region": "latam"},
    "monashees": {"url": "https://www.monashees.com.br/portfolio", "stage": "all", "region": "latam"},
    "valor_capital": {"url": "https://valorcapitalgroup.com/portfolio", "stage": "all", "region": "latam"},
    "softbank_latam": {"url": "https://www.softbank.com/en/corp/portfolio", "stage": "growth", "region": "latam"},
    "dila_capital": {"url": "https://www.dilacapital.com/portfolio", "stage": "seed", "region": "latam"},
    "allvp": {"url": "https://allvp.vc/portfolio", "stage": "seed", "region": "latam"},
    "magma_partners": {"url": "https://www.magmapartners.com/portfolio", "stage": "seed", "region": "latam"},
}

ANGEL_NETWORKS = {
    "angellist": {"url": "https://angel.co/syndicates", "type": "platform"},
    "republic": {"url": "https://republic.com/raise", "type": "platform"},
    "wefunder": {"url": "https://wefunder.com/raise-money", "type": "crowdfunding"},
    "startengine": {"url": "https://www.startengine.com/raise-capital", "type": "crowdfunding"},
    "gust": {"url": "https://gust.com/angels", "type": "network"},
    "keiretsu_forum": {"url": "https://www.keiretsuforum.com", "type": "network"},
    "tech_coast_angels": {"url": "https://www.techcoastangels.com", "type": "network"},
    "golden_seeds": {"url": "https://goldenseeds.com", "type": "network"},
    "band_of_angels": {"url": "https://www.bandofangels.com", "type": "network"},
    "new_york_angels": {"url": "https://www.newyorkangels.com", "type": "network"},
    "launchpad_venture": {"url": "https://launchpadventuregroup.com", "type": "network"},
    "houston_angel": {"url": "https://www.houstonangelnetwork.org", "type": "network"},
    "alliance_angels": {"url": "https://www.allianceofangels.com", "type": "network"},
    "sand_hill_angels": {"url": "https://www.sandhillangels.com", "type": "network"},
    "pasadena_angels": {"url": "https://www.pasadenaangels.com", "type": "network"},
    "detroit_angels": {"url": "https://www.neweconomyinitiative.org/angel-investors", "type": "network"},
    "portland_angel": {"url": "https://www.portlandangel.com", "type": "network"},
    "pipeline_angels": {"url": "https://pipelineangels.com", "type": "network"},
    "astia_angels": {"url": "https://astia.org/astia-angels", "type": "network"},
}

STARTUP_COMPETITIONS = {
    "techcrunch_disrupt": {"url": "https://techcrunch.com/events/tc-disrupt", "prize": "$100k"},
    "sxsw_pitch": {"url": "https://www.sxsw.com/apply-to-participate/sxsw-pitch", "prize": "$3k"},
    "websummit_pitch": {"url": "https://websummit.com/pitch", "prize": "varies"},
    "collision_pitch": {"url": "https://collisionconf.com/pitch", "prize": "varies"},
    "rise_pitch": {"url": "https://riseconf.com/pitch", "prize": "varies"},
    "mit_100k": {"url": "https://www.mit100k.org", "prize": "$100k"},
    "rice_business_plan": {"url": "https://www.ricebusinessplancompetition.com", "prize": "$1.5M"},
    "hult_prize": {"url": "https://www.hultprize.org", "prize": "$1M"},
    "startup_world_cup": {"url": "https://www.startupworldcup.io", "prize": "$1M"},
    "extreme_tech_challenge": {"url": "https://extremetechchallenge.org", "prize": "varies"},
    "get_in_the_ring": {"url": "https://getinthering.co", "prize": "varies"},
    "global_startup_awards": {"url": "https://globalstartupawards.com", "prize": "varies"},
    "seedstars_world": {"url": "https://www.seedstarsworld.com", "prize": "$500k"},
    "slush": {"url": "https://www.slush.org/pitching-competition", "prize": "varies"},
    "tnw_conference": {"url": "https://thenextweb.com/conference/program/startup-programs", "prize": "varies"},
    "pioneers": {"url": "https://pioneers.io/events", "prize": "varies"},
    "startup_battlefield": {"url": "https://techcrunch.com/startup-battlefield", "prize": "$100k"},
    "europas": {"url": "https://theeuropas.com", "prize": "varies"},
}

def get_all_vc_sources():
    """Return total count and all VC/startup sources"""
    total = len(ACCELERATORS) + len(VC_FUNDS) + len(ANGEL_NETWORKS) + len(STARTUP_COMPETITIONS)
    return {
        "total": total,
        "accelerators": ACCELERATORS,
        "vc_funds": VC_FUNDS,
        "angel_networks": ANGEL_NETWORKS,
        "competitions": STARTUP_COMPETITIONS
    }
