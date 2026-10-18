# PRE-REGISTRATION: context factors as filters on the operator's stop-ladder trade at a level, BTCUSDT 1m, DEV (frozen 2026-10-16)

Session: Fable 5.1 (worktree branch `claude/context-factors-backtesting-1a25f2`, claim `context-factors`). Docs, counts and one
card only; no outcome column exists in this folder. The commit that adds this file precedes the commit that adds any result;
`git log` is the proof (convention of `research/gross_effect_screen_2026-10-15/PRE_REG.md:4`). Status: EXPLORATORY TRIAL.
Nothing here adopts a rule.

Why: the operator (chat 2026-10-16) says everything is "the probability of what happens when ..." a context holds, and that it
"can be measured in the past historical data". `CONTEXT_FACTORS_SPEC.md` defines seven context factors point-in-time and
`ANGLES.md` proves the builder. This file freezes the one run that asks, per factor and side, whether the factor changes the
outcome of the operator's own trade (stop below the prior candle, fixed R target) at a side-aware level, against controls that
share the market context (`research/context_null_2026-10-16/context_null.py`).

Labels: SOURCED = file:line or operator quote; OURS = our judgement. DECISION (OURS) marks a default taken because the repo had
no answer; the conservative reading was chosen each time.

## 0. Zero-judgement contract for the executing session (lane SONNET)
- Read sections 1-8 and run them as written. A missing number BLOCKS the run with the item named; do not choose one.
- One run. No parameter changes after the first outcome is read. Every cell in section 3 is computed and printed, verdict or not.
- Bars dated 2024-07-01 or later are never opened for an outcome (`context_asof.load_dev` and `context_null.run` both refuse
  them). Do not read other studies' `RESULT.md` for numbers.
- The episode ledger (section 5) is written, committed and its row counts compared with `EPISODE_COUNTS.md` BEFORE any
  outcome is computed. A count that differs from `EPISODE_COUNTS.md` by more than 0 is a BLOCK (the grid is deterministic).
- `context_null.run` gets ONE optional argument `outcome=` (a per-bar array that replaces its internal close-to-close `fwd`);
  with `outcome=None` the function must reproduce its current test numbers (`test_context_null.py` unchanged and green). No
  other change to `context_null.py`. Nothing is written in `research/pit_levels_2026-10-16/`.
- CI RED on `STATUS.md:6` (oldest ungreen commit 86ee2701, 3.2 h) at the time of writing: a stale note as in the gross screen
  (`PRE_REG.md:19`); DECISION (OURS): no CI work in this study, the executing card checks `gh run list --branch fast-track` first.

## 1. Economic target
| Item | Value | Label |
|---|---|---|
| Venue, instrument, bars | Binance USD-M BTCUSDT perpetual, 1m klines on disk (`F:/MTS/data/tom_raw/klines`), UTC; research target only, Deribit execution check separate | SOURCED (`gross_effect_screen_2026-10-15/PRE_REG.md:23-26`) |
| Decision grid | every 1h close of DEV (`t % 60 == 59`), features = `context_at(bars, t, side)` (both builds agree, `compare_result.txt`) | SOURCED (this folder) |
| Entry | market at `open[t+1]` (the next 1m bar) | DECISION (OURS); same as `gross_effect_screen` d = 1 |
| Stop | the ladder stop of the episode row: long = low of the rung candle (1d, else 12h, else 8h; `CONTEXT_FACTORS_SPEC.md` F3), short = its high | SOURCED (operator: "the stop would be below the previous daily candle ... refined for 12 hours or 8 hours") |
| Risk R | `abs(entry - stop)`; an episode whose `open[t+1]` is already at or beyond the stop is DROPPED (counted, not traded) | DECISION (OURS) |
| Target | entry + 1.5 R (long) / entry - 1.5 R (short), fixed | DECISION (OURS); TARGET_R 1.5 as in `COUNTS.md` section 0 |
| Exit rule on 1m bars after the fill bar | a bar whose low <= stop (long) is a stop exit at `min(open, stop)`; a bar whose high >= target is a target exit at the target; a bar that touches both is a STOP (conservative). Fill bar: stop only (`backtest/tom_bt.py:205-208`) | SOURCED gap rule (`tom_bt.py:207`), both-touched = stop DECISION (OURS) |
| Max hold | 1440 bars (24 h) after the fill, then exit at that bar's close | DECISION (OURS) |
| Gross outcome | `gross_r = sgn x (exit - entry) / R` | arithmetic |
| Cost | all-taker round trip 0.14 % of entry: `cost_r = 0.14 / stop_pct` with `stop_pct = R / entry x 100`; maker-in readout 0.09 % reported beside it, never a verdict | SOURCED (`backtest/research_kit.py:21-22`, `TOM_LAYER_V2_SPEC.md:331-332` rule) |
| Net outcome | `net_r = gross_r - cost_r` (reported; the verdicts below are on the cost-free contrast, section 4) | arithmetic |
| Funding | a 24 h hold straddles up to 3 settlements; the realised rate from `F:/MTS/Dumps/backtest/raw/fundingRate` (on disk for DEV, `context_asof.load_funding`) is added to the cost of the straddling trade in R (long pays a positive rate) | DECISION (OURS) |
| Size, turnover | one unit of R per trade; trades may overlap (episodes are first touches of distinct levels, ~1.8 per side per day); SE is day-clustered, never i.i.d. | DECISION (OURS) |

## 2. Outcome function and the per-bar outcome arrays
`outcome.py: ladder_outcome(bars, t, side, row) -> dict(gross_r, net_r, cost_r, reason, bars_held, dropped)` with `row` = the
grid row's `ladder_rung`, `ladder_stop_pct` and the rung candle's low/high (recomputed from `context_at`, never read from the
csv). `Y_side[t]` = `gross_r` at grid bars where an outcome is defined, NaN elsewhere (off-grid bars, dropped episodes, the last
1441 bars of DEV). Test (`test_outcome.py`, must fail on a stubbed function first): a 10-day synthetic tape with hand-written
numbers for a stop exit with a gap, a target exit, a both-touched bar, a time exit and a dropped entry.

## 3. Contrasts (one verdict per factor per side; frozen now; counts from `EPISODE_COUNTS.md`, no outcome read)
Episode = grid row with `at_level`, `first_touch`, `ladder_rung != none`, `ladder_below_floor == False`. The contrast's arm =
episodes where the factor condition holds; the pre-declared direction is the operator's reading (section 0 of
`CONTEXT_FACTORS_SPEC.md` quotes). n_min = 572 (section 4).

| cell | factor condition on the episode | direction | long n (2022/2023/2024H1) | short n | verdict possible now? |
|---|---|---|---|---|---|
| F1 | every episode (being at a side-aware level with a first touch) | + | 1636 (646/696/294) | 1651 (681/646/324) | yes / yes |
| F2 | `n_layers >= 2` | + | 1305 (520/538/247) | 1307 (540/487/280) | yes / yes |
| F3 | `ladder_cond` (close past the prior daily open in the trade direction) | + | 965 (346/428/191) | 965 (416/374/175) | yes / yes |
| F4 | last closed 4h pattern with the trade (bull_engulf or bull_pin for longs, bear_* for shorts) | + | 261 (106/92/63) | 287 (110/119/58) | INCONCLUSIVE by count / same |
| F5 | long: `bb_long_conf` (4h re-entry from below the lower band); short: `bb_short_veto_walk` (4h walk down) | + / - (veto) | 36 (13/17/6) | 40 (23/13/4) | INCONCLUSIVE by count / same |
| F6 | `phase_a == markup` (long) / `markdown` (short) | + | 578 (177/291/110) | 382 (177/179/26) | yes / INCONCLUSIVE by count |
| F7 | `htf_align` (weekly close vs 4 weeks earlier with the trade) | + | 885 (184/494/207) | 667 (379/178/110) | yes / yes |

Nine cells can reach a verdict; the five below n_min are computed and printed with their MDE and keep the word INCONCLUSIVE
whatever the number says. No other field, pair or threshold gets a verdict; `COUNTS.md` pairs and the other F7 fields
(`vol_regime`, `squeeze`, `session`, `weekend`, `approach`, `sweep`, `funding`) are printed as descriptive rows, no verdict.
Trials T1-T8 (`trials.csv`) were decided by reason before this file; their alternatives are not run.

## 4. Statistics and pass/fail (fixed now; DEV only)
- Control: `context_null.run(C, events, h=1439, d=1, cfg=Config(seed=20261016, K=20), level=lvl, outcome=Y_side)` per cell and
  side; `W = d + h = 1440` = the max hold, so no control window overlaps an event window; matching keys hour, vol, trend (the
  module's own, all trailing) plus `lvl` = the episode's nearest-level source index 1..9 at grid rows with `at_level`, 0 at
  other grid rows, -1 off-grid. For F1 `lvl` = 0 at every grid row (controls = grid rows not at a level, same hour/vol/trend);
  for F2-F7 controls are grid rows at the same kind of level, whatever the factor says there.
- Effect = `trigger_effect` (mean over matched episodes of event outcome minus its controls' mean outcome, in R), SE
  day-clustered (`screen.cluster_mean_se`), `t = effect / SE`, two-sided normal p. The cost cancels in this contrast (both
  arms pay the same ladder cost), so the power rule uses cost = 0:
  `power_check(n, sd=1.25 x sqrt(1 + 1/20), plausible=0.15, cost=0)` -> MDE = 2.8 x 1.2808 / sqrt(n) <= 0.15 R iff
  n >= 572 (`EPISODE_COUNTS.md`; sd bound = the largest SD of a -1 / +1.5 outcome; 0.15 R plausible = OURS).
- Holm: m = 14 (`verdicts.py count --split DEV`, pasted in section 9) + 8 (`trials.csv`) + 14 (these cells) = 36;
  `research_kit.holm(p, m=36)`.
- **PASS** iff `n_matched >= 572` and Holm-adjusted p <= 0.05 and the sign equals the pre-declared direction and the
  sub-period effects (same rows split 2022 / 2023 / 2024H1) all carry that sign.
- **INCONCLUSIVE** iff `n_matched < 572`; MDE printed; never relabelled.
- **FAIL** otherwise. Kill scope of a FAIL: "factor X as a FILTER on the ladder trade at a side-aware level, 1h grid, BTCUSDT 1m,
  outcome of section 1". It does not kill the factor as a setup, as a level source, in any other outcome definition, or any
  prior study's family (section 9 and `ANGLES.md` prior-verdict review).
- Secondary rows, no verdict: `event_mean`, `control_mean`, `context_effect`, net R of the arm (`event net_r` mean), maker-in
  net, dropped count, funding cost mean, `n_controls_mean`, `control_reuse`. A net-positive claim for any arm would need
  `power_check(n, 1.25, 0.15, cost=0.105)` -> n >= 5943 (`COUNTS.md` section 0); no cell has it, so this run makes NO net
  claim. REFUSAL RULE applied now: the net question is not pre-registered; it waits for VALIDATION + more DEV-like data.

## 5. Episode ledger (written before any outcome)
`episodes.csv`: t, utc_close, side, near_src, ladder_rung, ladder_stop_pct, ladder_cost_r, and one boolean per cell F2-F7
(F1 = every row). Counts per cell, side and period must equal `EPISODE_COUNTS.md`. No outcome column. Committed with the
message `context-factors: episode ledger (no outcome)` before `outcome.py` runs.

## 6. Data split
- DEV: bar open 2022-01-01 .. 2024-06-30 (`PRE_REG_VOLUME_2026-10-09.md:23` standard split). The first 70 days carry
  warm-up (`PCT_WIN` 180 closed 4h bars = 30 days; weekly trend 4 weeks); episodes before day 70 are dropped and counted.
- VALIDATION 2024-07-01 .. 2025-06-30: read once, later, by a separate card, only for cells that PASS here, this file unchanged.
- HOLDOUT 2025-07-01 ..: sealed; opening it needs the operator (`TOM_ON_BTC.md:124`).

## 7. Known traps (each one is a check in the script or a test)
1. The prior candle at a bucket close (RT-1): `PRIOR_RULE = "last_closed"` in both builds, `test_rt1_day_close_grid_uses_the_day_that_just_closed`.
2. Stop from the partial day's low: plant `ladder_final_day` caught; the ladder reads only closed candles.
3. Gap through the stop: fill at `min(open, stop)` (long), stop-only on the fill bar (`tom_bt.py:205-208`); test case in `test_outcome.py`.
4. Both target and stop inside one 1m bar: stop (conservative); test case.
5. Entry already beyond the stop: dropped, counted; test case.
6. Overlapping trades: day-clustered SE; controls never inside an event window (`context_null` forbid mask).
7. Week anchor Monday 00:00 UTC (RT-2): `test_bucket_convention`, hand check.
8. Full-sample percentiles: plant `pct_fullsample` caught; `context_null` vol cuts are trailing by construction.
9. Funding read before settlement: plant `funding_next` caught; `load_funding` keeps calc_time only.
10. Multiplicity: m = 36 in Holm, fixed here; no cell added later.
11. Power: n before outcomes (section 3); INCONCLUSIVE is separate from FAIL.
12. One-run: `context_null` is run once per cell; a re-run with any change is a new PRE_REG.

## 8. Outputs of the executing session
`outcome.py`, `test_outcome.py` (listed in `scripts/dev/run_extra_tests.py`), `episodes.csv`, `RESULT.md` (verdict table first:
cell, side, n_matched, effect R, SE, t, Holm p, sub-period signs, verdict; then the secondary rows; dropped and warm-up counts;
funding availability), the `context_null.py` one-argument change with its test, then `python scripts/dev/verdicts.py add` one
row per cell (14 rows), `lookahead_lint.py` clean, `run_all_tests.py --quick` green, `sync.py ship`. The result commit must come
after this file's commit.

## 9. Registry checks run before freezing (`python scripts/dev/verdicts.py check "<word>"`, 2026-10-16)
```
check 'context': no prior row matches (need 1 of ['conte']). Safe to pre-register; append your row after RESULT.
check 'level': 1 prior row(s) (match 1+ of ['level'])
        t087_session_levels_2026-10-09 | (study) | UNPARSED | ... | UNPARSED | one_run=no | 71df3aad 2026-10-09
check 'Bollinger': 1 prior row(s) (match 1+ of ['bolli'])
  BLOCK wlow_bounce_bbrsi60_2026-10-16 | EVENT (break+bounce+hold) | DEV | n=8 mean=-0.293 se=0.116 cost=0.14 | INCONCLUSIVE | one_run=yes | 8bc4b9fa 2026-10-16
        kill_scope: none
BLOCKED: a one_run PRE_REG may not be re-run and a FAIL kills its family. A new PRE_REG must say why it is a different hypothesis.
check 'candle': no prior row matches (need 1 of ['candl']). Safe to pre-register; append your row after RESULT.
check 'phase': no prior row matches (need 1 of ['phase']). Safe to pre-register; append your row after RESULT.
check 'stop': 2 prior row(s) (match 1+ of ['stop'])
  BLOCK gross_effect_screen_2026-10-15 | T | DEV | n=40 mean=-0.0568 se=0.1304 cost=0.14 | INCONCLUSIVE | one_run=yes | b42cef1b 2026-10-16
  BLOCK gross_effect_screen_2026-10-15 | C | DEV | n=1439 mean=-0.0081 se=0.0246 cost=0.14 | FAIL | one_run=yes | b42cef1b 2026-10-16
        kill_scope: FAIL means stop: no detector, chart, layer or management work on this hypothesis family (session-extreme fade with delta flow on 1m BTC) ...
BLOCKED: (same text)
check 'confluence': no prior row matches (need 1 of ['confl']). Safe to pre-register; append your row after RESULT.
```
Why this is a different hypothesis from the two BLOCKs: `wlow_bounce` (`VERDICTS.csv:21`) tests the weekly-low break + bounce +
RSI-60 hold SETUP; here the prior-week low is one of nine level sources and no bounce or RSI rule exists; its kill scope is
"none" and it is not re-run. `gross_effect_screen` (`VERDICTS.csv:4-5`) tests the session-extreme fade with delta flow; no
session extreme and no flow is used here; its row matches on the word "stop" in its kill-scope sentence only. Every cell here
is a context FILTER on the operator's ladder trade, a family no prior row names (`ANGLES.md`, family statement).
`verdicts.py count --split DEV` = 14.
