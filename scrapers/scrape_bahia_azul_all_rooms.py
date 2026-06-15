import asyncio, json, os, re, sys
from playwright.async_api import async_playwright
sys.stdout.reconfigure(encoding='utf-8')

EXCHANGE = 4200.0
OUTPUT = os.path.join("data", "bahia_azul_full_prices.json")

SEASONS = [
    {"label": "feb (baja)",   "ci": "2027-02-10", "co": "2027-02-13", "nights": 3},
    {"label": "jul (media)",  "ci": "2026-07-15", "co": "2026-07-17", "nights": 2},
    {"label": "nov (festival)","ci": "2026-11-01", "co": "2026-11-03", "nights": 2},
    {"label": "dic (navidad)", "ci": "2026-12-20", "co": "2026-12-27", "nights": 7},
]

BOOKING_URL = "https://www.booking.com/hotel/co/bahia-azul-manga-cartagena.html"

results = []

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
            locale="es-CO", viewport={"width": 1920, "height": 1080},
        )
        page = await context.new_page()

        for s in SEASONS:
            lbl = s["label"]
            url = f"{BOOKING_URL}?checkin={s['ci']}&checkout={s['co']}&group_adults=2&no_rooms=1&selected_currency=COP"
            try:
                await page.goto(url, timeout=30000, wait_until="domcontentloaded")
                await page.wait_for_timeout(6000)
            except:
                print(f"  {lbl}: timeout")
                results.append({"season": lbl, "rooms": []})
                continue

            html = await page.content()
            text = await page.inner_text("body")

            # Find all room prices: "COP X.XXX" patterns after room descriptions
            room_sections = re.split(r"\n\s*\n\s*(?:Habitaci[oó]n|Suite)", text)

            rooms = []
            # Find room names (the section headers)
            room_names = re.findall(r"(?:Habitaci[oó]n\s+Doble[^\\n]*|Suite)", text)

            # Find all unique prices after "Precio COP" or "COP X.XXX" in price blocks
            price_matches = re.findall(r"COP[^\S\r\n]*([\d.]+)", text)

            # De-duplicate prices (some appear twice due to "1 adulto" variants)
            seen = set()
            unique_prices = []
            for p in price_matches:
                val = int(p.replace(".", ""))
                if val not in seen and val > 100:
                    seen.add(val)
                    unique_prices.append(val)

            # Map room types to prices based on order
            # Structure is: room name, then its price, then maybe "1 persona" with same price
            # After each room's price section, next room starts
            room_type_order = [
                "Habitacion Doble con bano privado (1 cama)",
                "Habitacion Doble con bano privado - 2 camas",
                "Suite",
            ]

            # More precise: find unique prices that are room totals (not impuestos, not desayuno)
            room_totals = []
            # Pattern: "COP X.XXX" on a line by itself (before "Precio COP" or after room name)
            clean_matches = re.findall(r"^COP[^\S\r\n]*([\d.]+)$", text, re.MULTILINE)
            for p in clean_matches:
                val = int(p.replace(".", ""))
                if val not in room_totals and val > 100:
                    room_totals.append(val)

            if not room_totals:
                room_totals = unique_prices[:6]  # fallback

            # Group: first price is for room type 1 (max 2 pax), then same price for 1 pax variant
            # then next price for room type 2, etc.
            prices_clean = []
            i = 0
            while i < len(room_totals):
                prices_clean.append(room_totals[i])
                if i + 1 < len(room_totals) and room_totals[i + 1] == room_totals[i]:
                    i += 2  # skip duplicate (1 pax variant)
                else:
                    i += 1

            for idx, total in enumerate(prices_clean[:3]):
                rname = room_type_order[idx] if idx < len(room_type_order) else f"Room {idx+1}"
                per_night_cop = total // s["nights"]
                usd = round(per_night_cop / EXCHANGE, 2)
                rooms.append({
                    "type": rname,
                    "total_cop": total,
                    "per_night_cop": per_night_cop,
                    "usd_per_night": usd,
                })
                print(f"  {lbl:20s} {rname:45s} COP {total:>9,} total -> COP {per_night_cop:>6,}/noche -> ${usd:.0f}/noche USD")

            if rooms:
                min_p = min(r["usd_per_night"] for r in rooms)
                max_p = max(r["usd_per_night"] for r in rooms)
                avg_p = sum(r["usd_per_night"] for r in rooms) / len(rooms)
                print(f"  {'':20s} {'RANGO':45s} ${min_p:.0f} - ${max_p:.0f} USD/noche (avg ${avg_p:.0f})")
            else:
                print(f"  {lbl}: no prices found")

            results.append({"season": lbl, "rooms": rooms})

        await browser.close()

    os.makedirs("data", exist_ok=True)
    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\nSaved to {OUTPUT}")

asyncio.run(main())
