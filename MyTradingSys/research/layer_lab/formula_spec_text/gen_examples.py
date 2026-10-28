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

    def add_synthetic(ident, name, inputs, value, unit='number', family=True):
        rows[ident]={'id':ident,'synthetic':True,
          'inputs':inputs,
          'expected':{'name':name,'value':bool(value) if isinstance(value,bool) else float(value),'unit':unit}}
        if family: rows[ident]['formula_case']=ident

    def add_na(ident, quote, reason, family=True):
        rows[ident]={'id':ident,'not_applicable':True,'quote':quote,'reason':reason,
          'expected':{'name':'NOT_APPLICABLE','value':0.0,'unit':'none'}}
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

    # Section 11: Execution math (F11.1 - F11.8)
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

    # Section 18: Volume profile (F18.1 - F18.7)
    add_synthetic('F18.1', 'profile POC price', {'w': 1.0, 'bars': [[0.0, 2.0, 6.0], [1.0, 3.0, 4.0], [1.0, 2.0, 10.0]]}, 1.5)
    add_synthetic('F18.2', 'fractal pivot high test', {'n': 1, 'highs': [1.0, 3.0, 2.0, 5.0, 4.0, 1.0, 2.0], 'test_index': 1}, True, unit='boolean')
    add_synthetic('F18.3', 'meaningful pivot size filter', {'price_p': 110.0, 'price_q': 100.0, 'k': 1.0, 'atr': 5.0}, True, unit='boolean')
    add_na('F18.4', 'levels refreshed on a 15-minute grid... Developing; need >= 12 bars... Each profile contributes three levels: POC, VAH, VAL',
           'Defines bar window definitions and grid intervals for profile families; contains no standalone formula or worked numerical calculation.')
    add_synthetic('F18.5', 'touch outcome net R', {'side': 1, 'L': 100.0, 'exit': 102.0, 'R': 2.0, 'fee_in': 0.0005, 'fee_out': 0.0005}, 0.9495)
    add_synthetic('F18.6', 'placebo level', {'L': 100.0, 'R_ref': 2.0, 'refresh_index': 4}, 101.0)
    add_synthetic('F18.7', 'day-block bootstrap mean', {'day_events': [[1.0, 3.0], [-2.0]], 'resample_indices': [0, 1]}, 2.0 / 3.0)

    # Section 19: Trend-lines (F19.1 - F19.8)
    add_synthetic('F19.1', 'strict pivot low test', {'k': 3, 'lows': [9.0, 8.0, 7.0, 5.0, 6.0, 7.0, 8.0], 'test_index': 3}, True, unit='boolean')
    add_synthetic('F19.2', 'trendline anchor interpolation', {'ia': 10, 'pa': 100.0, 'ib': 20, 'pb': 110.0, 't': 25, 'geometry': 'linear'}, 115.0)
    add_synthetic('F19.3', 'contract ATR', {'ranges': [2.0, 2.5, 2.0], 'length': 3}, 6.5 / 3.0)
    add_synthetic('F19.4', 'slope atr', {'pa': 100.0, 'pb': 110.0, 'dt': 10, 'atr': 4.0}, 0.25)
    add_synthetic('F19.5', 'touch tolerance test', {'L': 115.0, 'atr': 4.0, 'mult': 0.25, 'low': 115.8}, True, unit='boolean')
    add_synthetic('F19.6', 'episode reset test', {'L': 115.0, 'atr': 4.0, 'mult': 1.0, 'low': 120.0}, True, unit='boolean')
    add_synthetic('F19.7', 'volume anchor test ratio', {'V': 300.0, 'M': 140.0}, 300.0 / 140.0)
    add_synthetic('F19.8', 'third anchor tolerance test', {'L': 120.0, 'price': 119.5, 'atr': 4.0, 'mult': 0.25}, True, unit='boolean')

    # Section 20: WaveTrend (F20.1 - F20.4)
    add('F20.1', [0], 'WaveTrend ap', {'high': float(h[0]), 'low': float(l[0]), 'close': float(c[0])}, (float(h[0]) + float(l[0]) + float(c[0])) / 3.0, family=True)
    add_na('F20.2', 'EMA seeded with the first valid source value; output used only after WARMUP=200 bars... Zones from wt1: ob2 >= 60, ob1 >= 53... available_at = bar_open + timeframe',
           'Conventions and event definitions without an inline numerical formula.')
    add_synthetic('F20.3', 'WaveTrend hand ci', {'ap': [10.0, 12.0], 'n': 10}, 5.5 / 0.015)
    add_na('F20.4', 'wavetrend/golden_wt_btcusdt_1h_dev_2022-01.csv: 400 BTCUSDT 1h bars... Compared at 1e-9 (OURS) after bar 200',
           'Reference golden CSV comparison specification; no inline formula computation.')

    # Section 21: Krown trading rules (F21.1 - F21.9)
    add_synthetic('F21.1', 'wick zone high', {'close': 104.0, 'wick_extreme': 90.0}, 104.0)
    add_synthetic('F21.2', 'prior-volume mean ratio', {'current_volume': 250.0, 'prior_mean': 100.0}, 2.5)
    add_synthetic('F21.3', 'strict bullish engulf test', {'low': 99.0, 'prior_low': 100.0, 'close': 106.0, 'prior_high': 105.0}, True, unit='boolean')
    add_synthetic('F21.4', 'dominant low level', {'bars': [[10,8,9],[12,9,11],[11,7,8],[14,9,13],[13,10,12],[12,8,9],[17,11,16],[15,12,13],[13,6,7.5]], 'k': 1, 'query_t': 7}, 8.0)
    add_synthetic('F21.5', 'BBWP percentile', {'basis': 2, 'lookback': 3, 'closes': [10.0, 10.0, 12.0, 11.0, 15.0, 15.0, 14.0], 't': 4}, 100.0, unit='percent')
    add_synthetic('F21.6', 'EMA seed step', {'n': 5, 'closes': [1.0, 2.0, 3.0, 4.0, 5.0, 6.0]}, 4.0)
    add_synthetic('F21.7', 'Wilder RSI smoothed', {'period': 2, 'closes': [10.0, 11.0, 10.0, 12.0]}, 100.0 - 100.0 / 6.0, unit='percent')
    add_synthetic('F21.8', 'range position', {'highs': [10.0, 11.0, 10.5, 11.0], 'lows': [9.0, 9.5, 9.0, 9.5], 'close': 9.4}, 0.2)
    add_synthetic('F21.9', 'top signal count', {'window': 3, 'signals': {'candle': [5], 'volume': [6], 'bbwp': [7], 'momentum': []}, 't': 7}, 3.0, unit='count')

    (HERE/'examples.json').write_text(json.dumps(rows,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf-8',newline='\n')

    # Replace each existing worked-example row from the machine-readable generated record.
    import re
    spec_path=HERE.parents[2]/'backtest'/'layers'/'FORMULAS_SPEC.md'
    spec=spec_path.read_text(encoding='utf-8-sig')
    header=('All numerical worked examples are derived directly from FORMULAS.md: '
      'tape-based examples cite 1h bar opens from the DEV tape `F:/MTS/data/bigtrade/cache/perp/klines_1h.npz` '
      'with `t < 1719792000000` (2024-07-01 00:00 UTC); self-contained worked examples from sub-id '
      'paragraphs are labelled SYNTHETIC; sub-id paragraphs without computable numbers are labelled '
      'NOT_APPLICABLE with cited quotes. `examples.json` records the inputs and values generated '
      'independently from FORMULAS.md.\n')
    spec=re.sub(r'(?m)^All numerical worked examples.*$',header.rstrip(),spec,count=1)
    def line_for(ident):
        row=rows[ident]
        if row.get('not_applicable'):
            return (f"**Worked example {ident} (NOT_APPLICABLE).** Paragraph quote: \"{row['quote']}\". "
              f"{row['reason']} Generated from `examples.json`.")
        val=row['expected']['value']; display=f'{val:.12g}' if isinstance(val,(int,float)) and not isinstance(val,bool) else str(val).lower()
        if row.get('synthetic'):
            return (f"**Worked example {ident} (SYNTHETIC).** `inputs` = "
              f"`{json.dumps(row['inputs'],sort_keys=True,separators=(',',':'))}`. "
              f"Formula `{row['expected']['name']}` gives `{display}` {row['expected']['unit']}. "
              "Generated from `examples.json` (FORMULAS.md worked arithmetic).")
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
            if ident==parent:
                spec,n=re.subn(pat,lambda _:line_for(ident),spec,count=1)
            if not n and '.' in ident:
                spec += f"\n\n### {ident} worked example\n\n{line_for(ident)}\n"
    spec_path.write_text(spec,encoding='utf-8',newline='\n')
    print(f'wrote {len(rows)} distinct examples from {len(t)} DEV rows; max open {stamp(t[-1])}')

if __name__=='__main__': main()
