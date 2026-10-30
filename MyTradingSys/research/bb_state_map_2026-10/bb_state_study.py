"""BB state x candle x regime x TF map. DEV 2022-2025 only. Definitions: MAP.md."""
import glob, sys
import numpy as np
import pandas as pd

SRC = sys.argv[1] if len(sys.argv) > 1 else 'F:/MTS/data/tom_raw/klines/BTCUSDT-1m-*.csv'
H = 12
TFS = {'15m': '15min', '1h': '1h', '4h': '4h', '12h': '12h'}


def classify(o, h, l, c, n=20):
    """Return DataFrame of mid, up, lo, state, candle, regime per bar."""
    cs = pd.Series(c)
    mid = cs.rolling(n).mean().to_numpy()
    sd = cs.rolling(n).std(ddof=0).to_numpy()
    up, lo = mid + 2 * sd, mid - 2 * sd
    state = np.where(c >= up, 'ABOVE_UP', np.where(c >= mid, 'UP_HALF', np.where(c > lo, 'LOW_HALF', 'BELOW_LOW')))
    rng = np.maximum(h - l, 1e-12)
    body = np.abs(c - o) / rng
    candle = np.where(body < 0.10, 'DOJI', np.where(c > o, 'GREEN', 'RED'))
    mid5 = np.roll(mid, 5); mid5[:5] = np.nan
    regime = np.where(np.abs(mid - mid5) > 0.5 * sd, 'MOVING', 'NOT_MOVING')
    valid = ~(np.isnan(mid) | np.isnan(mid5))
    return mid, up, lo, state, candle, regime, valid


def load():
    fs = [f for f in sorted(glob.glob(SRC)) if '2026' not in f]
    if not fs:
        sys.exit('no data at ' + SRC)
    df = pd.concat([pd.read_csv(f, usecols=[0, 1, 2, 3, 4], header=None if False else 'infer') for f in fs], ignore_index=True)
    df.columns = ['t', 'o', 'h', 'l', 'c']
    df = df[pd.to_numeric(df['t'], errors='coerce').notna()].astype(float)
    t = df['t'].where(df['t'] < 1e14, df['t'] / 1000)
    df.index = pd.to_datetime(t, unit='ms')
    df = df[~df.index.duplicated(keep='first')].sort_index()  # 2025-09 has monthly + daily overlap
    return df[(df.index >= '2022-01-01') & (df.index < '2026-01-01')]


def cells(df, tf):
    b = df.resample(TFS[tf]).agg({'o': 'first', 'h': 'max', 'l': 'min', 'c': 'last'}).dropna()
    o, h, l, c = (b[k].to_numpy() for k in 'ohlc')
    mid, up, lo, st, cd, rg, ok = classify(o, h, l, c)
    rows = []
    for i in range(len(b) - H - 1):
        if not ok[i]:
            continue
        hi, lw = h[i + 1:i + 1 + H], l[i + 1:i + 1 + H]
        tu, tl = np.flatnonzero(hi >= up[i]), np.flatnonzero(lw <= lo[i])
        fu, fl = (tu[0] if len(tu) else 99), (tl[0] if len(tl) else 99)
        first = 'neither' if fu == fl == 99 else 'same' if fu == fl else 'upper_first' if fu < fl else 'lower_first'
        rows.append(dict(tf=tf, state=st[i], candle=cd[i], regime=rg[i],
                         nxt_up=float(c[i + 1] > c[i]),
                         r_up=float(len(tu) > 0), r_lo=float(len(tl) > 0),
                         r_mid=float(((hi >= mid[i]) if c[i] < mid[i] else (lw <= mid[i])).any()),
                         first=first,
                         fav=(hi.max() - c[i]) / c[i] * 100, adv=(c[i] - lw.min()) / c[i] * 100))
    return pd.DataFrame(rows)


def summarize(r):
    g = r.groupby(['tf', 'state', 'candle', 'regime'])
    out = g.agg(n=('nxt_up', 'size'), next_up=('nxt_up', 'mean'), reach_upper=('r_up', 'mean'),
                reach_lower=('r_lo', 'mean'), reach_mid=('r_mid', 'mean'),
                med_fav=('fav', 'median'), med_adv=('adv', 'median')).reset_index()
    fr = r.groupby(['tf', 'state', 'candle', 'regime'])['first'].value_counts(normalize=True).unstack(fill_value=0).reset_index()
    out = out.merge(fr, on=['tf', 'state', 'candle', 'regime'])
    out['grey'] = (out['n'] < 30).astype(int)
    return out


if __name__ == '__main__':
    d = load()
    res = pd.concat([cells(d, tf) for tf in TFS], ignore_index=True)
    summarize(res).to_csv('map.csv', index=False, lineterminator='\n')
    print('cells written', len(res))
