"""
EarlyBird configuration.

Single source of truth for sources, target companies, profile keywords, and
filters. Edit this file to tune the pipeline without touching core logic.

Secrets (API keys, personal identity) stay in .env and are never placed here.
"""

# ---------------------------------------------------------------------------
# Profile keywords -- drive relevance filtering and ranking.
# A role is relevant if any of these appear in its title or description.
# Higher tiers add more weight during ranking.
# ---------------------------------------------------------------------------
PROFILE_KEYWORDS = {
    # Strong signals for the AI/ML niche (weight 3)
    "high": [
        "rag", "llm", "agent", "agentic", "embedding", "vector db", "vector database",
        "fine-tune", "fine tuning", "ai", "genai", "generative ai", "prompt", "inference",
        "retrieval-augmented", "langchain", "llamaindex",
    ],
    # Core stack (weight 2)
    "core": [
        "python", "fastapi", "next.js", "nextjs", "react", "typescript",
        "postgres", "postgresql", "docker", "aws",
    ],
    # Adjacent / role-family terms (weight 1)
    "bonus": [
        "machine learning", " ml ", "ml engineer", "ai engineer", "software engineer",
        "full stack", "full-stack", "fullstack", "backend", "back-end", "frontend",
        "front-end", "node", "graphql", "developer",
    ],
}

# ---------------------------------------------------------------------------
# Role targeting -- paid, entry/mid, IC software/AI roles only.
# ---------------------------------------------------------------------------
# Internships are included but hard-guarded in job_pipeline_full.py:
# explicit unpaid/for-credit or enrollment-required postings are dropped;
# ambiguous ones are kept with a "verify enrollment requirement" note.
INCLUDE_INTERNSHIPS = True

# Exclude roles requiring a conferred degree by start date: "deprioritize" or "filter".
DEGREE_REQUIREMENT_MODE = "deprioritize"

# --- Seniority ceiling (default ON) ---
# Titles containing any of these are excluded. Tuned for an entry-to-mid
# candidate: no staff/principal/lead/senior/management roles.
# Matched against the normalized title (lowercase, punctuation collapsed to
# spaces, space-padded), so space-wrapped tokens are word-bounded: " lead "
# cannot match "leadership" and " architect " cannot match "architecture".
SENIORITY_EXCLUDE = [
    "staff", "principal", "distinguished", "fellow", "senior", " sr ",
    "manager", " director ", "head of", "vice president", " vp ",
    " lead ", " architect ",
]
# Exclude roles whose description requires this many years of experience or more.
MAX_YEARS = 5

# Positive signals for an entry/mid IC role (used for ranking bonus).
ENTRY_MID_SIGNALS = [
    "engineer i", "engineer ii", "engineer 1", "engineer 2", "associate",
    "junior", "jr.", "jr ", "new grad", "new graduate", "early career",
    "entry level", "entry-level", "university grad", "recent grad", "apprentice",
]

# --- Ops / infra / database-ops filter ---
# Titles containing any of these are excluded: the track is software /
# full-stack / AI engineering, not ops, infra, or database operations.
# Matched against the title padded with spaces, so " dba " is word-bounded.
# Edit this list to re-admit a family (e.g. remove "mlops" to allow MLOps roles).
OPS_INFRA_EXCLUDE = [
    "operations engineer", "ops engineer", "devops", "sysops", "mlops",
    "infrastructure", " infra ", "infra/", "infra &", "reliability engineer",
    "systems engineer",
    "systems software", "database engineer", "database administrator",
    "database reliability", " dba ", "clickhouse", "network operations",
    "data center", "datacenter", "kubernetes engineer", "cloud engineer",
    "cloud operations",
]

# --- Track gate (title-level) ---
# The TITLE itself must carry a track signal to pass: at least one keyword
# below, or one of the startup-title patterns in TRACK_TITLE_ALLOW.
# Description keywords still boost rank but can no longer rescue a title
# with no track signal (kills bare "Engineering" listings).
# Matched against the title padded with spaces.
TRACK_TITLE_KEYWORDS = [
    "software", "developer", "full stack", "full-stack", "fullstack",
    "backend", "back-end", "back end", "frontend", "front-end", "front end",
    "web", " ai ", "ai/", " ml ", "machine learning", "swe", "llm",
    "genai", "generative ai", "deep learning",
]

# AI-startup title patterns that pass the track gate even without a standard
# track keyword. "Founding Engineer" and "Product Engineer" included: they are
# the standard small-startup titles for exactly this track.
TRACK_TITLE_ALLOW = [
    "member of technical staff", "applied scientist",
    "forward deployed engineer", "ai engineer", "research engineer",
    "founding engineer", "product engineer",
    # Early-career program titles that often omit a standard track keyword
    # ("engineering intern" also matches "engineering internship").
    "engineering intern", "software intern", "swe intern", "developer intern",
    "engineering co-op", "engineering apprentice", "engineering fellowship",
    "software fellowship",
]

# --- Function filter ---
# Titles containing any of these are excluded (off-target functions).
# Matched against the normalized title (see SENIORITY_EXCLUDE note), so
# " sre " is word-bounded. "Embedded" is matched as systems/firmware phrases
# only, so "Embedded Analytics Engineer" (a BI software role) is not dropped.
FUNCTION_EXCLUDE = [
    "security", "infosec", "site reliability", " sre ", "sysadmin",
    "system administrator", "systems administrator", "it systems",
    "information technology", "network engineer", "hardware", "firmware",
    "embedded systems", "embedded software", "embedded engineer",
    "data scientist", "data science", "research scientist",
    "sales engineer", "solutions engineer", "solution engineer",
    "support engineer", "customer engineer", "customer success", "qa engineer",
    "quality assurance", "test engineer", "developer advocate",
    "developer relations", "devrel",
]

# ---------------------------------------------------------------------------
# Company targeting -- smaller firms, not mega-caps.
# ---------------------------------------------------------------------------
# Companies excluded entirely (mega-caps / unicorns / frontier labs). Matched
# as a lowercase substring of the company name.
EXCLUDE_COMPANIES = [
    "databricks", "airbnb", "figma", "robinhood", "flexport",
    "scale ai", "scaleai", "anthropic",
]

# Company-size proxy: number of open postings on a company's ATS board.
# Boards larger than LARGE are penalized (big company); boards at or under
# SMALL get a bonus (startup). Roles from aggregated boards (RemoteOK) are neutral.
LARGE_BOARD_THRESHOLD = 120
SMALL_BOARD_THRESHOLD = 40

# ---------------------------------------------------------------------------
# Location filter. US work authorization held, sponsorship never required.
# A role is accepted ONLY if it is remote (US-eligible or unrestricted) or
# onsite/hybrid in an accepted metro below. Everything else -- SF, Seattle,
# Austin, all other metros -- is dropped. Edit the list to change geography.
# ---------------------------------------------------------------------------
ACCEPT_REMOTE = True   # remote/remote-US roles accepted and rank-boosted

# Onsite/hybrid metros within commuting range (matched as word-bounded
# lowercase tokens against the location string).
ACCEPTED_METROS = [
    # New York City + area
    "new york", "nyc", "brooklyn", "manhattan", "queens", "bronx",
    "jersey city", "newark", "hoboken", "stamford", "greenwich", "norwalk",
    "white plains", "yonkers", "westchester", "long island",
    "new brunswick", "morristown", "edison",
    # Philadelphia + area
    "philadelphia", "philly", "conshohocken", "king of prussia", "camden",
    "wilmington", "malvern", "radnor", "blue bell", "wayne", "exton",
    "berwyn", "paoli", "villanova", "bryn mawr", "west chester", "norristown",
    "horsham", "fort washington", "plymouth meeting", "cherry hill",
    "mount laurel", "princeton", "trenton", "doylestown",
    # Lehigh Valley
    "allentown", "bethlehem", "easton", "lehigh valley",
]

# ---------------------------------------------------------------------------
# Sources -- toggle each on or off.
# Ashby and Lever skew to startups; Greenhouse is kept but not treated as the
# main pool. RemoteOK covers AI/remote boards via a documented JSON API.
# YC "Work at a Startup" is scraped from the JSON payload embedded in the
# jobs page (robots.txt permits; one request per run; no per-job timestamps,
# so listings are treated as 48h old and never flag Fresh).
# Wellfound is fragile HTML (best-effort). JobSpy (LinkedIn/Indeed) is disabled
# (anti-bot + terms). ai-jobs.net exposes no stable public feed.
# ---------------------------------------------------------------------------
SOURCES = {
    "greenhouse": True,
    "lever": True,
    "ashby": True,
    "remoteok": True,
    "remotive": True,   # documented public API; main remote/contract supply
    "yc": True,
    "wellfound": False,
    "jobspy": False,
}

# ---------------------------------------------------------------------------
# Company watchlist (Greenhouse + Lever). Each entry: name, ats_type, slug.
# Rebalanced toward smaller companies; slugs verified live. Dead slugs are
# skipped gracefully. Dynamic discovery can append more verified companies.
# ---------------------------------------------------------------------------
WATCHLIST = [
    # Greenhouse (smaller / mid, non-unicorn)
    {"name": "Webflow",       "ats_type": "greenhouse", "slug": "webflow"},
    {"name": "Hightouch",     "ats_type": "greenhouse", "slug": "hightouch"},
    {"name": "Cortex",        "ats_type": "greenhouse", "slug": "cortex"},
    {"name": "Pantheon",      "ats_type": "greenhouse", "slug": "pantheon"},
    {"name": "Labelbox",      "ats_type": "greenhouse", "slug": "labelbox"},
    {"name": "AssemblyAI",    "ats_type": "greenhouse", "slug": "assemblyai"},
    {"name": "Cockroach Labs","ats_type": "greenhouse", "slug": "cockroachlabs"},
    # Greenhouse -- validated live 2026-07-10 (board returns 200 with jobs)
    {"name": "Together AI",   "ats_type": "greenhouse", "slug": "togetherai"},
    {"name": "Lightning AI",  "ats_type": "greenhouse", "slug": "lightningai"},
    {"name": "Arize AI",      "ats_type": "greenhouse", "slug": "arizeai"},
    {"name": "Galileo",       "ats_type": "greenhouse", "slug": "galileo"},
    {"name": "Comet",         "ats_type": "greenhouse", "slug": "comet"},
    {"name": "Descript",      "ats_type": "greenhouse", "slug": "descript"},
    {"name": "HeyGen",        "ats_type": "greenhouse", "slug": "heygen"},
    {"name": "Black Forest Labs", "ats_type": "greenhouse", "slug": "blackforestlabs"},
    {"name": "StackBlitz",    "ats_type": "greenhouse", "slug": "stackblitz"},
    {"name": "Vercel",        "ats_type": "greenhouse", "slug": "vercel"},
    {"name": "Netlify",       "ats_type": "greenhouse", "slug": "netlify"},
    {"name": "SingleStore",   "ats_type": "greenhouse", "slug": "singlestore"},
    {"name": "Honeycomb",     "ats_type": "greenhouse", "slug": "honeycomb"},
    {"name": "PlanetScale",   "ats_type": "greenhouse", "slug": "planetscale"},
    {"name": "Prisma",        "ats_type": "greenhouse", "slug": "prisma"},
    {"name": "Glean",         "ats_type": "greenhouse", "slug": "gleanwork"},
    {"name": "SmarterDx",     "ats_type": "greenhouse", "slug": "smarterdx"},
    {"name": "Lithic",        "ats_type": "greenhouse", "slug": "lithic"},
    {"name": "Highnote",      "ats_type": "greenhouse", "slug": "highnote"},
    # Lever (AI / smaller)
    {"name": "Mistral AI",    "ats_type": "lever",      "slug": "mistral"},
    {"name": "Neon",          "ats_type": "lever",      "slug": "neon"},
    {"name": "AngelList",     "ats_type": "lever",      "slug": "angellist"},
    # Lever -- validated live 2026-07-10
    {"name": "Zilliz",        "ats_type": "lever",      "slug": "zilliz"},
    {"name": "Metabase",      "ats_type": "lever",      "slug": "metabase"},
]

# Ashby-hosted boards (slug in api.ashbyhq.com/posting-api/job-board/<slug>).
# Startup and AI-company heavy; slugs verified live (batch below validated
# 2026-07-10: every slug returned HTTP 200 with at least one posting).
ASHBY_COMPANIES = [
    "posthog", "baseten", "modal", "weaviate", "browserbase", "dust", "writer",
    "runway", "linear", "mercor", "abridge", "decagon", "perplexity", "vanta",
    "cohere", "elevenlabs", "sierra", "harvey",
    # AI inference / GPU / model platforms
    "fireworksai", "cerebras", "anyscale", "lambda", "runpod", "sfcompute",
    # Vector / data / agent infra
    "pinecone", "trychroma", "lancedb", "unstructured", "llamaindex",
    "langchain", "letta", "mem0", "e2b", "firecrawl", "exa", "tavily",
    # LLM ops / eval
    "braintrust", "langfuse",
    # Voice / media AI
    "deepgram", "cartesia", "vapi", "retell-ai", "bland", "rime", "opusclip",
    "suno", "pika", "krea", "ideogram", "photoroom",
    # Coding AI / dev platforms
    "cursor", "cognition", "poolside", "continue", "greptile", "factory",
    "zed", "warp", "replit", "render", "railway", "supabase", "convex-dev",
    "workos", "resend", "inngest", "triggerdev", "temporal", "prefect",
    "airbyte", "astronomer", "motherduck", "turbopuffer", "materialize",
    "influxdata", "axiom-co", "mintlify", "attio", "granola", "omni",
    # Applied AI verticals
    "rogo", "norm-ai", "ambiencehealthcare", "openevidence", "freed",
    "anterior", "tennr", "candidhealth",
    # Fintech (smaller)
    "column", "unit", "moderntreasury",
]

# ---------------------------------------------------------------------------
# Run tuning.
# ---------------------------------------------------------------------------
DEFAULT_HOURS = 168       # standard lookback window (7 days). 72h was the
                          # binding constraint on volume: Greenhouse alone went
                          # 0 -> 3 -> 14 ranked roles at 72h -> 168h -> 336h.
FRESH_HOURS = 6           # window used by the fast --fresh polling mode
OUTREACH_TOP_N = 15       # generate an outreach contact + draft for the top N ranked roles

# Dynamic-discovery cache (verified company slugs from the cold-outreach cache).
WATCHLIST_CACHE_FILE = "watchlist_cache.json"
WATCHLIST_CACHE_MAX_DAYS = 7
