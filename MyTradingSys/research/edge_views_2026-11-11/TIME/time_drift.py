import glob, math, sys
import numpy as np, pandas as pd
files = sorted(glob.glob('F:/MTS/Dumps/backtest/spot_2017/BTCUSDT/1h/klines/*.csv'))
df = pd.concat([pd.read_csv(f, header=None, usecols=[0,1,4], names=['t','o','c']) for f in files])
df['t'] = np.where(df.t > 1e14, df.t // 1000, df.t)
df['ts'] = pd.to_datetime(df.t, unit='ms')
df = df.drop_duplicates('ts').set_index('ts').sort_index()
full = pd.date_range(df.index[0], df.index[-1], freq='1h')
print('bars', len(df), 'missing', len(full)-len(df), df.index[0], df.index[-1])
df = df.reindex(full)
O = df.o.values; C = df.c.values; idx = full
def win(start_hours_off, nbars, starts):
    """return array bp for windows beginning at positions starts"""
    out = np.full(len(starts), np.nan)
    for k, s in enumerate(starts):
        e = s + nbars - 1
        if e < len(O) and not (np.isnan(O[s]) or np.isnan(C[e])):
            out[k] = (C[e]/O[s]-1)*1e4
    return out
hour = idx.hour.values; dow = idx.dayofweek.values
cells = []  # (id, name, dates(Series of start ts), values)
def add(cid, name, pos, vals):
    pos = np.asarray(pos); vals = np.asarray(vals)
    ok = ~np.isnan(vals)
    cells.append((cid, name, idx[pos][ok], vals[ok]))
for h in range(24):
    p = np.where(hour == h)[0]; add('a', f'hour {h:02d}Z', p, win(0,1,p))
p0 = np.where(hour == 0)[0]
for d in range(7):
    p = p0[dow[p0] == d]; add('b', ['Mon','Tue','Wed','Thu','Fri','Sat','Sun'][d]+' 24h', p, win(0,24,p))
ps = p0[dow[p0] == 5]; add('c', 'weekend Sat-Mon', ps, win(0,48,ps))
pm = p0[dow[p0] == 0]; add('c', 'weekdays Mon-Sat', pm, win(0,120,pm))
add('d', 'Asia 00-08Z', p0, win(0,8,p0))
p8 = np.where(hour == 8)[0]; add('d', 'Europe 08-14Z', p8, win(0,6,p8))
p14 = np.where(hour == 14)[0]; us = win(0,7,p14); add('d', 'US 14-21Z', p14, us)
first = win(0,1,p14); rest = win(0,6,p14+1)
add('e', 'sign(14-15Z)*ret(15-21Z)', p14, np.sign(first)*rest)
asia = win(0,8,p14-14)  # day's 00Z index = p14-14 (valid if no gaps)
add('f', 'sign(Asia)*US', p14, np.sign(asia)*us)
for h in (0,8,16):
    p = np.where(hour == h)[0]; p = p[p >= 1]
    add('g', f'before {h:02d}Z (bar {(h-1)%24:02d}-{h:02d})', p-1, win(0,1,p-1))
    add('g', f'after {h:02d}Z (bar {h:02d}-{(h+1)%24:02d})', p, win(0,1,p))
print('family size', len(cells))
T0 = idx[0]; T1 = idx[-1]
span = (T1 - T0)
dev_end = T0 + span*0.6; val_start = dev_end + pd.Timedelta(days=30); rec_start = T1 - pd.Timedelta(days=365)
print('DEV end', dev_end, 'VAL start', val_start, 'RECENT start', rec_start)
def st(v):
    n = len(v)
    if n < 3: return (n, float('nan'), float('nan'), float('nan'))
    m = v.mean(); se = v.std(ddof=1)/math.sqrt(n)
    return (n, m, m/se if se > 0 else float('nan'), (v > 0).mean()*100)
def f(s): return f'{s[0]} / {s[1]:+.2f} / {s[2]:+.2f} / {s[3]:.0f}'
rows = []; marked = []
TCRIT = 3.25
for cid, name, d, v in cells:
    d = pd.DatetimeIndex(d)
    a = st(v); dv = st(v[d <= dev_end]); vl = st(v[d >= val_start]); rc = st(v[d >= rec_start])
    mark = abs(dv[2]) >= TCRIT and np.sign(dv[1]) == np.sign(vl[1]) and abs(dv[1]) > 10
    if mark: marked.append(name)
    rows.append((cid, name, a, dv, vl, rc, mark))
out = ['| id | cell | ALL n/mean bp/t/%pos | DEV n/mean/t/%pos | VAL n/mean/t/%pos | LAST12M n/mean/t/%pos | mark |', '|---|---|---|---|---|---|---|']
for cid, name, a, dv, vl, rc, mark in rows:
    out.append(f'| {cid} | {name} | {f(a)} | {f(dv)} | {f(vl)} | {f(rc)} | {"YES" if mark else "-"} |')
open('tables.md', 'w').write('\n'.join(out))
print('\n'.join(out)); print('MARKED', marked)
big = [(r[1], r[3][2]) for r in rows if abs(r[3][2]) >= TCRIT]
print('DEV beyond Bonferroni (t only):', big)
print('largest |mean| ALL:', sorted([(abs(r[2][1]), r[1]) for r in rows], reverse=True)[:5])
