"""Candle pattern event table on DEV klines; signal stamped at close, forward bars begin at i+1."""
import argparse
import importlib.util
from pathlib import Path

DEV_START_MS=1640995200000   # 2022-01-01 UTC
DEV_END_MS=1719792000000     # 2024-07-01 UTC, exclusive
DEFAULT_NPZ="F:/MTS/data/bigtrade/cache/perp/klines_1h.npz"
BAR_MS={'1h':3_600_000,'4h':14_400_000}
_spec=importlib.util.spec_from_file_location('candle_patterns',Path(__file__).with_name('patterns.py'))
_patterns=importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_patterns)
DETECTORS=_patterns.DETECTORS

def build_event_table(events, bars, horizon=20, step=None):
    rows=[]
    for event in events:
        i=int(event['index']); side=int(event['side'])
        if i<0 or i>=len(bars) or side not in (-1,1):
            rows.append({'pattern':event.get('pattern',''),'event_time':None,'mfe_R':None,'mae_R':None,'bars_forward':0,'status':'NOT_IN_DATA'});continue
        b=bars[i]; price=float(b['c']); risk=float(b['h'])-float(b['l']); end=min(len(bars),i+1+max(0,int(horizon)))
        if risk<=0 or end<=i+1:
            rows.append({'pattern':event.get('pattern',''),'event_time':b.get('close_t',b.get('t')),'mfe_R':None,'mae_R':None,'bars_forward':0,'status':'NOT_IN_DATA'});continue
        future=bars[i+1:end]
        if step:
            # gap or truncated window = NOT_IN_DATA; never bridge missing bars
            ts=[b['t']]+[x['t'] for x in future]
            if len(future)<int(horizon) or any(q-p!=step for p,q in zip(ts,ts[1:])):
                rows.append({'pattern':event.get('pattern',''),'event_time':b.get('close_t',b.get('t')),'mfe_R':None,'mae_R':None,'bars_forward':0,'status':'NOT_IN_DATA'});continue
        favorable = ((float(x['h']) - price) if side == 1 else (price - float(x['l'])) for x in future)
        adverse = ((price - float(x['l'])) if side == 1 else (float(x['h']) - price) for x in future)
        mfe=max(0.0,max(favorable)/risk)
        mae=max(0.0,max(adverse)/risk)
        rows.append({'event_time':b.get('close_t',b.get('t')),'pattern':event.get('pattern',''),'side':side,'signal_index':i,'event_price':price,'risk_price':risk,'mfe_R':mfe,'mae_R':mae,'bars_forward':len(future),'status':'OK'})
    return rows


def load_dev_npz(path, timeframe, dev_start_ms=DEV_START_MS, dev_end_ms=DEV_END_MS):
    """DEV bars (open in [start,end)); mask is applied to the arrays before any bar dict exists.
    4h = four consecutive 1h bars from a 4h UTC boundary; incomplete buckets are skipped."""
    import numpy as np
    if timeframe not in BAR_MS:
        raise ValueError("timeframe must be '1h' or '4h'")
    with np.load(path) as z:
        keep=(z['t']>=dev_start_ms)&(z['t']<dev_end_ms)
        cols={k:z[k][keep] for k in ('t','o','h','l','c')}
    hourly={int(t):(float(o),float(h),float(l),float(c))
            for t,o,h,l,c in zip(cols['t'],cols['o'],cols['h'],cols['l'],cols['c'])}
    h1=BAR_MS['1h']
    if timeframe=='1h':
        return [{'t':t,'close_t':t+h1,'o':v[0],'h':v[1],'l':v[2],'c':v[3]} for t,v in sorted(hourly.items())]
    out=[]
    for t in sorted({x-x%BAR_MS['4h'] for x in hourly}):
        parts=[hourly.get(t+k*h1) for k in range(4)]
        if any(p is None for p in parts):
            continue
        out.append({'t':t,'close_t':t+BAR_MS['4h'],'o':parts[0][0],'h':max(p[1] for p in parts),
                    'l':min(p[2] for p in parts),'c':parts[3][3]})
    return out


def detect(bars):
    """Events on every closed bar; inside bar/doji are oriented by bar colour (OURS); a flat close gives side 0 = NOT_IN_DATA."""
    events=[]
    for name,fn in DETECTORS.items():
        for i in range(len(bars)):
            s=fn(bars,i)
            if not s:
                continue
            if name in ('inside_bar','doji'):
                s=1 if bars[i]['c']>bars[i]['o'] else -1 if bars[i]['c']<bars[i]['o'] else 0
            events.append({'pattern':name,'index':i,'side':s})
    return events


def run(input_path, timeframe, horizon=20):
    bars=load_dev_npz(input_path,timeframe)
    rows=build_event_table(detect(bars),bars,horizon,step=BAR_MS[timeframe])
    for r in rows:
        r['timeframe']=timeframe
    return rows


def summarize(rows):
    out={}
    for r in rows:
        d=out.setdefault(r.get('pattern',''),{'rows':0,'ok':0,'not_in_data':0,'mfe':0.0,'mae':0.0})
        d['rows']+=1
        if r['status']=='OK':
            d['ok']+=1; d['mfe']+=r['mfe_R']; d['mae']+=r['mae_R']
        else:
            d['not_in_data']+=1
    for d in out.values():
        d['mean_mfe_R']=round(d.pop('mfe')/d['ok'],4) if d['ok'] else None
        d['mean_mae_R']=round(d.pop('mae')/d['ok'],4) if d['ok'] else None
    return out


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--input',default=DEFAULT_NPZ)
    ap.add_argument('--timeframe',choices=tuple(BAR_MS),required=True)
    ap.add_argument('--horizon',type=int,default=20)
    a=ap.parse_args()
    for pat,d in sorted(summarize(run(a.input,a.timeframe,a.horizon)).items()):
        print(a.timeframe,pat,d)


if __name__=='__main__':
    main()
