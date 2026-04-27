# EarlyBird

> Apply before everyone else does.

EarlyBird is a job search automation pipeline for students and early-career engineers who want to apply to roles within hours of posting — before listings hit mass job boards and inboxes flood with applicants.

It polls company ATS systems (Greenhouse, Lever), runs live web searches for campus recruiters, drafts personalized outreach messages, and outputs a color-coded Excel tracker. There is also a React dashboard for viewing results.

---

## Features

- Scrapes Greenhouse, Lever, LinkedIn, Indeed, Wellfound within hours of posting
- Filters by US location and remote — no international noise
- Scores each role 0-100 by keyword match against your background
- Deduplicates across sources so the same role never appears twice
- Uses Claude API with live web search to find real campus recruiters by name
- Drafts personalized LinkedIn messages and emails per contact
- Generates a color-coded Excel file: green = posted under 6h, blue = under 24h, yellow = under 48h
- Cold outreach tab: researches campus recruiters at target companies even with no open roles
- Apollo Lookup links and Company Domain columns for email pattern discovery
- Prints tool-use block count to confirm web search is actually running

---

## Dashboard (React)

A React + Vite frontend is included in `earlybird-ui/` and deployed to Vercel.

It includes:
- Dashboard with stat cards, fresh job highlights, outreach to-do list, source breakdown
- Job Leads table with search, filter, and color-coded rows
- Outreach panel with LinkedIn message and email draft per contact
- Cold Outreach table with Apollo links and editable email pattern fields
- Settings page for profile, pipeline config, and API key status

**Live:** [earlybird-ui.vercel.app](https://earlybird-ui.vercel.app)

To run locally:
```bash
cd earlybird-ui
npm install
npm run dev
```

---

## Quickstart

### 1. Clone

```bash
git clone https://github.com/anishkask/EarlyBird.git
cd EarlyBird
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment

```bash
cp .env.example .env
```

Fill in `.env`:

```
ANTHROPIC_API_KEY=sk-ant-...
YOUR_NAME=Your Name
YOUR_EMAIL=you@email.com
YOUR_SCHOOL=Your University
YOUR_LINKEDIN=https://linkedin.com/in/yourhandle
MY_BACKGROUND=Brief summary of your skills and experience
```

### 4. Run

```bash
# Standard run — last 72 hours
python job_pipeline_full.py

# Fresh only
python job_pipeline_full.py --hours 24

# Include cold outreach (campus recruiter research)
python job_pipeline_full.py --hours 72 --cold-outreach

# Skip email sending
python job_pipeline_full.py --no-email

# Scrape only, skip all Claude API calls
python job_pipeline_full.py --scrape-only
```

---

## How It Works

1. Scrapes Greenhouse and Lever ATS boards using their public APIs
2. Aggregates LinkedIn and Indeed via JobSpy
3. Filters to US/remote only, deduplicates by company + title
4. For each fresh job (under 96h), calls Claude API with web search enabled to find real recruiter contacts
5. Drafts a LinkedIn message and email per contact using your background
6. Optionally runs cold outreach: searches for campus recruiters at all companies in your watchlist, even those with no current openings
7. Writes everything to a timestamped Excel file with three tabs: Jobs, Outreach, Cold Outreach

---

## Excel Output

**Jobs tab** — color-coded by posting age, with apply links and match scores

**Outreach tab** — contact name, title, LinkedIn URL, drafted message and email, plus:
- Company Domain (extracted from apply link)
- Apollo Lookup (clickable link to search contacts by domain)
- Email Pattern (blank column for manual entry)

**Cold Outreach tab** — same structure, for proactive outreach at companies with no current openings

---

## Web Search Confirmation

Every run prints:

```
Tool-use blocks in Claude API responses: N
```

If N is 0, web search is not being invoked. If N > 0, real-time recruiter search is working. Each web search call uses approximately 10k tokens, so the free API tier (30k tokens/min) processes about 3 companies per minute.

---

## Automating Daily Runs

### Windows (Task Scheduler)

Create `run_earlybird.bat`:

```bat
@echo off
cd C:\path\to\EarlyBird
python job_pipeline_full.py --hours 24 >> logs\pipeline_log.txt 2>&1
```

Set a daily trigger at 8 AM in Task Scheduler.

### Mac / Linux (cron)

```bash
crontab -e
# Add:
0 8 * * * cd /path/to/EarlyBird && python job_pipeline_full.py --hours 24 >> logs/pipeline_log.txt 2>&1
```

---

## Stack

**Pipeline**
- Python 3.10+
- [Anthropic SDK](https://github.com/anthropics/anthropic-sdk-python) with `web_search_20250305` tool
- [JobSpy](https://github.com/cullenwatson/JobSpy) for LinkedIn and Indeed
- openpyxl, BeautifulSoup, requests, python-dotenv

**Dashboard**
- React + Vite
- Tailwind CSS v3
- Deployed on Vercel

---

## Notes

- LinkedIn and Indeed scraping via JobSpy may conflict with their terms of service. Run at most once per day.
- Never commit `.env`, `token.json`, `credentials.json`, or `*.xlsx` files — all are in `.gitignore`.
- The `--cold-outreach` flag spaces API calls 22 seconds apart to avoid rate limits. For 10 companies expect about 4 minutes.

---

## Roadmap

- Connect dashboard to live pipeline output (FastAPI backend)
- Resume-to-job matching using embeddings
- Slack digest summarizing each morning's run
- Handshake integration for student-exclusive postings

---

## License

MIT
