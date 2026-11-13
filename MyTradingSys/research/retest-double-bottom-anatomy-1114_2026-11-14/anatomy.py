import numpy as np, pandas as pd, json, sys
C='F:/MTS/data_cache/btc_anatomy/'
REPO='C:/Users/E-ngineers/IdeaProjects/mts-jis-nb-retest-double-bottom-anatomy-1114/'
FEE=0.0012
def load():
    d=pd.read_csv(C+'BTCUSDT_1d.csv'); d['dt']=pd.to_datetime(d.t,unit='ms')
    h=pd.read_csv(C+'BTCUSDT_4h.csv'); h['dt']=pd.to_datetime(h.t,unit='ms')
    old=pd.read_csv(REPO+'MyTradingSys/research/btc_cycles_2026-11/btc_daily.csv',parse_dates=['date'])
    old=old[(old.date<d.dt.iloc[0])&(old.date>='2011-01-01')]
    o=pd.DataFrame({'dt':old.date,'h':old.high,'l':old.low,'c':old.close}); o['o']=o.c.shift(1); o['v']=np.nan; o['tbv']=np.nan
    d=pd.concat([o,d[['dt','o','h','l','c','v','tbv']]],ignore_index=True)
    return d.reset_index(drop=True),h
def ema(x,n): return pd.Series(x).ewm(span=n,adjust=False).mean().values
def rsi(c,n=14):
    c=pd.Series(c); dl=c.diff(); up=dl.clip(lower=0).ewm(alpha=1/n,adjust=False).mean(); dn=(-dl.clip(upper=0)).ewm(alpha=1/n,adjust=False).mean()
    return (100-100/(1+up/dn)).values
def wt(h,l,c):
    ap=(h+l+c)/3; esa=ema(ap,10); dd=ema(np.abs(ap-esa),10); ci=(ap-esa)/(0.015*dd); w1=ema(ci,21); w2=pd.Series(w1).rolling(4).mean().values
    return w1,w2
def add_ind(d):
    c=d.c.values; d['rsi']=rsi(c); d['wt1'],d['wt2']=wt(d.h.values,d.l.values,c)
    m=ema(c,12)-ema(c,26); d['macdh']=m-ema(m,9)
    s=pd.Series(c); ma=s.rolling(20).mean(); sd=s.rolling(20).std(ddof=0); d['pctb']=(s-(ma-2*sd))/(4*sd); d['sma20']=ma
    d['sma200']=s.rolling(200).mean()
    dl=2*d.tbv-d.v; d['dlt14']=dl.rolling(14,min_periods=14).sum()/d.v.rolling(14,min_periods=14).sum()
    d['v14']=d.v.rolling(14).mean()
    return d
def fall_state(d,bpd):
    wk=d.set_index('dt').c.resample('W-SUN').last().dropna()
    red=(wk<wk.shift(1)).astype(int); st=[];s=0
    for r in red: s=s+1 if r else 0; st.append(s)
    st=pd.Series(st,index=wk.index)
    prevst=st.shift(1).fillna(0); prevc=wk.shift(1)
    wend=d.dt.dt.to_period('W-SUN').dt.end_time.dt.normalize()
    # map each bar to its week-end label
    lab=d.dt.dt.normalize()+pd.to_timedelta((6-d.dt.dt.weekday),unit='D')
    ps=lab.map(prevst).fillna(0).values; pc=lab.map(prevc).values
    streak=np.where(d.c.values<pc,ps+1,0)
    hi56=d.h.rolling(56*bpd,min_periods=1).max().shift(1).values
    drop=d.c.values<=0.8*hi56
    return (streak>=4)|drop, streak
def fractal_lows(d,fall,bpd,n=10,gap=30):
    low=d.l.values; N=n*bpd; cand=[]
    for i in range(N,len(d)-N):
        if fall[i] and low[i]==low[i-N:i+N+1].min(): cand.append(i)
    kept=[]
    for i in cand:
        if kept and i-kept[-1]<gap*bpd:
            if low[i]<low[kept[-1]]: kept[-1]=i
        else: kept.append(i)
    return kept
def second_low(d,i0,bpd,horizon=120):
    h=d.h.values;l=d.l.values;c=d.c.values; pL=l[i0]; end=min(len(d)-1,i0+horizon*bpd)
    peak=h[i0]; pk=i0; res=dict(cls='open',S=None,necklineIdx=None,peak=None,pb=None)
    for j in range(i0+1,end+1):
        if h[j]>peak: peak=h[j]; pk=j
        if l[j]<pL*0.97:   # breach
            k=min(len(d)-1,j+20*bpd); jj=j+int(np.argmin(l[j:k+1])); r=c[j:min(len(d),j+5*bpd+1)].max()>pL
            res.update(cls='LL_reclaim' if r else 'LL',S=jj,peak=peak,pk=pk,breach=j); return res
        if peak>=pL*1.30: res.update(cls='V',peak=peak,pk=pk); return res
        if peak>=pL*1.08 and l[j]<=peak*0.92:
            res['pb']=j; k=min(end,j+60*bpd); S=j; neck=None
            for m in range(j,k+1):
                if l[m]<l[S]: S=m
                if l[m]<pL*0.97: break
                if c[m]>peak: neck=m; break
            lo=l[S]; ratio=lo/pL
            cl='LL' if ratio<0.97 else ('retest' if ratio<=1.03 else 'HL')
            if cl=='LL':
                r=c[S:min(len(d),S+5*bpd+1)].max()>pL; cl='LL_reclaim' if r else 'LL'
            res.update(cls=cl,S=S,necklineIdx=neck,peak=peak,pk=pk); return res
    res.update(peak=peak,pk=pk); res['cls']='range' if end-i0>=horizon*bpd else 'open'; return res
def outcome(d,i,entry,stop,tgt,hor):
    h=d.h.values;l=d.l.values;c=d.c.values; T=entry*(1+tgt); end=min(len(d)-1,i+hor)
    for j in range(i+1,end+1):
        if l[j]<=stop: return 0,stop/entry-1-FEE
        if h[j]>=T: return 1,tgt-FEE
    if end-i<hor: return -1,np.nan   # unresolved, data ends
    return 2,c[end]/entry-1-FEE
def boot(x,rng,nb=2000):
    x=np.array(x,float); x=x[~np.isnan(x)]
    if len(x)<3: return (np.nan,np.nan)
    m=[rng.choice(x,len(x)).mean() for _ in range(nb)]; return tuple(np.percentile(m,[2.5,97.5]))
