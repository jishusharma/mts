"""Operator shot 97857881eb00 (2026-10-30 00:15Z): BTC 5m cascade 80.4k -> 77.65k, closes under the lower BB,
RSI 19, OI rising while CVD falls. He asks: which supports, what do the layers say, can MTS see a momentum shift,
does it anticipate bounces accurately? 'Start testing it.'

Definitions fixed before the first run (all OURS; descriptive, no fees; DEV 2022-2025, 1m kline archive + metrics OI):
- 5m bars. BB(20, 2, population std). RSI14 Wilder.
- TRIGGER (the shot's state): close < lower BB, RSI <= 25, close >= 2.5% under the 24 h high. After one, skip 48 bars.
- Context at the trigger:
  OI over the last 60 min: up >= +0.25% (shorts pressing), down <= -0.25% (longs flushed), else flat.
  Round level: close within 0.3% of a 1,000 multiple. Prior-day low: close already under the prior UTC day's low.
- Momentum-shift signals, each at its FIRST bar within 24 bars (2 h) after the trigger:
  S1 back-inside: first close back above the lower band.
  S2 rsi30: RSI crosses back above 30.
  S3 divergence: a new low since the trigger with RSI >= 5 points above the lowest RSI since the trigger.
  S4 buyers: a green bar with taker delta share >= +0.20.
  S5 reclaim: close above the high of the bar that made the lowest low since the trigger (lowest bar >= 2 bars back).
  RANDOM: one random bar in the same 24 (seeded): the base rate for 'some time after the trigger'.
- Outcomes from that bar's close: which first within 4 h, +0.5% or -0.5%; close 60 min later up;
  trigger low broken later (within 4 h); max up within 4 h >= 1%.
"""
import glob
import numpy as np, pandas as pd

def load():
    m = pd.concat([pd.read_csv(f, usecols=[0, 2]) for f in sorted(glob.glob('F:/MTS/data/binance_metrics/BTCUSDT-metrics-202[2-5]-*.csv'))])
    m.columns = ['ts', 'oi']
    m['g'] = ((pd.to_datetime(m.ts) - pd.Timestamp(0)).dt.total_seconds() // 300).astype('int64') - 1
    fs = [f for f in sorted(glob.glob('F:/MTS/data/tom_raw/klines/BTCUSDT-1m-*.csv')) if '2026' not in f]
    k = pd.concat([pd.read_csv(f, usecols=[0, 1, 2, 3, 4, 5, 9]) for f in fs], ignore_index=True)
    k.columns = ['t', 'o', 'h', 'l', 'c', 'v', 'tb']
    k['t'] = np.where(k.t > 1e14, k.t // 1000, k.t) // 1000
    k = k.drop_duplicates('t').sort_values('t'); k['g'] = k.t // 300
    b = k.groupby('g').agg(o=('o', 'first'), h=('h', 'max'), l=('l', 'min'), c=('c', 'last'), v=('v', 'sum'),
                           tb=('tb', 'sum'), n=('c', 'size'))
    b = b.join(m.drop_duplicates('g').set_index('g')[['oi']], how='left').reset_index()
    return b[b.n == 5].reset_index(drop=True)

def first_hit(h, l, c0, j0, up=0.005):
    u, d = c0 * (1 + up), c0 * (1 - up)
    for j in range(j0 + 1, j0 + 49):
        a, z = h[j] >= u, l[j] <= d
        if a and z: return 'both'
        if a: return 'up'
        if z: return 'down'
    return 'none'

def run():
    b = load(); g = b.g.to_numpy()
    o, h, l, c, v, tb, oi = (b[x].to_numpy(float) for x in ['o', 'h', 'l', 'c', 'v', 'tb', 'oi'])
    cs = pd.Series(c); mid = cs.rolling(20).mean(); sd = cs.rolling(20).std(ddof=0)
    lb = (mid - 2 * sd).to_numpy()
    dl = cs.diff(); up = dl.clip(lower=0).ewm(alpha=1 / 14, adjust=False).mean(); dn = (-dl.clip(upper=0)).ewm(alpha=1 / 14, adjust=False).mean()
    rsi = (100 - 100 / (1 + up / dn)).to_numpy()
    hi24 = pd.Series(h).rolling(288).max().to_numpy()
    day = g * 300 // 86400
    dlow = pd.Series(l).groupby(day).min(); pdl = pd.Series(day - 1).map(dlow).to_numpy()
    ds = np.where(v > 0, (2 * tb - v) / v, 0)
    yr = pd.to_datetime(g * 300, unit='s').year.to_numpy()
    rng = np.random.default_rng(7)
    ev, sig = [], []
    i = 300; N = len(c)
    while i < N - 75:
        if not (c[i] < lb[i] and rsi[i] <= 25 and c[i] <= hi24[i] * 0.975) or g[i + 72] - g[i - 12] != 84:
            i += 1; continue
        doi = oi[i] / oi[i - 12] - 1 if oi[i] > 0 and oi[i - 12] > 0 else np.nan
        ctx = dict(yr=yr[i], oi='up' if doi >= .0025 else 'down' if doi <= -.0025 else 'flat' if doi == doi else 'na',
                   rnd=abs(c[i] / 1000 - round(c[i] / 1000)) * 1000 / c[i] < .003, pdl=c[i] < pdl[i])
        lowi = l[i]
        def out(j):
            return dict(first=first_hit(h, l, c[j], j), up60=c[j + 12] > c[j], broke=l[j + 1:j + 49].min() < min(lowi, l[i:j + 1].min()),
                        mu1=h[j + 1:j + 49].max() >= c[j] * 1.01)
        ev.append(dict(ctx, **out(i)))
        fired = {}; lo, lo_j, rlo = l[i], i, rsi[i]
        for j in range(i + 1, i + 25):
            if 'S1' not in fired and c[j] > lb[j]: fired['S1'] = j
            if 'S2' not in fired and rsi[j] > 30 and rsi[j - 1] <= 30: fired['S2'] = j
            if 'S3' not in fired and l[j] < lo and rsi[j] >= rlo + 5: fired['S3'] = j
            if 'S4' not in fired and c[j] > o[j] and ds[j] >= .20: fired['S4'] = j
            if 'S5' not in fired and j - lo_j >= 2 and c[j] > h[lo_j]: fired['S5'] = j
            if l[j] < lo: lo, lo_j = l[j], j
            rlo = min(rlo, rsi[j])
        fired['RANDOM'] = i + int(rng.integers(1, 25))
        for s, j in fired.items():
            sig.append(dict(ctx, sig=s, lag=j - i, **out(j)))
        i += 48
    E, S = pd.DataFrame(ev), pd.DataFrame(sig)
    agg = dict(n=('up60', 'size'), up_first=('first', lambda s: (s == 'up').mean()), down_first=('first', lambda s: (s == 'down').mean()),
               up60=('up60', 'mean'), low_broken=('broke', 'mean'), max_up_1pct=('mu1', 'mean'))
    print(f'triggers {len(E)}')
    print('\n== AT THE TRIGGER (the shot state) =='); print(E.agg(**{k: v for k, v in agg.items()}).T.round(3).to_string() if False else E.assign(all='all').groupby('all').agg(**agg).round(3).to_string())
    for col in ['oi', 'rnd', 'pdl', 'yr']:
        print(f'\n-- by {col}'); print(E.groupby(col).agg(**agg).round(3).to_string())
    print('\n== MOMENTUM-SHIFT SIGNALS (first firing within 2 h) ==')
    t = S.groupby('sig').agg(**agg, med_lag=('lag', 'median')); t['fired_share'] = t.n / len(E)
    print(t.round(3).to_string())
    print('\n-- signals by year: up_first'); print(S.pivot_table(index='sig', columns='yr', values='first', aggfunc=lambda s: (s == 'up').mean()).round(3).to_string())
    print('\n-- signals x OI: up_first (n)')
    print(S.groupby(['sig', 'oi']).agg(n=('up60', 'size'), up_first=('first', lambda s: (s == 'up').mean())).round(3).unstack().to_string())

if __name__ == '__main__':
    run()
