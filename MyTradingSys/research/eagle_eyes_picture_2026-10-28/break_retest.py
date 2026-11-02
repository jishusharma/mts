# OURS: range break and retest on 1m. L = lowest low of the prior 60 bars. Break: a 1m close below L.
# Retest: within 20 bars the high comes back to L (>= L*(1-0.0002)) before any close above L. Reclaim-early: a close above L before any retest.
# After the retest bar: within 30 bars, new low below the break low (REJECT) or a close above L (RECLAIM), or neither.
# Mirror for range highs (break up, retest from above). 2022-01-01..2025-06-30 (HOLDOUT sealed). Descriptive, no fees.
import glob,csv,collections,datetime as dt
END=dt.date(2025,7,1); k=[]
for f in sorted(glob.glob('F:/MTS/data/tom_raw/klines/BTCUSDT-1m-*.csv')):
    for r in csv.reader(open(f)):
        if r[0]=='open_time':continue
        t=int(r[0]); t=t//1000 if t>1e14 else t; t//=1000
        if dt.datetime.fromtimestamp(t,dt.timezone.utc).date()>=END: break
        k.append((t,float(r[1]),float(r[2]),float(r[3]),float(r[4])))
def run(sign):
    # sign=-1: break down (use lows); sign=+1: break up (mirror by negating prices)
    o=[(t,sign*op,sign*(lo if sign>0 else hi)*0+ (sign*hi if sign>0 else sign*lo), (sign*lo if sign>0 else sign*hi), sign*c) for t,op,hi,lo,c in k] if False else None
    P=[(t,-op,-lo,-hi,-c) if sign>0 else (t,op,hi,lo,c) for t,op,hi,lo,c in k]  # for breaks up, flip so 'low' logic applies
    out=collections.Counter(); i=60; last_break=-999
    while i<len(P)-60:
        t,op,hi,lo,c=P[i]
        if P[i][0]-P[i-60][0]!=3600: i+=1; continue
        L=min(x[3] for x in P[i-60:i])
        if c<L and i-last_break>30:
            last_break=i; blow=lo; retest=None
            for j in range(i+1,i+21):
                if P[j][4]>L: out['reclaim before any retest']+=1; break
                blow=min(blow,P[j][3])
                if P[j][2]>=L*(1-0.0002): retest=j; break
            else:
                out['no retest, no reclaim in 20']+=1
            if retest:
                res='neither in 30'
                for j in range(retest+1,retest+31):
                    if P[j][3]<blow: res='REJECT: new low below the break low'; break
                    if P[j][4]>L: res='RECLAIM: close back above the level'; break
                out[res]+=1
            i+=1
        else: i+=1
    n=sum(out.values()); print('%s breaks n=%d'%('DOWN' if sign<0 else 'UP (mirrored)',n))
    rt=sum(v for key,v in out.items() if key.startswith(('REJECT','RECLAIM','neither')))
    for key,v in sorted(out.items(),key=lambda x:-x[1]):
        extra='  (%2.0f%% of retests)'%(100*v/rt) if key.startswith(('REJECT','RECLAIM','neither')) else ''
        print('  %-42s %6d  %2.0f%%%s'%(key,v,100*v/n,extra))
print('1m bars',len(k))
run(-1); run(+1)
