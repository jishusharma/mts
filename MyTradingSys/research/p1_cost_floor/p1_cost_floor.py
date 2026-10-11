"""P1 cost-floor and passive-fill adverse-selection study (research only, no signal).
Data: MyTradingSys/runtime/orderflow_live/*.csv (1m BTCUSDT, 2026-09-29..10-03). Fees: backtest/fees.py.
Run: python research/p1_cost_floor/p1_cost_floor.py   (from MyTradingSys/)
"""
import sys, glob, json
import numpy as np, pandas as pd
sys.path.insert(0, "backtest")
from fees import DERIBIT_TAKER, DERIBIT_MAKER, BINANCE_TAKER, BINANCE_MAKER

fs = sorted(glob.glob("runtime/orderflow_live/20*.csv"))
d = pd.concat([pd.read_csv(f, usecols=["t","o","h","l","c","buy_vol","sell_vol"]) for f in fs])
d["t"] = pd.to_datetime(d.t, unit="ms"); d = d.drop_duplicates("t").sort_values("t").reset_index(drop=True)
# one real gap (3h02m) -> split into contiguous segments so no window crosses it
seg = (d.t.diff() != pd.Timedelta(minutes=1)).cumsum(); d["seg"] = seg
out = {"bars": len(d), "start": str(d.t.min()), "end": str(d.t.max()), "segments": int(seg.nunique())}

# A. cost in R vs stop distance (round trip, as fraction of entry price)
profiles = {
  "Binance taker/taker":      2*BINANCE_TAKER,
  "Binance maker/taker(stop)":BINANCE_MAKER+BINANCE_TAKER,
  "Binance maker/maker":      2*BINANCE_MAKER,
  "Deribit taker/taker":      2*DERIBIT_TAKER,
  "Deribit maker entry+target, taker stop (loser pays taker, winner maker)": None,
  "Deribit maker/maker":      2*DERIBIT_MAKER,
}
stops = [0.0010,0.0020,0.0030,0.0043,0.0060,0.0100]
A = {k:{f"{s*100:.2f}%":round(v/s,3) for s in stops} for k,v in profiles.items() if v is not None}
A["Deribit entry-maker/target-maker WIN, stop-taker LOSS"] = {f"{s*100:.2f}%":{"win_R":round(0/s,3),"loss_R":round(DERIBIT_TAKER/s,3)} for s in stops}
out["A_cost_in_R_by_stop_pct"] = A

# B. share of windows whose absolute move exceeds the cost floor
B = {}
for h in (5,15,60):
    r=[]
    for _,g in d.groupby("seg"):
        c=g.c.values
        if len(c)>h: r.append(np.abs(c[h:]/c[:-h]-1))
    r=np.concatenate(r)
    B[f"{h}m"]={"n":int(len(r)),"median_abs_bp":round(float(np.median(r)*1e4),1),
      **{f"share>{b}bp":round(float((r>b/1e4).mean()),3) for b in (5,10,12,20)}}
out["B_abs_move_vs_cost_floor"]=B

# C. passive limit orders with NO signal: fill by touch vs trade-through, forward return from the limit price
def run(offset_bp, mode, hold):
    res=[]
    for _,g in d.groupby("seg"):
        g=g.reset_index(drop=True); c=g.c.values; lo=g.l.values; hi=g.h.values
        for i in range(len(g)-1-hold):
            for side in (1,-1):
                px = c[i]*(1-side*offset_bp/1e4)          # buy below close / sell above close
                nxt_hit = lo[i+1] <= px if side==1 else hi[i+1] >= px
                strict  = lo[i+1] <  px if side==1 else hi[i+1] >  px
                filled = nxt_hit if mode=="touch" else strict
                if filled:
                    exit_px=c[i+1+hold]
                    res.append((g.t[i], side*(exit_px/px-1)*1e4))
    return pd.DataFrame(res,columns=["t","bp"])
C={}
for off in (0,2,5):
    for mode in ("touch","through"):
        for hold in (5,15):
            r=run(off,mode,hold)
            day=r.groupby(r.t.dt.date).bp.mean()
            C[f"offset{off}bp_{mode}_hold{hold}m"]={"fills":len(r),"mean_bp_from_limit_px":round(float(r.bp.mean()),2),
                "sd_bp":round(float(r.bp.std()),1),"daily_means_bp":[round(float(x),2) for x in day.values]}
# benchmark: market-at-close, same holds (should be ~0 by symmetry)
out["C_passive_fill_signalless"]=C
json.dump(out,open("research/p1_cost_floor/results.json","w"),indent=1)
print(json.dumps(out,indent=1))
