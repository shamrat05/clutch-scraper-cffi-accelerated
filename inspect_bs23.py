import duckdb

conn = duckdb.connect('clutch_outreach.duckdb', read_only=True)
bs23 = conn.execute("SELECT company_name, rating, review_count, reviews_sample FROM companies WHERE LOWER(company_name) LIKE '%brain%station%'").fetchall()
print(f"Found {len(bs23)} companies matching 'brain station':")
for r in bs23:
    print("Company Name:", r[0])
    print("Rating:", r[1], "Review Count:", r[2])
    print("Reviews Sample:", r[3])

revs = conn.execute("SELECT vendor_agency_name, reviewer_name, review_title FROM reviews WHERE LOWER(vendor_agency_name) LIKE '%brain%station%'").fetchall()
print(f"\nFound {len(revs)} reviews in reviews table for 'brain station':")
for r in revs:
    print(r)
