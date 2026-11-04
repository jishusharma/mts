# C31 halves + fee-net + power (card c31-daily-short-from-the-upper-bb-with-t). Fee-net per FORMULAS.md 18.5:
# net_R = (gross_move - fee_in*e - fee_out*x) / risk, taker 0.0005 each side (+ slip 0.0002 RT, FORMULAS section 13). OURS: slip on.
# Rows A = the script's rule (entry = price trades under prior close, stop prev high, target BB middle), SHORT, edge, trend down.
# Rows B = entry = first CLOSE back inside the upper band (after a close above it within the last 3 candles), stop = highest
# high since the walk began, target = BB middle at that candle. Same 20-candle hold, path on 1m. HOLDOUT sealed (END 2025-07-01).
# Run: python c31_halves.py  (asserts the two reference numbers first; exit 1 if they are not reproduced)
import glob,csv,sys,statistics as st,datetime as dt,collections
END=dt.date(2025,7,1); FEE=0.0005; SLIP=0.0002; HOLD=20; k=[]
for f in sorted(glob.glob('F:/MTS/data/tom_raw/klines/BTCUSDT-1m-*.csv')):
    for r in csv.reader(open(f)):
        if r[0]=='open_time':continue
        t=int(r[0]); t=t//1000 if t>1e14 else t; t//=1000
        if dt.datetime.fromtimestamp(t,dt.timezone.utc).date()>=END: break
        k.append((t,float(r[1]),float(r[2]),float(r[3]),float(r[4])))
k.sort()
B=[];cur=None
for t,o,h,l,c in k:
    g=t//86400
    if g!=cur: B.append([g,o,h,l,c,[]]); cur=g
    b=B[-1]; b[2]=max(b[2],h); b[3]=min(b[3],l); b[4]=c; b[5].append((t,o,h,l,c))
n=len(B); mid=[None]*n; up=[None]*n; sma=[None]*n
for i in range(19,n):
    w=[b[4] for b in B[i-19:i+1]]; m=sum(w)/20; sd=(sum((x-m)**2 for x in w)/20)**.5
    mid[i]=m; up[i]=m+2*sd
for i in range(49,n): sma[i]=sum(b[4] for b in B[i-49:i+1])/50
def day(i): return dt.datetime.fromtimestamp(B[i][0]*86400,dt.timezone.utc).date()
def sim(e,stop,target,path):
    """SHORT. returns (hit, gross_R, net_R)."""
    dist=(stop-e)/e; tdist=(e-target)/e
    if dist<=0 or tdist<=0: return None
    hit='none'
    for t,o,h,l,c in path:
        if h>=stop: hit='STOP';break
        if l<=target: hit='TGT';break
    x=stop if hit=='STOP' else target if hit=='TGT' else path[-1][4]
    gross=(e-x)/e/dist; net=gross-(2*FEE+SLIP)/dist
    return hit,gross,net
A=collections.defaultdict(list)   # (rule,trend) -> [(date,hit,gross,net)]
for i in range(50,n-HOLD-1):
    prev=B[i-1]; trend='up' if prev[4]>sma[i-1] else 'down'
    edge=any(B[j][4]>up[j] for j in range(i-3,i))
    # rule A: first 1m bar of candle i trading under the prior close
    ent=None
    for j,(t,o,h,l,c) in enumerate(B[i][5]):
        if l<prev[4]: ent=j;break
    if ent is not None:
        m1=[x for b in B[i:i+HOLD] for x in b[5]]
        r=sim(prev[4],prev[2],mid[i-1],m1[ent+1:])
        if r: A[('A','edge' if edge else 'base',trend)].append((day(i),)+r)
    # rule B: candle i closes back inside the band, one of the last 3 closes above it, the one before i was above
    if B[i][4]<=up[i] and B[i-1][4]>up[i-1]:
        walk=[j for j in range(i-3,i) if B[j][4]>up[j]]
        stop=max(B[j][2] for j in range(walk[0],i+1))
        path=[x for b in B[i+1:i+1+HOLD] for x in b[5]]
        r=sim(B[i][4],stop,mid[i],path)
        t2='up' if B[i][4]>sma[i] else 'down'
        if r: A[('B','edge',t2)].append((day(i),)+r)
def stats(xs):
    N=len(xs)
    if N==0: return 'n=0'
    g=[x[2] for x in xs]; ne=[x[3] for x in xs]; w=sum(1 for x in xs if x[1]=='TGT')
    sd=st.stdev(ne) if N>1 else float('nan')
    return 'n=%3d tgt %3.0f%% grossR %+.2f netR %+.2f sd %.2f'%(N,100*w/N,st.mean(g),st.mean(ne),sd)
def halves(xs):
    h1=[x for x in xs if x[0].year<=2023]; h2=[x for x in xs if x[0].year>=2024]; return h1,h2
# reference gate (fee-free, gross) must match the card
ld=A[('A','edge','down')]; un=A[('A','edge','down')]+A[('A','edge','up')]
ref_ok=(len(ld)==15 and round(100*sum(x[1]=='TGT' for x in ld)/15)==73 and round(st.mean(x[2] for x in ld),2)==1.10
        and len(un)==165 and round(100*sum(x[1]=='TGT' for x in un)/165)==21 and round(st.mean(x[2] for x in un),2)==-0.07)
print('REFERENCE LEAD 73%% +1.10R n=15 and unfiltered 21%% -0.07R n=165 reproduced: %s'%ref_ok)
if not ref_ok: sys.exit(1)
def z(p):  # normal quantiles used: one-sided alpha .05 -> 1.645, power .80 -> 0.842
    return {'a':1.645,'b':0.842}[p]
def need(mean,sd): return float('inf') if mean<=0 else ((z('a')+z('b'))*sd/mean)**2
for key in [('A','edge','down'),('A','edge','up'),('A','base','down'),('B','edge','down'),('B','edge','up')]:
    xs=A[key]; h1,h2=halves(xs)
    print(key,'TOTAL',stats(xs)); print('   2022-23',stats(h1)); print('   2024-25',stats(h2))
    yrs=collections.Counter(x[0].year for x in xs); print('   by year',dict(sorted(yrs.items())))
    if len(xs)>1:
        ne=[x[3] for x in xs]; print('   n needed for observed netR (power .8, 1-sided .05): %.0f; for 0.30R: %.0f'%(need(st.mean(ne),st.stdev(ne)),need(0.30,st.stdev(ne))))
