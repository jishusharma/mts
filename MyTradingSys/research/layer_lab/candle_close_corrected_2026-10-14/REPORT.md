# Corrected candle-close study — DEV findings

Zero candidates pass the registered evidence gates. This is not proof that candle signatures never work: phase applicability remains unproven, especially in sparsely matched range and trend contexts.

The input is 1,313,280 Binance BTCUSDT perpetual minute bars (January 2022–June 2024), with 30 price and 30 funding archives verified. The ledger contains 79,174 real/placebo side rows and 112,606 reused matching records, not independent trades. No validation or holdout was read by this study. This DEV window was already inspected; this is exploratory evidence.

## What was tested

Six closing signatures on 1/2/3/5/15/30/60-minute candles at prior completed 4h/day/week highs and lows. OURS phase rules use completed 4h and 1h bars: structural up/down trends, bounded ranges, transitions, volatility, side alignment and level position. Daily momentum is metadata, not a bull/bear-cycle classifier. Phase is frozen before contact, and may change before the decision.

Every encounter uses the same decision clock: close of its third trigger candle. Matched real nonsignature controls share scope, side, approach and context; proximity, volatility and time-of-day constraints apply without fallback. Outcomes use 60-minute and one-day horizons, 14/20bp cost scenarios and historical funding as a trade-price notional proxy, not exact account PnL. One-day barrier and extreme-retention outcomes cannot establish macro bottoms or tops.

The final family has 2,016 cells: 1,764 informative cells (six signatures plus a directional level-bounce baseline) and 252 bidirectional level diagnostics that are never candidates. Multiple-testing scope is 6,048 primary metrics. Fixed-graph seven-day block resampling separately normalizes signal and weighted control means.

## Phase-specific findings

| Context | Nonempty cells | Sample/coverage/balance gates pass | Positive net14 point means |
|---|---:|---:|---:|
| RANGE_EDGE | 46 | 0 | 24 |
| RANGE_INTERIOR | 104 | 0 | 27 |
| TRANSITION_HIGH_VOL | 138 | 0 | 62 |
| TRANSITION_OTHER | 294 | 64 | 56 |
| TREND_ALIGNED | 4 | 0 | 2 |
| TREND_CONFLICT | 242 | 0 | 96 |

Only 64 informative cells meet the sample, day-count, coverage and balance gates; all are TRANSITION_OTHER. None establishes both positive probability lift and positive own net return under adjusted uncertainty. Positive point means are hypotheses, not validated edges. Range and aligned-trend results are chiefly limited by sample size and comparable controls; they do not justify selecting or rejecting a phase policy.

## Checks and corrections

Thirteen dedicated tests pass with no skips. An independent verifier checks 126 raw phase/level/context/outcome cases, 126 control selections, all 2,016 cell counts/means and ten intervals from five highest-count candle cells. All pass. It does not independently rebuild every interval.

Fail-first checks repaired an import error being hidden as a skip, future-length-dependent placebo randomness, and a resampling denominator error. Funding timestamps were normalized only after confirming complete nominal settlement coverage. The bidirectional level diagnostic was retained and a causal approach-side bounce baseline registered separately. Original analyses and freezes are archived; the canonical ledger SHA was restored exactly after a cache re-encoding incident. PRE_OUTCOME_FIXES.md, LEVEL_ORIENTATION_AMENDMENT.md and BOOTSTRAP_AMENDMENT.md record the chronology. Statistical reruns are listed in TRIALS.md; these repairs do not create fresh out-of-sample evidence.

## Next move

First benchmark the phase labels against independently annotated charts and measure matched-sample power by phase. Resolve sparse/common-support contexts before another performance search. Then freeze a small, causally defined hypothesis set and evaluate it once on an untouched window, with explicit exposure, execution costs and risk. Macro-cycle bottoms require a separate longer-horizon study and adequate independent cycles. The anonymous YouTube demonstration has not been identified, so these OURS rules are not a faithful trader replication.
