"""Operator question 2026-10-30 (shot 072bbb83f7b1): open interest is rising while price drifts sideways; which side
are the new positions on, and which way does price go next?

OI is side-neutral: every new contract has one long and one short. What can be read is who was the AGGRESSOR
(market orders, the taker delta) and which accounts grew (the top-trader long/short ratio).
Definitions fixed before the first run (all OURS; descriptive, no fees; DEV 2022-2025 only):
- 5m grid. OI = sum_open_interest (Binance metrics archive); price, taker delta from the 1m kline archive.
- Window = last 30 min (6 bars). dOI, dP = % change; ds = taker delta share (2*takerbuy - vol) / vol over the window.
- OI up: dOI >= +0.25%; OI down: dOI <= -0.25%; price flat: |dP| <= 0.15%, up / down beyond that.
- Outcomes from the window end: close 60 min and 4 h later up or down; which comes first within 4 h, +0.5% or -0.5%.
- Events do not overlap (after one, skip 6 bars).
- Cycle splits (operator 10-30, 'every time frame is different as there are cycles'): calendar year; price above or below its 20-day mean.
"""
import glob, sys
import numpy as np, pandas as pd

def load():
    m = pd.concat([pd.read_csv(f, usecols=[0, 2, 5]) for f in sorted(glob.glob('F:/MTS/data/binance_metrics/BTCUSDT-metrics-202[2-5]-*.csv'))])
    m.columns = ['ts', 'oi', 'tt']
    m['g'] = ((pd.to_datetime(m.ts) - pd.Timestamp(0)).dt.total_seconds() // 300).astype('int64')
    fs = [f for f in sorted(glob.glob('F:/MTS/data/tom_raw/klines/BTCUSDT-1m-*.csv')) if '2026' not in f]
    k = pd.concat([pd.read_csv(f, usecols=[0, 2, 3, 4, 5, 9]) for f in fs], ignore_index=True)
    k.columns = ['t', 'h', 'l', 'c', 'v', 'tb']
    k['t'] = np.where(k.t > 1e14, k.t // 1000, k.t) // 1000
    k = k.drop_duplicates('t'); k['g'] = k.t // 300
    b = k.groupby('g').agg(h=('h', 'max'), l=('l', 'min'), c=('c', 'last'), v=('v', 'sum'), tb=('tb', 'sum'), n=('c', 'size'))
    # metrics stamp = end of the 5m bar; kline group g covers [g, g+1): align OI at g+1 with the bar g close
    m['g'] = m.g - 1
    d = b.join(m.drop_duplicates('g').set_index('g')[['oi', 'tt']], how='inner').reset_index()
    d = d[(d.n == 5) & (d.oi > 0) & (d.v > 0)].reset_index(drop=True)
    return d

def run():
    d = load(); g = d.g.to_numpy(); c, h, l, oi, v, tb, tt = (d[x].to_numpy(float) for x in ['c', 'h', 'l', 'oi', 'v', 'tb', 'tt'])
    ma = pd.Series(c).rolling(288 * 20).mean().to_numpy()  # 20-day mean: the cycle (OURS)
    yr = pd.to_datetime(g * 300, unit='s').year.to_numpy()
    rows = []; i = 6; N = len(c)
    while i < N - 49:
        if g[i + 48] - g[i - 6] != 54:
            i += 1; continue
        dOI = oi[i] / oi[i - 6] - 1; dP = c[i] / c[i - 6] - 1
        ds = (2 * tb[i - 5:i + 1].sum() - v[i - 5:i + 1].sum()) / v[i - 5:i + 1].sum()
        oic = 'up' if dOI >= .0025 else 'down' if dOI <= -.0025 else None
        if oic is None:
            i += 1; continue
        pc = 'flat' if abs(dP) <= .0015 else 'up' if dP > 0 else 'down'
        up, dn = c[i] * 1.005, c[i] * 0.995; first = 'none'
        for j in range(i + 1, i + 49):
            hu, hd = h[j] >= up, l[j] <= dn
            if hu and hd: first = 'both'; break
            if hu: first = 'up'; break
            if hd: first = 'down'; break
        rows.append(dict(year=yr[i], cycle='n/a' if np.isnan(ma[i]) else ('above 20d mean' if c[i] > ma[i] else 'below 20d mean'), oi=oic, price=pc, ds=ds, tt=tt[i] / tt[i - 6] - 1,
                         up60=c[i + 12] > c[i], up240=c[i + 48] > c[i], first=first))
        i += 6
    R = pd.DataFrame(rows)
    R['delta'] = np.where(R.ds <= -.05, 'sellers', np.where(R.ds >= .05, 'buyers', 'mixed'))
    R['top'] = np.where(R.tt > 0.01, 'top longs grew', np.where(R.tt < -0.01, 'top shorts grew', 'top flat'))
    def tab(G):
        t = R.groupby(G).agg(n=('up60', 'size'), up60=('up60', 'mean'), up240=('up240', 'mean'),
                             up_first=('first', lambda s: (s == 'up').mean()), down_first=('first', lambda s: (s == 'down').mean()))
        return t.round(3).to_string()
    print('events', len(R))
    print('\nA. OI x price over the last 30 min'); print(tab(['oi', 'price']))
    for G in ('year', 'cycle'):
        t = R.groupby([G, 'oi', 'price']).up60.agg(['mean', 'size']).unstack(G)
        print(f'\nA-{G}. up 60 min later, by {G}'); print(t.round(3).to_string())
    F = R[(R.oi == 'up') & (R.price == 'flat')]
    R = F
    print('\nB. OI up, price flat: by taker delta in the window'); print(tab(['delta']))
    print('\nC. OI up, price flat: by top-trader long/short ratio change'); print(tab(['top']))
    print('\nD. OI up, price flat: delta x top-trader'); print(tab(['delta', 'top']))

if __name__ == '__main__':
    run()
