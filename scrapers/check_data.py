import json
from collections import Counter

with open("data/booking_reviews_clean.json", "r", encoding="utf-8") as f:
    reviews = json.load(f)

print(f"Total reviews: {len(reviews)}")
print(f"With rating: {sum(1 for x in reviews if x.get('rating'))}")
print(f"With text: {sum(1 for x in reviews if x.get('text') and len(x['text']) > 10)}")
print(f"Unique countries: {len(set(x.get('country') for x in reviews if x.get('country')))}")

countries = {}
for x in reviews:
    c = x.get("country", "?")
    countries[c] = countries.get(c, 0) + 1
print(f"Countries: {json.dumps(countries, ensure_ascii=False, indent=2)}")

ratings = [float(x["rating"]) for x in reviews if x.get("rating")]
dist = Counter(ratings)
print(f"Rating distribution: {dict(sorted(dist.items()))}")
print(f"Rating avg: {sum(ratings)/len(ratings):.2f}")

# Sample countries with text
print("\nSample countries:", list(countries.keys())[:10])
