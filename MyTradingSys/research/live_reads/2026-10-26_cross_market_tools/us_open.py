import json, urllib.request, datetime as dt

UA = {"User-Agent": "Mozilla/5.0"}


def get(url):
    return json.load(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=20))


def yf(sym, rng="1mo", itv="1d"):
    j = get(f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}?range={rng}&interval={itv}&includePrePost=true")
    r = j["chart"]["result"][0]
    q = r["indicators"]["quote"][0]
    rows = []
    for i, t in enumerate(r["timestamp"]):
        if q["close"][i] is None:
            continue
        rows.append((t, q["open"][i], q["high"][i], q["low"][i], q["close"][i], q["volume"][i]))
    return r["meta"], rows


def d(t):
    return dt.datetime.fromtimestamp(t, dt.UTC).strftime("%a %m-%d %H:%MZ")


print("== BTC 1d (Binance spot, UTC day) ==")
k = get("https://data-api.binance.vision/api/v3/klines?symbol=BTCUSDT&interval=1d&limit=14")
btc = []
for x in k:
    o, h, l, c, v, tb = (float(x[1]), float(x[2]), float(x[3]), float(x[4]), float(x[5]), float(x[9]))
    btc.append((x[0] // 1000, o, h, l, c, v, tb))
    rng = h - l
    body = (c - o) / o * 100
    cl = (c - l) / rng if rng else 0
    print(d(x[0] // 1000)[:9], f"O{o:.0f} H{h:.0f} L{l:.0f} C{c:.0f} body{body:+.2f}% range{rng/o*100:.2f}% closepos{cl:.2f} taker_buy{tb/v:.2f}", "(forming)" if x is k[-1] else "")

for sym in ["^GSPC", "^IXIC", "^DJI", "^RUT", "^VIX", "ES=F", "NQ=F", "DX-Y.NYB", "^TNX", "GC=F", "CL=F"]:
    try:
        meta, rows = yf(sym, "1mo", "1d")
    except Exception as e:
        print(sym, "ERR", e)
        continue
    print(f"\n== {sym} 1d  last quote {meta.get('regularMarketPrice')} @ {d(meta.get('regularMarketTime'))} prevclose {meta.get('chartPreviousClose')} ==")
    for t, o, h, l, c, v in rows[-8:]:
        rng = h - l
        print(d(t)[:9], f"O{o:.2f} H{h:.2f} L{l:.2f} C{c:.2f} body{(c-o)/o*100:+.2f}% range{rng/o*100:.2f}% closepos{(c-l)/rng if rng else 0:.2f}")

print("\n== Futures last 6h, 15m (ES, NQ) ==")
for sym in ["ES=F", "NQ=F"]:
    meta, rows = yf(sym, "1d", "15m")
    for t, o, h, l, c, v in rows[-14:]:
        print(sym, d(t), f"C{c:.2f}")
