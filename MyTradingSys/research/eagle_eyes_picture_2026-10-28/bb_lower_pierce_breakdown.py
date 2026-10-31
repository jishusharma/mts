"""C21: lower-BB pierce in a downtrend, split by macro breakdown context; where does the ride end. Research only, no orders.
Pierce (OURS): first close below BB(20,2) lower band with the mid falling (mid < mid 4 bars ago) and no close below it in the prior 10 bars.
Breakdown context (OURS): the pierce close is below the lowest low of the prior 14 days (a new 2-week low); else 'other'.
Short entry at the next bar open. Exits (OURS): MID = first close above the BB mid; RSI = RSI14 went under 30, then first close
with RSI back above its SMA14. MFE/MAE measured until the MID exit, in % and in ATR14."""
import json, os, sys, tempfile, time, urllib.request, statistics as st
from datetime import datetime, timezone

REPO = sys.argv[1]
sys.path.insert(0, REPO)
from MyTradingSys.backtest.layers.rsi.rsi_core import rsi_core
from MyTradingSys.backtest.fees import BINANCE_TAKER

FEE = BINANCE_TAKER * 2  # round trip from backtest/fees.py; slippage and funding not modelled
CACHE = os.path.join(tempfile.gettempdir(), "btc15m_bbdiv.json")  # public klines, never committed


def fetch():
    if os.path.exists(CACHE) and time.time() - os.path.getmtime(CACHE) < 900:
        return json.load(open(CACHE))
    start = int(datetime(2022, 1, 1, tzinfo=timezone.utc).timestamp() * 1000); out = []
    while True:
        u = "https://data-api.binance.vision/api/v3/klines?symbol=BTCUSDT&interval=15m&limit=1000&startTime=%d" % start
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


def agg(rows, k):
    """k x 15m -> one bar, grouped by time bucket; incomplete buckets dropped."""
    span = k * 900000; groups = {}
    for x in rows:
        groups.setdefault(x[0] // span, []).append(x)
    return [[w[0][0], w[0][1], max(x[2] for x in w), min(x[3] for x in w), w[-1][4]]
            for _, w in sorted(groups.items()) if len(w) == k]


def study(rows, bars_per_day, label, now_mode=False):
    T = [x[0] for x in rows]; O = [x[1] for x in rows]; H = [x[2] for x in rows]; L = [x[3] for x in rows]; C = [x[4] for x in rows]
    N = len(C); R = rsi_core(C, 14)
    RM = [None] * N; MID = [None] * N; LO = [None] * N; ATR = [None] * N
    for i in range(N):
        if i >= 27 and all(v is not None for v in R[i - 13:i + 1]):
            RM[i] = sum(R[i - 13:i + 1]) / 14
        if i >= 19:
            w = C[i - 19:i + 1]; m = sum(w) / 20; sd = st.pstdev(w); MID[i], LO[i] = m, m - 2 * sd
        if i >= 15:
            ATR[i] = sum(max(H[k] - L[k], abs(H[k] - C[k - 1]), abs(L[k] - C[k - 1])) for k in range(i - 13, i + 1)) / 14

    def forward_outcome(i):
        """Short from the next open, walked to the first close above the mid. Outcome only, never a signal input."""
        px = O[i + 1]; mfe = 0.0; mae = 0.0; x_mid = x_rsi = None; low_k = i + 1; under30 = False
        for k in range(i + 1, N):
            mfe = max(mfe, (px - L[k]) / px)
            if mfe == (px - L[k]) / px:
                low_k = k
            mae = max(mae, (H[k] - px) / px)
            if R[k] is not None and R[k] < 30:
                under30 = True
            if x_rsi is None and under30 and RM[k] is not None and R[k] > RM[k]:
                x_rsi = (k, C[k])
            if C[k] > MID[k]:
                x_mid = (k, C[k]); break
        return px, mfe, mae, x_mid, x_rsi, low_k

    lb = 14 * bars_per_day
    ev = []
    for i in range(max(lb, 30), N - 1):
        if not (C[i] < LO[i] and MID[i] < MID[i - 4]):
            continue
        if any(C[k] < LO[k] for k in range(i - 10, i)):
            continue
        ctx = "breakdown" if C[i] < min(L[i - lb:i - (i % bars_per_day) if bars_per_day > 1 else i]) else "other"
        px, mfe, mae, x_mid, x_rsi, low_k = forward_outcome(i)
        if x_mid is None:
            if now_mode:
                ev.append(dict(t=T[i], ctx=ctx, open=True, px=px, atr=ATR[i], i=i))
            continue
        r_mid = (px - x_mid[1]) / px - FEE
        r_rsi = (px - x_rsi[1]) / px - FEE if x_rsi and x_rsi[0] <= x_mid[0] else r_mid
        ev.append(dict(t=T[i], ctx=ctx, mid=r_mid, rsi=r_rsi, mfe=mfe, mae=mae, mfe_atr=mfe * px / ATR[i], bars_mid=x_mid[0] - i,
                       bars_low=low_k - i, open=False))
    print("== %s (%d bars)" % (label, N))
    split = int(datetime(2024, 7, 1, tzinfo=timezone.utc).timestamp() * 1000)
    for ctx in ("breakdown", "other"):
        for per, f in (("2022-01..2024-06", lambda e: e["t"] < split), ("2024-07..now", lambda e: e["t"] >= split)):
            x = [e for e in ev if e["ctx"] == ctx and not e["open"] and f(e)]
            if len(x) < 5:
                print("  %-9s %s n=%d" % (ctx, per, len(x))); continue
            q = lambda v: (sorted(v)[len(v) // 4], st.median(v), sorted(v)[3 * len(v) // 4])
            m = [e["mfe"] * 100 for e in x]; a = [e["mfe_atr"] for e in x]
            print("  %-9s %s n=%4d | exit MID net %+.3f%% win %2.0f%% | exit RSI net %+.3f%% win %2.0f%% | MFE %% q25/med/q75 %.2f/%.2f/%.2f = ATR %.1f/%.1f/%.1f"
                  " | low at bar med %d, mid exit med %d" % (
                      ctx, per, len(x), st.mean(e["mid"] for e in x) * 100, 100 * sum(e["mid"] > 0 for e in x) / len(x),
                      st.mean(e["rsi"] for e in x) * 100, 100 * sum(e["rsi"] > 0 for e in x) / len(x), *q(m), *q(a),
                      st.median(e["bars_low"] for e in x), st.median(e["bars_mid"] for e in x)))
    for e in ev:
        if e["open"] or e["t"] >= T[-1] - 3 * 86400000:
            print("  recent: %s ctx=%s %s" % (datetime.fromtimestamp(e["t"] / 1000, timezone.utc).strftime("%m-%d %H:%M"), e["ctx"],
                  "OPEN entry %.0f atr %.0f" % (e["px"], e["atr"]) if e["open"] else "closed MID net %+.2f%% MFE %.2f%%" % (e["mid"] * 100, e["mfe"] * 100)))


rows = fetch()[:-1]
study(rows, 96, "15m", True)
study(agg(rows, 2), 48, "30m", True)
study(agg(rows, 16), 6, "4h", True)
