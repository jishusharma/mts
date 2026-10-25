"""Independent touched-only, family/month distance-matched LC1 audit."""
import csv, datetime as dt, random, sys
from collections import defaultdict
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "MyTradingSys/research/levels_confluence_2026-10-14"))
from levels import levels_by_day
from MyTradingSys.backtest.bt.bt_data import load_klines

DAY = 86_400_000
START = int(dt.datetime(2022,3,21,tzinfo=dt.timezone.utc).timestamp()*1000)
DEV = int(dt.datetime(2022,4,1,tzinfo=dt.timezone.utc).timestamp()*1000)
END = int(dt.datetime(2024,7,1,tzinfo=dt.timezone.utc).timestamp()*1000)
SEED = 20261024
K = 20
B = 2000

def month(day):
    d = dt.date(1970,1,1) + dt.timedelta(days=day)
    return d.year*12+d.month

def width(mid, price):
    return max(.004*mid, .001*abs(price))

def result(rows, level, w, prev):
    side = None
    touched = False
    for j, bar in enumerate(rows):
        hi, lo = float(bar['h']), float(bar['l'])
        if not touched:
            if lo <= level <= hi:
                ref = prev if prev is not None else float(bar['o'])
                side = 1 if ref >= level else -1
                touched = True
                first = True
            else:
                continue
        else:
            first = False
        favorable = hi >= level+w if side == 1 else lo <= level-w
        adverse = lo <= level-w if side == 1 else hi >= level+w
        if adverse:
            return 'BREAK'
        if favorable and not first:
            return 'HOLD'
    return 'NEITHER'

def main():
    bars = load_klines('F:/MTS/data/tom_raw', start_ms=START, end_ms=END)
    assert bars and min(x['t'] for x in bars) >= START and max(x['t'] for x in bars) < END
    byday = defaultdict(list)
    for bar in bars: byday[bar['t']//DAY].append(bar)
    # Build candidate lines from each decision day and its preceding 14 calendar days.
    levs = {}
    for day in sorted(byday):
        if day*DAY < DEV: continue
        window = [x for d in range(day-14, day+1) for x in byday.get(d,())]
        levs[day] = levels_by_day(window).get(day, [])
    devbars = {d: sorted(v,key=lambda x:x['t']) for d,v in byday.items() if d*DAY >= DEV}
    assert min(d*DAY for d in devbars) >= DEV and max(d*DAY for d in devbars)+DAY <= END
    pools = defaultdict(list)
    for day, rows in devbars.items():
        mid=float(rows[0]['o'])
        for lev in levs.get(day,()): pools[(lev['family'],month(day))].append(abs(float(lev['price'])-mid))
    rng=random.Random(SEED)
    byfam=defaultdict(lambda: defaultdict(lambda:[0,0,0,0]))
    same_distance=defaultdict(lambda:[0,0])
    for day, rows in sorted(devbars.items()):
        mid=float(rows[0]['o']); lo=np.fromiter((float(x['l']) for x in rows),float); hi=np.fromiter((float(x['h']) for x in rows),float)
        for lev in levs.get(day,()):
            fam=lev['family']; price=float(lev['price']); pool=pools[(fam,month(day))]
            # For a line, locate its first intraday touch and classify using only subsequent bars.
            def classify(p):
                ix=np.flatnonzero((lo<=p)&(p<=hi))
                if not len(ix): return None
                i=int(ix[0]); prev=float(rows[i-1]['c']) if i else None
                return result(rows[i:],p,width(mid,p),prev)
            real=classify(price)
            values=byfam[fam][day]
            if real is not None:
                values[0]+=int(real=='HOLD'); values[1]+=1
            matched=0; exact=0
            for _ in range(K):
                dist=pool[rng.randrange(len(pool))]
                sign=-1 if rng.random()<.5 else 1
                p=mid+sign*dist
                matched += int(abs(dist-abs(price-mid))<1e-9)
                exact += int(abs(p-price)<1e-9)
                outcome=classify(p)
                if outcome is not None:
                    values[2]+=int(outcome=='HOLD'); values[3]+=1
            same_distance[fam][0]+=matched
            same_distance[fam][1]+=K
    out=[]
    for fam, days in sorted(byfam.items()):
        keys=sorted(days); a=np.array([days[d] for d in keys],float)
        rr=np.random.default_rng(SEED + sum(ord(c) for c in fam))
        ix=rr.integers(0,len(keys),(B,len(keys)))
        sm=a[ix].sum(axis=1)
        dif=sm[:,0]/sm[:,1] - sm[:,2]/sm[:,3]
        lcb=float(np.quantile(dif,.025)); ucb=float(np.quantile(dif,.975))
        vals=a.sum(axis=0); n=int(vals[1]); cn=int(vals[3]); real=vals[0]/n; ctl=vals[2]/cn; delta=real-ctl
        out.append((fam,n,real,cn,ctl,delta,lcb,ucb,'KEEP' if lcb>0 else 'DROP',same_distance[fam][0]/same_distance[fam][1]))
    path=Path(__file__).parent/'independent_results.csv'
    with path.open('w',newline='',encoding='utf-8') as f:
        w=csv.writer(f); w.writerow(['family','real_touches','real_hold_rate','control_touches','control_hold_rate','diff','ci_lo','ci_hi','verdict','pool_draw_same_distance_share']); w.writerows(out)
    print('bars',len(bars),'dev_days',len(devbars),'families',len(out),'seed',SEED,'K',K,'bootstrap',B)
    for r in out: print(f'{r[0]} n={r[1]} real={r[2]:.4%} ctrl_n={r[3]} ctrl={r[4]:.4%} diff={r[5]*100:+.2f}pp CI=[{r[6]*100:+.2f},{r[7]*100:+.2f}] {r[8]} same-distance-draw={r[9]:.2%}')
    print('csv',path)
if __name__=='__main__': main()


