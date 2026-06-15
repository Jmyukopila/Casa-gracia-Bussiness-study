import asyncio, sys, re
from playwright.async_api import async_playwright
sys.stdout.reconfigure(encoding='utf-8')

ROOMS = {
    "Queen 101": "https://www.airbnb.mx/rooms/1197228721608888257",
    "Queen 203": "https://www.airbnb.mx/rooms/1247150160057099135",
    "King 202": "https://www.airbnb.mx/rooms/1265108254884566985",
    "Multiple 103": "https://www.airbnb.com.co/rooms/1202495221808518235",
}

DATE_SLUGS = [
    ("Julio", "2026-07-15", "2026-07-17"),
    ("Noviembre", "2026-11-01", "2026-11-03"),
    ("Diciembre", "2026-12-20", "2026-12-27"),
    ("Febrero", "2027-02-10", "2027-02-13"),
]

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            locale="es-MX", viewport={"width": 1440, "height": 900},
        )
        page = await context.new_page()

        for name, url in ROOMS.items():
            print(f"\n{'='*50}")
            print(f"  {name}")
            print(f"{'='*50}")

            for season, ci, co in DATE_SLUGS:
                date_url = f"{url.split('?')[0]}?check_in={ci}&check_out={co}&adults=2"
                try:
                    await page.goto(date_url, timeout=15000, wait_until="domcontentloaded")
                    await page.wait_for_timeout(4000)
                except:
                    print(f"  {season}: timeout")
                    continue

                text = await page.inner_text("body")
                lines = text.split("\n")

                # Find "en total" lines
                for i, line in enumerate(lines):
                    l = line.strip()
                    if "en total" in l and ("MXN" in l or "COP" in l or "$" in l):
                        # Print context around this line
                        print(f"  {season}: {l}")
                        for j in range(max(0,i-1), min(len(lines), i+3)):
                            if j != i:
                                print(f"         {lines[j].strip()}")
                        break
                else:
                    # Try other patterns
                    for i, line in enumerate(lines):
                        l = line.strip()
                        if "$" in l and ("MXN" in l or "COP" in l):
                            print(f"  {season} (alt): {l}")

        await browser.close()

asyncio.run(main())
