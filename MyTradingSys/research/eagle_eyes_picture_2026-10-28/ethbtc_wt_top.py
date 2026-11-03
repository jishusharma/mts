"""Operator 11-03 14:28Z (ETHBTC 4h TradingView shot a1595851438f): "what WaveTrend and Krown analysis says about ETHBTC".
Picture: WT 10/21/4 at the +53/60 band with a cross-down dot, RSI14 above 60 (Krown KR-S03: >60 = uptrend emerging).
Count on synthetic ETHBTC 4h = ETHUSDT/BTCUSDT 1m closes folded to 4h, 2022-01..2024-06 (the F:/MTS/data/tom_raw ETHUSDT archive ends 2024-06, so the 2025-06 END below clips to it; the quoted n=37 / -2.19 % / n=43 / +0.71 % are for that window; on 2022-01..2025-06 the counts differ, see gemini_audits_2026-11-03/eagle_1103_blind_read.md). Events: (a) WT cross down with wt1 > 53,
(b) same with RSI > 60 at the cross (today), (c) RSI closes over 60 after >= 30 bars under it (Krown regime flip). Outcomes: close 12 / 30 / 60 bars later
(2 / 5 / 10 days), max up / max down within 30 bars. Descriptive, no fees."""
import glob, csv, datetime as dt, statistics as st
def load(sym):
    d = {}
    for f in sorted(glob.glob('F:/MTS/data/tom_raw/klines/%s-1m-*.csv' % sym)):
        for r in csv.reader(open(f)):
            if r[0] == 'open_time': continue
            t = int(r[0]); t = t // 1000 if t > 1e14 else t; t //= 1000
            if t % 14400 == 14340: d[t - 14340] = float(r[4])  # last 1m close of each 4h bucket
    return d
E, B = load('ETHUSDT'), load('BTCUSDT')
ks = sorted(k for k in E if k in B and dt.date(2022, 1, 1) <= dt.datetime.fromtimestamp(k, dt.timezone.utc).date() < dt.date(2025, 7, 1))
C = [E[k] / B[k] for k in ks]; n = len(C); print('4h bars', n, dt.datetime.fromtimestamp(ks[0], dt.timezone.utc).date(), dt.datetime.fromtimestamp(ks[-1], dt.timezone.utc).date())
def ema(xs, k):
    a = 2 / (k + 1); o = [xs[0]]
    for x in xs[1:]: o.append(o[-1] + a * (x - o[-1]))
    return o
esa = ema(C, 10); dd = ema([abs(c - e) for c, e in zip(C, esa)], 10)
wt1 = ema([(c - e) / (0.015 * d) if d else 0 for c, e, d in zip(C, esa, dd)], 21)
wt2 = [None] * 3 + [sum(wt1[i - 3:i + 1]) / 4 for i in range(3, n)]
rsi = [None] * n; ag = al = 0.0
for i in range(1, n):
    ch = C[i] - C[i - 1]; g = max(ch, 0); lo = max(-ch, 0)
    if i <= 14: ag += g / 14; al += lo / 14
    else: ag = (ag * 13 + g) / 14; al = (al * 13 + lo) / 14
    if i >= 14: rsi[i] = 100 - 100 / (1 + ag / al) if al else 100
def out(i):
    p = C[i]; w = C[i + 1:i + 31]
    return dict(r12=C[i + 12] / p - 1, r30=C[i + 30] / p - 1, r60=C[min(n - 1, i + 60)] / p - 1, mx=max(w) / p - 1, mn=min(w) / p - 1)
A, Bv, K = [], [], []
side = 0; under = 0
for i in range(60, n - 31):
    s = 1 if wt1[i] > wt2[i] else -1 if wt1[i] < wt2[i] else 0
    if side == 1 and s == -1 and wt1[i] > 53:
        A.append(out(i))
        if rsi[i] > 60: Bv.append(out(i))
    if s: side = s
    if rsi[i] > 60:
        if under >= 30: K.append(out(i))
        under = 0
    else: under += 1
def rep(name, X):
    k = len(X); print('%-48s n=%4d  r2d %+.2f%% (up %2.0f%%)  r5d %+.2f%% (up %2.0f%%)  r10d %+.2f%% (up %2.0f%%)  max up %.2f%%  max dn %.2f%%' % (
        name, k, 100 * st.median(x['r12'] for x in X), 100 * sum(x['r12'] > 0 for x in X) / k, 100 * st.median(x['r30'] for x in X), 100 * sum(x['r30'] > 0 for x in X) / k,
        100 * st.median(x['r60'] for x in X), 100 * sum(x['r60'] > 0 for x in X) / k, 100 * st.median(x['mx'] for x in X), 100 * st.median(x['mn'] for x in X)))
rep('all 4h bars (baseline)', [out(i) for i in range(60, n - 31)])
rep('WT cross down from > 53', A); rep('WT cross down from > 53 AND RSI > 60 (TODAY)', Bv); rep('RSI first close > 60 after >= 5 days under (Krown)', K)
