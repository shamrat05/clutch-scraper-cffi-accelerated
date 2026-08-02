from curl_cffi import requests
from bs4 import BeautifulSoup
import json
import orjson
import re

url = "https://clutch.co/profile/ignite-visibility"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

JSON_LD_RE = re.compile(r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', re.DOTALL | re.IGNORECASE)

all_reviews = []

# Fetch page 0 to page 5
for page_num in range(5):
    page_url = f"{url}?page={page_num}#reviews"
    r = requests.get(page_url, impersonate="chrome124", headers=headers, timeout=10)
    print(f"Page {page_num} Status: {r.status_code}")
    
    # Check JSON-LD reviews
    for match in JSON_LD_RE.finditer(r.text):
        try:
            data = orjson.loads(match.group(1).strip())
            if isinstance(data, dict) and 'review' in data:
                revs = data['review']
                print(f"  JSON-LD Page {page_num} found {len(revs)} reviews")
                for rev in revs:
                    title = rev.get('name')
                    if title and title not in [r['title'] for r in all_reviews]:
                        all_reviews.append({'title': title, 'rating': rev.get('reviewRating', {}).get('ratingValue'), 'body': rev.get('reviewBody', '')[:100]})
        except Exception as e:
            pass

    # Check DOM review cards
    soup = BeautifulSoup(r.text, 'html.parser')
    review_cards = soup.find_all(class_=lambda c: c and ('review' in c or 'profile-review' in c or 'review-card' in c))
    print(f"  DOM Page {page_num} review nodes: {len(review_cards)}")

print(f"\nTotal Unique Reviews Collected across 5 pages: {len(all_reviews)}")
for rev in all_reviews[:5]:
    print(" -", rev['title'], "| Rating:", rev['rating'])
