import time
import json
import re
import sys
import orjson
from bs4 import BeautifulSoup
from selectolax.parser import HTMLParser

sys.stdout.reconfigure(encoding="utf-8")

with open(r'C:\Users\LevelAxis\.gemini\antigravity-cli\brain\2cceb594-d798-42f2-a874-a90266528fa2\scratch\profile_brain_station_23.html', 'r', encoding='utf-8') as f:
    html = f.read()

profile_url = "https://clutch.co/profile/brain-station-23"

def parse_bs4(html_content, profile_url):
    soup = BeautifulSoup(html_content, "html.parser")
    json_lds = soup.find_all("script", type="application/ld+json")
    main_ld = {}
    for j in json_lds:
        try:
            if not j.string:
                continue
            data = json.loads(j.string)
            if isinstance(data, dict) and data.get("@type") in ["Organization", "LocalBusiness"]:
                main_ld = data
                break
        except Exception:
            pass
    return main_ld.get("name") or ""

JSON_LD_RE = re.compile(r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', re.DOTALL | re.IGNORECASE)

def parse_c_level(html_content, profile_url):
    main_ld = {}
    for match in JSON_LD_RE.finditer(html_content):
        script_text = match.group(1).strip()
        if not script_text:
            continue
        try:
            data = orjson.loads(script_text)
            if isinstance(data, dict) and data.get("@type") in ["Organization", "LocalBusiness"]:
                main_ld = data
                break
        except Exception:
            pass

    name = main_ld.get("name")
    if not name:
        tree = HTMLParser(html_content)
        h1 = tree.css_first("h1")
        name = h1.text().strip() if h1 else ""
    return name

iterations = 500
print(f"Benchmarking {iterations} page parses...")
sys.stdout.flush()

start_bs4 = time.time()
for _ in range(iterations):
    parse_bs4(html, profile_url)
time_bs4 = time.time() - start_bs4

start_c = time.time()
for _ in range(iterations):
    parse_c_level(html, profile_url)
time_c = time.time() - start_c

print(f"\n--- BENCHMARK RESULTS ---")
print(f"Before (BS4 + std json): {time_bs4:.4f} seconds ({iterations/time_bs4:.1f} pages/sec per core)")
print(f"After  (C Regex + orjson + selectolax): {time_c:.4f} seconds ({iterations/time_c:.1f} pages/sec per core)")
print(f"Speedup Factor: {time_bs4 / time_c:.2f}x FASTER!")
sys.stdout.flush()
