import asyncio, sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8')

URLS = {
    "queen_101": "https://www.airbnb.mx/rooms/1197228721608888257",
    "queen_203": "https://www.airbnb.mx/rooms/1247150160057099135",
    "king_202": "https://www.airbnb.mx/rooms/1265108254884566985",
    "multiple_103": "https://www.airbnb.mx/rooms/1220198022423928832",
}

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            locale="es-MX", viewport={"width": 1280, "height": 900},
        )

        for name, url in URLS.items():
            page = await context.new_page()
            try:
                print(f"\n--- {name} ---")
                await page.goto(url, timeout=20000, wait_until="domcontentloaded")
                await page.wait_for_timeout(6000)
                title = await page.title()
                text = await page.evaluate("() => document.body.innerText")
                print(f"Title: {title}")
                print(f"Text: {len(text)} chars")
                if len(text) < 500:
                    print(f"BLOCKED or empty page: {text[:300]}")
                else:
                    # Look for price
                    lines = text.split("\n")
                    for i, l in enumerate(lines):
                        l = l.strip()
                        if "$" in l and ("noche" in l.lower() or "MXN" in l or "USD" in l):
                            print(f"  Price line ({i}): {l[:100]}")
                        if "rating" in l.lower() or "reseña" in l.lower() or "opinión" in l.lower():
                            print(f"  Review line ({i}): {l[:100]}")
                    # Show first 500 chars for context
                    print(f"  First 500: {text[:500]}")
            except Exception as e:
                print(f"{name}: Error {e}")
            finally:
                await page.close()

        await browser.close()

asyncio.run(main())
