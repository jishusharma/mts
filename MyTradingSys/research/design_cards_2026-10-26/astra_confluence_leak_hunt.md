# Confluence frozen-test leak and reuse audit

RESULT (2026-10-26, JIS-NUC): 18/18 Holm slots reviewed; 2 CLEAN and 16 LEAK under the card's broad definition (15 disclosed DEV-reuse rows, 1 noncausal sizing-calibration row). These are audit classifications, not trading verdicts or 16 independent defects. The frozen document and code were not changed. No VALIDATION, HOLDOUT, sealed outcomes or external market data were opened.

Evidence paths below: P = `MyTradingSys/research/krown_audit_2026-10-22/PRE_REG_CONFLUENCE.md`; D = the same folder's `FABLE_DESIGN.md`; J = `run/joined_events.csv`; K = `MyTradingSys/backtest/layers/krown/krown_context.py`; R = its sibling `run_counts.py`. Line references are against audited HEAD 8d795bec4. Labels and classifications are OURS audit judgements; cited protocol parameters retain their original SOURCED/OURS labels.

## Meaning and limits

CLEAN means no future **decision input** or explicit prior-window reuse proved for that primary definition. It is not a source-data certification or approval to run. LEAK/reuse means the calendar window has already informed the programme, as expressly admitted at P:126-127; it does not mean S leaks future prices. Ordinary forward returns are legitimate labels, not predictor leakage. S3/S4 results and their implementations are not present in the committed run folder, so this is a definition/input audit, not an execution audit. The binary labels deliberately retain this distinction.

Let e be the next-open entry/decision boundary. Daily and 4h context must satisfy available_at < e (K:206-212); D3 uses the last 15m close <= e (R:192-195). Fixed-horizon outcomes finish at e+4h, with e+24h beside (P:27-30). For reuse rows, the earliest future label component is the first post-entry bar close, e+tf; the endpoint is e+4h. This describes the new test, not a claim that the old study used that same horizon. Prior read dates and first old outcome timestamps cannot be recovered from J; reuse is proved by P:126-127, not inferred from a future label alone.

## All 18 frozen slots

| # | Test | Verdict | Inputs and timing relative to e; proof |
|---|---|---|---|
| 1 | D1 vs naive trend | CLEAN | Last strictly available daily/weekly trends and naive SMA200/ret20; label ends e+24h. P:52-58 explicitly chooses the best baseline on DEV and fixes it for DEV_EXT. That is disclosed retrospective comparator selection, not an entry-time predictor. No evidence this exact D1 race was already read. |
| 2 | Pooled D1 contrast | LEAK (reuse) | D1 before e; same-side controls have their own historical decisions; new label e+4h. Reuses the 12 already-examined DEV triggers: P:79-86,126-127; D:33. Earliest usable pooled entry 2022-01-18 21:00 UTC, first 1h outcome close 22:00, endpoint 2022-01-19 01:00 (derived from J). No future-context join proved. |
| 3 | bb_top_reversal slope | LEAK (reuse) | S before/at e; first label close e+15m, endpoint e+4h. P:40,93-95,126-127; D:33. |
| 4 | malkan_rsi slope | LEAK (reuse) | S before/at e; first label close e+1h, endpoint e+4h. P:40,93-95,126-127; D:33. |
| 5 | rsi_reclaim slope | LEAK (reuse) | S before/at e; first label close e+1h, endpoint e+4h. P:40,93-95,126-127; D:33. |
| 6 | cc_msb slope | LEAK (reuse) | S before/at e; first label close e+1h, endpoint e+4h. P:40,93-95,126-127; D:33. |
| 7 | fabio_escalation slope | LEAK (reuse) | S before/at e; first label close e+1h, endpoint e+4h. P:40,93-95,126-127; D:33. |
| 8 | session_momentum slope | LEAK (reuse) | Decision follows sixth 5m bar; first label close e+5m, endpoint e+4h. P:28,40,93-95,126-127; run/COUNTS.md:26. |
| 9 | rsi_divergence_1h slope | LEAK (reuse) | S before/at e; first label close e+1h, endpoint e+4h. P:40,93-95,126-127; D:33. |
| 10 | rsi_divergence_4h slope | LEAK (reuse) | S before/at e; first label close and endpoint e+4h. P:40,93-95,126-127; D:33. |
| 11 | candle_pattern_1h slope | LEAK (reuse) | Trigger close at e, context strictly earlier; first label close e+1h, endpoint e+4h. P:40,93-95,126-127; run/COUNTS.md:27. |
| 12 | candle_pattern_4h slope | LEAK (reuse) | Trigger close at e; first label close and endpoint e+4h. P:40,93-95,126-127; run/COUNTS.md:27. |
| 13 | volume_1h slope | LEAK (reuse) | Spike closes at e; first label close e+1h, endpoint e+4h. P:40,93-95,126-127; run/COUNTS.md:28. |
| 14 | volume_4h slope | LEAK (reuse) | Spike closes at e; first label close and endpoint e+4h. P:40,93-95,126-127; run/COUNTS.md:28. |
| 15 | wlow_bounce slope | LEAK (reuse) | Prior-week location, trigger closes at e; first label close e+1h, endpoint e+4h. P:40,93-95,126-127; D:89. Parent DEV already examined; this slope remains descriptive. |
| 16 | T2 compression breakout | CLEAN | Previous six closed 4h BBWP values and confirming close precede next-open e; compression range ends before trigger. P:98-104; D:125-137. Future stop/target/BBWP observations determine exits only as they arrive, up to 30 bars. The peak condition is implemented in the definition as having reached 85 followed by a moving-average cross, not a future global maximum. No exact T2 prior read proved. |
| 17 | T4 weekly-low reclaim | LEAK (reuse) | Prior ISO-week low; poke then reclaim close within 1-3 bars and RSI at decision; subsequent exits <= e+24h. P:110-112; D:150-156 explicitly builds on eight already-counted wlow parent events. Window reuse is established, not an earlier read of this exact new reclaim strategy. First future outcome observation e+1h. Optional context branch also selected using full DEV test 1. |
| 18 | Vol-target sizing | LEAK (look-ahead in calibration) | P:68-73 uses DEV next-24h volatility calibration, chooses fallback from its correlation, sets target to full-DEV median predictions and normalises capital over full DEV. At an early e these quantities include later DEV observations. Earliest possible calibration label after a 4h decision is its first future 1h return at e+1h, with complete target e+24h. Concrete latest input: a 4h bar opened 2024-06-30 20:00 closes at 2024-07-01 00:00, later than the first pooled entry 2022-01-18 21:00; its next-24h target reaches 2024-07-02 00:00 if not censored. This is a definition-level noncausal fit, not proof S4 executed it. |

The family has 13 descriptive slope slots, not 13 discoveries (P:40,44-45,93-95). Reuse was already acknowledged by its authors. Keep all reused-DEV results hypothesis-generating per P:126-127. DEV_EXT sign agreement and the later single pooled VALIDATION read are the specified safeguards (P:117-119,135-139); this audit spends neither read.

## Findings requiring care before execution

1. **Sizing fit/evaluation separation is unspecified.** P:68-73 does not freeze a training-only mapping, chronological out-of-fold predictions, or a lagged target/capital normalisation. A retrospective full-DEV sizing comparison can be described honestly as fitted DEV exploration, but cannot establish an entry-time sizing edge. Freeze any remedy before reading S3/S4 outcomes; this audit does not amend the pre-registration. Its references to predicted volatility do not by themselves license using future realised volatility directly as a position size.
2. **Outcome windows can cross the sealed boundary.** P:52 calls for every DEV hour with a 24h label, while P:21,25 forbid post-cut bars. The final DEV decision would need observations after 2024-07-01. Parsing all J rows independently gives 0 usable events with e+4h > cut, but 4 usable layer-events with e+24h > cut. These are future-label boundary hazards, not observed forbidden reads. Censoring/NOT_RUN must be explicit rather than silently fetching the missing bars. P:122-123 forbids quietly substituting a different window.
3. **The documented guard is weaker than its wording.** R:40-43 rejects tmax > CUT, not equality; it logs supplied timestamps rather than checking every outcome endpoint. Equality can be valid for a decision boundary, but not for the open of a forbidden bar. S1 passes this boundary convention; it is not a sufficient S3/S4 outcome guard.
4. **Baseline selection and optional context branches reuse in-sample results.** Test 1's best-baseline choice (P:57-58) is deliberately a conservative retrospective comparator race; it is not evidence a baseline was selected in real time. T4's optional branch (D:153) and the sizing fallback (P:70) depend on full DEV readings. Describe those branches as fitted DEV analysis; do not present the year split as independent chronological training/testing.
5. **Forward-availability filtering is not a proven predictor leak.** R:127-129 filters status == OK; COUNTS.md:3 says this is forward-data availability. It can select a complete-label population using future missingness. No evidence here shows outcome-sign filtering. Sealed source membership and missingness causes are not independently verified.

## Revalidation

`python -m unittest discover -s MyTradingSys/backtest/layers/krown -p test_krown_context*.py`: 24 tests passed. Includes strict boundary, planted shifted joins, causal truncation and F6 direction checks. No new code/test was needed for this report-only task.

An independent standard-library csv scan read all 23,213 J rows, selected all 22,862 usable rows and checked both stored context timestamps using open+period+60,000 < decision_ts: **0 violations**. The scan also counted the 4h/24h endpoint hazards above without reading prices or outcomes. These are conditional checks on producer snapshots, not source reconstruction. `run/context_dev.csv` and J are committed inputs; run contains only ACCESS_LOG.md, COUNTS.md, bands.json, context_dev.csv, counts_cells.csv and joined_events.csv. CONTEXT_READ.md, DEV_RESULTS.md and COUNTS_T2.md are absent from this run folder.

This review does not certify all S0 preconditions, source membership, future S3/S4 implementations, controls, exit fills, or funding timing. It makes no keep/drop/demote/park decision for any layer.
