"""Descriptive diagnostic (not a cell): why the parent's 69% reach-POC differs from the gated count. python -I diag5.py <npz_dir>"""
import sys, json
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
import parent_study as ps
import study5 as s5

def run(syms, d):
    rows = []
    for sym in syms:
        for ev in ps.day_events(sym, d)[0]:
            b = ps.find_setup(ev["inside"], True)
            if b is None:
                continue
            ei = (b + 1) * ps.BLOCK - 1
            H, L, C, side, poc = ev["H"], ev["L"], ev["C"], ev["side"], ev["poc"]
            entry = float(C[ei])
            dist = side * (poc - entry) / entry
            parent_reach = bool((L[ei + 1:] <= poc).any()) if side == -1 else bool((H[ei + 1:] >= poc).any())
            rows.append((dist, parent_reach))
    a = np.array(rows, dtype=float)
    dist, rch = a[:, 0], a[:, 1] > 0
    out = dict(n=len(a), parent_definition_reach_pct=100 * rch.mean())
    for nm, m in (("poc_already_passed_or_behind (dist<=0)", dist <= 0), ("0<dist<36bp", (dist > 0) & (dist < s5.MIN_TGT)), (">=36bp ahead", dist >= s5.MIN_TGT)):
        out[nm] = dict(n=int(m.sum()), share_pct=100 * m.mean(), reach_pct=100 * float(rch[m].mean()) if m.any() else None)
    return out

if __name__ == "__main__":
    print(json.dumps(dict(new=run(s5.NEW, sys.argv[1]), seen=run(s5.SEEN, sys.argv[1])), indent=1))
