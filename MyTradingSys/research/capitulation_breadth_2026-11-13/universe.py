"""Universe rule (run BEFORE outcomes): candidates with first 4h bar <= 2021-12-31, still trading (last bar within 7 days of the newest), ranked by quote volume of the last 90 days in the cache, top 60."""
import json, os, glob, sys
from fetch import OUT
CUT = 1640908800000  # 2021-12-31 00:00 UTC
def build():
    res = []
    LAST = max(json.load(open(f))[-1][0] for f in glob.glob(os.path.join(OUT, "*_4h.json")))
    for f in glob.glob(os.path.join(OUT, "*_4h.json")):
        c = os.path.basename(f)[:-8]
        r = json.load(open(f))
        if r[0][0] <= CUT and r[-1][0] >= LAST - 7 * 86400000:  # still trading
            res.append((sum(x[5] for x in r[-540:]), c, r[0][0]))
    res.sort(reverse=True)
    return res
if __name__ == "__main__":
    rs = build()
    print(len(rs), "pass listing filter")
    print(" ".join(c for _, c, _ in rs[:60]))
    print("dropped (rank>60):", " ".join(c for _, c, _ in rs[60:]))
