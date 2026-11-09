"""Reads ledger.csv (one DEV run) and prints every cell of PRE_REG.md s7 for the 10-symbol pool. No new simulation."""
import importlib.util
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(REPO))
from MyTradingSys.backtest import research_kit as rk  # noqa: E402
from MyTradingSys.backtest import splits  # noqa: E402

_sp = importlib.util.spec_from_file_location("run_10sym", HERE / "run_10sym.py")
r = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(r)


def mdd(cum):
    peak = np.maximum.accumulate(np.concatenate([[0.0], cum]))
    return float((peak[1:] - cum).max())


def regime_context():
    spec = importlib.util.spec_from_file_location("ep", REPO / "MyTradingSys/research/bb_range_retest_eth_pool_2026-11/study.py")
    ep = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ep)
    regime_at = ep.prev.make_regime_at(*ep.spot_context("BTCUSDT", ep.DEV_END_MS))
    wk = list(ep.prev.week_starts(ep.DEV_START_MS, ep.DEV_END_MS))
    return regime_at, wk, ep.DAY


def main():
    df = pd.read_csv(HERE / "ledger.csv")
    df = df.sort_values(["day", "sym"]).reset_index(drop=True)
    x = df["net_bps"].to_numpy()
    n = len(x)
    m, se_c = rk.cluster_mean_se(x, df["day"].to_numpy())
    se_p = float(x.std(ddof=1) / np.sqrt(n))
    t_c, t_p = m / se_c, m / se_p
    sd = float(x.std(ddof=1))
    tgt, tm = df[df.outcome == "TARGET"], df[df.outcome == "TIME"]
    cum = np.cumsum(x) / 100.0                                  # % of K, pooled chronological (bps / 100)
    dd = mdd(cum)
    # buy-and-hold BTC max drawdown over DEV from 1m closes, last close of each UTC day
    btc = r.to_grid(r.load_klines("BTCUSDT"))[3]
    dclose = np.array([row[~np.isnan(row)][-1] for row in btc])
    bh = float(((np.maximum.accumulate(dclose) - dclose) / np.maximum.accumulate(dclose)).max() * 100)
    regime_at, wk, DAY = regime_context()
    wreg = [regime_at(t) for t in wk]
    mix = rk.regime_mix_line(wreg)
    wk_days = np.array([t // DAY for t in wk])
    reg_of_day = {}
    for d in df["day"].unique():
        abs_day = (splits.DEV_START.value // 10**9 // 86400) + int(d)
        j = int(np.searchsorted(wk_days, abs_day, side="right") - 1)
        reg_of_day[d] = wreg[j] or "none"
    df["regime"] = df["day"].map(reg_of_day)
    cond = (n >= 250) and m > 0 and t_c >= 2.0 and (tm.net_bps.sum() > -tgt.net_bps.sum()) and dd <= bh
    verdict = "PASS" if cond else ("INCONCLUSIVE" if n < 250 else "FAIL")
    out = {"n": n, "mean_bps": m, "se_cluster": se_c, "t_cluster": t_c, "se_plain": se_p, "t_plain": t_p, "sd": sd,
           "ci95": [m - 1.96 * se_c, m + 1.96 * se_c], "win_rate": float((x > 0).mean()),
           "mean_winner": float(x[x > 0].mean()), "mean_loser": float(x[x <= 0].mean()),
           "target_n": len(tgt), "target_sum_bps": float(tgt.net_bps.sum()), "timecap_n": len(tm), "timecap_sum_bps": float(tm.net_bps.sum()),
           "mdd_pct_K": dd, "bh_mdd_pct": bh, "mae_pct_q": [float(v) for v in np.percentile(df.mae_pct, [50, 90, 99, 100])],
           "regime_mix": mix, "verdict": verdict, "tranche_dist": df.tranches.value_counts().sort_index().to_dict()}
    print(json.dumps(out, indent=1, default=float))
    per = df.groupby("sym").agg(n=("net_bps", "size"), mean=("net_bps", "mean"), sd=("net_bps", "std"), win=("net_bps", lambda v: (v > 0).mean()),
                                timecap=("outcome", lambda v: (v == "TIME").sum()), sum_bps=("net_bps", "sum"))
    print(per.round(2).to_string())
    byreg = df.groupby("regime").agg(n=("net_bps", "size"), mean=("net_bps", "mean"))
    print(byreg.round(2).to_string())
    print("by year:", df.assign(y=df.date.str[:4]).groupby("y").net_bps.agg(["size", "mean"]).round(2).to_dict())
    per.to_csv(HERE / "per_symbol.csv", lineterminator="\n")
    json.dump(out, open(HERE / "analysis.json", "w", newline="\n"), indent=1, default=float)


if __name__ == "__main__":
    main()
