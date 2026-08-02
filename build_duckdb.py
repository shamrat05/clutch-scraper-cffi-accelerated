import os
import sys
import time
import duckdb
import orjson

sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = r"C:\Users\LevelAxis\Desktop\Clutch_Scraper_Project"
JSONL_FILE = os.path.join(BASE_DIR, "Clutch_218k_Companies_Deep_Details.jsonl")
DUCKDB_FILE = os.path.join(BASE_DIR, "clutch_outreach.duckdb")

def build_duckdb_database():
    start_time = time.time()
    print("=" * 70)
    print("      BUILDING DUCKDB HIGH-PERFORMANCE OUTREACH DATABASE")
    print("=" * 70)

    if not os.path.exists(JSONL_FILE):
        print(f"[!] Target dataset {JSONL_FILE} not found!")
        return

    if os.path.exists(DUCKDB_FILE):
        try:
            os.remove(DUCKDB_FILE)
            print("[+] Removed old DuckDB database file.")
        except Exception:
            pass

    conn = duckdb.connect(DUCKDB_FILE)

    print("[+] Creating DuckDB table schema and loading JSONL data...")
    # Fast native JSON import using DuckDB
    jsonl_path = JSONL_FILE.replace("\\", "/")
    conn.execute(f"""
        CREATE TABLE companies AS 
        SELECT 
            company_name,
            profile_url,
            official_website,
            phone,
            founding_year,
            price_range,
            rating,
            review_count,
            street_address,
            locality,
            region,
            postcode,
            country,
            services_offered,
            certifications,
            team_leadership,
            total_reviews_extracted,
            reviews_sample,
            description,
            CASE 
                WHEN official_website != '' AND phone != '' AND rating >= 4.8 AND review_count >= 10 THEN 95
                WHEN official_website != '' AND phone != '' THEN 85
                WHEN official_website != '' THEN 70
                ELSE 50
            END as lead_score
        FROM read_json_auto('{jsonl_path}', columns={{
            'company_name': 'VARCHAR',
            'profile_url': 'VARCHAR',
            'official_website': 'VARCHAR',
            'phone': 'VARCHAR',
            'founding_year': 'VARCHAR',
            'price_range': 'VARCHAR',
            'rating': 'DOUBLE',
            'review_count': 'INT',
            'street_address': 'VARCHAR',
            'locality': 'VARCHAR',
            'region': 'VARCHAR',
            'postcode': 'VARCHAR',
            'country': 'VARCHAR',
            'services_offered': 'VARCHAR',
            'certifications': 'VARCHAR',
            'team_leadership': 'VARCHAR',
            'total_reviews_extracted': 'INT',
            'reviews_sample': 'VARCHAR',
            'description': 'VARCHAR'
        }}, ignore_errors=true);
    """)

    count = conn.execute("SELECT COUNT(*) FROM companies").fetchone()[0]
    print(f"[+] Loaded {count:,} company profiles into DuckDB table.")

    print("[+] Creating high-speed multi-column B-tree indexes...")
    conn.execute("CREATE INDEX idx_country ON companies (country);")
    conn.execute("CREATE INDEX idx_rating ON companies (rating DESC);")
    conn.execute("CREATE INDEX idx_reviews ON companies (review_count DESC);")
    conn.execute("CREATE INDEX idx_score ON companies (lead_score DESC);")

    conn.close()
    elapsed = time.time() - start_time
    size_mb = os.path.getsize(DUCKDB_FILE) / (1024 * 1024)
    print(f"[✔] DuckDB database created successfully in {elapsed:.2f}s! Size: {size_mb:.2f} MB")

if __name__ == "__main__":
    build_duckdb_database()
