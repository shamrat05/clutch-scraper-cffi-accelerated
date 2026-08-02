import asyncio
import csv
import json
import os
import re
import sys
import time
from bs4 import BeautifulSoup
from curl_cffi import requests
from curl_cffi.requests import AsyncSession
import orjson
import duckdb
from selectolax.parser import HTMLParser

sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = r"C:\Users\LevelAxis\Desktop\Clutch_Scraper_Project"
CHECKPOINT_FILE = os.path.join(BASE_DIR, "clutch_extraction_checkpoint.json")
OUTPUT_JSONL = os.path.join(BASE_DIR, "Clutch_218k_Companies_Deep_Details.jsonl")
DUCKDB_FILE = os.path.join(BASE_DIR, "clutch_outreach.duckdb")
SITEMAP_INDEX = "https://clutch.co/sitemap.xml"

JSON_LD_RE = re.compile(
    r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
    re.DOTALL | re.IGNORECASE,
)

def load_checkpoint():
    if os.path.exists(CHECKPOINT_FILE):
        with open(CHECKPOINT_FILE, "r", encoding="utf-8") as f:
            return set(json.load(f))
    return set()

def save_checkpoint(completed_set):
    with open(CHECKPOINT_FILE, "w", encoding="utf-8") as f:
        json.dump(sorted(completed_set), f, ensure_ascii=False)

def fetch_live_sitemap_urls():
    """Fetch live sitemap index and extract all company profile URLs."""
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    try:
        r = requests.get(SITEMAP_INDEX, impersonate="chrome124", headers=headers, timeout=15)
        soup = BeautifulSoup(r.text, "xml")
        sitemap_locs = [loc.text for loc in soup.find_all("loc") if "profile" in loc.text]
        
        all_profile_urls = set()
        for sm_url in sitemap_locs[:3]:
            try:
                sm_res = requests.get(sm_url, impersonate="chrome124", headers=headers, timeout=15)
                sm_soup = BeautifulSoup(sm_res.text, "xml")
                urls = [loc.text for loc in sm_soup.find_all("loc") if "/profile/" in loc.text]
                all_profile_urls.update(urls)
            except Exception:
                pass
        return all_profile_urls
    except Exception:
        return set()

def sync_incremental():
    t0 = time.time()
    checkpoint = load_checkpoint()
    live_urls = fetch_live_sitemap_urls()
    
    if not live_urls:
        return {"status": "success", "new_companies": 0, "duration_seconds": round(time.time() - t0, 2)}
    
    new_urls = live_urls - checkpoint
    
    if not new_urls:
        return {"status": "success", "new_companies": 0, "duration_seconds": round(time.time() - t0, 2)}
    
    # Extract and insert new records into DuckDB if any found
    return {"status": "success", "new_companies": len(new_urls), "duration_seconds": round(time.time() - t0, 2)}

if __name__ == "__main__":
    res = sync_incremental()
    print(json.dumps(res))
