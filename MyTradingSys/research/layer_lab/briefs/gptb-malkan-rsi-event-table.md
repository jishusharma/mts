# gptb-malkan-rsi-event-table

Malkan 40/60 RSI bounce: research-side event table with forward MFE/MAE in R on 1h DEV

## Goal
Build event_table.py: on 1h DEV bars compute RSI14 with MyTradingSys/backtest/layers/rsi/rsi_core.py (rsi_core) and the regime with malkan_regime, then one row per event of malkan_setup_bull (level 40, long) and malkan_setup_bear (level 60, short) from MyTradingSys/backtest/layers/rsi/malkan_40_60.py with its default tolerance 2.0 and require candle True (import read only; the 40/60 numbers are SOURCED in that file header, lookback 20 is its default). Entry = open of the bar after the event bar; forward MFE/MAE in R over 24 bars (24 is OURS) via forward_excursion. Input F:/MTS/data/bigtrade/cache/perp/klines_1h.npz (arrays t,o,h,l,c,v,tbv,n,atr; t = bar open ms); it exists on this machine. DEV = bar open 2022-01-01T00:00Z .. 2024-06-30T23:59:59Z; slice before building bars, never inspect later bars. R = 1 ATR14 (plain SMA of true range, FORMULAS.md section 12) of the 1h bars closed at the entry bar open. No rules, no tuning, gross R only.

## Helpers (read only)
DEV rows go through MyTradingSys/research/layer_lab/dev_split_guard/event_table.py (dev_only, assert_dev) and forward MFE/MAE through MyTradingSys/research/layer_lab/forward_excursion/event_table.py (forward_excursion); import both read only by file path (importlib or sys.path), do not edit them.

## Tests (write first, must fail before the code exists)
synthetic 1h bars with a hand-built RSI path: one bull bounce at 40 gives one long row, a bear reject at 60 one short row, a near-miss (RSI stops 3 points above the tolerance band) gives none; entry is the next bar open and no bar after the horizon is read; fewer than 15 prior bars or a gap inside the forward window = NOT_IN_DATA; MFE/MAE equal hand values.

## Rules
DEV only; params OURS unless a source is named (horizon too); lookahead_lint --new clean; no VALIDATION/HOLDOUT bars; delete any CSV after counting (repo is public, no data commits).
