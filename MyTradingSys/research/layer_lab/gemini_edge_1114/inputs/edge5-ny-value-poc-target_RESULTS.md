# RESULT: prior-NY-session POC as the target, confirmed on 10 NEW coins

**Verdict: FAIL, 0 of 8 cells pass. The "70% to the POC" count only reproduces when setups whose POC is already behind or next to entry are counted; at a real 36 bp+ distance the POC is reached about 41-47% (not 69%), and every cell has negative fee-net mean R (best: balanced / stop extreme / short, -0.006 R, CI straddles 0, fails Bonferroni).**

Slug edge5-ny-value-poc-target-1113. PRE_REG.md was committed (sha 7bb8e9922) before any outcome. Code: fetch_1m.py, parent_study.py (parent code, unchanged), study5.py, report5.py, diag5.py, test_study5.py (3 tests pass).
Data: Binance spot 1m (data.binance.vision), 2020-01 to 2026-10, no monthly file errors; late listings start later (AVAX 2020-09-22, DOT 2020-08-18; SOL in the seen set 2020-08-11, parent used 2020-09). Costs 5 bp taker + 1 bp slip per side (12 bp round trip). Time exit at session end, stop-first, closed bars.
Pass rule: all six PRE_REG checks per cell (mean > 0; trade CI and day CI lower bound > 0; n >= 100 and >= 60 days; placebo p95 and placebo p < 0.00625 with 2000 draws; Bonferroni day-cluster p < 0.00625; 2024+ slice mean > 0).

## What the 69% really was (descriptive diagnostic, diag5.py, not a cell)
Parent definition of reach-POC (any 1m bar after entry touches the POC, including a POC already at or behind entry) gives 69.3% on the 10 new coins (n = 2786 setups; seen coins 68.5%), so the number replicates. But it is made of three groups:

| group (new coins) | n | share | reach-POC % |
|---|---|---|---|
| POC already at/behind entry (dist <= 0): touched on the next bar, no trade exists | 977 | 35.1% | 94.8 |
| POC ahead but < 36 bp away (below 3 x round-trip cost) | 673 | 24.2% | 77.6 |
| POC >= 36 bp ahead (tradable) | 1136 | 40.8% | 42.6 |

Seen coins, same split: 35.2% / 24.7% / 40.1% of setups, reach 93.8 / 79.1 / 39.7%. Skipped for the 36 bp rule: 1650 of 2786 setups (59.2%) on new coins, 545 of 910 (59.9%) on seen coins. The tradable share reaches the POC only about 40-47% of the time, and with a stop as wide as the session extreme (median reward-to-risk 0.5) that is not enough.

## Coverage new coins

| coin | first | last | 1m bars | sessions | open outside | setups | skipped (POC < 36 bp) |
|---|---|---|---|---|---|---|---|
| BNBUSDT | 2020-01-01 | 2026-10-31 | 3,591,914 | 1781 | 1381 | 264 | 162 |
| XRPUSDT | 2020-01-01 | 2026-10-31 | 3,591,915 | 1781 | 1334 | 291 | 178 |
| DOGEUSDT | 2020-01-01 | 2026-10-31 | 3,591,914 | 1781 | 1339 | 307 | 180 |
| ADAUSDT | 2020-01-01 | 2026-10-31 | 3,591,914 | 1781 | 1345 | 268 | 151 |
| AVAXUSDT | 2020-09-22 | 2026-10-31 | 3,210,826 | 1593 | 1219 | 274 | 151 |
| LINKUSDT | 2020-01-01 | 2026-10-31 | 3,591,914 | 1781 | 1345 | 277 | 147 |
| LTCUSDT | 2020-01-01 | 2026-10-31 | 3,591,915 | 1781 | 1357 | 301 | 172 |
| DOTUSDT | 2020-08-18 | 2026-10-31 | 3,260,236 | 1617 | 1216 | 259 | 147 |
| TRXUSDT | 2020-01-01 | 2026-10-31 | 3,591,914 | 1781 | 1419 | 265 | 192 |
| BCHUSDT | 2020-01-01 | 2026-10-31 | 3,591,914 | 1781 | 1365 | 280 | 170 |
| total | | | | | | 2786 | 1650 (59.2%) |

## New coins (TEST)

### Count table

| cell | n | days | reach-POC % | reach-stop % | median RR | mean R gross | mean R net | best 10 days R / total R (sum over trades) | per-year mean net R (n) |
|---|---|---|---|---|---|---|---|---|---|
| all / stop extreme / long | 467 | 330 | 40.7 | 16.3 | 0.47 | -0.009 | -0.084 | 20.4 / -39.3 | 2020:-0.24(52) 2021:0.01(59) 2022:-0.13(81) 2023:0.01(71) 2024:-0.08(77) 2025:-0.07(60) 2026:-0.11(67) |
| balanced / stop extreme / long | 250 | 190 | 37.6 | 20.8 | 0.51 | -0.070 | -0.154 | 13.0 / -38.6 | 2020:-0.36(24) 2021:-0.14(28) 2022:-0.15(49) 2023:-0.11(36) 2024:-0.10(44) 2025:-0.14(28) 2026:-0.16(41) |
| all / stop extreme / short | 669 | 420 | 43.9 | 16.9 | 0.51 | 0.015 | -0.062 | 30.5 / -41.3 | 2020:-0.10(68) 2021:-0.01(119) 2022:-0.05(105) 2023:-0.09(108) 2024:-0.10(100) 2025:-0.10(107) 2026:0.03(62) |
| balanced / stop extreme / short | 370 | 238 | 46.5 | 14.6 | 0.52 | 0.077 | -0.006 | 25.7 / -2.3 | 2020:-0.03(27) 2021:-0.04(62) 2022:-0.02(69) 2023:0.04(50) 2024:-0.06(56) 2025:0.01(68) 2026:0.07(38) |
| all / stop edge / long | 467 | 330 | 40.7 | 57.8 | 2.17 | 0.007 | -0.379 | 70.4 / -177.2 | 2020:-0.81(52) 2021:-0.12(59) 2022:-0.46(81) 2023:-0.26(71) 2024:-0.15(77) 2025:-0.47(60) 2026:-0.48(67) |
| balanced / stop edge / long | 250 | 190 | 37.6 | 59.6 | 2.15 | -0.090 | -0.501 | 43.6 / -125.3 | 2020:-1.28(24) 2021:-0.19(28) 2022:-0.49(49) 2023:-0.57(36) 2024:-0.12(44) 2025:-0.81(28) 2026:-0.40(41) |
| all / stop edge / short | 669 | 420 | 43.9 | 56.5 | 2.00 | -0.028 | -0.346 | 75.4 / -231.5 | 2020:-0.33(68) 2021:-0.24(119) 2022:-0.33(105) 2023:-0.22(108) 2024:-0.53(100) 2025:-0.41(107) 2026:-0.41(62) |
| balanced / stop edge / short | 370 | 238 | 46.5 | 52.7 | 2.00 | 0.123 | -0.225 | 73.7 / -83.1 | 2020:-0.03(27) 2021:-0.15(62) 2022:-0.14(69) 2023:-0.08(50) 2024:-0.35(56) 2025:-0.31(68) 2026:-0.48(38) |

### Trade table

| cell | n | days | reach-POC % | median RR | mean R gross | mean R net | trade CI | day CI | placebo p (mean / p95) | 2024+ mean (n) | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| all / stop extreme / long | 467 | 330 | 40.7 | 0.47 | -0.009 | -0.084 | [-0.138, -0.030] | [-0.148, -0.020] | 0.0005 (-0.125 / -0.107) | -0.088 (204) | FAIL |
| balanced / stop extreme / long | 250 | 190 | 37.6 | 0.51 | -0.070 | -0.154 | [-0.229, -0.076] | [-0.239, -0.071] | 0.0855 (-0.176 / -0.149) | -0.132 (113) | FAIL |
| all / stop extreme / short | 669 | 420 | 43.9 | 0.51 | 0.015 | -0.062 | [-0.112, -0.010] | [-0.124, 0.001] | 0.0025 (-0.097 / -0.079) | -0.070 (269) | FAIL |
| balanced / stop extreme / short | 370 | 238 | 46.5 | 0.52 | 0.077 | -0.006 | [-0.074, 0.065] | [-0.085, 0.073] | 0.0015 (-0.051 / -0.026) | 0.001 (162) | FAIL |
| all / stop edge / long | 467 | 330 | 40.7 | 2.17 | 0.007 | -0.379 | [-0.523, -0.226] | [-0.539, -0.214] | 0.2025 (-0.424 / -0.332) | -0.354 (204) | FAIL |
| balanced / stop edge / long | 250 | 190 | 37.6 | 2.15 | -0.090 | -0.501 | [-0.689, -0.295] | [-0.689, -0.299] | 0.4745 (-0.504 / -0.376) | -0.394 (113) | FAIL |
| all / stop edge / short | 669 | 420 | 43.9 | 2.00 | -0.028 | -0.346 | [-0.461, -0.223] | [-0.476, -0.213] | 0.4595 (-0.350 / -0.266) | -0.453 (269) | FAIL |
| balanced / stop edge / short | 370 | 238 | 46.5 | 2.00 | 0.123 | -0.225 | [-0.393, -0.041] | [-0.421, -0.020] | 0.1415 (-0.297 / -0.188) | -0.362 (162) | FAIL |

Failed checks per cell: all / stop extreme / long: mean,trade_ci,day_ci,bonf,slice2024; balanced / stop extreme / long: mean,trade_ci,day_ci,placebo,bonf,slice2024; all / stop extreme / short: mean,trade_ci,day_ci,bonf,slice2024; balanced / stop extreme / short: mean,trade_ci,day_ci,bonf; all / stop edge / long: mean,trade_ci,day_ci,placebo,bonf,slice2024; balanced / stop edge / long: mean,trade_ci,day_ci,placebo,bonf,slice2024; all / stop edge / short: mean,trade_ci,day_ci,placebo,bonf,slice2024; balanced / stop edge / short: mean,trade_ci,day_ci,placebo,bonf,slice2024

## Coverage seen data

| coin | first | last | 1m bars | sessions | open outside | setups | skipped (POC < 36 bp) |
|---|---|---|---|---|---|---|---|
| BTCUSDT | 2020-01-01 | 2026-10-31 | 3,591,915 | 1781 | 1334 | 328 | 221 |
| ETHUSDT | 2020-01-01 | 2026-10-31 | 3,591,914 | 1781 | 1311 | 293 | 165 |
| SOLUSDT | 2020-08-11 | 2026-10-31 | 3,271,335 | 1623 | 1271 | 289 | 159 |
| total | | | | | | 910 | 545 (59.9%) |

## Seen data (BTC/ETH/SOL, NOT part of the verdict)

### Count table

| cell | n | days | reach-POC % | reach-stop % | median RR | mean R gross | mean R net | best 10 days R / total R (sum over trades) | per-year mean net R (n) |
|---|---|---|---|---|---|---|---|---|---|
| all / stop extreme / long | 142 | 129 | 36.6 | 16.2 | 0.37 | -0.006 | -0.079 | 11.3 / -11.2 | 2020:0.12(16) 2021:-0.16(16) 2022:-0.29(20) 2023:-0.03(12) 2024:-0.09(28) 2025:-0.06(29) 2026:-0.01(21) |
| balanced / stop extreme / long | 78 | 72 | 37.2 | 17.9 | 0.41 | 0.027 | -0.056 | 10.5 / -4.3 | 2020:0.35(8) 2021:-0.43(5) 2022:-0.33(13) 2023:0.04(9) 2024:-0.07(14) 2025:0.04(17) 2026:-0.05(12) |
| all / stop extreme / short | 223 | 199 | 41.7 | 17.0 | 0.48 | 0.009 | -0.067 | 19.6 / -14.9 | 2020:0.07(21) 2021:-0.18(37) 2022:0.03(39) 2023:0.06(30) 2024:-0.00(37) 2025:-0.17(44) 2026:-0.35(15) |
| balanced / stop extreme / short | 126 | 111 | 40.5 | 16.7 | 0.47 | 0.047 | -0.036 | 17.3 / -4.5 | 2020:0.47(8) 2021:-0.19(19) 2022:0.04(27) 2023:0.08(16) 2024:0.11(19) 2025:-0.21(25) 2026:-0.32(12) |
| all / stop edge / long | 142 | 129 | 36.6 | 57.0 | 1.87 | 0.037 | -0.333 | 48.4 / -47.3 | 2020:0.11(16) 2021:0.52(16) 2022:-1.00(20) 2023:-0.34(12) 2024:-0.56(28) 2025:-0.43(29) 2026:-0.24(21) |
| balanced / stop edge / long | 78 | 72 | 37.2 | 53.8 | 1.98 | 0.044 | -0.357 | 28.9 / -27.9 | 2020:0.98(8) 2021:-0.53(5) 2022:-1.29(13) 2023:-0.77(9) 2024:-0.37(14) 2025:-0.18(17) 2026:-0.10(12) |
| all / stop edge / short | 223 | 199 | 41.7 | 60.5 | 2.19 | -0.120 | -0.484 | 45.0 / -107.9 | 2020:-0.13(21) 2021:-0.27(37) 2022:-0.41(39) 2023:-0.45(30) 2024:-0.61(37) 2025:-0.71(44) 2026:-0.76(15) |
| balanced / stop edge / short | 126 | 111 | 40.5 | 54.0 | 2.06 | 0.027 | -0.334 | 35.3 / -42.1 | 2020:0.07(8) 2021:-0.09(19) 2022:-0.31(27) 2023:-0.20(16) 2024:-0.68(19) 2025:-0.40(25) 2026:-0.54(12) |

### Trade table

| cell | n | days | reach-POC % | median RR | mean R gross | mean R net | trade CI | day CI | placebo p (mean / p95) | 2024+ mean (n) | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| all / stop extreme / long | 142 | 129 | 36.6 | 0.37 | -0.006 | -0.079 | [-0.178, 0.023] | [-0.177, 0.022] | 0.0925 (-0.108 / -0.072) | -0.058 (78) | FAIL (seen, info) |
| balanced / stop extreme / long | 78 | 72 | 37.2 | 0.41 | 0.027 | -0.056 | [-0.200, 0.094] | [-0.205, 0.100] | 0.1480 (-0.091 / -0.036) | -0.024 (43) | FAIL (seen, info) |
| all / stop extreme / short | 223 | 199 | 41.7 | 0.48 | 0.009 | -0.067 | [-0.159, 0.035] | [-0.166, 0.036] | 0.0045 (-0.121 / -0.088) | -0.134 (96) | FAIL (seen, info) |
| balanced / stop extreme / short | 126 | 111 | 40.5 | 0.47 | 0.047 | -0.036 | [-0.171, 0.113] | [-0.180, 0.123] | 0.0135 (-0.099 / -0.052) | -0.128 (56) | FAIL (seen, info) |
| all / stop edge / long | 142 | 129 | 36.6 | 1.87 | 0.037 | -0.333 | [-0.642, 0.052] | [-0.656, 0.040] | 0.0805 (-0.479 / -0.301) | -0.426 (78) | FAIL (seen, info) |
| balanced / stop edge / long | 78 | 72 | 37.2 | 1.98 | 0.044 | -0.357 | [-0.706, 0.026] | [-0.727, 0.048] | 0.4895 (-0.356 / -0.112) | -0.219 (43) | FAIL (seen, info) |
| all / stop edge / short | 223 | 199 | 41.7 | 2.19 | -0.120 | -0.484 | [-0.680, -0.273] | [-0.691, -0.261] | 0.7565 (-0.424 / -0.273) | -0.682 (96) | FAIL (seen, info) |
| balanced / stop edge / short | 126 | 111 | 40.5 | 2.06 | 0.027 | -0.334 | [-0.599, -0.058] | [-0.608, -0.053] | 0.5040 (-0.327 / -0.133) | -0.526 (56) | FAIL (seen, info) |

Failed checks per cell: all / stop extreme / long: mean,trade_ci,day_ci,placebo,bonf,slice2024; balanced / stop extreme / long: mean,trade_ci,day_ci,size,placebo,bonf,slice2024; all / stop extreme / short: mean,trade_ci,day_ci,bonf,slice2024; balanced / stop extreme / short: mean,trade_ci,day_ci,placebo,bonf,slice2024; all / stop edge / long: mean,trade_ci,day_ci,placebo,bonf,slice2024; balanced / stop edge / long: mean,trade_ci,day_ci,size,placebo,bonf,slice2024; all / stop edge / short: mean,trade_ci,day_ci,placebo,bonf,slice2024; balanced / stop edge / short: mean,trade_ci,day_ci,placebo,bonf,slice2024

## Per coin, stop A, both sides, all days

| coin | n | reach-POC % | mean net R |
|---|---|---|---|
| BNBUSDT | 102 | 43.1 | -0.089 |
| XRPUSDT | 113 | 45.1 | -0.053 |
| DOGEUSDT | 127 | 38.6 | -0.135 |
| ADAUSDT | 117 | 47.0 | -0.031 |
| AVAXUSDT | 123 | 43.1 | -0.071 |
| LINKUSDT | 130 | 41.5 | -0.040 |
| LTCUSDT | 129 | 40.3 | -0.166 |
| DOTUSDT | 112 | 50.0 | 0.039 |
| TRXUSDT | 73 | 34.2 | -0.156 |
| BCHUSDT | 110 | 40.9 | -0.024 |

Regime mix: BTC UTC days (close vs 200-day SMA, 5% band): DEV bull 54.0% / bear 37.0% / range 9.0%; 2024+ bull 56.4% / bear 29.8% / range 13.8%. New-coin setups (stop A, all days) by that label: DEV {'bull': 48.9, 'bear': 35.1, 'range': 7.5, 'n/a': 8.4, 'balanced_share': 52.0, 'n': 663}; 2024+ {'bull': 58.4, 'bear': 27.5, 'range': 14.2, 'n/a': 0.0, 'balanced_share': 58.1, 'n': 473}.

Reading the tables: gross mean R is about zero in every cell (best +0.12 R, stop edge, balanced short, with a 53% stop rate); the 12 bp round trip then takes 0.07-0.4 R depending on the stop width. Stop B (value edge + 10 bp) is tight (median RR about 2) and is hit 53-60% of the time, so it loses more after costs. The placebo (random entry inside value with the same stop/target logic) loses 0.05-0.5 R too, so the entry timing beats random in the stop-extreme cells (placebo p 0.0005-0.0025) yet still does not make money. Best-10-days column is the sum of R over the 10 best session dates over the total R sum; with negative totals the ratio is meaningless, so sums are shown.
The 8 cells overlap (balanced is a subset of all days; stops A and B share the same entries), so they are not independent and the Bonferroni divisor 8 is conservative; it does not matter here, no cell is positive.
Per-year signs are mostly negative in every year (no year-dependent rescue); the one near-zero cell (balanced / stop extreme / short, 2024+ +0.001 on n=162) has a day CI [-0.085, 0.073].

## Limits
- Spot volume, not perp; US holidays treated as sessions; 30m closes from 1m closes; fills at close with fixed 1 bp slippage; stop gaps inside a 1m bar not modelled.
- The placebo draws one random candidate per trade (candidates = 1m closes from bar 89 to session end inside value, passing the 36 bp rule); trades with no candidate are left out of the placebo only.
- Balanced rule, 36 bp POC gate, stop buffers, bin size are OURS (see PRE_REG parameter table).
- The "69%" diagnostic and the three-group split were added after seeing the parent numbers: descriptive only.
