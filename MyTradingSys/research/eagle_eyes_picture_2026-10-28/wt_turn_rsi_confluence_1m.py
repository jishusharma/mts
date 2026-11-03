"""Operator 11-03 13:56Z (1m TradingView shot 954c669106bd): "make sure we can identify wavetrend points like this using wavetrend
basics and RSI confluence - divergence + support on RSI MA and wavetrend shift in momentum - MTS should be able to identify them".
The circled point: WaveTrend cross up from below -60 at 08:43Z, RSI turning off 30, then a 1.5 % rally.

Base rates on 1m Binance klines 2023-01-01..2025-06-30 (HOLDOUT from 2025-07-01 sealed). Descriptive, no fees, no orders.
WT 10/21/4 bands +-53/60: SOURCED (LazyBear). RSI14 Wilder + SMA14: SOURCED (his chart). Everything else OURS:
  event   = wt1 crosses above wt2 (first bar strictly above after being strictly below) with wt1 at the cross < -53
  rsi_low = min RSI over the 5 bars up to the cross < 35
  rsi_ma  = RSI closes above its SMA14 within 3 bars after the cross (support on the RSI MA)
  div     = bullish divergence, live_aid rule: price low of the 15 bars up to the cross < low of the 15 before, and wt1 low of the
            last 15 > wt1 low of the 15 before
Outcomes from the close of the cross bar: +0.30 % reached before -0.30 % within 60 bars (TARGET FIRST), max up / max down in 60 bars,
return at 30 and 60 bars. Mirror for the bear cross (wt1 > 53) with the signs flipped.
Usage: python wt_turn_rsi_confluence_1m.py   (reads F:/MTS/data/tom_raw/klines)"""
import glob, csv, datetime as dt, statistics as st

START, END = dt.date(2023, 1, 1), dt.date(2025, 7, 1)
T, O, H, L, C = [], [], [], [], []
for f in sorted(glob.glob('F:/MTS/data/tom_raw/klines/BTCUSDT-1m-*.csv')):
    for r in csv.reader(open(f)):
        if r[0] == 'open_time': continue
        t = int(r[0]); t = t // 1000 if t > 1e14 else t; t //= 1000
        d = dt.datetime.fromtimestamp(t, dt.timezone.utc).date()
        if d < START: continue
        if d >= END: break
        T.append(t); O.append(float(r[1])); H.append(float(r[2])); L.append(float(r[3])); C.append(float(r[4]))
n = len(C); print('bars', n, dt.datetime.fromtimestamp(T[0], dt.timezone.utc).date(), dt.datetime.fromtimestamp(T[-1], dt.timezone.utc).date())


def ema(xs, k):
    a = 2 / (k + 1); o = [xs[0]]
    for x in xs[1:]: o.append(o[-1] + a * (x - o[-1]))
    return o


ap = [(h + l + c) / 3 for h, l, c in zip(H, L, C)]; esa = ema(ap, 10); dd = ema([abs(a - e) for a, e in zip(ap, esa)], 10)
wt1 = ema([(a - e) / (0.015 * d) if d else 0 for a, e, d in zip(ap, esa, dd)], 21)
wt2 = [None] * 3 + [(wt1[i - 3] + wt1[i - 2] + wt1[i - 1] + wt1[i]) / 4 for i in range(3, n)]
# RSI14 Wilder
rsi = [None] * n; ag = al = 0.0
for i in range(1, n):
    ch = C[i] - C[i - 1]; g = max(ch, 0); lo = max(-ch, 0)
    if i <= 14: ag += g / 14; al += lo / 14
    else: ag = (ag * 13 + g) / 14; al = (al * 13 + lo) / 14
    if i >= 14: rsi[i] = 100 - 100 / (1 + ag / al) if al else 100
rs = [None] * n  # SMA14 of RSI (the blue line on his chart)
for i in range(27, n): rs[i] = sum(rsi[i - 13:i + 1]) / 14

STEP, HOR = 0.003, 60


def outcome(i, sd):
    p = C[i]; first = None; mx = mn = 0
    for j in range(i + 1, min(n, i + HOR + 1)):
        up = sd * (H[j] / p - 1) if sd > 0 else sd * (L[j] / p - 1)
        dn = sd * (L[j] / p - 1) if sd > 0 else sd * (H[j] / p - 1)
        mx = max(mx, up); mn = min(mn, dn)
        if first is None:
            if up >= STEP and dn <= -STEP: first = 'both'
            elif up >= STEP: first = 'T'
            elif dn <= -STEP: first = 'S'
    r30 = sd * (C[min(n - 1, i + 30)] / p - 1); r60 = sd * (C[min(n - 1, i + 60)] / p - 1)
    return first, mx, mn, r30, r60


rows = []
side = 0
for i in range(100, n - HOR - 1):
    if wt2[i] is None: continue
    s_now = 1 if wt1[i] > wt2[i] else -1 if wt1[i] < wt2[i] else 0
    if s_now == 0: continue
    if side and s_now != side:
        sd = s_now
        if (sd > 0 and wt1[i] < -53) or (sd < 0 and wt1[i] > 53):
            # confluences (direction-aware)
            rwin = [x for x in rsi[i - 4:i + 1] if x is not None]
            rsi_ext = (min(rwin) < 35) if sd > 0 else (max(rwin) > 65)
            rsi_ma = any(rs[j] is not None and ((rsi[j] > rs[j]) if sd > 0 else (rsi[j] < rs[j])) for j in range(i, min(n, i + 4)))
            a, b = i - 29, i - 14
            if sd > 0: div = min(L[b:i + 1]) < min(L[a:b]) and min(wt1[b:i + 1]) > min(wt1[a:b])
            else: div = max(H[b:i + 1]) > max(H[a:b]) and max(wt1[b:i + 1]) < max(wt1[a:b])
            f, mx, mn, r30, r60 = outcome(i, sd)
            rows.append(dict(sd=sd, ext=rsi_ext, ma=rsi_ma, div=div, first=f, mx=mx, mn=mn, r30=r30, r60=r60))
    side = s_now


def rep(name, xs):
    k = len(xs)
    if k < 20: print('%-52s n=%d' % (name, k)); return
    t = sum(x['first'] == 'T' for x in xs); s_ = sum(x['first'] == 'S' for x in xs); b = sum(x['first'] == 'both' for x in xs)
    print('%-52s n=%6d  target first %4.1f%%  stop first %4.1f%%  both %3.1f%%  neither %4.1f%%  max up %.2f%%  max dn %.2f%%  r30 %+.3f%% (up %2.0f%%)  r60 %+.3f%%' % (
        name, k, 100 * t / k, 100 * s_ / k, 100 * b / k, 100 * (k - t - s_ - b) / k, 100 * st.median(x['mx'] for x in xs), 100 * st.median(x['mn'] for x in xs),
        100 * st.median(x['r30'] for x in xs), 100 * sum(x['r30'] > 0 for x in xs) / k, 100 * st.median(x['r60'] for x in xs)))


for sd, lab in ((1, 'BULL: wt cross up from < -53'), (-1, 'BEAR: wt cross down from > 53')):
    X = [x for x in rows if x['sd'] == sd]
    print('\n' + lab + '  (target = %.1f%% in the cross direction before %.1f%% against, %d bars)' % (100 * STEP, 100 * STEP, HOR))
    rep('all crosses', X)
    rep('+ RSI extreme (5-bar min<35 / max>65)', [x for x in X if x['ext']])
    rep('+ RSI crosses its SMA14 within 3 bars', [x for x in X if x['ma']])
    rep('+ WT divergence (15 vs 15 bars)', [x for x in X if x['div']])
    rep('+ RSI extreme + RSI MA cross', [x for x in X if x['ext'] and x['ma']])
    rep('+ RSI extreme + divergence', [x for x in X if x['ext'] and x['div']])
    rep('+ all three (HIS POINT)', [x for x in X if x['ext'] and x['ma'] and x['div']])
    rep('none of the three', [x for x in X if not x['ext'] and not x['ma'] and not x['div']])
