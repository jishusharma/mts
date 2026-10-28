import json, glob, os

files = sorted(glob.glob(r".\runtime_data\snapshots\BTCUSDT_*.json"), key=os.path.getmtime)

# Filter: keep only snapshots >= 10 min apart (avoid test-burst noise)
import time
filtered = []
last_t = 0
for f in files:
    t = os.path.getmtime(f)
    if t - last_t >= 600:
        filtered.append(f)
        last_t = t

# Load last 8 filtered snapshots
data = []
for f in filtered[-8:]:
    with open(f, encoding="utf-8") as fh:
        s = json.load(fh)
    data.append({
        "file": os.path.basename(f),
        "time": s.get("timestamp_utc", "")[11:19],
        "price": s.get("current_price", 0),
        "cvd": s.get("cvd", {}).get("value", 0),
        "net_delta": s.get("trade_flow", {}).get("net_delta_1m", 0),
        "oi_dir": s.get("open_interest", {}).get("direction", "unknown"),
        "oi_pct": s.get("open_interest", {}).get("change_1h_pct", 0),
        "session": s.get("cvd", {}).get("session_start_utc", ""),
    })

# Thresholds for meaningful change
PRICE_MIN = 30.0       # pts
CVD_MIN = 200.0        # absolute delta
ND_MIN = 20.0          # absolute delta

def direction(a, b, threshold):
    d = b - a
    if abs(d) < threshold:
        return "flat"
    return "up" if d > 0 else "down"

print("=" * 92)
print("DIVERGENCE MONITOR — last 6 snapshots")
print("=" * 92)
print()

# Pairwise direction matrix
print(f"{'pair':<22} {'price':>7} {'cvd':>7} {'netdelta':>9} {'oi':>10} | flags")
print("-" * 92)

for i in range(1, len(data)):
    a, b = data[i-1], data[i]
    # Skip cross-session pairs (CVD resets at 00:00 UTC)
    if a.get("session") != b.get("session"):
        continue
    p_dir = direction(a["price"], b["price"], PRICE_MIN)
    c_dir = direction(a["cvd"], b["cvd"], CVD_MIN)
    n_dir = direction(a["net_delta"], b["net_delta"], ND_MIN)
    oi_dir = b["oi_dir"]  # snapshot direction field

    flags = []
    # 1. Price vs CVD
    if p_dir == "up" and c_dir == "down":
        flags.append("PRICE-CVD DIV (bearish)")
    elif p_dir == "down" and c_dir == "up":
        flags.append("PRICE-CVD DIV (bullish)")
    # 2. Price vs OI
    if p_dir == "up" and oi_dir == "falling":
        flags.append("SHORT COVERING")
    elif p_dir == "up" and oi_dir == "rising":
        flags.append("NEW LONGS")
    elif p_dir == "down" and oi_dir == "rising":
        flags.append("NEW SHORTS")
    elif p_dir == "down" and oi_dir == "falling":
        flags.append("LONG CAPIT")
    # 3. Price vs Net Delta
    if p_dir == "up" and n_dir == "down":
        flags.append("BUYERS FADING")
    elif p_dir == "down" and n_dir == "up":
        flags.append("SELLERS FADING")
    # 5. Silent absorption (price flat, CVD up sharply)
    if p_dir == "flat" and c_dir == "up":
        flags.append("SILENT ACCUMULATION")
    elif p_dir == "flat" and c_dir == "down":
        flags.append("SILENT DISTRIBUTION")
    # 4. CVD vs OI
    if c_dir == "up" and oi_dir == "falling":
        flags.append("CVD-OI: covering")
    elif c_dir == "up" and oi_dir == "rising":
        flags.append("CVD-OI: new longs")
    elif c_dir == "down" and oi_dir == "rising":
        flags.append("CVD-OI: new shorts")
    elif c_dir == "down" and oi_dir == "falling":
        flags.append("CVD-OI: closing")

    pair_label = f"{a['time']} -> {b['time']}"
    flag_str = " | ".join(flags) if flags else "—"
    print(f"{pair_label:<22} {p_dir:>7} {c_dir:>7} {n_dir:>9} {oi_dir:>10} | {flag_str}")

print()
print("=" * 92)
print("LEGEND:")
print("  PRICE-CVD DIV bearish = price up but CVD down  → sellers winning, rally suspect")
print("  PRICE-CVD DIV bullish = price down but CVD up  → buyers absorbing, drop suspect")
print("  SHORT COVERING        = price up, OI falling    → weak rally, ends when shorts done")
print("  NEW LONGS             = price up, OI rising     → real buyers, rally can extend")
print("  NEW SHORTS            = price down, OI rising   → real sellers, drop can extend")
print("  LONG CAPIT            = price down, OI falling  → longs giving up")
print("  BUYERS FADING         = price up, net delta down → momentum weakening")
print("  SELLERS FADING        = price down, net delta up → momentum weakening")
print("=" * 92)
