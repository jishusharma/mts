"""Run the frozen PRE_REG. Writes results.csv next to this file. DEV only."""
import sys
from pathlib import Path
import numpy as np
import pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parent))
import trigger_study as ts
from count_events import load_all

M = 24


def main():
    C = load_all()
    alts = [s for s in C if s != "BTC"]
    rows = []
    for kind in ("under", "over", "golden", "death"):
        sign = ts.DIRECTION[kind]
        for h in ts.HORIZONS:
            elig = {s: ts.eligible_days(C[s], h) for s in C}
            for uni, syms in (("BTC", ["BTC"]), ("alts", alts)):
                dates, vals, cnt = [], [], {}
                for s in syms:
                    ev = ts.dev_event_filter(C[s], ts.events(C[s], kind), h)
                    cnt[s] = len(ev)
                    dates += ev
                    vals += list(ts.fwd_net(C[s], ev, h, sign))
                n = len(vals)
                row = dict(trigger=kind, h=h, universe=uni, n=n, mean_net=np.nan, ci_lo=np.nan, ci_hi=np.nan,
                           null_mean=np.nan, p=np.nan)
                if n:
                    row["mean_net"] = float(np.mean(vals))
                if n >= 5:
                    nm = ts.null_means({s: elig[s] for s in syms}, C, cnt, h, sign)
                    mu = float(np.nanmean(nm))
                    p = (1 + np.sum(np.abs(nm - mu) >= abs(row["mean_net"] - mu))) / (1 + len(nm))
                    lo, hi = ts.week_block_ci(dates, vals)
                    row.update(ci_lo=lo, ci_hi=hi, null_mean=mu, p=float(p))
                rows.append(row)
    df = pd.DataFrame(rows)
    ps = df["p"].fillna(1.0).values
    order = np.argsort(ps)
    adj = np.empty(len(ps)); run = 0.0
    for rank, i in enumerate(order):
        run = max(run, (M - rank) * ps[i]); adj[i] = min(1.0, run)
    df["p_holm"] = np.where(df["p"].isna(), np.nan, adj)

    def verdict(r):
        if r["n"] < 5:
            return "INCONCLUSIVE"
        if r["p_holm"] < 0.05 and r["mean_net"] > 0 and r["ci_lo"] > 0:
            return "PASS"
        if r["ci_hi"] <= 0 or (r["n"] >= 20 and r["p_holm"] >= 0.05 and r["mean_net"] <= 0):
            return "FAIL"
        return "INCONCLUSIVE"
    df["verdict"] = df.apply(verdict, axis=1)
    df.to_csv(Path(__file__).resolve().parent / "results.csv", index=False, float_format="%.5f", lineterminator="\n")
    print(df.to_string())


if __name__ == "__main__":
    main()
