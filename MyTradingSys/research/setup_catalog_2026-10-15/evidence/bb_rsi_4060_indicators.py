"""Recompute the BB(20,2) / RSI14 / RSI-SMA14 / taker-delta / OI legends for the 2026-10-15 operator teaching shots
(9317fd8402ed, 672453a288eb) from OUR 1m Binance klines (free public fapi), so the pixel reads are not trusted alone.
Usage: python bb_rsi_4060_indicators.py <raw_dir> [oi_json]
BB = SMA20 of closes +/- 2 population std (TradingView); RSI = Wilder RMA 14 seeded on the full 15-day history; RSI-SMA = SMA14 of RSI.
CVD = running sum of taker delta (2*taker_buy_base - volume) anchored at the stated start bar; net delta = per-bar taker delta."""
import csv, glob, sys, json, math
from datetime import datetime, timezone
raw = sys.argv[1]
rows = []
for f in sorted(glob.glob(raw + "/klines/BTCUSDT-1m-*.csv")):
    with open(f) as fh:
        r = csv.reader(fh); next(r)
        for x in r:
            rows.append((int(x[0]), float(x[1]), float(x[2]), float(x[3]), float(x[4]), float(x[5]), float(x[9])))
ts = [r[0] for r in rows]; cl = [r[4] for r in rows]
def hhmm(t): return datetime.fromtimestamp(t / 1000, timezone.utc).strftime("%H:%M")
# Wilder RSI
rsi = [None] * len(cl); ag = al = 0.0
for i in range(1, len(cl)):
    d = cl[i] - cl[i - 1]; g = max(d, 0); l = max(-d, 0)
    if i <= 14:
        ag += g / 14; al += l / 14
        if i == 14: rsi[i] = 100 - 100 / (1 + ag / al) if al else 100
    else:
        ag = (ag * 13 + g) / 14; al = (al * 13 + l) / 14
        rsi[i] = 100 - 100 / (1 + ag / al) if al else 100
def sma_rsi(i): return sum(rsi[i - 13:i + 1]) / 14
def bb(i):
    w = cl[i - 19:i + 1]; m = sum(w) / 20; s = math.sqrt(sum((c - m) ** 2 for c in w) / 20); return m - 2 * s, m, m + 2 * s
idx = {hhmm(t): i for i, t in enumerate(ts) if datetime.fromtimestamp(t / 1000, timezone.utc).day == 15}
def delta(i): return 2 * rows[i][6] - rows[i][5]
out = []
def line(lab, i, cvd_from):
    lo, mid, up = bb(i); c = cl[i]
    cvd = sum(delta(j) for j in range(idx[cvd_from], i + 1))
    pb = (c - lo) / (up - lo)
    print(f"{lab:14s} bar {hhmm(ts[i])} O{rows[i][1]:.1f} H{rows[i][2]:.1f} L{rows[i][3]:.1f} C{c:.1f} | BB lo {lo:.1f} mid {mid:.1f} up {up:.1f} %B {pb:.2f} | RSI {rsi[i]:.2f} SMA14 {sma_rsi(i):.2f} | netdelta {delta(i):.1f} CVD(from {cvd_from}) {cvd:.0f}")
if __name__ == "__main__":
    for lab, t in [("V1 12:39", "12:39"), ("V2 12:51", "12:51"), ("V3 13:15", "13:15"), ("shot1 last", "13:22"), ("shot2 last", "13:28")]:
        line(lab, idx[t], "11:30")
    print("--- bars 13:20-13:31 (break)")
    for t in ["13:%02d" % m for m in range(20, 32) if "13:%02d" % m in idx]:
        line("", idx[t], "11:30")
    print("--- bars 12:36-12:42"); [line("", idx[t], "11:30") for t in ["12:%02d" % m for m in range(36, 43)]]
    print("--- bars 12:48-12:54"); [line("", idx[t], "11:30") for t in ["12:%02d" % m for m in range(48, 55)]]
    print("--- bars 13:12-13:18"); [line("", idx[t], "11:30") for t in ["13:%02d" % m for m in range(12, 19)]]

def forming(label, t, last_close):
    """Re-compute the legend with the forming bar's close replaced by the close shown in the screenshot (the shot was taken mid-bar)."""
    global cl, rsi
    i = idx[t]; save = cl[i]; cl[i] = last_close
    ag = al = 0.0; r = [None] * len(cl)
    for k in range(1, i + 1):
        d = cl[k] - cl[k - 1]; g = max(d, 0); l = max(-d, 0)
        if k <= 14:
            ag += g / 14; al += l / 14
            if k == 14: r[k] = 100 - 100 / (1 + ag / al)
        else:
            ag = (ag * 13 + g) / 14; al = (al * 13 + l) / 14; r[k] = 100 - 100 / (1 + ag / al)
    lo, mid, up = bb(i); sm = sum(r[i - 13:i + 1]) / 14
    print(f"{label}: forming bar {t} close {last_close} -> BB lo {lo:.1f} mid {mid:.1f} up {up:.1f} | RSI {r[i]:.2f} SMA14 {sm:.2f}")
    cl[i] = save

if __name__ == "__main__":
    print("--- legend check (screenshot legend: shot1 BB 80458.0/80592.2/80323.7 RSI 39.05 SMA 37.98; shot2 BB 80402.8/80552.9/80252.6 RSI 29.95 SMA 37.46)")
    forming("shot 9317fd8402ed", "13:23", 80388.0)
    forming("shot 672453a288eb", "13:28", 80234.1)
