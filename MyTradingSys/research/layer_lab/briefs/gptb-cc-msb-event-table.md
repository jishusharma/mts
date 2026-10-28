# gptb-cc-msb-event-table

CryptoCred market-structure break: event table with forward MFE/MAE in R on 1h DEV

## Goal
Build event_table.py: on 1h DEV bars call find_swings (left 2, right 2, use_body True) then classify_msb (require_prior_sequence True, filter_range_noise False) from MyTradingSys/backtest/layers/cryptocred/cc_structure.py (import read only; read the event dict keys and direction field in the file first). One row per MSB event; side = break direction (up = long, down = short); entry = open of the bar after the break bar; forward MFE/MAE in R over 24 bars (OURS) via forward_excursion. Columns: event bar t, broken swing t, direction, entry, R, mfe_R, mae_R, status. Input F:/MTS/data/bigtrade/cache/perp/klines_1h.npz (arrays t,o,h,l,c,v,tbv,n,atr; t = bar open ms); it exists on this machine. DEV = bar open 2022-01-01T00:00Z .. 2024-06-30T23:59:59Z; slice before building bars, never inspect later bars. R = 1 ATR14 (plain SMA of true range, FORMULAS.md section 12) of the 1h bars closed at the entry bar open. No rules, no tuning, gross R only.

## Helpers (read only)
DEV rows go through MyTradingSys/research/layer_lab/dev_split_guard/event_table.py (dev_only, assert_dev) and forward MFE/MAE through MyTradingSys/research/layer_lab/forward_excursion/event_table.py (forward_excursion); import both read only by file path (importlib or sys.path), do not edit them.

## Tests (write first, must fail before the code exists)
synthetic 1h bars with a hand-built lower-high then close above it: exactly one up-MSB row stamped on the break bar, the swing is not used before confirmed_i, each broken swing fires once, a close back inside gives no second row; entry is the next bar open; gap or short forward window = NOT_IN_DATA; MFE/MAE equal hand values.

## Rules
DEV only; params OURS unless a source is named (horizon too); lookahead_lint --new clean; no VALIDATION/HOLDOUT bars; delete any CSV after counting (repo is public, no data commits).
