import time
import duckdb

def benchmark_scaling():
    print("=" * 70)
    print("      DUCKDB C++ SIMD SCALABILITY & MIGRATION SPEED TEST")
    print("=" * 70)

    conn = duckdb.connect()
    conn.execute("PRAGMA threads=8;")

    print("[+] Generating 1,000,000 synthetic JSON lead objects in memory...")
    t0 = time.time()
    conn.execute("""
        CREATE TABLE synthetic_data AS
        SELECT 
            'Agency_' || range AS company_name,
            'https://clutch.co/profile/agency-' || range AS profile_url,
            '[{"author":"Decision Maker ' || range || '", "title":"Project ' || range || ' for Enterprise", "rating":"5.0", "body":"Great work done"}]' AS reviews_sample
        FROM range(1000000);
    """)
    print(f"    1,000,000 records generated in: {(time.time() - t0):.2f}s")

    print("[+] Executing C++ SIMD JSON unnest migration query over 1,000,000 records...")
    t1 = time.time()
    conn.execute("""
        CREATE TABLE migrated_reviews AS
        SELECT 
            json_extract_string(rev_elem, '$.author') AS reviewer_name,
            json_extract_string(rev_elem, '$.title') AS review_title,
            company_name AS vendor_agency_name
        FROM (
            SELECT company_name, UNNEST(from_json(reviews_sample, '["JSON"]')) AS rev_elem
            FROM synthetic_data
        );
    """)
    t_migration = time.time() - t1
    print(f"    1,000,000 leads migrated in: {t_migration:.2f} seconds!")

    print("[+] Testing B-Tree Search speed over 1,000,000 migrated records...")
    t2 = time.time()
    res = conn.execute("SELECT * FROM migrated_reviews WHERE vendor_agency_name = 'Agency_999999'").fetchall()
    t_query = (time.time() - t2) * 1000
    print(f"    Query result: {res[0] if res else 'None'}")
    print(f"    Search Query Execution Time: {t_query:.2f} milliseconds!")

    conn.close()

if __name__ == "__main__":
    benchmark_scaling()
