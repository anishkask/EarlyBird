#!/usr/bin/env python3
"""
================================================================
  Job Search Pipeline
  Strategy: Find postings before 100 people apply.
================================================================
See full docstring in script for setup and usage.
Run: python job_pipeline_full.py
     python job_pipeline_full.py --no-email
     python job_pipeline_full.py --hours 12
     python job_pipeline_full.py --hours 72 --cold-outreach
"""

import os
import sys
import re
import time
import random
import json
import csv
import argparse
import warnings
from datetime import datetime, timezone, timedelta
from pathlib import Path
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup
import pandas as pd
from dotenv import load_dotenv
warnings.filterwarnings("ignore")

# Load environment variables from .env file
load_dotenv(override=True)

YOUR_NAME      = os.getenv("YOUR_NAME", "")
YOUR_EMAIL     = os.getenv("YOUR_EMAIL", "")
YOUR_SCHOOL    = os.getenv("YOUR_SCHOOL", "")
YOUR_LINKEDIN  = os.getenv("YOUR_LINKEDIN", "")
YOUR_GITHUB    = os.getenv("YOUR_GITHUB", "")
YOUR_PORTFOLIO = os.getenv("YOUR_PORTFOLIO", "")
MY_BACKGROUND  = os.getenv("MY_BACKGROUND", "")
EMAIL_DELAY_MIN = int(os.getenv("EMAIL_DELAY_MIN", "120"))
EMAIL_DELAY_MAX = int(os.getenv("EMAIL_DELAY_MAX", "300"))

# Global counter for tool_use blocks across all Claude API calls
tool_use_block_count = 0

# === Dynamic Company Loading ===
# Companies are loaded from companies.json (updated weekly via funding_pull.py)
# with a fallback list of known companies in case the dynamic list fails.

COMPANIES_CACHE_FILE = "companies.json"
COMPANIES_CACHE_MAX_AGE_DAYS = 7

# Fallback list: 10 known companies with confirmed ATS (used if companies.json unavailable)
FALLBACK_COMPANIES = [
    {"name": "Airbnb", "website": "https://www.airbnb.com", "ats_type": "greenhouse", "slug": "airbnb"},
    {"name": "Brex", "website": "https://www.brex.com", "ats_type": "greenhouse", "slug": "brex"},
    {"name": "Coinbase", "website": "https://www.coinbase.com", "ats_type": "lever", "slug": "coinbase"},
    {"name": "Notion", "website": "https://www.notion.so", "ats_type": "greenhouse", "slug": "notion"},
    {"name": "Vercel", "website": "https://vercel.com", "ats_type": "lever", "slug": "vercel"},
    {"name": "Linear", "website": "https://linear.app", "ats_type": "lever", "slug": "linear"},
    {"name": "Retool", "website": "https://retool.com", "ats_type": "lever", "slug": "retool"},
    {"name": "Glydways", "website": "https://www.glydways.com", "ats_type": "greenhouse", "slug": "glydways"},
    {"name": "Monarch Money", "website": "https://www.monarchmoney.com", "ats_type": "greenhouse", "slug": "monarchmoney"},
    {"name": "Eulerity", "website": "https://eulerity.com", "ats_type": "greenhouse", "slug": "eulerity"},
]

def load_companies():
    """
    Load companies from companies.json cache.
    Returns list of company dicts with: name, website, ats_type, slug
    Automatically refreshes if cache is > 7 days old.
    Falls back to hardcoded list if cache unavailable.
    """
    # Check if we need to refresh the cache
    if Path(COMPANIES_CACHE_FILE).exists():
        file_age_seconds = time.time() - Path(COMPANIES_CACHE_FILE).stat().st_mtime
        file_age_days = file_age_seconds / (24 * 3600)

        if file_age_days > COMPANIES_CACHE_MAX_AGE_DAYS:
            print(f"  [STALE] companies.json is {file_age_days:.1f} days old (threshold: {COMPANIES_CACHE_MAX_AGE_DAYS} days)")
            print(f"  [REFRESH] Running funding_pull.py to refresh company list...")
            try:
                import subprocess
                result = subprocess.run(
                    [sys.executable, "funding_pull.py"],
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                if result.returncode == 0:
                    print(f"  [SUCCESS] Company list updated successfully")
                else:
                    print(f"  [WARNING] funding_pull.py failed, using cached list")
            except Exception as e:
                print(f"  [WARNING] Could not run funding_pull.py: {e}")

    # Load from cache file if it exists
    if Path(COMPANIES_CACHE_FILE).exists():
        try:
            with open(COMPANIES_CACHE_FILE, "r") as f:
                data = json.load(f)
                companies = data.get("companies", [])
                if companies:
                    print(f"  [LOADED] {len(companies)} companies from cache")
                    return companies
        except Exception as e:
            print(f"  [WARNING] Could not read companies.json: {e}")

    # Fall back to hardcoded list
    print(f"  [FALLBACK] Using fallback list ({len(FALLBACK_COMPANIES)} companies)")
    return FALLBACK_COMPANIES

# Load companies on startup
COMPANIES = load_companies()

# Extract ATS-specific lists for backward compatibility with scrape functions
GREENHOUSE_SLUGS = [c["slug"] for c in COMPANIES if c.get("ats_type") == "greenhouse"]
LEVER_SLUGS = [c["slug"] for c in COMPANIES if c.get("ats_type") == "lever"]
ASHBY_SLUGS = []  # No Ashby companies in this setup yet

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

def extract_domain(url):
    """Extract base domain from a URL, stripping job-board subdomains."""
    if not url:
        return ""
    try:
        if not url.startswith("http"):
            url = "https://" + url
        hostname = urlparse(url).hostname or ""
        parts = hostname.split(".")
        # Strip known ATS/job-board subdomains (and www.)
        strip_prefixes = {"www", "careers", "jobs", "boards", "apply", "recruiting", "hire", "work", "job"}
        while len(parts) > 2 and parts[0] in strip_prefixes:
            parts = parts[1:]
        return ".".join(parts)
    except Exception:
        return ""

def hours_ago(dt):
    """Calculate hours elapsed since datetime dt. Returns 999 if dt is None."""
    if dt is None:
        return 999
    now = datetime.now(timezone.utc)
    if hasattr(dt, 'astimezone'):
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
    else:
        return 999
    delta = now - dt
    return int(delta.total_seconds() / 3600)

def is_intern(title):
    """Check if job title is for an internship."""
    if not title:
        return False
    t = title.lower()
    return "intern" in t or "co-op" in t or "graduate" in t


def resume_hint(title, desc=""):
    t = (title + " " + desc).lower()
    if any(k in t for k in ["rag", "llm", "ai ", "ml ", "machine learning", "genai"]):
        return "AI/ML Resume"
    if any(k in t for k in ["data pipeline", "analytics", "etl", "sql", "data engineer"]):
        return "Data Resume"
    if any(k in t for k in ["frontend", "front-end", "react", "css", "html"]):
        return "Frontend Resume"
    return "SWE Base Resume"

def score(title, desc=""):
    """Calculate match score (0-100) for a job based on title and description."""
    if not title:
        return 0
    text = (title + " " + desc).lower()
    score_val = 0

    # High-value keywords (25 points each)
    high_value = ["rag", "llm", "ai ", "ml ", "machine learning", "genai", "data engineer", "analytics"]
    score_val += sum(25 for keyword in high_value if keyword in text)

    # Medium-value keywords (15 points each)
    medium_value = ["backend", "fullstack", "frontend", "react", "python", "java", "c++", "go"]
    score_val += sum(15 for keyword in medium_value if keyword in text)

    # Low-value keywords (5 points each)
    low_value = ["remote", "flexible", "hybrid", "relocation", "visa"]
    score_val += sum(5 for keyword in low_value if keyword in text)

    return min(score_val, 100)  # Cap at 100

def job(title,company,location,url,dt,source,desc=""):
    ha = hours_ago(dt)
    return {"title":title,"company":company,"location":location,"job_url":url,
            "hours_ago":ha,"source":source,"description":desc[:400]}

def scrape_greenhouse(max_h):
    """Scrape Greenhouse ATS boards using public API."""
    out = []
    for token in GREENHOUSE_SLUGS:
        try:
            url = f"https://boards-api.greenhouse.io/v1/boards/{token}/jobs?content=true"
            r = requests.get(url, headers=HEADERS, timeout=8)
            if r.status_code == 404:
                # Token doesn't exist, skip silently
                continue
            if r.status_code != 200:
                continue

            for j in r.json().get("jobs", []):
                title = j.get("title", "")
                if not is_intern(title):
                    continue

                # Parse timestamp from updated_at or created_at
                dt = None
                for ts_field in ["updated_at", "created_at"]:
                    ts_str = j.get(ts_field, "")
                    if ts_str:
                        try:
                            dt = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
                            break
                        except Exception as e:
                            print(f"WARNING: [Greenhouse:{token}] timestamp parse error: {e}")
                            continue

                # Default to 72h ago if no timestamp found
                if dt is None:
                    dt = datetime.now(timezone.utc) - timedelta(hours=72)

                if hours_ago(dt) > max_h:
                    continue

                location = j.get("location", {})
                if isinstance(location, dict):
                    loc_name = location.get("name", "")
                else:
                    loc_name = str(location)

                out.append(job(
                    title,
                    token.replace("-", " ").title(),
                    loc_name,
                    j.get("absolute_url", ""),
                    dt,
                    "Greenhouse",
                    BeautifulSoup(j.get("content", ""), "html.parser").get_text()[:400]
                ))
        except Exception as e:
            print(f"WARNING: [Greenhouse:{token}] {e}")
    return out

def scrape_lever(max_h):
    """Scrape Lever ATS boards using public API."""
    out = []
    for slug in LEVER_SLUGS:
        try:
            url = f"https://api.lever.co/v0/postings/{slug}?mode=json"
            r = requests.get(url, headers=HEADERS, timeout=8)
            if r.status_code == 404:
                # Company doesn't have Lever board, skip silently
                continue
            if r.status_code != 200:
                continue

            for j in r.json():
                title = j.get("text", "")
                if not is_intern(title):
                    continue

                # Parse createdAt Unix timestamp (in milliseconds)
                dt = None
                created_ms = j.get("createdAt", 0)
                if created_ms and created_ms > 0:
                    try:
                        dt = datetime.fromtimestamp(created_ms / 1000.0, tz=timezone.utc)
                    except Exception as e:
                        print(f"WARNING: [Lever:{slug}] timestamp parse error: {e}")

                # Default to 72h ago if no timestamp found
                if dt is None:
                    dt = datetime.now(timezone.utc) - timedelta(hours=72)

                if hours_ago(dt) > max_h:
                    continue

                location = j.get("categories", {}).get("location", "")
                out.append(job(
                    title,
                    slug.replace("-", " ").title(),
                    location,
                    j.get("hostedUrl", ""),
                    dt,
                    "Lever",
                    j.get("descriptionPlain", "")[:400]
                ))
        except Exception as e:
            print(f"WARNING: [Lever:{slug}] {e}")
    return out

def scrape_ashby(max_h):
    out=[]
    for slug in ASHBY_SLUGS:
        try:
            payload={"operationName":"ApiJobBoardWithTeams",
                     "variables":{"organizationHostedJobsPageName":slug},
                     "query":"query ApiJobBoardWithTeams($organizationHostedJobsPageName:String!){jobBoard:publishedJobBoard(organizationHostedJobsPageName:$organizationHostedJobsPageName){jobPostings{id title locationName publishedDate externalLink}}}"}
            r=requests.post("https://jobs.ashbyhq.com/api/non-user-graphql?op=ApiJobBoardWithTeams",
                            json=payload,headers=HEADERS,timeout=6)
            if r.status_code != 200:
                continue
            job_postings = (r.json().get("data", {}).get("jobBoard", {}) or {}).get("jobPostings", []) or []
            for j in job_postings:
                t = j.get("title", "")
                if not is_intern(t):
                    continue
                dt = None
                try:
                    dt = datetime.fromisoformat(str(j.get("publishedDate", "")).replace("Z", "+00:00"))
                except Exception as e:
                    print(f"WARNING: [Ashby:{slug}] timestamp parse error: {e}")
                if hours_ago(dt) > max_h:
                    continue
                url = j.get("externalLink") or f"https://jobs.ashbyhq.com/{slug}/{j.get('id','')}"
                out.append(job(
                    t,
                    slug.replace("-", " ").title(),
                    j.get("locationName", ""),
                    url,
                    dt,
                    "Ashby/YC"
                ))
        except Exception as e:
            print(f"WARNING: [Ashby:{slug}] {e}")
    return out

def scrape_wellfound():
    out=[]
    try:
        r = requests.get("https://wellfound.com/jobs?role=engineer&job_type=internship",
                        headers=HEADERS, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        for card in soup.select("div[class*='JobListing'], div[class*='job-listing']")[:30]:
            a = card.find("a", href=True)
            co = card.find(class_=re.compile("company", re.I))
            if a and is_intern(a.text):
                dt = datetime.now(timezone.utc) - timedelta(hours=72)
                out.append(job(
                    a.text.strip(),
                    co.text.strip() if co else "",
                    "Remote",
                    "https://wellfound.com" + a["href"],
                    dt,
                    "Wellfound"
                ))
    except Exception as e:
        print(f"WARNING: [Wellfound] {e}")
    return out

def scrape_jobspy(max_h):
    """Scrape LinkedIn and Indeed using JobSpy (ZipRecruiter removed)."""
    out = []
    try:
        from jobspy import scrape_jobs
        for term in [
            "software engineering intern 2026",
            "AI engineering intern remote",
            "backend engineer intern",
            "fullstack intern"
        ]:
            try:
                df = scrape_jobs(
                    site_name=["linkedin", "indeed"],
                    search_term=term,
                    location="United States",
                    results_wanted=15,
                    hours_old=max_h,
                    country_indeed="USA",
                    is_remote=True
                )
                if df is not None and not df.empty:
                    for _, row in df.iterrows():
                        t = str(row.get("title", ""))
                        if not is_intern(t):
                            continue

                        # Convert date_posted to UTC datetime
                        dt = row.get("date_posted")
                        if hasattr(dt, "to_pydatetime"):
                            dt = dt.to_pydatetime()

                        # Ensure UTC timezone
                        if dt and isinstance(dt, datetime):
                            if dt.tzinfo is None:
                                # Assume UTC if no timezone info
                                dt = dt.replace(tzinfo=timezone.utc)

                        # Default to 72h ago if no timestamp
                        if dt is None:
                            dt = datetime.now(timezone.utc) - timedelta(hours=72)

                        if hours_ago(dt) > max_h:
                            continue

                        out.append(job(
                            t,
                            str(row.get("company", "")),
                            str(row.get("location", "")),
                            str(row.get("job_url", "")),
                            dt,
                            str(row.get("site", "")).title(),
                            str(row.get("description", ""))[:400]
                        ))
            except Exception as e:
                print(f"WARNING: [JobSpy:{term!r}] {e}")
    except ImportError:
        print("  [jobspy] skipped — run: pip install python-jobspy")
    return out

def find_contacts(company, role, client):
    """
    Find LinkedIn contacts at a company for internship outreach.
    Uses Claude with web search to return real, currently-found contacts.
    """
    global tool_use_block_count
    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            tools=[{"type": "web_search_20250305", "name": "web_search"}],
            messages=[{
                "role": "user",
                "content": (
                    f"Search LinkedIn and the web right now for the current campus recruiter "
                    f"or university recruiting contact at {company}. Also search for their email address. "
                    f"Return only real people you actually find via web search. "
                    f"Return JSON array only:\n"
                    f"[{{\"name\": \"\", \"title\": \"\", \"reason\": \"\", \"linkedin_url\": \"\", \"email\": \"\"}}]"
                )
            }]
        )

        # Count tool_use / server_tool_use blocks (proves web search was invoked)
        for block in response.content:
            if hasattr(block, "type") and block.type in ("tool_use", "server_tool_use"):
                tool_use_block_count += 1

        # Concatenate all text blocks
        result_text = ""
        for block in response.content:
            if hasattr(block, "type") and block.type == "text":
                result_text += block.text

        clean = re.sub(r"```json|```", "", result_text).strip()
        # Find JSON array in the response
        match = re.search(r"\[.*\]", clean, re.DOTALL)
        if match:
            return json.loads(match.group())
        # Maybe Claude returned a single object instead of array
        match = re.search(r"\{.*\}", clean, re.DOTALL)
        if match:
            return [json.loads(match.group())]
        return []
    except Exception as e:
        print(f"WARNING: [find_contacts:{company}] {e}")
        return []

def draft_messages(company,role,url,contact,client):
    name=contact.get("name") or ""
    reason=contact.get("reason","")
    school = os.getenv("YOUR_SCHOOL", "my university")
    angle=(f"I noticed we both went to {school}!" if "alumni" in reason.lower() or school.lower().split()[0] in reason.lower()
           else f"I came across your profile while researching {company}.")
    try:
        r=client.messages.create(model="claude-sonnet-4-20250514",max_tokens=700,
            messages=[{"role":"user","content":f"""Draft outreach from {YOUR_NAME} to {name or 'this person'} at {company} re: {role}.
Connection: {angle}
Background: {MY_BACKGROUND}
Job: {url}
No em-dashes. Warm, specific, professional.
Return JSON only: {{"email_subject":"","email_body":"","linkedin_message":"(under 280 chars)"}}"""}])
        return json.loads(re.sub(r'```json|```','',r.content[0].text).strip())
    except Exception as e:
        print(f"WARNING: [draft_messages:{company}] {e}")
        return {"email_subject":"","email_body":"","linkedin_message":""}

def get_gmail():
    try:
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from google.auth.transport.requests import Request
        from googleapiclient.discovery import build
        SCOPES=["https://www.googleapis.com/auth/gmail.send"]
        creds=None
        if Path("token.json").exists():
            creds=Credentials.from_authorized_user_file("token.json",SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not Path("credentials.json").exists():
                    return None
                creds=InstalledAppFlow.from_client_secrets_file("credentials.json",SCOPES).run_local_server(port=0)
            Path("token.json").write_text(creds.to_json())
        return build("gmail","v1",credentials=creds)
    except Exception as e:
        print(f"WARNING: [Gmail setup] {e}")
        return None

def send_email(gmail,to,subject,body,dry_run=False):
    import base64
    from email.mime.text import MIMEText
    if dry_run or not gmail:
        print(f"    [draft] {to} | {subject[:45]}")
        return False
    try:
        msg = MIMEText(body)
        msg["to"] = to
        msg["from"] = YOUR_EMAIL
        msg["subject"] = subject
        gmail.users().messages().send(userId="me",
            body={"raw":base64.urlsafe_b64encode(msg.as_bytes()).decode()}).execute()
        return True
    except Exception as e:
        print(f"    Email failed: {e}")
        return False

def write_excel(jobs, outreach, cold_outreach_data=None):
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment
    from openpyxl.utils import get_column_letter

    ts = datetime.now().strftime("%Y-%m-%d_%H-%M")
    fname = f"job_leads_{ts}.xlsx"
    wb = Workbook()
    hfill = PatternFill("solid", fgColor="0F2940")
    link_font = Font(name="Arial", color="0563C1", underline="single", size=9)

    # ── Jobs sheet ──────────────────────────────────────────────────────────
    ws = wb.active
    ws.title = "Jobs — Apply Here"
    hdrs = [
        "#", "Role", "Company", "Location", "Source", "Posted", "Apply Link",
        "Match Score", "Applied?", "Date Applied", "Status", "Notes"
    ]
    ws.append(hdrs)
    for c in ws[1]:
        c.font = Font(name="Arial", bold=True, color="FFFFFF", size=9)
        c.fill = hfill
        c.alignment = Alignment(horizontal="center")

    for i, j in enumerate(jobs, 1):
        ha = j.get("hours_ago", 999)
        posted = f"{ha:.0f}h ago" if ha < 999 else "Unknown"
        ws.append([
            i,
            j["title"],
            j["company"],
            j["location"],
            j["source"],
            posted,
            j["job_url"],
            score(j["title"], j.get("description", "")),
            "",             # Applied?
            "",             # Date Applied
            "Not Applied",  # Status
            ""              # Notes
        ])
        color = (
            "D5F5E3" if ha <= 6 else
            "D6EAF8" if ha <= 24 else
            "FEF9E7" if ha <= 48 else "FDFEFE"
        )
        for c in ws[i + 1]:
            c.fill = PatternFill("solid", fgColor=color)

    for i, w in enumerate([4, 35, 22, 18, 12, 14, 50, 12, 18, 14, 14, 20], 1):
        ws.column_dimensions[get_column_letter(i)].width = w
    ws.freeze_panes = "A2"

    # ── Outreach sheet ───────────────────────────────────────────────────────
    ws2 = wb.create_sheet("Outreach — Do This")
    hdrs2 = [
        "Company", "Role", "Contact Name", "Contact Title", "Why Reach Out",
        "LinkedIn URL", "LinkedIn Message (copy+send manually)",
        "Email Address",
        "Company Domain", "Apollo Lookup", "Email Pattern",
        "Email Subject", "Email Body Preview", "Email Sent?", "LinkedIn Sent?"
    ]
    ws2.append(hdrs2)
    for c in ws2[1]:
        c.font = Font(name="Arial", bold=True, color="FFFFFF", size=9)
        c.fill = hfill
        c.alignment = Alignment(horizontal="center")

    for row_idx, row in enumerate(outreach, 2):
        job_url = row.get("job_url", "")
        domain = extract_domain(job_url)
        apollo_url = f"https://app.apollo.io/#/people?q_organization_domains[]={domain}" if domain else ""

        ws2.append([
            row.get("company", ""),
            row.get("role", ""),
            row.get("name", ""),
            row.get("title", ""),
            row.get("reason", ""),
            row.get("linkedin_url", ""),
            row.get("linkedin_msg", ""),
            row.get("email", ""),
            domain,
            "Open Apollo" if apollo_url else "",
            "",  # Email Pattern — manual entry
            row.get("email_subj", ""),
            (row.get("email_body", "")[:250] + "...") if row.get("email_body") else "",
            row.get("email_sent", ""),
            "SEND MANUALLY via LinkedIn"
        ])
        # Apply hyperlink to Apollo Lookup cell (column 10)
        if apollo_url:
            cell = ws2.cell(row=row_idx, column=10)
            cell.hyperlink = apollo_url
            cell.font = link_font

    col_widths2 = [22, 30, 20, 22, 28, 50, 55, 28, 20, 16, 16, 35, 45, 14, 25]
    for i, w in enumerate(col_widths2, 1):
        ws2.column_dimensions[get_column_letter(i)].width = w
    ws2.freeze_panes = "A2"

    # ── Cold Outreach sheet (optional) ───────────────────────────────────────
    if cold_outreach_data:
        ws3 = wb.create_sheet("Cold Outreach")
        hdrs3 = [
            "Site", "Company", "Contact Name", "Title", "LinkedIn URL",
            "Contact Date", "Email",
            "Company Domain", "Apollo Lookup", "Email Pattern"
        ]
        ws3.append(hdrs3)
        for c in ws3[1]:
            c.font = Font(name="Arial", bold=True, color="FFFFFF", size=9)
            c.fill = hfill
            c.alignment = Alignment(horizontal="center")

        for row_idx, row in enumerate(cold_outreach_data, 2):
            site = row.get("site", "")
            domain = extract_domain(site) if site else extract_domain(row.get("company_website", ""))
            apollo_url = f"https://app.apollo.io/#/people?q_organization_domains[]={domain}" if domain else ""

            ws3.append([
                site,
                row.get("company", ""),
                row.get("contact_name", ""),
                row.get("title", ""),
                row.get("linkedin_url", ""),
                row.get("contact_date", ""),
                row.get("email", ""),
                domain,
                "Open Apollo" if apollo_url else "",
                "",  # Email Pattern — manual entry
            ])
            if apollo_url:
                cell = ws3.cell(row=row_idx, column=9)
                cell.hyperlink = apollo_url
                cell.font = link_font

        col_widths3 = [35, 22, 22, 22, 50, 14, 28, 20, 16, 16]
        for i, w in enumerate(col_widths3, 1):
            ws3.column_dimensions[get_column_letter(i)].width = w
        ws3.freeze_panes = "A2"

    # ── Legend sheet ─────────────────────────────────────────────────────────
    ws_legend = wb.create_sheet("Legend & Setup")
    for legend_row in [
        ["COLOR KEY", ""],
        ["Green", "Posted < 6 hours — apply IMMEDIATELY, you may be in first 10"],
        ["Blue", "Posted < 24 hours — apply today"],
        ["Yellow", "Posted < 48 hours — apply this week"],
        ["White", "Posted > 48 hours — still worth applying"],
        [""],
        ["OUTREACH INSTRUCTIONS", ""],
        ["LinkedIn messages", "Copy from Outreach tab → open LinkedIn search URL → send. Takes 30 sec each."],
        ["Emails", "Sent automatically to guessed addresses. Check your Sent folder."],
        ["Apollo Lookup", "Click the 'Open Apollo' link to search company contacts by domain."],
        ["Email Pattern", "Fill in manually after finding via Apollo (e.g. first.last@company.com)."],
        [""],
        ["SETUP", ""],
        ["1. Install", "pip install python-jobspy pandas openpyxl anthropic requests beautifulsoup4"],
        ["   Gmail", "pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client"],
        ["2. API key", "export ANTHROPIC_API_KEY='sk-...'"],
        ["3. Gmail", "Get credentials.json from Google Cloud Console (enable Gmail API, OAuth Desktop)"],
        ["4. Run", "python job_pipeline_full.py"],
        ["   Dry run", "python job_pipeline_full.py --no-email"],
        ["   Fresh only", "python job_pipeline_full.py --hours 12"],
        ["   Cold outreach", "python job_pipeline_full.py --hours 72 --cold-outreach"],
    ]:
        ws_legend.append(legend_row)
    ws_legend.column_dimensions["A"].width = 20
    ws_legend.column_dimensions["B"].width = 80

    wb.save(fname)
    return fname

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--no-email", action="store_true")
    p.add_argument("--hours", type=int, default=72)
    p.add_argument("--limit", type=int, default=None)
    p.add_argument("--scrape-only", action="store_true",
                   help="Run scrapers and write Excel only — skip all Claude API and Gmail calls")
    p.add_argument("--cold-outreach", action="store_true",
                   help="Also run cold outreach contact research and add a Cold Outreach tab")
    args = p.parse_args()

    if not args.scrape_only:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            print("Set ANTHROPIC_API_KEY in .env file or:\n  export ANTHROPIC_API_KEY='sk-...'")
            sys.exit(1)

        for var in ["YOUR_NAME", "YOUR_EMAIL", "YOUR_LINKEDIN", "YOUR_SCHOOL", "MY_BACKGROUND"]:
            if not os.getenv(var):
                print(f"WARNING: {var} is not set in .env — outreach messages may be incomplete")

        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
    else:
        client = None
        api_key = None

    gmail = get_gmail() if (not args.no_email and not args.scrape_only) else None

    print(f"\n{'='*60}")
    print(f"  Job Pipeline — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"  Finding jobs posted within {args.hours} hours")
    print(f"{'='*60}\n")

    all_jobs = []
    source_stats = {}  # Track raw vs filtered for each source

    for label, fn, kw in [
        ("Greenhouse ATS (startups/tech)", scrape_greenhouse, {"max_h": args.hours}),
        ("Lever ATS", scrape_lever, {"max_h": args.hours}),
        ("Ashby/YC startups", scrape_ashby, {"max_h": args.hours}),
        ("Wellfound/AngelList", scrape_wellfound, {}),
        ("LinkedIn/Indeed", scrape_jobspy, {"max_h": args.hours}),
    ]:
        print(f"Scraping {label}...")
        found = fn(**kw)
        raw_count = len(found)
        print(f"  {raw_count} internships found (raw)")
        all_jobs.extend(found)
        source_stats[label] = {"raw": raw_count, "filtered": 0}

    # Geographic filtering: Only keep jobs in PA, Remote, or US (no non-US cities/countries)
    PA_CITIES = [
        "philadelphia", "exton", "hatfield", "king of prussia", "malvern", "wayne", "conshohocken"
    ]
    def is_usa_location(loc):
        if not loc or not isinstance(loc, str):
            return False
        location_str = loc.lower()
        non_us_keywords = [
            "dublin", "luxembourg", "bengaluru", "são paulo", "warsaw", "toronto", "canada", "india", "brazil", "ireland", "germany", "uk", "united kingdom", "france", "europe", "singapore", "australia", "china", "japan", "hong kong", "mexico", "spain", "netherlands", "sweden", "switzerland", "italy", "israel", "uae", "dubai", "new zealand", "south africa", "argentina", "chile", "colombia", "peru", "denmark", "norway", "finland", "belgium", "austria", "czech", "poland", "russia", "turkey", "egypt", "saudi", "korea", "taiwan", "malaysia", "thailand", "philippines", "indonesia", "vietnam", "romania", "portugal", "greece", "ukraine", "hungary", "slovakia", "slovenia", "croatia", "serbia", "bulgaria", "latvia", "lithuania", "estonia", "africa", "asia", "south america", "middle east"
        ]
        if any(x in location_str for x in non_us_keywords):
            return False
        if any(city in location_str for city in PA_CITIES) or re.search(r',?\s*pa(\s|$|,)', location_str):
            return True
        if re.fullmatch(r'\s*remote\s*', location_str) or re.fullmatch(r'\s*united states\s*', location_str):
            return True
        if location_str.strip() in ["remote", "united states"]:
            return True
        if "remote" in location_str and not any(x in location_str for x in non_us_keywords):
            return True
        if re.search(r'\busa\b|\bunited states\b|\bus\b', location_str) and not any(x in location_str for x in non_us_keywords):
            return True
        return False

    all_jobs = [j for j in all_jobs if is_intern(j["title"]) and is_usa_location(j.get("location", ""))]

    # Deduplication: use compound key (company + title)
    seen = set()
    deduped = []
    for j in all_jobs:
        company = j["company"].lower().strip()
        title = j["title"].lower().strip()
        dedup_key = (company, title)
        if dedup_key not in seen:
            seen.add(dedup_key)
            deduped.append(j)

    all_jobs = sorted(deduped, key=lambda x: x.get("hours_ago", 999))

    # Count filtered jobs by source
    for j in all_jobs:
        source = j.get("source", "Unknown")
        if source in source_stats:
            source_stats[source]["filtered"] += 1

    print("Per-Source Summary:")
    for source, stats in source_stats.items():
        raw = stats["raw"]
        filtered = stats["filtered"]
        pct = f"({filtered}/{raw})" if raw > 0 else "(0/0)"
        print(f"  {source}: {filtered} passing filters {pct}")
    print()

    if args.limit:
        all_jobs = all_jobs[:args.limit]

    fresh = sum(1 for j in all_jobs if j.get("hours_ago", 999) <= 24)
    print(f"\nTotal: {len(all_jobs)} unique internships | {fresh} posted in last 24h\n")

    # Filter for outreach: only jobs posted within 96 hours (4 days)
    FRESHNESS_CUTOFF_H = 96
    fresh_jobs = [j for j in all_jobs if j.get("hours_ago", 999) <= FRESHNESS_CUTOFF_H]
    print(f"Jobs passing freshness check (<={FRESHNESS_CUTOFF_H}h): {len(fresh_jobs)}/{len(all_jobs)}\n")

    outreach = []
    if args.scrape_only:
        print("--scrape-only: skipping Claude API calls and outreach drafting\n")
    else:
        print("Researching contacts and drafting outreach...\n")
        for j in fresh_jobs[:35]:
            co = j.get("company", "")
            role = j.get("title", "")
            url = j.get("job_url", "")
            if not co or not role:
                continue
            print(f"  {co} — {role} ({j.get('hours_ago', 999):.0f}h ago)")
            contacts = find_contacts(co, role, client)
            for c in contacts[:2]:
                msgs = draft_messages(co, role, url, c, client)
                email = c.get("email", "") or c.get("guessed_email", "")
                sent = ""
                if email and not args.no_email:
                    delay = random.randint(EMAIL_DELAY_MIN, EMAIL_DELAY_MAX)
                    print(f"    Waiting {delay//60}m{delay%60}s before emailing {email}...")
                    time.sleep(delay)
                    ok = send_email(gmail, email, msgs.get("email_subject", ""), msgs.get("email_body", ""))
                    sent = "Sent" if ok else "Failed"
                elif email:
                    sent = "Drafted — send manually"
                else:
                    sent = "No email — LinkedIn only"
                outreach.append({
                    "company": co,
                    "role": role,
                    "job_url": url,
                    "name": c.get("name", ""),
                    "title": c.get("title", ""),
                    "reason": c.get("reason", ""),
                    "linkedin_url": c.get("linkedin_url", "") or c.get("linkedin_search_url", ""),
                    "linkedin_msg": msgs.get("linkedin_message", ""),
                    "email": email,
                    "email_subj": msgs.get("email_subject", ""),
                    "email_body": msgs.get("email_body", ""),
                    "email_sent": sent
                })

    # ── Cold Outreach ─────────────────────────────────────────────────────────
    cold_outreach_data = []
    if args.cold_outreach and not args.scrape_only:
        print("\nRunning cold outreach contact research...\n")
        from cold_outreach import run_cold_outreach
        import cold_outreach as _co_module
        cold_outreach_data = run_cold_outreach(COMPANIES[:25], client)
        # Sync the tool_use block counter from the cold_outreach module
        global tool_use_block_count
        tool_use_block_count += _co_module.tool_use_block_count
    elif args.cold_outreach and args.scrape_only:
        print("--scrape-only active: skipping cold outreach\n")

    fname = write_excel(all_jobs, outreach, cold_outreach_data if cold_outreach_data else None)

    print("\n" + "=" * 60)
    print("  COMPLETE")
    print(f"  {len(all_jobs)} jobs | {fresh} fresh | {len(outreach)} outreach drafted")
    if cold_outreach_data:
        print(f"  {len(cold_outreach_data)} cold outreach contacts researched")
    print(f"  File: {fname}")
    print(f"\n  Tool-use blocks in Claude API responses: {tool_use_block_count}")
    if tool_use_block_count == 0:
        print("  WARNING: 0 tool_use blocks — web search tool may not be invoking correctly")
    else:
        print(f"  OK: web search tool was invoked {tool_use_block_count} time(s)")
    print("\n  NEXT STEPS:")
    print("  1. Open file — start with GREEN rows (< 6h old)")
    print("  2. Go to Outreach tab — send LinkedIn messages (30 sec each)")
    print("  3. Click Apollo Lookup links to find email patterns")
    print("  4. Run tomorrow morning: python job_pipeline_full.py --hours 24")
    print("=" * 60 + "\n")

if __name__=="__main__":
    main()
