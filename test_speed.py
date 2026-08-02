import os
import time
import duckdb

BASE_DIR = r"C:\Users\LevelAxis\Desktop\Clutch_Scraper_Project"
DUCKDB_FILE = os.path.join(BASE_DIR, "clutch_outreach.duckdb")

def test_speed():
    t0 = time.time()
    conn = duckdb.connect(DUCKDB_FILE, read_only=True)
    conn.execute("PRAGMA threads=8;")
    print(f"Connection setup: {(time.time() - t0)*1000:.2f} ms")

    # Benchmark Meta Query
    t1 = time.time()
    total = conn.execute("SELECT COUNT(*) FROM companies").fetchone()[0]
    countries = conn.execute("SELECT DISTINCT country FROM companies WHERE country != '' ORDER BY country").fetchall()
    print(f"Meta query ({total} companies): {(time.time() - t1)*1000:.2f} ms")

    # Benchmark Company Search
    t2 = time.time()
    companies = conn.execute("""
        SELECT company_name, locality, country, rating, review_count, lead_score 
        FROM companies 
        WHERE country = 'US' AND rating >= 4.8 
        ORDER BY lead_score DESC 
        LIMIT 24
    """).fetchall()
    print(f"Company filter query (24 items): {(time.time() - t2)*1000:.2f} ms")

    # Benchmark Reviewer Lead Search
    t3 = time.time()
    reviews = conn.execute("""
        SELECT reviewer_name, reviewer_company, review_title, review_rating, vendor_agency_name 
        FROM reviews 
        WHERE LOWER(reviewer_name) LIKE '%john%' OR LOWER(reviewer_company) LIKE '%real estate%' 
        LIMIT 20
    """).fetchall()
    print(f"Reviewer search query (20 items): {(time.time() - t3)*1000:.2f} ms")

    conn.close()

if __name__ == "__main__":
    test_speed()
