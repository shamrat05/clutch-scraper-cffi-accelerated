import os
import sys
import time
import duckdb

sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = r"C:\Users\LevelAxis\Desktop\Clutch_Scraper_Project"
DUCKDB_FILE = os.path.join(BASE_DIR, "clutch_outreach.duckdb")

def build_reviews():
    t0 = time.time()
    print("Building unnested DuckDB reviews table...")
    conn = duckdb.connect(DUCKDB_FILE)

    conn.execute("""
        ALTER TABLE companies ADD COLUMN IF NOT EXISTS cert_count INT;
        UPDATE companies SET cert_count = CASE 
            WHEN certifications IS NULL OR certifications = '' THEN 0
            ELSE len(string_split(certifications, ','))
        END;
    """)

    conn.execute("DROP TABLE IF EXISTS reviews;")
    conn.execute("""
        CREATE TABLE reviews AS
        SELECT 
            c.company_name,
            c.profile_url,
            c.official_website,
            c.phone,
            c.locality,
            c.country,
            json_extract_string(r.elem, '$.title') as review_title,
            json_extract_string(r.elem, '$.author') as reviewer_name,
            TRY_CAST(json_extract_string(r.elem, '$.rating') AS DOUBLE) as review_rating,
            json_extract_string(r.elem, '$.body') as review_body
        FROM companies c,
        UNNEST(from_json(c.reviews_sample, 'JSON[]')) as r(elem)
        WHERE json_extract_string(r.elem, '$.author') IS NOT NULL 
          AND json_extract_string(r.elem, '$.author') != '';
    """)

    count = conn.execute("SELECT COUNT(*) FROM reviews").fetchone()[0]
    print(f"Done in {time.time()-t0:.2f}s! Total extracted review leads: {count:,}")
    conn.close()

if __name__ == "__main__":
    build_reviews()
