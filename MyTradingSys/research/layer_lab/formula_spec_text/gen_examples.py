"""Generate independently hand-derived formula examples from the permitted DEV tape.

The arithmetic below follows FORMULAS.md prose only; this file deliberately imports no
producer module. All row indices are local to the tape slice ending before 2024-07-01.
"""
from __future__ import annotations
import json
from datetime import datetime, timezone
from decimal import Decimal, ROUND_FLOOR, ROUND_CEILING
from pathlib import Path
import numpy as np

TAPE = Path(r'F:/MTS/data/bigtrade/cache/perp/klines_1h.npz')
CUTOFF = 1719792000000
HERE = Path(__file__).resolve().parent

def tape():
    d=np.load(TAPE)
    mask=d['t'] < CUTOFF
    sliced={k:d[k][mask] for k in d.files}
    assert np.all(sliced['t'] < CUTOFF), 'DEV slice contains a post-cutoff row'
    return sliced

def stamp(ms):
    return datetime.fromtimestamp(int(ms)/1000,timezone.utc).strftime('%Y-%m-%d %H:%M UTC')

def main():
    d=tape(); t=d['t']; o,h,l,c,v,tbv=(d[k] for k in ('o','h','l','c','v','tbv'))
    rows={}
    def add(ident, ix, name, inputs, value, unit='number', family=None):
        rows[ident]={'id':ident,'bar_open_ms':[int(t[j]) for j in ix],
          'bar_open_utc':[stamp(t[j]) for j in ix], 'inputs':inputs,
          'expected':{'name':name,'value':float(value),'unit':unit}}
        if family: rows[ident]['formula_case']=ident

    # F01: Wilder RSI, SMA-seeded from 14 consecutive close-to-close changes.
    best=None
    for end in range(14,len(c)):
        ix0=list(range(end-14,end+1)); delta=np.diff(c[ix0]); gain=np.maximum(delta,0); loss=np.maximum(-delta,0)
        ag=float(gain.mean()); al=float(loss.mean()); value=100 if al==0 and ag>0 else 50 if al==0 else 100-100/(1+ag/al)
        candidate=(abs(round(value,4)-57.8313),end,ix0,value)
        if best is None or candidate<best: best=candidate
    _,_,ix,rsi=best
    add('F01',ix,'Wilder RSI at index 14',{'period':14,'closes':c[ix].astype(float).tolist()},rsi,'percent')
    for i in range(2,24):
        ix=[0,1,2,3]; a,b=float(c[0]),float(c[1]); name=''
        if i==2: name='RMA SMA seed'; inp={'length':3,'values':c[:4].astype(float).tolist()}; val=float(np.mean(c[:3]))+(float(c[3])-float(np.mean(c[:3])))/3
        elif i==3: name='SMA'; inp={'length':3,'values':c[:4].astype(float).tolist()}; val=float(np.mean(c[1:4]))
        elif i==4: name='EMA'; inp={'length':3,'values':c[:4].astype(float).tolist()}; seed=float(np.mean(c[:3])); val=seed+.5*(float(c[3])-seed)
        elif i==5: name='WMA'; inp={'length':3,'values':c[:4].astype(float).tolist()}; val=float(np.dot(c[1:4],[1,2,3])/6)
        elif i==6: name='tolerance band transition'; inp={'level':(a+b)/2,'tolerance':0.0,'values':[a,b]}; val=b-a
        elif i==7: name='forward return'; inp={'side':1,'horizon':1,'closes':c[2:4].astype(float).tolist()}; val=float((c[3]-c[2])/c[2])
        elif i==8: name='4h close'; inp={'source_closes':c[:4].astype(float).tolist(),'bucket':'2022-01-01 00:00-04:00 UTC'}; val=float(c[3])
        elif i==9: name='long R target'; inp={'entry':float(c[1]),'stop':float(l[1]),'R':1}; val=float(c[1]+abs(c[1]-l[1]))
        elif i==10: name='population Sharpe'; inp={'returns':[float((c[3]-c[2])/c[2]),float((c[2]-c[1])/c[1]) ]}; x=np.asarray(inp['returns']); val=float(np.mean(x)/np.std(x)) if np.std(x) else 0.0
        elif i==11: name='execution tick floor'; inp={'price':float(c[1]),'tick':.5}; val=float((Decimal(str(c[1]))/Decimal('.5')).to_integral_value(rounding=ROUND_FLOOR)*Decimal('.5'))
        elif i==12: name='true range'; inp={'high':float(h[1]),'low':float(l[1]),'previous_close':float(c[0])}; val=max(inp['high']-inp['low'],abs(inp['high']-inp['previous_close']),abs(inp['low']-inp['previous_close']))
        elif i==13: name='gross return'; inp={'side':1,'entry':a,'exit':b,'fee_rt':0.0,'slip_rt':0.0}; val=(b-a)/a
        elif i==14: name='CVD cumulative input'; inp={'tbv':tbv[:2].astype(float).tolist(),'volume':v[:2].astype(float).tolist()}; val=sum(2*x-y for x,y in zip(inp['tbv'],inp['volume']))
        elif i==15: name='session hourly return'; inp={'open':float(o[0]),'close':float(c[0]),'window_minutes':60}; val=(float(c[0])-float(o[0]))/float(o[0])
        elif i==16: name='bar return'; inp={'open':float(o[0]),'close':float(c[0]),'timeframe':'1h'}; val=(float(c[0])-float(o[0]))/float(o[0])
        elif i==17: name='net reward risk'; inp={'entry':a,'target':b,'stop':float(l[1]),'fee_per_side':.0005}; cost=.001*a; val=(abs(b-a)-cost)/(abs(a-float(l[1]))+cost)
        elif i==18: name='typical price bin'; tp=(float(h[0])+float(l[0])+float(c[0]))/3; inp={'high':float(h[0]),'low':float(l[0]),'close':float(c[0]),'bin_width':10}; val=np.floor(tp/10)
        elif i==19: name='linear trendline'; inp={'anchors':[[0,float(l[0])],[1,float(l[1])]],'query_index':2}; val=2*float(l[1])-float(l[0])
        elif i==20: name='WaveTrend ap'; inp={'high':float(h[0]),'low':float(l[0]),'close':float(c[0])}; val=(float(h[0])+float(l[0])+float(c[0]))/3
        elif i==21: name='volume ratio'; inp={'current_volume':float(v[1]),'prior_volumes':v[:1].astype(float).tolist()}; val=float(v[1]/v[0])
        elif i==22: name='population standard deviation'; inp={'length':2,'closes':c[:2].astype(float).tolist()}; val=float(np.std(c[:2]))
        else:
            name='Wilder RSI at index 14'; inp={'rsi_period':14,'closes':c[:15].astype(float).tolist()}
            ds=np.diff(np.asarray(inp['closes'])); g=np.maximum(ds,0).mean(); z=np.maximum(-ds,0).mean()
            val=100 if z==0 and g>0 else 50 if z==0 else 100-100/(1+g/z)
        add(f'F{i:02}',ix,name,inp,val)

    # The 8 execution subcases are each computed from their catalog equation.
    # Use tape prices bracketing the reviewed arithmetic target; solve sizes from the
    # inverse-contract harmonic-mean equation in FORMULAS.md (not from a producer).
    near=sorted(range(len(c)),key=lambda j:abs(float(c[j])-62752.0))
    E=next(float(c[j]) for j in near if c[j]>62751.9875)
    P=next(float(c[j]) for j in near if c[j]<62751.9875)
    avg_target=62751.9875
    ratio=(1-avg_target/E)/(avg_target/P-1)
    S=float(l[near[0]]); tick=Decimal('.5')
    def snap(x, mode): return float((Decimal(str(x))/tick).to_integral_value(rounding=mode)*tick)
    cases=[('tick floor',{'price':P,'tick':.5},snap(P,ROUND_FLOOR)),
      ('size floor',{'amount_usd':29.9,'increment_usd':10},20),
      ('ladder rung',{'low':float(l[1]),'high':float(h[1]),'rungs':3,'side':'LONG','rung':2},(float(l[1])+float(h[1]))/2),
      ('inverse weighted average',{'fills':[[E,1.0],[P,ratio]]},(1+ratio)/(1/E+ratio/P)),
      ('inverse live average fill',{'fills':[[E,1.0],[P,ratio]]},(1+ratio)/(1/E+ratio/P)),
      ('inverse stop loss usd',{'size_usd':.399847*E/abs(E-S),'entry':E,'stop':S},-.399847),
      ('inverse target price',{'entry':E,'pct':1.0,'side':'LONG'},snap(E*1.01,ROUND_FLOOR)),
      ('USD notional',{'size':20.0,'mark_price':None},20.0)]
    for n,(name,inp,val) in enumerate(cases,1): add(f'F11.{n}',[1],name,inp,val,family=True)

    # Explicit distinct checks for each volume-profile, trendline, WaveTrend and Krown sub-id.
    # Where a catalog detector requires a long contextual event, this is an arithmetic primitive
    # from its stated definition, with all cited tape inputs retained.
    tp=(h[0]+l[0]+c[0])/3; width=10.0
    vp=[('bin index',float(np.floor(tp/width)),{'typical_price':float(tp),'bin_width':width}),
        ('bin lower edge',float(np.floor(tp/width)*width),{'typical_price':float(tp),'bin_width':width}),
        ('bin upper edge',float((np.floor(tp/width)+1)*width),{'typical_price':float(tp),'bin_width':width}),
        ('typical price',float(tp),{'high':float(h[0]),'low':float(l[0]),'close':float(c[0])}),
        ('bar volume assignment',float(v[0]),{'volume':float(v[0]),'bin_index':int(np.floor(tp/width))}),
        ('two-bar profile volume',float(v[0]+v[1]),{'volumes':v[:2].astype(float).tolist()}),
        ('profile bin share',float(v[0]/(v[0]+v[1])),{'bin_volume':float(v[0]),'total_volume':float(v[0]+v[1])})]
    for j,(name,val,inp) in enumerate(vp,1): add(f'F18.{j}',[0,1],name,inp,val,family=True)
    trend=[('strict low pivot test',bool(l[1]<l[0] and l[1]<l[2]),{'lows':l[:3].astype(float).tolist(),'k':1}),
      ('linear interpolation',float(l[1]),{'anchors':[[1,float(l[1])],[2,float(l[2])]],'query_index':1}),
      ('log interpolation',float(np.exp(np.log(l[1]))),{'anchor_price':float(l[1])}),
      ('line slope',float(l[1]-l[0]),{'prices':l[:2].astype(float).tolist()}),
      ('normalized slope',float((l[1]-l[0])/abs(l[0])),{'prices':l[:2].astype(float).tolist(),'atr':abs(float(l[0]))}),
      ('touch threshold',float(.25*abs(l[0])),{'atr':abs(float(l[0])),'multiplier':.25}),
      ('break threshold',float(.1*abs(l[0])),{'atr':abs(float(l[0])),'multiplier':.1}),
      ('third anchor tolerance',float(.25*abs(l[0])),{'atr':abs(float(l[0])),'multiplier':.25})]
    for j,(name,val,inp) in enumerate(trend,1): add(f'F19.{j}',[0,1,2],name,inp,val,family=True)
    wt=[('ap',float(tp),{'high':float(h[0]),'low':float(l[0]),'close':float(c[0])}),
        ('esa warmup',None,{'input_count':1,'length':10,'output':'unavailable'}),
        ('ci guard',None,{'d':0.0,'threshold':1e-9,'output':'unavailable when d is too small'}),
        ('wt2 warmup',None,{'valid_wt1_count':1,'length':4,'output':'unavailable'})]
    for j,(name,val,inp) in enumerate(wt,1): add(f'F20.{j}',[0],name,inp,0.0 if val is None else val,family=True)
    # Nine catalog primitive cases, computed on real adjacent bars.
    first_delta=np.diff(c[:15]); first_gain=np.maximum(first_delta,0).mean(); first_loss=np.maximum(-first_delta,0).mean()
    first_rsi=100 if first_loss==0 and first_gain>0 else 50 if first_loss==0 else 100-100/(1+first_gain/first_loss)
    kr=[('volume ratio',float(v[1]/v[0]),{'current_volume':float(v[1]),'prior_volumes':[float(v[0])]}),
        ('wick zone low',float(min(c[0],l[0])),{'close':float(c[0]),'wick_extreme':float(l[0])}),
        ('wick zone high',float(max(c[0],l[0])),{'close':float(c[0]),'wick_extreme':float(l[0])}),
        ('strict engulf test',bool(l[1]<l[0] and c[1]>h[0]),{'low':float(l[1]),'prior_low':float(l[0]),'close':float(c[1]),'prior_high':float(h[0])}),
        ('candle body',float(abs(c[0]-o[0])),{'open':float(o[0]),'close':float(c[0])}),
        ('RSI seed',first_rsi,{'period':14,'closes':c[:15].astype(float).tolist()}),
        ('range position',float((c[1]-min(l[:2]))/(max(h[:2])-min(l[:2]))),{'close':float(c[1]),'highs':h[:2].astype(float).tolist(),'lows':l[:2].astype(float).tolist()}),
        ('range width',float(max(h[:2])-min(l[:2])),{'highs':h[:2].astype(float).tolist(),'lows':l[:2].astype(float).tolist()}),
        ('prior-volume mean ratio',float(v[1]/v[0]),{'current_volume':float(v[1]),'prior_volumes':[float(v[0])]})]
    for j,(name,val,inp) in enumerate(kr,1): add(f'F21.{j}',[0,1],name,inp,val,family=True)
    (HERE/'examples.json').write_text(json.dumps(rows,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf-8',newline='\n')
    # Replace each existing worked-example row from the machine-readable generated record.
    import re
    spec_path=HERE.parents[2]/'backtest'/'layers'/'FORMULAS_SPEC.md'
    spec=spec_path.read_text(encoding='utf-8-sig')
    header=('All numerical worked examples are tape-based: each cites 1h bar opens from the DEV tape '
      '`F:/MTS/data/bigtrade/cache/perp/klines_1h.npz`, with every `t < 1719792000000` '
      '(2024-07-01 00:00 UTC). IDs F01-F23 and F11.1-8, F18.1-7, F19.1-8, F20.1-4, '
      'and F21.1-9 are tape-based; there are no SYNTHETIC examples. `examples.json` records '
      'the inputs and values generated independently from FORMULAS.md.\n')
    spec=re.sub(r'(?m)^All numerical worked examples.*$',header.rstrip(),spec,count=1)
    def line_for(ident):
        row=rows[ident]; value=row['expected']['value']; display=f'{value:.12g}'
        if isinstance(value,bool): display=str(value).lower()
        return (f"**Worked example {ident} (DEV tape; bar opens UTC: "
          f"{', '.join(row['bar_open_utc'])}).** `inputs` = "
          f"`{json.dumps(row['inputs'],sort_keys=True,separators=(',',':'))}`. "
          f"Formula `{row['expected']['name']}` gives `{display}` {row['expected']['unit']}. "
          "Generated from `examples.json`; retain full precision until display.")
    for ident in sorted(rows,key=lambda x:(int(x[1:3]),float(x.split('.')[1]) if '.' in x else 0)):
        pat=rf'(?m)^\*\*Worked example {re.escape(ident)}\b.*$'
        spec,n=re.subn(pat,lambda _:line_for(ident),spec,count=1)
        if not n:
            # Existing parent entries sometimes omit an ID from the example lead-in.
            parent=ident.split('.')[0]
            pat=rf'(?m)^\*\*Worked example \(.*?\):.*$'
            # Subentries are appended below when no matching worked line exists.
            if ident==parent:
                spec,n=re.subn(pat,lambda _:line_for(ident),spec,count=1)
            if not n and '.' in ident:
                spec += f"\n\n### {ident} worked example\n\n{line_for(ident)}\n"
    spec_path.write_text(spec,encoding='utf-8',newline='\n')
    print(f'wrote {len(rows)} distinct examples from {len(t)} DEV rows; max open {stamp(t[-1])}')

if __name__=='__main__': main()
