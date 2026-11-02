# OURS: 5m bar with an OI jump (top 2% of 5m OI changes, positive) and positive taker delta but price going nowhere
# (|close/open-1| < 0.05%): aggressive longs absorbed. Outcome next 12 bars (60 min): return, and whether the bar's low
# or high is broken first. Compared with the same OI jump when price did follow (bar up >= 0.15%).
# Data: Binance 1m klines + 5m metrics, 2022-01-01..2025-06-30 (HOLDOUT sealed). Descriptive, no fees.
import glob,csv,collections,statistics as st,datetime as dt
END=dt.date(2025,7,1); k={}
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
        t=int(dt.datetime.strptime(r['create_time'],'%Y-%m-%d %H:%M:%S').replace(tzinfo=dt.timezone.utc).timestamp()); oi[t]=float(r['sum_open_interest'])
b5={}
for t0 in range(min(k)//300*300,max(k),300):
    m=[k[t] for t in range(t0,t0+300,60) if t in k]
    if len(m)<5 or not oi.get(t0) or not oi.get(t0+300): continue
    b5[t0]=dict(o=m[0][0],h=max(x[1] for x in m),l=min(x[2] for x in m),c=m[-1][3],d=sum(2*x[5]-x[4] for x in m),doi=oi[t0+300]/oi[t0]-1)
ts=sorted(b5); thr=sorted(b5[t]['doi'] for t in ts)[int(0.98*len(ts))]
print('5m bars',len(ts),'OI-jump threshold %+.3f%%'%(100*thr))
res=collections.defaultdict(list)
for t in ts:
    x=b5[t]
    if x['doi']<thr or x['d']<=0: continue
    fwd=[t+300*j for j in range(1,13)]
    if any(f not in b5 for f in fwd): continue
    chg=x['c']/x['o']-1
    key='absorbed (|bar|<0.05%)' if abs(chg)<0.0005 else ('followed (bar up>=0.15%)' if chg>=0.0015 else None)
    if not key: continue
    first=None
    for f in fwd:
        y=b5[f]
        if y['l']<x['l']: first='L';break
        if y['h']>x['h']: first='H';break
    res[key].append((first,b5[fwd[-1]]['c']/x['c']-1,min(b5[f]['l'] for f in fwd)/x['c']-1))
for key,xs in res.items():
    n=len(xs); c=collections.Counter(f for f,_,_ in xs)
    print('OI jump + buy delta, %-26s n=%5d  bar low broken first %2.0f%%  high first %2.0f%%  60m ret med %+.2f%%  up %2.0f%%  60m max drawdown med %+.2f%%'%(key,n,100*c['L']/n,100*c['H']/n,100*st.median(r for _,r,_ in xs),100*sum(r>0 for _,r,_ in xs)/n,100*st.median(d for _,_,d in xs)))
