# Fabio LVN touch event table (DEV, 1h)

Command: `python MyTradingSys/research/layer_lab/fabio_lvn_touch_event_table/event_table.py --output <csv>` (CSV deleted after counting).
Input: F:/MTS/data/bigtrade/cache/perp/klines_1h.npz masked to open 2022-01-01..2024-06-30 before bars are built; VALIDATION/HOLDOUT unread.

Definition: swing_legs(left 2, right 2, body); profile over a_i..b_i, 20 bins, value area 70%, lowest-volume bin; level = bin midpoint (OURS).
One row at the first bar after confirmed_i (within 48 bars, OURS) whose high-low range contains the level; none if a newer leg is confirmed first.
Entry = open of the next bar; horizon 24 bars from that open, entry bar included (OURS); R = ATR14 (plain SMA, FORMULAS.md s12) at entry open. Long and short both recorded. Gross R, no rules.

## Result (real DEV run)
| rows | OK | NOT_IN_DATA | long MFE / MAE (R) | short MFE / MAE (R) |
|---|---|---|---|---|
| 1546 | 1546 | 0 | 3.2349 / 3.1667 | 3.1667 / 3.2349 |

Short numbers mirror long by construction (same window, opposite side), so MFE is about MAE: the table states no direction and shows no edge by itself. Reading it as a rule needs fee-net out-of-sample testing on VALIDATION, which this task does not do.

Tests: `python -m pytest MyTradingSys/research/layer_lab/fabio_lvn_touch_event_table -q` (9 pass; red before event_table.py existed).
