"""Data sanity before any result run: daily continuity, 1m continuity, and parity of the 1d archive files against
daily bars aggregated from the 1m archive (DEV window only). Writes data_check.txt."""
import sys
sys.dont_write_bytecode = True
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import cdata  # noqa: E402

out = []
d = cdata.load_daily()
gaps = cdata.contiguous(d, cdata.DAY)
out.append("daily DEV bars %d  first %s  last %s  gaps %d" % (len(d), d[0]["t"], d[-1]["t"], len(gaps)))
bad = [b for b in d if not (b["l"] <= min(b["o"], b["c"]) and b["h"] >= max(b["o"], b["c"]) and b["l"] > 0)]
out.append("daily bars violating l<=min(o,c), h>=max(o,c): %d" % len(bad))

m1 = cdata.load_1m(cdata.HOURLY_START_MS, cdata.DEV_END_MS)
g1 = cdata.contiguous(m1, 60000)
out.append("1m DEV bars %d (2022-01..2024-06)  gaps %d  missing minutes %d" % (len(m1), len(g1), sum((m1[i]["t"] - m1[i - 1]["t"]) // 60000 - 1 for i in g1)))
dd, dropped = cdata.resample_offset(m1, 1440, 0)
out.append("1m -> 1d buckets %d, partial dropped %d" % (len(dd), dropped))
byt = {b["t"]: b for b in d}
mism, worst = 0, 0.0
for b in dd:
    x = byt.get(b["t"])
    if x is None:
        mism += 1
        continue
    rel = max(abs(b[k] - x[k]) / x[k] for k in "ohlc")
    worst = max(worst, rel)
    if rel > 1e-9:
        mism += 1
out.append("parity 1d-archive vs 1m-aggregate: %d days compared, %d mismatches, worst relative OHLC diff %.3g" % (len(dd), mism, worst))
f = cdata.Funding()
out.append("funding rows %d  first %s  last %s" % (len(f.rows), f.rows[0][0], f.rows[-1][0]))
h, dr = cdata.resample_offset(m1, 60, 0)
out.append("1h bars %d, partial dropped %d" % (len(h), dr))
text = "\n".join(out)
print(text)
Path(__file__).with_name("data_check.txt").write_text(text + "\n", encoding="utf-8", newline="\n")
