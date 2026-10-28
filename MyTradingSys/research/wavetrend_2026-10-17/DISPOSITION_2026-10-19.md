# WaveTrend audit disposition (2026-10-19)

This records a judgment and metadata correction from already-read MTS evidence. It is not a new outcome run. The frozen BTCUSDT Binance USD-M DEV atlas covers 2022-01-01 through 2024-06-30; its loader excludes later dates. VALIDATION and HOLDOUT remain unread. No fees, funding, strategy exits or live wiring were added.

## C1 divergence

The written C1 definition requires a confirmed price pivot paired with a confirmed WT pivot. The frozen detector confirms price pivots, then compares WT values at those price-pivot bars without confirming WT pivots. The synthetic proof reproduces price pivots `[(10, 12), (20, 22)]`, WT pivots `[(12, 14), (18, 20)]`, and a reported event `[(22, 1)]` although neither compared WT value is a WT pivot.

Disposition: W07/W08 do not measure the preregistered confirmed-WT-pivot divergence and are not evidence for or against that pattern. Preserve the frozen code/results. A versioned detector needs fail-first fixtures and independent review; then a DEV-only count pass and new preregistration must be frozen before any new outcome read.

## Verdict re-gate and control arm

The already-read `research/fable_audit_2026-10-18/REGATE_AUDIT.md` Q3 re-gates the existing nine-cell set at a 200-day floor, up from 153; all nine cells retain sufficient event-days. Q3 requires W04–W08 to be `INCONCLUSIVE` based on realized MDE; W01–W03 and W09 stay `FAIL`. `research/VERDICTS.csv` now reflects this exact classification, with cost `0.14` and `one_run=yes` on W04–W08. No outcomes were recomputed. W07/W08 carry the INCONCLUSIVE ledger label for the prior atlas and also have the separate C1 detector-invalid limitation above.

The event arm uncertainty is day-clustered, while the random/context control uncertainty is the standard deviation of sampled draw means; the difference calculation assumes independence. That does not preserve the shared clock and day/block dependence. No cell passed the original gross screen. A new paired day/block resampling or randomization method must be reviewed and frozen in a new analysis version before another outcome run.

## Source manifest and layer status

The old exposure ledger identifies the klines directory but not the exact source-file digests and timestamp-integrity counts. Before any new outcome read, pin the 30 DEV input files by name, size, SHA-256, timestamp coverage, duplicate/missing-minute counts and usable timeframe bars. Add a new ledger row; do not rewrite historical entries.

MTS now lists WaveTrend as a family in `system/layer_index.json` and generated `system/LAYERS.md`. The causal observation module and formula/reference parity checks exist. There is no WaveTrend backtest row in `system/layer_map.json`, validated fee-net strategy, or live integration. The outcome state remains exploratory: four FAIL, five INCONCLUSIVE, with two of those five also invalid for the specified C1 definition. No edge is established.

Claude review is requested in desk row `20261018-212747-claude-priority-review-wavetrend-2026-10`. The planner's card `wavetrend-audit-c1-disposition` remains refined pending a real Lab_Guy review stamp; its original completion gate and additional VERDICTS.csv scope are preserved.
