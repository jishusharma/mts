"""Phase mix per split (days and 4H decision bars) - no outcomes. Output goes into PRE_REG.md Context."""
import sys, os
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib
from fetch import COINS
SPL = {"DEV": (0, 1704067200000), "VAL": (1704067200000, 1e18), "RECENT": (1751328000000, 1e18)}
cnt = {s: np.zeros(6) for s in SPL}
dcnt = {s: np.zeros(6) for s in SPL}
for c in COINS:
    dd = lib.load(c, "1d"); ph = lib.phases(dd)
    for s, (a, b) in SPL.items():
        m = (dd[:, 0] >= a) & (dd[:, 0] < b)
        dcnt[s] += np.bincount(ph[m], minlength=6)
for s in SPL:
    tot = dcnt[s][1:].sum()
    print(f"Regime mix: {s} (coin-days, 20 coins, n={int(dcnt[s].sum())}, n/a excluded from %): " + ", ".join(f"{lib.PHASE_NAME[i]} {100*dcnt[s][i]/tot:.1f}%" for i in range(1, 6)))
