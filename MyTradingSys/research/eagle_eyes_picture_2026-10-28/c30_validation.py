"""C30 VALIDATION read (card c30-validation-read). Frozen rule: PRE_REG_C30.md (H1 30m any-trend, H2 15m with last closed 2h trend up),
buy dot wt1 <= -53 + bullish RSI divergence, exit X1, fee-net. Reuses wt_rsi_div.run unchanged. Window 2024-07-01..2025-06-30;
bars from 2024-04-01 are warm-up only. HOLDOUT (2025-07-01+) is never requested: the fetch stops at END. Research only, no orders.
Usage: python c30_validation.py <repo> [outdir]"""
import json, math, os, random, statistics as st, sys, tempfile, urllib.request
from datetime import datetime, timezone

REPO = sys.argv[1]; OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.dirname(os.path.abspath(__file__))
MS = lambda y, m, d: int(datetime(y, m, d, tzinfo=timezone.utc).timestamp() * 1000)
WARM, START, END, MID = MS(2024, 4, 1), MS(2024, 7, 1), MS(2025, 7, 1), MS(2025, 1, 1)  # END exclusive: HOLDOUT never fetched
CACHE = os.path.join(tempfile.gettempdir(), "btc5m_val_2024-04_2025-06.json")


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


# The study modules read DEV caches at import; point them at stubs, then swap in VALIDATION bars.
_td = tempfile.mkdtemp(); tempfile.tempdir = _td
for n in ("btc15m_bbdiv.json", "btc5m_2022_2024h1.json"):
    json.dump([[0, 1.0, 1.0, 1.0, 1.0]], open(os.path.join(_td, n), "w"))
sys.argv = [sys.argv[0], REPO]; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wavetrend_dots as WD, wt_context as WC, wt_lower_tf as LT, wt_rsi_div as V

R5 = fetch5(); assert R5[-1][0] < END and R5[0][0] >= WARM
B = {}
for x in R5:
    B.setdefault(x[0] // 900000, []).append(x)
R15 = [(g[0][0], g[0][1], max(y[2] for y in g), min(y[3] for y in g), g[-1][4]) for _, g in sorted(B.items()) if len(g) == 3]
WD.R15 = [list(x) for x in R15]; LT.R5 = R5


def trades(tf):
    b = LT.agg5(6) if tf == "30m" else LT.agg5(3)
    name, src = ("buy dot <= -53 + bull div", "any" if tf == "30m" else "2h")
    for n, s, ex, x in V.run(b, 30 if tf == "30m" else 15):
        if n == name and s == src and ex == WC.EXITS[0]:
            return b, [r for r in x if r["t"] >= START]


def stats(x):
    v = [r["net"] for r in x]; n = len(v)
    if n < 2:
        return dict(n=n)
    m, sd = st.mean(v), st.stdev(v); se = sd / n ** 0.5; t = m / se if se else 0.0
    # one-sided p, t-test; df-aware normal approximation (Hill 1970-style correction of t to z)
    df = n - 1; z = t * (1 - 1 / (4 * df)) / math.sqrt(1 + t * t / (2 * df)); p = 0.5 * math.erfc(z / math.sqrt(2))
    h = lambda q: dict(n=len(q), mean=st.mean(q)) if q else dict(n=0)
    return dict(n=n, mean=m, sd=sd, ci_lo=m - 1.96 * se, ci_hi=m + 1.96 * se, win=100 * sum(q > 0 for q in v) / n, worst=min(v), t=t, p_one_sided=p,
                h1=h([r["net"] for r in x if r["t"] < MID]), h2=h([r["net"] for r in x if r["t"] >= MID]))


def preflight(tf, b, x):
    """P1 coverage, P2b prefix (bars <= i only), P6 fee identity, P7 overlap, P8 random entries, on VALIDATION bars."""
    res = []; O = [y[1] for y in b]; T = {y[0]: j for j, y in enumerate(b)}; k = 6 if tf == "30m" else 3
    span = (b[-1][0] - b[0][0]) // (k * 300000) + 1
    res.append(("P1 coverage %s" % tf, len(b) >= 0.995 * span, "%d of %d bars" % (len(b), span)))
    H = [y[2] for y in b]; L = [y[3] for y in b]; Rr = V.rsi([y[4] for y in b]); mins = 30 if tf == "30m" else 15
    tr = LT.htf_trend(b, mins); rnd = random.Random(5); bad = 0; cuts = 15; full15 = WD.R15
    for i in rnd.sample(range(2000, len(b) - 1), cuts):
        WD.R15 = [y for y in full15 if y[0] + 900000 <= b[i][0] + mins * 60000]
        pb = b[:i + 1]; pR = V.rsi([y[4] for y in pb])
        bad += LT.htf_trend(pb, mins)[-1] != tr[i] or abs(pR[-1] - Rr[i]) > 1e-9 or V.divergence([y[2] for y in pb], [y[3] for y in pb], pR, i, 1) != V.divergence(H, L, Rr, i, 1)
    WD.R15 = full15
    res.append(("P2b prefix %s" % tf, bad == 0, "%d of %d cuts differ" % (bad, cuts)))
    worst = 0.0
    for r in x:
        j = T[r["t"]]; e = j + r["bars"]
        if e < len(O):
            worst = max(worst, abs(r["net"] - (r["d"] * (O[e] / O[j] - 1) * 100 - WD.FEE)))
    res.append(("P6 fee identity %s" % tf, worst < 1e-6, "max gap %.2e" % worst))
    ov = sum(1 for a, c in zip(x, x[1:]) if T[c["t"]] < T[a["t"]] + a["bars"])
    res.append(("P7 overlap %s" % tf, ov == 0, "%d overlaps" % ov))
    return res


def p8(tf, b, x, draws=30):
    w1, w2 = WD.wavetrend(b); trd = LT.htf_trend(b, 30 if tf == "30m" else 15); need = 0 if tf == "30m" else 1
    pool = [i for i in range(100, len(b) - 2) if b[i][0] >= START and (need == 0 or trd[i] == need)]
    rnd = random.Random(11); means = []
    for _ in range(draws):
        v = [V.forward_trade([y[1] for y in b], w1, w2, trd, i, 1, 0, need != 0, [y[0] for y in b]) for i in rnd.sample(pool, min(len(x), len(pool)))]
        means.append(st.mean(r["net"] for r in v if r))
    m = st.mean(r["net"] for r in x); return m, st.median(means), sum(m > q for q in means), draws


out = {}; pre = []
for tf, h in (("30m", "H1"), ("15m", "H2")):
    b, x = trades(tf); pre += preflight(tf, b, x)
    out[h] = stats(x); out[h]["trades"] = [(datetime.fromtimestamp(r["t"] / 1000, timezone.utc).strftime("%Y-%m-%d %H:%M"), round(r["net"], 4), r["bars"]) for r in x]
    if len(x) >= 5:
        out[h]["p8"] = p8(tf, b, x)
for name, ok, d in pre:
    print("%-4s %-28s %s" % ("PASS" if ok else "FAIL", name, d))
if any(not ok for _, ok, _ in pre):
    print("PREFLIGHT FAILED: no verdict"); sys.exit(2)
ps = sorted((out[h].get("p_one_sided", 1.0), h) for h in ("H1", "H2"))
holm = {}; prev = 0.0
for rank, (p, h) in enumerate(ps):
    prev = max(prev, min(1.0, p * (2 - rank))); holm[h] = prev
for h in ("H1", "H2"):
    s = out[h]; s["holm_p"] = holm[h]
    s["verdict"] = ("FAIL" if s["n"] < 2 or s["mean"] <= 0 else "PASS" if s["n"] >= 15 and holm[h] < 0.05 else "INCONCLUSIVE")
    print(h, {k: v for k, v in s.items() if k != "trades"})
json.dump(dict(study="eagle_c30_prereg", window="2024-07-01..2025-06-30", split="VALIDATION", holdout_read=False,
               H1=out["H1"], H2=out["H2"]), open(os.path.join(OUT, "c30_validation_verdict.json"), "w"), indent=1)
