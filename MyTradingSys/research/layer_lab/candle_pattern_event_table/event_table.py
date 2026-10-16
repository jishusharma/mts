"""Forward excursion table; signal timestamp is close and forward bars begin at i+1."""
def build_event_table(events, bars, horizon=20):
    rows=[]
    for event in events:
        i=int(event['index']); side=int(event['side'])
        if i<0 or i>=len(bars) or side not in (-1,1):
            rows.append({'event_time':None,'mfe_R':None,'mae_R':None,'bars_forward':0,'status':'NOT_IN_DATA'});continue
        b=bars[i]; price=float(b['c']); risk=float(b['h'])-float(b['l']); end=min(len(bars),i+1+max(0,int(horizon)))
        if risk<=0 or end<=i+1:
            rows.append({'event_time':b.get('t'),'mfe_R':None,'mae_R':None,'bars_forward':0,'status':'NOT_IN_DATA'});continue
        future=bars[i+1:end]
        favorable = ((float(x['h']) - price) if side == 1 else (price - float(x['l'])) for x in future)
        adverse = ((price - float(x['l'])) if side == 1 else (float(x['h']) - price) for x in future)
        mfe=max(0.0,max(favorable)/risk)
        mae=max(0.0,max(adverse)/risk)
        rows.append({'event_time':b.get('t'),'pattern':event.get('pattern',''),'side':side,'signal_index':i,'event_price':price,'risk_price':risk,'mfe_R':mfe,'mae_R':mae,'bars_forward':len(future),'status':'OK'})
    return rows
