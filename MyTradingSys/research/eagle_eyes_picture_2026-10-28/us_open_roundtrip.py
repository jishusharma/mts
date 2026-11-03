"""Operator 11-03 14:24Z: "what u expect at US open - apply MTS". Setup today: 13:30Z spike up (+0.7 %), full round trip down
below the 13:30 open by 14:00Z, retest of the broken level from below at 14:25Z. Count: weekdays 2022-01..2025-06, 1m klines.
Setup = high(13:30-14:25) >= open(13:30)*1.004 AND close(14:24) < open(13:30). Outcomes from close(14:24) to 15:30Z/16:30Z:
which first (14:25 low broken vs 13:30-14:25 high retaken), returns, first-hour range vs all days. Descriptive only."""
import glob, csv, datetime as dt, statistics as st
START, END = dt.date(2022, 1, 1), dt.date(2025, 7, 1)
D = {}
for f in sorted(glob.glob('F:/MTS/data/tom_raw/klines/BTCUSDT-1m-*.csv')):
    for r in csv.reader(open(f)):
        if r[0] == 'open_time': continue
        t = int(r[0]); t = t // 1000 if t > 1e14 else t; t //= 1000
        u = dt.datetime.fromtimestamp(t, dt.timezone.utc); d = u.date()
        if d < START or d >= END or u.weekday() > 4: continue
        m = u.hour * 60 + u.minute
        if 810 <= m <= 990: D.setdefault(d, {})[m] = (float(r[1]), float(r[2]), float(r[3]), float(r[4]))
def stats(days):
    rows = []
    for d in days:
        b = D[d]
        if any(m not in b for m in (810, 864, 870, 930, 990)): continue
        o = b[810][0]; hi = max(b[m][1] for m in range(810, 865) if m in b); lo = min(b[m][2] for m in range(810, 865) if m in b); c = b[864][3]
        setup = hi >= o * 1.004 and c < o
        first = None; mx = mn = 0
        for m in range(870, 931):
            if m not in b: continue
            mx = max(mx, b[m][1] / c - 1); mn = min(mn, b[m][2] / c - 1)
            if first is None:
                if b[m][1] >= hi: first = 'HI'
                elif b[m][2] < lo: first = 'LO'
        rng = (max(b[m][1] for m in range(870, 931) if m in b) - min(b[m][2] for m in range(870, 931) if m in b)) / c
        rows.append(dict(setup=setup, first=first, r1=b[930][3] / c - 1, r2=b[990][3] / c - 1, mx=mx, mn=mn, rng=rng, lo=lo / c - 1, hi=hi / c - 1))
    return rows
R = stats(sorted(D))
def rep(name, X):
    k = len(X); print('%-34s n=%4d  low first %3.0f%%  high first %3.0f%%  neither %3.0f%%  r@15:30 %+.2f%% (up %2.0f%%)  r@16:30 %+.2f%% (up %2.0f%%)  maxup %.2f%% maxdn %.2f%%  1h range %.2f%%  dist lo %.2f%% hi %+.2f%%' % (
        name, k, 100 * sum(x['first'] == 'LO' for x in X) / k, 100 * sum(x['first'] == 'HI' for x in X) / k, 100 * sum(x['first'] is None for x in X) / k,
        100 * st.median(x['r1'] for x in X), 100 * sum(x['r1'] > 0 for x in X) / k, 100 * st.median(x['r2'] for x in X), 100 * sum(x['r2'] > 0 for x in X) / k,
        100 * st.median(x['mx'] for x in X), 100 * st.median(x['mn'] for x in X), 100 * st.median(x['rng'] for x in X), 100 * st.median(x['lo'] for x in X), 100 * st.median(x['hi'] for x in X)))
rep('all weekdays', R); rep('spike up then round trip (TODAY)', [x for x in R if x['setup']]); rep('no setup', [x for x in R if not x['setup']])
