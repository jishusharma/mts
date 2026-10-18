"""Control: same trade count/side mix/ATR draw as each setup's TRAIN fires, but entry times drawn at random
(without replacement, TF-aligned, inside the TRAIN date span). Shows what MFE / gross / net look like with NO signal."""
import json, sys, os
import numpy as np
import mfe_exit_study as M

k1 = M.load_1m(); ft, fc = M.load_funding()
out = {}
rng = np.random.default_rng(20261013)
for name, fname, m in M.SETUPS:
    f = [x for x in M.thin(M.read_fires(fname), m) if x[3] == "TRAIN"]
    t0, t1_ = f[0][0], f[-1][0]
    grid = np.arange((t0 // (m * 60000)) * m * 60000, t1_, K_ := M.K * m * 60000)
    pick = rng.choice(grid, size=min(len(f), len(grid)), replace=False)
    sides = rng.choice([1, -1], size=len(pick))
    atrs = np.array([x[2] for x in f])[rng.permutation(len(f))[:len(pick)]]
    fires = [(int(t), int(s), float(a), "TRAIN") for t, s, a in zip(pick, sides, atrs)]
    tm = M.trade_matrix(k1, fires, m, ft, fc)
    g, n = tm["gross"][:, M.K - 1], tm["net"][:, M.K - 1]
    out[name] = {"n": tm["n"], "mfe_bp_mean": float(tm["mfe"].mean() * 1e4), "mae_bp_mean": float(tm["mae"].mean() * 1e4),
                 "gross_time_exit_bp": float(g.mean() * 1e4), "t_gross": M.tstat(g), "net_time_exit_bp": float(n.mean() * 1e4)}
    print(name, out[name])
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "control_random_entries.json"), "w", newline="\n"), indent=1)
