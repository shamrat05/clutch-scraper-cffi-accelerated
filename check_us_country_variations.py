import duckdb

conn = duckdb.connect('clutch_outreach.duckdb', read_only=True)

print("--- All distinct country values in DB containing U or S or A ---")
rows = conn.execute("""
    SELECT country, COUNT(*) 
    FROM companies 
    WHERE LOWER(country) LIKE '%u%' OR LOWER(country) LIKE '%s%' OR LOWER(country) LIKE '%a%'
    GROUP BY 1 
    ORDER BY 2 DESC 
    LIMIT 30
""").fetchall()

for c, cnt in rows:
    print(f"  - country = '{c}': {cnt:,} companies")

print("\n--- Check how US cities are stored ---")
us_city_sample = conn.execute("""
    SELECT DISTINCT locality, country 
    FROM companies 
    WHERE country = 'US' AND locality != '' 
    LIMIT 15
""").fetchall()
for city, c in us_city_sample:
    print(f"  - city = '{city}', country = '{c}'")

conn.close()
