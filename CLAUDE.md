# EarlyBird -- Project Context for Claude Code

## What This Project Does

EarlyBird is a job search automation pipeline for an early-career software /
full-stack / AI engineer. It polls company ATS APIs and startup job boards,
filters hard for attainable paid roles (right level, right track, right
geography), ranks them, researches outreach contacts with the Claude API plus
live web search, and outputs a color-coded Excel tracker. A FastAPI backend
(api.py) and React dashboard (earlybird-ui/) wrap the same pipeline for the
web; the hosted demo takes each visitor's own Anthropic key per request.

Target: paid roles of every type (full-time, contract ranked first,
part-time, apprenticeship, paid internship behind a guard), remote US or
NYC/Philadelphia/Lehigh Valley metros, smaller companies over mega-caps.

## File Structure

- job_pipeline_full.py -- main pipeline: collect, filter, rank, outreach, Excel
- config.py -- ALL tuning: sources, watchlist, keywords, filters, thresholds
- api.py -- FastAPI backend (deployed on Render via render.yaml)
- cold_outreach.py -- STANDALONE VC-portfolio founder research; not called by
  the pipeline (the old integration was removed deliberately -- do not re-add)
- earlybird-ui/ -- React + Vite + Tailwind dashboard (deployed on Vercel;
  security headers in earlybird-ui/vercel.json)
- requirements.txt, .env.example, .gitignore, LICENSE, README.md

## How to Run

```bash
pip install -r requirements.txt
cp .env.example .env    # fill in ANTHROPIC_API_KEY at minimum

python job_pipeline_full.py                  # standard run with outreach
python job_pipeline_full.py --fresh          # fast poll, no API calls
python job_pipeline_full.py --scrape-only    # no API key needed
python job_pipeline_full.py --hours 24       # custom window
python cold_outreach.py                      # standalone cold outreach

uvicorn api:app --reload --port 8000         # backend
cd earlybird-ui && npm run dev               # frontend on :5173
```

## Sources

Greenhouse, Lever, Ashby (config.WATCHLIST / ASHBY_COMPANIES), YC Work at a
Startup (embedded JSON, robots.txt permits, includes a remote=yes query),
Remotive and RemoteOK (documented JSON APIs). Wellfound and JobSpy
(LinkedIn/Indeed) exist behind config flags but ship DISABLED -- anti-bot
fragility and terms conflicts. Do not re-enable JobSpy by default.

## Filter Design Principles (do not regress these)

1. Word-bound short tokens. "intern" once substring-matched "internal" and
   silently dropped full-time roles for weeks. role_type() uses a word-bounded
   regex; SENIORITY_EXCLUDE and FUNCTION_EXCLUDE match against _norm_title()
   (lowercase, punctuation collapsed, space-padded) so " lead " cannot match
   "leadership" and " architect " cannot match "architecture".
2. Fail open on ambiguity. Blank locations pass. Postings ambiguous about
   internship pay/enrollment are KEPT with a "verify" note, never dropped.
   Undated postings get a 72h-old fallback timestamp in every scraper rather
   than being silently discarded.
3. Per-source isolation. Every scraper wraps its work in try/except and prints
   "WARNING: [source] {e}". One dead board must never kill a run. Silent
   except-pass blocks are not acceptable.
4. All tuning lives in config.py; core logic never hardcodes filter values.

## Excel Output (preserve this structure)

Workbook job_leads_<timestamp>.xlsx with three sheets: Jobs, Outreach, Legend.
Jobs columns: #, Role, Company, Type, Location, Source, Posted, Fresh, Rank,
Apply Link, Applied?, Status, Notes. Fresh flags: "<1h!" under 1 hour, "<6h"
under 6 hours. URLs are real openpyxl hyperlinks, never plain text.

## Contact Research (critical)

The web search tool MUST be passed explicitly in every contact-research call:

```python
tools=[{"type": "web_search_20250305", "name": "web_search"}]
```

Without it Claude answers from training data and fabricates contacts. Fields
that cannot be verified stay blank. Never invent names, titles, or emails.

## Environment Variables (.env, never committed)

ANTHROPIC_API_KEY (required), YOUR_NAME, YOUR_EMAIL, YOUR_LINKEDIN,
YOUR_PORTFOLIO, MY_BACKGROUND (identity for outreach drafts),
CRUNCHBASE_API_KEY (unused by the pipeline), ALLOWED_HOSTS / PORT (api.py).

## What Not to Break

- Do not re-add the cold-outreach pipeline integration, Gmail drafting, or
  Apollo/Hunter API dependencies -- all intentionally removed.
- --scrape-only and --fresh must skip ALL Claude API calls entirely.
- Do not hardcode personal info; use os.getenv() only.
- Do not commit .env, token.json, credentials.json, or *.xlsx files.
- No emojis in code, output, or docs.
- api.py security model: per-request keys never logged or stored, unguessable
  run tokens, TTL expiry, rate limiting. Do not weaken it.
