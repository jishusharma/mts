"""After a long-liquidation flush (5m: price -0.25%+ and OI -0.2%+ in one bar), what does the OI path over the next
40 min say about the next 1h/4h? Bybit linear BTCUSDT public data, ~120 days. OURS thresholds. Research only."""
import json, os, time, urllib.request, statistics as st

import tempfile
CACHE = os.path.join(tempfile.gettempdir(), "bybit_oi_k5.json")  # public data, never committed
DAYS = 120


def get(u):
    with urllib.request.urlopen(u, timeout=20) as r:
        return json.loads(r.read())["result"]


def fetch():
    if os.path.exists(CACHE) and time.time() - os.path.getmtime(CACHE) < 3600:
        return json.load(open(CACHE))
    end = int(time.time() * 1000); start = end - DAYS * 86400000
    k = {}; e = end
    while e > start:
        r = get("https://api.bybit.com/v5/market/kline?category=linear&symbol=BTCUSDT&interval=5&limit=1000&end=%d" % e)["list"]
        if not r:
            break
        for x in r:
            k[int(x[0])] = [float(x[1]), float(x[2]), float(x[3]), float(x[4])]
        e = int(r[-1][0]) - 1
    oi = {}; e = end
    while e > start:
        r = get("https://api.bybit.com/v5/market/open-interest?category=linear&symbol=BTCUSDT&intervalTime=5min&limit=200&endTime=%d" % e)["list"]
        if not r:
            break
        for x in r:
            oi[int(x["timestamp"])] = float(x["openInterest"])
        e = int(r[-1]["timestamp"]) - 1
    rows = [[t] + k[t] + [oi[t]] for t in sorted(k) if t in oi and t >= start]
    json.dump(rows, open(CACHE, "w"))
    return rows


def flush_oi_change(O, C, I, j, pairing="new"):
    """OI change belonging to flush bar j. Bybit OI is stamped at snapshot time t = bar open, so bar j's own OI change
    is I[j+1]/I[j]-1 (new). The old pairing used I[j]/I[j-1]-1, i.e. the previous bar's change (off by one)."""
    if pairing == "old":
        return I[j] / I[j - 1] - 1
    return I[j + 1] / I[j] - 1


def classify(O, C, I, N, pairing):
    """Group flush events; returns {group: [forward outcomes]}. Thresholds OURS."""
    def fwd(j):
        return {h: (C[j + h] / C[j] - 1) * 100 if j + h < N else None for h in (12, 48)}
    groups = {"OI rebuilds >= +0.2%": [], "OI flat": [], "OI keeps falling <= -0.2%": []}
    last = -999
    for i in range(2, N - 9):
        if not (C[i] / C[i - 1] - 1 <= -0.0025 and flush_oi_change(O, C, I, i, pairing) <= -0.002) or i - last < 12:
            continue
        last = i; j = i + 8  # 40 min after the flush bar, decision at that close
        if abs(C[j] / C[i] - 1) > 0.008:
            continue  # price must chop, not trend, over those 40 min
        # OI level at the flush bar's close / at the decision close: new = stamps i+1, j+1; old = stamps i, j
        d = (I[j + 1] / I[i + 1] - 1) if pairing == "new" else (I[j] / I[i] - 1)
        g = "OI rebuilds >= +0.2%" if d >= 0.002 else "OI keeps falling <= -0.2%" if d <= -0.002 else "OI flat"
        groups[g].append(fwd(j))
    return groups


def report(groups, base):
    for g, v in list(groups.items()) + [("base (every 30 min)", base)]:
        for h, lab in ((12, "1h"), (48, "4h")):
            x = [e[h] for e in v if e[h] is not None]
            if len(x) < 3:
                print("%-27s %s n=%d" % (g, lab, len(x))); continue
            print("%-27s %s n=%4d mean %+.2f%% med %+.2f%% up %3.0f%% | drop >1%% %3.0f%% rise >1%% %3.0f%%" % (
                g, lab, len(x), st.mean(x), st.median(x), 100 * sum(a > 0 for a in x) / len(x),
                100 * sum(a < -1 for a in x) / len(x), 100 * sum(a > 1 for a in x) / len(x)))


if __name__ == "__main__":
    R = fetch()[:-1]
    T = [r[0] for r in R]; O = [r[1] for r in R]; C = [r[4] for r in R]; I = [r[5] for r in R]; N = len(R)
    print("bars %d, %s .. %s" % (N, time.strftime("%m-%d", time.gmtime(T[0] / 1000)), time.strftime("%m-%d %H:%M", time.gmtime(T[-1] / 1000))))
    base = [{h: (C[j + h] / C[j] - 1) * 100 if j + h < N else None for h in (12, 48)} for j in range(0, N - 1, 6)]
    for p in ("old", "new"):
        print("=== pairing: %s ===" % p)
        report(classify(O, C, I, N, p), base)
