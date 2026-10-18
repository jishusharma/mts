# CryptoCred market-structure break (MSB) - DEV event table (1h)

Date 2026-10-17. DEV only (bar open 2022-01-01 .. 2024-06-30); VALIDATION/HOLDOUT never loaded (npz sliced by `t` before bars are built). Gross R, no fees, no rules.

Command: `python MyTradingSys/research/layer_lab/cc_msb_event_table/event_table.py` (no CSV written)

| | n | mean MFE (R) | mean MAE (R) |
|---|---|---|---|
| all OK | 830 | 3.3400 | 3.1092 |
| up break (long) | 414 | 3.3319 | 3.0785 |
| down break (short) | 416 | 3.3481 | 3.1399 |

Counts: 21,888 DEV 1h bars; 831 event rows; 830 OK; 1 NOT_IN_DATA (a data gap inside the swing, ATR or forward window).

Definitions: `find_swings` (left 2, right 2, use_body True) then `classify_msb` (require_prior_sequence True, filter_range_noise False) from `cc_structure.py`, read only. One row per event; up = close above the most recent confirmed lower high (long), down = close below the most recent confirmed higher low (short). Entry = next bar open; R = ATR14 plain SMA of TR at the break bar close (FORMULAS.md section 12); forward window 24 bars including the entry bar (OURS), measured by `forward_excursion`. Columns: event_t, swing_t, direction, side, entry_t, entry, risk_r, mfe_R, mae_R, bars_forward, status.

Reading: MFE and MAE are nearly equal and above 3 ATR on both sides: a 24-bar window spans several ATR whichever way price goes, so the unconditioned table shows no directional edge. This report makes no claim about rules or net-of-cost results.

Tests: `python -m pytest MyTradingSys/research/layer_lab/cc_msb_event_table` (8 pass; red before event_table.py existed). `lookahead_lint --new`: no hits on these files.
