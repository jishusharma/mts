# RSI 40/60 reclaim - DEV event table (1h)

Date 2026-10-17. DEV only (bar open 2022-01-01 .. 2024-06-30); VALIDATION/HOLDOUT never loaded (npz sliced by `t` before bars are built). Gross R, no fees, no rules.

Command: `python MyTradingSys/research/layer_lab/rsi_reclaim_event_table/event_table.py` (no CSV written)

| | n | mean MFE (R) | mean MAE (R) |
|---|---|---|---|
| all OK | 982 | 2.8116 | 2.8662 |
| long (RSI reclaims 40 up) | 504 | 2.7947 | 2.8463 |
| short (RSI reclaims 60 down) | 478 | 2.8293 | 2.8872 |

Counts: 21,888 DEV 1h bars; 982 event rows; 982 OK; 0 NOT_IN_DATA (no gap in below-run/ATR/forward windows on this file).

Definitions: RSI14 = `rsi_core`; events = `rsi_reclaim_events` level 40 up / level 60 down, clearance 2.0 (OURS). Columns dwell_below, band_bars, depth are copied from the event; no retest filter, no bucket cut-offs. Entry = next bar open; R = ATR14 plain SMA of TR at the reclaim bar close (FORMULAS.md section 12); forward window 24 bars including the entry bar (OURS), measured by `forward_excursion`.

Reading: MFE and MAE are nearly equal and well above 1 ATR on both sides: a 24-bar window spans several ATR whichever way price goes, so the unbucketed table shows no directional edge. The dwell/depth/band columns are there for the later bucket cut; this report makes no claim about rules or net-of-cost results.

Tests: `python -m pytest MyTradingSys/research/layer_lab/rsi_reclaim_event_table` (14 pass; red before event_table.py existed). `lookahead_lint --new`: no hits on these files.
