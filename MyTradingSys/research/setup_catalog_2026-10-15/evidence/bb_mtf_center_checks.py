"""Checks for the operator's 2026-10-15 ~14:30Z multi-timeframe BB(20,2) centre-line reading (OPR-BB-MTF-CENTER).
Recomputes 30m and 1h BB = SMA20 +/- 2 population SD of closes (forming bar included, as the chart legend does) from OUR Binance fapi 1m klines
(scratch raw dir built from fapi, closed 1m bars only). Prints the legends minute by minute around 14:30Z so the operator's numbers
(1h wick 81,390, 1h mid 81,240, 1h last 81,026, 1h upper 82,162; 30m mid 80,952, 30m last 81,001, 30m upper 81,636) can be matched to a minute.
Also prints the 1h bars of the last 12 hours against their BB mid (close above / below the mid) for the study definition.
Usage: python bb_mtf_center_checks.py <raw_dir>"""
import csv, glob, math, sys
from datetime import datetime, timezone
raw = sys.argv[1]
m1 = []
for f in sorted(glob.glob(raw + "/klines/BTCUSDT-1m-*.csv")):
    with open(f, newline="") as fh:
        r = csv.reader(fh); next(r)
        for x in r: m1.append((int(x[0]), float(x[1]), float(x[2]), float(x[3]), float(x[4])))
def hm(t): return datetime.fromtimestamp(t / 1000, timezone.utc).strftime("%m-%d %H:%M")
def tsms(h): return int(datetime(2026, 10, 15, int(h[:2]), int(h[3:5]), tzinfo=timezone.utc).timestamp() * 1000)
def agg(upto_ms, step):
    b = {}
    for t, o, h, l, c in m1:
        if t >= upto_ms: continue
        k = t - t % (step * 60000)
        if k in b: e = b[k]; e[1] = max(e[1], h); e[2] = min(e[2], l); e[3] = c
        else: b[k] = [o, h, l, c]
    return sorted(b), b
def bb(c):
    w = c[-20:]; m = sum(w) / 20; s = math.sqrt(sum((x - m) ** 2 for x in w) / 20)
    return m - 2 * s, m, m + 2 * s
print("== legends minute by minute (1m bars closed before the stated time; forming bar included)")
print("time  | 30m bar O H L C | 30m BB lo/mid/up | 1h bar O H L C | 1h BB lo/mid/up")
for hh in ("14:25", "14:28", "14:30", "14:31", "14:32", "14:33", "14:35", "14:38", "14:40"):
    upto = tsms(hh)
    k30, b30 = agg(upto, 30); k60, b60 = agg(upto, 60)
    e30, e60 = b30[k30[-1]], b60[k60[-1]]
    l3 = bb([b30[k][3] for k in k30]); l6 = bb([b60[k][3] for k in k60])
    print(f"{hh}Z | {hm(k30[-1])[6:]} {e30[0]:.1f} {e30[1]:.1f} {e30[2]:.1f} {e30[3]:.1f} | {l3[0]:.1f}/{l3[1]:.1f}/{l3[2]:.1f} | {hm(k60[-1])[6:]} {e60[0]:.1f} {e60[1]:.1f} {e60[2]:.1f} {e60[3]:.1f} | {l6[0]:.1f}/{l6[1]:.1f}/{l6[2]:.1f}")
print("operator: 1h wick 81,390 above 1h mid 81,240, last 81,026, 1h upper 82,162; 30m mid 80,952, last 81,001, 30m upper 81,636")
print("\n== 1h bars (closed) vs their own BB mid, last 14 hours: close side of the mid, touch of the mid by the wick")
upto = tsms("14:40")
k60, b60 = agg(upto, 60); cl = [b60[k][3] for k in k60]
for i in range(len(k60) - 14, len(k60)):
    lo, mid, up = bb(cl[:i + 1]); o, h, l, c = b60[k60[i]]
    side = "above" if c > mid else "below"
    touch = "TOUCH" if (h >= mid >= l) else "-"
    print(f"{hm(k60[i])} O{o:.1f} H{h:.1f} L{l:.1f} C{c:.1f} | BB {lo:.1f}/{mid:.1f}/{up:.1f} | close {side} mid | wick-touch {touch}{' (forming)' if i == len(k60) - 1 else ''}")
print("\n== 30m bars last 10, close vs mid")
k30, b30 = agg(upto, 30); cl = [b30[k][3] for k in k30]
for i in range(len(k30) - 10, len(k30)):
    lo, mid, up = bb(cl[:i + 1]); o, h, l, c = b30[k30[i]]
    print(f"{hm(k30[i])} O{o:.1f} H{h:.1f} L{l:.1f} C{c:.1f} | BB {lo:.1f}/{mid:.1f}/{up:.1f} | close {'above' if c > mid else 'below'} mid{' (forming)' if i == len(k30) - 1 else ''}")
