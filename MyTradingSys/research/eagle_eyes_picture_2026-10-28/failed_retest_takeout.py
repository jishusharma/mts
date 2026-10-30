"""C26: a 15m high (or low) is retested and NOT taken out, shorts (longs) build; later it IS taken out (operator's 10-31 chart:
circles 1-2 = 10-28 highs ~81.4-81.5k held, circle 3 = 10-29 took them out, then the crash). Research only, no orders.
All rules OURS:
  pivot high  = highest high of +-16 bars (4h each side), confirmed 16 bars later
  pull-back   = some low after the pivot at least 0.8% under it
  failed retest = first later bar with high within 0.4% under the pivot, pivot never exceeded so far, pivot age <= 72h;
                  decision 4 bars (1h) after the retest bar if still not exceeded and close below the pivot
  take-out    = first high above the pivot after the decision (mirror for lows)
  control     = the same pivots at age-matched times with the close 0.4-1.5% under the pivot, no retest condition
Measured: share taken out within 24/48/72h, hours pivot->retest and retest->take-out, and what follows the take-out:
'sweep' = close back under the pivot within 4 bars of the take-out, then the move 24h later.
Phase = 15m close vs its 200-bar SMA at the decision. In-sample 2022-01..2024-06, out-of-sample 2024-07..now."""
import json, os, sys, tempfile, time, urllib.request, statistics as st
from datetime import datetime, timezone

REPO = sys.argv[1]
sys.path.insert(0, REPO)
from MyTradingSys.backtest.fees import BINANCE_TAKER

FEE = BINANCE_TAKER * 2  # round trip from backtest/fees.py
CACHE = os.path.join(tempfile.gettempdir(), "btc15m_bbdiv.json")  # public klines, never committed
W, PB, NEAR, MAXAGE, CONF = 16, 0.008, 0.004, 288, 4


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


rows = fetch()[:-1]
T = [x[0] for x in rows]; O = [x[1] for x in rows]; C = [x[4] for x in rows]; N = len(C)
SPLIT = int(datetime(2024, 7, 1, tzinfo=timezone.utc).timestamp() * 1000)
SMA = [None] * N
for i in range(199, N):
    SMA[i] = sum(C[i - 199:i + 1]) / 200


def run(side):
    """side +1 = highs (shorts build under them), -1 = lows. Prices mirrored so one code path serves both."""
    Hs = [x[2] if side > 0 else -x[3] for x in rows]; Ls = [x[3] if side > 0 else -x[2] for x in rows]
    Cs = [c if side > 0 else -c for c in C]

    def forward_outcome(j, lvl):
        """From decision bar j: bars to the take-out (None if > 72h), and the sweep read after it. Outcome only."""
        for k in range(j + 1, min(N, j + 1 + MAXAGE)):
            if Hs[k] > lvl:
                back = any(Cs[m] < lvl for m in range(k, min(N, k + CONF + 1)))
                after = (C[k + 96] / C[k] - 1) * side * 100 if k + 96 < N else None  # + = kept going through the level, - = reversed
                return k - j, back, after
        return None, None, None

    pivots = []; events = []; ctrl = []
    for i in range(2 * W, N - 1):
        p = i - W
        if Hs[p] == max(Hs[i - 2 * W:i + 1]):
            pivots.append(dict(p=p, lvl=Hs[p], pulled=False, done=False, cdone=False))
        for pv in pivots:
            if pv["done"] and pv["cdone"]:
                continue
            if i - pv["p"] > MAXAGE or Hs[i] > pv["lvl"]:
                pv["done"] = pv["cdone"] = True; continue
            if i <= pv["p"] + W:
                continue
            if Ls[i] <= pv["lvl"] * (1 - PB) if side > 0 else Ls[i] <= pv["lvl"] * (1 + PB):
                pv["pulled"] = True
            if not pv["pulled"]:
                continue
            gap = (pv["lvl"] - Cs[i]) / abs(pv["lvl"])
            if not pv["cdone"] and i % 8 == 0 and NEAR <= gap <= 0.015 and SMA[i] is not None:
                pv["cdone"] = True
                ctrl.append((T[i] >= SPLIT, forward_outcome(i, pv["lvl"])))
            if not pv["done"] and Hs[i] >= pv["lvl"] - NEAR * abs(pv["lvl"]):
                pv["done"] = True
                j = i + CONF
                if j >= N or SMA[j] is None or any(Hs[m] > pv["lvl"] for m in range(i, j + 1)) or Cs[j] >= pv["lvl"]:
                    continue
                trend = "with" if (C[j] > SMA[j]) == (side > 0) else "against"  # highs in an uptrend = 'with'
                events.append(dict(oos=T[j] >= SPLIT, trend=trend, age=(i - pv["p"]) / 4, t=T[j], lvl=pv["lvl"],
                                   out=forward_outcome(j, pv["lvl"])))
        pivots = [pv for pv in pivots if not (pv["done"] and pv["cdone"])]
    return events, ctrl


def share(xs, h):
    return 100 * sum(1 for x in xs if x[0] is not None and x[0] <= h * 4) / len(xs)


for side, name in ((1, "HIGHS (shorts build under a held high)"), (-1, "LOWS (longs build over a held low)")):
    ev, ctrl = run(side)
    print("== %s" % name)
    for oos, per in ((False, "2022-01..2024-06"), (True, "2024-07..now")):
        c = [o for f, o in ctrl if f == oos]
        print("  %s control n=%4d  taken 24h %2.0f%% 48h %2.0f%% 72h %2.0f%%" % (per, len(c), share(c, 24), share(c, 48), share(c, 72)))
        for tr in ("with", "against", None):
            x = [e for e in ev if e["oos"] == oos and (tr is None or e["trend"] == tr)]
            if len(x) < 10:
                continue
            o = [e["out"] for e in x]
            tk = [v for v in o if v[0] is not None]
            sw = [v for v in tk if v[1]]
            aft = [v[2] for v in sw if v[2] is not None]
            print("  %s retest-held %-7s n=%4d taken 24h %2.0f%% 48h %2.0f%% 72h %2.0f%% | age at retest med %4.1fh | retest->take-out med %4.1fh"
                  " | take-outs that swept back %2.0f%%, 24h later med %+.2f%% (n=%d, - = reversed)" % (
                      per, tr or "all", len(x), share(o, 24), share(o, 48), share(o, 72), st.median(e["age"] for e in x),
                      st.median(v[0] / 4 for v in tk) if tk else 0, 100 * len(sw) / max(1, len(tk)), st.median(aft) if aft else 0, len(aft)))
    for e in ev:
        if e["t"] >= T[-1] - 4 * 86400000:
            print("  recent: %s level %.0f age %.1fh -> %s" % (datetime.fromtimestamp(e["t"] / 1000, timezone.utc).strftime("%m-%d %H:%M"),
                  abs(e["lvl"]), e["age"], "taken after %.1fh, swept back %s" % (e["out"][0] / 4, e["out"][1]) if e["out"][0] else "not taken"))
