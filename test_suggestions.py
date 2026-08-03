import duckdb

conn = duckdb.connect('clutch_outreach.duckdb', read_only=True)

print("--- Distinct Cities for US ---")
cities = [r[0] for r in conn.execute("SELECT DISTINCT locality FROM companies WHERE country='US' AND locality != '' ORDER BY locality LIMIT 15").fetchall()]
print(cities)

print("\n--- Matching Company Suggestions for 'brain' ---")
companies = [r[0] for r in conn.execute("SELECT DISTINCT company_name FROM companies WHERE LOWER(company_name) LIKE 'brain%' ORDER BY company_name LIMIT 10").fetchall()]
print(companies)

print("\n--- Matching Reviewer Suggestions for 'las' ---")
reviewers = [r[0] for r in conn.execute("SELECT DISTINCT reviewer_name FROM reviews WHERE LOWER(reviewer_name) LIKE 'las%' ORDER BY reviewer_name LIMIT 10").fetchall()]
print(reviewers)

print("\n--- Matching Vendor Agency Suggestions for 'viser' ---")
vendors = [r[0] for r in conn.execute("SELECT DISTINCT vendor_agency_name FROM reviews WHERE LOWER(vendor_agency_name) LIKE 'viser%' ORDER BY vendor_agency_name LIMIT 10").fetchall()]
print(vendors)

conn.close()
