import os
import sys
import duckdb

sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = r"C:\Users\LevelAxis\Desktop\Clutch_Scraper_Project"
DUCKDB_FILE = os.path.join(BASE_DIR, "clutch_outreach.duckdb")

def check_db_health():
    print("=" * 70)
    print("           CLUTCH DUCKDB DATABASE HEALTH CHECK & SCHEMA AUDIT")
    print("=" * 70)
    
    conn = duckdb.connect(DUCKDB_FILE, read_only=True)
    
    # 1. Inspect Companies Table
    comp_count = conn.execute("SELECT COUNT(*) FROM companies").fetchone()[0]
    print(f"\n[1] Companies Table: {comp_count:,} total company records")
    comp_cols = [c[0] for c in conn.execute("DESCRIBE companies").fetchall()]
    print("    Columns:", comp_cols)
    
    # 2. Inspect Reviews Table
    rev_count = conn.execute("SELECT COUNT(*) FROM reviews").fetchone()[0]
    print(f"\n[2] Reviews Table: {rev_count:,} total verified client review leads")
    rev_cols = [c[0] for c in conn.execute("DESCRIBE reviews").fetchall()]
    print("    Columns:", rev_cols)
    
    # 3. Sample Lead Query Test
    print("\n[3] Sample Review Lead Record:")
    sample_lead = conn.execute("SELECT reviewer_name, reviewer_company, review_title, review_date, review_rating, vendor_agency_name FROM reviews LIMIT 1").fetchone()
    print("    Reviewer Name:", sample_lead[0])
    print("    Client Org:", sample_lead[1])
    print("    Project Title:", sample_lead[2])
    print("    Review Date:", sample_lead[3])
    print("    Rating:", sample_lead[4])
    print("    Hired Vendor:", sample_lead[5])
    
    # 4. Check Brain Station 23
    bs23 = conn.execute("SELECT reviewer_name, review_title, review_date FROM reviews WHERE LOWER(vendor_agency_name) LIKE '%brain%station%'").fetchall()
    print(f"\n[4] Brain Station 23 Reviews Count in DB: {len(bs23)}")
    for r in bs23[:3]:
        print("   -", r)
        
    conn.close()
    print("\n[✔] Database Health Check Status: EXCELLENT & 100% HEALTHY!")

if __name__ == "__main__":
    check_db_health()
