import asyncio, json, re
from playwright.async_api import async_playwright

OUTPUT = "../data/booking_manga_hotels.json"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        ctx = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            locale="es-CO",
            viewport={"width": 1920, "height": 1080}
        )
        page = await ctx.new_page()

        # Search Booking.com for Cartagena Manga
        # First search Cartagena then filter by Manga district
        urls = [
            # Direct Manga district search
            "https://www.booking.com/searchresults.es.html?ss=Cartagena+de+Indias%2C+Colombia&district=3342&checkin=2026-09-01&checkout=2026-09-03&group_adults=2&no_rooms=1&order=bayesian_review_score",
            # Also search hoteles boutique
            "https://www.booking.com/searchresults.es.html?ss=Cartagena+de+Indias%2C+Colombia&nflt=ht_id%3D204&checkin=2026-09-01&checkout=2026-09-03&group_adults=2&no_rooms=1&order=bayesian_review_score",
        ]

        all_hotels = []

        for url in urls:
            try:
                print(f"Fetching: {url}")
                await page.goto(url, timeout=30000, wait_until="domcontentloaded")
                await page.wait_for_timeout(5000)

                # Scroll to load more results
                for _ in range(3):
                    await page.evaluate("window.scrollBy(0, 800)")
                    await page.wait_for_timeout(1000)

                # Get all hotel cards
                cards = await page.query_selector_all('[data-testid="property-card"]')
                print(f"  Found {len(cards)} cards")

                for card in cards:
                    try:
                        text = await card.inner_text()
                    except:
                        continue

                    # Title
                    title_el = await card.query_selector('[data-testid="title"]')
                    title = ""
                    if title_el:
                        title = (await title_el.inner_text()).strip()

                    # Rating
                    rating = None
                    rm = re.search(r"(\d[.,]\d)\s*(?:Puntuación|Maravilloso|Fabuloso|Muy bien|Fantástico|Estupendo|Bien|Excepcional|Wonderful|Excellent|Very Good|Good)", text)
                    if rm:
                        rating = float(rm.group(1).replace(",", "."))

                    # Reviews
                    reviews = None
                    revm = re.search(r"(\d[\d.,]*)\s*(?:opiniones|reseñas|comentarios)", text)
                    if revm:
                        reviews = int(revm.group(1).replace(".", "").replace(",", ""))

                    # Price
                    price = None
                    pm = re.findall(r"COP\s*[$\xa0]*([\d.,]+)", text)
                    if pm:
                        cop = 0
                        for p in pm:
                            cop = max(cop, int(p.replace(".", "").replace(",", "")))
                        price_night = round(cop / 4200)

                    all_hotels.append({
                        "title": title,
                        "rating": rating,
                        "reviews": reviews,
                        "price_usd_night": price_night if price else None,
                        "url": url,
                    })
                    print(f"  {title[:40]:40s} R={rating} N={reviews} P={price_night if price else None}")

            except Exception as e:
                print(f"  Error: {e}")

        await browser.close()

        # Deduplicate
        seen = set()
        unique = []
        for h in all_hotels:
            key = h["title"].lower()
            if key not in seen:
                seen.add(key)
                unique.append(h)

        with open(OUTPUT, "w", encoding="utf-8") as f:
            json.dump(unique, f, indent=2, ensure_ascii=False)

        print(f"\nTotal unique: {len(unique)} saved to {OUTPUT}")

        # Also check specific known boutique hotels in Manga
        print("\n--- Checking specific Manga boutique hotels ---")
        manga_hotels = [
            "casa-roman-hotel-boutique",
            "casa-gracia-hotel-manga-cartagena",
            "tierra-del-mar",
        ]

        for slug in manga_hotels:
            url = f"https://www.booking.com/hotel/co/{slug}.html"
            try:
                await page.goto(url, timeout=15000, wait_until="domcontentloaded")
                await page.wait_for_timeout(3000)
                text = await page.inner_text("body")

                rating = None
                rm = re.search(r"(\d[.,]\d)\s*(?:Puntuación|Maravilloso|Fabuloso|Muy bien)", text)
                if rm:
                    rating = float(rm.group(1).replace(",", "."))

                reviews = None
                revm = re.search(r"(\d[\d.,]*)\s*(?:opiniones|comentarios|reseñas)", text)
                if revm:
                    reviews = int(revm.group(1).replace(".", "").replace(",", ""))

                print(f"  {slug:40s} R={rating} N={reviews}")

            except Exception as e:
                print(f"  {slug}: error - {e}")

asyncio.run(main())
