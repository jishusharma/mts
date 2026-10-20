"""Independent scalar/raw verifier. Does not import engine or rules."""
import hashlib
import io
import json
import math
from statistics import NormalDist
from pathlib import Path
import zipfile

import numpy as np
import pandas as pd

OUT=Path(__file__).resolve().parent


def independent_state(c,h,l):
    tr=[max(h[i]-l[i],abs(h[i]-c[i]),abs(l[i]-c[i])) for i in range(20)]
    atr=sum(tr)/20
    efficiency=abs(c[-1]-c[0])/sum(abs(c[i+1]-c[i]) for i in range(20))
    upper,lower=max(h),min(l)
    oldh,newh=max(h[:10]),max(h[10:]); oldl,newl=min(l[:10]),min(l[10:])
    phase='TRANSITION'
    if efficiency>=.4 and c[-1]>c[0] and newh>oldh+.5*atr and newl>oldl+.5*atr: phase='UP_TREND'
    elif efficiency>=.4 and c[-1]<c[0] and newh<oldh-.5*atr and newl<oldl-.5*atr: phase='DOWN_TREND'
    else:
        def touches(values,test):
            ids=[]
            for i,x in enumerate(values):
                if test(x) and (not ids or i-ids[-1]>=2): ids.append(i)
            return len(ids)
        if efficiency<=.3 and upper-lower>=2*atr and abs(oldh-newh)<=.75*atr and abs(oldl-newl)<=.75*atr:
            if touches(h,lambda x:x>=upper-.5*atr)>=2 and touches(l,lambda x:x<=lower+.5*atr)>=2: phase='BOUNDED_RANGE'
    return phase,atr,efficiency,lower,upper


def main():
    r=json.loads((OUT/'results.json').read_text())
    frozen=json.loads((OUT/'FROZEN.json').read_text())
    for name,digest in r['code_hashes'].items():
        assert digest==frozen['files'][name]==hashlib.sha256((OUT/name).read_bytes()).hexdigest()
    parts=[]
    for x in r['price_manifest']:
        assert '2022-01'<=x['month']<='2024-06'
        raw=Path(x['path']).read_bytes(); assert hashlib.sha256(raw).hexdigest()==x['checksum']
        with zipfile.ZipFile(io.BytesIO(raw)) as z: b=pd.read_csv(z.open(z.namelist()[0]),header=None,usecols=list(range(6)),dtype=str)
        b=b[pd.to_numeric(b[0],errors='coerce').notna()].astype(float)
        b.index=pd.to_datetime(b.pop(0).astype('int64'),unit='ms',utc=True)
        b.columns=['o','h','l','c','v']; parts.append(b)
    a=pd.concat(parts); assert len(a)==r['bars']
    assert np.asarray(a.index[1:]-a.index[:-1]==pd.Timedelta(minutes=1)).all()
    fparts=[]
    for x in r['funding_manifest']:
        raw=Path(x['path']).read_bytes(); assert hashlib.sha256(raw).hexdigest()==x['sha256']
        with zipfile.ZipFile(io.BytesIO(raw)) as z: fparts.append(pd.read_csv(z.open(z.namelist()[0])))
    f=pd.concat(fparts).sort_values('calc_time')
    ft=pd.DatetimeIndex(pd.to_datetime(f.calc_time,unit='ms',utc=True)).floor('8h')
    fr=f.last_funding_rate.to_numpy()
    fp=a.o.reindex(ft).to_numpy()
    e=pd.read_csv(OUT/'encounters.csv.gz'); m=pd.read_csv(OUT/'matches.csv.gz')
    assert len(e)==r['ledger_rows'] and len(m)==r['matched_pairs']
    period={}
    for minutes in [60,240]:
        count=len(a)//minutes
        h=a.h.to_numpy().reshape(count,minutes).max(axis=1)
        l=a.l.to_numpy().reshape(count,minutes).min(axis=1)
        c=a.c.to_numpy().reshape(count,minutes)[:,-1]
        prior=np.r_[np.nan,c[:-1]]
        tr=np.maximum(h-l,np.maximum(abs(h-prior),abs(l-prior)))
        atr=pd.Series(tr).rolling(20,min_periods=20).mean().to_numpy()
        period[minutes]=(h,l,c,atr)
    checked=0
    for _,row in e.sample(min(126,len(e)),random_state=73).iterrows():
        encounter=pd.Timestamp(row.encounter); decision=pd.Timestamp(row.decision)
        assert decision-encounter==pd.Timedelta(minutes=3*int(row.tf))
        states={}
        for minutes in [60,240]:
            k=int((encounter.floor(f'{minutes}min')-a.index[0])/pd.Timedelta(minutes=minutes))-1
            h,l,c,atr=period[minutes]
            states[minutes]=independent_state(c[k-20:k+1],h[k-19:k+1],l[k-19:k+1])
            if minutes==240:
                v=(atr[k]/c[k])/np.median((atr/c)[k-180:k])
                assert abs(v-row.vol_ratio)<1e-10
        ph,A,er,B,U=states[240]
        assert ph==row.phase and states[60][0]==row.local_phase
        assert abs(A-row.atr)<1e-9 and abs(er-row.efficiency)<1e-10
        boundary=encounter.floor('4h' if row.family=='4h' else 'D') if row.family!='week' else encounter.floor('D')-pd.Timedelta(days=encounter.weekday())
        start=boundary-pd.Timedelta(hours=4 if row.family=='4h' else (24 if row.family=='day' else 168))
        old=a.loc[(a.index>=start)&(a.index<boundary)]
        real=old.h.max() if row.edge=='h' else old.l.min()
        level=real
        if row.source=='PLACEBO':
            px=a.at[boundary,'o']
            key=f'20261014|{row.family}|{row.edge}|{boundary}'.encode()
            rng=np.random.default_rng(int.from_bytes(hashlib.sha256(key).digest()[:8],'big'))
            level=px+rng.choice([-1,1])*rng.uniform(.75,1.25)*abs(real-px)
        assert abs(level-row.level)<1e-8
        direct={'UP_TREND':1,'DOWN_TREND':-1}.get(ph,0)
        localdir={'UP_TREND':1,'DOWN_TREND':-1}.get(states[60][0],0)
        if direct: ctx='TREND_ALIGNED' if direct==row.side and localdir==row.side else 'TREND_CONFLICT'
        elif ph=='BOUNDED_RANGE' and (B-.5*A<=level<=B+.25*(U-B) or U-.25*(U-B)<=level<=U+.5*A): ctx='RANGE_EDGE'
        elif ph=='BOUNDED_RANGE' and B+.25*(U-B)<level<U-.25*(U-B): ctx='RANGE_INTERIOR'
        else: ctx='TRANSITION_HIGH_VOL' if v>=1.5 else 'TRANSITION_OTHER'
        assert ctx==row.context
        path=a.loc[(a.index>=encounter)&(a.index<decision)]
        assert len(path)==3*row.tf
        close=path.c.iloc[-1]
        assert abs(row.distance-row.side*(close-level)/A)<1e-9
        current=path.iloc[-int(row.tf):]
        prev=path.c.iloc[-int(row.tf)-1]; prev2=path.c.iloc[-2*int(row.tf)-1]
        x,p,q=row.side*(close-level),row.side*(prev-level),row.side*(prev2-level)
        low,high=current.l.min(),current.h.max()
        span=high-low
        loc=(close-low if row.side==1 else high-close)/span if span>0 else 0
        body=abs(close-current.o.iloc[0])/span if span>0 else 0
        expected=dict(rejection=p>0 and (low<level if row.side==1 else high>level) and x>0,
            acceptance=q<=0 and p>0 and x>0,reclaim=q>0 and p<0 and x>0,
            retest=q>0 and p>0 and (low<=level if row.side==1 else high>=level) and x>0,
            strong_break=p<=0 and x>0 and loc>=.75 and body>=.6)
        expected['break']=p<=0 and x>0
        for sig,value in expected.items(): assert bool(row[sig])==value
        extreme=path.l.min() if row.side==1 else path.h.max()
        assert abs(extreme-row.candidate_extreme)<1e-8
        for H in [60,1440]:
            end=decision+pd.Timedelta(minutes=H)
            if end not in a.index:
                assert np.isnan(row[f'gross_{H}']); continue
            gross=row.side*(a.at[end,'o']/a.at[decision,'o']-1)
            fund=row.side*sum(fr[(ft>decision)&(ft<=end)]*fp[(ft>decision)&(ft<=end)])/a.at[decision,'o']
            assert abs(gross-row[f'gross_{H}'])<1e-12
            assert abs(fund-row[f'funding_{H}'])<1e-12
            assert abs(gross-fund-.0014-row[f'net14_{H}'])<1e-12
        checked+=1
    clocks=pd.to_datetime(e.decision,utc=True)
    day=clocks.dt.floor('D')
    clock=(clocks.dt.hour*3600+clocks.dt.minute*60).to_numpy()
    feat=np.c_[e.distance,np.log(e.vol_ratio),np.sin(clock*2*np.pi/86400),np.cos(clock*2*np.pi/86400)]
    matchchecked=0
    for _,row in m.sample(min(126,len(m)),random_state=81).iterrows():
        i=int(row.event_id); subject=e.iloc[i]; H=int(row.horizon)
        mask=np.isfinite(e[f'gross_{H}'])
        for key in ['tf','family','edge','side','approach','context']: mask &= e[key]==subject[key]
        mask &= e.source==('PLACEBO' if row.signature in ['level_test','level_bounce'] else 'REAL')
        if row.signature not in ['level_test','level_bounce']: mask &= ~e[row.signature]
        options=[]
        for j in np.flatnonzero(mask):
            d=abs(clock[j]-clock[i]); d=min(d,86400-d)
            delta=feat[j]-feat[i]
            if day.iloc[j]==day.iloc[i] or np.sign(feat[j,0])!=np.sign(feat[i,0]): continue
            if abs(delta[0])>.5 or abs(delta[1])>math.log(2) or d>10800: continue
            dist=delta[0]**2+delta[1]**2+.25*(delta[2]**2+delta[3]**2)
            options.append((dist,int(j)))
        ids=[]; used=set()
        for _,j in sorted(options):
            if day.iloc[j] not in used: ids.append(j); used.add(day.iloc[j])
            if len(ids)==10: break
        assert len(ids)>=5
        assert ids==list(map(int,str(row.control_ids).split('|')))
        matchchecked+=1
    group=m.groupby(['tf','family','context','signature','horizon'])
    countchecks=0
    for row in r['rows']:
        key=tuple(row[k] for k in ['tf','family','context','signature','horizon'])
        if row['n']==0:
            assert key not in group.indices; countchecks+=1; continue
        pairs=group.get_group(key); assert len(pairs)==row['n']
        ids=pairs.event_id.astype(int).to_numpy(); H=row['horizon']
        gross=e.iloc[ids][f'gross_{H}'].mean(); net=e.iloc[ids][f'net14_{H}'].mean()
        lift=sum(e.at[int(pair.event_id),f'win_{H}']-e.iloc[list(map(int,str(pair.control_ids).split('|')))][f'win_{H}'].mean()
                 for pair in pairs.itertuples())/len(pairs)
        assert abs(gross-row['gross'])<1e-12 and abs(net-row['net14'])<1e-12 and abs(lift-row['lift'])<1e-12
        countchecks+=1
    # Independently rebuild inference for five cells chosen by count, not return.
    nday=(a.index[-1].floor('D')-a.index[0].floor('D')).days+1
    rng=np.random.default_rng(20261014)
    starts=rng.integers(0,nday,size=(1000,(nday+6)//7))
    sampled=[[(int(start)+offset)%nday for start in ss for offset in range(7)][:nday] for ss in starts]
    dayids=((day-a.index[0].floor('D'))/pd.Timedelta(days=1)).astype(int).to_numpy()
    z=NormalDist().inv_cdf(1-.05/(2*r['inference_family'])); cichecks=0
    for row in sorted([x for x in r['rows'] if x['n'] and not x['signature'].startswith('level_')],key=lambda x:-x['n'])[:5]:
        key=tuple(row[k] for k in ['tf','family','context','signature','horizon'])
        pairs=group.get_group(key); H=row['horizon']
        cnt=[0]*nday; sigwin=[0.]*nday; ctrlwin=[0.]*nday; ctrlmass=[0.]*nday; netbook=[0.]*nday
        for pair in pairs.itertuples():
            i=int(pair.event_id); ids=list(map(int,str(pair.control_ids).split('|')))
            cnt[dayids[i]]+=1; netbook[dayids[i]]+=e.at[i,f'net14_{H}']; sigwin[dayids[i]]+=e.at[i,f'win_{H}']
            for j in ids:
                ctrlwin[dayids[j]]+=e.at[j,f'win_{H}']/len(ids); ctrlmass[dayids[j]]+=1/len(ids)
        for metric,book in [('lift',sigwin),('net14',netbook)]:
            draws=[]
            for daysample in sampled:
                denominator=sum(cnt[d] for d in daysample)
                if not denominator: continue
                value=sum(book[d] for d in daysample)/denominator
                if metric=='lift':
                    control_den=sum(ctrlmass[d] for d in daysample)
                    if not control_den: continue
                    value-=sum(ctrlwin[d] for d in daysample)/control_den
                draws.append(value)
            ci=np.quantile(draws,[.025,.975]); se=np.std(draws,ddof=1)
            assert np.max(abs(ci-row[metric+'_ci']))<1e-10
            expected=[row[metric]-z*se,row[metric]+z*se]
            assert np.max(abs(np.array(expected)-row[metric+'_bonf']))<1e-10
            cichecks+=1
    answer=dict(status='PASS',price_hashes=30,funding_hashes=30,raw_phase_level_context_return_funding_checks=checked,
                independent_control_selection_checks=matchchecked,registered_count_and_mean_checks=countchecks,
                independently_rebuilt_real_cell_intervals=cichecks,
                bootstrap_arithmetic='five highest-count candle-signature cells, two metrics each; plus independent known fixture; not every interval replicated')
    (OUT/'verification.json').write_text(json.dumps(answer,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(answer))


if __name__=='__main__': main()
