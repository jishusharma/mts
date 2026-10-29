"""15m Bollinger pierce near the US open: what force is behind it, and does it reach the prior-day level. Descriptive, no fees.
Definitions fixed before the first run (all OURS):
- Binance USD-M BTCUSDT 1m -> 15m (UTC), with taker buy volume. Weekdays. A = US cash open (13:30Z US DST, else 14:30Z).
- Pierce = first 15m CLOSE outside BB(20,2) after the previous close was inside, bar open in [A-2h, A+2h).
- Coil = BandWidth at the bar before the pierce in the lowest 20% of the prior 30 days.
- Force: vol ratio = pierce-bar volume / mean of the 20 bars before; delta share = (2*taker_buy - volume)/volume, signed so
  + = in the pierce direction (taker-flow proxy for the CVD candle). OI is not in this archive (NOT_IN_DATA).
- Level: prior UTC day high (PDH) for up pierces, low (PDL) for down, only when still beyond the pierce close.
- Outcome over the next 32 bars (8 h): REACHED = level traded before a close back across the BB mid of the pierce bar;
  FAILED = mid close first; NEITHER. Also: max run in the pierce direction in % before the mid close.
"""
import glob, csv, datetime as dt, statistics as st, collections, sys
B = {}
for f in sorted(glob.glob('F:/MTS/data/tom_raw/klines/BTCUSDT-1m-*.csv')):
    for r in csv.reader(open(f)):
        if r[0] == 'open_time': continue
        t = int(r[0]); t = t // 1000 if t > 1e14 else t; t //= 1000; k = t - t % 900
        o, h, l, c, v, tb = float(r[1]), float(r[2]), float(r[3]), float(r[4]), float(r[5]), float(r[9])
        if k in B: x = B[k]; B[k] = [x[0], max(x[1], h), min(x[2], l), c, x[4] + v, x[5] + tb]
        else: B[k] = [o, h, l, c, v, tb]
ts = sorted(B); n = len(ts); C = [B[t][3] for t in ts]
up = [None]*n; lo = [None]*n; mid = [None]*n; bw = [None]*n
for i in range(19, n):
    w = C[i-19:i+1]; m = sum(w)/20; sd = (sum((x-m)**2 for x in w)/20)**.5
    up[i], lo[i], mid[i], bw[i] = m+2*sd, m-2*sd, m, 4*sd/m
dayhl = {}
for t in ts:
    d = t // 86400; h, l = B[t][1], B[t][2]
    dayhl[d] = (max(dayhl[d][0], h), min(dayhl[d][1], l)) if d in dayhl else (h, l)
def fs(y, mo, k):
    d = dt.date(y, mo, 1); d += dt.timedelta((6-d.weekday()) % 7); return d + dt.timedelta(7*(k-1))
def A_of(d):
    dst = fs(d.year, 3, 2) <= d < fs(d.year, 11, 1)
    return int(dt.datetime(d.year, d.month, d.day, 13 if dst else 14, 30, tzinfo=dt.timezone.utc).timestamp())
ev = []; seen = set()
for i in range(2900, n-33):
    t = ts[i]; d = dt.datetime.fromtimestamp(t, dt.timezone.utc).date()
    if d.weekday() > 4 or ts[i+32] - t != 32*900 or ts[i] - ts[i-20] != 20*900: continue
    A = A_of(d)
    if not (A-7200 <= t < A+7200): continue
    side = 'up' if C[i] > up[i] and C[i-1] <= up[i-1] else 'down' if C[i] < lo[i] and C[i-1] >= lo[i-1] else None
    if not side or (d, side) in seen: continue
    seen.add((d, side))
    hist = [x for x in bw[i-2880:i-1] if x]; coil = sum(x < bw[i-1] for x in hist)/len(hist) <= .2
    v = B[t][4]; vr = v / (sum(B[ts[j]][4] for j in range(i-20, i))/20)
    ds = (2*B[t][5]-v)/v * (1 if side == 'up' else -1)
    pd = dayhl.get(t//86400 - 1); lvl = pd[0] if side == 'up' else pd[1] if pd else None
    if side == 'up' and lvl <= C[i] or side == 'down' and lvl >= C[i]: lvl = None
    out = 'NEITHER'; run = 0
    for j in range(i+1, i+33):
        o, h, l, c = B[ts[j]][:4]
        run = max(run, (h/C[i]-1) if side == 'up' else (1-l/C[i]))
        if lvl and (h >= lvl if side == 'up' else l <= lvl): out = 'REACHED'; break
        if (c < mid[i] if side == 'up' else c > mid[i]): out = 'FAILED'; break
    dist = abs(lvl/C[i]-1) if lvl else None
    ev.append(dict(side=side, coil=coil, vr=vr, ds=ds, lvl=lvl is not None, dist=dist, out=out, run=run))
print('pierces', len(ev), 'coil', sum(e['coil'] for e in ev))
def show(lab, E):
    E = [e for e in E if e['lvl']]
    if len(E) < 15: print(f'{lab:40s} n={len(E)} (too few)'); return
    c = collections.Counter(e['out'] for e in E)
    print(f"{lab:40s} n={len(E):4d} REACHED {100*c['REACHED']/len(E):3.0f}% FAILED {100*c['FAILED']/len(E):3.0f}% "
          f"| level dist med {100*st.median(e['dist'] for e in E):.2f}% | run med {100*st.median(e['run'] for e in E):.2f}%")
show('ALL with level beyond', ev)
for s in ('up', 'down'): show(f'{s}', [e for e in ev if e['side'] == s])
for cl in (True, False): show(f'coil={cl}', [e for e in ev if e['coil'] == cl])
vrs = sorted(e['vr'] for e in ev); q1, q2 = vrs[len(vrs)//3], vrs[2*len(vrs)//3]
print(f'force: vol ratio terciles cut at {q1:.2f}x / {q2:.2f}x; median vol ratio {st.median(vrs):.2f}x, median delta share {st.median(e["ds"] for e in ev):+.2f}')
show('vol ratio low tercile', [e for e in ev if e['vr'] < q1])
show('vol ratio mid tercile', [e for e in ev if q1 <= e['vr'] < q2])
show('vol ratio top tercile', [e for e in ev if e['vr'] >= q2])
show('delta with pierce (>+0.10)', [e for e in ev if e['ds'] > .10])
show('delta weak/against (<=+0.10)', [e for e in ev if e['ds'] <= .10])
show('top vol + delta with', [e for e in ev if e['vr'] >= q2 and e['ds'] > .10])
show('level within 0.5%', [e for e in ev if e['dist'] is not None and e['dist'] <= .005])
show('level 0.5-1.5%', [e for e in ev if e['dist'] is not None and .005 < e['dist'] <= .015])
show('level > 1.5%', [e for e in ev if e['dist'] is not None and e['dist'] > .015])
show('coil + top vol + delta with', [e for e in ev if e['coil'] and e['vr'] >= q2 and e['ds'] > .10])
print('-- distance-matched (level 0.5-1.5%)')
M = [e for e in ev if e['dist'] is not None and .005 < e['dist'] <= .015]
show('  top vol + delta with', [e for e in M if e['vr'] >= q2 and e['ds'] > .10])
show('  everything else', [e for e in M if not (e['vr'] >= q2 and e['ds'] > .10)])
show('  coil', [e for e in M if e['coil']]); show('  no coil', [e for e in M if not e['coil']])
