import duckdb

conn = duckdb.connect('clutch_outreach.duckdb', read_only=True)

query = """
    SELECT COUNT(DISTINCT TRIM(locality))
    FROM companies 
    WHERE country = ? 
      AND locality != '' 
      AND locality NOT LIKE '%Ste%' 
      AND locality NOT LIKE '%Suite%' 
      AND locality NOT LIKE '%#%' 
      AND NOT regexp_matches(locality, '^[0-9]')
"""

for country_code in ['US', 'BD', 'GB', 'CA', 'AU', 'IN', 'DE']:
    cnt = conn.execute(query, [country_code]).fetchone()[0]
    print(f"  - Total Distinct Cities in {country_code}: {cnt:,}")

conn.close()
