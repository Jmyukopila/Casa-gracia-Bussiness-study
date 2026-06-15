import asyncio, sys, json
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8')

URLS = {
    "bahia_azul_booking": "https://www.booking.com/hotel/co/bahia-azul-manga-cartagena.html",
    "lunala_booking": "https://www.booking.com/hotel/co/lunala-cartagena.html",
}

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            locale="es-ES", viewport={"width": 1280, "height": 900},
        )
        results = {}

        for name, url in URLS.items():
            page = await context.new_page()
            try:
                await page.goto(url, timeout=20000, wait_until="domcontentloaded")
                await page.wait_for_timeout(4000)
                text = await page.evaluate("() => document.body.innerText")
                title = await page.title()
                print(f"\n--- {name} ---")
                print(f"Title: {title}")
                print(f"Text: {len(text)} chars")

                # Look for rating, price, review count
                lines = text.split("\n")
                rating_line = None
                price_line = None
                review_line = None
                for i, l in enumerate(lines):
                    l = l.strip()
                    if re.search(r'\d+[.,]?\d*\s*/\s*\d+', l) and ("Puntuación" in l or "puntuación" in l):
                        rating_line = l
                    if "COP" in l and "$" in l:
                        price_line = l
                    if "reseña" in l or "opinion" in l or "comentario" in l:
                        review_line = l

                results[name] = {
                    "title": title[:100],
                    "text_sample": text[:2000],
                    "rating_line": rating_line,
                    "price_line": price_line,
                    "review_line": review_line,
                }
                with open(f"data/{name}_page.txt", "w", encoding="utf-8") as f:
                    f.write(text)
            except Exception as e:
                print(f"{name}: Error {e}")
                results[name] = {"error": str(e)}
            finally:
                await page.close()

        print("\n\n=== RESULTS ===")
        print(json.dumps(results, ensure_ascii=False, indent=2)[:2000])
        await browser.close()

import re
asyncio.run(main())
