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
    url = f"{BOOKING_URL}?checkin={checkin}&checkout={checkout}&group_adults=2&no_rooms=1&selected_currency=COP"
    try:
        await page.goto(url, timeout=30000, wait_until="domcontentloaded")
        await page.wait_for_timeout(6000)
    except:
        return None

    text = await page.inner_text("body")
    price = None

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
    currency = "MXN" if (".mx" in url or "es" in url) else "COP"
    if ".es" in url or "com.ar" in url:
        currency = "COP"

    # For MXN listings, the price format might be different
    if currency == "MXN":
        # Try "$X MXN total"
        m = re.search(r'\$([\d,]+)\s*MXN\s*total', text)
        if m:
            return {"total": int(m.group(1).replace(",", "")), "currency": "MXN"}
        # Try "$X MXN" near nights
        m = re.search(r'\$([\d,]+)\s*MXN\s*[\s\S]{0,100}?' + str(nights) + r'\s*noche', text)
        if m:
            return {"total": int(m.group(1).replace(",", "")), "currency": "MXN"}
        # Try any MXN price near the top of the page
        first = text[:5000]
        matches = re.findall(r'\$([\d,]+)\s*MXN', first)
        if matches:
            vals = [int(m.replace(",", "")) for m in matches if int(m.replace(",", "")) > 500]
            if vals:
                return {"total": vals[0], "currency": "MXN"}
    else:
        # COP patterns
        m = re.search(r'\$([\d,]+)\s*COP\s*en\s*total', text)
        if m:
            return {"total": int(m.group(1).replace(",", "")), "currency": "COP"}

        m = re.search(r'\$([\d,]+)\s*COP[\s\S]{0,200}?por\s*' + str(nights) + r'\s*noche', text)
        if m:
            return {"total": int(m.group(1).replace(",", "")), "currency": "COP"}

        first = text[:5000]
        matches = re.findall(r'\$([\d,]+)\s*COP', first)
        if matches:
            vals = [int(m.replace(",", "")) for m in matches if int(m.replace(",", "")) > 20000]
            if vals:
                return {"total": vals[0], "currency": "COP"}
    return None

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
            locale="es-CO", viewport={"width": 1920, "height": 1080},
        )
        page = await context.new_page()

        print("=" * 60)
        print("BAHIA AZUL - BOOKING.COM")
        print("=" * 60)
        for label, ci, co, nights in SEASONS:
            price_cop = await scrape_booking(page, label, ci, co, nights)
            if price_cop and price_cop > 1000:
                per_night = price_cop // nights
                usd = round(per_night / EXCHANGE, 2)
                print(f"  {label:20s} COP ${price_cop:>8,} total ({nights}n) → ${per_night}/noche → ${usd}/noche USD")
                results["booking"][label] = {"cop": price_cop, "per_night_cop": per_night, "usd": usd, "nights": nights}
            else:
                print(f"  {label:20s} N/A")
                results["booking"][label] = None

        print("\n" + "=" * 60)
        print("BAHIA AZUL - AIRBNB")
        print("=" * 60)
        first_room = True
        for room_name, room_url in AIRBNB_ROOMS.items():
            print(f"\n  {room_name}")
            for label, ci, co, nights in SEASONS:
                result = await scrape_airbnb(page, room_name, room_url, label, ci, co, nights)
                if result:
                    total, cur = result["total"], result["currency"]
                    rate = 17.0 if cur == "MXN" else EXCHANGE
                    usd = round(total / nights / rate, 2)
                    per_night_cur = total // nights
                    print(f"    {label:20s} {'':>3s}{total:,} {cur} total ({nights}n) → {per_night_cur:,}/{cur} noche → ${usd}/noche USD")
                    results["airbnb"].setdefault(room_name, {})[label] = {"total": total, "currency": cur, "usd": usd, "per_night_cur": per_night_cur}
                else:
                    print(f"    {label:20s} N/A")
                    results["airbnb"].setdefault(room_name, {})[label] = None

        await browser.close()

    os.makedirs("data", exist_ok=True)
    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\nSaved to {OUTPUT}")

asyncio.run(main())
