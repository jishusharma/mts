"""C23: BTC DAILY shorts from the operator's 10-31 chart read. Research only, no orders.
  A  bearish RSI divergence at a price high (repo rsi_divergence, Malkan close-to-close rules, SOURCED);
     chain = how many lower RSI highs in a row (his Aug 21 -> Sep 21 -> Oct 4 picture = chain 2).
  B  BB mid rejection in a falling band: high >= mid, close < mid, mid below its value 5 days ago (OURS).
     B60  + RSI stayed under 60 for the last 10 days ("bullish range not accepted", OURS 60 = Malkan 40/60 line)
     BLB  + the lower band was touched in the last 10 days (his last circle: bounce from lower band, rejected at mid)
     BRS  + RSI closed back under its SMA14 after touching it in the last 3 days (rejected at the RSI average)
Short at the next day open. Outcome: fixed 5/10/20-day hold, and a band exit (lower-band touch = target,
close above the signal-day high = stop, 20 days max). Base rate = a short opened every day.
Fee: backtest/fees.py taker round trip; funding not modelled (it mostly pays shorts in up-trends, costs them in down-trends)."""
import json, os, sys, tempfile, time, urllib.request, statistics as st
from datetime import datetime, timezone

REPO = sys.argv[1] if len(sys.argv) > 1 else os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, REPO)
from MyTradingSys.backtest.layers.rsi.rsi_core import rsi_core
from MyTradingSys.backtest.layers.rsi.rsi_divergence import rsi_divergence
from MyTradingSys.backtest.fees import BINANCE_TAKER

FEE = BINANCE_TAKER * 2  # round trip from backtest/fees.py
CACHE = os.path.join(tempfile.gettempdir(), "btc1d_c23.json")  # public klines, never committed
SPLIT = "2023-01-01"  # IS = 2017-08..2022-12, OOS = 2023-01..now (OURS)


def fetch():
    if os.path.exists(CACHE) and time.time() - os.path.getmtime(CACHE) < 3600:
        return json.load(open(CACHE))
    start = int(datetime(2017, 8, 1, tzinfo=timezone.utc).timestamp() * 1000); out = []
    while True:
        u = "https://data-api.binance.vision/api/v3/klines?symbol=BTCUSDT&interval=1d&limit=1000&startTime=%d" % start
        with urllib.request.urlopen(u, timeout=20) as r:
            b = json.loads(r.read())
        if not b:
            break
        out += [[x[0], float(x[1]), float(x[2]), float(x[3]), float(x[4])] for x in b]
        if len(b) < 1000:
            break
        start = b[-1][0] + 1
    json.dump(out, open(CACHE, "w"))
    return out


ROWS = fetch()[:-1]  # drop the forming day
TS = [datetime.fromtimestamp(x[0] / 1000, timezone.utc).strftime("%Y-%m-%d") for x in ROWS]
O = [x[1] for x in ROWS]; H = [x[2] for x in ROWS]; L = [x[3] for x in ROWS]; C = [x[4] for x in ROWS]
N = len(C); R = rsi_core(C, 14)
RM = [None] * N; MID = [None] * N; LO = [None] * N; UP = [None] * N
for i in range(N):
    if i >= 27 and all(v is not None for v in R[i - 13:i + 1]):
        RM[i] = sum(R[i - 13:i + 1]) / 14
    if i >= 19:
        w = C[i - 19:i + 1]; m = sum(w) / 20; sd = st.pstdev(w); MID[i], LO[i], UP[i] = m, m - 2 * sd, m + 2 * sd


def forward_outcome(i):
    """Short from O[i+1]: fixed-hold nets and the band-exit net. Outcome only, never used to pick a signal."""
    e = i + 1; px = O[e]; out = {}
    for hd in (5, 10, 20):
        k = e + hd - 1
        out[hd] = (px - C[k]) / px - FEE if k < N else None
    stop = H[i]; band = None
    for k in range(e, min(N, e + 20)):
        if L[k] <= LO[k]:
            band = (px - min(LO[k], O[k])) / px - FEE; break
        if C[k] > stop:
            band = (px - C[k]) / px - FEE; break
    if band is None and e + 19 < N:
        band = (px - C[e + 19]) / px - FEE
    out["band"] = band
    return out


def signals():
    sig = {"base": list(range(30, N - 1))}
    div = rsi_divergence(C, R, TS, 3, 40, kind="bearish")
    sig["A_div"] = [d["i"] for d in div if d["i"] < N - 1]
    sig["A_chain2+"] = [d["i"] for d in div if d["chain"] >= 2 and d["i"] < N - 1]
    sig["A_div_rsi60+"] = [d["i"] for d in div if d["rsi_a"] >= 60 and d["i"] < N - 1]
    # A_major (OURS): his non-adjacent read. Major high p = close above the 5 closes on each side, known at i = p + 5;
    # divergence when the close is >= 98% of the previous major high within 60 days and RSI is >= 3 points lower.
    major = []; amaj = []
    for i in range(40, N - 1):
        p = i - 5
        if C[p] > max(C[p - 5:p]) and C[p] > max(C[i - 4:i + 1]):
            prev = [q for q in major if p - q <= 60]
            if prev and C[p] >= 0.98 * C[prev[-1]] and R[p] <= R[prev[-1]] - 3:
                amaj.append(i)
            major.append(p)
    sig["A_major"] = amaj
    b, b60, blb, brs = [], [], [], []
    for i in range(30, N - 1):
        if not (H[i] >= MID[i] > C[i] and MID[i] < MID[i - 5]):
            continue
        b.append(i)
        if max(R[i - 9:i + 1]) < 60:
            b60.append(i)
        if any(L[k] <= LO[k] for k in range(i - 9, i + 1)):
            blb.append(i)
        if R[i] < RM[i] and any(R[k] >= RM[k] for k in range(i - 3, i)):
            brs.append(i)
    sig.update({"B_mid": b, "B60": b60, "BLB": blb, "BRS": brs,
                "B60+BLB": sorted(set(b60) & set(blb)), "B60+BRS": sorted(set(b60) & set(brs))})
    return sig, div


def first_per_cluster(idx, gap=5):  # one trade per cluster of signals (OURS): drop a signal within 5 days of the last kept
    kept = []
    for i in idx:
        if not kept or i - kept[-1] > gap:
            kept.append(i)
    return kept


def summ(vals):
    v = [x for x in vals if x is not None]
    if len(v) < 3:
        return "n=%3d" % len(v)
    return "n=%3d mean %+6.2f%% med %+6.2f%% win %3.0f%%" % (len(v), 100 * st.mean(v), 100 * st.median(v), 100 * sum(x > 0 for x in v) / len(v))


SIG, DIV = signals()
print("BTCUSDT 1d %s .. %s, %d days, fee RT %.2f%%" % (TS[0], TS[-1], N, 100 * FEE))
for name, idx in SIG.items():
    idx = idx if name == "base" else first_per_cluster(idx)
    res = {i: forward_outcome(i) for i in idx}
    for per, f in (("IS ", lambda i: TS[i] < SPLIT), ("OOS", lambda i: TS[i] >= SPLIT)):
        sel = [i for i in idx if f(i)]
        print("%-10s %s | 10d %s | 20d %s | band %s" % (name, per, summ([res[i][10] for i in sel]), summ([res[i][20] for i in sel]),
                                                     summ([res[i]["band"] for i in sel])))
print("\n-- 2026 signals --")
for name in ("A_div", "A_major", "B_mid", "B60", "BLB", "BRS"):
    for i in first_per_cluster(SIG[name]):
        if TS[i] >= "2026-07-01":
            r = forward_outcome(i)
            print("%-6s %s close %.0f rsi %.1f | 5d %s 10d %s band %s" % (name, TS[i], C[i], R[i],
                  *["%+.1f%%" % (100 * r[k]) if r[k] is not None else "open" for k in (5, 10, "band")]))
for d in DIV:
    if d["b_t"] >= "2026-07-01":
        print("div A %s c%.0f rsi %.1f -> B %s c%.0f rsi %.1f chain %d" % (d["a_t"], d["close_a"], d["rsi_a"], d["b_t"], d["close_b"], d["rsi_b"], d["chain"]))
