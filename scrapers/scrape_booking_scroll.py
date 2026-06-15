import asyncio, json, sys, re
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8')

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=["--disable-blink-features=AutomationControlled"])
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            locale="es-ES", viewport={"width": 1280, "height": 900},
        )
        page = await context.new_page()

        # Listen for API calls
        api_responses = []
        page.on("response", lambda resp: api_responses.append({
            "url": resp.url,
            "status": resp.status,
        }) if "review" in resp.url.lower() or "api" in resp.url.lower() else None)

        await page.goto(
            "https://www.booking.com/reviews/co/hotel/casa-gracia.es.html",
            timeout=30000, wait_until="domcontentloaded"
        )
        await page.wait_for_timeout(5000)

        try:
            accept = page.locator("button:has-text('Aceptar')")
            if await accept.count() > 0:
                await accept.first.click()
                await page.wait_for_timeout(1000)
        except:
            pass

        # Try scrolling page to trigger lazy loading
        for scroll in range(5):
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await page.wait_for_timeout(2000)
            print(f"Scroll {scroll+1}: {await page.evaluate('document.body.scrollHeight')}px")

        # Also try clicking "Translate" or "Mostrar más" buttons
        more_btns = await page.evaluate("""() => {
            const btns = [];
            document.querySelectorAll('button, a').forEach(el => {
                const t = el.textContent.trim().toLowerCase();
                if (t.includes('más') || t.includes('more') || t.includes('mostrar') || t.includes('ver todo')) {
                    btns.push(el.textContent.trim());
                }
            });
            return btns;
        }""")
        print(f"More/show buttons: {more_btns}")

        # Get API calls
        review_apis = [r for r in api_responses if "review" in r["url"].lower()]
        print(f"\nReview-related API calls: {len(review_apis)}")
        for r in review_apis[:5]:
            print(f"  {r['status']} {r['url'][:150]}")

        # Get current text
        text = await page.evaluate("() => document.body.innerText")
        with open("data/booking_scrolled.txt", "w", encoding="utf-8") as f:
            f.write(text)
        print(f"\nTotal text after scrolling: {len(text)} chars")

        # Count reviews
        count = text.count("Escrito en ")
        print(f"Review count: {count}")

        await browser.close()

asyncio.run(main())
