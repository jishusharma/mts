"""Operator question 2026-10-30 (shot 32fd5d2253ee): short from a 5m close back below the BB mid; price walks the
lower band ("Bollinger dance"). When is the dance over, and does taking profit early lose the bigger move?

Definitions fixed before the first run (all OURS; descriptive, no fees, DEV 2022-2025 only):
- 5m bars from the Binance USD-M BTCUSDT 1m archive; BB(20, 2) on closes.
- Entry: a 5m close below the mid after the previous close at or above it (start of his slanting arrow), at that close.
- Trade alive until a 5m close above the mid (his "still in the trade") or 288 bars (one day).
- Touch: bar low <= lower band. The dance starts at the first touch after entry.
- k = closed bars since the last touch (k=0 on a touching bar). %b = (close - lower) / (upper - lower).
- Question per state (first bar where k reaches 1..6): does price print a new low below the low so far
  BEFORE a close above the mid? Split by %b of that bar (near band < 0.25, otherwise).
- Exits compared (gross % from entry, short): X0 first close back inside after a touch (k=1);
  Xk close when k reaches 3; Xfar first close after a touch with %b >= 0.25; Xmid close above the mid.
  An exit not reached before the mid close (or the one-day cap) takes the Xmid price, so every rule covers every short.
"""
import glob, json, sys, urllib.request
import numpy as np, pandas as pd

def bands(c):
    s = pd.Series(c); m = s.rolling(20).mean().to_numpy(); sd = s.rolling(20).std(ddof=0).to_numpy()
    return m, m + 2 * sd, m - 2 * sd

def load():
    fs = [f for f in sorted(glob.glob('F:/MTS/data/tom_raw/klines/BTCUSDT-1m-*.csv')) if '2026' not in f]
    df = pd.concat([pd.read_csv(f, usecols=[0, 2, 3, 4]) for f in fs], ignore_index=True)
    df.columns = ['t', 'h', 'l', 'c']
    df['t'] = np.where(df.t > 1e14, df.t // 1000, df.t) // 1000
    df = df.drop_duplicates('t').sort_values('t')
    df['g'] = df.t // 300
    b = df.groupby('g').agg(h=('h', 'max'), l=('l', 'min'), c=('c', 'last'), n=('c', 'size')).reset_index()
    return b[b.n == 5].reset_index(drop=True)

def walk(g, h, l, c, mid, lo, up, e, K=6):
    """Follow one short from bar e; returns per-k states and exit prices."""
    ent = c[e]; low = l[e]; touched = False; k = None
    st = {}; x0 = xk = xfar = xmid = None
    end = min(e + 288, len(c) - 1)
    for j in range(e + 1, end + 1):
        if g[j] - g[j - 1] != 1: return None
        if c[j] > mid[j]:
            xmid = c[j]; break
        newlow = l[j] < low
        for kk, s in st.items():
            if s['res'] is None and newlow: s['res'] = 1
        low = min(low, l[j])
        if l[j] <= lo[j]:
            touched = True; k = 0
        elif touched:
            k += 1
            if k == 1 and x0 is None: x0 = c[j]
            if k == 3 and xk is None: xk = c[j]
            if (c[j] - lo[j]) / (up[j] - lo[j]) >= 0.25 and xfar is None: xfar = c[j]
            if 1 <= k <= K and k not in st:
                st[k] = dict(pb=(c[j] - lo[j]) / (up[j] - lo[j]), res=None)
    if xmid is None: xmid = c[end]
    for s in st.values():
        if s['res'] is None: s['res'] = 0
    if not touched: return None
    x0, xk, xfar = (xmid if x is None else x for x in (x0, xk, xfar))
    return ent, st, x0, xk, xfar, xmid

def run():
    b = load(); g = b.g.to_numpy(); h, l, c = (b[k].to_numpy(float) for k in 'hlc')
    mid, up, lo = bands(c)
    rows, ex = [], []; e = 21
    while e < len(c) - 1:
        if c[e] < mid[e] and c[e - 1] >= mid[e - 1] and g[e] - g[e - 1] == 1:
            r = walk(g, h, l, c, mid, lo, up, e)
            if r:
                ent, st, x0, xk, xfar, xmid = r
                for k, s in st.items(): rows.append((k, s['pb'] < 0.25, s['res']))
                f = lambda x: None if x is None else (ent - x) / ent * 100
                ex.append((f(x0), f(xk), f(xfar), f(xmid)))
        e += 1
    R = pd.DataFrame(rows, columns=['k', 'near', 'newlow'])
    print('shorts with a lower-band touch:', len(ex))
    print('\nP(new low before a close above the mid), by bars since the last touch (k) and %b of that close')
    t = R.groupby(['k', 'near']).newlow.agg(['mean', 'size']).unstack()
    t.columns = [f'{a}_{"near" if b else "far"}' for a, b in t.columns]
    print(t.round(3).to_string())
    E = pd.DataFrame(ex, columns=['X0_first_close_inside', 'Xk3_three_bars_no_touch', 'Xfar_close_pb_ge_025', 'Xmid_close_above_mid'])
    print('\nGross % per short (no fees), mean / median / share > 0:')
    for col in E:
        v = E[col].dropna(); print(f'{col:26s} n={len(v):5d} mean={v.mean():.3f} med={v.median():.3f} win={(v > 0).mean():.3f}')

def live():
    u = 'https://data-api.binance.vision/api/v3/klines?symbol=BTCUSDT&interval=5m&startTime=1793293200000&endTime=1793313600000&limit=1000'
    k = json.load(urllib.request.urlopen(u, timeout=20))
    t = np.array([x[0] for x in k]) // 1000; h, l, c = (np.array([float(x[i]) for x in k]) for i in (2, 3, 4))
    mid, up, lo = bands(c)
    for i in range(len(c)):
        if not np.isnan(mid[i]) and t[i] >= 1793300400:
            ts = pd.to_datetime(t[i], unit='s').strftime('%H:%M')
            print(f'{ts} c={c[i]:.0f} l={l[i]:.0f} lo={lo[i]:.0f} mid={mid[i]:.0f} touch={int(l[i] <= lo[i])} %b={(c[i] - lo[i]) / (up[i] - lo[i]):.2f} abovemid={int(c[i] > mid[i])}')

if __name__ == '__main__':
    live() if 'live' in sys.argv else run()
