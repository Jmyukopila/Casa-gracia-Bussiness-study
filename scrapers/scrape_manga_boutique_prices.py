import asyncio, json, re
from playwright.async_api import async_playwright

OUTPUT = "../data/manga_boutique_prices.json"

# Specific Manga boutique hotel slugs on Booking.com
TARGETS = [
    {
        "slug": "boutique-tierra-del-mar-cartagena",
        "hotel": "Boutique Tierra Del Mar",
        "area": "Manga"
    },
    {
        "slug": "abel-boutique-house",
        "hotel": "Abel Boutique House",
        "area": "Manga"
    },
    {
        "slug": "casa-roman-hotel-boutique",
        "hotel": "Casa Roman Hotel Boutique",
        "area": "Manga"
    },
    {
        "slug": "mishka-boutique",
        "hotel": "Mishka Hotel Boutique",
        "area": "Manga"
    },
    {
        "slug": "maranga-boutique",
        "hotel": "Maranga Boutique",
        "area": "Manga"
    },
    # Also check Casa Ebano 967 (Getsemani, mid-size)
    {
        "slug": "casa-ebano-967",
        "hotel": "Casa Ebano 967",
        "area": "Getsemani"
    },
    # Del Mar Guest House
    {
        "slug": "del-mar-guest-house",
        "hotel": "Del Mar Guest House",
        "area": "Bocagrande"
    },
    # San Sebastian Real (verify)
    {
        "slug": "hotel-san-sebastian-real",
        "hotel": "Hotel San Sebastian Real",
        "area": "Manga/Cabrero"
    },
]

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        ctx = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            locale="es-CO",
            viewport={"width": 1920, "height": 1080}
        )
        page = await ctx.new_page()

        results = []

        for t in TARGETS:
            print(f"\n--- {t['hotel']} ---")
            slug = t["slug"]
            url = f"https://www.booking.com/hotel/co/{slug}.html"

            try:
                await page.goto(url, timeout=25000, wait_until="domcontentloaded")
                await page.wait_for_timeout(4000)
                text = await page.inner_text("body")

                # Rating
                rating = None
                rm = re.search(r"Scored\s+(\d[.,]\d)", text)
                if rm:
                    rating = float(rm.group(1).replace(",", "."))
                if not rating:
                    rm = re.search(r"(\d[.,]\d)\s*(?:Rated|Puntuación|Maravilloso|Fabuloso|Wonderful|Excellent|Very Good|Good|Normal|Muy bien|Fantástico|Excepcional)", text)
                    if rm:
                        rating = float(rm.group(1).replace(",", "."))

                # Reviews count
                reviews = None
                revm = re.search(r"(\d[\d.,]*)\s*(?:opiniones|comentarios|reseñas|review)", text)
                if revm:
                    reviews = int(revm.group(1).replace(".", "").replace(",", ""))
                if not reviews:
                    revm = re.search(r"rated\s+(?:by\s+)?(\d[\d.,]*)", text, re.IGNORECASE)
                    if revm:
                        reviews = int(revm.group(1).replace(".", "").replace(",", ""))

                # Price — search with checkin dates to get a live price
                # First try to find price on page
                price = None
                pm = re.search(r"COP\s*[$\xa0]*([\d.,]+)", text)
                if pm:
                    cop = int(pm.group(1).replace(".", "").replace(",", ""))
                    price = round(cop / 4200)

                print(f"  R={rating} N={reviews} P=${price}")

                results.append({
                    "hotel": t["hotel"],
                    "slug": slug,
                    "area": t["area"],
                    "rating": rating,
                    "reviews": reviews,
                    "price_usd": price,
                })

            except Exception as e:
                print(f"  Error: {e}")

        await browser.close()

        with open(OUTPUT, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        print(f"\nSaved {len(results)} hotels to {OUTPUT}")
        print("\n=== CANDIDATES for scatter ===")
        for r in results:
            if r["rating"] and r["reviews"] and 10 <= r["reviews"] <= 600:
                print(f"  {r['hotel']:35s} | R={r['rating']} | N={r['reviews']} | ${r['price_usd']} | {r['area']}")

asyncio.run(main())
