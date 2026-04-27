# EarlyBird

> Apply before everyone else does.

EarlyBird is a Python-based job search automation pipeline built for students and early-career engineers who want to maximize their chances by applying to roles as soon as they are posted, before listings hit mass job boards and inboxes flood with applicants.

Most job seekers find openings on LinkedIn or Indeed, where a posting may already be 2-3 days old and have hundreds of applicants. EarlyBird goes directly to the source: polling company ATS systems (Greenhouse, Lever), VC portfolio job boards, and a hardcoded watchlist of 80+ target companies to surface roles within hours of posting.

Run it every morning. Open the Excel output. Apply first.

---

## Why EarlyBird

Timing is one of the most underrated factors in internship and new grad hiring. Recruiters often review applications in the order they arrive, and many roles are filled before they even trend on LinkedIn. EarlyBird is built around that reality.

- Finds jobs hours before they reach LinkedIn or Indeed
- Filters by your target geography and remote preferences
- Scores each role by skill match so you triage smarter
- Researches outreach contacts per company and drafts personalized emails
- Sends emails via Gmail with randomized delays
- Logs everything to a color-coded Excel tracker with direct apply links
- Runs automatically every morning via Task Scheduler or cron

---

## What It Does

1. Scrapes job postings from Greenhouse ATS, Lever ATS, LinkedIn, Indeed, and a direct watchlist of 80+ companies
2. Pulls from VC portfolio boards: YC Work at a Startup, a16z, First Round Capital, Contrary Capital, Dreamit Ventures
3. Scrapes staffing firms: Robert Half, Theoris, TEKsystems, Apex Systems, Insight Global
4. Filters by your configured target locations and remote preferences
5. Scores each listing against your skill set using keyword overlap
6. Deduplicates across sources so the same role does not appear twice
7. Flags anything posted under 6 hours ago as URGENT (red row in Excel)
8. Researches outreach contacts per company via web search, ranked by leverage (alumni, recruiter, engineer)
9. Drafts personalized outreach emails and LinkedIn messages using the Claude API
10. Sends emails via Gmail API with randomized delays between sends
11. Outputs a color-coded Excel file with role, company, location, match score, apply link, posting age, and outreach status

---

## Stack

- Python 3.10+
- [JobSpy](https://github.com/cullenwatson/JobSpy) for LinkedIn and Indeed scraping
- Anthropic Claude API for outreach message drafting
- Gmail API for automated email sending
- openpyxl for Excel output
- BeautifulSoup for ATS and careers page scraping
- Greenhouse and Lever public APIs for direct company job polling
- python-dotenv for environment variable management

---

## Setup

### 1. Clone the repo

```bash
git clone https://github.com/anishkask/EarlyBird.git
cd EarlyBird
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set up environment variables

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

```
ANTHROPIC_API_KEY=        # get from console.anthropic.com
GMAIL_ADDRESS=            # your Gmail address
YOUR_NAME=                # your full name
YOUR_SCHOOL=              # your university (used in outreach messages)
YOUR_LINKEDIN=            # linkedin.com/in/yourhandle
YOUR_PORTFOLIO=           # yoursite.com (optional)
YOUR_GITHUB=              # github.com/yourusername
MY_BACKGROUND=            # 1-2 sentence summary of your skills and experience
EMAIL_DELAY_MIN=180       # minimum seconds between emails (default 3 min)
EMAIL_DELAY_MAX=300       # maximum seconds between emails (default 5 min)
```

### 4. Set up Gmail API

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project
3. Enable the Gmail API
4. Go to Credentials and create an OAuth 2.0 Client ID (Desktop App)
5. Download the credentials JSON and save it as `credentials.json` in the project root
6. On first run, a browser window will open asking you to authorize access. Complete the flow once and `token.json` will be saved automatically for future runs.

### 5. Configure your search

Open `job_pipeline_full.py` and update the configuration block at the top:

```python
# Your skills -- used for match scoring
MY_SKILLS = ["Python", "TypeScript", "React", "FastAPI", "PostgreSQL",
             "REST APIs", "Docker", "SQL", "RAG pipelines"]

# Target locations -- add your own city, state, or region
TARGET_LOCATIONS = ["Your City", "Your State", "Remote", "United States"]

# Role keywords -- what kinds of roles to surface
ROLE_KEYWORDS = ["software engineer", "software developer", "backend", "frontend",
                 "full stack", "AI", "ML", "data engineer", "platform engineer"]
```

To add companies to the direct ATS watchlist, find the `WATCHLIST` dictionary and add entries:

```python
"company-greenhouse-token": "greenhouse",
"company-lever-slug": "lever",
```

### 6. Run it

```bash
python job_pipeline_full.py
```

To limit to jobs posted in the last 24 hours:

```bash
python job_pipeline_full.py --hours 24
```

To test scraping only without spending API credits:

```bash
python job_pipeline_full.py --scrape-only
```

To run without sending emails:

```bash
python job_pipeline_full.py --no-email
```

---

## Automating Daily Runs

### Windows (Task Scheduler)

1. Create `run_earlybird.bat` in the project folder:

```bat
@echo off
cd C:\path\to\EarlyBird
python job_pipeline_full.py >> logs\pipeline_log.txt 2>&1
```

2. Create a `logs\` folder in the project directory
3. Open Task Scheduler and click "Create Basic Task"
4. Set trigger to Daily at your preferred time (8 AM recommended)
5. Set action to run `run_earlybird.bat`
6. Under Conditions, check "Wake the computer to run this task" if your machine sleeps overnight

### Mac / Linux (cron)

```bash
crontab -e
```

Add:

```
0 8 * * * cd /path/to/EarlyBird && python job_pipeline_full.py >> logs/pipeline_log.txt 2>&1
```

---

## Output

Each run generates a timestamped Excel file (e.g. `job_leads_2026-04-14_08-00.xlsx`) with two tabs:

**Jobs tab**

- Role title, company, location, source, hours since posted
- Direct apply link
- Match score (0-100 based on skill overlap)
- Color coding: red = URGENT (under 6h), green = fresh (under 24h), yellow = recent (24-72h)

**Outreach tab**

- Contact name, title, company, LinkedIn URL
- Leverage score (alumni ranked highest, then recruiter, then engineer)
- Drafted email subject and body
- Drafted LinkedIn message (under 280 characters)
- Send status

---

## Important Notes

- **LinkedIn and Indeed** are scraped via JobSpy. Scraping these platforms may violate their terms of service. Use responsibly and do not run more than once per day.
- **ZipRecruiter** blocks automated access and is excluded from this pipeline.
- **LinkedIn outreach** cannot be automated without risking account restriction. The script drafts LinkedIn messages for you to send manually.
- **Gmail sending** uses your real Gmail account. Delays are randomized to reduce spam filter risk. Do not lower `EMAIL_DELAY_MIN` below 60 seconds.
- **Never commit** `.env`, `token.json`, `credentials.json`, or any `*.xlsx` output files. All are included in `.gitignore`.

---

## .gitignore

Your `.gitignore` should include at minimum:

```
.env
token.json
credentials.json
credentials.json.json
*.xlsx
*.xls
__pycache__/
.mypy_cache/
.venv/
venv/
logs/
*.pyc
.DS_Store
```

---

## Roadmap

- [ ] Slack or email digest summarizing each morning's run
- [ ] Browser extension to one-click add a company to the watchlist
- [ ] Resume-to-job matching using embeddings instead of keyword overlap
- [ ] Dynamic company sourcing from Crunchbase API based on recent funding rounds
- [ ] Handshake integration for student-exclusive postings

---

## Contributing

Pull requests welcome. If you add a new ATS source, job board, or VC portfolio board, open a PR with the source added to the appropriate scraper and a note in this README.

---

## License

MIT