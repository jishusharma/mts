"""Count-only gate for the build-then-flush rule (OURS, no returns, no fees, no verdict). Same cache and day-labelling as count_pool20.py.
Build window = days d-4..d-1: OI(d-1)/OI(d-4)-1 >= +3 % and close(d-1) < close(d-4) (new positions while price falls).
Flush day d: OI(d)/OI(d-1)-1 <= -3 % (forced unwind) and close(d)/close(d-1)-1 <= -3 %.
Entry candidate = open of d+1 (bar d is complete at its close). Cooldown 5 days per coin. DEV = d < 2024-01-01, VAL = d >= 2024-01-01 (counts only)."""
import glob, json, os
import numpy as np, pandas as pd
R = 'F:/MTS/data_cache/binance/combo-edge-miner-1114/'
BUILD, FL_OI, FL_PX, CD = 0.03, -0.03, -0.03, 5

def one(sym):
    s = pd.read_csv(R + f'spot_1d/{sym}.csv'); s['day'] = pd.to_datetime(s.ts // 86400000 * 86400, unit='s'); s = s.set_index('day')
    o = pd.read_csv(R + f'oi/{sym}.csv'); o['day'] = pd.to_datetime(o.ts // 86400000 * 86400, unit='s'); o = o.drop_duplicates('day').set_index('day').oi
    d = s[['o', 'c']].copy(); d['oi'] = o; d = d.asfreq('D')
    d['fwd_close'] = d.c.shift(-1)
    build = (d.oi.shift(1) / d.oi.shift(4) - 1 >= BUILD) & (d.c.shift(1) < d.c.shift(4))
    flush = (d.oi / d.oi.shift(1) - 1 <= FL_OI) & (d.c / d.c.shift(1) - 1 <= FL_PX)
    raw = (build & flush & d.fwd_close.notna()).fillna(False)
    keep, last = [], -99
    for i, v in enumerate(raw.to_numpy()):
        if v and i - last > CD: keep.append(True); last = i
        else: keep.append(False)
    d['sym'] = sym; return d[np.array(keep)], int(raw.sum())

syms = sorted(os.path.basename(p)[:-4] for p in glob.glob(R + 'oi/*.csv'))
res = [one(s) for s in syms]; ev = pd.concat([r[0] for r in res])
D, V = ev[ev.index < '2024-01-01'], ev[ev.index >= '2024-01-01']
out = dict(coins=len(syms), raw_before_cooldown=sum(r[1] for r in res), dev_n=len(D), dev_weeks=int(D.index.to_period('W').nunique()), dev_days=int(D.index.nunique()),
           val_n=len(V), val_weeks=int(V.index.to_period('W').nunique()), val_days=int(V.index.nunique()), by_year=ev.index.year.value_counts().sort_index().to_dict())
print(json.dumps(out, indent=1, default=int)); json.dump(out, open('counts_buildflush.json', 'w'), indent=1, default=int)
