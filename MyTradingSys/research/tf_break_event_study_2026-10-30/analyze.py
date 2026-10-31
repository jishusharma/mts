"""Summaries of events.csv -> markdown tables on stdout, compact numbers to a json.
Usage: python analyze.py events.csv [numbers.json] > output.md
Costs come from MyTradingSys/backtest/fees.py: regime A (all-taker, Binance taker both legs) headline, regime D (maker both legs)
sensitivity. No slippage is modelled (stated limit)."""
import json
import os
import sys

import numpy as np
import pandas as pd

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')))
from backtest import fees  # noqa: E402

EV = pd.read_csv(sys.argv[1])
NUMS = sys.argv[2] if len(sys.argv) > 2 else None
ORDER = ['W', '1D', '4h', '1h', '15m']
RT_A = 2 * fees.BINANCE_TAKER
RT_D = 2 * fees.BINANCE_MAKER
rng = np.random.default_rng(1)
out = {'rt_regime_A_pct': 100 * RT_A, 'rt_regime_D_pct': 100 * RT_D, 'cells': []}


def wk_boot(sub, col, nb=1000):
    """week-block bootstrap 95% CI of mean(col)."""
    if len(sub) < 10:
        return (np.nan, np.nan)
    wk = (sub.t // 604800).astype(int).to_numpy()
    vals = sub[col].to_numpy()
    s = [vals[wk == w] for w in np.unique(wk)]
    ms = [np.concatenate([s[j] for j in rng.integers(0, len(s), len(s))]).mean() for _ in range(nb)]
    return tuple(np.percentile(ms, [2.5, 97.5]))


def pct(x):
    return f'{100 * x:.1f}'


def ci(lo, hi, d=2):
    return 'na' if np.isnan(lo) else f'[{100 * lo:.{d}f}, {100 * hi:.{d}f}]'


def f3(v):
    return 'na' if v is None else f'{v:.3f}'


print('## T0 headline: events per TF x class and fee-net mean % per trade (week-block 95% CI), real levels, both sides pooled')
print(f'trade = H: follow the break; R: fade the break; W1: fade the pierce (go back the way the wick came). Entry at the open after the class is known, exit after 4 bars (h4) or 24 (h24). Cost regime A = round trip {100 * RT_A:.2f}%; regime D (maker both legs) = {100 * RT_D:.2f}%. No slippage. CI shown when n >= 10.')
print('| TF | class | n DEV | n VAL | DEV net h4 % | DEV CI | VAL net h4 % | VAL CI | DEV net h24 % | VAL net h24 % | DEV net h4 % (D) | VAL net h4 % (D) |')
print('|---|---|---|---|---|---|---|---|---|---|---|---|')
R = EV[EV.ctl == 'real'].copy()
for tf in ORDER:
    for k, sgn in (('H', 1), ('R', -1), ('W1', -1)):
        cells = {}
        for sp in ('DEV', 'VAL'):
            s = R[(R.tf == tf) & (R.cls == k) & (R.split == sp)].copy()
            s['net4'] = sgn * s.cont4 - RT_A
            lo, hi = wk_boot(s, 'net4')
            cells[sp] = dict(n=len(s), net4=100 * s.net4.mean() if len(s) else None, lo=lo, hi=hi,
                             net24=100 * (sgn * s.cont24.mean() - RT_A) if len(s) else None,
                             net4_D=100 * (sgn * s.cont4.mean() - RT_D) if len(s) else None)
            out['cells'].append(dict(tf=tf, cls=k, split=sp, n=cells[sp]['n'], net4=cells[sp]['net4'],
                                     lo=None if np.isnan(lo) else 100 * lo, hi=None if np.isnan(hi) else 100 * hi,
                                     net24=cells[sp]['net24'], net4_D=cells[sp]['net4_D']))
        d, v = cells['DEV'], cells['VAL']
        print(f"| {tf} | {k} | {d['n']} | {v['n']} | {f3(d['net4'])} | {ci(d['lo'], d['hi'])} | {f3(v['net4'])} | {ci(v['lo'], v['hi'])} | {f3(d['net24'])} | {f3(v['net24'])} | {f3(d['net4_D'])} | {f3(v['net4_D'])} |")

print('\n## T1 class frequencies (real vs pseudo-level control), DEV | VAL')
print('| TF | side | split | n real | W1% | R% | H% | n ctl | W1% ctl | R% ctl | H% ctl |')
print('|---|---|---|---|---|---|---|---|---|---|---|')
for tf in ORDER:
    for side in ('low', 'high'):
        for sp in ('DEV', 'VAL'):
            r = EV[(EV.tf == tf) & (EV.side == side) & (EV.split == sp) & (EV.ctl == 'real')]
            p = EV[(EV.tf == tf) & (EV.side == side) & (EV.split == sp) & (EV.ctl == 'pseudo')]
            share = lambda d, k: pct((d.cls == k).mean()) if len(d) else 'na'
            print(f'| {tf} | {side} | {sp} | {len(r)} | {share(r, "W1")} | {share(r, "R")} | {share(r, "H")} | {len(p)} | {share(p, "W1")} | {share(p, "R")} | {share(p, "H")} |')

print('\n## T2 hold share among close-breaks, H/(H+R), both sides pooled: real (week-block CI) vs control')
print('| TF | split | n breaks real | H share real | 95% CI | H share ctl |')
print('|---|---|---|---|---|---|')
for tf in ORDER:
    for sp in ('DEV', 'VAL'):
        r = EV[(EV.tf == tf) & (EV.split == sp) & (EV.ctl == 'real') & (EV.cls != 'W1')].copy()
        p = EV[(EV.tf == tf) & (EV.split == sp) & (EV.ctl == 'pseudo') & (EV.cls != 'W1')]
        r['isH'] = (r.cls == 'H').astype(float)
        lo, hi = wk_boot(r, 'isH')
        print(f'| {tf} | {sp} | {len(r)} | {pct(r.isH.mean()) if len(r) else "na"} | {"na" if np.isnan(lo) else f"[{pct(lo)}, {pct(hi)}]"} | {pct((p.cls == "H").mean()) if len(p) else "na"} |')

print('\n## T3 indicator state before / at / after (real events, DEV+VAL pooled; medians)')
print('flow = taker-flow ratio (2*taker_buy - volume)/volume signed so + = flow WITH the break direction; RSI mirrored for highs so lows and highs pool')
print('| TF | class | n | RSI pre | RSI at | RSI post | flow pre | flow at | flow post | vol at/med20 | vol post/at |')
print('|---|---|---|---|---|---|---|---|---|---|---|')
M = R.copy()
for c in ('rsi_pre', 'rsi_at', 'rsi_post'):
    M[c] = np.where(M.side == 'high', 100 - M[c], M[c])
for tf in ORDER:
    for k in ('W1', 'R', 'H'):
        s = M[(M.tf == tf) & (M.cls == k)]
        if len(s) == 0:
            continue
        m = s[['rsi_pre', 'rsi_at', 'rsi_post', 'flow_pre', 'flow_at', 'flow_post', 'vol_at', 'vol_post']].median()
        print(f'| {tf} | {k} | {len(s)} | {m.rsi_pre:.1f} | {m.rsi_at:.1f} | {m.rsi_post:.1f} | {m.flow_pre:.3f} | {m.flow_at:.3f} | {m.flow_post:.3f} | {m.vol_at:.2f} | {m.vol_post:.2f} |')

print('\n## T4 does state AT the break separate H from R? H share below/above the DEV median of the AT-bar variable (cut from DEV, applied to VAL)')
print('| TF | variable | cut (DEV median) | H share below DEV | above DEV | below VAL | above VAL | n DEV | n VAL |')
print('|---|---|---|---|---|---|---|---|---|')
B = M[M.cls != 'W1'].copy()
B['isH'] = (B.cls == 'H').astype(float)
for tf in ORDER:
    for var in ('flow_at', 'vol_at', 'rsi_at', 'dist_atr'):
        d = B[(B.tf == tf) & (B.split == 'DEV')].dropna(subset=[var])
        v = B[(B.tf == tf) & (B.split == 'VAL')].dropna(subset=[var])
        if len(d) < 20:
            continue
        cut = d[var].median()
        g = lambda s, up: pct(s[(s[var] > cut) == up].isH.mean()) if len(s[(s[var] > cut) == up]) else 'na'
        print(f'| {tf} | {var} | {cut:.3f} | {g(d, False)} | {g(d, True)} | {g(v, False)} | {g(v, True)} | {len(d)} | {len(v)} |')

print('\n## T5 gross continuation in the break direction, mean % (real levels; + = price kept going the break way)')
print('| TF | class | split | n | cont h1 | h4 | h12 | h24 |')
print('|---|---|---|---|---|---|---|---|')
for tf in ORDER:
    for k in ('H', 'R', 'W1'):
        for sp in ('DEV', 'VAL'):
            s = R[(R.tf == tf) & (R.cls == k) & (R.split == sp)]
            if len(s) < 5:
                continue
            print(f'| {tf} | {k} | {sp} | {len(s)} | {100 * s.cont1.mean():.3f} | {100 * s.cont4.mean():.3f} | {100 * s.cont12.mean():.3f} | {100 * s.cont24.mean():.3f} |')

if NUMS:
    json.dump(out, open(NUMS, 'w', newline='\n'), indent=1)
