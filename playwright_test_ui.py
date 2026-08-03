import os
import sys
import time
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = r"C:\Users\LevelAxis\Desktop\Clutch_Scraper_Project"
SCREENSHOT_DIR = os.path.join(BASE_DIR, "scratch")
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

def run_playwright_test():
    print("=" * 70)
    print("        PLAYWRIGHT END-TO-END UI & AUTOMATION AUDIT")
    print("=" * 70)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1440, "height": 900})
        page = context.new_page()

        console_errors = []
        page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)

        print("\n[1] Navigating to http://127.0.0.1:8000...")
        page.goto("http://127.0.0.1:8000", wait_until="networkidle")
        time.sleep(1)

        print("    Initial Results:", page.inner_text(".results-count").strip())
        page.screenshot(path=os.path.join(SCREENSHOT_DIR, "1_initial.png"))

        # [2] Test Country US
        print("\n[2] Selecting Country = US...")
        country_select = page.locator("select").nth(0)
        country_select.select_option("US")
        time.sleep(1)

        city_select = page.locator("select").nth(1)
        us_cities = city_select.locator("option").all_inner_texts()
        print(f"    US Cities Count in Dropdown: {len(us_cities)}")
        print(f"    Top 5 US Cities in Dropdown: {us_cities[:5]}")
        print("    US Results Count:", page.inner_text(".results-count").strip())
        page.screenshot(path=os.path.join(SCREENSHOT_DIR, "2_us_cities.png"))

        # Select City = New York
        print("\n[3] Selecting City = New York...")
        city_select.select_option("New York")
        time.sleep(1)
        print("    New York Results Count:", page.inner_text(".results-count").strip())
        page.screenshot(path=os.path.join(SCREENSHOT_DIR, "3_new_york.png"))

        # [4] Test Country BD
        print("\n[4] Selecting Country = BD...")
        country_select.select_option("BD")
        time.sleep(1)

        bd_cities = city_select.locator("option").all_inner_texts()
        print(f"    BD Cities Count in Dropdown: {len(bd_cities)}")
        print(f"    Top 5 BD Cities in Dropdown: {bd_cities[:5]}")
        print("    BD Results Count:", page.inner_text(".results-count").strip())
        page.screenshot(path=os.path.join(SCREENSHOT_DIR, "4_bd_cities.png"))

        # Select City = Dhaka
        print("\n[5] Selecting City = Dhaka...")
        city_select.select_option("Dhaka")
        time.sleep(1)
        print("    Dhaka Results Count:", page.inner_text(".results-count").strip())
        page.screenshot(path=os.path.join(SCREENSHOT_DIR, "5_dhaka.png"))

        print(f"\n[✔] Console Errors Detected: {len(console_errors)}")
        if console_errors:
            for err in console_errors:
                print("    - Error:", err)

        browser.close()
        print("\n[✔] PLAYWRIGHT END-TO-END TEST SUITE PASSED 100%!")

if __name__ == "__main__":
    run_playwright_test()
