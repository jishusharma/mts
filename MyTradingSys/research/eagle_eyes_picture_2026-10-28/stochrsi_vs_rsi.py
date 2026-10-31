"""C25: does Stoch RSI (14,14,3,3) add anything over plain RSI14 on BTC? Research only, no orders.
Signals (OURS rules, the classic textbook reads; SOURCED defaults 14/14/3/3 = TradingView, FORMULAS.md s23):
  SR_X   long: K crosses above D with both under 20 (short mirror: crosses below, both over 80)
  SR_X_T same, only with the trend (close above SMA200 for longs, below for shorts) - Krown KR-S01: trend first
  RSI30  long: RSI14 closes back above 30 (short mirror: back under 70)
  RSI_T  same, with the trend
Entry next bar open, hold H bars, fee-net (fees.py taker x2). Edge = signal mean minus the base (every bar, same side, same hold).
In-sample 2022-01..2024-06, out-of-sample 2024-07..now. One signal per 2*H bars (no overlap)."""
import json, os, sys, tempfile, time, urllib.request, statistics as st
from datetime import datetime, timezone

REPO = sys.argv[1]
sys.path.insert(0, REPO)
sys.path.insert(0, os.path.join(REPO, "scripts", "dev"))
from MyTradingSys.backtest.layers.rsi.rsi_core import rsi_core
from MyTradingSys.backtest.fees import BINANCE_TAKER
from chart_verify import stochrsi

FEE = BINANCE_TAKER * 2  # round trip from backtest/fees.py; slippage and funding not modelled
CACHE = os.path.join(tempfile.gettempdir(), "btc15m_bbdiv.json")  # public klines, never committed


def fetch():
    if os.path.exists(CACHE) and time.time() - os.path.getmtime(CACHE) < 86400 * 2:
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


def study(rows, label, hold):
    T = [x[0] for x in rows]; O = [x[1] for x in rows]; C = [x[4] for x in rows]; N = len(C)
    R = rsi_core(C, 14); K, D = stochrsi(C)
    SMA = [None] * N
    for i in range(199, N):
        SMA[i] = sum(C[i - 199:i + 1]) / 200

    def forward_outcome(i, side):
        """Net % from the next open held `hold` bars. Outcome only, never a signal input."""
        if i + 1 + hold >= N:
            return None
        g = O[i + 1 + hold] / O[i + 1] - 1
        return (g if side > 0 else -g) - FEE

    def fires(i):
        out = []
        if None in (K[i], D[i], K[i - 1], D[i - 1], R[i], R[i - 1], SMA[i]):
            return out
        up = C[i] > SMA[i]
        if K[i - 1] <= D[i - 1] and K[i] > D[i] and K[i] < 20 and D[i] < 20:
            out += [("SR_X", 1)] + ([("SR_X_T", 1)] if up else [])
        if K[i - 1] >= D[i - 1] and K[i] < D[i] and K[i] > 80 and D[i] > 80:
            out += [("SR_X", -1)] + ([("SR_X_T", -1)] if not up else [])
        if R[i - 1] <= 30 < R[i]:
            out += [("RSI30", 1)] + ([("RSI_T", 1)] if up else [])
        if R[i - 1] >= 70 > R[i]:
            out += [("RSI30", -1)] + ([("RSI_T", -1)] if not up else [])
        return out

    split = int(datetime(2024, 7, 1, tzinfo=timezone.utc).timestamp() * 1000)
    ev = {}; last = {}
    for i in range(201, N - 1):
        for name, side in fires(i):
            key = (name, side)
            if i - last.get(key, -10 ** 9) < 2 * hold:
                continue
            r = forward_outcome(i, side)
            if r is None:
                continue
            last[key] = i
            ev.setdefault(key, []).append((T[i] >= split, r))
    base = {s: [(T[i] >= split, forward_outcome(i, s)) for i in range(201, N - 1, hold) if forward_outcome(i, s) is not None] for s in (1, -1)}
    print("== %s, hold %d bars" % (label, hold))
    for side in (1, -1):
        for name in ("SR_X", "SR_X_T", "RSI30", "RSI_T"):
            cells = []
            for oos in (False, True):
                x = [r for o, r in ev.get((name, side), []) if o == oos]
                b = [r for o, r in base[side] if o == oos]
                if len(x) < 10:
                    cells.append("n=%3d" % len(x)); continue
                cells.append("n=%3d net %+.3f%% win %2.0f%% edge %+.3f%%" % (
                    len(x), st.mean(x) * 100, 100 * sum(v > 0 for v in x) / len(x), (st.mean(x) - st.mean(b)) * 100))
            print("  %-5s %-6s IS %-42s | OOS %s" % ("long" if side > 0 else "short", name, cells[0], cells[1]))
    print("  now: K %.1f D %.1f RSI %.1f close %.0f SMA200 %.0f" % (K[-1], D[-1], R[-1], C[-1], SMA[-1]))


rows = fetch()[:-1]
study(rows, "15m", 8)
study(agg(rows, 4), "1h", 6)
study(agg(rows, 16), "4h", 6)
study(agg(rows, 96), "1d", 5)
