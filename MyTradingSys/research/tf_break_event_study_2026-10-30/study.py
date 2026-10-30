"""T058 per-TF break event study (ledger P0-45), re-land. Price/volume/RSI/taker-flow only (no OI/funding locally 2022-2025).
Definitions (OURS, frozen in PRE_REG.md before the run; from T058_BROKEN_EXTREMES.md 3.2-3.5):
 swing = fractal L bars each side, confirmed at the close of bar k+L, usable from bar k+L+1; only the latest live swing per side.
 first bar whose range pierces the level consumes it: close beyond level by 0.1*ATR14(SMA) -> break, else W1 wick sweep.
 break: R if a close is back inside within N bars, else H. Forward measures start at the open of bar e+1 (class known).
 control C1: pseudo-level = low/high of a random non-swing bar among the last M bars on the near side; same pipeline.
 Signs: side=-1 low break, +1 high break; cont = return * side (+ = price moved in the BREAK direction),
 flow = taker-flow ratio * side (+ = taker flow WITH the break direction).
 DEV 2022-01..2024-06, VAL 2024-07..2025-06. HOLDOUT 2025-07+ is never loaded.
Usage: python study.py [events.csv]   (default F:/MTS/runs/tf_break_event_study/events.csv, outside the repo)"""
import glob
import os
import re
import sys

import numpy as np
import pandas as pd

# tf minutes, fractal L, reclaim window N, major lookback M
CFG = {'W': (10080, 2, 2, 26), '1D': (1440, 3, 3, 60), '4h': (240, 3, 6, 90), '1h': (60, 5, 6, 96), '15m': (15, 5, 8, 96)}
HZ = (1, 4, 12, 24)
KLINES = 'F:/MTS/data/tom_raw/klines'
LAST_MONTH = '2025-06'  # holdout 2025-07+ files are never opened
VAL_START = pd.Timestamp('2024-07-01', tz='UTC').timestamp()
END = pd.Timestamp('2025-07-01', tz='UTC').timestamp()
DEFAULT_OUT = 'F:/MTS/runs/tf_break_event_study/events.csv'


def _file_month(path):
    m = re.search(r'-(\d{4}-\d{2})(?:-\d{2})?\.csv$', path.replace('\\', '/'))
    return m.group(1) if m else None


def load(folder=KLINES, last_month=LAST_MONTH):
    """BTCUSDT 1m only (monthly and daily files overlap): files up to last_month, deduped by timestamp."""
    fs = [f for f in sorted(glob.glob(os.path.join(folder, 'BTCUSDT-1m-*.csv')))
          if os.path.basename(f).startswith('BTCUSDT-1m-') and (_file_month(f) or '9999') <= last_month]
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
    d = np.diff(c, prepend=c[0])
    up = np.where(d > 0, d, 0.)
    dn = np.where(d < 0, -d, 0.)
    au = pd.Series(up).ewm(alpha=1 / n, adjust=False).mean().to_numpy()
    ad = pd.Series(dn).ewm(alpha=1 / n, adjust=False).mean().to_numpy()
    return 100 - 100 / (1 + au / np.where(ad == 0, 1e-12, ad))


def confirmed_pivots(x, L, low):
    """conf[i] True when the bar k=i-L is a fractal pivot, known at the close of bar i.
    Built only from past-shifted series: left window x[k-L..k-1] (strict), right window x[k+1..k+L=i] (non-strict)."""
    s = pd.Series(x)
    pivot = s.shift(L)
    if low:
        left = s.rolling(L).min().shift(L + 1)
        right = s.rolling(L).min()
        conf = (pivot < left) & (pivot <= right)
    else:
        left = s.rolling(L).max().shift(L + 1)
        right = s.rolling(L).max()
        conf = (pivot > left) & (pivot >= right)
    return conf.to_numpy(), pivot.to_numpy()


def forward_measures(o, c, v, cv, R, i, e, N, side, lv):
    """Everything after the break bar i, by design: reclaim check, post-state, entry at open of bar e+1 and horizon returns.
    Outcomes only; no value computed here feeds a decision on bar i."""
    fwd_back = [(c[i + q] >= lv) if side < 0 else (c[i + q] <= lv) for q in range(1, N + 1)]
    fwd_post = dict(rsi_post=R[i + N], flow_post=cv[i + 1:i + N + 1].mean() * side,
                    vol_post=v[i + 1:i + N + 1].mean() / v[i])
    fwd_entry = o[e + 1]
    fwd_ret = {f'cont{hz}': (c[e + hz] / fwd_entry - 1) * side for hz in HZ}
    return fwd_back, fwd_post, fwd_ret


def events(b, tfname, side, pseudo, rng):
    """side=-1 low break, +1 high break."""
    _, L, N, M = CFG[tfname]
    h, l, c, o, v, tbv, t = (b[k].to_numpy(float) for k in ['h', 'l', 'c', 'o', 'v', 'tbv', 't'])
    n = len(b)
    x = l if side < 0 else h
    conf, pivot = confirmed_pivots(x, L, side < 0)
    pc = np.r_[c[0], c[:-1]]
    tr = np.maximum(h - l, np.maximum(abs(h - pc), abs(l - pc)))
    atr = pd.Series(tr).rolling(14).mean().to_numpy()
    R = rsi(c)
    cv = (2 * tbv - v) / np.where(v == 0, 1, v)
    vmed = pd.Series(v).rolling(20).median().shift(1).to_numpy()
    piv = np.zeros(n, bool)  # pivots known so far, filled as they are confirmed
    out = []
    level = None
    for i in range(max(30, M), n - N - 2 - max(HZ)):
        if conf[i - 1]:  # confirmed at the close of bar i-1, usable on bar i
            piv[i - 1 - L] = True
            if not pseudo:
                level = pivot[i - 1]
            else:
                cand = [j for j in range(i - 1 - M, i - L) if not piv[j] and ((x[j] < c[i - 1]) if side < 0 else (x[j] > c[i - 1]))]
                level = x[rng.choice(cand)] if cand else None
        if level is None or np.isnan(atr[i]):
            continue
        pierce = (l[i] < level) if side < 0 else (h[i] > level)
        if not pierce:
            continue
        buf = 0.1 * atr[i]
        beyond = (c[i] < level - buf) if side < 0 else (c[i] > level + buf)
        lv = level
        level = None
        if not beyond:
            cls, e = 'W1', i
            fwd_back, fwd_post, fwd_ret = forward_measures(o, c, v, cv, R, i, i, N, side, lv)
        else:
            e = i + N
            fwd_back, fwd_post, fwd_ret = forward_measures(o, c, v, cv, R, i, e, N, side, lv)
            cls = 'R' if any(fwd_back) else 'H'
        rec = dict(tf=tfname, side='low' if side < 0 else 'high', ctl='pseudo' if pseudo else 'real', cls=cls, t=t[i],
                   split='VAL' if t[i] >= VAL_START else 'DEV', dist_atr=abs(c[i] - lv) / atr[i],
                   rsi_pre=R[i - 1], rsi_at=R[i], flow_pre=cv[i - 5:i].mean() * side, flow_at=cv[i] * side,
                   vol_at=v[i] / vmed[i] if vmed[i] > 0 else np.nan)
        rec.update(fwd_post)
        rec.update(fwd_ret)
        out.append(rec)
    return out


def run(df, seed=58):
    df = df[df.t < END]
    rng = np.random.default_rng(seed)
    rows = []
    for tfn, (tf, *_r) in CFG.items():
        b = bars(df, tf)
        print(tfn, len(b), 'bars', file=sys.stderr)
        for side in (-1, 1):
            for pseudo in (False, True):
                rows += events(b, tfn, side, pseudo, rng)
    return pd.DataFrame(rows)


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_OUT
    os.makedirs(os.path.dirname(out), exist_ok=True)
    df = load()
    print('1m rows', len(df), pd.to_datetime(df.t.iloc[0], unit='s'), pd.to_datetime(df.t.iloc[-1], unit='s'), file=sys.stderr)
    run(df).to_csv(out, index=False, lineterminator='\n')


if __name__ == '__main__':
    main()
