import asyncio, sys, re
from playwright.async_api import async_playwright
sys.stdout.reconfigure(encoding='utf-8')

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            locale="es-MX", viewport={"width": 1440, "height": 900},
        )
        page = await context.new_page()

        url = "https://www.airbnb.mx/rooms/1197228721608888257?check_in=2026-11-01&check_out=2026-11-03&adults=2"
        await page.goto(url, timeout=15000, wait_until="domcontentloaded")
        await page.wait_for_timeout(5000)

        text = await page.inner_text("body")
        lines = text.split("\n")

        # Find lines that contain $ or precio or total
        print("=== Lines with $, MXN, COP, precio, total, noche ===")
        for i, line in enumerate(lines):
            l = line.strip()
            keywords = ["$", "MXN", "COP", "precio", "total", "noche", "USD"]
            if any(kw in l for kw in keywords):
                print(f"  {i:4d}: {l[:150]}")

        print(f"\n=== All lines 100-130 ===")
        for i in range(min(100, len(lines)), min(130, len(lines))):
            print(f"  {i:4d}: {lines[i][:150]}")

        # Also get the raw HTML around price elements
        price_html = await page.evaluate("""() => {
            const els = document.querySelectorAll('[class*="price"], [data-testid*="price"], [class*="Price"]');
            const results = [];
            els.forEach(el => {
                results.push({
                    tag: el.tagName,
                    class: el.className.substring(0, 60),
                    text: el.textContent.trim().substring(0, 100),
                });
            });
            return results;
        }""")
        print(f"\n=== Price-related HTML elements ({len(price_html)}) ===")
        for p in price_html[:10]:
            print(f"  {p}")

        await browser.close()

asyncio.run(main())
