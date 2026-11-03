"""Independent causal/EXACT pitchfork replay; loads only minute files through 2024-06."""
import csv, glob, math, random
from datetime import datetime, timezone
from pathlib import Path
import tempfile
import sys
import numpy as np
ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT))
from MyTradingSys.backtest.fees import BINANCE_MAKER, BINANCE_TAKER

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
START = int(datetime(2020,1,1,tzinfo=timezone.utc).timestamp()*1000)
CUT = int(datetime(2024,7,1,tzinfo=timezone.utc).timestamp()*1000)
BAR = 14_400_000
LB, SWING, STOP, HORIZON = 4, .03, .015, 60
FEE = BINANCE_MAKER + BINANCE_TAKER + BINANCE_MAKER  # SOURCED: fees.py maker entry, taker exit, maker-sized slip

def month_of(path):
    parts=Path(path).stem.rsplit('-',2)
    return int(parts[-2])*100+int(parts[-1])

def admitted_files(paths):
    return sorted(set(p for p in paths if 202001 <= month_of(p) <= 202406))

def minute_files():
    pats = [r'F:/MTS/data/dev_ext_2019_2021/klines/BTCUSDT-1m-*.csv', r'F:/MTS/data/tom_raw/klines/BTCUSDT-1m-*.csv']
    paths=[]
    for pat in pats:
        paths.extend(glob.glob(pat))
    # File names are BTCUSDT-1m-YYYY-MM.csv; discard post-cutoff paths before opening any file.
    return admitted_files(paths)

def load_bars():
    by_ts={}; duplicate_rows=0; conflicts=0
    for p in minute_files():
        with open(p,encoding='utf-8') as f:
            for row in csv.reader(f):
                if len(row)<6 or not row[0].isdigit(): continue
                ts=int(row[0])
                if ts<START or ts>=CUT: continue
                o,h,l,c,v=map(float,row[1:6]); candle=(o,h,l,c,v)
                if ts in by_ts:
                    duplicate_rows+=1
                    if by_ts[ts]!=candle: conflicts+=1
                    continue
                by_ts[ts]=candle
    # Aggregate only after timestamp sort/dedup so overlapping source files cannot set a stale close.
    data={}
    for ts,(o,h,l,c,v) in sorted(by_ts.items()):
        k=ts//BAR*BAR
        if k not in data:data[k]=[o,h,l,c,v]
        else:
            x=data[k]; x[1]=max(x[1],h); x[2]=min(x[2],l); x[3]=c; x[4]+=v
    bars=[(ts,*data[ts]) for ts in sorted(data)]
    if conflicts: raise ValueError(f'{conflicts} conflicting duplicate minute timestamps')
    mins=np.array([(ts,*by_ts[ts][:4]) for ts in sorted(by_ts)],dtype=float)
    print('source files admitted',len(minute_files()),'dedup identical rows',duplicate_rows,flush=True)
    return bars,mins,{'source_files':len(minute_files()),'identical_duplicate_rows':duplicate_rows,'conflicting_duplicate_rows':conflicts}

def pivot_sets(bars, causal=True):
    hi=[x[2] for x in bars]; lo=[x[3] for x in bars]; piv=[]; last=None; out=[]
    for confirm in range(2*LB,len(bars)):
        i=confirm-LB
        ph=all(hi[i]>=hi[j] for j in range(i-LB,confirm+1) if j!=i)
        pl=all(lo[i]<=lo[j] for j in range(i-LB,confirm+1) if j!=i)
        changed=False
        if last is None:
            if ph: piv.append((i,hi[i],True)); last=True; changed=True
            elif pl: piv.append((i,lo[i],False)); last=False; changed=True
        elif last:
            if ph and hi[i]>piv[-1][1]: piv[-1]=(i,hi[i],True); changed=True
            elif pl and (piv[-1][1]-lo[i])/max(1e-9,piv[-1][1])>=SWING: piv.append((i,lo[i],False)); last=False; changed=True
        else:
            if pl and lo[i]<piv[-1][1]: piv[-1]=(i,lo[i],False); changed=True
            elif ph and (hi[i]-piv[-1][1])/max(1e-9,piv[-1][1])>=SWING: piv.append((i,hi[i],True)); last=True; changed=True
        if changed and len(piv)>=3: out.append((tuple(piv[-3:]),confirm))
    if causal: return out
    # Final pivot list: one terminal representation per adjacent triplet.
    p=[]; last=None
    for i in range(2*LB,len(bars)):
        j=i-LB
        ph=all(hi[j]>=hi[k] for k in range(j-LB,i+1) if k!=j); pl=all(lo[j]<=lo[k] for k in range(j-LB,i+1) if k!=j)
        if last is None:
            if ph:p.append((j,hi[j],True));last=True
            elif pl:p.append((j,lo[j],False));last=False
        elif last:
            if ph and hi[j]>p[-1][1]:p[-1]=(j,hi[j],True)
            elif pl and (p[-1][1]-lo[j])/max(1e-9,p[-1][1])>=SWING:p.append((j,lo[j],False));last=False
        else:
            if pl and lo[j]<p[-1][1]:p[-1]=(j,lo[j],False)
            elif ph and (hi[j]-p[-1][1])/max(1e-9,p[-1][1])>=SWING:p.append((j,hi[j],True));last=True
    # Retrospective control only: adjacent final pivots, not the causal trading arm.
    return [(triple, triple[2][0]+LB) for triple in zip(p, p[1:], p[2:])]

def profile_va(bars, ps):
    a,b=sorted((ps[0][0],ps[2][0])); sub=bars[a:b+1]
    if len(sub)<2:return None
    lo=min(x[3] for x in sub); hi=max(x[2] for x in sub)
    if hi<=lo:return None
    bins={}
    for x in sub:
        low,high,volume=x[3],x[2],x[5]
        first=math.floor(low/10); last=max(first,math.ceil(high/10)-1)
        for key in range(first,last+1):
            overlap=max(0.,min(high,(key+1)*10)-max(low,key*10))
            bins[key]=bins.get(key,0)+(volume*overlap/(high-low) if high>low else volume)
    if not bins:return None
    keys=sorted(bins); total=sum(bins.values()); poc=max(keys,key=lambda k:bins[k]); vol=bins[poc]; left=right=poc
    first,last=keys[0],keys[-1]
    while vol<.7*total and (left>keys[0] or right<keys[-1]):
        lv=bins.get(left-1,0); rv=bins.get(right+1,0)
        if lv>=rv and left>first:left-=1;vol+=lv
        elif right<last:right+=1;vol+=rv
        elif left>first:left-=1;vol+=lv
        else:break
    return (left*10,(right+1)*10)

def geometry(ps):
    (i0,y0,_),(i1,y1,_),(i2,y2,side2)=ps
    # Modified Schiff: shift P0 halfway in price toward P1, keep its time; parallel tines through P1/P2.
    t0=float(i0); p0=y0+.5*(y1-y0); tm=(i1+i2)/2; pm=(y1+y2)/2
    if tm<=t0: return None
    slope=(pm-p0)/(tm-t0); ml0=p0-slope*t0
    o1=y1-(slope*(i1-t0)+p0); o2=y2-(slope*(i2-t0)+p0)
    upper=max(o1,o2); lower=min(o1,o2)
    return (slope,ml0,upper,lower,not side2)

def line(g,t,which):
    m,b,u,l,long=g; return m*t+b+(l if which=='entry' and long else u if which=='entry' else 0)

def activation_index(known,exact):
    return known+1 if exact else known

def walk_1m(rows,start,deadline,long,entry,target):
    stop=entry*(1-STOP if long else 1+STOP)
    for r in rows[start:]:
        if r[0]>=deadline:break
        if (r[3]<=stop if long else r[2]>=stop):return -STOP
        tgt=target(int(r[0])) if callable(target) else target
        if (r[2]>=tgt if long else r[3]<=tgt):return (tgt-entry)/entry if long else (entry-tgt)/entry
    if start>=len(rows):return 0.
    end=min(np.searchsorted(rows[:,0],deadline,'left')-1,len(rows)-1)
    close=rows[max(start,end),4]
    return (close-entry)/entry if long else (entry-close)/entry

def trade(ps,known,bars,minute,exact=True):
    g=geometry(ps)
    if g is None:return None
    slope,b,u,l,long=g; start=activation_index(known,exact)
    end=min(known+HORIZON,len(bars)-1)
    if start>end:return None
    p2idx=ps[2][0]
    # RESTING limit only becomes active next 4h bar for EXACT; study arm begins on confirmation bar.
    for k in range(start,end+1):
        ts=bars[k][0]; tine=slope*k+b+(l if long else u)
        a=np.searchsorted(minute[:,0],ts,'left'); z=np.searchsorted(minute[:,0],ts+BAR,'left')
        q=minute[a:z]
        hit=np.flatnonzero((q[:,3]<=tine)&(q[:,2]>=tine))
        if not len(hit):continue
        ix=a+int(hit[0]); entry_ts=int(minute[ix,0]); stop=tine*(1-STOP if long else 1+STOP)
        target=lambda t: slope*((t-bars[0][0])//BAR)+b
        # Independent 1m event walk; within each minute adverse stop has priority.
        tgt=target(entry_ts)
        gross=walk_1m(minute,ix,bars[end][0]+BAR,long,tine,target)
        return (entry_ts,gross,long,abs(tgt-tine)/tine)
    return None

def study_trade(ps,known,bars):
    """OHLC approximation of study semantics, separately labeled from the 1m EXACT walk."""
    g=geometry(ps)
    if g is None:return None
    slope,b,u,l,long=g; entry=None; start=known; end=min(known+HORIZON,len(bars))
    for k in range(start,end):
        ts,o,h,low,c,_v=bars[k]
        tine=slope*k+b+(l if long else u)
        if entry is None:
            if low<=tine<=h: entry=(tine,ts)
            continue
        target=slope*k+b
        # Preserve study ordering: target is evaluated before the stop on each later 4h bar.
        if (h>=target if long else low<=target):
            return (entry[1],((target-entry[0])/entry[0] if long else (entry[0]-target)/entry[0]),long,abs(target-entry[0])/entry[0])
        if (low<=entry[0]*(1-STOP) if long else h>=entry[0]*(1+STOP)):
            return (entry[1],-STOP,long,abs(target-entry[0])/entry[0])
    if entry is None:return None
    c=bars[end-1][4]
    return (entry[1],((c-entry[0])/entry[0] if long else (entry[0]-c)/entry[0]),long,abs(slope*(end-1)+b-entry[0])/entry[0])

def metrics(trades):
    if not trades:return (0,0,None,0)
    vals=np.array([r[1]-FEE for r in trades])*100; months={}
    for (ts,_,*__),v in zip(trades,vals):months.setdefault(datetime.fromtimestamp(ts/1000,timezone.utc).strftime('%Y-%m'),[]).append(v)
    keys=list(months); rng=random.Random(7); boot=[]
    for _ in range(2000):
        s=[]
        for __ in keys:s.extend(months[rng.choice(keys)])
        boot.append(sum(s)/len(s))
    pos=vals[vals>0].sum(); neg=-vals[vals<=0].sum()
    return (len(vals),round(float(vals.mean()),3),(round(sorted(boot)[50],3),round(sorted(boot)[1950],3)),round(float(pos/neg),2) if neg else float('inf'))

def run_checks():
    # A post-cutoff sentinel path is rejected before any attempt to open it.
    with tempfile.TemporaryDirectory(dir=OUT) as td:
        sentinel=Path(td)/'BTCUSDT-1m-2024-07.csv'; sentinel.write_text('must not be opened',encoding='utf-8')
        assert str(sentinel) not in admitted_files([str(sentinel)])
    # Hand-worked four equal-volume bins; 70% VA expands from the lower tied POC to the upper edge.
    fixture=[(0,0,15,5,0,10),(1,0,35,25,0,10)]
    assert profile_va(fixture,((0,5,False),(0,0,True),(1,25,False)))==(0,30)
    # Same-minute target and stop: adverse stop is first.
    same=np.array([[0,100,102,98,100]],dtype=float)
    assert walk_1m(same,0,60_000,True,100,101)==-STOP
    assert walk_1m(same,0,60_000,False,100,99)==-STOP
    # Mirrored paths have symmetric +1% target outcomes.
    up=np.array([[0,100,100.5,99.9,100.2],[60_000,100.2,101.2,100,101]],dtype=float)
    dn=np.array([[0,100,100.1,99.5,99.8],[60_000,99.8,100,98.8,99]],dtype=float)
    assert abs(walk_1m(up,0,120_000,True,100,101)-.01)<1e-12
    assert abs(walk_1m(dn,0,120_000,False,100,99)-.01)<1e-12
    sloped=np.array([[0,100,100.5,99.9,100.2],[60_000,100.2,102.5,100,102]],dtype=float)
    assert abs(walk_1m(sloped,0,120_000,True,100,lambda ts:101 if ts==0 else 103)-.02)<1e-12
    assert activation_index(20,True)==21 and activation_index(20,False)==20
    print('hand checks passed: cutoff sentinel, VA bins, stop-first, long/short symmetry, next-bar activation',flush=True)

def main():
    run_checks()
    bars,mins,ingest=load_bars(); assert bars and bars[-1][0]+BAR<=CUT
    print('bars4h',len(bars),'cut',datetime.fromtimestamp((bars[-1][0]+BAR)/1000,timezone.utc).isoformat(),flush=True)
    print('bars1m',len(mins),'missing 1m slots',int((mins[-1,0]-mins[0,0])//60000+1-len(mins)),flush=True)
    ts4=np.array([b[0] for b in bars]); sizes=np.searchsorted(mins[:,0],ts4+BAR)-np.searchsorted(mins[:,0],ts4)
    partial=ts4[sizes!=240]
    print('4h groups not equal to 240 minutes',len(partial),'timestamps',partial[:20].astype(int).tolist(),flush=True)
    rows=[]
    for label,ss in [('CAUSAL',pivot_sets(bars,True)),('FINAL',pivot_sets(bars,False))]:
        tr=[]
        for ps,k in ss:
            if k>=len(bars):continue
            va=profile_va(bars,ps)
            if va and va[0]<=ps[2][1]<=va[1]:
                r=study_trade(ps,k,bars)
                if r:tr.append(r)
        rows.append((label,tr));print(label,'setups',len(ss),'stats',metrics(tr),flush=True)
    exact=[]
    for ps,k in pivot_sets(bars,True):
        if k>=len(bars):continue
        va=profile_va(bars,ps)
        if va and va[0]<=ps[2][1]<=va[1]:
            r=trade(ps,k,bars,mins,exact=True)
            if r:exact.append(r)
    print('EXACT setups/stats',len(pivot_sets(bars,True)),metrics(exact),flush=True)
    # Placebo uses matched exact side and target distance at a random same-year 4h open.
    rng=random.Random(11); years={}
    for b in bars[:-HORIZON]:years.setdefault(datetime.fromtimestamp(b[0]/1000,timezone.utc).year,[]).append(b)
    placebo=[]; placebo_seed=11
    rng=random.Random(placebo_seed)
    for _ in range(100):
        vals=[]
        for ts,gross,side,gap in exact:
            y=datetime.fromtimestamp(ts/1000,timezone.utc).year; b0=rng.choice(years[y]); i=np.searchsorted(mins[:,0],b0[0]);
            if i>=len(mins):continue
            entry=mins[i,1]; end=b0[0]+HORIZON*BAR; stop=entry*(1-STOP if side else 1+STOP); tgt=entry*(1+gap if side else 1-gap)
            raw=walk_1m(mins,i,end,side,entry,tgt)
            vals.append(raw-FEE)
        placebo.append(float(np.mean(vals))*100 if vals else 0.)
    result={
        'window_utc':['2020-01-01','2024-07-01 exclusive'],'input_files':ingest['source_files'],
        'bars_4h':len(bars),'bars_1m':len(mins),'missing_1m_slots':int((mins[-1,0]-mins[0,0])//60000+1-len(mins)),
        'incomplete_4h_groups':len(partial),'identical_duplicate_minute_rows':ingest['identical_duplicate_rows'],'conflicting_duplicate_rows':ingest['conflicting_duplicate_rows'],
        'labels':{'params':'SOURCED from audit/study as encoding under test; not trader-verified, OURS as trading settings','entry_stop_walk_placebo':'OURS independent implementation','cost':'SOURCED fees.py maker+taker rates; extra maker-sized 2bp slippage is OURS assumption; 9bp total'},
        'parameters':{'zigzag_lookback':LB,'swing_threshold':SWING,'stop':STOP,'horizon_4h_bars':HORIZON,'fee':FEE,'placebo_runs':100,'placebo_seed':placebo_seed,'bootstrap_draws':2000,'bootstrap_seed':7},
        'arms':{'STUDY_final_pivots':metrics(rows[1][1]),'CAUSAL':metrics(rows[0][1]),'EXACT':metrics(exact)},
        'placebo':{'mean_net_pct':round(float(np.mean(placebo)),3),'p95_net_pct':round(float(np.percentile(placebo,95)),3),'run_means_net_pct':[round(x,6) for x in placebo]},
    }
    (OUT/'recheck_results.json').write_text(__import__('json').dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    print('EXACT',metrics(exact),'PLACEBO mean/p95',round(float(np.mean(placebo)),3),round(float(np.percentile(placebo,95)),3),flush=True)
if __name__=='__main__':
    if sys.argv[1:] == ['--checks-only']: run_checks()
    else: main()
