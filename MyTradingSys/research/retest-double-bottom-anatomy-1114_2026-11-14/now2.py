import sys; sys.path.insert(0,'.')
from anatomy import *
TMP='C:/Users/E-ngineers/AppData/Local/Temp/'
d=pd.read_pickle(TMP+'d.pkl');h=pd.read_pickle(TMP+'h.pkl');E=pd.read_pickle(TMP+'E.pkl');P=pd.read_pickle(TMP+'P.pkl')
d['sma1400']=d.c.rolling(1400).mean()
E['near200w']=[(d.c.iloc[i]<=1.03*d.sma1400.iloc[i]) if not np.isnan(d.sma1400.iloc[i]) else np.nan for i in E.i0]
print(E[E.near200w==True][['L_dt','L','cls','reg']])
print('since 2017-09 class mix',E[E.L_dt>='2017-09-01'].cls.value_counts().to_dict())
print('bear since 2017',E[(E.L_dt>='2017-09-01')&(E.reg=='bear')].cls.value_counts().to_dict())
print('now fund7',d.fund7.iloc[-1],'oi',d.oi.iloc[-1],'oi14',d.oi_chg14.iloc[-1],'dlt14',d.dlt14.iloc[-1],'v14 ratio vs 90d',d.v14.iloc[-1]/d.v.tail(90).mean())
fl=d.loc[E.i0[E.L_dt>='2020-06-01'],['fund7','oi_chg14','dlt14']]; print(fl.describe().round(5))
# 4H low-bar state percentiles
r=[]
for dt in E.L_dt[E.L_dt>='2017-09-01']:
    seg=h[(h.dt>=dt)&(h.dt<dt+pd.Timedelta(days=1))]
    if len(seg): b=seg.loc[seg.l.idxmin()]; r.append((b.rsi,b.wt1,b.pctb))
R=pd.DataFrame(r,columns=['rsi','wt1','pctb']); print(R.describe().round(2))
now=h[(h.dt>='2026-11-13')&(h.dt<'2026-11-14')]; b=now.loc[now.l.idxmin()]; print('now 4H low bar',b['dt'],b.l,b.rsi,b.wt1,b.pctb, 'pctile rsi',(R.rsi<b.rsi).mean(),'wt',(R.wt1<b.wt1).mean())
dl=d.iloc[-1]; A=d.loc[E.i0[E.L_dt>='2017-09-01']]
for c in ['rsi','wt1','pctb','dlt14']: print(c,round(dl[c],3),'pctile among hist L (since 2017-09, daily):',round((A[c]<dl[c]).mean(),2))
print('wt1<-60?',dl.wt1,'WT2',dl.wt2,'cross?',d.wt1.iloc[-1]>d.wt2.iloc[-1])
L=67568.0
for nm,v in [('-5% stop',.95),('-3% sweep line',.97),('+3% retest top',1.03),('+8% bounce needed',1.08),('+30% V',1.30)]: print(nm,round(L*v))
print('sma20',d.sma20.iloc[-1],'sma200d',d.sma200.iloc[-1],'hi20',d.h.tail(20).max())
# Fisher LL vs others for RSI up
