import json, re

COP_TO_USD = 4200  # approximate

with open("data/booking_competitor_prices.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Parse numeric price from COP string
def parse_cop_price(s):
    if not s or s == "N/A":
        return None
    nums = re.findall(r'[\d,]+', s.replace("COP", "").replace("$", ""))
    if nums:
        return int(nums[0].replace(",", ""))
    return None

# Hotels in Manga area (Manga-specific search would be ideal, but Booking
# doesn't filter by neighborhood easily. We'll identify Manga hotels manually.)
MANGA_HOTELS = {"Casa Gracia", "Bahía Azul", "Hotel San Sebastian Real"}
# Actually from the data, Hotel San Sebastian Real appeared - let me check if it's in Manga
# Let me just compute general market stats

print("=" * 80)
print("PRECIOS DE MERCADO - CARTAGENA (Booking.com)")
print(f"Tasa de cambio: 1 USD = {COP_TO_USD:,} COP")
print("=" * 80)

seasons_display = {"jul": "Julio (temporada media)", "nov": "Noviembre (Festival Náutico)", "dec": "Diciembre (Navidad)", "feb": "Febrero (temporada baja)"}

for season in ["jul", "nov", "dec", "feb"]:
    hotels = data.get(season, [])
    prices = []
    for h in hotels:
        p = parse_cop_price(h["price"])
        if p:
            prices.append(p)
    
    if prices:
        avg_cop = sum(prices) / len(prices)
        min_cop = min(prices)
        max_cop = max(prices)
        print(f"\n  {seasons_display.get(season, season)}:")
        print(f"    {len(prices)} hoteles con precio")
        print(f"    Promedio: COP ${avg_cop:,.0f} = ${avg_cop/COP_TO_USD:.0f} USD/noche")
        print(f"    Rango: COP ${min_cop:,} - ${max_cop:,} (${min_cop/COP_TO_USD:.0f} - ${max_cop/COP_TO_USD:.0f} USD)")

# Now find cheapest non-hostel hotels in each season as comps for Casa Gracia
print("\n" + "=" * 80)
print("COMPETIDORES DIRECTOS (boutique hotels < $100 USD/noche)")
print("=" * 80)

for season in ["jul", "nov", "dec", "feb"]:
    hotels = data.get(season, [])
    cheap_boutiques = []
    for h in hotels:
        p = parse_cop_price(h["price"])
        if p and p / COP_TO_USD < 150:
            title = h["title"].strip()
            rating = h["rating"].strip()[:20] if h["rating"] else "N/A"
            cheap_boutiques.append((title, p / COP_TO_USD, rating))
    
    print(f"\n  {seasons_display.get(season, season)}:")
    for name, price_usd, rating in sorted(cheap_boutiques, key=lambda x: x[1])[:8]:
        print(f"    ${price_usd:.0f} | {rating} | {name[:50]}")

# Casa Gracia competitors specifically (hotels that appear to be in Manga/Cabrero area)
print("\n" + "=" * 80)
print("PRECIOS HOTEL SAN SEBASTIAN REAL (posible Manga) por temporada")
print("=" * 80)
for season in ["jul", "nov", "dec", "feb"]:
    hotels = data.get(season, [])
    for h in hotels:
        if "San Sebastian" in h["title"] or "Agena" in h["title"]:
            p = parse_cop_price(h["price"])
            usd = p / COP_TO_USD if p else 0
            print(f"  {seasons_display.get(season, season)}: {h['title'][:40]} | {h['price'][:30]} | ${usd:.0f} USD")
