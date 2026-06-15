import requests, re, json

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}

HOTELS = [
    {"slug": "le-marie-casa-boutique", "name": "Le Marie B&B"},
    {"slug": "mishka-boutique", "name": "Mishka H. Boutique"},
]

results = []

for h in HOTELS:
    print(f"\n--- {h['name']} ---")
    url = f"https://www.booking.com/hotel/co/{h['slug']}.html"

    try:
        r = requests.get(url, headers=headers, timeout=15)
        t = r.text

        # Rating from JSON-LD or data attributes
        rating = None
        rm = re.search(r'"averageScore":([\d.]+)', t)
        if rm:
            rating = float(rm.group(1))

        # Reviews
        reviews = None
        rv = re.search(r'"numberOfReviews":(\d+)', t)
        if rv:
            reviews = int(rv.group(1))
        if not reviews:
            rv2 = re.search(r'(\d+)\s*(?:review|opinion|opinione)', t)
            if rv2:
                reviews = int(rv2.group(1))

        # Sub-scores from JSON
        scores = {}
        for label in ["staff", "facilities", "cleanliness", "comfort", "value_for_money", "location", "free_wifi"]:
            m = re.search(rf'"{label}":([\d.]+)', t)
            if m:
                scores[label] = float(m.group(1))

        # Price - search for various patterns
        price_usd = None
        # Try JSON price
        pm = re.search(r'"price":\{[^}]*"value":([\d.]+)', t)
        if pm:
            price_usd = round(float(pm.group(1)))
        if not price_usd:
            pm2 = re.findall(r'COP[^0-9]*([\d.,]+)', t)
            if pm2:
                cop = int(pm2[0].replace(".", "").replace(",", ""))
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
        })

    except Exception as e:
        print(f"  Error: {e}")

with open("../data/lemarie_mishka_datos.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print(f"\nSaved {len(results)} hotels")
