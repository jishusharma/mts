COUNTS: MATCH=93 DIFF=5 NOT_IN_DATA=3

# Re-derivation: pre_us_failed_break_10sym_2026-11/RESULT.md

Run 2026-11-12 by `rederive-preus` (Antigravity), task `gpt-rederive-pre-us-failed-break-10sym-1108`.
Reads only (`RESULT.md`, `PRE_REG.md`, `ledger.csv`, `per_symbol.csv`, `COUNT.json`, `analysis.json`, `FORMULAS.md`); study code (`run_10sym.py`, `analyze.py`) was not read. No source files edited; no git commit or ship.

## 1. Pooled & Check numbers (from `ledger.csv`, n=1393)

| # | RESULT.md claim | Recomputed | Status | Notes |
|---|---|---|---|---|
| 1 | Pooled `n` = 1393 | 1393 | MATCH | Row count in `ledger.csv` |
| 2 | Mean net bps of K = -2.47 | -2.467156 (-2.47) | MATCH | Arithmetic mean of `net_bps` |
| 3 | SE (day-clustered) = 4.39 | 4.391812 (4.39) | MATCH | Cluster-robust SE by UTC `date` (`G=584` days) without `G/(G-1)` DFC; with `G/(G-1)` DFC: 4.395577 (4.40) |
| 4 | `t` (day-clustered) = -0.56 | -0.561763 (-0.56) | MATCH | `mean / SE_cluster` |
| 5 | 95% CI lower = -11.08 | -11.075107 (-11.08) | MATCH | `mean - 1.96 * SE_cluster` |
| 6 | 95% CI upper = +6.14 | +6.140795 (+6.14) | MATCH | `mean + 1.96 * SE_cluster` |
| 7 | SE plain = 3.21 | 3.214786 (3.21) | MATCH | `sd_sample / sqrt(n)` |
| 8 | `t` plain = -0.77 | -0.767440 (-0.77) | MATCH | `mean / SE_plain` |
| 9 | Measured `sd` = 119.99 | 119.985186 (119.99) | MATCH | Sample SD (`ddof=1`) of `net_bps` |
| 10 | Time-cap days = 1270 | 1270 | MATCH | `outcome == "TIME"` (91.17% of 1393; Reading "91%" matches) |
| 11 | Time-cap sum = -16,400 bps | -16399.801702 (-16,400) | MATCH | Sum of `net_bps` where `outcome == "TIME"` (Reading "-16.4k bps" matches) |
| 12 | Target days = 123 | 123 | MATCH | `outcome == "TARGET"` |
| 13 | Target sum = +12,963 bps | +12963.053071 (+12,963) | MATCH | Sum of `net_bps` where `outcome == "TARGET"` (Reading "+13.0k bps" matches) |
| 14 | MDD of cumulative net (pooled, % of K) = 97.9 | 97.930719 (97.9) | MATCH | Additive cumulative `net_bps / 100` sorted by `(date, sym)` (Reading "98%" matches). Note: strict `(date, t_min, sym)` chronological sort gives 97.437331 (97.4%) |
| 15 | Win rate = 60.7% | 60.7322% (60.7%) | MATCH | `846 / 1393` with `net_bps > 0` |
| 16 | Mean winner = +45.96 bps | +45.958449 (+45.96) | MATCH | Mean of `net_bps > 0` (`n=846`) |
| 17 | Mean loser = -77.36 bps | -77.363065 (-77.36) | MATCH | Mean of `net_bps <= 0` (`n=547`, all strictly `< 0`) |
| 18 | MAE % of K p50 = 0.21 | 0.206274 (0.21) | MATCH | Linear-interpolated 50th percentile of `mae_pct` |
| 19 | MAE % of K p90 = 1.87 | 1.867970 (1.87) | MATCH | Linear-interpolated 90th percentile of `mae_pct` |
| 20 | MAE % of K p99 = 6.22 | 6.218739 (6.22) | MATCH | Linear-interpolated 99th percentile of `mae_pct` |
| 21 | MAE % of K max = 22.25 | 22.249139 (22.25) | MATCH | Max of `mae_pct` |
| 22 | Tranches filled 1 = 553 | 553 | MATCH | Count of `tranches == 1` |
| 23 | Tranches filled 2 = 310 | 310 | MATCH | Count of `tranches == 2` |
| 24 | Tranches filled 3 = 190 | 190 | MATCH | Count of `tranches == 3` |
| 25 | Tranches filled 4 = 340 | 340 | MATCH | Count of `tranches == 4` |

## 2. By year & positive symbol count (from `ledger.csv`)

| # | RESULT.md claim | Recomputed | Status | Notes |
|---|---|---|---|---|
| 26 | 2022 `n` = 552 | 552 | MATCH | `date` starting with `2022` |
| 27 | 2022 `mean` = +3.64 | +3.640349 (+3.64) | MATCH | |
| 28 | 2023 `n` = 573 | 573 | MATCH | `date` starting with `2023` |
| 29 | 2023 `mean` = -8.29 | -8.293715 (-8.29) | MATCH | |
| 30 | 2024 `n` = 268 | 268 | MATCH | `date` starting with `2024` |
| 31 | 2024 `mean` = -2.59 | -2.589264 (-2.59) | MATCH | |
| 32 | Five of ten symbols positive = 5 | 5 | MATCH | BNBUSDT, DOGEUSDT, ADAUSDT, AVAXUSDT, LINKUSDT |

## 3. Per-symbol table (from `ledger.csv`, 10 symbols x 6 metrics = 60 numbers)

| Symbol | n (claim / rec) | mean (claim / rec) | sd (claim / rec) | win (claim / rec) | time-cap days (claim / rec) | sum bps (claim / rec) | Status |
|---|---|---|---|---|---|---|---|
| BTCUSDT | 177 / 177 | -3.24 / -3.237955 | 68.96 / 68.957663 | 0.60 / 0.604520 | 155 / 155 | -573 / -573.118008 | 6 MATCH |
| ETHUSDT | 186 / 186 | -2.51 / -2.505941 | 87.23 / 87.228018 | 0.58 / 0.575269 | 171 / 171 | -466 / -466.104946 | 6 MATCH |
| SOLUSDT | 141 / 141 | -24.04 / -24.040643 | 152.02 / 152.024448 | 0.61 / 0.609929 | 136 / 136 | -3390 / -3389.730596 | 6 MATCH |
| BNBUSDT | 128 / 128 | +3.47 / 3.472738 | 61.81 / 61.808953 | 0.61 / 0.609375 | 120 / 120 | +445 / 444.510471 | 6 MATCH |
| XRPUSDT | 124 / 124 | -0.07 / -0.074491 | 81.52 / 81.523577 | 0.57 / 0.572581 | 109 / 109 | -9 / -9.236887 | 6 MATCH |
| DOGEUSDT | 131 / 131 | +1.65 / 1.648283 | 232.59 / 232.594497 | 0.66 / 0.664122 | 122 / 122 | +216 / 215.925042 | 6 MATCH |
| ADAUSDT | 106 / 106 | +11.86 / 11.863933 | 118.06 / 118.055340 | 0.58 / 0.584906 | 95 / 95 | +1258 / 1257.576936 | 6 MATCH |
| AVAXUSDT | 115 / 115 | +3.05 / 3.052420 | 121.71 / 121.710815 | 0.62 / 0.617391 | 101 / 101 | +351 / 351.028285 | 6 MATCH |
| LINKUSDT | 137 / 137 | +9.68 / 9.683396 | 92.63 / 92.633131 | 0.64 / 0.635036 | 125 / 125 | +1327 / 1326.625255 | 6 MATCH |
| LTCUSDT | 148 / 148 | -17.53 / -17.528542 | 109.19 / 109.192042 | 0.61 / 0.608108 | 136 / 136 | -2594 / -2594.224182 | 6 MATCH |

## 4. Gate output (`scripts/dev/prereg_gate.py`)

Command from `RESULT.md`:
`python scripts/dev/prereg_gate.py --n 1393 --sd 120 --sd-source "analysis.json (measured sd of net bps)" --cost 14 --m auto --new-cells 1 --max-gross 30`

| # | RESULT.md claim | Recomputed (`--m auto`) | Status | Notes |
|---|---|---|---|---|
| 93 | `m 221` | `249` | DIFF | Trial ledger grew since 2026-11-08; `--m 221` reproduces exact downstream values |
| 94 | `z_holm 3.688` | `3.718` | DIFF | `3.688` when run with `--m 221` |
| 95 | `MDE 14.558` | `14.655` | DIFF | `14.558` when run with `--m 221` |
| 96 | `R + cost 14 = 28.558` | `28.655` | DIFF | `28.558` when run with `--m 221` |
| 97 | `n needed 1153` | `1169` | DIFF | `1153` when run with `--m 221` |
| 98 | `PASS: may freeze` | `PASS: may freeze` | MATCH | Verdict unchanged under both `m=221` and `m=249` |

## 5. External-data items (`NOT_IN_DATA`)

| # | RESULT.md claim | Status | Notes |
|---|---|---|---|
| 99 | BTC buy-and-hold MDD = 66.9% | NOT_IN_DATA | BTC 1d price tape over DEV (2022-01-01..2024-06-30) is not in the folder or repo |
| 100 | Regime mix: `130 weeks: bull 25 (19%) \| bear 0 (0%) \| range 105 (81%) \| n/a 0 (0%)` | NOT_IN_DATA | BTC spot 1d context (`research_kit.weekly_regimes`) not in folder or repo |
| 101 | By regime week: `bull n=255 mean -2.43; range n=1138 mean -2.48; bear 0` | NOT_IN_DATA | Weekly regime tags not in folder or repo |
