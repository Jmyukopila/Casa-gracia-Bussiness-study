import asyncio
from playwright.async_api import async_playwright
import json, os

URLS = {
    "casa_gracia": "https://www.booking.com/reviews/co/hotel/casa-gracia.es.html",
    "bahia_azul": "https://www.booking.com/hotel/co/bahia-azul-manga-cartagena.html",
}

async def try_booking(url, name):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            locale="es-ES",
            viewport={"width": 1280, "height": 800},
        )
        page = await context.new_page()
        try:
            print(f"\n--- Trying {name}: {url} ---")
            await page.goto(url, timeout=30000, wait_until="domcontentloaded")
            await page.wait_for_timeout(5000)
            title = await page.title()
            content = await page.content()
            print(f"Title: {title}")
            print(f"Content length: {len(content)}")

            if "captcha" in content.lower() or "blocked" in content.lower() or len(content) < 2000:
                print(f"BLOCKED or minimal content ({len(content)} chars)")
                # Save raw
                with open(f"data/{name}_blocked.html", "w", encoding="utf-8") as f:
                    f.write(content)
                return False

            # Check for review content
            body_text = await page.inner_text("body")
            print(f"Body text length: {len(body_text)}")
            print(f"First 500 chars: {body_text[:500]}")

            # Find review items
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(content, "lxml")
            review_blocks = soup.find_all("div", class_=lambda x: x and "review" in x.lower())
            print(f"Review-like divs: {len(review_blocks)}")

            # Save
            with open(f"data/{name}_success.html", "w", encoding="utf-8") as f:
                f.write(content)
            print(f"Saved to data/{name}_success.html")
            return True

        except Exception as e:
            print(f"Error: {e}")
            return False
        finally:
            await browser.close()

async def main():
    results = {}
    for name, url in URLS.items():
        results[name] = await try_booking(url, name)
    print("\n\nResults:", json.dumps(results, indent=2))

asyncio.run(main())
