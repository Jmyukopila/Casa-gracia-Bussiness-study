from playwright.sync_api import sync_playwright
import json

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    
    # Kayak hotels search for Cartagena
    page.goto(
        "https://www.kayak.com/hotels/Cartagena,Colombia-c20223/2026-07-01/2026-07-04/2adults?sort=price_a",
        timeout=30000
    )
    page.wait_for_timeout(5000)
    
    print("Page title:", page.title())
    print("URL:", page.url())
    
    # Try to find all text
    text = page.locator("body").text_content()
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    currency_lines = [l for l in lines if "$" in l or "COP" in l or "USD" in l]
    print(f"\nTotal lines: {len(lines)}, Lines with currency: {len(currency_lines)}")
    for l in currency_lines[:40]:
        print(f"  {l[:200]}")
    
    # Check for hotel listings
    hotel_keywords = ["hotel", "Hotel", "Casa", "HOSTEL", "Inn"]
    hotel_lines = [l for l in lines if any(k in l for k in hotel_keywords)]
    print(f"\nLines with hotel keywords: {len(hotel_lines)}")
    for l in hotel_lines[:20]:
        print(f"  {l[:200]}")
    
    browser.close()
