"""Weight sensitivity: perturb every OURS weight by a random factor and count how often the validation anchors stay in the top 10."""
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import score as S

NAMES = ["W_NAMED", "W_CORE", "W_GEN", "W_RSI", "DESC_FACTOR", "W_HINDI", "W_SERIES_NUM", "W_XREF", "W_VIEWS", "W_LEN_TEACH",
         "W_CHAPTERS", "P_MARKET_UPDATE", "P_STOCKTIP", "P_OPTIONS", "P_NONTEACH_PL"]
base = {n: getattr(S, n) for n in NAMES}
random.seed(20261015)
SPREAD = float(sys.argv[1]) if len(sys.argv) > 1 else 0.3
res = {"A-CQiV_UFB4": [], "W1HrDl70Lhk": [], "Wvq1TZh8aF0": []}
for _ in range(300):
    for n, v in base.items():
        setattr(S, n, v * random.uniform(1 - SPREAD, 1 + SPREAD))
    out = S.compute()[0]
    for k in res:
        res[k].append(next(o["rank"] for o in out if o["id"] == k))
for k, r in res.items():
    r.sort()
    print(f"spread +/-{SPREAD:.0%} {k}: median rank {r[len(r)//2]}, top10 in {sum(x <= 10 for x in r)/len(r):.0%}, worst {r[-1]}")
