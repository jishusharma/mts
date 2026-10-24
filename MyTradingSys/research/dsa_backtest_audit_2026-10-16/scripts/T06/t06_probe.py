"""Counts for the report: how many G5 arms move more than 10 percent relative or 0.01 pp with real funding."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
j = json.load(open(HERE / "out" / "funding_rerun.json"))
tot = rel = ab = 0
for s, v in j["g5"].items():
    for (n1, r1), (n2, r2) in zip(v["flat"]["arms"], v["real"]["arms"]):
        tot += 1
        d = abs(r2["mean"] - r1["mean"])
        rel += d > 0.1 * abs(r1["mean"])
        ab += d > 0.01
print("arms", tot, "rel>10%", rel, "abs>0.01pp", ab)
