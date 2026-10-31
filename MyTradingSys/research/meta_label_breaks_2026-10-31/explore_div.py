"""EXPLORATORY (DEV only, not pre-registered): Malkan RSI divergence (regular + reverse PRD/NRD) and CVD divergence on the
trade timeframe and the next lower one, for the tf_break trades of meta.py.

A. At entry: does a divergence with / against the trade in the last LOOK trade-TF bars separate winners (and the best 5 %)?
B. Exit: hold until the first divergence AGAINST the trade (or MAXH bars) vs the fixed 4-bar exit and a fixed MAXH-bar exit.

Detector: backtest/layers/rsi/rsi_divergence.py, Malkan settings from params/malkan_divergence_default.json (SOURCED: regular
3-10 bars close to close; reverse 5-14 bars with RSI >= 60 / <= 40). An event stamped on bar k is known at the CLOSE of bar k.
OURS: LOOK = 10 trade-TF bars, MAXH = 24 trade-TF bars (12 at 4h), CVD = cumulative taker delta used in place of RSI
(regular kinds only; reverse needs RSI levels), lower TF = 15m->5m, 1h->15m, 4h->1h. No funding, no slippage.
Every outcome here is DEV (bars before 2024-07-01 only); a frozen re-run on 2020-2021 is the test.
Usage: python explore_div.py [out_dir]
"""
import json
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import meta as M  # noqa: E402
from backtest.layers.rsi import rsi_divergence as RD  # noqa: E402

S = M.S
P = json.load(open(os.path.join(M.MTS, 'backtest', 'layers', 'rsi', 'params', 'malkan_divergence_default.json'), encoding='utf-8'))
LOWER = {'15m': 5, '1h': 15, '4h': 60}
MAXH = {'15m': 24, '1h': 24, '4h': 12}
LOOK = 10
# for a long (d = +1): kinds AGAINST the trade, kinds WITH it; a short swaps them
AGAINST_LONG = ('bearish', 'nrd')
WITH_LONG = ('bullish', 'prd')


def div_events(b, tf_min):
    """{(source, kind): sorted array of the time each event becomes known (close of its stamp bar)}."""
    c = b['c'].to_numpy(float)
    t = b['t'].to_numpy(np.int64)
    rsi = S.rsi(c)
    cvd = np.cumsum(2 * b['tbv'].to_numpy(float) - b['v'].to_numpy(float))
    out = {}
    for kind in RD.KINDS:
        rev = kind in ('prd', 'nrd')
        lo, hi = (P['reverse']['min_bars'], P['reverse']['max_bars']) if rev else (P['min_bars'], P['max_bars'])
        ev = RD.rsi_divergence(list(c), list(rsi), list(t), lo, hi, kind=kind)
        out[('rsi', kind)] = np.sort(np.array([e['t'] + tf_min * 60 for e in ev], np.int64))
        if not rev:
            ev = RD.rsi_divergence(list(c), list(cvd), list(t), lo, hi, kind=kind)
            out[('cvd', kind)] = np.sort(np.array([e['t'] + tf_min * 60 for e in ev], np.int64))
    return out


def any_in(times, lo, hi):
    """an event known in (lo, hi]."""
    k = np.searchsorted(times, lo, side='right')
    return k < len(times) and times[k] <= hi


def first_after(times, lo):
    k = np.searchsorted(times, lo, side='right')
    return int(times[k]) if k < len(times) else None


def trade_outcomes(o, c, t, e, d, H, tf):
    """after the entry, by design: entry at open e+1, gross at the close of e+4 and e+H, and the time bar e+H closes."""
    entry = o[e + 1]
    return entry, d * (c[e + 4] / entry - 1), d * (c[e + H] / entry - 1), int(t[e + H]) + tf * 60


def build(df):
    rows = []
    for tfn in M.TFS:
        tf = S.CFG[tfn][0]
        N = S.CFG[tfn][2]
        b = S.bars(df, tf)
        lb = S.bars(df, LOWER[tfn])
        t = b['t'].to_numpy(np.int64)
        o, c = b['o'].to_numpy(float), b['c'].to_numpy(float)
        idx = {int(x): k for k, x in enumerate(t)}
        evs = {'same': div_events(b, tf), 'lower': div_events(lb, LOWER[tfn])}
        lc = pd.Series(lb['c'].to_numpy(float), index=lb['t'].to_numpy(np.int64) + LOWER[tfn] * 60)  # close, keyed by close time
        H = MAXH[tfn]
        for side in (-1, 1):
            for ev in S.events(b, tfn, side, False, None):
                if ev['split'] != 'DEV':
                    continue
                i = idx[int(ev['t'])]
                e = i if ev['cls'] == 'W1' else i + N
                if e + H >= len(b):
                    continue
                d = side * M.SGN[ev['cls']]
                t_entry = int(t[e]) + tf * 60
                entry, g4, gH, t_end = trade_outcomes(o, c, t, e, d, H, tf)
                r = dict(tf=tfn, cls=ev['cls'], t=t_entry, g4=g4, gH=gH)
                ag = AGAINST_LONG if d > 0 else WITH_LONG
                wi = WITH_LONG if d > 0 else AGAINST_LONG
                for where, E in evs.items():
                    for (src, kind), times in E.items():
                        role = 'against' if kind in ag else 'with'
                        r[f'at_{where}_{src}_{kind}_{role}'] = float(any_in(times, t_entry - LOOK * tf * 60, t_entry))
                    # exit on the first divergence against the trade (any kind, this source), known after entry
                    for src in ('rsi', 'cvd'):
                        cand = [first_after(E[(src, k)], t_entry) for k in ag if (src, k) in E]
                        cand = [x for x in cand if x is not None and x <= t_end]
                        if cand:
                            tx = min(cand)
                            if where == 'same':
                                px = c[idx[tx - tf * 60]]
                            else:
                                px = lc.get(tx, np.nan)
                            r[f'x_{where}_{src}'] = d * (px / entry - 1)
                            r[f'xbars_{where}_{src}'] = (tx - t_entry) / (tf * 60)
                        else:
                            r[f'x_{where}_{src}'] = r['gH']
                            r[f'xbars_{where}_{src}'] = H
                rows.append(r)
        print(tfn, sum(1 for x in rows if x['tf'] == tfn), file=sys.stderr)
    return pd.DataFrame(rows)


def stats(g, t):
    n = g - M.RT
    s = np.sort(n)[::-1]
    k = max(1, int(len(s) * 0.05))
    lo, hi = M.wk_boot(n, t)
    pos, neg = n[n > 0].sum(), -n[n < 0].sum()
    return dict(n=len(n), net=100 * n.mean(), lo=100 * lo, hi=100 * hi, win=100 * (n > 0).mean(),
                pf=pos / neg if neg > 0 else np.nan, no_top5=100 * s[k:].mean())


def report(T):
    out = []
    for tfn, g in T.groupby('tf', sort=False):
        t = g.t.to_numpy(np.int64)
        out.append(f'\n## {tfn} (DEV trades {len(g)}; held to the first divergence against the trade or {MAXH[tfn]} bars)')
        out.append('| exit | trades | net % | 95 % CI | win % | PF | net % without best 5 % | median bars held |')
        out.append('|---|---|---|---|---|---|---|---|')
        arms = [('fixed 4 bars (meta.py)', g.g4.to_numpy(), 4), (f'fixed {MAXH[tfn]} bars', g.gH.to_numpy(), MAXH[tfn])]
        for where in ('same', 'lower'):
            for src in ('rsi', 'cvd'):
                arms.append((f'{src.upper()} divergence against, {where} TF', g[f'x_{where}_{src}'].to_numpy(),
                             np.median(g[f'xbars_{where}_{src}'])))
        for name, v, mb in arms:
            s = stats(v, t)
            out.append(f"| {name} | {s['n']} | {s['net']:+.3f} | {s['lo']:+.3f}..{s['hi']:+.3f} | {s['win']:.0f} | {s['pf']:.2f} | {s['no_top5']:+.3f} | {mb:.0f} |")
        n4 = g.g4.to_numpy() - M.RT
        top = n4 >= np.quantile(n4, 0.95)
        out.append('\nAt entry (fixed 4-bar trades): a divergence known in the last 10 bars')
        out.append('| divergence | role | share of all trades | share of best 5 % | net % with | n with | net % without |')
        out.append('|---|---|---|---|---|---|---|')
        for col in [x for x in g.columns if x.startswith('at_')]:
            f = g[col].to_numpy() > 0
            if f.sum() < 30:
                continue
            _, where, src, kind, role = col.split('_')
            out.append(f'| {src.upper()} {kind}, {where} TF | {role} | {100 * f.mean():.0f} % | {100 * f[top].mean():.0f} % | '
                       f'{100 * n4[f].mean():+.3f} | {f.sum()} | {100 * n4[~f].mean():+.3f} |')
    return '\n'.join(out)


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else M.DEFAULT_OUT
    df = S.load()
    df = df[df.t < M.DEV_END]  # no bar at or after 2024-07-01 is loaded
    T = build(df)
    T.to_csv(os.path.join(out, 'div_table.csv'), index=False, lineterminator='\n')
    txt = report(T)
    open(os.path.join(HERE, 'explore_div_output.md'), 'w', encoding='utf-8', newline='\n').write(
        '# EXPLORATORY, DEV only: Malkan divergence at entry and as exit on the tf_break trades\n' + txt + '\n')
    print(txt)


if __name__ == '__main__':
    main()
