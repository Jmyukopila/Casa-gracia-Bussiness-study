import asyncio, json, os, re, sys
from playwright.async_api import async_playwright
sys.stdout.reconfigure(encoding='utf-8')

EXCHANGE = 4200.0

SEASONS = [
    ("feb (baja)",   "2027-02-10", "2027-02-13", 3),
    ("jul (media)",  "2026-07-15", "2026-07-17", 2),
    ("nov (festival)","2026-11-01", "2026-11-03", 2),
    ("dic (navidad)", "2026-12-20", "2026-12-27", 7),
]

BOOKING_URL = "https://www.booking.com/hotel/co/suite-en-cartagena-tipica.html"
AIRBNB_URL = "https://www.airbnb.mx/rooms/971336225095032768"

results = {"booking": {}, "airbnb": {}}

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            locale="es-CO", viewport={"width": 1920, "height": 1080},
        )
        page = await context.new_page()

        print("CASA CARTAGENA TIPICA - BOOKING.COM")
        for label, ci, co, nights in SEASONS:
            url = f"{BOOKING_URL}?checkin={ci}&checkout={co}&group_adults=2&no_rooms=1&selected_currency=COP"
            try:
                await page.goto(url, timeout=30000, wait_until="domcontentloaded")
                await page.wait_for_timeout(6000)
            except:
                results["booking"][label] = None
                continue
            text = await page.inner_text("body")
            price = None
            m = re.search(r"COP\s*(\d[\d,.]*)", text)
            if m:
                val = m.group(1).replace(",","").replace(".","")
                if 4 <= len(val) <= 8:
                    price = int(val)
            if not price:
                m = re.search(r"(\d[\d,.]*)\s*COP", text)
                if m:
                    val = m.group(1).replace(",","").replace(".","")
                    if 4 <= len(val) <= 8:
                        price = int(val)
            if price and price > 1000:
                per_night = price // nights
                usd = round(per_night / EXCHANGE, 2)
                print(f"  {label:20s} COP {price:>8,} total ({nights}n) -> {per_night}/noche -> ${usd}/noche USD")
                results["booking"][label] = {"cop": price, "per_night_cop": per_night, "usd": usd}
            else:
                print(f"  {label:20s} N/A")
                results["booking"][label] = None

        print("\nCASA CARTAGENA TIPICA - AIRBNB")
        for label, ci, co, nights in SEASONS:
            url = f"{AIRBNB_URL.split('?')[0]}?check_in={ci}&check_out={co}&adults=2"
            try:
                await page.goto(url, timeout=20000, wait_until="domcontentloaded")
                await page.wait_for_timeout(5000)
            except:
                results["airbnb"][label] = None
                continue
            text = await page.inner_text("body")
            total = None
            m = re.search(r'\$([\d,]+)\s*MXN\s*total', text)
            if m:
                total = int(m.group(1).replace(",",""))
            if not total:
                m = re.search(r'\$([\d,]+)\s*MXN[\s\S]{0,100}?' + str(nights) + r'\s*noche', text)
                if m:
                    total = int(m.group(1).replace(",",""))
            if not total:
                matches = re.findall(r'\$([\d,]+)\s*MXN', text[:5000])
                if matches:
                    vals = [int(m.replace(",","")) for m in matches if int(m.replace(",","")) > 500]
                    if vals:
                        total = vals[0]
            if total:
                per_night_mxn = total // nights
                usd = round(per_night_mxn / 17.0, 2)
                print(f"  {label:20s} ${total:,} MXN total ({nights}n) -> {per_night_mxn}/noche -> ${usd}/noche USD")
                results["airbnb"][label] = {"total": total, "per_night_mxn": per_night_mxn, "usd": usd}
            else:
                print(f"  {label:20s} N/A")
                results["airbnb"][label] = None

        await browser.close()

    with open(os.path.join("data","cc_tipica_prices.json"), "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved to data/cc_tipica_prices.json")

asyncio.run(main())
