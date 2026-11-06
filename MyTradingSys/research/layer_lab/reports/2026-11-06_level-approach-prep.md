MATCH=11 DIFF=19 NOT_IN_DATA=0

# Re-derive: level_approach_prep_2026-11-05 RESULT numbers (GPT-style audit, producer is not the study code)

Method: wrote an independent script from PRE_REG.md definitions only (study.py not read). FORMULAS.md has no formula for this study (grep approach/absorption: 0 hits), so PRE_REG.md definitions are the spec. Raw data: F:/MTS/data/tom_raw/klines/BTCUSDT-1m-*.csv 2022-01..2024-06 (1,313,280 bars, 0 missing minutes) and F:/MTS/data/metrics/BTCUSDT/*.csv. RESULT.md says metrics path binance_metrics; the files are under data/metrics/BTCUSDT.

Verdict rule: MATCH = recomputed value rounds to the RESULT figure (n exact). All recomputed values are OURS. Not stamped REVIEWED.

| # | RESULT.md item | RESULT value | Recomputed (OURS) | Verdict |
|---|---|---|---|---|
| 1 | regime bull | 29% | 29.1% | MATCH |
| 2 | regime bear | 21% | 20.4% | DIFF |
| 3 | regime range | 50% | 50.5% | MATCH (rounding edge) |
| 4 | total approaches | 887 | 887 | MATCH |
| 5 | U1 absorption n | 228 | 224 | DIFF |
| 6 | absorption reversal | 18% | 17.9% | MATCH |
| 7 | absorption break | 22% | 21.9% | MATCH |
| 8 | non-absorption n | 659 | 663 | DIFF |
| 9 | non-absorption reversal | 27% | 27.0% (26.1% if a same-bar tie counts as break) | MATCH |
| 10 | non-absorption break | 45% | 44.0% | DIFF |
| 11 | reweighted n | 659 | 663 | DIFF |
| 12 | reweighted reversal | 27% | 26.9% | MATCH |
| 13 | U2 UP n | 67 | 65 | DIFF |
| 14 | U2 UP reversal | 18% | 18.5% | MATCH |
| 15 | U2 FLAT n | 88 | 83 | DIFF |
| 16 | U2 FLAT reversal | 15% | 13.3% | DIFF |
| 17 | U2 DOWN n | 73 | 68 | DIFF |
| 18 | U2 DOWN reversal | 23% | 19.1% | DIFF |
| 19 | U3 0 TF n | 280 | 285 | DIFF |
| 20 | U3 0 TF hold | 18% | 17.5% | MATCH |
| 21 | U3 1 TF n | 129 | 130 | DIFF |
| 22 | U3 1 TF hold | 25% | 24.6% | MATCH |
| 23 | U3 2 TF n | 137 | 134 | DIFF |
| 24 | U3 2 TF hold | 23% | 23.9% | DIFF |
| 25 | U3 3+ TF n | 187 | 184 | DIFF |
| 26 | U3 3+ TF hold | 23% | 23.9% | DIFF |
| 27 | U3 total n (sum of rows) | 733 | 733 | MATCH |
| 28 | prose "OI 15-23 %, n 67-88" | 15-23%, 67-88 | 13-19%, 65-83 (8 absorption events have no OI stamp) | DIFF |
| 29 | prose "18% (no TF) to 23-25%" | 18 / 23-25 | 17.5 / 23.9-24.6 | DIFF |
| 30 | prose "ETH not run: no ETHUSDT 1m or ETH metrics on disk" | none on disk | 30 ETHUSDT-1m files and 1763 ETH metrics files on disk now | DIFF |

NOT_IN_DATA: none. Every number could be recomputed from the raw data (BTCUSDT-1m klines, BTCUSDT metrics).
## Reading
- Headline direction reproduces: absorption reverses ~18% vs ~27% matched, breaks ~22% vs ~44%; wick 0 TF ~17.5% vs 24-25% for 1+ TFs, no gain beyond 1 TF; total n 887 and 733 match exactly.
- U2 does not reproduce closely: RESULT 15-23% per group, mine 13-19%; claim 'OI does not separate outcomes' holds in both.
- n DIFFs of 1-5 come from PRE_REG ambiguity (tie handling inside a bar, OI stamp choice, regime reference bar, push straddling midnight). Not resolved here; study author should state them. DIFF means 'my reading of PRE_REG gives another number', not proven error.
- RESULT.md ETH claim is stale on this machine.

## Command (recompute)
Python 3.14/pandas 3.0.6. Script below, run as `python rd.py`:

```python
import glob, numpy as np, pandas as pd, sys
fs = sorted(glob.glob('F:/MTS/data/tom_raw/klines/BTCUSDT-1m-202[234]-*.csv'))
fs = [f for f in fs if f[-11:-4] <= '2024-06']
d = pd.concat([pd.read_csv(f, usecols=['open_time','open','high','low','close','volume','taker_buy_volume']) for f in fs])
d = d.drop_duplicates('open_time').sort_values('open_time')
d['t'] = (d.open_time // 60000).astype('int64')
d = d[d.t < pd.Timestamp('2024-07-01', tz='UTC').value // 60_000_000_000]
t0, t1 = d.t.min(), d.t.max()
print('bars', len(d), 'span', t1 - t0 + 1)
idx = np.arange(t0, t1 + 1)
d = d.set_index('t').reindex(idx)
print('missing minutes', int(d.close.isna().sum()))
O, H, L, C, V, TB = (d[k].values for k in ['open','high','low','close','volume','taker_buy_volume'])
mi = idx - t0  # minute index
dayid = idx // 1440
days = np.unique(dayid)
oi = pd.concat([pd.read_csv(f, usecols=['create_time','sum_open_interest']) for f in sorted(glob.glob('F:/MTS/data/metrics/BTCUSDT/BTCUSDT-metrics-202[234]-*.csv'))])
oi['m'] = ((pd.to_datetime(oi.create_time) - pd.Timestamp('1970-01-01')) // pd.Timedelta('1min')).astype('int64')  # minutes (naive=UTC)
oi = oi.drop_duplicates('m').set_index('m').sum_open_interest
def oi_at(m):  # stamp at or before m
    k = oi.index.searchsorted(m, side='right') - 1
    return oi.iloc[k] if k >= 0 and m - oi.index[k] < 10 else np.nan
def rng(day):
    s = (day * 1440) - t0
    return s, s + 1440
res = []; res3 = []
for di in days[1:]:
    ps, pe = rng(di - 1); s, e = rng(di)
    if ps < 0 or e > len(C) or np.isnan(H[ps:pe]).all(): continue
    PDH, PDL = np.nanmax(H[ps:pe]), np.nanmin(L[ps:pe])
    # regime: prior-day last close vs close 30 days earlier
    cs = ps - 29 * 1440
    reg = 'range'
    if cs >= 0:
        r = C[pe - 1] / C[cs + 1439] - 1 if False else C[pe - 1] / C[ps - 30*1440 + 1439] - 1 if ps - 30*1440 + 1439 >= 0 else np.nan
        reg = 'bull' if r > .10 else 'bear' if r < -.10 else 'range'
    for side in ('H', 'L'):
        lv = PDH if side == 'H' else PDL
        sg = 1 if side == 'H' else -1
        hi, lo = (H, L) if side == 'H' else (-L, -H)   # work in signed price space
        # signed price p' = sg*p ; level lv' = sg*lv ; push direction = up in signed space
        sl = sg * lv
        P_hi = (H if side == 'H' else -L); P_lo = (L if side == 'H' else -H); P_c = sg * C; P_o = sg * O
        # day opened inside zone?
        if P_o[s] >= sl * (1 - .003) if sl > 0 else P_o[s] >= sl * (1 + .003):
            pass
        zone = (lambda x: x >= sl - abs(sl) * .003)
        if zone(P_o[s]): continue
        w = np.arange(s, e)
        # approach bar
        a = w[zone(P_hi[w])]
        if len(a) and a[0] >= 3 and a[0] + 63 < len(C):
            t = a[0]
            ds = 0
            q = slice(t - 2, t + 1)
            ds = sg * np.sum(2 * TB[q] - V[q]) / np.sum(V[q])
            ext = (np.nanmax(P_hi[t+1:t+4]) - P_c[t]) / abs(P_c[t])
            absn = ds >= .3 and ext < .001
            c0 = P_c[t + 3]
            win = slice(t + 4, t + 64)
            brk = P_c[win] > sl + abs(sl) * .001
            rev = P_lo[win] <= c0 - abs(c0) * .005
            ib = np.argmax(brk) if brk.any() else 10**9
            ir = np.argmax(rev) if rev.any() else 10**9
            rev_first = ir < 10**9 and ir <= ib   # tie: intrabar reversal precedes bar close
            rev_first_strict = ir < 10**9 and ir < ib
            brk_first = ib < 10**9 and ib < ir
            dist = (sl - P_c[t]) / abs(sl)
            bucket = 0 if dist < 0 else 1 if dist < .001 else 2 if dist < .002 else 3
            m1 = oi_at(t - t0 + t0 - 2) if False else None
            o1 = oi_at(t + t0 + 4); o0 = oi_at(t + t0 - 2 - 5)
            oich = (o1 / o0 - 1) if o0 == o0 and o1 == o1 else np.nan
            res.append(dict(side=side, reg=reg, abs=absn, rev=rev_first, revs=rev_first_strict, brk=brk_first, b=bucket, oich=oich))
        # touch bar
        g = w[P_hi[w] >= sl]
        if len(g) and g[0] >= 15 and g[0] + 59 < len(C):
            u = g[0]
            cnt = 0
            for tf in (1, 2, 3, 5):
                ok = False
                for b0 in range(((u - 15 + tf - 1 + t0) // tf) * tf - t0, u - tf + 1, tf):
                    if b0 < u - 15 or b0 + tf > u: continue
                    sh = P_hi[b0:b0+tf].max(); sl_ = P_lo[b0:b0+tf].min()
                    o_, c_ = P_o[b0], P_c[b0 + tf - 1]
                    if sh >= sl - abs(sl) * .003 and sh - max(o_, c_) >= .5 * (sh - sl_) and sh > sl_:
                        ok = True; break
                cnt += ok
            hold = not (P_c[u:u+60] > sl + abs(sl) * .001).any()
            res3.append(dict(cnt=min(cnt, 3), hold=hold))
R = pd.DataFrame(res); T = pd.DataFrame(res3)
print('approaches', len(R)); print(R.reg.value_counts(normalize=True).round(3).to_dict())
A, N = R[R['abs']], R[~R['abs']]
print('abs n', len(A), 'rev', A.rev.mean().round(3), 'revstrict', A.revs.mean().round(3), 'brk', A.brk.mean().round(3))
print('non n', len(N), 'rev', N.rev.mean().round(3), 'revstrict', N.revs.mean().round(3), 'brk', N.brk.mean().round(3))
mix = A.b.value_counts(normalize=True)
rw = sum(mix[b] * N[N.b == b].rev.mean() for b in mix.index if (N.b == b).any())
print('reweighted', round(rw, 3), 'A bucket mix', mix.round(3).to_dict(), 'N mix', N.b.value_counts(normalize=True).round(3).to_dict())
A = A.copy(); A['g'] = np.where(A.oich > .001, 'UP', np.where(A.oich < -.001, 'DOWN', 'FLAT')); A.loc[A.oich.isna(), 'g'] = 'NA'
print(A.groupby('g').rev.agg(['count', 'mean']).round(3))
print(T.groupby('cnt').hold.agg(['count', 'mean']).round(3))


```n