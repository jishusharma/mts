"""Independent 20-bar example for FORMULAS.md section 24. Does NOT import stoch_core or quad_rotation.

Plain Python, written from the section 24 definition: raw %K_k[t] = 100*(C-LL)/(HH-LL) over bars t-k+1..t (HH=LL gives
NaN), line = SMA_d(raw %K) (D line, KURISKO_SPEC s5 gap 2). Prints a table; the golden CSV is written from it.
Run: python make_golden.py   (rewrites golden_stoch_k5d3.csv; review the diff before committing)
"""
import math
from pathlib import Path

# 20 hand-chosen bars (high, low, close). Bars 7, 8 are flat (h=l=c=111) but sit inside 5-bar windows that have range,
# so raw %K stays defined (100); the HH=LL NaN rule is tested separately on a flat series.
BARS = [
    (102, 98, 100), (104, 99, 103), (105, 101, 102), (106, 102, 105), (107, 103, 104),
    (108, 104, 107), (110, 106, 109), (111, 111, 111), (111, 111, 111), (110, 106, 107),
    (109, 105, 106), (108, 104, 105), (107, 103, 104), (106, 102, 103), (105, 101, 102),
    (104, 100, 101), (103, 99, 102), (105, 100, 104), (107, 102, 106), (108, 104, 107),
]
K, D = 5, 3


def raw_k(i):
    if i < K - 1:
        return math.nan
    w = BARS[i - K + 1:i + 1]
    hh, ll, c = max(b[0] for b in w), min(b[1] for b in w), BARS[i][2]
    return math.nan if hh == ll else 100.0 * (c - ll) / (hh - ll)


raws = [raw_k(i) for i in range(len(BARS))]
lines = []
for i in range(len(BARS)):
    w = raws[i - D + 1:i + 1] if i >= D - 1 else []
    lines.append(math.nan if len(w) < D or any(math.isnan(v) for v in w) else sum(w) / D)

if __name__ == "__main__":
    out = ["i,high,low,close,raw_k,line"]
    for i, (h, l, c) in enumerate(BARS):
        f = lambda v: "" if math.isnan(v) else "%.10f" % v
        out.append(f"{i},{h},{l},{c},{f(raws[i])},{f(lines[i])}")
    Path(__file__).with_name("golden_stoch_k5d3.csv").write_text("\n".join(out) + "\n", newline="\n")
    print("\n".join(out))
