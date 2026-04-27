# Cold Outreach Examples & Output Reference

## Example Terminal Output

### Test Mode

```bash
$ python job_pipeline_full.py --test-cold-outreach

============================================================
  Job Pipeline — 2026-04-16 08:23
  Finding jobs posted within 72 hours
============================================================

Scraping Greenhouse ATS (startups/tech)...
  5 internships found (raw)
...
(Job board scraping output)
...

============================================================
  Cold Outreach Pipeline
  Mode: TEST
============================================================

1. SCRAPING VC PORTFOLIOS

    Scraping Robin Hood Ventures...
      Found 5 companies (after dedup)

  Total companies found: 5

2. ENRICHING WITH APOLLO.IO

    [CACHE] Acme Tech
    [API] BuildCo
      → Sarah Johnson (CEO)
    [API] DataFlow Inc
      → Not contact found
    [API] EchoAI
      → Mike Chen (Founder)
    [API] FusionLabs
      → Skipped: 120 employees (threshold: 75)

  Enriched contacts: 3

3. DEDUPLICATING

    [DEDUP] Acme Tech already processed
    [NEW] BuildCo — Sarah Johnson
    [NEW] EchoAI — Mike Chen

  New unique contacts: 2

4. GENERATING EMAIL DRAFTS

    Drafting email for BuildCo...
      ✓ Saved to buildco.txt
    Drafting email for EchoAI...
      ✓ Saved to echoai.txt

5. WRITING COLD OUTREACH TAB

  Sheet: Cold Outreach TEST

6. [TEST MODE] Skipping deduplication database update

============================================================
  COLD OUTREACH COMPLETE
  2 new contacts found and drafted
============================================================

============================================================
  COMPLETE
  12 jobs | 3 fresh | 8 outreach drafted
  2 cold outreach contacts drafted
  File: job_leads_2026-04-16_08-23.xlsx
...
```

### Production Mode (Daily Run)

```bash
$ python job_pipeline_full.py --hours 24

[Job board scraping output...]

============================================================
  Cold Outreach Pipeline
  Mode: PRODUCTION
============================================================

1. SCRAPING VC PORTFOLIOS

    Scraping Robin Hood Ventures...
      Found 8 companies (after dedup)
    Scraping Osage Venture Partners...
      Found 6 companies (after dedup)
    Scraping DreamIT (SecureTech)...
      Found 4 companies (after dedup)
    Scraping DreamIT (HealthTech)...
      Found 5 companies (after dedup)

  Total companies found: 23

2. ENRICHING WITH APOLLO.IO

    [CACHE] Company A
    [API] Company B
      → Sarah Johnson (CEO)
    [API] Company C
      → Not contact found
    ...
    [APOLLO RATE LIMITED] Company X
    ...

  Enriched contacts: 18

3. DEDUPLICATING

    [DEDUP] Acme Tech already processed
    [DEDUP] jane@buildco.com already in outreach sheet
    [NEW] Company D — Contact
    [NEW] Company E — Contact
    ...

  New unique contacts: 8

[CAP] Limiting to 10 per day (found 12)

4. GENERATING EMAIL DRAFTS

    Drafting email for Company D...
      ✓ Saved to company-d.txt
    ...

5. CREATING GMAIL DRAFTS

    ✓ Company D
    ✓ Company E
    ...

6. WRITING COLD OUTREACH TAB

  Sheet: Cold Outreach

7. UPDATING DEDUPLICATION DATABASE

  Saved 8 company names

============================================================
  COLD OUTREACH COMPLETE
  8 new contacts found and drafted
  7 Gmail drafts created
============================================================
```

---

## Example Excel Output

### Cold Outreach Sheet

| # | Company Name | Contact Name | Title | Email | Email Status | LinkedIn URL | Company Website | Employees | VC Source | Date Added | Email Draft | Gmail Link | Outreach Status | Response Date | Notes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | BuildCo | Sarah Johnson | CEO | sarah@buildco.io | VERIFIED | [View Profile] | [buildco.io] | 12 | Robin Hood Ventures | 2026-04-16 | Subject: Exploring Opportunity at BuildCo ... | [Open Draft] | Not Sent | | |
| 2 | EchoAI | Mike Chen | Founder | m.chen@echoai.com | ESTIMATED | [View Profile] | [echoai.com] | 8 | Robin Hood Ventures | 2026-04-16 | Subject: Your RAG Infrastructure Approach ... | [Open Draft] | Not Sent | | |
| 3 | FusionLabs | Alex Patel | CTO | alex.patel@fusion... | VERIFIED | [View Profile] | [fusionlabs.dev] | 15 | Osage Venture Partners | 2026-04-16 | Subject: Interest in Platform Engineering ... | [Open Draft] | Not Sent | | |

---

## Example Email Drafts

### Draft 1: BuildCo

```
Subject: Interest in Contributing to BuildCo's Infrastructure

Hi Sarah,

I noticed BuildCo is building infrastructure for AI model lifecycle management.
I spent the last few months building a semantic code search pipeline using
ChromaDB, FastAPI, and React, and learned a lot about making complex AI
pipelines usable.

Given your focus on developer experience with AI, I'd love to chat about
how I could contribute. Would 15 minutes next week work?

Thanks,
Anishka Kakade
anishkakade.vercel.app | anishka.s.kakade@gmail.com
```

### Draft 2: EchoAI

```
Subject: Your RAG Infrastructure Approach — Let's Talk

Hi Mike,

I came across EchoAI while researching RAG implementations at early-stage
companies. Your approach to embedding lifecycle management caught my eye
because it solves the exact bottleneck I hit building semantic search.

I'm a senior CS student at Temple graduating in December 2026, and I've
been building full-stack AI systems: Python backends, React frontends,
working with vector DBs and APIs. I'd be excited to help you scale.

Could we grab 20 minutes sometime this week?

Thanks,
Anishka Kakade
anishkakade.vercel.app | anishka.s.kakade@gmail.com
```

---

## Data Files Created

### data/seen_companies.json

```json
{
  "companies": [
    "acme tech",
    "buildco",
    "dataflow inc",
    "echoai",
    "fusionlabs",
    "glydways",
    "hypothesis ai"
  ]
}
```

### data/apollo_cache.json

```json
{
  "BuildCo": {
    "first_name": "Sarah",
    "last_name": "Johnson",
    "title": "CEO",
    "email": "sarah@buildco.io",
    "linkedin_url": "https://linkedin.com/in/sarahjohnson",
    "organization_name": "BuildCo",
    "organization_website": "https://buildco.io",
    "employees": 12,
    "vc_source": "Robin Hood Ventures",
    "website": "https://buildco.io"
  },
  "EchoAI": {
    "first_name": "Mike",
    "last_name": "Chen",
    "title": "Founder",
    "email": null,
    "linkedin_url": "https://linkedin.com/in/mikechenai",
    "organization_name": "EchoAI",
    "organization_website": "https://echoai.com",
    "employees": 8,
    "vc_source": "Robin Hood Ventures",
    "website": "https://echoai.com"
  }
}
```

### data/drafts/buildco.txt

```
Subject: Interest in Contributing to BuildCo's Infrastructure

Hi Sarah,

I noticed BuildCo is building infrastructure for AI model lifecycle management.
I spent the last few months building a semantic code search pipeline using
ChromaDB, FastAPI, and React, and learned a lot about making complex AI
pipelines usable.

Given your focus on developer experience with AI, I'd love to chat about
how I could contribute. Would 15 minutes next week work?

Thanks,
Anishka Kakade
anishkakade.vercel.app | anishka.s.kakade@gmail.com
```

---

## Email Status Legend

### Email Status Codes

| Status | Meaning | What to Do |
|--------|---------|-----------|
| VERIFIED | Email returned by Apollo API (high confidence) | Can send directly |
| ESTIMATED | Email guessed from domain (medium confidence) | Verify before sending; check company website for email format |
| NOT FOUND | Apollo had no contact or email (low confidence) | Reach out via LinkedIn instead of email |

### Color Coding in Excel

- **Yellow highlight** (Column E): Email is ESTIMATED — extra caution
- **Normal text**: Email is VERIFIED or NOT FOUND

---

## Outreach Status Workflow

```
Start: "Not Sent"
   ↓
[You send email]
   ↓
"Sent"
   ↓
[Waiting for response...]
   ↓
[They reply] → "Replied"
   ↓
[Schedule call] → "Meeting Booked"
   ↓
[Had call, not moving forward] → "Pass"
   ↓
[No response after follow-up] → "No Response"
```

---

## Common Scenarios

### Scenario 1: Verify an Estimated Email

**Found:** Email is yellow (ESTIMATED)

**Steps:**
1. Click LinkedIn URL (Column G) → verify person exists
2. Visit company website, look for "Team" or "About" page
3. Check if email follows expected pattern
4. Ask trusted friend who knows company
5. If confident → send; if not → reach out via LinkedIn instead

### Scenario 2: Email Doesn't Exist or Verified Wrong

**Error:** Gmail bounce or "address not found"

**Steps:**
1. Delete draft or mark "No Response" after 3 days
2. Next run, that company won't be processed again (cached)
3. To re-process from scratch: 
   ```bash
   # Option A: Remove from seen_companies.json manually
   # Option B: Try finding them on LinkedIn via search URL
   ```

### Scenario 3: Got a Reply!

**Scenario:** Contact replied to cold email

**Steps:**
1. Reply thoughtfully (use the original email context)
2. Update Excel:
   - "Outreach Status" → "Replied"
   - "Response Date" → actual date they replied
   - "Notes" → next steps (e.g., "Mentioned open eng role, first call Tues")
3. Track further communication in Notes column
4. Once meeting is booked → mark "Meeting Booked"

### Scenario 4: You Want to Manually Edit an Email Draft

**Scenario:** Generated email isn't quite right

**Steps:**
1. Open `data/drafts/company-slug.txt`
2. Edit the TEXT FILE (not Excel)
3. Save as `data/drafts/company-slug.txt` (overwrite)
4. Re-open Excel, copy updated text
5. (The Excel preview won't auto-update; that's OK)

### Scenario 5: You Want to Re-Check a Company

**Scenario:** You want to re-process "BuildCo" (maybe for a different contact)

**Steps:**
1. Remove from `data/seen_companies.json`:
   ```json
   {
     "companies": [
       "acme tech",
       // "buildco",   ← comment out or delete
       "dataflow inc"
     ]
   }
   ```
2. Next run will re-fetch BuildCo from Apollo API
3. Or delete `data/apollo_cache.json` to force re-fetch everything

---

## Excel Pivot Tables

### Track Outreach by Status

**Pivot Table Setup:**
1. Select data in Cold Outreach sheet
2. Insert → Pivot Table
3. Rows: Outreach Status
4. Values: Count of Company Name
5. Filter by VC Source for sub-breakdowns

**Example Output:**
```
Outreach Status
Not Sent        8
Sent            3
Replied         1
```

### Track Email Quality

**Pivot Table Setup:**
1. Rows: Email Status
2. Values: Count

**Example Output:**
```
Email Status
ESTIMATED       3
VERIFIED        8
NOT FOUND       2
```

---

## Troubleshooting Emails

### Email Looks Generic or Bad

**Symptom:** Draft doesn't feel personalized

**Cause:** Claude API doesn't have detailed info about the company

**Fix:**
1. Check column L (Email Draft) — read full text
2. Open company website in another tab
3. Add specific insight to opening (replace generic hook)
4. Personalize closing with unique value prop

### Company Name or Email Wrong

**Symptom:** Excel shows "BuildCo" but company is actually "Build Co Inc"

**Cause:** Apollo scraped the name differently or website doesn't match Apollo

**Fix:**
1. Click Company Website link (Column H)
2. Verify it's the right company
3. If wrong: Delete entire row, mark as "Not Relevant"
4. (No need to delete from cache — company is already there)

### Contact Info Outdated

**Symptom:** Email sends but bounces; LinkedIn says person left company

**Cause:** Apollo data might be stale (updates weekly)

**Fix:**
1. Check company website for updated team page
2. Search LinkedIn for person (Column G has search URL)
3. Update Notes column with findings
4. Mark "No Response" after 3 days if email bounced

---

## Monthly Metrics

Track these in Excel using Pivot Tables or SUMIF formulas:

```
Emails Sent This Month: 32
Replies: 4 (12.5% reply rate)
Meetings Booked: 1
Passes: 2
```

Aim for:
- **Reply Rate**: 5-15% (depends on personalization)
- **Meeting Rate**: 20-50% of replies
- **Response Time**: 1-3 days typical

---

## Tips for Success

1. **Personalize Every Email**
   - Don't send the draft as-is
   - Add sentence about their specific company/product
   - Mention why you care (beyond "internship")

2. **Send at Optimal Times**
   - Tuesday-Thursday, 9 AM - Noon (recipient's timezone)
   - Avoid Monday (inboxes flooded) and Friday (low attention)

3. **Follow Up**
   - No reply after 5 days? Send gentle follow-up: "Just checking in..."
   - No reply after 10 days? Move to "No Response"

4. **Link to Proof**
   - Always include portfolio/GitHub link
   - Make it clickable: https://anishkakade.vercel.app

5. **Keep Subject Lines Short**
   - Under 50 characters
   - No emojis, no all-caps
   - Example: "Your RAG Infrastructure — Let's Talk"

---

## Next Steps

→ Go to [COLD_OUTREACH_GUIDE.md](./COLD_OUTREACH_GUIDE.md) for setup instructions.

→ Go to [README.md](./README.md#cold-outreach) for feature overview.

---

**Last Updated:** 2026-04-16
