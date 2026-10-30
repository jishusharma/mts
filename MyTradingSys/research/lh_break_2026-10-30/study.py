"""Operator 2026-10-30: analyst Michael (Pizzino) tracked lower highs and expected a break toward 75k; price reached
76.4k. 'We do not understand what the break can mean.' How far does a support break after lower highs travel?

Definitions fixed before the first run (all OURS; descriptive, no fees; DEV 2022-01..2025-12, 2026 untouched):
- 4h bars from the Binance BTCUSDT perp 1m archive.
- Support S at bar t = lowest low of the previous 60 bars (10 days), t-60..t-1.
- Pivot high = high above the 2 bars each side, usable only once confirmed (2 bars later, so <= t-1).
- LOWER-HIGHS break: close[t] < S, and the confirmed pivot highs in t-60..t-1 that sit above S include >= 3 strictly
  falling ones (the last 3 pivots each lower than the one before). Height H = highest of those pivots - S.
- CONTROL: any other close below S (no lower-high staircase). H = highest high of t-60..t-1 - S.
- Non-overlap: after a break, skip 30 bars (5 days).
- Outcomes over the next 42 bars (7 days), measured below S: max drop reached 0.5 H / 1.0 H / 1.618 H;
  failed break = a close back above S within 6 bars (24 h); median max drop in H units.
"""
import glob
import numpy as np, pandas as pd

def load():
    fs = [f for f in sorted(glob.glob('F:/MTS/data/tom_raw/klines/BTCUSDT-1m-*.csv')) if f[-11:-4] <= '2025-12']
    k = pd.concat([pd.read_csv(f, usecols=[0, 2, 3, 4]) for f in fs], ignore_index=True)
    k.columns = ['t', 'h', 'l', 'c']
    k['t'] = np.where(k.t > 1e14, k.t // 1000, k.t) // 1000
    k = k.drop_duplicates('t').sort_values('t'); k['g'] = k.t // 14400
    b = k.groupby('g').agg(h=('h', 'max'), l=('l', 'min'), c=('c', 'last'), n=('c', 'size')).reset_index()
    return b[b.n == 240].reset_index(drop=True)

def run():
    b = load(); g = b.g.to_numpy(); h, l, c = (b[x].to_numpy(float) for x in 'hlc'); N = len(c)
    piv = np.zeros(N, bool)
    for p in range(2, N - 2):
        piv[p] = h[p] > max(h[p - 2], h[p - 1], h[p + 1], h[p + 2])
    rows = []; t = 60
    while t < N - 42:
        if g[t + 42] - g[t - 60] != 102:
            t += 1; continue
        S = l[t - 60:t].min()
        if not c[t] < S:
            t += 1; continue
        ps = [p for p in range(t - 60, t - 2) if piv[p] and h[p] > S]   # confirmed by t-1
        last3 = [h[p] for p in ps[-3:]]
        lh = len(last3) == 3 and last3[0] > last3[1] > last3[2]
        H = (max(h[p] for p in ps[-3:]) if lh else h[t - 60:t].max()) - S
        drop = (S - l[t + 1:t + 43].min()) / H
        failed = (c[t + 1:t + 7] > S).any()
        rows.append(dict(kind='lower-highs' if lh else 'control', yr=pd.to_datetime(g[t] * 14400, unit='s').year,
                         Hpct=H / S * 100, r05=drop >= .5, r10=drop >= 1, r16=drop >= 1.618, failed=failed, drop=drop))
        t += 30
    R = pd.DataFrame(rows)
    agg = dict(n=('r05', 'size'), H_pct_med=('Hpct', 'median'), reach_half_H=('r05', 'mean'), reach_1H=('r10', 'mean'),
               reach_1618H=('r16', 'mean'), failed_24h=('failed', 'mean'), med_drop_H=('drop', 'median'))
    print(f'4h bars {N}; breaks {len(R)}')
    print(R.groupby('kind').agg(**agg).round(3).to_string())
    print('\n-- by year'); print(R.groupby(['kind', 'yr']).agg(**agg).round(3).to_string())
    print('\n-- lower-highs, failed vs held in 24 h'); print(R[R.kind == 'lower-highs'].groupby('failed').agg(**agg).round(3).to_string())

if __name__ == '__main__':
    run()
