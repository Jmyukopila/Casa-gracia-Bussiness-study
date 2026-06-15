import csv
from collections import defaultdict

months = defaultdict(list)
with open("../casa_gracia_precios.csv", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        m = int(row["fecha"][5:7])
        months[m].append(float(row["precio_usd"]))

print("Real CG monthly ranges (Jun-Dec):")
for m in range(6, 13):
    if m in months:
        vals = months[m]
        lo = min(vals); hi = max(vals); avg = sum(vals)/len(vals)
        print(f"  Month {m:2d}: ${lo:.0f} - ${hi:.0f}  avg=${avg:.0f}  n={len(vals)}")

print()

# Estimated for Jan-May
estimates = {
    1: (60, 66, 62),
    2: (60, 66, 62),
    3: (63, 68, 65),
    4: (63, 68, 66),
    5: (60, 66, 62),
}
cg_min = [estimates[m][0] if m in estimates else None for m in range(1,13)]
cg_max = [estimates[m][1] if m in estimates else None for m in range(1,13)]
cg_avg = [estimates[m][2] if m in estimates else None for m in range(1,13)]

for m in range(1, 13):
    if m in months:
        vals = months[m]
        lo = min(vals); hi = max(vals); avg = round(sum(vals)/len(vals))
        cg_min[m-1] = int(lo)
        cg_max[m-1] = int(hi)
        cg_avg[m-1] = avg

print(f"cg_min = {cg_min}")
print(f"cg_max = {cg_max}")
print(f"cg_avg = {cg_avg}")
