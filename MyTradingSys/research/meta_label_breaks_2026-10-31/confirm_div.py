"""Fresh-data check of the explore_div.py lead (PRE_REG_DIV.md, frozen first): tf_break trades with a Malkan reverse divergence
WITH the trade on the next lower TF, BTCUSDT 1m 2020-01..2021-12. One run; no re-tuning.
Usage: python confirm_div.py [out_dir]   (default F:/MTS/runs/meta_label_breaks)"""
import glob
import json
import os
import sys

import numpy as np
import pandas as pd

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import meta as M  # noqa: E402
import explore_div as X  # noqa: E402

FRESH = 'F:/MTS/Dumps/backtest/raw_1m_2019/klines'
MONTHS = [f'{y}-{m:02d}' for y in (2020, 2021) for m in range(1, 13)]
FRESH_END = pd.Timestamp('2022-01-01', tz='UTC').timestamp()
FLAG = ('at_lower_rsi_prd_with', 'at_lower_rsi_nrd_with')
Y2021 = pd.Timestamp('2021-01-01', tz='UTC').timestamp()


def load_fresh(folder=FRESH):
    """2020-01..2021-12 monthly files only (no header in these files); fails if any bar is at or after 2022-01-01."""
    fs = [os.path.join(folder, f'BTCUSDT-1m-{m}.csv') for m in MONTHS]
    miss = [f for f in fs if not os.path.exists(f)]
    if miss:
        raise FileNotFoundError(miss)
    df = pd.concat([pd.read_csv(f, header=None, usecols=[0, 1, 2, 3, 4, 5, 9]) for f in fs], ignore_index=True)
    df.columns = ['t', 'o', 'h', 'l', 'c', 'v', 'tbv']
    df = df.apply(pd.to_numeric, errors='coerce').dropna()
    df['t'] = (np.where(df.t > 1e14, df.t // 1000, df.t) // 1000).astype(np.int64)
    df = df.drop_duplicates('t').sort_values('t').reset_index(drop=True)
    check_window(df.t.to_numpy())
    return df


def check_window(t):
    if len(t) == 0 or t.max() >= FRESH_END or t.min() < pd.Timestamp('2020-01-01', tz='UTC').timestamp():
        raise ValueError('bars outside 2020-01-01..2021-12-31')


def flagged(T):
    return (T[FLAG[0]].to_numpy() > 0) | (T[FLAG[1]].to_numpy() > 0)


def boot(vals, t, nb=M.NBOOT, seed=1):
    """week-block bootstrap: (lo, hi, one-sided p = share of resampled means <= 0)."""
    rng = np.random.default_rng(seed)
    wk = (t // M.WEEK).astype(np.int64)
    groups = [vals[wk == w] for w in np.unique(wk)]
    ms = np.array([np.concatenate([groups[j] for j in rng.integers(0, len(groups), len(groups))]).mean() for _ in range(nb)])
    lo, hi = np.percentile(ms, [2.5, 97.5])
    return lo, hi, float((ms <= 0).mean())


def verdicts(cells):
    """cells: {tf: dict(n, net, lo, p)} -> adds holm and verdict per tf, returns the card verdict."""
    tfs = [k for k in cells if cells[k]['n'] >= 30]
    adj = dict(zip(tfs, M.holm([cells[k]['p'] for k in tfs]))) if tfs else {}
    for k, c in cells.items():
        if c['n'] < 30:
            c['holm'], c['verdict'] = None, 'INCONCLUSIVE (too few)'
        elif c['net'] > 0 and c['lo'] > 0 and adj[k] < 0.05:
            c['holm'], c['verdict'] = adj[k], 'PASS'
        else:
            c['holm'], c['verdict'] = adj[k], 'FAIL' if c['net'] <= 0 else 'INCONCLUSIVE'
    if any(cells[k]['verdict'] == 'PASS' for k in ('1h', '4h') if k in cells):
        return 'PASS'
    if all(c['net'] <= 0 for c in cells.values()):
        return 'FAIL'
    return 'INCONCLUSIVE'


def run(T):
    cells, extra = {}, {}
    for tfn, g in T.groupby('tf', sort=False):
        n4 = g.g4.to_numpy() - M.RT
        t = g.t.to_numpy(np.int64)
        f = flagged(g)
        lo, hi, p = boot(n4[f], t[f]) if f.sum() >= 10 else (np.nan, np.nan, 1.0)
        cells[tfn] = dict(n=int(f.sum()), net=100 * n4[f].mean() if f.any() else np.nan, lo=100 * lo, hi=100 * hi, p=p)
        top = n4 >= np.quantile(n4, 0.95)
        long_ = g[FLAG[0]].to_numpy() > 0  # PRD-with is set only on longs, NRD-with only on shorts
        short_ = g[FLAG[1]].to_numpy() > 0
        yr = t >= Y2021
        extra[tfn] = dict(trades=len(g), all_net=100 * n4.mean(), not_flag_net=100 * n4[~f].mean(),
                          long_n=int(long_.sum()), long_net=100 * n4[long_].mean() if long_.any() else np.nan,
                          short_n=int(short_.sum()), short_net=100 * n4[short_].mean() if short_.any() else np.nan,
                          top5_flag_share=100 * f[top].mean(), all_flag_share=100 * f.mean(),
                          y2020_n=int((f & ~yr).sum()), y2020_net=100 * n4[f & ~yr].mean() if (f & ~yr).any() else np.nan,
                          y2021_n=int((f & yr).sum()), y2021_net=100 * n4[f & yr].mean() if (f & yr).any() else np.nan)
    card = verdicts(cells)
    return card, cells, extra


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else M.DEFAULT_OUT
    df = load_fresh()
    T = X.build(df)
    card, cells, extra = run(T)
    res = dict(card=card, cells=cells, extra=extra, bars_1m=len(df), first=int(df.t.min()), last=int(df.t.max()))
    json.dump(res, open(os.path.join(out, 'confirm_div.json'), 'w', encoding='utf-8', newline='\n'), indent=1, default=float)
    print(json.dumps(res, indent=1, default=float))


if __name__ == '__main__':
    main()
