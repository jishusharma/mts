# OURS: overnight window 00:00-12:59Z (H,L); P0 = 13:00Z open. Event: H made after 03:00Z and giveback (H-P0)/(H-L) >= 0.5.
# Outcomes in US window 13:00-19:59Z: first touch of H or L, neither; close 20:00Z vs P0. Descriptive, no fees.
import glob,csv,collections,statistics as st,datetime as dt
bars={}
for f in sorted(glob.glob('F:/MTS/data/tom_raw/klines/BTCUSDT-1m-*.csv')):
    for r in csv.reader(open(f)):
        if r[0]=='open_time':continue
        t=int(r[0]); t=t//1000 if t>1e14 else t
        bars[t//1000]=(float(r[1]),float(r[2]),float(r[3]),float(r[4]))
days=sorted({t//86400 for t in bars})
def rng(a,b): return [(t,bars[t]) for t in range(a,b,60) if t in bars]
ev=[];allm=[]
for d in days:
    s=d*86400; ov=rng(s,s+13*3600); us=rng(s+13*3600,s+20*3600)
    if len(ov)<700 or len(us)<380 or (s+13*3600) not in bars: continue
    H=max(b[1] for _,b in ov); tH=[t for t,b in ov if b[1]==H][0]; L=min(b[2] for _,b in ov); P0=bars[s+13*3600][0]; C=us[-1][1][3]
    if H==L: continue
    gb=(H-P0)/(H-L); wd=dt.date.fromordinal(dt.date(1970,1,1).toordinal()+d).weekday()
    first=None
    for _,b in us:
        if b[1]>H: first='H';break
        if b[2]<L: first='L';break
    rec=dict(wd=wd,gb=gb,first=first,ret=C/P0-1,late=(tH-s)>=3*3600)
    allm.append(rec)
    if rec['late'] and gb>=0.5: ev.append(rec)
def rep(name,xs):
    n=len(xs); c=collections.Counter(x['first'] for x in xs)
    print('%-22s n=%3d  takes H first %3d (%2.0f%%)  takes L first %3d (%2.0f%%)  neither %3d  US ret median %+.2f%% up %2.0f%%'%(name,n,c['H'],100*c['H']/n,c['L'],100*c['L']/n,c[None],100*st.median([x['ret'] for x in xs]),100*sum(x['ret']>0 for x in xs)/n))
print('days',len(allm),days[0] and dt.date.fromordinal(dt.date(1970,1,1).toordinal()+days[0]),'..',dt.date.fromordinal(dt.date(1970,1,1).toordinal()+days[-1]))
rep('all days',allm); rep('event (late H, gb>=.5)',ev); rep('event Mondays',[x for x in ev if x['wd']==0]); rep('all Mondays',[x for x in allm if x['wd']==0])
rep('event gb>=.8',[x for x in ev if x['gb']>=0.8])
