import sys
sys.dont_write_bytecode = True
import importlib.util, statistics
from pathlib import Path
from collections import defaultdict
from math import sqrt
R = Path(r"C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed")
s = importlib.util.spec_from_file_location("vp", str(R/"MyTradingSys/research/loose_code/vpin_proxy_2026-10-10.py"))
vp = importlib.util.module_from_spec(s)
s.loader.exec_module(vp)
bars = vp.load_1m(); _, vt_map = vp.build_vpin(bars)
bt = [b[0] for b in bars]; ca = {b[0]: b[4] for b in bars}
vt = sorted(vt_map)
def meas(i):
    c0 = ca[bt[i]]; o = {}
    for n, h in [("abs_1h",60),("abs_4h",240)]:
        if i+h < len(bt): o[n] = abs(ca[bt[i+h]]-c0)/c0*100
    hi = c0; lo = c0
    for j in range(i+1, min(i+61, len(bt))):
        cj = ca[bt[j]]
        if cj > hi: hi = cj
        if cj < lo: lo = cj
    o["adv_60"] = max(hi-c0, c0-lo)/c0*100
    return o
sp = []
for i, t in enumerate(vt):
    v = vt_map[t]; cut = t - vp.PCTILE_WINDOW_DAYS*86400000
    h = [vt_map[x] for x in vt[max(0,i-5000):i] if x >= cut]
    if len(h) < 200: continue
    h.sort(); k = int(len(h)*vp.SPIKE_PCTILE)
    if v > h[min(k, len(h)-1)]: sp.append(t)
print("spikes", len(sp))
bb = defaultdict(lambda: {"abs_1h":[],"abs_4h":[],"adv_60":[]})
for i in range(len(bt)):
    m = meas(i); d = bt[i]//86400000
    for k,v in m.items(): bb[d][k].append(v)
sb = defaultdict(lambda: {"abs_1h":[],"abs_4h":[],"adv_60":[]})
for t in sp:
    lo,hi,bi = 0,len(bt)-1,None
    while lo<=hi:
        mid=(lo+hi)//2
        if bt[mid]<=t: bi=mid; lo=mid+1
        else: hi=mid-1
    if bi is None or bi+241>=len(bt): continue
    m = meas(bi); d = t//86400000
    for k,v in m.items(): sb[d][k].append(v)
out = ["# VPIN Proxy - day-clustered t", ""]
out.append("| measure | spike n | spike days | base days | spike mean | base mean | diff | se | t |")
out.append("|---|---|---|---|---|---|---|---|---|")
for k in ["abs_1h","abs_4h","adv_60"]:
    sv=[x for d in sb.values() for x in d[k]]; bv=[x for d in bb.values() for x in d[k]]
    sd=[statistics.mean(d[k]) for d in sb.values() if d[k]]
    bd=[statistics.mean(d[k]) for d in bb.values() if d[k]]
    ses=statistics.pstdev(sd)/sqrt(len(sd)) if len(sd)>1 else 0
    seb=statistics.pstdev(bd)/sqrt(len(bd)) if len(bd)>1 else 0
    se=sqrt(ses**2+seb**2); df=statistics.mean(sv)-statistics.mean(bv)
    out.append("| {} | {} | {} | {} | {:+.4f} | {:+.4f} | {:+.4f} | {:.4f} | {:+.2f} |".format(k,len(sv),len(sd),len(bd),statistics.mean(sv),statistics.mean(bv),df,se,df/se if se>0 else 0))
open(R/"MyTradingSys/research/_archive/loose_2026-10/VPIN_DAYCLUSTERED_2026-10-10.md","w",encoding="utf-8",newline="\n").write("\n".join(out)+"\n")
print("done")