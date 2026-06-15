import asyncio
from playwright.async_api import async_playwright
import json

URL = "https://www.tripadvisor.es/Hotel_Review-g297476-d33258412-Reviews-Casa_Gracia_Hotel_Boutique-Cartagena_Cartagena_District_Bolivar_Department.html"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            locale="es-ES",
            viewport={"width": 1280, "height": 800},
        )
        page = await context.new_page()
        try:
            await page.goto(URL, timeout=30000, wait_until="domcontentloaded")
            await page.wait_for_timeout(3000)
            content = await page.content()
            title = await page.title()
            print(f"Title: {title}")
            print(f"Content length: {len(content)}")
            # Check if we got past cloudflare
            if "Please enable JS" in content or "disable any ad blocker" in content:
                print("BLOCKED by Cloudflare")
            else:
                # Try to find review count
                text = await page.inner_text("body")
                print(f"Body text length: {len(text)}")
                # Find rating info
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(content, "lxml")
                rating_spans = soup.find_all("span", class_=lambda x: x and "review" in x.lower())
                print(f"Review-related spans: {len(rating_spans)}")
                for s in rating_spans[:5]:
                    print(f"  {s.get('class')}: {s.text.strip()[:100]}")
                # Save full HTML for inspection
                with open("data/tripadvisor_raw.html", "w", encoding="utf-8") as f:
                    f.write(content)
                print("Saved to data/tripadvisor_raw.html")
        except Exception as e:
            print(f"Error: {e}")
        finally:
            await browser.close()

asyncio.run(main())
