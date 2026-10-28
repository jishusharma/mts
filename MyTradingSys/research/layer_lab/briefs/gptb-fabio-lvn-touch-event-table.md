# gptb-fabio-lvn-touch-event-table

Fabio volume-profile LVN touch: event table with forward MFE/MAE in R on 1h DEV

## Goal
Build event_table.py: on 1h DEV bars use swing_legs (left 2, right 2, use_body True), build_profile (n_bins 20), value_area (pct 0.70) and lowest_volume_level from MyTradingSys/backtest/layers/fabio/fabio_volume_fvg.py (import read only). For each leg, only after leg confirmed_i, the profile of the leg (a_i..b_i) gives the lowest-volume level in the value area; one row at the FIRST later bar (within 48 bars of confirmed_i, 48 is OURS) whose high-low range touches that level; no row if a newer leg is confirmed first. Side: record both long and short columns (mfe_R and mae_R for each) because the module states no direction. Entry = open of the bar after the touch bar; horizon 24 bars (OURS) via forward_excursion. Input F:/MTS/data/bigtrade/cache/perp/klines_1h.npz (arrays t,o,h,l,c,v,tbv,n,atr; t = bar open ms); it exists on this machine. DEV = bar open 2022-01-01T00:00Z .. 2024-06-30T23:59:59Z; slice before building bars, never inspect later bars. R = 1 ATR14 (plain SMA of true range, FORMULAS.md section 12) of the 1h bars closed at the entry bar open. No rules, no tuning, gross R only.

## Helpers (read only)
DEV rows go through MyTradingSys/research/layer_lab/dev_split_guard/event_table.py (dev_only, assert_dev) and forward MFE/MAE through MyTradingSys/research/layer_lab/forward_excursion/event_table.py (forward_excursion); import both read only by file path (importlib or sys.path), do not edit them.

## Tests (write first, must fail before the code exists)
synthetic 1h legs with a hand-built volume profile: the LVN price equals the hand value, the first touch bar gets the single row, a touch after a newer confirmed leg gives none, a touch before confirmed_i is ignored (no look-ahead), a leg whose profile is empty = NOT_IN_DATA; entry is the next bar open; long and short excursions equal hand values.

## Rules
DEV only; params OURS unless a source is named (horizon too); lookahead_lint --new clean; no VALIDATION/HOLDOUT bars; delete any CSV after counting (repo is public, no data commits).
