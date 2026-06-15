import asyncio, sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8')

URL = "https://www.instagram.com/casagracia.ctg/"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            locale="es-ES", viewport={"width": 1280, "height": 900},
        )
        page = await context.new_page()
        await page.goto(URL, timeout=30000, wait_until="domcontentloaded")
        await page.wait_for_timeout(8000)

        # Check if we got the page
        title = await page.title()
        print(f"Title: {title}")

        # Try to extract profile info
        text = await page.evaluate("() => document.body.innerText")
        print(f"Text length: {len(text)}")
        print(f"First 1000 chars:\n{text[:1000]}")

        # Save full page
        html = await page.content()
        with open("data/instagram_page.html", "w", encoding="utf-8") as f:
            f.write(html)
        print(f"\nSaved HTML: {len(html)} chars")

        # Look for follower count, post count
        meta_desc = await page.evaluate("""() => {
            const meta = document.querySelector('meta[property="og:description"]');
            return meta ? meta.getAttribute('content') : 'not found';
        }""")
        print(f"Meta description: {meta_desc}")

        await browser.close()

asyncio.run(main())
