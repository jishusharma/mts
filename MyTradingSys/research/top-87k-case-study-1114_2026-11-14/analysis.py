import sys; sys.path.insert(0,'C:/Users/E-NGIN~1/AppData/Local/Temp/w')
from lib import *
import numpy as np, pandas as pd
pd.set_option('display.width',250); pd.set_option('display.max_rows',500)
TMP='C:/Users/E-NGIN~1/AppData/Local/Temp/w/'
b=load15(); d0=daily_ext()
d=d0[['o','h','l','c','v']].copy(); d['delta']=d0.delta
H4=rs(b,'4h')
W=d.resample('W-MON',label='left',closed='left').agg({'o':'first','h':'max','l':'min','c':'last','v':'sum'}).dropna()
fd=funding_daily(); oi=oi_daily()
d['sma200']=d.c.rolling(200).mean()
d['phase']=np.where((d.c>d.sma200)&(d.sma200>d.sma200.shift(30)),'BULL',np.where((d.c<d.sma200)&(d.sma200<d.sma200.shift(30)),'BEAR','BASE'))
d.loc[d.sma200.isna(),'phase']='NA'
for df in (d,W,H4):
    df['rsi']=rsi(df.c); df['wt']=wt(df); df['bm'],df['bu'],df['bl']=bb(df.c)
    df['adx'],df['pdi'],df['mdi']=adx(df)
W['sma20']=W.c.rolling(20).mean(); W['sma50']=W.c.rolling(50).mean(); W['sma200']=W.c.rolling(200).mean()

def pivots(df,k,kind):
    x=df.h.values if kind=='H' else df.l.values; n=len(x); out=[]
    for i in range(k,n-k):
        w=x[i-k:i+k+1]
        if kind=='H' and x[i]==w.max() and (w==x[i]).sum()==1: out.append(i)
        if kind=='L' and x[i]==w.min() and (w==x[i]).sum()==1: out.append(i)
    return out

def div_events(df,k,L,osc,thr,side,usebb):
    ev=[]; kind='H' if side=='S' else 'L'
    P=pivots(df,k,kind); o=df[osc].values; bu=df.bu.values; bl=df.bl.values; h=df.h.values; l=df.l.values
    for a,bi in zip(P[:-1],P[1:]):
        if bi-a>L: continue
        if side=='S':
            ok=h[bi]>h[a] and o[bi]<o[a] and o[a]>thr and (not usebb or (h[bi]>bu[bi] or h[a]>bu[a]))
        else:
            lowthr=(100-thr) if osc=='rsi' else -thr
            ok=l[bi]<l[a] and o[bi]>o[a] and o[a]<lowthr and (not usebb or (l[bi]<bl[bi] or l[a]<bl[a]))
        if ok: ev.append((bi+k,a,bi))
    return ev

EVS=[]
def step(tf): return {'1D':pd.Timedelta(days=1),'1W':pd.Timedelta(days=7),'4H':pd.Timedelta(hours=4)}[tf]
for side in ('S','L'):
    for tf,df,k,L in (('1D',d,3,60),('1W',W,2,40),('4H',H4,5,120)):
        for nm,osc,thr,bbq in (('DIV_RSI_BB','rsi',60,True),('DIV_WT_BB','wt',40,True),('DIV_RSI_noBB','rsi',60,False)):
            for (f,a,bi) in div_events(df,k,L,osc,thr,side,bbq):
                if f>=len(df): continue
                EVS.append(dict(sig=nm+('' if side=='S' else '_UP'),tf=tf,date=df.index[f],ent_t=df.index[f]+step(tf),price=df.c.iloc[f],side=side,p1=a,p2=bi))

def add(side,name,tf,dates,df=d):
    for t in dates:
        if t in df.index:
            EVS.append(dict(sig=name,tf=tf,date=t,ent_t=t+step(tf),price=df.c[t],side=side,p1=None,p2=None))
def cooldown(dates,n):
    out=[];last=None
    for t in dates:
        if last is None or (t-last).days>=n: out.append(t); last=t
    return out
hh=d.h.rolling(60).max().shift(1); ll=d.l.rolling(60).min().shift(1)
fbo=[];fbd=[]
for i in range(60,len(d)-3):
    if d.h.iloc[i]>hh.iloc[i]:
        for j in range(i,i+4):
            if j<len(d) and d.c.iloc[j]<hh.iloc[i]: fbo.append(d.index[j]); break
    if d.l.iloc[i]<ll.iloc[i]:
        for j in range(i,i+4):
            if j<len(d) and d.c.iloc[j]>ll.iloc[i]: fbd.append(d.index[j]); break
add('S','FAILED_BO','1D',cooldown(sorted(set(fbo)),10)); add('L','FAILED_BD','1D',cooldown(sorted(set(fbd)),10))
fr=fd.rolling(365,min_periods=200)
add('S','FUND_EXT','1D',cooldown(list(fd[(fd>=fr.quantile(.9))&(fd>0)].index),20))
add('L','FUND_NEG','1D',cooldown(list(fd[(fd<=fr.quantile(.1))&(fd<0)].index),20))
oq=oi.rolling(365,min_periods=200).quantile(.9)
add('S','OI_EXT','1D',cooldown(list(oi[oi>=oq].index),20))
dl=d.delta.rolling(14).sum(); hi30=d.c>=d.c.rolling(30).max(); lo30=d.c<=d.c.rolling(30).min()
add('S','CVD_DIV','1D',cooldown(list(d.index[hi30&(dl<0)]),10)); add('L','CVD_DIV_UP','1D',cooldown(list(d.index[lo30&(dl>0)]),10))
def cross(cond,df): return df.index[cond&~cond.shift(1,fill_value=False)]
for nm,col,sd,below in (('W_BELOW_20W','sma20','S',True),('W_BELOW_50W','sma50','S',True),('W_ABOVE_20W','sma20','L',False),('W_ABOVE_50W','sma50','L',False)):
    cnd=((W.c<W[col]) if below else (W.c>W[col]))&W[col].notna()
    add(sd,nm,'1W',list(cross(cnd,W)),W)
def struct(kind,k=5):
    P=pivots(d,k,'H' if kind=='LH' else 'L'); out=[]
    for a_,b_ in zip(P[:-1],P[1:]):
        if kind=='LH' and d.h.iloc[b_]<d.h.iloc[a_]:
            lvl=d.l.iloc[a_:b_+1].min()
            for j in range(b_+k,min(len(d),b_+k+40)):
                if d.h.iloc[j]>d.h.iloc[b_]: break
                if d.c.iloc[j]<lvl: out.append(d.index[j]); break
        if kind=='HL' and d.l.iloc[b_]>d.l.iloc[a_]:
            lvl=d.h.iloc[a_:b_+1].max()
            for j in range(b_+k,min(len(d),b_+k+40)):
                if d.l.iloc[j]<d.l.iloc[b_]: break
                if d.c.iloc[j]>lvl: out.append(d.index[j]); break
    return out
add('S','LH_BREAK','1D',sorted(set(struct('LH')))); add('L','HL_BREAK','1D',sorted(set(struct('HL'))))
dix=(d.mdi>d.pdi)&(d.mdi.shift()<=d.pdi.shift())&(d.adx>=20); add('S','DI_DEATH','1D',list(d.index[dix]))
dix2=(d.pdi>d.mdi)&(d.pdi.shift()<=d.mdi.shift())&(d.adx>=20); add('L','DI_BIRTH','1D',list(d.index[dix2]))
ev=pd.DataFrame(EVS)

# sequences
mdi_x=dix; pdi_x=dix2
out=[]
base=ev[ev.sig.isin(['DIV_RSI_BB','DIV_WT_BB','DIV_RSI_BB_UP','DIV_WT_BB_UP'])&ev.tf.isin(['1D','1W'])].sort_values('ent_t')
for _,r in base.iterrows():
    side=r.side; tfdf=d if r.tf=='1D' else W
    t1,t2=tfdf.index[int(r.p1)],tfdf.index[int(r.p2)]
    seg=d.loc[t1:t2+(pd.Timedelta(days=6) if r.tf=='1W' else pd.Timedelta(0))]
    if side=='S': lvl=seg.l.min(); ext=seg.h.max()
    else: lvl=seg.h.max(); ext=seg.l.min()
    start=r.ent_t.normalize(); win=d.loc[start:start+pd.Timedelta(days=40)]
    trig=None;trig2=None
    for t,row in win.iterrows():
        if side=='S':
            if row.h>ext: break
            if trig is None and row.c<lvl: trig=t
            if trig2 is None and mdi_x.get(t,False) and (t-start).days<=30: trig2=t
        else:
            if row.l<ext: break
            if trig is None and row.c>lvl: trig=t
            if trig2 is None and pdi_x.get(t,False) and (t-start).days<=30: trig2=t
    nm='' if side=='S' else '_UP'
    def mk(sig,t): return dict(sig=sig,tf='1D',date=t,ent_t=t+pd.Timedelta(days=1),price=d.c[t],side=side,p1=None,p2=None,src=r.sig+'/'+r.tf)
    if trig is not None:
        out.append(mk('SEQ_A'+nm,trig))
        wk=W[W.index+pd.Timedelta(days=7)<=trig+pd.Timedelta(days=1)]
        sm=wk.sma20.iloc[-1]
        wc=pd.notna(sm) and ((wk.c.iloc[-1]<sm) if side=='S' else (wk.c.iloc[-1]>sm))
        di=(d.mdi[trig]>d.pdi[trig]) if side=='S' else (d.pdi[trig]>d.mdi[trig])
        if wc or di: out.append(mk('SEQ_B'+nm,trig))
    if trig2 is not None: out.append(mk('SEQ_C'+nm,trig2))
sq=pd.DataFrame(out).sort_values(['sig','date']).drop_duplicates(['sig','date'])
ev=pd.concat([ev,sq],ignore_index=True)

last=d.c.iloc[-1]; DEND=d.index[-1]+pd.Timedelta(days=1)
def outcome(r):
    side=r.side; tf=r.tf
    df=H4 if tf=='4H' else d
    t=r.ent_t
    if tf=='4H': tp,sl,hor=(.04,.02,15) if side=='S' else (.06,.03,15)
    else: tp,sl,hor=(.08,.04,45) if side=='S' else (.12,.06,45)
    seg=df.loc[t:t+pd.Timedelta(days=hor)]
    e=r.price; res='N' if len(seg) else 'NA'
    for x in seg.itertuples():
        if side=='S': hs=x.h>=e*(1+sl); ht=x.l<=e*(1-tp)
        else: hs=x.l<=e*(1-sl); ht=x.h>=e*(1+tp)
        if hs: res='L';break
        if ht: res='W';break
    t30=t+pd.Timedelta(days=30)
    if t30<=DEND:
        r30=d.loc[:t30-pd.Timedelta(days=1)].c.iloc[-1]/e-1; ret=(-r30 if side=='S' else r30)-0.0024
    else: ret=np.nan
    tod=((e-last)/e if side=='S' else (last-e)/e)
    s2=d.loc[t.normalize():]
    if len(s2): mfe=(e-s2.l.min())/e if side=='S' else (s2.h.max()-e)/e; mae=(s2.h.max()-e)/e if side=='S' else (e-s2.l.min())/e
    else: mfe=mae=np.nan
    return pd.Series(dict(res=res,ret30=ret,to_today=tod,mfe=mfe,mae=mae))
ev=pd.concat([ev,ev.apply(outcome,axis=1)],axis=1)
ev['phase']=[d.phase.get(pd.Timestamp(t).normalize(),'NA') for t in ev.date]
ev['period']=np.where(ev.date<'2024-01-01',np.where(ev.date<'2020-01-01','DEV','DEV'),np.where(ev.date<'2026-01-01','VAL','CASE'))
ev.to_pickle(TMP+'ev.pkl'); d.to_pickle(TMP+'d.pkl'); W.to_pickle(TMP+'W.pkl'); H4.to_pickle(TMP+'H4.pkl')
fd.to_pickle(TMP+'fd.pkl'); oi.to_pickle(TMP+'oi.pkl')
print(len(ev)); print(ev.groupby(['side','sig','tf']).size())
