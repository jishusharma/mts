# gptb-fabio-escalation-event-table

Fabio escalation/absorption: event table with forward MFE/MAE in R on 1h DEV

## Goal
Build event_table.py: on 1h DEV bars (bars need keys t,o,h,l,c,v,tbv; delta = 2*tbv - v) call escalation_events with the module defaults (left 2, right 2, use_body True, level_tolerance 0.001, aggression_k 2.0, record_lookback 20; all OURS per the module header) from MyTradingSys/backtest/layers/fabio/fabio_escalation.py (import read only; read the event dict keys first). One row per event, side = the event's breakout direction; entry = open of the bar after the event bar; forward MFE/MAE in R over 24 bars (OURS) via forward_excursion. Input F:/MTS/data/bigtrade/cache/perp/klines_1h.npz (arrays t,o,h,l,c,v,tbv,n,atr; t = bar open ms); it exists on this machine. DEV = bar open 2022-01-01T00:00Z .. 2024-06-30T23:59:59Z; slice before building bars, never inspect later bars. R = 1 ATR14 (plain SMA of true range, FORMULAS.md section 12) of the 1h bars closed at the entry bar open. No rules, no tuning, gross R only.

## Helpers (read only)
DEV rows go through MyTradingSys/research/layer_lab/dev_split_guard/event_table.py (dev_only, assert_dev) and forward MFE/MAE through MyTradingSys/research/layer_lab/forward_excursion/event_table.py (forward_excursion); import both read only by file path (importlib or sys.path), do not edit them.

## Tests (write first, must fail before the code exists)
synthetic 1h bars with tbv set so a record-delta bar breaks an absorbed swing level: one row on that bar, side in the aggressor's direction; a bar with delta below aggression_k times the average gives none; the swing is not used before confirmed_i; entry is the next bar open; gap or short forward window = NOT_IN_DATA.

## Rules
DEV only; params OURS unless a source is named (horizon too); lookahead_lint --new clean; no VALIDATION/HOLDOUT bars; delete any CSV after counting (repo is public, no data commits).
