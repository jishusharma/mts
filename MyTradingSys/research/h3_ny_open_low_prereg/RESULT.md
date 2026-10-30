# H3 result (rule frozen in PRE_REG.md, run once; numbers from `h3_test.py`, raw in `results.json`)

**Verdict: FAIL on the pre-registered criteria (criterion 1: n=6 < 30). Direction agreed, but the sample is far too small to say anything. Not usable.**

Data note (deviation from the plan, forced): the Binance USDT-M archive has no BTCUSDT 1m monthly files before 2020-01
(404 for 2019-09..2019-12), so the "untouched" sample is 2020-01-01..2021-12-31 (88 weekdays lost, 0 other days beyond the 5-minute gap rule).
Command: `fetch_binance_archive.py --start 2019-09-01 --end 2021-12-31 --datasets klines --out Dumps/backtest/raw_1m_2019`.
Run: `python MyTradingSys/research/h3_ny_open_low_prereg/h3_test.py <Dumps/backtest>`.

| Period | n | Hit rate (Wilson 95%) | Mean gross bp | Mean net bp (taker 10 bp RT) | Bootstrap 95% net bp | Binomial p (>=50%) |
|---|---|---|---|---|---|---|
| Test 2020-01..2021-12 (decides) | 6 | 83.3% [43.7, 97.0] | 79.0 | 69.0 | [2.4, 148.9] | 0.109 |
| Main 2022-01..2026-09 (in-sample) | 59 | 72.9% [60.4, 82.6] | 28.9 | 18.9 | [-15.1, 50.0] | 0.0003 |

By year, test: 2020 n=2, 2021 n=4 (5 of 6 up). Main: 2022 n=8 75%; 2023 n=11 82%; 2024 n=11 73%; 2025 n=16 56% (net -27.9 bp); 2026 n=13 85%.
The main run reproduces the study (n=59, 72.9%).

| Criterion | Result |
|---|---|
| 1. n >= 30 | NO (6) |
| 2. hit >= 60% and p < 0.05 | NO (83.3%, p=0.109) |
| 3. net > 0 and bootstrap lower > 0 | yes (69 bp, 2.4) |
| 4. at most 1 bad year | yes |

Reading: the event was rare in 2020-2021 (6 events in about 520 days, against 59 in about 1200 days later), so the untouched sample cannot confirm or reject
the effect. Main-period net edge is positive on average (18.9 bp) but its bootstrap interval includes zero and 2025 was negative, in-sample and after ~70
cells of search. H3 long is NOT validated. Funding and slippage not modelled. Parameters all OURS.
A different untouched sample (another venue/instrument, or the 2019-09..12 months from another source) would need its own pre-registration.
