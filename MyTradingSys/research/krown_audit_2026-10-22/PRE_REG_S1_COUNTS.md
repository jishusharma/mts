# PRE-REG: confluence-s1-context-counts (counts pass, no outcome read)
Written 2026-10-23 by Lab_Guy, BEFORE any S1 code runs or any result exists. S1 reads timestamps and context only. Outcome columns are
never opened (they go to `run/sealed/`). Parent: FABLE_CARD_CONFLUENCE.md s4 S1; amendments from REVIEW_OPUS.md.
Class C2 (defines the context object every later step reads), weight CRUCIAL. Nothing in this file is a result.

## 1. Findings the card must satisfy (each is a checked line in COUNTS.md)
| Finding | Requirement fixed now | Check (fails the card if absent) |
|---|---|---|
| F2 (day-level independence, year dummy, DEV only 912 days) | Inference unit = ISO week (or 20-day block). COUNTS.md reports per layer and cell: n events, distinct ISO weeks, and MDE with week clustering. Counts split into regime sets 2022 vs 2023-24H1, and DEV_EXT 2020-21 as a second set (DEV_EXT allowed at DEV stage, OPERATOR_DECISIONS.md:883,894). Same-sign-in-both-sets is stated as the later pass bar, not tested here. | COUNTS.md has columns n, iso_weeks, mde_week, set in {2022, 2023-24H1, DEV_EXT}; day-clustered MDE is shown only as a footnote |
| F3 (fee wall: cost/R is not edge) | The fee-wall metric is cost % / mean signed gross move %, never cost/R alone. S1 may only report the cost/R distribution as a feasibility filter (cost/R < 0.25, OURS; PROJECT_VISION economics line) and states in COUNTS.md that cost/R falling is not evidence of improvement. Mean gross move is NOT computed in S1 (it is an outcome); the column is reserved empty. | COUNTS.md header carries the sentence; no gross-move or R-outcome value appears |
| F8 (power not costed; shares assumed) | Real D1/D2/D3 shares and the S histogram are computed from data before any band is frozen. Cell sizes are compared with the review's expected shares (S=+3 about 1.6 %, S>=+2 about 12 %, S<=-2 about 13 %, OURS approximations). Per-layer verdict gate: MDE <= 0.10 R per S unit with week clustering, else DESCRIPTIVE; computed here, applied later. Bands for D2/D3 freeze from these counts only, with D3 coverage targets +1 = 15-30 % and -1 = 15-30 % of events (REVIEW_OPUS F10, OURS). | COUNTS.md has per-layer TESTABLE/DESCRIPTIVE flag and the frozen bands with the counts that fixed them; `prereg_gate.py` run for the pooled n |
| F12 (construct validity: OURS detectors failed recall, 3/12, 0 strict hits: RECALL.md:36) | Every context field is named and labelled "OURS impl. of KR-x" in code, CSV header and COUNTS.md. A naive trend baseline (close vs 200d SMA; sign of the 20d return) is a column of the context table so S3 can race D1 against it. | context_dev.csv has `naive_trend_sma200`, `naive_trend_ret20`; each Krown field name ends `_ours` or has a label row |

## 2. No-lookahead test (required, must fail on a leak)
`test_krown_context.py` contains, and `tasks.py done --result` must quote the red run of:
1. `test_shifted_join_leaks`: a deliberately leaking variant (join on bar open instead of `available_at < decision_ts`, or context row shifted
   by one bar forward) MUST make the point-in-time check fail (assert the check raises/returns FAIL on the leaking variant, passes on the real join).
2. Truncation test as in `context_factors_pit_2026-10-16/test_context_asof.py`: recompute the row for decision time t from data truncated at t;
   it must equal the full-history row (swing pivots confirmed k bars later, krown_core.py:190-249, must not use bars after t).
3. Join rule: `available_at = bar close + 1 min (write latency, OURS)`; decision_ts = event bar open + tf; usable iff `available_at < decision_ts`.
   Both 1d and 1w range gives D1 = 0 (REVIEW_OPUS F17).
4. Planted-leak lint: grep-style check that no join key uses a timestamp >= decision_ts.
Test rule (CLAUDE.md): the new tests also fail on the pre-change tree (module absent). Expected numbers from FORMULAS.md section 1 (RSI) and the
BBWP 21.5 hand number, computed independently of the code.

## 3. Parameters: SOURCED or OURS
| Parameter | Value | Label | Source |
|---|---|---|---|
| Event/zone detector zone_k, swing_tol, range_n | 3, 0.01, 20 | OURS | `backtest/layers/krown/params/krown_params.json` (labels OURS; KR-L01, KR-L10, KR-R01 give no number) |
| Order of importance trend > volatility > structure > momentum | ordering only | SOURCED | `krown_capture_2026-10-16/transcripts/ta101_missing4/hNfjyrJEytI_timed.txt` 00:10:22-00:10:50 (per FABLE_CARD s2) |
| BBWP expansion threshold 85 | 85 | OURS (S16 rule is his qualitative "near the end of the move"; the number is ours) | design s9 / REVIEW_OPUS F7 |
| BBWP timeframe | 4h | OURS | REVIEW_OPUS F6 |
| Write latency | 1 min | OURS | REVIEW_OPUS F17 |
| Naive baselines | SMA200, 20d return sign | OURS | REVIEW_OPUS F12 |
| ATR | plain SMA ATR | SOURCED (operator decision 2026-09-28) | `backtest/layers/FORMULAS.md:324` |
| Data sets | DEV 2022-01-01..2024-06-30; DEV_EXT 2020-01-01..2021-12-31 | SOURCED (operator) | `system/OPERATOR_DECISIONS.md:883,894` |
| Cost/R feasibility cap | 0.25 | OURS | PROJECT_VISION economics line (per REVIEW_OPUS F3) |
| D3 coverage targets | 15-30 % each side | OURS | REVIEW_OPUS F10 |
| MDE gate | 0.10 R per S unit, week clustered | OURS | REVIEW_OPUS F8 |
| Costs (for cost/R) | 0.10 %, 0.14 % round trip | OURS scenario | REVIEW_OPUS amendment 3 |
Bands frozen from counts are OURS, chosen on DEV counts with no outcome read. Any variant tried goes to `research/layer_lab/TRIALS.md`.

## 4. Fails (any one fails S1)
A bar >= 2024-07-01 in ACCESS_LOG; any outcome column read; a band changed after COUNTS.md; an unlabelled number; the leak variant passing.

## 5. Prior art (REVIEW_OPUS F1, cited, not computed here)
`research/context_factors_2026-10-16/REPORT.md:17-21`, `RESULT.md:1,9-15` (INCONCLUSIVE, E -0.023 R, SE 0.074); reuse `context_asof.py`.
