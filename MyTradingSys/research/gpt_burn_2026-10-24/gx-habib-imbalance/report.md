# GPT audit: Habib imbalance work (2026-10-24)

Scope: `research/habib_plan_imbalance_2026-10-20/`, `research/imbalance_qriptal_2026-10-16/`, `backtest/layers/run_t055_c3_imbalance.py`, compared with `backtest/layers/FORMULAS.md`. Read-only audit; no backtest, tests, Git, sync, or push commands were run.

## Findings

### 1. Plan hit scorer can credit target movement from the same candle as entry — HIGH

`MyTradingSys/research/habib_plan_imbalance_2026-10-20/plan_score.py:48-64`: after the first candle touching entry sets `filled_at`, the target/progress scan includes that candle (`t < filled_at` is skipped, so `t == filled_at` is scored). A 1-minute candle with `low=100, high=110`, long entry 100, target 110 is therefore “full”, even though OHLC cannot show whether 110 happened before or after entry. Partial progress is exposed to the same ambiguity. This affects the scorer’s outcome label; the note correctly says it is not an execution/P&L test.

Reproduction by values: one candle `(00:00, high=110, low=100)`, long `entry=100`, `target=110`, `posted=00:00` yields `full` under the current comparisons. Require target/progress to occur on a later candle, or conservatively resolve same-candle ordering as ambiguous.

### 2. Published “check” returns overlap the repo’s sealed main HOLDOUT; it was exposed twice — HIGH

`MyTradingSys/research/imbalance_qriptal_2026-10-16/EXPOSURE_LEDGER.csv:2-3` records two backtest runs, k=2 and k=3, each publishing returns through 2026-06-25. The independent main split says HOLDOUT is 2025-07-01..2026-09-30 (`research/dsa_backtest_audit_2026-10-16/AUDIT_BRIEF.md:16`); the Qriptal/Tom split instead calls 2025-09-01..2026-06-25 “check” (`imb.py:50-51`, `BACKTEST.md:6`). The overlap is 2025-09-01..2026-06-25, entirely inside the main HOLDOUT. Thus the main-HOLDOUT return window was read in both parameter runs; it is not clean OOS/validation evidence. `README.md:98-101` itself records this exposure and says later tests cannot call that interval clean OOS.

Reproduction/count: parse the ledger data rows: 2 fee-net backtest rows (`--k 2.0`, `--k 3.0`) both declare the same end date `2026-06-25`; intersect that interval with the main HOLDOUT start `2025-07-01` = 2 exposed runs. The label-check and candle-parity rows (ledger lines 4-5) also read HOLDOUT-period bars, but explicitly say no returns were read there. The nine plan rows dated 2026-07-14..09-22 remain marked `NOT_SCORED_HOLDOUT_WINDOW`; the plan note says no candle was read for them (`habib_plan_imbalance_2026-10-20/README.md:56-59`).

### 3. C3 “imbalance” is a different construct, and its formula is absent from the canonical formula contract — LOW

`MyTradingSys/backtest/layers/run_t055_c3_imbalance.py:2-7,22-40` tests quarter-hour taker-buy delta `(2*tbv - v)/v` over a 1- or 5-minute opening window, with momentum/contrarian directions. This is not Habib’s per-exchange volume-anomaly candle, which the Qriptal source note identifies as construct F (`research/imbalance_qriptal_2026-10-16/README.md:28-39`). The C3b formula and source/OURS split do not appear in `FORMULAS.md`: section 13 documents shared fees, and section 16 documents turn-of-candle returns, not the C3b signal (`FORMULAS.md:343-395`). The code’s arithmetic is internally consistent with its stated proxy: for total volume 100 and taker-buy volume 70, `(2*70-100)/100 = 0.40`. The issue is contract/provenance coverage and naming, not a demonstrated arithmetic error.

Provenance: the paper’s opening order-imbalance premise is SOURCED as noted in the script comment; this taker-buy proxy, 1/5-bar windows, `min_abs` grid, momentum/contrarian directions, horizons, split and other thresholds are OURS. In the Qriptal candle study, qualitative “high volume + small body means failed price movement” is SOURCED to the quotes cited in its README; relative-volume median/lookback, k grid, 30%/70% body cutoffs, 20-bar extreme, 24-bar hold and target choices are OURS (`imb.py:37-51`, `README.md:31-39,47,68`). The spoken plan prices are source data; the scorer’s thresholds are OURS (`habib_plan_imbalance_2026-10-20/README.md:49,57`).

### 4. C3’s OOS is a floating split, not a sealed calendar holdout — HIGH

`MyTradingSys/backtest/layers/run_t055_c3_imbalance.py:55-79` splits by row count at 70%, searches the full 8-variant grid on IS, then reports six horizon-specific OOS results, selecting a best IS variant separately per horizon. `:85` loads the full `raw_1m_2022`/`raw` dataset. This is causal with respect to parameter selection (the OOS result is not used to choose the IS parameters), but it does not enforce dates outside exposed periods and the same OOS segment is reported across six horizons. The repo audit already identifies this floating 70/30 design as unsafe for data extending into the sealed HOLDOUT (`dsa_backtest_audit_2026-10-16/AUDIT_BRIEF.md:25,113`). Do not describe a run over current full-history data as a fresh holdout pass.

Reproduction: inspect `n_is = int(len(bars)*0.7)` at lines 57-58, the per-horizon OOS loop at 71-79, and the input paths at 85. For a sealed OOS claim, print/record the actual first and last timestamps in each split and compare them against the pre-registered calendar boundaries before scoring.

## Look-ahead review

- C3b signal timing is causal in the code inspected: it starts only on a quarter-hour boundary, requires contiguous completed minute bars, calculates the signal from the 1- or 5-bar window, and places event index at the last window bar (`run_t055_c3_imbalance.py:25-40`). Shared runner enters at that event bar’s close and exits at a later close (`run_t055.py:111-135`). No future bar is used to form the C3b signal. Its split-local windowing drops boundary events rather than borrowing future bars.
- The plan scorer has the same-candle ordering ambiguity described in finding 1.
- Qriptal relative volume excludes the current candle from its 50-bar median (`imb.py:168-172`), and its candle backtest enters at the next bar’s open (`:303-323`), so no direct signal look-ahead was found there. Candle labels use only candles closed by video publication time (`:210-215`).

## What is still needed for a fee-net out-of-sample test

1. Decide the target: plan hit-rate, Habib’s candle-as-context method, or a mechanical entry strategy. The existing plan scorer excludes execution, while the earlier candle test is a mechanical fade that already reports NO EDGE; C3b is taker-delta research and does not test Habib’s candle.
2. Obtain enough eligible timestamped, typed plans and uncropped charts/transcripts to define the actual level, entry trigger, invalidation/stop, exit/target, optional sweep rule, and what “imbalance” means. Current ledger has 9 priced plans, all in the holdout window and 0 scored on DEV (`habib_plan_imbalance_2026-10-20/README.md:42-46,55-59`). The current threshold scorer alone cannot support fees or a tradable return.
3. Correct the same-candle scoring ambiguity and freeze a source/OURS parameter ledger before any scoring. Register all variants and prior exposure: the k=2/k=3 Qriptal outcome interval is already exposed; the main-HOLDOUT overlap cannot be reused as untouched OOS.
4. Pre-register a calendar DEV window, one VALIDATION read, and a genuinely untouched OOS window after the prior exposed data (or collect new future data); freeze parameters after DEV/VALIDATION. Do not use a floating split as proof of sealed holdout.
5. Define realistic fills and all costs for the intended venue/instrument: entry/exit timing, maker/taker mix, fee schedule, spread/slippage, funding when applicable, gaps, partial fills, stop/target order when both are touched, and a minimum-risk/position-sizing rule. The earlier fade charges 0.05% per side only (`imb.py:49,296-300`); T055’s canonical shared model is 10 bp RT fees + 2 bp RT slippage + signed funding (`FORMULAS.md:343-354`). State which one applies and justify it for the venue.
6. Run once on the frozen OOS window, report trade count, net return/expectancy and uncertainty against the predeclared benchmark/control, and log the exact input window, code/parameter hash, and exposure. No fee-net OOS result exists for the Sunday-plan study yet.

Result: No signal look-ahead found in C3b or the candle detector; plan scorer has same-bar outcome ambiguity, Qriptal returns exposed main HOLDOUT twice, and no clean fee-net OOS test of Habib’s plan/candle method is ready.
