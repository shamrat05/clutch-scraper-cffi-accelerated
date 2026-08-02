# Clutch.co Master Extraction Engine (218,865 Companies)

Welcome to the **Clutch.co Master Extraction Suite**. This project contains full datasets, master URL indices, and a high-performance un-throttled async scraper built with `curl_cffi` to extract deep company profiles across all Clutch pages and sub-sections.

---

## 📁 Directory Structure & Files

```text
Clutch_Scraper_Project/
├── run_clutch_scraper.py                   # Hybrid Async scraper (curl_cffi fast path + browser CF bypass)
├── cloudflare_bypass/                      # Cloned CF bypass toolkit (seleniumbase UC, cookies, etc.)
├── Clutch_All_127k_Companies_Master_List.csv # Master list of 218,865 company profile URLs
├── Clutch_218k_Companies_Deep_Details.jsonl # JSON Lines database for deep extracted company data
├── Clutch_218k_Companies_Deep_Details.csv   # CSV database of deep extracted company data
├── Clutch_US_Digital_Marketing_Agencies_Live.csv # Pre-extracted 1,200 US digital marketing agencies
├── clutch_extraction_checkpoint.json       # Automatic checkpoint file tracking completed URLs
├── clutch_failed_checkpoint.json           # (auto) URLs blocked/failed - retried until success
├── clutch_cf_session.json                  # (auto) Last browser-solved Cloudflare clearance session
└── README.md                               # Project documentation & usage guide
```

---

## ⚡ How to Run & Resume Extraction

The scraper is configured to **always pick up exactly where it left off**. It checks `clutch_extraction_checkpoint.json` on startup and skips all URLs that have already been extracted.

### Run Command:
Open PowerShell or Command Prompt in this folder and run:

```bash
python run_clutch_scraper.py
```

### Cloudflare Bypass (Hybrid, Automatic):
The scraper ships with the `cloudflare_bypass/` toolkit and runs a **hybrid strategy** so it is never stopped by Cloudflare:

1. **Fast path first:** every URL is fetched with `curl_cffi` (TLS fingerprint impersonation) using the browser-solved `cf_clearance` cookies.
2. **Automatic browser solve:** when the fast path gets blocked (`403` / challenge page), the scraper automatically opens real Chrome (SeleniumBase UC Mode), solves the challenge, saves the fresh session to `clutch_cf_session.json`, and retries.
3. **Automatic session refresh:** if the clearance cookie ages out (`SESSION_MAX_AGE = 20 min`), it re-solves in the background before the next batch.
4. **Never loses work:** every failure is written to `clutch_failed_checkpoint.json` and re-queued automatically. Failed URLs are retried on the next pass — and on the next run — with exponential backoff (`30s` → `300s`) until they succeed.
5. **Resumable:** you can stop, interrupt, or restart the script at any time without losing data or re-scraping completed profiles.

> Note: `cf_clearance` is bound to your IP + User-Agent, so the cookie reuse path uses the exact UA the browser solved with (fingerprint `chrome146` by default). Do not switch proxies/network mid-run without a re-solve.

### Features:
1. **Automatic Checkpointing:** Progress is continuously saved to `clutch_extraction_checkpoint.json`.
2. **Automatic Fail Recovery:** Blocked/failed URLs persist in `clutch_failed_checkpoint.json` and are retried with backoff until success.
3. **Hybrid Cloudflare Bypass:** `curl_cffi` TLS impersonation + real-Chrome UC solve fallback + cookie reuse.
4. **Resumable:** You can stop, interrupt, or restart the script at any time without losing data or re-scraping completed profiles.
5. **Un-throttled Speed:** Operates with 20 parallel `curl_cffi` workers for maximum throughput.
6. **UTF-8 Safe:** Standardized output handling for international company names, locations, and characters.

---

## 📊 Extracted Data Schema

Each company profile extraction extracts data from all major sections:

* **Contact & Overview (`#contact`)**: Company Name, Direct Official Website, Phone Number, Year Founded, Price Range / Hourly Rate.
* **HQ & Address (`#location`)**: Street Address, Locality (City), Region (State), Postal Code, Country Code.
* **Services offered (`#packages`)**: Complete Offer Catalog (e.g. AI Dev, Custom Software, SEO, Mobile Apps).
* **Verification (`#verification`)**: Clutch Certified Badges, Verification Badges, Industry Credentials.
* **Reviews (`#reviews`)**: Aggregate Rating, Review Count, Reviewer Names, Ratings, Review Body Snippets.
* **Leadership (`#about-the-team`)**: Founders, CEOs, and Executive Names.
* **Description (`#portfolio-and-awards`)**: Full Overview & About text.
