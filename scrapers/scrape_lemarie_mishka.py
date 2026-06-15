import asyncio, json, re
from playwright.async_api import async_playwright

HOTELS = [
    {"slug": "le-marie-casa-boutique", "name": "Le Marie B&B"},
    {"slug": "mishka-boutique", "name": "Mishka H. Boutique"},
]

OUTPUT = "../data/lemarie_mishka_datos.json"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        ctx = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            locale="es-CO", viewport={"width": 1920, "height": 1080}
        )
        page = await ctx.new_page()

        results = []

        for h in HOTELS:
            print(f"\n--- {h['name']} ---")
            url = f"https://www.booking.com/hotel/co/{h['slug']}.html"

            try:
                await page.goto(url, timeout=25000, wait_until="domcontentloaded")
                await page.wait_for_timeout(5000)
                text = await page.inner_text("body")

                # Rating
                rating = None
                rm = re.search(r"Scored\s+(\d[.,]\d)", text)
                if rm:
                    rating = float(rm.group(1).replace(",", "."))

                # Reviews count
                reviews = None
                revm = re.search(r"(\d[\d.,]*)\s*(?:opiniones|comentarios|reseñas|review)", text)
                if revm:
                    reviews = int(revm.group(1).replace(".", "").replace(",", ""))

                # Sub-scores
                scores = {}
                score_labels = [
                    "Personal", "Staff", "Instalaciones", "Facilities",
                    "Limpieza", "Cleanliness", "Confort", "Comfort",
                    "Relación calidad-precio", "Value for money",
                    "Ubicación", "Location", "WiFi gratis", "Free WiFi",
                    "Desayuno", "Breakfast",
                ]
                for label in score_labels:
                    # Pattern: "label   X.X" or "label  X.X"
                    m = re.search(rf"{re.escape(label)}\s*(\d[.,]\d)", text, re.IGNORECASE)
                    if m:
                        key = label[:10]  # Shorten key
                        scores[key] = float(m.group(1).replace(",", "."))

                # Price from search results with dates
                pm = re.findall(r"COP\s*[$\xa0]*([\d.,]+)", text)
                price_usd = None
                if pm:
                    cop = int(pm[-1].replace(".", "").replace(",", ""))
                    price_usd = round(cop / 4200)

                # Also try to find the listed price range
                # Check for "Precio desde" patterns
                pm2 = re.search(r"(?:desde|from)\s*(?:COP)?\s*[$\xa0]*([\d.,]+)", text)
                if pm2 and not price_usd:
                    cop = int(pm2.group(1).replace(".", "").replace(",", ""))
                    price_usd = round(cop / 4200)

                print(f"  R={rating} N={reviews} P=${price_usd}")
                print(f"  Scores: {scores}")

                results.append({
                    "hotel": h["name"],
                    "slug": h["slug"],
                    "rating": rating,
                    "reviews": reviews,
                    "price_usd": price_usd,
                    "sub_scores": scores,
                    "raw_snippet": text[:1000],
                })

            except Exception as e:
                print(f"  Error: {e}")

        await browser.close()

        with open(OUTPUT, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        print(f"\nSaved to {OUTPUT}")

asyncio.run(main())
