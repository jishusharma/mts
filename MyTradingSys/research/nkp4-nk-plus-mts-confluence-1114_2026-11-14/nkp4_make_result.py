"""Build RESULT.md from dev_stepA.json, dev_cells.csv, cells_frozen.json, val_results.json (no new numbers computed here)."""
import json
from pathlib import Path
import pandas as pd
import nkp4_phases as PH

HERE = Path(__file__).resolve().parent
dev = json.loads((HERE / "dev_stepA.json").read_text())
val = json.loads((HERE / "val_results.json").read_text())
fz = json.loads((HERE / "cells_frozen.json").read_text())
cells = pd.read_csv(HERE / "dev_cells.csv")
ev = cells.dropna(subset=["mean"])
kept = fz["kept"]
f = lambda x, d=3: "" if x is None or pd.isna(x) else f"{x:.{d}f}"


def md(df):
    cols = list(df.columns)
    out = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    for _, r in df.iterrows():
        out.append("| " + " | ".join(str(r[c]) for c in cols) + " |")
    return "\n".join(out)


def stepA_table(rows):
    a = pd.DataFrame([r for r in rows if r["kind"] == "app_vs_opp"])
    a["phase"] = pd.Categorical(a["phase"], PH.LABELS, ordered=True)
    a = a.sort_values(["phase", "rule"])
    t = pd.DataFrame({"phase": a["phase"].astype(str), "rule": a["rule"], "approp. dir": a["phase"].map(
        lambda p: {"CAPITULATION": "long", "MARKDOWN": "short", "RELIEF": "long", "ACCUM-RANGE": "geometry", "MARKUP": "long",
                   "DISTRIBUTION": "short"}[str(p)]),
        "n app": a["n_app"], "days": a["days_app"], "gross R": a["gross_app"].map(f), "cost R (12bp)": a["cost_app"].map(f),
        "net R": a["net_app"].map(f), "n opp": a["n_opp"], "opp net R": a["net_opp"].map(f), "diff": a["diff"].map(f),
        "se": a["se"].map(f)})
    return md(t)


def mix(rows, split):
    a = pd.DataFrame([r for r in rows if r["kind"] == "dir"])
    g = a.groupby("phase")["n"].sum()
    return ", ".join(f"{p} {int(g.get(p, 0))}" for p in PH.LABELS)


rd = val["regime_days"]
pct = lambda d, tot: " / ".join(f"{k} {100 * d.get(k, 0) / tot:.0f}%" for k in PH.LABELS)
best = ev.sort_values("lo90", ascending=False).head(10).copy()
best["phase kept?"] = best["eligible"].map({True: "eligible", False: "under 5% of DEV days"})
bt = pd.DataFrame({"rule": best["rule"], "phase": best["phase"], "layer": best["layer"], "bucket": best["bucket"], "n": best["n"].astype(int),
                   "days": best["days"].astype(int), "gross R": best["gross"].map(f), "cost R": best["cost"].map(f),
                   "net R": best["mean"].map(f), "lo90 (score)": best["lo90"].map(f), "status": best["phase kept?"]})
elig = ev[ev["eligible"] == True]
d_ = pd.DataFrame([r for r in val["stepA"] if r["kind"] == "dir"])
d_["pd"] = d_["phase"].map(PH.PHASE_DIR)
d_ = d_[d_["pd"] == d_["dirn"]].sort_values("mean", ascending=False).head(6)
vt = pd.DataFrame({"rule": d_["rule"], "phase": d_["phase"], "dir": d_["dirn"].map({1: "long", -1: "short"}), "n": d_["n"].astype(int),
                   "days": d_["days"].astype(int), "gross R": d_["gross"].map(f), "cost R": d_["cost"].map(f), "net R": d_["mean"].map(f),
                   "day CI low (95%)": d_["lo95"].map(f)})
nd = pd.DataFrame(dev["nodata"]).T.reset_index().rename(columns={"index": "rule"})
af = pd.DataFrame(val["aux_first"]).T
today = val["today"]
tl = pd.DataFrame(today["last10"])
ctxrows = []
for s in ("BTC", "ETH"):
    c = today[s]
    ctxrows.append({"coin": s, "last closed 15m bar (UTC)": c["last_bar"], "phase": c["phase"], **{k.split("_")[0]: v for k, v in c["ctx"].items()}})
dev_pos = int((elig["lo90"] > 0).sum()); all_pos = int((ev["lo90"] > 0).sum())
capd = pd.DataFrame([r for r in dev["stepA"] if r["kind"] == "dir" and r["phase"] == "CAPITULATION" and r["dirn"] == 1]).set_index("rule")
capv = pd.DataFrame([r for r in val["stepA"] if r["kind"] == "dir" and r["phase"] == "CAPITULATION" and r["dirn"] == 1]).set_index("rule")
captab = pd.DataFrame({"rule": capd.index, "DEV n": capd["n"].astype(int).values, "DEV days": capd["days"].astype(int).values,
                       "DEV gross R": capd["gross"].map(f).values, "DEV net R": capd["mean"].map(f).values,
                       "VAL n": capv.reindex(capd.index)["n"].astype(int).values, "VAL days": capv.reindex(capd.index)["days"].astype(int).values,
                       "VAL gross R": capv.reindex(capd.index)["gross"].map(f).values, "VAL net R": capv.reindex(capd.index)["mean"].map(f).values,
                       "VAL day CI low": capv.reindex(capd.index)["lo95"].map(f).values})
ndev_pos = sum(1 for r in dev["stepA"] if r["kind"] == "app_vs_opp" and r["net_app"] > 0)
nval_pos = sum(1 for r in val["stepA"] if r["kind"] == "app_vs_opp" and r["net_app"] > 0)
verdict = (f"VERDICT: NO EDGE - 0 of {dev['cells_evaluated']} testable DEV cells (9 rules x 6 phases x 8 context layers x 3 buckets) had a day-clustered "
           f"lower 90% bound of net R above 0 at 12 bp, so 0 cells were kept and 0 went to VAL (best DEV score {f(best['lo90'].iloc[0])} R, "
           f"in CAPITULATION which holds only 2.8% of DEV days; best eligible-phase score {f(elig['lo90'].max())} R). Only CAPITULATION-long is positive in both splits, on 52 DEV days and 6 VAL days: UNDERPOWERED, not a pass")

txt = f"""{verdict}

Study nkp4-nk-plus-mts-confluence-1114: the five NK layers combined with MTS context (OI unwind/build, funding extreme, 24h taker-delta divergence, 4h RSI, daily WaveTrend, 4h Bollinger %B, volatility, session) inside six causal BTC phases; NK + MTS agreement counted in the phase direction (rules X1-X3). Method = MTS_BRAINS_SPEC_1114. PRE_REG.md and all study code committed before any outcome (sha {fz['code_commit'][:9]}); DEV stage ran on signals <= 2023-12-31 only (inputs truncated), cells_frozen.json (empty) committed before the VAL stage. 20 Binance spot USDT coins, 15m. Trade: next open, stop max(1 ATR, 0.5%), target 2R, 24-bar exit, 12 bp round trip taker (6 bp maker row with fill model is only run on kept cells, so none).

## Context
Phase = one label per UTC day from BTC closes through the prior day: CAPITULATION (long only), MARKDOWN (short), RELIEF (long), ACCUM-RANGE (long at lower third / short at upper third of the 40d range), MARKUP (long), DISTRIBUTION (short). Cycle state BEAR/BULL/BASE from drawdown, SMA200, 200-week SMA. Every table below is per phase, in the phase-appropriate direction; there is no pooled-phase headline. Cost R = fee as a fraction of the stop distance (12 bp x entry / stop); net R = gross R - cost R.

Regime mix: BTC days DEV (2019-2023, {rd['DEV_total']} days): {pct(rd['DEV'], rd['DEV_total'])}. VAL (2024-01-01 to 2026-11-13, {rd['VAL_total']} days): {pct(rd['VAL'], rd['VAL_total'])}.
Signals per phase (all rules, both directions), DEV: {mix(dev['stepA'], 'DEV')}. VAL: {mix(val['stepA'], 'VAL')}.
Sanity windows (labels, not tuned): CAPITULATION 2020-03-12..15 reads 75% CAPITULATION, 2022-06-13..18 83%; MARKDOWN 2022-01..10 51%, 2025-11..2026-02 68%; MARKUP 2020-11..2021-03 100%, 2023-10..2024-03 68%. CAPITULATION is 2.8% of DEV days (52 days), below the 5% floor, so it cannot supply a kept cell (UNDERPOWERED, not "fail"); it has only 6 VAL days.

## Step A: does the phase-appropriate direction beat the opposite one? (DEV, net of 12 bp)
diff = net R(appropriate) - net R(opposite), day-clustered; se by day-cluster bootstrap. Rows of the confluence rules X1-X3 are the "NK + MTS" test; N1-N5 and NN are the NK-only rules for comparison.

{stepA_table(dev['stepA'])}

Reading: phase-appropriate net R is negative in {54 - ndev_pos} of 54 DEV rows; the one positive row is CAPITULATION X3 (+0.052 R). The largest diff/se ratio is 1.9 (CAPITULATION X3; DISTRIBUTION N3 also 1.9), below 2. The phase direction does not beat the opposite direction in a way that survives noise and pays the fee, so Step B is labelled exploratory per the spec (it was still run, as the spec requires).

CAPITULATION long, the only phase with a consistent sign (DEV vs VAL, 12 bp, per rule):

{md(captab)}

Gross R in CAPITULATION long is positive in DEV (up to +0.14 R) and larger in VAL (+0.16 to +0.49 R), but VAL contains 6 CAPITULATION days, so the day-cluster interval is wide and the phase is under the 5% DEV-day floor. It is a lead for a later, separate pre-registration with more symbols or history, not a result of this study.

## Step B: DEV cell selection
Cells testable (n >= 150 signals and >= 40 days): {dev['cells_evaluated']} of 1296. Cells with lower 90% bound > 0: {all_pos} (eligible phases: {dev_pos}). Kept: 0. Ten best DEV cells by score, none kept:

{md(bt)}

In the five phases that can supply cells, no cell's lower bound is above -0.07 R (best: N1 first-hour x DISTRIBUTION x 4h RSI HIGH, net +0.017 R, gross 0.186 R, cost 0.169 R). CAPITULATION cells reach net +0.17 R on 40 to 50 days but their lower bounds stay below 0 and the phase is under the 5% floor.

C4/C5 data limits (futures OI from 2020-09 for BTC, 2021-12 for most others; funding from 2020-01 or listing; spot 1h taker data from 2019 or listing): signals with OI / funding available, per rule (phase-appropriate signals on DEV):

{md(nd)}

First available date per coin (OI first date is when the Binance archive starts, not a gap): see `val_results.json` key aux_first. Example: BTC OI {val['aux_first']['BTC']['oi']}, ETH OI {val['aux_first']['ETH']['oi']}, FIL OI {val['aux_first']['FIL']['oi']}, BTC funding {val['aux_first']['BTC']['fund']}. No cell was marked NO-DATA for a whole rule (every rule has more than 150 DEV signals with OI and funding).

## Step C: DEV-chosen cells on VAL (run once, kept cells only)
No kept cells, so no VAL cell, no placebo, no BH, no maker row. DEV cells passed VAL: 0 of 0 (nothing to shrink). Fee/R reference at 12 bp: cost R per rule is 0.08 to 0.11 R in DEV CAPITULATION and 0.15 to 0.23 R in the other phases (VAL Step A table), against gross R between -0.12 and +0.09 R outside CAPITULATION.

Descriptive only, not selected: the six best VAL Step A rows by net R in the phase-appropriate direction (VAL has {nval_pos} of 54 positive rows, all in CAPITULATION, 6 days):

{md(vt)}

VAL Step A per phase and rule (same layout as DEV):

{stepA_table(val['stepA'])}

## Useful trades now (descriptive only, no advice)
Today's phase label (BTC, applied to BTC and ETH) from the last 10 days; the 2026-11-14 row is provisional because it uses the incomplete 2026-11-13 daily candle (data to 2026-11-13 20:15 UTC):

{md(tl)}

Current context buckets on the last closed 15m bar:

{md(pd.DataFrame(ctxrows))}

Active kept cells for BTC/ETH: none, because there are no kept cells. Both coins currently sit in MARKDOWN (short phase) with 4h RSI at or below 40 and daily WaveTrend at or below -53 (oversold) - the exact exhaustion-against-the-phase state; DEV found no cell in MARKDOWN that pays fees (best MARKDOWN cell: X3 with daily WaveTrend OB, lower bound -0.10 R). C4 (OI) shows NO-DATA because the archive's daily files end before the last bar.

## Limits, stated
- BTC-only phase label on 20 coins: effective n is days. 4 cycles. CAPITULATION and ACCUM-RANGE are thin; VAL has 6 CAPITULATION days.
- OI and funding are USD-M perp series used as context for spot-priced trades; no funding cost charged on the spot trades.
- Parameters are OURS (phase thresholds, bucket cutoffs, MTS-agreement mapping, stop/target/hold); not tuned on DEV or VAL. Nothing was added after the DEV result.
- Zero kept cells is a valid pre-registered outcome; it supports "no NK or NK+MTS rule has fee-net edge on 15m crypto in any single-bucket phase cell", and does not show that other timeframes, exits or maker-only execution would fail.
- Files: PRE_REG.md, nkp4_study.py, nkp4_phases.py, nkp4_stats.py, nkp4_run.py, test_nkp4_study.py, nkp4_fetch.py, dev_cells.csv, dev_stepA.json, cells_frozen.json, val_results.json. Raw data in F:\\MTS\\data_cache\\ (not in git).
"""
(HERE / "RESULT.md").write_text(txt, encoding="utf-8")
print(txt[:1500])
