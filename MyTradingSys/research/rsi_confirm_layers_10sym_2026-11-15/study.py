"""rsi_confirm_layers_10sym_2026-11-15: the rsi_confirm_layers_2026-11-13 rule and 14 layers, UNCHANGED, on 10 symbols, fee-net 0.14 % round trip
(research_kit.TAKER_RT_PCT), Holm over 56 day-clustered tests, phase split by BTC regime. See PRE_REG.md.
Passes: --pass count (builds trades, writes counts.csv, NO return is computed), --pass run (returns, cells.csv, base.csv, phase.csv, survivors.json).
Look-ahead: forward windows only via the fwd_* helpers of rsi_grid_lib (reused through the 11-13 study module); every layer reads data closed at or before the signal close."""
import argparse
import importlib.util
import json
import sys
from math import erfc, sqrt
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(HERE))
from MyTradingSys.backtest import research_kit as rk  # noqa: E402
import regime_ctx  # noqa: E402

PARENT = REPO / "MyTradingSys" / "research" / "rsi_confirm_layers_2026-11-13"
sys.path.insert(0, str(PARENT))
_sp = importlib.util.spec_from_file_location("rsi_layers_1113", PARENT / "study.py")
S = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(S)

COINS = "BTC ETH SOL XRP DOGE BNB ADA LINK LTC AVAX".split()
S.COINS = COINS
S.CACHE = str(REPO / "runtime_data" / "rsi-confirm-10sym-1115")
S.TAKER = rk.TAKER_RT_PCT / 100.0 / 2.0          # per side; round trip = research_kit.TAKER_RT_PCT, no constant defined here
S.rng = np.random.default_rng(20261115)
DAY, HOUR, VAL0 = S.DAY, S.HOUR, S.VAL0
HALF = int(np.datetime64("2025-07-01", "ms").astype(np.int64))
M_FAMILY = len(S.TFS) * len(S.EXITS) * len(S.LAYERS)   # 56


def p_one_sided(m, se):
    """One-sided p for mean <= 0 from a normal t = m / se (day-clustered SE)."""
    if not np.isfinite(se) or se <= 0:
        return 1.0
    return 0.5 * erfc((m / se) / sqrt(2.0))


def cell(df, mask, tf, ex, base):
    col = "net_" + ex
    sub = df[(df.tf == tf) & mask(df)]
    dev, val = sub[sub.entry_t < VAL0], sub[sub.entry_t >= VAL0]
    v = val[col].values
    m, se = rk.cluster_mean_se(v, (val.entry_t // DAY).values) if len(v) else (np.nan, np.nan)
    bm, blo, bhi, bp = S.boot(v, S.week_of(val.entry_t.values)) if len(v) else (np.nan,) * 4
    h1, h2 = val[val.entry_t < HALF][col], val[val.entry_t >= HALF][col]
    pp = S.placebo_p(base["vals"], len(v), m) if len(v) >= 5 else np.nan
    return dict(tf=tf, exit=ex, n_dev=len(dev), mean_dev=float(dev[col].mean()) if len(dev) else np.nan, n_val=len(v),
                win_val=float((v > 0).mean()) if len(v) else np.nan, mean_val=m, se_val=se, mde=rk.MDE_Z * se if np.isfinite(se) else np.nan,
                lo_val=blo, hi_val=bhi, p_raw=p_one_sided(m, se) if len(v) else 1.0, vs_base=m - base["mean"] if len(v) else np.nan,
                n_h1=len(h1), mean_h1=float(h1.mean()) if len(h1) else np.nan, n_h2=len(h2), mean_h2=float(h2.mean()) if len(h2) else np.nan,
                placebo_p=pp)


def build_df():
    coins = {c: S.Coin(c) for c in COINS}
    rows = []
    for c in COINS:
        rows += S.build(coins[c], coins["BTC"])
    df = pd.DataFrame(rows).sort_values(["entry_t", "coin"]).reset_index(drop=True)
    regime_at = regime_ctx.regime_fn()
    df["regime"] = [regime_at(int(t)) or "none" for t in df.entry_t]
    return coins, df


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pass", dest="pass_", required=True, choices=("count", "run"))
    a = ap.parse_args()
    coins, df = build_df()
    df, tert = S.add_layer_flags(df)
    if a.pass_ == "count":
        out = []
        for tf in S.TFS:
            for split, msk in (("DEV", df.entry_t < VAL0), ("VAL", df.entry_t >= VAL0)):
                b = df[(df.tf == tf) & msk]
                out.append(dict(tf=tf, split=split, layer="BASE", n=len(b), days=int((b.entry_t // DAY).nunique())))
                for lay in S.LAYERS:
                    s = b[b["L_" + lay]]
                    out.append(dict(tf=tf, split=split, layer=lay, n=len(s), days=int((s.entry_t // DAY).nunique())))
        pd.DataFrame(out).to_csv(HERE / "counts.csv", index=False)
        print(pd.DataFrame(out).to_string())
        return
    df = S.run_exits(coins, df)
    df.to_csv(Path(S.CACHE) / "trades.csv", index=False)
    cells, bases, base_rows = [], {}, []
    for tf in S.TFS:
        for ex in S.EXITS:
            b = df[(df.tf == tf) & (df.entry_t >= VAL0)]
            bd = df[(df.tf == tf) & (df.entry_t < VAL0)]
            col = "net_" + ex
            bases[(tf, ex)] = dict(vals=b[col].values, mean=float(b[col].mean()))
            c = cell(df, lambda s: np.ones(len(s), bool), tf, ex, bases[(tf, ex)])
            c["layer"] = "BASE"
            c["mean_dev"] = float(bd[col].mean())
            base_rows.append(c)
            for lay in S.LAYERS:
                c = cell(df, lambda s, lay=lay: s["L_" + lay], tf, ex, bases[(tf, ex)])
                c["layer"] = lay
                cells.append(c)
    r = pd.DataFrame(cells)
    r["p_holm"] = rk.holm(r.p_raw.values, m=M_FAMILY)
    ver = []
    for x in r.itertuples():
        if x.n_val < 30:
            ver.append("UNDERPOWERED")
            continue
        ok = (x.mean_val > 0 and x.p_holm <= 0.05 and x.vs_base > 0 and x.mean_h1 > 0 and x.mean_h2 > 0
              and np.isfinite(x.placebo_p) and x.placebo_p <= 0.05)
        ver.append("PASS" if ok else "FAIL")
    r["verdict"] = ver
    r.to_csv(HERE / "cells.csv", index=False)
    pd.DataFrame(base_rows).to_csv(HERE / "base.csv", index=False)
    # phase split: base sets and layers with Holm p <= 0.20, VALIDATION, by BTC regime and by BTC side of SMA200
    ph = []
    keys = [("BASE", tf, ex) for tf in S.TFS for ex in S.EXITS] + [(x.layer, x.tf, x.exit) for x in r.itertuples() if x.p_holm <= 0.20]
    for lay, tf, ex in keys:
        s = df[(df.tf == tf) & (df.entry_t >= VAL0)]
        if lay != "BASE":
            s = s[s["L_" + lay]]
        for nm, mk in (("regime=bull", s.regime == "bull"), ("regime=range", s.regime == "range"), ("regime=bear", s.regime == "bear"),
                       ("BTC>SMA200", s.btc_above == 1.0), ("BTC<SMA200", s.btc_above == 0.0)):
            g = s[mk]["net_" + ex]
            m, se = rk.cluster_mean_se(g.values, (s[mk].entry_t // DAY).values) if len(g) else (np.nan, np.nan)
            ph.append(dict(layer=lay, tf=tf, exit=ex, phase=nm, n=len(g), mean_net_r=m, se=se, win=float((g > 0).mean()) if len(g) else np.nan))
    pd.DataFrame(ph).to_csv(HERE / "phase.csv", index=False)
    surv = r[r.verdict == "PASS"][["layer", "tf", "exit", "n_val", "mean_val", "p_holm"]]
    surv.to_json(HERE / "survivors.json", orient="records", indent=1)
    cov = {str(tf): dict(n=int((df.tf == tf).sum()), n_dev=int(((df.tf == tf) & (df.entry_t < VAL0)).sum()), n_val=int(((df.tf == tf) & (df.entry_t >= VAL0)).sum()),
                         n_oi=int(df[df.tf == tf].has_OI.sum()), small_r_cut=float(tert[tf])) for tf in S.TFS}
    json.dump(dict(coverage=cov, taker_rt_pct=rk.TAKER_RT_PCT, m_family=M_FAMILY, data_end=str(pd.to_datetime(df.entry_t.max(), unit="ms")),
                   n_pass=int(len(surv)), n_underpowered=int((r.verdict == "UNDERPOWERED").sum())), open(HERE / "results.json", "w"), indent=1)
    pd.set_option("display.width", 250)
    print(pd.DataFrame(base_rows).round(3).to_string())
    print(r.round(3).to_string())
    print(json.dumps(cov, indent=1), "PASS:", len(surv))


if __name__ == "__main__":
    main()
