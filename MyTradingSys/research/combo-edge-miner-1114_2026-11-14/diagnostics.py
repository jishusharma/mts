"""Post-run replication diagnostic (NOT pre-registered, NOT used for selection): how do ALL DEV cells with n >= 100 behave on VAL?
Reads dev_cells.csv written by run.py, evaluates each cell's VAL mean net R (12 bp, no bootstrap) and the same-phase random-entry mean."""
import os
import sys
import json
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import miner as M  # noqa: E402
import run as R  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
df = pd.read_csv(os.path.join(M.DATA, "dev_cells.csv"))
frames = {tf: M.build_frame(tf) for tf in ("1d", "4h")}
pools = {}
rows = []
for r in df.itertuples():
    fr = frames[r.tf]
    feats = [M.FIDX[x] for x in r.combo.split("+")]
    pm = np.zeros(6, bool)
    pm[r.phase] = True
    pk = M.cell_picks(fr, r.d, feats, r.kind, pm, "val")
    key = (r.tf, r.d, r.kind, r.phase)
    if key not in pools:
        pools[key] = R.pool(fr, r.d, r.kind, pm, "val")[1]
    rp = pools[key]
    if pk.size == 0:
        rows.append((np.nan, 0, float(rp.mean()) if len(rp) else np.nan))
        continue
    rr = M.net_r(fr.sim[(r.d, r.kind)], pk, M.COST12)
    rows.append((float(rr.mean()), int(pk.size), float(rp.mean()) if len(rp) else np.nan))
df["val_mean"], df["val_n"], df["val_rand"] = zip(*rows)
df["ci_lo"] = df.mean12 - 1.96 * df.se12
df["val_excess"] = df.val_mean - df.val_rand
df.to_csv(os.path.join(M.DATA, "dev_val_cells.csv"), index=False)
ok = df[df.val_n >= 30]
out = {"cells_dev_n100": int(len(df)), "cells_val_n30": int(len(ok))}


def summ(x):
    return dict(cells=int(len(x)), val_mean_pos=float((x.val_mean > 0).mean()) if len(x) else None,
                val_excess_pos=float((x.val_excess > 0).mean()) if len(x) else None,
                val_mean_median=float(x.val_mean.median()) if len(x) else None,
                val_excess_median=float(x.val_excess.median()) if len(x) else None,
                dev_mean_median=float(x.mean12.median()) if len(x) else None)


out["all"] = summ(ok)
out["dev_ci_pos"] = summ(ok[ok.ci_lo > 0])
out["dev_bh05"] = summ(ok[ok.q < 0.05]) if "q" in ok else None
out["spearman_dev_val_mean"] = float(ok.mean12.rank().corr(ok.val_mean.rank()))
out["spearman_dev_val_excess"] = float((ok.mean12 - 0).rank().corr(ok.val_excess.rank()))
out["by_dir"] = {str(k): summ(g) for k, g in ok[ok.ci_lo > 0].groupby("d")}
out["by_kind"] = {k: summ(g) for k, g in ok[ok.ci_lo > 0].groupby("kind")}
out["by_phase"] = {M.PHASES[int(k)]: summ(g) for k, g in ok[ok.ci_lo > 0].groupby("phase")}
out["by_tf"] = {k: summ(g) for k, g in ok[ok.ci_lo > 0].groupby("tf")}
# feature frequency among DEV CI>0 cells (which layers keep showing up)
feat_count = {}
for combo in df[df.ci_lo > 0].combo:
    for f in combo.split("+"):
        feat_count[f] = feat_count.get(f, 0) + 1
out["feature_count_in_dev_ci_pos"] = dict(sorted(feat_count.items(), key=lambda kv: -kv[1]))
# cells replicating on VAL: DEV CI low > 0 AND VAL mean > 0 AND VAL excess over random > 0 AND VAL n >= 30
rep = ok[(ok.ci_lo > 0) & (ok.val_mean > 0) & (ok.val_excess > 0)]
out["replicating_cells"] = int(len(rep))
out["replicating_by_combo_family"] = rep.groupby(["tf", "d", "kind", "phase"]).size().sort_values(ascending=False).head(8).reset_index().astype(str).values.tolist()
json.dump(out, open(os.path.join(HERE, "diagnostics.json"), "w"), indent=1)
print(json.dumps(out, indent=1))
