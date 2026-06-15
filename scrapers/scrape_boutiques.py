import asyncio, json, os, re, csv
from playwright.async_api import async_playwright

OUTPUT = os.path.join("..", "data", "booking_boutiques.json")
KNOWN_FILE = os.path.join("..", "data", "booking_competitor_prices.json")

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        ctx = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            locale="es-CO", viewport={"width": 1920, "height": 1080},
        )
        page = await ctx.new_page()

        # Known boutique hotels from our data to check specific pages
        known_boutiques = [
            "hotel-boutique-la-artilleria",
            "casa-don-luis-by-faranda-boutique",
            "casa-ebano-967",
            "del-mar-guest-house",
            "villa-alta-guest-house",
            "agena-cabrero",
            "oz-hotel-luxury",
        ]

        results = []

        for slug in known_boutiques:
            url = f"https://www.booking.com/hotel/co/{slug}.html"
            try:
                await page.goto(url, timeout=20000, wait_until="domcontentloaded")
                await page.wait_for_timeout(3000)
                text = await page.inner_text("body")

                # Extract rating
                rating = None
                rm = re.search(r"(\d[.,]\d)\s*(?:Puntuación|Wonderful|Excellent|Very Good|Good)", text)
                if not rm:
                    rm = re.search(r"Scored\s+(\d[.,]\d)", text)
                if rm:
                    rating = float(rm.group(1).replace(",", "."))

                # Extract review count
                reviews = None
                revm = re.search(r"(\d[\d.,]*)\s*(?:comentarios|opiniones|reviews)", text)
                if not revm:
                    revm = re.search(r"(\d+)\s*(?:reseñas|opiniones)", text)
                if revm:
                    reviews = int(revm.group(1).replace(".", "").replace(",", ""))

                # Check for price by searching with dates
                price = None
                pm = re.search(r"COP\s*([\d.]+)", text)
                if pm:
                    price_cop = int(pm.group(1).replace(".", ""))
                    price = round(price_cop / 4200, 0)

                name = slug.replace("-", " ").title()

                results.append({
                    "hotel": name,
                    "slug": slug,
                    "rating": rating,
                    "reviews": reviews,
                    "price_usd": price,
                })
                print(f"  {name:40s} R={rating} N={reviews} ${price}")

            except Exception as e:
                print(f"  {slug}: error - {e}")

        await browser.close()

    # Also extract from known data file
    with open(KNOWN_FILE, encoding="utf-8") as f:
        known = json.load(f)

    # Build unique hotels from the file
    seen = set()
    for season, hotels in known.items():
        for h in hotels:
            title = h["title"]
            if title in seen:
                continue
            seen.add(title)

            rating = None
            rm = re.search(r"Scored\s+(\d[.,]\d)", h["rating"])
            if rm:
                rating = float(rm.group(1).replace(",", "."))
            else:
                rm = re.search(r"(\d[.,]\d)\s*(?:Wonderful|Excellent|Very Good|Good)", h["rating"])
                if rm:
                    rating = float(rm.group(1).replace(",", "."))

            reviews = None
            revm = re.search(r"(\d[\d.,]*)\s*(?:reviews|comentarios)", h["rating"])
            if revm:
                reviews = int(revm.group(1).replace(".", "").replace(",", ""))

            # Check if already in results
            exists = any(r["hotel"].lower() == title.lower() for r in results)
            if not exists and rating and reviews:
                results.append({
                    "hotel": title,
                    "slug": "",
                    "rating": rating,
                    "reviews": reviews,
                    "price_usd": None,
                })
                print(f"  {title:40s} R={rating} N={reviews} (from known data)")

    os.makedirs("..", exist_ok=True)
    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\nSaved {len(results)} hotels to {OUTPUT}")

    # Filter to boutique candidates (50-500 reviews)
    print("\n--- Boutique candidates (50-500 reviews) ---")
    candidates = [r for r in results if r["reviews"] and 30 <= r["reviews"] <= 600]
    for c in sorted(candidates, key=lambda x: x["reviews"]):
        print(f"  {c['hotel']:40s} R={c['rating']} N={c['reviews']} ${c['price_usd']}")

asyncio.run(main())
