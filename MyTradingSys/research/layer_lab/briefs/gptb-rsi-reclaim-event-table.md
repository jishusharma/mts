# gptb-rsi-reclaim-event-table

RSI 40/60 reclaim (operator 2a): event table with dwell/depth buckets and forward MFE/MAE in R on 1h DEV

## Goal
Build event_table.py: RSI14 (rsi_core) on 1h DEV, then rsi_reclaim_events from MyTradingSys/backtest/layers/rsi/rsi_reclaim.py with level 40 direction up (long) and level 60 direction down (short), clearance 2.0 (OURS, the module has no default on purpose). One row per reclaim with columns dwell_below, band_bars, depth copied from the event; no retest filter, no bucket cut-offs. Entry = open of the bar after the reclaim bar; forward MFE/MAE in R over 24 bars (OURS) via forward_excursion. Input F:/MTS/data/bigtrade/cache/perp/klines_1h.npz (arrays t,o,h,l,c,v,tbv,n,atr; t = bar open ms); it exists on this machine. DEV = bar open 2022-01-01T00:00Z .. 2024-06-30T23:59:59Z; slice before building bars, never inspect later bars. R = 1 ATR14 (plain SMA of true range, FORMULAS.md section 12) of the 1h bars closed at the entry bar open. No rules, no tuning, gross R only.

## Helpers (read only)
DEV rows go through MyTradingSys/research/layer_lab/dev_split_guard/event_table.py (dev_only, assert_dev) and forward MFE/MAE through MyTradingSys/research/layer_lab/forward_excursion/event_table.py (forward_excursion); import both read only by file path (importlib or sys.path), do not edit them.

## Tests (write first, must fail before the code exists)
synthetic RSI series (inject via a function argument so the test needs no klines): a direct cross gives band_bars 0, a 4-bar below-run gives dwell_below 4, a band pop between two below-runs restarts dwell; the short side mirrors; None bars carry state; entry is next bar open; incomplete forward window = NOT_IN_DATA.

## Rules
DEV only; params OURS unless a source is named (horizon too); lookahead_lint --new clean; no VALIDATION/HOLDOUT bars; delete any CSV after counting (repo is public, no data commits).
