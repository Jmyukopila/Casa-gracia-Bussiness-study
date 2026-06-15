from playwright.sync_api import sync_playwright

def try_trivago(browser):
    page = browser.new_page()
    page.goto("https://www.trivago.com/en-US/srl?search=Cartagena-20016868&isLandingPage=false", timeout=30000)
    page.wait_for_timeout(5000)
    print("=== TRIVAGO ===")
    print("Title:", page.title())
    text = page.locator("body").text_content()
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    currency_lines = [l for l in lines if "$" in l]
    print(f"Lines with $: {len(currency_lines)}")
    for l in currency_lines[:20]:
        print(f"  {l[:150]}")

def try_hotelscom(browser):
    page = browser.new_page()
    page.goto(
        "https://www.hotels.com/search.do?destination=Cartagena%2C+Colombia&searchType=GEO&filters=price%3AL1",
        timeout=30000
    )
    page.wait_for_timeout(5000)
    print("\n=== HOTELS.COM ===")
    print("Title:", page.title())
    text = page.locator("body").text_content()
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    currency_lines = [l for l in lines if "$" in l]
    print(f"Lines with $: {len(currency_lines)}")
    for l in currency_lines[:20]:
        print(f"  {l[:150]}")

def try_expedia(browser):
    page = browser.new_page()
    page.goto(
        "https://www.expedia.com/Hotel-Search?destination=Cartagena%2C+Colombia&startDate=07%2F01%2F2026&endDate=07%2F04%2F2026&adults=2",
        timeout=30000
    )
    page.wait_for_timeout(5000)
    print("\n=== EXPEDIA ===")
    print("Title:", page.title())
    text = page.locator("body").text_content()
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    currency_lines = [l for l in lines if "$" in l]
    print(f"Lines with $: {len(currency_lines)}")
    for l in currency_lines[:20]:
        print(f"  {l[:150]}")

def try_priceline(browser):
    page = browser.new_page()
    page.goto(
        "https://www.priceline.com/search/hotels/region/Cartagena-Colombia/checkin=07-01-2026/checkout=07-04-2026",
        timeout=30000
    )
    page.wait_for_timeout(5000)
    print("\n=== PRICELINE ===")
    print("Title:", page.title())
    text = page.locator("body").text_content()
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    currency_lines = [l for l in lines if "$" in l]
    print(f"Lines with $: {len(currency_lines)}")
    for l in currency_lines[:20]:
        print(f"  {l[:150]}")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    try_trivago(browser)
    try_hotelscom(browser)
    try_expedia(browser)
    try_priceline(browser)
    browser.close()
