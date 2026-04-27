#!/usr/bin/env python3
"""
Cold Outreach Module
Scrapes VC portfolio sites, classifies tech companies, finds founders/CEOs via
Claude web search, and drafts personalized cold outreach emails.

Standalone:  python cold_outreach.py [--refresh] [--limit N]
Via pipeline: imported by job_pipeline_full.py --cold-outreach
"""

import os
import re
import sys
import json
import time
import argparse
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv(override=True)

# ── Config ────────────────────────────────────────────────────────────────────
CACHE_FILE       = "cold_outreach_cache.json"
CALL_DELAY       = 3          # seconds between Claude API calls
RATE_LIMIT_WAIT  = 22         # seconds to wait on 429
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

YOUR_PORTFOLIO = os.getenv("YOUR_PORTFOLIO", "")
YOUR_NAME      = os.getenv("YOUR_NAME", "")

# Shared tool-use block counter (importable by job_pipeline_full.py)
tool_use_block_count = 0


# ── Cache helpers ─────────────────────────────────────────────────────────────

def load_cache():
    if Path(CACHE_FILE).exists():
        try:
            with open(CACHE_FILE) as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def save_cache(cache):
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f, indent=2)


# ── Domain helper ─────────────────────────────────────────────────────────────

def extract_domain(url):
    if not url:
        return ""
    try:
        if not url.startswith("http"):
            url = "https://" + url
        hostname = urlparse(url).hostname or ""
        parts = hostname.split(".")
        strip = {"www", "careers", "jobs", "boards", "apply", "recruiting"}
        while len(parts) > 2 and parts[0] in strip:
            parts = parts[1:]
        return ".".join(parts)
    except Exception:
        return ""


# ── VC Portfolio Scrapers ──────────────────────────────────────────────────────

SKIP_DOMAINS = {
    "linkedin", "twitter", "instagram", "facebook", "youtube", "tiktok",
    "crunchbase", "angel.co", "pitchbook", "mailto", "apple.com",
    "google.com", "github.com", "bloomberg", "techcrunch", "axios",
}

def _is_skip_href(href):
    return any(x in href for x in SKIP_DOMAINS) or href.startswith("#") or not href.startswith("http")

def _dedup(results):
    seen = set()
    out = []
    for r in results:
        k = r["company_name"].lower().strip()
        if k and len(k) > 1 and k not in seen:
            seen.add(k)
            out.append(r)
    return out


def scrape_era_nyc():
    """https://www.eranyc.com/companies/ — server-rendered, article tags per company."""
    results = []
    try:
        r = requests.get("https://www.eranyc.com/companies/", headers=HEADERS, timeout=12)
        soup = BeautifulSoup(r.text, "html.parser")
        for article in soup.select("article"):
            # First heading inside article = company name
            name_el = article.find(["h1", "h2", "h3", "h4", "h5", "strong"])
            if not name_el:
                continue
            name = name_el.get_text(strip=True)
            # External link inside article (not email-protection)
            href = ""
            for a in article.select("a[href^='http']"):
                if "eranyc.com" not in a["href"] and "cdn-cgi" not in a["href"]:
                    href = a["href"]
                    break
            if name and 1 < len(name) < 60:
                results.append({"company_name": name, "website": href, "source": "ERA NYC"})
        deduped = _dedup(results)
        print(f"  [ERA NYC] {len(deduped)} companies found")
        return deduped
    except Exception as e:
        print(f"  [ERA NYC] ERROR: {e}")
        return []


def scrape_fj_labs():
    """https://www.fjlabs.com/portfolio — server-rendered, a[href^=http] links."""
    results = []
    try:
        r = requests.get("https://www.fjlabs.com/portfolio", headers=HEADERS, timeout=12)
        soup = BeautifulSoup(r.text, "html.parser")
        for a in soup.select("a[href^='http']"):
            name = a.get_text(strip=True)
            href = a["href"]
            if not name or len(name) < 2 or len(name) > 60:
                continue
            if _is_skip_href(href) or "fjlabs" in href:
                continue
            results.append({"company_name": name, "website": href, "source": "FJ Labs"})
        deduped = _dedup(results)
        print(f"  [FJ Labs] {len(deduped)} companies found")
        return deduped
    except Exception as e:
        print(f"  [FJ Labs] ERROR: {e}")
        return []


def scrape_pioneer():
    """https://pioneer.app/companies — server-rendered YC-style accelerator portfolio."""
    # Skip personal/founder pages and known non-company domains
    personal_skip = {"dcgross.com", "x.com", "twitter.com", "substack.com", "medium.com"}
    results = []
    try:
        r = requests.get("https://pioneer.app/companies", headers=HEADERS, timeout=12)
        soup = BeautifulSoup(r.text, "html.parser")
        for a in soup.select("a[href^='http']"):
            name = a.get_text(strip=True)
            href = a["href"]
            if not name or len(name) < 2 or len(name) > 50:
                continue
            if _is_skip_href(href) or "pioneer.app" in href:
                continue
            if any(s in href for s in personal_skip):
                continue
            # Skip names that look like full person names (e.g. "John Smith")
            if re.match(r"^[A-Z][a-z]+ [A-Z][a-z]+$", name):
                continue
            results.append({"company_name": name, "website": href, "source": "Pioneer"})
        deduped = _dedup(results)
        print(f"  [Pioneer] {len(deduped)} companies found")
        return deduped
    except Exception as e:
        print(f"  [Pioneer] ERROR: {e}")
        return []


def scrape_village_global():
    """https://villageglobal.vc/portfolio/ — server-rendered VC portfolio."""
    results = []
    try:
        r = requests.get("https://villageglobal.vc/portfolio/", headers=HEADERS, timeout=12)
        soup = BeautifulSoup(r.text, "html.parser")
        for a in soup.select("a[href^='http']"):
            name = a.get_text(strip=True)
            href = a["href"]
            if not name or len(name) < 2 or len(name) > 50:
                continue
            if _is_skip_href(href) or "villageglobal" in href:
                continue
            # Skip names that look like @handles
            if name.startswith("@"):
                continue
            results.append({"company_name": name, "website": href, "source": "Village Global"})
        deduped = _dedup(results)
        print(f"  [Village Global] {len(deduped)} companies found")
        return deduped
    except Exception as e:
        print(f"  [Village Global] ERROR: {e}")
        return []


def scrape_500global():
    """https://500.co/companies — server-rendered list of portfolio companies."""
    results = []
    try:
        r = requests.get("https://500.co/companies", headers=HEADERS, timeout=12)
        soup = BeautifulSoup(r.text, "html.parser")
        for a in soup.select("a[href^='http']"):
            name = a.get_text(strip=True)
            href = a["href"]
            if not name or len(name) < 2 or len(name) > 60:
                continue
            if _is_skip_href(href) or "500.co" in href or "500startups" in href:
                continue
            results.append({"company_name": name, "website": href, "source": "500 Global"})
        deduped = _dedup(results)
        print(f"  [500 Global] {len(deduped)} companies found")
        return deduped
    except Exception as e:
        print(f"  [500 Global] ERROR: {e}")
        return []


def scrape_betaworks():
    """https://betaworks.com/companies — server-rendered NYC accelerator."""
    results = []
    try:
        r = requests.get("https://betaworks.com/companies", headers=HEADERS, timeout=12)
        soup = BeautifulSoup(r.text, "html.parser")
        # Try headings first (more precise)
        for heading in soup.find_all(["h2", "h3", "h4"]):
            name = heading.get_text(strip=True)
            parent = heading.parent
            href = ""
            if parent:
                link = parent.find("a", href=True)
                if link and link["href"].startswith("http") and "betaworks" not in link["href"]:
                    href = link["href"]
            if name and 1 < len(name) < 60 and not _is_skip_href(href or "http://x"):
                results.append({"company_name": name, "website": href, "source": "Betaworks"})
        # Fallback to all external links if headings yield nothing
        if not results:
            for a in soup.select("a[href^='http']"):
                name = a.get_text(strip=True)
                href = a["href"]
                if not name or len(name) < 2 or len(name) > 60:
                    continue
                if _is_skip_href(href) or "betaworks" in href:
                    continue
                results.append({"company_name": name, "website": href, "source": "Betaworks"})
        deduped = _dedup(results)
        print(f"  [Betaworks] {len(deduped)} companies found")
        return deduped
    except Exception as e:
        print(f"  [Betaworks] ERROR: {e}")
        return []


def scrape_all_sources():
    """Run all scrapers and return combined company list."""
    print("\nScraping VC portfolio sites...")
    all_companies = []
    for fn in [
        scrape_era_nyc,
        scrape_fj_labs,
        scrape_betaworks,
        scrape_pioneer,
        scrape_village_global,
        scrape_500global,
    ]:
        all_companies.extend(fn())
    print(f"\nTotal companies scraped: {len(all_companies)}\n")
    return all_companies


# ── Claude API helpers ────────────────────────────────────────────────────────

def _claude_call(client, prompt, max_tokens=500, retries=3):
    """Call Claude with web search tool. Returns (result_text, tool_use_count)."""
    global tool_use_block_count
    for attempt in range(retries + 1):
        try:
            response = client.messages.create(
                model="claude-sonnet-4-5",
                max_tokens=max_tokens,
                tools=[{"type": "web_search_20250305", "name": "web_search"}],
                messages=[{"role": "user", "content": prompt}]
            )
            count = sum(
                1 for b in response.content
                if hasattr(b, "type") and b.type in ("tool_use", "server_tool_use")
            )
            tool_use_block_count += count
            text = "".join(
                b.text for b in response.content
                if hasattr(b, "type") and b.type == "text"
            )
            return text, count
        except Exception as e:
            err = str(e)
            if ("rate_limit" in err or "529" in err) and attempt < retries:
                wait = RATE_LIMIT_WAIT * (2 ** attempt)  # 22s, 44s, 88s
                print(f"    [rate limit] waiting {wait}s (attempt {attempt+1}/{retries})...")
                time.sleep(wait)
                continue
            print(f"    [API error] {e}")
            return "", 0
    return "", 0


def _parse_json(text):
    """Strip markdown fences and parse first JSON object or array found."""
    clean = re.sub(r"```json|```", "", text).strip()
    match = re.search(r"(\{.*?\}|\[.*?\])", clean, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except Exception:
            pass
    return None


def classify_tech(company_name, website, client):
    """Return True if the company is a software/AI/tech company."""
    prompt = (
        f"Search the web for '{company_name}' (website: {website}). "
        f"Is this a software, AI, or technology company? "
        f"Exclude biotech, pharma, food, apparel, cosmetics, real estate, non-profit. "
        f"Reply JSON only: {{\"is_tech\": true/false, \"category\": \"one word\"}}"
    )
    text, _ = _claude_call(client, prompt, max_tokens=200)
    time.sleep(CALL_DELAY)
    data = _parse_json(text)
    if data and isinstance(data, dict):
        return bool(data.get("is_tech", True))
    return True  # default include if uncertain


def get_founding_year(company_name, website, client):
    """Return founding year as int, or None."""
    prompt = (
        f"Search the web for the founding year of '{company_name}' (website: {website}). "
        f"Reply JSON only: {{\"founded\": 2023}}"
    )
    text, _ = _claude_call(client, prompt, max_tokens=150)
    time.sleep(CALL_DELAY)
    data = _parse_json(text)
    if data and isinstance(data, dict):
        try:
            return int(data.get("founded", 0)) or None
        except Exception:
            pass
    return None


def find_founder(company_name, client):
    """Find CEO or co-founder via Claude web search."""
    prompt = (
        f"Search LinkedIn and the web right now for the CEO or co-founder of {company_name}. "
        f"Find their full name, title, LinkedIn URL, and email if publicly available. "
        f"Return only real people found via web search. "
        f'Return JSON only: {{"name": "", "title": "", "linkedin_url": "", "email": ""}}'
    )
    text, _ = _claude_call(client, prompt, max_tokens=600)
    time.sleep(CALL_DELAY)
    data = _parse_json(text)
    if data and isinstance(data, dict):
        return data
    return {"name": "", "title": "", "linkedin_url": "", "email": ""}


def draft_email(company_name, website, contact_name, contact_title, client):
    """Draft a personalized cold outreach email."""
    portfolio = YOUR_PORTFOLIO or "my portfolio"
    name = YOUR_NAME or "Anishka"
    prompt = (
        f"Search the web for recent news or product updates about {company_name} ({website}). "
        f"Then draft a short cold outreach email from {name} to {contact_name or 'the founder'} "
        f"({contact_title or 'CEO'}) at {company_name}.\n\n"
        f"Background: {name} is a CS student with experience in Python, FastAPI, React, TypeScript, "
        f"PostgreSQL, RAG pipelines, Claude API, and deployed projects including EarlyBird. "
        f"Interested in smaller companies for ownership and direct impact.\n"
        f"Portfolio: {portfolio}\n\n"
        f"Rules: Subject must be specific to what {company_name} builds. Opening must reference "
        f"one real, specific thing the company is working on. No em-dashes. No flattery. "
        f"No filler phrases. Professional and direct. Close with a specific ask for a 15-minute call. "
        f'Return JSON only: {{"subject": "", "body": ""}}'
    )
    text, _ = _claude_call(client, prompt, max_tokens=800)
    time.sleep(CALL_DELAY)
    data = _parse_json(text)
    if data and isinstance(data, dict):
        return data.get("subject", ""), data.get("body", "")
    return "", ""


# ── Excel output ──────────────────────────────────────────────────────────────

def write_excel(rows):
    """Write results to a timestamped Excel file."""
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment
    from openpyxl.utils import get_column_letter

    ts = datetime.now().strftime("%Y-%m-%d_%H-%M")
    fname = f"cold_outreach_{ts}.xlsx"
    wb = Workbook()
    ws = wb.active
    ws.title = "Cold Outreach"

    hfill     = PatternFill("solid", fgColor="0F2940")
    new_fill  = PatternFill("solid", fgColor="FFFDE7")  # light yellow for NEW companies
    link_font = Font(name="Arial", color="0563C1", underline="single", size=9)

    headers = [
        "Site", "Company", "Contact Name", "Title", "LinkedIn URL",
        "Contact Date", "Email", "Company Domain",
        "Apollo Lookup", "Email Pattern", "Email Subject", "Email Body",
        "Founded", "NEW?"
    ]
    ws.append(headers)
    for cell in ws[1]:
        cell.font      = Font(name="Arial", bold=True, color="FFFFFF", size=9)
        cell.fill      = hfill
        cell.alignment = Alignment(horizontal="center")

    for row_idx, row in enumerate(rows, 2):
        is_new  = row.get("is_new", False)
        domain  = row.get("domain", "")
        apollo  = f"https://app.apollo.io/#/people?q_organization_domains[]={domain}" if domain else ""
        linkedin = row.get("linkedin_url", "")

        ws.append([
            row.get("site", ""),
            row.get("company", ""),
            row.get("contact_name", ""),
            row.get("contact_title", ""),
            linkedin,
            row.get("contact_date", ""),
            row.get("email", ""),
            domain,
            "Open Apollo" if apollo else "",
            "",   # Email Pattern — manual
            row.get("email_subject", ""),
            row.get("email_body", ""),
            row.get("founded", ""),
            "NEW" if is_new else "",
        ])

        # Apply yellow fill to NEW rows
        if is_new:
            for cell in ws[row_idx]:
                cell.fill = new_fill

        # Apollo hyperlink (column 9)
        if apollo:
            cell = ws.cell(row=row_idx, column=9)
            cell.hyperlink = apollo
            cell.font      = link_font

        # LinkedIn hyperlink (column 5)
        if linkedin and linkedin.startswith("http"):
            cell = ws.cell(row=row_idx, column=5)
            cell.hyperlink = linkedin
            cell.font      = link_font

    col_widths = [35, 22, 22, 22, 45, 14, 28, 20, 14, 16, 40, 60, 10, 6]
    for i, w in enumerate(col_widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = w
    ws.freeze_panes = "A2"

    wb.save(fname)
    return fname


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--refresh", action="store_true", help="Reprocess all companies, ignoring cache")
    parser.add_argument("--limit",   type=int, default=None, help="Max companies to process per run")
    args = parser.parse_args()

    import anthropic
    api_key = os.getenv("ANTHROPIC_API_KEY", "").strip()
    if not api_key:
        print("Set ANTHROPIC_API_KEY in .env")
        sys.exit(1)
    client = anthropic.Anthropic(api_key=api_key)

    # Load cache
    cache = {} if args.refresh else load_cache()
    if args.refresh:
        print("[--refresh] Ignoring cache, reprocessing all companies.\n")

    # Scrape all VC portfolio sources
    companies = scrape_all_sources()

    # Filter out cached companies
    new_companies = [c for c in companies if c["company_name"].lower().strip() not in cache]
    skipped = len(companies) - len(new_companies)
    print(f"Cache: {skipped} companies skipped (already processed), {len(new_companies)} new\n")

    if args.limit:
        new_companies = new_companies[:args.limit]
        print(f"[--limit] Processing first {args.limit} companies\n")

    total = len(new_companies)
    results = []
    today   = datetime.now().strftime("%Y-%m-%d")

    for idx, company in enumerate(new_companies, 1):
        name    = company["company_name"].strip()
        website = company.get("website", "")
        source  = company.get("source", "")
        print(f"Researching [{name}] ({idx}/{total}) -- {source}")

        # 1. Classify as tech or not
        is_tech = classify_tech(name, website, client)
        if not is_tech:
            print(f"  Skipping: not a tech/software company")
            cache[name.lower().strip()] = {"skipped": True, "reason": "non-tech"}
            save_cache(cache)
            continue

        # 2. Get founding year
        founded = get_founding_year(name, website, client)
        is_new  = founded is not None and founded >= 2023

        # 3. Find founder / CEO
        contact = find_founder(name, client)
        contact_name  = contact.get("name", "")
        contact_title = contact.get("title", "")
        linkedin_url  = contact.get("linkedin_url", "")
        email         = contact.get("email", "")
        print(f"  Contact: {contact_name or '(none found)'} | Email: {email or '(none)'} | Founded: {founded or '?'} {'[NEW]' if is_new else ''}")

        # 4. Draft email
        email_subject, email_body = draft_email(name, website, contact_name, contact_title, client)

        domain = extract_domain(website)
        row = {
            "site":          website,
            "company":       name,
            "source":        source,
            "contact_name":  contact_name,
            "contact_title": contact_title,
            "linkedin_url":  linkedin_url,
            "contact_date":  today,
            "email":         email,
            "domain":        domain,
            "email_subject": email_subject,
            "email_body":    email_body,
            "founded":       founded or "",
            "is_new":        is_new,
        }
        results.append(row)

        # Update cache
        cache[name.lower().strip()] = {
            "processed_date": today,
            "contact":        contact_name,
            "email":          email,
            "founded":        founded,
        }
        save_cache(cache)

    # Sort: NEW companies first
    results.sort(key=lambda r: (0 if r.get("is_new") else 1, r["company"]))

    # Write Excel
    fname = ""
    if results:
        fname = write_excel(results)
    else:
        print("\nNo new companies to process.")

    # Summary
    contacts_found = sum(1 for r in results if r.get("contact_name"))
    emails_found   = sum(1 for r in results if r.get("email"))
    new_count      = sum(1 for r in results if r.get("is_new"))

    print(f"\n{'='*60}")
    print(f"  COLD OUTREACH COMPLETE")
    print(f"  Total scraped:          {len(companies)}")
    print(f"  Skipped (cache):        {skipped}")
    print(f"  Processed this run:     {len(results)}")
    print(f"  NEW companies (2023+):  {new_count}")
    print(f"  Contacts found:         {contacts_found}")
    print(f"  Emails found:           {emails_found}")
    print(f"  Tool-use blocks:        {tool_use_block_count}")
    if tool_use_block_count == 0:
        print("  WARNING: 0 tool_use blocks -- web search may not be invoking correctly")
    else:
        print(f"  OK: web search confirmed active ({tool_use_block_count} search blocks)")
    if fname:
        print(f"  File: {fname}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
