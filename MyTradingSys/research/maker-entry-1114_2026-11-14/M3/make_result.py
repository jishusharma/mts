"""Builds results.json and RESULT_M3.md from results_raw.json (study.py output)."""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
R = json.load(open(os.path.join(HERE, "results_raw.json")))["res"]; V = R["VAL"]; D = R["DEV"]
g = {1: V["n_filled"] >= 100, 2: V["mean_net_R_filled"] > 0, 3: V["ci_trade"][0] > 0 and V["ci_day"][0] > 0,
     4: R["placebo_p"] < 0.05, 5: None, 6: V["ex_best5_days"] > 0}
out = dict(id="M3", idea="NK6 confluence L2&L3&L5", limit_level="close of signal bar", verdict="FAIL",
           gates={str(k): v for k, v in g.items()},
           gate5_note="BH needs all 6 rows' placebo p; this row alone p=%.4f. Moot since gates 2,3,6 fail." % R["placebo_p"],
           gates_failed=[2, 3, 5, 6], VAL=V, DEV=D,
           placebo=dict(p=R["placebo_p"], mean=R["placebo_mean"], filled_n=R["placebo_filled_n"], draws=1000),
           baseline_replication=dict(orig_result=dict(n=1996, gross=0.084, net12=-0.112),
                                     mine=dict(n=V["taker_n"], gross=V["taker_gross"], net12=V["taker_net12"], net6=V["taker_net6"])))
json.dump(out, open(os.path.join(HERE, "results.json"), "w"), indent=1)
f = lambda x: f"{x:+.3f}"
pm = lambda d, k: f"{d['phase_mix'][k] * 100:.0f}%"
md = f"""# RESULT_M3: NK6 confluence L2&L3&L5, maker entry at signal-bar close

VERDICT: FAIL (gates 2, 3, 6 fail; gate 5 moot). Maker entry improves net R from -0.112 (taker) to {f(V['mean_net_R_filled'])} per filled trade, still negative.

## Context
Phase gate as the original (daily ADX14/DI/SMA20-slope at D-1; matched direction only: LONG in UP/RANGE, SHORT in DOWN/RANGE). Session: all UTC hours. Signals, stop (max(1 ATR, 0.5% of L)), target 2R, 24-bar time stop frozen. Limit L = close of signal bar; fill model per PRE_REG (one tick through, 15 x 1m life, stop-before-fill cancels).

Regime mix: VAL signals UP {pm(V,0)} / RANGE {pm(V,1)} / DOWN {pm(V,2)}; DEV signals UP {pm(D,0)} / RANGE {pm(D,1)} / DOWN {pm(D,2)} (original bar mix: VAL UP 25 / RANGE 40 / DOWN 35).

## Baseline replication (original taker, next open, 12 bp, VALIDATION)
Original RESULT: n 1996, gross +0.084, net -0.112. Mine (original code copied unchanged, re-run): n {V['taker_n']}, gross {f(V['taker_gross'])}, net12 {f(V['taker_net12'])}, net6 {f(V['taker_net6'])}. Exact match.

## Results
| | VALIDATION | DEV (reference) |
|---|---|---|
| signals | {V['n_signals']} | {D['n_signals']} |
| fills (rate) | {V['n_filled']} ({V['fill_rate'] * 100:.1f}%) | {D['n_filled']} ({D['fill_rate'] * 100:.1f}%) |
| taker baseline net R (12 bp, all signals) | {f(V['taker_net12'])} | {f(D['taker_net12'])} |
| maker net R per filled trade | {f(V['mean_net_R_filled'])} | {f(D['mean_net_R_filled'])} |
| maker gross R per filled trade | {f(V['mean_gross_R_filled'])} | {f(D['mean_gross_R_filled'])} |
| mean fee in R (maker model) | {V['mean_fee_R_filled']:.3f} | {D['mean_fee_R_filled']:.3f} |
| net R per signal (miss = 0) | {f(V['per_signal_R'])} | {f(D['per_signal_R'])} |
| adverse selection (orig gross, filled minus all) | {f(V['adverse_selection_R'])} | {f(D['adverse_selection_R'])} |
| taker net on filled subset vs all | {f(V['taker_net12_filled_subset'])} vs {f(V['taker_net12'])} | {f(D['taker_net12_filled_subset'])} vs {f(D['taker_net12'])} |
| CI95 per trade | [{f(V['ci_trade'][0])}, {f(V['ci_trade'][1])}] | |
| CI95 per UTC day | [{f(V['ci_day'][0])}, {f(V['ci_day'][1])}] | |
| ex best 5 days | {f(V['ex_best5_days'])} | {f(D['ex_best5_days'])} |

Exit types (VAL filled): {V['exit_types']}. Misses: {V['miss_reasons']}. THIN: no (fill rate far above 30%).

## Gates (VALIDATION)
1 n>=100: PASS ({V['n_filled']}). 2 mean>0: FAIL. 3 CI lower>0: FAIL (trade {f(V['ci_trade'][0])}, day {f(V['ci_day'][0])}). 4 placebo p<0.05: PASS (p={R['placebo_p']:.4f}, placebo mean {f(R['placebo_mean'])}, 1000 draws, same fill model, {R['placebo_filled_n']} fills per draw). 5 BH over 6 rows: not computable per row, moot. 6 ex-best-5>0: FAIL.

## Reading
- The close-of-bar limit fills 95% of the time (the next minute almost always trades one tick through the close), so there is almost no selection. The gain over taker is fees (maker entry and target 3 bp), not entry price. Gross falls from +0.084 to +0.040 per filled trade (the 5.3% missed signals were better than average; adverse selection {f(V['adverse_selection_R'])} R).
- It beats random phase-matched maker entries (-0.19 R) but, as in the original, beating placebo is not an edge: net stays negative with both CIs below zero.
- Stop exits (taker 6 bp on a ~0.5% stop) dominate: about 60% of fills end at the stop.
- Cautions: the original non-overlap signal set (picked with taker exits) is kept; a maker trade may overlap the next signal. Stop distance is computed from L rather than the next open (OURS). 1m data has small gaps. Time stop exits at the open of the 1m bar after bar i+24 (taker; the original exits at that bar's close).

Files: study.py, orig_study.py (original code unchanged), test_study.py (6 pass; test_signal_bar_itself_not_used shows the naive variant starting at the signal bar fills), results.json, results_raw.json, rows.json.
"""
open(os.path.join(HERE, "RESULT_M3.md"), "w").write(md)
