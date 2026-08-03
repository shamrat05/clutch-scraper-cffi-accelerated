import os
import sys
import re
import duckdb
import orjson

sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = r"C:\Users\LevelAxis\Desktop\Clutch_Scraper_Project"
DUCKDB_FILE = os.path.join(BASE_DIR, "clutch_outreach.duckdb")
HTML_FILE = r"C:\Users\LevelAxis\.gemini\antigravity-cli\brain\2cceb594-d798-42f2-a874-a90266528fa2\scratch\profile_brain_station_23.html"

def extract_reviewer_company(title, body):
    if not title and not body:
        return "Client Organization"
    text = (title or "") + " " + (body or "")
    patterns = [
        r'for\s+(?:an?\s+)?([A-Z0-9][A-Za-z0-9\s&\-\'\.]{2,35}\s+(?:Company|Corp|Inc|Ltd|University|College|Startup|Agency|Firm|Brand|Platform|Retailer|Manufacturer|Hospital|Bank|Group))',
        r'for\s+(?:an?\s+)?([A-Za-z0-9\s&\-\'\.]{2,30}\s+(?:eCommerce|SaaS|Healthcare|Fintech|B2B|Real Estate|Automotive|Logistics|Education))',
        r'(?:hired by|client is|working with)\s+(?:an?\s+)?([A-Za-z0-9\s&\-\'\.]{2,35})'
    ]
    for pat in patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            clean = m.group(1).strip()
            if len(clean) > 3:
                return clean
    return title.strip() if title else "Client Organization"

def upgrade_reviews_schema():
    print("[+] Reading Brain Station 23 HTML reviews with published dates...")
    with open(HTML_FILE, "r", encoding="utf-8") as f:
        html = f.read()

    JSON_LD_RE = re.compile(r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', re.DOTALL | re.IGNORECASE)
    bs23_reviews = []
    
    for match in JSON_LD_RE.finditer(html):
        try:
            data = orjson.loads(match.group(1).strip())
            if isinstance(data, dict) and "review" in data:
                revs = data["review"]
                for r in revs:
                    if isinstance(r, dict):
                        author = ""
                        a_obj = r.get("author")
                        if isinstance(a_obj, dict):
                            author = a_obj.get("name", "")
                        elif isinstance(a_obj, str):
                            author = a_obj
                            
                        title = r.get("name", "")
                        body = r.get("reviewBody", "")
                        date_pub = r.get("datePublished", "")
                        rating_obj = r.get("reviewRating", {})
                        rating_val = rating_obj.get("ratingValue") if isinstance(rating_obj, dict) else "5.0"
                        
                        if author and author != "Clutch.co":
                            bs23_reviews.append({
                                "title": title,
                                "author": author,
                                "date": date_pub,
                                "rating": float(rating_val) if rating_val else 5.0,
                                "body": body[:600] if body else ""
                            })
        except Exception:
            pass

    print(f"[✔] Found {len(bs23_reviews)} reviews with datePublished!")
    
    conn = duckdb.connect(DUCKDB_FILE)
    
    # Update Brain Station 23 in companies table
    conn.execute("""
        UPDATE companies 
        SET reviews_sample = ?, total_reviews_extracted = ? 
        WHERE LOWER(company_name) LIKE '%brain%station%'
    """, (orjson.dumps(bs23_reviews).decode("utf-8"), len(bs23_reviews)))

    print("[+] Upgrading DuckDB reviews table schema to include review_date...")
    conn.execute("DROP TABLE IF EXISTS reviews;")
    conn.execute("""
        CREATE TABLE reviews (
            reviewer_name VARCHAR,
            reviewer_company VARCHAR,
            review_title VARCHAR,
            review_date VARCHAR,
            review_rating DOUBLE,
            review_body VARCHAR,
            vendor_agency_name VARCHAR,
            vendor_profile_url VARCHAR,
            vendor_website VARCHAR,
            vendor_phone VARCHAR,
            vendor_locality VARCHAR,
            vendor_country VARCHAR
        );
    """)

    rows = conn.execute("""
        SELECT company_name, profile_url, official_website, phone, locality, country, reviews_sample 
        FROM companies 
        WHERE reviews_sample IS NOT NULL AND reviews_sample != '[]' AND reviews_sample != ''
    """).fetchall()

    review_records = []
    for row in rows:
        c_name, p_url, website, phone, locality, country, raw_json = row
        try:
            parsed = orjson.loads(raw_json)
            if isinstance(parsed, list):
                for r in parsed:
                    if isinstance(r, dict):
                        author = (r.get("author") or "").strip()
                        title = (r.get("title") or "").strip()
                        body = (r.get("body") or "").strip()
                        r_date = (r.get("date") or r.get("datePublished") or "").strip()
                        rating_raw = r.get("rating")
                        try:
                            rating_val = float(rating_raw) if rating_raw else None
                        except (ValueError, TypeError):
                            rating_val = None

                        if author or title or body:
                            reviewer_comp = extract_reviewer_company(title, body)
                            review_records.append((
                                author or "Verified Decision-Maker",
                                reviewer_comp,
                                title,
                                r_date,
                                rating_val,
                                body,
                                c_name,
                                p_url,
                                website,
                                phone,
                                locality,
                                country
                            ))
        except Exception:
            pass

    print(f"[+] Inserting {len(review_records):,} review records into DuckDB...")
    conn.executemany("INSERT INTO reviews VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", review_records)

    conn.execute("CREATE INDEX idx_reviewer_name ON reviews (reviewer_name);")
    conn.execute("CREATE INDEX idx_reviewer_company ON reviews (reviewer_company);")
    conn.execute("CREATE INDEX idx_rev_rating ON reviews (review_rating DESC);")
    conn.execute("CREATE INDEX idx_vendor_name ON reviews (vendor_agency_name);")

    conn.close()
    print("[✔] Database schema upgrade complete!")

if __name__ == "__main__":
    upgrade_reviews_schema()
