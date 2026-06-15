import csv
from collections import defaultdict

months = defaultdict(list)
with open("../bahia_azul_precios.csv", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        m = int(row["fecha"][5:7])
        months[m].append(float(row["precio_usd"]))

result = {}
for m in range(1, 13):
    if m in months:
        vals = months[m]
        result[m] = {
            "min": min(vals), "max": max(vals), "avg": sum(vals)/len(vals)
        }
    else:
        result[m] = None

# Print as Python arrays for 12 months (index 0 = Jan)
mins = []
maxs = []
avgs = []
for m in range(1, 13):
    if result[m]:
        mins.append(result[m]["min"])
        maxs.append(result[m]["max"])
        avgs.append(round(result[m]["avg"]))
        print(f"  Month {m:2d}: ${result[m]['min']:.0f} - ${result[m]['max']:.0f}  avg=${result[m]['avg']:.0f}")
    else:
        mins.append(None)
        maxs.append(None)
        avgs.append(None)
        print(f"  Month {m:2d}: no data")

print(f"\nba_min = {mins}")
print(f"ba_max = {maxs}")
print(f"ba_avg = {avgs}")
