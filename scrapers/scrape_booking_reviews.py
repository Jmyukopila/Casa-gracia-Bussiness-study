import asyncio
import json, os, re
from playwright.async_api import async_playwright

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
        await page.wait_for_timeout(3000)

        # Click cookie/consent if any
        try:
            consent = page.locator("button:has-text('Aceptar')")
            if await consent.count() > 0:
                await consent.click()
                await page.wait_for_timeout(1000)
        except:
            pass

        # Click "show more" buttons to load all reviews
        max_clicks = 30
        for i in range(max_clicks):
            try:
                btn = page.locator("button:has-text('mostrar más'), button:has-text('Show more'), button[data-testid='review-list-show-more']")
                if await btn.count() == 0:
                    print(f"No more 'show more' buttons after {i} clicks")
                    break
                await btn.first.click()
                await page.wait_for_timeout(1500)
                print(f"Clicked 'show more' #{i+1}")
            except Exception as e:
                print(f"Click #{i+1} failed: {e}")
                break

        # Now extract review data
        reviews = await page.evaluate("""() => {
            const items = document.querySelectorAll('[data-testid^="review-card"], [data-testid="review_list_item"], .review_list_item, .c-review-block');
            const results = [];
            items.forEach(item => {
                const titleEl = item.querySelector('[data-testid="review-title"], .review_list_item_title, h3, .c-review-block__title');
                const textEl = item.querySelector('[data-testid="review-text"], .review_list_item_text, p, .c-review-block__text');
                const ratingEl = item.querySelector('[data-testid="review-score"], .review_list_item_score, .bui-review-score__badge');
                const dateEl = item.querySelector('[data-testid="review-date"], .review_list_item_date, .c-review-block__date');
                results.push({
                    title: titleEl ? titleEl.textContent.trim() : '',
                    text: textEl ? textEl.textContent.trim() : '',
                    rating: ratingEl ? ratingEl.textContent.trim() : '',
                    date: dateEl ? dateEl.textContent.trim() : '',
                });
            });
            return results;
        }""")

        print(f"Extracted {len(reviews)} reviews via evaluate")

        if len(reviews) == 0:
            # Fallback: get all page text and search for review patterns
            body = await page.inner_text("body")
            print(f"Body text length: {len(body)}")
            print("First 2000 chars:", body[:2000])

            # Save full HTML
            html = await page.content()
            with open("data/booking_full_page.html", "w", encoding="utf-8") as f:
                f.write(html)
            print("Saved full HTML to data/booking_full_page.html")
        else:
            with open(OUTPUT, "w", encoding="utf-8") as f:
                json.dump(reviews, f, ensure_ascii=False, indent=2)
            print(f"Saved {len(reviews)} reviews to {OUTPUT}")

        await browser.close()

asyncio.run(main())
