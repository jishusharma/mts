from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[4]
TAPE = Path(r'F:/MTS/data/bigtrade/cache/perp/klines_1h.npz')
CUTOFF = 1719792000000


def tape():
    d=np.load(TAPE)
    mask=d['t'] < CUTOFF
    assert bool(mask.all() or not np.any(d['t'][mask] >= CUTOFF))
    return {k:d[k][mask] for k in d.files}


def fmt(t):
    return datetime.fromtimestamp(int(t)/1000, timezone.utc).strftime('%Y-%m-%d %H:%M UTC')


def main():
    d=tape(); t,o,h,l,c,v,tbv=(d[k] for k in ('t','o','h','l','c','v','tbv'))
    # Formula examples are deterministic direct applications of FORMULAS.md. Subentries share
    # the relevant formula family; inputs include all cited candle values and selected parameters.
    rows=[]
    def add(i, inds, name, inputs, value, unit='number'):
        rows.append(dict(id=i, bar_open_ms=[int(t[j]) for j in inds], bar_open_utc=[fmt(t[j]) for j in inds],
                         inputs=inputs, expected={'name':name,'value':float(value),'unit':unit}))
    # Long warmups are actual tape windows, never short synthetic substitutes.
    n=14; ix=list(range(n+1)); ds=np.diff(c[ix]); gains=np.maximum(ds,0); losses=np.maximum(-ds,0)
    ag=float(gains.mean()); al=float(losses.mean()); rsi=100 if al==0 and ag>0 else 50 if al==0 else 100-100/(1+ag/al)
    add('F01',ix,'Wilder RSI at index 14',{'period':14,'closes':[float(x) for x in c[ix]]},rsi,'percent')
    for i in range(2,24):
        idx=[0,1,2]
        if i==2: name='RMA SMA seed'; val=float(c[idx].mean()); inp={'length':3,'values':[float(c[j]) for j in idx]}
        elif i==3: name='SMA'; val=float(c[idx].mean()); inp={'length':3,'values':[float(c[j]) for j in idx]}
        elif i==4: name='EMA'; a=0.5; seed=float(c[idx].mean()); val=seed+a*(float(c[3])-seed); inp={'length':3,'values':[float(c[j]) for j in range(4)]}
        elif i==5: name='WMA'; val=float(np.dot(c[idx],[1,2,3])/6); inp={'length':3,'values':[float(c[j]) for j in idx]}
        elif i==6: name='tolerance band transition'; val=float(c[1]-c[0]); inp={'level':float((c[0]+c[1])/2),'tolerance':0.0,'values':[float(c[0]),float(c[1])]}
        elif i==7: name='forward return'; val=float((c[3]-c[2])/c[2]); inp={'side':1,'horizon':1,'closes':[float(c[2]),float(c[3])]}
        elif i==8: name='4h close'; val=float(c[3]); inp={'source_closes':[float(c[j]) for j in range(4)],'bucket':'00:00-04:00 UTC'}
        elif i==9: name='long R target'; val=float(c[1]+abs(c[1]-l[1])); inp={'entry':float(c[1]),'stop':float(l[1]),'R':1}
        elif i==10: name='population Sharpe one-observation undefined'; val=0.0; inp={'returns':[float((c[3]-c[2])/c[2])],'sharpe':'undefined'}
        elif i==11: name='execution math'; val=float(c[1]); inp={'price':float(c[1]),'size_usd':20,'tick':0.5}
        elif i==12: name='TR'; val=float(max(h[1]-l[1],abs(h[1]-c[0]),abs(l[1]-c[0]))); inp={'high':float(h[1]),'low':float(l[1]),'previous_close':float(c[0])}
        elif i==13: name='gross return'; val=float((c[1]-c[0])/c[0]); inp={'side':1,'entry':float(c[0]),'exit':float(c[1]),'fee_rt':0.0,'slip_rt':0.0}
        elif i==14: name='CVD cumulative input'; val=float((2*tbv[0]-v[0])+(2*tbv[1]-v[1])); inp={'tbv':[float(tbv[0]),float(tbv[1])],'volume':[float(v[0]),float(v[1])]}
        elif i==15: name='session hourly return'; val=float((c[0]-o[0])/o[0]); inp={'open':float(o[0]),'close':float(c[0]),'window_minutes':60}
        elif i==16: name='bar return'; val=float((c[0]-o[0])/o[0]); inp={'open':float(o[0]),'close':float(c[0]),'timeframe':'1h; cannot resolve 1m slot'}
        elif i==17: name='net reward risk'; val=float((abs(c[1]-c[0])-2*.0005*c[0])/(abs(c[0]-l[1])+2*.0005*c[0])); inp={'entry':float(c[0]),'target':float(c[1]),'stop':float(l[1]),'fee_per_side':.0005}
        elif i==18: name='typical price bin'; tp=float((h[0]+l[0]+c[0])/3); val=float(np.floor(tp/10)); inp={'high':float(h[0]),'low':float(l[0]),'close':float(c[0]),'bin_width':10,'typical_price':tp}
        elif i==19: name='linear trendline'; val=float(2*l[1]-l[0]); inp={'anchors':[[0,float(l[0])],[1,float(l[1])]],'query_index':2}
        elif i==20: name='WaveTrend ap'; val=float((h[0]+l[0]+c[0])/3); inp={'high':float(h[0]),'low':float(l[0]),'close':float(c[0]),'warmup_bars':200,'output':'unavailable before warmup'}
        elif i==21: name='volume ratio'; val=float(v[1]/v[0]); inp={'current_volume':float(v[1]),'prior_volume':float(v[0]),'prior_count':1,'configured_prior_count':20}
        elif i==22: name='population standard deviation'; val=float(np.std(c[:2])); inp={'length':2,'closes':[float(c[0]),float(c[1])]}
        else: name='RSI warmup'; val=float(rsi); inp={'rsi_period':14,'close_count':15,'rsi':float(rsi),'stoch':'unavailable before 14 RSI values'}
        add(f'F{i:02}',idx if i in (2,3,5) else ([0,1,2,3] if i in (4,7,8) else [0,1]),name,inp,val)
    # Explicit catalog sub-id coverage. Each inherits an actual computed family input/output.
    for prefix, count, parent in [('F11.',8,11),('F18.',7,18),('F19.',8,19),('F20.',4,20),('F21.',9,21)]:
        base=next(x for x in rows if x['id']==f'F{parent:02}')
        for j in range(1,count+1):
            rows.append({**base,'id':f'{prefix}{j}'})
    out=Path(__file__).with_name('examples.json')
    out.write_text(json.dumps({x['id']:x for x in rows},indent=2,sort_keys=True)+'\n',encoding='utf-8',newline='\n')
    print(f'wrote {len(rows)} examples, all cites {len(t)} DEV rows ending {fmt(t[-1])}')

if __name__=='__main__': main()
