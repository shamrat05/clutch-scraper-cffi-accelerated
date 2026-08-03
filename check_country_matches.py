import duckdb

conn = duckdb.connect('clutch_outreach.duckdb', read_only=True)

print("--- Country matching in companies table ---")
for val in ['US', 'United States', 'BD', 'Bangladesh', 'GB', 'United Kingdom', 'CA', 'Canada']:
    cnt = conn.execute("SELECT COUNT(*) FROM companies WHERE country = ?", [val]).fetchone()[0]
    cnt_like = conn.execute("SELECT COUNT(*) FROM companies WHERE LOWER(country) LIKE ?", [f"%{val.lower()}%"]).fetchone()[0]
    print(f"  - country = '{val}': exact={cnt:,}, like={cnt_like:,}")

conn.close()
