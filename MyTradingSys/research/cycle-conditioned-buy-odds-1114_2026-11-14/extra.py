import pandas as pd,numpy as np
F=pd.read_csv('F:/MTS/data_cache/btc_cycle_features_1114.csv',index_col=0,parse_dates=True)
d=pd.read_csv('../btc_cycles_2026-11/btc_daily.csv',parse_dates=['date']).set_index('date')
P=F.dropna(subset=['r90','m90','d200w','d_ath'])
def ep(S,ex=30):
    out=[];cur=None
    for x in S.index:
        if cur is None or (x-last).days>ex: cur=[x];out.append(cur)
        else: cur.append(x)
        last=x
    return out
pd.set_option('display.width',250)
for nm,mk in [('B1',P.d200w<=.10),('B12',(P.d200w<=.10)&P.d_ath.between(350,450)),('B1 below200w',P.d200w<0)]:
    S=P[mk];print('\n',nm,len(S))
    rows=[]
    for g in ep(S):
        s=S.loc[g];rows.append((str(g[0].date()),str(g[-1].date()),len(g),round(s.d200w.min(),3),round(s.r90.median(),3),round(s.m90.median(),3),s.phase.mode()[0],round(s.mvrv.median(),2)))
    print(pd.DataFrame(rows,columns=['start','end','days','min_d200w','med_r90','med_mae90','phase','mvrv']).to_string())
    for lab,sl in [('DEV<=2023',S[S.index<='2023-12-31']),('VAL2024+',S[S.index>='2024-01-01'])]:
        if len(sl):print(lab,len(sl),'med r90',round(sl.r90.median(),3),'pos',round((sl.r90>0).mean(),2),'med mae',round(sl.m90.median(),3),'mean r90 net',round(sl.r90.mean()-.0024,3))
    # episode-level: median of episode medians
    em=[S.loc[g].r90.median() for g in ep(S)];print('episode medians: n',len(em),'median',round(np.median(em),3),'min',round(min(em),3),'share>0',round(np.mean(np.array(em)>0),2))
    rr=np.random.default_rng(1);b=[np.median(rr.choice(em,len(em))) for _ in range(10000)];print('CI of episode-median',np.round(np.percentile(b,[2.5,97.5]),3))
print('\nALL pcts r90',P.r90.quantile([.1,.25,.5,.75,.9]).round(3).to_dict(),'mae90',P.m90.quantile([.1,.25,.5,.75,.9]).round(3).to_dict())
for nm,mk in [('B12',(P.d200w<=.10)&P.d_ath.between(350,450)),('B1',P.d200w<=.10)]:
    S=P[mk];print(nm,'r90 q',S.r90.quantile([.1,.25,.5,.75,.9]).round(3).to_dict(),'mae90 q',S.m90.quantile([.1,.25,.5,.75,.9]).round(3).to_dict(),'pct rank of med',round((P.r90<S.r90.median()).mean()*100,1))
print('mvrv now',F.mvrv.dropna().iloc[-1],'mvrv in B1 median',P[P.d200w<=.1].mvrv.median(),'all',P.mvrv.median(),'mvrv<1.4 days r90',P[P.mvrv<1.4].r90.median(),(P.mvrv<1.4).sum(),'1.2-1.5',P[P.mvrv.between(1.2,1.5)].r90.median(),P[P.mvrv.between(1.2,1.5)].m90.median(),P.mvrv.between(1.2,1.5).sum())
s=d.loc['2025-10-06':];print('low since ATH',s.low.min(),s.low.idxmin(),'ATH',s.high.max(),s.high.idxmax())
print('min low after 2026-07-01',d.loc['2026-07-02':].low.min())
print(F.tail(3)[['dd','d200w','d50w','rsiw','wtw','streak']])
print('sma200w now approx',(d.close.rolling(1400).mean()).iloc[-1],'sma50w',d.close.rolling(350).mean().iloc[-1])
# days where streak>=6
S=P[P.streak>=6];print('streak>=6',len(S),'ep',len(ep(S)),'med r90',S.r90.median(),'pos',(S.r90>0).mean(),'mae',S.m90.median())
S=P[(P.streak>=5)];print('streak>=5',len(S),len(ep(S)),S.r90.median(),(S.r90>0).mean(),S.m90.median())
S=P[(P.rsiw<50)&(P.d200w<=.1)];print('rsiw<50&B1',len(S),len(ep(S)),S.r90.median(),(S.r90>0).mean())
