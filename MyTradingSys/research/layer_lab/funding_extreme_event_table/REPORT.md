# Funding extreme event table

**Verdict: BUILT** — DEV-only funding event table with trailing PIT 90-print 95th-percentile flags and 24h forward excursions in ATR14 units.

`event_table.py` reads funding history from the local BTCUSDT monthly funding zips and takes the 1h OHLC/ATR14 archive. It emits one row per DEV funding print. The percentile uses the 90 immediately preceding absolute rates and excludes the current print; a positive funding print is faded short and a negative print is faded long. Entry price and R denominator use the close and ATR14 of the last fully completed 1h bar before the print, so the still-open bar cannot leak into the entry. MFE/MAE use high/low over 24 forward 1h bars. Fewer than 90 prior prints, missing entry ATR, missing klines, or an incomplete horizon are `NOT_IN_DATA`.

Data run: DEV 2022-01-01 through 2024-06-30 only. The funding loader does not open archives from July 2024 onward; the kline loader slices timestamps to `< 2024-07-01`. No validation or holdout data was read.

| Count | Result |
|---|---:|
| Funding prints | 2,736 |
| Initial rows without 90 prior prints | 90 `NOT_IN_DATA` |
| Rows with available baseline | 2,646 |
| Extreme events | 726 (695 short fades, 31 long fades) |
| Extreme events with complete 24-bar forward window | 726 |

Test-first evidence: before implementation, pytest collection failed because `event_table.py` did not exist. Final command `python -m pytest MyTradingSys/research/layer_lab/funding_extreme_event_table/test_event_table.py -q -p no:cacheprovider` -> **5 passed**. The synthetic fixtures hand-check the 95th percentile (`0.008455`), current-print exclusion, insufficient history, missing klines, fade side, no use of the open bar's close, and 24-bar cutoff.

Wiring: test listed in `scripts/dev/run_extra_tests.py`; module registered as research-only TOOL in `MyTradingSys/system/wiring_registry.json`. No trading rule or tuning is included.
