import pandas as pd, numpy as np, sys
B='C:/Users/E-ngineers/IdeaProjects/BinanceDataFeed/MyTradingSys/'
d=pd.read_csv(B+'research/pattern_book_2026-11/data/BTCUSDT_1d.csv')
d['t']=pd.to_datetime(d.t,unit='ms'); d=d.set_index('t')[['o','h','l','c']]
p=pd.read_csv(B+'options/data/hist/perp_1h.csv'); p['t']=pd.to_datetime(p.ts_ms,unit='ms'); p=p.set_index('t')
print('perp1h bars',len(p),p.index[0],p.index[-1],'gaps>1h',(p.index.to_series().diff()>pd.Timedelta('1h')).sum())
h4=p.resample('4h').agg({'open':'first','high':'max','low':'min','close':'last'}).dropna(); h4.columns=list('ohlc')
FEE=0.001
def donchian(df,N,X):
    o,h,l,c=[df[k].values for k in 'ohlc']; n=len(c); tr=[]; pos=0
    hi=pd.Series(h).shift(1).rolling(N).max().values; lo=pd.Series(l).shift(1).rolling(N).min().values
    xh=pd.Series(h).shift(1).rolling(X).max().values; xl=pd.Series(l).shift(1).rolling(X).min().values
    i=max(N,X)
    while i<n-1:
        if pos==0:
            s=1 if c[i]>hi[i] else (-1 if c[i]<lo[i] else 0)
            if s: pos=s; e=i+1; ep=o[e]; stop=xl[i] if s==1 else xh[i]; risk=abs(ep-stop)/ep
        else:
            if (pos==1 and c[i]<xl[i]) or (pos==-1 and c[i]>xh[i]):
                tr.append((pos,e,i+1,pos*(o[i+1]/ep-1)-FEE,risk)); pos=0; continue
        i+=1
    if pos: tr.append((pos,e,n-1,pos*(c[n-1]/ep-1)-FEE,risk))
    return tr
def tsmom(df):
    c=df.c.values; o=df.o.values; n=len(c); tr=[]; pos=0
    for i in range(28,n-1,7):
        s=1 if c[i]/c[i-28]-1>0 else -1
        if s!=pos:
            if pos: tr.append((pos,e,i+1,pos*(o[i+1]/ep-1)-FEE,np.nan))
            pos=s; e=i+1; ep=o[e]
    if pos: tr.append((pos,e,n-1,pos*(c[n-1]/ep-1)-FEE,np.nan))
    return tr
def stats(tr):
    if not tr: return None
    r=np.array([t[3] for t in tr]); R=np.array([t[3]/t[4] for t in tr if t[4]==t[4] and t[4]>0])
    w=r[r>0]; l=r[r<=0]
    return dict(n=len(r),win=(r>0).mean(),aw=w.mean() if len(w) else 0,al=l.mean() if len(l) else 0,mean=r.mean(),
        R=R.mean() if len(R) else np.nan,t=r.mean()/(r.std(ddof=1)/np.sqrt(len(r))) if len(r)>2 and r.std()>0 else np.nan)
def placebo(df,tr,rng,draws=200):
    if not tr: return np.nan
    c=df.c.values; o=df.o.values; n=len(c); dirs=np.array([t[0] for t in tr]); hold=np.array([t[2]-t[1] for t in tr])
    act=np.mean([t[3] for t in tr]); ms=[]
    for _ in range(draws):
        hs=rng.choice(hold,len(tr)); st=rng.integers(1,n-1-hs.clip(max=n-3)) if True else 0
        st=np.array([rng.integers(1,max(2,n-1-h)) for h in hs]); en=np.minimum(st+hs,n-1)
        ms.append(np.mean(dirs*(c[en]/o[st]-1)-FEE))
    return (np.array(ms)<act).mean()*100
rng=np.random.default_rng(1)
out=[]
for name,df,fn,gap in [('R1 daily Donchian 20/10',d,lambda x:donchian(x,20,10),30),('R2 4h Donchian 55/20',h4,lambda x:donchian(x,55,20),180),('R3 TSMOM 28d weekly (daily)',d,tsmom,30)]:
    k=int(len(df)*0.6); dev=df.iloc[:k]; val=df.iloc[k+gap:]
    out.append(f'\n## {name}\nDEV {dev.index[0].date()}..{dev.index[-1].date()} ({len(dev)} bars); VAL {val.index[0].date()}..{val.index[-1].date()} ({len(val)} bars)\n')
    out.append('| seg | side | n | win % | avg win % | avg loss % | net/trade % | net R | t | placebo pctile | B&H % |\n|---|---|---|---|---|---|---|---|---|---|---|')
    for seg,sd in [('DEV',dev),('VAL',val)]:
        tr=fn(sd); bh=(sd.c.iloc[-1]/sd.o.iloc[0]-1)*100
        for side,f in [('ALL',lambda t:True),('long',lambda t:t[0]==1),('short',lambda t:t[0]==-1)]:
            sub=[t for t in tr if f(t)]; s=stats(sub)
            if not s: out.append(f'| {seg} | {side} | 0 | | | | | | | | {bh:.0f} |'); continue
            pc=placebo(sd,sub,rng)
            out.append(f"| {seg} | {side} | {s['n']} | {s['win']*100:.0f} | {s['aw']*100:.2f} | {s['al']*100:.2f} | {s['mean']*100:+.2f} | {s['R']:+.2f} | {s['t']:+.2f} | {pc:.0f} | {bh:.0f} |")
txt='\n'.join(out); print(txt); open('C:/Users/E-ngineers/IdeaProjects/mts-jis-nb-supervisor-c-2026-11-11-l5/MyTradingSys/research/edge_views_2026-11-11/TREND/tables.md','w').write(txt)
