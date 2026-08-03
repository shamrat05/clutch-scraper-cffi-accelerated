import duckdb
import orjson
import sys

sys.stdout.reconfigure(encoding="utf-8")

conn = duckdb.connect('clutch_outreach.duckdb', read_only=True)

print("[+] Counting total companies with reviews_sample...")
companies_with_reviews = conn.execute("""
    SELECT count(*) 
    FROM companies 
    WHERE reviews_sample IS NOT NULL AND reviews_sample != '' AND reviews_sample != '[]'
""").fetchone()[0]
print(f"Companies with non-empty reviews_sample: {companies_with_reviews:,}")

print("\n[+] Counting total individual review items inside companies table...")
rows = conn.execute("""
    SELECT reviews_sample 
    FROM companies 
    WHERE reviews_sample IS NOT NULL AND reviews_sample != '' AND reviews_sample != '[]'
""").fetchall()

total_reviews_found = 0
valid_author_reviews = 0

for (raw_json,) in rows:
    try:
        parsed = orjson.loads(raw_json)
        if isinstance(parsed, list):
            total_reviews_found += len(parsed)
            for r in parsed:
                if isinstance(r, dict):
                    if r.get("title") or r.get("body") or r.get("author"):
                        valid_author_reviews += 1
    except Exception:
        pass

print(f"Total Review Items Found in JSON: {total_reviews_found:,}")
print(f"Valid Review Items with Content: {valid_author_reviews:,}")

conn.close()
