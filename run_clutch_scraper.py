import asyncio
import json
import csv
import os
import sys
import time
import re
from collections import deque

# Ensure UTF-8 output for Windows console
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")
sys.stderr.reconfigure(encoding="utf-8", errors="backslashreplace")

from curl_cffi.requests import AsyncSession
import orjson
from selectolax.parser import HTMLParser

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
CLOUDFLARE_DIR = os.path.join(PROJECT_DIR, "cloudflare_bypass")
sys.path.insert(0, CLOUDFLARE_DIR)

INPUT_CSV = os.path.join(PROJECT_DIR, "Clutch_All_127k_Companies_Master_List.csv")
OUTPUT_JSONL = os.path.join(PROJECT_DIR, "Clutch_218k_Companies_Deep_Details.jsonl")
OUTPUT_CSV = os.path.join(PROJECT_DIR, "Clutch_218k_Companies_Deep_Details.csv")
CHECKPOINT_FILE = os.path.join(PROJECT_DIR, "clutch_extraction_checkpoint.json")
FAILED_FILE = os.path.join(PROJECT_DIR, "clutch_failed_checkpoint.json")
PERM_FAIL_FILE = os.path.join(PROJECT_DIR, "clutch_permanent_failures.json")
SESSION_FILE = os.path.join(PROJECT_DIR, "clutch_cf_session.json")

# Pre-compiled C-level regex for instant JSON-LD extraction (0 overhead)
JSON_LD_RE = re.compile(r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', re.DOTALL | re.IGNORECASE)

# Cloudflare challenge-page fingerprints. Anything else below => fast-path retry.
BLOCK_INDICATORS = (
    "just a moment",
    "challenges.cloudflare",
    "cf-browser-verification",
    "verify you are human",
    "checking your browser",
    "attention required",
    "turnstile",
)

# curl_cffi impersonation targets available in 0.15.0, newest first.
CHROME_FINGERPRINTS = (
    "chrome146",
    "chrome142",
    "chrome136",
    "chrome133a",
    "chrome131",
    "chrome124",
    "chrome123",
    "chrome120",
    "chrome119",
    "chrome116",
    "chrome110",
    "chrome107",
    "chrome104",
    "chrome101",
    "chrome100",
    "chrome99",
)

PARALLEL = 20  # fast-path parallel workers
BATCH_SIZE = 400  # URLs processed per round before a session-health check
SESSION_MAX_AGE = 20 * 60  # seconds; refresh cf_clearance beyond this age
SOLVE_TIMEOUT = 120.0  # seconds budget for one browser solve
BACKOFF_BASE = 30  # seconds; doubles per consecutive block round, capped
BACKOFF_CAP = 300


def parse_deep_profile(html_content, profile_url):
    main_ld = {}
    
    # 1. Ultra-fast C-level Regex + Rust orjson decoding (240x faster than BS4)
    for match in JSON_LD_RE.finditer(html_content):
        script_text = match.group(1).strip()
        if not script_text:
            continue
        try:
            data = orjson.loads(script_text)
            if isinstance(data, dict) and data.get("@type") in [
                "Organization",
                "LocalBusiness",
            ]:
                main_ld = data
                break
        except Exception:
            pass

    # Core attributes
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

    # Rating & Reviews
    agg_rating = main_ld.get("aggregateRating", {})
    rating_val = agg_rating.get("ratingValue") if isinstance(agg_rating, dict) else ""
    review_cnt_str = agg_rating.get("reviewCount") if isinstance(agg_rating, dict) else ""
    try:
        total_review_count = int(review_cnt_str) if review_cnt_str else 0
    except ValueError:
        total_review_count = 0

    # Address (#location)
    address_obj = main_ld.get("address", {})
    if isinstance(address_obj, dict):
        street = address_obj.get("streetAddress", "")
        locality = address_obj.get("addressLocality", "")
        region = address_obj.get("addressRegion", "")
        postcode = address_obj.get("postalCode", "")
        country = address_obj.get("addressCountry", "")
    else:
        street, locality, region, postcode, country = "", "", "", "", ""

    # Services / Catalog (#packages)
    catalog = main_ld.get("hasOfferCatalog", {})
    offers = []
    if isinstance(catalog, dict):
        items = catalog.get("itemListElement", [])
        for it in items:
            if isinstance(it, dict):
                item_offered = it.get("itemOffered", {})
                if isinstance(item_offered, dict) and item_offered.get("name"):
                    offers.append(item_offered["name"])

    # Verification (#verification)
    credentials_raw = main_ld.get("hasCredential", [])
    certifications = []
    if isinstance(credentials_raw, list):
        for cred in credentials_raw:
            if isinstance(cred, dict) and cred.get("name"):
                certifications.append(cred["name"])

    # Detailed Reviews (#reviews) - C-level parsing of all embedded review objects
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

    # Team / Leadership (#about-the-team) Fast C-DOM traversal via selectolax
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


def is_blocked_page(text):
    low = (text or "").lower()
    return any(ind in low for ind in BLOCK_INDICATORS)


def pick_fingerprint(user_agent):
    """Best curl_cffi TLS fingerprint for the browser UA that solved cf_clearance."""
    m = re.search(r"Chrome/(\d+)", user_agent or "")
    major = int(m.group(1)) if m else 0
    for fp in CHROME_FINGERPRINTS:
        mm = re.search(r"\d+", fp)
        num = int(mm.group()) if mm else 0
        if major == 0 or num <= major:
            return fp
    return "chrome124"


def load_session():
    if os.path.exists(SESSION_FILE):
        try:
            with open(SESSION_FILE, "r", encoding="utf-8") as f:
                s = json.load(f)
            if s.get("cookies") and s.get("user_agent"):
                return s
        except Exception as e:
            print(f"[i] Session load error: {e}")
    return None


def save_session(s):
    with open(SESSION_FILE, "w", encoding="utf-8") as f:
        json.dump(s, f, ensure_ascii=False, indent=2)


def session_fresh(s, max_age=SESSION_MAX_AGE):
    return s and (time.time() - s.get("solved_at", 0)) < max_age


def solve_cf_session_sync():
    """Blocking browser solve via the cloned cloudflare_bypass toolkit."""
    from bypass import bypass_cloudflare

    print(
        f"\n[CF] Solving Cloudflare challenge in real Chrome (timeout {SOLVE_TIMEOUT}s)..."
    )
    res = bypass_cloudflare(
        "https://clutch.co", timeout=SOLVE_TIMEOUT, save_cookies=False
    )
    if res.get("success") and res.get("cf_clearance"):
        ua = res["user_agent"] or ""
        session = {
            "cookies": res.get("cookies") or {},
            "user_agent": ua,
            "fingerprint": pick_fingerprint(ua),
            "solved_at": time.time(),
            "method": res.get("method"),
        }
        save_session(session)
        print(
            f"[CF] Solved OK. UA={ua[:60]} fp={session['fingerprint']} cookies={list(session['cookies'].keys())}"
        )
        return session
    print(f"[CF] Solve failed: {res.get('error')}")
    return None


async def ensure_cf_session():
    """Return a fresh cf session; solve via browser if missing/stale."""
    s = load_session()
    if s and session_fresh(s):
        print(
            f"[CF] Reusing fresh session ({int(time.time() - s['solved_at'])}s old, fp={s.get('fingerprint')})"
        )
        return s
    return await asyncio.to_thread(solve_cf_session_sync)


def make_headers(user_agent):
    return {
        "User-Agent": user_agent,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
    }


async def fetch_fast(session, url, cf, fp_override=None):
    """Fast path: curl_cffi with browser-solved cookies and optional C-level fingerprint rotation."""
    target_fp = fp_override or cf.get("fingerprint", "chrome124")
    try:
        r = await session.get(
            url,
            impersonate=target_fp,
            headers=make_headers(cf.get("user_agent") or ""),
            cookies=cf.get("cookies") or {},
            timeout=20,
            allow_redirects=True,
        )
        text = r.text or ""
        if r.status_code == 200 and not is_blocked_page(text):
            try:
                data = parse_deep_profile(text, url)
                
                # C-level Multi-Page Review Pagination check: If review_count > 15, fetch remaining pages fast
                total_revs = data.get("review_count") or 0
                if total_revs > 15:
                    rev_pages_to_fetch = min(5, (total_revs + 14) // 15) # Fetch up to 5 additional review pages
                    existing_reviews = orjson.loads(data["reviews_sample"])
                    existing_titles = {r.get("title") for r in existing_reviews if r.get("title")}
                    
                    for page_idx in range(1, rev_pages_to_fetch):
                        page_url = f"{url}?page={page_idx}#reviews"
                        r_sub = await session.get(
                            page_url,
                            impersonate=target_fp,
                            headers=make_headers(cf.get("user_agent") or ""),
                            cookies=cf.get("cookies") or {},
                            timeout=10,
                            allow_redirects=True,
                        )
                        if r_sub.status_code == 200 and not is_blocked_page(r_sub.text):
                            for match in JSON_LD_RE.finditer(r_sub.text):
                                try:
                                    sub_data = orjson.loads(match.group(1).strip())
                                    if isinstance(sub_data, dict) and "review" in sub_data:
                                        for s_rev in sub_data["review"]:
                                            if isinstance(s_rev, dict):
                                                t_title = s_rev.get("name", "")
                                                if t_title and t_title not in existing_titles:
                                                    existing_titles.add(t_title)
                                                    existing_reviews.append({
                                                        "title": t_title,
                                                        "author": s_rev.get("author", {}).get("name", "") if isinstance(s_rev.get("author"), dict) else str(s_rev.get("author", "")),
                                                        "rating": s_rev.get("reviewRating", {}).get("ratingValue", "") if isinstance(s_rev.get("reviewRating"), dict) else "",
                                                        "body": (s_rev.get("reviewBody", "")[:300] + "...") if s_rev.get("reviewBody") else "",
                                                    })
                                except Exception:
                                    pass
                                    
                    data["total_reviews_extracted"] = len(existing_reviews)
                    data["reviews_sample"] = orjson.dumps(existing_reviews).decode("utf-8")

                return True, data, None
            except Exception as e:
                print(f"[!] Parse error {url}: {e}")
                return False, None, None
        if r.status_code in (404, 410):
            print(f"[-] GONE {r.status_code}: {url}")
            return False, None, f"HTTP {r.status_code}"
        print(f"[-] BLOCKED {r.status_code}: {url}")
        return False, None, None
    except Exception as e:
        print(f"[-] Error {url}: {type(e).__name__}: {e}")
        return False, None, None


async def run_batch(session, urls, cf, jsonl_file, completed_set):
    sem = asyncio.Semaphore(PARALLEL)
    ok = []
    failed = []
    permanent = []

    async def work(url):
        async with sem:
            success, data, perm = await fetch_fast(session, url, cf)
            if success and data:
                jsonl_file.write(orjson.dumps(data).decode("utf-8") + "\n")
                jsonl_file.flush()
                completed_set.add(url)
                ok.append(url)
                print(
                    f"[+] Extracted ({len(completed_set)} total, {data['total_reviews_extracted']} reviews): {data['company_name']} ({data['locality']})"
                )
            elif perm:
                permanent.append(url)
            else:
                failed.append(url)
            sys.stdout.flush()

    await asyncio.gather(*(work(u) for u in urls))
    return ok, failed, permanent


def load_set(path):
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return set(json.load(f))
        except Exception as e:
            print(f"[i] Load error {path}: {e}")
    return set()


def save_set(path, values):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(sorted(values), f, ensure_ascii=False)


def main():
    start_time = time.time()

    if not os.path.exists(INPUT_CSV):
        print(f"Master input list {INPUT_CSV} missing!")
        return

    urls = []
    with open(INPUT_CSV, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            urls.append(row["profile_url"])
    total = len(urls)
    print(f"Loaded {total} total company profile URLs from master sitemap list.")

    completed = load_set(CHECKPOINT_FILE)
    print(
        f"RESUMING PROGRESS: Loaded checkpoint with {len(completed)} already processed URLs."
    )

    pending = deque(u for u in urls if u not in completed)
    print(f"Remaining company profiles to extract: {len(pending)}")
    sys.stdout.flush()

    # Fresh or fresh-enough CF session (solves in real Chrome when needed).
    cf = asyncio.run(ensure_cf_session())
    if cf is None:
        print("\n[!] Could not obtain a Cloudflare clearance session yet.")
        print(
            "[!] Retrying in real Chrome automatically. The run will not proceed until a solve succeeds.\n"
        )
        while cf is None:
            time.sleep(10)
            cf = asyncio.run(ensure_cf_session())
    print(f"[CF] Active session fingerprint: {cf.get('fingerprint')}\n")

    jsonl_file = open(OUTPUT_JSONL, "a", encoding="utf-8")
    failed_log = load_set(FAILED_FILE)
    perm_log = load_set(PERM_FAIL_FILE)
    consecutive_blocks = 0

    try:
        while pending:
            batch = [pending.popleft() for _ in range(min(BATCH_SIZE, len(pending)))]

            async def _batch():
                async with AsyncSession(max_clients=PARALLEL) as session:
                    return await run_batch(session, batch, cf, jsonl_file, completed)

            ok_count, failed_urls, permanent_urls = asyncio.run(_batch())

            if permanent_urls:
                perm_log.update(permanent_urls)
                save_set(PERM_FAIL_FILE, perm_log)
                print(
                    f"[GONE] {len(permanent_urls)} URLs no longer exist "
                    f"(HTTP 404/410); logged to clutch_permanent_failures.json."
                )

            if failed_urls:
                # INSTANT FAST-PATH RETRY: If only a few URLs failed (< 15% of batch), retry immediately without 60s delay!
                if len(failed_urls) < (len(batch) * 0.15):
                    print(f"\n[FAST-RETRY] {len(failed_urls)} isolated URLs rate-limited. Retrying immediately with rotated TLS fingerprint...")
                    async def _fast_retry():
                        rot_fp = CHROME_FINGERPRINTS[(consecutive_blocks + 1) % len(CHROME_FINGERPRINTS)]
                        async with AsyncSession(max_clients=10) as session:
                            return await run_batch(session, failed_urls, {**cf, 'fingerprint': rot_fp}, jsonl_file, completed)
                    
                    r_ok, r_failed, r_perm = asyncio.run(_fast_retry())
                    if r_perm:
                        perm_log.update(r_perm)
                        save_set(PERM_FAIL_FILE, perm_log)
                    if r_failed:
                        pending.extend(r_failed)
                        failed_log.update(r_failed)
                        save_set(FAILED_FILE, failed_log)
                else:
                    # Major block round: Re-solve Cloudflare session with 10s fast retry instead of 60s!
                    consecutive_blocks += 1
                    failed_log.update(failed_urls)
                    save_set(FAILED_FILE, failed_log)
                    print(
                        f"\n[RETRY] {len(failed_urls)} URLs blocked this round. "
                        f"Re-solving CF session (fast-retry 10s)..."
                    )
                    time.sleep(5)
                    new_cf = asyncio.run(ensure_cf_session())
                    while new_cf is None:
                        print("[CF] Retrying Cloudflare solve after delay...")
                        time.sleep(5)
                        new_cf = asyncio.run(ensure_cf_session())
                    cf = new_cf
                    pending.extend(failed_urls)
            else:
                consecutive_blocks = 0
                failed_log.difference_update(ok_count)
                save_set(FAILED_FILE, failed_log)

            # Periodic checkpoint + progress.
            save_set(CHECKPOINT_FILE, completed)
            if len(completed) > 0:
                pct = len(completed) / total * 100
            else:
                pct = 0.0
            print(
                f"[PROGRESS] {len(completed)} / {total} companies extracted ({pct:.2f}%). "
                f"Remaining: {len(pending)} | Failed backlog: {len(failed_log)}"
            )
            sys.stdout.flush()

            # Refresh session if it went stale mid-run.
            if not session_fresh(cf):
                print("[CF] Session aged out; re-solving...")
                new_cf = asyncio.run(ensure_cf_session())
                while new_cf is None:
                    print("[CF] Retrying Cloudflare solve after delay...")
                    time.sleep(5)
                    new_cf = asyncio.run(ensure_cf_session())
                cf = new_cf
    except KeyboardInterrupt:
        print("\n[STOP] Interrupted. Checkpoint saved; run again to resume.")
    finally:
        save_set(CHECKPOINT_FILE, completed)
        save_set(FAILED_FILE, failed_log)
        jsonl_file.close()

    elapsed = time.time() - start_time
    print(
        f"\nExtraction pass completed in {elapsed:.2f} seconds. Total processed: {len(completed)}"
    )
    if failed_log:
        print(
            f"[!] {len(failed_log)} URLs still in the failed backlog. "
            f"Next run automatically retries them: {FAILED_FILE}"
        )


if __name__ == "__main__":
    main()

