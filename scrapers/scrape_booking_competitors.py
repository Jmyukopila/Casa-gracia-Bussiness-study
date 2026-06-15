from playwright.sync_api import sync_playwright
import json

# Search Booking.com for hotels in Manga, Cartagena with competitor prices
URLS = {
    "jul": "https://www.booking.com/searchresults.html?ss=Cartagena+de+Indias%2C+Colombia&checkin=2026-07-01&checkout=2026-07-04&group_adults=2&no_rooms=1&nflt=ht_id%3D204%3B",
    "nov": "https://www.booking.com/searchresults.html?ss=Cartagena+de+Indias%2C+Colombia&checkin=2026-11-20&checkout=2026-11-23&group_adults=2&no_rooms=1&nflt=ht_id%3D204%3B",
    "dec": "https://www.booking.com/searchresults.html?ss=Cartagena+de+Indias%2C+Colombia&checkin=2026-12-20&checkout=2026-12-23&group_adults=2&no_rooms=1&nflt=ht_id%3D204%3B",
    "feb": "https://www.booking.com/searchresults.html?ss=Cartagena+de+Indias%2C+Colombia&checkin=2027-02-10&checkout=2027-02-13&group_adults=2&no_rooms=1&nflt=ht_id%3D204%3B",
}

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    
    # Create a realistic browser context
    context = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        viewport={"width": 1920, "height": 1080},
        locale="en-US",
    )
    page = context.new_page()
    
    all_results = {}
    
    for season, url in URLS.items():
        print(f"\n=== Season: {season} ===")
        page.goto(url, timeout=30000)
        page.wait_for_timeout(4000)
        
        # Try to get hotel cards
        hotels = page.locator('[data-testid="property-card"]').all()
        print(f"  Hotels found: {len(hotels)}")
        
        season_results = []
        for i, hotel in enumerate(hotels[:15]):
            try:
                title_el = hotel.locator('[data-testid="title"]')
                title = title_el.text_content() if title_el.count() > 0 else "N/A"
                
                price_el = hotel.locator('[data-testid="price-and-discounted-price"]')
                price = price_el.text_content() if price_el.count() > 0 else "N/A"
                
                rating_el = hotel.locator('[data-testid="review-score"]')
                rating = rating_el.text_content() if rating_el.count() > 0 else "N/A"
                
                # Check if it's in Manga area
                subtitle_el = hotel.locator('[data-testid="subtitle"]')
                subtitle = subtitle_el.text_content() if subtitle_el.count() > 0 else ""
                
                season_results.append({
                    "title": title.strip() if title else "",
                    "price": price.strip().replace("\n", " ") if price else "",
                    "rating": rating.strip().replace("\n", " ") if rating else "",
                    "location": subtitle.strip() if subtitle else "",
                })
                
                print(f"  {i+1}. {title[:50]} | {price[:40]} | {rating[:30]}")
            except Exception as e:
                print(f"  {i+1}. Error: {e}")
        
        all_results[season] = season_results
    
    browser.close()
    
    with open("data/booking_competitor_prices.json", "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
    
    print("\nDone! Saved to data/booking_competitor_prices.json")
