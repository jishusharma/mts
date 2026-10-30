"""Operator shot 0a7af8773801 (2026-10-30, Bitstamp BTCUSD 30m, WT_CROSS_LB): he walks the 10-22..10-30 30m WaveTrend
sequence (OB-to-OS falls while price falls, centre crosses up that price ignores, OB divergences 10-27/28, 82k top on
10-29 then WT straight to OS, now back near 0 with a red cross) and asks what WT on 30m tells, 'the hidden stuff'.

Definitions fixed before the first run (descriptive, no fees):
- WaveTrend 10/21/4 on hlc3, levels +/-53 (SOURCED: LazyBear, PARITY_CONTRACT.md). Everything else OURS.
- Data: Binance BTCUSDT perp 1m archive rolled to 30m and 4h. DEV 2022-01..2024-06 only: the WT validation window
  (2024-07+) stays unread, as in wavetrend_2026-10-17/PRE_REG.md.
- Context = wt1 sign of the last CLOSED 4h bar at the 30m event close (4h down / 4h up).
- Events on 30m, at the close of the confirming bar (each type: skip 8 bars after one):
  T1 top cross: wt1 crosses below wt2 with wt1[t-1] >= 53.       T2 bottom cross: up-cross with wt1[t-1] <= -53.
  T3 bearish divergence: confirmed wt1 pivot high (2 bars each side) >= 53, the previous wt1 pivot high >= 53 within
     48 bars, second WT peak >= 3 lower, price high around the second peak above the first (bars p-2..p+2).
     Confirmed at p+2.                                              T4 bullish divergence: mirror at <= -53.
  T5 centre cross up (wt1 < 0 to > 0).                             T6 centre cross down.
  T7 centre rejection from below: down-cross with -25 < wt1 < 0 and wt1 <= -53 within the last 24 bars (now, 10-30).
  T8 centre rejection from above: mirror.
  T9 fast top-to-bottom: wt1 <= -53 and max wt1 of the last 8 bars >= 53 (the 82k -> 77k move).
  T9b (added after run 1, T9 had n=0; the 10-29 swing took about 16 bars): same with the last 16 bars.
- Outcomes from the event close: up after 4 h (8 bars) and 12 h (24 bars); which first within 24 h, +1% or -1%;
  mean 12 h return %. Baseline: every 30m bar with the same 4h context.
"""
import glob
import numpy as np, pandas as pd

def wt(h, l, c):
    ap = pd.Series((h + l + c) / 3)
    esa = ap.ewm(span=10, adjust=False).mean()
    d = (ap - esa).abs().ewm(span=10, adjust=False).mean()
    w1 = ((ap - esa) / (0.015 * d)).ewm(span=21, adjust=False).mean()
    return w1.to_numpy(), w1.rolling(4).mean().to_numpy()

def bars(k, sec):
    k = k.assign(g=k.t // sec)
    b = k.groupby('g').agg(h=('h', 'max'), l=('l', 'min'), c=('c', 'last'), n=('c', 'size')).reset_index()
    return b[b.n == sec // 60].reset_index(drop=True)

def load():
    fs = [f for f in sorted(glob.glob('F:/MTS/data/tom_raw/klines/BTCUSDT-1m-*.csv')) if f[-11:-4] <= '2024-06']
    k = pd.concat([pd.read_csv(f, usecols=[0, 2, 3, 4]) for f in fs], ignore_index=True)
    k.columns = ['t', 'h', 'l', 'c']
    k['t'] = np.where(k.t > 1e14, k.t // 1000, k.t) // 1000
    return k.drop_duplicates('t').sort_values('t')

def run():
    k = load(); b = bars(k, 1800); f = bars(k, 14400)
    w4 = pd.Series(wt(*(f[x].to_numpy(float) for x in 'hlc'))[0], index=f.g)
    g = b.g.to_numpy(); h, l, c = (b[x].to_numpy(float) for x in 'hlc')
    w1, w2 = wt(h, l, c)
    ctx4 = pd.Series((g + 1) * 1800 // 14400 - 1).map(w4).to_numpy()
    N = len(c); ok = np.zeros(N, bool)
    ok[60:N - 49] = (g[60 + 48:N - 1] - g[60:N - 49]) == 48
    ok &= ~np.isnan(ctx4)
    up = (w1 > w2) & ~(np.roll(w1 > w2, 1)); dn = (w1 < w2) & ~(np.roll(w1 < w2, 1))
    ph = [p for p in range(2, N - 2) if w1[p] == w1[p - 2:p + 3].max()]
    pl = [p for p in range(2, N - 2) if w1[p] == w1[p - 2:p + 3].min()]
    ev = {x: np.zeros(N, bool) for x in ['T1', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'T8', 'T9', 'T9b']}
    for t in range(1, N):
        ev['T1'][t] = dn[t] and w1[t - 1] >= 53
        ev['T2'][t] = up[t] and w1[t - 1] <= -53
        ev['T5'][t] = w1[t - 1] < 0 < w1[t]
        ev['T6'][t] = w1[t - 1] > 0 > w1[t]
        ev['T7'][t] = dn[t] and -25 < w1[t] < 0 and w1[max(0, t - 24):t].min() <= -53
        ev['T8'][t] = up[t] and 0 < w1[t] < 25 and w1[max(0, t - 24):t].max() >= 53
        ev['T9'][t] = w1[t] <= -53 and w1[max(0, t - 8):t].max() >= 53
        ev['T9b'][t] = w1[t] <= -53 and w1[max(0, t - 16):t].max() >= 53
    for piv, key, s in [(ph, 'T3', 1), (pl, 'T4', -1)]:
        for a, p in zip(piv, piv[1:]):
            if p + 2 >= N or p - a > 48 or s * w1[a] < 53 or s * w1[p] < 53 or s * (w1[a] - w1[p]) < 3: continue
            pa = h[a - 2:a + 3].max() if s > 0 else -l[a - 2:a + 3].min()
            pp = h[p - 2:p + 3].max() if s > 0 else -l[p - 2:p + 3].min()
            if pp > pa: ev[key][p + 2] = True
    def outc(t):
        u, d = c[t] * 1.01, c[t] * 0.99; first = 'none'
        for j in range(t + 1, t + 49):
            if h[j] >= u and l[j] <= d: first = 'both'; break
            if h[j] >= u: first = 'up'; break
            if l[j] <= d: first = 'down'; break
        return dict(up4=c[t + 8] > c[t], up12=c[t + 24] > c[t], first=first, r12=(c[t + 24] / c[t] - 1) * 100)
    rows = []
    for name, m in ev.items():
        last = -99
        for t in np.flatnonzero(m & ok):
            if t - last < 8: continue
            last = t; rows.append(dict(ev=name, ctx='4h down' if ctx4[t] < 0 else '4h up', **outc(t)))
    rng = np.random.default_rng(7)
    for t in rng.choice(np.flatnonzero(ok), 20000, replace=False):
        rows.append(dict(ev='BASE', ctx='4h down' if ctx4[t] < 0 else '4h up', **outc(t)))
    R = pd.DataFrame(rows)
    agg = dict(n=('up4', 'size'), up4h=('up4', 'mean'), up12h=('up12', 'mean'),
               up1_first=('first', lambda s: (s == 'up').mean()), dn1_first=('first', lambda s: (s == 'down').mean()),
               mean_r12=('r12', 'mean'))
    print(f'30m bars {N} (DEV 2022-01..2024-06)')
    print('\n== all contexts'); print(R.groupby('ev').agg(**agg).round(3).to_string())
    print('\n== by 4h WT context'); print(R.groupby(['ev', 'ctx']).agg(**agg).round(3).to_string())
    # full swing: after a top cross, how often does wt1 reach the bottom zone within 48 bars, and what did price do
    sw = []
    for t in np.flatnonzero(ev['T1'] & ok):
        j = next((j for j in range(t + 1, t + 49) if w1[j] <= -53), None)
        sw.append(dict(ctx='4h down' if ctx4[t] < 0 else '4h up', reached=j is not None,
                       r_at=(c[j] / c[t] - 1) * 100 if j else np.nan, bars=j - t if j else np.nan))
    S = pd.DataFrame(sw)
    print('\n== after a top cross (T1): wt1 reaches <= -53 within 24 h')
    print(S.groupby('ctx').agg(n=('reached', 'size'), reached=('reached', 'mean'), med_bars=('bars', 'median'),
                               med_price_move_pct=('r_at', 'median')).round(3).to_string())

if __name__ == '__main__':
    run()
