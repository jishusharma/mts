import sys; sys.path.insert(0,'.')
from anatomy import *
TMP='C:/Users/E-ngineers/AppData/Local/Temp/'
rng=np.random.default_rng(7)
d,h=load(); d=add_ind(d); h=add_ind(h)
fr=pd.read_csv(C+'funding_bybit.csv'); fr['dt']=pd.to_datetime(fr.t,unit='ms'); fr=fr.set_index('dt').rate.astype(float)
fund_d=fr.resample('D').sum().rolling(7).mean()
oi=pd.read_csv(C+'oi_bybit.csv'); oi['dt']=pd.to_datetime(oi.t,unit='ms').dt.normalize(); oi=oi.set_index('dt').oi.astype(float)
d['fund7']=d.dt.dt.normalize().map(fund_d); d['oi']=d.dt.dt.normalize().map(oi)
d['oi_chg14']=d.oi/d.oi.shift(14)-1
fall,streak=fall_state(d,1); d['fall']=fall; d['streak']=streak
d['ath']=d.h.cummax(); d['dd']=1-d.c/d.ath
def regime(i):
    r=d.iloc[i]
    if np.isnan(r.sma200): return 'n/a'
    if r.c<r.sma200 and r.dd>0.30: return 'bear'
    if r.c>r.sma200 and r.dd<0.20: return 'bull'
    return 'base'
L=fractal_lows(d,fall,1)
h['fall']=fall_state(h,6)[0]
def h_idx(ts): return int(np.searchsorted(h.dt.values,ts))
def first_c2(i0,hor=120):
    if not d.c.iloc[i0]<d.sma20.iloc[i0]: return None
    for j in range(i0+1,min(len(d),i0+hor+1)):
        if d.c.iloc[j]>d.sma20.iloc[j]: return j
def first_c4(i0,hor=120):
    for j in range(i0+1,min(len(d),i0+hor+1)):
        if d.wt1.iloc[j]>d.wt2.iloc[j] and d.wt1.iloc[j-1]<=d.wt2.iloc[j-1] and d.wt1.iloc[j]<-53: return j
def first_c3(i0,hor_days=120):
    pL=d.l.iloc[i0]; k0=h_idx(d.dt.iloc[i0]); k1=min(len(h)-1,k0+hor_days*6)
    if k0>=len(h)-10 or d.dt.iloc[i0]<h.dt.iloc[0]: return None
    H=h.h.values;Lw=h.l.values;Cc=h.c.values
    swh=None; swl=None
    for m in range(k0+4,k1+1):
        a=m-3
        if a>k0:
            if H[a]>H[a-3:a].max() and H[a]>H[a+1:m+1].max(): swh=H[a]
            if Lw[a]<Lw[a-3:a].min() and Lw[a]<Lw[a+1:m+1].min(): swl=Lw[a]
        if swh is not None and swl is not None and swl>=pL and Cc[m]>swh and m>k0+6:
            return m
    return None
eps=[]
for i0 in L:
    s=second_low(d,i0,1)
    r=dict(i0=i0,L_dt=d.dt.iloc[i0],L=d.l.iloc[i0],cls=s['cls'],reg=regime(i0),streak=int(d.streak.iloc[i0]),
           drop=1-d.c.iloc[i0]/d.h.iloc[max(0,i0-56):i0].max() if i0>0 else np.nan)
    r['has_vol']=not np.isnan(d.v.iloc[i0])
    r['neck']=s['peak']; r['pk_gain']=(s['peak']/d.l.iloc[i0]-1) if s['peak'] else np.nan
    if s['S'] is not None:
        S=s['S']; r.update(S_dt=d.dt.iloc[S],S=d.l.iloc[S],gap=S-i0,depth=d.l.iloc[S]/d.l.iloc[i0]-1,S_idx=S,neck_idx=s['necklineIdx'])
    r['s']=s; eps.append(r)
E=pd.DataFrame(eps)
cols=['rsi','wt1','wt2','macdh','pctb','dlt14','v14','fund7','oi_chg14']
rows=[]
for r in eps:
    if r.get('S_idx') is None or np.isnan(r['S_idx']): continue
    a=d.iloc[r['i0']]; b=d.iloc[int(r['S_idx'])]
    row=dict(L_dt=r['L_dt'].date(),S_dt=r['S_dt'].date(),cls=r['cls'],gap=r['gap'],depth=round(r['depth']*100,1),reg=r['reg'])
    for c in cols: row[c+'_L']=a[c]; row[c+'_S']=b[c]
    rows.append(row)
P=pd.DataFrame(rows)
div={}
sub=P[P.cls.isin(['retest','LL','LL_reclaim'])]
for c in ['rsi','wt1','macdh','dlt14','pctb']:
    x=sub.dropna(subset=[c+'_L',c+'_S']); div[c]=(len(x),int((x[c+'_S']>x[c+'_L']).sum()))
x=sub.dropna(subset=['v14_L','v14_S']); div['vol_lower_at_S']=(len(x),int((x.v14_S<x.v14_L).sum()))
trig=[]
def fire(r,name,j):
    if j is None: return
    i0=r['i0']; pL=d.l.iloc[i0]; ent=d.c.iloc[j] if name!='C3' else h.c.iloc[j]
    stop=0.95*pL
    if ent<=stop: return
    t=dict(L_dt=r['L_dt'],trig=name,reg=r['reg'],cls=r['cls'],when=(d.dt.iloc[j] if name!='C3' else h.dt.iloc[j]),prem=ent/pL-1,dev=r['L_dt']<=pd.Timestamp('2023-12-31'))
    if name=='C3':
        n=len(h)
        for tg,key in [(0.10,'o10'),(0.20,'o20')]:
            T_=ent*(1+tg);res=None;end=min(n-1,j+180*6)
            for m in range(j+1,end+1):
                if h.l.iloc[m]<=stop: res=(0,stop/ent-1-FEE);break
                if h.h.iloc[m]>=T_: res=(1,tg-FEE);break
            if res is None: res=(-1,np.nan) if end-j<180*6 else (2,h.c.iloc[end]/ent-1-FEE)
            t[key]=res
    else:
        t['o10']=outcome(d,j,ent,stop,0.10,180); t['o20']=outcome(d,j,ent,stop,0.20,180)
    trig.append(t)
for r in eps:
    s=r['s']; i0=r['i0']
    fire(r,'B0',i0)
    if s.get('necklineIdx') is not None: fire(r,'C1',s['necklineIdx'])
    fire(r,'C2',first_c2(i0)); fire(r,'C3',first_c3(i0)); fire(r,'C4',first_c4(i0))
T=pd.DataFrame(trig)
def summ(sel,tag):
    out=[]
    for name in ['B0','C1','C2','C3','C4']:
        t=sel[sel.trig==name]
        if not len(t): out.append((tag,name,0)); continue
        res={}
        for k in ['o10','o20']:
            st=np.array([x[0] for x in t[k]]); ret=np.array([x[1] for x in t[k]],float)
            ok=st>=0; hit=(st[ok]==1).mean() if ok.sum() else np.nan
            res[k]=(round(hit,3),round(np.nanmean(ret[ok]),4) if ok.sum() else np.nan,tuple(np.round(boot((st[ok]==1).astype(float),rng),2)),int(ok.sum()))
        out.append((tag,name,len(t),round(t.prem.median()*100,1),res['o10'],res['o20']))
    return out
rows_s=[]
for tag,sel in [('ALL',T),('DEV',T[T.dev]),('VAL',T[~T.dev]),('bear',T[T.reg=='bear']),('base',T[T.reg=='base']),('bull',T[T.reg=='bull'])]:
    rows_s+=summ(sel,tag)
pl=[]
low20=d.l.rolling(20).min().shift(1)
idx=np.where(d.fall.values&~np.isnan(low20.values))[0]
for j in idx:
    stop=0.95*low20.iloc[j]; ent=d.c.iloc[j]
    if ent<=stop or j>len(d)-181: continue
    pl.append((j,outcome(d,j,ent,stop,0.10,180),outcome(d,j,ent,stop,0.20,180),ent/low20.iloc[j]-1))
pl10=np.array([p[1][0] for p in pl]);pl20=np.array([p[2][0] for p in pl]);pr10=np.array([p[1][1] for p in pl],float)
placebo=dict(n=len(pl),h10=float((pl10[pl10>=0]==1).mean()),h20=float((pl20[pl20>=0]==1).mean()),ret10=float(np.nanmean(pr10[pl10>=0])),prem=float(np.median([p[3] for p in pl])))
def cls_tab(sel): return sel.groupby('cls').size().to_dict()
E['is_dev']=E.L_dt<=pd.Timestamp('2023-12-31')
res=dict(n_ep=len(E),cls_all=cls_tab(E),cls_dev=cls_tab(E[E.is_dev]),cls_val=cls_tab(E[~E.is_dev]),reg=E.reg.value_counts().to_dict(),
 cls_by_reg={k:cls_tab(g) for k,g in E.groupby('reg')},div=div,placebo=placebo)
pd.set_option('display.width',250,'display.max_columns',50,'display.max_rows',200)
print(json.dumps(res,default=str,indent=1))
print(E[['L_dt','L','cls','reg','streak','drop','pk_gain','gap','depth','has_vol']].round(3).to_string())
print('\n--- trigger summary (tag,trig,n,median premium %, (hit10,net10,CI,n), (hit20,net20,CI,n))')
for r in rows_s: print(r)
print('\n--- gap/depth stats')
print(P.groupby('cls')[['gap','depth']].describe().round(1).to_string())
print(P[['L_dt','S_dt','cls','gap','depth','rsi_L','rsi_S','wt1_L','wt1_S','macdh_L','macdh_S','pctb_L','pctb_S','dlt14_L','dlt14_S','fund7_L','fund7_S','oi_chg14_L','oi_chg14_S']].round(3).to_string())
for n_,o in [('T',T),('E',E.drop(columns=['s'])),('P',P),('d',d),('h',h)]: o.to_pickle(TMP+n_+'.pkl')
