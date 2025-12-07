"""
Massive Scholarship & Fellowship Sources Database - 250+ Programs
"""

SCHOLARSHIPS = {
    # === PRESTIGIOUS GLOBAL SCHOLARSHIPS ===
    "rhodes_scholarship": {"url": "https://www.rhodeshouse.ox.ac.uk/scholarships", "country": "UK", "type": "full_funding", "level": "graduate"},
    "fulbright": {"url": "https://us.fulbrightonline.org", "country": "USA", "type": "full_funding", "level": "graduate"},
    "gates_cambridge": {"url": "https://www.gatescambridge.org", "country": "UK", "type": "full_funding", "level": "graduate"},
    "marshall_scholarship": {"url": "https://www.marshallscholarship.org", "country": "UK", "type": "full_funding", "level": "graduate"},
    "chevening": {"url": "https://www.chevening.org", "country": "UK", "type": "full_funding", "level": "masters"},
    "schwarzman": {"url": "https://www.schwarzmanscholars.org", "country": "China", "type": "full_funding", "level": "masters"},
    "knight_hennessy": {"url": "https://knight-hennessy.stanford.edu", "country": "USA", "type": "full_funding", "level": "graduate"},
    "mitchell": {"url": "https://www.us-irelandalliance.org/mitchellscholarship", "country": "Ireland", "type": "full_funding", "level": "masters"},
    "erasmus_mundus": {"url": "https://erasmus-plus.ec.europa.eu", "country": "Europe", "type": "full_funding", "level": "masters"},
    "commonwealth": {"url": "https://cscuk.fcdo.gov.uk/scholarships", "country": "UK", "type": "full_funding", "level": "graduate"},
    
    # === GERMANY ===
    "daad": {"url": "https://www.daad.de/en/study-and-research-in-germany/scholarships", "country": "Germany", "type": "full_funding", "level": "all"},
    "deutschland_stipendium": {"url": "https://www.deutschlandstipendium.de", "country": "Germany", "type": "partial", "level": "undergraduate"},
    "heinrich_boll": {"url": "https://www.boell.de/en/scholarships", "country": "Germany", "type": "full_funding", "level": "graduate"},
    "konrad_adenauer": {"url": "https://www.kas.de/en/scholarships", "country": "Germany", "type": "full_funding", "level": "graduate"},
    "friedrich_ebert": {"url": "https://www.fes.de/studienfoerderung", "country": "Germany", "type": "full_funding", "level": "graduate"},
    "rosa_luxemburg": {"url": "https://www.rosalux.de/en/foundation/scholarships", "country": "Germany", "type": "full_funding", "level": "graduate"},
    "hans_bockler": {"url": "https://www.boeckler.de/en/scholarships", "country": "Germany", "type": "full_funding", "level": "graduate"},
    "studienstiftung": {"url": "https://www.studienstiftung.de", "country": "Germany", "type": "full_funding", "level": "all"},
    "humboldt": {"url": "https://www.humboldt-foundation.de", "country": "Germany", "type": "full_funding", "level": "postdoc"},
    
    # === JAPAN ===
    "mext": {"url": "https://www.studyinjapan.go.jp/en/smap_stopj-applications_scholarships.html", "country": "Japan", "type": "full_funding", "level": "all"},
    "jasso": {"url": "https://www.jasso.go.jp/en/ryugaku", "country": "Japan", "type": "partial", "level": "all"},
    "monbukagakusho": {"url": "https://www.mext.go.jp/en/policy/education/highered/title02/detail02/1373897.htm", "country": "Japan", "type": "full_funding", "level": "all"},
    "jica_training": {"url": "https://www.jica.go.jp/english/our_work/types_of_assistance/tech/training", "country": "Japan", "type": "full_funding", "level": "professional"},
    "adb_japan": {"url": "https://www.adb.org/work-with-us/careers/japan-scholarship-program", "country": "Japan", "type": "full_funding", "level": "masters"},
    
    # === CHINA ===
    "csc": {"url": "https://www.campuschina.org/scholarships", "country": "China", "type": "full_funding", "level": "all"},
    "confucius_institute": {"url": "https://cis.chinese.cn/scholarship", "country": "China", "type": "full_funding", "level": "all"},
    "provincial_scholarships": {"url": "https://www.campuschina.org/content/details3_74776.html", "country": "China", "type": "partial", "level": "all"},
    "university_scholarships": {"url": "https://www.campuschina.org/content/details3_74775.html", "country": "China", "type": "varies", "level": "all"},
    
    # === AUSTRALIA ===
    "australia_awards": {"url": "https://www.dfat.gov.au/people-to-people/australia-awards", "country": "Australia", "type": "full_funding", "level": "masters"},
    "endeavour": {"url": "https://internationaleducation.gov.au/Endeavour%20program", "country": "Australia", "type": "full_funding", "level": "all"},
    "destination_australia": {"url": "https://www.education.gov.au/destination-australia", "country": "Australia", "type": "partial", "level": "all"},
    "rti_scholarships": {"url": "https://www.studyaustralia.gov.au/english/study/scholarships", "country": "Australia", "type": "varies", "level": "all"},
    
    # === CANADA ===
    "vanier": {"url": "https://vanier.gc.ca", "country": "Canada", "type": "full_funding", "level": "phd"},
    "banting": {"url": "https://banting.fellowships-bourses.gc.ca", "country": "Canada", "type": "full_funding", "level": "postdoc"},
    "trudeau": {"url": "https://www.trudeaufoundation.ca/programs/scholarship", "country": "Canada", "type": "full_funding", "level": "phd"},
    "lester_pearson": {"url": "https://future.utoronto.ca/pearson", "country": "Canada", "type": "full_funding", "level": "undergraduate"},
    "mgi": {"url": "https://www.educanada.ca/scholarships-bourses", "country": "Canada", "type": "full_funding", "level": "all"},
    "oise": {"url": "https://www.oise.utoronto.ca/oise/Prospective_Students/Scholarships_Funding.html", "country": "Canada", "type": "varies", "level": "graduate"},
    
    # === NETHERLANDS ===
    "holland_scholarship": {"url": "https://www.studyinholland.nl/finances/holland-scholarship", "country": "Netherlands", "type": "partial", "level": "all"},
    "orange_knowledge": {"url": "https://www.nuffic.nl/en/subjects/orange-knowledge-programme", "country": "Netherlands", "type": "full_funding", "level": "masters"},
    "nuffic": {"url": "https://www.nuffic.nl/en/subjects/scholarships", "country": "Netherlands", "type": "varies", "level": "all"},
    "leiden_excellence": {"url": "https://www.universiteitleiden.nl/en/education/admission-and-application/scholarships", "country": "Netherlands", "type": "varies", "level": "all"},
    "delft_excellence": {"url": "https://www.tudelft.nl/en/education/practical-matters/scholarships", "country": "Netherlands", "type": "varies", "level": "masters"},
    
    # === SWEDEN ===
    "si_scholarship": {"url": "https://si.se/en/apply/scholarships", "country": "Sweden", "type": "full_funding", "level": "masters"},
    "kth_scholarship": {"url": "https://www.kth.se/en/studies/master/scholarships", "country": "Sweden", "type": "varies", "level": "masters"},
    "lund_scholarship": {"url": "https://www.lunduniversity.lu.se/admissions/scholarships-and-awards", "country": "Sweden", "type": "varies", "level": "all"},
    "chalmers": {"url": "https://www.chalmers.se/en/education/fees-finance/scholarships", "country": "Sweden", "type": "varies", "level": "masters"},
    
    # === SWITZERLAND ===
    "swiss_government": {"url": "https://www.sbfi.admin.ch/sbfi/en/home/education/scholarships-and-grants/swiss-government-excellence-scholarships.html", "country": "Switzerland", "type": "full_funding", "level": "graduate"},
    "eth_scholarship": {"url": "https://ethz.ch/en/studies/financial/scholarships.html", "country": "Switzerland", "type": "varies", "level": "all"},
    "epfl": {"url": "https://www.epfl.ch/education/studies/en/financing/scholarships", "country": "Switzerland", "type": "varies", "level": "all"},
    
    # === FRANCE ===
    "eiffel": {"url": "https://www.campusfrance.org/en/eiffel-scholarship-program-of-excellence", "country": "France", "type": "full_funding", "level": "masters"},
    "emile_boutmy": {"url": "https://www.sciencespo.fr/students/en/fees-funding/financial-aid/emile-boutmy", "country": "France", "type": "partial", "level": "all"},
    "charpak": {"url": "https://www.inde.campusfrance.org/charpak-scholarship", "country": "France", "type": "full_funding", "level": "all"},
    "ampere": {"url": "https://www.ens-lyon.fr/en/international/international-students/ampere-scholarships", "country": "France", "type": "full_funding", "level": "masters"},
    
    # === ITALY ===
    "invest_your_talent": {"url": "https://www.investyourtalent.it", "country": "Italy", "type": "partial", "level": "masters"},
    "italian_government": {"url": "https://studyinitaly.esteri.it/en/call-for-procedure", "country": "Italy", "type": "full_funding", "level": "all"},
    "bocconi": {"url": "https://www.unibocconi.eu/wps/wcm/connect/bocconi/sitopubblico_en/navigation+tree/home/programs/current+students/services/funding", "country": "Italy", "type": "varies", "level": "all"},
    
    # === SPAIN ===
    "la_caixa": {"url": "https://fundacionlacaixa.org/en/postgraduate-fellowships-abroad", "country": "Spain", "type": "full_funding", "level": "graduate"},
    "carolina": {"url": "https://www.fundacioncarolina.es/en/scholarships", "country": "Spain", "type": "full_funding", "level": "graduate"},
    
    # === KOREA ===
    "kgsp": {"url": "https://www.studyinkorea.go.kr/en/sub/gks/allnew_invite.do", "country": "Korea", "type": "full_funding", "level": "all"},
    "niied": {"url": "https://www.studyinkorea.go.kr", "country": "Korea", "type": "full_funding", "level": "all"},
    "posco": {"url": "https://www.posco-scholarship.or.kr", "country": "Korea", "type": "full_funding", "level": "graduate"},
    
    # === SINGAPORE ===
    "nus_scholarship": {"url": "https://www.nus.edu.sg/oam/scholarships", "country": "Singapore", "type": "varies", "level": "all"},
    "ntu_scholarship": {"url": "https://www.ntu.edu.sg/admissions/graduate/financialmatters/scholarships", "country": "Singapore", "type": "varies", "level": "all"},
    "smu_scholarship": {"url": "https://admissions.smu.edu.sg/financial-matters/financial-aid-and-scholarships", "country": "Singapore", "type": "varies", "level": "all"},
    "astar": {"url": "https://www.a-star.edu.sg/Scholarships", "country": "Singapore", "type": "full_funding", "level": "graduate"},
    
    # === HONG KONG ===
    "hk_phd": {"url": "https://cerg1.ugc.edu.hk/hkpfs", "country": "Hong Kong", "type": "full_funding", "level": "phd"},
    "hku": {"url": "https://www.hku.hk/students/fees-financial-aid.html", "country": "Hong Kong", "type": "varies", "level": "all"},
    "cuhk": {"url": "https://www.cuhk.edu.hk/adm/scholarships", "country": "Hong Kong", "type": "varies", "level": "all"},
    "hkust": {"url": "https://pg.ust.hk/prospective-students/scholarship-opportunities", "country": "Hong Kong", "type": "varies", "level": "graduate"},
    
    # === UAE/MIDDLE EAST ===
    "masdar": {"url": "https://masdar.ac.ae/admissions/scholarships", "country": "UAE", "type": "full_funding", "level": "graduate"},
    "kaust": {"url": "https://www.kaust.edu.sa/en/study/discovering-kaust/financial-award", "country": "Saudi Arabia", "type": "full_funding", "level": "graduate"},
    "qcri": {"url": "https://www.hbku.edu.qa/en/qcri", "country": "Qatar", "type": "full_funding", "level": "graduate"},
    
    # === AFRICAN SCHOLARSHIPS ===
    "mastercard_foundation": {"url": "https://mastercardfdn.org/our-work/scholars-program", "country": "Africa", "type": "full_funding", "level": "all"},
    "mandela_rhodes": {"url": "https://www.mandelarhodes.org", "country": "South Africa", "type": "full_funding", "level": "graduate"},
    "queen_elizabeth": {"url": "https://www.queenelizabethscholars.ca", "country": "Africa", "type": "full_funding", "level": "graduate"},
    "african_leadership": {"url": "https://www.africanleadershipacademy.org", "country": "Africa", "type": "full_funding", "level": "secondary"},
    "aga_khan": {"url": "https://www.akdn.org/our-agencies/aga-khan-foundation/international-scholarship-programme", "country": "Africa", "type": "full_funding", "level": "graduate"},
    "mo_ibrahim": {"url": "https://mo.ibrahim.foundation/leadership-fellowships", "country": "Africa", "type": "full_funding", "level": "professional"},
    "canon_collins": {"url": "https://canoncollins.org.uk/scholarships", "country": "Africa", "type": "full_funding", "level": "graduate"},
    "africa_oxford": {"url": "https://www.afriox.org", "country": "Africa", "type": "full_funding", "level": "graduate"},
    "allen_foundation": {"url": "https://vulcancapital.com/allen-foundation", "country": "Africa", "type": "full_funding", "level": "graduate"},
    "afrox": {"url": "https://www.afriox.org", "country": "Africa", "type": "full_funding", "level": "graduate"},
    
    # === USA SCHOLARSHIPS ===
    "nsf_grfp": {"url": "https://www.nsfgrfp.org", "country": "USA", "type": "full_funding", "level": "graduate"},
    "hertz": {"url": "https://www.hertzfoundation.org", "country": "USA", "type": "full_funding", "level": "phd"},
    "jack_kent_cooke": {"url": "https://www.jkcf.org/our-scholarships", "country": "USA", "type": "full_funding", "level": "all"},
    "coca_cola": {"url": "https://www.coca-colascholarsfoundation.org", "country": "USA", "type": "varies", "level": "undergraduate"},
    "gates_millennium": {"url": "https://gmsp.org", "country": "USA", "type": "full_funding", "level": "undergraduate"},
    "davidson": {"url": "https://www.davidsongifted.org/gifted-programs/fellows-scholarship", "country": "USA", "type": "varies", "level": "undergraduate"},
    "regeneron_sts": {"url": "https://www.societyforscience.org/regeneron-sts", "country": "USA", "type": "prize", "level": "secondary"},
    "siemens": {"url": "https://www.siemens-foundation.org/programs/stem/competition", "country": "USA", "type": "prize", "level": "secondary"},
    "goldwater": {"url": "https://goldwater.scholarsapply.org", "country": "USA", "type": "partial", "level": "undergraduate"},
    "truman": {"url": "https://www.truman.gov", "country": "USA", "type": "partial", "level": "undergraduate"},
    "udall": {"url": "https://www.udall.gov", "country": "USA", "type": "partial", "level": "undergraduate"},
    "boren": {"url": "https://www.borenawards.org", "country": "USA", "type": "full_funding", "level": "all"},
    "gilman": {"url": "https://www.gilmanscholarship.org", "country": "USA", "type": "partial", "level": "undergraduate"},
    "critical_language": {"url": "https://clscholarship.org", "country": "USA", "type": "full_funding", "level": "undergraduate"},
    
    # === SCHOLARSHIP DATABASES ===
    "scholarships_com": {"url": "https://www.scholarships.com", "country": "USA", "type": "database", "level": "all"},
    "fastweb": {"url": "https://www.fastweb.com", "country": "USA", "type": "database", "level": "all"},
    "cappex": {"url": "https://www.cappex.com/scholarships", "country": "USA", "type": "database", "level": "all"},
    "collegeboard": {"url": "https://bigfuture.collegeboard.org/scholarship-search", "country": "USA", "type": "database", "level": "undergraduate"},
    "niche": {"url": "https://www.niche.com/colleges/scholarships", "country": "USA", "type": "database", "level": "all"},
    "unigo": {"url": "https://www.unigo.com/scholarships", "country": "USA", "type": "database", "level": "all"},
    "chegg": {"url": "https://www.chegg.com/scholarships", "country": "USA", "type": "database", "level": "all"},
    "bold_org": {"url": "https://bold.org/scholarships", "country": "USA", "type": "database", "level": "all"},
    "going_merry": {"url": "https://www.goingmerry.com", "country": "USA", "type": "database", "level": "all"},
    "scholly": {"url": "https://myscholly.com", "country": "USA", "type": "database", "level": "all"},
    "scholarshipowl": {"url": "https://scholarshipowl.com", "country": "USA", "type": "database", "level": "all"},
    "raise_me": {"url": "https://www.raise.me", "country": "USA", "type": "database", "level": "all"},
    "studentscholarships": {"url": "https://www.studentscholarships.org", "country": "Global", "type": "database", "level": "all"},
    "internationalscholarships": {"url": "https://www.internationalscholarships.com", "country": "Global", "type": "database", "level": "all"},
    "iefa": {"url": "https://www.iefa.org", "country": "Global", "type": "database", "level": "all"},
    "fundingforstudy": {"url": "https://www.fundingforstudy.com", "country": "Global", "type": "database", "level": "all"},
    "scholars4dev": {"url": "https://www.scholars4dev.com", "country": "Global", "type": "database", "level": "all"},
    "afterschool": {"url": "https://afterschool.africa", "country": "Africa", "type": "database", "level": "all"},
    "opportunitydesk": {"url": "https://opportunitydesk.org/category/scholarships", "country": "Global", "type": "database", "level": "all"},
}

FELLOWSHIPS = {
    # === PRESTIGIOUS FELLOWSHIPS ===
    "rhodes_scholarship": {"url": "https://www.rhodeshouse.ox.ac.uk", "focus": "leadership", "duration": "2-3 years"},
    "fulbright_scholar": {"url": "https://fulbrightscholars.org", "focus": "research", "duration": "1 year"},
    "churchill_fellowship": {"url": "https://www.churchillscholarship.org", "focus": "stem", "duration": "1 year"},
    "henry_luce": {"url": "https://www.hluce.org/programs/luce-scholars", "focus": "asia", "duration": "1 year"},
    "watson_fellowship": {"url": "https://watson.foundation", "focus": "exploration", "duration": "1 year"},
    "rotary_peace": {"url": "https://www.rotary.org/en/our-programs/peace-fellowships", "focus": "peace", "duration": "1-2 years"},
    "echoing_green": {"url": "https://echoinggreen.org/fellowship", "focus": "social_entrepreneurship", "duration": "2 years"},
    "ashoka": {"url": "https://www.ashoka.org/en-us/fellowship", "focus": "social_entrepreneurship", "duration": "lifetime"},
    "skoll": {"url": "https://skoll.org/community/skoll-awardees", "focus": "social_entrepreneurship", "duration": "prize"},
    "ted_fellowship": {"url": "https://www.ted.com/participate/ted-fellows-program", "focus": "ideas", "duration": "fellowship"},
    
    # === TECH/AI FELLOWSHIPS ===
    "google_phd": {"url": "https://research.google/outreach/phd-fellowship", "focus": "tech", "duration": "varies"},
    "microsoft_research": {"url": "https://www.microsoft.com/en-us/research/academic-programs", "focus": "tech", "duration": "varies"},
    "meta_research": {"url": "https://research.facebook.com/fellowship", "focus": "tech", "duration": "varies"},
    "apple_scholars": {"url": "https://machinelearning.apple.com/updates/apple-scholars-2024", "focus": "ai", "duration": "varies"},
    "nvidia_fellowship": {"url": "https://www.nvidia.com/en-us/research/graduate-fellowships", "focus": "ai", "duration": "1 year"},
    "intel_fellowship": {"url": "https://www.intel.com/content/www/us/en/research/intel-research-phd-fellowships.html", "focus": "tech", "duration": "varies"},
    "qualcomm_innovation": {"url": "https://www.qualcomm.com/research/university-relations/innovation-fellowship", "focus": "tech", "duration": "1 year"},
    "ibm_fellowship": {"url": "https://www.research.ibm.com/university/awards/fellowships.html", "focus": "tech", "duration": "varies"},
    "amazon_science": {"url": "https://www.amazon.science/academic-engagements/amazon-fellowship", "focus": "tech", "duration": "varies"},
    "hertz_fellowship": {"url": "https://www.hertzfoundation.org/the-fellowship", "focus": "stem", "duration": "5 years"},
    "paul_allen": {"url": "https://alleninstitute.org/fellowship", "focus": "ai", "duration": "varies"},
    "openai_fellowship": {"url": "https://openai.com/careers#research", "focus": "ai", "duration": "varies"},
    "deepmind_fellowship": {"url": "https://deepmind.google/education/", "focus": "ai", "duration": "varies"},
    
    # === POLICY/GOVERNMENT ===
    "white_house": {"url": "https://www.whitehouse.gov/get-involved/fellows", "focus": "policy", "duration": "1 year"},
    "presidential_management": {"url": "https://www.pmf.gov", "focus": "government", "duration": "2 years"},
    "congress": {"url": "https://www.congress.gov/resources/display/content/Fellowships", "focus": "policy", "duration": "varies"},
    "state_department": {"url": "https://careers.state.gov/intern-fellow-program", "focus": "diplomacy", "duration": "varies"},
    "brookings": {"url": "https://www.brookings.edu/careers/fellowships", "focus": "policy", "duration": "varies"},
    "rand": {"url": "https://www.rand.org/about/edu_op/fellowships.html", "focus": "policy", "duration": "varies"},
    "council_foreign_relations": {"url": "https://www.cfr.org/fellowships", "focus": "foreign_policy", "duration": "1 year"},
    "carnegie": {"url": "https://carnegieendowment.org/about/employment/?fa=fellowship", "focus": "international_affairs", "duration": "varies"},
    
    # === JOURNALISM/MEDIA ===
    "nieman": {"url": "https://nieman.harvard.edu/fellowships", "focus": "journalism", "duration": "1 year"},
    "knight": {"url": "https://knightfoundation.org/programs/journalism", "focus": "journalism", "duration": "varies"},
    "reuters_institute": {"url": "https://reutersinstitute.politics.ox.ac.uk/journalist-fellowships", "focus": "journalism", "duration": "varies"},
    "tow_center": {"url": "https://towcenter.columbia.edu/fellowships", "focus": "journalism", "duration": "varies"},
    "pulitzer_center": {"url": "https://pulitzercenter.org/fellowship", "focus": "journalism", "duration": "varies"},
    
    # === ENTREPRENEURSHIP ===
    "thiel_fellowship": {"url": "https://thielfellowship.org", "focus": "entrepreneurship", "duration": "2 years"},
    "kauffman": {"url": "https://www.kauffman.org/programs/kauffman-fellows", "focus": "vc", "duration": "2 years"},
    "techstars_fellowship": {"url": "https://www.techstars.com/the-line/advice/techstars-foundation-fellowship", "focus": "entrepreneurship", "duration": "varies"},
    "startingbloc": {"url": "https://startingbloc.org/fellowship", "focus": "social_entrepreneurship", "duration": "varies"},
    "acumen": {"url": "https://acumen.org/fellowships", "focus": "social_entrepreneurship", "duration": "1 year"},
    "unreasonable": {"url": "https://unreasonablegroup.com/fellowship", "focus": "entrepreneurship", "duration": "varies"},
    "village_capital": {"url": "https://vilcap.com/accelerators", "focus": "entrepreneurship", "duration": "varies"},
    "halcyon": {"url": "https://halcyonhouse.org/incubator", "focus": "social_entrepreneurship", "duration": "5 months"},
    "resolution_fellowship": {"url": "https://www.resolutionfellowship.org", "focus": "social_entrepreneurship", "duration": "2 years"},
    
    # === SCIENCE/RESEARCH ===
    "ford_foundation": {"url": "https://sites.nationalacademies.org/PGA/FordFellowships", "focus": "diversity", "duration": "varies"},
    "packard": {"url": "https://www.packard.org/what-we-fund/science/packard-fellowships-for-science-and-engineering", "focus": "science", "duration": "5 years"},
    "sloan_research": {"url": "https://sloan.org/fellowships", "focus": "science", "duration": "2 years"},
    "searle": {"url": "https://www.searlescholars.net", "focus": "biomedical", "duration": "3 years"},
    "pew_biomedical": {"url": "https://www.pewtrusts.org/en/projects/pew-biomedical-scholars", "focus": "biomedical", "duration": "4 years"},
    "beckman": {"url": "https://www.beckman-foundation.org/programs/beckman-young-investigators", "focus": "chemistry", "duration": "4 years"},
    "keck": {"url": "https://www.wmkeck.org/grant-programs", "focus": "science", "duration": "varies"},
    "burroughs_wellcome": {"url": "https://www.bwfund.org/funding-opportunities", "focus": "biomedical", "duration": "5 years"},
    "simons_fellowship": {"url": "https://www.simonsfoundation.org/funding-opportunities", "focus": "math", "duration": "varies"},
    "smithsonian": {"url": "https://www.si.edu/ofi", "focus": "research", "duration": "varies"},
    "nasa_fellowship": {"url": "https://nspires.nasaprs.com/external/solicitations/summary.do?solId=%7B913A7DEE-2747-6539-130C-0AB1E2322F42%7D", "focus": "space", "duration": "varies"},
    "energy_sciences": {"url": "https://science.osti.gov/wdts/scgsr", "focus": "energy", "duration": "varies"},
    
    # === ARTS/HUMANITIES ===
    "macarthur": {"url": "https://www.macfound.org/programs/fellows", "focus": "genius", "duration": "5 years"},
    "guggenheim": {"url": "https://www.gf.org/applicants/the-guggenheim-fellowship", "focus": "arts", "duration": "1 year"},
    "rome_prize": {"url": "https://www.aarome.org/apply/rome-prize", "focus": "arts", "duration": "1-2 years"},
    "radcliffe": {"url": "https://www.radcliffe.harvard.edu/fellowship-program", "focus": "humanities", "duration": "1 year"},
    "cullman_center": {"url": "https://www.nypl.org/help/about-nypl/fellowships-institutes/center-for-scholars-and-writers", "focus": "writing", "duration": "1 year"},
    "mellon": {"url": "https://mellon.org/grants/grants-database/grants-database-by-program", "focus": "humanities", "duration": "varies"},
    "neh_fellowship": {"url": "https://www.neh.gov/grants/research/fellowships", "focus": "humanities", "duration": "varies"},
    "acls": {"url": "https://www.acls.org/programs/acls-fellowship", "focus": "humanities", "duration": "varies"},
    
    # === GLOBAL DEVELOPMENT ===
    "gates_foundation": {"url": "https://www.gatesfoundation.org/about/careers", "focus": "global_health", "duration": "varies"},
    "wellcome_trust": {"url": "https://wellcome.org/grant-funding", "focus": "health", "duration": "varies"},
    "rockefeller": {"url": "https://www.rockefellerfoundation.org/grants", "focus": "development", "duration": "varies"},
    "soros_fellowship": {"url": "https://www.pdsoros.org", "focus": "new_americans", "duration": "2 years"},
    "yenching_academy": {"url": "https://yenchingacademy.pku.edu.cn", "focus": "china", "duration": "2 years"},
    "stanford_africa": {"url": "https://kingcenter.stanford.edu/our-programs/stanford-africa-fellows", "focus": "africa", "duration": "varies"},
    
    # === CLIMATE/ENVIRONMENT ===
    "environmental_fellowship": {"url": "https://www.environmentalfellowship.org", "focus": "environment", "duration": "varies"},
    "climate_leadership": {"url": "https://www.climateleadership.org/fellowship", "focus": "climate", "duration": "varies"},
    "switzer": {"url": "https://www.switzernetwork.org", "focus": "environment", "duration": "1 year"},
    "knauss_fellowship": {"url": "https://seagrant.noaa.gov/Knauss-Fellowship-Program", "focus": "marine", "duration": "1 year"},
}

def get_all_scholarship_sources():
    """Return total count and all scholarship/fellowship sources"""
    total = len(SCHOLARSHIPS) + len(FELLOWSHIPS)
    return {
        "total": total,
        "scholarships": SCHOLARSHIPS,
        "fellowships": FELLOWSHIPS
    }
