import duckdb

conn = duckdb.connect('clutch_outreach.duckdb', read_only=True)

where_clauses = [
    "locality != ''",
    "locality NOT LIKE '%Ste%'",
    "locality NOT LIKE '%Suite%'",
    "locality NOT LIKE '%#%'",
    "NOT regexp_matches(locality, '^[0-9]')"
]
where_clauses.append("country = ?")
params = ['BD']

where_str = " AND ".join(where_clauses)
sql = f"""
    SELECT TRIM(locality) AS city, COUNT(*) AS cnt 
    FROM companies 
    WHERE {where_str} 
    GROUP BY 1 
    ORDER BY cnt DESC 
    LIMIT 200
"""

rows = conn.execute(sql, params).fetchall()
print("Total rows returned for BD:", len(rows))
if rows:
    print("Sample row 0:", rows[0], "Type:", type(rows[0]), "Len:", len(rows[0]))
    print("Formatted result sample:", [{"city": r[0], "count": r[1]} for r in rows[:5] if r[0]])

conn.close()
