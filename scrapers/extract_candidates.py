import json, re

# Extract from known competitor data
with open("../data/booking_competitor_prices.json", encoding="utf-8") as f:
    data = json.load(f)

seen = {}
prices = {}  # hotel -> list of prices COP

for season, hotels in data.items():
    for h in hotels:
        title = h["title"]
        if title not in prices:
            prices[title] = []

        # Extract price (COP format: "COP\xa0540,000")
        pm = re.findall(r"[\d,]+", h["price"])
        if pm:
            cop = int(pm[-1].replace(",", ""))
            prices[title].append(cop)

        # Extract rating
        rating = None
        rm = re.search(r"Scored\s+(\d[.,]\d)", h["rating"])
        if rm:
            rating = float(rm.group(1).replace(",", "."))
        else:
            rm = re.search(r"(\d[.,]\d)\s*(?:Wonderful|Excellent|Very Good|Good)", h["rating"])
            if rm:
                rating = float(rm.group(1).replace(",", "."))

        # Extract reviews
        reviews = None
        revm = re.search(r"(\d+)\s*(?:reviews|comentarios|reseñas)", h["rating"])
        if revm:
            reviews = int(revm.group(1).replace(".", "").replace(",", ""))

        if title not in seen:
            seen[title] = {"rating": rating, "reviews": reviews}
        else:
            # Update if we got better data
            if seen[title]["rating"] is None and rating is not None:
                seen[title]["rating"] = rating
            if seen[title]["reviews"] is None and reviews is not None:
                seen[title]["reviews"] = reviews

# Calculate averages
for title, info in seen.items():
    p = prices[title]
    avg_cop = round(sum(p) / len(p))
    avg_usd = round(avg_cop / 4200)
    # Check if it's a 2-night stay price
    # Most Booking search results show total price for stay, not nightly
    nightly_usd = round(avg_cop / 4200)
    info["avg_cop"] = avg_cop
    info["nightly_usd"] = nightly_usd

print(f"{'Hotel':45s} {'Rating':7s} {'Rev':6s} {'$/night':8s}")
print("-" * 70)

boutique_candidates = []
for title in sorted(seen.keys(), key=lambda t: (seen[t]["reviews"] or 9999)):
    info = seen[title]
    r = info["rating"]
    n = info["reviews"]
    nly = info["nightly_usd"]
    print(f"{title:45s} {str(r):7s} {str(n if n else ''):6s} ${nly}")

    price_str = f"${nly}"
    rating_str = str(r) if r else ""

    if r and n and nly and 30 <= n <= 600:
        boutique_candidates.append({
            "hotel": title,
            "rating": r,
            "reviews": n,
            "nightly_usd": nly,
        })

print(f"\n=== Boutique candidates (30-600 reviews) ===")
for c in sorted(boutique_candidates, key=lambda x: x["reviews"]):
    print(f"  {c['hotel']:45s} R={c['rating']} N={c['reviews']} ${c['nightly_usd']}/night")
