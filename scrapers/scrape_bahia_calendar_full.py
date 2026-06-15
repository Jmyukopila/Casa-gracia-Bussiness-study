import asyncio, json, os, re, csv, sys
from datetime import datetime, timedelta
from playwright.async_api import async_playwright

EXCHANGE = 4200.0
OUTPUT = os.path.join("..", "data", "bahia_azul_precios_completo.csv")

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        ctx = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            locale="es-CO", viewport={"width": 1920, "height": 1080},
        )
        page = await ctx.new_page()

        url = "https://www.booking.com/hotel/co/bahia-azul-manga-cartagena.html"
        print("Loading page...")
        await page.goto(url, timeout=30000, wait_until="domcontentloaded")
        await page.wait_for_timeout(8000)

        # Try to find and click the calendar/date picker
        # The calendar is usually triggered by clicking on the check-in date field
        selectors = [
            'button[data-testid="date-display-field-start"]',
            '[data-testid="date-display-field-start"]',
            'button[class*="date"]',
            '[class*="DatePicker"]',
            '#checkin',
        ]
        clicked = False
        for sel in selectors:
            try:
                el = await page.query_selector(sel)
                if el:
                    await el.click()
                    await page.wait_for_timeout(2000)
                    clicked = True
                    print(f"  Clicked calendar via: {sel}")
                    break
            except:
                continue

        if not clicked:
            print("  Trying to trigger calendar via URL...")
            # Navigate with explicit dates to trigger calendar
            await page.goto(f"{url}?checkin=2026-06-01&checkout=2026-06-03", timeout=30000)
            await page.wait_for_timeout(5000)

        await page.wait_for_timeout(3000)
        await page.screenshot(path=os.path.join("..", "data", "bahia_calendar.png"))
        print("Screenshot saved")

        # Dump page text to see calendar structure
        text = await page.inner_text("body")
        with open(os.path.join("..", "data", "bahia_calendar_debug.txt"), "w", encoding="utf-8") as f:
            f.write(text)
        print("Debug text saved")

        await page.wait_for_timeout(5000)
        await browser.close()

asyncio.run(main())
