"""Corrected causal encounter study; frozen PRE_REG.md. DEV only."""
from concurrent.futures import ThreadPoolExecutor
import hashlib
import io
import json
from pathlib import Path
from statistics import NormalDist
import urllib.request
import zipfile

import numpy as np
import pandas as pd
import rules

OUT=Path(__file__).resolve().parent
OLD=OUT.parent/'candle_close_2026-10-14'
TFS=[1,2,3,5,15,30,60]
HORIZONS=[60,1440]
FAMILIES=['4h','day','week']
SIGS=rules.SIGNATURES+['level_test','level_bounce']


def aggregate(a,minutes):
    r=a.resample(f'{minutes}min',origin='epoch',closed='left',label='right')
    b=r.agg(dict(o='first',h='max',l='min',c='last',v='sum'))
    b.loc[r.c.count()!=minutes,:]=np.nan
    return b


def state_table(b):
    rows=[]
    for i in range(len(b)):
        p=rules.phase(b.c.iloc[i-20:i+1].to_numpy(),b.h.iloc[i-19:i+1].to_numpy(),
                      b.l.iloc[i-19:i+1].to_numpy()) if i>=20 else rules.phase([],[],[])
        rows.append(p)
    return pd.DataFrame(rows,index=b.index)


def load_dev():
    manifest=json.loads((OLD/'results.json').read_text())['manifest']
    parts=[]
    for item in manifest:
        if not '2022-01'<=item['month']<='2024-06': raise ValueError('sealed date requested')
        raw=Path(item['path']).read_bytes()
        if hashlib.sha256(raw).hexdigest()!=item['checksum']: raise ValueError('price checksum')
        with zipfile.ZipFile(io.BytesIO(raw)) as z:
            frame=pd.read_csv(z.open(z.namelist()[0]),header=None,usecols=list(range(6)),dtype=str)
        frame=frame[pd.to_numeric(frame[0],errors='coerce').notna()].astype(float)
        frame.index=pd.to_datetime(frame.pop(0).astype('int64'),unit='ms',utc=True)
        frame.columns=['o','h','l','c','v']; parts.append(frame)
    a=pd.concat(parts)
    if not a.index.is_unique or not a.index.is_monotonic_increasing: raise ValueError('duplicate/unordered data')
    if not np.isfinite(a.to_numpy()).all(): raise ValueError('nonfinite raw data')
    if not (np.asarray(a.index[1:]-a.index[:-1])==pd.Timedelta(minutes=1)).all(): raise ValueError('raw gaps')
    if ((a.h<a[['o','c','l']].max(axis=1))|(a.l>a[['o','c','h']].min(axis=1))).any(): raise ValueError('OHLC invalid')
    return a,manifest


def fetch_funding(month):
    if month not in [str(x) for x in pd.period_range('2022-01','2024-06',freq='M')]:
        raise ValueError('funding outside DEV')
    name=f'BTCUSDT-fundingRate-{month}.zip'
    url=f'https://data.binance.vision/data/futures/um/monthly/fundingRate/BTCUSDT/{name}'
    path=Path('F:/MTS/data/candle_close_dev_2022_2024')/name
    expected=urllib.request.urlopen(url+'.CHECKSUM',timeout=60).read().decode().split()[0]
    raw=path.read_bytes() if path.exists() else urllib.request.urlopen(url,timeout=60).read()
    if hashlib.sha256(raw).hexdigest()!=expected: raise ValueError('funding checksum')
    if not path.exists(): path.write_bytes(raw)
    with zipfile.ZipFile(io.BytesIO(raw)) as z: frame=pd.read_csv(z.open(z.namelist()[0]))
    required=['calc_time','funding_interval_hours','last_funding_rate']
    if not set(required)<=set(frame.columns): raise ValueError('unexpected funding schema '+str(list(frame.columns)))
    if not (frame.funding_interval_hours==8).all(): raise ValueError('unexpected funding interval')
    return frame,dict(month=month,url=url,path=str(path),sha256=expected)


def load_funding(a):
    months=[str(x) for x in pd.period_range('2022-01','2024-06',freq='M')]
    with ThreadPoolExecutor(max_workers=4) as pool: loaded=list(pool.map(fetch_funding,months))
    f=pd.concat([x[0] for x in loaded]).sort_values('calc_time')
    times=settlement_slots(pd.DatetimeIndex(pd.to_datetime(f.calc_time,unit='ms',utc=True)))
    expected=pd.date_range('2022-01-01','2024-06-30 16:00',freq='8h',tz='UTC')
    if len(times)!=len(expected) or not np.asarray(times==expected).all(): raise ValueError('funding coverage missing or duplicate')
    rates=f.last_funding_rate.to_numpy(dtype=float)
    if not np.isfinite(rates).all(): raise ValueError('nonfinite funding')
    prices=a.o.reindex(times).to_numpy()
    if not np.isfinite(prices).all(): raise ValueError('missing funding reference price')
    return times,rates,prices,[x[1] for x in loaded]


def settlement_slots(reported):
    nominal=reported.floor('8h')
    if not ((reported-nominal)<pd.Timedelta(minutes=1)).all():
        raise ValueError('funding timestamp outside nominal settlement minute')
    return nominal


def funding_charge(times,rates,prices,start,end,entry,side):
    mask=(times>start)&(times<=end)
    return float(side*np.sum(rates[mask]*prices[mask])/entry)


def outcome(a,start,side,atr,extreme,horizon,funding):
    end=start+pd.Timedelta(minutes=horizon)
    if start not in a.index or end not in a.index:
        return dict(gross=np.nan,funding=np.nan,net14=np.nan,net20=np.nan,win=np.nan,
                    barrier_low=np.nan,barrier_high=np.nan,persist=np.nan,censored=True)
    entry=float(a.at[start,'o']); exitprice=float(a.at[end,'o'])
    gross=side*(exitprice/entry-1)
    fee=funding_charge(*funding,start,end,entry,side) if funding is not None else np.nan
    result=dict(gross=gross,funding=fee,net14=gross-fee-.0014,net20=gross-fee-.002,
                win=float(gross>0),censored=False)
    if horizon==1440:
        i=a.index.get_loc(start); bs=a.iloc[i:i+horizon]
        hi=np.r_[bs.h.to_numpy(),exitprice]; lo=np.r_[bs.l.to_numpy(),exitprice]
        up=hi>=entry+atr if side==1 else lo<=entry-atr
        down=lo<=entry-atr if side==1 else hi>=entry+atr
        ui=np.flatnonzero(up); di=np.flatnonzero(down)
        u=int(ui[0]) if len(ui) else horizon+2
        d=int(di[0]) if len(di) else horizon+2
        result['barrier_low']=float(u<d)
        result['barrier_high']=float(u<d or u==d and u<=horizon)
        result['barrier_status']='AMBIGUOUS' if u==d and u<=horizon else ('TARGET' if u<d else ('ADVERSE' if d<u else 'TIMEOUT'))
        survives=lo.min()>=extreme-.25*atr if side==1 else hi.max()<=extreme+.25*atr
        result['persist']=float(survives and len(ui)>0)
        result['mfe_atr']=max(0,float((hi.max()-entry if side==1 else entry-lo.min())/atr))
        result['mae_atr']=max(0,float((entry-lo.min() if side==1 else hi.max()-entry)/atr))
    return result


def feature_ledger(a):
    parents={'4h':aggregate(a,240),'day':aggregate(a,1440)}
    r=a.resample('W-MON',closed='left',label='right')
    week=r.agg(dict(o='first',h='max',l='min',c='last',v='sum'))
    week.loc[r.c.count()!=10080,:]=np.nan; parents['week']=week
    four=state_table(parents['4h']); hour=state_table(aggregate(a,60))
    atrpct=four.atr/parents['4h'].c
    four['vol_ratio']=atrpct/atrpct.shift(1).rolling(180,min_periods=180).median()
    day=parents['day']; momentum=day.c/day.c.shift(30)-1
    history=day.c.rolling(31,min_periods=31).count()==31
    placebo={}
    for family in FAMILIES:
        p=parents[family]; px=a.o.reindex(p.index)
        for edge in ['h','l']:
            multipliers=[]
            for timestamp in p.index:
                key=f'20261014|{family}|{edge}|{timestamp}'.encode()
                rng=np.random.default_rng(int.from_bytes(hashlib.sha256(key).digest()[:8],'big'))
                multipliers.append(rng.choice([-1,1])*rng.uniform(.75,1.25))
            values=px+np.asarray(multipliers)*abs(p[edge]-px)
            values[abs(p[edge]-px)==0]=np.nan
            placebo[(family,edge)]=values
    rows=[]; audit=dict(first_encounters=0,unknown_context=0,incomplete_confirmation=0,unknown_approach=0)
    for tf in TFS:
        b=aggregate(a,tf).dropna(); opens=b.index-pd.Timedelta(minutes=tf)
        fp=four.reindex(opens,method='ffill'); hp=hour.reindex(opens,method='ffill')
        warm=history.reindex(opens,method='ffill').fillna(False).to_numpy(dtype=bool)
        mom=momentum.reindex(opens,method='ffill').to_numpy()
        for family in FAMILIES:
            for edge in ['h','l']:
                for source in ['REAL','PLACEBO']:
                    series=parents[family][edge] if source=='REAL' else placebo[(family,edge)]
                    lev=series.reindex(opens,method='ffill').to_numpy()
                    hit=(b.l.to_numpy()<=lev)&(b.h.to_numpy()>=lev)&np.isfinite(lev)
                    ids=np.flatnonzero(hit)
                    if len(ids):
                        _,first=np.unique(b.index[ids].floor('D'),return_index=True); ids=ids[first]
                    for i in ids:
                        audit['first_encounters']+=1; j=int(i)+2
                        if j>=len(b) or b.index[j]-b.index[i]!=pd.Timedelta(minutes=2*tf):
                            audit['incomplete_confirmation']+=1; continue
                        p=fp.iloc[i].to_dict(); local=hp.iloc[i]['phase']; vol=p['vol_ratio']
                        if not warm[i] or p['phase']=='UNKNOWN' or not np.isfinite(vol):
                            audit['unknown_context']+=1; continue
                        level=float(lev[i]); prev=float(b.c.iloc[i-1]) if i>0 else float(b.o.iloc[i])
                        approach=int(np.sign(prev-level)) or int(np.sign(b.o.iloc[i]-level))
                        if not approach: audit['unknown_approach']+=1; continue
                        decision=b.index[j]; current=b.iloc[j]
                        for side in [1,-1]:
                            ctx=rules.context(p,local,side,level,vol)
                            row=dict(tf=tf,family=family,edge=edge,source=source,side=side,approach=approach,
                                context=ctx,phase=p['phase'],local_phase=local,vol_ratio=vol,
                                volatility='ELEVATED' if vol>=1.5 else ('QUIET' if vol<.75 else 'ORDINARY'),
                                momentum='UP_MOMENTUM' if mom[i]>.1 else ('DOWN_MOMENTUM' if mom[i]<-.1 else 'NEUTRAL'),
                                encounter=str(opens[i]),decision=str(decision),level=level,atr=p['atr'],
                                range_lower=p['lower'],range_upper=p['upper'],efficiency=p['efficiency'],
                                decision_close=float(current.c),distance=side*(current.c-level)/p['atr'],
                                candidate_extreme=float(b.l.iloc[i:j+1].min() if side==1 else b.h.iloc[i:j+1].max()))
                            row.update(rules.signatures(current.o,current.h,current.l,current.c,b.c.iloc[j-1],b.c.iloc[j-2],level,side))
                            rows.append(row)
        print(f'encounters tf={tf} complete',flush=True)
    e=pd.DataFrame(rows); e['event_id']=np.arange(len(e))
    return e,audit


def add_outcomes(e,a,funding):
    for horizon in HORIZONS:
        outcomes=[]
        for row in e.itertuples(index=False):
            outcomes.append(outcome(a,pd.Timestamp(row.decision),row.side,row.atr,row.candidate_extreme,horizon,funding))
        result=pd.DataFrame(outcomes).add_suffix('_'+str(horizon))
        e=pd.concat([e,result],axis=1)
        print(f'outcomes horizon={horizon} complete',flush=True)
    return e


def analyze(e,a,metadata):
    first=a.index[0].floor('D'); nday=(a.index[-1].floor('D')-first).days+1
    decisions=pd.to_datetime(e.decision,utc=True)
    days=((decisions.dt.floor('D')-first)/pd.Timedelta(days=1)).astype(int).to_numpy()
    clocks=(decisions.dt.hour*3600+decisions.dt.minute*60).to_numpy()
    features=np.c_[e.distance,np.log(e.vol_ratio),np.sin(clocks*2*np.pi/86400),np.cos(clocks*2*np.pi/86400)]
    groups=list(e.groupby(['tf','family','edge','side','approach','context'],sort=True).indices.values())
    books=[]; rows=[]; matchrows=[]
    for horizon in HORIZONS:
        valid=np.isfinite(e['gross_'+str(horizon)].to_numpy())
        win=e['win_'+str(horizon)].to_numpy(); net=e['net14_'+str(horizon)].to_numpy()
        for tf in TFS:
            for family in FAMILIES:
                for ctx in rules.CONTEXTS:
                    cell=(e.tf.to_numpy()==tf)&(e.family.to_numpy()==family)&(e.context.to_numpy()==ctx)
                    for sig in SIGS:
                        is_signal=e.source.to_numpy()=='REAL'
                        if sig=='level_bounce': is_signal &= e.side.to_numpy()==e.approach.to_numpy()
                        elif sig!='level_test': is_signal &= e[sig].to_numpy(dtype=bool)
                        candidates=np.flatnonzero(cell&is_signal&valid)
                        signals=[]; controls=[]
                        for ids in groups:
                            if not len(ids) or not cell[ids[0]]: continue
                            options=ids[valid[ids]&(e.source.to_numpy()[ids]==('PLACEBO' if sig in ['level_test','level_bounce'] else 'REAL'))]
                            if sig not in ['level_test','level_bounce']: options=options[~e[sig].to_numpy(dtype=bool)[options]]
                            for i in ids[is_signal[ids]&valid[ids]]:
                                js=rules.nearest_controls(features,days,clocks,int(i),options)
                                if len(js):
                                    signals.append(int(i)); controls.append(js)
                                    matchrows.append(dict(tf=tf,family=family,context=ctx,signature=sig,horizon=horizon,
                                        event_id=int(i),control_ids='|'.join(map(str,js))))
                        ids=np.asarray(signals,dtype=int)
                        row=dict(tf=tf,family=family,context=ctx,signature=sig,horizon=horizon,
                                 eligible=len(candidates),censored=int(np.sum(cell&is_signal&~valid)),
                                 n=len(ids),days=len(np.unique(days[ids])),coverage=len(ids)/len(candidates) if len(candidates) else 0,
                                 candidate=False)
                        book={k:np.zeros(nday) for k in ['count','win','lift','control_win','control_weight','net14','gross','net20','barrier_low','barrier_high','persist']}
                        if len(ids):
                            row['max_smd']=rules.imbalance(features,ids,controls)
                            book['count']=np.bincount(days[ids],minlength=nday)
                            for key,values in [('win',win),('gross',e['gross_'+str(horizon)].to_numpy()),
                                               ('net14',net),('net20',e['net20_'+str(horizon)].to_numpy())]:
                                book[key]=np.bincount(days[ids],weights=values[ids],minlength=nday)
                            book['lift']=rules.contrast_book(win,days,ids,controls,nday)
                            for js in controls:
                                np.add.at(book['control_win'],days[js],win[js]/len(js))
                                np.add.at(book['control_weight'],days[js],1/len(js))
                            for key in ['barrier_low','barrier_high','persist']:
                                if horizon==1440:
                                    book[key]=np.bincount(days[ids],weights=e[key+'_1440'].to_numpy()[ids],minlength=nday)
                        books.append(book); rows.append(row)
        print(f'matching horizon={horizon} complete',flush=True)
    rng=np.random.default_rng(20261014)
    starts=rng.integers(0,nday,size=(1000,(nday+6)//7))
    sample=((starts[:,:,None]+np.arange(7))%nday).reshape(1000,-1)[:,:nday]
    weights=np.array([np.bincount(x,minlength=nday) for x in sample],dtype=float)
    denom=weights@np.stack([b['count'] for b in books],axis=1)
    z=NormalDist().inv_cdf(1-.05/(2*6048))
    for key in ['win','lift','net14','gross','net20','barrier_low','barrier_high','persist']:
        totals=np.stack([b[key] for b in books],axis=1)
        if key=='lift':
            draws=rules.bootstrap_contrast(weights,np.stack([b['win'] for b in books],axis=1),
                np.stack([b['count'] for b in books],axis=1),np.stack([b['control_win'] for b in books],axis=1),
                np.stack([b['control_weight'] for b in books],axis=1))
        else:
            draws=np.divide(weights@totals,denom,out=np.full(denom.shape,np.nan),where=denom>0)
        for i,row in enumerate(rows):
            if not row['n'] or key in ['barrier_low','barrier_high','persist'] and row['horizon']!=1440: continue
            valid_draws=draws[:,i][np.isfinite(draws[:,i])]
            mean=float(totals[:,i].sum()/row['n'])
            se=float(valid_draws.std(ddof=1))
            row[key]=mean; row[key+'_ci']=np.quantile(valid_draws,[.025,.975]).tolist()
            row[key+'_bonf']=[mean-z*se,mean+z*se]
    for row in rows:
        if row['n']:
            row['candidate']=bool(row['signature']!='level_test' and row['n']>=100 and row['days']>=30 and row['coverage']>=.8
                and row['max_smd']<=.25 and row['lift_bonf'][0]>0 and row['net14_bonf'][0]>0)
    pd.DataFrame(rows).to_csv(OUT/'TRIAL_REGISTRY.csv',index=False,lineterminator='\n')
    pd.DataFrame(matchrows).to_csv(OUT/'matches.csv.gz',index=False,compression={'method':'gzip','mtime':0},lineterminator='\n')
    e.to_csv(OUT/'encounters.csv.gz',index=False,compression={'method':'gzip','mtime':0},lineterminator='\n')
    result=dict(metadata,rows=rows,registered_cells=2016,inference_family=6048,
        candidates=sum(r['candidate'] for r in rows),matched_pairs=len(matchrows),ledger_rows=len(e),
        code_hashes={name:hashlib.sha256((OUT/name).read_bytes()).hexdigest() for name in ['engine.py','rules.py','PRE_REG.md']})
    (OUT/'results.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ['rows','price_manifest','funding_manifest']}),flush=True)


if __name__=='__main__':
    if (OUT/'results.json').exists(): raise SystemExit('Existing outcomes: archive and log before another trial')
    raw,manifest=load_dev()
    ftime,frate,fprice,fmanifest=load_funding(raw)
    e,audit=feature_ledger(raw)
    e=add_outcomes(e,raw,(ftime,frate,fprice))
    analyze(e,raw,dict(price_manifest=manifest,funding_manifest=fmanifest,encounter_audit=audit,
                     start=str(raw.index[0]),end=str(raw.index[-1]),bars=len(raw)))
