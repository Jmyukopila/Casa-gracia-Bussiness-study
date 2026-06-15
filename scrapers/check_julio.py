import asyncio, sys
from playwright.async_api import async_playwright
sys.stdout.reconfigure(encoding='utf-8')

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0", locale="es-MX", viewport={"width": 1440, "height": 900},
        )
        page = await context.new_page()

        urls = [
            "https://www.airbnb.mx/rooms/1197228721608888257?check_in=2026-07-15&check_out=2026-07-17&adults=2",
            "https://www.airbnb.com.co/rooms/1202495221808518235?check_in=2026-07-15&check_out=2026-07-17&adults=2",
        ]

        for url in urls:
            await page.goto(url, timeout=15000, wait_until="domcontentloaded")
            await page.wait_for_timeout(4000)
            text = await page.inner_text("body")
            lines = text.split("\n")

            print(f"\n=== {url[:50]}... ===")
            # Find lines mentioning julio, price, total, noche
            keywords = ["julio", "jul", "price", "precio", "total", "$", "MXN", "COP", "noche", "disponible", "reservado"]
            for i, line in enumerate(lines):
                l = line.strip().lower()
                if any(kw in l for kw in keywords):
                    print(f"  {i}: {line.strip()[:200]}")

        await browser.close()

asyncio.run(main())
