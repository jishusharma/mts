import sys; sys.path.insert(0,'.')
from anatomy import *
TMP='C:/Users/E-ngineers/AppData/Local/Temp/'
d=pd.read_pickle(TMP+'d.pkl');h=pd.read_pickle(TMP+'h.pkl'); rng=np.random.default_rng(11)
fallrec=d.fall.rolling(10,min_periods=1).max().astype(bool).values
low30=d.l.rolling(30).min().shift(1).values; hi20=d.h.rolling(20).max().shift(1).values
c=d.c.values
ev={'C1c':[],'C2c':[],'C4c':[],'C3c':[]}
last={k:-99 for k in ev}
for j in range(210,len(d)):
    if not fallrec[j] or np.isnan(low30[j]): continue
    conds={'C1c':c[j]>hi20[j],'C2c':c[j]>d.sma20.iloc[j] and c[j-1]<=d.sma20.iloc[j-1],
           'C4c':d.wt1.iloc[j]>d.wt2.iloc[j] and d.wt1.iloc[j-1]<=d.wt2.iloc[j-1] and d.wt1.iloc[j]<-53}
    for k,v in conds.items():
        if v and j-last[k]>=10: ev[k].append(('d',j)); last[k]=j
# 4H C3c
dayfall=pd.Series(fallrec,index=d.dt.values); hf=h.dt.dt.normalize().map(dayfall).fillna(False).values
H=h.h.values;Lw=h.l.values;Cc=h.c.values; low30h=h.l.rolling(180).min().shift(1).values
swh=None;swl=None;lastk=-999
for m in range(210,len(h)):
    a=m-3
    if H[a]>H[a-3:a].max() and H[a]>H[a+1:m+1].max(): swh=H[a]
    if Lw[a]<Lw[a-3:a].min() and Lw[a]<Lw[a+1:m+1].min(): swl=Lw[a]
    if swh and swl and hf[m] and not np.isnan(low30h[m]) and swl>low30h[m] and Cc[m]>swh and Cc[m-1]<=swh and m-lastk>=60:
        ev['C3c'].append(('h',m)); lastk=m
def run(df,j,low30arr,tg):
    ent=df.c.iloc[j]; stop=0.95*low30arr[j]
    if ent<=stop: return None
    return outcome(df,j,ent,stop,tg,180 if df is d else 180*6)+(ent/low30arr[j]-1,)
def report(name,evs,df,l30):
    for tag,sel in [('ALL',lambda t:True),('DEV',lambda t:t<=pd.Timestamp('2023-12-31')),('VAL',lambda t:t>pd.Timestamp('2023-12-31'))]:
        o={}
        for tg in (0.10,0.20):
            R=[run(df,j,l30,tg) for k,j in evs if sel(df.dt.iloc[j])]; R=[r for r in R if r and r[0]>=0]
            if not R: o[tg]=None;continue
            hit=np.array([r[0]==1 for r in R],float); net=np.mean([r[1] for r in R]); prem=np.median([r[2] for r in R])
            o[tg]=(len(R),round(hit.mean(),3),tuple(np.round(boot(hit,rng),2)),round(net,4),round(prem*100,1))
        print(name,tag,o)
for k in ['C1c','C2c','C4c']: report(k,ev[k],d,low30)
report('C3c',ev['C3c'],h,low30h)
# matched placebo on daily
for tg in (0.10,0.20):
    rows=[]
    for j in range(210,len(d)-181):
        if fallrec[j] and not np.isnan(low30[j]):
            r=run(d,j,low30,tg)
            if r and r[0]>=0: rows.append((r[2],r[0]==1,r[1],d.dt.iloc[j]))
    Q=pd.DataFrame(rows,columns=['prem','hit','net','dt'])
    for lo,hi in [(0,.08),(.08,.15),(.15,.25),(.25,2)]:
        q=Q[(Q.prem>=lo)&(Q.prem<hi)]; print('placebo',tg,lo,hi,len(q),round(q.hit.mean(),3),round(q.net.mean(),4),'VAL',round(q[q.dt>'2023-12-31'].hit.mean(),3),len(q[q.dt>'2023-12-31']))
print({k:len(v) for k,v in ev.items()})
