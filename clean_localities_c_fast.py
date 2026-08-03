import os
import sys
import time
import duckdb

sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = r"C:\Users\LevelAxis\Desktop\Clutch_Scraper_Project"
DUCKDB_FILE = os.path.join(BASE_DIR, "clutch_outreach.duckdb")

def clean_c_fast():
    t0 = time.time()
    print("[+] Running C++ SIMD locality cleanup in DuckDB...")
    conn = duckdb.connect(DUCKDB_FILE)
    conn.execute("PRAGMA threads=8;")
    
    conn.execute(r"""
        UPDATE companies 
        SET locality = TRIM(regexp_replace(locality, '^[,\s\-\.#]+|,\s*(?:United States|USA|United Kingdom|UK|Canada|Australia|Germany|France|India|Bangladesh|Spain|Italy|Netherlands|Singapore|UAE|Dubai|Brazil).*$', '', 'i'))
        WHERE locality != '';
    """)

    conn.execute("CREATE INDEX IF NOT EXISTS idx_locality ON companies (locality);")

    sample = [r[0] for r in conn.execute("SELECT DISTINCT locality FROM companies WHERE country='US' AND locality!='' ORDER BY locality LIMIT 15").fetchall()]
    conn.close()

    elapsed = time.time() - t0
    print(f"[✔] Locality cleaned in {elapsed:.2f}s! US Cities sample:", sample)

if __name__ == "__main__":
    clean_c_fast()
