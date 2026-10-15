"""Checks for the operator's 2026-10-15 weekly-low + 80K sweep teaching (shots 4e8ef8d3f2e5 chart; 3016b2621f9d is NOT a chart, see the extract).
From OUR Binance fapi 1m klines (closed bars; scratch raw dir built from fapi because the archive has no 2026-10-15 file) and the 1m OI recorder.
Usage: python weekly_low_sweep_checks.py <raw_dir> <oi_1m.csv>"""
import csv, glob, math, sys
from datetime import datetime, timezone, timedelta
raw, oi_csv = sys.argv[1], sys.argv[2]
K = []
for f in sorted(glob.glob(raw + "/klines/BTCUSDT-1m-*.csv")):
    r = csv.reader(open(f)); next(r)
    for x in r: K.append((int(x[0]), float(x[1]), float(x[2]), float(x[3]), float(x[4]), float(x[5]), float(x[9])))
def T(s): return int(datetime.fromisoformat(s).replace(tzinfo=timezone.utc).timestamp() * 1000)
def hm(t): return datetime.fromtimestamp(t / 1000, timezone.utc).strftime("%m-%d %H:%M")
def rng(a, b): return [k for k in K if T(a) <= k[0] < T(b)]
def low(a, b): k = min(rng(a, b), key=lambda k: k[3]); return k[3], hm(k[0])
def high(a, b): k = max(rng(a, b), key=lambda k: k[2]); return k[2], hm(k[0])
print("== levels (1m lows/highs, closed bars)")
print("prior week Mon 10-05 .. Sun 10-11 low:", low("2026-10-05T00:00", "2026-10-12T00:00"))
print("prior week high:", high("2026-10-05T00:00", "2026-10-12T00:00"))
print("this week Mon 10-12 00:00 .. 13:30 low:", low("2026-10-12T00:00", "2026-10-15T13:30"))
print("today 00:00 .. 13:30 low:", low("2026-10-15T00:00", "2026-10-15T13:30"), " | today low up to 13:36:", low("2026-10-15T00:00", "2026-10-15T13:36"))
print("yesterday 10-14 low/high:", low("2026-10-14T00:00", "2026-10-15T00:00"), high("2026-10-14T00:00", "2026-10-15T00:00"))
print("sweep low 13:30-14:14:", low("2026-10-15T13:30", "2026-10-15T14:15"))
print("\n== first 1m close below each level (13:00 onward) and first 1m low below")
for lv in (80393.0, 80091.0, 80027.0, 80000.0, 79900.0):
    c = next((k for k in rng("2026-10-15T13:00", "2026-10-15T14:15") if k[4] < lv), None)
    l = next((k for k in rng("2026-10-15T13:00", "2026-10-15T14:15") if k[3] < lv), None)
    print(f"{lv:.0f}: first close below {hm(c[0]) if c else '-'} ({c[4] if c else ''}); first low below {hm(l[0]) if l else '-'} ({l[3] if l else ''})")
low_bar = min(rng("2026-10-15T13:30", "2026-10-15T14:15"), key=lambda k: k[3])
print("depth under 80000 at the low: %.1f pts = %.3f %%" % (80000 - low_bar[3], (80000 - low_bar[3]) / 80000 * 100))
print("\n== reclaim: first 1m close above 80000 after the low, and minutes since the low / since the first low below 80000")
fl = next(k for k in rng("2026-10-15T13:00", "2026-10-15T14:15") if k[3] < 80000)
rc = next(k for k in K if k[0] > low_bar[0] and k[4] > 80000)
print("first low below 80000:", hm(fl[0]), fl[3], "| lowest:", hm(low_bar[0]), low_bar[3], "| first close back above 80000:", hm(rc[0]), rc[4], "| minutes from the lowest bar:", (rc[0] - low_bar[0]) // 60000, "| from the first break:", (rc[0] - fl[0]) // 60000)
rc2 = next(k for k in K if k[0] > low_bar[0] and k[4] > 80027.0)
print("first close back above 80027.0:", hm(rc2[0]), rc2[4])
print("\n== top break: 81146.6 (12:25 top) and day high")
tb = next((k for k in rng("2026-10-15T13:54", "2026-10-15T14:15") if k[2] > 81146.6), None)
print("first 1m high above 81146.6:", (hm(tb[0]), tb[2]) if tb else None, "| first close above:", next(((hm(k[0]), k[4]) for k in rng("2026-10-15T13:54", "2026-10-15T14:15") if k[4] > 81146.6), None))
print("high 13:54-14:14:", high("2026-10-15T13:54", "2026-10-15T14:15"))
print("\n== RSI14 (Wilder, 1m), taker net delta and CVD since the low")
cl = [k[4] for k in K]; rs = [None] * len(cl); ag = al = 0.0
for i in range(1, len(cl)):
    d = cl[i] - cl[i - 1]; g = max(d, 0); l = max(-d, 0)
    if i <= 14:
        ag += g / 14; al += l / 14
        if i == 14: rs[i] = 100 - 100 / (1 + ag / al)
    else:
        ag = (ag * 13 + g) / 14; al = (al * 13 + l) / 14; rs[i] = 100 - 100 / (1 + ag / al)
idx = {k[0]: i for i, k in enumerate(K)}
cvd = 0
for k in rng("2026-10-15T13:50", "2026-10-15T14:15"):
    d = 2 * k[6] - k[5]; cvd += d
    print(hm(k[0]), f"O{k[1]:.1f} H{k[2]:.1f} L{k[3]:.1f} C{k[4]:.1f} | RSI {rs[idx[k[0]]]:.1f} | delta {d:.0f} | CVD since 13:50 {cvd:.0f}")
print("\n== OI (recorder 1m, sparse) 13:20-14:15")
rows = [(int(r[0]), float(r[3])) for r in list(csv.reader(open(oi_csv)))[1:]]
print([(hm(t)[6:], round(v)) for t, v in rows if T("2026-10-15T13:20") <= t <= T("2026-10-15T14:15")])
