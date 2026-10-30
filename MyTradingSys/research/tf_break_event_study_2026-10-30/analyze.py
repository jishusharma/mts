"""Summaries of events.csv -> printed markdown tables. Usage: python analyze.py events.csv"""
import sys
import numpy as np, pandas as pd

E = pd.read_csv(sys.argv[1])
ORDER = ['W', '1D', '4h', '1h', '15m']
COST = 0.0012
rng = np.random.default_rng(1)


def wk_boot(sub, col, nb=1000):
    """week-block bootstrap 95% CI of mean(col)."""
    if len(sub) < 10: return (np.nan, np.nan)
    wk = (sub.t // 604800).astype(int).to_numpy(); u = np.unique(wk)
    s = {w: sub[col].to_numpy()[wk == w] for w in u}
    ms = []
    for _ in range(nb):
        pick = rng.choice(u, len(u))
        a = np.concatenate([s[w] for w in pick]); ms.append(a.mean())
    return tuple(np.percentile(ms, [2.5, 97.5]))


def pct(x): return f'{100 * x:.1f}'


print('## T1 class frequencies (real vs pseudo-level control), DEV | VAL')
print('| TF | side | split | n real | W1% | R% | H% | n ctl | W1% ctl | R% ctl | H% ctl |')
print('|---|---|---|---|---|---|---|---|---|---|---|')
for tf in ORDER:
    for side in ('low', 'high'):
        for sp in ('DEV', 'VAL'):
            r = E[(E.tf == tf) & (E.side == side) & (E.split == sp) & (E.ctl == 'real')]
            p = E[(E.tf == tf) & (E.side == side) & (E.split == sp) & (E.ctl == 'pseudo')]
            f = lambda d, k: pct((d.cls == k).mean()) if len(d) else 'na'
            print(f'| {tf} | {side} | {sp} | {len(r)} | {f(r,"W1")} | {f(r,"R")} | {f(r,"H")} | {len(p)} | {f(p,"W1")} | {f(p,"R")} | {f(p,"H")} |')

print('\n## T2 hold share among close-breaks, H/(H+R), both sides pooled: real vs ctl, week-block CI of real-minus-nothing (real only)')
print('| TF | split | n breaks real | H share real | 95% CI | H share ctl |')
print('|---|---|---|---|---|---|')
for tf in ORDER:
    for sp in ('DEV', 'VAL'):
        r = E[(E.tf == tf) & (E.split == sp) & (E.ctl == 'real') & (E.cls != 'W1')].copy()
        p = E[(E.tf == tf) & (E.split == sp) & (E.ctl == 'pseudo') & (E.cls != 'W1')]
        r['isH'] = (r.cls == 'H').astype(float)
        lo, hi = wk_boot(r, 'isH')
        print(f'| {tf} | {sp} | {len(r)} | {pct(r.isH.mean()) if len(r) else "na"} | [{pct(lo)}, {pct(hi)}] | {pct((p.cls=="H").mean()) if len(p) else "na"} |')

print('\n## T3 indicator state before / at / after the break (real events, DEV+VAL pooled; medians)')
print('cvd = taker-flow ratio (2*tbv-v)/v signed so + = flow WITH break direction; rsi in raw points; low and high pooled with rsi sign-flipped for highs')
print('| TF | class | n | RSI pre | RSI at | RSI post | CVD pre | CVD at | CVD post | vol at/med20 | vol post/at |')
print('|---|---|---|---|---|---|---|---|---|---|---|')
R = E[E.ctl == 'real'].copy()
for c in ('rsi_pre', 'rsi_at', 'rsi_post'):
    R[c] = np.where(R.side == 'high', 100 - R[c], R[c])  # mirror so low and high comparable
for tf in ORDER:
    for k in ('W1', 'R', 'H'):
        s = R[(R.tf == tf) & (R.cls == k)]
        if len(s) == 0: continue
        m = s[['rsi_pre', 'rsi_at', 'rsi_post', 'cvd_pre', 'cvd_at', 'cvd_post', 'vol_at', 'vol_post']].median()
        print(f'| {tf} | {k} | {len(s)} | {m.rsi_pre:.1f} | {m.rsi_at:.1f} | {m.rsi_post:.1f} | {m.cvd_pre:.3f} | {m.cvd_at:.3f} | {m.cvd_post:.3f} | {m.vol_at:.2f} | {m.vol_post:.2f} |')

print('\n## T4 does state AT the break separate H from R? H share by split of the AT-bar variable (median cut taken on DEV, applied to VAL)')
print('| TF | variable | cut (DEV median) | H share below DEV | above DEV | below VAL | above VAL | n DEV | n VAL |')
print('|---|---|---|---|---|---|---|---|---|')
B = R[R.cls != 'W1'].copy(); B['isH'] = (B.cls == 'H').astype(float)
for tf in ORDER:
    for var in ('cvd_at', 'vol_at', 'rsi_at', 'dist_atr'):
        d = B[(B.tf == tf) & (B.split == 'DEV')].dropna(subset=[var]); v = B[(B.tf == tf) & (B.split == 'VAL')].dropna(subset=[var])
        if len(d) < 20: continue
        cut = d[var].median()
        g = lambda s, up: pct(s[(s[var] > cut) == up].isH.mean()) if len(s[(s[var] > cut) == up]) else 'na'
        print(f'| {tf} | {var} | {cut:.3f} | {g(d,False)} | {g(d,True)} | {g(v,False)} | {g(v,True)} | {len(d)} | {len(v)} |')

print('\n## T5 forward continuation (signed in break direction) from open after class known, mean %, net of 12 bp for the trade side')
print('follow = trade in break direction (H class); fade = trade against it (R class). net = mean cont - 12bp (follow) or -mean cont - 12bp (fade). week-block 95% CI on net at h=4.')
print('| TF | class | split | n | cont h1 | h4 | h12 | h24 | net trade h4 | CI h4 | net trade h24 |')
print('|---|---|---|---|---|---|---|---|---|---|---|')
for tf in ORDER:
    for k, sgn in (('H', 1), ('R', -1), ('W1', -1)):
        for sp in ('DEV', 'VAL'):
            s = R[(R.tf == tf) & (R.cls == k) & (R.split == sp)].copy()
            if len(s) < 5: continue
            s['net4'] = sgn * s.cont4 - COST
            lo, hi = wk_boot(s, 'net4')
            print(f'| {tf} | {k} | {sp} | {len(s)} | {pct(s.cont1.mean())} | {pct(s.cont4.mean())} | {pct(s.cont12.mean())} | {pct(s.cont24.mean())} | {100*s.net4.mean():.3f} | [{100*lo:.2f}, {100*hi:.2f}] | {100*(sgn*s.cont24.mean()-COST):.3f} |')
