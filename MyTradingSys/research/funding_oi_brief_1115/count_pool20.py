"""Descriptive count, 20-coin pool (OURS, no fees, no verdict): same definitions as count_red3_oi.py.
Daily bars = Binance SPOT 1d (SOURCED cache combo-edge-miner-1114/spot_1d); OI = last 5m row per UTC day (cache .../oi), funding = cache .../funding.
DEV = signal day < 2024-01-01 outcomes only; VAL (>= 2024-01-01) signal days COUNTED, outcomes not computed.
Weeks with at least one event = independent-cluster count (events across coins on the same day are correlated)."""
import json, glob, os
import numpy as np, pandas as pd
R = 'F:/MTS/data_cache/binance/combo-edge-miner-1114/'
OI_UP, OI_DN, FLUSH, DEV_END = 0.02, -0.02, -0.03, pd.Timestamp('2024-01-01')

def one(sym):
    s = pd.read_csv(R + f'spot_1d/{sym}.csv'); s['day'] = pd.to_datetime(s.ts // 86400000 * 86400, unit='s'); s = s.set_index('day')
    o = pd.read_csv(R + f'oi/{sym}.csv'); o['day'] = pd.to_datetime(o.ts // 86400000 * 86400, unit='s'); o = o.drop_duplicates('day').set_index('day').oi
    f = pd.read_csv(R + f'funding/{sym}.csv'); f['day'] = pd.to_datetime(f.ts // 86400000 * 86400, unit='s'); f = f.groupby('day').rate.mean()
    d = s[['o', 'h', 'l', 'c']].copy(); d['oi'] = o; d['fu'] = f
    d = d.asfreq('D')   # missing days become NaN rows, so streaks and shifts never span a hole
    red = (d.c < d.o).fillna(False)
    d['sig'] = red.groupby((~red).cumsum()).cumsum() == 3
    d['oi3'] = d.oi / d.oi.shift(3) - 1; d['fu3'] = d.fu.rolling(3).mean()
    d['fwd_low'] = d.l.shift(-1) / d.c - 1; d['fwd_close'] = d.c.shift(-1) / d.c - 1
    d['sym'] = sym
    return d[d.sig & d.oi3.notna() & d.fwd_low.notna() & d.fwd_close.notna()]

def st(g, name):
    if len(g) == 0: return dict(group=name, n=0)
    wk = g.index.to_period('W').nunique()
    return dict(group=name, n=len(g), weeks=int(wk), low_med=g.fwd_low.median(), low_mean=g.fwd_low.mean(), low_sd=g.fwd_low.std(), flush=(g.fwd_low <= FLUSH).mean(), close_mean=g.fwd_close.mean())

def main():
    syms = sorted(os.path.basename(p)[:-4] for p in glob.glob(R + 'oi/*.csv'))
    ev = pd.concat([one(s) for s in syms])
    ev['g'] = np.where(ev.oi3 >= OI_UP, 'OI up', np.where(ev.oi3 <= OI_DN, 'OI down', 'OI flat')); ev['fpos'] = ev.fu3 > 0
    dev, val = ev[ev.index < DEV_END], ev[ev.index >= DEV_END]
    rows = [st(dev, 'DEV 3 red, any OI')] + [st(dev[dev.g == g], 'DEV 3 red, ' + g) for g in ['OI up', 'OI flat', 'OI down']]
    rows += [st(dev[(dev.g == 'OI up') & dev.fpos], 'DEV 3 red, OI up, funding>0')]
    print('| group | events n | weeks | next-24h low median | low mean | low sd | share low <= -3% | next-24h close mean |'); print('|---|---|---|---|---|---|---|---|')
    for r in rows:
        print(f"| {r['group']} | {r['n']} | {r.get('weeks','')} | {r['low_med']*100:.2f}% | {r['low_mean']*100:.2f}% | {r['low_sd']*100:.2f}% | {r['flush']*100:.0f}% | {r['close_mean']*100:+.2f}% |")
    up, dn = dev[dev.g == 'OI up'], dev[dev.g == 'OI down']
    se = float(np.sqrt(up.fwd_low.var() / len(up) + dn.fwd_low.var() / len(dn)))
    diff = float(up.fwd_low.mean() - dn.fwd_low.mean())
    out = dict(coins=len(syms), dev_rows=rows, val_counts={g: int((val.g == g).sum()) for g in ['OI up', 'OI flat', 'OI down']}, val_oiup_fundpos=int(((val.g == 'OI up') & val.fpos).sum()),
               val_weeks=int(val.index.to_period('W').nunique()), up_minus_down_low_mean=diff, se_naive=se, sd_low=float(dev.fwd_low.std()))
    print(json.dumps({k: v for k, v in out.items() if k != 'dev_rows'}, indent=1)); json.dump(out, open('counts_pool20.json', 'w'), indent=1, default=float)
main()
