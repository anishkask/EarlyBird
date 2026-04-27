# Cold Outreach Guide

> Reach out directly to startup founders and CEOs, bypassing traditional applications.

---

## Table of Contents

1. [Quick Start (5 minutes)](#quick-start)
2. [How It Works](#how-it-works)
3. [Setup & Configuration](#setup--configuration)
4. [Running the Pipeline](#running-the-pipeline)
5. [Excel Tracker Guide](#excel-tracker-guide)
6. [Email Best Practices](#email-best-practices)
7. [Troubleshooting](#troubleshooting)
8. [API Quotas & Limits](#api-quotas--limits)
9. [Advanced Configuration](#advanced-configuration)

---

## Quick Start

### 1. Get Apollo.io API Key (2 min)

1. Go to [apollo.io/settings/integrations](https://app.apollo.io/settings/integrations)
2. Copy your API key
3. Add to `.env`:
   ```bash
   APOLLO_API_KEY=your_key_here
   ```

### 2. Test It (2 min)

```bash
python job_pipeline_full.py --test-cold-outreach
```

Output example:
```
============================================================
  Cold Outreach Pipeline
  Mode: TEST
============================================================

1. SCRAPING VC PORTFOLIOS

    Scraping Robin Hood Ventures...
      Found 3 companies (after dedup)

  Total companies found: 3

2. ENRICHING WITH APOLLO.IO
...
```

Check the output for:
- ✅ Companies found
- ✅ Contacts enriched from Apollo
- ✅ Email drafts generated
- ✅ Excel sheet created

### 3. Run Normally (1 min)

```bash
python job_pipeline_full.py --hours 24
```

A new "Cold Outreach" sheet will appear in the Excel output.

### 4. Send Cold Emails (10-30 min)

Open the Excel file and:
1. Go to "Cold Outreach" sheet
2. For each row:
   - Review email draft (column L) — click to see full text
   - Click LinkedIn URL (column G) to verify person exists
   - Click Gmail Link (column M) to open draft in Gmail
   - Review/personalize, send
   - Mark "Outreach Status" as "Sent"
   - Track response in "Response Date" and "Notes"

---

## How It Works

### Daily Pipeline

```
[Scrape VC Portfolios] 
        ↓
[Find New Companies] (seen_companies.json dedup)
        ↓
[Call Apollo API] (contact enrichment + caching)
        ↓
[Generate Emails] (Claude API + storage)
        ↓
[Optionally Create Gmail Drafts]
        ↓
[Write Excel Tab] + [Update Dedup DB]
```

### Data Files

```
data/
├── seen_companies.json         # {companies: [...]}  — prevents repeats
├── apollo_cache.json           # Cached API responses — saves quota
└── drafts/
    ├── company-name-1.txt      # Full email draft text
    ├── company-name-2.txt
    └── ...
```

### VC Portfolios Scraped

- **Robin Hood Ventures** — Philadelphia tech VCs, 500+ companies
- **Osage Venture Partners** — Midwest + East Coast focus
- **DreamIT (SecureTech)** — Hardware + security focus
- **DreamIT (HealthTech)** — Health tech startups

---

## Setup & Configuration

### Prerequisites

✅ Python 3.10+
✅ `anthropic` package (Claude API) — already in `requirements.txt`
✅ `requests` + `beautifulsoup4` for scraping — already installed
✅ `openpyxl` for Excel — already installed

### Environment Variables

**Required:**
```bash
ANTHROPIC_API_KEY=sk-ant-...    # From anthropic.com
APOLLO_API_KEY=...               # From apollo.io/settings
```

**Optional:**
```bash
YOUR_NAME=Anishka Kakade              # Used in email signature
YOUR_EMAIL=anishka@...                # Used in email signature
YOUR_SCHOOL=Temple University         # Used in email signature
```

### Configuration Options

Edit `run_cold_outreach()` call in `job_pipeline_full.py` to customize:

```python
config = {
    "cold_outreach_enabled": True,           # Enable/disable feature
    "apollo_api_key": os.getenv("APOLLO_API_KEY", ""),
    "create_gmail_drafts": not args.no_email,
    "cold_outreach_max_per_day": 10,         # Cap contacts per run
    "cold_outreach_min_employees": 1,        # Skip smaller companies
    "cold_outreach_max_employees": 75,       # Skip larger companies
}
```

---

## Running the Pipeline

### Test Mode (Dry-Run)

```bash
python job_pipeline_full.py --test-cold-outreach
```

Behavior:
- Scrapes only Robin Hood Ventures (first VC source)
- Limits to first 2 companies for Apollo enrichment
- Generates email drafts for those 2
- Writes to "Cold Outreach TEST" sheet (doesn't touch production)
- **Does NOT update** `data/seen_companies.json` (dry-run)
- Prints detailed summary to stdout

When to use: Verify API keys are working, check email quality, test new VC sources.

### Production Mode (Daily)

```bash
python job_pipeline_full.py --hours 24
```

Behavior:
- Scrapes all 4 VC portfolio pages
- Enriches up to 10 new companies per day (configurable)
- Generates email drafts for all new contacts
- Creates Gmail drafts if `--no-email` flag not used
- Writes to "Cold Outreach" sheet (overwrites previous)
- **Updates** `data/seen_companies.json` to prevent repeats
- Logs summary to stdout and `logs/pipeline_log.txt` (if scheduler)

### Skip Cold Outreach

```bash
python job_pipeline_full.py --no-cold-outreach
```

Useful for: Testing just the job board pipeline, saving API quota.

### Combined with Job Pipeline

```bash
python job_pipeline_full.py --hours 24 --no-email
```

Runs both job board scraping AND cold outreach, but:
- Skips Gmail setup (no Gmail drafts created)
- Still generates Claude email drafts
- Useful for CI/CD environments without Gmail credentials

---

## Excel Tracker Guide

The "Cold Outreach" sheet has 16 columns:

| # | Column | Format | Purpose |
|---|--------|--------|---------|
| A | # | Auto-increment | Row number |
| B | Company Name | Text | Startup name |
| C | Contact Name | Text | First Last |
| D | Title | Text | CEO, Founder, CTO, etc |
| E | Email | Text (yellow if estimated) | Contact email |
| F | Email Status | Text | VERIFIED / ESTIMATED / NOT FOUND |
| G | LinkedIn URL | Hyperlink | Profile or search URL |
| H | Company Website | Hyperlink | To company site |
| I | Employees | Number | ~estimated headcount |
| J | VC Source | Text | Which portfolio page |
| K | Date Added | Date | YYYY-MM-DD |
| L | Email Draft (Preview) | Text (truncated) | First 300 chars, click to read full |
| M | Gmail Link | Hyperlink | Opens Gmail draft (if created) |
| N | Outreach Status | Dropdown∗ | Not Sent / Sent / Replied / Meeting Booked / Pass / No Response |
| O | Response Date | Date (user fillable) | When they replied |
| P | Notes | Text (user fillable) | Follow-up notes |

∗ Dropdown is pre-configured via openpyxl data validation.

### Color Coding

- **Yellow** (Column E): Email is ESTIMATED — verify before sending
- **White/Light Gray**: Alternating rows for readability

### How to Use It

1. **Review Draft**: In column L, see preview of email. Click cell → double-click to see full text in edit box. For full readable text, open `data/drafts/<company-slug>.txt`.

2. **Verify Contact**: Click LinkedIn URL (column G). Confirm it's the right person.

3. **Send Email**: 
   - Option A: Click Gmail Link (column M) → compose → verify → send
   - Option B: Copy draft text from column L → compose in Gmail manually
   - Option C: Open full draft from `data/drafts/<company-slug>.txt`

4. **Update Status**: After sending, change column N from "Not Sent" to "Sent".

5. **Track Response**: Fill in "Response Date" (column O) and any notes (column P).

6. **Filter & Pivot**: Use Excel's AutoFilter to slice by:
   - Email Status (find estimated emails to verify)
   - VC Source (which portfolio found them)
   - Outreach Status (track your progress)

---

## Email Best Practices

### The Cold Email Formula

Your email should have 3 parts:

1. **Hook** (1 sentence)
   - Something specific about the company
   - Why you're excited about them
   - NOT flattery ("your product is amazing!")
   - YES company insight ("Your API for X is solving the bottleneck that Y companies face")

2. **About You** (2-3 sentences)
   - Why you're relevant
   - Relevant projects/experience
   - Link to proof (portfolio, GitHub)

3. **Ask** (1 sentence)
   - Specific ask, not vague
   - NOT "can we grab coffee?"
   - YES "I'm interested in contributing to [specific area]. Would a 15-minute call work?"

### Examples

**❌ Bad:**
```
Hi [First Name],

I'm a Temple University CS student interested in joining [Company].
Your product is amazing and I think I'd be a great fit.

Let me know if you'd like to chat!

Best,
Anishka
```

**✅ Good:**
```
Hi [First Name],

I noticed [Company] is using [specific architecture/approach] for [problem].
I built a similar system for [your project] using [tech stack], and learned [insight].

Given your focus on [specific area], I think I could help with [specific contribution].
Would you have 15 minutes next week to discuss?

Thanks,
Anishka Kakade
anishkakade.vercel.app | anishka.s.kakade@gmail.com
```

### Do's & Don'ts

**DO:**
- Personalize the opening (mention something from their website)
- Link to your portfolio/GitHub (proof of work)
- Keep it short (3-4 sentences max)
- Use their first name
- Be specific about what you can offer
- Ask for a specific time/duration

**DON'T:**
- Use generic salutations ("To Whom It May Concern")
- Attach resumes (send only if asked)
- Use em-dashes or fancy formatting
- Mention that you're "reaching out" or "thinking about applying"
- Ask vague questions like "Is there an internship?"
- Exceed 5 sentences

### The Claude Email Generator

EarlyBird's Cold Outreach module **auto-generates personalized emails** via Claude API using:
- Your background (CS student at Temple, graduating Dec 2026)
- Your technical stack
- Your key projects
- Company info from Apollo (size, industry, website)
- VC source context

**The generated email is a template.** Always:
1. Read it fully
2. Customize the hook (add specific insight about their company)
3. Verify all facts are correct
4. Send!

If a generated email feels off, you can rewrite it based on the structure above.

---

## Troubleshooting

### No Companies Found

**Symptom:**
```
Total companies found: 0
```

**Fixes:**
1. Check internet connection
2. Verify VC portfolio pages are accessible (visit in browser)
3. Check if pages have changed HTML structure (DreamIT pages are fragile)
4. Try with `--test-cold-outreach` to see detailed errors

### Apollo API Key Invalid

**Symptom:**
```
[APOLLO ERROR] 401 for Company Name
```

**Fixes:**
1. Verify `APOLLO_API_KEY` in `.env` is correct (no spaces/quotes)
2. Check key hasn't expired in Apollo dashboard
3. Verify account isn't suspended (check apollo.io/app)

### Rate Limited by Apollo

**Symptom:**
```
[APOLLO RATE LIMITED] Company Name
```

**Fixes:**
1. Apollo free tier: 50 requests/day
2. EarlyBird caps to 10 per day — you're safe!
3. Check if you ran multiple times today
4. Wait 24 hours and try again
5. (Advanced) Upgrade Apollo plan

### Email Drafts Not Created

**Symptom:**
```
Email Draft (Preview) column is empty
```

**Fixes:**
1. Check `ANTHROPIC_API_KEY` in `.env`
2. Verify key is valid at anthropic.com
3. Check Claude API quota/billing
4. Try with `--test-cold-outreach` to see detailed errors
5. Check `logs/pipeline_log.txt` for exceptions

### Gmail Drafts Not Created

**Symptom:**
```
Gmail Link column is empty (column M)
```

**Fixes:**
1. Run with `--no-email` to skip Gmail entirely
2. Verify `credentials.json` exists in project folder
3. Verify `token.json` exists (first run creates it)
4. Try re-authenticating Gmail:
   ```bash
   rm token.json
   python job_pipeline_full.py  # Will prompt to login
   ```

### Duplicate Contacts Appearing

**Symptom:**
```
Same company/email in Cold Outreach sheet twice
```

**Fixes:**
1. `data/seen_companies.json` might be corrupted
2. Try deleting it (will re-process all companies next run)
3. Check if company name differs slightly (e.g., "Company" vs "Company Inc.")

### Estimated Emails Are Wrong

**Symptom:**
```
Email highlighted yellow, but format is incorrect (acme@example.com not right)
```

**Fixes:**
1. Apollo API might not have correct domain
2. Always verify estimated emails before sending
3. Check actual company website for email format examples
4. Reach out via LinkedIn if uncertain

---

## API Quotas & Limits

### Apollo.io

| Plan | Requests/Day | Cost |
|------|--------------|------|
| Free | 50 | $0 |
| Growth | 500 | $500/mo |
| Pro | Unlimited | $2000/mo |

**EarlyBird caps to 10 per day** — safe margin on free tier.

**Cache strategy:** All Apollo responses cached in `data/apollo_cache.json`:
- Company names are cached, so re-running doesn't re-fetch
- Delete cache to force refresh: `rm data/apollo_cache.json`

### Claude API (Anthropic)

Pay-as-you-go (no quotas):
- ~$0.01 per email draft generated
- Daily cost: ~$0.10 (10 drafts)
- Monthly estimate: ~$3

### Greenhouse/Lever APIs

Unlimited (public, rate limit is loose).

---

## Advanced Configuration

### Add New VC Portfolios

Edit `cold_outreach.py`, update `VC_SOURCES`:

```python
VC_SOURCES = [
    {
        "name": "Your VC Name",
        "url": "https://vc-website.com/portfolio/",
    },
    # ... existing sources
]
```

Then scraping logic will automatically include it. If HTML structure is different, you may need to update `scrape_vc_portfolio()` extraction logic.

### Change Max Employees Filter

Edit the `config` dict in `job_pipeline_full.py`:

```python
"cold_outreach_max_employees": 100,  # Increase from 75 to 100
```

Companies larger than this will be skipped.

### Skip Gmail Drafts

Run with `--no-email`:

```bash
python job_pipeline_full.py --no-email --hours 24
```

Email drafts still generated, but no Gmail drafts created.

### Dry-Run Mode (Test Always)

Run with `--test-cold-outreach`:

```bash
python job_pipeline_full.py --test-cold-outreach
```

Test mode:
- Doesn't update `data/seen_companies.json`
- Writes to "Cold Outreach TEST" sheet (doesn't overwrite production)
- Small scope (1 VC, 2 companies)

Use to verify API keys, test new VC sources, verify email quality before production run.

### Scheduling

#### Windows Task Scheduler

Create `run_earlybird.bat`:

```batch
@echo off
cd C:\Users\YourName\Downloads\earlybird
python job_pipeline_full.py --hours 24 >> logs\cold_outreach.log 2>&1
```

Create task:
1. Task Scheduler → Create Basic Task
2. Trigger: Daily, 8 AM
3. Action: Run `run_earlybird.bat`
4. Conditions: Wake to run, Network available

#### Mac / Linux (cron)

Edit crontab:

```bash
crontab -e
```

Add:

```
0 8 * * * cd /home/user/earlybird && python job_pipeline_full.py --hours 24 >> logs/cold_outreach.log 2>&1
```

---

## Next Steps

1. ✅ Get Apollo API key and add to `.env`
2. ✅ Run `python job_pipeline_full.py --test-cold-outreach`
3. ✅ Review "Cold Outreach TEST" sheet, verify email quality
4. ✅ Run `python job_pipeline_full.py --hours 24` for production
5. ✅ Open Excel, read drafts, send emails
6. ✅ Schedule daily via Task Scheduler or cron
7. ✅ Track responses in Excel, iterate on outreach

---

## Questions?

Check [cold_outreach.py](./cold_outreach.py) for implementation details.

Check [job_pipeline_full.py](./job_pipeline_full.py) integration (lines 801-843).

---

**Last Updated:** 2026-04-16
