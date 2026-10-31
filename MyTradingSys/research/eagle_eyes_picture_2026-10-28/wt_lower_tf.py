"""C29: C28 on lower charts (operator 10-31: "WaveTrend almost never gets there in a downtrend ... then look for other time frames
- 30 mins - 15 mins - 10 mins"). Same rules as wt_context.py; two trend sources:
  same = trend structure on the trading chart itself; 2h = trend structure of the last CLOSED 2h bar (higher-timeframe context)
WT 10/21/4, bands +-53: SOURCED (LazyBear). Rest OURS (see wt_context.py). Binance spot 5m from 2022 (public, cached in temp),
built into 10m/15m/30m. Window 2022-01..2024-06 only (2024-07+ sealed by wavetrend_2026-10-17/PRE_REG.md). Research only, no orders.
Usage: python wt_lower_tf.py <repo>"""
import json, os, sys, tempfile, urllib.request, statistics as st
from datetime import datetime, timezone
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wavetrend_dots as WD
import wt_context as WC

CACHE = os.path.join(tempfile.gettempdir(), "btc5m_2022_2024h1.json")  # public klines, never committed
END = WD.END


def fetch5():
    if os.path.exists(CACHE):
        return json.load(open(CACHE))
    s = int(datetime(2022, 1, 1, tzinfo=timezone.utc).timestamp() * 1000); out = []
    while s < END:
        u = "https://data-api.binance.vision/api/v3/klines?symbol=BTCUSDT&interval=5m&limit=1000&startTime=%d" % s
        with urllib.request.urlopen(u, timeout=20) as r:
            b = json.loads(r.read())
        if not b:
            break
        out += [[x[0], float(x[1]), float(x[2]), float(x[3]), float(x[4])] for x in b if x[0] < END]
        s = b[-1][0] + 1
    json.dump(out, open(CACHE, "w"))
    return out


R5 = fetch5()


def agg5(k):
    B = {}
    for x in R5:
        B.setdefault(x[0] // (k * 300000), []).append(x)
    return [(g[0][0], g[0][1], max(y[2] for y in g), min(y[3] for y in g), g[-1][4]) for _, g in sorted(B.items()) if len(g) == k]


def htf_trend(b, mins):
    """Trend of the last 2h bar that has CLOSED by the close of each lower bar."""
    h = WD.agg(8); htr = WC.structure(h); out = []; j = -1
    for x in b:
        close_t = x[0] + mins * 60000
        while j + 1 < len(h) and h[j + 1][0] + 7200000 <= close_t:
            j += 1
        out.append(htr[j] if j >= 0 else 0)
    return out


_MEMO = {}


def trades(k, mins, rule, ex, src):
    if (k, src) not in _MEMO:
        b = agg5(k); w1, w2 = WD.wavetrend(b)
        _MEMO[(k, src)] = (b, w1, w2, WC.structure(b) if src == "same" else htf_trend(b, mins), [x[1] for x in b])
    b, w1, w2, tr, O = _MEMO[(k, src)]
    name, need, side, cond = rule
    out, busy = [], -1
    for i in range(100, len(b) - 2):
        if i > busy and tr[i] == need and cond(w1, w2, i):
            r = WC.forward_trade(b, w1, w2, tr, i, side, ex, guard=need == side, O=O)
            if r:
                out.append(r); busy = i + r["bars"]
    return out


if __name__ == "__main__":
    span = (R5[-1][0] - R5[0][0]) // 300000 + 1
    print("P1 5m bars %d of %d" % (len(R5), span))
    for tf, k, mins in (("10m", 2, 10), ("15m", 3, 15), ("30m", 6, 30)):
        print("P1 %s bars %d of %d" % (tf, len(agg5(k)), span // k))
        for src in ("same", "2h"):
            for rule in WC.RULES:
                for ex in range(4):
                    x = trades(k, mins, rule, ex, src)
                    if not x:
                        print("%s|%s|%s|%s|0" % (tf, src, rule[0], WC.EXITS[ex])); continue
                    v = [r["net"] for r in x]; a = [r["net"] for r in x if r["t"] < WC.HALF]; c = [r["net"] for r in x if r["t"] >= WC.HALF]
                    t = st.mean(v) / (st.stdev(v) / len(v) ** 0.5) if len(v) > 1 and st.stdev(v) else 0
                    print("%s|%s|%s|%s|%d|%.0f|%+.3f|%+.2f|%s|%s|%.0f" % (tf, src, rule[0], WC.EXITS[ex], len(v), 100 * sum(q > 0 for q in v) / len(v), st.mean(v), t,
                          "%+.3f(%d)" % (st.mean(a), len(a)) if a else "-", "%+.3f(%d)" % (st.mean(c), len(c)) if c else "-", st.median(r["bars"] for r in x)))
