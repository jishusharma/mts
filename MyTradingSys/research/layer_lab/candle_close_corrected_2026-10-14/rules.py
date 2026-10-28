"""Pure-numpy frozen phase, matching and inference rules (PRE_REG.md)."""
import numpy as np

CONTEXTS=['TREND_ALIGNED','TREND_CONFLICT','RANGE_EDGE','RANGE_INTERIOR',
          'TRANSITION_HIGH_VOL','TRANSITION_OTHER']
SIGNATURES=['rejection','break','acceptance','reclaim','retest','strong_break']


def phase(closes,highs,lows):
    c,h,l=map(lambda x:np.asarray(x,dtype=float),(closes,highs,lows))
    blank=dict(phase='UNKNOWN',atr=np.nan,efficiency=np.nan,upper=np.nan,lower=np.nan)
    if len(c)!=21 or len(h)!=20 or len(l)!=20 or not all(np.isfinite(x).all() for x in [c,h,l]):
        return blank
    tr=np.maximum(h-l,np.maximum(abs(h-c[:-1]),abs(l-c[:-1])))
    a=float(tr.mean()); travelled=float(abs(np.diff(c)).sum())
    if a<=0 or travelled<=0:
        return blank
    er=float(abs(c[-1]-c[0])/travelled)
    u,b=float(h.max()),float(l.min())
    hi_old,hi_new=h[:10].max(),h[10:].max()
    lo_old,lo_new=l[:10].min(),l[10:].min()
    result=dict(phase='TRANSITION',atr=a,efficiency=er,upper=u,lower=b)
    if er>=.4 and c[-1]>c[0] and hi_new>hi_old+.5*a and lo_new>lo_old+.5*a:
        result['phase']='UP_TREND'
    elif er>=.4 and c[-1]<c[0] and hi_new<hi_old-.5*a and lo_new<lo_old-.5*a:
        result['phase']='DOWN_TREND'
    elif (er<=.3 and u-b>=2*a and abs(hi_old-hi_new)<=.75*a and abs(lo_old-lo_new)<=.75*a
          and separated_count(np.flatnonzero(h>=u-.5*a))>=2
          and separated_count(np.flatnonzero(l<=b+.5*a))>=2):
        result['phase']='BOUNDED_RANGE'
    return result


def separated_count(indices):
    last=-100; count=0
    for i in indices:
        if i-last>=2:
            count+=1; last=i
    return count


def context(p,local,side,level,vol):
    if p['phase']=='UNKNOWN' or not np.isfinite(vol):
        return 'UNKNOWN'
    direction={'UP_TREND':1,'DOWN_TREND':-1}.get(p['phase'],0)
    if direction:
        return 'TREND_ALIGNED' if direction==side and {'UP_TREND':1,'DOWN_TREND':-1}.get(local,0)==side else 'TREND_CONFLICT'
    if p['phase']=='BOUNDED_RANGE':
        b,u,a=p['lower'],p['upper'],p['atr']; w=u-b
        if b-.5*a<=level<=b+.25*w or u-.25*w<=level<=u+.5*a:
            return 'RANGE_EDGE'
        if b+.25*w<level<u-.25*w:
            return 'RANGE_INTERIOR'
    return 'TRANSITION_HIGH_VOL' if vol>=1.5 else 'TRANSITION_OTHER'


def signatures(o,h,l,c,prev,prev2,level,side):
    x,p,q=side*(c-level),side*(prev-level),side*(prev2-level)
    span=h-l
    loc=(c-l if side==1 else h-c)/span if span>0 else 0
    body=abs(c-o)/span if span>0 else 0
    br=p<=0 and x>0
    return dict(rejection=p>0 and (l<level if side==1 else h>level) and x>0,
        **{'break':br},acceptance=q<=0 and p>0 and x>0,reclaim=q>0 and p<0 and x>0,
        retest=q>0 and p>0 and (l<=level if side==1 else h>=level) and x>0,
        strong_break=br and loc>=.75 and body>=.6)


def nearest_controls(features,days,clocks,event,eligible):
    ids=np.asarray(eligible,dtype=int)
    if not len(ids): return ids
    f=features[ids]-features[event]
    clock=abs(clocks[ids]-clocks[event]); clock=np.minimum(clock,86400-clock)
    ok=(days[ids]!=days[event])&(np.sign(features[ids,0])==np.sign(features[event,0]))
    ok &= (abs(f[:,0])<=.5)&(abs(f[:,1])<=np.log(2))&(clock<=10800)
    ids=ids[ok]; f=f[ok]
    distance=f[:,0]**2+f[:,1]**2+.25*(f[:,2]**2+f[:,3]**2)
    order=np.lexsort((ids,distance))
    selected=[]; used=set()
    for k in order:
        day=int(days[ids[k]])
        if day not in used:
            selected.append(ids[k]); used.add(day)
        if len(selected)==10: break
    return np.asarray(selected,dtype=int) if len(selected)>=5 else np.array([],dtype=int)


def contrast_book(y,days,signals,controls,nday):
    book=np.zeros(nday)
    for i,js in zip(signals,controls):
        book[int(days[i])]+=y[i]
        np.add.at(book,days[js],-y[js]/len(js))
    return book


def bootstrap_contrast(weights,signal_sum,signal_count,control_sum,control_weight):
    """Difference of separately normalized averages; either missing mass is undefined."""
    sd=weights@signal_count; cd=weights@control_weight
    s=np.divide(weights@signal_sum,sd,out=np.full(sd.shape,np.nan),where=sd>0)
    c=np.divide(weights@control_sum,cd,out=np.full(cd.shape,np.nan),where=cd>0)
    return s-c


def imbalance(features,signals,controls):
    a=features[signals]
    means=np.array([features[js].mean(axis=0) for js in controls])
    seconds=np.array([(features[js]**2).mean(axis=0) for js in controls])
    delta=a.mean(axis=0)-means.mean(axis=0)
    var=.5*(a.var(axis=0)+np.maximum(0,seconds.mean(axis=0)-means.mean(axis=0)**2))
    out=np.divide(abs(delta),np.sqrt(var),out=np.where(abs(delta)<1e-12,0.,np.inf),where=var>1e-20)
    return float(out.max())
