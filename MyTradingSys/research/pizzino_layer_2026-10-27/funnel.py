"""Count-only funnel for the default cell (no returns): how many bars pass each SPEC section 6 condition."""
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import study as S  # noqa: E402

pz = S.pz
bars = S.load(S.DEV_END)
prm = S.DEFAULT
H = [b["h"] for b in bars]; L = [b["l"] for b in bars]; C = [b["c"] for b in bars]
piv = [S.Pivots(H, L, n) for n in prm["ns"]]
c = Counter()
for i in range(len(bars) - 1):
    known = [p.at(i) for p in piv]
    st = [pz.swing_state([p.price for p in a if p.kind == "H"], [p.price for p in a if p.kind == "L"], C[i])[0] for a in known]
    conf = sum(st)
    c[f"conf{conf:+d}"] += 1
    ph3 = [p.price for p in known[2] if p.kind == "H"]; pl3 = [p.price for p in known[2] if p.kind == "L"]
    ph1 = [p.price for p in known[0] if p.kind == "H"]; pl1 = [p.price for p in known[0] if p.kind == "L"]
    if not (ph3 and pl3 and ph1 and pl1):
        continue
    mid = (ph3[-1] + pl3[-1]) / 2
    s0 = max(0, i - prm["R"] - prm["N"] - 1)
    for side, sg in (("long", 1), ("short", -1)):
        for nm, X in (("pivot", ph1[-1] if sg == 1 else pl1[-1]), ("mid", mid)):
            r = pz.break_retest(X, C[s0:i + 1], H[s0:i + 1], L[s0:i + 1], direction="up" if sg == 1 else "down")
            if r["retest_bar"] is not None and s0 + r["retest_bar"] == i:
                c[f"{side}_{nm}_retest"] += 1
                if r["outcome"] == "hold":
                    c[f"{side}_{nm}_hold"] += 1
                    if sg * conf >= 2:
                        c[f"{side}_{nm}_hold_conf2"] += 1
                        if (C[i] > mid) == (sg == 1):
                            c[f"{side}_{nm}_hold_conf2_half"] += 1
print(len(bars), "bars"); [print(k, v) for k, v in sorted(c.items())]
