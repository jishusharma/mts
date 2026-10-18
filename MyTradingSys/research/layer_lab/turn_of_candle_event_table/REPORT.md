# Turn-of-candle (T055 C3) 1m event table

**Result:** DEV 87,552 quarter-hour rows, 87,491 OK, 61 NOT_IN_DATA; mean gross 15-bar excursion in R: long MFE 0.2513 / MAE 0.2581, short MFE 0.2581 / MAE 0.2513. Descriptive gross data, not an edge claim.

## Built
- `event_table.py`: one row per 1m bar with minute-of-quarter 14 (`turn_of_candle_events(lead_minutes=1)`, FORMULAS.md s16, read only); entry = close of that bar, boundary bar = the next (minute 0). `ret_first_min = (c-o)/o` of the boundary bar.
- Long and short MFE/MAE over the next 15 one-minute bars (15 is OURS) via `forward_excursion`; short MFE = long MAE and vice versa, as the table shows.
- R = ATR14 (plain SMA of true range, FORMULAS.md s12) of the 1h bars closed at or before the entry bar open.
- NOT_IN_DATA (blank numbers, never 0): fewer than 15 contiguous forward bars, or fewer than 15 contiguous closed 1h bars. A missing minute-14 bar gives no row.
- Loader slices `t` to `[2022-01-01, 2024-07-01)` before touching other arrays; VALIDATION and HOLDOUT unread.
- Tests (8) written first, failed at collection; now green: `python -m pytest MyTradingSys/research/layer_lab/turn_of_candle_event_table/test_event_table.py -q -p no:cacheprovider`. `lookahead_lint.py --new`: no hits in these files.
- DEV run: `python MyTradingSys/research/layer_lab/turn_of_candle_event_table/event_table.py --output <csv>` -> `rows=87552 ok=87491 not_in_data=61`. CSV deleted after counting.
