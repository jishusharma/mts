import sys; sys.path.insert(0,'.')
from anatomy import *
TMP='C:/Users/E-ngineers/AppData/Local/Temp/'
d=pd.read_pickle(TMP+'d.pkl');h=pd.read_pickle(TMP+'h.pkl');P=pd.read_pickle(TMP+'P.pkl');E=pd.read_pickle(TMP+'E.pkl');T=pd.read_pickle(TMP+'T.pkl')
pd.set_option('display.width',250,'display.max_columns',50)
# premium matched placebo
low20=d.l.rolling(20).min().shift(1); rows=[]
for j in np.where(d.fall.values&~np.isnan(low20.values))[0]:
    stop=0.95*low20.iloc[j]; ent=d.c.iloc[j]
    if ent<=stop or j>len(d)-181: continue
    prem=ent/low20.iloc[j]-1
    o10=outcome(d,j,ent,stop,0.10,180);o20=outcome(d,j,ent,stop,0.20,180)
    rows.append((prem,o10[0],o10[1],o20[0],o20[1],d.dt.iloc[j]))
Q=pd.DataFrame(rows,columns=['prem','s10','r10','s20','r20','dt'])
for lo,hi in [(0,.05),(.05,.10),(.10,.15),(.15,.25),(.25,1)]:
    q=Q[(Q.prem>=lo)&(Q.prem<hi)]; a=q[q.s10>=0]; b=q[q.s20>=0]
    print('placebo prem',lo,hi,len(q),'h10',round((a.s10==1).mean(),3),'net10',round(a.r10.mean(),4),'h20',round((b.s20==1).mean(),3),'net20',round(b.r20.mean(),4))
q=Q[Q.dt>='2024-01-01']; a=q[q.s10>=0]; print('placebo VAL',len(q),round((a.s10==1).mean(),3))
# divergence by class
P['grp']=np.where(P.cls=='retest','retest',np.where(P.cls.str.startswith('LL'),'LL','HL'))
for g,x in P.groupby('grp'):
    print(g,len(x),{c:f"{int((x[c+'_S']>x[c+'_L']).sum())}/{int(x[[c+'_S',c+'_L']].notna().all(axis=1).sum())}" for c in ['rsi','wt1','macdh','dlt14','pctb']})
# 4H states at L and S
def h_at(dt):
    day=d[d.dt==pd.Timestamp(dt)]
    if not len(day): return None
    t0=pd.Timestamp(dt); seg=h[(h.dt>=t0)&(h.dt<t0+pd.Timedelta(days=1))]
    if not len(seg): return None
    return seg.loc[seg.l.idxmin()]
r4=[]
for _,r in P[P.L_dt>=pd.Timestamp('2017-09-01').date()].iterrows():
    a=h_at(r.L_dt);b=h_at(r.S_dt)
    if a is None or b is None: continue
    r4.append((r.cls,a.rsi,b.rsi,a.wt1,b.wt1,a.macdh,b.macdh,a.pctb,b.pctb))
R4=pd.DataFrame(r4,columns=['cls','rsiL','rsiS','wtL','wtS','mL','mS','bL','bS']); R4['grp']=np.where(R4.cls=='retest','retest',np.where(R4.cls.str.startswith('LL'),'LL','HL'))
for g,x in R4.groupby('grp'):
    print('4H',g,len(x),'rsi up',int((x.rsiS>x.rsiL).sum()),'wt up',int((x.wtS>x.wtL).sum()),'macdh up',int((x.mS>x.mL).sum()),'median 4H RSI L',round(x.rsiL.median(),1),'S',round(x.rsiS.median(),1),'WT L',round(x.wtL.median(),0),'S',round(x.wtS.median(),0))
# time to trigger and upside given up
print(T.groupby('trig').prem.describe().round(3))
# NOW
print(d.tail(12)[['dt','o','h','l','c','rsi','wt1','wt2','macdh','pctb','sma20','dlt14','fund7','oi_chg14','streak','fall']].round(3).to_string())
print(h.tail(6)[['dt','h','l','c','rsi','wt1','wt2','macdh','pctb']].round(2).to_string())
wk=d.set_index('dt').c.resample('W-SUN').last(); wo=d.set_index('dt').o.resample('W-SUN').first(); wl=d.set_index('dt').l.resample('W-SUN').min();wh=d.set_index('dt').h.resample('W-SUN').max()
print(pd.DataFrame({'open':wo,'high':wh,'low':wl,'close':wk}).tail(10))
print('200w sma',wk.tail(200).mean(),'sma200d',d.sma200.iloc[-1],'ath',d.ath.iloc[-1],'dd',d.dd.iloc[-1])
last=d.tail(40); i=last.l.idxmin(); print('lowest low last 40d',d.dt[i],d.l[i]); 
print('high since low', d.h[i:].max(), d.dt[d.h[i:].idxmax()])
print('prior 8w high',d.h.tail(56).max())
# historical states at L / S percentiles
A=pd.DataFrame([d.loc[i0,['rsi','wt1','pctb','macdh','dlt14','fund7','oi_chg14']] for i0 in E.i0 if E.loc[E.i0==i0,'L_dt'].iloc[0]>=pd.Timestamp('2020-01-01')])
print(A.describe().round(3))
