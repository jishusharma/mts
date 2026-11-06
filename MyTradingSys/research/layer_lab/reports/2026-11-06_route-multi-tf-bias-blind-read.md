# Layer Lab Report: `route-multi-tf-bias-blind-read`

- **Card**: `route-multi-tf-bias-blind-read`
- **Date**: 2026-11-06 UTC
- **Deliverable**: `MyTradingSys/research/gemini_audits_2026-11-04/BLIND_READ_MULTI_TF_BIAS_1104.md`
- **Audit Outcome**: `VERDICT: MATCH`

## Findings

1. **Protocol Adherence**:
   - `RESULTS.csv` [SOURCED `MyTradingSys/research/multi_tf_bias_2026-10-18/RESULTS.csv:1-7`] and `study.py` [SOURCED `MyTradingSys/research/multi_tf_bias_2026-10-18/study.py:1-187`] read and verified before `REPORT.md` [SOURCED `MyTradingSys/research/multi_tf_bias_2026-10-18/REPORT.md:1-34`].
   - All 1,313,280 raw 1m kline rows from `F:/MTS/data/tom_raw/klines/BTCUSDT-1m-*.csv` [OURS] loaded and processed independently across 5,469 four-hourly decision timestamps.

2. **Headline Number Reproduction (36 Discrete Table Metrics, 100% Match)**:
   - **STACK**: n = 1348 [SOURCED `REPORT.md:9`, `RESULTS.csv:2`, OURS: 1348]; days = 524 [SOURCED `REPORT.md:9`, `RESULTS.csv:2`, OURS: 524]; mean net bps = -6.58 [SOURCED `REPORT.md:9`, `RESULTS.csv:2`, OURS: -6.5795]; SE = 5.62 [SOURCED `REPORT.md:9`, `RESULTS.csv:2`, OURS: 5.6205]; t = -1.17 [SOURCED `REPORT.md:9`, `RESULTS.csv:2` (-1.171), OURS: -1.1706]; gross = +5.42 bps [SOURCED `REPORT.md:9`, `RESULTS.csv:2` (5.42), OURS: +5.4205].
   - **1h-only**: n = 5469, days = 912, mean net = -9.75 bps, SE = 2.37 bps, t = -4.12, gross = +2.25 bps [SOURCED `REPORT.md:10`, `RESULTS.csv:3`, OURS].
   - **1D-only**: n = 5464, days = 911, mean net = -8.25 bps, SE = 3.06 bps, t = -2.70, gross = +3.75 bps [SOURCED `REPORT.md:11`, `RESULTS.csv:4`, OURS].
   - **ALL-LONG**: n = 5469, days = 912, mean net = -9.73 bps, SE = 3.06 bps, t = -3.18, gross = +2.27 bps [SOURCED `REPORT.md:12`, `RESULTS.csv:5`, OURS].
   - **1h-only filtered-out**: n = 4121, days = 907, mean net = -10.78 bps, SE = 2.88 bps, t = -3.74, gross = +1.22 bps [SOURCED `REPORT.md:13`, `RESULTS.csv:6`, OURS].
   - **1D-only filtered-out**: n = 4116, days = 906, mean net = -5.54 bps, SE = 3.30 bps, t = -1.68, gross = +6.46 bps [SOURCED `REPORT.md:14`, `RESULTS.csv:7`, OURS].

3. **Narrative Claims Verification**:
   - Filter gap: -6.58 bps - (-10.78 bps) = +4.20 bps [OURS], matches reported 4.2 bps [SOURCED `REPORT.md:5`]. Well within STACK SE (5.62 bps) [SOURCED `REPORT.md:5`].
   - Filter vs 1D trades: 1D filtered out net -5.54 bps vs stack -6.58 bps; gross +6.46 bps vs +5.42 bps [SOURCED `REPORT.md:22`, OURS].
   - All gross returns positive (+1.22 to +6.46 bps) [SOURCED `REPORT.md:21`, OURS], all net returns negative after 12.0 bps cost.
   - Power constraint: 2 * SE = 11.24 bps (~11 bps) [SOURCED `REPORT.md:34`, OURS].
   - 17 unit tests in `test_study.py` pass cleanly [SOURCED `REPORT.md:17`, command `python MyTradingSys/research/multi_tf_bias_2026-10-18/test_study.py`].

4. **Conclusion**:
   - Independent confirmation: NO NET EDGE SHOWN on DEV data.
   - Final status: VERDICT: MATCH.
