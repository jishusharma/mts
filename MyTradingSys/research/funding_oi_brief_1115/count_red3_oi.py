"""Descriptive count (no fees, no verdict): after 3 red UTC days, next-24h low and close with 3-day OI up vs OI down.
All definitions OURS. DEV = 2022-01-01..2023-12-31 outcomes only; VAL (>= 2024-01-01) signal days are COUNTED, outcomes NOT computed.
Run: python count_red3_oi.py  -> prints markdown, writes counts.json
"""
import glob, json, os, sys
import numpy as np, pandas as pd

KDIR = {'BTCUSDT': 'F:/MTS/data/tom_raw/klines/BTCUSDT-1m-*.csv', 'ETHUSDT': 'F:/MTS/data/tom_raw/klines_eth/ETHUSDT-1m-*.csv'}
FUND = 'F:/MTS/data_cache/binance/combo-edge-miner-1114/funding/{}.csv'
OI_UP, OI_DN = 0.02, -0.02   # 3-day OI change threshold (OURS)
DEV_END = pd.Timestamp('2024-01-01')
FLUSH = -0.03                # next-24h low <= -3 % from the signal close (OURS)

def daily(sym):
    fs = sorted(f for f in glob.glob(KDIR[sym]) if len(os.path.basename(f)) == len('BTCUSDT-1m-2022-01.csv'))  # monthly files only
    k = pd.concat([pd.read_csv(f, usecols=[0, 1, 2, 3, 4]) for f in fs], ignore_index=True)
    k.columns = ['t', 'o', 'h', 'l', 'c']
    k['t'] = np.where(k.t > 1e14, k.t // 1000, k.t) // 1000
    k = k.drop_duplicates('t'); k['day'] = pd.to_datetime(k.t // 86400 * 86400, unit='s')
    d = k.groupby('day').agg(o=('o', 'first'), h=('h', 'max'), l=('l', 'min'), c=('c', 'last'), n=('c', 'size'))
    return d[d.n == 1440]

def oi_end_of_day(sym):
    # metrics stamp = END of the 5m bar; the 00:00:00 stamp of day D+1 is the OI at the close of day D (known at the close)
    m = pd.concat([pd.read_csv(f, usecols=[0, 2]) for f in sorted(glob.glob(f'F:/MTS/data/metrics/{sym}/{sym}-metrics-*.csv'))])
    m.columns = ['ts', 'oi']; m['ts'] = pd.to_datetime(m.ts)
    m = m[m.ts.dt.hour.eq(0) & m.ts.dt.minute.eq(0)].drop_duplicates('ts')
    s = m.set_index('ts').oi; s.index = s.index - pd.Timedelta(days=1)  # label = the day that just closed
    return s

def funding_day_mean(sym):
    f = pd.read_csv(FUND.format(sym)); f['day'] = pd.to_datetime(f.ts // 86400000 * 86400, unit='s')
    return f.groupby('day').rate.mean()

def events(sym):
    d = daily(sym); oi = oi_end_of_day(sym); fu = funding_day_mean(sym)
    d['oi'] = oi; d['fu'] = fu
    d['red'] = d.c < d.o
    run = d.red.groupby((~d.red).cumsum()).cumsum()
    d['sig'] = run == 3                       # first day the streak reaches 3: events cannot overlap
    d['oi3'] = d.oi / d.oi.shift(3) - 1       # OI at close of day d vs close of day d-3
    d['fu3'] = d.fu.rolling(3).mean()
    d['fwd_low'] = d.l.shift(-1) / d.c - 1; d['fwd_close'] = d.c.shift(-1) / d.c - 1; d['fwd_high'] = d.h.shift(-1) / d.c - 1
    # require 4 consecutive calendar days present and next day present
    idx = d.index.to_series()
    fwd_idx = idx.shift(-1)
    ok = (idx - idx.shift(3)).dt.days.eq(3) & (fwd_idx - idx).dt.days.eq(1)
    d['ok'] = ok & d.oi3.notna()
    d['sym'] = sym
    return d

def grp(x):
    return 'OI up' if x >= OI_UP else 'OI down' if x <= OI_DN else 'OI flat'

def stats(g, label):
    n = len(g)
    if n == 0: return dict(group=label, n=0)
    return dict(group=label, n=n, low_med=float(g.fwd_low.median()), low_mean=float(g.fwd_low.mean()), low_sd=float(g.fwd_low.std()),
                flush=float((g.fwd_low <= FLUSH).mean()), close_mean=float(g.fwd_close.mean()), close_up=float((g.fwd_close > 0).mean()), high_med=float(g.fwd_high.median()))

def main():
    out = {}; rows = []
    for sym in ['BTCUSDT', 'ETHUSDT']:
        d = events(sym)
        ev = d[d.sig & d.ok].copy(); ev['g'] = ev.oi3.map(grp); ev['fpos'] = ev.fu3 > 0
        dev = ev[ev.index < DEV_END]; val = ev[ev.index >= DEV_END]
        base = d[(d.index < DEV_END) & d.ok & d.fwd_low.notna()]
        out[sym] = dict(days_dev=int(len(base)), red3_dev=int(len(dev)), red3_val_counts_only=int(len(val)),
                        val_by_group=val.g.value_counts().to_dict(), val_oiup_fundpos=int(((val.g == 'OI up') & val.fpos).sum()),
                        oi_first=str(d.oi.first_valid_index().date()), kl_last=str(d.index[-1].date()))
        rows.append((sym, stats(base, 'ALL DAYS (base)')))
        rows.append((sym, stats(dev, '3 red, any OI')))
        for g in ['OI up', 'OI flat', 'OI down']:
            rows.append((sym, stats(dev[dev.g == g], '3 red, ' + g)))
        rows.append((sym, stats(dev[(dev.g == 'OI up') & dev.fpos], '3 red, OI up, funding>0')))
        rows.append((sym, stats(dev[(dev.g == 'OI up') & ~dev.fpos], '3 red, OI up, funding<=0')))
    # pooled BTC+ETH (days overlap in time, correlated: shown as n only, not independent)
    print('| sym | group | n | next-24h low median | low mean | low sd | share low <= -3% | next-24h close mean | close up share | next-24h high median |')
    print('|---|---|---|---|---|---|---|---|---|---|')
    for sym, s in rows:
        if s['n'] == 0: print(f"| {sym} | {s['group']} | 0 | | | | | | | |"); continue
        print(f"| {sym} | {s['group']} | {s['n']} | {s['low_med']*100:.2f}% | {s['low_mean']*100:.2f}% | {s['low_sd']*100:.2f}% | {s['flush']*100:.0f}% | {s['close_mean']*100:+.2f}% | {s['close_up']*100:.0f}% | {s['high_med']*100:.2f}% |")
    out['rows'] = [dict(sym=a, **b) for a, b in rows]
    print(json.dumps({k: v for k, v in out.items() if k != 'rows'}, indent=1))
    json.dump(out, open('counts.json', 'w'), indent=1)

if __name__ == '__main__':
    main()
