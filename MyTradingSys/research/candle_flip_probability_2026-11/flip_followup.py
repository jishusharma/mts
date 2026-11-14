"""Follow-up: recompute the candle-flip null with the session-adjusted variance clock (session_null.py), rescore the 7 cells that survived the
recalibrated baseline, write followup_cells.csv + FOLLOWUP.md + sim_desk/results/flip-engine-follow-up.json. Same fit/score windows, same bars, same
rows, same week clusters, same Holm and Brier rules as flip_model.py (imported, not copied). Definitions frozen in PRE_REG.md (Follow-up section).

    python flip_followup.py          # needs klines_1m_cache.csv.gz (fetch_1m.py); uses only bars up to the original window end (1,498,575 1m bars)
"""
import importlib.util
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
N_END = 1498575        # 1m bars of the original study (last open 2026-11-06T16:13Z); later bars are the fresh-data run, not touched here
SEVEN = [("G1 1m-15m", "split/Asia/at"), ("G1 1m-15m", "split/EU/at"), ("G2 30m-4h", "aligned/Asia/at"), ("G2 30m-4h", "aligned/US/at"),
         ("G2 30m-4h", "aligned/US/inside"), ("G2 30m-4h", "split/Asia/inside"), ("G3 6h-1d", "aligned/US/inside")]   # RESULT.md headline, baseline survivors at m = 48


def _load(name):
    spec = importlib.util.spec_from_file_location("flipfu_" + name, HERE / (name + ".py"))
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def build(ft, sn, o, h, l, c, flat_profile=False):
    cut_idx = (ft.CUT_MS - ft.START_MS) // ft.MIN_MS
    prof = np.ones(24) if flat_profile else sn.hour_profile(c, ft.START_MS, upto=cut_idx)   # fit window only
    cw = sn.weight_cumsum(prof, ft.START_MS, len(c))
    frames = []
    for tf, S in ft.TF_MIN.items():
        df = ft.tf_rows(o, h, l, c, S, tf=tf, clock=lambda B, J, S_, cw=cw: sn.session_t_left(cw, B, J, S_))
        if len(df):
            frames.append(df)
    return pd.concat(frames, ignore_index=True), prof


def family(fm, tab):
    tab = tab[tab["sess"] < 3].copy()
    tab["session"] = tab["sess"].map({0: "Asia", 1: "EU", 2: "US"})
    tab["cell"] = tab["htf"] + "/" + tab["session"] + "/" + tab["bb"]
    tab["cid"] = tab["tf"] + "|" + tab["bar_ms"].astype(str)
    tab["wid"] = (tab["bar_ms"] - fm.START_MS) // fm.WEEK_MS
    return tab


def with_clock(fm, fam, session):
    f = fam.copy()
    if session:
        f["t_left"] = f["t_left_s"]
        for col in ("open", "pc"):
            f["p0_" + col] = fm.p_keep(f["d_" + col].to_numpy(), f["t_left"].to_numpy())
    return f


def main():
    fm, ft, sn = _load("flip_model"), _load("flip_table"), _load("session_null")
    d = pd.read_csv(HERE / "klines_1m_cache.csv.gz")
    d = d.iloc[:N_END]
    assert d["open_time_ms"].iloc[0] == ft.START_MS and (np.diff(d["open_time_ms"].values) == ft.MIN_MS).all()
    o, h, l, c = (d[k].values for k in ("open", "high", "low", "close"))
    tab, prof = build(ft, sn, o, h, l, c)
    fam0 = family(fm, tab)
    groups = {k: [t for t in v if t != "1m"] for k, v in ft.GROUPS.items()}
    out = {}
    for name, session in (("flat", False), ("session", True)):
        fam = with_clock(fm, fam0, session)
        out[name] = fm.evaluate(fam, groups, "open")
    keep = ["group", "cell", "n", "bars", "weeks", "realised", "null", "delta", "delta2", "brier_null", "brier_cond", "brier_base", "brier_cond2",
            "holm12", "holm48", "holm12_2", "holm48_2", "counts", "counts2", "survives_48", "survives_48_2"]
    fl, se = out["flat"][keep], out["session"][keep]
    both = fl.merge(se, on=["group", "cell"], suffixes=("_flat", "_sess"))
    both.to_csv(HERE / "followup_cells.csv", index=False, lineterminator="\n", float_format="%.6g")
    # sanity: the flat recomputation must reproduce the committed cells.csv headline counts
    old = pd.read_csv(HERE / "cells.csv")
    old = old[old["colour"] == "open"]
    recon = {"counts": int(fl["counts"].sum()), "survives_48": int(fl["survives_48"].sum()), "counts2": int(fl["counts2"].sum()), "survives_48_2": int(fl["survives_48_2"].sum()),
             "committed": [int(old["counts"].sum()), int(old["survives_48"].sum()), int(old["counts2"].sum()), int(old["survives_48_2"].sum())]}
    seven = []
    for g, cell in SEVEN:
        r = both[(both["group"] == g) & (both["cell"] == cell)].iloc[0]
        seven.append({"group": g, "cell": cell, "n": int(r["n_sess"]), "bars": int(r["bars_sess"]), "weeks": int(r["weeks_sess"]),
                      "realised": r["realised_sess"], "flat_null": r["null_flat"], "session_null": r["null_sess"], "delta_flat": r["delta_flat"], "delta_session": r["delta_sess"],
                      "baseline_flat_delta2": r["delta2_flat"], "baseline_session_delta2": r["delta2_sess"],
                      "brier_null_flat": r["brier_null_flat"], "brier_null_session": r["brier_null_sess"],
                      "brier_cond_session": r["brier_cond_sess"], "brier_base_session": r["brier_base_sess"], "brier_cond2_session": r["brier_cond2_sess"],
                      "holm48_session_null": r["holm48_sess"], "holm48_session_baseline": r["holm48_2_sess"],
                      "counts_session_null": bool(r["counts_sess"]), "survives48_session_null": bool(r["survives_48_sess"]),
                      "counts_session_baseline": bool(r["counts2_sess"]), "survives48_session_baseline": bool(r["survives_48_2_sess"])})
    summary = {"study": "flip-engine-follow-up", "session_profile_utc_hour_weights_fit_2024": [round(float(x), 4) for x in prof],
               "flat_reproduction": recon,
               "session_null": {"counts": int(se["counts"].sum()), "survives_48": int(se["survives_48"].sum()), "names": [f"{r.group.split(' ')[0]} {r.cell}" for r in se[se["survives_48"]].itertuples()]},
               "session_baseline": {"counts": int(se["counts2"].sum()), "survives_48": int(se["survives_48_2"].sum()), "names": [f"{r.group.split(' ')[0]} {r.cell}" for r in se[se["survives_48_2"]].itertuples()]},
               "seven_cells": seven}
    res = HERE.parents[2] / "sim_desk" / "results" / "flip-engine-follow-up.json"   # repo-root sim_desk/results (the card path); not the catalogued research/sim_desk/results desk cards
    res.write_text(json.dumps(summary, indent=1, default=float) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({k: v for k, v in summary.items() if k != "seven_cells"}, indent=1))
    print(pd.DataFrame(seven).to_string())


if __name__ == "__main__":
    sys.exit(main())
