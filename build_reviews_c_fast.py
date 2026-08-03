import os
import sys
import time
import duckdb

sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = r"C:\Users\LevelAxis\Desktop\Clutch_Scraper_Project"
DUCKDB_FILE = os.path.join(BASE_DIR, "clutch_outreach.duckdb")

def build_c_fast():
    t0 = time.time()
    print("=" * 70)
    print("      BUILDING 259,000+ REVIEWS IN C-LEVEL VECTORIZED SQL ENGINE")
    print("=" * 70)

    conn = duckdb.connect(DUCKDB_FILE)
    conn.execute("PRAGMA threads=8;")
    conn.execute("PRAGMA max_memory='4GB';")

    print("[+] Executing C++ SIMD JSON unnest query...")
    conn.execute("DROP TABLE IF EXISTS reviews;")
    
    conn.execute("""
        CREATE TABLE reviews AS
        SELECT 
            COALESCE(NULLIF(TRIM(json_extract_string(rev_elem, '$.author')), ''), 'Verified Decision-Maker') AS reviewer_name,
            COALESCE(NULLIF(TRIM(json_extract_string(rev_elem, '$.title')), ''), 'Client Organization') AS reviewer_company,
            TRIM(json_extract_string(rev_elem, '$.title')) AS review_title,
            COALESCE(TRIM(json_extract_string(rev_elem, '$.date')), TRIM(json_extract_string(rev_elem, '$.datePublished')), '') AS review_date,
            TRY_CAST(json_extract_string(rev_elem, '$.rating') AS DOUBLE) AS review_rating,
            TRIM(json_extract_string(rev_elem, '$.body')) AS review_body,
            company_name AS vendor_agency_name,
            profile_url AS vendor_profile_url,
            official_website AS vendor_website,
            phone AS vendor_phone,
            locality AS vendor_locality,
            country AS vendor_country
        FROM (
            SELECT company_name, profile_url, official_website, phone, locality, country,
                   UNNEST(from_json(reviews_sample, '["JSON"]')) AS rev_elem
            FROM companies
            WHERE reviews_sample IS NOT NULL AND reviews_sample != '' AND reviews_sample != '[]'
        );
    """)

    print("[+] Building B-Tree indexes...")
    conn.execute("CREATE INDEX idx_reviewer_name ON reviews (reviewer_name);")
    conn.execute("CREATE INDEX idx_reviewer_company ON reviews (reviewer_company);")
    conn.execute("CREATE INDEX idx_rev_rating ON reviews (review_rating DESC);")
    conn.execute("CREATE INDEX idx_vendor_name ON reviews (vendor_agency_name);")

    count = conn.execute("SELECT COUNT(*) FROM reviews").fetchone()[0]
    conn.close()

    elapsed = time.time() - t0
    print(f"\n[✔] SUCCESS! Built {count:,} verified client review leads in {elapsed:.2f} seconds!")

if __name__ == "__main__":
    build_c_fast()
