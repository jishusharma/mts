"""vfi_state.py - descriptive VFI state on BTCUSDT 1d and 15m, last 90 days (Bybit public klines). No verdict."""
import json
import os
import sys
import time
import urllib.request
from datetime import datetime, timezone

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "backtest", "layers", "vfi"))
from vfi import vfi  # noqa: E402

TFS = [("1d", "D", 86400), ("15m", "15", 900)]
WARM = 130 + 130 + 10          # vfi is defined from bar 259 (FORMULAS s32.1); a few spare bars
SWEEP_MS = int(datetime(2026, 11, 6, 15, 0, tzinfo=timezone.utc).timestamp() * 1000)   # Friday 2026-11-06 15:00Z 15m bar


def fetch(interval, end_ms, n):
    out = {}
    cur_end = end_ms
    while len(out) < n:
        url = ("https://api.bybit.com/v5/market/kline?category=linear&symbol=BTCUSDT&interval=%s&limit=1000&end=%d"
               % (interval, cur_end))
        rows = json.load(urllib.request.urlopen(url, timeout=30))["result"]["list"]
        if not rows:
            break
        for r in rows:
            out[int(r[0])] = tuple(float(x) for x in r[1:6])   # o h l c volume
        cur_end = min(int(r[0]) for r in rows) - 1
        time.sleep(0.2)
    ks = sorted(out)
    return ks[-n:], [out[k] for k in ks[-n:]]


def ts(ms):
    return datetime.fromtimestamp(ms / 1000, timezone.utc).strftime("%Y-%m-%d %H:%MZ")


def main():
    now_ms = int(time.time() * 1000)
    lines = ["# VFI state, BTCUSDT (Bybit linear public klines), last 90 days - descriptive, n printed, no verdict", "",
             "Generated %s. Engine: layers/vfi/vfi.py, FORMULAS s32, LazyBear defaults length 130, coef 0.2, vcoef 2.5, stdev 30, "
             "smoothing 3 (SOURCED). Sign and zero cross use the raw vfi. The last bar of each series is partial and excluded. "
             "TradingView check by Lead C is pending (FORMULAS s32.1 lists what to compare)." % datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%MZ"), ""]
    for name, iv, sec in TFS:
        n90 = 90 * 86400 // sec
        ks, rows = fetch(iv, now_ms, n90 + WARM + 1)
        ks, rows = ks[:-1], rows[:-1]
        H = [r[1] for r in rows]; L = [r[2] for r in rows]; C = [r[3] for r in rows]; V = [r[4] for r in rows]
        raw, sm = vfi(H, L, C, V)
        lo = len(ks) - n90
        idx = [i for i in range(max(lo, 0), len(ks)) if raw[i] is not None]
        pos = sum(1 for i in idx if raw[i] > 0)
        lines.append("## %s: n = %d bars with a defined vfi (%s to %s), %d bars fetched in total" % (name, len(idx), ts(ks[idx[0]]), ts(ks[idx[-1]]), len(ks)))
        lines.append("- vfi > 0 on %d of %d bars = %.1f%%; last vfi %+.3f (smoothed %s)" % (
            pos, len(idx), 100.0 * pos / len(idx), raw[idx[-1]], "%+.3f" % sm[idx[-1]] if sm[idx[-1]] is not None else "n/a"))
        crosses = [i for i in idx if i > 0 and raw[i - 1] is not None and raw[i - 1] != 0 and (raw[i - 1] > 0) != (raw[i] > 0)]
        lines.append("- zero crosses in the window n = %d; last 5 (raw vfi sign change; close move over the next 12 bars):" % len(crosses))
        for i in crosses[-5:]:
            mv = "%+.2f%%" % (100.0 * (C[i + 12] / C[i] - 1)) if i + 12 < len(C) else "n/a (fewer than 12 bars after)"
            lines.append("  - %s  vfi %+.3f -> %+.3f (%s)  next-12-bar move %s" % (
                ts(ks[i]), raw[i - 1], raw[i], "up" if raw[i] > 0 else "down", mv))
        if iv == "15":
            if SWEEP_MS in ks:
                j = ks.index(SWEEP_MS)
                lines.append("- Friday 2026-11-06 15:00Z sweep bar (15m open time; high %.1f low %.1f close %.1f volume %.1f): vfi %+.3f, smoothed %s" % (
                    H[j], L[j], C[j], V[j], raw[j], "%+.3f" % sm[j] if sm[j] is not None else "n/a"))
                lines.append("- the 20 bars before it, then the sweep bar (open time, close, raw vfi, change vs the previous bar):")
                for k in range(j - 20, j + 1):
                    d = raw[k] - raw[k - 1]
                    lines.append("  - %s  close %.1f  vfi %+.3f  %+.3f%s" % (ts(ks[k]), C[k], raw[k], d, "  <- sweep bar" if k == j else ""))
                first, last = raw[j - 20], raw[j - 1]
                falling = sum(1 for k in range(j - 19, j) if raw[k] < raw[k - 1])
                lines.append("- over those 20 bars vfi went %+.3f -> %+.3f (change %+.3f); it fell on %d of the 19 steps (n = 19, descriptive, no verdict)" % (
                    first, last, last - first, falling))
            else:
                lines.append("- sweep bar 2026-11-06 15:00Z not in the fetched series")
        lines.append("")
        print(name, len(idx), pos)
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "VFI_STATE.md"), "w", newline="\n") as f:
        f.write("\n".join(lines))


if __name__ == "__main__":
    main()
