# Bigtrade event table — 2026-10-16

**CONTAMINATED (DEV read VALIDATION 2024-07..12)**: DEV end was 2025-01-01; corrected in bigtrade_event_table/DEV_BOUNDARY_FIX_2026-10-17.md (128,078 rows, 5,685 OK).

**Build result:** 153,685 DEV fire rows; 6,748 measured and 146,937 marked `NOT_IN_DATA`. Test suite: 4 passed.

## Work and evidence

- [event_table.py](/F:/MTS/mts-codex-lab/MyTradingSys/research/layer_lab/bigtrade_event_table/event_table.py:15) defines DEV as 2022-01-01 to 2025-01-01 UTC, uses a 20-bar horizon, excludes the fire bar from excursions, and clips forward bars at the DEV end.
- [fires_kline.py](/F:/MTS/mts-codex-lab/MyTradingSys/backtest/bigtrade/fires_kline.py:445) records `t_fire_ms` at the firing bar close; cached arrays contain candle open times. The table loader adds the timeframe duration before matching.
- Command: `python MyTradingSys/research/layer_lab/bigtrade_event_table/event_table.py --output MyTradingSys/research/layer_lab/bigtrade_event_table/event_table.csv` -> 153,685 rows (6,748 OK; 146,937 `NOT_IN_DATA`). 1m: 105,209 missing; 5m: 25,878 missing; 15m: 5,400 OK / 13,046 missing; 1h: 1,348 OK / 2,804 missing.
- Test-first evidence: before the implementation, pytest collection failed with `FileNotFoundError` for `event_table.py`. After implementation: `python -m pytest MyTradingSys/research/layer_lab/bigtrade_event_table/test_event_table.py -q -p no:cacheprovider` -> `4 passed in 0.39s`.
- [REPORT.md](/F:/MTS/mts-codex-lab/MyTradingSys/research/layer_lab/bigtrade_event_table/REPORT.md:1) records methodology, data range, counts, and test output. The generated [event_table.csv](/F:/MTS/mts-codex-lab/MyTradingSys/research/layer_lab/bigtrade_event_table/event_table.csv) preserves missing cases explicitly.

No trading rule or parameter was changed; no tuning trial was run.
