import os
import json
import duckdb
from fastapi import FastAPI, Query, HTTPException, Response
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
import csv
import io
import orjson

BASE_DIR = r"C:\Users\LevelAxis\Desktop\Clutch_Scraper_Project"
DUCKDB_FILE = os.path.join(BASE_DIR, "clutch_outreach.duckdb")

app = FastAPI(title="Clutch Intelligence & Lead Generation Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    return duckdb.connect(DUCKDB_FILE, read_only=True)

# Mount static and template paths
os.makedirs(os.path.join(BASE_DIR, "static"), exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, "templates"), exist_ok=True)
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

@app.get("/", response_class=HTMLResponse)
def index():
    with open(os.path.join(BASE_DIR, "templates", "index.html"), "r", encoding="utf-8") as f:
        return f.read()

@app.get("/api/meta")
def get_meta():
    conn = get_db()
    total_count = conn.execute("SELECT COUNT(*) FROM companies").fetchone()[0]
    countries = [r[0] for r in conn.execute("SELECT DISTINCT country FROM companies WHERE country != '' ORDER BY country").fetchall()]
    price_ranges = [r[0] for r in conn.execute("SELECT DISTINCT price_range FROM companies WHERE price_range != '' ORDER BY price_range").fetchall()]
    conn.close()
    return {
        "total_companies": total_count,
        "countries": countries,
        "price_ranges": price_ranges
    }

@app.get("/api/companies")
def search_companies(
    search: Optional[str] = "",
    country: Optional[str] = "",
    price_range: Optional[str] = "",
    min_rating: Optional[float] = None,
    min_reviews: Optional[int] = None,
    has_phone: Optional[bool] = False,
    has_website: Optional[bool] = False,
    sort_by: Optional[str] = "lead_score",
    sort_order: Optional[str] = "DESC",
    page: int = 1,
    limit: int = 24
):
    conn = get_db()
    where_clauses = ["1=1"]
    params = []

    if search:
        s_like = f"%{search.strip().lower()}%"
        where_clauses.append("(LOWER(company_name) LIKE ? OR LOWER(locality) LIKE ? OR LOWER(services_offered) LIKE ?)")
        params.extend([s_like, s_like, s_like])
    if country:
        where_clauses.append("country = ?")
        params.append(country)
    if price_range:
        where_clauses.append("price_range = ?")
        params.append(price_range)
    if min_rating is not None and min_rating > 0:
        where_clauses.append("rating >= ?")
        params.append(min_rating)
    if min_reviews is not None and min_reviews > 0:
        where_clauses.append("review_count >= ?")
        params.append(min_reviews)
    if has_phone:
        where_clauses.append("phone != ''")
    if has_website:
        where_clauses.append("official_website != ''")

    where_str = " AND ".join(where_clauses)
    
    # Allowed sort columns
    allowed_sorts = {
        "company_name": "company_name",
        "rating": "rating",
        "review_count": "review_count",
        "lead_score": "lead_score",
        "founding_year": "founding_year",
        "country": "country"
    }
    sort_col = allowed_sorts.get(sort_by, "lead_score")
    sort_dir = "DESC" if sort_order.upper() == "DESC" else "ASC"

    # Count matching query
    count_sql = f"SELECT COUNT(*) FROM companies WHERE {where_str}"
    total_matched = conn.execute(count_sql, params).fetchone()[0]

    offset = (page - 1) * limit
    data_sql = f"""
        SELECT 
            company_name, profile_url, official_website, phone, founding_year, 
            price_range, rating, review_count, locality, region, country, 
            services_offered, certifications, team_leadership, lead_score,
            total_reviews_extracted, description, reviews_sample
        FROM companies 
        WHERE {where_str} 
        ORDER BY {sort_col} {sort_dir} NULLS LAST
        LIMIT {limit} OFFSET {offset}
    """
    rows = conn.execute(data_sql, params).fetchall()
    cols = [column[0] for column in conn.description]
    
    items = []
    for row in rows:
        item = dict(zip(cols, row))
        try:
            item["reviews_sample"] = orjson.loads(item["reviews_sample"]) if item["reviews_sample"] else []
        except Exception:
            item["reviews_sample"] = []
        items.append(item)

    conn.close()
    return {
        "total": total_matched,
        "page": page,
        "limit": limit,
        "total_pages": (total_matched + limit - 1) // limit if limit > 0 else 1,
        "items": items
    }

@app.post("/api/export")
def export_companies(payload: dict):
    search = payload.get("search", "")
    country = payload.get("country", "")
    price_range = payload.get("price_range", "")
    min_rating = payload.get("min_rating")
    min_reviews = payload.get("min_reviews")
    has_phone = payload.get("has_phone", False)
    has_website = payload.get("has_website", False)
    selected_columns = payload.get("columns", [])
    export_format = payload.get("format", "csv").lower()

    conn = get_db()
    where_clauses = ["1=1"]
    params = []

    if search:
        s_like = f"%{search.strip().lower()}%"
        where_clauses.append("(LOWER(company_name) LIKE ? OR LOWER(locality) LIKE ? OR LOWER(services_offered) LIKE ?)")
        params.extend([s_like, s_like, s_like])
    if country:
        where_clauses.append("country = ?")
        params.append(country)
    if price_range:
        where_clauses.append("price_range = ?")
        params.append(price_range)
    if min_rating:
        where_clauses.append("rating >= ?")
        params.append(float(min_rating))
    if min_reviews:
        where_clauses.append("review_count >= ?")
        params.append(int(min_reviews))
    if has_phone:
        where_clauses.append("phone != ''")
    if has_website:
        where_clauses.append("official_website != ''")

    where_str = " AND ".join(where_clauses)
    
    all_valid_cols = [
        "company_name", "profile_url", "official_website", "phone", "founding_year",
        "price_range", "rating", "review_count", "street_address", "locality", "region",
        "postcode", "country", "services_offered", "certifications", "team_leadership",
        "lead_score", "description"
    ]
    
    if selected_columns:
        cols_to_fetch = [c for c in selected_columns if c in all_valid_cols]
    else:
        cols_to_fetch = all_valid_cols

    if not cols_to_fetch:
        cols_to_fetch = ["company_name", "official_website", "phone", "locality", "country", "rating"]

    cols_str = ", ".join(cols_to_fetch)
    query_sql = f"SELECT {cols_str} FROM companies WHERE {where_str} ORDER BY lead_score DESC LIMIT 50000"
    rows = conn.execute(query_sql, params).fetchall()
    conn.close()

    output = io.StringIO()
    if export_format == "csv":
        writer = csv.writer(output)
        writer.writerow(cols_to_fetch)
        for r in rows:
            writer.writerow(r)
        media_type = "text/csv"
        filename = "clutch_leads_export.csv"
        content = output.getvalue()
    elif export_format == "tsv":
        writer = csv.writer(output, delimiter="\t")
        writer.writerow(cols_to_fetch)
        for r in rows:
            writer.writerow(r)
        media_type = "text/tab-separated-values"
        filename = "clutch_leads_export.tsv"
        content = output.getvalue()
    elif export_format == "json":
        items = [dict(zip(cols_to_fetch, r)) for r in rows]
        content = json.dumps(items, indent=2, ensure_ascii=False)
        media_type = "application/json"
        filename = "clutch_leads_export.json"
        content = content
    elif export_format == "jsonl":
        items = [json.dumps(dict(zip(cols_to_fetch, r)), ensure_ascii=False) for r in rows]
        content = "\n".join(items)
        media_type = "application/x-ndjson"
        filename = "clutch_leads_export.jsonl"
    else:
        raise HTTPException(status_code=400, detail="Invalid format")

    return Response(
        content=content,
        media_type=media_type,
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
