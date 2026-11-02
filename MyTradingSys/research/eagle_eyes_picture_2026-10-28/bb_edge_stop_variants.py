# OURS (operator 2026-11-03 "devise a better stop"): same 1D setup as bb_edge_candle_rule.py (one of the last 3 closes
# beyond the BB(20,2) band, price trades through the prior close), target = middle band, hold 20 candles, 1m-ordered paths.
# Stops compared: prior candle extreme; 5- and 10-candle swing extreme; the band itself; 1x/2x ATR14; the extreme of the
# highest-volume candle of the last 10 (Tom/Fabio "level where a lot traded": leaving it = out); 20-candle extreme.
# Fee-free, 2022-01-01..2025-06-30, HOLDOUT sealed. R = target distance / stop distance on a hit, -1 on a stop.
import glob,csv,statistics as st,datetime as dt,collections
END=dt.date(2025,7,1); k=[]
for f in sorted(glob.glob('F:/MTS/data/tom_raw/klines/BTCUSDT-1m-*.csv')):
    for r in csv.reader(open(f)):
        if r[0]=='open_time':continue
        t=int(r[0]); t=t//1000 if t>1e14 else t; t//=1000
        if dt.datetime.fromtimestamp(t,dt.timezone.utc).date()>=END: break
        k.append((t,float(r[1]),float(r[2]),float(r[3]),float(r[4]),float(r[5])))
k.sort(); B=[]; cur=None
for t,o,h,l,c,v in k:
    g=t//86400
    if g!=cur: B.append([g,o,h,l,c,0.0,[]]); cur=g
    b=B[-1]; b[2]=max(b[2],h); b[3]=min(b[3],l); b[4]=c; b[5]+=v; b[6].append((t,o,h,l,c))
n=len(B); mid=[None]*n; up=[None]*n; lo=[None]*n; sma=[None]*n; atr=[None]*n
for i in range(19,n):
    w=[b[4] for b in B[i-19:i+1]]; m=sum(w)/20; sd=(sum((x-m)**2 for x in w)/20)**.5; mid[i]=m; up[i]=m+2*sd; lo[i]=m-2*sd
    atr[i]=sum(max(B[j][2]-B[j][3],abs(B[j][2]-B[j-1][4]),abs(B[j][3]-B[j-1][4])) for j in range(i-13,i+1))/14
for i in range(49,n): sma[i]=sum(b[4] for b in B[i-49:i+1])/50
HOLD=20; res=collections.defaultdict(list)
for i in range(50,n-HOLD-1):
    prev=B[i-1]; e=prev[4]; trend='down' if e<sma[i-1] else 'up'
    hv=max(range(i-10,i),key=lambda j:B[j][5])
    for side,cond,target in (('SHORT',any(B[j][4]>up[j] for j in range(i-3,i)),mid[i-1]),('LONG',any(B[j][4]<lo[j] for j in range(i-3,i)),mid[i-1])):
        if not cond: continue
        if (side=='SHORT' and target>=e) or (side=='LONG' and target<=e): continue
        ent=next((j for j,(t,o,h,l,c) in enumerate(B[i][6]) if (l<e if side=='SHORT' else h>e)),None)
        if ent is None: continue
        path=B[i][6][ent+1:]+[x for b in B[i+1:i+HOLD] for x in b[6]]
        ext=(lambda js:max(B[j][2] for j in js)) if side=='SHORT' else (lambda js:min(B[j][3] for j in js))
        stops={'prior candle':ext([i-1]),'5-candle swing':ext(range(i-5,i)),'10-candle swing':ext(range(i-10,i)),'20-candle swing':ext(range(i-20,i)),
               'the band itself':up[i-1] if side=='SHORT' else lo[i-1],'1x ATR14':e+atr[i-1]*(1 if side=='SHORT' else -1),'2x ATR14':e+2*atr[i-1]*(1 if side=='SHORT' else -1),
               'high-volume candle (10)':ext([hv])}
        for sname,stop in stops.items():
            dist=abs(stop-e)/e; tdist=abs(target-e)/e
            if (stop<=e if side=='SHORT' else stop>=e): continue  # stop must sit beyond the entry
            hit='none'
            for t,o,h,l,c in path:
                if side=='SHORT':
                    if h>=stop: hit='STOP';break
                    if l<=target: hit='TGT';break
                else:
                    if l<=stop: hit='STOP';break
                    if h>=target: hit='TGT';break
            R=tdist/dist if hit=='TGT' else (-1.0 if hit=='STOP' else ((e-path[-1][4]) if side=='SHORT' else (path[-1][4]-e))/e/dist)
            for tr in (trend,'all'): res[(side,sname,tr)].append((hit,dist,R))
print('1D candles',n)
for key in sorted(res,key=lambda x:(x[0],x[2],-st.mean(R for _,_,R in res[x]))):
    xs=res[key]; N=len(xs); c=collections.Counter(h for h,_,_ in xs)
    print('%-5s trend=%-4s stop=%-24s n=%3d  stop dist med %.2f%%  middle first %3.0f%%  stopped %3.0f%%  neither %3.0f%%  mean R %+.2f'%(
        key[0],key[2],key[1],N,100*st.median(d for _,d,_ in xs),100*c['TGT']/N,100*c['STOP']/N,100*c['none']/N,st.mean(R for _,_,R in xs)))
