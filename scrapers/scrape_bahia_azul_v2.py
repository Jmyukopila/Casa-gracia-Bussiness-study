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

async def dump_html(page, name):
    html = await page.content()
    safe = re.sub(r'[\\/:*?"<>|]', "_", name)
    with open(os.path.join("data", f"debug_{safe}.html"), "w", encoding="utf-8") as f:
        f.write(html[:50000])
    print(f"    saved debug_{safe}.html ({len(html)} chars)")

async def scrape_booking(page, season_label, checkin, checkout, nights):
    url = f"{BOOKING_URL}?checkin={checkin}&checkout={checkout}&group_adults=2&no_rooms=1&selected_currency=COP"
    try:
        await page.goto(url, timeout=30000, wait_until="domcontentloaded")
        await page.wait_for_timeout(6000)
    except:
        print(f"    {season_label}: timeout")
        return None

    text = await page.inner_text("body")

    # Save debug
    safe = re.sub(r'[\\/:*?"<>|]', "_", f"booking_{season_label}")
    with open(os.path.join("data", f"debug_{safe}.txt"), "w", encoding="utf-8") as f:
        f.write(text[:30000])
    print(f"    {season_label}: saved debug_{safe}.txt")

    # Look for price patterns in the raw HTML
    html = await page.content()

    # Check various price patterns on Booking's hotel page
    price = None

    # Pattern 1: Look for COP price near "Reserva ahora" / "Precio"
    m = re.search(r'COP\s*(\d[\d,.]*)', text)
    if m:
        val = m.group(1).replace(",", "").replace(".", "")
        if len(val) >= 4 and len(val) <= 8:
            price = int(val)

    if not price:
        m = re.search(r'(\d[\d,.]*)\s*COP', text)
        if m:
            val = m.group(1).replace(",", "").replace(".", "")
            if len(val) >= 4 and len(val) <= 8:
                price = int(val)

    # Pattern 3: Look for "total" near a price
    if not price:
        m = re.search(r'\$?(\d[\d,]*)\s*</[^>]+>\s*<[^>]+>\s*total', html[:100000])
        if m:
            price = int(m.group(1).replace(",", "").replace(".", ""))

    if not price:
        # Check the debug file manually
        pass

    return price

async def scrape_airbnb(page, name, url, season_label, checkin, checkout, nights):
    date_url = f"{url.split('?')[0]}?check_in={checkin}&check_out={checkout}&adults=2"
    try:
        await page.goto(date_url, timeout=20000, wait_until="domcontentloaded")
        await page.wait_for_timeout(5000)
    except:
        print(f"    {season_label}: timeout")
        return None

    text = await page.inner_text("body")

    total = None
    currency = "MXN" if ".mx" in url else "COP"

    # Pattern 1: "$X XXX MXN/COP en total"
    m = re.search(r'\$([\d,]+)\s*' + currency + r'\s*en\s*total', text)
    if m:
        total = int(m.group(1).replace(",", ""))

    # Pattern 2: "por X noches" with same currency
    if not total:
        m = re.search(r'\$([\d,]+)\s*' + currency + r'[\s\S]{0,200}?por\s*' + str(nights) + r'\s*noche', text)
        if m:
            total = int(m.group(1).replace(",", ""))

    # Pattern 3: for MXN rooms, try "en total" (newline tolerant)
    if not total:
        m = re.search(r'\$([\d,]+)\s*(?:MXN|COP)\s*en\s*total', text)
        if m:
            total = int(m.group(1).replace(",", ""))

    # Pattern 4: any COP/MXN price near the top of the page
    if not total:
        first_5000 = text[:5000]
        matches = re.findall(r'\$([\d,]+)\s*' + currency, first_5000)
        if matches:
            # Take the first price that looks like a total for the stay
            vals = [int(m.replace(",", "")) for m in matches]
            vals = [v for v in vals if v > 10000 and v < 10000000]
            if vals:
                total = vals[0]
    return total

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
            locale="es-CO", viewport={"width": 1920, "height": 1080},
        )
        page = await context.new_page()

        print("=" * 60)
        print("SCRAPING BAHIA AZUL - BOOKING.COM")
        print("=" * 60)
        for label, ci, co, nights in SEASONS:
            price_cop = await scrape_booking(page, label, ci, co, nights)
            if price_cop and price_cop > 1000:
                usd = round(price_cop / EXCHANGE, 2)
                print(f"  {label:20s} COP ${price_cop:>8,} → ${usd}/noche USD")
                results["booking"][label] = {"cop": price_cop, "usd": usd}
            else:
                print(f"  {label:20s} N/A (price={price_cop})")
                results["booking"][label] = None

        print("\n" + "=" * 60)
        print("SCRAPING BAHIA AZUL - AIRBNB")
        print("=" * 60)
        for room_name, room_url in AIRBNB_ROOMS.items():
            print(f"\n  {room_name}")
            for label, ci, co, nights in SEASONS:
                total = await scrape_airbnb(page, room_name, room_url, label, ci, co, nights)
                if total:
                    currency = "MXN" if ".mx" in room_url else "COP"
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
