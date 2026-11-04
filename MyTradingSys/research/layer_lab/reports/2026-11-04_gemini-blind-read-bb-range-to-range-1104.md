# Layer Lab Report: `gemini-blind-read-bb-range-to-range-1104`

- **Card**: `gemini-blind-read-bb-range-to-range-1104`
- **Date**: 2026-11-04 UTC
- **Deliverable**: `MyTradingSys/research/gemini_audits_2026-11-04/bb_range_to_range_blind_read.md`
- **Headline Counts**: `FOUND=52 DIFF=0 NOT_IN_DATA=1`

## Findings

1. **Exact Verification of `RESULT.md` against Saved Data Files (`FOUND=52, DIFF=0, NOT_IN_DATA=1`)**:
   - Every number, statistic, sample size $n$, active day count, confidence interval, $t$-statistic, and survivor outcome quoted in `MyTradingSys/research/bb_range_to_range_2026-11-04/RESULT.md` was cross-checked against `counts.csv`, `dev_cells.csv`, `dev_survivors.json`, and `regime_mix_count.txt`.
   - All 6 powered test cells (`15m`, `asia/london/ny`, `signal/retest` in `RESULT.md:10-15`) match `dev_cells.csv` and `counts.csv` exactly.
   - Descriptive slices (15m ungated, 15m bull regime, 15m late session, wide vs narrow band splits, long vs short splits, 1h and 4h timeframes, retest fill fraction) all match values in `dev_cells.csv` and `counts.csv` without discrepancies.
   - Zero survivors (`dev_survivors.json` is `[]`, 0 of 6 cells pass) confirmed.
   - Unit tests: all 7 wiring tests in `test_range_wiring.py` pass cleanly (`pytest` passes 7/7).
   - `NOT_IN_DATA=1`: Raw 1m kline bar files in `F:/MTS/Dumps/backtest` are absent on this host, as expected per card instructions ("NOT_IN_DATA when klines are absent on the host").
