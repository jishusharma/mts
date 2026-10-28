"""Worker C (screenshot observations): reproducible check of F-BT-08 (Java buildVp volume weighting).

Emulates MarketDataSnapshot.buildVp (1m bars, 5-USD-ish bins, triangular weight around hlc3, weights NOT normalised)
and compares its POC with (a) the same algorithm with per-bar weights normalised to the bar volume and
(b) the trade-level profile from orderflow_live fp ($10 buckets, real traded volume).
Read-only. Not imported by any live process. Run: python MyTradingSys/backtest/bigtrade/obs_vp_check.py
Expected Java values (snapshots): Oct 5 prior_day.poc 85510.32, Oct 6 86269.35, Oct 7 83702.35, Oct 4 86574.75.
"""
import bisect
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
KL = ROOT / "Dumps" / "backtest" / "raw" / "klines"
OF = ROOT / "MyTradingSys" / "runtime" / "orderflow_live"


def load_klines(day):
    rows = []
    with open(KL / ("BTCUSDT-1m-%s.csv" % day), newline="") as f:
        for r in csv.DictReader(f):
            rows.append(dict(h=float(r["high"]), l=float(r["low"]), c=float(r["close"]), v=float(r["volume"])))
    return rows


def trade_profile(day):
    prof = {}
    with open(OF / ("%s.csv" % day), newline="") as f:
        for r in csv.DictReader(f):
            for cell in r["fp"].split("|"):
                if cell:
                    p, b, s = cell.split(":")
                    prof[float(p)] = prof.get(float(p), 0.0) + float(b) + float(s)
    return prof


def java_vp_poc(bars, normalize=False):
    lo = min(b["l"] for b in bars)
    hi = max(b["h"] for b in bars)
    rng = hi - lo
    nb = max(50, int(rng / 5))
    bs = rng / nb
    keys = [lo + i * bs for i in range(nb + 1)]
    prof = dict.fromkeys(keys, 0.0)
    total = 0.0

    def floorkey(p):
        i = bisect.bisect_right(keys, p) - 1
        return keys[i] if i >= 0 else keys[0]

    for b in bars:
        tp = (b["h"] + b["l"] + b["c"]) / 3.0
        half = (b["h"] - b["l"]) / 2.0
        n = int(max(1, (b["h"] - b["l"]) / bs))
        ws = []
        for i in range(n):
            p = b["l"] + i * (b["h"] - b["l"]) / n
            w = 1.0 - abs(p - tp) / half if half > 0 else 1.0
            ws.append((p, max(w, 0.0)))
        s = sum(w for _, w in ws)
        for p, w in ws:
            f = ((w / s * b["v"]) if s > 0 else 0.0) if normalize else w * b["v"]
            prof[floorkey(p)] += f
            total += f
    return max(prof, key=prof.get), total


def main():
    print("day | real vol | java weight sum (x) | java POC | normalised POC | trade-level POC ($10)")
    out = []
    for day in ("2026-10-04", "2026-10-05", "2026-10-06", "2026-10-07"):
        bars = load_klines(day)
        real = sum(b["v"] for b in bars)
        poc_j, tot = java_vp_poc(bars, False)
        poc_n, _ = java_vp_poc(bars, True)
        tp = trade_profile(day)
        poc_t = max(tp, key=tp.get)
        out.append((day, real, tot / real, poc_j, poc_n, poc_t))
        print("%s | %.0f | %.2fx | %.2f | %.1f | %.0f" % (day, real, tot / real, poc_j, poc_n, poc_t))
    return out


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
