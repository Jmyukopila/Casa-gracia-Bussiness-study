import asyncio, json, csv, os, sys, re, traceback
from datetime import datetime
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8')

ROOMS = {
    "Queen 101": "https://www.airbnb.mx/rooms/1197228721608888257",
    "Queen 203": "https://www.airbnb.mx/rooms/1247150160057099135",
    "King 202": "https://www.airbnb.mx/rooms/1265108254884566985",
    "Multiple 103": "https://www.airbnb.com.co/rooms/1202495221808518235",
}

OUTPUT = "data/airbnb_prices.csv"
results = []

async def try_room(browser, name, url):
    print(f"\n{'='*50}")
    print(f"  {name}")
    print(f"{'='*50}")

    context = await browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        locale="es-MX",
        viewport={"width": 1440, "height": 900},
    )
    page = await context.new_page()

    try:
        # Load page with 15s timeout
        await page.goto(url, timeout=15000, wait_until="domcontentloaded")
        await page.wait_for_timeout(3000)
        title = await page.title()
        print(f"  Title: {title[:80]}")

        # Try to see if page loaded properly
        body = await page.inner_text("body")
        print(f"  Body length: {len(body)}")

        if len(body) < 200 or "No pudimos encontrar" in body or "404" in body:
            print(f"  PAGE ERROR: {body[:200]}")
            return

        # Strategy 1: Try URL-based approach (add date params)
        date_params = [
            ("Julio", "2026-07-15", "2026-07-17"),
            ("Noviembre", "2026-11-01", "2026-11-03"),
            ("Diciembre", "2026-12-20", "2026-12-27"),
            ("Febrero", "2027-02-10", "2027-02-13"),
        ]

        for season, ci, co in date_params:
            print(f"  --- {season}: {ci} a {co} ---")
            price = await get_price_with_dates(page, ci, co)
            print(f"  PRICE: {price}")
            results.append({
                "room": name,
                "season": season,
                "checkin": ci,
                "checkout": co,
                "price_usd": price,
                "date_extracted": datetime.now().strftime("%Y-%m-%d"),
            })

    except Exception as e:
        print(f"  ERROR: {e}")
        traceback.print_exc()
    finally:
        await context.close()

async def get_price_with_dates(page, checkin, checkout):
    """Try to get price by navigating to URL with date params."""
    base_url = page.url.split("?")[0]
    date_url = f"{base_url}?check_in={checkin}&check_out={checkout}&adults=2"

    try:
        await page.goto(date_url, timeout=15000, wait_until="domcontentloaded")
        await page.wait_for_timeout(4000)
    except:
        print(f"    Timeout loading date URL, trying fallback...")
        return None

    text = await page.inner_text("body")

    # Try to find price
    patterns = [
        (r'\$(\d+(?:,\d+)?)\s*/\s*noche', lambda m: int(m.group(1).replace(",",""))),
        (r'\$(\d+(?:,\d+)?)\s*MXN', lambda m: int(m.group(1).replace(",",""))),
        (r'(\d+(?:,\d+)?)\s*MXN', lambda m: int(m.group(1).replace(",",""))),
        (r'COP\s*\$?(\d+(?:,\d+)?)', lambda m: int(m.group(1).replace(",",""))),
        (r'\$(\d+(?:,\d+)?)', lambda m: int(m.group(1).replace(",",""))),
    ]

    for pattern, extractor in patterns:
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            val = extractor(m)
            if val > 0:
                return val

    return None

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        for name, url in ROOMS.items():
            await try_room(browser, name, url)
            await asyncio.sleep(3)

        await browser.close()

    csv_path = "data/airbnb_prices.csv"
    os.makedirs("data", exist_ok=True)

    if results:
        keys = ["room", "season", "checkin", "checkout", "price_usd", "date_extracted"]
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=keys)
            w.writeheader()
            w.writerows(results)
        print(f"\nSaved {len(results)} prices to {csv_path}")
    else:
        print("\nNo prices extracted")

    print("\n=== RESULTS ===")
    for r in results:
        print(f"  {r['room']:15s} | {r['season']:15s} | ${r['price_usd']}")

asyncio.run(main())
