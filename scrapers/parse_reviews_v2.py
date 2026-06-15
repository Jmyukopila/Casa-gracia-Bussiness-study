import json, re, sys
sys.stdout.reconfigure(encoding='utf-8')

with open("data/booking_all_pages.txt", "r", encoding="utf-8") as f:
    text = f.read()

blocks = re.split(r'\n(?=Escrito en )', text)
reviews = []

for block in blocks:
    if not block.startswith("Escrito en "):
        continue

    lines = block.strip().split("\n")
    entry = {
        "date_written": lines[0].replace("Escrito en ", "").strip(),
        "guest_name": "",
        "country": "",
        "rating": "",
        "title": "",
        "travel_type": "",
        "group_type": "",
        "room_type": "",
        "stay_nights": "",
        "negative_text": "",
        "positive_text": "",
        "stay_date": "",
    }

    # Scan through lines to identify parts
    i = 1
    mode = "preamble"  # preamble -> header -> bullet -> text -> done
    header_items = []
    text_paragraphs = []
    bullets_done = False

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if mode == "preamble":
            if stripped == "":
                i += 1
                continue
            # Check raw line for leading space (country indicator)
            if not entry["country"] and line.startswith(" "):
                entry["country"] = stripped
                i += 1
                continue
            # This is name or country before header items
            if not entry["guest_name"] and len(stripped) < 40:
                entry["guest_name"] = stripped
            elif "comentario" in stripped:
                pass  # skip
            elif "voto" in stripped:
                pass  # skip
            elif re.match(r'^\d+[.,]?\d*\s*$', stripped.replace("\t", "")):
                entry["rating"] = stripped.replace(",", ".").strip()
            elif stripped.startswith('"') and stripped.endswith('"'):
                entry["title"] = stripped.strip('"')
            elif stripped and not stripped.startswith("•"):
                entry["title"] = stripped
            elif stripped.startswith("•"):
                mode = "bullet"
                continue
            i += 1

        elif mode == "bullet":
            if stripped == "":
                # End of bullet section
                mode = "text"
                i += 1
                continue
            if stripped.startswith("•"):
                i += 1
                continue
            # This is a bullet value
            if "Viaje" in stripped:
                entry["travel_type"] = stripped
            elif any(g in stripped for g in ["Persona que viaja sola", "Pareja", "Familia", "Grupo", "Amigos"]):
                entry["group_type"] = stripped
            elif "Habitación" in stripped:
                entry["room_type"] = stripped
            elif "Estancia" in stripped:
                entry["stay_nights"] = stripped
            elif "Enviado por" in stripped:
                pass
            i += 1

        elif mode == "text":
            if "Se alojó en " in line:
                entry["stay_date"] = line.replace("Se alojó en ", "").strip()
                mode = "done"
                break
            if stripped:
                text_paragraphs.append(stripped)
            i += 1

        elif mode == "done":
            break
        else:
            i += 1

    # Parse text paragraphs: first short one is negative, rest are positive
    if len(text_paragraphs) >= 2 and len(text_paragraphs[0]) < 150 and len(text_paragraphs[0]) < len(text_paragraphs[1]) * 0.6:
        entry["negative_text"] = text_paragraphs[0]
        entry["positive_text"] = " ".join(text_paragraphs[1:])
    elif len(text_paragraphs) >= 1:
        entry["positive_text"] = " ".join(text_paragraphs)

    entry["text"] = (entry["negative_text"] + " " + entry["positive_text"]).strip()

    if entry.get("rating") or entry.get("text"):
        reviews.append(entry)

print(f"Parsed {len(reviews)} reviews")

ratings = [float(r["rating"].replace(",", ".")) for r in reviews if r.get("rating")]
if ratings:
    print(f"Ratings: min={min(ratings):.1f}, max={max(ratings):.1f}, avg={sum(ratings)/len(ratings):.2f}")
with_text = [r for r in reviews if r.get("text")]
print(f"With text: {len(with_text)}, with names: {sum(1 for r in reviews if r.get('guest_name'))}")
print(f"With country: {sum(1 for r in reviews if r.get('country'))}")

# Show samples
print("\n--- Samples ---")
for idx in [0, 1, 6, 15]:
    if idx < len(reviews):
        r = reviews[idx]
        print(f"\nReview #{idx}: {r.get('guest_name','?')} from {r.get('country','?')} | Rating: {r.get('rating','?')} | Title: {r.get('title','?')}")
        if r.get("negative_text"):
            print(f"  NEG: {r['negative_text'][:150]}")
        if r.get("positive_text"):
            print(f"  POS: {r['positive_text'][:200]}")

with open("data/booking_reviews_clean.json", "w", encoding="utf-8") as f:
    json.dump(reviews, f, ensure_ascii=False, indent=2)
print(f"\nSaved to data/booking_reviews_clean.json")
