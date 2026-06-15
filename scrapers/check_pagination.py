import asyncio, sys
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
        await page.goto(
            "https://www.booking.com/reviews/co/hotel/casa-gracia.es.html",
            timeout=30000, wait_until="domcontentloaded"
        )
        await page.wait_for_timeout(5000)

        # Find all pagination links/buttons
        pagination = await page.evaluate("""() => {
            const results = [];
            // Find all <a> and <button> elements
            document.querySelectorAll('a, button, [role="button"]').forEach(el => {
                const text = el.textContent.trim();
                const aria = el.getAttribute('aria-label') || '';
                const href = el.getAttribute('href') || '';
                const cls = el.className || '';
                if (text && (text.includes('Página') || text.includes('Next') || text.includes('Siguiente') || text.includes('>'))) {
                    results.push({
                        tag: el.tagName,
                        text: text.substring(0, 50),
                        aria: aria.substring(0, 50),
                        href: href.substring(0, 100),
                        class: cls.substring(0, 100),
                        disabled: el.getAttribute('aria-disabled') || 'false',
                    });
                }
            });
            return results;
        }""")

        for p in pagination:
            print(p)

        # Also check for page number links
        page_links = await page.evaluate("""() => {
            const links = [];
            document.querySelectorAll('a[aria-label*="Página"], a[aria-label*="Page"]').forEach(a => {
                links.push({
                    text: a.textContent.trim(),
                    aria: a.getAttribute('aria-label'),
                    href: a.getAttribute('href'),
                });
            });
            return links;
        }""")
        print("\nPage number links:")
        for l in page_links:
            print(l)

        # Check for any numbers that look like page navigation
        all_links = await page.evaluate("""() => {
            const results = [];
            document.querySelectorAll('a').forEach(a => {
                const t = a.textContent.trim();
                if (/^\\d+$/.test(t)) {
                    results.push({text: t, href: a.getAttribute('href'), aria: a.getAttribute('aria-label')});
                }
            });
            return results;
        }""")
        print("\nNumber-only links (pages?):")
        for l in all_links[:10]:
            print(l)

        # Check overall page structure
        structure = await page.evaluate("""() => {
            const main = document.querySelector('main') || document.querySelector('[data-testid="review-list"]');
            return {
                hasMain: !!main,
                mainChildren: main ? main.children.length : 0,
                bodyClass: document.body.className.substring(0, 100),
            };
        }""")
        print(f"\nPage structure: {structure}")

        # Get the review list area
        review_section = await page.evaluate("""() => {
            const sections = [];
            document.querySelectorAll('section, div[data-testid]').forEach(el => {
                const tid = el.getAttribute('data-testid') || '';
                if (tid.includes('review') || tid.includes('Review')) {
                    sections.push(tid);
                }
            });
            return sections;
        }""")
        print(f"Review sections found: {review_section}")

        await browser.close()

asyncio.run(main())
