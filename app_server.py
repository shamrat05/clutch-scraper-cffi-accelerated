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

# Shared C-level DuckDB connection pool & in-memory cache
GLOBAL_CONN = duckdb.connect(DUCKDB_FILE, read_only=True)
GLOBAL_CONN.execute("PRAGMA threads=8;")
GLOBAL_CONN.execute("PRAGMA max_memory='4GB';")

# Pre-calculate metadata cache on server startup for 0.01ms response time
META_CACHE = {
    "total_companies": GLOBAL_CONN.execute("SELECT COUNT(*) FROM companies").fetchone()[0],
    "countries": [r[0] for r in GLOBAL_CONN.execute("SELECT DISTINCT country FROM companies WHERE country != '' ORDER BY country").fetchall()],
    "price_ranges": [r[0] for r in GLOBAL_CONN.execute("SELECT DISTINCT price_range FROM companies WHERE price_range != '' ORDER BY price_range").fetchall()],
    "cities": [r[0] for r in GLOBAL_CONN.execute("SELECT DISTINCT TRIM(locality) FROM companies WHERE locality != '' ORDER BY 1 LIMIT 500").fetchall()]
}

def get_db():
    return GLOBAL_CONN

VITE_DIST_DIR = os.path.join(BASE_DIR, "frontend", "dist")

if os.path.exists(VITE_DIST_DIR):
    app.mount("/assets", StaticFiles(directory=os.path.join(VITE_DIST_DIR, "assets")), name="assets")

@app.post("/api/sync")
def trigger_sync():
    """Triggers live incremental update against Clutch sitemap index"""
    try:
        import run_clutch_incremental
        result = run_clutch_incremental.sync_incremental()
        return result
    except Exception as e:
        return {"status": "error", "message": str(e), "new_companies": 0, "duration_seconds": 0.05}

@app.get("/", response_class=HTMLResponse)
def index():
    if os.path.exists(os.path.join(VITE_DIST_DIR, "index.html")):
        with open(os.path.join(VITE_DIST_DIR, "index.html"), "r", encoding="utf-8") as f:
            return f.read()
    with open(os.path.join(BASE_DIR, "templates", "index.html"), "r", encoding="utf-8") as f:
        return f.read()

@app.get("/api/meta")
def get_meta():
    return META_CACHE

@app.get("/api/cities")
def get_cities(country: str = "", q: str = ""):
    conn = get_db()
    where_clauses = [
        "locality != ''",
        "locality NOT LIKE '%Ste%'",
        "locality NOT LIKE '%Suite%'",
        "locality NOT LIKE '%#%'",
        "NOT regexp_matches(locality, '^[0-9]')"
    ]
    params = []
    if country and country.strip():
        where_clauses.append("country = ?")
        params.append(country.strip())
    if q and q.strip():
        where_clauses.append("LOWER(locality) LIKE ?")
        params.append(f"%{q.strip().lower()}%")
    
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
    return [{"city": r[0], "count": r[1]} for r in rows if r[0]]

@app.get("/api/suggestions")
def get_suggestions(q: str = "", type: str = "company", country: str = ""):
    if not q or len(q.strip()) < 1:
        return []
    
    conn = get_db()
    term = f"%{q.strip().lower()}%"
    type_clean = type.lower().strip()
    
    if type_clean == "city":
        where_clauses = [
            "locality != ''",
            "LOWER(locality) LIKE ?",
            "locality NOT LIKE '%Ste%'",
            "locality NOT LIKE '%Suite%'",
            "locality NOT LIKE '%#%'",
            "NOT regexp_matches(locality, '^[0-9]')"
        ]
        params = [term]
        if country and country.strip():
            where_clauses.append("country = ?")
            params.append(country.strip())
        where_str = " AND ".join(where_clauses)
        sql = f"SELECT TRIM(locality), COUNT(*) AS cnt FROM companies WHERE {where_str} GROUP BY 1 ORDER BY cnt DESC LIMIT 10"
        return [r[0] for r in conn.execute(sql, params).fetchall()]

    elif type_clean == "reviewer":
        sql = "SELECT DISTINCT reviewer_name FROM reviews WHERE LOWER(reviewer_name) LIKE ? AND reviewer_name != '' ORDER BY 1 LIMIT 10"
        return [r[0] for r in conn.execute(sql, [term]).fetchall()]

    elif type_clean == "vendor":
        sql = "SELECT DISTINCT vendor_agency_name FROM reviews WHERE LOWER(vendor_agency_name) LIKE ? AND vendor_agency_name != '' ORDER BY 1 LIMIT 10"
        return [r[0] for r in conn.execute(sql, [term]).fetchall()]

    elif type_clean == "buyer_company":
        sql = "SELECT DISTINCT reviewer_company FROM reviews WHERE LOWER(reviewer_company) LIKE ? AND reviewer_company != '' ORDER BY 1 LIMIT 10"
        return [r[0] for r in conn.execute(sql, [term]).fetchall()]

    else:
        sql = "SELECT DISTINCT company_name FROM companies WHERE LOWER(company_name) LIKE ? AND company_name != '' ORDER BY 1 LIMIT 10"
        return [r[0] for r in conn.execute(sql, [term]).fetchall()]

@app.get("/api/companies")
def search_companies(
    search: str = "",
    country: str = "",
    city: str = "",
    price_range: str = "",
    min_rating: str = "",
    min_reviews: str = "",
    has_phone: bool = False,
    has_website: bool = False,
    sort_by: str = "lead_score",
    sort_order: str = "DESC",
    page: int = 1,
    limit: int = 24
):
    conn = get_db()
    where_clauses = ["1=1"]
    params = []

    if search and search.strip():
        s_like = f"%{search.strip().lower()}%"
        where_clauses.append("(LOWER(company_name) LIKE ? OR LOWER(locality) LIKE ? OR LOWER(services_offered) LIKE ?)")
        params.extend([s_like, s_like, s_like])
    if country and country.strip():
        where_clauses.append("country = ?")
        params.append(country.strip())
    if city and city.strip():
        where_clauses.append("LOWER(locality) LIKE ?")
        params.append(f"%{city.strip().lower()}%")
    if price_range and price_range.strip():
        where_clauses.append("price_range = ?")
        params.append(price_range.strip())
    if min_rating and min_rating.strip():
        try:
            where_clauses.append("rating >= ?")
            params.append(float(min_rating))
        except ValueError:
            pass
    if min_reviews and min_reviews.strip():
        try:
            where_clauses.append("review_count >= ?")
            params.append(int(min_reviews))
        except ValueError:
            pass
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
        "country": "country",
        "locality": "locality"
    }
    sort_col = allowed_sorts.get(sort_by, "lead_score")
    sort_dir = "DESC" if sort_order.upper() == "DESC" else "ASC"

    # Count matching query
    count_sql = f"SELECT COUNT(*) FROM companies WHERE {where_str}"
    count_row = conn.execute(count_sql, params).fetchone()
    total_matched = count_row[0] if count_row else 0

    offset = (page - 1) * limit
    data_sql = f"""
        SELECT 
            company_name, profile_url, official_website, phone, founding_year, 
            price_range, rating, review_count, locality, region, country, 
            services_offered, certifications, cert_count, team_leadership, lead_score,
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

    return {
        "total": total_matched,
        "page": page,
        "limit": limit,
        "total_pages": (total_matched + limit - 1) // limit if limit > 0 else 1,
        "items": items
    }

@app.get("/api/reviews")
def search_reviews(
    search: str = "",
    reviewer_company: str = "",
    country: str = "",
    min_rating: str = "",
    sort_by: str = "review_rating",
    sort_order: str = "DESC",
    page: int = 1,
    limit: int = 20
):
    """Google & LinkedIn style Client Buyer & Reviewer Lead Search Engine"""
    conn = get_db()
    where_clauses = ["1=1"]
    params = []

    if search and search.strip():
        s_like = f"%{search.strip().lower()}%"
        where_clauses.append("(LOWER(reviewer_name) LIKE ? OR LOWER(reviewer_company) LIKE ? OR LOWER(review_title) LIKE ? OR LOWER(review_body) LIKE ?)")
        params.extend([s_like, s_like, s_like, s_like])
    if reviewer_company and reviewer_company.strip():
        c_like = f"%{reviewer_company.strip().lower()}%"
        where_clauses.append("(LOWER(vendor_agency_name) LIKE ? OR LOWER(reviewer_company) LIKE ?)")
        params.extend([c_like, c_like])
    if country and country.strip():
        where_clauses.append("vendor_country = ?")
        params.append(country.strip())
    if min_rating and min_rating.strip():
        try:
            where_clauses.append("review_rating >= ?")
            params.append(float(min_rating))
        except ValueError:
            pass

    where_str = " AND ".join(where_clauses)
    
    allowed_sorts = {
        "review_rating": "review_rating",
        "reviewer_name": "reviewer_name",
        "reviewer_company": "reviewer_company"
    }
    sort_col = allowed_sorts.get(sort_by, "review_rating")
    sort_dir = "DESC" if sort_order.upper() == "DESC" else "ASC"

    try:
        count_sql = f"SELECT COUNT(*) FROM reviews WHERE {where_str}"
        total_matched = conn.execute(count_sql, params).fetchone()[0]

        offset = (page - 1) * limit
        data_sql = f"""
            SELECT 
                reviewer_name, reviewer_company, review_title, review_date, review_rating, review_body,
                vendor_agency_name, vendor_profile_url, vendor_website, vendor_phone, vendor_locality, vendor_country
            FROM reviews
            WHERE {where_str}
            ORDER BY {sort_col} {sort_dir} NULLS LAST
            LIMIT {limit} OFFSET {offset}
        """
        rows = conn.execute(data_sql, params).fetchall()
        cols = [column[0] for column in conn.description]
        items = [dict(zip(cols, r)) for r in rows]
    except Exception as e:
        print("[!] Exception in search_reviews:", e)
        total_matched = 0
        items = []

    return {
        "total": total_matched,
        "page": page,
        "limit": limit,
        "total_pages": (total_matched + limit - 1) // limit if limit > 0 else 1,
        "items": items
    }

@app.post("/api/export_reviews")
def export_reviews(payload: dict):
    search = payload.get("search", "")
    reviewer_company = payload.get("reviewer_company", "")
    country = payload.get("country", "")
    min_rating = payload.get("min_rating")
    selected_columns = payload.get("columns", [])
    export_format = payload.get("format", "csv").lower()

    conn = get_db()
    where_clauses = ["1=1"]
    params = []

    if search:
        s_like = f"%{search.strip().lower()}%"
        where_clauses.append("(LOWER(reviewer_name) LIKE ? OR LOWER(reviewer_company) LIKE ? OR LOWER(review_title) LIKE ? OR LOWER(review_body) LIKE ?)")
        params.extend([s_like, s_like, s_like, s_like])
    if reviewer_company:
        c_like = f"%{reviewer_company.strip().lower()}%"
        where_clauses.append("(LOWER(vendor_agency_name) LIKE ? OR LOWER(reviewer_company) LIKE ?)")
        params.extend([c_like, c_like])
    if country:
        where_clauses.append("vendor_country = ?")
        params.append(country)
    if min_rating:
        where_clauses.append("review_rating >= ?")
        params.append(float(min_rating))

    where_str = " AND ".join(where_clauses)
    
    all_valid_cols = [
        "reviewer_name", "reviewer_company", "review_title", "review_rating", "review_body",
        "vendor_agency_name", "vendor_profile_url", "vendor_website", "vendor_phone", "vendor_locality", "vendor_country"
    ]
    
    cols_to_fetch = [c for c in selected_columns if c in all_valid_cols] or all_valid_cols

    cols_str = ", ".join(cols_to_fetch)
    query_sql = f"SELECT {cols_str} FROM reviews WHERE {where_str} ORDER BY review_rating DESC LIMIT 50000"
    rows = conn.execute(query_sql, params).fetchall()

    output = io.StringIO()
    if export_format == "csv":
        writer = csv.writer(output)
        writer.writerow(cols_to_fetch)
        for r in rows:
            writer.writerow(r)
        media_type = "text/csv"
        filename = "clutch_client_buyer_leads.csv"
        content = output.getvalue()
    elif export_format == "json":
        items = [dict(zip(cols_to_fetch, r)) for r in rows]
        content = json.dumps(items, indent=2, ensure_ascii=False)
        media_type = "application/json"
        filename = "clutch_client_buyer_leads.json"
    else:
        items = [json.dumps(dict(zip(cols_to_fetch, r)), ensure_ascii=False) for r in rows]
        content = "\n".join(items)
        media_type = "application/x-ndjson"
        filename = "clutch_client_buyer_leads.jsonl"

    return Response(
        content=content,
        media_type=media_type,
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

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
