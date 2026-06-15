import asyncio
import json, os, sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8')

OUTPUT = "data/booking_reviews.json"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=["--disable-blink-features=AutomationControlled"])
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            locale="es-ES",
            viewport={"width": 1280, "height": 900},
        )
        page = await context.new_page()
        await page.goto(
            "https://www.booking.com/reviews/co/hotel/casa-gracia.es.html",
            timeout=30000, wait_until="domcontentloaded"
        )
        await page.wait_for_timeout(5000)

        # Save full HTML for analysis
        html = await page.content()
        with open("data/booking_page.html", "w", encoding="utf-8") as f:
            f.write(html)

        # Try different selectors for reviews
        selectors = [
            '[data-testid^="review-card"]',
            '[data-testid="review_list_item"]',
            '.review_list_item',
            '.c-review-block',
            '[class*="review"]',
            'article',
            '[data-review-id]',
            '[class*="Review"]',
        ]
        for sel in selectors:
            count = await page.locator(sel).count()
            print(f"Selector '{sel}': {count} elements")

        # Try extracting all text from the page
        body_text = await page.evaluate("() => document.body.innerText")
        with open("data/booking_body_text.txt", "w", encoding="utf-8") as f:
            f.write(body_text)
        print(f"Body text saved: {len(body_text)} chars")

        await browser.close()

asyncio.run(main())
