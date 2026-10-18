"""Checks for the operator's 2026-10-15 ~15:25Z teaching (shot 8fc58204ee18): RSI regular bullish divergence at the sweep, the 5m upper-band walk,
and "1 min, 2 min and 3 min divergence already possible" (OPR-RSI-DIV-SWEEP-BAND-WALK).
Everything is recomputed from OUR Binance fapi 1m klines (scratch raw dir, closed 1m bars only); 2m, 3m and 5m are resampled from 1m (bar open = epoch minute rounded down).
BB = SMA20 of closes +/- 2 population SD; RSI = Wilder RMA 14 on each timeframe's own closes, seeded over all days in the raw dir; RSI-SMA = SMA14 of RSI.
Divergence rule (OURS, thresholds are grid values, not Malkan's or the operator's numbers):
  price pivot low  = a close that is the minimum of the k bars on each side and itself (k = 2, 3), first occurrence on ties
  regular bullish  = two ADJACENT close pivot lows P1, P2 with close(P2) < close(P1) and RSI(P2) > RSI(P1) (price lower low, RSI higher low), at most B bars apart
                     (B = 10: the 'less than 10 bars' of Malkan glossary 2.4, W; B = 30 as a wider grid value, OURS)
  signal time      = close of bar P2 + k (the first moment the pivot is known); price at the signal = that close; P2 itself must lie in the window below
Usage: python rsi_divergence_mtf_checks.py <raw_dir>"""
import csv, glob, math, sys
from datetime import datetime, timezone
sys.stdout.reconfigure(newline="\n")
raw = sys.argv[1]
m1 = []
for f in sorted(glob.glob(raw + "/klines/BTCUSDT-1m-*.csv")):
    with open(f, newline="") as fh:
        r = csv.reader(fh); next(r)
        for x in r:
            m1.append((int(x[0]), float(x[1]), float(x[2]), float(x[3]), float(x[4]), float(x[5]), float(x[9])))
def hm(t): return datetime.fromtimestamp(t / 1000, timezone.utc).strftime("%H:%M")
def ms(hhmm): return int(datetime(2026, 10, 15, int(hhmm[:2]), int(hhmm[3:5]), tzinfo=timezone.utc).timestamp() * 1000)
def resample(step, upto=None):
    """complete bars only, unless upto is given: then bars with 1m opens < upto, the last one possibly forming. returns list of [t,o,h,l,c,vol,tb,n]"""
    b = {}
    for t, o, h, l, c, v, tb in m1:
        if upto is not None and t >= upto: continue
        k = t - t % (step * 60000)
        if k in b:
            e = b[k]; e[2] = max(e[2], h); e[3] = min(e[3], l); e[4] = c; e[5] += v; e[6] += tb; e[7] += 1
        else:
            b[k] = [k, o, h, l, c, v, tb, 1]
    out = [b[k] for k in sorted(b)]
    return out if upto is not None else [e for e in out if e[7] == step]
def wilder(cl):
    rsi = [None] * len(cl); ag = al = 0.0
    for i in range(1, len(cl)):
        d = cl[i] - cl[i - 1]; g = max(d, 0); l = max(-d, 0)
        if i <= 14:
            ag += g / 14; al += l / 14
            if i == 14: rsi[i] = 100 - 100 / (1 + ag / al) if al else 100
        else:
            ag = (ag * 13 + g) / 14; al = (al * 13 + l) / 14
            rsi[i] = 100 - 100 / (1 + ag / al) if al else 100
    return rsi
def bb(cl, i):
    w = cl[i - 19:i + 1]; m = sum(w) / 20; s = math.sqrt(sum((c - m) ** 2 for c in w) / 20)
    return m - 2 * s, m, m + 2 * s
def rsisma(rsi, i): return sum(rsi[i - 13:i + 1]) / 14

print("== A. chart legend of shot 8fc58204ee18 (5m, forming bar 15:20, countdown 00:48 => about 15:24:12Z) against our 1m klines")
print("chart: O82269.9 H82319.2 L82124.0 C82319.2 | BB 20 2: mid 81355.6 upper 82794.9 lower 79916.4 | RSI14 75.32 SMA14 67.56 | net delta 3.718K")
for cut in ("15:23", "15:24", "15:25"):
    bars = resample(5, ms(cut)); cl = [e[4] for e in bars]; rsi = wilder(cl); i = len(bars) - 1; e = bars[i]
    lo, mid, up = bb(cl, i)
    print(f"1m closed through {hm(ms(cut) - 60000)}: bar {hm(e[0])} O{e[1]:.1f} H{e[2]:.1f} L{e[3]:.1f} C{e[4]:.1f} | BB lo {lo:.1f} mid {mid:.1f} up {up:.1f} | RSI {rsi[i]:.2f} SMA {rsisma(rsi, i):.2f} | taker delta of bar {2 * e[6] - e[5]:.3f} BTC ({e[7]} of 5 1m bars)")
print("(chart reads the live tick; our legend is the last closed 1m, so last/close and RSI/BB differ slightly)")

bars = resample(5, ms("15:24")); cl = [e[4] for e in bars]
cl[-1] = 82319.2; rsi = wilder(cl); i = len(bars) - 1; lo, mid, up = bb(cl, i)
print(f"chart tick substituted (1m closed through 15:23, last close set to the chart's 82319.2): BB lo {lo:.1f} mid {mid:.1f} up {up:.1f} | RSI {rsi[i]:.2f} SMA {rsisma(rsi, i):.2f}")
print("chart:                                                                                       BB lo 79916.4 mid 81355.6 up 82794.9 | RSI 75.32 SMA 67.56")
print("chart net delta 3.718K vs our taker delta of the bar (BTC, negative above) differ in sign and size: the CoinGlass Net Delta panel is a different quantity or unit and is NOT reproduced")

print("\n== B. marked lines of the shot: 79732.3 sweep low, 80027.0, 80743.5, 81146.6 (1m extremes on 2026-10-15)")
d15 = [x for x in m1 if x[0] >= ms("00:00")]
for lv in (79732.3, 80027.0, 80743.5, 81146.6):
    hit = [hm(x[0]) for x in d15 if x[3] == lv or x[2] == lv]
    print(f"level {lv}: 1m bars with that exact low/high: {hit if hit else 'none'}")
lowest = min(d15, key=lambda x: x[3])
print(f"day low {lowest[3]:.1f} at {hm(lowest[0])}Z 1m bar (low of 5m bar {hm(lowest[0] - lowest[0] % 300000)})")

print("\n== C. RSI regular bullish divergence on close pivot lows, window: P2 in 13:00..14:10Z, per timeframe")
for step in (1, 2, 3, 5):
    bars = resample(step); cl = [e[4] for e in bars]; rsi = wilder(cl)
    for k in (2, 3):
        piv = []
        for i in range(k, len(cl) - k):
            w = cl[i - k:i + k + 1]
            if cl[i] == min(w) and cl.index(min(w), i - k) == i and rsi[i] is not None: piv.append(i)
        for B in (10, 30):
            found = []
            for a, b in zip(piv, piv[1:]):
                if not (ms("13:00") <= bars[b][0] <= ms("14:10")): continue
                if b - a > B: continue
                if cl[b] < cl[a] and rsi[b] > rsi[a]: found.append((a, b))
            print(f"TF {step}m k={k} B={B}: {len(found)} divergence(s)")
            for a, b in found:
                sig = b + k; sbar = bars[sig]
                print(f"   P1 {hm(bars[a][0])} close {cl[a]:.1f} RSI {rsi[a]:.1f} | P2 {hm(bars[b][0])} close {cl[b]:.1f} RSI {rsi[b]:.1f} | {b - a} bars apart | signal {hm(sbar[0] + step * 60000)}Z (close of bar {hm(sbar[0])}) price {sbar[4]:.1f} | RSI at P2 below 40: {rsi[b] < 40}")

print("\n== D. after the sweep: first close above RSI 40 and RSI 60, first close above the marked lines (from 13:30Z)")
for step in (1, 2, 3, 5):
    bars = resample(step); cl = [e[4] for e in bars]; rsi = wilder(cl); res = {}
    for i, e in enumerate(bars):
        if e[0] < ms("13:30") or rsi[i] is None: continue
        for name, ok in (("RSI>40", rsi[i] > 40 and rsi[i - 1] <= 40), ("RSI>60", rsi[i] > 60 and rsi[i - 1] <= 60), ("close>80743.5", cl[i] > 80743.5), ("close>81146.6", cl[i] > 81146.6)):
            if ok and name not in res and (name.startswith("close") or e[0] >= ms("13:55")): res[name] = f"{hm(e[0] + step * 60000)}Z close of bar {hm(e[0])} ({cl[i]:.1f}, RSI {rsi[i]:.1f})"
    print(f"TF {step}m (RSI crosses counted from 13:55Z): " + "; ".join(f"{k} {v}" for k, v in res.items()))

print("\n== E. 5m band walk after the reclaim: %b = (close - lower) / (upper - lower); H = high >= upper; mid slope = mid - mid 3 bars earlier")
bars = resample(5, ms("15:25")); cl = [e[4] for e in bars]; rsi = wilder(cl); rows = []
for i, e in enumerate(bars):
    if e[0] < ms("13:50") or i < 20: continue
    lo, mid, up = bb(cl, i); _, mid3, _ = bb(cl, i - 3)
    pb = (cl[i] - lo) / (up - lo)
    rows.append((e[0], pb, e[2] >= up, mid - mid3))
    print(f"{hm(e[0])} C{cl[i]:.1f} lo {lo:.1f} mid {mid:.1f} up {up:.1f} | %b {pb:.2f} | high>=upper {'H' if e[2] >= up else '-'} | mid slope {mid - mid3:+.1f} | RSI {rsi[i]:.1f}{' (forming)' if e[7] < 5 else ''}")
print("walk rule (OURS): a walk bar has a closed 5m close with %b >= x (grid 0.7, 0.8, 0.9); a walk = >= 3 consecutive walk bars; it ends at the first closed bar with %b < e (grid 0.8, 0.5 = the mid)")
closed = [r for r in rows if bars[[e[0] for e in bars].index(r[0])][7] == 5]
for x in (0.7, 0.8, 0.9):
    runs = []; cur = []
    for r in closed:
        if r[1] >= x: cur.append(r)
        else:
            if len(cur) >= 3: runs.append(cur)
            cur = []
    if len(cur) >= 3: runs.append(cur)
    print(f"x={x}: " + (" ; ".join(f"walk {hm(g[0][0])}..{hm(g[-1][0])} ({len(g)} bars)" + (" still running at the last closed bar" if g[-1] is closed[-1] else " ended") for g in runs) if runs else "no walk"))

print("\n== F. the same two points on every timeframe: the bar that closes at 13:30Z against the lowest-close bar closing 13:45..13:56Z (RSI on that timeframe)")
for step in (1, 2, 3, 5):
    bars = resample(step); cl = [e[4] for e in bars]; rsi = wilder(cl)
    ia = [i for i, e in enumerate(bars) if e[0] + step * 60000 == ms("13:30")][0]
    cand = [i for i, e in enumerate(bars) if ms("13:45") <= e[0] + step * 60000 <= ms("13:56")]
    ib = min(cand, key=lambda i: cl[i])
    print(f"TF {step}m: A = bar {hm(bars[ia][0])} close {cl[ia]:.1f} RSI {rsi[ia]:.1f} | B = bar {hm(bars[ib][0])} close {cl[ib]:.1f} RSI {rsi[ib]:.1f} | price {'lower' if cl[ib] < cl[ia] else 'higher'} low, RSI {'higher' if rsi[ib] > rsi[ia] else 'lower'} low => {'regular bullish divergence' if cl[ib] < cl[ia] and rsi[ib] > rsi[ia] else 'no divergence'} (RSI gap {rsi[ib] - rsi[ia]:+.1f})")

print("\n== G. order flow from OUR klines (5m taker delta = 2 * taker_buy_base - volume, BTC; CVD = running sum from 13:00Z, anchor OURS; chart CVD/net delta are CoinGlass quantities and are not reproduced)")
bars = resample(5, ms("15:25")); cvd = 0.0
for e in bars:
    if e[0] < ms("13:00"): continue
    dl = 2 * e[6] - e[5]; cvd += dl
    if ms("13:25") <= e[0] <= ms("14:25") or e[0] in (ms("14:45"), ms("15:05"), ms("15:20")):
        print(f"{hm(e[0])} C{e[4]:.1f} vol {e[5]:.0f} taker delta {dl:+.0f} | CVD from 13:00 {cvd:+.0f}{' (forming)' if e[7] < 5 else ''}")
