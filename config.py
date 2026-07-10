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
        "fine-tune", "fine tuning", "genai", "generative ai", "prompt", "inference",
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
INCLUDE_INTERNSHIPS = False

# Exclude roles requiring a conferred degree by start date: "deprioritize" or "filter".
DEGREE_REQUIREMENT_MODE = "deprioritize"

# --- Seniority ceiling (default ON) ---
# Titles containing any of these are excluded. Tuned for an entry-to-mid
# candidate: no staff/principal/lead/senior/management roles.
SENIORITY_EXCLUDE = [
    "staff", "principal", "distinguished", "fellow", "senior", "sr.", "sr ",
    "manager", "director", "head of", "vice president", "vp ", "vp,",
    "lead ", "lead,", " lead", "architect",
]
# Exclude roles whose description requires this many years of experience or more.
MAX_YEARS = 5

# Positive signals for an entry/mid IC role (used for ranking bonus).
ENTRY_MID_SIGNALS = [
    "engineer i", "engineer ii", "engineer 1", "engineer 2", "associate",
    "junior", "jr.", "jr ", "new grad", "new graduate", "early career",
    "entry level", "entry-level", "university grad", "recent grad", "apprentice",
]

# --- Function filter ---
# Titles containing any of these are excluded (off-target functions).
FUNCTION_EXCLUDE = [
    "security", "infosec", "site reliability", " sre ", "sysadmin",
    "system administrator", "systems administrator", "it systems",
    "information technology", "network engineer", "hardware", "firmware",
    "embedded", "data scientist", "data science", "research scientist",
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
# ---------------------------------------------------------------------------
REMOTE_OK = True

# ---------------------------------------------------------------------------
# Sources -- toggle each on or off.
# Ashby and Lever skew to startups; Greenhouse is kept but not treated as the
# main pool. RemoteOK covers AI/remote boards via a documented JSON API.
# Wellfound is fragile HTML (best-effort). JobSpy (LinkedIn/Indeed) is disabled
# (anti-bot + terms). ai-jobs.net and YC "Work at a Startup" expose no stable
# public feed and are intentionally not integrated.
# ---------------------------------------------------------------------------
SOURCES = {
    "greenhouse": True,
    "lever": True,
    "ashby": True,
    "remoteok": True,
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
    # Lever (AI / smaller)
    {"name": "Mistral AI",    "ats_type": "lever",      "slug": "mistral"},
    {"name": "Neon",          "ats_type": "lever",      "slug": "neon"},
    {"name": "AngelList",     "ats_type": "lever",      "slug": "angellist"},
]

# Ashby-hosted boards (slug in api.ashbyhq.com/posting-api/job-board/<slug>).
# Startup and AI-company heavy; slugs verified live.
ASHBY_COMPANIES = [
    "posthog", "baseten", "modal", "weaviate", "browserbase", "dust", "writer",
    "runway", "linear", "mercor", "abridge", "decagon", "perplexity", "vanta",
    "cohere", "elevenlabs", "sierra", "harvey",
]

# ---------------------------------------------------------------------------
# Run tuning.
# ---------------------------------------------------------------------------
DEFAULT_HOURS = 72        # standard lookback window
FRESH_HOURS = 6           # window used by the fast --fresh polling mode
OUTREACH_TOP_N = 15       # generate an outreach contact + draft for the top N ranked roles

# Dynamic-discovery cache (verified company slugs from the cold-outreach cache).
WATCHLIST_CACHE_FILE = "watchlist_cache.json"
WATCHLIST_CACHE_MAX_DAYS = 7
