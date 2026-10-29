"""Pre-US Bollinger contraction -> what the US session does next. Descriptive only, no fees, no edge claim.
Definitions fixed before the first run (all OURS unless noted):
- Data: Binance USD-M BTCUSDT 1m (F:/MTS/data/tom_raw/klines), resampled to 15m, UTC. Weekdays only.
- A = US cash open: 13:30Z during US DST (2nd Sun Mar .. 1st Sun Nov), else 14:30Z.
- Pre-US box = A-8h .. A: box high/low = its high/low.
- BB(20,2) on 15m closes; BandWidth BW = (upper-lower)/mid at the last 15m bar closed at A.
- Squeeze = BW at A in the lowest 20% of the BW values of the prior 30 days (all 15m bars). "Wide" = top 20%.
- Outcome window A .. A+4h. UP = 15m close at A+4h above box high; DOWN = below box low; SIDEWAYS = inside.
  Also: which side of the box broke first, and whether both sides broke (whipsaw); expansion = window range / box range.
- Phase = F6 option A (research/context_factors_2026-10-16/CONTEXT_FACTORS_SPEC.md): last COMPLETED weekly close vs SMA10
  of weekly closes; slope = SMA10 now minus 2 weeks earlier. above&rising markup, above&not rising distribution,
  below&falling markdown, below&not falling accumulation.
"""
import glob, csv, datetime as dt, collections, statistics as st, json, sys
P = 'F:/MTS/data/tom_raw/klines/BTCUSDT-1m-*.csv'
b15 = {}
for f in sorted(glob.glob(P)):
    for r in csv.reader(open(f)):
        if r[0] == 'open_time': continue
        t = int(r[0]); t = t // 1000 if t > 1e14 else t; t //= 1000
        k = t - t % 900; o, h, l, c = map(float, r[1:5])
        if k in b15:
            x = b15[k]; b15[k] = (x[0], max(x[1], h), min(x[2], l), c)
        else: b15[k] = (o, h, l, c)
ts = sorted(b15); idx = {t: i for i, t in enumerate(ts)}
C = [b15[t][3] for t in ts]
bw = [None] * len(ts)
for i in range(19, len(ts)):
    w = C[i-19:i+1]; m = sum(w) / 20; sd = (sum((x-m)**2 for x in w) / 20) ** .5
    bw[i] = 4 * sd / m
def first_sunday(y, mo, nth):
    d = dt.date(y, mo, 1); d += dt.timedelta((6 - d.weekday()) % 7); return d + dt.timedelta(7 * (nth - 1))
def us_open(d):
    dst = first_sunday(d.year, 3, 2) <= d < first_sunday(d.year, 11, 1)
    return dt.datetime(d.year, d.month, d.day, 13 if dst else 14, 30, tzinfo=dt.timezone.utc)
# weekly closes (week ends Sunday 23:59Z) for F6
wk = collections.OrderedDict()
for t in ts:
    d = dt.datetime.fromtimestamp(t, dt.timezone.utc).date(); mon = d - dt.timedelta(d.weekday()); wk[mon] = b15[t][3]
wmons = list(wk); wcl = [wk[m] for m in wmons]
def phase(d):
    mon = d - dt.timedelta(d.weekday()); j = wmons.index(mon) - 1  # last completed week
    if j < 11: return None
    s = lambda k: sum(wcl[k-9:k+1]) / 10
    above = wcl[j] > s(j); rising = s(j) - s(j-2) > 0
    return ('markup' if rising else 'distribution') if above else ('markdown' if not rising else 'accumulation')
rows = []
d0 = dt.datetime.fromtimestamp(ts[0], dt.timezone.utc).date(); d1 = dt.datetime.fromtimestamp(ts[-1], dt.timezone.utc).date()
d = d0
while d <= d1:
    if d.weekday() < 5:
        A = int(us_open(d).timestamp()); a15 = A - A % 900  # A at :30 is a 15m boundary
        box = [b15.get(a15 - 900 * k) for k in range(1, 33)]; win = [b15.get(a15 + 900 * k) for k in range(16)]
        last = idx.get(a15 - 900)
        if None not in box and None not in win and last is not None and last >= 2900 and bw[last]:
            hist = [x for x in bw[last-2880:last] if x]
            pct = sum(x < bw[last] for x in hist) / len(hist)
            bh = max(x[1] for x in box); bl = min(x[2] for x in box); cl = win[-1][3]
            first = None
            for x in win:
                if x[1] > bh and x[2] < bl: first = 'both_same_bar'; break
                if x[1] > bh: first = 'up'; break
                if x[2] < bl: first = 'down'; break
            both = max(x[1] for x in win) > bh and min(x[2] for x in win) < bl
            out = 'UP' if cl > bh else 'DOWN' if cl < bl else 'SIDEWAYS'
            exp = (max(x[1] for x in win) - min(x[2] for x in win)) / (bh - bl)
            rows.append(dict(d=str(d), pct=pct, grp='squeeze' if pct <= .2 else 'wide' if pct >= .8 else 'mid',
                             out=out, first=first, both=both, exp=exp, ph=phase(d), boxpct=(bh-bl)/bl))
    d += dt.timedelta(1)
json.dump(rows, open(sys.argv[1] if len(sys.argv) > 1 else 'rows.json', 'w'))
def show(lab, R):
    n = len(R)
    if n < 10: print(f'{lab:32s} n={n} (too few)'); return
    c = collections.Counter(r['out'] for r in R); f = [r for r in R if r['first'] in ('up', 'down')]
    held = sum((r['first'] == 'up' and r['out'] == 'UP') or (r['first'] == 'down' and r['out'] == 'DOWN') for r in f)
    print(f"{lab:32s} n={n:4d} UP {100*c['UP']/n:3.0f}% DOWN {100*c['DOWN']/n:3.0f}% SIDE {100*c['SIDEWAYS']/n:3.0f}% | "
          f"broke both {100*sum(r['both'] for r in R)/n:3.0f}% | first break held {100*held/max(1,len(f)):3.0f}% | "
          f"expansion median {st.median(r['exp'] for r in R):.2f}x")
for g in ('squeeze', 'mid', 'wide'): show('BW ' + g, [r for r in rows if r['grp'] == g])
show('ALL', rows)
for ph in ('markup', 'distribution', 'markdown', 'accumulation'):
    for g in ('squeeze', 'wide'): show(f'{ph} / {g}', [r for r in rows if r['ph'] == ph and r['grp'] == g])
    show(f'{ph} / all', [r for r in rows if r['ph'] == ph])
for y in ('2022', '2023', '2024', '2025', '2026'): show(f'{y} squeeze', [r for r in rows if r['d'][:4] == y and r['grp'] == 'squeeze'])
