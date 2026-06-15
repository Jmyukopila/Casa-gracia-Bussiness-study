import asyncio, json, sys, re
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8')

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=["--disable-blink-features=AutomationControlled"])
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            locale="es-ES", viewport={"width": 1280, "height": 900},
        )
        page = await context.new_page()
        await page.goto(
            "https://www.booking.com/reviews/co/hotel/casa-gracia.es.html",
            timeout=30000, wait_until="domcontentloaded"
        )
        await page.wait_for_timeout(5000)

        try:
            accept = page.locator("button:has-text('Aceptar')")
            if await accept.count() > 0:
                await accept.first.click()
                await page.wait_for_timeout(1000)
        except:
            pass

        all_text = []
        page_num = 0
        max_pages = 15

        while page_num < max_pages:
            page_num += 1
            await page.wait_for_timeout(2500)
            text = await page.evaluate("() => document.body.innerText")
            all_text.append(text)
            print(f"Page {page_num}: {len(text)} chars")

            # Find the "Página siguiente" link by text
            next_btn = page.locator("a:has-text('Página siguiente')")
            count = await next_btn.count()
            print(f"  Next buttons found: {count}")

            if count == 0:
                print("No more 'Página siguiente' — stopping")
                break

            is_disabled = await next_btn.first.get_attribute("aria-disabled")
            if is_disabled == "true":
                print("Next button disabled — stopping")
                break

            await next_btn.first.click()
            await page.wait_for_timeout(3000)

        full = "\n".join(all_text)
        with open("data/booking_all_pages.txt", "w", encoding="utf-8") as f:
            f.write(full)
        print(f"\nCollected {page_num} pages, {len(full)} total chars")

        # --- Parse reviews robustly ---
        # Split by review boundary: "Escrito en {date}"
        reviews = []
        blocks = re.split(r'Escrito en ', full)

        for block in blocks[1:]:
            entry = {}
            lines = block.split("\n")

            # First line = date
            entry["date_written"] = lines[0].strip() if len(lines) > 0 else ""

            # Find "Se alojó en" line to split header from text
            stay_idx = None
            for i, line in enumerate(lines):
                if "Se alojó en " in line:
                    entry["stay_date"] = line.replace("Se alojó en ", "").strip()
                    stay_idx = i
                    break

            # Everything before stay_idx is header
            header_lines = []
            if stay_idx:
                header_lines = lines[1:stay_idx]
                # Everything after stay_idx but before next review is review text
                review_text_lines = lines[stay_idx+1:]
            else:
                header_lines = lines[1:]
                review_text_lines = []

            # Parse header
            for h in header_lines:
                h = h.strip()
                if not h:
                    continue
                # Metadata lines
                if h.startswith("•"):
                    h = h.replace("•", "").strip()
                    if "Viaje" in h:
                        entry["travel_type"] = h
                    elif any(g in h for g in ["Persona que viaja sola", "Pareja", "Familia", "Grupo", "Amigos"]):
                        entry["group_type"] = h
                    elif "Habitación" in h:
                        entry["room_type"] = h
                    elif "Estancia" in h:
                        entry["stay_nights"] = h
                    elif "Enviado por" in h:
                        entry["device"] = h
                    else:
                        entry.setdefault("other_meta", []).append(h)
                elif re.match(r'^\d+[.,]?\d*$', h):
                    entry["rating"] = h.replace(",", ".")
                elif h.startswith('"') and h.endswith('"'):
                    entry["title"] = h.strip('"')
                elif "comentario" in h:
                    entry["guest_comments"] = h
                elif "voto" in h:
                    entry["guest_votes"] = h
                elif len(h) < 40 and h.isupper() and not any(c in h for c in ["/", "@", "http"]):
                    entry["guest_name"] = h
                elif h.startswith(" ") or (len(h) < 30 and not h[0].isupper() if h else True):
                    entry["country"] = h.strip()

            # Review text — split into segments (negative before positive, or single)
            cleaned = [l.strip() for l in review_text_lines if l.strip() and not l.strip().startswith("Mostrando") and not l.strip().startswith("Página")]
            # Common pattern: first paragraph is negative ("Nada", "Que no..."), second is positive
            # Or just one paragraph
            text = " ".join(cleaned)
            entry["text"] = text

            # Try to split positive/negative based on patterns
            # Often there are two paragraphs: first negative (short), second longer positive
            # But not always - some have only positive, some only negative
            paragraphs = [c for c in cleaned if len(c) > 5]
            if len(paragraphs) >= 2:
                # Usually the first short one is negative, second longer is positive
                if len(paragraphs[0]) < len(paragraphs[1]) * 0.7:
                    entry["negative_text"] = paragraphs[0]
                    entry["positive_text"] = " ".join(paragraphs[1:])
                else:
                    entry["positive_text"] = " ".join(paragraphs)
            elif len(paragraphs) == 1:
                entry["positive_text"] = paragraphs[0] if len(paragraphs[0]) > 10 else ""
                if len(paragraphs[0]) <= 10:
                    entry["negative_text"] = paragraphs[0]
            else:
                entry["positive_text"] = text

            if entry.get("rating") or entry.get("text"):
                reviews.append(entry)

        print(f"\nParsed {len(reviews)} reviews")

        # Show stats
        with_rating = sum(1 for r in reviews if r.get("rating"))
        with_text = sum(1 for r in reviews if r.get("text"))
        with_name = sum(1 for r in reviews if r.get("guest_name"))
        print(f"With rating: {with_rating}, With text: {with_text}, With name: {with_name}")

        # Save
        with open("data/booking_reviews.json", "w", encoding="utf-8") as f:
            json.dump(reviews, f, ensure_ascii=False, indent=2)
        print(f"Saved to data/booking_reviews.json")

        # Sample
        for r in reviews[:2]:
            print(json.dumps({k:v for k,v in r.items() if v}, ensure_ascii=False, indent=2)[:500])

        await browser.close()

asyncio.run(main())
