"""squeeze_state.py - descriptive squeeze state on BTCUSDT 1d/1h/15m, last 90 days (Bybit public klines). No verdict."""
import json
import os
import statistics
import sys
import time
import urllib.request
from datetime import datetime, timezone

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "backtest", "layers", "squeeze"))
from squeeze import squeeze_momentum  # noqa: E402

TFS = [("1d", "D", 86400), ("1h", "60", 3600), ("15m", "15", 900)]
WARM = 60


def fetch(interval, sec, end_ms, n):
    out = {}
    cur_end = end_ms
    while len(out) < n:
        url = ("https://api.bybit.com/v5/market/kline?category=linear&symbol=BTCUSDT&interval=%s&limit=1000&end=%d"
               % (interval, cur_end))
        rows = json.load(urllib.request.urlopen(url, timeout=30))["result"]["list"]
        if not rows:
            break
        for r in rows:
            out[int(r[0])] = tuple(float(x) for x in r[1:5])
        cur_end = min(int(r[0]) for r in rows) - 1
        time.sleep(0.2)
    ks = sorted(out)
    return ks[-n:], [out[k] for k in ks[-n:]]


def main():
    now_ms = int(time.time() * 1000)
    lines = ["# Squeeze state, BTCUSDT (Bybit linear public klines), last 90 days - descriptive, n printed, no verdict",
             "", "Generated %s. Engine: layers/squeeze/squeeze.py, FORMULAS s31, LazyBear defaults 20/2.0/1.5/20 (SOURCED). "
             "The last bar of each series is partial (still forming) and is excluded." % datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%MZ"), ""]
    for name, iv, sec in TFS:
        n90 = 90 * 86400 // sec
        ks, rows = fetch(iv, sec, now_ms, n90 + WARM + 1)
        ks, rows = ks[:-1], rows[:-1]
        H = [r[1] for r in rows]; L = [r[2] for r in rows]; C = [r[3] for r in rows]
        on, off, mom = squeeze_momentum(H, L, C)
        lo = len(ks) - n90
        idx = [i for i in range(max(lo, 0), len(ks)) if on[i] is not None]
        n_on = sum(1 for i in idx if on[i])
        runs, run = [], 0
        for i in idx:
            if on[i]:
                run += 1
            elif run:
                runs.append(run); run = 0
        if run:
            runs.append(run)
        rel = [i for i in idx if i > 0 and on[i - 1] and not on[i] and mom[i] is not None]
        lines.append("## %s: n = %d bars (%s to %s)" % (name, len(idx),
                     datetime.fromtimestamp(ks[idx[0]] / 1000, timezone.utc).strftime("%Y-%m-%d %H:%MZ"),
                     datetime.fromtimestamp(ks[idx[-1]] / 1000, timezone.utc).strftime("%Y-%m-%d %H:%MZ")))
        lines.append("- in squeeze: %d of %d bars = %.1f%%; squeeze runs n = %d, median length %s bars" % (
            n_on, len(idx), 100.0 * n_on / len(idx), len(runs), statistics.median(runs) if runs else "n/a"))
        lines.append("- last 5 releases (squeeze ON -> not ON; momentum sign at the release bar; close move over the next 12 bars):")
        for i in rel[-5:]:
            t = datetime.fromtimestamp(ks[i] / 1000, timezone.utc).strftime("%Y-%m-%d %H:%MZ")
            mv = "%+.2f%%" % (100.0 * (C[i + 12] / C[i] - 1)) if i + 12 < len(C) else "n/a (fewer than 12 bars after)"
            lines.append("  - %s  momentum %s (%+.1f)  next-12-bar move %s" % (t, "+" if mom[i] > 0 else "-", mom[i], mv))
        lines.append("")
        print(name, len(idx), n_on)
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "SQUEEZE_STATE.md"), "w", newline="\n") as f:
        f.write("\n".join(lines))


if __name__ == "__main__":
    main()
