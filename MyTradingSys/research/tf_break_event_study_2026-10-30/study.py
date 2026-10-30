"""T058 per-TF break event study (ledger P0-45). Reduced version: price/volume/RSI/CVD only (no OI/funding locally 2022-2025).
Definitions (OURS, from T058_BROKEN_EXTREMES.md 3.2-3.5, frozen before first run):
 swing = fractal L bars each side (W2,D3,4h3,1h5,15m5), known at bar k+L close; only latest live swing per side.
 first bar whose range pierces the level consumes it: close beyond level by 0.1*ATR14(SMA) -> break, else W1 wick sweep.
 break: R if a close is back inside within N bars (W2,D3,4h6,1h6,15m8), else H.
 forward measures start at open of bar i+N+1 (class known), h=1,4,12,24 bars.
 control C1: pseudo-level = low/high of a random non-fractal bar among the last M bars on the near side; same pipeline.
 DEV 2022-01..2024-06, VAL 2024-07..2025-08. Holdout 2025-09+ not read.
Usage: python study.py events.csv"""
import glob, sys
import numpy as np, pandas as pd

# tf minutes, fractal L, reclaim window N, major lookback M
CFG = {'W': (10080, 2, 2, 26), '1D': (1440, 3, 3, 60), '4h': (240, 3, 6, 90), '1h': (60, 5, 6, 96), '15m': (15, 5, 8, 96)}
HZ = (1, 4, 12, 24)
VAL_START = pd.Timestamp('2024-07-01', tz='UTC').timestamp()
END = pd.Timestamp('2025-09-01', tz='UTC').timestamp()


def load():
    fs = [f for f in sorted(glob.glob('F:/MTS/data/tom_raw/klines/BTCUSDT-1m-20??-??.csv')) if f[-11:-4] <= '2025-08']
    df = pd.concat([pd.read_csv(f, usecols=[0, 1, 2, 3, 4, 5, 9]) for f in fs], ignore_index=True)
    df.columns = ['t', 'o', 'h', 'l', 'c', 'v', 'tbv']
    df['t'] = np.where(df.t > 1e14, df.t // 1000, df.t) // 1000
    return df.drop_duplicates('t').sort_values('t').reset_index(drop=True)


def bars(df, tf):
    g = (df.t.to_numpy() // (tf * 60)).astype(np.int64)
    d = df.assign(g=g).groupby('g').agg(o=('o', 'first'), h=('h', 'max'), l=('l', 'min'), c=('c', 'last'),
                                        v=('v', 'sum'), tbv=('tbv', 'sum'), n=('t', 'size'))
    d = d[d.n == tf].copy()  # complete buckets only
    d['t'] = d.index.to_numpy() * tf * 60
    return d.reset_index(drop=True)


def rsi(c, n=14):
    d = np.diff(c, prepend=c[0]); up = np.where(d > 0, d, 0.); dn = np.where(d < 0, -d, 0.)
    au = pd.Series(up).ewm(alpha=1 / n, adjust=False).mean().to_numpy()
    ad = pd.Series(dn).ewm(alpha=1 / n, adjust=False).mean().to_numpy()
    return 100 - 100 / (1 + au / np.where(ad == 0, 1e-12, ad))


def fractals(x, L, low):
    n = len(x); sw = np.zeros(n, bool)
    for k in range(L, n - L):
        if low: sw[k] = all(x[k] < x[k - j] and x[k] <= x[k + j] for j in range(1, L + 1))
        else: sw[k] = all(x[k] > x[k - j] and x[k] >= x[k + j] for j in range(1, L + 1))
    return sw


def events(b, tfname, side, pseudo, rng):
    """side=-1 low break, +1 high break."""
    _, L, N, M = CFG[tfname]
    h, l, c, o, v, tbv, t = (b[k].to_numpy(float) for k in ['h', 'l', 'c', 'o', 'v', 'tbv', 't'])
    n = len(b); x = l if side < 0 else h
    sw = fractals(x, L, side < 0)
    pc = np.r_[c[0], c[:-1]]
    tr = np.maximum(h - l, np.maximum(abs(h - pc), abs(l - pc)))
    atr = pd.Series(tr).rolling(14).mean().to_numpy()
    R = rsi(c); cv = (2 * tbv - v) / np.where(v == 0, 1, v)
    vmed = pd.Series(v).rolling(20).median().shift(1).to_numpy()
    out = []; level = None
    for i in range(max(30, M), n - N - 2 - max(HZ)):
        kk = i - 1 - L  # swing at kk is known at close of kk+L = i-1, usable on bar i
        if sw[kk]:
            if not pseudo: level = x[kk]
            else:
                cand = [j for j in range(i - 1 - M, i - 1) if not sw[j] and ((x[j] < c[i - 1]) if side < 0 else (x[j] > c[i - 1]))]
                level = x[rng.choice(cand)] if cand else None
        if level is None or np.isnan(atr[i]): continue
        pierce = (l[i] < level) if side < 0 else (h[i] > level)
        if not pierce: continue
        buf = 0.1 * atr[i]
        beyond = (c[i] < level - buf) if side < 0 else (c[i] > level + buf)
        lv = level; level = None
        if not beyond:
            cls = 'W1'; e = i
        else:
            back = [(c[i + q] >= lv) if side < 0 else (c[i + q] <= lv) for q in range(1, N + 1)]
            cls = 'R' if any(back) else 'H'; e = i + N
        ent = o[e + 1]
        rec = dict(tf=tfname, side='low' if side < 0 else 'high', ctl='pseudo' if pseudo else 'real', cls=cls, t=t[i],
                   split='VAL' if t[i] >= VAL_START else 'DEV',
                   dist_atr=abs(c[i] - lv) / atr[i],
                   rsi_pre=R[i - 1], rsi_at=R[i], rsi_post=R[i + N],
                   cvd_pre=cv[i - 5:i].mean() * -side, cvd_at=cv[i] * -side,  # + means taker flow WITH the break direction
                   cvd_post=cv[i + 1:i + N + 1].mean() * -side,
                   vol_at=v[i] / vmed[i] if vmed[i] > 0 else np.nan, vol_post=v[i + 1:i + N + 1].mean() / v[i])
        for hz in HZ:
            rec[f'cont{hz}'] = (c[e + hz] / ent - 1) * -side  # + = continuation in the break direction
        out.append(rec)
    return out


def main():
    df = load(); df = df[df.t < END]
    print('1m rows', len(df), pd.to_datetime(df.t.iloc[0], unit='s'), pd.to_datetime(df.t.iloc[-1], unit='s'), file=sys.stderr)
    rng = np.random.default_rng(58)
    rows = []
    for tfn, (tf, *_r) in CFG.items():
        b = bars(df, tf)
        print(tfn, len(b), 'bars', file=sys.stderr)
        for side in (-1, 1):
            for pseudo in (False, True):
                rows += events(b, tfn, side, pseudo, rng)
    pd.DataFrame(rows).to_csv(sys.argv[1], index=False, lineterminator='\n')


main()
