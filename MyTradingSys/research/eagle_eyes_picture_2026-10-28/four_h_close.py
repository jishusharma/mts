# OURS: 4h bars (UTC 0/4/8/12/16/20, from 1m) that (a) close in the bottom 20% of their range, (b) range >= 0.8%, (c) make a new low below the prior 24h low.
# Next 4h bar: direction, low-first vs high-first, median low extension. 2022-01-01..2025-06-30. Descriptive.
import glob,csv,datetime as dt,collections,statistics as st
END=dt.date(2025,7,1); b={}
for f in sorted(glob.glob('F:/MTS/data/tom_raw/klines/BTCUSDT-1m-*.csv')):
    for r in csv.reader(open(f)):
        if r[0]=='open_time':continue
        t=int(r[0]); t=t//1000 if t>1e14 else t; t//=1000
        if dt.datetime.fromtimestamp(t,dt.timezone.utc).date()>=END: break
        k=t//14400*14400; o,h,l,c=float(r[1]),float(r[2]),float(r[3]),float(r[4])
        x=b.get(k)
        if x is None: b[k]=[o,h,l,c]
        else: x[1]=max(x[1],h); x[2]=min(x[2],l); x[3]=c
ts=sorted(b); n=0; up=0; lf=0; hf=0; ext=[]; ret=[]
for i in range(7,len(ts)-1):
    t=ts[i]; o,h,l,c=b[t]
    if ts[i+1]-t!=14400: continue
    rng=h/l-1
    if rng<0.008 or (c-l)/(h-l)>0.2: continue
    if l>=min(b[ts[j]][2] for j in range(i-6,i)): continue
    n+=1; no,nh,nl,nc=b[ts[i+1]]
    up+=nc>c; ext.append(nl/l-1); ret.append(nc/c-1)
    # which first: use 1m? approximate with next bar: if nl<l and nh<=h -> low first-ish. count low broken
    lf+=nl<l
print('4h bars n=%d (close bottom 20%%, range>=0.8%%, new 24h low)'%n)
print('next 4h: closes higher %2.0f%%  median ret %+.2f%%  breaks this bar low %2.0f%%  median low ext %+.2f%%  p25 %+.2f%%'%(100*up/n,100*st.median(ret),100*lf/n,100*st.median(ext),100*sorted(ext)[n//4]))
