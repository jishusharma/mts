import json, urllib.request, datetime as dt, math

UA = {"User-Agent": "Mozilla/5.0"}
get = lambda u: json.load(urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=20))


def yf(sym, itv="5m"):
    r = get(f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}?range=2d&interval={itv}&includePrePost=true")["chart"]["result"][0]
    c = r["indicators"]["quote"][0]["close"]
    return {t: v for t, v in zip(r["timestamp"], c) if v is not None}, r["meta"]


def corr(x, y):
    n = len(x)
    if n < 5:
        return float("nan")
    mx, my = sum(x) / n, sum(y) / n
    sx = math.sqrt(sum((a - mx) ** 2 for a in x)); sy = math.sqrt(sum((b - my) ** 2 for b in y))
    return sum((a - mx) * (b - my) for a, b in zip(x, y)) / (sx * sy) if sx and sy else float("nan")


k = get("https://data-api.binance.vision/api/v3/klines?symbol=BTCUSDT&interval=5m&limit=300")
btc = {x[0] // 1000: float(x[4]) for x in k}
now = dt.datetime.now(dt.UTC)
today = now.replace(hour=0, minute=0, second=0, microsecond=0)
openT = int(today.replace(hour=13, minute=30).timestamp())
print("now", now.strftime("%H:%MZ"), "(US open 13:30Z)")
series = {"BTC": btc}
for s in ["ES=F", "NQ=F", "^VIX"]:
    series[s], meta = yf(s)
    series[s + "_meta"] = meta


def at(d, t):
    ks = [x for x in d if x <= t]
    return d[max(ks)] if ks else None


def last(d):
    return d[max(d)]


print("\nSINCE OPEN (13:30Z):")
for s in ["BTC", "ES=F", "NQ=F", "^VIX"]:
    d = series[s]
    o = at(d, openT)
    print(f"  {s:5s} open {o:.2f} now {last(d):.2f}  {(last(d)/o-1)*100:+.2f}%")
print("\nSINCE 12:00Z (premarket+open):")
t12 = int(today.replace(hour=12).timestamp())
for s in ["BTC", "ES=F", "NQ=F"]:
    d = series[s]
    print(f"  {s:5s} {(last(d)/at(d, t12)-1)*100:+.2f}%")

print("\n5m closes, last 8 bars (Z time):")
ts = sorted(t for t in series["ES=F"])[-8:]
print("  time   BTC      ES       NQ")
for t in ts:
    print(f"  {dt.datetime.fromtimestamp(t, dt.UTC):%H:%M} {at(btc, t):8.0f} {at(series['ES=F'], t):8.2f} {at(series['NQ=F'], t):9.2f}")

common = sorted(set(btc) & set(series["ES=F"]) & set(series["NQ=F"]))
def rets(d):
    return {common[i]: d[common[i]] / d[common[i - 1]] - 1 for i in range(1, len(common)) if common[i] - common[i - 1] == 300}
rb, re_, rn = rets(btc), rets(series["ES=F"]), rets(series["NQ=F"])
ks = sorted(set(rb) & set(re_) & set(rn))
print("\nROLLING 5m-return correlation (BTC vs ES / NQ):")
for label, n in [("last 1h (12 bars)", 12), ("last 3h (36)", 36), ("last 8h (96)", 96), ("all 2d", len(ks))]:
    sel = ks[-n:]
    print(f"  {label:18s} ES r={corr([rb[x] for x in sel],[re_[x] for x in sel]):+.2f}  NQ r={corr([rb[x] for x in sel],[rn[x] for x in sel]):+.2f}  n={len(sel)}")
# since open only
sel = [x for x in ks if x >= openT]
print(f"  since open ({len(sel)} bars) ES r={corr([rb[x] for x in sel],[re_[x] for x in sel]):+.2f} NQ r={corr([rb[x] for x in sel],[rn[x] for x in sel]):+.2f}")
