# OURS: 1h WaveTrend (LazyBear, n1=10 n2=21) crossing down through 0 after wt1>=50 within the prior 12 bars, with RSI14<40 on the same bar.
# Next 6h / 12h: return, low-first vs high-first, further drop. 2022-01-01..2025-06-30. Descriptive.
import glob,csv,datetime as dt,statistics as st,collections
END=dt.date(2025,7,1); b={}
for f in sorted(glob.glob('F:/MTS/data/tom_raw/klines/BTCUSDT-1m-*.csv')):
    for r in csv.reader(open(f)):
        if r[0]=='open_time':continue
        t=int(r[0]); t=t//1000 if t>1e14 else t; t//=1000
        if dt.datetime.fromtimestamp(t,dt.timezone.utc).date()>=END: break
        k=t//3600*3600; o,h,l,c=float(r[1]),float(r[2]),float(r[3]),float(r[4]); x=b.get(k)
        if x is None: b[k]=[o,h,l,c]
        else: x[1]=max(x[1],h); x[2]=min(x[2],l); x[3]=c
ts=sorted(b); H=[b[t] for t in ts]
def ema(xs,n):
    a=2/(n+1); out=[xs[0]]
    for v in xs[1:]: out.append(a*v+(1-a)*out[-1])
    return out
ap=[(x[1]+x[2]+x[3])/3 for x in H]; esa=ema(ap,10); d=ema([abs(a-e) for a,e in zip(ap,esa)],10)
ci=[(a-e)/(0.015*dd) if dd else 0 for a,e,dd in zip(ap,esa,d)]; wt1=ema(ci,21)
cl=[x[3] for x in H]; g=[0.0]; L=[0.0]
for i in range(1,len(cl)):
    ch=cl[i]-cl[i-1]; g.append(max(ch,0)); L.append(max(-ch,0))
ag=ema(g,27); al=ema(L,27)  # Wilder 14 ~ ema 27
rsi=[100-100/(1+(a/b_)) if b_ else 100 for a,b_ in zip(ag,al)]
res=[];base=[]
for i in range(30,len(ts)-13):
    if ts[i+12]-ts[i]!=12*3600: continue
    cond=wt1[i]<0<=wt1[i-1] and max(wt1[i-12:i])>=50 and rsi[i]<40
    o,h,l,c=H[i]; fwd=H[i+1:i+13]
    first=None
    for y in fwd:
        if y[2]<l: first='L';break
        if y[1]>h: first='H';break
    rec=(first,fwd[5][3]/c-1,fwd[11][3]/c-1,min(y[2] for y in fwd)/c-1)
    (res if cond else base).append(rec)
for name,xs in (('WT1h cross<0 from>=50, RSI<40',res),('all 1h bars',base)):
    n=len(xs); cnt=collections.Counter(x[0] for x in xs)
    print('%-32s n=%6d  low first %2.0f%%  high first %2.0f%%  6h ret med %+.2f%% up %2.0f%%  12h ret med %+.2f%% up %2.0f%%  12h max drop med %+.2f%%'%(name,n,100*cnt['L']/n,100*cnt['H']/n,100*st.median(x[1] for x in xs),100*sum(x[1]>0 for x in xs)/n,100*st.median(x[2] for x in xs),100*sum(x[2]>0 for x in xs)/n,100*st.median(x[3] for x in xs)))
