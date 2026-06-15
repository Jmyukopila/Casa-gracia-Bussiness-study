import json, re, sys

sys.stdout.reconfigure(encoding='utf-8')

# Read the raw text from both pages
with open("data/booking_all_pages.txt", "r", encoding="utf-8") as f:
    text = f.read()

# Split into review blocks
blocks = re.split(r'\n(?=Escrito en )', text)
print(f"Total blocks: {len(blocks)}")

reviews = []

for block in blocks:
    if not block.startswith("Escrito en "):
        continue

    lines = block.strip().split("\n")
    entry = {
        "date_written": "",
        "guest_name": "",
        "country": "",
        "rating": "",
        "title": "",
        "travel_type": "",
        "group_type": "",
        "room_type": "",
        "stay_nights": "",
        "positive_text": "",
        "negative_text": "",
        "stay_date": "",
    }

    # First line is date
    entry["date_written"] = lines[0].replace("Escrito en ", "").strip()

    # Find the stay date line to split header from body
    body_start = None
    for i, line in enumerate(lines):
        if "Se alojó en " in line:
            entry["stay_date"] = line.replace("Se alojó en ", "").strip()
            body_start = i
            break

    if body_start is None:
        body_start = len(lines)

    # Header = lines[1:body_start]
    header_lines = [l.strip() for l in lines[1:body_start] if l.strip()]

    # Parse header
    mode = "metadata"
    for h in header_lines:
        if h.startswith("•"):
            h_clean = h.replace("•", "").strip()
            if "Viaje" in h_clean:
                entry["travel_type"] = h_clean
            elif any(g in h_clean for g in ["Persona que viaja sola", "Pareja", "Familia", "Grupo", "Amigos"]):
                entry["group_type"] = h_clean
            elif "Habitación" in h_clean:
                entry["room_type"] = h_clean
            elif "Estancia" in h_clean:
                entry["stay_nights"] = h_clean
            elif "Enviado por" in h_clean:
                pass
        elif re.match(r'^\d+[.,]?\d*$', h):
            entry["rating"] = h.replace(",", ".")
        elif h.startswith('"') and h.endswith('"'):
            entry["title"] = h.strip('"')
        elif "comentario" in h or "voto" in h or "votos" in h:
            pass
        elif len(h) < 40 and h.isupper() and not any(c in h for c in ["/", "@", "http", ".com"]):
            entry["guest_name"] = h
        elif h[0].isupper() and len(h) < 25 and not entry["country"]:
            entry["country"] = h

    # Body = lines after stay_date
    body_lines = []
    if body_start and body_start + 1 < len(lines):
        for l in lines[body_start+1:]:
            l = l.strip()
            if l and not l.startswith("Mostrando") and not l.startswith("Página") and not l.startswith("Igualamos"):
                body_lines.append(l)

    # The review text: often two paragraphs (negative first, positive second)
    # But structure varies. Some have just one paragraph.
    # Also sometimes there's no clear split.
    body_text = " ".join(body_lines)

    # Heuristic: if there are 2+ paragraphs and first is short (<50% of second), it's negative
    paragraphs = [b for b in body_lines if len(b) > 5]
    if len(paragraphs) >= 2 and len(paragraphs[0]) < len(paragraphs[1]) * 0.5:
        entry["negative_text"] = paragraphs[0]
        entry["positive_text"] = " ".join(paragraphs[1:])
    elif len(paragraphs) >= 1:
        entry["positive_text"] = " ".join(paragraphs)

    entry["text"] = body_text

    if entry["rating"] or body_text:
        reviews.append(entry)

print(f"Parsed {len(reviews)} reviews")

# Stats
ratings = [float(r["rating"]) for r in reviews if r.get("rating")]
if ratings:
    print(f"Rating range: {min(ratings):.1f} - {max(ratings):.1f}, avg: {sum(ratings)/len(ratings):.2f}")

with_text = [r for r in reviews if r.get("text")]
print(f"With text: {len(with_text)}")
with_names = [r for r in reviews if r.get("guest_name")]
print(f"With guest name: {len(with_names)}")

# Show samples
print("\n--- Sample 1 ---")
r = reviews[0]
for k, v in r.items():
    if v:
        print(f"  {k}: {v[:200]}")

print("\n--- Sample 2 ---")
r = reviews[1] if len(reviews) > 1 else reviews[0]
for k, v in r.items():
    if v:
        print(f"  {k}: {v[:200]}")

# Save clean JSON
with open("data/booking_reviews_clean.json", "w", encoding="utf-8") as f:
    json.dump(reviews, f, ensure_ascii=False, indent=2)
print(f"\nSaved clean JSON to data/booking_reviews_clean.json")
