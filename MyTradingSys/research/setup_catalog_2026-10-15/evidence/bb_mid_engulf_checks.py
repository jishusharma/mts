"""Checks for the operator's 2026-10-15 5m teaching (shots 29b79af8ff8f, 587ee73bd78c): BB(20,2) midline rejection, bearish engulf, second break.
Recomputes from OUR Binance fapi 1m klines (closed bars; archive has no 2026-10-15 file, so a scratch raw dir was built from fapi): 5m / 1h / 4h bars,
BB = SMA20 +/- 2 population SD of closes, RSI = Wilder 14 seeded on the full history, RSI-SMA = SMA14 of RSI.
Usage: python bb_mid_engulf_checks.py <raw_dir> [oi_csv]
The forming bar is rebuilt from the 1m bars that had closed when the shot was taken (shot 1 about 13:52:41Z, shot 2 about 13:54:05Z, from the countdown timers)."""
import csv, glob, math, sys
from datetime import datetime, timezone
raw = sys.argv[1]
oi_csv = sys.argv[2] if len(sys.argv) > 2 else None
m1 = []
for f in sorted(glob.glob(raw + "/klines/BTCUSDT-1m-*.csv")):
    with open(f) as fh:
        r = csv.reader(fh); next(r)
        for x in r: m1.append((int(x[0]), float(x[1]), float(x[2]), float(x[3]), float(x[4]), float(x[5]), float(x[9])))
def hm(t): return datetime.fromtimestamp(t / 1000, timezone.utc).strftime("%H:%M")
def tsms(h): return int(datetime(2026, 10, 15, int(h[:2]), int(h[3:5]), tzinfo=timezone.utc).timestamp() * 1000)
def agg(upto_ms, step):
    """bars of step minutes from 1m bars with open_time < upto_ms (the last bar may be forming)"""
    b = {}
    for t, o, h, l, c, v, tb in m1:
        if t >= upto_ms: continue
        k = t - t % (step * 60000)
        if k in b: e = b[k]; e[1] = max(e[1], h); e[2] = min(e[2], l); e[3] = c; e[4] += v; e[5] += tb
        else: b[k] = [o, h, l, c, v, tb]
    return sorted(b), b
def rsi(c):
    r = [None] * len(c); ag = al = 0.0
    for i in range(1, len(c)):
        d = c[i] - c[i - 1]; g = max(d, 0); l = max(-d, 0)
        if i <= 14:
            ag += g / 14; al += l / 14
            if i == 14: r[i] = 100 - 100 / (1 + ag / al)
        else:
            ag = (ag * 13 + g) / 14; al = (al * 13 + l) / 14; r[i] = 100 - 100 / (1 + ag / al)
    return r
def legend(step, upto_ms):
    ks, b = agg(upto_ms, step); c = [b[k][3] for k in ks]; r = rsi(c); i = len(c) - 1
    w = c[i - 19:i + 1]; m = sum(w) / 20; s = math.sqrt(sum((x - m) ** 2 for x in w) / 20)
    return hm(ks[-1]), c[i], m - 2 * s, m, m + 2 * s, r[i], sum(r[i - 13:i + 1]) / 14
print("== closed 5m bars 13:25-13:50 on 2026-10-15 (O H L C, colour, BB at each bar close, RSI, delta)")
ks, b = agg(tsms("13:55"), 5)
for k in ks:
    if tsms("13:25") <= k <= tsms("13:50"):
        o, h, l, c, v, tb = b[k]
        _, cc, lo, mid, up, rr, sm = legend(5, k + 300000)
        print(f"{hm(k)} O{o:.1f} H{h:.1f} L{l:.1f} C{c:.1f} {'GREEN' if c >= o else 'RED'} body {abs(c-o):.1f} | BB {lo:.1f}/{mid:.1f}/{up:.1f} | RSI {rr:.2f} SMA {sm:.2f} | delta {2*tb-v:.0f}")
print("\n== engulf test (operator wording: red 5m candle closes below the OPEN of the previous green candle)")
g, red = b[tsms("13:40")], b[tsms("13:45")]
print(f"previous green 13:40: open {g[0]:.1f} close {g[3]:.1f} body {g[3]-g[0]:.1f}; red 13:45: open {red[0]:.1f} close {red[3]:.1f} body {red[0]-red[3]:.1f}")
print(f"close < previous open: {red[3] < g[0]} (by {g[0]-red[3]:.1f}); red open >= previous close (strict classic engulf): {red[0] >= g[3]}; body ratio {(red[0]-red[3])/(g[3]-g[0]):.1f}")
print(f"marked line 80654.5 vs previous green open {g[0]:.1f} and 13:35 bar close {b[tsms('13:35')][3]:.1f}")
print(f"red 13:45 high {red[1]:.1f}, low {red[2]:.1f}")
print("\n== forming-bar legends at the two shots (1m bars closed before the shot; forming close = last closed 1m close)")
for lab, upto in [("shot 1 ~13:52:41 (bars through 13:52)", "13:53"), ("shot 2 ~13:54:05 (bars through 13:53)", "13:54")]:
    t, c, lo, mid, up, rr, sm = legend(5, tsms(upto))
    ks2, b2 = agg(tsms(upto), 5); e = b2[ks2[-1]]
    print(f"{lab}: forming 5m {t} O{e[0]:.1f} H{e[1]:.1f} L{e[2]:.1f} C{e[3]:.1f} | BB {lo:.1f}/{mid:.1f}/{up:.1f} | RSI {rr:.2f} SMA {sm:.2f} | CVD since 13:50 {2*e[5]-e[4]:.0f}")
print("image legends: shot 1 BB 80058.5/80615.8/81173.2 (O80342.3 H80355.0 L80053.7 C80083.6), RSI 34.56 SMA 38.14, CVD -11.14K, OI 94.14K;")
print("               shot 2 BB 80015.7/80607.7/81199.7 (L79831.4 C79920.3), RSI 31.86 SMA 37.94, CVD -11.938K, OI 94.174K")
print("\n== swept low: 5m 13:30 bar low and 1m lows 13:25-13:40")
print("5m 13:30 low", b[tsms("13:30")][2], "; 1m lows:", [(hm(t), l) for t, o, h, l, c, v, tb in m1 if "13:25" <= hm(t) <= "13:40" and l < 80100])
print("\n== higher timeframes at ~13:54 (forming bar = bars closed through 13:53)")
for step, name in [(15, "15m"), (60, "1h"), (240, "4h")]:
    t, c, lo, mid, up, rr, sm = legend(step, tsms("13:54"))
    print(f"{name} bar {t}: close {c:.1f} | BB {lo:.1f}/{mid:.1f}/{up:.1f} | price below mid: {c < mid} (by {mid-c:.1f}) | RSI {rr:.2f} SMA {sm:.2f}")
print("\n== what price did after the signals (one instance, after the fact, NOT a result)")
def after(t0, label):
    e = [x for x in m1 if x[0] >= tsms(t0)]; entry = e[0][1]; hi = max(x[2] for x in e); lo = min(x[3] for x in e)
    print(f"{label}: entry at open {entry:.1f} ({t0}); to the last closed 1m ({hm(e[-1][0])}): max high {hi:.1f} (adverse {hi-entry:.1f}), min low {lo:.1f} (favourable {entry-lo:.1f}); 12 bp round trip = {entry*0.0012:.0f} pts")
after("13:50", "after first confirmation (engulf closed 13:50:00)")
after("13:55", "after second confirmation (13:50 bar closed 13:55:00)")
if oi_csv:
    rows = [(int(r[0]), float(r[3])) for r in list(csv.reader(open(oi_csv)))[1:]]
    print("\n== OI recorder rows 13:20-13:56 (sparse):", [(hm(t), round(v)) for t, v in rows if tsms("13:20") <= t <= tsms("13:56") + 59000])
