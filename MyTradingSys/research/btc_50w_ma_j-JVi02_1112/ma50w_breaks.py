"""BTC weekly close vs 50-week simple MA: every week the close crosses from above to below, and what followed.

Usage (repo root): python MyTradingSys/research/btc_50w_ma_j-JVi02_1112/ma50w_breaks.py [--csv weekly.csv]
Data: Binance spot BTCUSDT 1w klines (public, data-api.binance.vision /api/v3/klines, weeks open Monday 00:00 UTC), fetched once
unless --csv points to a saved copy. Descriptive only: no fees, no trade rule, no parameter search.
MA = mean of the last 50 weekly closes including the current week (SOURCED: video title "50W Moving Average";
simple vs exponential is not stated in data we hold, so SMA is OURS).
Break = close[t] < MA[t] and close[t-1] >= MA[t-1]. A break within 8 weeks of the previous break is a re-break
(OURS) and is listed but marked.
Forward returns: close[t+h] / close[t] - 1 for h = 4, 12, 26 weeks; min and max close inside (t, t+26].
"""
import argparse
import csv
import json
import sys
import urllib.request
from datetime import datetime, timezone

URL = "https://data-api.binance.vision/api/v3/klines?symbol=BTCUSDT&interval=1w&limit=1000"
N = 50
H = (4, 12, 26)
REBREAK = 8


def load(path):
    if path:
        with open(path, newline="") as f:
            return [(r["open_time"], float(r["close"])) for r in csv.DictReader(f)]
    with urllib.request.urlopen(URL, timeout=30) as r:
        rows = json.load(r)
    now_ms = datetime.now(timezone.utc).timestamp() * 1000
    rows = [k for k in rows if k[6] < now_ms]  # closed weeks only: the running week is not a weekly close
    return [(datetime.fromtimestamp(k[0] / 1000, timezone.utc).strftime("%Y-%m-%d"), float(k[4])) for k in rows]


def breaks(rows):
    closes = [c for _, c in rows]
    ma = [None] * len(closes)
    for i in range(N - 1, len(closes)):
        ma[i] = sum(closes[i - N + 1:i + 1]) / N
    out, last = [], None
    for i in range(N, len(closes)):
        if ma[i - 1] is None:
            continue
        if closes[i] < ma[i] and closes[i - 1] >= ma[i - 1]:
            fw = {h: (closes[i + h] / closes[i] - 1) if i + h < len(closes) else None for h in H}
            win = closes[i + 1:i + 27]
            out.append({
                "week": rows[i][0], "close": closes[i], "ma": ma[i],
                "rebreak": last is not None and i - last <= REBREAK,
                **{f"r{h}w": fw[h] for h in H},
                "min26": (min(win) / closes[i] - 1) if len(win) == 26 else None,
                "max26": (max(win) / closes[i] - 1) if len(win) == 26 else None,
            })
            last = i
    return out, ma, closes


def pct(x):
    return "n/a" if x is None else f"{x * 100:+.1f}%"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv")
    ap.add_argument("--save")
    a = ap.parse_args()
    rows = load(a.csv)
    if a.save:
        with open(a.save, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["open_time", "close"])
            w.writerows(rows)
    out, ma, closes = breaks(rows)
    print(f"weeks={len(rows)} first={rows[0][0]} last={rows[-1][0]} last_close={closes[-1]:.0f} last_ma50={ma[-1]:.0f}")
    print("| week | close | 50W MA | re-break | +4w | +12w | +26w | min in 26w | max in 26w |")
    print("|---|---|---|---|---|---|---|---|---|")
    for b in out:
        print(f"| {b['week']} | {b['close']:.0f} | {b['ma']:.0f} | {'yes' if b['rebreak'] else 'no'} | "
              f"{pct(b['r4w'])} | {pct(b['r12w'])} | {pct(b['r26w'])} | {pct(b['min26'])} | {pct(b['max26'])} |")
    first = [b for b in out if not b["rebreak"]]
    for h in H:
        v = [b[f"r{h}w"] for b in first if b[f"r{h}w"] is not None]
        if v:
            print(f"first breaks +{h}w: n={len(v)} up={sum(x > 0 for x in v)} median={pct(sorted(v)[len(v) // 2])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
