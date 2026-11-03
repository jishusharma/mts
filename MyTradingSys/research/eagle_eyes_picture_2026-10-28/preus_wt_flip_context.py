"""Operator 11-03 13:00Z: "price is bouncing before the US open; 1h/30m WaveTrend flipping up, 4h/6h/1D still down; Monday was a down day.
Local bottom, macro bottom, or nothing? What can we expect in this session and this week?"
Three base rates, 1m Binance klines 2022-01-01..2025-06-30 (HOLDOUT from 2025-07-01 sealed). Descriptive, no fees, no orders.
WT 10/21/4, bands +-53: SOURCED (LazyBear). Everything else OURS.
A. At 13:00Z: 1h WT crossed up within the last 4 closed bars from below -30, 4h WT bearish (wt1<wt2), last closed 1D wt1 < -53,
   price above the 00Z open. Outcomes in the US window 13:00-21:00Z: overnight (00-13Z) high or low taken first; 21Z close vs 13Z; max up/down.
B. Tuesday 13:00Z after a red Monday, Tuesday price above its open: Tue close, Fri close vs 13Z; Monday low broken by Friday; a daily close back above the week open by Friday.
C. Last closed 1D bar has wt1 < -53, falling, wt1<wt2 (Monday's state): next 5/10/20 days make a lower low than that bar? max down / max up from its close.
Usage: python preus_wt_flip_context.py   (reads F:/MTS/data/tom_raw/klines)"""
import glob, csv, collections, statistics as st, datetime as dt
END = dt.date(2025, 7, 1)
k = {}
for f in sorted(glob.glob('F:/MTS/data/tom_raw/klines/BTCUSDT-1m-*.csv')):
    for r in csv.reader(open(f)):
        if r[0] == 'open_time': continue
        t = int(r[0]); t = t // 1000 if t > 1e14 else t; t //= 1000
        if dt.datetime.fromtimestamp(t, dt.timezone.utc).date() >= END: break
        k[t] = (float(r[1]), float(r[2]), float(r[3]), float(r[4]))


def bars(sec):
    out = {}
    for t0 in range(min(k) // sec * sec, max(k), sec):
        m = [k[t] for t in range(t0, t0 + sec, 60) if t in k]
        if len(m) < sec // 60 * 0.9: continue
        out[t0] = (m[0][0], max(x[1] for x in m), min(x[2] for x in m), m[-1][3])
    return out


def ema(xs, n):
    a = 2 / (n + 1); o = [xs[0]]
    for x in xs[1:]: o.append(o[-1] + a * (x - o[-1]))
    return o


def wt(seq):
    ap = [(x[1] + x[2] + x[3]) / 3 for x in seq]; esa = ema(ap, 10); d = ema([abs(a - e) for a, e in zip(ap, esa)], 10)
    w1 = ema([(a - e) / (0.015 * dd) if dd else 0 for a, e, dd in zip(ap, esa, d)], 21)
    w2 = [None] * 3 + [sum(w1[i - 3:i + 1]) / 4 for i in range(3, len(w1))]
    return w1, w2


H1, H4, D1 = bars(3600), bars(14400), bars(86400)
t1, t4, td = sorted(H1), sorted(H4), sorted(D1)
w1h, w2h = wt([H1[t] for t in t1]); w14, w24 = wt([H4[t] for t in t4]); w1d, w2d = wt([D1[t] for t in td])
i1 = {t: i for i, t in enumerate(t1)}; i4 = {t: i for i, t in enumerate(t4)}; idd = {t: i for i, t in enumerate(td)}


def rep(name, xs, keys):
    n = len(xs)
    if n < 5: print('%-46s n=%d' % (name, n)); return
    s = '%-46s n=%4d' % (name, n)
    for kk, lab in keys:
        v = [x[kk] for x in xs if x[kk] is not None]
        if not v: continue
        if isinstance(v[0], bool) or kk == 'first':
            if kk == 'first':
                c = collections.Counter(v); s += '  H first %2.0f%% L first %2.0f%% neither %2.0f%%' % (100 * c['H'] / n, 100 * c['L'] / n, 100 * c[None] / n)
            else: s += '  %s %2.0f%%' % (lab, 100 * sum(v) / len(v))
        else: s += '  %s med %+.2f%% (up %2.0f%%)' % (lab, 100 * st.median(v), 100 * sum(x > 0 for x in v) / len(v))
    print(s)


# ---------- A ----------
A = []; Abase = []
for day in td:
    t13 = day + 13 * 3600
    if t13 not in k or t13 - 3600 not in i1 or day - 86400 not in idd: continue
    ih = i1[t13 - 3600]  # last closed 1h bar (12:00-13:00)
    if ih < 30: continue
    crossed = None
    for j in range(ih, ih - 4, -1):
        if w2h[j] is None or w2h[j - 1] is None: break
        if w1h[j] > w2h[j] and w1h[j - 1] <= w2h[j - 1]: crossed = j; break
    i4b = i4.get(t13 - 3600 * 1 - (t13 % 14400 - 3600) if False else (t13 // 14400) * 14400 - 14400)  # last closed 4h bar (08-12Z)
    if i4b is None or w24[i4b] is None: continue
    idb = idd[day - 86400]
    if w2d[idb] is None: continue
    p13 = k[t13][0]; p0 = D1[day][0]
    ov = [k[t] for t in range(day, t13, 60) if t in k]; us = [(t, k[t]) for t in range(t13, day + 21 * 3600, 60) if t in k]
    if len(ov) < 700 or len(us) < 420: continue
    oh = max(x[1] for x in ov); ol = min(x[2] for x in ov)
    first = None; mx = mn = 0
    for _, b in us:
        mx = max(mx, b[1] / p13 - 1); mn = min(mn, b[2] / p13 - 1)
        if first is None:
            if b[1] > oh: first = 'H'
            elif b[2] < ol: first = 'L'
    nd = D1.get(day + 86400)
    rec = dict(first=first, ret=us[-1][1][3] / p13 - 1, mx=mx, mn=mn, nxt=(nd[3] / p13 - 1) if nd else None,
               d1os=w1d[idb] < -53, h4bear=w14[i4b] < w24[i4b], above=p13 > p0,
               flip=crossed is not None and w1h[crossed - 1] < -30 and w1h[ih] > w2h[ih])
    Abase.append(rec)
    if rec['flip'] and rec['h4bear'] and rec['d1os'] and rec['above']: A.append(rec)
K = [('first', ''), ('ret', '21Z vs 13Z'), ('mx', 'max up'), ('mn', 'max dn'), ('nxt', 'next day close')]
print('A. US window after a 1h WT flip up at 13Z')
rep('all days', Abase, K)
rep('1h flip up from <-30 (any higher TF)', [x for x in Abase if x['flip']], K)
rep('  + 4h WT bear', [x for x in Abase if x['flip'] and x['h4bear']], K)
rep('  + 4h bear + 1D wt1<-53', [x for x in Abase if x['flip'] and x['h4bear'] and x['d1os']], K)
rep('  + above 00Z open (TODAY)', A, K)
rep('1D wt1<-53 at 13Z, any lower TF', [x for x in Abase if x['d1os']], K)
rep('1D wt1<-53, 1h NOT flipped', [x for x in Abase if x['d1os'] and not x['flip']], K)

# ---------- B ----------
B = []; Ball = []
for day in td:
    d = dt.datetime.fromtimestamp(day, dt.timezone.utc).date()
    if d.weekday() != 1: continue
    mon = day - 86400; t13 = day + 13 * 3600
    if mon not in D1 or t13 not in k: continue
    wk = [D1.get(day + 86400 * j) for j in range(0, 4)]
    if any(x is None for x in wk): continue
    p13 = k[t13][0]; wo = D1[mon][0]
    rec = dict(redmon=D1[mon][3] < D1[mon][0], above=p13 > D1[day][0],
               tue=D1[day][3] / p13 - 1, fri=wk[3][3] / p13 - 1,
               monlow=min(x[2] for x in wk) < D1[mon][2], retake=any(x[3] > wo for x in wk),
               wkmx=max(x[1] for x in wk) / p13 - 1, wkmn=min(x[2] for x in wk) / p13 - 1)
    Ball.append(rec)
    if rec['redmon'] and rec['above']: B.append(rec)
KB = [('tue', 'Tue close'), ('fri', 'Fri close'), ('monlow', 'Mon low broken by Fri'), ('retake', 'close above week open by Fri'), ('wkmx', 'max up to Fri'), ('wkmn', 'max dn to Fri')]
print('\nB. Tuesday 13Z, week shape')
rep('all Tuesdays', Ball, KB)
rep('red Monday', [x for x in Ball if x['redmon']], KB)
rep('red Monday + Tue above its open (TODAY)', B, KB)
rep('red Monday + Tue below its open', [x for x in Ball if x['redmon'] and not x['above']], KB)
rep('green Monday', [x for x in Ball if not x['redmon']], KB)

# ---------- C ----------
C = []; Call = []
for i in range(30, len(td) - 21):
    if w2d[i] is None: continue
    t = td[i]; b = D1[t]; nxt = [D1[td[j]] for j in range(i + 1, i + 21)]
    rec = dict(os=w1d[i] < -53 and w1d[i] < w1d[i - 1] and w1d[i] < w2d[i],
               ll5=min(x[2] for x in nxt[:5]) < b[2], ll10=min(x[2] for x in nxt[:10]) < b[2], ll20=min(x[2] for x in nxt) < b[2],
               mn20=min(x[2] for x in nxt) / b[3] - 1, mx20=max(x[1] for x in nxt) / b[3] - 1, r5=nxt[4][3] / b[3] - 1, r20=nxt[-1][3] / b[3] - 1,
               cross=next((j for j in range(1, 21) if w1d[i + j] > w2d[i + j]), None))
    Call.append(rec)
    if rec['os']: C.append(rec)
KC = [('ll5', 'lower low in 5d'), ('ll10', 'in 10d'), ('ll20', 'in 20d'), ('mn20', 'max dn 20d'), ('mx20', 'max up 20d'), ('r5', '5d ret'), ('r20', '20d ret')]
print('\nC. 1D WT oversold and still falling (last closed day)')
rep('all days', Call, KC)
rep('1D wt1<-53 falling, wt1<wt2 (TODAY)', C, KC)
cr = [x['cross'] for x in C if x['cross']]
print('   days until the 1D WT bull cross: median %d, 75%% within %d, none within 20d %.0f%%' % (st.median(cr), sorted(cr)[int(0.75 * len(cr))], 100 * (len(C) - len(cr)) / len(C)))
# the low vs the cross: was the lowest low before the cross made within the 3 days before it?
lows = []
for i in range(30, len(td) - 21):
    if w2d[i] is None or w2d[i - 1] is None: continue
    if w1d[i] > w2d[i] and w1d[i - 1] <= w2d[i - 1] and w1d[i - 1] < -53:
        seg = [D1[td[j]][2] for j in range(i - 10, i + 1)]; fwd = [D1[td[j]][2] for j in range(i + 1, i + 21)]
        lows.append(min(fwd) < min(seg))
print('   1D WT bull cross from <-53 (n=%d): the 10-day low before the cross is broken within 20 days %.0f%%' % (len(lows), 100 * sum(lows) / len(lows)))
