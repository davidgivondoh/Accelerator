"""
Comprehensive Opportunity Sources Database
==========================================
100+ sources for jobs, grants, fellowships, competitions, and more.
Target: 100 applications per day
"""

OPPORTUNITY_SOURCES = {
    # ═══════════════════════════════════════════════════════════════
    # JOB BOARDS - Major Platforms
    # ═══════════════════════════════════════════════════════════════
    "job_boards": {
        "linkedin": {
            "name": "LinkedIn Jobs",
            "url": "https://www.linkedin.com/jobs",
            "api": "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search",
            "type": "jobs",
            "frequency": "hourly",
            "volume": "high",
            "apply_method": "easy_apply"
        },
        "indeed": {
            "name": "Indeed",
            "url": "https://www.indeed.com",
            "api": "https://www.indeed.com/jobs",
            "type": "jobs",
            "frequency": "hourly",
            "volume": "high",
            "apply_method": "direct"
        },
        "glassdoor": {
            "name": "Glassdoor",
            "url": "https://www.glassdoor.com/Job",
            "type": "jobs",
            "frequency": "daily",
            "volume": "high",
            "apply_method": "direct"
        },
        "ziprecruiter": {
            "name": "ZipRecruiter",
            "url": "https://www.ziprecruiter.com/jobs",
            "type": "jobs",
            "frequency": "daily",
            "volume": "high",
            "apply_method": "one_click"
        },
        "monster": {
            "name": "Monster",
            "url": "https://www.monster.com",
            "type": "jobs",
            "frequency": "daily",
            "volume": "medium",
            "apply_method": "direct"
        },
        "careerbuilder": {
            "name": "CareerBuilder",
            "url": "https://www.careerbuilder.com",
            "type": "jobs",
            "frequency": "daily",
            "volume": "medium",
            "apply_method": "direct"
        },
        "dice": {
            "name": "Dice (Tech Jobs)",
            "url": "https://www.dice.com/jobs",
            "type": "tech_jobs",
            "frequency": "daily",
            "volume": "medium",
            "apply_method": "direct"
        },
        "simplyhired": {
            "name": "SimplyHired",
            "url": "https://www.simplyhired.com",
            "type": "jobs",
            "frequency": "daily",
            "volume": "medium",
            "apply_method": "direct"
        },
    },

    # ═══════════════════════════════════════════════════════════════
    # FREELANCE PLATFORMS - Gig Economy
    # ═══════════════════════════════════════════════════════════════
    "freelance_platforms": {
        "upwork": {
            "name": "Upwork",
            "url": "https://upwork.com",
            "type": "freelance_platform",
            "frequency": "hourly",
            "volume": "high",
            "apply_method": "proposal"
        },
        "fiverr": {
            "name": "Fiverr",
            "url": "https://fiverr.com",
            "type": "freelance_platform",
            "frequency": "hourly",
            "volume": "high",
            "apply_method": "gig_listing"
        },
        "guru": {
            "name": "Guru",
            "url": "https://guru.com",
            "type": "freelance_platform",
            "frequency": "daily",
            "volume": "medium",
            "apply_method": "proposal"
        },
        "peopleperhour": {
            "name": "PeoplePerHour",
            "url": "https://peopleperhour.com",
            "type": "freelance_platform",
            "frequency": "daily",
            "volume": "medium",
            "apply_method": "proposal"
        },
        "freelancer": {
            "name": "Freelancer",
            "url": "https://freelancer.com",
            "type": "freelance_platform",
            "frequency": "hourly",
            "volume": "high",
            "apply_method": "proposal"
        },
        "toptal": {
            "name": "Toptal",
            "url": "https://toptal.com",
            "type": "freelance_platform",
            "frequency": "rolling",
            "volume": "low",
            "apply_method": "screening",
            "tier": "premium"
        },
        "catalant": {
            "name": "Catalant",
            "url": "https://catalant.com",
            "type": "consulting_platform",
            "frequency": "rolling",
            "volume": "low",
            "apply_method": "screening",
            "tier": "premium"
        },
        "outsourcingangel": {
            "name": "Outsourcing Angel",
            "url": "https://outsourcingangel.com",
            "type": "freelance_platform",
            "frequency": "daily",
            "volume": "low",
            "apply_method": "proposal"
        },
        "freeup": {
            "name": "FreeUp",
            "url": "https://freeup.net",
            "type": "freelance_platform",
            "frequency": "rolling",
            "volume": "low",
            "apply_method": "screening"
        },
        "contra": {
            "name": "Contra",
            "url": "https://contra.com",
            "type": "freelance_platform",
            "frequency": "daily",
            "volume": "medium",
            "apply_method": "direct"
        },
        "malt": {
            "name": "Malt",
            "url": "https://malt.com",
            "type": "freelance_platform",
            "frequency": "daily",
            "volume": "medium",
            "apply_method": "proposal",
            "region": "europe"
        },
        "workana": {
            "name": "Workana",
            "url": "https://workana.com",
            "type": "freelance_platform",
            "frequency": "daily",
            "volume": "medium",
            "apply_method": "proposal",
            "region": "latin_america"
        },
        "truelancer": {
            "name": "Truelancer",
            "url": "https://truelancer.com",
            "type": "freelance_platform",
            "frequency": "daily",
            "volume": "medium",
            "apply_method": "proposal"
        },
        "99designs": {
            "name": "99designs",
            "url": "https://99designs.com",
            "type": "design_platform",
            "frequency": "daily",
            "volume": "medium",
            "apply_method": "contest",
            "specialty": "design"
        },
        "designcrowd": {
            "name": "DesignCrowd",
            "url": "https://designcrowd.com",
            "type": "design_platform",
            "frequency": "daily",
            "volume": "medium",
            "apply_method": "contest",
            "specialty": "design"
        },
        "crowdspring": {
            "name": "CrowdSpring",
            "url": "https://crowdspring.com",
            "type": "design_platform",
            "frequency": "daily",
            "volume": "medium",
            "apply_method": "contest",
            "specialty": "design"
        },
        "voices": {
            "name": "Voices.com",
            "url": "https://voices.com",
            "type": "voice_platform",
            "frequency": "daily",
            "volume": "medium",
            "apply_method": "audition",
            "specialty": "voice_talent"
        },
        "soundbetter": {
            "name": "SoundBetter",
            "url": "https://soundbetter.com",
            "type": "audio_platform",
            "frequency": "daily",
            "volume": "low",
            "apply_method": "direct",
            "specialty": "music_audio"
        },
    },

    # ═══════════════════════════════════════════════════════════════
    # TECH & STARTUP - Specialized Platforms
    # ═══════════════════════════════════════════════════════════════
    "tech_startup": {
        "wellfound": {
            "name": "Wellfound (AngelList)",
            "url": "https://wellfound.com/jobs",
            "api": "https://wellfound.com/api/jobs",
            "type": "startup_jobs",
            "frequency": "hourly",
            "volume": "high",
            "apply_method": "direct"
        },
        "ycombinator": {
            "name": "Y Combinator Jobs",
            "url": "https://www.workatastartup.com/jobs",
            "type": "startup_jobs",
            "frequency": "daily",
            "volume": "high",
            "apply_method": "direct"
        },
        "builtin": {
            "name": "Built In",
            "url": "https://builtin.com/jobs",
            "type": "tech_jobs",
            "frequency": "daily",
            "volume": "medium",
            "apply_method": "direct"
        },
        "techcrunch": {
            "name": "TechCrunch Jobs",
            "url": "https://techcrunch.com/jobs",
            "type": "tech_jobs",
            "frequency": "daily",
            "volume": "low",
            "apply_method": "direct"
        },
        "weworkremotely": {
            "name": "We Work Remotely",
            "url": "https://weworkremotely.com",
            "type": "remote_jobs",
            "frequency": "daily",
            "volume": "medium",
            "apply_method": "direct"
        },
        "remoteok": {
            "name": "Remote OK",
            "url": "https://remoteok.com",
            "api": "https://remoteok.com/api",
            "type": "remote_jobs",
            "frequency": "hourly",
            "volume": "medium",
            "apply_method": "direct"
        },
        "remoteco": {
            "name": "Remote.co",
            "url": "https://remote.co/remote-jobs",
            "type": "remote_jobs",
            "frequency": "daily",
            "volume": "medium",
            "apply_method": "direct"
        },
        "flexjobs": {
            "name": "FlexJobs",
            "url": "https://www.flexjobs.com",
            "type": "remote_jobs",
            "frequency": "daily",
            "volume": "medium",
            "apply_method": "direct"
        },
        "stackoverflow": {
            "name": "Stack Overflow Jobs",
            "url": "https://stackoverflow.com/jobs",
            "type": "tech_jobs",
            "frequency": "daily",
            "volume": "medium",
            "apply_method": "direct"
        },
        "github_jobs": {
            "name": "GitHub Jobs",
            "url": "https://github.com/topics/jobs",
            "type": "tech_jobs",
            "frequency": "daily",
            "volume": "low",
            "apply_method": "direct"
        },
        "hackernews": {
            "name": "Hacker News Jobs",
            "url": "https://news.ycombinator.com/jobs",
            "type": "startup_jobs",
            "frequency": "daily",
            "volume": "medium",
            "apply_method": "direct"
        },
        "workingnomads": {
            "name": "Working Nomads",
            "url": "https://workingnomads.co",
            "type": "remote_jobs",
            "frequency": "daily",
            "volume": "medium",
            "apply_method": "direct"
        },
        "remoters": {
            "name": "Remoters",
            "url": "https://remoters.net",
            "type": "remote_jobs",
            "frequency": "daily",
            "volume": "low",
            "apply_method": "direct"
        },
        "europeremotely": {
            "name": "Europe Remotely",
            "url": "https://europeremotely.com",
            "type": "remote_jobs",
            "frequency": "daily",
            "volume": "low",
            "apply_method": "direct",
            "region": "europe"
        },
        "skipthedrive": {
            "name": "Skip The Drive",
            "url": "https://skipthedrive.com",
            "type": "remote_jobs",
            "frequency": "daily",
            "volume": "low",
            "apply_method": "direct"
        },
        "jobspresso": {
            "name": "Jobspresso",
            "url": "https://jobspresso.co",
            "type": "remote_jobs",
            "frequency": "daily",
            "volume": "low",
            "apply_method": "direct"
        },
        "remotewoman": {
            "name": "Remote Woman",
            "url": "https://remotewoman.com",
            "type": "remote_jobs",
            "frequency": "daily",
            "volume": "low",
            "apply_method": "direct",
            "diversity": "women"
        },
        "powertofly": {
            "name": "PowerToFly",
            "url": "https://powertofly.com",
            "type": "remote_jobs",
            "frequency": "daily",
            "volume": "medium",
            "apply_method": "direct",
            "diversity": "women"
        },
        "landingjobs": {
            "name": "Landing.jobs",
            "url": "https://landing.jobs",
            "type": "tech_jobs",
            "frequency": "daily",
            "volume": "medium",
            "apply_method": "direct",
            "region": "europe"
        },
        "justremote": {
            "name": "JustRemote",
            "url": "https://justremote.co",
            "type": "remote_jobs",
            "frequency": "daily",
            "volume": "medium",
            "apply_method": "direct"
        },
        "dynamitejobs": {
            "name": "DynamiteJobs",
            "url": "https://dynamitejobs.com",
            "type": "remote_jobs",
            "frequency": "daily",
            "volume": "low",
            "apply_method": "direct"
        },
        "remotive": {
            "name": "Remotive",
            "url": "https://remotive.io",
            "type": "remote_jobs",
            "frequency": "daily",
            "volume": "medium",
            "apply_method": "direct"
        },
        "hubstaff_jobs": {
            "name": "Hubstaff Jobs",
            "url": "https://hubstaff.com/jobs",
            "type": "remote_jobs",
            "frequency": "daily",
            "volume": "low",
            "apply_method": "direct"
        },
        "themuse_remote": {
            "name": "The Muse Remote",
            "url": "https://themuse.com/jobs/remote",
            "type": "remote_jobs",
            "frequency": "daily",
            "volume": "medium",
            "apply_method": "direct"
        },
        "virtualvocations": {
            "name": "Virtual Vocations",
            "url": "https://virtualvocations.com",
            "type": "remote_jobs",
            "frequency": "daily",
            "volume": "medium",
            "apply_method": "direct"
        },
        "workingnotworking": {
            "name": "Working Not Working",
            "url": "https://workingnotworking.com",
            "type": "creative_jobs",
            "frequency": "daily",
            "volume": "medium",
            "apply_method": "direct",
            "specialty": "creative"
        },
        "gun_io": {
            "name": "Gun.io",
            "url": "https://gun.io",
            "type": "freelance_dev",
            "frequency": "rolling",
            "volume": "low",
            "apply_method": "direct",
            "specialty": "developers"
        },
        "arc_dev": {
            "name": "Arc.dev",
            "url": "https://arc.dev",
            "type": "freelance_dev",
            "frequency": "rolling",
            "volume": "medium",
            "apply_method": "direct",
            "specialty": "developers"
        },
        "lemon_io": {
            "name": "Lemon.io",
            "url": "https://lemon.io",
            "type": "freelance_dev",
            "frequency": "rolling",
            "volume": "low",
            "apply_method": "direct",
            "specialty": "developers"
        },
        "braintrust": {
            "name": "Braintrust",
            "url": "https://braintrust.com",
            "type": "freelance_platform",
            "frequency": "rolling",
            "volume": "medium",
            "apply_method": "direct"
        },
        "uplifted_ai": {
            "name": "Uplifted.ai",
            "url": "https://uplifted.ai",
            "type": "ai_jobs",
            "frequency": "daily",
            "volume": "low",
            "apply_method": "direct",
            "specialty": "artificial_intelligence"
        },
        "ai_jobs_net": {
            "name": "AI Jobs",
            "url": "https://ai-jobs.net",
            "type": "ai_jobs",
            "frequency": "daily",
            "volume": "medium",
            "apply_method": "direct",
            "specialty": "artificial_intelligence"
        },
        "remoteafrica": {
            "name": "Remote Africa",
            "url": "https://remoteafrica.io",
            "type": "remote_jobs",
            "frequency": "daily",
            "volume": "low",
            "apply_method": "direct",
            "region": "africa"
        },
        "africaremotejobs": {
            "name": "Africa Remote Jobs",
            "url": "https://africaremotejobs.com",
            "type": "remote_jobs",
            "frequency": "daily",
            "volume": "low",
            "apply_method": "direct",
            "region": "africa"
        },
        "remotejobs_africa": {
            "name": "Remote Jobs Africa",
            "url": "https://remotejobs.africa",
            "type": "remote_jobs",
            "frequency": "daily",
            "volume": "low",
            "apply_method": "direct",
            "region": "africa"
        },
        "jobinja_remote": {
            "name": "Jobinja Remote",
            "url": "https://jobinja.com/remote",
            "type": "remote_jobs",
            "frequency": "daily",
            "volume": "low",
            "apply_method": "direct",
            "region": "middle_east"
        },
        "jobboxx": {
            "name": "JobBoxx",
            "url": "https://jobboxx.com",
            "type": "remote_jobs",
            "frequency": "daily",
            "volume": "low",
            "apply_method": "direct"
        },
    },

    # ═══════════════════════════════════════════════════════════════
    # AI & ML SPECIFIC
    # ═══════════════════════════════════════════════════════════════
    "ai_ml": {
        "ai_jobs": {
            "name": "AI Jobs",
            "url": "https://aijobs.net",
            "type": "ai_jobs",
            "frequency": "daily",
            "volume": "medium",
            "apply_method": "direct"
        },
        "ml_jobs": {
            "name": "Machine Learning Jobs",
            "url": "https://www.machinelearningjobs.com",
            "type": "ml_jobs",
            "frequency": "daily",
            "volume": "low",
            "apply_method": "direct"
        },
        "deeplearning_ai": {
            "name": "DeepLearning.AI Jobs",
            "url": "https://www.deeplearning.ai/jobs",
            "type": "ai_jobs",
            "frequency": "weekly",
            "volume": "low",
            "apply_method": "direct"
        },
    },

    # ═══════════════════════════════════════════════════════════════
    # FREELANCE & GIG PLATFORMS
    # ═══════════════════════════════════════════════════════════════
    "freelance": {
        "upwork": {
            "name": "Upwork",
            "url": "https://www.upwork.com/nx/find-work",
            "type": "freelance",
            "frequency": "hourly",
            "volume": "high",
            "apply_method": "proposal"
        },
        "toptal": {
            "name": "Toptal",
            "url": "https://www.toptal.com/talent/apply",
            "type": "freelance",
            "frequency": "daily",
            "volume": "low",
            "apply_method": "application"
        },
        "fiverr": {
            "name": "Fiverr",
            "url": "https://www.fiverr.com",
            "type": "freelance",
            "frequency": "daily",
            "volume": "high",
            "apply_method": "gig"
        },
        "contra": {
            "name": "Contra",
            "url": "https://contra.com/opportunities",
            "type": "freelance",
            "frequency": "daily",
            "volume": "medium",
            "apply_method": "direct"
        },
        "freelancer": {
            "name": "Freelancer",
            "url": "https://www.freelancer.com/jobs",
            "type": "freelance",
            "frequency": "hourly",
            "volume": "high",
            "apply_method": "bid"
        },
        "guru": {
            "name": "Guru",
            "url": "https://www.guru.com/d/jobs",
            "type": "freelance",
            "frequency": "daily",
            "volume": "medium",
            "apply_method": "proposal"
        },
        "peopleperhour": {
            "name": "PeoplePerHour",
            "url": "https://www.peopleperhour.com/freelance-jobs",
            "type": "freelance",
            "frequency": "daily",
            "volume": "medium",
            "apply_method": "proposal"
        },
    },

    # ═══════════════════════════════════════════════════════════════
    # GRANTS & FUNDING
    # ═══════════════════════════════════════════════════════════════
    "grants": {
        "grants_gov": {
            "name": "Grants.gov",
            "url": "https://www.grants.gov/search-grants",
            "api": "https://www.grants.gov/grantsws/rest/opportunities/search",
            "type": "government_grants",
            "frequency": "daily",
            "volume": "high",
            "apply_method": "application"
        },
        "nsf": {
            "name": "NSF Grants",
            "url": "https://www.nsf.gov/funding",
            "type": "research_grants",
            "frequency": "weekly",
            "volume": "medium",
            "apply_method": "application"
        },
        "nih": {
            "name": "NIH Grants",
            "url": "https://grants.nih.gov/funding/index.htm",
            "type": "research_grants",
            "frequency": "weekly",
            "volume": "medium",
            "apply_method": "application"
        },
        "doe": {
            "name": "DOE Funding",
            "url": "https://www.energy.gov/science/office-science-funding-opportunities",
            "type": "research_grants",
            "frequency": "weekly",
            "volume": "low",
            "apply_method": "application"
        },
        "darpa": {
            "name": "DARPA",
            "url": "https://www.darpa.mil/work-with-us/opportunities",
            "type": "research_grants",
            "frequency": "weekly",
            "volume": "low",
            "apply_method": "application"
        },
        "sbir": {
            "name": "SBIR/STTR",
            "url": "https://www.sbir.gov/sbirsearch/topic/current",
            "type": "small_business_grants",
            "frequency": "weekly",
            "volume": "medium",
            "apply_method": "application"
        },
        "foundation_directory": {
            "name": "Foundation Directory",
            "url": "https://fconline.foundationcenter.org",
            "type": "foundation_grants",
            "frequency": "daily",
            "volume": "medium",
            "apply_method": "application"
        },
        "instrumentl": {
            "name": "Instrumentl",
            "url": "https://www.instrumentl.com",
            "type": "grants",
            "frequency": "daily",
            "volume": "medium",
            "apply_method": "application"
        },
        "global_innovation_fund": {
            "name": "Global Innovation Fund",
            "url": "https://globalinnovationfund.org",
            "type": "innovation_fund",
            "frequency": "rolling",
            "volume": "low",
            "apply_method": "application",
            "tier": "tier1",
            "region": "global"
        },
        "globalgiving": {
            "name": "GlobalGiving",
            "url": "https://globalgiving.org",
            "type": "crowdfunding_platform",
            "frequency": "rolling",
            "volume": "high",
            "apply_method": "platform",
            "tier": "platform",
            "region": "global"
        },
        "un_foundation": {
            "name": "UN Foundation",
            "url": "https://unfoundation.org",
            "type": "foundation_grants",
            "frequency": "rolling",
            "volume": "medium",
            "apply_method": "application",
            "tier": "tier1",
            "region": "global"
        },
        "gates_foundation": {
            "name": "Bill & Melinda Gates Foundation",
            "url": "https://gatesfoundation.org",
            "type": "foundation_grants",
            "frequency": "rolling",
            "volume": "medium",
            "apply_method": "application",
            "tier": "tier1",
            "region": "global",
            "focus": "global_health_development"
        },
        "schmidt_ventures": {
            "name": "Schmidt Ventures",
            "url": "https://schmidtventures.com",
            "type": "venture_philanthropy",
            "frequency": "rolling",
            "volume": "low",
            "apply_method": "application",
            "tier": "tier1",
            "region": "global"
        },
        "schmidt_futures": {
            "name": "Schmidt Futures",
            "url": "https://schmidtfutures.com",
            "type": "fellowship_foundation",
            "frequency": "rolling",
            "volume": "low",
            "apply_method": "application",
            "tier": "tier1",
            "region": "global",
            "focus": "science_technology"
        },
        "ford_foundation": {
            "name": "Ford Foundation",
            "url": "https://fordfoundation.org",
            "type": "foundation_grants",
            "frequency": "rolling",
            "volume": "medium",
            "apply_method": "application",
            "tier": "tier1",
            "region": "global",
            "focus": "social_justice"
        },
    },

    # ═══════════════════════════════════════════════════════════════
    # SCHOLARSHIPS & FELLOWSHIPS (GLOBAL) - 120+ SITES
    # ═══════════════════════════════════════════════════════════════
    "scholarships": {
        # MAJOR SCHOLARSHIP PLATFORMS & DATABASES
        "scholarships_com": {
            "name": "Scholarships.com",
            "url": "https://scholarships.com",
            "type": "scholarship_platform",
            "frequency": "daily",
            "volume": "high",
            "apply_method": "direct",
            "tier": "platform",
            "region": "global"
        },
        "scholars4dev": {
            "name": "Scholars4Dev",
            "url": "https://scholars4dev.com",
            "type": "scholarship_platform",
            "frequency": "daily",
            "volume": "high",
            "apply_method": "direct",
            "tier": "platform",
            "region": "global"
        },
        "opportunity_desk": {
            "name": "OpportunityDesk",
            "url": "https://opportunitydesk.org",
            "type": "scholarship_platform",
            "frequency": "daily",
            "volume": "high",
            "apply_method": "direct",
            "tier": "platform",
            "region": "global"
        },
        "scholarship_portal": {
            "name": "ScholarshipPortal",
            "url": "https://scholarshipportal.com",
            "type": "scholarship_platform",
            "frequency": "daily",
            "volume": "high",
            "apply_method": "direct",
            "tier": "platform",
            "region": "global"
        },
        "scholly": {
            "name": "Scholly",
            "url": "https://scholly.com",
            "type": "scholarship_platform",
            "frequency": "daily",
            "volume": "medium",
            "apply_method": "app",
            "tier": "platform",
            "region": "us"
        },
        "fastweb": {
            "name": "Fastweb",
            "url": "https://fastweb.com",
            "type": "scholarship_platform",
            "frequency": "daily",
            "volume": "high",
            "apply_method": "direct",
            "tier": "platform",
            "region": "us"
        },

        # TIER 1 - PRESTIGIOUS GOVERNMENT & INSTITUTIONAL SCHOLARSHIPS
        "chevening": {
            "name": "Chevening Scholarships",
            "url": "https://chevening.org",
            "type": "government_scholarship",
            "frequency": "yearly",
            "volume": "low",
            "apply_method": "application",
            "award": "Full funding",
            "tier": "tier1",
            "region": "uk"
        },
        "commonwealth_uk": {
            "name": "Commonwealth Scholarships UK",
            "url": "https://cscuk.fcdo.gov.uk",
            "type": "government_scholarship",
            "frequency": "yearly",
            "volume": "medium",
            "apply_method": "application",
            "award": "Full funding",
            "tier": "tier1",
            "region": "commonwealth"
        },
        "fulbright": {
            "name": "Fulbright Program",
            "url": "https://fulbrightprogram.org",
            "type": "government_scholarship",
            "frequency": "yearly",
            "volume": "medium",
            "apply_method": "application",
            "award": "Full funding",
            "tier": "tier1",
            "region": "global"
        },
        "daad": {
            "name": "DAAD Germany",
            "url": "https://daad.de/en",
            "type": "government_scholarship",
            "frequency": "biannual",
            "volume": "high",
            "apply_method": "application",
            "award": "€850-€1,200/month",
            "tier": "tier1",
            "region": "germany"
        },
        "erasmus_plus": {
            "name": "Erasmus+ Programme",
            "url": "https://erasmus-plus.ec.europa.eu",
            "type": "government_scholarship",
            "frequency": "yearly",
            "volume": "high",
            "apply_method": "university",
            "award": "€150-€700/month",
            "tier": "tier1",
            "region": "europe"
        },
        
        # TIER 1 - ELITE UNIVERSITY SCHOLARSHIPS
        "gates_cambridge": {
            "name": "Gates Cambridge Scholarships",
            "url": "https://gatescambridge.org",
            "type": "university_scholarship",
            "frequency": "yearly",
            "volume": "low",
            "apply_method": "application",
            "award": "Full funding",
            "tier": "tier1",
            "institution": "cambridge"
        },
        "rhodes_scholarship": {
            "name": "Rhodes Scholarship",
            "url": "https://rhodeshouse.ox.ac.uk",
            "type": "university_scholarship",
            "frequency": "yearly",
            "volume": "low",
            "apply_method": "application",
            "award": "Full funding",
            "tier": "tier1",
            "institution": "oxford"
        },
        "clarendon_oxford": {
            "name": "Clarendon Scholarships",
            "url": "https://oxford-university.scholarships",
            "type": "university_scholarship",
            "frequency": "yearly",
            "volume": "low",
            "apply_method": "application",
            "award": "Full funding",
            "tier": "tier1",
            "institution": "oxford"
        },
        "knight_hennessy": {
            "name": "Knight-Hennessy Scholars",
            "url": "https://knight-hennessy.stanford.edu",
            "type": "university_scholarship",
            "frequency": "yearly",
            "volume": "low",
            "apply_method": "application",
            "award": "Full funding",
            "tier": "tier1",
            "institution": "stanford"
        },
        "schwarzman_scholars": {
            "name": "Schwarzman Scholars",
            "url": "https://schwarzmanscholars.org",
            "type": "university_scholarship",
            "frequency": "yearly",
            "volume": "low",
            "apply_method": "application",
            "award": "Full funding",
            "tier": "tier1",
            "institution": "tsinghua"
        },
        "yenching_academy": {
            "name": "Yenching Academy",
            "url": "https://yenchingacademy.pku.edu.cn",
            "type": "university_scholarship",
            "frequency": "yearly",
            "volume": "low",
            "apply_method": "application",
            "award": "Full funding",
            "tier": "tier1",
            "institution": "peking"
        },
        "harvard_financial_aid": {
            "name": "Harvard Financial Aid",
            "url": "https://college.harvard.edu/financial-aid",
            "type": "university_scholarship",
            "frequency": "yearly",
            "volume": "medium",
            "apply_method": "application",
            "tier": "tier1",
            "institution": "harvard"
        },
        "mit_scholarships": {
            "name": "MIT Scholarships",
            "url": "https://studentlife.mit.edu/sfs",
            "type": "university_scholarship",
            "frequency": "yearly",
            "volume": "medium",
            "apply_method": "application",
            "tier": "tier1",
            "institution": "mit"
        },
        "yale_gsas": {
            "name": "Yale GSAS Funding",
            "url": "https://gsas.yale.edu/funding",
            "type": "university_scholarship",
            "frequency": "yearly",
            "volume": "medium",
            "apply_method": "application",
            "tier": "tier1",
            "institution": "yale"
        },
        
        # FOUNDATION & PRIVATE SCHOLARSHIPS
        "mastercard_foundation": {
            "name": "Mastercard Foundation Scholars",
            "url": "https://mastercardfdn.org/scholars",
            "type": "foundation_scholarship",
            "frequency": "yearly",
            "volume": "medium",
            "apply_method": "application",
            "award": "Full funding",
            "tier": "tier1",
            "region": "africa"
        },
        "mandela_scholars": {
            "name": "Mandela Rhodes Scholarships",
            "url": "https://mandela-rhodes.org",
            "type": "foundation_scholarship",
            "frequency": "yearly",
            "volume": "low",
            "apply_method": "application",
            "award": "Full funding",
            "tier": "tier1",
            "region": "africa"
        },
        "rotary_scholarships": {
            "name": "Rotary Scholarships",
            "url": "https://rotaryscholarships.org",
            "type": "foundation_scholarship",
            "frequency": "yearly",
            "volume": "medium",
            "apply_method": "application",
            "tier": "tier2",
            "region": "global"
        },
        "thiel_fellowship": {
            "name": "Thiel Fellowship",
            "url": "https://thielfellowship.org",
            "type": "foundation_scholarship",
            "frequency": "yearly",
            "volume": "low",
            "apply_method": "application",
            "award": "$100,000",
            "tier": "tier1",
            "specialty": "entrepreneurship"
        },
        "stamps_scholars": {
            "name": "Stamps Scholars",
            "url": "https://stampsfoundation.org",
            "type": "foundation_scholarship",
            "frequency": "yearly",
            "volume": "low",
            "apply_method": "university",
            "award": "Full funding",
            "tier": "tier1",
            "region": "us"
        },
        "jefferson_scholars": {
            "name": "Jefferson Scholars",
            "url": "https://jeffersonscholars.org",
            "type": "foundation_scholarship",
            "frequency": "yearly",
            "volume": "low",
            "apply_method": "application",
            "award": "Full funding",
            "tier": "tier1",
            "institution": "uva"
        },
        "national_merit": {
            "name": "National Merit Scholarship",
            "url": "https://nationalmerit.org",
            "type": "merit_scholarship",
            "frequency": "yearly",
            "volume": "high",
            "apply_method": "test_based",
            "tier": "tier2",
            "region": "us"
        },
        
        # REGIONAL/COUNTRY-SPECIFIC SCHOLARSHIPS
        "japanese_mext": {
            "name": "MEXT Japanese Government Scholarships",
            "url": "https://mext.go.jp",
            "type": "government_scholarship",
            "frequency": "yearly",
            "volume": "high",
            "apply_method": "embassy",
            "award": "¥117,000/month + tuition",
            "tier": "tier1",
            "region": "japan"
        },
        "japanese_scholarship_portal": {
            "name": "Japanese Scholarship Portal",
            "url": "https://japanese-scholarship.com",
            "type": "scholarship_platform",
            "frequency": "daily",
            "volume": "medium",
            "apply_method": "direct",
            "tier": "platform",
            "region": "japan"
        },
        "monbukagakusho": {
            "name": "Monbukagakusho Scholarship",
            "url": "https://monbukagakusho.org",
            "type": "government_scholarship",
            "frequency": "yearly",
            "volume": "medium",
            "apply_method": "embassy",
            "tier": "tier1",
            "region": "japan"
        },
        "australia_awards": {
            "name": "Australia Awards Africa",
            "url": "https://australiaawardsafrica.org",
            "type": "government_scholarship",
            "frequency": "yearly",
            "volume": "medium",
            "apply_method": "application",
            "award": "Full funding",
            "tier": "tier1",
            "region": "australia-africa"
        },
        "nz_scholarships": {
            "name": "New Zealand Government Scholarships",
            "url": "https://nzscholarships.govt.nz",
            "type": "government_scholarship",
            "frequency": "yearly",
            "volume": "low",
            "apply_method": "application",
            "award": "Full funding",
            "tier": "tier1",
            "region": "new_zealand"
        },
        "swiss_excellence": {
            "name": "Swiss Government Excellence Scholarships",
            "url": "https://swissgovernmentexcellencescholarships.ch",
            "type": "government_scholarship",
            "frequency": "yearly",
            "volume": "low",
            "apply_method": "application",
            "award": "CHF 1,920/month",
            "tier": "tier1",
            "region": "switzerland"
        },
        "vlir_uos": {
            "name": "VLIR-UOS Belgium Scholarships",
            "url": "https://vlir-uos.be",
            "type": "government_scholarship",
            "frequency": "yearly",
            "volume": "medium",
            "apply_method": "application",
            "tier": "tier2",
            "region": "belgium"
        },
        "kfupm_scholarships": {
            "name": "KFUPM Scholarships",
            "url": "https://kfupm.edu.sa/scholarships",
            "type": "university_scholarship",
            "frequency": "biannual",
            "volume": "medium",
            "apply_method": "application",
            "tier": "tier2",
            "region": "saudi_arabia"
        },
        "kuwait_culture": {
            "name": "Kuwait Cultural Centre Scholarships",
            "url": "https://kuwaitculture.com",
            "type": "government_scholarship",
            "frequency": "yearly",
            "volume": "low",
            "apply_method": "application",
            "tier": "tier2",
            "region": "kuwait"
        },
        "mohsen_scholarships": {
            "name": "Mohsen Scholarships",
            "url": "https://mohsenscholarships.com",
            "type": "foundation_scholarship",
            "frequency": "yearly",
            "volume": "low",
            "apply_method": "application",
            "tier": "tier2",
            "region": "middle_east"
        },
        
        # RESEARCH & ACADEMIC FOUNDATIONS
        "wenner_gren": {
            "name": "Wenner-Gren Foundation",
            "url": "https://wennergren.org",
            "type": "research_grant",
            "frequency": "rolling",
            "volume": "medium",
            "apply_method": "application",
            "specialty": "anthropology",
            "tier": "tier1"
        },
        "humboldt_foundation": {
            "name": "Alexander von Humboldt Foundation",
            "url": "https://humboldt-foundation.de",
            "type": "research_scholarship",
            "frequency": "rolling",
            "volume": "high",
            "apply_method": "application",
            "tier": "tier1",
            "region": "germany"
        },
        "acls_fellowships": {
            "name": "ACLS Fellowships",
            "url": "https://acls.org/fellowships",
            "type": "research_fellowship",
            "frequency": "yearly",
            "volume": "medium",
            "apply_method": "application",
            "specialty": "humanities",
            "tier": "tier1"
        },
        "ford_foundation": {
            "name": "Ford Foundation Fellowships",
            "url": "https://fordscholar.org",
            "type": "foundation_scholarship",
            "frequency": "yearly",
            "volume": "medium",
            "apply_method": "application",
            "tier": "tier1",
            "diversity": "focus"
        },
        "macarthur_fellows": {
            "name": "MacArthur Fellows Program",
            "url": "https://macfound.org/programs/fellows",
            "type": "fellowship",
            "frequency": "yearly",
            "volume": "low",
            "apply_method": "nomination_only",
            "award": "$800,000",
            "tier": "tier1"
        },
        "mellon_mays": {
            "name": "Mellon Mays Fellowship",
            "url": "https://mellonmaysfellowship.org",
            "type": "fellowship",
            "frequency": "yearly",
            "volume": "medium",
            "apply_method": "university",
            "tier": "tier1",
            "diversity": "focus"
        },
        "open_philanthropy": {
            "name": "Open Philanthropy Scholarships",
            "url": "https://openphilanthropy.org/scholarships",
            "type": "foundation_scholarship",
            "frequency": "rolling",
            "volume": "low",
            "apply_method": "application",
            "tier": "tier1"
        },
        
        # CORPORATE & TECH SCHOLARSHIPS
        "google_scholarships": {
            "name": "Google Scholarships",
            "url": "https://buildyourfuture.withgoogle.com/scholarships",
            "type": "corporate_scholarship",
            "frequency": "yearly",
            "volume": "high",
            "apply_method": "application",
            "specialty": "computer_science",
            "tier": "tier1",
            "company": "google"
        },
        "microsoft_scholarships": {
            "name": "Microsoft Scholarships",
            "url": "https://microsoft.com/scholarships",
            "type": "corporate_scholarship",
            "frequency": "yearly",
            "volume": "medium",
            "apply_method": "application",
            "specialty": "computer_science",
            "tier": "tier1",
            "company": "microsoft"
        },
        "adobe_fellowship": {
            "name": "Adobe Research Fellowship",
            "url": "https://research.adobe.com/fellowship",
            "type": "corporate_fellowship",
            "frequency": "yearly",
            "volume": "low",
            "apply_method": "application",
            "specialty": "computer_graphics",
            "tier": "tier1",
            "company": "adobe"
        },
        "nvidia_fellowship": {
            "name": "NVIDIA Graduate Fellowship",
            "url": "https://nvidia.com/fellowships",
            "type": "corporate_fellowship",
            "frequency": "yearly",
            "volume": "low",
            "apply_method": "application",
            "specialty": "ai_ml",
            "tier": "tier1",
            "company": "nvidia"
        },
        "deepmind_scholarships": {
            "name": "DeepMind Scholarships",
            "url": "https://deepmind.com/scholarships",
            "type": "corporate_scholarship",
            "frequency": "yearly",
            "volume": "low",
            "apply_method": "application",
            "specialty": "ai_research",
            "tier": "tier1",
            "company": "deepmind"
        },
        "ibm_phd_fellowship": {
            "name": "IBM PhD Fellowship",
            "url": "https://research.ibm.com/university/awards/fellowships.html",
            "type": "corporate_fellowship",
            "frequency": "yearly",
            "volume": "low",
            "apply_method": "application",
            "specialty": "computer_science",
            "tier": "tier1",
            "company": "ibm"
        },
        "meta_phd_fellowship": {
            "name": "Meta PhD Fellowship",
            "url": "https://research.facebook.com/fellowship",
            "type": "corporate_fellowship",
            "frequency": "yearly",
            "volume": "low",
            "apply_method": "application",
            "specialty": "computer_science",
            "tier": "tier1",
            "company": "meta"
        },
        "apple_scholars": {
            "name": "Apple Scholars",
            "url": "https://developer.apple.com/scholarships",
            "type": "corporate_scholarship",
            "frequency": "yearly",
            "volume": "medium",
            "apply_method": "application",
            "specialty": "app_development",
            "tier": "tier1",
            "company": "apple"
        },
        "amazon_dli": {
            "name": "Amazon DLI Scholarship",
            "url": "https://amazon.com/scholarships",
            "type": "corporate_scholarship",
            "frequency": "yearly",
            "volume": "medium",
            "apply_method": "application",
            "specialty": "machine_learning",
            "tier": "tier1",
            "company": "amazon"
        },
        
        # AFRICAN-FOCUSED SCHOLARSHIPS
        "unicaf": {
            "name": "UNICAF Scholarships",
            "url": "https://unicaf.org/scholarships",
            "type": "foundation_scholarship",
            "frequency": "rolling",
            "volume": "high",
            "apply_method": "application",
            "tier": "tier2",
            "region": "africa"
        },
        "commonwealth_youth": {
            "name": "Commonwealth Youth Council",
            "url": "https://thecommonwealth.org/youth",
            "type": "youth_program",
            "frequency": "rolling",
            "volume": "medium",
            "apply_method": "application",
            "tier": "tier2",
            "region": "commonwealth"
        },
        "ashinaga_africa": {
            "name": "Ashinaga Africa Initiative",
            "url": "https://ashinaga.org/africa",
            "type": "foundation_scholarship",
            "frequency": "yearly",
            "volume": "medium",
            "apply_method": "application",
            "award": "Full funding",
            "tier": "tier1",
            "region": "africa"
        },
        "alu_financial_aid": {
            "name": "African Leadership University Financial Aid",
            "url": "https://alueducation.com/financial-aid",
            "type": "university_scholarship",
            "frequency": "rolling",
            "volume": "high",
            "apply_method": "application",
            "tier": "tier2",
            "region": "africa"
        },
        "aga_khan": {
            "name": "Aga Khan Foundation Scholarships",
            "url": "https://akdn.org/education/scholarships",
            "type": "foundation_scholarship",
            "frequency": "yearly",
            "volume": "medium",
            "apply_method": "application",
            "tier": "tier1",
            "region": "developing"
        },
        "kofi_annan": {
            "name": "Kofi Annan Scholarship",
            "url": "https://kofiannanfoundation.org/scholarships",
            "type": "foundation_scholarship",
            "frequency": "yearly",
            "volume": "low",
            "apply_method": "application",
            "tier": "tier1",
            "region": "africa"
        },
        "zawadi_africa": {
            "name": "Zawadi Africa Education Fund",
            "url": "https://zawadiafrica.org",
            "type": "foundation_scholarship",
            "frequency": "yearly",
            "volume": "medium",
            "apply_method": "application",
            "tier": "tier1",
            "region": "africa",
            "gender": "women"
        },
        "african_coding_network": {
            "name": "African Coding Network Scholarships",
            "url": "https://africancoding.network/scholarships",
            "type": "foundation_scholarship",
            "frequency": "rolling",
            "volume": "medium",
            "apply_method": "application",
            "specialty": "coding",
            "tier": "tier2",
            "region": "africa"
        },
        
        # INTERNATIONAL ORGANIZATIONS & UN SYSTEM
        "opec_fund": {
            "name": "OPEC Fund Scholarship",
            "url": "https://opecfund.org/scholarships",
            "type": "international_scholarship",
            "frequency": "yearly",
            "volume": "low",
            "apply_method": "application",
            "tier": "tier1",
            "region": "developing"
        },
        "islamic_development_bank": {
            "name": "Islamic Development Bank Scholarship",
            "url": "https://isdb.org/scholarships",
            "type": "international_scholarship",
            "frequency": "yearly",
            "volume": "medium",
            "apply_method": "application",
            "tier": "tier1",
            "region": "muslim_countries"
        },
        "african_union": {
            "name": "African Union Scholarship",
            "url": "https://au.int/scholarships",
            "type": "regional_scholarship",
            "frequency": "yearly",
            "volume": "medium",
            "apply_method": "application",
            "tier": "tier1",
            "region": "africa"
        },
        "afdb_scholarship": {
            "name": "AfDB Scholarship Program",
            "url": "https://afdb.org/scholarships",
            "type": "development_scholarship",
            "frequency": "yearly",
            "volume": "medium",
            "apply_method": "application",
            "tier": "tier1",
            "region": "africa"
        },
        "world_bank_scholarship": {
            "name": "World Bank Scholarship Program",
            "url": "https://worldbank.org/scholarships",
            "type": "international_scholarship",
            "frequency": "yearly",
            "volume": "medium",
            "apply_method": "application",
            "tier": "tier1",
            "region": "developing"
        },
        "imf_scholarship": {
            "name": "IMF Training & Scholarship",
            "url": "https://imf.org/training",
            "type": "professional_scholarship",
            "frequency": "rolling",
            "volume": "low",
            "apply_method": "application",
            "specialty": "economics",
            "tier": "tier1"
        },
        "un_ypp": {
            "name": "UN Young Professionals Program",
            "url": "https://careers.un.org/ypp",
            "type": "professional_program",
            "frequency": "yearly",
            "volume": "medium",
            "apply_method": "exam",
            "tier": "tier1",
            "organization": "un"
        },
        "un_volunteers": {
            "name": "UN Volunteers Program",
            "url": "https://unv.org",
            "type": "volunteer_program",
            "frequency": "rolling",
            "volume": "high",
            "apply_method": "application",
            "tier": "tier2",
            "organization": "un"
        },
        "unesco_opportunities": {
            "name": "UNESCO Opportunities",
            "url": "https://unesco.org/opportunities",
            "type": "international_program",
            "frequency": "rolling",
            "volume": "medium",
            "apply_method": "application",
            "tier": "tier1",
            "organization": "unesco"
        },
        "wfp_fellowship": {
            "name": "WFP Innovation Accelerator Fellowships",
            "url": "https://innovation.wfp.org/fellowships",
            "type": "fellowship",
            "frequency": "rolling",
            "volume": "low",
            "apply_method": "application",
            "specialty": "innovation",
            "tier": "tier1",
            "organization": "wfp"
        },
        "undp_fellowship": {
            "name": "UNDP Fellowship",
            "url": "https://undp.org/fellowships",
            "type": "fellowship",
            "frequency": "rolling",
            "volume": "low",
            "apply_method": "application",
            "tier": "tier1",
            "organization": "undp"
        },
        "unhcr_fellowship": {
            "name": "UNHCR Fellowship",
            "url": "https://unhcr.org/fellowships",
            "type": "fellowship",
            "frequency": "yearly",
            "volume": "low",
            "apply_method": "application",
            "specialty": "refugee_studies",
            "tier": "tier1",
            "organization": "unhcr"
        },
        "who_internship": {
            "name": "WHO Internship Program",
            "url": "https://who.int/internships",
            "type": "internship",
            "frequency": "rolling",
            "volume": "medium",
            "apply_method": "application",
            "specialty": "public_health",
            "tier": "tier2",
            "organization": "who"
        },
        
        # SCIENTIFIC & RESEARCH ORGANIZATIONS
        "iaea_fellowship": {
            "name": "IAEA Fellowship",
            "url": "https://iaea.org/fellowships",
            "type": "technical_fellowship",
            "frequency": "rolling",
            "volume": "medium",
            "apply_method": "application",
            "specialty": "nuclear_science",
            "tier": "tier1",
            "organization": "iaea"
        },
        "cern_students": {
            "name": "CERN Technical Student Program",
            "url": "https://cern.ch/students",
            "type": "student_program",
            "frequency": "biannual",
            "volume": "high",
            "apply_method": "application",
            "specialty": "physics_engineering",
            "tier": "tier1",
            "organization": "cern"
        },
        "cern_summer": {
            "name": "CERN Summer School",
            "url": "https://cern.ch/summerschool",
            "type": "summer_program",
            "frequency": "yearly",
            "volume": "medium",
            "apply_method": "application",
            "specialty": "particle_physics",
            "tier": "tier1",
            "organization": "cern"
        },
        "cern_doctoral": {
            "name": "CERN Doctoral Student Program",
            "url": "https://cern.ch/doctoral",
            "type": "doctoral_program",
            "frequency": "rolling",
            "volume": "medium",
            "apply_method": "application",
            "specialty": "physics",
            "tier": "tier1",
            "organization": "cern"
        },
        "esa_scholarships": {
            "name": "ESA Scholarships",
            "url": "https://esa.int/scholarships",
            "type": "space_scholarship",
            "frequency": "yearly",
            "volume": "low",
            "apply_method": "application",
            "specialty": "space_science",
            "tier": "tier1",
            "organization": "esa"
        },
        "nasa_internships": {
            "name": "NASA Internships",
            "url": "https://intern.nasa.gov",
            "type": "internship",
            "frequency": "rolling",
            "volume": "high",
            "apply_method": "application",
            "specialty": "aerospace",
            "tier": "tier1",
            "organization": "nasa"
        },
        "jaxa_internships": {
            "name": "JAXA Internships",
            "url": "https://jaxa.jp/internship",
            "type": "internship",
            "frequency": "yearly",
            "volume": "low",
            "apply_method": "application",
            "specialty": "space_technology",
            "tier": "tier1",
            "organization": "jaxa"
        },
        
        # SPECIALIZED PROGRAM PORTALS
        "common_app": {
            "name": "Common Application Scholarships",
            "url": "https://commonapp.org",
            "type": "application_platform",
            "frequency": "yearly",
            "volume": "high",
            "apply_method": "platform",
            "tier": "platform",
            "region": "us"
        },
        "college_board": {
            "name": "College Board Scholarships",
            "url": "https://collegeboard.org",
            "type": "scholarship_platform",
            "frequency": "daily",
            "volume": "high",
            "apply_method": "platform",
            "tier": "platform",
            "region": "us"
        },
        "uni_assist": {
            "name": "Uni-Assist Germany",
            "url": "https://uni-assist.de",
            "type": "application_platform",
            "frequency": "rolling",
            "volume": "high",
            "apply_method": "platform",
            "tier": "platform",
            "region": "germany"
        },
        "singapore_tech": {
            "name": "Singapore Tech Scholarships",
            "url": "https://singaporetech.edu.sg/scholarships",
            "type": "university_scholarship",
            "frequency": "yearly",
            "volume": "medium",
            "apply_method": "application",
            "tier": "tier2",
            "region": "singapore"
        },
        "q_scholarships": {
            "name": "QScholarships",
            "url": "https://qscholarships.com",
            "type": "scholarship_platform",
            "frequency": "daily",
            "volume": "medium",
            "apply_method": "direct",
            "tier": "platform",
            "region": "global"
        },
        
        # EDUCATION ACCESS & DIVERSITY ORGANIZATIONS
        "educationusa": {
            "name": "EducationUSA Scholarship Hub",
            "url": "https://educationusa.org/scholarships",
            "type": "scholarship_platform",
            "frequency": "daily",
            "volume": "high",
            "apply_method": "direct",
            "tier": "platform",
            "region": "global"
        },
        "amideast": {
            "name": "AMIDEAST Scholarships",
            "url": "https://amideast.org/scholarships",
            "type": "regional_scholarship",
            "frequency": "yearly",
            "volume": "medium",
            "apply_method": "application",
            "tier": "tier1",
            "region": "middle_east"
        },
        "daad_epos": {
            "name": "DAAD EPOS Program",
            "url": "https://daad.de/epos",
            "type": "development_scholarship",
            "frequency": "yearly",
            "volume": "medium",
            "apply_method": "application",
            "tier": "tier1",
            "region": "developing"
        },
        "erasmus_mundus": {
            "name": "Erasmus Mundus Joint Masters",
            "url": "https://erasmus-plus.ec.europa.eu/erasmus-mundus",
            "type": "joint_masters",
            "frequency": "yearly",
            "volume": "high",
            "apply_method": "application",
            "award": "Full funding",
            "tier": "tier1",
            "region": "europe"
        },
        
        # UNIVERSITY-SPECIFIC PROGRAMS (INTERNATIONAL)
        "columbia_sipa": {
            "name": "Columbia SIPA Fellowships",
            "url": "https://sipa.columbia.edu/fellowships",
            "type": "university_fellowship",
            "frequency": "yearly",
            "volume": "medium",
            "apply_method": "application",
            "tier": "tier1",
            "institution": "columbia"
        },
        "harvard_kennedy": {
            "name": "Harvard Kennedy School Fellowships",
            "url": "https://hks.harvard.edu/fellowships",
            "type": "university_fellowship",
            "frequency": "yearly",
            "volume": "medium",
            "apply_method": "application",
            "tier": "tier1",
            "institution": "harvard_hks"
        },
        "oxford_weidenfeld": {
            "name": "Oxford Weidenfeld Scholarships",
            "url": "https://weidenfeld-hoffmann.ox.ac.uk",
            "type": "university_scholarship",
            "frequency": "yearly",
            "volume": "low",
            "apply_method": "application",
            "tier": "tier1",
            "institution": "oxford"
        },
        "cambridge_trust": {
            "name": "Cambridge Trust Scholarships",
            "url": "https://cambridge.org/scholarships",
            "type": "university_scholarship",
            "frequency": "yearly",
            "volume": "high",
            "apply_method": "application",
            "tier": "tier1",
            "institution": "cambridge"
        },
        "eth_zurich": {
            "name": "ETH Zurich Excellence Scholarships",
            "url": "https://ethz.ch/scholarships",
            "type": "university_scholarship",
            "frequency": "yearly",
            "volume": "low",
            "apply_method": "application",
            "tier": "tier1",
            "institution": "eth_zurich"
        },
        "epfl_excellence": {
            "name": "EPFL Excellence Fellowships",
            "url": "https://epfl.ch/fellowships",
            "type": "university_scholarship",
            "frequency": "yearly",
            "volume": "low",
            "apply_method": "application",
            "tier": "tier1",
            "institution": "epfl"
        },
        "ku_leuven": {
            "name": "KU Leuven Scholarships",
            "url": "https://kuleuven.be/scholarships",
            "type": "university_scholarship",
            "frequency": "yearly",
            "volume": "medium",
            "apply_method": "application",
            "tier": "tier2",
            "institution": "ku_leuven"
        },
        "university_toronto": {
            "name": "University of Toronto Scholarships",
            "url": "https://utoronto.ca/scholarships",
            "type": "university_scholarship",
            "frequency": "yearly",
            "volume": "high",
            "apply_method": "application",
            "tier": "tier1",
            "institution": "university_toronto"
        },
        "ubc_scholars": {
            "name": "UBC International Scholars Program",
            "url": "https://ubc.ca/scholarships",
            "type": "university_scholarship",
            "frequency": "yearly",
            "volume": "medium",
            "apply_method": "application",
            "tier": "tier1",
            "institution": "ubc"
        },
        "mcgill_scholarships": {
            "name": "McGill Scholarships",
            "url": "https://mcgill.ca/scholarships",
            "type": "university_scholarship",
            "frequency": "yearly",
            "volume": "high",
            "apply_method": "application",
            "tier": "tier1",
            "institution": "mcgill"
        },
        "university_alberta": {
            "name": "University of Alberta Scholarships",
            "url": "https://ualberta.ca/scholarships",
            "type": "university_scholarship",
            "frequency": "yearly",
            "volume": "high",
            "apply_method": "application",
            "tier": "tier2",
            "institution": "university_alberta"
        },
        "kaust_scholarships": {
            "name": "KAUST Scholarships",
            "url": "https://kaust.edu.sa/scholarships",
            "type": "university_scholarship",
            "frequency": "rolling",
            "volume": "high",
            "apply_method": "application",
            "award": "Full funding + stipend",
            "tier": "tier1",
            "institution": "kaust"
        },
        
        # AFRICAN ACADEMIC INSTITUTIONS & NETWORKS
        "aims_scholarship": {
            "name": "AIMS Scholarship",
            "url": "https://aims.ac.za/scholarships",
            "type": "academic_scholarship",
            "frequency": "yearly",
            "volume": "medium",
            "apply_method": "application",
            "specialty": "mathematical_sciences",
            "tier": "tier1",
            "region": "africa"
        },
        "ruforum": {
            "name": "RUFORUM Scholarships",
            "url": "https://ruforum.org/scholarships",
            "type": "academic_scholarship",
            "frequency": "yearly",
            "volume": "medium",
            "apply_method": "application",
            "specialty": "agriculture",
            "tier": "tier1",
            "region": "africa"
        },
        "aims_mathematical": {
            "name": "African Institute for Mathematical Sciences",
            "url": "https://aims.ac.za",
            "type": "institute_scholarship",
            "frequency": "yearly",
            "volume": "medium",
            "apply_method": "application",
            "specialty": "mathematics",
            "tier": "tier1",
            "region": "africa"
        },
        
        # TECHNOLOGY & INNOVATION FELLOWSHIPS
        "icann_fellowship": {
            "name": "ICANN Fellowship",
            "url": "https://icann.org/fellowships",
            "type": "professional_fellowship",
            "frequency": "rolling",
            "volume": "low",
            "apply_method": "application",
            "specialty": "internet_governance",
            "tier": "tier1"
        },
        "internet_society": {
            "name": "Internet Society Fellowship",
            "url": "https://internetsociety.org/fellowships",
            "type": "professional_fellowship",
            "frequency": "rolling",
            "volume": "low",
            "apply_method": "application",
            "specialty": "internet_policy",
            "tier": "tier1"
        },
        "mozilla_fellows": {
            "name": "Mozilla Fellows Program",
            "url": "https://mozilla.org/fellowships",
            "type": "tech_fellowship",
            "frequency": "yearly",
            "volume": "low",
            "apply_method": "application",
            "specialty": "open_internet",
            "tier": "tier1"
        },
        "national_geographic": {
            "name": "National Geographic Explorer Grants",
            "url": "https://nationalgeographic.org/grants",
            "type": "explorer_grant",
            "frequency": "rolling",
            "volume": "medium",
            "apply_method": "application",
            "specialty": "exploration",
            "tier": "tier1"
        },
        
        # LEADERSHIP & SOCIAL IMPACT PROGRAMS
        "obama_foundation": {
            "name": "Obama Foundation Scholars",
            "url": "https://obamascholarsprogram.org",
            "type": "leadership_scholarship",
            "frequency": "yearly",
            "volume": "low",
            "apply_method": "application",
            "tier": "tier1",
            "specialty": "leadership"
        },
        "obama_leaders": {
            "name": "Obama Leaders Program",
            "url": "https://obamaleaders.org",
            "type": "leadership_program",
            "frequency": "yearly",
            "volume": "medium",
            "apply_method": "application",
            "tier": "tier1",
            "specialty": "leadership"
        },
        "harvard_african_studies": {
            "name": "Harvard Center for African Studies Funding",
            "url": "https://africa.harvard.edu/funding",
            "type": "research_funding",
            "frequency": "yearly",
            "volume": "low",
            "apply_method": "application",
            "specialty": "african_studies",
            "tier": "tier1",
            "institution": "harvard"
        },
        "skoll_scholarships": {
            "name": "Skoll Scholarships",
            "url": "https://skollscholarships.org",
            "type": "social_entrepreneurship",
            "frequency": "yearly",
            "volume": "low",
            "apply_method": "application",
            "specialty": "social_entrepreneurship",
            "tier": "tier1"
        },
        "dalai_lama_fellows": {
            "name": "Dalai Lama Fellows",
            "url": "https://dalailmafellows.org",
            "type": "leadership_fellowship",
            "frequency": "yearly",
            "volume": "low",
            "apply_method": "application",
            "specialty": "social_impact",
            "tier": "tier1"
        },
        "acumen_fellowship": {
            "name": "Acumen Fellowship",
            "url": "https://acumen.org/fellowships",
            "type": "social_fellowship",
            "frequency": "yearly",
            "volume": "low",
            "apply_method": "application",
            "specialty": "social_change",
            "tier": "tier1"
        },
        
        # UNICEF & UN CHILDREN/EDUCATION PROGRAMS
        "unicef_portal": {
            "name": "UNICEF Learning Portal",
            "url": "https://unicef.org/learning",
            "type": "education_platform",
            "frequency": "rolling",
            "volume": "high",
            "apply_method": "registration",
            "tier": "platform",
            "organization": "unicef"
        },
        "un_careers": {
            "name": "UN Careers Portal",
            "url": "https://careers.un.org",
            "type": "career_platform",
            "frequency": "daily",
            "volume": "high",
            "apply_method": "application",
            "tier": "platform",
            "organization": "un"
        }
    },

    # ═══════════════════════════════════════════════════════════════
    # STARTUP ACCELERATORS & INCUBATORS - 120+ SITES
    # ═══════════════════════════════════════════════════════════════
    "accelerators": {
        # TIER 1 - Major Global Accelerators
        "ycombinator": {
            "name": "Y Combinator",
            "url": "https://ycombinator.com",
            "apply_url": "https://www.ycombinator.com/apply",
            "type": "accelerator",
            "frequency": "biannual",
            "volume": "low",
            "apply_method": "application",
            "funding": "$500,000",
            "tier": "tier1"
        },
        "techstars": {
            "name": "Techstars",
            "url": "https://techstars.com",
            "apply_url": "https://www.techstars.com/accelerators",
            "type": "accelerator",
            "frequency": "quarterly",
            "volume": "low",
            "apply_method": "application",
            "funding": "$120,000",
            "tier": "tier1"
        },
        "500_global": {
            "name": "500 Global",
            "url": "https://500.co",
            "apply_url": "https://500.co/accelerators",
            "type": "accelerator",
            "frequency": "quarterly",
            "volume": "low",
            "apply_method": "application",
            "funding": "$150,000",
            "tier": "tier1"
        },
        "seedstars": {
            "name": "Seedstars",
            "url": "https://seedstars.com",
            "type": "accelerator",
            "frequency": "quarterly",
            "volume": "low",
            "apply_method": "application",
            "tier": "tier1"
        },
        "foundersfactory": {
            "name": "Founders Factory",
            "url": "https://foundersfactory.com",
            "type": "accelerator",
            "frequency": "rolling",
            "volume": "low",
            "apply_method": "application",
            "tier": "tier1"
        },
        "entrepreneurfirst": {
            "name": "Entrepreneur First",
            "url": "https://entrepreneurfirst.com",
            "type": "accelerator",
            "frequency": "quarterly",
            "volume": "low",
            "apply_method": "application",
            "tier": "tier1"
        },
        "antler": {
            "name": "Antler",
            "url": "https://antler.co",
            "type": "accelerator",
            "frequency": "quarterly",
            "volume": "low",
            "apply_method": "application",
            "tier": "tier1"
        },
        "plug_and_play": {
            "name": "Plug and Play",
            "url": "https://plugandplaytechcenter.com",
            "type": "accelerator",
            "frequency": "quarterly",
            "volume": "low",
            "apply_method": "application",
            "tier": "tier1"
        },
        "masschallenge": {
            "name": "MassChallenge",
            "url": "https://masschallenge.org",
            "type": "accelerator",
            "frequency": "yearly",
            "volume": "low",
            "apply_method": "application",
            "tier": "tier1"
        },
        "startupbootcamp": {
            "name": "Startupbootcamp",
            "url": "https://startupbootcamp.org",
            "type": "accelerator",
            "frequency": "quarterly",
            "volume": "low",
            "apply_method": "application",
            "tier": "tier1"
        },
        "village_global": {
            "name": "Village Global",
            "url": "https://villageglobal.vc",
            "type": "accelerator",
            "frequency": "rolling",
            "volume": "low",
            "apply_method": "application",
            "tier": "tier1"
        },
        
        # TIER 2 - Regional & Specialized Accelerators
        "onedevcamp": {
            "name": "OneDev Camp",
            "url": "https://onedevcamp.com",
            "type": "accelerator",
            "frequency": "quarterly",
            "volume": "low",
            "apply_method": "application",
            "tier": "tier2"
        },
        "sosv": {
            "name": "SOSV",
            "url": "https://sosv.com",
            "type": "accelerator",
            "frequency": "quarterly",
            "volume": "low",
            "apply_method": "application",
            "tier": "tier2"
        },
        "indiebio": {
            "name": "IndieBio",
            "url": "https://indiebio.co",
            "type": "accelerator",
            "frequency": "biannual",
            "volume": "low",
            "apply_method": "application",
            "specialty": "biotech",
            "tier": "tier2"
        },
        "hax": {
            "name": "HAX Hardware Accelerator",
            "url": "https://hax.co",
            "type": "accelerator",
            "frequency": "biannual",
            "volume": "low",
            "apply_method": "application",
            "specialty": "hardware",
            "tier": "tier2"
        },
        "alchemist": {
            "name": "Alchemist Accelerator",
            "url": "https://alchemistaccelerator.com",
            "type": "accelerator",
            "frequency": "biannual",
            "volume": "low",
            "apply_method": "application",
            "specialty": "enterprise_b2b",
            "tier": "tier2"
        },
        "bolt_accelerator": {
            "name": "Bolt Accelerator",
            "url": "https://bolt.io",
            "type": "accelerator",
            "frequency": "quarterly",
            "volume": "low",
            "apply_method": "application",
            "tier": "tier2"
        },
        
        # CORPORATE ACCELERATORS
        "google_startups": {
            "name": "Google for Startups",
            "url": "https://googleforstartups.com",
            "type": "corporate_accelerator",
            "frequency": "rolling",
            "volume": "medium",
            "apply_method": "application",
            "tier": "corporate"
        },
        "aws_startups": {
            "name": "AWS Startups",
            "url": "https://awsstartups.com",
            "type": "corporate_accelerator",
            "frequency": "rolling",
            "volume": "medium",
            "apply_method": "application",
            "tier": "corporate"
        },
        "microsoft_founders": {
            "name": "Microsoft Founders Hub",
            "url": "https://microsoftfoundershub.com",
            "type": "corporate_accelerator",
            "frequency": "rolling",
            "volume": "medium",
            "apply_method": "application",
            "tier": "corporate"
        },
        "nvidia_inception": {
            "name": "NVIDIA Inception Program",
            "url": "https://nvidia-inception-program.com",
            "type": "corporate_accelerator",
            "frequency": "rolling",
            "volume": "medium",
            "apply_method": "application",
            "specialty": "ai_ml",
            "tier": "corporate"
        },
        "intel_ignited": {
            "name": "Intel Ignited",
            "url": "https://intel-ignited.com",
            "type": "corporate_accelerator",
            "frequency": "rolling",
            "volume": "low",
            "apply_method": "application",
            "specialty": "deep_tech",
            "tier": "corporate"
        },
        "ibm_hyper_protect": {
            "name": "IBM Hyper Protect Accelerator",
            "url": "https://ibm.com/cloud/hyper-protect-accelerator",
            "type": "corporate_accelerator",
            "frequency": "quarterly",
            "volume": "low",
            "apply_method": "application",
            "specialty": "security",
            "tier": "corporate"
        },
        "apple_entrepreneur": {
            "name": "Apple Entrepreneur Camp",
            "url": "https://developer.apple.com/entrepreneur-camp",
            "type": "corporate_accelerator",
            "frequency": "quarterly",
            "volume": "low",
            "apply_method": "application",
            "specialty": "mobile_apps",
            "tier": "corporate"
        },
        
        # UNIVERSITY ACCELERATORS
        "mit_sandbox": {
            "name": "MIT Sandbox",
            "url": "https://sandbox.mit.edu",
            "type": "university_accelerator",
            "frequency": "yearly",
            "volume": "low",
            "apply_method": "application",
            "tier": "university"
        },
        "mit_deltav": {
            "name": "MIT Delta V",
            "url": "https://entrepreneurship.mit.edu/accelerator",
            "type": "university_accelerator",
            "frequency": "yearly",
            "volume": "low",
            "apply_method": "application",
            "tier": "university"
        },
        "harvard_ilab": {
            "name": "Harvard Innovation Labs",
            "url": "https://i-lab.harvard.edu",
            "type": "university_accelerator",
            "frequency": "yearly",
            "volume": "low",
            "apply_method": "application",
            "tier": "university"
        },
        "stanford_startx": {
            "name": "Stanford StartX",
            "url": "https://startx.com",
            "type": "university_accelerator",
            "frequency": "biannual",
            "volume": "low",
            "apply_method": "application",
            "tier": "university"
        },
        "berkeley_skydeck": {
            "name": "Berkeley SkyDeck",
            "url": "https://skydeck.berkeley.edu",
            "type": "university_accelerator",
            "frequency": "biannual",
            "volume": "low",
            "apply_method": "application",
            "tier": "university"
        },
        
        # CLIMATE & CLEANTECH ACCELERATORS
        "climate_kic": {
            "name": "Climate-KIC Accelerator",
            "url": "https://www.climate-kic.org",
            "type": "climate_accelerator",
            "frequency": "quarterly",
            "volume": "low",
            "apply_method": "application",
            "specialty": "climate_tech",
            "tier": "specialty"
        },
        "greentown_labs": {
            "name": "Greentown Labs",
            "url": "https://greentownlabs.com",
            "type": "climate_accelerator",
            "frequency": "quarterly",
            "volume": "low",
            "apply_method": "application",
            "specialty": "clean_energy",
            "tier": "specialty"
        },
        "elemental_excelerator": {
            "name": "Elemental Excelerator",
            "url": "https://elementalexcelerator.com",
            "type": "climate_accelerator",
            "frequency": "yearly",
            "volume": "low",
            "apply_method": "application",
            "specialty": "climate_tech",
            "tier": "specialty"
        },
        "clean_energy_trust": {
            "name": "Clean Energy Trust",
            "url": "https://cleanenergytrust.org",
            "type": "climate_accelerator",
            "frequency": "quarterly",
            "volume": "low",
            "apply_method": "application",
            "specialty": "clean_energy",
            "tier": "specialty"
        },
        "founders_factory_climate": {
            "name": "Founders Factory Climate Tech",
            "url": "https://foundersfactory.com/climate",
            "type": "climate_accelerator",
            "frequency": "quarterly",
            "volume": "low",
            "apply_method": "application",
            "specialty": "climate_tech",
            "tier": "specialty"
        },
        "mit_climatetech": {
            "name": "MIT ClimateTech",
            "url": "https://climatetech.mit.edu",
            "type": "climate_accelerator",
            "frequency": "yearly",
            "volume": "low",
            "apply_method": "application",
            "specialty": "climate_tech",
            "tier": "specialty"
        },
        
        # AFRICA-FOCUSED ACCELERATORS
        "africas_talking": {
            "name": "Africa's Talking AT Labs",
            "url": "https://labs.africastalking.com",
            "type": "regional_accelerator",
            "frequency": "quarterly",
            "volume": "low",
            "apply_method": "application",
            "region": "africa",
            "tier": "regional"
        },
        "antler_nairobi": {
            "name": "Antler Nairobi",
            "url": "https://antler.co/locations/nairobi",
            "type": "regional_accelerator",
            "frequency": "quarterly",
            "volume": "low",
            "apply_method": "application",
            "region": "africa",
            "tier": "regional"
        },
        "founders_factory_africa": {
            "name": "Founders Factory Africa",
            "url": "https://foundersfactory.com/africa",
            "type": "regional_accelerator",
            "frequency": "quarterly",
            "volume": "low",
            "apply_method": "application",
            "region": "africa",
            "tier": "regional"
        },
        "afrilabs": {
            "name": "AfriLabs",
            "url": "https://afrilabs.com",
            "type": "regional_accelerator",
            "frequency": "rolling",
            "volume": "medium",
            "apply_method": "application",
            "region": "africa",
            "tier": "regional"
        },
        "mest_africa": {
            "name": "MEST Africa",
            "url": "https://meltwater.org",
            "type": "regional_accelerator",
            "frequency": "yearly",
            "volume": "low",
            "apply_method": "application",
            "region": "africa",
            "tier": "regional"
        },
        "cchub": {
            "name": "Co-Creation Hub (CcHub)",
            "url": "https://cchubnigeria.com",
            "type": "regional_accelerator",
            "frequency": "quarterly",
            "volume": "low",
            "apply_method": "application",
            "region": "africa",
            "tier": "regional"
        },
        "ihub": {
            "name": "iHub",
            "url": "https://ihub.co.ke",
            "type": "regional_accelerator",
            "frequency": "quarterly",
            "volume": "low",
            "apply_method": "application",
            "region": "africa",
            "tier": "regional"
        },
        "gearbox_nairobi": {
            "name": "Gearbox Nairobi",
            "url": "https://gearbox.co.ke",
            "type": "regional_accelerator",
            "frequency": "quarterly",
            "volume": "low",
            "apply_method": "application",
            "region": "africa",
            "tier": "regional"
        },
        "nailab": {
            "name": "Nailab",
            "url": "https://nailab.co.ke",
            "type": "regional_accelerator",
            "frequency": "quarterly",
            "volume": "low",
            "apply_method": "application",
            "region": "africa",
            "tier": "regional"
        },
        "villgro_africa": {
            "name": "Villgro Africa",
            "url": "https://villgro.org/africa",
            "type": "regional_accelerator",
            "frequency": "quarterly",
            "volume": "low",
            "apply_method": "application",
            "region": "africa",
            "tier": "regional"
        },
        "savanna_circuits": {
            "name": "Savanna Circuits",
            "url": "https://savannacircuits.com",
            "type": "regional_accelerator",
            "frequency": "quarterly",
            "volume": "low",
            "apply_method": "application",
            "region": "africa",
            "specialty": "iot",
            "tier": "regional"
        },
        "safaricom_spark": {
            "name": "Safaricom Spark Fund",
            "url": "https://spark.safaricom.co.ke",
            "type": "regional_accelerator",
            "frequency": "rolling",
            "volume": "low",
            "apply_method": "application",
            "region": "africa",
            "tier": "regional"
        },
        "blue_moon_ethiopia": {
            "name": "Blue Moon Ethiopia",
            "url": "https://bluemoonethiopia.com",
            "type": "regional_accelerator",
            "frequency": "quarterly",
            "volume": "low",
            "apply_method": "application",
            "region": "africa",
            "tier": "regional"
        },
        "tony_elumelu": {
            "name": "Tony Elumelu Foundation",
            "url": "https://tonyelumelufoundation.org",
            "type": "regional_accelerator",
            "frequency": "yearly",
            "volume": "medium",
            "apply_method": "application",
            "region": "africa",
            "tier": "regional"
        },
        "orange_fab": {
            "name": "Orange Fab",
            "url": "https://orangefab.com",
            "type": "corporate_accelerator",
            "frequency": "quarterly",
            "volume": "low",
            "apply_method": "application",
            "region": "africa",
            "tier": "corporate"
        },
        
        # FINTECH & PAYMENT COMPANY PROGRAMS
        "huawei_cloud_startup": {
            "name": "Huawei Cloud Startup Program",
            "url": "https://huaweicloud.com/startup",
            "type": "corporate_accelerator",
            "frequency": "rolling",
            "volume": "medium",
            "apply_method": "application",
            "tier": "corporate"
        },
        "stripe_atlas": {
            "name": "Stripe Atlas",
            "url": "https://stripe.com/atlas",
            "type": "startup_program",
            "frequency": "rolling",
            "volume": "high",
            "apply_method": "direct",
            "tier": "startup_program"
        },
        "paystack_startup": {
            "name": "Paystack Startup Program",
            "url": "https://paystack.com/startup-program",
            "type": "startup_program",
            "frequency": "rolling",
            "volume": "medium",
            "apply_method": "application",
            "region": "africa",
            "tier": "startup_program"
        },
        "flutterwave_startup": {
            "name": "Flutterwave Startup Fund",
            "url": "https://flutterwave.com/startup-fund",
            "type": "startup_program",
            "frequency": "rolling",
            "volume": "medium",
            "apply_method": "application",
            "region": "africa",
            "tier": "startup_program"
        },
        "foundersforge": {
            "name": "FoundersForge",
            "url": "https://foundersforge.com",
            "type": "accelerator",
            "frequency": "quarterly",
            "volume": "low",
            "apply_method": "application",
            "tier": "tier2"
        },
        
        # DIVERSITY & INCLUSION PROGRAMS
        "google_black_founders": {
            "name": "Google Black Founders Fund",
            "url": "https://googleforstartups.com/black-founders-fund",
            "type": "diversity_program",
            "frequency": "yearly",
            "volume": "low",
            "apply_method": "application",
            "tier": "diversity"
        },
        
        # INTERNATIONAL ORGANIZATIONS & FUNDS
        "gsma_innovation": {
            "name": "GSMA Innovation Fund",
            "url": "https://gsma.com/innovation-fund",
            "type": "innovation_fund",
            "frequency": "rolling",
            "volume": "low",
            "apply_method": "application",
            "tier": "international"
        },
        "mastercard_start_path": {
            "name": "Mastercard Start Path",
            "url": "https://startpath.com",
            "type": "corporate_accelerator",
            "frequency": "quarterly",
            "volume": "low",
            "apply_method": "application",
            "specialty": "fintech",
            "tier": "corporate"
        },
        "visa_everywhere": {
            "name": "Visa Everywhere Initiative",
            "url": "https://developer.visa.com/visa-everywhere",
            "type": "innovation_challenge",
            "frequency": "yearly",
            "volume": "low",
            "apply_method": "application",
            "specialty": "fintech",
            "tier": "corporate"
        },
        "ifc_startup_catalyst": {
            "name": "IFC Startup Catalyst",
            "url": "https://ifc.org/startup-catalyst",
            "type": "innovation_fund",
            "frequency": "rolling",
            "volume": "low",
            "apply_method": "application",
            "tier": "international"
        },
        "undp_innovation": {
            "name": "UNDP Innovation Challenge",
            "url": "https://undp.org/innovation",
            "type": "innovation_challenge",
            "frequency": "yearly",
            "volume": "low",
            "apply_method": "application",
            "tier": "international"
        },
        "unicef_venture": {
            "name": "UNICEF Venture Fund",
            "url": "https://unicefinnovationfund.org",
            "type": "innovation_fund",
            "frequency": "rolling",
            "volume": "low",
            "apply_method": "application",
            "tier": "international"
        },
        "unido_itpo": {
            "name": "UNIDO ITPO",
            "url": "https://unido.org/itpo",
            "type": "innovation_program",
            "frequency": "rolling",
            "volume": "low",
            "apply_method": "application",
            "tier": "international"
        },
        "wfp_innovation": {
            "name": "WFP Innovation Accelerator",
            "url": "https://innovation.wfp.org",
            "type": "innovation_accelerator",
            "frequency": "rolling",
            "volume": "low",
            "apply_method": "application",
            "tier": "international"
        },
        
        # PRIZE COMPETITIONS & CHALLENGES
        "africa_prize": {
            "name": "Africa Prize for Engineering Innovation",
            "url": "https://raeng.org.uk/africa-prize",
            "type": "prize_competition",
            "frequency": "yearly",
            "volume": "low",
            "apply_method": "application",
            "region": "africa",
            "tier": "competition"
        },
        "mit_solve": {
            "name": "MIT Solve",
            "url": "https://solve.mit.edu",
            "type": "prize_competition",
            "frequency": "yearly",
            "volume": "low",
            "apply_method": "application",
            "tier": "competition"
        },
        "xprize": {
            "name": "XPRIZE Competitions",
            "url": "https://xprize.org",
            "type": "prize_competition",
            "frequency": "rolling",
            "volume": "low",
            "apply_method": "application",
            "tier": "competition"
        },
        "asme_ishow": {
            "name": "ASME ISHOW",
            "url": "https://asme.org/programs/competitions/ishow",
            "type": "innovation_competition",
            "frequency": "yearly",
            "volume": "low",
            "apply_method": "application",
            "specialty": "engineering",
            "tier": "competition"
        },
        
        # TECH COMPANY STARTUP PROGRAMS
        "autodesk_technology_impact": {
            "name": "Autodesk Technology Impact Program",
            "url": "https://autodesk.com/technology-impact-program",
            "type": "startup_program",
            "frequency": "rolling",
            "volume": "medium",
            "apply_method": "application",
            "tier": "startup_program"
        },
        "openai_startup_fund": {
            "name": "OpenAI Startup Fund",
            "url": "https://openai.com/startup-fund",
            "type": "startup_fund",
            "frequency": "rolling",
            "volume": "low",
            "apply_method": "application",
            "specialty": "ai",
            "tier": "startup_fund"
        },
        "frontier_ai_grants": {
            "name": "Frontier AI Grants",
            "url": "https://frontier.ai/grants",
            "type": "grant_program",
            "frequency": "rolling",
            "volume": "low",
            "apply_method": "application",
            "specialty": "ai",
            "tier": "grant"
        },
        "nvidia_grants": {
            "name": "NVIDIA Grants",
            "url": "https://nvidia.com/grants",
            "type": "grant_program",
            "frequency": "rolling",
            "volume": "low",
            "apply_method": "application",
            "specialty": "ai_gpu",
            "tier": "grant"
        },
        "replit_launchpad": {
            "name": "Replit Launchpad",
            "url": "https://replit.com/launchpad",
            "type": "startup_program",
            "frequency": "rolling",
            "volume": "medium",
            "apply_method": "application",
            "tier": "startup_program"
        },
        "figma_creator_fund": {
            "name": "Figma Creator Fund",
            "url": "https://figma.com/creator-fund",
            "type": "creator_fund",
            "frequency": "rolling",
            "volume": "medium",
            "apply_method": "application",
            "specialty": "design",
            "tier": "creator_fund"
        },
        "notion_startup_program": {
            "name": "Notion Startup Program",
            "url": "https://notion.so/startup-program",
            "type": "startup_program",
            "frequency": "rolling",
            "volume": "high",
            "apply_method": "application",
            "tier": "startup_program"
        },
        "hubspot_for_startups": {
            "name": "HubSpot for Startups",
            "url": "https://hubspot.com/startups",
            "type": "startup_program",
            "frequency": "rolling",
            "volume": "high",
            "apply_method": "application",
            "tier": "startup_program"
        },
        "twilio_startups": {
            "name": "Twilio Startups",
            "url": "https://twilio.com/startups",
            "type": "startup_program",
            "frequency": "rolling",
            "volume": "medium",
            "apply_method": "application",
            "tier": "startup_program"
        },
        
        # CLOUD & INFRASTRUCTURE STARTUP PROGRAMS
        "digitalocean_hatch": {
            "name": "DigitalOcean Hatch",
            "url": "https://digitalocean.com/hatch",
            "type": "startup_program",
            "frequency": "rolling",
            "volume": "high",
            "apply_method": "application",
            "tier": "startup_program"
        },
        "oracle_for_startups": {
            "name": "Oracle for Startups",
            "url": "https://oracle.com/startups",
            "type": "startup_program",
            "frequency": "rolling",
            "volume": "medium",
            "apply_method": "application",
            "tier": "startup_program"
        },
        "ovhcloud_startup": {
            "name": "OVHcloud Startup Program",
            "url": "https://ovhcloud.com/startup-program",
            "type": "startup_program",
            "frequency": "rolling",
            "volume": "medium",
            "apply_method": "application",
            "tier": "startup_program"
        },
        "ibm_startup_program": {
            "name": "IBM Startup Program",
            "url": "https://ibm.com/startup-program",
            "type": "startup_program",
            "frequency": "rolling",
            "volume": "medium",
            "apply_method": "application",
            "tier": "startup_program"
        },
        "cloudflare_startup": {
            "name": "Cloudflare Startup Program",
            "url": "https://cloudflare.com/startup-program",
            "type": "startup_program",
            "frequency": "rolling",
            "volume": "medium",
            "apply_method": "application",
            "tier": "startup_program"
        },
        "supabase_startup": {
            "name": "Supabase Startup Program",
            "url": "https://supabase.com/startup-program",
            "type": "startup_program",
            "frequency": "rolling",
            "volume": "medium",
            "apply_method": "application",
            "tier": "startup_program"
        },
        "render_startup": {
            "name": "Render Startup Program",
            "url": "https://render.com/startup-program",
            "type": "startup_program",
            "frequency": "rolling",
            "volume": "medium",
            "apply_method": "application",
            "tier": "startup_program"
        },
        "vercel_startup": {
            "name": "Vercel Startup Program",
            "url": "https://vercel.com/startup-program",
            "type": "startup_program",
            "frequency": "rolling",
            "volume": "medium",
            "apply_method": "application",
            "tier": "startup_program"
        },
        "github_startup": {
            "name": "GitHub Startup Program",
            "url": "https://github.com/startup-program",
            "type": "startup_program",
            "frequency": "rolling",
            "volume": "high",
            "apply_method": "application",
            "tier": "startup_program"
        },
        
        # CLIMATE & SUSTAINABILITY PROGRAMS
        "stripe_climate": {
            "name": "Stripe Climate",
            "url": "https://stripe.com/climate",
            "type": "climate_program",
            "frequency": "rolling",
            "volume": "medium",
            "apply_method": "application",
            "specialty": "carbon_removal",
            "tier": "climate"
        },
        
        # EDUCATIONAL & COMMUNITY PROGRAMS
        "yc_startup_school": {
            "name": "YC Startup School",
            "url": "https://startupschool.org",
            "type": "educational_program",
            "frequency": "quarterly",
            "volume": "high",
            "apply_method": "registration",
            "tier": "educational"
        },
        "founder_institute": {
            "name": "Founder Institute",
            "url": "https://fi.co",
            "type": "accelerator",
            "frequency": "quarterly",
            "volume": "medium",
            "apply_method": "application",
            "tier": "tier2"
        },
        "starta_accelerator": {
            "name": "Starta Accelerator",
            "url": "https://startaaccelerator.com",
            "type": "accelerator",
            "frequency": "quarterly",
            "volume": "low",
            "apply_method": "application",
            "tier": "tier2"
        },
        
        # VENTURE CAPITAL & INVESTMENT PROGRAMS
        "blueyard_capital": {
            "name": "BlueYard Capital",
            "url": "https://blueyard.com",
            "type": "vc_program",
            "frequency": "rolling",
            "volume": "low",
            "apply_method": "application",
            "tier": "vc"
        },
        "first_round_capital": {
            "name": "First Round Capital",
            "url": "https://firstround.com",
            "type": "vc_program",
            "frequency": "rolling",
            "volume": "low",
            "apply_method": "application",
            "tier": "vc"
        },
        "lux_capital": {
            "name": "Lux Capital",
            "url": "https://luxcapital.com",
            "type": "vc_program",
            "frequency": "rolling",
            "volume": "low",
            "apply_method": "application",
            "tier": "vc"
        },
        "a16z_start": {
            "name": "A16z START Program",
            "url": "https://a16z.com/start",
            "type": "vc_program",
            "frequency": "rolling",
            "volume": "low",
            "apply_method": "application",
            "tier": "vc"
        },
        "neo_scholars": {
            "name": "Neo Scholars",
            "url": "https://neo.com/scholars",
            "type": "fellowship_program",
            "frequency": "yearly",
            "volume": "low",
            "apply_method": "application",
            "tier": "fellowship"
        },
        "lightspeed_extreme": {
            "name": "Lightspeed Extreme Startups",
            "url": "https://lsvp.com/extreme-startups",
            "type": "vc_program",
            "frequency": "rolling",
            "volume": "low",
            "apply_method": "application",
            "tier": "vc"
        },
        
        # MEDIA & DEMO DAY OPPORTUNITIES
        "techcrunch_battlefield": {
            "name": "TechCrunch Startup Battlefield",
            "url": "https://techcrunch.com/startup-battlefield",
            "type": "competition",
            "frequency": "yearly",
            "volume": "low",
            "apply_method": "application",
            "tier": "competition"
        },
        "africa_tech_summit": {
            "name": "Africa Tech Summit",
            "url": "https://africatech.com",
            "type": "conference_competition",
            "frequency": "yearly",
            "volume": "low",
            "apply_method": "application",
            "region": "africa",
            "tier": "competition"
        },
        
        # AFRICA VC & INVESTMENT
        "future_africa": {
            "name": "Future Africa",
            "url": "https://future.africa",
            "type": "vc_program",
            "frequency": "rolling",
            "volume": "low",
            "apply_method": "application",
            "region": "africa",
            "tier": "vc"
        },
        "loftyinc_capital": {
            "name": "LoftyInc Capital",
            "url": "https://loftyinc.com",
            "type": "vc_program",
            "frequency": "rolling",
            "volume": "low",
            "apply_method": "application",
            "region": "africa",
            "tier": "vc"
        },
        "ingressive_capital": {
            "name": "Ingressive Capital",
            "url": "https://ingressive.co",
            "type": "vc_program",
            "frequency": "rolling",
            "volume": "low",
            "apply_method": "application",
            "region": "africa",
            "tier": "vc"
        },
        "saviu_ventures": {
            "name": "Saviu Ventures",
            "url": "https://saviu.vc",
            "type": "vc_program",
            "frequency": "rolling",
            "volume": "low",
            "apply_method": "application",
            "region": "africa",
            "tier": "vc"
        },
        "novastar_ventures": {
            "name": "Novastar Ventures",
            "url": "https://novastar.vc",
            "type": "vc_program",
            "frequency": "rolling",
            "volume": "low",
            "apply_method": "application",
            "region": "africa",
            "tier": "vc"
        },
        "tlcom_capital": {
            "name": "TLcom Capital",
            "url": "https://tlcom.co.uk",
            "type": "vc_program",
            "frequency": "rolling",
            "volume": "low",
            "apply_method": "application",
            "region": "africa",
            "tier": "vc"
        },
        "partech_africa": {
            "name": "Partech Africa",
            "url": "https://partechpartners.com/africa",
            "type": "vc_program",
            "frequency": "rolling",
            "volume": "low",
            "apply_method": "application",
            "region": "africa",
            "tier": "vc"
        },
        "chandaria_capital": {
            "name": "Chandaria Capital",
            "url": "https://chandariacapital.com",
            "type": "vc_program",
            "frequency": "rolling",
            "volume": "low",
            "apply_method": "application",
            "region": "africa",
            "tier": "vc"
        },
        "enza_capital": {
            "name": "Enza Capital",
            "url": "https://enza.capital",
            "type": "vc_program",
            "frequency": "rolling",
            "volume": "low",
            "apply_method": "application",
            "region": "africa",
            "tier": "vc"
        },
        "kepple_africa": {
            "name": "Kepple Africa Ventures",
            "url": "https://keppleafrica.com",
            "type": "vc_program",
            "frequency": "rolling",
            "volume": "low",
            "apply_method": "application",
            "region": "africa",
            "tier": "vc"
        },
        "goodwell_investments": {
            "name": "Goodwell Investments",
            "url": "https://goodwell.nl",
            "type": "vc_program",
            "frequency": "rolling",
            "volume": "low",
            "apply_method": "application",
            "region": "africa",
            "tier": "vc"
        },
        "algebra_ventures": {
            "name": "Algebra Ventures",
            "url": "https://algebraventures.com",
            "type": "vc_program",
            "frequency": "rolling",
            "volume": "low",
            "apply_method": "application",
            "region": "mena",
            "tier": "vc"
        },
        "echovc": {
            "name": "EchoVC",
            "url": "https://echovc.com",
            "type": "vc_program",
            "frequency": "rolling",
            "volume": "low",
            "apply_method": "application",
            "region": "africa",
            "tier": "vc"
        },
        
        # SPECIALIZED SECTOR ACCELERATORS
        "katapult_vc": {
            "name": "Katapult VC",
            "url": "https://katapult.vc",
            "type": "impact_accelerator",
            "frequency": "quarterly",
            "volume": "low",
            "apply_method": "application",
            "specialty": "impact",
            "tier": "specialty"
        },
        "blue_impact_fund": {
            "name": "Blue Impact Fund",
            "url": "https://blueimpactfund.com",
            "type": "impact_fund",
            "frequency": "rolling",
            "volume": "low",
            "apply_method": "application",
            "specialty": "ocean_sustainability",
            "tier": "specialty"
        },
        "acumen_fund": {
            "name": "Acumen Fund",
            "url": "https://acumen.org",
            "type": "impact_fund",
            "frequency": "rolling",
            "volume": "low",
            "apply_method": "application",
            "specialty": "social_impact",
            "tier": "specialty"
        },
        "gsma_agritech": {
            "name": "GSMA AgriTech",
            "url": "https://gsma.com/agritech",
            "type": "sector_program",
            "frequency": "rolling",
            "volume": "low",
            "apply_method": "application",
            "specialty": "agriculture",
            "tier": "sector"
        },
        "gsma_digital_utilities": {
            "name": "GSMA Digital Utilities",
            "url": "https://gsma.com/digital-utilities",
            "type": "sector_program",
            "frequency": "rolling",
            "volume": "low",
            "apply_method": "application",
            "specialty": "utilities",
            "tier": "sector"
        },
        
        # LEADERSHIP & FELLOWSHIP PROGRAMS
        "seed_transformation": {
            "name": "Seed Transformation Program (Stanford)",
            "url": "https://seed.stanford.edu",
            "type": "fellowship_program",
            "frequency": "yearly",
            "volume": "low",
            "apply_method": "application",
            "tier": "fellowship"
        },
        "yali": {
            "name": "Young African Leaders Initiative (YALI)",
            "url": "https://yali.state.gov",
            "type": "leadership_program",
            "frequency": "yearly",
            "volume": "medium",
            "apply_method": "application",
            "region": "africa",
            "tier": "leadership"
        },
        "obama_africa_leaders": {
            "name": "Obama Africa Leaders",
            "url": "https://obamaafricaleaders.org",
            "type": "leadership_program",
            "frequency": "yearly",
            "volume": "low",
            "apply_method": "application",
            "region": "africa",
            "tier": "leadership"
        },
        "mandela_washington": {
            "name": "Mandela Washington Fellowship",
            "url": "https://mandelawashingtonfellowship.org",
            "type": "fellowship_program",
            "frequency": "yearly",
            "volume": "low",
            "apply_method": "application",
            "region": "africa",
            "tier": "fellowship"
        }
    },

    # ═══════════════════════════════════════════════════════════════
    # COMPETITIONS & CHALLENGES
    # ═══════════════════════════════════════════════════════════════
    "competitions": {
        "kaggle": {
            "name": "Kaggle Competitions",
            "url": "https://www.kaggle.com/competitions",
            "api": "https://www.kaggle.com/api/v1/competitions/list",
            "type": "competition",
            "frequency": "daily",
            "volume": "medium",
            "apply_method": "submission"
        },
        "devpost": {
            "name": "Devpost Hackathons",
            "url": "https://devpost.com/hackathons",
            "type": "hackathon",
            "frequency": "daily",
            "volume": "high",
            "apply_method": "registration"
        },
        "hackathon_io": {
            "name": "Hackathon.io",
            "url": "https://www.hackathon.io",
            "type": "hackathon",
            "frequency": "daily",
            "volume": "medium",
            "apply_method": "registration"
        },
        "mlh": {
            "name": "Major League Hacking",
            "url": "https://mlh.io/seasons/2025/events",
            "type": "hackathon",
            "frequency": "weekly",
            "volume": "medium",
            "apply_method": "registration"
        },
        "xprize": {
            "name": "XPRIZE",
            "url": "https://www.xprize.org/prizes",
            "type": "competition",
            "frequency": "yearly",
            "volume": "low",
            "apply_method": "application"
        },
        "herox": {
            "name": "HeroX Challenges",
            "url": "https://www.herox.com/crowdsourcing-projects",
            "type": "competition",
            "frequency": "daily",
            "volume": "medium",
            "apply_method": "submission"
        },
        "innocentive": {
            "name": "InnoCentive",
            "url": "https://www.innocentive.com/ar/challenge/browse",
            "type": "competition",
            "frequency": "daily",
            "volume": "medium",
            "apply_method": "submission"
        },
        "topcoder": {
            "name": "Topcoder",
            "url": "https://www.topcoder.com/challenges",
            "type": "competition",
            "frequency": "daily",
            "volume": "high",
            "apply_method": "submission"
        },
    },

    # ═══════════════════════════════════════════════════════════════
    # COMPANY CAREER PAGES - Top Tech
    # ═══════════════════════════════════════════════════════════════
    "company_careers": {
        "google": {
            "name": "Google Careers",
            "url": "https://careers.google.com/jobs",
            "type": "jobs",
            "frequency": "daily",
            "volume": "high",
            "apply_method": "direct"
        },
        "apple": {
            "name": "Apple Jobs",
            "url": "https://jobs.apple.com",
            "type": "jobs",
            "frequency": "daily",
            "volume": "high",
            "apply_method": "direct"
        },
        "meta": {
            "name": "Meta Careers",
            "url": "https://www.metacareers.com/jobs",
            "type": "jobs",
            "frequency": "daily",
            "volume": "high",
            "apply_method": "direct"
        },
        "amazon": {
            "name": "Amazon Jobs",
            "url": "https://www.amazon.jobs",
            "type": "jobs",
            "frequency": "daily",
            "volume": "high",
            "apply_method": "direct"
        },
        "microsoft": {
            "name": "Microsoft Careers",
            "url": "https://careers.microsoft.com",
            "type": "jobs",
            "frequency": "daily",
            "volume": "high",
            "apply_method": "direct"
        },
        "netflix": {
            "name": "Netflix Jobs",
            "url": "https://jobs.netflix.com",
            "type": "jobs",
            "frequency": "daily",
            "volume": "medium",
            "apply_method": "direct"
        },
        "stripe": {
            "name": "Stripe Jobs",
            "url": "https://stripe.com/jobs",
            "type": "jobs",
            "frequency": "daily",
            "volume": "medium",
            "apply_method": "direct"
        },
        "openai": {
            "name": "OpenAI Careers",
            "url": "https://openai.com/careers",
            "type": "jobs",
            "frequency": "daily",
            "volume": "low",
            "apply_method": "direct"
        },
        "anthropic": {
            "name": "Anthropic Careers",
            "url": "https://www.anthropic.com/careers",
            "type": "jobs",
            "frequency": "daily",
            "volume": "low",
            "apply_method": "direct"
        },
        "tesla": {
            "name": "Tesla Careers",
            "url": "https://www.tesla.com/careers",
            "type": "jobs",
            "frequency": "daily",
            "volume": "medium",
            "apply_method": "direct"
        },
        "spacex": {
            "name": "SpaceX Careers",
            "url": "https://www.spacex.com/careers",
            "type": "jobs",
            "frequency": "daily",
            "volume": "medium",
            "apply_method": "direct"
        },
        "nvidia": {
            "name": "NVIDIA Careers",
            "url": "https://nvidia.wd5.myworkdayjobs.com/NVIDIAExternalCareerSite",
            "type": "jobs",
            "frequency": "daily",
            "volume": "medium",
            "apply_method": "direct"
        },
        "salesforce": {
            "name": "Salesforce Careers",
            "url": "https://www.salesforce.com/company/careers",
            "type": "jobs",
            "frequency": "daily",
            "volume": "medium",
            "apply_method": "direct"
        },
        "airbnb": {
            "name": "Airbnb Careers",
            "url": "https://careers.airbnb.com",
            "type": "jobs",
            "frequency": "daily",
            "volume": "medium",
            "apply_method": "direct"
        },
        "uber": {
            "name": "Uber Careers",
            "url": "https://www.uber.com/us/en/careers",
            "type": "jobs",
            "frequency": "daily",
            "volume": "medium",
            "apply_method": "direct"
        },
        "lyft": {
            "name": "Lyft Careers",
            "url": "https://www.lyft.com/careers",
            "type": "jobs",
            "frequency": "daily",
            "volume": "medium",
            "apply_method": "direct"
        },
        "coinbase": {
            "name": "Coinbase Careers",
            "url": "https://www.coinbase.com/careers",
            "type": "jobs",
            "frequency": "daily",
            "volume": "medium",
            "apply_method": "direct"
        },
        "robinhood": {
            "name": "Robinhood Careers",
            "url": "https://robinhood.com/us/en/careers",
            "type": "jobs",
            "frequency": "daily",
            "volume": "medium",
            "apply_method": "direct"
        },
        "plaid": {
            "name": "Plaid Careers",
            "url": "https://plaid.com/careers",
            "type": "jobs",
            "frequency": "daily",
            "volume": "low",
            "apply_method": "direct"
        },
        "figma": {
            "name": "Figma Careers",
            "url": "https://www.figma.com/careers",
            "type": "jobs",
            "frequency": "daily",
            "volume": "low",
            "apply_method": "direct"
        },
        "notion": {
            "name": "Notion Careers",
            "url": "https://www.notion.so/careers",
            "type": "jobs",
            "frequency": "daily",
            "volume": "low",
            "apply_method": "direct"
        },
        "discord": {
            "name": "Discord Careers",
            "url": "https://discord.com/careers",
            "type": "jobs",
            "frequency": "daily",
            "volume": "low",
            "apply_method": "direct"
        },
        "databricks": {
            "name": "Databricks Careers",
            "url": "https://www.databricks.com/company/careers",
            "type": "jobs",
            "frequency": "daily",
            "volume": "medium",
            "apply_method": "direct"
        },
        "snowflake": {
            "name": "Snowflake Careers",
            "url": "https://careers.snowflake.com",
            "type": "jobs",
            "frequency": "daily",
            "volume": "medium",
            "apply_method": "direct"
        },
    },

    # ═══════════════════════════════════════════════════════════════
    # INTERNSHIPS & EARLY CAREER
    # ═══════════════════════════════════════════════════════════════
    "internships": {
        "handshake": {
            "name": "Handshake",
            "url": "https://app.joinhandshake.com/stu/postings",
            "type": "internships",
            "frequency": "daily",
            "volume": "high",
            "apply_method": "direct"
        },
        "wayup": {
            "name": "WayUp",
            "url": "https://www.wayup.com/s/internships",
            "type": "internships",
            "frequency": "daily",
            "volume": "high",
            "apply_method": "direct"
        },
        "ripplematch": {
            "name": "RippleMatch",
            "url": "https://ripplematch.com/index",
            "type": "internships",
            "frequency": "daily",
            "volume": "medium",
            "apply_method": "direct"
        },
        "intern_supply": {
            "name": "Intern.Supply",
            "url": "https://intern.supply",
            "type": "internships",
            "frequency": "daily",
            "volume": "medium",
            "apply_method": "direct"
        },
    },

    # ═══════════════════════════════════════════════════════════════
    # DIVERSITY & INCLUSION FOCUSED
    # ═══════════════════════════════════════════════════════════════
    "diversity": {
        "diversity_jobs": {
            "name": "DiversityJobs",
            "url": "https://www.diversityjobs.com",
            "type": "jobs",
            "frequency": "daily",
            "volume": "medium",
            "apply_method": "direct"
        },
        "jopwell": {
            "name": "Jopwell",
            "url": "https://www.jopwell.com/jobs",
            "type": "jobs",
            "frequency": "daily",
            "volume": "medium",
            "apply_method": "direct"
        },
        "powertofly": {
            "name": "PowerToFly",
            "url": "https://powertofly.com/jobs",
            "type": "jobs",
            "frequency": "daily",
            "volume": "medium",
            "apply_method": "direct"
        },
        "fairygodboss": {
            "name": "Fairygodboss",
            "url": "https://fairygodboss.com/jobs",
            "type": "jobs",
            "frequency": "daily",
            "volume": "medium",
            "apply_method": "direct"
        },
        "hiretechladies": {
            "name": "Hire Tech Ladies",
            "url": "https://www.hiretechladies.com/jobs",
            "type": "jobs",
            "frequency": "daily",
            "volume": "medium",
            "apply_method": "direct"
        },
        "outintech": {
            "name": "Out in Tech",
            "url": "https://outintech.com/jobs",
            "type": "jobs",
            "frequency": "daily",
            "volume": "low",
            "apply_method": "direct"
        },
    },

    # ═══════════════════════════════════════════════════════════════
    # GOVERNMENT & PUBLIC SECTOR
    # ═══════════════════════════════════════════════════════════════
    "government": {
        "usajobs": {
            "name": "USAJOBS",
            "url": "https://www.usajobs.gov",
            "api": "https://data.usajobs.gov/api/search",
            "type": "government_jobs",
            "frequency": "daily",
            "volume": "high",
            "apply_method": "application"
        },
        "govloop": {
            "name": "GovLoop",
            "url": "https://www.govloop.com/careers",
            "type": "government_jobs",
            "frequency": "daily",
            "volume": "medium",
            "apply_method": "direct"
        },
        "clearancejobs": {
            "name": "ClearanceJobs",
            "url": "https://www.clearancejobs.com",
            "type": "government_jobs",
            "frequency": "daily",
            "volume": "medium",
            "apply_method": "direct"
        },
    },

    # ═══════════════════════════════════════════════════════════════
    # INTERNATIONAL
    # ═══════════════════════════════════════════════════════════════
    "international": {
        "unjobs": {
            "name": "UN Jobs",
            "url": "https://careers.un.org",
            "type": "international",
            "frequency": "daily",
            "volume": "medium",
            "apply_method": "application"
        },
        "devex": {
            "name": "Devex",
            "url": "https://www.devex.com/jobs",
            "type": "international",
            "frequency": "daily",
            "volume": "medium",
            "apply_method": "direct"
        },
        "idealist": {
            "name": "Idealist",
            "url": "https://www.idealist.org/en/jobs",
            "type": "nonprofit",
            "frequency": "daily",
            "volume": "high",
            "apply_method": "direct"
        },
        "reliefweb": {
            "name": "ReliefWeb",
            "url": "https://reliefweb.int/jobs",
            "type": "humanitarian",
            "frequency": "daily",
            "volume": "medium",
            "apply_method": "direct"
        },
    },

    # ═══════════════════════════════════════════════════════════════
    # TECH / AI / LEARNING / BOOTCAMPS - 70+ Educational Platforms
    # ═══════════════════════════════════════════════════════════════
    "tech_learning_platforms": {
        # MAJOR MOOC PLATFORMS
        "coursera": {
            "name": "Coursera",
            "url": "https://www.coursera.org",
            "type": "education",
            "subtype": "mooc",
            "offers": ["professional_certificates", "scholarships", "courses"],
            "frequency": "daily",
            "tier": 1,
            "volume": "high",
            "region": "global"
        },
        "edx": {
            "name": "edX",
            "url": "https://www.edx.org",
            "type": "education",
            "subtype": "mooc",
            "offers": ["certificates", "degrees", "scholarships"],
            "frequency": "daily",
            "tier": 1,
            "volume": "high",
            "region": "global"
        },
        "udacity": {
            "name": "Udacity",
            "url": "https://www.udacity.com",
            "type": "education",
            "subtype": "nanodegree",
            "offers": ["nanodegree_scholarships", "tech_programs"],
            "frequency": "daily",
            "tier": 1,
            "volume": "high",
            "specialty": "tech"
        },
        "udemy": {
            "name": "Udemy",
            "url": "https://www.udemy.com",
            "type": "education",
            "subtype": "marketplace",
            "offers": ["instructor_income", "courses"],
            "frequency": "daily",
            "tier": 1,
            "volume": "high",
            "monetization": "instructor_revenue"
        },

        # SPECIALIZED TECH LEARNING
        "datacamp": {
            "name": "DataCamp",
            "url": "https://www.datacamp.com",
            "type": "education",
            "subtype": "data_science",
            "offers": ["certificates", "competitions"],
            "frequency": "daily",
            "tier": 2,
            "specialty": "data_science"
        },
        "kaggle": {
            "name": "Kaggle",
            "url": "https://www.kaggle.com",
            "type": "education",
            "subtype": "competitions",
            "offers": ["competitions", "jobs", "datasets", "notebooks"],
            "frequency": "daily",
            "tier": 1,
            "volume": "high",
            "specialty": "machine_learning"
        },

        # AI/ML SPECIALIZED PLATFORMS
        "deeplearning_ai": {
            "name": "DeepLearning.AI",
            "url": "https://www.deeplearning.ai",
            "type": "education",
            "subtype": "ai_specialization",
            "offers": ["courses", "certificates", "specializations"],
            "frequency": "weekly",
            "tier": 1,
            "specialty": "ai_ml"
        },
        "openai_learn": {
            "name": "OpenAI Learning Resources",
            "url": "https://openai.com/learn",
            "type": "education",
            "subtype": "ai_resources",
            "offers": ["documentation", "guides", "examples"],
            "frequency": "weekly",
            "tier": 1,
            "specialty": "ai"
        },
        "google_ai_education": {
            "name": "Google AI Education",
            "url": "https://ai.google/education",
            "type": "education",
            "subtype": "corporate_training",
            "offers": ["courses", "research", "tools"],
            "frequency": "weekly",
            "tier": 1,
            "specialty": "ai"
        },
        "google_developers": {
            "name": "Google Developers Programs",
            "url": "https://developers.google.com/programs",
            "type": "education",
            "subtype": "developer_programs",
            "offers": ["certifications", "programs", "grants"],
            "frequency": "weekly",
            "tier": 1,
            "specialty": "development"
        },
        "microsoft_learn": {
            "name": "Microsoft Learn",
            "url": "https://microsoft.com/learn",
            "type": "education",
            "subtype": "corporate_training",
            "offers": ["certifications", "learning_paths", "credentials"],
            "frequency": "daily",
            "tier": 1,
            "specialty": "cloud_development"
        },
        "aws_training": {
            "name": "AWS Training",
            "url": "https://aws.amazon.com/training",
            "type": "education",
            "subtype": "cloud_training",
            "offers": ["certifications", "training", "credits"],
            "frequency": "daily",
            "tier": 1,
            "specialty": "cloud_aws"
        },

        # AI RESEARCH & COMMUNITY PLATFORMS
        "google_ai_blog": {
            "name": "Google AI Blog",
            "url": "https://ai.googleblog.com",
            "type": "education",
            "subtype": "research_announcements",
            "offers": ["announcements", "research", "opportunities"],
            "frequency": "weekly",
            "tier": 2,
            "specialty": "ai_research"
        },
        "huggingface": {
            "name": "Hugging Face",
            "url": "https://huggingface.co",
            "type": "education",
            "subtype": "open_source_ai",
            "offers": ["grants", "programs", "community", "spaces"],
            "frequency": "daily",
            "tier": 1,
            "specialty": "ai_open_source"
        },
        "fast_ai": {
            "name": "Fast.ai",
            "url": "https://www.fast.ai",
            "type": "education",
            "subtype": "ai_courses",
            "offers": ["courses", "community", "research"],
            "frequency": "weekly",
            "tier": 1,
            "specialty": "practical_ai"
        },
        "pytorch": {
            "name": "PyTorch",
            "url": "https://pytorch.org",
            "type": "education",
            "subtype": "framework_ecosystem",
            "offers": ["tutorials", "community", "jobs"],
            "frequency": "weekly",
            "tier": 1,
            "specialty": "deep_learning"
        },
        "tensorflow": {
            "name": "TensorFlow",
            "url": "https://www.tensorflow.org/resources",
            "type": "education",
            "subtype": "framework_resources",
            "offers": ["tutorials", "certifications", "community"],
            "frequency": "weekly",
            "tier": 1,
            "specialty": "machine_learning"
        },
        "papers_with_code": {
            "name": "Papers with Code",
            "url": "https://paperswithcode.com",
            "type": "education",
            "subtype": "research_platform",
            "offers": ["sota_challenges", "research_collab"],
            "frequency": "daily",
            "tier": 1,
            "specialty": "ml_research"
        },
        "openml": {
            "name": "OpenML",
            "url": "https://www.openml.org",
            "type": "education",
            "subtype": "collaborative_ml",
            "offers": ["datasets", "experiments", "competitions"],
            "frequency": "weekly",
            "tier": 2,
            "specialty": "collaborative_ml"
        },

        # DEVELOPER MONETIZATION PLATFORMS
        "replit_bounties": {
            "name": "Replit Bounties",
            "url": "https://replit.com/bounties",
            "type": "education",
            "subtype": "coding_bounties",
            "offers": ["bounties", "coding_jobs"],
            "frequency": "daily",
            "tier": 2,
            "monetization": "bounties"
        },
        "github_sponsors": {
            "name": "GitHub Sponsors",
            "url": "https://github.com/sponsors",
            "type": "education",
            "subtype": "open_source_funding",
            "offers": ["sponsorships", "funding"],
            "frequency": "daily",
            "tier": 1,
            "monetization": "sponsorship"
        },
        "github_marketplace": {
            "name": "GitHub Marketplace",
            "url": "https://github.com/marketplace",
            "type": "education",
            "subtype": "dev_tools_ecosystem",
            "offers": ["paid_tools", "developer_revenue"],
            "frequency": "weekly",
            "tier": 2,
            "monetization": "marketplace"
        },
        "gitcoin": {
            "name": "Gitcoin",
            "url": "https://gitcoin.co",
            "type": "education",
            "subtype": "web3_bounties",
            "offers": ["bounties", "grants", "hackathons"],
            "frequency": "daily",
            "tier": 2,
            "specialty": "web3_development"
        },

        # CONTENT & WRITING PLATFORMS
        "dev_to": {
            "name": "Dev.to",
            "url": "https://dev.to",
            "type": "education",
            "subtype": "developer_content",
            "offers": ["writing", "sponsorships", "community"],
            "frequency": "daily",
            "tier": 2,
            "monetization": "content_sponsorship"
        },
        "hashnode": {
            "name": "Hashnode",
            "url": "https://hashnode.com",
            "type": "education",
            "subtype": "tech_blogging",
            "offers": ["paid_writing", "blogging_platform"],
            "frequency": "daily",
            "tier": 2,
            "monetization": "writing_programs"
        },
        "medium_partner": {
            "name": "Medium Partner Program",
            "url": "https://medium.com/partner-program",
            "type": "education",
            "subtype": "writing_monetization",
            "offers": ["paid_writing", "subscriptions"],
            "frequency": "daily",
            "tier": 2,
            "monetization": "content_revenue"
        },
        "substack": {
            "name": "Substack",
            "url": "https://substack.com",
            "type": "education",
            "subtype": "newsletter_platform",
            "offers": ["newsletter_monetization", "subscriptions"],
            "frequency": "daily",
            "tier": 2,
            "monetization": "subscription_revenue"
        },
        "ghost": {
            "name": "Ghost",
            "url": "https://ghost.org",
            "type": "education",
            "subtype": "creator_platform",
            "offers": ["publishing", "creator_opportunities"],
            "frequency": "weekly",
            "tier": 3,
            "monetization": "creator_economy"
        },
        "indie_hackers": {
            "name": "Indie Hackers",
            "url": "https://www.indiehackers.com",
            "type": "education",
            "subtype": "founder_community",
            "offers": ["collaborations", "networking", "opportunities"],
            "frequency": "daily",
            "tier": 2,
            "specialty": "entrepreneurship"
        },

        # CODING BOOTCAMPS & STRUCTURED PROGRAMS
        "freecodecamp": {
            "name": "freeCodeCamp",
            "url": "https://www.freecodecamp.org",
            "type": "education",
            "subtype": "coding_bootcamp",
            "offers": ["certificates", "local_groups", "curriculum"],
            "frequency": "daily",
            "tier": 1,
            "volume": "high",
            "cost": "free"
        },
        "odin_project": {
            "name": "The Odin Project",
            "url": "https://www.theodinproject.com",
            "type": "education",
            "subtype": "full_stack_curriculum",
            "offers": ["full_stack_training", "community"],
            "frequency": "weekly",
            "tier": 2,
            "cost": "free"
        },
        "app_academy": {
            "name": "App Academy",
            "url": "https://www.appacademy.io",
            "type": "education",
            "subtype": "intensive_bootcamp",
            "offers": ["bootcamp", "job_placement"],
            "frequency": "weekly",
            "tier": 2,
            "specialty": "full_stack"
        },
        "bloom_tech": {
            "name": "BloomTech (Lambda School)",
            "url": "https://www.bloomtech.com",
            "type": "education",
            "subtype": "income_share_bootcamp",
            "offers": ["bootcamp", "isa_programs"],
            "frequency": "weekly",
            "tier": 2,
            "financing": "income_share_agreement"
        },
        "general_assembly": {
            "name": "General Assembly",
            "url": "https://generalassemb.ly",
            "type": "education",
            "subtype": "skills_bootcamp",
            "offers": ["bootcamps", "workshops", "corporate_training"],
            "frequency": "weekly",
            "tier": 2,
            "specialty": "design_tech"
        },
        "le_wagon": {
            "name": "Le Wagon",
            "url": "https://www.lewagon.com",
            "type": "education",
            "subtype": "coding_bootcamp",
            "offers": ["bootcamp", "global_campuses"],
            "frequency": "weekly",
            "tier": 2,
            "region": "global",
            "specialty": "web_development"
        },
        "microverse": {
            "name": "Microverse",
            "url": "https://www.microverse.org",
            "type": "education",
            "subtype": "remote_dev_school",
            "offers": ["remote_training", "global_program"],
            "frequency": "weekly",
            "tier": 2,
            "region": "global",
            "format": "remote"
        },
        "alx_africa": {
            "name": "ALX Africa",
            "url": "https://www.alxafrica.com",
            "type": "education",
            "subtype": "african_tech_school",
            "offers": ["software_engineering", "african_focus"],
            "frequency": "weekly",
            "tier": 2,
            "region": "africa",
            "specialty": "software_engineering"
        },
        "holberton": {
            "name": "Holberton School",
            "url": "https://www.holbertonschool.com",
            "type": "education",
            "subtype": "project_based_school",
            "offers": ["software_engineering", "peer_learning"],
            "frequency": "weekly",
            "tier": 2,
            "methodology": "project_based"
        },
        "andela": {
            "name": "Andela",
            "url": "https://andela.com",
            "type": "education",
            "subtype": "engineering_network",
            "offers": ["talent_network", "engineering_jobs"],
            "frequency": "daily",
            "tier": 2,
            "region": "africa_global",
            "specialty": "engineering"
        },

        # PREMIUM LEARNING PLATFORMS
        "pluralsight": {
            "name": "Pluralsight",
            "url": "https://www.pluralsight.com",
            "type": "education",
            "subtype": "tech_skills_platform",
            "offers": ["skill_assessments", "learning_paths"],
            "frequency": "daily",
            "tier": 2,
            "specialty": "enterprise_tech"
        },
        "egghead": {
            "name": "Egghead.io",
            "url": "https://egghead.io",
            "type": "education",
            "subtype": "web_dev_platform",
            "offers": ["concise_tutorials", "expert_instructors"],
            "frequency": "weekly",
            "tier": 2,
            "specialty": "web_development"
        },
        "frontend_masters": {
            "name": "Frontend Masters",
            "url": "https://frontendmasters.com",
            "type": "education",
            "subtype": "frontend_specialization",
            "offers": ["expert_courses", "workshops"],
            "frequency": "weekly",
            "tier": 2,
            "specialty": "frontend"
        },
        "scrimba": {
            "name": "Scrimba",
            "url": "https://scrimba.com",
            "type": "education",
            "subtype": "interactive_coding",
            "offers": ["interactive_courses", "bootcamp"],
            "frequency": "weekly",
            "tier": 2,
            "specialty": "web_development"
        },
        "codecademy": {
            "name": "Codecademy",
            "url": "https://www.codecademy.com",
            "type": "education",
            "subtype": "interactive_learning",
            "offers": ["interactive_courses", "career_paths"],
            "frequency": "daily",
            "tier": 2,
            "specialty": "programming_basics"
        },

        # UNIVERSITY & ACADEMIC PLATFORMS
        "cs50_harvard": {
            "name": "CS50 Harvard",
            "url": "https://cs50.harvard.edu",
            "type": "education",
            "subtype": "university_course",
            "offers": ["computer_science", "certificates"],
            "frequency": "weekly",
            "tier": 1,
            "institution": "harvard",
            "cost": "free"
        },
        "mit_ocw": {
            "name": "MIT OpenCourseWare",
            "url": "https://ocw.mit.edu",
            "type": "education",
            "subtype": "open_courseware",
            "offers": ["mit_courses", "free_materials"],
            "frequency": "weekly",
            "tier": 1,
            "institution": "mit",
            "cost": "free"
        },
        "stanford_online": {
            "name": "Stanford Online",
            "url": "https://online.stanford.edu",
            "type": "education",
            "subtype": "university_online",
            "offers": ["stanford_courses", "certificates"],
            "frequency": "weekly",
            "tier": 1,
            "institution": "stanford"
        },

        # SPECIALIZED AI/ML INSTITUTIONS & EVENTS
        "nvidia_dli": {
            "name": "NVIDIA Deep Learning Institute",
            "url": "https://www.nvidia.com/dli",
            "type": "education",
            "subtype": "deep_learning_institute",
            "offers": ["dl_courses", "certifications", "workshops"],
            "frequency": "weekly",
            "tier": 1,
            "specialty": "deep_learning_gpu"
        },
        "deep_learning_indaba": {
            "name": "Deep Learning Indaba",
            "url": "https://www.deeplearningindaba.com",
            "type": "education",
            "subtype": "ai_conference",
            "offers": ["conferences", "workshops", "community"],
            "frequency": "yearly",
            "tier": 2,
            "region": "africa",
            "specialty": "ai_africa"
        },
        "deep_learning_indaba_x": {
            "name": "Deep Learning IndabaX",
            "url": "https://www.deeplearningindabaX.com",
            "type": "education",
            "subtype": "regional_ai_events",
            "offers": ["regional_events", "workshops"],
            "frequency": "yearly",
            "tier": 2,
            "region": "africa_regional"
        },
        "hpc_wire": {
            "name": "HPCwire Events",
            "url": "https://www.hpcwire.com/events",
            "type": "education",
            "subtype": "hpc_opportunities",
            "offers": ["hpc_events", "supercomputing"],
            "frequency": "weekly",
            "tier": 3,
            "specialty": "high_performance_computing"
        },

        # ACADEMIC CONFERENCES & RESEARCH
        "ieee_conferences": {
            "name": "IEEE Conferences",
            "url": "https://www.ieee.org/conferences_events",
            "type": "education",
            "subtype": "academic_conferences",
            "offers": ["conferences", "publications", "networking"],
            "frequency": "weekly",
            "tier": 2,
            "specialty": "engineering_research"
        },
        "acm_conferences": {
            "name": "ACM Conferences",
            "url": "https://www.acm.org/conferences",
            "type": "education",
            "subtype": "computing_conferences",
            "offers": ["conferences", "publications", "community"],
            "frequency": "weekly",
            "tier": 2,
            "specialty": "computer_science"
        },
        "neurips": {
            "name": "NeurIPS",
            "url": "https://neurips.cc",
            "type": "education",
            "subtype": "ai_conference",
            "offers": ["conference", "competitions", "workshops"],
            "frequency": "yearly",
            "tier": 1,
            "specialty": "neural_computation"
        },
        "iclr": {
            "name": "ICLR",
            "url": "https://iclr.cc",
            "type": "education",
            "subtype": "learning_representations",
            "offers": ["conference", "papers", "community"],
            "frequency": "yearly",
            "tier": 1,
            "specialty": "representation_learning"
        },
        "icml": {
            "name": "ICML",
            "url": "https://icml.cc",
            "type": "education",
            "subtype": "machine_learning_conference",
            "offers": ["conference", "research", "networking"],
            "frequency": "yearly",
            "tier": 1,
            "specialty": "machine_learning"
        },
        "cvpr": {
            "name": "CVPR",
            "url": "https://cvpr.thecvf.com",
            "type": "education",
            "subtype": "computer_vision",
            "offers": ["conference", "computer_vision", "research"],
            "frequency": "yearly",
            "tier": 1,
            "specialty": "computer_vision"
        },
        "eccv": {
            "name": "ECCV",
            "url": "https://eccv202x.org",
            "type": "education",
            "subtype": "european_computer_vision",
            "offers": ["conference", "research", "european_focus"],
            "frequency": "biannual",
            "tier": 1,
            "region": "europe",
            "specialty": "computer_vision"
        },

        # CLOUD & COLLABORATION PLATFORMS
        "google_colab": {
            "name": "Google Colab",
            "url": "https://colab.research.google.com",
            "type": "education",
            "subtype": "cloud_notebooks",
            "offers": ["hosted_notebooks", "collaboration"],
            "frequency": "daily",
            "tier": 1,
            "specialty": "data_science_notebooks"
        },
        "modal_examples": {
            "name": "Modal Examples",
            "url": "https://modal.com/examples",
            "type": "education",
            "subtype": "cloud_platform",
            "offers": ["jobs", "grants", "builders_program"],
            "frequency": "weekly",
            "tier": 2,
            "specialty": "serverless_ml"
        },
        "replicate_labs": {
            "name": "Replicate Labs",
            "url": "https://replicatelabs.com",
            "type": "education",
            "subtype": "ml_deployment",
            "offers": ["developers_program", "model_deployment"],
            "frequency": "weekly",
            "tier": 2,
            "specialty": "ml_deployment"
        },
        "runpod_community": {
            "name": "RunPod Community",
            "url": "https://runpod.io",
            "type": "education",
            "subtype": "gpu_cloud_community",
            "offers": ["community", "bounties", "gpu_compute"],
            "frequency": "weekly",
            "tier": 2,
            "specialty": "gpu_cloud"
        },
        "huggingface_spaces": {
            "name": "Hugging Face Spaces",
            "url": "https://huggingface.co/spaces",
            "type": "education",
            "subtype": "ml_portfolio",
            "offers": ["showcase_work", "community"],
            "frequency": "daily",
            "tier": 2,
            "specialty": "ml_demos"
        },
        "kaggle_kernels": {
            "name": "Kaggle Kernels",
            "url": "https://www.kaggle.com/kernels",
            "type": "education",
            "subtype": "data_science_portfolio",
            "offers": ["portfolio", "hiring_visibility"],
            "frequency": "daily",
            "tier": 1,
            "specialty": "data_science"
        },

        # ML COMMUNITIES & SPECIALIZED PLATFORMS
        "mlops_community": {
            "name": "MLOps Community",
            "url": "https://mlops.community",
            "type": "education",
            "subtype": "mlops_specialization",
            "offers": ["jobs", "collaborations", "community"],
            "frequency": "daily",
            "tier": 2,
            "specialty": "mlops"
        },
        "weights_and_biases": {
            "name": "Weights & Biases",
            "url": "https://weightsandbiases.com",
            "type": "education",
            "subtype": "ml_tools_community",
            "offers": ["community", "tools", "best_practices"],
            "frequency": "weekly",
            "tier": 2,
            "specialty": "ml_experiment_tracking"
        },
        "wandb_sweeps": {
            "name": "Wandb Sweeps",
            "url": "https://wandb.ai/sweeps",
            "type": "education",
            "subtype": "mlops_competitions",
            "offers": ["competitions", "use_cases", "optimization"],
            "frequency": "weekly",
            "tier": 2,
            "specialty": "hyperparameter_optimization"
        },
        "papers_with_code_ai": {
            "name": "Papers with Code AI Area",
            "url": "https://paperswithcode.com/area/ai",
            "type": "education",
            "subtype": "research_collaboration",
            "offers": ["research_collab", "state_of_art"],
            "frequency": "daily",
            "tier": 1,
            "specialty": "ai_research_collaboration"
        }
    },

    # ═══════════════════════════════════════════════════════════════
    # CLIMATE / SUSTAINABILITY / GREEN JOBS - 60+ Environmental Platforms
    # ═══════════════════════════════════════════════════════════════
    "climate_sustainability": {
        # CLIMATE ACTION & POLICY ORGANIZATIONS
        "climate_links": {
            "name": "Climate Links",
            "url": "https://www.climatelinks.org/opportunities",
            "type": "climate",
            "subtype": "policy_opportunities",
            "offers": ["opportunities", "funding", "partnerships"],
            "frequency": "weekly",
            "tier": 1,
            "specialty": "climate_policy",
            "region": "global"
        },
        "climate_kic": {
            "name": "Climate-KIC",
            "url": "https://www.climate-kic.org",
            "type": "climate",
            "subtype": "innovation_community",
            "offers": ["innovation_programs", "startups", "education"],
            "frequency": "weekly",
            "tier": 1,
            "specialty": "climate_innovation",
            "region": "europe"
        },
        "climate_foundation": {
            "name": "Climate Foundation",
            "url": "https://www.climatefoundation.org",
            "type": "climate",
            "subtype": "research_foundation",
            "offers": ["grants", "research", "programs"],
            "frequency": "quarterly",
            "tier": 2,
            "specialty": "climate_solutions"
        },
        "climate_collective": {
            "name": "Climate Collective",
            "url": "https://www.climatecollective.net",
            "type": "climate",
            "subtype": "collaborative_platform",
            "offers": ["collaborations", "networking", "projects"],
            "frequency": "weekly",
            "tier": 2,
            "specialty": "climate_collaboration"
        },
        "climate_action": {
            "name": "Climate Action",
            "url": "https://www.climateaction.org/opportunities",
            "type": "climate",
            "subtype": "action_platform",
            "offers": ["opportunities", "jobs", "partnerships"],
            "frequency": "weekly",
            "tier": 2,
            "specialty": "climate_action"
        },

        # CLEAN ENERGY INITIATIVES & ORGANIZATIONS
        "clean_energy_ministerial": {
            "name": "Clean Energy Ministerial",
            "url": "https://www.cleanenergyministerial.org/initiatives",
            "type": "energy",
            "subtype": "ministerial_initiatives",
            "offers": ["initiatives", "partnerships", "policy"],
            "frequency": "quarterly",
            "tier": 1,
            "specialty": "clean_energy_policy",
            "region": "global"
        },
        "ren21": {
            "name": "REN21",
            "url": "https://www.ren21.net/opportunities",
            "type": "energy",
            "subtype": "renewable_network",
            "offers": ["opportunities", "research", "networking"],
            "frequency": "weekly",
            "tier": 1,
            "specialty": "renewable_energy"
        },
        "se_for_all": {
            "name": "Sustainable Energy for All",
            "url": "https://www.seforall.org/get-involved",
            "type": "energy",
            "subtype": "sustainable_energy",
            "offers": ["involvement_opportunities", "partnerships"],
            "frequency": "weekly",
            "tier": 1,
            "specialty": "sustainable_energy_access"
        },
        "seia": {
            "name": "Solar Energy Industries Association",
            "url": "https://www.seia.org/resources/jobs",
            "type": "energy",
            "subtype": "solar_industry",
            "offers": ["jobs", "resources", "industry_info"],
            "frequency": "daily",
            "tier": 2,
            "specialty": "solar_energy"
        },
        "irena": {
            "name": "IRENA",
            "url": "https://www.irena.org/employment",
            "type": "energy",
            "subtype": "renewable_agency",
            "offers": ["employment", "research", "policy"],
            "frequency": "weekly",
            "tier": 1,
            "specialty": "renewable_energy_international"
        },
        "iea": {
            "name": "International Energy Agency",
            "url": "https://www.iea.org/jobs",
            "type": "energy",
            "subtype": "energy_agency",
            "offers": ["jobs", "internships", "fellowships"],
            "frequency": "weekly",
            "tier": 1,
            "specialty": "energy_policy"
        },

        # CLEAN TECH & GREEN JOBS PLATFORMS
        "clean_technica": {
            "name": "CleanTechnica Jobs",
            "url": "https://cleantechnica.com/jobs",
            "type": "cleantech",
            "subtype": "job_board",
            "offers": ["cleantech_jobs", "industry_news"],
            "frequency": "daily",
            "tier": 2,
            "specialty": "clean_technology"
        },
        "solar_jobs": {
            "name": "Solar Jobs",
            "url": "https://www.solarjobs.com",
            "type": "energy",
            "subtype": "solar_job_board",
            "offers": ["solar_jobs", "career_resources"],
            "frequency": "daily",
            "tier": 2,
            "specialty": "solar_careers"
        },
        "recharge_news": {
            "name": "Recharge News Jobs",
            "url": "https://www.recharge-news.com/jobs",
            "type": "energy",
            "subtype": "renewable_news_jobs",
            "offers": ["renewable_jobs", "industry_news"],
            "frequency": "daily",
            "tier": 2,
            "specialty": "offshore_renewables"
        },
        "green_biz": {
            "name": "GreenBiz Careers",
            "url": "https://www.greenbiz.com/careers",
            "type": "sustainability",
            "subtype": "business_sustainability",
            "offers": ["sustainability_careers", "business_focus"],
            "frequency": "daily",
            "tier": 2,
            "specialty": "sustainable_business"
        },
        "grist": {
            "name": "Grist Fellowships",
            "url": "https://grist.org/fellowships",
            "type": "media",
            "subtype": "environmental_journalism",
            "offers": ["fellowships", "journalism", "storytelling"],
            "frequency": "yearly",
            "tier": 2,
            "specialty": "environmental_media"
        },
        "climate_base": {
            "name": "Climatebase",
            "url": "https://climatebase.org",
            "type": "climate",
            "subtype": "climate_job_platform",
            "offers": ["climate_jobs", "fellowships", "startups"],
            "frequency": "daily",
            "tier": 1,
            "specialty": "climate_careers",
            "volume": "high"
        },
        "sustainable_careers": {
            "name": "Sustainable Careers",
            "url": "https://www.sustainablecareers.org",
            "type": "sustainability",
            "subtype": "career_platform",
            "offers": ["sustainable_jobs", "career_guidance"],
            "frequency": "daily",
            "tier": 2,
            "specialty": "sustainability_careers"
        },
        "power_the_future": {
            "name": "Power the Future",
            "url": "https://www.powerthefuture.org",
            "type": "energy",
            "subtype": "energy_opportunities",
            "offers": ["opportunities", "advocacy", "jobs"],
            "frequency": "weekly",
            "tier": 2,
            "specialty": "energy_jobs"
        },

        # ENERGY RESEARCH & INFORMATION PLATFORMS
        "energypedia": {
            "name": "Energypedia",
            "url": "https://energypedia.info/jobs",
            "type": "energy",
            "subtype": "knowledge_platform",
            "offers": ["jobs", "knowledge_sharing", "projects"],
            "frequency": "weekly",
            "tier": 2,
            "specialty": "energy_development"
        },
        "energy_partnership": {
            "name": "Energy Partnership",
            "url": "https://www.energypartnership.de/en/opportunities",
            "type": "energy",
            "subtype": "international_partnership",
            "offers": ["opportunities", "partnerships", "cooperation"],
            "frequency": "weekly",
            "tier": 2,
            "specialty": "energy_cooperation",
            "region": "germany_international"
        },
        "global_wind_organisation": {
            "name": "Global Wind Organisation",
            "url": "https://globalwindorganisation.org/careers",
            "type": "energy",
            "subtype": "wind_industry",
            "offers": ["careers", "training", "safety"],
            "frequency": "weekly",
            "tier": 2,
            "specialty": "wind_energy"
        },
        "re100": {
            "name": "RE100 Members Jobs",
            "url": "https://www.re100.org/members-jobs",
            "type": "energy",
            "subtype": "corporate_renewable",
            "offers": ["member_jobs", "corporate_sustainability"],
            "frequency": "weekly",
            "tier": 1,
            "specialty": "corporate_renewables"
        },
        "carbon_brief": {
            "name": "Carbon Brief",
            "url": "https://www.carbonbrief.org/jobs",
            "type": "climate",
            "subtype": "climate_science_media",
            "offers": ["jobs", "climate_science", "communication"],
            "frequency": "weekly",
            "tier": 2,
            "specialty": "climate_communication"
        },

        # CARBON MARKETS & CLIMATE TECH COMPANIES
        "south_pole": {
            "name": "South Pole",
            "url": "https://www.southpole.com/careers",
            "type": "climate",
            "subtype": "climate_solutions_company",
            "offers": ["careers", "climate_solutions", "consulting"],
            "frequency": "weekly",
            "tier": 1,
            "specialty": "carbon_markets"
        },
        "verra": {
            "name": "Verra",
            "url": "https://verra.org",
            "type": "climate",
            "subtype": "carbon_standards",
            "offers": ["jobs", "standards_development", "verification"],
            "frequency": "weekly",
            "tier": 1,
            "specialty": "carbon_standards"
        },
        "gold_standard": {
            "name": "Gold Standard",
            "url": "https://www.goldstandard.org",
            "type": "climate",
            "subtype": "carbon_certification",
            "offers": ["jobs", "grants", "certification"],
            "frequency": "weekly",
            "tier": 1,
            "specialty": "carbon_certification"
        },
        "carbon_credits": {
            "name": "Carbon Credits",
            "url": "https://carboncredits.com",
            "type": "climate",
            "subtype": "carbon_market_platform",
            "offers": ["resources", "market_info", "opportunities"],
            "frequency": "weekly",
            "tier": 2,
            "specialty": "carbon_trading"
        },
        "sylvera": {
            "name": "Sylvera",
            "url": "https://www.sylvera.com/careers",
            "type": "climate",
            "subtype": "carbon_data_company",
            "offers": ["careers", "carbon_data", "analytics"],
            "frequency": "weekly",
            "tier": 2,
            "specialty": "carbon_data_analytics"
        },
        "patch_io": {
            "name": "Patch",
            "url": "https://www.patch.io/careers",
            "type": "climate",
            "subtype": "carbon_removal_platform",
            "offers": ["careers", "carbon_removal", "marketplace"],
            "frequency": "weekly",
            "tier": 2,
            "specialty": "carbon_removal"
        },
        "nori": {
            "name": "Nori",
            "url": "https://nori.com/careers",
            "type": "climate",
            "subtype": "carbon_removal_marketplace",
            "offers": ["careers", "carbon_marketplace", "agriculture"],
            "frequency": "weekly",
            "tier": 2,
            "specialty": "agricultural_carbon"
        },
        "regen_network": {
            "name": "Regen Network",
            "url": "https://regen.network",
            "type": "climate",
            "subtype": "regenerative_finance",
            "offers": ["community", "regenerative_economy", "blockchain"],
            "frequency": "weekly",
            "tier": 2,
            "specialty": "regenerative_finance"
        },
        "regen_foundation": {
            "name": "Regen Foundation",
            "url": "https://regenfoundation.org/grants",
            "type": "climate",
            "subtype": "regenerative_grants",
            "offers": ["grants", "regenerative_projects"],
            "frequency": "quarterly",
            "tier": 2,
            "specialty": "regenerative_agriculture"
        },

        # FOREST & CONSERVATION ORGANIZATIONS
        "open_forests": {
            "name": "Open Forests",
            "url": "https://openforests.com",
            "type": "conservation",
            "subtype": "forest_platform",
            "offers": ["forest_data", "conservation_tools"],
            "frequency": "weekly",
            "tier": 2,
            "specialty": "forest_conservation"
        },
        "rainforest_alliance": {
            "name": "Rainforest Alliance",
            "url": "https://www.rainforest-alliance.org/work-us",
            "type": "conservation",
            "subtype": "conservation_organization",
            "offers": ["jobs", "conservation_work", "certification"],
            "frequency": "weekly",
            "tier": 1,
            "specialty": "rainforest_conservation"
        },
        "forest_trends": {
            "name": "Forest Trends",
            "url": "https://www.forest-trends.org/opportunities",
            "type": "conservation",
            "subtype": "forest_economics",
            "offers": ["opportunities", "research", "policy"],
            "frequency": "weekly",
            "tier": 1,
            "specialty": "forest_economics"
        },
        "iccsglobal": {
            "name": "ICCS Global",
            "url": "https://www.iccsglobal.org",
            "type": "climate",
            "subtype": "carbon_capture",
            "offers": ["opportunities", "carbon_capture_storage"],
            "frequency": "weekly",
            "tier": 2,
            "specialty": "carbon_capture"
        },

        # UN & INTERNATIONAL DEVELOPMENT ORGANIZATIONS
        "fao": {
            "name": "FAO",
            "url": "https://www.fao.org/employment/opportunities",
            "type": "agriculture",
            "subtype": "un_agency",
            "offers": ["employment", "agriculture_development"],
            "frequency": "weekly",
            "tier": 1,
            "specialty": "food_agriculture",
            "region": "global"
        },
        "ifad": {
            "name": "IFAD",
            "url": "https://www.ifad.org/work",
            "type": "agriculture",
            "subtype": "agricultural_development",
            "offers": ["work_opportunities", "rural_development"],
            "frequency": "weekly",
            "tier": 1,
            "specialty": "rural_development"
        },
        "wfp_innovation": {
            "name": "WFP Innovation",
            "url": "https://www.wfp.org/innovation",
            "type": "agriculture",
            "subtype": "food_innovation",
            "offers": ["innovation", "climate_adaptation"],
            "frequency": "weekly",
            "tier": 1,
            "specialty": "food_security_climate"
        },
        "afdb": {
            "name": "African Development Bank",
            "url": "https://www.afdb.org/en/topics-and-sectors/sectors/agriculture",
            "type": "agriculture",
            "subtype": "development_bank",
            "offers": ["agriculture_sector", "development_programs"],
            "frequency": "weekly",
            "tier": 1,
            "specialty": "african_agriculture",
            "region": "africa"
        },

        # AGRICULTURAL RESEARCH & DEVELOPMENT
        "alliance_bioversity": {
            "name": "Alliance Bioversity CIAT",
            "url": "https://alliancebioversityciat.org/opportunities",
            "type": "agriculture",
            "subtype": "research_institute",
            "offers": ["opportunities", "research", "biodiversity"],
            "frequency": "weekly",
            "tier": 1,
            "specialty": "agricultural_biodiversity"
        },
        "cimmyt": {
            "name": "CIMMYT",
            "url": "https://www.cimmyt.org/work-with-us",
            "type": "agriculture",
            "subtype": "crop_research",
            "offers": ["work_opportunities", "wheat_maize_research"],
            "frequency": "weekly",
            "tier": 1,
            "specialty": "crop_improvement"
        },
        "icrisat": {
            "name": "ICRISAT",
            "url": "https://www.icrisat.org/careers",
            "type": "agriculture",
            "subtype": "dryland_research",
            "offers": ["careers", "dryland_agriculture"],
            "frequency": "weekly",
            "tier": 1,
            "specialty": "dryland_crops"
        },
        "iwmi": {
            "name": "IWMI",
            "url": "https://www.iwmi.cgiar.org/jobs",
            "type": "agriculture",
            "subtype": "water_management",
            "offers": ["jobs", "water_agriculture"],
            "frequency": "weekly",
            "tier": 1,
            "specialty": "agricultural_water"
        },
        "africa_rice": {
            "name": "AfricaRice",
            "url": "https://www.africarice.org/jobs",
            "type": "agriculture",
            "subtype": "rice_research",
            "offers": ["jobs", "rice_development"],
            "frequency": "weekly",
            "tier": 1,
            "specialty": "rice_systems",
            "region": "africa"
        },

        # CLIMATE FINANCE & INVESTMENT FUNDS
        "world_bank_climate": {
            "name": "World Bank Climate Investment Funds",
            "url": "https://www.worldbank.org",
            "type": "climate_finance",
            "subtype": "development_bank",
            "offers": ["climate_investments", "development_finance"],
            "frequency": "weekly",
            "tier": 1,
            "specialty": "climate_finance"
        },
        "gef": {
            "name": "Global Environment Facility",
            "url": "https://www.globalenvironmentfacility.org",
            "type": "climate_finance",
            "subtype": "environmental_funding",
            "offers": ["environmental_funding", "grants"],
            "frequency": "quarterly",
            "tier": 1,
            "specialty": "environmental_projects"
        },
        "green_climate_fund": {
            "name": "Green Climate Fund",
            "url": "https://www.greenclimate.fund/opportunities",
            "type": "climate_finance",
            "subtype": "climate_funding",
            "offers": ["opportunities", "climate_finance"],
            "frequency": "quarterly",
            "tier": 1,
            "specialty": "climate_adaptation_mitigation"
        },
        "forest_carbon_partnership": {
            "name": "Forest Carbon Partnership",
            "url": "https://forestcarbonpartnership.org/opportunities",
            "type": "climate_finance",
            "subtype": "forest_carbon",
            "offers": ["opportunities", "redd_plus", "forest_finance"],
            "frequency": "quarterly",
            "tier": 1,
            "specialty": "forest_carbon_finance"
        },

        # AGRICULTURAL INNOVATION & FOOD SYSTEMS
        "africa_agri_forum": {
            "name": "Africa Agri Forum",
            "url": "https://www.africaagri-forum.com",
            "type": "agriculture",
            "subtype": "agricultural_forum",
            "offers": ["opportunities", "networking", "investment"],
            "frequency": "yearly",
            "tier": 2,
            "specialty": "african_agribusiness",
            "region": "africa"
        },
        "ag_funder_news": {
            "name": "AgFunder News Jobs",
            "url": "https://agfundernews.com/jobs",
            "type": "agriculture",
            "subtype": "agtech_news",
            "offers": ["agtech_jobs", "startup_news"],
            "frequency": "daily",
            "tier": 2,
            "specialty": "agricultural_technology"
        },
        "thought_for_food": {
            "name": "Thought For Food",
            "url": "https://thoughtforfood.org",
            "type": "agriculture",
            "subtype": "food_innovation",
            "offers": ["challenges", "innovation", "youth_programs"],
            "frequency": "yearly",
            "tier": 2,
            "specialty": "food_system_innovation"
        },
        "food_systems_dashboard": {
            "name": "Food Systems Dashboard",
            "url": "https://foodsystemsdashboard.org/resources/opportunities",
            "type": "agriculture",
            "subtype": "food_systems",
            "offers": ["resources", "opportunities", "data"],
            "frequency": "weekly",
            "tier": 2,
            "specialty": "food_systems_transformation"
        },
        "world_food_prize": {
            "name": "World Food Prize",
            "url": "https://www.worldfoodprize.org",
            "type": "agriculture",
            "subtype": "food_prize",
            "offers": ["awards", "programs", "youth_programs"],
            "frequency": "yearly",
            "tier": 1,
            "specialty": "food_security"
        },
        "borlaug_fellow": {
            "name": "Borlaug Fellowship Program",
            "url": "https://borlaugfellow.org",
            "type": "agriculture",
            "subtype": "fellowship_program",
            "offers": ["fellowships", "research", "development"],
            "frequency": "yearly",
            "tier": 1,
            "specialty": "agricultural_research"
        },
        "grow_africa": {
            "name": "Grow Africa",
            "url": "https://growafrica.com/opportunities",
            "type": "agriculture",
            "subtype": "african_agriculture",
            "offers": ["opportunities", "partnerships", "investment"],
            "frequency": "weekly",
            "tier": 1,
            "specialty": "african_agricultural_transformation",
            "region": "africa"
        },
        "agrihack": {
            "name": "AgriHack",
            "url": "https://www.cta.int/agrihack",
            "type": "agriculture",
            "subtype": "agtech_competition",
            "offers": ["competitions", "innovation", "funding"],
            "frequency": "yearly",
            "tier": 2,
            "specialty": "agricultural_innovation"
        },
        "ispag": {
            "name": "ISPAG",
            "url": "https://www.ispag.org/JobPostings",
            "type": "agriculture",
            "subtype": "precision_agriculture",
            "offers": ["job_postings", "precision_ag"],
            "frequency": "weekly",
            "tier": 2,
            "specialty": "precision_agriculture"
        },
        "cgiar_climate": {
            "name": "CGIAR Climate Smart Agriculture",
            "url": "https://cgiar.org",
            "type": "agriculture",
            "subtype": "climate_smart_ag",
            "offers": ["climate_smart_initiatives", "research"],
            "frequency": "weekly",
            "tier": 1,
            "specialty": "climate_smart_agriculture"
        },

        # WATER & SANITATION ORGANIZATIONS
        "securing_water_for_food": {
            "name": "Securing Water for Food",
            "url": "https://securingwaterforfood.org",
            "type": "water",
            "subtype": "water_innovation",
            "offers": ["water_innovations", "agriculture_focus"],
            "frequency": "weekly",
            "tier": 2,
            "specialty": "water_agriculture_nexus"
        },
        "water_org": {
            "name": "Water.org",
            "url": "https://water.org/careers",
            "type": "water",
            "subtype": "water_access",
            "offers": ["careers", "water_access", "sanitation"],
            "frequency": "weekly",
            "tier": 1,
            "specialty": "water_sanitation_access"
        },
        "wash_funders": {
            "name": "WASH Funders",
            "url": "https://washfunders.org",
            "type": "water",
            "subtype": "wash_funding",
            "offers": ["funding_coordination", "wash_sector"],
            "frequency": "weekly",
            "tier": 2,
            "specialty": "wash_funding"
        },
        "global_water_partnership": {
            "name": "Global Water Partnership",
            "url": "https://www.globalwaterpartnership.org/opportunities",
            "type": "water",
            "subtype": "water_partnership",
            "offers": ["opportunities", "water_governance"],
            "frequency": "weekly",
            "tier": 1,
            "specialty": "water_governance"
        },

        # SUSTAINABLE ENERGY ACCESS & DEVELOPMENT
        "alliance_sustainable_energy": {
            "name": "Alliance for Sustainable Energy",
            "url": "https://allianceforsustainableenergy.org",
            "type": "energy",
            "subtype": "sustainable_energy_alliance",
            "offers": ["programs", "policy", "advocacy"],
            "frequency": "weekly",
            "tier": 2,
            "specialty": "sustainable_energy_policy"
        },
        "clean_cooking_alliance": {
            "name": "Clean Cooking Alliance",
            "url": "https://cleancookingalliance.org",
            "type": "energy",
            "subtype": "clean_cooking",
            "offers": ["opportunities", "clean_cooking_solutions"],
            "frequency": "weekly",
            "tier": 1,
            "specialty": "clean_cooking"
        },
        "power_for_all": {
            "name": "Power for All",
            "url": "https://powerforall.org/opportunities",
            "type": "energy",
            "subtype": "energy_access",
            "offers": ["opportunities", "energy_access", "advocacy"],
            "frequency": "weekly",
            "tier": 1,
            "specialty": "decentralized_energy"
        },
        "energise_africa": {
            "name": "Energise Africa",
            "url": "https://www.energiseafrica.com",
            "type": "energy",
            "subtype": "african_energy",
            "offers": ["partnerships", "investment", "energy_projects"],
            "frequency": "weekly",
            "tier": 2,
            "specialty": "african_renewable_energy",
            "region": "africa"
        },
        "africa_energy_forum": {
            "name": "Africa Energy Forum",
            "url": "https://www.africa-energy-forum.com",
            "type": "energy",
            "subtype": "energy_forum",
            "offers": ["networking", "deals", "investment"],
            "frequency": "yearly",
            "tier": 2,
            "specialty": "african_energy_markets",
            "region": "africa"
        }
    },

    # ═══════════════════════════════════════════════════════════════
    # INTERNATIONAL EVENTS / CONFERENCES / VOLUNTEER OPPORTUNITIES - 70+ Global Platforms
    # ═══════════════════════════════════════════════════════════════
    "international_events_opportunities": {
        # MAJOR GLOBAL CONFERENCES & EVENTS
        "mit_global_scale": {
            "name": "MIT Global Scale Events",
            "url": "https://mitglobalscale.org/events",
            "type": "conference",
            "subtype": "innovation_conference",
            "offers": ["events", "networking", "innovation_focus"],
            "frequency": "yearly",
            "tier": 1,
            "specialty": "global_innovation",
            "region": "global"
        },
        "one_young_world": {
            "name": "One Young World",
            "url": "https://one-young-world.com",
            "type": "conference",
            "subtype": "youth_leadership",
            "offers": ["summit", "youth_leadership", "global_networking"],
            "frequency": "yearly",
            "tier": 1,
            "specialty": "youth_leadership",
            "region": "global"
        },
        "world_economic_forum": {
            "name": "World Economic Forum Events",
            "url": "https://www.worldeconomicforum.org/events",
            "type": "conference",
            "subtype": "economic_forum",
            "offers": ["events", "global_leadership", "policy"],
            "frequency": "quarterly",
            "tier": 1,
            "specialty": "global_economic_policy",
            "region": "global"
        },

        # YOUTH PROGRAMS & EXCHANGES
        "world_youth_alliance": {
            "name": "World Youth Alliance",
            "url": "https://wya.net/programs",
            "type": "youth_program",
            "subtype": "youth_advocacy",
            "offers": ["programs", "advocacy", "training"],
            "frequency": "rolling",
            "tier": 2,
            "specialty": "youth_advocacy",
            "region": "global"
        },
        "aiesec": {
            "name": "AIESEC",
            "url": "https://aiesec.org",
            "type": "youth_program",
            "subtype": "youth_exchanges",
            "offers": ["exchanges", "internships", "leadership"],
            "frequency": "rolling",
            "tier": 1,
            "specialty": "youth_exchanges",
            "region": "global",
            "volume": "high"
        },
        "rotary_exchange": {
            "name": "Rotary Exchange Programs",
            "url": "https://rotary.org/en/our-programs/exchange-programs",
            "type": "exchange_program",
            "subtype": "cultural_exchange",
            "offers": ["exchange_programs", "cultural_immersion"],
            "frequency": "yearly",
            "tier": 1,
            "specialty": "cultural_exchange",
            "region": "global"
        },
        "erasmus_plus": {
            "name": "Erasmus+ Programme",
            "url": "https://erasmus-plus.ec.europa.eu/opportunities/individuals",
            "type": "exchange_program",
            "subtype": "european_exchange",
            "offers": ["study_abroad", "work_placement", "volunteering"],
            "frequency": "yearly",
            "tier": 1,
            "specialty": "european_mobility",
            "region": "europe"
        },
        "iaeste": {
            "name": "IAESTE",
            "url": "https://iaeste.org",
            "type": "internship_program",
            "subtype": "technical_internships",
            "offers": ["technical_internships", "international_experience"],
            "frequency": "yearly",
            "tier": 1,
            "specialty": "technical_exchanges",
            "region": "global"
        },
        "isfit": {
            "name": "ISFIT",
            "url": "https://isfit.org",
            "type": "conference",
            "subtype": "student_festival",
            "offers": ["student_festival", "international_networking"],
            "frequency": "biannual",
            "tier": 2,
            "specialty": "student_leadership",
            "region": "norway_international"
        },
        "iswi": {
            "name": "ISWI",
            "url": "https://iswi.org",
            "type": "conference",
            "subtype": "student_week",
            "offers": ["student_week", "technical_focus"],
            "frequency": "yearly",
            "tier": 2,
            "specialty": "technical_students",
            "region": "germany_international"
        },
        "ship_for_world_youth": {
            "name": "Ship for World Youth",
            "url": "https://shipforthworldyouth.org",
            "type": "youth_program",
            "subtype": "cultural_exchange",
            "offers": ["cultural_exchange", "leadership", "sailing"],
            "frequency": "yearly",
            "tier": 2,
            "specialty": "cultural_exchange_leadership",
            "region": "global"
        },
        "global_changemakers": {
            "name": "Global Changemakers",
            "url": "https://globalchangemakers.org",
            "type": "youth_program",
            "subtype": "social_change",
            "offers": ["social_change", "youth_programs"],
            "frequency": "rolling",
            "tier": 2,
            "specialty": "social_innovation",
            "region": "global"
        },
        "global_shapers": {
            "name": "Global Shapers Community",
            "url": "https://globalshapers.org",
            "type": "community",
            "subtype": "young_leaders",
            "offers": ["youth_hubs", "leadership", "networking"],
            "frequency": "rolling",
            "tier": 1,
            "specialty": "young_professional_leadership",
            "region": "global"
        },

        # TECH & BUSINESS CONFERENCES
        "tedx_events": {
            "name": "TEDx Events",
            "url": "https://ted.com/tedx/events",
            "type": "conference",
            "subtype": "ideas_conference",
            "offers": ["speaking_opportunities", "networking", "ideas"],
            "frequency": "rolling",
            "tier": 1,
            "specialty": "thought_leadership",
            "region": "global",
            "volume": "high"
        },
        "quartz_events": {
            "name": "Quartz Events",
            "url": "https://qz.com/events",
            "type": "conference",
            "subtype": "business_tech",
            "offers": ["business_tech_events", "networking"],
            "frequency": "quarterly",
            "tier": 2,
            "specialty": "business_technology",
            "region": "global"
        },
        "aws_events": {
            "name": "AWS Events",
            "url": "https://aws.amazon.com/events",
            "type": "conference",
            "subtype": "cloud_technology",
            "offers": ["cloud_events", "training", "certification"],
            "frequency": "monthly",
            "tier": 1,
            "specialty": "cloud_computing",
            "region": "global"
        },
        "google_cloud_events": {
            "name": "Google Cloud Community Events",
            "url": "https://googlecloudcommunity.com/events",
            "type": "conference",
            "subtype": "cloud_community",
            "offers": ["cloud_events", "community", "networking"],
            "frequency": "monthly",
            "tier": 1,
            "specialty": "google_cloud",
            "region": "global"
        },
        "ml_summit": {
            "name": "ML Summit",
            "url": "https://mlsummit.ai",
            "type": "conference",
            "subtype": "machine_learning",
            "offers": ["ml_conferences", "ai_networking"],
            "frequency": "yearly",
            "tier": 1,
            "specialty": "machine_learning_ai",
            "region": "global"
        },
        "ai_expo": {
            "name": "AI Expo",
            "url": "https://ai-expo.net",
            "type": "conference",
            "subtype": "ai_exhibition",
            "offers": ["ai_expo", "business_ai", "networking"],
            "frequency": "yearly",
            "tier": 1,
            "specialty": "artificial_intelligence_business",
            "region": "global"
        },

        # ENERGY & SUSTAINABILITY CONFERENCES
        "world_future_energy": {
            "name": "World Future Energy Summit",
            "url": "https://worldfutureenergy.com",
            "type": "conference",
            "subtype": "energy_summit",
            "offers": ["energy_summit", "renewable_energy", "networking"],
            "frequency": "yearly",
            "tier": 1,
            "specialty": "future_energy",
            "region": "middle_east_global"
        },
        "cop_unfccc": {
            "name": "UNFCCC COP",
            "url": "https://cop28.com",
            "type": "conference",
            "subtype": "climate_summit",
            "offers": ["climate_summit", "policy", "networking"],
            "frequency": "yearly",
            "tier": 1,
            "specialty": "climate_policy",
            "region": "global"
        },

        # AGRICULTURAL & FOOD TECH CONFERENCES
        "agritechnica": {
            "name": "Agritechnica",
            "url": "https://agritechnica.com",
            "type": "conference",
            "subtype": "agricultural_engineering",
            "offers": ["ag_engineering_expo", "technology"],
            "frequency": "biannual",
            "tier": 1,
            "specialty": "agricultural_technology",
            "region": "europe_global"
        },
        "world_agritech_innovation": {
            "name": "World Agritech Innovation Summit",
            "url": "https://worldagritechinnovation.com",
            "type": "conference",
            "subtype": "agtech_innovation",
            "offers": ["agtech_innovation", "startups", "investment"],
            "frequency": "yearly",
            "tier": 1,
            "specialty": "agricultural_innovation",
            "region": "global"
        },
        "africa_agribusiness_conference": {
            "name": "Africa Agribusiness Conference",
            "url": "https://africaagribusinessconference.com",
            "type": "conference",
            "subtype": "african_agribusiness",
            "offers": ["african_agribusiness", "investment", "networking"],
            "frequency": "yearly",
            "tier": 1,
            "specialty": "african_agriculture",
            "region": "africa"
        },

        # RENEWABLE ENERGY & TECH EXHIBITIONS
        "solar_power_events": {
            "name": "Solar Power Events",
            "url": "https://solarpowerevents.com",
            "type": "conference",
            "subtype": "solar_energy",
            "offers": ["solar_events", "renewable_energy", "business"],
            "frequency": "yearly",
            "tier": 1,
            "specialty": "solar_energy",
            "region": "global"
        },
        "intersolar": {
            "name": "Intersolar",
            "url": "https://intersolar.net",
            "type": "conference",
            "subtype": "solar_exhibition",
            "offers": ["solar_exhibition", "energy_storage", "networking"],
            "frequency": "yearly",
            "tier": 1,
            "specialty": "solar_technology",
            "region": "global"
        },
        "power_electronics_events": {
            "name": "Power Electronics Events",
            "url": "https://powerelectronicsnews.com/events",
            "type": "conference",
            "subtype": "power_electronics",
            "offers": ["power_electronics", "technical_events"],
            "frequency": "quarterly",
            "tier": 2,
            "specialty": "power_electronics",
            "region": "global"
        },
        "electronica": {
            "name": "Electronica",
            "url": "https://electronica.de",
            "type": "conference",
            "subtype": "electronics_exhibition",
            "offers": ["electronics_expo", "innovation", "networking"],
            "frequency": "biannual",
            "tier": 1,
            "specialty": "electronics_industry",
            "region": "europe_global"
        },
        "embedded_world": {
            "name": "Embedded World",
            "url": "https://embedded-world.de",
            "type": "conference",
            "subtype": "embedded_systems",
            "offers": ["embedded_systems", "iot", "technology"],
            "frequency": "yearly",
            "tier": 1,
            "specialty": "embedded_technology",
            "region": "europe_global"
        },

        # MAKER & OPEN SOURCE EVENTS
        "maker_faire": {
            "name": "Maker Faire",
            "url": "https://makerfaire.com",
            "type": "conference",
            "subtype": "maker_movement",
            "offers": ["maker_events", "diy", "innovation"],
            "frequency": "yearly",
            "tier": 1,
            "specialty": "maker_movement",
            "region": "global"
        },
        "fab_foundation_events": {
            "name": "Fab Foundation Events",
            "url": "https://fabfoundation.org/events",
            "type": "conference",
            "subtype": "digital_fabrication",
            "offers": ["fab_events", "digital_fabrication"],
            "frequency": "yearly",
            "tier": 2,
            "specialty": "digital_fabrication",
            "region": "global"
        },
        "hackaday_contests": {
            "name": "Hackaday Contests",
            "url": "https://hackaday.io/contests",
            "type": "competition",
            "subtype": "hardware_challenges",
            "offers": ["hardware_challenges", "contests", "events"],
            "frequency": "quarterly",
            "tier": 2,
            "specialty": "hardware_hacking",
            "region": "global"
        },
        "oshwa_events": {
            "name": "OSHWA Events",
            "url": "https://oshwa.org/events",
            "type": "conference",
            "subtype": "open_source_hardware",
            "offers": ["open_hardware_events", "community"],
            "frequency": "yearly",
            "tier": 2,
            "specialty": "open_source_hardware",
            "region": "global"
        },
        "open_hardware_community": {
            "name": "Open Hardware Communities",
            "url": "https://openhardware.io",
            "type": "community",
            "subtype": "hardware_communities",
            "offers": ["communities", "collaboration", "projects"],
            "frequency": "rolling",
            "tier": 2,
            "specialty": "hardware_collaboration",
            "region": "global"
        },

        # TRAVEL & NETWORKING SUPPORT
        "world_travel_awards": {
            "name": "World Travel Awards",
            "url": "https://worldtravelawards.com",
            "type": "conference",
            "subtype": "travel_industry",
            "offers": ["industry_networking", "travel_industry"],
            "frequency": "yearly",
            "tier": 2,
            "specialty": "travel_industry_networking",
            "region": "global"
        },
        "skyscanner": {
            "name": "Skyscanner",
            "url": "https://skyscanner.net",
            "type": "travel_support",
            "subtype": "flight_booking",
            "offers": ["cheap_flights", "conference_travel"],
            "frequency": "daily",
            "tier": 1,
            "specialty": "travel_logistics",
            "region": "global"
        },
        "hostelworld": {
            "name": "Hostelworld",
            "url": "https://hostelworld.com",
            "type": "travel_support",
            "subtype": "budget_accommodation",
            "offers": ["budget_travel", "conference_accommodation"],
            "frequency": "daily",
            "tier": 1,
            "specialty": "budget_travel",
            "region": "global"
        },

        # VOLUNTEER & WORK EXCHANGE PROGRAMS
        "workaway": {
            "name": "Workaway",
            "url": "https://workaway.info",
            "type": "volunteer_program",
            "subtype": "work_exchange",
            "offers": ["volunteer_work", "cultural_exchange"],
            "frequency": "rolling",
            "tier": 1,
            "specialty": "work_exchange",
            "region": "global",
            "volume": "high"
        },
        "wwoof": {
            "name": "WWOOF",
            "url": "https://wwoof.net",
            "type": "volunteer_program",
            "subtype": "farm_volunteering",
            "offers": ["farm_volunteering", "organic_farming", "cultural_exchange"],
            "frequency": "rolling",
            "tier": 1,
            "specialty": "sustainable_agriculture_volunteer",
            "region": "global"
        },
        "helpx": {
            "name": "HelpX",
            "url": "https://helpx.net",
            "type": "volunteer_program",
            "subtype": "skill_exchange",
            "offers": ["work_exchange", "skill_sharing"],
            "frequency": "rolling",
            "tier": 2,
            "specialty": "skills_exchange",
            "region": "global"
        },
        "worldpackers": {
            "name": "Worldpackers",
            "url": "https://worldpackers.com",
            "type": "volunteer_program",
            "subtype": "travel_work",
            "offers": ["travel_work", "volunteering", "accommodation"],
            "frequency": "rolling",
            "tier": 1,
            "specialty": "nomadic_volunteering",
            "region": "global"
        },
        "volunteer_hq": {
            "name": "Volunteer HQ (IVHQ)",
            "url": "https://volunteerhq.org",
            "type": "volunteer_program",
            "subtype": "international_volunteering",
            "offers": ["international_volunteering", "development_work"],
            "frequency": "rolling",
            "tier": 1,
            "specialty": "international_development_volunteer",
            "region": "global"
        },
        "unv": {
            "name": "UN Volunteers",
            "url": "https://unv.org/opportunities",
            "type": "volunteer_program",
            "subtype": "un_volunteering",
            "offers": ["un_opportunities", "international_development"],
            "frequency": "rolling",
            "tier": 1,
            "specialty": "un_development_volunteer",
            "region": "global"
        },
        "peace_corps": {
            "name": "Peace Corps",
            "url": "https://peacecorps.gov/volunteer",
            "type": "volunteer_program",
            "subtype": "government_volunteering",
            "offers": ["peace_corps", "international_service"],
            "frequency": "rolling",
            "tier": 1,
            "specialty": "international_service",
            "region": "us_international"
        },
        "vso_international": {
            "name": "VSO International",
            "url": "https://vsointernational.org/volunteering",
            "type": "volunteer_program",
            "subtype": "development_volunteering",
            "offers": ["development_volunteering", "skill_sharing"],
            "frequency": "rolling",
            "tier": 1,
            "specialty": "international_development_skills",
            "region": "global"
        },
        "red_cross_volunteer": {
            "name": "Red Cross Volunteer",
            "url": "https://redcross.int/volunteer",
            "type": "volunteer_program",
            "subtype": "humanitarian_volunteering",
            "offers": ["humanitarian_work", "disaster_response"],
            "frequency": "rolling",
            "tier": 1,
            "specialty": "humanitarian_response",
            "region": "global"
        },
        "doctors_without_borders": {
            "name": "Doctors Without Borders",
            "url": "https://doctorswithoutborders.org/work-field",
            "type": "volunteer_program",
            "subtype": "medical_volunteering",
            "offers": ["medical_missions", "humanitarian_healthcare"],
            "frequency": "rolling",
            "tier": 1,
            "specialty": "medical_humanitarian",
            "region": "global"
        },
        "engineers_without_borders": {
            "name": "Engineers Without Borders",
            "url": "https://engineerswithoutborders.org/opportunities",
            "type": "volunteer_program",
            "subtype": "engineering_volunteering",
            "offers": ["engineering_projects", "development_work"],
            "frequency": "rolling",
            "tier": 1,
            "specialty": "engineering_development",
            "region": "global"
        },
        "ewb_uk": {
            "name": "Engineers Without Borders UK",
            "url": "https://ewb-uk.org/get-involved",
            "type": "volunteer_program",
            "subtype": "uk_engineering_volunteer",
            "offers": ["engineering_volunteering", "uk_chapter"],
            "frequency": "rolling",
            "tier": 2,
            "specialty": "engineering_volunteer_uk",
            "region": "uk_international"
        },
        "ewb_usa": {
            "name": "Engineers Without Borders USA",
            "url": "https://ewb-usa.org/get-involved",
            "type": "volunteer_program",
            "subtype": "us_engineering_volunteer",
            "offers": ["engineering_projects", "us_chapter"],
            "frequency": "rolling",
            "tier": 2,
            "specialty": "engineering_volunteer_usa",
            "region": "us_international"
        },
        "givingway": {
            "name": "GivingWay",
            "url": "https://givingway.com",
            "type": "volunteer_program",
            "subtype": "volunteer_matching",
            "offers": ["volunteer_matching", "opportunity_discovery"],
            "frequency": "rolling",
            "tier": 2,
            "specialty": "volunteer_matching_platform",
            "region": "global"
        },
        "idealist_volunteering": {
            "name": "Idealist Volunteering",
            "url": "https://idealist.org",
            "type": "volunteer_program",
            "subtype": "volunteer_job_platform",
            "offers": ["volunteering", "nonprofit_jobs"],
            "frequency": "rolling",
            "tier": 1,
            "specialty": "nonprofit_volunteering",
            "region": "global"
        },

        # STUDY ABROAD & CULTURAL EXCHANGE
        "go_abroad": {
            "name": "Go Abroad",
            "url": "https://goabroad.com",
            "type": "study_abroad",
            "subtype": "international_programs",
            "offers": ["study_abroad", "travel", "volunteer_programs"],
            "frequency": "rolling",
            "tier": 1,
            "specialty": "international_education",
            "region": "global"
        },
        "go_overseas": {
            "name": "Go Overseas",
            "url": "https://gooverseas.com",
            "type": "study_abroad",
            "subtype": "overseas_programs",
            "offers": ["overseas_programs", "cultural_immersion"],
            "frequency": "rolling",
            "tier": 1,
            "specialty": "cultural_immersion",
            "region": "global"
        },
        "fulbright": {
            "name": "Fulbright Exchange Programs",
            "url": "https://fulbright.gov",
            "type": "exchange_program",
            "subtype": "academic_exchange",
            "offers": ["academic_exchange", "research", "teaching"],
            "frequency": "yearly",
            "tier": 1,
            "specialty": "academic_cultural_exchange",
            "region": "us_international"
        },
        "daad": {
            "name": "DAAD Germany",
            "url": "https://daad.de/en/study-and-research-in-germany/plan-your-studies/scholarships-database/",
            "type": "scholarship_program",
            "subtype": "german_scholarships",
            "offers": ["german_study", "research", "scholarships"],
            "frequency": "yearly",
            "tier": 1,
            "specialty": "german_academic_exchange",
            "region": "germany_international"
        },
        "mit_misti": {
            "name": "MIT MISTI",
            "url": "https://mitmisti.mit.edu",
            "type": "exchange_program",
            "subtype": "mit_international",
            "offers": ["international_programs", "research", "internships"],
            "frequency": "yearly",
            "tier": 1,
            "specialty": "mit_international_programs",
            "region": "mit_global"
        },

        # UN & INTERNATIONAL ORGANIZATION EVENTS
        "unitar_events": {
            "name": "UNITAR Events",
            "url": "https://unitar.org/events",
            "type": "conference",
            "subtype": "un_training",
            "offers": ["un_training", "capacity_building", "events"],
            "frequency": "monthly",
            "tier": 1,
            "specialty": "un_capacity_building",
            "region": "global"
        },
        "unesco_events": {
            "name": "UNESCO Events",
            "url": "https://unesco.org/events",
            "type": "conference",
            "subtype": "unesco_programs",
            "offers": ["unesco_events", "education", "culture"],
            "frequency": "monthly",
            "tier": 1,
            "specialty": "education_culture_international",
            "region": "global"
        },
        "un_habitat_events": {
            "name": "UN-Habitat Events",
            "url": "https://unhabitat.org/events",
            "type": "conference",
            "subtype": "urban_development",
            "offers": ["urban_events", "sustainable_cities"],
            "frequency": "quarterly",
            "tier": 1,
            "specialty": "urban_development",
            "region": "global"
        },
        "world_urban_forum": {
            "name": "World Urban Forum",
            "url": "https://worldurbanforum.org",
            "type": "conference",
            "subtype": "urban_planning",
            "offers": ["urban_forum", "city_planning", "sustainability"],
            "frequency": "biannual",
            "tier": 1,
            "specialty": "urban_sustainability",
            "region": "global"
        },
        "world_water_forum": {
            "name": "World Water Forum",
            "url": "https://worldwaterforum.org",
            "type": "conference",
            "subtype": "water_conference",
            "offers": ["water_forum", "water_security", "innovation"],
            "frequency": "triennial",
            "tier": 1,
            "specialty": "water_sustainability",
            "region": "global"
        },
        "world_bank_events": {
            "name": "World Bank Events",
            "url": "https://worldbank.org/en/events",
            "type": "conference",
            "subtype": "development_finance",
            "offers": ["development_events", "finance", "policy"],
            "frequency": "monthly",
            "tier": 1,
            "specialty": "development_finance",
            "region": "global"
        },
        "imf_events": {
            "name": "IMF Events",
            "url": "https://imf.org/en/News/Seminars",
            "type": "conference",
            "subtype": "monetary_finance",
            "offers": ["economic_seminars", "monetary_policy"],
            "frequency": "monthly",
            "tier": 1,
            "specialty": "international_finance",
            "region": "global"
        },

        # AFRICAN CONFERENCES & SUMMITS
        "africa_climate_summit": {
            "name": "Africa Climate Summit",
            "url": "https://africaclimatesummit.org",
            "type": "conference",
            "subtype": "african_climate",
            "offers": ["climate_summit", "african_focus", "policy"],
            "frequency": "yearly",
            "tier": 1,
            "specialty": "african_climate_action",
            "region": "africa"
        },
        "african_union_summits": {
            "name": "African Union Summits",
            "url": "https://africaunion.org/summits",
            "type": "conference",
            "subtype": "pan_african",
            "offers": ["au_summits", "african_integration"],
            "frequency": "biannual",
            "tier": 1,
            "specialty": "african_integration",
            "region": "africa"
        },
        "innovation_week_kenya": {
            "name": "Innovation Week Kenya",
            "url": "https://innovationweek.co.ke",
            "type": "conference",
            "subtype": "kenyan_innovation",
            "offers": ["innovation_week", "kenyan_tech"],
            "frequency": "yearly",
            "tier": 2,
            "specialty": "east_african_innovation",
            "region": "east_africa"
        },
        "nairobi_tech_week": {
            "name": "Nairobi Tech Week",
            "url": "https://nairobitechweek.com",
            "type": "conference",
            "subtype": "nairobi_tech",
            "offers": ["tech_week", "startup_ecosystem"],
            "frequency": "yearly",
            "tier": 2,
            "specialty": "kenyan_tech_ecosystem",
            "region": "kenya"
        },
        "lagos_startup_week": {
            "name": "Lagos Startup Week",
            "url": "https://lagosstartupweek.com",
            "type": "conference",
            "subtype": "nigerian_startups",
            "offers": ["startup_week", "nigerian_ecosystem"],
            "frequency": "yearly",
            "tier": 2,
            "specialty": "nigerian_startup_ecosystem",
            "region": "nigeria"
        },
        "cairo_ict": {
            "name": "Cairo ICT",
            "url": "https://cairoict.com",
            "type": "conference",
            "subtype": "middle_east_ict",
            "offers": ["ict_expo", "middle_east_tech"],
            "frequency": "yearly",
            "tier": 2,
            "specialty": "middle_east_ict",
            "region": "middle_east_north_africa"
        }
    },

    # ═══════════════════════════════════════════════════════════════
    # CREATOR ECONOMY / FUNDING PLATFORMS / STARTUP ECOSYSTEMS - 90+ Comprehensive Platforms
    # ═══════════════════════════════════════════════════════════════
    "creator_economy_funding": {
        # OPPORTUNITY HUBS & AGGREGATION PORTALS
        "opportunity_desk": {
            "name": "OpportunityDesk",
            "url": "https://opportunitydesk.org",
            "type": "opportunity_hub",
            "subtype": "global_hub",
            "offers": ["scholarships", "jobs", "contests", "grants"],
            "frequency": "daily",
            "tier": 1,
            "specialty": "global_opportunity_aggregation",
            "region": "global",
            "volume": "high"
        },
        "youth_opportunities": {
            "name": "Youth Opportunities",
            "url": "https://youthop.com",
            "type": "opportunity_hub",
            "subtype": "youth_focused",
            "offers": ["youth_programs", "global_opportunities"],
            "frequency": "daily",
            "tier": 1,
            "specialty": "global_youth_opportunities",
            "region": "global"
        },
        "opportunities_corners": {
            "name": "Opportunities Corners",
            "url": "https://opportunitiescorners.info",
            "type": "opportunity_hub",
            "subtype": "information_hub",
            "offers": ["opportunity_listings", "information"],
            "frequency": "daily",
            "tier": 2,
            "specialty": "opportunity_information",
            "region": "global"
        },
        "study_portals": {
            "name": "StudyPortals",
            "url": "https://studyportals.com",
            "type": "education_hub",
            "subtype": "study_scholarships",
            "offers": ["study_abroad", "scholarships", "programs"],
            "frequency": "daily",
            "tier": 1,
            "specialty": "international_education",
            "region": "global"
        },
        "global_portal": {
            "name": "Global Portal Opportunities",
            "url": "https://globalportal.com/opportunities",
            "type": "opportunity_hub",
            "subtype": "generic_portal",
            "offers": ["generic_opportunities", "global_listings"],
            "frequency": "daily",
            "tier": 2,
            "specialty": "general_opportunities",
            "region": "global"
        },
        "scholarship_positions": {
            "name": "Scholarship Positions",
            "url": "https://scholarship-positions.com",
            "type": "scholarship_hub",
            "subtype": "scholarship_aggregator",
            "offers": ["scholarship_listings", "academic_positions"],
            "frequency": "daily",
            "tier": 1,
            "specialty": "scholarship_aggregation",
            "region": "global"
        },
        "fully_funded_scholarships": {
            "name": "Fully Funded Scholarships",
            "url": "https://fullyfundedscholarships.com",
            "type": "scholarship_hub",
            "subtype": "funded_scholarships",
            "offers": ["fully_funded_programs", "scholarships"],
            "frequency": "daily",
            "tier": 1,
            "specialty": "funded_education",
            "region": "global"
        },
        "scholars4dev": {
            "name": "Scholars4Dev",
            "url": "https://scholars4dev.com",
            "type": "scholarship_hub",
            "subtype": "development_scholarships",
            "offers": ["development_scholarships", "research"],
            "frequency": "daily",
            "tier": 1,
            "specialty": "development_focused_education",
            "region": "global"
        },
        "world_scholarship_forum": {
            "name": "World Scholarship Forum",
            "url": "https://worldscholarshipforum.com",
            "type": "scholarship_hub",
            "subtype": "scholarship_community",
            "offers": ["scholarship_forum", "community"],
            "frequency": "daily",
            "tier": 1,
            "specialty": "scholarship_community",
            "region": "global"
        },
        "hotcourses_abroad": {
            "name": "Hotcourses Abroad",
            "url": "https://hotcoursesabroad.com",
            "type": "education_hub",
            "subtype": "international_courses",
            "offers": ["international_courses", "study_abroad"],
            "frequency": "daily",
            "tier": 1,
            "specialty": "international_course_discovery",
            "region": "global"
        },
        "profellow": {
            "name": "ProFellow",
            "url": "https://profellow.com",
            "type": "fellowship_hub",
            "subtype": "fellowship_aggregator",
            "offers": ["fellowships", "grants", "awards"],
            "frequency": "daily",
            "tier": 1,
            "specialty": "fellowship_aggregation",
            "region": "global"
        },
        "opportunity_for_africans": {
            "name": "Opportunity for Africans",
            "url": "https://opportunityforafricans.com",
            "type": "opportunity_hub",
            "subtype": "african_focused",
            "offers": ["african_opportunities", "scholarships", "jobs"],
            "frequency": "daily",
            "tier": 1,
            "specialty": "african_opportunity_aggregation",
            "region": "africa"
        },
        "o4af": {
            "name": "O4AF",
            "url": "https://o4af.com",
            "type": "opportunity_hub",
            "subtype": "african_opportunities",
            "offers": ["african_focus", "opportunities"],
            "frequency": "daily",
            "tier": 2,
            "specialty": "african_opportunities",
            "region": "africa"
        },
        "mladi_info": {
            "name": "Mladi Info",
            "url": "https://mladiinfo.eu",
            "type": "opportunity_hub",
            "subtype": "european_youth",
            "offers": ["youth_opportunities", "european_focus"],
            "frequency": "daily",
            "tier": 2,
            "specialty": "european_youth_opportunities",
            "region": "europe"
        },
        "iie_programs": {
            "name": "IIE Programs",
            "url": "https://iie.org/en/Programs",
            "type": "education_hub",
            "subtype": "international_education",
            "offers": ["international_education", "exchanges"],
            "frequency": "weekly",
            "tier": 1,
            "specialty": "institutional_international_education",
            "region": "us_international"
        },

        # CROWDFUNDING & PROJECT FUNDING PLATFORMS
        "gofundme": {
            "name": "GoFundMe",
            "url": "https://gofundme.com",
            "type": "crowdfunding",
            "subtype": "personal_project_funding",
            "offers": ["personal_funding", "project_initiatives"],
            "frequency": "daily",
            "tier": 1,
            "specialty": "personal_project_crowdfunding",
            "region": "global",
            "volume": "high"
        },
        "experiment": {
            "name": "Experiment",
            "url": "https://experiment.com",
            "type": "crowdfunding",
            "subtype": "research_funding",
            "offers": ["research_crowdfunding", "scientific_projects"],
            "frequency": "daily",
            "tier": 2,
            "specialty": "scientific_research_funding",
            "region": "global"
        },
        "kickstarter": {
            "name": "Kickstarter",
            "url": "https://kickstarter.com",
            "type": "crowdfunding",
            "subtype": "creative_hardware",
            "offers": ["creative_projects", "hardware_funding"],
            "frequency": "daily",
            "tier": 1,
            "specialty": "creative_hardware_crowdfunding",
            "region": "global",
            "volume": "high"
        },
        "indiegogo": {
            "name": "Indiegogo",
            "url": "https://indiegogo.com",
            "type": "crowdfunding",
            "subtype": "flexible_funding",
            "offers": ["flexible_funding", "innovation_projects"],
            "frequency": "daily",
            "tier": 1,
            "specialty": "flexible_crowdfunding",
            "region": "global"
        },

        # CREATOR MONETIZATION PLATFORMS
        "patreon": {
            "name": "Patreon",
            "url": "https://patreon.com",
            "type": "creator_platform",
            "subtype": "subscription_support",
            "offers": ["creator_income", "subscription_model"],
            "frequency": "daily",
            "tier": 1,
            "specialty": "creator_subscription_monetization",
            "region": "global"
        },
        "buy_me_coffee": {
            "name": "Buy Me a Coffee",
            "url": "https://buymeacoffee.com",
            "type": "creator_platform",
            "subtype": "tip_support",
            "offers": ["creator_income", "tip_support"],
            "frequency": "daily",
            "tier": 1,
            "specialty": "creator_tip_monetization",
            "region": "global"
        },
        "ko_fi": {
            "name": "Ko-fi",
            "url": "https://ko-fi.com",
            "type": "creator_platform",
            "subtype": "creator_support",
            "offers": ["creator_income", "fan_support"],
            "frequency": "daily",
            "tier": 1,
            "specialty": "creator_fan_support",
            "region": "global"
        },

        # MERCHANDISE & DESIGN MARKETPLACES
        "teespring": {
            "name": "Teespring",
            "url": "https://teespring.com",
            "type": "marketplace",
            "subtype": "merchandise",
            "offers": ["merchandise_sales", "print_on_demand"],
            "frequency": "daily",
            "tier": 2,
            "specialty": "custom_merchandise",
            "region": "global"
        },
        "redbubble": {
            "name": "Redbubble",
            "url": "https://redbubble.com",
            "type": "marketplace",
            "subtype": "design_merchandise",
            "offers": ["design_sales", "merchandise"],
            "frequency": "daily",
            "tier": 1,
            "specialty": "design_merchandise_marketplace",
            "region": "global"
        },
        "society6": {
            "name": "Society6",
            "url": "https://society6.com",
            "type": "marketplace",
            "subtype": "artist_marketplace",
            "offers": ["artist_sales", "home_decor"],
            "frequency": "daily",
            "tier": 2,
            "specialty": "artist_home_decor_marketplace",
            "region": "global"
        },
        "envato": {
            "name": "Envato",
            "url": "https://envato.com",
            "type": "marketplace",
            "subtype": "digital_assets",
            "offers": ["themes", "stock_assets", "marketplace"],
            "frequency": "daily",
            "tier": 1,
            "specialty": "digital_asset_marketplace",
            "region": "global"
        },
        "themeforest": {
            "name": "ThemeForest",
            "url": "https://themeforest.net",
            "type": "marketplace",
            "subtype": "theme_marketplace",
            "offers": ["theme_sales", "web_templates"],
            "frequency": "daily",
            "tier": 1,
            "specialty": "web_theme_marketplace",
            "region": "global"
        },
        "codecanyon": {
            "name": "CodeCanyon",
            "url": "https://codecanyon.net",
            "type": "marketplace",
            "subtype": "code_marketplace",
            "offers": ["code_sales", "scripts", "plugins"],
            "frequency": "daily",
            "tier": 1,
            "specialty": "code_script_marketplace",
            "region": "global"
        },
        "creative_fabrica": {
            "name": "Creative Fabrica",
            "url": "https://creativefabrica.com",
            "type": "marketplace",
            "subtype": "creative_marketplace",
            "offers": ["creative_assets", "design_resources"],
            "frequency": "daily",
            "tier": 2,
            "specialty": "creative_asset_marketplace",
            "region": "global"
        },

        # STOCK MEDIA & CONTENT PLATFORMS
        "shutterstock": {
            "name": "Shutterstock Contributors",
            "url": "https://shutterstock.com/contributors",
            "type": "stock_platform",
            "subtype": "stock_photography",
            "offers": ["stock_photography", "contributor_income"],
            "frequency": "daily",
            "tier": 1,
            "specialty": "stock_photography_marketplace",
            "region": "global"
        },
        "getty_images": {
            "name": "Getty Images Contributors",
            "url": "https://gettyimages.com/contributors",
            "type": "stock_platform",
            "subtype": "premium_stock",
            "offers": ["premium_stock", "editorial_content"],
            "frequency": "daily",
            "tier": 1,
            "specialty": "premium_stock_photography",
            "region": "global"
        },
        "adobe_stock": {
            "name": "Adobe Stock Contributors",
            "url": "https://stock.adobe.com/contributor",
            "type": "stock_platform",
            "subtype": "integrated_stock",
            "offers": ["adobe_integrated_stock", "creative_content"],
            "frequency": "daily",
            "tier": 1,
            "specialty": "adobe_ecosystem_stock",
            "region": "global"
        },
        "pond5": {
            "name": "Pond5",
            "url": "https://pond5.com",
            "type": "stock_platform",
            "subtype": "video_audio",
            "offers": ["video_contributors", "audio_contributors"],
            "frequency": "daily",
            "tier": 2,
            "specialty": "video_audio_stock",
            "region": "global"
        },
        "storyblocks": {
            "name": "Storyblocks Contributors",
            "url": "https://storyblocks.com/contributors",
            "type": "stock_platform",
            "subtype": "subscription_stock",
            "offers": ["subscription_model", "unlimited_downloads"],
            "frequency": "daily",
            "tier": 2,
            "specialty": "subscription_stock_model",
            "region": "global"
        },
        "istock": {
            "name": "iStock Contributors",
            "url": "https://istockphoto.com/contributor",
            "type": "stock_platform",
            "subtype": "accessible_stock",
            "offers": ["accessible_stock", "diverse_content"],
            "frequency": "daily",
            "tier": 2,
            "specialty": "accessible_stock_photography",
            "region": "global"
        },

        # DESIGN & CREATIVE JOB PLATFORMS
        "dribbble": {
            "name": "Dribbble",
            "url": "https://dribbble.com",
            "type": "creative_platform",
            "subtype": "design_jobs",
            "offers": ["design_jobs", "portfolio", "networking"],
            "frequency": "daily",
            "tier": 1,
            "specialty": "design_portfolio_jobs",
            "region": "global"
        },
        "behance": {
            "name": "Behance Jobs",
            "url": "https://behance.net/joblist",
            "type": "creative_platform",
            "subtype": "creative_jobs",
            "offers": ["creative_jobs", "portfolio_showcase"],
            "frequency": "daily",
            "tier": 1,
            "specialty": "adobe_creative_jobs",
            "region": "global"
        },
        "adobe_99u": {
            "name": "Adobe 99U",
            "url": "https://99u.adobe.com",
            "type": "creative_platform",
            "subtype": "creative_events",
            "offers": ["events", "creative_opportunities"],
            "frequency": "weekly",
            "tier": 2,
            "specialty": "creative_professional_development",
            "region": "global"
        },
        "artstation": {
            "name": "ArtStation Jobs",
            "url": "https://artstation.com/jobs",
            "type": "creative_platform",
            "subtype": "digital_art_jobs",
            "offers": ["digital_art_jobs", "game_industry"],
            "frequency": "daily",
            "tier": 1,
            "specialty": "digital_art_game_industry",
            "region": "global"
        },
        "deviantart": {
            "name": "DeviantArt",
            "url": "https://deviantart.com",
            "type": "creative_platform",
            "subtype": "art_commissions",
            "offers": ["art_jobs", "commissions", "community"],
            "frequency": "daily",
            "tier": 2,
            "specialty": "art_community_commissions",
            "region": "global"
        },

        # GAMING & INTERACTIVE MEDIA PLATFORMS
        "itch_io": {
            "name": "Itch.io",
            "url": "https://itch.io",
            "type": "game_platform",
            "subtype": "indie_games",
            "offers": ["indie_games", "marketplace", "revenue_share"],
            "frequency": "daily",
            "tier": 1,
            "specialty": "indie_game_marketplace",
            "region": "global"
        },
        "steam_direct": {
            "name": "Steam Direct",
            "url": "https://steamcommunity.com",
            "type": "game_platform",
            "subtype": "game_publishing",
            "offers": ["game_publishing", "steam_distribution"],
            "frequency": "daily",
            "tier": 1,
            "specialty": "pc_game_distribution",
            "region": "global"
        },
        "epic_games_store": {
            "name": "Epic Games Store Publishing",
            "url": "https://epicgames.com/store/publish",
            "type": "game_platform",
            "subtype": "epic_publishing",
            "offers": ["game_dev", "epic_store", "revenue_share"],
            "frequency": "weekly",
            "tier": 1,
            "specialty": "epic_game_publishing",
            "region": "global"
        },
        "unity_asset_store": {
            "name": "Unity Asset Store",
            "url": "https://unity.com/solutions/asset-store",
            "type": "game_platform",
            "subtype": "game_assets",
            "offers": ["sell_assets", "unity_ecosystem"],
            "frequency": "daily",
            "tier": 1,
            "specialty": "unity_asset_marketplace",
            "region": "global"
        },
        "unreal_marketplace": {
            "name": "Unreal Engine Marketplace",
            "url": "https://unrealengine.com/marketplace",
            "type": "game_platform",
            "subtype": "unreal_assets",
            "offers": ["unreal_assets", "game_development"],
            "frequency": "daily",
            "tier": 1,
            "specialty": "unreal_asset_marketplace",
            "region": "global"
        },
        "blender_artists": {
            "name": "Blender Artists Jobs",
            "url": "https://blenderartists.org/jobs",
            "type": "creative_platform",
            "subtype": "3d_art_jobs",
            "offers": ["3d_art_jobs", "blender_community"],
            "frequency": "weekly",
            "tier": 2,
            "specialty": "3d_art_blender_jobs",
            "region": "global"
        },

        # DIGITAL PRODUCT & ECOMMERCE PLATFORMS
        "gumroad": {
            "name": "Gumroad",
            "url": "https://gumroad.com",
            "type": "ecommerce_platform",
            "subtype": "digital_products",
            "offers": ["sell_digital_products", "creator_economy"],
            "frequency": "daily",
            "tier": 1,
            "specialty": "digital_product_sales",
            "region": "global"
        },
        "lemon_squeezy": {
            "name": "Lemon Squeezy",
            "url": "https://lemon-squeezy.com",
            "type": "ecommerce_platform",
            "subtype": "saas_licenses",
            "offers": ["sell_saas", "licenses", "digital_products"],
            "frequency": "daily",
            "tier": 2,
            "specialty": "saas_digital_licensing",
            "region": "global"
        },
        "shopify": {
            "name": "Shopify",
            "url": "https://shopify.com",
            "type": "ecommerce_platform",
            "subtype": "ecommerce_store",
            "offers": ["ecommerce", "online_stores", "dropshipping"],
            "frequency": "daily",
            "tier": 1,
            "specialty": "comprehensive_ecommerce",
            "region": "global",
            "volume": "high"
        },
        "woocommerce": {
            "name": "WooCommerce",
            "url": "https://woocommerce.com",
            "type": "ecommerce_platform",
            "subtype": "wordpress_ecommerce",
            "offers": ["wordpress_commerce", "open_source"],
            "frequency": "daily",
            "tier": 1,
            "specialty": "wordpress_ecommerce_integration",
            "region": "global"
        },
        "big_cartel": {
            "name": "Big Cartel",
            "url": "https://bigcartel.com",
            "type": "ecommerce_platform",
            "subtype": "small_creators",
            "offers": ["small_creator_stores", "artist_focused"],
            "frequency": "daily",
            "tier": 2,
            "specialty": "small_creator_ecommerce",
            "region": "global"
        },
        "etsy": {
            "name": "Etsy",
            "url": "https://etsy.com",
            "type": "marketplace",
            "subtype": "handmade_goods",
            "offers": ["handmade", "vintage", "craft_supplies"],
            "frequency": "daily",
            "tier": 1,
            "specialty": "handmade_vintage_marketplace",
            "region": "global",
            "volume": "high"
        },
        "printful": {
            "name": "Printful",
            "url": "https://printful.com",
            "type": "print_platform",
            "subtype": "print_on_demand",
            "offers": ["print_on_demand", "dropshipping"],
            "frequency": "daily",
            "tier": 1,
            "specialty": "print_on_demand_fulfillment",
            "region": "global"
        },
        "printify": {
            "name": "Printify",
            "url": "https://printify.com",
            "type": "print_platform",
            "subtype": "custom_printing",
            "offers": ["custom_printing", "print_network"],
            "frequency": "daily",
            "tier": 1,
            "specialty": "print_network_platform",
            "region": "global"
        },
        "spreadshirt": {
            "name": "Spreadshirt",
            "url": "https://spreadshirt.com",
            "type": "print_platform",
            "subtype": "apparel_printing",
            "offers": ["apparel_printing", "design_marketplace"],
            "frequency": "daily",
            "tier": 2,
            "specialty": "apparel_design_printing",
            "region": "global"
        },
        "cafepress": {
            "name": "CafePress",
            "url": "https://cafepress.com",
            "type": "print_platform",
            "subtype": "custom_products",
            "offers": ["custom_products", "design_sales"],
            "frequency": "daily",
            "tier": 2,
            "specialty": "custom_product_printing",
            "region": "global"
        },

        # RESALE & SECONDARY MARKETPLACES
        "depop": {
            "name": "Depop",
            "url": "https://depop.com",
            "type": "resale_platform",
            "subtype": "fashion_resale",
            "offers": ["fashion_resale", "vintage_clothing"],
            "frequency": "daily",
            "tier": 2,
            "specialty": "fashion_resale_social",
            "region": "global"
        },
        "poshmark": {
            "name": "Poshmark",
            "url": "https://poshmark.com",
            "type": "resale_platform",
            "subtype": "fashion_marketplace",
            "offers": ["fashion_marketplace", "social_selling"],
            "frequency": "daily",
            "tier": 2,
            "specialty": "social_fashion_marketplace",
            "region": "us_canada"
        },
        "vinted": {
            "name": "Vinted",
            "url": "https://vinted.com",
            "type": "resale_platform",
            "subtype": "clothing_exchange",
            "offers": ["clothing_exchange", "second_hand"],
            "frequency": "daily",
            "tier": 2,
            "specialty": "clothing_exchange_platform",
            "region": "europe_us"
        },

        # DIGITAL ASSET & BUSINESS MARKETPLACES
        "flippa": {
            "name": "Flippa",
            "url": "https://flippa.com",
            "type": "asset_marketplace",
            "subtype": "digital_assets",
            "offers": ["digital_assets", "domains", "websites"],
            "frequency": "daily",
            "tier": 1,
            "specialty": "digital_asset_trading",
            "region": "global"
        },
        "microacquire": {
            "name": "MicroAcquire",
            "url": "https://microacquire.com",
            "type": "acquisition_platform",
            "subtype": "startup_acquisition",
            "offers": ["acquire_startups", "small_business_sales"],
            "frequency": "daily",
            "tier": 2,
            "specialty": "micro_startup_acquisition",
            "region": "global"
        },
        "empire_flippers": {
            "name": "Empire Flippers",
            "url": "https://empireflippers.com",
            "type": "asset_marketplace",
            "subtype": "online_business",
            "offers": ["online_business_sales", "due_diligence"],
            "frequency": "weekly",
            "tier": 2,
            "specialty": "established_online_business",
            "region": "global"
        },

        # STARTUP & PRODUCT LAUNCH PLATFORMS
        "indie_hackers_products": {
            "name": "Indie Hackers Products",
            "url": "https://indiehackers.com/products",
            "type": "product_platform",
            "subtype": "indie_products",
            "offers": ["indie_products", "founder_community"],
            "frequency": "daily",
            "tier": 1,
            "specialty": "indie_maker_products",
            "region": "global"
        },
        "product_hunt": {
            "name": "Product Hunt",
            "url": "https://producthunt.com",
            "type": "product_platform",
            "subtype": "product_launch",
            "offers": ["product_launches", "startup_discovery"],
            "frequency": "daily",
            "tier": 1,
            "specialty": "product_discovery_launch",
            "region": "global",
            "volume": "high"
        },
        "betalist": {
            "name": "BetaList",
            "url": "https://betalist.com",
            "type": "product_platform",
            "subtype": "beta_launches",
            "offers": ["beta_launches", "early_adopters"],
            "frequency": "daily",
            "tier": 2,
            "specialty": "beta_product_launches",
            "region": "global"
        },
        "beta_labs": {
            "name": "Beta Labs",
            "url": "https://betalabs.io",
            "type": "product_platform",
            "subtype": "beta_communities",
            "offers": ["beta_communities", "product_testing"],
            "frequency": "weekly",
            "tier": 3,
            "specialty": "beta_testing_communities",
            "region": "global"
        },
        "hackernews_hiring": {
            "name": "Hacker News Who's Hiring",
            "url": "https://news.ycombinator.com",
            "type": "job_platform",
            "subtype": "tech_hiring",
            "offers": ["tech_hiring", "startup_jobs", "monthly_threads"],
            "frequency": "monthly",
            "tier": 1,
            "specialty": "tech_startup_hiring",
            "region": "global"
        },
        "side_projectors": {
            "name": "Side Projectors",
            "url": "https://sideprojectors.com",
            "type": "project_platform",
            "subtype": "side_projects",
            "offers": ["side_project_marketplace", "collaboration"],
            "frequency": "weekly",
            "tier": 3,
            "specialty": "side_project_collaboration",
            "region": "global"
        },

        # NO-CODE & BUILDER COMMUNITIES
        "makerpad": {
            "name": "Makerpad",
            "url": "https://makerpad.co",
            "type": "community_platform",
            "subtype": "no_code_builders",
            "offers": ["no_code_opportunities", "builder_community"],
            "frequency": "daily",
            "tier": 2,
            "specialty": "no_code_builder_opportunities",
            "region": "global"
        },
        "nocode_founders": {
            "name": "No Code Founders",
            "url": "https://nocodefounders.com",
            "type": "community_platform",
            "subtype": "nocode_entrepreneurs",
            "offers": ["nocode_entrepreneurship", "founder_community"],
            "frequency": "weekly",
            "tier": 2,
            "specialty": "nocode_founder_community",
            "region": "global"
        },
        "nocode_tech": {
            "name": "NoCode.tech",
            "url": "https://nocode.tech/resources",
            "type": "resource_platform",
            "subtype": "nocode_resources",
            "offers": ["nocode_resources", "tools", "opportunities"],
            "frequency": "weekly",
            "tier": 2,
            "specialty": "nocode_tool_resources",
            "region": "global"
        },
        "saastock": {
            "name": "SaaStock",
            "url": "https://saastock.com/events",
            "type": "conference",
            "subtype": "saas_networking",
            "offers": ["saas_events", "networking", "funding"],
            "frequency": "yearly",
            "tier": 1,
            "specialty": "saas_networking_events",
            "region": "europe_global"
        },

        # FOUNDER & BUILDER FELLOWSHIPS
        "on_deck": {
            "name": "On Deck",
            "url": "https://ondeck.com",
            "type": "fellowship_platform",
            "subtype": "founder_fellowships",
            "offers": ["founder_fellowships", "builder_programs"],
            "frequency": "quarterly",
            "tier": 1,
            "specialty": "founder_builder_fellowships",
            "region": "global"
        },
        "pioneer": {
            "name": "Pioneer",
            "url": "https://pioneer.app",
            "type": "fellowship_platform",
            "subtype": "founder_tournament",
            "offers": ["founder_tournament", "funding"],
            "frequency": "rolling",
            "tier": 2,
            "specialty": "competitive_founder_program",
            "region": "global"
        },
        "buildspace": {
            "name": "Buildspace",
            "url": "https://buildspace.so",
            "type": "community_platform",
            "subtype": "build_cohorts",
            "offers": ["build_cohorts", "funding", "exposure"],
            "frequency": "quarterly",
            "tier": 1,
            "specialty": "builder_cohort_community",
            "region": "global"
        },

        # ALTERNATIVE FUNDING PLATFORMS
        "tinyseed": {
            "name": "TinySeed",
            "url": "https://tinyseed.com",
            "type": "funding_platform",
            "subtype": "saas_accelerator",
            "offers": ["saas_funding", "accelerator", "bootstrap_alternative"],
            "frequency": "yearly",
            "tier": 2,
            "specialty": "saas_founder_accelerator",
            "region": "global"
        },
        "calm_fund": {
            "name": "Calm Fund",
            "url": "https://calmfund.com",
            "type": "funding_platform",
            "subtype": "profitable_founder",
            "offers": ["profitable_founder_funding", "sustainable_growth"],
            "frequency": "rolling",
            "tier": 3,
            "specialty": "sustainable_founder_funding",
            "region": "global"
        },
        "pipe": {
            "name": "Pipe",
            "url": "https://pipe.com",
            "type": "funding_platform",
            "subtype": "revenue_based",
            "offers": ["revenue_based_funding", "saas_funding"],
            "frequency": "rolling",
            "tier": 2,
            "specialty": "recurring_revenue_funding",
            "region": "global"
        },
        "capchase": {
            "name": "Capchase",
            "url": "https://capchase.com",
            "type": "funding_platform",
            "subtype": "saas_financing",
            "offers": ["saas_financing", "revenue_acceleration"],
            "frequency": "rolling",
            "tier": 2,
            "specialty": "saas_growth_financing",
            "region": "global"
        },
        "clearco": {
            "name": "Clearco",
            "url": "https://clear.co",
            "type": "funding_platform",
            "subtype": "ecommerce_funding",
            "offers": ["ecommerce_funding", "data_driven_investment"],
            "frequency": "rolling",
            "tier": 2,
            "specialty": "ecommerce_growth_funding",
            "region": "global"
        },

        # EQUITY CROWDFUNDING & INVESTMENT PLATFORMS
        "republic": {
            "name": "Republic",
            "url": "https://republic.com",
            "type": "investment_platform",
            "subtype": "equity_crowdfunding",
            "offers": ["equity_crowdfunding", "startup_investment"],
            "frequency": "daily",
            "tier": 1,
            "specialty": "retail_equity_investment",
            "region": "global"
        },
        "seedrs": {
            "name": "Seedrs",
            "url": "https://seedrs.com",
            "type": "investment_platform",
            "subtype": "uk_equity_crowdfunding",
            "offers": ["uk_crowdfunding", "european_startups"],
            "frequency": "daily",
            "tier": 2,
            "specialty": "european_equity_crowdfunding",
            "region": "uk_europe"
        },
        "crowdcube": {
            "name": "Crowdcube",
            "url": "https://crowdcube.com",
            "type": "investment_platform",
            "subtype": "uk_investment",
            "offers": ["uk_startup_investment", "equity_crowdfunding"],
            "frequency": "daily",
            "tier": 2,
            "specialty": "uk_startup_equity_investment",
            "region": "uk"
        },
        "startengine": {
            "name": "StartEngine",
            "url": "https://startengine.com",
            "type": "investment_platform",
            "subtype": "us_equity_crowdfunding",
            "offers": ["us_equity_crowdfunding", "regulation_cf"],
            "frequency": "daily",
            "tier": 2,
            "specialty": "us_regulation_cf_investment",
            "region": "us"
        },
        "wefunder": {
            "name": "Wefunder",
            "url": "https://wefunder.com",
            "type": "investment_platform",
            "subtype": "startup_funding",
            "offers": ["startup_funding", "community_investment"],
            "frequency": "daily",
            "tier": 2,
            "specialty": "community_startup_funding",
            "region": "us"
        },
        "netcapital": {
            "name": "NetCapital",
            "url": "https://netcapital.com",
            "type": "investment_platform",
            "subtype": "private_market",
            "offers": ["private_market_access", "startup_investment"],
            "frequency": "weekly",
            "tier": 3,
            "specialty": "private_market_startup_access",
            "region": "us"
        },

        # STARTUP INTELLIGENCE & NETWORKING
        "angellist": {
            "name": "AngelList (Wellfound)",
            "url": "https://wellfound.com",
            "type": "startup_platform",
            "subtype": "startup_ecosystem",
            "offers": ["startup_jobs", "funding", "talent"],
            "frequency": "daily",
            "tier": 1,
            "specialty": "comprehensive_startup_ecosystem",
            "region": "global",
            "volume": "high"
        },
        "gust": {
            "name": "Gust",
            "url": "https://gust.com",
            "type": "funding_platform",
            "subtype": "investor_platform",
            "offers": ["startup_investor_platform", "deal_flow"],
            "frequency": "daily",
            "tier": 2,
            "specialty": "startup_investor_matching",
            "region": "global"
        },
        "crunchbase": {
            "name": "Crunchbase",
            "url": "https://crunchbase.com",
            "type": "intelligence_platform",
            "subtype": "startup_intelligence",
            "offers": ["startup_intelligence", "investor_discovery"],
            "frequency": "daily",
            "tier": 1,
            "specialty": "startup_market_intelligence",
            "region": "global"
        },
        "pitchbook": {
            "name": "PitchBook",
            "url": "https://pitchbook.com",
            "type": "intelligence_platform",
            "subtype": "deal_intelligence",
            "offers": ["deal_intelligence", "market_data"],
            "frequency": "daily",
            "tier": 1,
            "specialty": "private_market_intelligence",
            "region": "global"
        },
        "f6s": {
            "name": "F6S",
            "url": "https://f6s.com",
            "type": "startup_platform",
            "subtype": "startup_accelerator_jobs",
            "offers": ["startups", "accelerators", "jobs"],
            "frequency": "daily",
            "tier": 2,
            "specialty": "startup_accelerator_ecosystem",
            "region": "global"
        },
        "dealroom": {
            "name": "Dealroom",
            "url": "https://dealroom.co",
            "type": "intelligence_platform",
            "subtype": "european_startups",
            "offers": ["european_startup_data", "market_intelligence"],
            "frequency": "weekly",
            "tier": 2,
            "specialty": "european_startup_intelligence",
            "region": "europe"
        },
        "cb_insights": {
            "name": "CB Insights",
            "url": "https://cbinsights.com",
            "type": "intelligence_platform",
            "subtype": "market_intelligence",
            "offers": ["market_intelligence", "trend_analysis"],
            "frequency": "daily",
            "tier": 1,
            "specialty": "comprehensive_market_intelligence",
            "region": "global"
        },

        # AI TOOLS & EMERGING TECH COMMUNITIES
        "futurepedia": {
            "name": "Futurepedia",
            "url": "https://futurepedia.io",
            "type": "ai_platform",
            "subtype": "ai_tools",
            "offers": ["ai_tools", "product_launches"],
            "frequency": "daily",
            "tier": 2,
            "specialty": "ai_tool_discovery",
            "region": "global"
        },
        "theresanaiforthat": {
            "name": "There's An AI For That",
            "url": "https://theresanaiforthat.com",
            "type": "ai_platform",
            "subtype": "ai_marketplace",
            "offers": ["ai_tools", "ai_markets"],
            "frequency": "daily",
            "tier": 2,
            "specialty": "ai_tool_marketplace",
            "region": "global"
        },

        # REMOTE & GLOBAL COMMUNITIES
        "remote_clan": {
            "name": "Remote Clan",
            "url": "https://remoteclan.com",
            "type": "community_platform",
            "subtype": "remote_workers",
            "offers": ["remote_worker_community", "opportunities"],
            "frequency": "daily",
            "tier": 2,
            "specialty": "remote_work_community",
            "region": "global"
        },
        "indie_worldwide": {
            "name": "Indie Worldwide",
            "url": "https://indieworldwide.com",
            "type": "community_platform",
            "subtype": "indie_founders",
            "offers": ["founder_community", "indie_jobs"],
            "frequency": "daily",
            "tier": 2,
            "specialty": "indie_founder_global_community",
            "region": "global"
        }
    },
}

# Summary statistics
def get_source_stats():
    """Calculate statistics about opportunity sources"""
    total_sources = 0
    by_category = {}
    by_frequency = {"hourly": 0, "daily": 0, "weekly": 0, "yearly": 0, "rolling": 0, "biannual": 0, "quarterly": 0}
    
    for category, sources in OPPORTUNITY_SOURCES.items():
        category_count = len(sources)
        total_sources += category_count
        by_category[category] = category_count
        
        for source in sources.values():
            freq = source.get("frequency", "daily")
            if freq in by_frequency:
                by_frequency[freq] += 1
    
    return {
        "total_sources": total_sources,
        "by_category": by_category,
        "by_frequency": by_frequency
    }

if __name__ == "__main__":
    stats = get_source_stats()
    print(f"Total Opportunity Sources: {stats['total_sources']}")
    print("\nBy Category:")
    for cat, count in stats['by_category'].items():
        print(f"  {cat}: {count}")
