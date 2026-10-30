"""C26 arms A (ride to the level) and B (fade the swept take-out), exactly as C26_PRE_REG.md (committed 21fbba6b before this run).
Research only, no orders. Usage: python c26_arms.py <repo>"""
import os, sys, statistics as st
from datetime import datetime, timezone

sys.argv = sys.argv[:2]
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import failed_retest_takeout as F

H = [x[2] for x in F.rows]; L = [x[3] for x in F.rows]; O, C, T, N = F.O, F.C, F.T, F.N
FWD = int(datetime(2026, 11, 1, tzinfo=timezone.utc).timestamp() * 1000)


def forward_trade(e0, d, target, stop, last):
    """Enter at O[e0], walk to bar `last`; stop wins a same-bar tie. Net % after fees."""
    if e0 >= N or last >= N:
        return None
    E = O[e0]
    if target is not None and d * (E - target) >= 0:
        return -F.FEE * 100
    for k in range(e0, last + 1):
        if (d > 0 and L[k] <= stop) or (d < 0 and H[k] >= stop):
            return (d * (stop / E - 1) - F.FEE) * 100
        if target is not None and ((d > 0 and H[k] >= target) or (d < 0 and L[k] <= target)):
            return (d * (target / E - 1) - F.FEE) * 100
    return (d * (C[last] / E - 1) - F.FEE) * 100


def forward_arm_a(e, side):
    j, lvl = e["j"], abs(e["lvl"]); d = side
    return forward_trade(j + 1, d, lvl, O[j + 1] * (1 - 0.008 * d) if j + 1 < N else 0, j + 96)


def forward_arm_b(e, side):
    if e["out"][0] is None:
        return None
    k = e["j"] + e["out"][0]; lvl = abs(e["lvl"]); d = -side
    for s in range(k, min(N - 1, k + 5)):
        if (side > 0 and C[s] < lvl) or (side < 0 and C[s] > lvl):
            ext = max(H[k:s + 1]) * 1.0005 if side > 0 else min(L[k:s + 1]) * 0.9995
            return forward_trade(s + 1, d, O[s + 1] * (1 + 0.01 * d), ext, s + 96)
    return None


res = {}
for side in (1, -1):
    ev, _ = F.run(side)
    for e in ev:
        per = "forward" if e["t"] >= FWD else ("2024-07..10-31" if e["oos"] else "2022-01..2024-06")
        for arm, f in (("A ride", forward_arm_a), ("B fade", forward_arm_b)):
            r = f(e, side)
            if r is not None:
                res.setdefault((arm, per, side), []).append(r)
print("fee per trade %.3f%%" % (F.FEE * 100))
for arm in ("A ride", "B fade"):
    for per in ("2022-01..2024-06", "2024-07..10-31", "forward"):
        for side, sn in ((1, "highs"), (-1, "lows"), (0, "pooled")):
            x = res.get((arm, per, side), []) if side else res.get((arm, per, 1), []) + res.get((arm, per, -1), [])
            if len(x) < 2:
                print("  %s %-16s %-6s n=%d" % (arm, per, sn, len(x))); continue
            m = st.mean(x); t = m / (st.stdev(x) / len(x) ** 0.5) if st.stdev(x) > 0 else 0
            print("  %s %-16s %-6s n=%4d win %2.0f%% mean net %+.3f%% t %+.2f" % (arm, per, sn, len(x), 100 * sum(v > 0 for v in x) / len(x), m, t))
