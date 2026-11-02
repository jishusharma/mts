# OURS: 5m bars. Pattern at bar t: impulse close[t]/close[t-9]-1 >= +0.25% (45 min), then last 3 bars (15 min)
# flat-to-down (-0.15%..+0.05%), OI[t]-OI[t-3] > 0, CVD over last 3 bars < 0 (taker buy - taker sell).
# Outcomes next 12 bars (60 min): return, impulse-high (max high of last 12 bars) vs impulse-low (min low) first.
# Data: Binance 1m klines + 5m metrics (sum_open_interest). Window 2022-01-01..2025-06-30 (HOLDOUT from 2025-07-01 sealed).
# Also: median 1h range by UTC hour (US cash open 13:30Z summer / 14:30Z winter). Descriptive, no fees.
import glob,csv,collections,statistics as st,datetime as dt
END=dt.date(2025,7,1)
k={}
for f in sorted(glob.glob('F:/MTS/data/tom_raw/klines/BTCUSDT-1m-*.csv')):
    for r in csv.reader(open(f)):
        if r[0]=='open_time':continue
        t=int(r[0]); t=t//1000 if t>1e14 else t; t//=1000
        if dt.datetime.fromtimestamp(t,dt.timezone.utc).date()>=END: break
        k[t]=(float(r[1]),float(r[2]),float(r[3]),float(r[4]),float(r[5]),float(r[9]))
oi={}
for f in sorted(glob.glob('F:/MTS/data/binance_metrics/BTCUSDT-metrics-*.csv')):
    if f[-14:-4]>=str(END): break
    for r in csv.DictReader(open(f)):
        t=int(dt.datetime.strptime(r['create_time'],'%Y-%m-%d %H:%M:%S').replace(tzinfo=dt.timezone.utc).timestamp())
        oi[t]=float(r['sum_open_interest'])
# 5m bars
b5={}
for t0 in range(min(k)//300*300,max(k),300):
    m=[k[t] for t in range(t0,t0+300,60) if t in k]
    if len(m)<5: continue
    b5[t0]=dict(o=m[0][0],h=max(x[1] for x in m),l=min(x[2] for x in m),c=m[-1][3],cvd=sum(2*x[5]-x[4] for x in m))
ts=sorted(b5); idx={t:i for i,t in enumerate(ts)}
ev=[]
for i in range(12,len(ts)-12):
    t=ts[i]
    if ts[i-12]!=t-3600 or t not in oi or t-900 not in oi: continue
    fwd=[t+300*j for j in range(1,13)]  # outcome window, by time, evaluated only after the condition is fixed
    if any(x not in b5 for x in fwd): continue
    c=b5[t]['c']; imp=c/b5[ts[i-9]]['c']-1; flat=c/b5[ts[i-3]]['c']-1
    if imp<0.0025 or not(-0.0015<=flat<=0.0005): continue
    doi=oi[t]-oi[t-900]; cvd=sum(b5[ts[j]]['cvd'] for j in range(i-2,i+1))
    H=max(b5[ts[j]]['h'] for j in range(i-11,i+1)); L=min(b5[ts[j]]['l'] for j in range(i-11,i+1))
    first=None;mx=mn=0
    for tf_ in fwd:
        x=b5[tf_]; mx=max(mx,x['h']/c-1); mn=min(mn,x['l']/c-1)
        if first is None:
            if x['h']>H: first='H'
            elif x['l']<L: first='L'
    hr=(t%86400)/3600
    ev.append(dict(t=t,hr=hr,oi_up=doi>0,cvd_dn=cvd<0,first=first,ret=b5[fwd[-1]]['c']/c-1,mx=mx,mn=mn))
def rep(name,xs):
    n=len(xs)
    if n<5: print('%-40s n=%d'%(name,n));return
    cnt=collections.Counter(x['first'] for x in xs)
    print('%-40s n=%4d  H first %2.0f%%  L first %2.0f%%  neither %2.0f%%  60m ret med %+.2f%% up %2.0f%%  max up med %+.2f%% max dn med %+.2f%%'%(
        name,n,100*cnt['H']/n,100*cnt['L']/n,100*cnt[None]/n,100*st.median([x['ret'] for x in xs]),100*sum(x['ret']>0 for x in xs)/n,
        100*st.median([x['mx'] for x in xs]),100*st.median([x['mn'] for x in xs])))
print('5m bars',len(ts),dt.datetime.fromtimestamp(ts[0],dt.timezone.utc).date(),'..',dt.datetime.fromtimestamp(ts[-1],dt.timezone.utc).date(),'oi pts',len(oi))
rep('impulse+flat, any OI/CVD',ev)
rep('  OI up & CVD down (today)',[x for x in ev if x['oi_up'] and x['cvd_dn']])
rep('  OI up & CVD up',[x for x in ev if x['oi_up'] and not x['cvd_dn']])
rep('  OI down & CVD down',[x for x in ev if not x['oi_up'] and x['cvd_dn']])
rep('  OI down & CVD up',[x for x in ev if not x['oi_up'] and not x['cvd_dn']])
pre=[x for x in ev if 12<=x['hr']<13.5]
rep('12:00-13:30Z only, any',pre)
rep('  12:00-13:30Z OI up & CVD down',[x for x in pre if x['oi_up'] and x['cvd_dn']])
# hourly range profile (1h range / close) by UTC hour, weekdays, split by US DST
rngs=collections.defaultdict(list)
for t0 in range(ts[0]//3600*3600,ts[-1],3600):
    m=[b5[t] for t in range(t0,t0+3600,300) if t in b5]
    if len(m)<12: continue
    d=dt.datetime.fromtimestamp(t0,dt.timezone.utc)
    if d.weekday()>=5: continue
    # US DST: second Sunday March .. first Sunday November
    y=d.year; mar=dt.date(y,3,8)+dt.timedelta((6-dt.date(y,3,8).weekday())%7); nov=dt.date(y,11,1)+dt.timedelta((6-dt.date(y,11,1).weekday())%7)
    dst=mar<=d.date()<nov
    rngs[(dst,d.hour)].append((max(x['h'] for x in m)-min(x['l'] for x in m))/m[-1]['c'])
print('median 1h range %% by UTC hour (weekdays)  DST=summer (US open 13:30Z) / STD=winter (US open 14:30Z)')
for h in range(10,18):
    print('  %02dZ  summer %.2f%% (n=%d)   winter %.2f%% (n=%d)'%(h,100*st.median(rngs[(True,h)]),len(rngs[(True,h)]),100*st.median(rngs[(False,h)]),len(rngs[(False,h)])))
