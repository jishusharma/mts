# Data notes

## raw_1d (Dumps/backtest/raw_1d/klines) is not the 1m resample (T01-F2)

- Finding: against the 1m resample (tom_raw) over 912 DEV days, 905 days differ on open, 0 on high/low/close, 847 on volume (max relative diff 12.01%, median 0).
- Reading: raw_1d is a distinct snapshot from a different Binance pull. Do not treat it as equal to the 1m-derived daily bar.
- Rule: new studies derive daily bars from 1m. Existing readers of raw_1d carry a `T01-F2` comment line (guarded by `MyTradingSys/tests/test_raw_1d_label.py`).
- Source: MyTradingSys/research/dsa_backtest_audit_2026-10-16/T01_data_forensics.md (T01-F2); scripts/T01/out/resample_summary.txt.
