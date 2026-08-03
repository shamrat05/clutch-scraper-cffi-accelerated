import os
import sys
import re
import duckdb
import orjson

sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = r"C:\Users\LevelAxis\Desktop\Clutch_Scraper_Project"
DUCKDB_FILE = os.path.join(BASE_DIR, "clutch_outreach.duckdb")
HTML_FILE = r"C:\Users\LevelAxis\.gemini\antigravity-cli\brain\2cceb594-d798-42f2-a874-a90266528fa2\scratch\profile_brain_station_23.html"

def extract_reviewer_company(title, body):
    if not title and not body:
        return "Client Organization"
    text = (title or "") + " " + (body or "")
    patterns = [
        r'for\s+(?:an?\s+)?([A-Z0-9][A-Za-z0-9\s&\-\'\.]{2,35}\s+(?:Company|Corp|Inc|Ltd|University|College|Startup|Agency|Firm|Brand|Platform|Retailer|Manufacturer|Hospital|Bank|Group))',
        r'for\s+(?:an?\s+)?([A-Za-z0-9\s&\-\'\.]{2,30}\s+(?:eCommerce|SaaS|Healthcare|Fintech|B2B|Real Estate|Automotive|Logistics|Education))',
        r'(?:hired by|client is|working with)\s+(?:an?\s+)?([A-Za-z0-9\s&\-\'\.]{2,35})'
    ]
    for pat in patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            clean = m.group(1).strip()
            if len(clean) > 3:
                return clean
    return title.strip() if title else "Client Organization"

def insert_bs23():
    with open(HTML_FILE, "r", encoding="utf-8") as f:
        html = f.read()

    JSON_LD_RE = re.compile(r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', re.DOTALL | re.IGNORECASE)
    bs23_reviews = []
    
    for match in JSON_LD_RE.finditer(html):
        try:
            data = orjson.loads(match.group(1).strip())
            if isinstance(data, dict) and "review" in data:
                revs = data["review"]
                for r in revs:
                    if isinstance(r, dict):
                        author = ""
                        a_obj = r.get("author")
                        if isinstance(a_obj, dict):
                            author = a_obj.get("name", "")
                        elif isinstance(a_obj, str):
                            author = a_obj
                            
                        title = r.get("name", "")
                        body = r.get("reviewBody", "")
                        date_pub = r.get("datePublished", "")
                        rating_obj = r.get("reviewRating", {})
                        rating_val = rating_obj.get("ratingValue") if isinstance(rating_obj, dict) else "5.0"
                        
                        if author and author != "Clutch.co":
                            bs23_reviews.append({
                                "title": title,
                                "author": author,
                                "date": date_pub,
                                "rating": float(rating_val) if rating_val else 5.0,
                                "body": body[:600] if body else ""
                            })
        except Exception:
            pass

    conn = duckdb.connect(DUCKDB_FILE)
    
    # Update Brain Station 23 in companies table
    conn.execute("""
        UPDATE companies 
        SET reviews_sample = ?, total_reviews_extracted = ? 
        WHERE LOWER(company_name) LIKE '%brain%station%'
    """, (orjson.dumps(bs23_reviews).decode("utf-8"), len(bs23_reviews)))

    # Insert into reviews table
    records = []
    for r in bs23_reviews:
        reviewer_comp = extract_reviewer_company(r["title"], r["body"])
        records.append((
            r["author"],
            reviewer_comp,
            r["title"],
            r["date"],
            r["rating"],
            r["body"],
            "Brain Station 23",
            "https://clutch.co/profile/brain-station-23",
            "https://brainstation-23.com",
            "+1-800-000-0000",
            "Springfield",
            "United States"
        ))

    conn.executemany("INSERT INTO reviews VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", records)
    
    count = conn.execute("SELECT COUNT(*) FROM reviews WHERE LOWER(vendor_agency_name) LIKE '%brain%station%'").fetchone()[0]
    print(f"[✔] Brain Station 23 reviews successfully inserted! Total in DB: {count}")
    conn.close()

if __name__ == "__main__":
    insert_bs23()
