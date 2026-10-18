"""counts_v2.py: PRE_REG_V2.md s.2 counts only (keys, pool membership, candidate counts). No outcome, no price after T.

  python counts_v2.py  -> matched events/days under variant A (V2 pool: at-level hours with a ladder stop, no ledger cooldown)
Variant B (all stop-valid hours) is printed for reference only; V2 uses A.
"""
import sys, numpy as np, pandas as pd
from pathlib import Path
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import study as S
fr = S.frames()
led = {s: S.tradeable_ledger(fr[s]) for s in fr}
cset = {s: S.form_c(led[s], s) for s in led}
b = S.load_1m()
cn = S.load_context_null()
cfg = cn.Config(bar_min=60, cooldown=4, seed=0)
Cc, miss = S.hourly_closes(b)
rv = cn.rolling_rv(Cc, cfg.vol_win_min // cfg.bar_min)
def keyof(T): 
    return cn.context_key(Cc, int((T - S.HOUR - S.DEV_START_MS)//S.HOUR), cfg, rv=rv)
for variant in ("A_atlevel_nocooldown","B_allhours_stop"):
  tot_ev=0; days=set()
  for s in ("long","short"):
    f = fr[s]
    Tn = f["T"].to_numpy(np.int64)
    ok = (f["f3_stop_tf"]!="none").to_numpy().copy()
    if variant.startswith("A"): ok &= f["f1_at_level"].to_numpy(bool)
    Tc = cset[s]["T"].to_numpy(np.int64)
    near = (np.abs(Tn[:,None]-Tc[None,:])<=S.DAY).any(axis=1)
    pool = ok & ~near
    keys = {}
    for i in np.flatnonzero(pool):
        k = keyof(Tn[i])
        if k is not None: keys.setdefault(k,[]).append(Tn[i])
    rng=np.random.default_rng(0)
    m=0; ncand=[]; mdays=set(); nokey=0
    for T in Tc:
        k=keyof(T)
        if k is None: nokey+=1; continue
        cand=np.array(keys.get(k,[]),np.int64); ncand.append(len(cand))
        rng.shuffle(cand); ch=[]
        for j in cand:
            if len(ch)>=cfg.K: break
            if any(abs(int(j)-c)<=cfg.cooldown*S.HOUR for c in ch): continue
            ch.append(int(j))
        if len(ch)>=cfg.kmin: m+=1; mdays.add(int(T//S.DAY))
    print(variant,s,"pool",int(pool.sum()),"C",len(Tc),"nokey",nokey,"matched",m,"days",len(mdays),"median cand",int(np.median(ncand)))
    tot_ev+=m; days|=mdays
  print(variant,"POOLED matched",tot_ev,"days",len(days))
