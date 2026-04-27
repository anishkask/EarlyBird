# EarlyBird — Project Context for Claude Code

## What This Project Does

EarlyBird is a Python-based job search automation pipeline built for a CS student (Temple University, graduating December 2026) looking for summer 2026 software engineering internships. It runs daily and does three things:

1. **Job discovery** -- aggregates internship listings from multiple sources and surfaces them within hours of posting, before they reach mass job boards
2. **Job outreach contacts** -- for each job found, researches real outreach contacts at that company using Claude API web search
3. **Cold outreach discovery** -- scrapes VC portfolio sites to find seed/pre-seed companies and researches their founders/CEOs for cold outreach

Output is a color-coded Excel file with three tabs: Jobs, Outreach, Cold Outreach.

---

## File Structure

```
earlybird/
├── job_pipeline_full.py   -- main script, runs job scraping + outreach research
├── cold_outreach.py       -- cold outreach module, scrapes VC portfolios
├── funding_pull.py        -- Crunchbase-based dynamic company sourcing (in progress)
├── job_hunter.py          -- supplementary job search utilities
├── companies.json         -- cache of companies from funding pull
├── cold_outreach_cache.json -- cache of already-processed cold outreach companies
├── .env                   -- never commit this
├── .env.example           -- safe to commit, no values filled in
├── .gitignore
├── requirements.txt
├── README.md
├── logs/
│   └── .gitkeep
└── data/
```

---

## How to Run

```bash
# Activate virtual environment first
source ~/job-pipeline-env/bin/activate   # Linux/WSL
.venv\Scripts\activate                   # Windows

# Standard run -- find jobs + research contacts
python job_pipeline_full.py --hours 72

# Scrape only -- no Claude API calls, just find jobs and write Excel
python job_pipeline_full.py --scrape-only --hours 72

# With cold outreach -- adds Cold Outreach tab to Excel
python job_pipeline_full.py --hours 72 --cold-outreach

# Cold outreach only
python cold_outreach.py

# Force refresh cold outreach cache
python cold_outreach.py --refresh
```

---

## Environment Variables

All personal info lives in `.env`. Never hardcode any of these in the script.

```
ANTHROPIC_API_KEY=        # required for contact research and cold outreach
YOUR_NAME=
YOUR_SCHOOL=Temple University
YOUR_LINKEDIN=
YOUR_PORTFOLIO=
YOUR_GITHUB=
EMAIL_DELAY_MIN=180
EMAIL_DELAY_MAX=300
```

Optional (not currently active):
```
APOLLO_API_KEY=           # not used -- Apollo removed from codebase
HUNTER_API_KEY=           # not used
CRUNCHBASE_API_KEY=       # used in funding_pull.py
```

---

## Target Geography

Jobs are filtered to keep only:
- Pennsylvania locations: Philadelphia, Exton, Hatfield, King of Prussia, Malvern, Wayne, Conshohocken, Blue Bell, Newtown, Horsham, Lansdale, Collegeville, Berwyn, Paoli, Radnor, Villanova, Bryn Mawr, Media, West Chester, Norristown, Audubon, Oaks, or anywhere containing "PA" or "Pennsylvania"
- Remote: location is blank, null, "Remote", "Anywhere", "United States", "USA", "US", "Work from home", "WFH"

Filter OUT: any job with a specific non-PA city or non-US country (Dublin, London, Toronto, Bengaluru, Luxembourg, Warsaw, Sao Paulo, etc.)

---

## Role Filtering

Keep roles where title contains: "intern", "internship", "co-op", "coop", "summer"

Filter OUT: "senior", "staff", "principal", "director", "manager", "lead", "VP", "head of" -- unless "intern" also appears in the title.

---

## Job Sources

- Greenhouse ATS -- polls `https://boards-api.greenhouse.io/v1/boards/{token}/jobs?content=true`
- Lever ATS -- polls `https://api.lever.co/v0/postings/{slug}?mode=json`
- LinkedIn and Indeed -- via JobSpy
- Watchlist -- 80+ hardcoded company tokens/slugs (being replaced by dynamic funding pull)
- VC portfolio boards: YC Work at a Startup, a16z, First Round Capital, Contrary Capital, Dreamit Ventures
- Staffing firms: Robert Half, Theoris, TEKsystems, Apex Systems, Insight Global

ZipRecruiter is permanently removed -- always returns 403.

---

## Contact Research -- Critical Implementation Notes

**The web search tool MUST be explicitly passed in every Claude API call for contact research.** Without it Claude uses training data only and returns blanks. This is the most common failure mode.

Correct pattern:
```python
response = anthropic_client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1000,
    tools=[{"type": "web_search_20250305", "name": "web_search"}],
    messages=[{
        "role": "user",
        "content": "Search LinkedIn and the web right now for..."
    }]
)

# Parse response correctly -- web search returns multiple content blocks
result_text = ""
for block in response.content:
    if block.type == "text":
        result_text += block.text
```

**Apollo is completely removed.** Do not re-add Apollo API checks. Do not gate contact research behind any API key other than ANTHROPIC_API_KEY.

**Contact research priority order:**
1. Campus recruiter or university recruiting contact
2. Engineering recruiter or talent acquisition
3. Alumni from Temple University at the company
4. Senior engineer on the relevant team

**Return only real information found via web search.** If a field is not found, leave it blank. Never hallucinate names, titles, or emails.

---

## Excel Output Structure

**Jobs tab columns:**
Row number, Role, Company, Location, Source, Posted (hours ago), Apply Link, Match Score, Applied?, Date Applied, Status

Color coding:
- Red = posted under 6 hours (URGENT)
- Green = posted under 24 hours
- Yellow = posted under 48 hours
- White = posted over 48 hours

**Outreach tab columns:**
Company, Role, Contact Name, Title, LinkedIn URL, Email

All URLs must be real clickable Excel hyperlinks using `openpyxl`'s `cell.hyperlink` property. Never write raw URLs as plain text.

**Cold Outreach tab columns:**
Site, Company, Contact Name, Title, LinkedIn URL, Contact Date, Email

Newly founded companies (2023 or later) should have a light yellow row fill and be sorted to the top.

---

## Cold Outreach Module

`cold_outreach.py` scrapes these VC portfolio sites fresh on every run:
- `https://www.eranyc.com/companies/`
- `https://www.brooklynbridge.vc/portfolio`
- `https://www.lererhippeau.com/portfolio`
- `https://www.fjlabs.com/portfolio`
- `https://www.techstars.com/portfolio?worldregion=Americas&yearMin=2025`
- `https://www.antler.co/portfolio`
- `https://venturecapitalcareers.com/`

Each source has its own scraper function (e.g. `scrape_era_nyc()`, `scrape_brooklyn_bridge()`).

After scraping, compare against `cold_outreach_cache.json` and only process new companies. This avoids re-researching companies already contacted.

For each new company:
1. Classify as tech/software or non-tech using Claude API web search -- skip non-tech
2. Find founding year -- flag as NEW if founded 2023 or later
3. Find CEO/co-founder contact: name, title, LinkedIn URL, email if publicly available
4. Output to Excel and cache

---

## What Not to Break

- Do not re-add Apollo or Hunter API dependencies
- Do not re-add Gmail sending or email drafting -- those were intentionally removed
- Do not add emojis to print statements or console output
- Do not hardcode personal info (name, email, school, LinkedIn) -- always use os.getenv()
- Do not commit .env, token.json, credentials.json, or *.xlsx files
- The --scrape-only flag must always skip ALL Claude API calls entirely
- Silent except: pass blocks are not acceptable -- always log errors with print(f"WARNING: {e}")

---

## Email Finding Workflow (Apollo.io Pattern Method)

When EarlyBird finds a contact name but no email, the user manually finds emails using Apollo.io with a one-credit-per-company approach. The script should support this workflow.

**How it works:**
1. EarlyBird finds contact name and company domain via web search -- email left blank
2. User clicks the Apollo Lookup link in Excel -- opens Apollo filtered to that company
3. User spends 1 Apollo credit to reveal one email -- this exposes the company email pattern
4. User fills in the Email Pattern column (e.g. `{first}.{last}@company.com`)
5. User constructs remaining contact emails manually from the pattern -- no more credits needed
6. User brings contact info to Claude for outreach draft

**Required columns in both Outreach and Cold Outreach tabs:**

After the Email column, always include these three additional columns:

1. **Company Domain** -- auto-extracted from apply link or company website URL. Strip to root domain only (e.g. `airbnb.com` not `careers.airbnb.com`). This is what gets pasted into Apollo.

2. **Apollo Lookup** -- clickable Excel hyperlink that opens Apollo people search pre-filtered to that company domain:
   `https://app.apollo.io/#/people?q_organization_domains[]={company_domain}`
   Display text: "Open Apollo"

3. **Email Pattern** -- blank column for manual entry after Apollo lookup. Example values the user would fill in: `{first}@company.com`, `{first}.{last}@company.com`, `{f}{last}@company.com`

**Implementation notes:**
- Company Domain should be extracted automatically from the apply link URL using Python's `urllib.parse` -- strip subdomains like `careers.`, `jobs.`, `boards.` to get the root domain
- Apollo Lookup must be a real clickable Excel hyperlink using openpyxl `cell.hyperlink`
- Never attempt to guess or construct emails without a confirmed pattern -- leave Email blank until the user fills in the pattern manually

- Greenhouse and Lever watchlist scrapers return 0 -- token/slug formats need verification
- LinkedIn/Indeed via JobSpy returns 0 intermittently -- search terms need tuning
- Geographic filter may be too aggressive -- jobs with blank location should always pass
- Cold outreach tab not yet appending to main Excel output when --cold-outreach flag is used
- Claude API contact research returns blanks -- confirmed cause is missing web search tool in API call

---

## Candidate Background (for outreach context)

Skills: Python, TypeScript, React, FastAPI, PostgreSQL, Docker, ChromaDB, REST APIs, OpenAI API, RAG Pipelines, HuggingFace, BeautifulSoup, Claude API, openpyxl, JobSpy

Key projects:
- EarlyBird (this project) -- job search automation pipeline
- Semantic Code Search -- production RAG pipeline, FastAPI + ChromaDB + React, benchmarked MiniLM vs OpenAI embeddings, 70% Recall@5
- ReMo -- full-stack TypeScript/React + FastAPI/PostgreSQL, Google OAuth, real users, deployed
- PasswordManager -- desktop app, team of 6, PyQt6, Agile

Experience: Software Engineering Intern at Bourns Inc (June-August 2024) -- RPA automation, UiPath, Python, REST APIs, SAP, Agile

School: Temple University, B.S. Computer Science

Portfolio: stored in YOUR_PORTFOLIO env var
GitHub: stored in YOUR_GITHUB env var
LinkedIn: stored in YOUR_LINKEDIN env var
