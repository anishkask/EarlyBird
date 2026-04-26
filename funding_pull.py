#!/usr/bin/env python3
"""
Funding Pull Module — Dynamically detect recently funded startups using Crunchbase API
and identify which ones use Greenhouse or Lever for recruitment.

Usage:
    python funding_pull.py                    # Force refresh
    python funding_pull.py --check-only       # Check if refresh needed
    
This module is called automatically from job_pipeline_full.py if companies.json is > 7 days old.
"""

import os
import sys
import json
import time
import requests
from datetime import datetime, timezone, timedelta
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

CRUNCHBASE_API_KEY = os.getenv("CRUNCHBASE_API_KEY", "")
CACHE_FILE = "companies.json"
CACHE_MAX_AGE_DAYS = 7
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

def should_refresh_cache():
    """Check if cache is older than CACHE_MAX_AGE_DAYS."""
    if not Path(CACHE_FILE).exists():
        return True
    
    file_age_seconds = time.time() - Path(CACHE_FILE).stat().st_mtime
    file_age_days = file_age_seconds / (24 * 3600)
    
    return file_age_days > CACHE_MAX_AGE_DAYS

def query_crunchbase():
    """
    Query Crunchbase API for recently funded startups.
    Returns list of companies with name and website.
    """
    if not CRUNCHBASE_API_KEY:
        print("[WARNING] CRUNCHBASE_API_KEY not set in .env. Skipping Crunchbase query.")
        return []
    
    try:
        # Calculate date 90 days ago
        cutoff_date = (datetime.now(timezone.utc) - timedelta(days=90)).isoformat()
        
        # Crunchbase API v4 endpoint
        url = "https://api.crunchbase.com/api/v4/searches/organizations"
        
        payload = {
            "field_ids": ["name", "website", "headquarters_location", "short_description"],
            "order_by": [{"field_id": "founded_on", "sort": "desc"}],
            "limit": 50,
            "filters": [
                {
                    "field_id": "funding_total",
                    "operator_id": "gte",
                    "value": 100000
                },
                {
                    "field_id": "last_funding_type",
                    "operator_id": "includes",
                    "value": ["seed", "pre_seed"]
                },
                {
                    "field_id": "founded_on",
                    "operator_id": "gte",
                    "value": cutoff_date
                },
                {
                    "field_id": "location_country_code",
                    "operator_id": "eq",
                    "value": "US"
                },
                {
                    "field_id": "categories",
                    "operator_id": "includes",
                    "value": ["software", "technology", "saas", "artificial-intelligence"]
                }
            ]
        }
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "X-Cb-User-Key": CRUNCHBASE_API_KEY
        }
        
        print("[QUERYING] Crunchbase API for recently funded startups...")
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        
        if response.status_code != 200:
            print(f"   [WARNING] Crunchbase API returned status {response.status_code}")
            return []
        
        data = response.json()
        companies = []
        
        for entity in data.get("entities", []):
            name = entity.get("name", "").strip()
            website = entity.get("website", "").strip()
            
            if name and website:
                companies.append({
                    "name": name,
                    "website": website
                })
        
        print(f"   [SUCCESS] Found {len(companies)} recently funded companies")
        return companies
    
    except Exception as e:
        print(f"   [ERROR] Crunchbase query failed: {e}")
        return []

def detect_ats(company_name, website):
    """
    Detect if company uses Greenhouse or Lever by testing common slug patterns.
    Returns: ("greenhouse"|"lever"|None, slug) or (None, None)
    """
    # Generate common slug formats
    slug_variants = [
        company_name.lower().replace(" ", "-").replace(".", ""),
        company_name.lower().replace(" ", ""),
        company_name.split()[0].lower(),  # First word only
    ]
    
    # Remove duplicates
    slug_variants = list(dict.fromkeys(slug_variants))
    
    for slug in slug_variants:
        # Test Greenhouse
        try:
            gh_url = f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs?content=false"
            resp = requests.head(gh_url, headers=HEADERS, timeout=5)
            if resp.status_code == 200:
                return ("greenhouse", slug)
        except Exception:
            pass
        
        # Test Lever
        try:
            lv_url = f"https://api.lever.co/v0/postings/{slug}?mode=json"
            resp = requests.head(lv_url, headers=HEADERS, timeout=5)
            if resp.status_code == 200:
                return ("lever", slug)
        except Exception:
            pass
    
    return (None, None)

def refresh_cache(companies):
    """
    Detect ATS for each company and save to cache file.
    """
    print(f"[DETECTING] ATS systems for {len(companies)} companies...")
    
    companies_with_ats = []
    
    for i, company in enumerate(companies, 1):
        name = company["name"]
        website = company["website"]
        
        ats_type, slug = detect_ats(name, website)
        
        if ats_type:
            print(f"   [{i}/{len(companies)}] [FOUND] {name} -> {ats_type.upper()}")
            companies_with_ats.append({
                "name": name,
                "website": website,
                "ats_type": ats_type,
                "slug": slug
            })
        else:
            print(f"   [{i}/{len(companies)}] [SKIPPED] {name} - No ATS detected")
    
    # Save to cache
    cache_data = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": "crunchbase",
        "count": len(companies_with_ats),
        "companies": companies_with_ats
    }
    
    with open(CACHE_FILE, "w") as f:
        json.dump(cache_data, f, indent=2)
    
    print(f"\n[SAVED] {len(companies_with_ats)} companies with ATS to {CACHE_FILE}")
    return companies_with_ats

def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Pull funded startups from Crunchbase and detect ATS")
    parser.add_argument("--check-only", action="store_true", help="Check if refresh is needed without refreshing")
    parser.add_argument("--force", action="store_true", help="Force refresh regardless of cache age")
    args = parser.parse_args()
    
    if args.check_only:
        if should_refresh_cache():
            print("Cache is stale. Refresh needed.")
            sys.exit(1)
        else:
            print("Cache is fresh.")
            sys.exit(0)
    
    if args.force or should_refresh_cache():
        companies = query_crunchbase()
        if companies:
            refresh_cache(companies)
        else:
            print("No companies found from Crunchbase.")
    else:
        age_days = time.time() - Path(CACHE_FILE).stat().st_mtime
        age_days = age_days / (24 * 3600)
        print(f"Cache is fresh ({age_days:.1f} days old). Skipping refresh.")

if __name__ == "__main__":
    main()
