# OURS: a GREEN bar (close>open) whose taker delta is NEGATIVE (taker buy < taker sell): hidden selling?
# Outcome: in the next 12 bars, is the bar's low broken before its high (L first) or the high before the low (H first)?
# Also the 12-bar return. Compared with green bars with positive delta. Context 'bounce': a 60-bar low was set within the last 5 bars.
# Timeframes 1m, 5m, 15m from Binance 1m klines. Window 2022-01-01..2025-06-30 (HOLDOUT from 2025-07-01 sealed). Descriptive, no fees.
import glob,csv,collections,statistics as st,datetime as dt
END=dt.date(2025,7,1); k=[]
for f in sorted(glob.glob('F:/MTS/data/tom_raw/klines/BTCUSDT-1m-*.csv')):
    for r in csv.reader(open(f)):
        if r[0]=='open_time':continue
        t=int(r[0]); t=t//1000 if t>1e14 else t; t//=1000
        if dt.datetime.fromtimestamp(t,dt.timezone.utc).date()>=END: break
        k.append((t,float(r[1]),float(r[2]),float(r[3]),float(r[4]),float(r[5]),float(r[9])))
def agg(n):
    out=[]
    for i in range(0,len(k)-n+1,n):
        w=k[i:i+n]
        if w[-1][0]-w[0][0]!=60*(n-1): continue
        out.append(dict(t=w[0][0],o=w[0][1],h=max(x[2] for x in w),l=min(x[3] for x in w),c=w[-1][4],d=sum(2*x[6]-x[5] for x in w)))
    return out
def study(name,b):
    res=collections.defaultdict(list)
    for i in range(60,len(b)-12):
        x=b[i]
        if x['c']<=x['o']: continue
        bounce=min(y['l'] for y in b[i-4:i+1])<=min(y['l'] for y in b[i-60:i-4])
        first=None
        for y in b[i+1:i+13]:
            if y['l']<x['l']: first='L';break
            if y['h']>x['h']: first='H';break
        ret=b[i+12]['c']/x['c']-1
        key=('neg' if x['d']<0 else 'pos')
        res[key].append((first,ret));
        if bounce: res[key+'@bounce'].append((first,ret))
    for key in ['pos','neg','pos@bounce','neg@bounce']:
        xs=res[key]; n=len(xs); c=collections.Counter(f for f,_ in xs)
        print('%-4s green bar, delta %-11s n=%7d  low broken first %2.0f%%  high first %2.0f%%  12-bar ret med %+.3f%%  up %2.0f%%'%(name,key,n,100*c['L']/n,100*c['H']/n,100*st.median(r for _,r in xs),100*sum(r>0 for _,r in xs)/n))
print('1m bars',len(k),dt.datetime.fromtimestamp(k[0][0],dt.timezone.utc).date(),'..',dt.datetime.fromtimestamp(k[-1][0],dt.timezone.utc).date())
for name,n in [('1m',1),('5m',5),('15m',15)]: study(name,agg(n))
