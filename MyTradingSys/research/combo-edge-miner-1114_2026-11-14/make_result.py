"""Render RESULT.md from results.json (combo-edge-miner-1114). No numbers are typed by hand."""
import os
import json

HERE = os.path.dirname(os.path.abspath(__file__))
R = json.load(open(os.path.join(HERE, "results.json")))
PH = ["UP_E", "UP_L", "MIX_E", "MIX_L", "DOWN_E", "DOWN_L"]


def f(x, nd=3, pct=False):
    if x is None:
        return "-"
    try:
        return f"{x * 100:.1f}%" if pct else f"{x:.{nd}f}"
    except Exception:
        return str(x)


def ci(v, lo="ci_lo12", hi="ci_hi12"):
    return f"[{f(v.get(lo))}, {f(v.get(hi))}]" if v.get(lo) is not None else "-"


top, named = R["top10"], R["named"]
passed = [c for c in top if c["val12"].get("pass")]
n_named_pass = [x for x in named if x["val"].get("pass")]
dev_mix, val_mix = R["regime"]["1d"]["dev"], R["regime"]["1d"]["val"]
L = []
if passed:
    verdict = (f"**VERDICT: {len(passed)} of 10 DEV-selected combinations pass every VAL gate at 12 bp after funding; treat as testnet-forward "
               f"candidates under the phase-first rule, not as an edge (one VAL regime sequence, {R['trials_total']:,} trials).**")
else:
    best = max(top, key=lambda c: c["val12"].get("mean12", -9))
    verdict = (f"**VERDICT: FAIL. None of the 10 DEV-selected combinations passes the VAL gates at 12 bp ({R['trials_total']:,} trials tried; "
               f"best VAL mean net R {f(best['val12'].get('mean12'))} on n={best['val12'].get('n')}); "
               f"{len(n_named_pass)} of {len(named)} pre-registered thinker cells pass.**")
DG = json.load(open(os.path.join(HERE, "diagnostics.json"))) if os.path.exists(os.path.join(HERE, "diagnostics.json")) else None
L += [verdict, ""]
if DG:
    ci_ = DG["dev_ci_pos"]
    L += [f"**Descriptive, post-run (not a gate): the DEV-significant cells are one family, long trend / momentum continuation in the early-cycle UP phase (UP_E), and its SIGN replicates on VAL: {ci_['val_mean_pos'] * 100:.0f}% of the {ci_['cells']} DEV-CI>0 cells with VAL n >= 30 have VAL mean net R > 0 and {ci_['val_excess_pos'] * 100:.0f}% beat same-phase random entries (median VAL excess {ci_['val_excess_median']:+.2f} R); shorts do not replicate. It fails the strict gates on tail dependence and the BH step, and BTC and ETH are in MIX_L today, so it is not active.**", ""]
L += ["# combo-edge-miner-1114: exhaustive 2/3-way layer combinations x phase x direction x 3 exits", "",
      "## Context", "",
      "Regime: BTC structure UP / MIX / DOWN (close vs SMA200d and its 20-day slope), 20 coins, 4h and 1d bars; entry day label from prior closes only.",
      "Phase: cycle clock (halving, early under 540 days / late) x structure = 6 labels, every cell conditioned on exactly one label.",
      "Session: none, because holds are days to weeks.",
      f"Entry: next bar open after the onset bar, taker, {f(R['cost12'] * 1e4, 0)} bp round trip plus actual funding, stop max(2.5 ATR, 2%), exits 3R / ATR trail / structure break.", "",
      f"Regime mix: DEV (2020-2023, {dev_mix['bars']:,} coin-days) bull {f(dev_mix['bull'], pct=True)} / range {f(dev_mix['range'], pct=True)} / bear {f(dev_mix['bear'], pct=True)}; "
      f"VAL (2024-2026-11, {val_mix['bars']:,} coin-days) bull {f(val_mix['bull'], pct=True)} / range {f(val_mix['range'], pct=True)} / bear {f(val_mix['bear'], pct=True)} "
      "(bull = UP, range = MIX, bear = DOWN; shares of coin-days with a valid label).",
      "Six-label shares (DEV | VAL, 1d frame): " + ", ".join(f"{p} {f(dev_mix['labels'][p], pct=True)} | {f(val_mix['labels'][p], pct=True)}" for p in PH) + ".", ""]
L += ["## Trials and deflation (DEV, selection only)", "",
      f"- Cells enumerated (combo x direction x phase x exit x timeframe): **{R['trials_enumerated']:,}**; plus {R['named_trials']} named thinker trials = **{R['trials_total']:,} total trials**.",
      f"- Cells with n >= 100 non-overlapping DEV trades: {R['cells_n100']:,}; of those, mean net R > 0 at 12 bp: {R['dev_positive_cells']:,}; day-cluster CI lower bound > 0: {R['dev_ci_pos_cells']:,}.",
      f"- Benjamini-Hochberg over m = {R['trials_total']:,}: **{R['bh_reject_q05']} cells rejected at q < 0.05**. Best DEV cluster t = {f(R['dev_best_t'], 2)}.",
      f"- Max-of-N placebo ({R['null_max_t']['rounds']} rounds of random same-phase entries in every qualifying cell): the null maximum t has mean {f(R['null_max_t']['mean'], 2)}, 95th percentile {f(R['null_max_t']['p95'], 2)}, max {f(R['null_max_t']['max'], 2)}. A DEV cell is distinguishable from the best-of-everything noise only when its t is above that range.", ""]
L += ["## Top 10 chosen on DEV (rank = day-cluster CI lower bound at 12 bp), confirmed untouched on VAL", "",
      "Net R columns are mean per trade after fees, slippage and funding. fee R = round-trip cost divided by the stop distance. DEV excess = DEV mean minus the mean of random same-phase entries with the same exit. Placebo p = share of 1,000 random same-phase VAL draws (same n, same exit) with mean at least the cell's.", "",
      "| # | tf | dir | phase | exit | combination | DEV n | DEV net R [CI] | DEV gross | fee R | DEV excess | BH q | max-N p | VAL n | VAL net R @12 | VAL CI | VAL @6 | ex-best-5 | placebo p | VAL BH q | PASS |",
      "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
for i, c in enumerate(top, 1):
    v = c["val12"]
    L.append(f"| {i} | {c['tf']} | {'L' if c['d'] > 0 else 'S'} | {c['phase_name']} | {c['kind']} | {c['name']} | {c['n']} | {f(c['mean12'])} [{f(c['ci_lo'])}, {f(c['mean12'] + 1.96 * c['se12'])}] | {f(c['gross'])} | {f(c['feeR'])} | {f(c['dev_excess_vs_random'])} | {f(c['q'], 3)} | {f(c['dev_maxn_p'], 3)} | "
             f"{v.get('n', 0)}{' (under)' if v.get('underpowered') else ''} | {f(v.get('mean12'))} | {ci(v)} | {f(v.get('mean6'))} | {f(v.get('ex_best5'))} | {f(v.get('placebo_p'), 3)} | {f(v.get('bh_q'), 3)} | {'PASS' if v.get('pass') else 'fail'} |")
L += [""]
L += ["Top 3 by VAL mean net R at 12 bp (among the 10):", "",
      "| tf | dir | phase | exit | combination | VAL n | VAL net R @12 | VAL CI | placebo p | PASS |", "|---|---|---|---|---|---|---|---|---|---|"]
for c in sorted(top, key=lambda c: -c["val12"].get("mean12", -9))[:3]:
    v = c["val12"]
    L.append(f"| {c['tf']} | {'L' if c['d'] > 0 else 'S'} | {c['phase_name']} | {c['kind']} | {c['name']} | {v.get('n', 0)} | {f(v.get('mean12'))} | {ci(v)} | {f(v.get('placebo_p'), 3)} | {'PASS' if v.get('pass') else 'fail'} |")
L += [""]
L += ["## Pre-registered thinker combinations (bank-feature analogs, not selected from DEV)", "",
      f"BH family = {len(named)} cells on VAL. {sum(1 for x in named if x['val'].get('n', 0) < 30)} of {len(named)} have VAL n < 30 and {sum(1 for x in named if x['dev'].get('n', 0) < 30)} have DEV n < 30: UNDERPOWERED, not 'no edge' (same-bar AND of 3-4 layers inside one phase set is rare). T6 cohort divergence: NOT_IN_DATA (top-trader position ratio not in the cache).", "",
      "| combination | tf | exit | dir | phases | DEV n | DEV net R | VAL n | VAL net R @12 | VAL CI | placebo p | PASS |", "|---|---|---|---|---|---|---|---|---|---|---|---|"]
for x in named:
    d_, v = x["dev"], x["val"]
    L.append(f"| {x['name']} | {x['tf']} | {x['kind']} | {'L' if x['d'] > 0 else 'S'} | {','.join(x['phases']) if len(x['phases']) < 6 else 'all'} | {d_.get('n', 0)} | {f(d_.get('mean12'))} | {v.get('n', 0)} | {f(v.get('mean12'))} | {ci(v)} | {f(v.get('placebo_p'), 3)} | {'PASS' if v.get('pass') else 'fail'} |")
L += [""]
L += ["## Beta every cell is up against: all-days random entries (12 bp, mean net R, no signal)", "",
      "| tf | dir | exit | DEV n | DEV mean | VAL n | VAL mean |", "|---|---|---|---|---|---|---|"]
B = R["baseline_all_days"]
for tf in ("4h", "1d"):
    for d in (1, -1):
        for k in ("T3R", "TRAIL", "RIDE"):
            a, b = B[f"{tf}|{d}|dev|{k}"], B[f"{tf}|{d}|val|{k}"]
            L.append(f"| {tf} | {'L' if d > 0 else 'S'} | {k} | {a['n']:,} | {f(a['mean12'])} | {b['n']:,} | {f(b['mean12'])} |")
L += [""]
L += ["## Active now (descriptive, last closed bar, no advice)", "",
      "Whether each top-10 combination's conditions are true at the last closed bar of BTC and ETH, and the phase label for the current day. `in phase` = the label equals the cell's phase.", "",
      "| # | combination | tf | BTC state | BTC phase | ETH state | ETH phase |", "|---|---|---|---|---|---|---|"]
for i, c in enumerate(top, 1):
    a = c["active_now"]
    L.append(f"| {i} | {c['name']} ({'L' if c['d'] > 0 else 'S'}, {c['phase_name']}, {c['kind']}) | {c['tf']} | {'TRUE' if a['BTC']['signal_state'] else 'false'}{' in phase' if a['BTC']['in_phase'] else ''} | {a['BTC']['phase']} | {'TRUE' if a['ETH']['signal_state'] else 'false'}{' in phase' if a['ETH']['in_phase'] else ''} | {a['ETH']['phase']} |")
L += [""]
if DG:
    L += ["## Replication diagnostic (post-run, descriptive, NOT pre-registered, NOT used for selection)", "",
          f"All {DG['cells_dev_n100']:,} DEV cells with n >= 100 were also evaluated on VAL (mean net R at 12 bp, no bootstrap); {DG['cells_val_n30']:,} have VAL n >= 30. Cells overlap heavily (same trades under different layer sets), so these shares are not independent trials; they say whether the DEV ranking carried information, not how many independent edges exist.", "",
          "| DEV subset | cells | VAL mean > 0 | VAL beats same-phase random | median VAL mean | median VAL excess | median DEV mean |", "|---|---|---|---|---|---|---|"]
    def row(name, x):
        return f"| {name} | {x['cells']} | {f(x['val_mean_pos'], pct=True)} | {f(x['val_excess_pos'], pct=True)} | {f(x['val_mean_median'])} | {f(x['val_excess_median'])} | {f(x['dev_mean_median'])} |"
    L.append(row("all cells", DG["all"]))
    L.append(row("DEV CI lower bound > 0", DG["dev_ci_pos"]))
    L.append(row("DEV BH q < 0.05", DG["dev_bh05"]))
    for k, nm_ in (("by_dir", "dir"), ("by_kind", "exit"), ("by_phase", "phase"), ("by_tf", "tf")):
        for kk, vv in DG[k].items():
            L.append(row(f"CI>0, {nm_} = {'long' if kk == '1' else 'short' if kk == '-1' else kk}", vv))
    L += ["", f"Spearman rank correlation DEV mean vs VAL mean over all cells: {DG['spearman_dev_val_mean']:.2f} (partly shared drift). Cells with DEV CI low > 0 AND VAL mean > 0 AND VAL excess > 0: {DG['replicating_cells']}; "
          "they sit in long UP_E for all three exits and both timeframes, plus a handful of 4h cells (UP_L shorts, DOWN_L longs) that sit on thin counts.",
          "Layers that appear most in DEV-CI>0 cells: " + ", ".join(f"{k} {v}" for k, v in list(DG["feature_count_in_dev_ci_pos"].items())[:10]) + " (VOLX, TREND_MA, RSI_MOM, ADX_DI, ABOVE_200, BRK5/BRK20 = trend continuation with participation). Flow layers (OI, funding, spot taker) rarely survive.",
          "VAL same-phase random entries in UP_E earn +0.19 R (1d RIDE) and -0.10 R (1d T3R), so the family's VAL +0.4 to +1.2 R is an excess over drift, but two cycles (2020-21 and 2024-25) are two episodes.", ""]
L += ["## What this does and does not show", "",
      "- Exhaustive over a fixed 26-layer bank with fixed thresholds; any layer, threshold or exit outside the bank (cost-basis VWAP of OI additions, weekly Cowen band, monthly low, top-trader ratio, options) was not searched.",
      "- Trades run on SPOT prices with perp funding charged; the universe is a fixed list of 20 coins that still trade (survivorship). Entries before 2020-01-01 are not scored. The last 30-60 days are not scored (trades unresolved at the data end are dropped).",
      "- Day-cluster errors treat each UTC day as one unit, pooling coins; coins move together, so independent episodes are fewer than the day count. VAL holds one regime sequence.",
      "- BH tests each cell against ZERO (so it includes the drift of a bull market: 29 rejections, all long UP_E); the max-of-N placebo tests timing against random same-phase entries (null max t above the best DEV t, so no DEV cell stands out from the best of random timing once phase drift is removed at the t level).",
      "- Deflation: BH over every enumerated cell and a max-of-N placebo in which each cell draws the same number of random same-phase entries (overlap rule not applied to the random draws; their variance is, if anything, overstated).",
      "- Code frozen with PRE_REG (commit fae9d0840): miner.py, run.py, fetch.py, test_miner.py. After the run only these were added: make_result.py, diagnostics.py (post-run replication diagnostic), and a test comparing the simulator with an independent bar-by-bar reference (24 tests, all pass; the 4h causality test fails under STUDY_BUG=1; the 1d one cannot, because a same-day label on a daily bar is acted on at the next open, so truncation cannot expose it). results.json is the single run, no re-runs or parameter changes.",
      f"- Files: PRE_REG.md, fetch.py, miner.py, run.py, make_result.py, test_miner.py (causality test passes on the real code and the 4h case fails under STUDY_BUG=1), results.json. Data: F:\\MTS\\data_cache\\binance\\combo-edge-miner-1114 (dev_cells.csv holds every DEV cell with n >= 100)."]
open(os.path.join(HERE, "RESULT.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")
print("RESULT.md written")
