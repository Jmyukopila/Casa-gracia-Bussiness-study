import asyncio, json, os, re, sys
from playwright.async_api import async_playwright
sys.stdout.reconfigure(encoding='utf-8')

EXCHANGE = 4200.0
OUTPUT = os.path.join("data", "bahia_azul_prices.json")

SEASONS = [
    ("feb (baja)",   "2027-02-10", "2027-02-13", 3),
    ("jul (media)",  "2026-07-15", "2026-07-17", 2),
    ("nov (festival)","2026-11-01", "2026-11-03", 2),
    ("dic (navidad)", "2026-12-20", "2026-12-27", 7),
]

BOOKING_URL = "https://www.booking.com/hotel/co/bahia-azul-manga-cartagena.html"

AIRBNB_ROOMS = {
    "Suite Manga (Airbnb)": "https://www.airbnb.mx/rooms/1395965846856217121",
    "Habitacion Nueva (Airbnb)": "https://www.airbnb.com/rooms/1395261514605535440",
    "Bahia Azul TW (Airbnb)": "https://www.airbnb.es/rooms/1398744182624780326",
}

results = {"booking": {}, "airbnb": {}}

async def scrape_booking(page, season_label, checkin, checkout, nights):
    url = f"{BOOKING_URL}?checkin={checkin}&checkout={checkout}&group_adults=2&no_rooms=1"
    try:
        await page.goto(url, timeout=20000, wait_until="domcontentloaded")
        await page.wait_for_timeout(5000)
    except:
        return None

    text = await page.inner_text("body")
    price = None

    # Try different price patterns on Booking hotel page
    patterns = [
        r'COP\s*\$?([\d,]+)\s*(?:por noche|total)',
        r'\$?([\d,]+)\s*COP\s*(?:por noche|total)',
        r'precio.*?COP\s*\$?([\d,]+)',
    ]
    for pat in patterns:
        m = re.search(pat, text)
        if m:
            price = int(m.group(1).replace(",", ""))
            break

    if not price:
        m = re.search(r'\$?([\d,]+)\s*' + re.escape("COP"), text)
        if m:
            price = int(m.group(1).replace(",", ""))
    return price

async def scrape_airbnb(page, name, url, season_label, checkin, checkout, nights):
    date_url = f"{url.split('?')[0]}?check_in={checkin}&check_out={checkout}&adults=2"
    try:
        await page.goto(date_url, timeout=15000, wait_until="domcontentloaded")
        await page.wait_for_timeout(5000)
    except:
        return None

    text = await page.inner_text("body")
    total = None

    patterns = [
        r'\$([\d,]+)\s*MXN\s*en\s*total',
        r'\$([\d,]+)\s*COP\s*en\s*total',
        r'\$([\d,]+)\s*MXN[\s\S]*?por\s*' + str(nights) + r'\s*noche',
        r'\$([\d,]+)\s*COP[\s\S]*?por\s*' + str(nights) + r'\s*noche',
    ]
    for pat in patterns:
        m = re.search(pat, text)
        if m:
            total = int(m.group(1).replace(",", ""))
            break
    return total

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            locale="es-CO", viewport={"width": 1920, "height": 1080},
        )
        page = await context.new_page()

        print("=" * 60)
        print("SCRAPING BAHIA AZUL - BOOKING.COM")
        print("=" * 60)
        for label, ci, co, nights in SEASONS:
            price_cop = await scrape_booking(page, label, ci, co, nights)
            if price_cop:
                usd = round(price_cop / EXCHANGE, 2)
                print(f"  {label:20s} COP ${price_cop:>8,} → ${usd}/noche USD")
                results["booking"][label] = {"cop": price_cop, "usd": usd}
            else:
                print(f"  {label:20s} N/A")
                results["booking"][label] = None

        print("\n" + "=" * 60)
        print("SCRAPING BAHIA AZUL - AIRBNB")
        print("=" * 60)
        for room_name, room_url in AIRBNB_ROOMS.items():
            print(f"\n  {room_name}")
            for label, ci, co, nights in SEASONS:
                total = await scrape_airbnb(page, room_name, room_url, label, ci, co, nights)
                if total:
                    currency = "MXN" if "com.mx" in room_url else "COP"
                    rate = 17.0 if currency == "MXN" else EXCHANGE
                    usd = round(total / nights / rate, 2)
                    print(f"    {label:20s} ${total:,} {currency} total → ${usd}/noche USD")
                    results["airbnb"].setdefault(room_name, {})[label] = {"total": total, "currency": currency, "usd": usd}
                else:
                    print(f"    {label:20s} N/A")
                    results["airbnb"].setdefault(room_name, {})[label] = None

        await browser.close()

    os.makedirs("data", exist_ok=True)
    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\nSaved to {OUTPUT}")

asyncio.run(main())
