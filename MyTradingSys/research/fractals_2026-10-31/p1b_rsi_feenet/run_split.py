"""Rerun p1_split on events_feenet.csv (PRE_REG s4). Writes split_cells.csv and prints a summary."""
import importlib.util
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
_S = importlib.util.spec_from_file_location("p1_split", HERE.parent / "p1_split" / "p1_split.py")
p1 = importlib.util.module_from_spec(_S)
_S.loader.exec_module(p1)

ev = pd.read_csv(HERE / "events_feenet.csv")
events = pd.DataFrame({"date": ev["date"], "r": ev["r_net"]})
tags = p1.load_tags()
out = []
for tag in p1.TAGS:
    m = p1.join_events(events, tags, tag)
    t, nt = p1.analyse(m)
    t.insert(0, "tag", tag)
    out.append(t)
    pt, pnt = p1.analyse(m, label_col="week_parity")
    pt.insert(0, "tag", tag + "|placebo")
    out.append(pt)
res = pd.concat(out, ignore_index=True)
res.to_csv(HERE / "split_cells.csv", index=False, lineterminator="\n")
pd.set_option("display.width", 200)
print(res.round(4).to_string())
print("pooled n", len(ev), "net", ev.r_net.mean().round(4), "gross", ev.r_gross.mean().round(4))
print(ev.exit_reason.value_counts(normalize=True).round(3).to_dict())
print(ev.groupby("timeframe")[["r_gross", "r_net"]].agg(["count", "mean"]).round(4))
