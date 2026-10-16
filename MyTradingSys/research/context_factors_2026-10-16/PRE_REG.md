# PRE-REGISTRATION: operator context composite vs a context-matched baseline, BTCUSDT 1h decisions with the daily-candle stop ladder (frozen 2026-10-16)

Session: context-factors (JIS-NUC worktree `jis-nuc/context-factors`, Opus 5.5). Template: `research/gross_effect_screen_2026-10-15/PRE_REG.md`.
The commit that adds this file precedes any commit that adds an outcome; `git log` is the proof. Status: EXPLORATORY TRIAL,
nothing here adopts a rule. Factor definitions: `CONTEXT_FACTORS_SPEC.md` and `context_asof.py` at this commit.
Counts behind every number below: `COUNTS.md`, `trials.csv`, `events_dev.csv` (no outcome column anywhere).

## 0. Zero-judgement contract for the executing session (lane SONNET)
- Run sections 2-6 as written. A missing number = BLOCKED with the item named; never choose one.
- One run. Only the cells marked READ in section 4 may have an outcome computed. Cells marked REFUSED_POWER must not be
  computed, printed or looked at: reading them burns them for a later, powered study.
- No bar with open >= 2024-07-01 for any input or outcome (the 24 h time stop of an event on 2024-06-30 is cut at
  2024-06-30 23:59; such trades exit at the last DEV 1m close and are counted in a `cut_at_split_end` line).
- Do not read other studies' RESULT.md for numbers.

## 1. Economic target
| item | value | label |
|---|---|---|
| venue, data | Binance USD-M BTCUSDT 1m archive (F:/MTS/data/tom_raw/klines), funding archive (F:/MTS/data/candle_close_dev_2022_2024) | SOURCED (study inputs, `context_asof.py` loaders) |
| cost per side | 5 bp taker fee + 2 bp slippage = 7 bp on entry and on exit (0.14 % round trip); maker-in readout 0.09 % (report only, never rescues a FAIL) | SOURCED gross_effect_screen PRE_REG s.1 |
| funding | realised 8h rate for every settlement inside the trade (long pays a positive rate), from the archive | SOURCED archive; OURS rule (same as the template) |
| unit | R = |entry - stop|; net_R = (sgn x (exit - entry) - 0.0007 x entry - 0.0007 x exit - funding x entry) / R | OURS (FORMULAS 18.5 form) |
| size | 1 unit per trade; trades of one side may overlap (day-clustered SE; overlap disclosed in s.7) | OURS |

## 2. Events, the composite, the trade
- **Decision hours**: every DEV 1h close T from 2022-04-01 to 2024-06-30 (`run_dev.py decisions`).
- **Ledger** (per side, `counts.py ledger`): f1_at_level, then a 4 h same-side cooldown, then f3_stop_tf != none.
  Counted before freezing: long 2,817 events / 769 days, short 2,781 / 754 (COUNTS.md).
- **Operator context composite C** (pre-specified from rules O1-O4 in CONTEXT_FACTORS_SPEC.md; no other combination is
  formed or read):
  - long: ledger event AND f2_conf_obj >= 2 (support confluence, O4) AND f3_armed (O1) AND NOT f5_veto (O3) AND
    f6_phaseA in {markup, accumulation} (O4 "the phase matters"; the direction mapping is OURS);
  - short: mirror (f6_phaseA in {markdown, distribution}).
  - Candle confidence (O2) is NOT in C: the operator says "some confidence", not a condition; it is a REFUSED_POWER cell.
  - Counted: long 554 events / 254 days, short 456 / 202, **pooled 1,010 events / 456 days**; by year 354 (2022 Apr-Dec),
    386 (2023), 270 (2024H1); median stop 2.11 %, median cost 0.066 R.
- **Trade at T** (events and controls alike): entry = open of the 1m bar that opens at T + 60 s (one-bar latency,
  template s.3.2). Stop = the ladder stop price of `f3_stop_tf` (prior D / 12h / 8h low for a long, high for a short),
  fixed at T. If the entry is already beyond the stop: skipped, counted `entry_beyond_stop`. Target = entry + 2 R (long),
  mirrored. Exit on 1m bars from the entry bar on: stop first when one bar holds both; a bar that opens beyond the stop
  fills at its open (template trap 1: fill = min(open, stop) long, max short); else target; else time stop at the close
  of the 1m bar ending entry + 24 h. Target and time stop are OURS (2 R: the fixed R target the operator asked for;
  24 h: keeps one trade inside about one day cluster).

## 3. Control arm: context-matched baseline
Control arm: context-null (`MyTradingSys/research/context_null_2026-10-16/context_null.py`, keys from its `context_key`),
keys hour + vol tercile + trend tag on the 1h close array (`Config(bar_min=60, cooldown=4, seed=0)`, K = 20, kmin = 10).
Pool: ledger events of the same side that are NOT in C, not within 24 h of any C event of that side. Each control gets
the same trade (its own ladder stop at its own T'). `context_null.run` computes only fixed-horizon returns, so the
executing session draws the controls with `context_key` and the same rules (same key, K without replacement, seed 0) and
computes net_R per control with the trade above; it does not edit context_null.py.
- **Trigger effect E** = mean over matched C events of (event net_R - mean net_R of its controls). SE day-clustered
  (`research_kit.cluster_mean_se`, day = UTC day of T). The context-only line (control mean minus all-ledger mean) is printed,
  never a gate.
- Note: phase B and f7_session / f7_volreg collide with the null's own keys (trend, hour, vol); they are not part of C.

## 4. Cells and verdicts (one per factor per side; decided by the count gate before any outcome)
Power gate (E1 of FABLE_RUNS_AUDIT): `n_needed = ((z_holm + 0.8416) x sd / (plausible - cost))^2`, sd = 1.5 R
(COUNTS.md: break-even 1R/2R trade sd 1.41 R, rounded up), cost = median cost in R of the cell, units = UTC days.
Holm m = **37** = 14 (`verdicts.py count --split DEV`) + 6 (rows it reports as split UNPARSED, counted to be safe) + 16
(distinct factor x definition rows in trials.csv) + 1 (this composite). z_holm = 3.205 (two-sided 0.05 / 37).

| cell | plausible effect | n_needed (days) | days available | verdict now |
|---|---|---|---|---|
| **C pooled (long + sign-flipped short)** | **0.375 R** | **387** | **456** | **READ** (MDE 0.284 R + cost 0.066 R = 0.351 R <= 0.375 R) |
| C long only | 0.375 R | 387 | 254 | REFUSED_POWER |
| C short only | 0.375 R | 387 | 202 | REFUSED_POWER |
| every single factor value, each side (F1-F7, 24 factors, 86 values) | 0.20 R | 1,242 at m = 1 (2,064 at m = 37) | largest bucket 768 (f5_veto False, long); every bucket in COUNTS.md is LOW | REFUSED_POWER |

Plausible effects (OURS): 0.20 R for one context filter = about a quarter of the best SOURCED whole-setup expectancy
(+0.75 R gross, CATALOGUE T-3 via FABLE_RUNS_AUDIT 3.2), set in `counts.py` before any count was printed. 0.375 R for
the whole composite = half of that expectancy; **this number was written after the counts were seen** (counts only, no
outcome). Sensitivity: at 0.35 R n_needed = 458 (> 456, refuse); at 0.30 R 675. So C is powered only if the operator's
whole context is worth at least about 0.35 R per trade before the trigger. If the operator thinks less, C is REFUSED_POWER
too and this PRE_REG has nothing to read.

Per factor and side (largest bucket in distinct days, long | short; all < 1,242): f1_near_layer 478 | 498; f2_conf_obj 614 |
609; f2_touch_cat 612 | 619; f3_armed 524 | 510; f3_stop_tf 698 | 707; f4_D/12h/8h/4h_align 507-710 | 497-690; f5_1h 754 | 735;
f5_4h 727 | 715; f5_veto, f5_conf 768 | 752; f6_phaseA 353 | 343; f6_phaseB 280 | 267; f6_intraday 721 | 723; f7_volreg
457 | 467; f7_squeeze 642 | 623; f7_session 683 | 664; f7_weekend 571 | 568; f7_approach 702 | 694; f7_sweep 721 | 713;
f7_htf_align 363 | 355; f7_funding 433 | 435. DEV has 821 decision days in total, so no single-factor cell can reach
1,242 on DEV.

**Verdict rule for the READ cell (C pooled)**:
- **PASS** iff matched days >= 387 AND E > 0 AND Holm-adjusted p <= 0.05 (two-sided p <= 0.05 / 37, |t| >= 3.205) AND
  mean net_R of C > 0 (all-taker, after funding) AND E > 0 in each of 2022 (Apr-Dec), 2023 and 2024H1 AND the max
  drawdown of cumulative net_R of C (sum, in R) <= that of the matched controls' mean path.
- **INCONCLUSIVE** iff matched days < 387 (MDE printed; never relabelled FAIL).
- **FAIL** otherwise.
- Printed beside it, no verdict: E per side, maker-in readout, week-clustered SE of E (overlap check), the counts of
  skipped trades (entry beyond stop, no controls, cut at split end), exit mix (stop / target / time).

## 5. Ledger, exposure, kill scope
- `ledger_C.csv` (T, side, stop_tf, stop, entry, exit, exit kind, net_R, matched control T's) and `controls.csv`.
- `EXPOSURE_LEDGER.csv` row: study, run_utc, data_source, window_read (DEV 2022-04-01..2024-06-30), split DEV,
  rule_sha256 of this file at the run commit, verdict, decision_informed.
- After RESULT: `verdicts.py add` one row for C pooled, with kill_scope as below.
- **Kill scope of a FAIL**: only the composite C exactly as defined at this commit (1h decisions, these layers, the D/12h/8h
  ladder, 2 R target, 24 h time stop). It does NOT park any single factor, any trader's setup, Tom, Fabio, Krown or any
  layer. It does not overlap the prior one-run studies (ANGLES.md, prior-verdict review): they tested trigger setups
  (5m midline engulf, 1h BB-mid touch, weekly-low/round sweep within 5 min, prior-week-low bounce, RSI divergence,
  1m session-extreme fade) at fixed horizons; C is a context filter on a stop-ladder trade and contains none of those triggers.

## 6. Data split
DEV only (bar open 2022-01-01 .. 2024-06-30; decisions from 2022-04-01). VALIDATION (2024-07-01 .. 2025-06-30) is read
once, later, by a separate card only after a PASS, with this file unchanged. HOLDOUT sealed (operator).

## 7. Known traps (checks in the executing script)
1. Gap through the stop: fill at the bar open (s.2). 2. Entry after T only (1m bar opening at T + 60 s). 3. Overlapping
trades: day-clustered SE understates the SE when one trade spans two days; the week-clustered SE is printed, and a
PASS with week-clustered |t| < 2 is reported as "PASS (day-clustered only)". 4. Controls in the same context as C by
construction: trend/hour/vol are matched, so phase-A's trend content is partly matched away (intended). 5. Composite
built from factor columns of `context_frame` at this commit; any change to `context_asof.py` after this commit voids the
run (check the sha). 6. Funding sign: long pays a positive rate.

## 8. Outputs of the executing session
`study.py`, `test_study.py` (trade simulator on a hand fixture: stop-first, gap fill, target, time stop, funding sign),
`ledger_C.csv`, `controls.csv`, `EXPOSURE_LEDGER.csv`, `RESULT.md` (verdict line first, then the READ-cell table, the
per-side and robustness rows, skipped counts). Verdict words: PASS | INCONCLUSIVE | FAIL; every other cell is listed
as REFUSED_POWER with its count.

## 9. `verdicts.py check` output at freeze (verbatim, also in VERDICTS_CHECK.txt)
The BLOCK rows are one-run studies of different trigger families (s.5 kill scope); none is re-run here.

```
$ python scripts/dev/verdicts.py check "support resistance level"
check 'support resistance level': no prior row matches (need 2 of ['level', 'resis', 'suppo']). Safe to pre-register; append your row after RESULT.
(exit 0)
$ python scripts/dev/verdicts.py check "confluence layers"
check 'confluence layers': no prior row matches (need 2 of ['confl', 'layer']). Safe to pre-register; append your row after RESULT.
(exit 0)
$ python scripts/dev/verdicts.py check "daily candle stop"
check 'daily candle stop': no prior row matches (need 2 of ['candl', 'daily', 'stop']). Safe to pre-register; append your row after RESULT.
(exit 0)
$ python scripts/dev/verdicts.py check "candle pattern engulf"
check 'candle pattern engulf': no prior row matches (need 2 of ['candl', 'engul', 'patte']). Safe to pre-register; append your row after RESULT.
(exit 0)
$ python scripts/dev/verdicts.py check "bollinger band walk"
check 'bollinger band walk': 1 prior row(s) (match 2+ of ['band', 'bolli', 'walk'])
  BLOCK wlow_bounce_bbrsi60_2026-10-16 | EVENT (break+bounce+hold) | DEV | n=8 mean=-0.293 se=0.116 cost=0.14 | INCONCLUSIVE | one_run=yes | 8bc4b9fa 2026-10-16
        kill_scope: none
BLOCKED: a one_run PRE_REG may not be re-run and a FAIL kills its family. A new PRE_REG must say why it is a different hypothesis. (kill_scope UNPARSED = read the study's PRE_REG/RESULT for the scope.)
(exit 1)
$ python scripts/dev/verdicts.py check "bollinger lower band"
check 'bollinger lower band': 3 prior row(s) (match 2+ of ['band', 'bolli', 'lower'])
  BLOCK opr_bb_mtf_center_2026-10-16 | AU: touch bar closes above its mid, LONG, h=120 | DEV | n=194 mean=0.0196 se=0.0824 cost=0.14 | INCONCLUSIVE | one_run=yes | 1318ef9e 2026-10-16
        kill_scope: none
  BLOCK opr_bb_mtf_center_2026-10-16 | AD: touch bar closes below its mid, SHORT, h=120 | DEV | n=282 mean=0.0322 se=0.0397 cost=0.14 | FAIL | one_run=yes | 1318ef9e 2026-10-16
        kill_scope: UNPARSED
  BLOCK wlow_bounce_bbrsi60_2026-10-16 | EVENT (break+bounce+hold) | DEV | n=8 mean=-0.293 se=0.116 cost=0.14 | INCONCLUSIVE | one_run=yes | 8bc4b9fa 2026-10-16
        kill_scope: none
BLOCKED: a one_run PRE_REG may not be re-run and a FAIL kills its family. A new PRE_REG must say why it is a different hypothesis. (kill_scope UNPARSED = read the study's PRE_REG/RESULT for the scope.)
(exit 1)
$ python scripts/dev/verdicts.py check "phase regime trend"
check 'phase regime trend': no prior row matches (need 2 of ['phase', 'regim', 'trend']). Safe to pre-register; append your row after RESULT.
(exit 0)
$ python scripts/dev/verdicts.py check "session"
check 'session': 4 prior row(s) (match 1+ of ['sessi'])
        b154_stratified_2026-10-09 | (study) | UNPARSED | n=UNPARSED mean=UNPARSED se=UNPARSED cost=UNPARSED | UNPARSED | one_run=no | 7252ef97 2026-10-10
        kill_scope: UNPARSED
  BLOCK gross_effect_screen_2026-10-15 | T | DEV | n=40 mean=-0.0568 se=0.1304 cost=0.14 | INCONCLUSIVE | one_run=yes | b42cef1b 2026-10-16
        kill_scope: FAIL means stop: no detector, chart, layer or management work on this hypothesis family (session-extreme fade with delta flow on 1m BTC). Krown Q66-Q69 and Tom T5 (`TOM_ON_BTC.md:136`) stay parked for it.
  BLOCK gross_effect_screen_2026-10-15 | C | DEV | n=1439 mean=-0.0081 se=0.0246 cost=0.14 | FAIL | one_run=yes | b42cef1b 2026-10-16
        kill_scope: FAIL means stop: no detector, chart, layer or management work on this hypothesis family (session-extreme fade with delta flow on 1m BTC). Krown Q66-Q69 and Tom T5 (`TOM_ON_BTC.md:136`) stay parked for it. (derived)
        t087_session_levels_2026-10-09 | (study) | UNPARSED | n=UNPARSED mean=UNPARSED se=UNPARSED cost=UNPARSED | UNPARSED | one_run=no | 71df3aad 2026-10-09
        kill_scope: UNPARSED
BLOCKED: a one_run PRE_REG may not be re-run and a FAIL kills its family. A new PRE_REG must say why it is a different hypothesis. (kill_scope UNPARSED = read the study's PRE_REG/RESULT for the scope.)
(exit 1)
$ python scripts/dev/verdicts.py check "volatility squeeze"
check 'volatility squeeze': no prior row matches (need 2 of ['squee', 'volat']). Safe to pre-register; append your row after RESULT.
(exit 0)
$ python scripts/dev/verdicts.py check "sweep reclaim"
check 'sweep reclaim': 2 prior row(s) (match 2+ of ['recla', 'sweep'])
  BLOCK opr_weekly_low_round_sweep_2026-10-16 | RL: reclaim within 5 min, LONG at the reclaim close, h=60 | DEV | n=685 mean=0.0317 se=0.0335 cost=0.14 | FAIL | one_run=yes | 0584b035 2026-10-16
        kill_scope: UNPARSED
  BLOCK opr_weekly_low_round_sweep_2026-10-16 | AS: first three closes below, SHORT at the third close, h=60 | DEV | n=525 mean=-0.0389 se=0.0462 cost=0.14 | FAIL | one_run=yes | 0584b035 2026-10-16
        kill_scope: UNPARSED
BLOCKED: a one_run PRE_REG may not be re-run and a FAIL kills its family. A new PRE_REG must say why it is a different hypothesis. (kill_scope UNPARSED = read the study's PRE_REG/RESULT for the scope.)
(exit 1)
$ python scripts/dev/verdicts.py check "funding"
check 'funding': no prior row matches (need 1 of ['fundi']). Safe to pre-register; append your row after RESULT.
(exit 0)
$ python scripts/dev/verdicts.py check "weekend"
check 'weekend': no prior row matches (need 1 of ['weeke']). Safe to pre-register; append your row after RESULT.
(exit 0)
$ python scripts/dev/verdicts.py check "approach speed"
check 'approach speed': no prior row matches (need 2 of ['appro', 'speed']). Safe to pre-register; append your row after RESULT.
(exit 0)
$ python scripts/dev/verdicts.py check "context filter"
check 'context filter': no prior row matches (need 2 of ['conte', 'filte']). Safe to pre-register; append your row after RESULT.
(exit 0)
$ python scripts/dev/verdicts.py count --split DEV
# distinct variants (study, arm) read on DEV: 14 from 9 studies; 6 rows have split_read UNPARSED and are not counted; secondary cells and variant grids are not counted (lower bound for Holm m).
14
```
