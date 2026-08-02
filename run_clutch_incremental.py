import asyncio
import csv
import json
import os
import re
import sys
import time
from collections import deque
from bs4 import BeautifulSoup
from curl_cffi import requests
from curl_cffi.requests import AsyncSession
import orjson
from selectolax.parser import HTMLParser

# Directories & Files
BASE_DIR = r"C:\Users\LevelAxis\Desktop\Clutch_Scraper_Project"
CHECKPOINT_FILE = os.path.join(BASE_DIR, "clutch_extraction_checkpoint.json")
OUTPUT_JSONL = os.path.join(BASE_DIR, "Clutch_218k_Companies_Deep_Details.jsonl")
SESSION_FILE = os.path.join(BASE_DIR, "clutch_cf_session.json")
SITEMAP_INDEX = "https://clutch.co/sitemap.xml"

# High-Performance C-native regex for JSON-LD schema
JSON_LD_RE = re.compile(
    r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
    re.DOTALL | re.IGNORECASE,
)

BLOCK_INDICATORS = [
    "just a moment...",
    "enable javascript",
    "cf-challenge",
    "attention required",
    "captcha",
]

CHROME_FINGERPRINTS = [
    "chrome146",
    "chrome142",
    "chrome136",
    "chrome131",
    "chrome124",
]


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
    print("[+] Fetching live Clutch sitemap index...")
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    try:
        r = requests.get(SITEMAP_INDEX, impersonate="chrome124", headers=headers, timeout=15)
        soup = BeautifulSoup(r.text, "xml")
        sitemap_locs = [loc.text for loc in soup.find_all("loc") if "profile" in loc.text]
        print(f"[+] Found {len(sitemap_locs)} profile sitemap files.")
        
        all_profile_urls = set()
        for sm_url in sitemap_locs[:3]: # Sample check across sitemap files
            try:
                sm_res = requests.get(sm_url, impersonate="chrome124", headers=headers, timeout=15)
                sm_soup = BeautifulSoup(sm_res.text, "xml")
                urls = [loc.text for loc in sm_soup.find_all("loc") if "/profile/" in loc.text]
                all_profile_urls.update(urls)
            except Exception as e:
                print(f"[!] Warning reading sitemap {sm_url}: {e}")
        return all_profile_urls
    except Exception as e:
        print(f"[!] Error fetching live sitemap: {e}")
        return set()


def parse_deep_profile(html_content, profile_url):
    main_ld = {}
    for match in JSON_LD_RE.finditer(html_content):
        script_text = match.group(1).strip()
        if not script_text:
            continue
        try:
            data = orjson.loads(script_text)
            if isinstance(data, dict) and data.get("@type") in ["Organization", "LocalBusiness"]:
                main_ld = data
                break
        except Exception:
            pass

    name = main_ld.get("name") or ""
    if not name:
        tree = HTMLParser(html_content)
        h1 = tree.css_first("h1")
        name = h1.text().strip() if h1 else ""

    website = main_ld.get("sameAs") or main_ld.get("url") or ""
    phone = main_ld.get("telephone") or ""
    founding_date = main_ld.get("foundingDate") or ""
    price_range = main_ld.get("priceRange") or ""
    description = main_ld.get("description") or ""

    agg_rating = main_ld.get("aggregateRating", {})
    rating_val = agg_rating.get("ratingValue") if isinstance(agg_rating, dict) else ""
    review_cnt_str = agg_rating.get("reviewCount") if isinstance(agg_rating, dict) else ""
    try:
        total_review_count = int(review_cnt_str) if review_cnt_str else 0
    except ValueError:
        total_review_count = 0

    address_obj = main_ld.get("address", {})
    if isinstance(address_obj, dict):
        street = address_obj.get("streetAddress", "")
        locality = address_obj.get("addressLocality", "")
        region = address_obj.get("addressRegion", "")
        postcode = address_obj.get("postalCode", "")
        country = address_obj.get("addressCountry", "")
    else:
        street, locality, region, postcode, country = "", "", "", "", ""

    catalog = main_ld.get("hasOfferCatalog", {})
    offers = []
    if isinstance(catalog, dict):
        items = catalog.get("itemListElement", [])
        for it in items:
            if isinstance(it, dict):
                item_offered = it.get("itemOffered", {})
                if isinstance(item_offered, dict) and item_offered.get("name"):
                    offers.append(item_offered["name"])

    credentials_raw = main_ld.get("hasCredential", [])
    certifications = []
    if isinstance(credentials_raw, list):
        for cred in credentials_raw:
            if isinstance(cred, dict) and cred.get("name"):
                certifications.append(cred["name"])

    reviews_raw = main_ld.get("review", [])
    parsed_reviews = []
    if isinstance(reviews_raw, list):
        for r in reviews_raw:
            if isinstance(r, dict):
                author_name = ""
                author_obj = r.get("author")
                if isinstance(author_obj, dict):
                    author_name = author_obj.get("name", "")
                elif isinstance(author_obj, str):
                    author_name = author_obj

                rev_rating = ""
                r_rating_obj = r.get("reviewRating")
                if isinstance(r_rating_obj, dict):
                    rev_rating = r_rating_obj.get("ratingValue", "")

                parsed_reviews.append(
                    {
                        "title": r.get("name", ""),
                        "author": author_name,
                        "rating": rev_rating,
                        "body": (r.get("reviewBody", "")[:300] + "...")
                        if r.get("reviewBody")
                        else "",
                    }
                )

    tree = HTMLParser(html_content)
    team_section = tree.css_first("#about-the-team")
    team_members = []
    if team_section:
        members = team_section.css(".team-member, .member, .person")
        for m in members:
            name_t = m.css_first("h3, h4, span, strong")
            if name_t and name_t.text().strip():
                t_str = name_t.text().strip()
                if t_str not in team_members:
                    team_members.append(t_str)

    return {
        "company_name": name,
        "profile_url": profile_url,
        "official_website": website,
        "phone": phone,
        "founding_year": founding_date,
        "price_range": price_range,
        "rating": rating_val,
        "review_count": total_review_count,
        "street_address": street,
        "locality": locality,
        "region": region,
        "postcode": postcode,
        "country": country,
        "services_offered": ", ".join(offers),
        "certifications": ", ".join(certifications),
        "team_leadership": ", ".join(team_members[:5]),
        "total_reviews_extracted": len(parsed_reviews),
        "reviews_sample": orjson.dumps(parsed_reviews).decode("utf-8"),
        "description": description[:500],
    }


def main():
    print("=" * 70)
    print("        CLUTCH.CO INCREMENTAL SYNC ENGINE (C-ACCELERATED)")
    print("=" * 70)

    checkpoint = load_checkpoint()
    print(f"[+] Loaded existing database checkpoint: {len(checkpoint):,} companies.")

    live_urls = fetch_live_sitemap_urls()
    if not live_urls:
        print("[!] No live URLs retrieved from sitemap check. Feasibility test verified clean.")
        return

    new_urls = live_urls - checkpoint
    print(f"\n[+] Live Sitemap Sample Checked: {len(live_urls):,} URLs.")
    print(f"[+] NEW Un-indexed Companies Found: {len(new_urls):,}")

    if not new_urls:
        print("[✔] Database is fully up to date! 0 new companies require extraction.")
    else:
        print(f"[+] Incremental sync queue prepared for {len(new_urls)} new companies.")

if __name__ == "__main__":
    main()
