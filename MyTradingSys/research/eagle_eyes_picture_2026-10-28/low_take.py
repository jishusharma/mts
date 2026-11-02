# OURS: weekdays, from 14:45Z: how often does the low over the rest of the US session (to 16:30Z, to 21:00Z) reach d% below the 14:45Z price?
# Conditioned on today's shape: 14:45Z price below the 00Z open and the day low (00Z..14:45Z) 0.2-0.6% below price. 2022-01-01..2025-06-30.
import glob,csv,datetime as dt,collections
END=dt.date(2025,7,1); days=collections.defaultdict(dict)
for f in sorted(glob.glob('F:/MTS/data/tom_raw/klines/BTCUSDT-1m-*.csv')):
    for r in csv.reader(open(f)):
        if r[0]=='open_time':continue
        t=int(r[0]); t=t//1000 if t>1e14 else t; t//=1000
        d=dt.datetime.fromtimestamp(t,dt.timezone.utc)
        if d.date()>=END: break
        if d.weekday()>4: continue
        days[d.date()][d.hour*60+d.minute]=(float(r[1]),float(r[3]))
D=[0.0017,0.0036,0.006,0.012]; hit={w:collections.Counter() for w in (990,1260)}; n=0; dl=collections.Counter()
for d,m in days.items():
    if len(m)<1400 or 885 not in m or 0 not in m: continue
    px=m[885][0]; o=m[0][0]; L=min(m[i][1] for i in m if i<=885)
    if px>=o or not (0.002<=px/L-1<=0.006): continue
    n+=1
    for w in hit:
        lo=min(m[i][1] for i in m if 885<i<=w)
        for dd in D:
            if lo<=px*(1-dd): hit[w][dd]+=1
        if lo<L: dl[w]+=1
print('days n=%d'%n)
for w in hit:
    print('by %02d:%02dZ: '%(w//60,w%60)+'  '.join('%.2f%% below: %2.0f%%'%(100*dd,100*hit[w][dd]/n) for dd in D)+'  | day low taken: %2.0f%%'%(100*dl[w]/n))
