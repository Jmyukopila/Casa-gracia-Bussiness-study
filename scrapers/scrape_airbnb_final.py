import asyncio, csv, os, sys, re
from datetime import datetime
from playwright.async_api import async_playwright
sys.stdout.reconfigure(encoding='utf-8')

ROOMS = {
    "Queen 101": "https://www.airbnb.mx/rooms/1197228721608888257",
    "Queen 203": "https://www.airbnb.mx/rooms/1247150160057099135",
    "King 202": "https://www.airbnb.mx/rooms/1265108254884566985",
    "Multiple 103": "https://www.airbnb.com.co/rooms/1202495221808518235",
}

DATE_SLUGS = [
    ("Julio (alta)", "2026-07-15", "2026-07-17", 2),
    ("Noviembre (Festival)", "2026-11-01", "2026-11-03", 2),
    ("Diciembre (Navidad)", "2026-12-20", "2026-12-27", 7),
    ("Febrero (baja)", "2027-02-10", "2027-02-13", 3),
]

EXCHANGE = {"MXN": 17.0, "COP": 4200.0}
OUTPUT = "data/airbnb_prices.csv"
results = []

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            locale="es-MX", viewport={"width": 1440, "height": 900},
        )
        page = await context.new_page()

        for name, url in ROOMS.items():
            print(f"\n  {name}")
            currency = "COP" if "com.co" in url else "MXN"

            for season, ci, co, nights in DATE_SLUGS:
                date_url = f"{url.split('?')[0]}?check_in={ci}&check_out={co}&adults=2"
                try:
                    await page.goto(date_url, timeout=15000, wait_until="domcontentloaded")
                    await page.wait_for_timeout(4000)
                except:
                    print(f"    {season}: timeout")
                    results.append(room_result(name, season, ci, co, nights, None, currency))
                    continue

                text = await page.inner_text("body")
                total_price = None

                # Strategy 1: "en total" pattern (MXN rooms)
                if not total_price:
                    m = re.search(r'\$([\d,]+)\s*' + currency + r'\s*en\s*total', text)
                    if m:
                        total_price = int(m.group(1).replace(",", ""))

                # Strategy 2: "por X noches" pattern (allows newlines between price and noches)
                if not total_price:
                    m = re.search(r'\$([\d,]+)\s*' + currency + r'[\s\S]*?por\s*' + str(nights) + r'\s*noche[s]?', text)
                    if m:
                        total_price = int(m.group(1).replace(",", ""))

                # Strategy 3: first "$X COP" that's on its own line with the currency
                if not total_price:
                    matches = re.findall(r'\$([\d,]+)\s*' + currency, text)
                    if matches:
                        total_price = int(matches[0].replace(",", ""))

                if total_price:
                    per_night_currency = total_price // nights
                    per_night_usd = round(per_night_currency / EXCHANGE[currency], 2)
                    print(f"    {season}: ${total_price:,} {currency} total → ${per_night_usd}/noche USD")
                else:
                    per_night_usd = None
                    print(f"    {season}: N/A")

                results.append(room_result(name, season, ci, co, nights, per_night_usd, currency, total_price))

        await browser.close()

    os.makedirs("data", exist_ok=True)
    keys = ["room", "season", "checkin", "checkout", "nights", "total_local", "currency", "price_usd_per_night"]
    with open(OUTPUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        w.writerows(results)
    print(f"\nSaved {len(results)} prices to {OUTPUT}")

    print(f"\n{'='*60}")
    print(f"  {'Room':15s} {'Season':25s} {'USD/noche':>10s}")
    print(f"{'='*60}")
    for r in results:
        p = f"${r['price_usd_per_night']:.0f}" if r['price_usd_per_night'] else "N/A"
        print(f"  {r['room']:15s} {r['season']:25s} {p:>10s}")

def room_result(name, season, ci, co, nights, usd, currency, total=None):
    return {
        "room": name, "season": season,
        "checkin": ci, "checkout": co, "nights": nights,
        "total_local": total, "currency": currency,
        "price_usd_per_night": usd,
    }

asyncio.run(main())
