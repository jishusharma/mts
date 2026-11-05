# Data notes

## raw_1d (Dumps/backtest/raw_1d/klines) is not the 1m resample (T01-F2)

- Finding: against the 1m resample (tom_raw) over 912 DEV days, 905 days differ on open, 0 on high/low/close, 847 on volume (max relative diff 12.01%, median 0).
- Reading: raw_1d is a distinct snapshot from a different Binance pull. Do not treat it as equal to the 1m-derived daily bar.
- Rule: new studies derive daily bars from 1m. Existing readers of raw_1d carry a `T01-F2` comment line (guarded by `MyTradingSys/tests/test_raw_1d_label.py`).
- Source: MyTradingSys/research/dsa_backtest_audit_2026-10-16/T01_data_forensics.md (T01-F2); scripts/T01/out/resample_summary.txt.

## Futures metrics (OI, long/short ratios) live in one shared root

- Path: `MTS_METRICS_ROOT` (else `MTS_DATA_ROOT`/metrics); fleet path F:/MTS/data/metrics/<SYMBOL>/<SYMBOL>-metrics-YYYY-MM-DD.csv. Fetcher: `MyTradingSys/backtest/fetch_futures_metrics.py` (public data.binance.vision, SHA256-checked, re-run skips present days).
- Coverage 2026-11-05: BTCUSDT and ETHUSDT 2022-01-01..2026-11-04, 1769/1769 days each, 0 missing (2026-11-04 topped up on the re-land run; a re-run fetched only that day).
- Short days (rows of 288): 2023-09-12 285, 2024-02-16 163, 2024-10-28 286, 2025-08-29 285 (same on both symbols).
- Top-trader and global ratio columns are blank on 91,781 of 509,051 rows, last blank day 2022-12-13: ratio studies start 2022-12-14.
- Older copy F:/MTS/data/binance_metrics (BTCUSDT 2022-2025 only) is superseded.
