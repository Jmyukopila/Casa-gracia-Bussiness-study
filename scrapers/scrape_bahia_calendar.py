import asyncio, json, os, re, csv
from playwright.async_api import async_playwright

EXCHANGE = 4200.0
OUTPUT = os.path.join("..", "data", "bahia_azul_precios_completo.csv")
HOTEL_URL = "https://www.booking.com/hotel/co/bahia-azul-manga-cartagena.html"

SEASONS = [
    ("2026-01-05", "2026-01-07", "ene"),
    ("2026-02-09", "2026-02-11", "feb"),
    ("2026-03-09", "2026-03-11", "mar"),
    ("2026-04-06", "2026-04-08", "abr"),
    ("2026-05-04", "2026-05-06", "may"),
]

async def get_calendar_prices(page, checkin, checkout, label):
    url = f"{HOTEL_URL}?checkin={checkin}&checkout={checkout}&group_adults=2&no_rooms=1&selected_currency=COP"
    print(f"  Loading {label} ({checkin}-{checkout})...")
    await page.goto(url, timeout=30000, wait_until="domcontentloaded")
    await page.wait_for_timeout(5000)
    text = await page.inner_text("body")

    price = None
    # Find the first room price (cheapest room)
    m = re.search(r"COP[^\S\r\n]*([\d.]+)", text)
    if m:
        total_cop = int(m.group(1).replace(".", ""))
        nights = (__import__("datetime").datetime.strptime(checkout, "%Y-%m-%d")
                  - __import__("datetime").datetime.strptime(checkin, "%Y-%m-%d")).days
        per_night = total_cop // nights
        usd = round(per_night / EXCHANGE, 2)
        price = usd
        print(f"    Cheapest room: COP {total_cop:,} total -> ${usd}/noche USD")
    else:
        print(f"    No price found!")

    return {"label": label, "checkin": checkin, "checkout": checkout, "price_usd": price}

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        ctx = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            locale="es-CO", viewport={"width": 1920, "height": 1080},
        )
        page = await ctx.new_page()

        results = []
        for ci, co, lbl in SEASONS:
            r = await get_calendar_prices(page, ci, co, lbl)
            results.append(r)

        await browser.close()

    # Load existing CSV
    existing_rows = []
    csv_path = os.path.join("..", "bahia_azul_precios.csv")
    if os.path.exists(csv_path):
        with open(csv_path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                existing_rows.append(row)
        print(f"\nExisting CSV: {len(existing_rows)} rows (Jun-Dec)")

    print(f"\nNew data:")
    for r in results:
        print(f"  {r['label']}: ${r['price_usd']}/noche" if r['price_usd'] else f"  {r['label']}: NO DATA")

asyncio.run(main())
