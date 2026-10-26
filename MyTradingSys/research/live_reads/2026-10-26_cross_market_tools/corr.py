import json, urllib.request, datetime as dt, math

UA = {"User-Agent": "Mozilla/5.0"}


def get(url):
    return json.load(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=20))


def yf_daily(sym, rng="6mo"):
    r = get(f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}?range={rng}&interval=1d")["chart"]["result"][0]
    q = r["indicators"]["quote"][0]
    out = {}
    for i, t in enumerate(r["timestamp"]):
        if q["close"][i] is None:
            continue
        day = dt.datetime.fromtimestamp(t, dt.UTC).date()
        out[day] = (q["open"][i], q["high"][i], q["low"][i], q["close"][i])
    return out


k = get("https://data-api.binance.vision/api/v3/klines?symbol=BTCUSDT&interval=1d&limit=200")
btc = {dt.datetime.fromtimestamp(x[0] / 1000, dt.UTC).date(): tuple(float(x[i]) for i in (1, 2, 3, 4)) for x in k}


def ret(d, a, b):
    return d[b][3] / d[a][3] - 1


def corr(x, y):
    n = len(x)
    mx, my = sum(x) / n, sum(y) / n
    sx = math.sqrt(sum((a - mx) ** 2 for a in x))
    sy = math.sqrt(sum((b - my) ** 2 for b in y))
    return sum((a - mx) * (b - my) for a, b in zip(x, y)) / (sx * sy) if sx and sy else float("nan")


idx = {s: yf_daily(s) for s in ["^GSPC", "^IXIC", "^VIX"]}
for s, d in idx.items():
    days = sorted(d)
    # index close-to-close return keyed by trading day
    rets = {days[i]: d[days[i]][3] / d[days[i - 1]][3] - 1 for i in range(1, len(days))}
    # BTC UTC-day return keyed by day
    bd = sorted(btc)
    brets = {bd[i]: btc[bd[i]][3] / btc[bd[i - 1]][3] - 1 for i in range(1, len(bd))}
    common = sorted(set(rets) & set(brets))
    for label, sel in [("last 5 sessions", common[-5:]), ("last 20", common[-20:]), ("last 60", common[-60:]), ("all ~%d" % len(common), common)]:
        x = [brets[c] for c in sel]
        y = [rets[c] for c in sel]
        sign = sum(1 for a, b in zip(x, y) if (a > 0) == (b > 0)) / len(sel)
        print(f"{s} same-day corr BTC vs idx {label}: r={corr(x, y):+.2f}  sign-agree={sign:.0%}  n={len(sel)}")
    # BTC prior-day return (UTC day t-1, which includes weekend) vs idx next session
    nxt = []
    for c in common:
        prev = c - dt.timedelta(days=1)
        if prev in brets:
            nxt.append((brets[prev], rets[c]))
    for label, n in [("last 20", 20), ("last 60", 60), ("all", len(nxt))]:
        sel = nxt[-n:]
        x = [a for a, _ in sel]
        y = [b for _, b in sel]
        print(f"{s} BTC(t-1 UTC day) -> idx(t) {label}: r={corr(x, y):+.2f}  n={len(sel)}")
    print()

# Last week side-by-side
print("Day-by-day last week (BTC UTC day vs index session):")
print("day        BTC body%  BTC closepos | SPX body% closepos | NDX body% closepos | VIX chg%")
for day in [dt.date(2026, 10, 19) + dt.timedelta(days=i) for i in range(5)]:
    b = btc[day]
    bb = (b[3] - b[0]) / b[0] * 100
    bp = (b[3] - b[2]) / (b[1] - b[2])
    s = idx["^GSPC"].get(day)
    n = idx["^IXIC"].get(day)
    v = idx["^VIX"].get(day)
    pv = idx["^VIX"].get(day - dt.timedelta(days=1 if day.weekday() else 3))
    f = lambda c: ((c[3] - c[0]) / c[0] * 100, (c[3] - c[2]) / (c[1] - c[2]))
    sb, sp = f(s)
    nb, np_ = f(n)
    print(f"{day} {bb:+6.2f}   {bp:5.2f}      | {sb:+6.2f}  {sp:5.2f}     | {nb:+6.2f}  {np_:5.2f}     | {(v[3]/pv[3]-1)*100 if pv else float('nan'):+6.1f}")

# weekly candles
def week(d, start, end):
    days = [x for x in sorted(d) if start <= x <= end]
    o = d[days[0]][0]; c = d[days[-1]][3]
    h = max(d[x][1] for x in days); l = min(d[x][2] for x in days)
    return o, h, l, c

for name, d, a, b in [("BTC wk (Mon-Sun UTC)", btc, dt.date(2026, 10, 19), dt.date(2026, 10, 25)), ("SPX wk", idx["^GSPC"], dt.date(2026, 10, 19), dt.date(2026, 10, 23)), ("NDX wk", idx["^IXIC"], dt.date(2026, 10, 19), dt.date(2026, 10, 23)), ("BTC prior wk", btc, dt.date(2026, 10, 12), dt.date(2026, 10, 18)), ("SPX prior wk", idx["^GSPC"], dt.date(2026, 10, 12), dt.date(2026, 10, 16)), ("NDX prior wk", idx["^IXIC"], dt.date(2026, 10, 12), dt.date(2026, 10, 16))]:
    o, h, l, c = week(d, a, b)
    print(f"{name}: O{o:.1f} H{h:.1f} L{l:.1f} C{c:.1f} body{(c-o)/o*100:+.2f}% range{(h-l)/o*100:.2f}% closepos{(c-l)/(h-l):.2f}")
