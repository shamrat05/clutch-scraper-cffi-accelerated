import os
import sys
import time
import duckdb

sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = r"C:\Users\LevelAxis\Desktop\Clutch_Scraper_Project"
DUCKDB_FILE = os.path.join(BASE_DIR, "clutch_outreach.duckdb")

def upgrade_duckdb_with_reviews():
    start_time = time.time()
    print("=" * 70)
    print("    UPGRADING DUCKDB WITH REVIEWS & CERTIFICATION INDEXES")
    print("=" * 70)

    conn = duckdb.connect(DUCKDB_FILE)

    # 1. Add cert_count column if not exists
    print("[+] Calculating certification counts...")
    conn.execute("""
        ALTER TABLE companies ADD COLUMN IF NOT EXISTS cert_count INT;
        UPDATE companies SET cert_count = CASE 
            WHEN certifications IS NULL OR certifications = '' THEN 0
            ELSE len(string_split(certifications, ','))
        END;
    """)

    # 2. Create unnested REVIEWS table for instant Google/LinkedIn style Reviewer Lead Search
    print("[+] Building unnested REVIEWS search table...")
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
            r.title as review_title,
            r.author as reviewer_name,
            TRY_CAST(r.rating AS DOUBLE) as review_rating,
            r.body as review_body
        FROM companies c,
        UNNEST(
            CAST(
                json_transform(
                    c.reviews_sample, 
                    '[{title: VARCHAR, author: VARCHAR, rating: VARCHAR, body: VARCHAR}]'
                ) AS STRUCT(title VARCHAR, author VARCHAR, rating VARCHAR, body VARCHAR)[]
            )
        ) as r
        WHERE r.author IS NOT NULL AND r.author != '';
    """)

    review_count = conn.execute("SELECT COUNT(*) FROM reviews").fetchone()[0]
    print(f"[+] Successfully extracted and indexed {review_count:,} client reviews into dedicated REVIEWS table!")

    print("[+] Creating indexes for Reviewer Lead Search...")
    conn.execute("CREATE INDEX idx_reviewer ON reviews (reviewer_name);")
    conn.execute("CREATE INDEX idx_rev_rating ON reviews (review_rating DESC);")
    conn.execute("CREATE INDEX idx_rev_company ON reviews (company_name);")

    conn.close()
    elapsed = time.time() - start_time
    print(f"[✔] DuckDB upgrade complete in {elapsed:.2f}s!")

if __name__ == "__main__":
    upgrade_duckdb_with_reviews()
