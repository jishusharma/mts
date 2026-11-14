# RESULT: re-derive HTF RSI extreme on 10 symbols, fee-net OOS 2024+ (rederive-rsi-htf-extreme-1115)

**Verdict: NO EDGE.** 0 of 40 pre-registered cells PASS (20 FAIL, 20 UNDERPOWERED). Same answer as the 20-coin parent (0/40). Fee-net, VALIDATION (2024-01-01..now) n 636 total confirmed signals over 10 symbols (DEV+VAL, 6 years); n per cell below.

Regime mix: BTC daily close vs 200d SMA (bull > +5 %, bear < -5 %, else range): DEV (2020-2023) bull 51 % / bear 40 % / range 10 %; VALIDATION (2024-now) bull 56 % / bear 30 % / range 14 % (parent said 15 %, rounding; 1049 days).
Setup: PRE_REG.md in this folder, 10 Bybit linear USDT perps (BTC ETH SOL XRP DOGE BNB ADA LINK LTC AVAX, none missing), parent's code unchanged, costs 5 bp taker + 1 bp slippage per side (OURS, fees.py), rule parameters SOURCED (operator: RSI extreme red bar, next bar closes above, stop = extreme low, 1R/2R/3R, 10-bar time exit) or OURS (re-arm > 30, 20-bar cap, thresholds grid, cost level) as labelled in PRE_REG.

## Table (40 cells)
| cell | n DEV | n VAL | mean R DEV | mean R VAL | CI VAL (week-block) | placebo p | VAL days | day mean R | day CI | verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| 4h<=20 tgt1R | 60 | 69 | -0.04 | 0.15 | -0.16..0.47 | 0.01 | 24 | 0.08 | -0.25..0.42 | FAIL |
| 4h<=20 tgt2R | 60 | 69 | -0.29 | 0.40 | -0.13..0.92 | 0.01 | 24 | 0.34 | -0.16..0.84 | FAIL |
| 4h<=20 tgt3R | 60 | 69 | -0.30 | 0.57 | -0.11..1.22 | 0.01 | 24 | 0.31 | -0.30..0.92 | FAIL |
| 4h<=20 time10 | 60 | 69 | -0.34 | 0.35 | -0.17..0.93 | 0.01 | 24 | 0.34 | -0.32..1.16 | FAIL |
| 4h<=15 tgt1R | 20 | 31 | -0.03 | 0.17 | -0.12..0.46 | 0.01 | 15 | 0.16 | -0.26..0.53 | FAIL |
| 4h<=15 tgt2R | 20 | 31 | -0.22 | 0.42 | -0.07..0.91 | 0.01 | 15 | 0.33 | -0.20..0.87 | FAIL |
| 4h<=15 tgt3R | 20 | 31 | -0.09 | 0.51 | -0.06..1.15 | 0.01 | 15 | 0.38 | -0.24..1.02 | FAIL |
| 4h<=15 time10 | 20 | 31 | -0.61 | 0.57 | -0.03..1.30 | 0.01 | 15 | 0.42 | -0.32..1.38 | FAIL |
| 4h<=12 tgt1R | 9 | 12 | 0.27 | 0.27 | -0.53..0.65 | 0.01 | 7 | 0.02 | -0.60..0.57 | UNDERPOWERED |
| 4h<=12 tgt2R | 9 | 12 | 0.80 | 0.45 | -0.32..0.99 | 0.02 | 7 | 0.20 | -0.50..0.91 | UNDERPOWERED |
| 4h<=12 tgt3R | 9 | 12 | 0.61 | 0.70 | -0.35..1.49 | 0.01 | 7 | 0.40 | -0.57..1.41 | UNDERPOWERED |
| 4h<=12 time10 | 9 | 12 | -0.07 | 0.79 | -0.37..1.50 | 0.01 | 7 | 0.39 | -0.47..1.42 | UNDERPOWERED |
| 4h<=12 d<30 tgt1R | 5 | 10 | 0.57 | 0.23 | -0.52..0.72 | 0.02 | 6 | 0.02 | -0.68..0.61 | UNDERPOWERED |
| 4h<=12 d<30 tgt2R | 5 | 10 | 1.11 | 0.35 | -0.52..1.00 | 0.01 | 6 | 0.20 | -0.60..1.12 | UNDERPOWERED |
| 4h<=12 d<30 tgt3R | 5 | 10 | 0.38 | 0.55 | -0.32..1.50 | 0.01 | 6 | 0.41 | -0.56..1.56 | UNDERPOWERED |
| 4h<=12 d<30 time10 | 5 | 10 | -0.42 | 0.65 | -0.43..1.55 | 0.01 | 6 | 0.40 | -0.59..1.47 | UNDERPOWERED |
| 8h<=25 tgt1R | 83 | 77 | -0.04 | 0.13 | -0.17..0.43 | 0.01 | 37 | 0.01 | -0.28..0.30 | FAIL |
| 8h<=25 tgt2R | 83 | 77 | -0.08 | 0.13 | -0.29..0.58 | 0.01 | 37 | -0.02 | -0.39..0.38 | FAIL |
| 8h<=25 tgt3R | 83 | 77 | -0.15 | 0.07 | -0.41..0.57 | 0.01 | 37 | -0.08 | -0.48..0.35 | FAIL |
| 8h<=25 time10 | 83 | 77 | -0.16 | 0.12 | -0.32..0.66 | 0.01 | 37 | -0.08 | -0.43..0.33 | FAIL |
| 8h<=20 tgt1R | 34 | 33 | -0.04 | 0.32 | -0.05..0.55 | 0.01 | 16 | 0.08 | -0.33..0.46 | FAIL |
| 8h<=20 tgt2R | 34 | 33 | -0.31 | 0.25 | -0.21..0.54 | 0.01 | 16 | -0.01 | -0.51..0.50 | FAIL |
| 8h<=20 tgt3R | 34 | 33 | -0.25 | 0.22 | -0.28..0.52 | 0.01 | 16 | -0.11 | -0.62..0.52 | FAIL |
| 8h<=20 time10 | 34 | 33 | -0.04 | 0.20 | -0.36..0.65 | 0.01 | 16 | -0.02 | -0.58..0.65 | FAIL |
| 8h<=15 tgt1R | 12 | 11 | -0.12 | 0.63 | 0.16..0.96 | 0.01 | 5 | 0.45 | -0.33..0.94 | UNDERPOWERED (BH) |
| 8h<=15 tgt2R | 12 | 11 | -0.14 | 0.38 | -0.54..0.94 | 0.02 | 5 | 0.02 | -0.79..0.84 | UNDERPOWERED |
| 8h<=15 tgt3R | 12 | 11 | 0.03 | 0.25 | -0.54..0.60 | 0.07 | 5 | -0.12 | -0.81..0.56 | UNDERPOWERED |
| 8h<=15 time10 | 12 | 11 | 1.92 | 0.38 | -0.49..1.00 | 0.03 | 5 | 0.02 | -0.85..0.90 | UNDERPOWERED |
| 12h<=25 tgt1R | 56 | 54 | -0.14 | 0.20 | -0.28..0.70 | 0.01 | 20 | 0.25 | -0.11..0.61 | FAIL |
| 12h<=25 tgt2R | 56 | 54 | -0.15 | -0.02 | -0.49..0.58 | 0.01 | 20 | 0.07 | -0.39..0.54 | FAIL |
| 12h<=25 tgt3R | 56 | 54 | -0.10 | -0.11 | -0.56..0.50 | 0.01 | 20 | 0.00 | -0.46..0.51 | FAIL |
| 12h<=25 time10 | 56 | 54 | -0.12 | 0.18 | -0.39..1.05 | 0.01 | 20 | 0.54 | -0.26..1.65 | FAIL |
| 12h<=20 tgt1R | 31 | 24 | -0.19 | 0.54 | -0.03..0.85 | 0.01 | 10 | 0.37 | -0.14..0.78 | UNDERPOWERED |
| 12h<=20 tgt2R | 31 | 24 | -0.15 | 0.54 | 0.11..0.98 | 0.01 | 10 | 0.54 | -0.24..1.28 | UNDERPOWERED (BH) |
| 12h<=20 tgt3R | 31 | 24 | -0.19 | 0.67 | 0.22..1.28 | 0.01 | 10 | 0.79 | -0.15..1.77 | UNDERPOWERED (BH) |
| 12h<=20 time10 | 31 | 24 | -0.22 | 0.38 | -0.38..1.11 | 0.01 | 10 | 0.40 | -0.45..1.52 | UNDERPOWERED |
| 12h<=15 tgt1R | 8 | 12 | -0.00 | 0.60 | -0.06..0.82 | 0.01 | 5 | 0.46 | -0.33..0.94 | UNDERPOWERED |
| 12h<=15 tgt2R | 8 | 12 | -0.13 | 0.49 | 0.44..0.58 | 0.01 | 5 | 0.23 | -0.74..1.19 | UNDERPOWERED (BH) |
| 12h<=15 tgt3R | 8 | 12 | -0.00 | 0.25 | -0.08..0.94 | 0.01 | 5 | 0.30 | -0.84..1.81 | UNDERPOWERED |
| 12h<=15 time10 | 8 | 12 | 0.47 | 0.05 | -0.30..0.73 | 0.01 | 5 | -0.00 | -0.88..0.88 | UNDERPOWERED |

## What the table says
- Nothing PASSes. All 4h and 8h cells with n >= 30 FAIL: VAL week-block CI includes 0 (best: 4h<=15 time10 mean +0.57R n 31, CI -0.03..1.30, day CI -0.32..1.38). DEV means are negative for nearly every cell (4h<=20: -0.04 to -0.34; 12h<=25: -0.10 to -0.15), so the positive 2024+ means look like the bull-leaning validation regime, not a stable rule.
- The cells that clear the BH filter are all UNDERPOWERED and tiny: 8h<=15 tgt1R (n 11, 5 days), 12h<=20 tgt2R and tgt3R (n 24, 10 days; CI 0.11..0.98 and 0.22..1.28 but day CI -0.24..1.28 and -0.15..1.77, DEV -0.15 / -0.19), 12h<=15 tgt2R (n 12, 5 days). VAL n < 30 voids them. 12h<=20 is the same cell family the parent flagged (47 trades on 20 coins, week-block CI above 0, day CI crossing 0, BH-rejected); with 10 symbols it falls to n 24, 10 days: unchanged story, thin and regime-dependent.
- Operator's gated cell (4h<=12, daily RSI < 30): n 10 VAL / 5 DEV, 6 distinct VAL days, +0.35R (2R) / +0.55R (3R), CI -0.52..1.00 and -0.32..1.50: UNDERPOWERED. Same sign in DEV (+1.11 / +0.38, n 5) as VAL, as in the parent, but 10 trades cannot decide. The BTC 2-3R observation remains an anecdote.
- Placebo p is 0.01 almost everywhere (random same-week longs lose after fees), so it does not discriminate; week-block CI, DEV sign and day-cluster CI do.

## Compared with the parent (20 coins)
Same verdict (0 PASS), same BH cells in the same families (8h<=15 tgt1R, 12h<=20 tgt2R/3R appear now; the parent had 8h<=15 tgt1R only), VALIDATION means for cells with n >= 30 within about 0.1-0.2 R of the parent. Halving the universe halves n; it does not reveal a hidden edge on liquid coins.

## Limits
No funding; stops on hourly lows; tiny signal bars inflate R; 10 symbols are highly correlated (day-cluster n 5-37); BH over 40 is approximate (cells share entries across exits); VAL is 56 % bull; the 4h<=12 and daily<30 cells would need pooled history before 2020 or more symbols (the parent's next-best-test) to be judged. Files: PRE_REG.md, study.py, fetch.py, htf_lib.py, rsi_grid_lib.py, test_htf.py (3 tests OK), cells.csv, bands.csv, meta.json, trades_4h12_daily_lt30.csv, study.log, fetch.log.
