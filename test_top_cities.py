import duckdb

conn = duckdb.connect('clutch_outreach.duckdb', read_only=True)

print("--- Top 20 US Cities by Agency Count ---")
query_us = """
    SELECT TRIM(locality) AS city, COUNT(*) AS cnt 
    FROM companies 
    WHERE country='US' 
      AND locality != '' 
      AND locality NOT LIKE '%Ste%' 
      AND locality NOT LIKE '%Suite%' 
      AND locality NOT LIKE '%#%' 
      AND NOT regexp_matches(locality, '^[0-9]')
    GROUP BY 1 
    ORDER BY cnt DESC 
    LIMIT 20
"""
rows_us = conn.execute(query_us).fetchall()
for city, cnt in rows_us:
    print(f"  - {city}: {cnt:,} agencies")

print("\n--- Top 20 Global Cities by Agency Count ---")
query_global = """
    SELECT TRIM(locality) AS city, COUNT(*) AS cnt 
    FROM companies 
    WHERE locality != '' 
      AND locality NOT LIKE '%Ste%' 
      AND locality NOT LIKE '%Suite%' 
      AND locality NOT LIKE '%#%' 
      AND NOT regexp_matches(locality, '^[0-9]')
    GROUP BY 1 
    ORDER BY cnt DESC 
    LIMIT 20
"""
rows_global = conn.execute(query_global).fetchall()
for city, cnt in rows_global:
    print(f"  - {city}: {cnt:,} agencies")

conn.close()
