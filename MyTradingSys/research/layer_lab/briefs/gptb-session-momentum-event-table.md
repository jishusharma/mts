# gptb-session-momentum-event-table

Session momentum (T055 C2): daily event table with forward MFE/MAE in R on 5m DEV

## Goal
Build event_table.py: on 5m DEV bars call session_momentum_events (bar_min 5, session_start_min 0, first_min 30, entry_min 30, min_abs 0.0 = FORMULAS.md section 15 defaults) from MyTradingSys/backtest/layers/session/session_momentum.py (import read only). One row per UTC day with an event; side = sign of the first-30-minute return; entry = close of the event bar (as the module does); forward bars start with the next 5m bar and run to 24:00 UTC of that day (session end; OURS). Forward MFE/MAE in R via forward_excursion. Input F:/MTS/data/bigtrade/cache/perp/klines_5m.npz (arrays t,o,h,l,c,v,tbv,n,atr; t = bar open ms); it exists on this machine. DEV = bar open 2022-01-01T00:00Z .. 2024-06-30T23:59:59Z; slice before building bars, never inspect later bars. R = 1 ATR14 (plain SMA of true range, FORMULAS.md section 12) of the 1h bars closed at the entry bar open. No rules, no tuning, gross R only.

## Helpers (read only)
DEV rows go through MyTradingSys/research/layer_lab/dev_split_guard/event_table.py (dev_only, assert_dev) and forward MFE/MAE through MyTradingSys/research/layer_lab/forward_excursion/event_table.py (forward_excursion); import both read only by file path (importlib or sys.path), do not edit them.

## Tests (write first, must fail before the code exists)
synthetic 5m day: first-30-minute return +0.4% gives one long row at the close of the 6th bar, -0.4% a short row, exactly 0 gives none; forward window ends at 24:00 UTC and never crosses into the next day; a day with a missing bar in the first 30 minutes = NOT_IN_DATA; MFE/MAE equal hand values; R uses only 1h bars closed at or before the entry bar open.

## Rules
DEV only; params OURS unless a source is named (horizon too); lookahead_lint --new clean; no VALIDATION/HOLDOUT bars; delete any CSV after counting (repo is public, no data commits).
