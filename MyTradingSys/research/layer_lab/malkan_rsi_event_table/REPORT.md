# Malkan 40/60 RSI bounce - DEV event table (1h)

Date 2026-10-17. DEV only (bar open 2022-01-01 .. 2024-06-30); VALIDATION/HOLDOUT never loaded (npz sliced by `t` before bars are built). Gross R, no fees, no rules.

Command: `python MyTradingSys/research/layer_lab/malkan_rsi_event_table/event_table.py` (no CSV written)

| | n | mean MFE (R) | mean MAE (R) |
|---|---|---|---|
| all OK | 132 | 3.1810 | 3.0644 |
| long (bull bounce at 40) | 59 | 3.1578 | 2.7976 |
| short (bear reject at 60) | 73 | 3.1996 | 3.2800 |

Counts: 21,888 DEV 1h bars; 132 event rows; 132 OK; 0 NOT_IN_DATA (no gap in lookback/ATR/forward windows on this file).

Definitions: RSI14 = `rsi_core`; regime = `malkan_regime` (40/60, lookback 20); events = `malkan_setup_bull`/`malkan_setup_bear` defaults (tolerance 2.0, candle colour required). Entry = next bar open; R = ATR14 plain SMA of TR at the event bar close (FORMULAS.md section 12); forward window 24 bars including the entry bar (OURS), measured by `forward_excursion`.

Reading: MFE and MAE are nearly equal and large relative to 1 ATR: a 24-bar window spans several ATR whichever way price goes, so the table shows no directional edge by itself. Event enumeration only; no claim about rules or net-of-cost results.

Tests: `python -m pytest MyTradingSys/research/layer_lab/malkan_rsi_event_table` (10 pass; red before event_table.py existed).
