import re
import orjson
from selectolax.parser import HTMLParser

with open(r"C:\Users\LevelAxis\.gemini\antigravity-cli\brain\2cceb594-d798-42f2-a874-a90266528fa2\scratch\profile_brain_station_23.html", "r", encoding="utf-8") as f:
    html = f.read()

tree = HTMLParser(html)

print("=== JSON-LD Reviews ===")
JSON_LD_RE = re.compile(r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', re.DOTALL | re.IGNORECASE)
for match in JSON_LD_RE.finditer(html):
    try:
        data = orjson.loads(match.group(1).strip())
        if isinstance(data, dict) and "review" in data:
            revs = data["review"]
            print(f"JSON-LD contains {len(revs)} reviews:")
            for r in revs:
                print(" - Author:", r.get("author", {}).get("name"), "| Title:", r.get("name"))
    except Exception:
        pass

print("\n=== HTML Review Cards ===")
review_elements = tree.css("[class*='review']")
print(f"Total HTML elements with class containing 'review': {len(review_elements)}")

titles = tree.css("h3, h4, .field-name-title, .review-title")
print(f"Found titles: {len(titles)}")
for t in titles[:15]:
    txt = t.text().strip()
    if txt and len(txt) > 5:
        print(" Title:", txt)
