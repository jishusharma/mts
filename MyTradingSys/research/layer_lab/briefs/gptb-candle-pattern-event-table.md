# gptb-candle-pattern-event-table

## Why this is a rerun
The code and synthetic tests already exist in MyTradingSys/research/layer_lab/candle_pattern_event_table/ (committed by the earlier BLOCKED runs). Both earlier runs ended BLOCKED only because the brief named no data path (see research/layer_lab/LAB_BLOCKED_2026-10-17.md). DO NOT search Dumps/backtest or F:/MTS/data/binance_tf: they are not the DEV source.

## Goal
Add a DEV loader and CLI to event_table.py for klines_1h.npz (and 4h built from 1h), run the four pure detectors (engulfing, pin bar, inside bar, doji; definitions MyTradingSys/research/candle_patterns_2026-10-04/PRE_REG_CANDLE_PILOT.md:41-48,56, cite file:line in REPORT) on closed bars, stamp each event at the closing bar, forward path starts the next bar, MFE/MAE in R (R = signal bar range, as the module does; OURS). Report counts per pattern x timeframe (1h, 4h). No rules, no tuning.

## Data
F:/MTS/data/bigtrade/cache/perp/klines_1h.npz (arrays t,o,h,l,c,v,tbv,n,atr; t = bar open ms, 41,784 bars, 2022-01-01..2026-10-07). DEV = bar open < 2024-07-01 (2024-07-01T00:00Z = 1719792000000 ms); slice with a numpy mask BEFORE building bar dicts; never inspect later bars. 4h = 4 consecutive 1h bars at 00/04/08/12/16/20 UTC, complete buckets only.

## Helpers (read only)
DEV rows go through MyTradingSys/research/layer_lab/dev_split_guard/event_table.py (dev_only, assert_dev); forward MFE/MAE R-units via MyTradingSys/research/layer_lab/forward_excursion/event_table.py (forward_excursion) where it fits; import read only by file path.

## Tests
Existing 6 synthetic tests stay green; new red-first tests: the loader returns only bars with open < 2024-07-01 (a synthetic npz with a 2024-07-01 bar proves it is dropped); a 4h bucket with a missing 1h bar is skipped; each pattern fires on its example and not its near-miss; forward path starts the next bar; gap in forward window = NOT_IN_DATA.

## Rules
DEV only; params OURS unless sourced; lookahead_lint --new clean; add a failing-first test for every change you make to the existing module; delete any CSV after counting (repo is public).
