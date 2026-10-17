# gptb-volume-event-table

## Why this is a rerun
The code and synthetic tests already exist in MyTradingSys/research/layer_lab/volume_event_table/ (committed by the earlier BLOCKED runs). Both earlier runs ended BLOCKED only because the brief named no data path (see research/layer_lab/LAB_BLOCKED_2026-10-17.md). DO NOT search Dumps/backtest or F:/MTS/data/binance_tf: they are not the DEV source.

## Goal
Add a DEV loader and CLI to event_table.py for klines_1h.npz (4h built from 1h), compute relative volume per bar (same hour-of-week median over the prior N weeks, N = 8 weeks (module default n_weeks=8, horizon 6; OURS: the pre-reg RVadj at PRE_REG_VOLUME_2026-10-09.md:35 uses 8 weeks for 1d and 20 days for 4h slots, not hour-of-week)), emit rows for spikes >= 2x with forward MFE/MAE in R (R = spike bar range, body direction; module choice, OURS). Report counts for 1h and 4h. No rules, no tuning, HOLDOUT sealed.

## Data
F:/MTS/data/bigtrade/cache/perp/klines_1h.npz (arrays t,o,h,l,c,v,tbv,n,atr; t = bar open ms, 41,784 bars, 2022-01-01..2026-10-07). DEV = bar open < 2024-07-01 (2024-07-01T00:00Z = 1719792000000 ms); slice with a numpy mask BEFORE building bar dicts; never inspect later bars. 4h = 4 consecutive 1h bars at 00/04/08/12/16/20 UTC, complete buckets only.

## Helpers (read only)
DEV rows go through MyTradingSys/research/layer_lab/dev_split_guard/event_table.py (dev_only, assert_dev); forward MFE/MAE R-units via MyTradingSys/research/layer_lab/forward_excursion/event_table.py (forward_excursion) where it fits; import read only by file path.

## Tests
Existing 5 synthetic tests stay green; new red-first tests: loader drops bars with open >= 2024-07-01; the baseline never contains the current bar (hand ratio); fewer than N prior weeks = NOT_IN_DATA; a 4h bucket with a missing 1h bar is skipped; spike at a known bar is flagged with hand-computed forward MFE/MAE.

## Rules
DEV only; params OURS unless sourced; lookahead_lint --new clean; add a failing-first test for every change you make to the existing module; delete any CSV after counting (repo is public).
