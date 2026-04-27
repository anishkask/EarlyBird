#!/usr/bin/env python3
"""
Cold Outreach Module
Finds campus recruiters and university recruiting contacts for proactive outreach.
Can be run standalone or imported by job_pipeline_full.py via --cold-outreach flag.
"""

import os
import re
import sys
import json
import time
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Seconds to wait between API calls to avoid rate limits (web search uses ~10k tokens/call)
# At 30k tokens/min limit, each call needs ~20s gap to be safe
COLD_OUTREACH_DELAY = 22

load_dotenv(override=True)

# Shared counter — job_pipeline_full.py imports and increments this too
tool_use_block_count = 0


def find_campus_recruiter(company, client, retries=2):
    """Find campus recruiter at a company using Claude web search. Retries on rate limit."""
    global tool_use_block_count
    for attempt in range(retries + 1):
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
                        f"Return JSON: {{\"name\": \"\", \"title\": \"\", \"linkedin_url\": \"\", \"email\": \"\"}}"
                    )
                }]
            )
            # Count server_tool_use blocks (built-in web search returns "server_tool_use", not "tool_use")
            for block in response.content:
                if hasattr(block, "type") and block.type in ("tool_use", "server_tool_use"):
                    tool_use_block_count += 1

            # Concatenate text blocks
            result_text = ""
            for block in response.content:
                if hasattr(block, "type") and block.type == "text":
                    result_text += block.text

            # Try to parse JSON from the text
            clean = re.sub(r"```json|```", "", result_text).strip()
            match = re.search(r"\{.*\}", clean, re.DOTALL)
            if match:
                return json.loads(match.group())
            return {"name": "", "title": "", "linkedin_url": "", "email": ""}

        except Exception as e:
            err_str = str(e)
            if "rate_limit" in err_str and attempt < retries:
                wait = 30 * (attempt + 1)
                print(f"  [rate limit] waiting {wait}s before retry {attempt+1}/{retries}...")
                time.sleep(wait)
                continue
            print(f"  WARNING: [cold_outreach:{company}] {e}")
            return {"name": "", "title": "", "linkedin_url": "", "email": ""}


def classify_company(company_name, website, client):
    """Use Claude with web search to confirm company is a tech company worth cold-outreaching."""
    global tool_use_block_count
    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=300,
            tools=[{"type": "web_search_20250305", "name": "web_search"}],
            messages=[{
                "role": "user",
                "content": (
                    f"Search the web for '{company_name}' ({website}). "
                    f"Does this company hire software engineering interns? "
                    f"Reply with JSON only: {{\"hires_interns\": true/false, \"reason\": \"one sentence\"}}"
                )
            }]
        )
        for block in response.content:
            if hasattr(block, "type") and block.type in ("tool_use", "server_tool_use"):
                tool_use_block_count += 1

        result_text = ""
        for block in response.content:
            if hasattr(block, "type") and block.type == "text":
                result_text += block.text

        clean = re.sub(r"```json|```", "", result_text).strip()
        match = re.search(r"\{.*\}", clean, re.DOTALL)
        if match:
            return json.loads(match.group()).get("hires_interns", True)
        return True
    except Exception:
        return True  # Default to include if classification fails


def run_cold_outreach(companies, client, classify=False):
    """
    Run cold outreach research for a list of companies.

    Args:
        companies: list of company dicts (name, website) or plain strings
        client:    anthropic.Anthropic client
        classify:  if True, first verify company hires interns (costs extra API call)

    Returns:
        list of dicts with keys: site, company, contact_name, title,
        linkedin_url, contact_date, email
    """
    results = []
    today = datetime.now().strftime("%Y-%m-%d")

    for company in companies:
        if isinstance(company, str):
            name = company
            website = ""
        else:
            name = company.get("name", "")
            website = company.get("website", "")

        if not name:
            continue

        if classify:
            hires = classify_company(name, website, client)
            if not hires:
                print(f"  [Cold Outreach] Skipping {name} (does not appear to hire interns)")
                continue

        print(f"  [Cold Outreach] Searching for campus recruiter at {name}...")
        contact = find_campus_recruiter(name, client)
        # Throttle to stay under 30k input tokens/min rate limit
        time.sleep(COLD_OUTREACH_DELAY)

        results.append({
            "site": website,
            "company": name,
            "contact_name": contact.get("name", ""),
            "title": contact.get("title", ""),
            "linkedin_url": contact.get("linkedin_url", ""),
            "contact_date": today,
            "email": contact.get("email", ""),
        })

    return results


def main():
    """Standalone entry point — runs cold outreach on companies from companies.json."""
    import anthropic

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("Set ANTHROPIC_API_KEY in .env or export it.")
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)

    # Load companies
    companies_file = Path("companies.json")
    if companies_file.exists():
        with open(companies_file) as f:
            data = json.load(f)
        companies = data.get("companies", [])[:30]
    else:
        print("companies.json not found — using sample companies")
        companies = [
            {"name": "Airbnb", "website": "https://www.airbnb.com"},
            {"name": "Notion", "website": "https://www.notion.so"},
            {"name": "Vercel", "website": "https://vercel.com"},
        ]

    print(f"\nRunning cold outreach research for {len(companies)} companies...\n")
    results = run_cold_outreach(companies, client)

    print(f"\nTool-use blocks in API responses: {tool_use_block_count}")
    print(f"\nResults ({len(results)} companies):")
    for r in results:
        print(f"  {r['company']}: {r['contact_name'] or '(no contact found)'} — {r['email'] or '(no email)'}")


if __name__ == "__main__":
    main()
