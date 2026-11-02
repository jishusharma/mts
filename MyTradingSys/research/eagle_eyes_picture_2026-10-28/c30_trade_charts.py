"""Per-trade chart data for the C30 H1 VALIDATION trades (sim page, operator item 2: "when you get into the trade and when you get out").
Rebuilds the frozen H1 trades exactly as c30_validation.py does (same bars, same wt_rsi_div.run), checks each net % against
c30_validation_verdict.json, then writes, per trade, the 30m candles around it as % distance from the entry price (no prices),
with WaveTrend (wt1, wt2), RSI 14, the signal bar, entry bar, exit bar and the two divergence lows. Window 2024-07-01..2025-06-30,
already read once for the verdict; HOLDOUT never fetched. Research only, no orders.
Usage: python c30_trade_charts.py <repo> [out.json]"""
import json, os, sys, tempfile, urllib.request
from datetime import datetime, timezone

REPO = sys.argv[1]
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "c30_trade_charts.json")
MS = lambda y, m, d: int(datetime(y, m, d, tzinfo=timezone.utc).timestamp() * 1000)
WARM, START, END = MS(2024, 4, 1), MS(2024, 7, 1), MS(2025, 7, 1)  # END exclusive: HOLDOUT never fetched
CACHE = os.path.join(tempfile.gettempdir(), "btc5m_val_2024-04_2025-06.json")
BEFORE, AFTER = 45, 6  # 30m bars shown before the signal and after the exit fill


def fetch5():
    if os.path.exists(CACHE):
        return json.load(open(CACHE))
    s, out = WARM, []
    while s < END:
        u = "https://data-api.binance.vision/api/v3/klines?symbol=BTCUSDT&interval=5m&limit=1000&startTime=%d&endTime=%d" % (s, END - 1)
        with urllib.request.urlopen(u, timeout=30) as r:
            b = json.loads(r.read())
        if not b:
            break
        out += [[x[0], float(x[1]), float(x[2]), float(x[3]), float(x[4])] for x in b if x[0] < END]
        s = b[-1][0] + 1
    json.dump(out, open(CACHE, "w"))
    return out


# Same stub trick as c30_validation.py: the study modules read DEV caches at import.
_td = tempfile.mkdtemp(); tempfile.tempdir = _td
for n in ("btc15m_bbdiv.json", "btc5m_2022_2024h1.json"):
    json.dump([[0, 1.0, 1.0, 1.0, 1.0]], open(os.path.join(_td, n), "w"))
sys.argv = [sys.argv[0], REPO]; sys.path.insert(0, HERE)
import wavetrend_dots as WD, wt_context as WC, wt_lower_tf as LT, wt_rsi_div as V

R5 = fetch5(); assert R5[-1][0] < END and R5[0][0] >= WARM
B = {}
for x in R5:
    B.setdefault(x[0] // 900000, []).append(x)
WD.R15 = [[g[0][0], g[0][1], max(y[2] for y in g), min(y[3] for y in g), g[-1][4]] for _, g in sorted(B.items()) if len(g) == 3]
LT.R5 = R5

b = LT.agg5(6)
x = next(t for n, s, ex, t in V.run(b, 30) if n == "buy dot <= -53 + bull div" and s == "any" and ex == WC.EXITS[0])
x = [r for r in x if r["t"] >= START]
ref = json.load(open(os.path.join(HERE, "c30_validation_verdict.json")))["H1"]["trades"]
assert len(ref) == len(x), (len(ref), len(x))
O = [y[1] for y in b]; H = [y[2] for y in b]; L = [y[3] for y in b]; C = [y[4] for y in b]; T = {y[0]: j for j, y in enumerate(b)}
w1, w2 = WD.wavetrend(b); R = V.rsi(C)
rd = lambda v, k=3: None if v is None else round(v, k)
trades = []
for r, (rt, rnet, rbars) in zip(x, ref):
    j = T[r["t"]]; i = j - 1; e = j + r["bars"]; k = e - 1  # signal bar i, entry at open of j, exit decided on bar k, filled at open of e
    assert abs(r["net"] - rnet) < 1e-3 and r["bars"] == rbars, (rt, r["net"], rnet)
    p = min(range(i - 40, i - 7), key=lambda m: L[m]); q = min(range(i - 7, i + 1), key=lambda m: L[m])
    a, z = i - BEFORE, min(len(b) - 1, e + AFTER); E = O[j]; pc = lambda v: round((v / E - 1) * 100, 3)
    trades.append(dict(
        d=datetime.fromtimestamp(r["t"] / 1000, timezone.utc).strftime("%Y-%m-%d %H:%M"), t0=b[a][0], net=round(r["net"], 3), bars=r["bars"],
        why="WaveTrend back above 0" if w1[k] > 0 else "60-candle time cap",
        sig=i - a, ent=j - a, ext=e - a, div=[p - a, q - a],
        c=[[pc(O[m]), pc(H[m]), pc(L[m]), pc(C[m])] for m in range(a, z + 1)],
        w1=[rd(w1[m], 1) for m in range(a, z + 1)], w2=[rd(w2[m], 1) for m in range(a, z + 1)], rsi=[rd(R[m], 1) for m in range(a, z + 1)]))
json.dump(dict(study="eagle_c30_prereg H1", tf="30m", window="2024-07-01..2025-06-30", split="VALIDATION", unit="% from entry price",
               trades=trades), open(OUT, "w", encoding="utf-8", newline="\n"), separators=(",", ":"))
print("ok", len(trades), "trades; all net % match the verdict file")
