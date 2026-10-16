"""LC2 causal first-touch event features and path measurements (DEV only)."""
import csv
import gzip
import math
import random
import statistics
from collections import defaultdict
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
sys.path.insert(0, str(Path(__file__).parent))
from MyTradingSys.backtest.layers.rsi.rsi_core import rsi_core
from levels import levels_by_day, _profile

KEEP = {'prior_day_high', 'prior_day_low', 'prior_day_poc', 'naked_poc',
        '4h_fractal_low', '4h_fractal_high', 'round_1000', 'prior_week_high'}
TF = {'1h': 60, '4h': 240, '6h': 360, '12h': 720, '1d': 1440}
DAY = 86400000


def bollinger_position(closes, period=20, width=2):
    """Population-SD Bollinger position; 0 lower, .5 middle, 1 upper."""
    if len(closes) < period: return None
    x = list(map(float, closes[-period:])); mean = statistics.mean(x)
    sd = statistics.pstdev(x); lo, hi = mean-width*sd, mean+width*sd
    return (x[-1]-lo)/(hi-lo) if hi != lo else .5


def _agg(bars, minutes):
    span = minutes*60000; groups = defaultdict(list)
    for b in bars: groups[int(b['t'])//span].append(b)
    out=[]
    for k, rows in sorted(groups.items()):
        rows.sort(key=lambda x:x['t'])
        out.append({'t':(k+1)*span-60000,'o':float(rows[0]['o']),'h':max(float(x['h']) for x in rows),
                    'l':min(float(x['l']) for x in rows),'c':float(rows[-1]['c']),
                    'v':sum(float(x['v']) for x in rows),'tbv':sum(float(x.get('tbv',0)) for x in rows)})
    return out


def _ema(values, n=20):
    if len(values)<n:return [None]*len(values)
    out=[None]*len(values); cur=sum(values[:n])/n; out[n-1]=cur; alpha=2/(n+1)
    for i in range(n,len(values)): cur=values[i]*alpha+cur*(1-alpha); out[i]=cur
    return out


def _bias_at(bars, touch_t, pd_value, aggregate_cache=None, price=None):
    ref=float(price) if price is not None else float(bars[0]['o'])
    result={'B1_value_area': None if pd_value is None else ('UP' if ref>pd_value['vah'] else 'DOWN' if ref<pd_value['val'] else 'NEUTRAL')}
    for tf, mins in TF.items():
        aggregated = aggregate_cache[mins] if aggregate_cache is not None else _agg([b for b in bars if int(b['t']) < touch_t], mins)
        closed=[b for b in aggregated if b['t']+60000 < touch_t]
        if len(closed)<21:
            result[f'B2_swing_{tf}']=None; result[f'B3_ema20_{tf}']=None; continue
        # Structure is direction of the last two confirmed 5-bar fractal highs/lows.
        hs=[]; ls=[]
        for i in range(2,len(closed)-2):
            if closed[i]['h']>max(x['h'] for x in closed[i-2:i]+closed[i+1:i+3]): hs.append((i,closed[i]['h']))
            if closed[i]['l']<min(x['l'] for x in closed[i-2:i]+closed[i+1:i+3]): ls.append((i,closed[i]['l']))
        result[f'B2_swing_{tf}']=('UP' if len(hs)>1 and len(ls)>1 and hs[-1][1]>hs[-2][1] and ls[-1][1]>ls[-2][1] else 'DOWN' if len(hs)>1 and len(ls)>1 and hs[-1][1]<hs[-2][1] and ls[-1][1]<ls[-2][1] else 'NEUTRAL')
        closes=[b['c'] for b in closed]; ema=_ema(closes)[-1]
        result[f'B3_ema20_{tf}']='UP' if closes[-1]>ema else 'DOWN' if closes[-1]<ema else 'NEUTRAL'
    return result


def _features(bars, i, side=1):
    # Indicators sample the last closed 5m bar strictly before touch-bar open.
    touch_t=int(bars[i]['t'])
    five=[x for x in _agg(bars[:i],5) if x['t']+60000<=touch_t]; closes=[x['c'] for x in five]
    rsi=rsi_core(closes,14) if len(closes)>14 else [None]*len(closes)
    rv=rsi[-1] if rsi else None
    ma=statistics.mean([x for x in rsi[-10:] if x is not None]) if sum(x is not None for x in rsi[-10:])==10 else None
    cvd=0.; series=[]
    for x in five:
        cvd+=2*x['tbv']-x['v']; series.append(cvd)
    slope=(series[-1]-series[-2]) if len(series)>1 else None
    bb=bollinger_position(closes)
    return {'E1_rsi14':rv,'E1_rsi_holds_40_60':None if rv is None else (rv>=40 if side>0 else rv<=60),
            'E2_rsi_ma':None if rv is None or ma is None else rv-ma,'E2_holds_ma':None if rv is None or ma is None else ((rv>=ma) if side>0 else (rv<=ma)),
            'E3_cvd_kline_slope':slope,'E3_cvd_sign':None if slope is None else (1 if slope>0 else -1 if slope<0 else 0),
            'E3_footprint_slope':None,'E4_bb_position':bb,'E4_outer_band':None if bb is None else (bb<=0 or bb>=1)}


def _stop_status(path, side, entry, stop, target, R, close15=False):
    if stop is None or target is None: return 'NOT_STOPPED'
    stopped_at=None
    for j,b in enumerate(path[1:],1):
        adverse = (float(b['c']) if close15 else float(b['l'])) <= stop if side>0 else (float(b['c']) if close15 else float(b['h'])) >= stop
        if adverse: stopped_at=j; break
    if stopped_at is None:return 'NOT_STOPPED'
    # To call it a bad stop, target must be reached later; good stop requires >=1R
    # additional adverse excursion before that target.
    for b in path[stopped_at+1:]:
        target_hit=float(b['h'])>=target if side>0 else float(b['l'])<=target
        if target_hit:
            beyond=max((stop-float(x['l']) if side>0 else float(x['h'])-stop) for x in path[stopped_at:])
            return 'STOP_THEN_1R_MORE' if beyond>=R else 'STOP_THEN_TARGET'
    return 'NOT_STOPPED'


def load_footprint(root, start_ms, end_ms):
    """Read available footprint deltas; missing minutes remain explicitly absent."""
    found={}; root=Path(root)
    for p in sorted(root.glob('2025-0[1-3]-*.csv.gz')):
        with gzip.open(p,'rt',newline='',encoding='utf-8') as f:
            for row in csv.DictReader(f):
                t=int(row['t'])
                if start_ms<=t<end_ms: found[t]=float(row['delta'])
    return found


def make_events(bars, keep=KEEP, horizon=1440, footprint=None):
    """Rows per first-touch level/day. Data passed must be DEV only."""
    levels=levels_by_day(bars); byday=defaultdict(list)
    aggregate_cache={mins:_agg(bars,mins) for mins in TF.values()}
    fp5=defaultdict(float)
    if footprint is not None:
        for t,v in footprint.items(): fp5[int(t)//300000*300000]+=v
    for b in bars: byday[int(b['t'])//DAY].append(b)
    rows=[]
    for d, daybars in sorted(byday.items()):
        daybars.sort(key=lambda x:x['t']); levs=[x for x in levels.get(d,[]) if x['family'] in keep]
        profile=next((x for x in levels.get(d,[]) if x['family']=='prior_day_poc'),None)
        pd={'vah':None,'val':None}
        # prior-day value boundaries are causal and used for B1 only.
        prior=[x for x in bars if int(x['t'])//DAY==d-1]
        if prior:
            pd=_profile(prior)
        for lev in levs:
            px=float(lev['price']); i=next((j for j,b in enumerate(daybars) if float(b['l'])<=px<=float(b['h'])),None)
            if i is None: continue
            b=daybars[i]; side=1 if (float(daybars[i-1]['c']) if i else float(b['o']))>=px else -1; R=max(.004*float(b['o']),.001*px)
            future=daybars[i:min(len(daybars),i+horizon+1)]; mfe=max([side*(float(x['h'] if side>0 else x['l'])-px)/R for x in future[1:]] or [0]); mae=max([-side*(float(x['l'] if side>0 else x['h'])-px)/R for x in future] or [0])
            other=sorted([float(x['price']) for x in levs if (float(x['price'])-px)*side>0],key=lambda x:abs(x-px))
            opp=other[0] if other else None; hit=next((x for x in future[1:] if opp is not None and float(x['l'])<=opp<=float(x['h'])),None)
            feats=_features(daybars,i,side); ref=float(daybars[i-1]['c']) if i else float(b['o']); bias=_bias_at(bars,int(b['t']),pd,aggregate_cache,ref)
            if footprint is not None:
                t5=int(b['t'])//300000*300000
                cur=fp5.get(t5-300000,0.0)
                prev=fp5.get(t5-600000,0.0)
                feats['E3_footprint_slope']=cur-prev
            row={'day':d,'touch_t':int(b['t']),'family':lev['family'],'source':lev['source'],'level':px,'side':side,'entry':px,'R_price':R,
                 'MFE_pct':mfe*R/px*100,'MAE_pct':mae*R/px*100,'MFE_R':mfe,'MAE_R':mae,'first_opposing_level':opp,'first_opposing_hit_t':int(hit['t']) if hit else None,
                 'L2_filled':bool(hit),'stop_K1':px-side*max(.001*px,1e-9),'stop_K2':(opp-side*.001*opp) if opp else None,
                 'stop_K3':(opp-side*R*.5) if opp else None,'stop_K4':(opp-side*.001*opp) if opp else None,'stop_K5':(min(float(x['l']) for x in daybars[:i+1]) if side>0 else max(float(x['h']) for x in daybars[:i+1])),**bias,**feats}
            stops=[row[f'stop_K{k}'] for k in range(1,6)]
            target=opp
            for k,stop in enumerate(stops,1):
                path15=_agg(future,15) if k==4 else future
                row[f'K{k}_status']=_stop_status(path15,side,px,stop,target,R,close15=(k==4))
                used=path15
                if stop is not None:
                    for j,x in enumerate(path15[1:],1):
                        hit=(float(x['c'])<=stop if side>0 else float(x['c'])>=stop) if k==4 else (float(x['l'])<=stop if side>0 else float(x['h'])>=stop)
                        if hit: used=path15[:j+1]; break
                fav=max((side*((float(x['h']) if side>0 else float(x['l']))-px)/px*100 for x in used),default=0.)
                adv=max((-side*((float(x['l']) if side>0 else float(x['h']))-px)/px*100 for x in used),default=0.)
                row[f'K{k}_MFE_pct']=fav; row[f'K{k}_MAE_pct']=adv
                row[f'K{k}_MFE_R']=fav*px/100/R; row[f'K{k}_MAE_R']=adv*px/100/R
            rows.append(row)
    return rows


def write_csv(rows,path):
    path=Path(path); path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]) if rows else ['day']); w.writeheader(); w.writerows(rows)


def write_separation(rows,path):
    """Exploratory one-feature splits with UTC-day block-bootstrap intervals."""
    features=['E1_rsi_holds_40_60','E2_holds_ma','E3_cvd_sign','E3_footprint_slope','E4_outer_band','B1_value_area']
    features += [f'B2_swing_{tf}' for tf in TF] + [f'B3_ema20_{tf}' for tf in TF]
    byday=defaultdict(list)
    for r in rows: byday[r['day']].append(r)
    lines=['# LC2 feature separation (DEV only)','',
      'Outcome label: **good** = first opposing KEEP level touched within the same UTC day; **bad** = not reached. One-at-a-time feature split is feature affirmative/present vs negative/absent; metric is mean forward MFE_R difference (affirmative minus negative). CIs resample whole UTC days (2,000 replicates, seed 20261016). This is descriptive selection on DEV, not a trading rule.', '',
      '## One-at-a-time results','', '| Feature | n yes/no | MFE_R yes | MFE_R no | Difference | 95% day-bootstrap CI |', '|---|---:|---:|---:|---:|---:|']
    result=[]
    for f in features:
        vals=[]
        for r in rows:
            x=r.get(f)
            if x in (None,''): continue
            if f in ('E3_cvd_sign','E3_footprint_slope'): yes=float(x)*int(r['side'])>0
            elif f=='B1_value_area' or f.startswith('B2_swing_') or f.startswith('B3_ema20_'): yes=(x=='UP' and int(r['side'])>0) or (x=='DOWN' and int(r['side'])<0)
            else: yes=x is True or str(x).lower()=='true'
            vals.append((r,yes,float(r['MFE_R'])))
        a=[x[2] for x in vals if x[1]]; b=[x[2] for x in vals if not x[1]]
        diff=(sum(a)/len(a)-sum(b)/len(b)) if a and b else 0.; days=sorted({x[0]['day'] for x in vals}); rng=random.Random(20261016); boots=[]
        daily={d:[0.,0.,0.,0.] for d in days}
        for row,yes,value in vals:
            z=daily[row['day']]; z[0 if yes else 2]+=value; z[1 if yes else 3]+=1
        for _ in range(2000):
            sampled=[days[rng.randrange(len(days))] for _ in days] if days else []
            sums=[sum(daily[d][i] for d in sampled) for i in range(4)]
            if sums[1] and sums[3]: boots.append(sums[0]/sums[1]-sums[2]/sums[3])
        boots.sort(); ci=(boots[int(.025*len(boots))],boots[min(len(boots)-1,int(.975*len(boots)))]) if boots else (float('nan'),float('nan'))
        ma=f'{sum(a)/len(a):.3f}' if a else 'NA'; mb=f'{sum(b)/len(b):.3f}' if b else 'NA'
        lines.append(f'| {f} | {len(a)}/{len(b)} | {ma} | {mb} | {diff:+.3f} | [{ci[0]:.3f}, {ci[1]:.3f}] |')
        result.append((diff,f,ci))
    # LC3 has no combinations registered unless the feature contrast is positive
    # and its day-block interval excludes zero; cap is six by the card.
    chosen=[x for x in sorted(result,reverse=True) if x[0]>0 and x[2][0]>0][:6]
    lines += ['', '## LC3 pre-registration (frozen before LC3)', '',
      'Selected combinations (max 6): '+(', '.join(x[1] for x in chosen) if chosen else '**none**; no one-at-a-time contrast had a positive lower 95% CI bound.'),
      '', 'These are candidate feature filters attached to KEEP levels, not trading rules. No LC3 simulation is included here.', '',
      f'Trials counted: one event-table generation; {len(features)} one-at-a-time feature contrasts. Total **{len(features)+1}** analysis arms, logged in `research/layer_lab/TRIALS.md`.']
    Path(path).write_text('\n'.join(lines)+'\n',encoding='utf-8',newline='\n')


if __name__=='__main__':
    from MyTradingSys.backtest.bt.bt_data import load_klines
    data=load_klines('F:/MTS/data/tom_raw','klines',1732147200000,1743465600000)
    fp=load_footprint('F:/MTS/data/orderflow_1m',1732147200000,1743465600000)
    write_csv(make_events(data,footprint=fp),Path(__file__).with_name('event_table.csv'))
