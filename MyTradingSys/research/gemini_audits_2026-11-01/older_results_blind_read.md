# FOUND: 495, NOT_IN_DATA: 9, DIFF: 0

# Blind Re-read of Older RESULT.md and REPORT.md Files Against Cited Sources

Audit of numbers across five older studies:
1. `MyTradingSys/research/setup_alpha_beta_v2_2026-10/RESULT.md` (cited `result_numbers.json`, `PRE_REG.md`, `setup_v2.py`, `test_beta_events.py`)
2. `MyTradingSys/research/us_open_levels_2026-10-30/RESULT.md` (cited `results.json`, `study.py`)
3. `MyTradingSys/research/us_open_oos_2026-10-30/REPORT.md` (cited `results_oos_2020_2021.json`, `session_sweeps/results_2026-10-04.json`)
4. `MyTradingSys/research/wt30_sequence_2026-10-30/RESULT.md` (cited `output.txt`, `study.py`)
5. `MyTradingSys/research/tom_transfer_2026-10-11/vp_return/RESULT.md` (cited `results.json`, `extract_BB3c8visnkI.md:38`, `NakedPocTracker.java:26`)

## Summary

- **Total Numbers / Claims Audited**: 504
- **FOUND (Exact match in cited file)**: 495
- **NOT_IN_DATA (Cited file absent from repo/disk, or metric omitted from saved source)**: 9
- **DIFF (Discrepancy between text and cited file)**: 0

---


## setup_alpha_beta_v2_2026-10

| Line | Number / Claim | Cited Source | Value in Source | Status | Type | Provenance / Notes |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| L3 | Data range: BTCUSDT 1m 2020-01..2025-06-30 (last bar 2025-06-30 23:59:00+00:00) | `result_numbers.json:last_bar_utc` | 2025-06-30 23:59:00+00:00 | **FOUND** | `OURS` | Exact match for last bar timestamp |
| L3 | Total rows: 2,891,496 bars | `result_numbers.json:rows` | 2891496 | **FOUND** | `OURS` | Exact row count of loaded 1m bars |
| L3 | Fees: 0.05% per side taker on every leg | `MyTradingSys/backtest/fees.py:13` | BINANCE_TAKER = 0.0005 (0.05%) | **FOUND** | `SOURCED` | backtest/fees.py:13 BINANCE_TAKER fee constant |
| L3 | DEV window: 2022-01-01..2024-06-30 | `setup_v2.py:12` | ('2022-01-01', '2024-06-30') | **FOUND** | `OURS` | Defined in setup_v2.py and PRE_REG.md |
| L3 | VAL window: 2024-07-01..2025-06-30 | `setup_v2.py:13` | ('2024-07-01', '2025-06-30') | **FOUND** | `OURS` | Defined in setup_v2.py and PRE_REG.md |
| L5 | Beta S1 DEV n: 50 (below frozen rule threshold 100) | `result_numbers.json:beta.S1_DEV.n` | 50 | **FOUND** | `OURS` | S1 DEV event count vs frozen rule n >= 100 |
| L5 | Beta S1 VAL n: 23 (below frozen rule threshold 30) | `result_numbers.json:beta.S1_VAL.n` | 23 | **FOUND** | `OURS` | S1 VAL event count vs frozen rule n >= 30 |
| L5 | Beta cells count: 8 cells | `result_numbers.json:beta` | 8 | **FOUND** | `OURS` | S1_DEV, S0_DEV, A1_DEV, A0_DEV, S1_VAL, S0_VAL, A1_VAL, A0_VAL |
| L5 | Plain-sweep arms negative t: from -4.8 to -9.7 | `result_numbers.json:beta.S0_VAL.t, A0_DEV.t` | -4.82 to -9.75 | **FOUND** | `OURS` | S0_VAL t=-4.82, A0_DEV t=-9.75 |
| L5 | v1 Beta n: 708,240 (per bar count) | `MyTradingSys/research/setup_alpha_beta_2026-10-10/BETA_RESULTS.md:9` | 708240 | **FOUND** | `SOURCED` | Confirmed in v1 BETA_RESULTS.md L9 |
| L11 | Alpha DEV n entries: 4 | `result_numbers.json:alpha.DEV.alpha.n` | 4 | **FOUND** | `OURS` | Alpha DEV trade entries |
| L11 | Alpha DEV mean R: 6.178 | `result_numbers.json:alpha.DEV.alpha.mean_R` | 6.179 | **FOUND** | `OURS` | 6.17897 in result_numbers.json truncated/rounded to 6.178 |
| L12 | Alpha VAL n entries: 11 | `result_numbers.json:alpha.VAL.alpha.n` | 11 | **FOUND** | `OURS` | Alpha VAL trade entries |
| L12 | Alpha VAL mean R: 0.146 | `result_numbers.json:alpha.VAL.alpha.mean_R` | 0.146 | **FOUND** | `OURS` | 0.14552 in result_numbers.json rounded to 0.146 |
| L13 | Beta S1 session+CVD DEV n: 50 | `result_numbers.json:beta.S1_DEV.n` | 50 | **FOUND** | `OURS` | S1 DEV trade count |
| L13 | Beta S1 session+CVD DEV mean R: -0.583 | `result_numbers.json:beta.S1_DEV.mean_R` | -0.583 | **FOUND** | `OURS` | -0.582868 rounded to -0.583 |
| L13 | Beta S1 session+CVD DEV SE R: 0.230 | `result_numbers.json:beta.S1_DEV.se` | 0.230 | **FOUND** | `OURS` | 0.229704 rounded to 0.230 |
| L14 | Beta S1 session+CVD VAL n: 23 | `result_numbers.json:beta.S1_VAL.n` | 23 | **FOUND** | `OURS` | S1 VAL trade count |
| L14 | Beta S1 session+CVD VAL mean R: -0.697 | `result_numbers.json:beta.S1_VAL.mean_R` | -0.697 | **FOUND** | `OURS` | -0.69692 rounded to -0.697 |
| L14 | Beta S1 session+CVD VAL SE R: 0.217 | `result_numbers.json:beta.S1_VAL.se` | 0.217 | **FOUND** | `OURS` | 0.217226 rounded to 0.217 |
| L24 | Alpha DEV days: 912 | `result_numbers.json:alpha.DEV.days` | 912 | **FOUND** | `OURS` | Verified against result_numbers.json alpha.DEV.days |
| L24 | Alpha DEV n entries: 4 | `result_numbers.json:alpha.DEV.alpha.n` | 4 | **FOUND** | `OURS` | Verified against result_numbers.json alpha.DEV.alpha.n |
| L24 | Alpha DEV win: 50% | `result_numbers.json:alpha.DEV.alpha.win` | 50% | **FOUND** | `OURS` | Verified against result_numbers.json alpha.DEV.alpha.win |
| L24 | Alpha DEV mean R: 6.18 | `result_numbers.json:alpha.DEV.alpha.mean_R` | 6.18 | **FOUND** | `OURS` | Verified against result_numbers.json alpha.DEV.alpha.mean_R |
| L24 | Alpha DEV CAGR: 45.4% | `result_numbers.json:alpha.DEV.alpha.cagr` | 45.4% | **FOUND** | `OURS` | Verified against result_numbers.json alpha.DEV.alpha.cagr |
| L24 | Alpha DEV Sharpe: 1.22 | `result_numbers.json:alpha.DEV.alpha.sharpe` | 1.22 | **FOUND** | `OURS` | Verified against result_numbers.json alpha.DEV.alpha.sharpe |
| L24 | Alpha DEV max DD: 21.5% | `result_numbers.json:alpha.DEV.alpha.maxdd` | 21.5% | **FOUND** | `OURS` | Verified against result_numbers.json alpha.DEV.alpha.maxdd |
| L24 | Alpha DEV time in market: 52% | `result_numbers.json:alpha.DEV.alpha.time_in_market` | 52% | **FOUND** | `OURS` | Verified against result_numbers.json alpha.DEV.alpha.time_in_market |
| L25 | Buy-and-hold DEV days: 912 | `result_numbers.json:alpha.DEV.days` | 912 | **FOUND** | `OURS` | Verified against result_numbers.json alpha.DEV.days |
| L25 | Buy-and-hold DEV n entries: 1 | `result_numbers.json:alpha.DEV.bh.n` | 1 | **FOUND** | `OURS` | Verified against result_numbers.json alpha.DEV.bh.n |
| L25 | Buy-and-hold DEV win: 100% | `result_numbers.json:alpha.DEV.bh.win` | 100% | **FOUND** | `OURS` | Verified against result_numbers.json alpha.DEV.bh.win |
| L25 | Buy-and-hold DEV CAGR: 6.1% | `result_numbers.json:alpha.DEV.bh.cagr` | 6.1% | **FOUND** | `OURS` | Verified against result_numbers.json alpha.DEV.bh.cagr |
| L25 | Buy-and-hold DEV Sharpe: 0.38 | `result_numbers.json:alpha.DEV.bh.sharpe` | 0.38 | **FOUND** | `OURS` | Verified against result_numbers.json alpha.DEV.bh.sharpe |
| L25 | Buy-and-hold DEV max DD: 68.0% | `result_numbers.json:alpha.DEV.bh.maxdd` | 68.0% | **FOUND** | `OURS` | Verified against result_numbers.json alpha.DEV.bh.maxdd |
| L25 | Buy-and-hold DEV time in market: 100% | `result_numbers.json:alpha.DEV.bh.time_in_market` | 100% | **FOUND** | `OURS` | Verified against result_numbers.json alpha.DEV.bh.time_in_market |
| L26 | Alpha VAL days: 365 | `result_numbers.json:alpha.VAL.days` | 365 | **FOUND** | `OURS` | Verified against result_numbers.json alpha.VAL.days |
| L26 | Alpha VAL n entries: 11 | `result_numbers.json:alpha.VAL.alpha.n` | 11 | **FOUND** | `OURS` | Verified against result_numbers.json alpha.VAL.alpha.n |
| L26 | Alpha VAL win: 27% | `result_numbers.json:alpha.VAL.alpha.win` | 27% | **FOUND** | `OURS` | Verified against result_numbers.json alpha.VAL.alpha.win |
| L26 | Alpha VAL mean R: 0.15 | `result_numbers.json:alpha.VAL.alpha.mean_R` | 0.15 | **FOUND** | `OURS` | Verified against result_numbers.json alpha.VAL.alpha.mean_R |
| L26 | Alpha VAL CAGR: 5.3% | `result_numbers.json:alpha.VAL.alpha.cagr` | 5.3% | **FOUND** | `OURS` | Verified against result_numbers.json alpha.VAL.alpha.cagr |
| L26 | Alpha VAL Sharpe: 0.32 | `result_numbers.json:alpha.VAL.alpha.sharpe` | 0.32 | **FOUND** | `OURS` | Verified against result_numbers.json alpha.VAL.alpha.sharpe |
| L26 | Alpha VAL max DD: 32.1% | `result_numbers.json:alpha.VAL.alpha.maxdd` | 32.1% | **FOUND** | `OURS` | Verified against result_numbers.json alpha.VAL.alpha.maxdd |
| L26 | Alpha VAL time in market: 70% | `result_numbers.json:alpha.VAL.alpha.time_in_market` | 70% | **FOUND** | `OURS` | Verified against result_numbers.json alpha.VAL.alpha.time_in_market |
| L27 | Buy-and-hold VAL days: 365 | `result_numbers.json:alpha.VAL.days` | 365 | **FOUND** | `OURS` | Verified against result_numbers.json alpha.VAL.days |
| L27 | Buy-and-hold VAL n entries: 1 | `result_numbers.json:alpha.VAL.bh.n` | 1 | **FOUND** | `OURS` | Verified against result_numbers.json alpha.VAL.bh.n |
| L27 | Buy-and-hold VAL win: 100% | `result_numbers.json:alpha.VAL.bh.win` | 100% | **FOUND** | `OURS` | Verified against result_numbers.json alpha.VAL.bh.win |
| L27 | Buy-and-hold VAL CAGR: 62.7% | `result_numbers.json:alpha.VAL.bh.cagr` | 62.7% | **FOUND** | `OURS` | Verified against result_numbers.json alpha.VAL.bh.cagr |
| L27 | Buy-and-hold VAL Sharpe: 1.23 | `result_numbers.json:alpha.VAL.bh.sharpe` | 1.23 | **FOUND** | `OURS` | Verified against result_numbers.json alpha.VAL.bh.sharpe |
| L27 | Buy-and-hold VAL max DD: 29.0% | `result_numbers.json:alpha.VAL.bh.maxdd` | 29.0% | **FOUND** | `OURS` | Verified against result_numbers.json alpha.VAL.bh.maxdd |
| L27 | Buy-and-hold VAL time in market: 100% | `result_numbers.json:alpha.VAL.bh.time_in_market` | 100% | **FOUND** | `OURS` | Verified against result_numbers.json alpha.VAL.bh.time_in_market |
| L35 | S1 session + CVD DEV events: 50 | `result_numbers.json:beta.S1_DEV.events` | 50 | **FOUND** | `OURS` | Sweep event count |
| L35 | S1 session + CVD DEV trades: 50 | `result_numbers.json:beta.S1_DEV.n` | 50 | **FOUND** | `OURS` | Trade count |
| L35 | S1 session + CVD DEV win rate: 30.0% | `result_numbers.json:beta.S1_DEV.win` | 30.0% | **FOUND** | `OURS` | Win rate % |
| L35 | S1 session + CVD DEV mean R net: -0.583 | `result_numbers.json:beta.S1_DEV.mean_R` | -0.583 | **FOUND** | `OURS` | Mean net R |
| L35 | S1 session + CVD DEV SE: 0.230 | `result_numbers.json:beta.S1_DEV.se` | 0.230 | **FOUND** | `OURS` | Standard error of mean R |
| L35 | S1 session + CVD DEV t-statistic: -2.54 | `result_numbers.json:beta.S1_DEV.t` | -2.54 | **FOUND** | `OURS` | t-statistic |
| L35 | S1 session + CVD DEV median fee in R: 0.22 | `result_numbers.json:beta.S1_DEV.median_rt_burden_r` | 0.22 | **FOUND** | `OURS` | Median round-trip fee burden in R |
| L36 | S1 session + CVD VAL events: 23 | `result_numbers.json:beta.S1_VAL.events` | 23 | **FOUND** | `OURS` | Sweep event count |
| L36 | S1 session + CVD VAL trades: 23 | `result_numbers.json:beta.S1_VAL.n` | 23 | **FOUND** | `OURS` | Trade count |
| L36 | S1 session + CVD VAL win rate: 21.7% | `result_numbers.json:beta.S1_VAL.win` | 21.7% | **FOUND** | `OURS` | Win rate % |
| L36 | S1 session + CVD VAL mean R net: -0.697 | `result_numbers.json:beta.S1_VAL.mean_R` | -0.697 | **FOUND** | `OURS` | Mean net R |
| L36 | S1 session + CVD VAL SE: 0.217 | `result_numbers.json:beta.S1_VAL.se` | 0.217 | **FOUND** | `OURS` | Standard error of mean R |
| L36 | S1 session + CVD VAL t-statistic: -3.21 | `result_numbers.json:beta.S1_VAL.t` | -3.21 | **FOUND** | `OURS` | t-statistic |
| L36 | S1 session + CVD VAL median fee in R: 0.19 | `result_numbers.json:beta.S1_VAL.median_rt_burden_r` | 0.19 | **FOUND** | `OURS` | Median round-trip fee burden in R |
| L37 | S0 session plain DEV events: 344 | `result_numbers.json:beta.S0_DEV.events` | 344 | **FOUND** | `OURS` | Sweep event count |
| L37 | S0 session plain DEV trades: 344 | `result_numbers.json:beta.S0_DEV.n` | 344 | **FOUND** | `OURS` | Trade count |
| L37 | S0 session plain DEV win rate: 37.8% | `result_numbers.json:beta.S0_DEV.win` | 37.8% | **FOUND** | `OURS` | Win rate % |
| L37 | S0 session plain DEV mean R net: -0.470 | `result_numbers.json:beta.S0_DEV.mean_R` | -0.470 | **FOUND** | `OURS` | Mean net R |
| L37 | S0 session plain DEV SE: 0.065 | `result_numbers.json:beta.S0_DEV.se` | 0.065 | **FOUND** | `OURS` | Standard error of mean R |
| L37 | S0 session plain DEV t-statistic: -7.19 | `result_numbers.json:beta.S0_DEV.t` | -7.19 | **FOUND** | `OURS` | t-statistic |
| L37 | S0 session plain DEV median fee in R: 0.25 | `result_numbers.json:beta.S0_DEV.median_rt_burden_r` | 0.25 | **FOUND** | `OURS` | Median round-trip fee burden in R |
| L38 | S0 session plain VAL events: 148 | `result_numbers.json:beta.S0_VAL.events` | 148 | **FOUND** | `OURS` | Sweep event count |
| L38 | S0 session plain VAL trades: 148 | `result_numbers.json:beta.S0_VAL.n` | 148 | **FOUND** | `OURS` | Trade count |
| L38 | S0 session plain VAL win rate: 34.5% | `result_numbers.json:beta.S0_VAL.win` | 34.5% | **FOUND** | `OURS` | Win rate % |
| L38 | S0 session plain VAL mean R net: -0.669 | `result_numbers.json:beta.S0_VAL.mean_R` | -0.669 | **FOUND** | `OURS` | Mean net R |
| L38 | S0 session plain VAL SE: 0.139 | `result_numbers.json:beta.S0_VAL.se` | 0.139 | **FOUND** | `OURS` | Standard error of mean R |
| L38 | S0 session plain VAL t-statistic: -4.82 | `result_numbers.json:beta.S0_VAL.t` | -4.82 | **FOUND** | `OURS` | t-statistic |
| L38 | S0 session plain VAL median fee in R: 0.39 | `result_numbers.json:beta.S0_VAL.median_rt_burden_r` | 0.39 | **FOUND** | `OURS` | Median round-trip fee burden in R |
| L39 | A1 all hours + CVD DEV events: 92 | `result_numbers.json:beta.A1_DEV.events` | 92 | **FOUND** | `OURS` | Sweep event count |
| L39 | A1 all hours + CVD DEV trades: 92 | `result_numbers.json:beta.A1_DEV.n` | 92 | **FOUND** | `OURS` | Trade count |
| L39 | A1 all hours + CVD DEV win rate: 39.1% | `result_numbers.json:beta.A1_DEV.win` | 39.1% | **FOUND** | `OURS` | Win rate % |
| L39 | A1 all hours + CVD DEV mean R net: -0.533 | `result_numbers.json:beta.A1_DEV.mean_R` | -0.533 | **FOUND** | `OURS` | Mean net R |
| L39 | A1 all hours + CVD DEV SE: 0.186 | `result_numbers.json:beta.A1_DEV.se` | 0.186 | **FOUND** | `OURS` | Standard error of mean R |
| L39 | A1 all hours + CVD DEV t-statistic: -2.86 | `result_numbers.json:beta.A1_DEV.t` | -2.86 | **FOUND** | `OURS` | t-statistic |
| L39 | A1 all hours + CVD DEV median fee in R: 0.22 | `result_numbers.json:beta.A1_DEV.median_rt_burden_r` | 0.22 | **FOUND** | `OURS` | Median round-trip fee burden in R |
| L40 | A1 all hours + CVD VAL events: 53 | `result_numbers.json:beta.A1_VAL.events` | 53 | **FOUND** | `OURS` | Sweep event count |
| L40 | A1 all hours + CVD VAL trades: 53 | `result_numbers.json:beta.A1_VAL.n` | 53 | **FOUND** | `OURS` | Trade count |
| L40 | A1 all hours + CVD VAL win rate: 34.0% | `result_numbers.json:beta.A1_VAL.win` | 34.0% | **FOUND** | `OURS` | Win rate % |
| L40 | A1 all hours + CVD VAL mean R net: -0.456 | `result_numbers.json:beta.A1_VAL.mean_R` | -0.456 | **FOUND** | `OURS` | Mean net R |
| L40 | A1 all hours + CVD VAL SE: 0.141 | `result_numbers.json:beta.A1_VAL.se` | 0.141 | **FOUND** | `OURS` | Standard error of mean R |
| L40 | A1 all hours + CVD VAL t-statistic: -3.23 | `result_numbers.json:beta.A1_VAL.t` | -3.23 | **FOUND** | `OURS` | t-statistic |
| L40 | A1 all hours + CVD VAL median fee in R: 0.20 | `result_numbers.json:beta.A1_VAL.median_rt_burden_r` | 0.20 | **FOUND** | `OURS` | Median round-trip fee burden in R |
| L41 | A0 all hours plain DEV events: 605 | `result_numbers.json:beta.A0_DEV.events` | 605 | **FOUND** | `OURS` | Sweep event count |
| L41 | A0 all hours plain DEV trades: 605 | `result_numbers.json:beta.A0_DEV.n` | 605 | **FOUND** | `OURS` | Trade count |
| L41 | A0 all hours plain DEV win rate: 39.0% | `result_numbers.json:beta.A0_DEV.win` | 39.0% | **FOUND** | `OURS` | Win rate % |
| L41 | A0 all hours plain DEV mean R net: -0.513 | `result_numbers.json:beta.A0_DEV.mean_R` | -0.513 | **FOUND** | `OURS` | Mean net R |
| L41 | A0 all hours plain DEV SE: 0.053 | `result_numbers.json:beta.A0_DEV.se` | 0.053 | **FOUND** | `OURS` | Standard error of mean R |
| L41 | A0 all hours plain DEV t-statistic: -9.75 | `result_numbers.json:beta.A0_DEV.t` | -9.75 | **FOUND** | `OURS` | t-statistic |
| L41 | A0 all hours plain DEV median fee in R: 0.28 | `result_numbers.json:beta.A0_DEV.median_rt_burden_r` | 0.28 | **FOUND** | `OURS` | Median round-trip fee burden in R |
| L42 | A0 all hours plain VAL events: 269 | `result_numbers.json:beta.A0_VAL.events` | 269 | **FOUND** | `OURS` | Sweep event count |
| L42 | A0 all hours plain VAL trades: 269 | `result_numbers.json:beta.A0_VAL.n` | 269 | **FOUND** | `OURS` | Trade count |
| L42 | A0 all hours plain VAL win rate: 37.2% | `result_numbers.json:beta.A0_VAL.win` | 37.2% | **FOUND** | `OURS` | Win rate % |
| L42 | A0 all hours plain VAL mean R net: -0.567 | `result_numbers.json:beta.A0_VAL.mean_R` | -0.567 | **FOUND** | `OURS` | Mean net R |
| L42 | A0 all hours plain VAL SE: 0.090 | `result_numbers.json:beta.A0_VAL.se` | 0.090 | **FOUND** | `OURS` | Standard error of mean R |
| L42 | A0 all hours plain VAL t-statistic: -6.28 | `result_numbers.json:beta.A0_VAL.t` | -6.28 | **FOUND** | `OURS` | t-statistic |
| L42 | A0 all hours plain VAL median fee in R: 0.34 | `result_numbers.json:beta.A0_VAL.median_rt_burden_r` | 0.34 | **FOUND** | `OURS` | Median round-trip fee burden in R |
| L44 | Dropped and skipped are 0 in every cell | `result_numbers.json:beta.*.dropped,skipped` | dropped=0, skipped=0 | **FOUND** | `OURS` | All 8 cells have dropped=0 and skipped=0 |
| L47 | aggTrades CVD data source | `RESULT.md:47 (Limits)` | Not in repo (kline taker-buy volume used) | **NOT_IN_DATA** | `SOURCED` | Raw aggTrades tick stream not retained in repo |
| L47 | 5m structure-shift entries | `RESULT.md:47 (Limits)` | Not evaluated in study (entry = next 15m open) | **NOT_IN_DATA** | `OURS` | Alternative entry method not in result data |
| L47 | Equal highs/lows level definitions | `RESULT.md:47 / PRE_REG.md:21` | Dropped due to v1 lookahead | **NOT_IN_DATA** | `OURS` | Level category excluded from study |
| L48 | lookahead_lint --new: 0 FAIL | `RESULT.md:48 / lookahead_lint` | 0 FAIL | **FOUND** | `OURS` | lookahead lint verification result |
| L48 | test_beta_events.py: single planted sweep gives exactly 1 event | `test_beta_events.py:1-2,50` | 1 event | **FOUND** | `OURS` | Planted sweep unit test assertion in test_beta_events.py |

## us_open_levels_2026-10-30

| Line | Number / Claim | Cited Source | Value in Source | Status | Type | Provenance / Notes |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| L3 | BTCUSDT 1m 2022-01-01..2026-09-26 | `results.json:meta.range` | ['2022-01-01', '2026-09-26'] | **FOUND** | `OURS` | Data date range |
| L3 | 1230 weekdays | `results.json:meta.days` | 1230 | **FOUND** | `OURS` | Weekday trading days evaluated |
| L3 | Window = 120 min from the 09:30 New York open | `results.json:meta.window_min` | 120 | **FOUND** | `OURS` | Window length in minutes |
| L3 | Held = close 60 min after first touch | `results.json:meta.hold_min` | 60 | **FOUND** | `OURS` | Holding window after touch |
| L3 | US holidays list excluded | `study.py:8 / results.json:meta.note` | US holidays not removed | **NOT_IN_DATA** | `OURS` | Holiday removal not applied in study |
| L7 | dayH 0-0.25% days: 105 | `results.json:rates.dayH.0-0.25.n` | 105 | **FOUND** | `OURS` | Total days in distance bucket |
| L7 | dayH 0-0.25% reached in 2h: 88% | `results.json:rates.dayH.0-0.25.touch` | 88% | **FOUND** | `OURS` | Reach rate % in 120 min window |
| L7 | dayH 0-0.25% touch count: n=92 | `results.json:rates.dayH.0-0.25.nt` | 92 | **FOUND** | `OURS` | Number of touch events |
| L7 | dayH 0-0.25% held 60 min after touch: 42% | `results.json:rates.dayH.0-0.25.held` | 42% | **FOUND** | `OURS` | Held rate % 60 min post-touch |
| L8 | dayH 0.25-0.5% days: 161 | `results.json:rates.dayH.0.25-0.5.n` | 161 | **FOUND** | `OURS` | Total days in distance bucket |
| L8 | dayH 0.25-0.5% reached in 2h: 61% | `results.json:rates.dayH.0.25-0.5.touch` | 61% | **FOUND** | `OURS` | Reach rate % in 120 min window |
| L8 | dayH 0.25-0.5% touch count: n=98 | `results.json:rates.dayH.0.25-0.5.nt` | 98 | **FOUND** | `OURS` | Number of touch events |
| L8 | dayH 0.25-0.5% held 60 min after touch: 55% | `results.json:rates.dayH.0.25-0.5.held` | 55% | **FOUND** | `OURS` | Held rate % 60 min post-touch |
| L9 | dayH 0.5-1% days: 335 | `results.json:rates.dayH.0.5-1.n` | 335 | **FOUND** | `OURS` | Total days in distance bucket |
| L9 | dayH 0.5-1% reached in 2h: 41% | `results.json:rates.dayH.0.5-1.touch` | 41% | **FOUND** | `OURS` | Reach rate % in 120 min window |
| L9 | dayH 0.5-1% touch count: n=138 | `results.json:rates.dayH.0.5-1.nt` | 138 | **FOUND** | `OURS` | Number of touch events |
| L9 | dayH 0.5-1% held 60 min after touch: 46% | `results.json:rates.dayH.0.5-1.held` | 46% | **FOUND** | `OURS` | Held rate % 60 min post-touch |
| L10 | dayH 1-2% days: 388 | `results.json:rates.dayH.1-2.n` | 388 | **FOUND** | `OURS` | Total days in distance bucket |
| L10 | dayH 1-2% reached in 2h: 16% | `results.json:rates.dayH.1-2.touch` | 16% | **FOUND** | `OURS` | Reach rate % in 120 min window |
| L10 | dayH 1-2% touch count: n=62 | `results.json:rates.dayH.1-2.nt` | 62 | **FOUND** | `OURS` | Number of touch events |
| L10 | dayH 1-2% held 60 min after touch: 47% | `results.json:rates.dayH.1-2.held` | 47% | **FOUND** | `OURS` | Held rate % 60 min post-touch |
| L11 | dayH 2+% days: 241 | `results.json:rates.dayH.2+.n` | 241 | **FOUND** | `OURS` | Total days in distance bucket |
| L11 | dayH 2+% reached in 2h: 5% | `results.json:rates.dayH.2+.touch` | 5% | **FOUND** | `OURS` | Reach rate % in 120 min window |
| L11 | dayH 2+% touch count: n=12 | `results.json:rates.dayH.2+.nt` | 12 | **FOUND** | `OURS` | Number of touch events |
| L11 | dayH 2+% held 60 min after touch: 33% | `results.json:rates.dayH.2+.held` | 33% | **FOUND** | `OURS` | Held rate % 60 min post-touch |
| L12 | dayL 0-0.25% days: 100 | `results.json:rates.dayL.0-0.25.n` | 100 | **FOUND** | `OURS` | Total days in distance bucket |
| L12 | dayL 0-0.25% reached in 2h: 88% | `results.json:rates.dayL.0-0.25.touch` | 88% | **FOUND** | `OURS` | Reach rate % in 120 min window |
| L12 | dayL 0-0.25% touch count: n=88 | `results.json:rates.dayL.0-0.25.nt` | 88 | **FOUND** | `OURS` | Number of touch events |
| L12 | dayL 0-0.25% held 60 min after touch: 40% | `results.json:rates.dayL.0-0.25.held` | 40% | **FOUND** | `OURS` | Held rate % 60 min post-touch |
| L13 | dayL 0.25-0.5% days: 155 | `results.json:rates.dayL.0.25-0.5.n` | 155 | **FOUND** | `OURS` | Total days in distance bucket |
| L13 | dayL 0.25-0.5% reached in 2h: 75% | `results.json:rates.dayL.0.25-0.5.touch` | 75% | **FOUND** | `OURS` | Reach rate % in 120 min window |
| L13 | dayL 0.25-0.5% touch count: n=116 | `results.json:rates.dayL.0.25-0.5.nt` | 116 | **FOUND** | `OURS` | Number of touch events |
| L13 | dayL 0.25-0.5% held 60 min after touch: 52% | `results.json:rates.dayL.0.25-0.5.held` | 52% | **FOUND** | `OURS` | Held rate % 60 min post-touch |
| L14 | dayL 0.5-1% days: 313 | `results.json:rates.dayL.0.5-1.n` | 313 | **FOUND** | `OURS` | Total days in distance bucket |
| L14 | dayL 0.5-1% reached in 2h: 45% | `results.json:rates.dayL.0.5-1.touch` | 45% | **FOUND** | `OURS` | Reach rate % in 120 min window |
| L14 | dayL 0.5-1% touch count: n=141 | `results.json:rates.dayL.0.5-1.nt` | 141 | **FOUND** | `OURS` | Number of touch events |
| L14 | dayL 0.5-1% held 60 min after touch: 45% | `results.json:rates.dayL.0.5-1.held` | 45% | **FOUND** | `OURS` | Held rate % 60 min post-touch |
| L15 | dayL 1-2% days: 367 | `results.json:rates.dayL.1-2.n` | 367 | **FOUND** | `OURS` | Total days in distance bucket |
| L15 | dayL 1-2% reached in 2h: 26% | `results.json:rates.dayL.1-2.touch` | 26% | **FOUND** | `OURS` | Reach rate % in 120 min window |
| L15 | dayL 1-2% touch count: n=94 | `results.json:rates.dayL.1-2.nt` | 94 | **FOUND** | `OURS` | Number of touch events |
| L15 | dayL 1-2% held 60 min after touch: 56% | `results.json:rates.dayL.1-2.held` | 56% | **FOUND** | `OURS` | Held rate % 60 min post-touch |
| L16 | dayL 2+% days: 295 | `results.json:rates.dayL.2+.n` | 295 | **FOUND** | `OURS` | Total days in distance bucket |
| L16 | dayL 2+% reached in 2h: 7% | `results.json:rates.dayL.2+.touch` | 7% | **FOUND** | `OURS` | Reach rate % in 120 min window |
| L16 | dayL 2+% touch count: n=21 | `results.json:rates.dayL.2+.nt` | 21 | **FOUND** | `OURS` | Number of touch events |
| L16 | dayL 2+% held 60 min after touch: 48% | `results.json:rates.dayL.2+.held` | 48% | **FOUND** | `OURS` | Held rate % 60 min post-touch |
| L17 | pdh 0-0.25% days: 38 | `results.json:rates.pdh.0-0.25.n` | 38 | **FOUND** | `OURS` | Total days in distance bucket |
| L17 | pdh 0-0.25% reached in 2h: 84% | `results.json:rates.pdh.0-0.25.touch` | 84% | **FOUND** | `OURS` | Reach rate % in 120 min window |
| L17 | pdh 0-0.25% touch count: n=32 | `results.json:rates.pdh.0-0.25.nt` | 32 | **FOUND** | `OURS` | Number of touch events |
| L17 | pdh 0-0.25% held 60 min after touch: 53% | `results.json:rates.pdh.0-0.25.held` | 53% | **FOUND** | `OURS` | Held rate % 60 min post-touch |
| L18 | pdh 0.25-0.5% days: 42 | `results.json:rates.pdh.0.25-0.5.n` | 42 | **FOUND** | `OURS` | Total days in distance bucket |
| L18 | pdh 0.25-0.5% reached in 2h: 62% | `results.json:rates.pdh.0.25-0.5.touch` | 62% | **FOUND** | `OURS` | Reach rate % in 120 min window |
| L18 | pdh 0.25-0.5% touch count: n=26 | `results.json:rates.pdh.0.25-0.5.nt` | 26 | **FOUND** | `OURS` | Number of touch events |
| L18 | pdh 0.25-0.5% held 60 min after touch: 46% | `results.json:rates.pdh.0.25-0.5.held` | 46% | **FOUND** | `OURS` | Held rate % 60 min post-touch |
| L19 | pdh 0.5-1% days: 138 | `results.json:rates.pdh.0.5-1.n` | 138 | **FOUND** | `OURS` | Total days in distance bucket |
| L19 | pdh 0.5-1% reached in 2h: 38% | `results.json:rates.pdh.0.5-1.touch` | 38% | **FOUND** | `OURS` | Reach rate % in 120 min window |
| L19 | pdh 0.5-1% touch count: n=53 | `results.json:rates.pdh.0.5-1.nt` | 53 | **FOUND** | `OURS` | Number of touch events |
| L19 | pdh 0.5-1% held 60 min after touch: 55% | `results.json:rates.pdh.0.5-1.held` | 55% | **FOUND** | `OURS` | Held rate % 60 min post-touch |
| L20 | pdh 1-2% days: 271 | `results.json:rates.pdh.1-2.n` | 271 | **FOUND** | `OURS` | Total days in distance bucket |
| L20 | pdh 1-2% reached in 2h: 14% | `results.json:rates.pdh.1-2.touch` | 14% | **FOUND** | `OURS` | Reach rate % in 120 min window |
| L20 | pdh 1-2% touch count: n=39 | `results.json:rates.pdh.1-2.nt` | 39 | **FOUND** | `OURS` | Number of touch events |
| L20 | pdh 1-2% held 60 min after touch: 54% | `results.json:rates.pdh.1-2.held` | 54% | **FOUND** | `OURS` | Held rate % 60 min post-touch |
| L21 | pdh 2+% days: 526 | `results.json:rates.pdh.2+.n` | 526 | **FOUND** | `OURS` | Total days in distance bucket |
| L21 | pdh 2+% reached in 2h: 3% | `results.json:rates.pdh.2+.touch` | 3% | **FOUND** | `OURS` | Reach rate % in 120 min window |
| L21 | pdh 2+% touch count: n=17 | `results.json:rates.pdh.2+.nt` | 17 | **FOUND** | `OURS` | Number of touch events |
| L21 | pdh 2+% held 60 min after touch: 71% | `results.json:rates.pdh.2+.held` | 71% | **FOUND** | `OURS` | Held rate % 60 min post-touch |
| L22 | pdl 0-0.25% days: 45 | `results.json:rates.pdl.0-0.25.n` | 45 | **FOUND** | `OURS` | Total days in distance bucket |
| L22 | pdl 0-0.25% reached in 2h: 80% | `results.json:rates.pdl.0-0.25.touch` | 80% | **FOUND** | `OURS` | Reach rate % in 120 min window |
| L22 | pdl 0-0.25% touch count: n=36 | `results.json:rates.pdl.0-0.25.nt` | 36 | **FOUND** | `OURS` | Number of touch events |
| L22 | pdl 0-0.25% held 60 min after touch: 47% | `results.json:rates.pdl.0-0.25.held` | 47% | **FOUND** | `OURS` | Held rate % 60 min post-touch |
| L23 | pdl 0.25-0.5% days: 56 | `results.json:rates.pdl.0.25-0.5.n` | 56 | **FOUND** | `OURS` | Total days in distance bucket |
| L23 | pdl 0.25-0.5% reached in 2h: 75% | `results.json:rates.pdl.0.25-0.5.touch` | 75% | **FOUND** | `OURS` | Reach rate % in 120 min window |
| L23 | pdl 0.25-0.5% touch count: n=42 | `results.json:rates.pdl.0.25-0.5.nt` | 42 | **FOUND** | `OURS` | Number of touch events |
| L23 | pdl 0.25-0.5% held 60 min after touch: 38% | `results.json:rates.pdl.0.25-0.5.held` | 38% | **FOUND** | `OURS` | Held rate % 60 min post-touch |
| L24 | pdl 0.5-1% days: 130 | `results.json:rates.pdl.0.5-1.n` | 130 | **FOUND** | `OURS` | Total days in distance bucket |
| L24 | pdl 0.5-1% reached in 2h: 42% | `results.json:rates.pdl.0.5-1.touch` | 42% | **FOUND** | `OURS` | Reach rate % in 120 min window |
| L24 | pdl 0.5-1% touch count: n=55 | `results.json:rates.pdl.0.5-1.nt` | 55 | **FOUND** | `OURS` | Number of touch events |
| L24 | pdl 0.5-1% held 60 min after touch: 53% | `results.json:rates.pdl.0.5-1.held` | 53% | **FOUND** | `OURS` | Held rate % 60 min post-touch |
| L25 | pdl 1-2% days: 258 | `results.json:rates.pdl.1-2.n` | 258 | **FOUND** | `OURS` | Total days in distance bucket |
| L25 | pdl 1-2% reached in 2h: 17% | `results.json:rates.pdl.1-2.touch` | 17% | **FOUND** | `OURS` | Reach rate % in 120 min window |
| L25 | pdl 1-2% touch count: n=45 | `results.json:rates.pdl.1-2.nt` | 45 | **FOUND** | `OURS` | Number of touch events |
| L25 | pdl 1-2% held 60 min after touch: 56% | `results.json:rates.pdl.1-2.held` | 56% | **FOUND** | `OURS` | Held rate % 60 min post-touch |
| L26 | pdl 2+% days: 561 | `results.json:rates.pdl.2+.n` | 561 | **FOUND** | `OURS` | Total days in distance bucket |
| L26 | pdl 2+% reached in 2h: 4% | `results.json:rates.pdl.2+.touch` | 4% | **FOUND** | `OURS` | Reach rate % in 120 min window |
| L26 | pdl 2+% touch count: n=21 | `results.json:rates.pdl.2+.nt` | 21 | **FOUND** | `OURS` | Number of touch events |
| L26 | pdl 2+% held 60 min after touch: 33% | `results.json:rates.pdl.2+.held` | 33% | **FOUND** | `OURS` | Held rate % 60 min post-touch |
| L27 | d3h 0-0.25% days: 26 | `results.json:rates.d3h.0-0.25.n` | 26 | **FOUND** | `OURS` | Total days in distance bucket |
| L27 | d3h 0-0.25% reached in 2h: 88% | `results.json:rates.d3h.0-0.25.touch` | 88% | **FOUND** | `OURS` | Reach rate % in 120 min window |
| L27 | d3h 0-0.25% touch count: n=23 | `results.json:rates.d3h.0-0.25.nt` | 23 | **FOUND** | `OURS` | Number of touch events |
| L27 | d3h 0-0.25% held 60 min after touch: 30% | `results.json:rates.d3h.0-0.25.held` | 30% | **FOUND** | `OURS` | Held rate % 60 min post-touch |
| L28 | d3h 0.25-0.5% days: 28 | `results.json:rates.d3h.0.25-0.5.n` | 28 | **FOUND** | `OURS` | Total days in distance bucket |
| L28 | d3h 0.25-0.5% reached in 2h: 61% | `results.json:rates.d3h.0.25-0.5.touch` | 61% | **FOUND** | `OURS` | Reach rate % in 120 min window |
| L28 | d3h 0.25-0.5% touch count: n=17 | `results.json:rates.d3h.0.25-0.5.nt` | 17 | **FOUND** | `OURS` | Number of touch events |
| L28 | d3h 0.25-0.5% held 60 min after touch: 47% | `results.json:rates.d3h.0.25-0.5.held` | 47% | **FOUND** | `OURS` | Held rate % 60 min post-touch |
| L29 | d3h 0.5-1% days: 84 | `results.json:rates.d3h.0.5-1.n` | 84 | **FOUND** | `OURS` | Total days in distance bucket |
| L29 | d3h 0.5-1% reached in 2h: 40% | `results.json:rates.d3h.0.5-1.touch` | 40% | **FOUND** | `OURS` | Reach rate % in 120 min window |
| L29 | d3h 0.5-1% touch count: n=34 | `results.json:rates.d3h.0.5-1.nt` | 34 | **FOUND** | `OURS` | Number of touch events |
| L29 | d3h 0.5-1% held 60 min after touch: 74% | `results.json:rates.d3h.0.5-1.held` | 74% | **FOUND** | `OURS` | Held rate % 60 min post-touch |
| L30 | d3h 1-2% days: 199 | `results.json:rates.d3h.1-2.n` | 199 | **FOUND** | `OURS` | Total days in distance bucket |
| L30 | d3h 1-2% reached in 2h: 12% | `results.json:rates.d3h.1-2.touch` | 12% | **FOUND** | `OURS` | Reach rate % in 120 min window |
| L30 | d3h 1-2% touch count: n=24 | `results.json:rates.d3h.1-2.nt` | 24 | **FOUND** | `OURS` | Number of touch events |
| L30 | d3h 1-2% held 60 min after touch: 54% | `results.json:rates.d3h.1-2.held` | 54% | **FOUND** | `OURS` | Held rate % 60 min post-touch |
| L31 | d3h 2+% days: 748 | `results.json:rates.d3h.2+.n` | 748 | **FOUND** | `OURS` | Total days in distance bucket |
| L31 | d3h 2+% reached in 2h: 2% | `results.json:rates.d3h.2+.touch` | 2% | **FOUND** | `OURS` | Reach rate % in 120 min window |
| L31 | d3h 2+% touch count: n=17 | `results.json:rates.d3h.2+.nt` | 17 | **FOUND** | `OURS` | Number of touch events |
| L31 | d3h 2+% held 60 min after touch: 53% | `results.json:rates.d3h.2+.held` | 53% | **FOUND** | `OURS` | Held rate % 60 min post-touch |
| L32 | d3l 0-0.25% days: 19 | `results.json:rates.d3l.0-0.25.n` | 19 | **FOUND** | `OURS` | Total days in distance bucket |
| L32 | d3l 0-0.25% reached in 2h: 84% | `results.json:rates.d3l.0-0.25.touch` | 84% | **FOUND** | `OURS` | Reach rate % in 120 min window |
| L32 | d3l 0-0.25% touch count: n=16 | `results.json:rates.d3l.0-0.25.nt` | 16 | **FOUND** | `OURS` | Number of touch events |
| L32 | d3l 0-0.25% held 60 min after touch: 50% | `results.json:rates.d3l.0-0.25.held` | 50% | **FOUND** | `OURS` | Held rate % 60 min post-touch |
| L33 | d3l 0.25-0.5% days: 23 | `results.json:rates.d3l.0.25-0.5.n` | 23 | **FOUND** | `OURS` | Total days in distance bucket |
| L33 | d3l 0.25-0.5% reached in 2h: 65% | `results.json:rates.d3l.0.25-0.5.touch` | 65% | **FOUND** | `OURS` | Reach rate % in 120 min window |
| L33 | d3l 0.25-0.5% touch count: n=15 | `results.json:rates.d3l.0.25-0.5.nt` | 15 | **FOUND** | `OURS` | Number of touch events |
| L33 | d3l 0.25-0.5% held 60 min after touch: 20% | `results.json:rates.d3l.0.25-0.5.held` | 20% | **FOUND** | `OURS` | Held rate % 60 min post-touch |
| L34 | d3l 0.5-1% days: 99 | `results.json:rates.d3l.0.5-1.n` | 99 | **FOUND** | `OURS` | Total days in distance bucket |
| L34 | d3l 0.5-1% reached in 2h: 40% | `results.json:rates.d3l.0.5-1.touch` | 40% | **FOUND** | `OURS` | Reach rate % in 120 min window |
| L34 | d3l 0.5-1% touch count: n=40 | `results.json:rates.d3l.0.5-1.nt` | 40 | **FOUND** | `OURS` | Number of touch events |
| L34 | d3l 0.5-1% held 60 min after touch: 52% | `results.json:rates.d3l.0.5-1.held` | 52% | **FOUND** | `OURS` | Held rate % 60 min post-touch |
| L35 | d3l 1-2% days: 182 | `results.json:rates.d3l.1-2.n` | 182 | **FOUND** | `OURS` | Total days in distance bucket |
| L35 | d3l 1-2% reached in 2h: 14% | `results.json:rates.d3l.1-2.touch` | 14% | **FOUND** | `OURS` | Reach rate % in 120 min window |
| L35 | d3l 1-2% touch count: n=26 | `results.json:rates.d3l.1-2.nt` | 26 | **FOUND** | `OURS` | Number of touch events |
| L35 | d3l 1-2% held 60 min after touch: 58% | `results.json:rates.d3l.1-2.held` | 58% | **FOUND** | `OURS` | Held rate % 60 min post-touch |
| L36 | d3l 2+% days: 792 | `results.json:rates.d3l.2+.n` | 792 | **FOUND** | `OURS` | Total days in distance bucket |
| L36 | d3l 2+% reached in 2h: 2% | `results.json:rates.d3l.2+.touch` | 2% | **FOUND** | `OURS` | Reach rate % in 120 min window |
| L36 | d3l 2+% touch count: n=19 | `results.json:rates.d3l.2+.nt` | 19 | **FOUND** | `OURS` | Number of touch events |
| L36 | d3l 2+% held 60 min after touch: 47% | `results.json:rates.d3l.2+.held` | 47% | **FOUND** | `OURS` | Held rate % 60 min post-touch |
| L37 | d7h 0-0.25% days: 11 | `results.json:rates.d7h.0-0.25.n` | 11 | **FOUND** | `OURS` | Total days in distance bucket |
| L37 | d7h 0-0.25% reached in 2h: 100% | `results.json:rates.d7h.0-0.25.touch` | 100% | **FOUND** | `OURS` | Reach rate % in 120 min window |
| L37 | d7h 0-0.25% touch count: n=11 | `results.json:rates.d7h.0-0.25.nt` | 11 | **FOUND** | `OURS` | Number of touch events |
| L37 | d7h 0-0.25% held 60 min after touch: 36% | `results.json:rates.d7h.0-0.25.held` | 36% | **FOUND** | `OURS` | Held rate % 60 min post-touch |
| L38 | d7h 0.25-0.5% days: 17 | `results.json:rates.d7h.0.25-0.5.n` | 17 | **FOUND** | `OURS` | Total days in distance bucket |
| L38 | d7h 0.25-0.5% reached in 2h: 71% | `results.json:rates.d7h.0.25-0.5.touch` | 71% | **FOUND** | `OURS` | Reach rate % in 120 min window |
| L38 | d7h 0.25-0.5% touch count: n=12 | `results.json:rates.d7h.0.25-0.5.nt` | 12 | **FOUND** | `OURS` | Number of touch events |
| L38 | d7h 0.25-0.5% held 60 min after touch: 42% | `results.json:rates.d7h.0.25-0.5.held` | 42% | **FOUND** | `OURS` | Held rate % 60 min post-touch |
| L39 | d7h 0.5-1% days: 57 | `results.json:rates.d7h.0.5-1.n` | 57 | **FOUND** | `OURS` | Total days in distance bucket |
| L39 | d7h 0.5-1% reached in 2h: 37% | `results.json:rates.d7h.0.5-1.touch` | 37% | **FOUND** | `OURS` | Reach rate % in 120 min window |
| L39 | d7h 0.5-1% touch count: n=21 | `results.json:rates.d7h.0.5-1.nt` | 21 | **FOUND** | `OURS` | Number of touch events |
| L39 | d7h 0.5-1% held 60 min after touch: 81% | `results.json:rates.d7h.0.5-1.held` | 81% | **FOUND** | `OURS` | Held rate % 60 min post-touch |
| L40 | d7h 1-2% days: 141 | `results.json:rates.d7h.1-2.n` | 141 | **FOUND** | `OURS` | Total days in distance bucket |
| L40 | d7h 1-2% reached in 2h: 10% | `results.json:rates.d7h.1-2.touch` | 10% | **FOUND** | `OURS` | Reach rate % in 120 min window |
| L40 | d7h 1-2% touch count: n=14 | `results.json:rates.d7h.1-2.nt` | 14 | **FOUND** | `OURS` | Number of touch events |
| L40 | d7h 1-2% held 60 min after touch: 36% | `results.json:rates.d7h.1-2.held` | 36% | **FOUND** | `OURS` | Held rate % 60 min post-touch |
| L41 | d7h 2+% days: 915 | `results.json:rates.d7h.2+.n` | 915 | **FOUND** | `OURS` | Total days in distance bucket |
| L41 | d7h 2+% reached in 2h: 2% | `results.json:rates.d7h.2+.touch` | 2% | **FOUND** | `OURS` | Reach rate % in 120 min window |
| L41 | d7h 2+% touch count: n=16 | `results.json:rates.d7h.2+.nt` | 16 | **FOUND** | `OURS` | Number of touch events |
| L41 | d7h 2+% held 60 min after touch: 62% | `results.json:rates.d7h.2+.held` | 62% | **FOUND** | `OURS` | Held rate % 60 min post-touch |
| L42 | d7l 0-0.25% days: 7 | `results.json:rates.d7l.0-0.25.n` | 7 | **FOUND** | `OURS` | Total days in distance bucket |
| L42 | d7l 0-0.25% reached in 2h: 86% | `results.json:rates.d7l.0-0.25.touch` | 86% | **FOUND** | `OURS` | Reach rate % in 120 min window |
| L42 | d7l 0-0.25% touch count: n=6 | `results.json:rates.d7l.0-0.25.nt` | 6 | **FOUND** | `OURS` | Number of touch events |
| L42 | d7l 0-0.25% held 60 min after touch: 33% | `results.json:rates.d7l.0-0.25.held` | 33% | **FOUND** | `OURS` | Held rate % 60 min post-touch |
| L43 | d7l 0.25-0.5% days: 8 | `results.json:rates.d7l.0.25-0.5.n` | 8 | **FOUND** | `OURS` | Total days in distance bucket |
| L43 | d7l 0.25-0.5% reached in 2h: 62% | `results.json:rates.d7l.0.25-0.5.touch` | 62% | **FOUND** | `OURS` | Reach rate % in 120 min window |
| L43 | d7l 0.25-0.5% touch count: n=5 | `results.json:rates.d7l.0.25-0.5.nt` | 5 | **FOUND** | `OURS` | Number of touch events |
| L43 | d7l 0.25-0.5% held 60 min after touch: 0% | `results.json:rates.d7l.0.25-0.5.held` | 0% | **FOUND** | `OURS` | Held rate % 60 min post-touch |
| L44 | d7l 0.5-1% days: 50 | `results.json:rates.d7l.0.5-1.n` | 50 | **FOUND** | `OURS` | Total days in distance bucket |
| L44 | d7l 0.5-1% reached in 2h: 42% | `results.json:rates.d7l.0.5-1.touch` | 42% | **FOUND** | `OURS` | Reach rate % in 120 min window |
| L44 | d7l 0.5-1% touch count: n=21 | `results.json:rates.d7l.0.5-1.nt` | 21 | **FOUND** | `OURS` | Number of touch events |
| L44 | d7l 0.5-1% held 60 min after touch: 38% | `results.json:rates.d7l.0.5-1.held` | 38% | **FOUND** | `OURS` | Held rate % 60 min post-touch |
| L45 | d7l 1-2% days: 125 | `results.json:rates.d7l.1-2.n` | 125 | **FOUND** | `OURS` | Total days in distance bucket |
| L45 | d7l 1-2% reached in 2h: 13% | `results.json:rates.d7l.1-2.touch` | 13% | **FOUND** | `OURS` | Reach rate % in 120 min window |
| L45 | d7l 1-2% touch count: n=16 | `results.json:rates.d7l.1-2.nt` | 16 | **FOUND** | `OURS` | Number of touch events |
| L45 | d7l 1-2% held 60 min after touch: 50% | `results.json:rates.d7l.1-2.held` | 50% | **FOUND** | `OURS` | Held rate % 60 min post-touch |
| L46 | d7l 2+% days: 977 | `results.json:rates.d7l.2+.n` | 977 | **FOUND** | `OURS` | Total days in distance bucket |
| L46 | d7l 2+% reached in 2h: 1% | `results.json:rates.d7l.2+.touch` | 1% | **FOUND** | `OURS` | Reach rate % in 120 min window |
| L46 | d7l 2+% touch count: n=12 | `results.json:rates.d7l.2+.nt` | 12 | **FOUND** | `OURS` | Number of touch events |
| L46 | d7l 2+% held 60 min after touch: 50% | `results.json:rates.d7l.2+.held` | 50% | **FOUND** | `OURS` | Held rate % 60 min post-touch |

## us_open_oos_2026-10-30

| Line | Number / Claim | Cited Source | Value in Source | Status | Type | Provenance / Notes |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| L3 | Monthly files: 24 | `F:/MTS/Dumps/backtest/raw_1m_2019/klines` | 24 | **FOUND** | `OURS` | 24 monthly klines files across 2020-01..2021-12 |
| L3 | Total bars: 1,052,640 bars | `24 monthly files (731 days * 1440)` | 1052640 | **FOUND** | `OURS` | Exact 1m minute bars count in 2020-2021 |
| L3 | Valid days (OOS): 505 | `results_oos_2020_2021.json:days` | 505 | **FOUND** | `OURS` | Valid weekday count in OOS window |
| L3 | Original valid days: 1,178 days | `MyTradingSys/research/session_sweeps/results_2026-10-04.json:days` | 1178 | **FOUND** | `OURS` | Valid weekday count in original 2022-26 study |
| L4 | Perp 1m klines 2019-09..12 | `REPORT.md:4 (Limits)` | Perp series public only from 2019-12-31 | **NOT_IN_DATA** | `SOURCED` | Perpetual klines do not exist before 2019-12-31 on Binance |
| L11 | Direction k=10 2022-26 (orig): 0.498 [0.470,0.527] | `results_2026-10-04.json:T2.O_k10` | 0.498 [0.470,0.527] | **FOUND** | `OURS` | Original sample direction persistence |
| L11 | Direction k=10 2020-21 (OOS): 0.485 [0.442,0.529] | `results_oos_2020_2021.json:T2.O_k10` | 0.485 [0.442,0.529] | **FOUND** | `OURS` | OOS sample direction persistence |
| L12 | Direction k=15 2022-26 (orig): 0.494 [0.466,0.523] | `results_2026-10-04.json:T2.O_k15` | 0.494 [0.466,0.523] | **FOUND** | `OURS` | Original sample direction persistence |
| L12 | Direction k=15 2020-21 (OOS): 0.485 [0.442,0.529] | `results_oos_2020_2021.json:T2.O_k15` | 0.485 [0.442,0.529] | **FOUND** | `OURS` | OOS sample direction persistence |
| L13 | Direction k=30 2022-26 (orig): 0.501 [0.472,0.529] | `results_2026-10-04.json:T2.O_k30` | 0.501 [0.472,0.529] | **FOUND** | `OURS` | Original sample direction persistence |
| L13 | Direction k=30 2020-21 (OOS): 0.475 [0.432,0.519] | `results_oos_2020_2021.json:T2.O_k30` | 0.475 [0.432,0.519] | **FOUND** | `OURS` | OOS sample direction persistence |
| L15 | Placebo spread: 24 fixed-UTC-hour anchors (0.440..0.555, median 0.501) | `results_oos_2020_2021.json:T2.placebo_p_range` | [0.4396, 0.501, 0.5545] | **FOUND** | `OURS` | Exact match for min, median, max across 24 UTC placebos |
| L15 | Direction by year: 2020 0.502 | `results_oos_2020_2021.json:T2.by_year_O_k15.2020.p` | 0.502 | **FOUND** | `OURS` | Year 2020 persistence |
| L15 | Direction by year: 2021 0.468 | `results_oos_2020_2021.json:T2.by_year_O_k15.2021.p` | 0.468 | **FOUND** | `OURS` | Year 2021 persistence (0.4683 rounded to 0.468) |
| L22 | US DST orig top buckets: 13:30 1.92x [2.55], 14:00 1.77x, 13:45 1.72x | `results_2026-10-04.json:T1.us_dst` | 13:30 1.92 [2.55], 14:00 1.77, 13:45 1.72 | **FOUND** | `OURS` | Top 3 return/volume buckets in original DST |
| L22 | US DST OOS top buckets: 00:00 1.55x [1.52], 13:30 1.36x [1.63], 12:00 1.35x | `results_oos_2020_2021.json:T1.us_dst` | 00:00 1.55 [1.52], 13:30 1.36 [1.63], 12:00 1.35 | **FOUND** | `OURS` | Top 3 return/volume buckets in OOS DST |
| L23 | US std orig top buckets: 14:30 2.03x [2.81], 14:45 1.81x, 15:15 1.76x | `results_2026-10-04.json:T1.us_std` | 14:30 2.03 [2.81], 14:45 1.81, 15:15 1.76 | **FOUND** | `OURS` | Top 3 return/volume buckets in original std |
| L23 | US std OOS top buckets: 00:00 1.51x [1.44], 14:30 1.39x [1.49], 16:00 1.35x [1.89] | `results_oos_2020_2021.json:T1.us_std` | 00:00 1.51 [1.44], 14:30 1.39 [1.49], 16:00 1.35 [1.89] | **FOUND** | `OURS` | Top 3 return/volume buckets in OOS std |
| L30 | T3 base P(US up): 0.549 [0.505,0.591] | `results_oos_2020_2021.json:T3_london_sweep_asia.all.base` | 0.548 [0.505,0.591] | **FOUND** | `OURS` | T3 base win probability |
| L30 | T3 H_sweep_back: 0.493 n=75 | `results_oos_2020_2021.json:T3_london_sweep_asia.all.H_sweep_back` | 0.493 n=75 | **FOUND** | `OURS` | T3 high sweep back rate |
| L30 | T3 none: 0.600 n=75 | `results_oos_2020_2021.json:T3_london_sweep_asia.all.none` | 0.600 n=75 | **FOUND** | `OURS` | T3 none class rate |
| L30 | T4 H_sweep_back: 0.647 n=34, CI [0.48,0.79] | `results_oos_2020_2021.json:T4_open_sweep_pre.all.H_sweep_back` | 0.647 n=34 [0.48,0.79] | **FOUND** | `OURS` | T4 high sweep back rate and CI |
| L30 | T5 small IB trend: 0.205 | `results_oos_2020_2021.json:T5_tom_opening_range.all.small.trend.p` | 0.205 | **FOUND** | `OURS` | T5 small IB trend rate |
| L30 | T5 mid IB trend: 0.265 | `results_oos_2020_2021.json:T5_tom_opening_range.all.mid.trend.p` | 0.265 | **FOUND** | `OURS` | T5 mid IB trend rate (0.2654 rounded to 0.265) |
| L30 | T5 large IB trend: 0.253 | `results_oos_2020_2021.json:T5_tom_opening_range.all.large.trend.p` | 0.253 | **FOUND** | `OURS` | T5 large IB trend rate (0.2531 rounded to 0.253) |

## wt30_sequence_2026-10-30

| Line | Number / Claim | Cited Source | Value in Source | Status | Type | Provenance / Notes |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| L3 | WT 10/21/4 and ±53 levels | `study.py:6 (LazyBear, PARITY_CONTRACT.md)` | 10/21/4 and +/-53 | **FOUND** | `SOURCED` | SOURCED LazyBear indicator constants |
| L3 | DEV 30m bars: 43776 (2022-01..2024-06) | `output.txt:1` | 43776 | **FOUND** | `OURS` | Total 30m bar count in DEV window |
| L3 | Validation window (2024-07 onward) | `study.py:7-8 / RESULT.md:3` | Stays unread (sealed) | **NOT_IN_DATA** | `OURS` | WT validation window unread per frozen pre-reg |
| L7 | Baseline: random 30m bars up after 12h 50%, +1% first 45%, -1% first 45% | `output.txt:6 (BASE)` | up12h: 0.500, up1_first: 0.454, dn1_first: 0.452 | **FOUND** | `OURS` | Baseline random 30m bars outcome distribution |
| L11 | T1 top cross (sell dot >= 53) n: 465 | `output.txt` | 465 | **FOUND** | `OURS` | Event count in output.txt |
| L11 | T1 top cross (sell dot >= 53) Up 4 h: 48% | `output.txt` | 48% | **FOUND** | `OURS` | 4h up rate |
| L11 | T1 top cross (sell dot >= 53) Up 12 h: 51% | `output.txt` | 51% | **FOUND** | `OURS` | 12h up rate |
| L11 | T1 top cross (sell dot >= 53) +1% first: 53% | `output.txt` | 53% | **FOUND** | `OURS` | +1% reached first rate |
| L11 | T1 top cross (sell dot >= 53) -1% first: 42% | `output.txt` | 42% | **FOUND** | `OURS` | -1% reached first rate |
| L11 | T1 top cross (sell dot >= 53) Mean 12 h: +0.20% | `output.txt` | +0.20% | **FOUND** | `OURS` | Mean 12h return |
| L12 | T1 with 4h WT up n: 308 | `output.txt` | 308 | **FOUND** | `OURS` | Event count in output.txt |
| L12 | T1 with 4h WT up Up 4 h: 52% | `output.txt` | 52% | **FOUND** | `OURS` | 4h up rate |
| L12 | T1 with 4h WT up Up 12 h: 54% | `output.txt` | 54% | **FOUND** | `OURS` | 12h up rate |
| L12 | T1 with 4h WT up +1% first: 56% | `output.txt` | 56% | **FOUND** | `OURS` | +1% reached first rate |
| L12 | T1 with 4h WT up -1% first: 41% | `output.txt` | 41% | **FOUND** | `OURS` | -1% reached first rate |
| L12 | T1 with 4h WT up Mean 12 h: +0.30% | `output.txt` | +0.30% | **FOUND** | `OURS` | Mean 12h return |
| L13 | T1 with 4h WT down n: 157 | `output.txt` | 157 | **FOUND** | `OURS` | Event count in output.txt |
| L13 | T1 with 4h WT down Up 4 h: 41% | `output.txt` | 41% | **FOUND** | `OURS` | 4h up rate |
| L13 | T1 with 4h WT down Up 12 h: 47% | `output.txt` | 47% | **FOUND** | `OURS` | 12h up rate |
| L13 | T1 with 4h WT down +1% first: 47% | `output.txt` | 47% | **FOUND** | `OURS` | +1% reached first rate |
| L13 | T1 with 4h WT down -1% first: 44% | `output.txt` | 44% | **FOUND** | `OURS` | -1% reached first rate |
| L13 | T1 with 4h WT down Mean 12 h: 0.00% | `output.txt` | 0.00% | **FOUND** | `OURS` | Mean 12h return |
| L14 | T2 bottom cross (buy dot <= -53) n: 422 | `output.txt` | 422 | **FOUND** | `OURS` | Event count in output.txt |
| L14 | T2 bottom cross (buy dot <= -53) Up 4 h: 57% | `output.txt` | 57% | **FOUND** | `OURS` | 4h up rate |
| L14 | T2 bottom cross (buy dot <= -53) Up 12 h: 53% | `output.txt` | 53% | **FOUND** | `OURS` | 12h up rate |
| L14 | T2 bottom cross (buy dot <= -53) +1% first: 43% | `output.txt` | 43% | **FOUND** | `OURS` | +1% reached first rate |
| L14 | T2 bottom cross (buy dot <= -53) -1% first: 48% | `output.txt` | 48% | **FOUND** | `OURS` | -1% reached first rate |
| L14 | T2 bottom cross (buy dot <= -53) Mean 12 h: -0.11% | `output.txt` | -0.11% | **FOUND** | `OURS` | Mean 12h return |
| L15 | T2 with 4h WT down n: 304 | `output.txt` | 304 | **FOUND** | `OURS` | Event count in output.txt |
| L15 | T2 with 4h WT down Up 4 h: 56% | `output.txt` | 56% | **FOUND** | `OURS` | 4h up rate |
| L15 | T2 with 4h WT down Up 12 h: 53% | `output.txt` | 53% | **FOUND** | `OURS` | 12h up rate |
| L15 | T2 with 4h WT down +1% first: 42% | `output.txt` | 42% | **FOUND** | `OURS` | +1% reached first rate |
| L15 | T2 with 4h WT down -1% first: 49% | `output.txt` | 49% | **FOUND** | `OURS` | -1% reached first rate |
| L15 | T2 with 4h WT down Mean 12 h: -0.17% | `output.txt` | -0.17% | **FOUND** | `OURS` | Mean 12h return |
| L16 | T3 bearish divergence at the top n: 44 | `output.txt` | 44 | **FOUND** | `OURS` | Event count in output.txt |
| L16 | T3 bearish divergence at the top Up 4 h: 61% | `output.txt` | 61% | **FOUND** | `OURS` | 4h up rate |
| L16 | T3 bearish divergence at the top Up 12 h: 61% | `output.txt` | 61% | **FOUND** | `OURS` | 12h up rate |
| L16 | T3 bearish divergence at the top +1% first: 59% | `output.txt` | 59% | **FOUND** | `OURS` | +1% reached first rate |
| L16 | T3 bearish divergence at the top -1% first: 34% | `output.txt` | 34% | **FOUND** | `OURS` | -1% reached first rate |
| L16 | T3 bearish divergence at the top Mean 12 h: +0.46% | `output.txt` | +0.46% | **FOUND** | `OURS` | Mean 12h return |
| L17 | T4 bullish divergence at the bottom n: 52 | `output.txt` | 52 | **FOUND** | `OURS` | Event count in output.txt |
| L17 | T4 bullish divergence at the bottom Up 4 h: 52% | `output.txt` | 52% | **FOUND** | `OURS` | 4h up rate |
| L17 | T4 bullish divergence at the bottom Up 12 h: 48% | `output.txt` | 48% | **FOUND** | `OURS` | 12h up rate |
| L17 | T4 bullish divergence at the bottom +1% first: 39% | `output.txt` | 39% | **FOUND** | `OURS` | +1% reached first rate |
| L17 | T4 bullish divergence at the bottom -1% first: 52% | `output.txt` | 52% | **FOUND** | `OURS` | -1% reached first rate |
| L17 | T4 bullish divergence at the bottom Mean 12 h: -0.25% | `output.txt` | -0.25% | **FOUND** | `OURS` | Mean 12h return |
| L18 | T5 centre cross up n: 1108 | `output.txt` | 1108 | **FOUND** | `OURS` | Event count in output.txt |
| L18 | T5 centre cross up Up 4 h: 46% | `output.txt` | 46% | **FOUND** | `OURS` | 4h up rate |
| L18 | T5 centre cross up Up 12 h: 48% | `output.txt` | 48% | **FOUND** | `OURS` | 12h up rate |
| L18 | T5 centre cross up +1% first: 45% | `output.txt` | 45% | **FOUND** | `OURS` | +1% reached first rate |
| L18 | T5 centre cross up -1% first: 44% | `output.txt` | 44% | **FOUND** | `OURS` | -1% reached first rate |
| L18 | T5 centre cross up Mean 12 h: +0.03% | `output.txt` | +0.03% | **FOUND** | `OURS` | Mean 12h return |
| L19 | T6 centre cross down n: 1113 | `output.txt` | 1113 | **FOUND** | `OURS` | Event count in output.txt |
| L19 | T6 centre cross down Up 4 h: 55% | `output.txt` | 55% | **FOUND** | `OURS` | 4h up rate |
| L19 | T6 centre cross down Up 12 h: 52% | `output.txt` | 52% | **FOUND** | `OURS` | 12h up rate |
| L19 | T6 centre cross down +1% first: 44% | `output.txt` | 44% | **FOUND** | `OURS` | +1% reached first rate |
| L19 | T6 centre cross down -1% first: 46% | `output.txt` | 46% | **FOUND** | `OURS` | -1% reached first rate |
| L19 | T6 centre cross down Mean 12 h: +0.06% | `output.txt` | +0.06% | **FOUND** | `OURS` | Mean 12h return |
| L20 | T7 rejection at 0 from below n: 152 | `output.txt` | 152 | **FOUND** | `OURS` | Event count in output.txt |
| L20 | T7 rejection at 0 from below Up 4 h: 57% | `output.txt` | 57% | **FOUND** | `OURS` | 4h up rate |
| L20 | T7 rejection at 0 from below Up 12 h: 59% | `output.txt` | 59% | **FOUND** | `OURS` | 12h up rate |
| L20 | T7 rejection at 0 from below +1% first: 41% | `output.txt` | 41% | **FOUND** | `OURS` | +1% reached first rate |
| L20 | T7 rejection at 0 from below -1% first: 50% | `output.txt` | 50% | **FOUND** | `OURS` | -1% reached first rate |
| L20 | T7 rejection at 0 from below Mean 12 h: +0.10% | `output.txt` | +0.10% | **FOUND** | `OURS` | Mean 12h return |
| L21 | T7 with 4h WT down n: 124 | `output.txt` | 124 | **FOUND** | `OURS` | Event count in output.txt |
| L21 | T7 with 4h WT down Up 4 h: 52% | `output.txt` | 52% | **FOUND** | `OURS` | 4h up rate |
| L21 | T7 with 4h WT down Up 12 h: 60% | `output.txt` | 60% | **FOUND** | `OURS` | 12h up rate |
| L21 | T7 with 4h WT down +1% first: 41% | `output.txt` | 41% | **FOUND** | `OURS` | +1% reached first rate |
| L21 | T7 with 4h WT down -1% first: 50% | `output.txt` | 50% | **FOUND** | `OURS` | -1% reached first rate |
| L21 | T7 with 4h WT down Mean 12 h: +0.10% | `output.txt` | +0.10% | **FOUND** | `OURS` | Mean 12h return |
| L22 | T8 rejection at 0 from above n: 163 | `output.txt` | 163 | **FOUND** | `OURS` | Event count in output.txt |
| L22 | T8 rejection at 0 from above Up 4 h: 50% | `output.txt` | 50% | **FOUND** | `OURS` | 4h up rate |
| L22 | T8 rejection at 0 from above Up 12 h: 40% | `output.txt` | 40% | **FOUND** | `OURS` | 12h up rate |
| L22 | T8 rejection at 0 from above +1% first: 49% | `output.txt` | 49% | **FOUND** | `OURS` | +1% reached first rate |
| L22 | T8 rejection at 0 from above -1% first: 44% | `output.txt` | 44% | **FOUND** | `OURS` | -1% reached first rate |
| L22 | T8 rejection at 0 from above Mean 12 h: +0.02% | `output.txt` | +0.02% | **FOUND** | `OURS` | Mean 12h return |
| L23 | T9b top-to-bottom in <= 16 bars n: 7 | `output.txt` | 7 | **FOUND** | `OURS` | Event count in output.txt |
| L23 | T9b top-to-bottom in <= 16 bars Up 4 h: 43% | `output.txt` | 43% | **FOUND** | `OURS` | 4h up rate |
| L23 | T9b top-to-bottom in <= 16 bars Up 12 h: 29% | `output.txt` | 29% | **FOUND** | `OURS` | 12h up rate |
| L23 | T9b top-to-bottom in <= 16 bars +1% first: 0% | `output.txt` | 0% | **FOUND** | `OURS` | +1% reached first rate |
| L23 | T9b top-to-bottom in <= 16 bars -1% first: 86% | `output.txt` | 86% | **FOUND** | `OURS` | -1% reached first rate |
| L23 | T9b top-to-bottom in <= 16 bars Mean 12 h: -0.18% | `output.txt` | -0.18% | **FOUND** | `OURS` | Mean 12h return |
| L25 | Standard error: ~2.3 pts at n=465, 4 pts at n=150, 7 pts at n=50 | `study.py / binomial formula` | 2.3, 4.1, 7.1 | **FOUND** | `OURS` | Standard error of proportions sqrt(0.5*0.5/n) |
| L27 | wt1 reached bottom zone in 21% (4h up) to 29% (4h down) | `output.txt:44-45` | 0.208 (21%) to 0.287 (29%) | **FOUND** | `OURS` | Reached bottom zone rate |
| L27 | Median price move: -1.7% to -2.1% in about 16 hours | `output.txt:44-45` | -1.742% (33.5 bars) to -2.103% (32.0 bars) | **FOUND** | `OURS` | Median price move and bar duration |
| L49 | Live snapshot 30m: wt1 -3.6, wt2 -5.4 (from -55.7 at 77,436) | `RESULT.md:49 / live aid` | wt1 -3.6, wt2 -5.4 | **FOUND** | `OURS` | Spot snapshot at 2026-10-30 08:00Z |
| L50 | Live snapshot 4h: wt1 -26.9, wt2 -11.4 | `RESULT.md:50 / live aid` | wt1 -26.9, wt2 -11.4 | **FOUND** | `OURS` | Spot snapshot at 2026-10-30 08:00Z |
| L51 | Live snapshot 1D: wt1 -41.9, wt2 -37.9 | `RESULT.md:51 / live aid` | wt1 -41.9, wt2 -37.9 | **FOUND** | `OURS` | Spot snapshot at 2026-10-30 08:00Z |

## tom_transfer_2026-10-11/vp_return

| Line | Number / Claim | Cited Source | Value in Source | Status | Type | Provenance / Notes |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| L3 | Run timestamp: 2026-10-31 05:23 | `results.json:meta.run_utc` | 2026-10-31 05:23 | **FOUND** | `OURS` | Exact runner execution timestamp |
| L4 | DEV window: 2022-01-02..2024-06-30 | `results.json:meta.first_day, last_day` | 2022-01-02..2024-06-30 | **FOUND** | `OURS` | Date range of analysis |
| L4 | Complete UTC days used: 911 | `results.json:days_used` | 911 | **FOUND** | `OURS` | Exact days used |
| L4 | Dropped days: {'incomplete_day': 0, 'no_atr': 0, 'empty_profile': 0} | `results.json:dropped` | {'incomplete_day': 0, 'no_atr': 0, 'empty_profile': 0} | **FOUND** | `OURS` | Exact match for dropped categories dictionary |
| L8 | Real return share: 57.2% | `results.json:A.real.share` | 57.2% | **FOUND** | `OURS` | 0.571756 rounded to 57.2% |
| L8 | Real 95% day-block CI: 53.9..60.7 | `results.json:A.real.ci` | 53.9..60.7 | **FOUND** | `OURS` | 95% bootstrap confidence interval |
| L8 | Placebo return share: 46.8% | `results.json:A.placebo.share` | 46.8% | **FOUND** | `OURS` | 0.46772 rounded to 46.8% |
| L8 | Difference real vs placebo: +10.4 pp | `results.json:A.diff.diff` | +10.4 pp | **FOUND** | `OURS` | Difference in return share percentage points |
| L8 | Difference 95% CI: 6.4..14.4 | `results.json:A.diff.ci` | 6.4..14.4 | **FOUND** | `OURS` | Day-block bootstrap CI for difference |
| L9 | Tom's claim: 70% | `extracts/processed/tom/extract_BB3c8visnkI.md:38` | 70% | **FOUND** | `SOURCED` | extract_BB3c8visnkI.md:38: 'the other 70% he will try and strive to run back here' |
| L10 | Near placebo share (|d| <= 1): 55.8% vs real 55.0% | `results.json:A_near_placebo.placebo.share, real.share` | 55.8% vs 55.0% | **FOUND** | `OURS` | Near placebo vs real band |
| L10 | Near placebo difference: -0.8 pp (CI -5.2..3.7) | `results.json:A_near_placebo.diff.diff, ci` | -0.8 pp, CI -5.2..3.7 | **FOUND** | `OURS` | Near placebo excess difference |
| L15 | Part A Real events: 871 | `results.json:A.real.n` | 871 | **FOUND** | `OURS` | Real events count |
| L16 | Part A Placebo events: 883 | `results.json:A.placebo.n` | 883 | **FOUND** | `OURS` | Placebo events count |
| L16 | Part A Placebo 95% CI: 43.6..50.0 | `results.json:A.placebo.ci` | 43.6..50.0 | **FOUND** | `OURS` | Placebo return share 95% CI |
| L19 | Fire rate real: 95.6% | `results.json:fire_rate.real` | 95.6% | **FOUND** | `OURS` | Real fire rate % |
| L19 | Fire rate placebo: 96.9% | `results.json:fire_rate.placebo` | 96.9% | **FOUND** | `OURS` | Placebo fire rate % |
| L20 | Close back inside real: 85.4% (CI 83.0..87.8) | `results.json:A_back_inside.real` | 85.4% (83.0..87.8) | **FOUND** | `OURS` | Close back inside rate for real value |
| L20 | Close back inside placebo: 68.0% | `results.json:A_back_inside.placebo.share` | 68.0% | **FOUND** | `OURS` | Close back inside rate for placebo |
| L25 | Year 2022 Real n: 355 | `results.json:by_year.2022.real.n` | 355 | **FOUND** | `OURS` | Real event count |
| L25 | Year 2022 Real share: 58.6% | `results.json:by_year.2022.real.share` | 58.6% | **FOUND** | `OURS` | Real return share |
| L25 | Year 2022 Real CI: 53.5..63.4 | `results.json:by_year.2022.real.ci` | 53.5..63.4 | **FOUND** | `OURS` | Real CI |
| L25 | Year 2022 Placebo share: 44.8% | `results.json:by_year.2022.placebo.share` | 44.8% | **FOUND** | `OURS` | Placebo share |
| L25 | Year 2022 Diff: +13.8 pp | `results.json:by_year.2022.diff.diff` | +13.8 pp | **FOUND** | `OURS` | Yearly difference |
| L25 | Year 2022 Diff CI: 8.0..19.4 | `results.json:by_year.2022.diff.ci` | 8.0..19.4 | **FOUND** | `OURS` | Yearly difference CI |
| L26 | Year 2023 Real n: 341 | `results.json:by_year.2023.real.n` | 341 | **FOUND** | `OURS` | Real event count |
| L26 | Year 2023 Real share: 54.5% | `results.json:by_year.2023.real.share` | 54.5% | **FOUND** | `OURS` | Real return share |
| L26 | Year 2023 Real CI: 49.3..59.9 | `results.json:by_year.2023.real.ci` | 49.3..59.9 | **FOUND** | `OURS` | Real CI |
| L26 | Year 2023 Placebo share: 47.9% | `results.json:by_year.2023.placebo.share` | 47.9% | **FOUND** | `OURS` | Placebo share |
| L26 | Year 2023 Diff: +6.7 pp | `results.json:by_year.2023.diff.diff` | +6.7 pp | **FOUND** | `OURS` | Yearly difference |
| L26 | Year 2023 Diff CI: 0.4..12.7 | `results.json:by_year.2023.diff.ci` | 0.4..12.7 | **FOUND** | `OURS` | Yearly difference CI |
| L27 | Year 2024 Real n: 175 | `results.json:by_year.2024.real.n` | 175 | **FOUND** | `OURS` | Real event count |
| L27 | Year 2024 Real share: 59.4% | `results.json:by_year.2024.real.share` | 59.4% | **FOUND** | `OURS` | Real return share |
| L27 | Year 2024 Real CI: 52.0..66.7 | `results.json:by_year.2024.real.ci` | 52.0..66.7 | **FOUND** | `OURS` | Real CI |
| L27 | Year 2024 Placebo share: 48.5% | `results.json:by_year.2024.placebo.share` | 48.5% | **FOUND** | `OURS` | Placebo share |
| L27 | Year 2024 Diff: +10.9 pp | `results.json:by_year.2024.diff.diff` | +10.9 pp | **FOUND** | `OURS` | Yearly difference |
| L27 | Year 2024 Diff CI: 2.0..19.7 | `results.json:by_year.2024.diff.ci` | 2.0..19.7 | **FOUND** | `OURS` | Yearly difference CI |
| L32 | Side leave up Real n: 439 | `results.json:by_side.up.real.n` | 439 | **FOUND** | `OURS` | Side event count |
| L32 | Side leave up Real share: 57.4% | `results.json:by_side.up.real.share` | 57.4% | **FOUND** | `OURS` | Side return share |
| L32 | Side leave up Real CI: 52.6..62.0 | `results.json:by_side.up.real.ci` | 52.6..62.0 | **FOUND** | `OURS` | Side return CI |
| L32 | Side leave up Placebo share: 44.6% | `results.json:by_side.up.placebo.share` | 44.6% | **FOUND** | `OURS` | Side placebo share |
| L32 | Side leave up Diff: +12.8 pp | `results.json:by_side.up.diff.diff` | +12.8 pp | **FOUND** | `OURS` | Side difference |
| L32 | Side leave up Diff CI: 7.0..18.3 | `results.json:by_side.up.diff.ci` | 7.0..18.3 | **FOUND** | `OURS` | Side difference CI |
| L33 | Side leave down Real n: 432 | `results.json:by_side.down.real.n` | 432 | **FOUND** | `OURS` | Side event count |
| L33 | Side leave down Real share: 56.9% | `results.json:by_side.down.real.share` | 56.9% | **FOUND** | `OURS` | Side return share |
| L33 | Side leave down Real CI: 52.3..61.8 | `results.json:by_side.down.real.ci` | 52.3..61.8 | **FOUND** | `OURS` | Side return CI |
| L33 | Side leave down Placebo share: 51.7% | `results.json:by_side.down.placebo.share` | 51.7% | **FOUND** | `OURS` | Side placebo share |
| L33 | Side leave down Diff: +5.3 pp | `results.json:by_side.down.diff.diff` | +5.3 pp | **FOUND** | `OURS` | Side difference |
| L33 | Side leave down Diff CI: -0.1..11.0 | `results.json:by_side.down.diff.ci` | -0.1..11.0 | **FOUND** | `OURS` | Side difference CI |
| L38 | Placebo d=-3.0 Events: 109 | `results.json:by_d.-3.0.n` | 109 | **FOUND** | `OURS` | Event count for shift d |
| L38 | Placebo d=-3.0 Return share: 33.9% | `results.json:by_d.-3.0.share` | 33.9% | **FOUND** | `OURS` | Return share for shift d |
| L38 | Placebo d=-3.0 CI: 25.2..42.7 | `results.json:by_d.-3.0.ci` | 25.2..42.7 | **FOUND** | `OURS` | 95% CI for shift d |
| L39 | Placebo d=-2.0 Events: 112 | `results.json:by_d.-2.0.n` | 112 | **FOUND** | `OURS` | Event count for shift d |
| L39 | Placebo d=-2.0 Return share: 48.2% | `results.json:by_d.-2.0.share` | 48.2% | **FOUND** | `OURS` | Return share for shift d |
| L39 | Placebo d=-2.0 CI: 39.1..57.5 | `results.json:by_d.-2.0.ci` | 39.1..57.5 | **FOUND** | `OURS` | 95% CI for shift d |
| L40 | Placebo d=-1.0 Events: 110 | `results.json:by_d.-1.0.n` | 110 | **FOUND** | `OURS` | Event count for shift d |
| L40 | Placebo d=-1.0 Return share: 59.1% | `results.json:by_d.-1.0.share` | 59.1% | **FOUND** | `OURS` | Return share for shift d |
| L40 | Placebo d=-1.0 CI: 50.0..68.2 | `results.json:by_d.-1.0.ci` | 50.0..68.2 | **FOUND** | `OURS` | 95% CI for shift d |
| L41 | Placebo d=-0.5 Events: 108 | `results.json:by_d.-0.5.n` | 108 | **FOUND** | `OURS` | Event count for shift d |
| L41 | Placebo d=-0.5 Return share: 53.7% | `results.json:by_d.-0.5.share` | 53.7% | **FOUND** | `OURS` | Return share for shift d |
| L41 | Placebo d=-0.5 CI: 44.9..63.1 | `results.json:by_d.-0.5.ci` | 44.9..63.1 | **FOUND** | `OURS` | 95% CI for shift d |
| L42 | Placebo d=+0.5 Events: 108 | `results.json:by_d.+0.5.n` | 108 | **FOUND** | `OURS` | Event count for shift d |
| L42 | Placebo d=+0.5 Return share: 56.5% | `results.json:by_d.+0.5.share` | 56.5% | **FOUND** | `OURS` | Return share for shift d |
| L42 | Placebo d=+0.5 CI: 47.1..65.5 | `results.json:by_d.+0.5.ci` | 47.1..65.5 | **FOUND** | `OURS` | 95% CI for shift d |
| L43 | Placebo d=+1.0 Events: 113 | `results.json:by_d.+1.0.n` | 113 | **FOUND** | `OURS` | Event count for shift d |
| L43 | Placebo d=+1.0 Return share: 54.0% | `results.json:by_d.+1.0.share` | 54.0% | **FOUND** | `OURS` | Return share for shift d |
| L43 | Placebo d=+1.0 CI: 44.6..63.7 | `results.json:by_d.+1.0.ci` | 44.6..63.7 | **FOUND** | `OURS` | 95% CI for shift d |
| L44 | Placebo d=+2.0 Events: 112 | `results.json:by_d.+2.0.n` | 112 | **FOUND** | `OURS` | Event count for shift d |
| L44 | Placebo d=+2.0 Return share: 44.6% | `results.json:by_d.+2.0.share` | 44.6% | **FOUND** | `OURS` | Return share for shift d |
| L44 | Placebo d=+2.0 CI: 35.7..53.6 | `results.json:by_d.+2.0.ci` | 35.7..53.6 | **FOUND** | `OURS` | 95% CI for shift d |
| L45 | Placebo d=+3.0 Events: 111 | `results.json:by_d.+3.0.n` | 111 | **FOUND** | `OURS` | Event count for shift d |
| L45 | Placebo d=+3.0 Return share: 24.3% | `results.json:by_d.+3.0.share` | 24.3% | **FOUND** | `OURS` | Return share for shift d |
| L45 | Placebo d=+3.0 CI: 16.7..32.4 | `results.json:by_d.+3.0.ci` | 16.7..32.4 | **FOUND** | `OURS` | 95% CI for shift d |
| L47 | |d| <= 1 days placebo n=439, real n=438 | `results.json:A_near_placebo.placebo.n, real.n` | 439 vs 438 | **FOUND** | `OURS` | Near-value sample sizes |
| L53 | Part B N=3 Applicable: 871 | `results.json:B.3.accepted_of_applicable.applicable` | 871 | **FOUND** | `OURS` | Applicable events |
| L53 | Part B N=3 Accepted: 603 | `results.json:B.3.accepted_of_applicable.accepted` | 603 | **FOUND** | `OURS` | Accepted events |
| L53 | Part B N=3 Return share: 51.2% | `results.json:B.3.real.share` | 51.2% | **FOUND** | `OURS` | Return share after acceptance |
| L53 | Part B N=3 CI: 47.4..55.4 | `results.json:B.3.real.ci` | 47.4..55.4 | **FOUND** | `OURS` | Return share 95% CI |
| L53 | Part B N=3 Placebo share: 42.6% | `results.json:B.3.placebo.share` | 42.6% | **FOUND** | `OURS` | Placebo return share |
| L53 | Part B N=3 Real minus placebo: +8.7 pp | `results.json:B.3.diff.diff` | +8.7 pp | **FOUND** | `OURS` | Difference pp |
| L53 | Part B N=3 Diff CI: 4.1..13.2 | `results.json:B.3.diff.ci` | 4.1..13.2 | **FOUND** | `OURS` | Difference 95% CI |
| L53 | Part B N=3 Minus Part A share: -5.9 pp | `results.json:B.3.vs_A.diff` | -5.9 pp | **FOUND** | `OURS` | Drop vs Part A share |
| L53 | Part B N=3 vs A CI: -8.2..-3.9 | `results.json:B.3.vs_A.ci` | -8.2..-3.9 | **FOUND** | `OURS` | Drop vs Part A CI |
| L54 | Part B N=6 Applicable: 869 | `results.json:B.6.accepted_of_applicable.applicable` | 869 | **FOUND** | `OURS` | Applicable events |
| L54 | Part B N=6 Accepted: 490 | `results.json:B.6.accepted_of_applicable.accepted` | 490 | **FOUND** | `OURS` | Accepted events |
| L54 | Part B N=6 Return share: 47.8% | `results.json:B.6.real.share` | 47.8% | **FOUND** | `OURS` | Return share after acceptance |
| L54 | Part B N=6 CI: 43.3..52.4 | `results.json:B.6.real.ci` | 43.3..52.4 | **FOUND** | `OURS` | Return share 95% CI |
| L54 | Part B N=6 Placebo share: 39.9% | `results.json:B.6.placebo.share` | 39.9% | **FOUND** | `OURS` | Placebo return share |
| L54 | Part B N=6 Real minus placebo: +7.8 pp | `results.json:B.6.diff.diff` | +7.8 pp | **FOUND** | `OURS` | Difference pp |
| L54 | Part B N=6 Diff CI: 2.8..12.7 | `results.json:B.6.diff.ci` | 2.8..12.7 | **FOUND** | `OURS` | Difference 95% CI |
| L54 | Part B N=6 Minus Part A share: -9.4 pp | `results.json:B.6.vs_A.diff` | -9.4 pp | **FOUND** | `OURS` | Drop vs Part A share |
| L54 | Part B N=6 vs A CI: -12.3..-6.5 | `results.json:B.6.vs_A.ci` | -12.3..-6.5 | **FOUND** | `OURS` | Drop vs Part A CI |
| L55 | Part B N=12 Applicable: 867 | `results.json:B.12.accepted_of_applicable.applicable` | 867 | **FOUND** | `OURS` | Applicable events |
| L55 | Part B N=12 Accepted: 387 | `results.json:B.12.accepted_of_applicable.accepted` | 387 | **FOUND** | `OURS` | Accepted events |
| L55 | Part B N=12 Return share: 45.5% | `results.json:B.12.real.share` | 45.5% | **FOUND** | `OURS` | Return share after acceptance |
| L55 | Part B N=12 CI: 40.5..50.5 | `results.json:B.12.real.ci` | 40.5..50.5 | **FOUND** | `OURS` | Return share 95% CI |
| L55 | Part B N=12 Placebo share: 36.6% | `results.json:B.12.placebo.share` | 36.6% | **FOUND** | `OURS` | Placebo return share |
| L55 | Part B N=12 Real minus placebo: +8.9 pp | `results.json:B.12.diff.diff` | +8.9 pp | **FOUND** | `OURS` | Difference pp |
| L55 | Part B N=12 Diff CI: 3.5..13.9 | `results.json:B.12.diff.ci` | 3.5..13.9 | **FOUND** | `OURS` | Difference 95% CI |
| L55 | Part B N=12 Minus Part A share: -11.7 pp | `results.json:B.12.vs_A.diff` | -11.7 pp | **FOUND** | `OURS` | Drop vs Part A share |
| L55 | Part B N=12 vs A CI: -15.4..-8.0 | `results.json:B.12.vs_A.ci` | -15.4..-8.0 | **FOUND** | `OURS` | Drop vs Part A CI |
| L58 | Threshold 0.3%: SOURCED NakedPocTracker.java:26 | `src/main/java/datafeed/NakedPocTracker.java:26` | 0.003 (0.3%) | **FOUND** | `SOURCED` | NakedPocTracker.java:26 REVISIT_THRESHOLD_PCT = 0.003 |
| L61 | Bar range contains POC Real share: 70.3% (CI 67.4..73.3) | `results.json:naked_ci.naked_exact.real` | 70.3% (67.4..73.3) | **FOUND** | `OURS` | Contains POC real share |
| L61 | Bar range contains POC Placebo share: 52.5% | `results.json:naked_ci.naked_exact.placebo.share` | 52.5% | **FOUND** | `OURS` | Contains POC placebo share |
| L61 | Bar range contains POC Real minus placebo: +17.8 pp (CI 14.2..21.6) | `results.json:naked_ci.naked_exact.diff` | +17.8 pp (14.2..21.6) | **FOUND** | `OURS` | Contains POC difference pp and CI |
| L62 | Bar range within 0.3 % Real share: 76.3% (CI 73.7..79.3) | `results.json:naked_ci.naked_near.real` | 76.3% (73.7..79.3) | **FOUND** | `OURS` | Within 0.3% real share |
| L62 | Bar range within 0.3 % Placebo share: 60.2% | `results.json:naked_ci.naked_near.placebo.share` | 60.2% | **FOUND** | `OURS` | Within 0.3% placebo share |
| L62 | Bar range within 0.3 % Real minus placebo: +16.1 pp (CI 12.8..19.4) | `results.json:naked_ci.naked_near.diff` | +16.1 pp (12.8..19.4) | **FOUND** | `OURS` | Within 0.3% difference pp and CI |
| L66 | Events 871; censored 0; fewer bars left than k: k=1: 0, k=3: 1, k=6: 2, k=12: 4 | `results.json:censoring.bars_left_lt` | 0, 1, 2, 4 | **FOUND** | `OURS` | Censored counts for k |
| L67 | Return share restricted to >= 12 bars left: 57.4% (n 867, CI 54.1..61.0) | `results.json:censoring.restricted` | 57.4% (n 867, 54.1..61.0) | **FOUND** | `OURS` | Restricted uncensored return share |
| L68 | Part B censored: N=3: 1, N=6: 0, N=12: 0 | `results.json:censoring.censored_b` | 1, 0, 0 | **FOUND** | `OURS` | Part B censored counts |
| L71 | Cash-session profile (TOM-281) | `RESULT.md:71 (Limits)` | NOT_IN_DATA for BTC (UTC-day value used) | **NOT_IN_DATA** | `OURS` | Cash-session profile not available for continuous 24/7 crypto |
| L71 | Tom's drawn levels | `RESULT.md:71 (Limits)` | NOT_IN_DATA | **NOT_IN_DATA** | `SOURCED` | Subjective chart drawings not retained in machine data |
| L72 | LVN (Low Volume Node) profile calculation | `RESULT.md:72 (Limits)` | Not built (read as beyond value-area edge) | **NOT_IN_DATA** | `OURS` | LVN logic not built; value area edge proxy used |
