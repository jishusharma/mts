# gptb-turn-of-candle-event-table

Turn-of-candle (T055 C3): per-quarter-hour event table with forward MFE/MAE in R on 1m DEV

## Goal
Build event_table.py: on 1m DEV bars, one row per 15-minute boundary where minute-of-quarter of the next bar is 0 (entry = close of the bar with mq == 14, i.e. lead_minutes 1 per FORMULAS.md section 16; use turn_of_candle_events from MyTradingSys/backtest/layers/turn_of_candle/turn_of_candle.py read only to cross-check boundaries). Columns for BOTH sides (long and short): mfe_R and mae_R over the next 15 one-minute bars (15 is OURS) via forward_excursion, plus ret_first_min = (c-o)/o of the boundary bar. R for this card = 1 ATR14 of the 1h bars closed at the entry bar open (needs klines_1h.npz, same DEV slice). Process 1m in numpy chunks; DEV is about 1.3M rows. Input F:/MTS/data/bigtrade/cache/perp/klines_1m.npz (arrays t,o,h,l,c,v,tbv,n,atr; t = bar open ms); it exists on this machine. DEV = bar open 2022-01-01T00:00Z .. 2024-06-30T23:59:59Z; slice before building bars, never inspect later bars. R = 1 ATR14 (plain SMA of true range, FORMULAS.md section 12) of the 1h bars closed at the entry bar open. No rules, no tuning, gross R only.

## Helpers (read only)
DEV rows go through MyTradingSys/research/layer_lab/dev_split_guard/event_table.py (dev_only, assert_dev) and forward MFE/MAE through MyTradingSys/research/layer_lab/forward_excursion/event_table.py (forward_excursion); import both read only by file path (importlib or sys.path), do not edit them.

## Tests (write first, must fail before the code exists)
synthetic 1m bars: boundary rows exist only where the next bar has minute-of-quarter 0, entry is the close of the minute-14 bar, long and short MFE/MAE equal hand values (short MFE = long MAE in price terms), forward bars are exactly the next 15, a gap in them = NOT_IN_DATA; the first 14 bars of the series give no row.

## Rules
DEV only; params OURS unless a source is named (horizon too); lookahead_lint --new clean; no VALIDATION/HOLDOUT bars; delete any CSV after counting (repo is public, no data commits).
