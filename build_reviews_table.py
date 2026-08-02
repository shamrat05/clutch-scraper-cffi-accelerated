import os
import sys
import time
import duckdb
import orjson

sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = r"C:\Users\LevelAxis\Desktop\Clutch_Scraper_Project"
DUCKDB_FILE = os.path.join(BASE_DIR, "clutch_outreach.duckdb")

def build_reviews_table():
    start_time = time.time()
    print("=" * 70)
    print("      BUILDING DEDICATED REVIEWS & REVIEWER LEAD TABLE")
    print("=" * 70)

    conn = duckdb.connect(DUCKDB_FILE)

    # 1. Update certification count
    print("[+] Calculating certification counts...")
    conn.execute("""
        ALTER TABLE companies ADD COLUMN IF NOT EXISTS cert_count INT;
        UPDATE companies SET cert_count = CASE 
            WHEN certifications IS NULL OR certifications = '' THEN 0
            ELSE len(string_split(certifications, ','))
        END;
    """)

    # 2. Re-create REVIEWS table
    print("[+] Creating REVIEWS table schema...")
    conn.execute("DROP TABLE IF EXISTS reviews;")
    conn.execute("""
        CREATE TABLE reviews (
            company_name VARCHAR,
            profile_url VARCHAR,
            official_website VARCHAR,
            phone VARCHAR,
            locality VARCHAR,
            country VARCHAR,
            review_title VARCHAR,
            reviewer_name VARCHAR,
            review_rating DOUBLE,
            review_body VARCHAR
        );
    """)

    print("[+] Fetching company reviews JSON samples...")
    rows = conn.execute("""
        SELECT company_name, profile_url, official_website, phone, locality, country, reviews_sample 
        FROM companies 
        WHERE reviews_sample IS NOT NULL AND reviews_sample != '[]' AND reviews_sample != ''
    """).fetchall()

    print(f"[+] Processing {len(rows):,} companies with extracted client reviews...")
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
                        rating_raw = r.get("rating")
                        
                        try:
                            rating_val = float(rating_raw) if rating_raw else None
                        except (ValueError, TypeError):
                            rating_val = None

                        if author or title or body:
                            review_records.append((
                                c_name, p_url, website, phone, locality, country,
                                title, author, rating_val, body
                            ))
        except Exception:
            pass

    print(f"[+] Inserting {len(review_records):,} client review records into DuckDB...")
    conn.executemany("""
        INSERT INTO reviews VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, review_records)

    print("[+] Building B-Tree indexes on Reviewer Leads...")
    conn.execute("CREATE INDEX idx_reviewer ON reviews (reviewer_name);")
    conn.execute("CREATE INDEX idx_rev_rating ON reviews (review_rating DESC);")
    conn.execute("CREATE INDEX idx_rev_company ON reviews (company_name);")

    conn.close()
    elapsed = time.time() - start_time
    print(f"[✔] Reviews Lead Database built successfully in {elapsed:.2f}s! Indexed {len(review_records):,} reviews.")

if __name__ == "__main__":
    build_reviews_table()
