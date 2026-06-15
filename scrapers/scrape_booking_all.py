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
        while page_num < 15:
            page_num += 1
            await page.wait_for_timeout(2000)
            text = await page.evaluate("() => document.body.innerText")
            all_text.append(text)
            print(f"Page {page_num}: {len(text)} chars")

            next_btn = page.locator("a[aria-label='Página siguiente'], button[aria-label='Página siguiente']")
            if await next_btn.count() == 0:
                next_btn = page.locator("a:has-text('Página siguiente'), button:has-text('Página siguiente')")
            if await next_btn.count() == 0:
                print("No next button")
                break
            disabled = await next_btn.first.get_attribute("aria-disabled")
            if disabled == "true":
                break
            await next_btn.first.click()

        full = "\n".join(all_text)
        with open("data/booking_all_pages.txt", "w", encoding="utf-8") as f:
            f.write(full)
        print(f"\nTotal: {page_num} pages, {len(full)} chars")

        # Parse reviews
        reviews = []
        raw_blocks = full.split("Escrito en ")

        for block in raw_blocks[1:]:
            lines = block.split("\n")
            review = {
                "date_written": lines[0].strip() if lines else "",
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

            i = 1
            current_section = "header"
            pos_parts = []
            neg_parts = []
            header_lines = []

            while i < len(lines):
                line = lines[i].strip()
                if not line:
                    i += 1
                    if current_section == "header":
                        current_section = "negative"
                    continue

                if current_section == "header":
                    if line.startswith("Se alojó en "):
                        review["stay_date"] = line.replace("Se alojó en ", "").strip()
                        current_section = "post_stay"
                    elif line.startswith("•"):
                        header_lines.append(line.replace("•", "").strip())
                    elif line.startswith("Mostrando") or line.startswith("Página"):
                        pass
                    elif re.match(r'^\d+[.,]?\d*$', line):
                        review["rating"] = line.replace(",", ".")
                    elif line.startswith('"') and line.endswith('"'):
                        review["title"] = line.strip('"')
                    elif len(line) < 40 and line.isupper() and not any(c in line for c in ["/", "@", "http"]):
                        review["guest_name"] = line
                    elif line.startswith(" "):
                        review["country"] = line.strip()
                    elif "comentario" in line or "voto" in line:
                        pass
                    else:
                        header_lines.append(line)
                    i += 1
                elif current_section == "negative":
                    if line.startswith("Se alojó en "):
                        review["stay_date"] = line.replace("Se alojó en ", "").strip()
                        current_section = "done"
                    elif line.startswith("•"):
                        pass
                    else:
                        neg_parts.append(line)
                    i += 1
                elif current_section == "positive":
                    if line.startswith("Se alojó en "):
                        review["stay_date"] = line.replace("Se alojó en ", "").strip()
                        current_section = "done"
                    else:
                        pos_parts.append(line)
                    i += 1
                elif current_section == "post_stay":
                    if line.startswith("Se alojó en "):
                        review["stay_date"] = line.replace("Se alojó en ", "").strip()
                        current_section = "done"
                    elif line:
                        pos_parts.append(line)
                    i += 1
                else:
                    i += 1

            review["positive_text"] = " ".join(pos_parts).strip()
            review["negative_text"] = " ".join(neg_parts).strip()
            review["text"] = review["positive_text"] + " " + review["negative_text"]

            # Parse header metadata
            for h in header_lines:
                if "Viaje de ocio" in h or "Viaje de negocios" in h:
                    review["travel_type"] = h
                elif any(g in h for g in ["Persona que viaja sola", "Pareja", "Familia", "Grupo"]):
                    review["group_type"] = h
                elif "Habitación" in h or "habitación" in h:
                    review["room_type"] = h
                elif "Estancia" in h:
                    review["stay_nights"] = h

            if review["rating"] or review["text"]:
                reviews.append(review)

        print(f"\nParsed {len(reviews)} reviews total")

        # Save as JSON
        with open("data/booking_reviews.json", "w", encoding="utf-8") as f:
            json.dump(reviews, f, ensure_ascii=False, indent=2)
        print(f"Saved {len(reviews)} reviews to data/booking_reviews.json")

        # Show sample
        for r in reviews[:3]:
            print(json.dumps(r, ensure_ascii=False, indent=2)[:400])
            print("---")

        await browser.close()

asyncio.run(main())
