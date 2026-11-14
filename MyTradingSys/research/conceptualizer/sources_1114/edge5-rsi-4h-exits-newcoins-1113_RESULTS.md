# RESULT: 4h RSI-extreme exits on 40 unseen coins (edge5-rsi-4h-exits-newcoins-1113)

**Verdict: time8 FAIL, confstop_2R FAIL.** Neither confirms the parent's near-miss. Test set = whole new-coin set, nothing tuned; code and rules as in PRE_REG.md (committed before outcomes).

Regime mix: BTC daily vs 200d SMA, 2021-01..2026-11: bull 51 % / bear 36 % / range 12 %; 2024-01..now: bull 56 % / bear 30 % / range 15 %.

Data: Bybit v5 public spot 1h, 40 coins with trades (history from ~2021-22), S3 (4h RSI<=20 + confirm) = 452 trades on 145 signal days. Cost 12 bp round trip (2 x 5 bp taker + 2 bp slippage) divided by stop distance.

| cell | n | win% | mean R net | trade CI (week-block) | day CI (plain / week-block) | placebo p (mean) | per-year mean R (n) | without best 5 days | verdict |
|---|---|---|---|---|---|---|---|---|---|
| time8 | 452 | 56.0 | +0.051 (gross +0.131) | [-0.161, +0.293], one-sided p 0.34 | [-0.273, +0.074] / [-0.262, +0.078]; day mean -0.092 | 0.005 (placebo mean -0.188) | 2021 +0.05 (7); 2022 +0.40 (83); 2023 -0.37 (84); 2024 +0.14 (108); 2025 +0.04 (123); 2026 +0.00 (47) | -0.151 (n 386, CI [-0.298, -0.005]) | FAIL |
| confstop_2R | 452 | 43.1 (median -1.01) | +0.081 (gross +0.129) | [-0.163, +0.330], one-sided p 0.28 | [-0.167, +0.260] / [-0.155, +0.255]; day mean +0.043 | 0.005 (placebo mean -0.391) | 2021 +0.67 (7); 2022 +0.15 (83); 2023 -0.12 (84); 2024 +0.01 (108); 2025 +0.30 (123); 2026 -0.17 (47) | -0.135 (n 374, CI [-0.345, +0.108]) | FAIL |

2024-01-01-onward slice (n 278): time8 +0.074 [-0.131, +0.281]; confstop_2R +0.107 [-0.270, +0.495]. Both CIs include 0.

Failed gates (both cells): trade CI lower bound < 0, both day-cluster lower bounds < 0, Bonferroni bootstrap p (0.34 / 0.28) > 0.025. Passed: n >= 100, placebo (the real entries beat random 4h closes of the same coin-week: the random baseline loses 0.19 / 0.39 R, so the confirm-after-capitulation entry adds something over random, but not enough to be positive with confidence).

Concentration: the best 5 signal days carry more than 100 % of total R (time8 351 %, confstop_2R 239 %); with those 5 days removed the mean is -0.151 (time8) and -0.135 (confstop_2R). Best days: 2022-05-10, 2024-07-05, 2025-04-07, 2025-02-03, 2026-02-06 (time8); 2025-04-07, 2025-10-11, 2024-07-05, 2024-08-05, 2022-11-10 (confstop_2R): market-wide capitulation days where many coins signal at once and bounce together. Day-level means (one value per day) are lower than the trade means (time8 day mean -0.09), i.e. multi-coin crash days carry the profit. The parent's near-misses do not replicate: mean R fell from +0.20 / +0.26 to +0.05 / +0.08, and the sign flips without the top days.

Limits: current-volume universe (survivorship, dead coins absent); spot series not the parent's perp series; stop-first on 1h bars; no funding; per-year n tiny for 2021.

Files: PRE_REG.md, fetch.py, study.py, exits_lib.py, rsi_grid_lib.py, test_study.py, results.json.
