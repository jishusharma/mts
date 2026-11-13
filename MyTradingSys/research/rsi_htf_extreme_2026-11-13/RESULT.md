# RESULT: higher-timeframe RSI extreme, next bar closes above, stop = extreme low (edge4-rsi-htf-extreme-1113)

**Verdict: no cell passes.** 0 of 40 pre-registered cells PASS (24 FAIL, 16 UNDERPOWERED; BH 10% significant on VALIDATION: 1 cell, 8h<=15 tgt1R, UNDERPOWERED with n 21). No edge claim.

Regime mix: BTC daily close vs 200d SMA (bull > +5 %, bear < -5 %, else range): DEV (2020-2023) bull 51 % / bear 40 % / range 10 %; VALIDATION (2024-now) bull 56 % / bear 30 % / range 15 %.
Setup: 20 Bybit linear USDT perps from listing (BTC ETH SOL XRP DOGE BNB ADA LINK LTC AVAX DOT ATOM UNI TRX BCH ETC FIL XLM NEAR SAND, none missing); 1288 confirmed signals in total. Signal = red TF bar with RSI(14) <= T (first touch, re-arm > 30), entry = close of the next bar if it closes above the signal close, stop = signal-bar low, 1h walk. Costs 5 bp taker + 1 bp slippage per side (fees.py; stricter than the brief's 4 bp). Net R per trade. Split by entry date: DEV to 2023-12-31, VALIDATION 2024-01-01 on. Targets cap at 20 TF bars, time exit = 10 TF bars.
CI = week-block bootstrap 95 % on VALIDATION per-trade mean R; placebo p = share of 100 random same-coin same-week same-stop draws with mean >= the real mean (0.01 = beat all draws; random longs lose in these windows); day-cluster = one observation per entry day (all coins/signals that day averaged), CI = bootstrap over days.

## Table (40 cells)

| cell | n DEV | n VAL | mean R DEV | mean R VAL | CI VAL (week-block) | placebo p (VAL) | VAL days | day-cluster mean R | day CI | verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| 4h<=20 tgt1R | 125 | 147 | -0.07 | 0.10 | -0.14..0.35 | 0.01 | 40 | 0.02 | -0.29..0.29 | FAIL |
| 4h<=20 tgt2R | 125 | 147 | -0.29 | 0.27 | -0.06..0.66 | 0.01 | 40 | 0.24 | -0.14..0.65 | FAIL |
| 4h<=20 tgt3R | 125 | 147 | -0.24 | 0.35 | -0.07..0.77 | 0.01 | 40 | 0.20 | -0.27..0.70 | FAIL |
| 4h<=20 time10 | 125 | 147 | -0.34 | 0.18 | -0.16..0.59 | 0.01 | 40 | 0.26 | -0.28..0.86 | FAIL |
| 4h<=15 tgt1R | 40 | 51 | 0.16 | 0.14 | -0.12..0.40 | 0.01 | 19 | 0.10 | -0.26..0.46 | FAIL |
| 4h<=15 tgt2R | 40 | 51 | -0.08 | 0.40 | -0.08..0.90 | 0.01 | 19 | 0.28 | -0.19..0.78 | FAIL |
| 4h<=15 tgt3R | 40 | 51 | -0.04 | 0.50 | -0.05..1.14 | 0.01 | 19 | 0.32 | -0.24..0.90 | FAIL |
| 4h<=15 time10 | 40 | 51 | -0.39 | 0.61 | -0.04..1.34 | 0.01 | 19 | 0.28 | -0.35..1.09 | FAIL |
| 4h<=12 tgt1R | 13 | 20 | 0.20 | 0.36 | -0.28..0.64 | 0.01 | 8 | 0.07 | -0.47..0.54 | UNDERPOWERED |
| 4h<=12 tgt2R | 13 | 20 | 0.55 | 0.69 | -0.23..1.05 | 0.01 | 8 | 0.27 | -0.39..0.93 | UNDERPOWERED |
| 4h<=12 tgt3R | 13 | 20 | 0.42 | 0.96 | -0.15..1.46 | 0.01 | 8 | 0.45 | -0.35..1.38 | UNDERPOWERED |
| 4h<=12 time10 | 13 | 20 | -0.12 | 1.17 | -0.25..1.85 | 0.01 | 8 | 0.42 | -0.39..1.31 | UNDERPOWERED |
| 4h<=12 d<30 tgt1R | 8 | 16 | 0.33 | 0.32 | -0.41..0.69 | 0.01 | 7 | 0.02 | -0.56..0.55 | UNDERPOWERED |
| 4h<=12 d<30 tgt2R | 8 | 16 | 0.65 | 0.60 | -0.32..0.99 | 0.01 | 7 | 0.23 | -0.51..0.95 | UNDERPOWERED |
| 4h<=12 d<30 tgt3R | 8 | 16 | 0.19 | 0.81 | -0.34..1.40 | 0.01 | 7 | 0.42 | -0.47..1.43 | UNDERPOWERED |
| 4h<=12 d<30 time10 | 8 | 16 | -0.33 | 1.06 | -0.35..1.70 | 0.01 | 7 | 0.47 | -0.47..1.48 | UNDERPOWERED |
| 8h<=25 tgt1R | 175 | 154 | -0.02 | -0.05 | -0.28..0.18 | 0.01 | 62 | -0.13 | -0.36..0.11 | FAIL |
| 8h<=25 tgt2R | 175 | 154 | -0.07 | -0.02 | -0.34..0.34 | 0.01 | 62 | -0.11 | -0.41..0.20 | FAIL |
| 8h<=25 tgt3R | 175 | 154 | -0.11 | 0.02 | -0.33..0.42 | 0.01 | 62 | -0.07 | -0.39..0.29 | FAIL |
| 8h<=25 time10 | 175 | 154 | -0.12 | 0.04 | -0.33..0.47 | 0.01 | 62 | -0.07 | -0.41..0.31 | FAIL |
| 8h<=20 tgt1R | 71 | 76 | 0.10 | 0.35 | -0.00..0.58 | 0.01 | 24 | 0.08 | -0.26..0.40 | FAIL |
| 8h<=20 tgt2R | 71 | 76 | -0.12 | 0.38 | -0.07..0.76 | 0.01 | 24 | -0.02 | -0.46..0.44 | FAIL |
| 8h<=20 tgt3R | 71 | 76 | -0.08 | 0.43 | -0.10..0.90 | 0.01 | 24 | -0.01 | -0.49..0.53 | FAIL |
| 8h<=20 time10 | 71 | 76 | 0.02 | 0.29 | -0.25..0.69 | 0.01 | 24 | -0.19 | -0.58..0.24 | FAIL |
| 8h<=15 tgt1R | 21 | 21 | 0.02 | 0.73 | 0.42..0.89 | 0.01 | 10 | 0.60 | 0.18..0.90 | UNDERPOWERED (BH) |
| 8h<=15 tgt2R | 21 | 21 | -0.08 | 0.26 | -0.50..0.57 | 0.01 | 10 | -0.22 | -0.75..0.34 | UNDERPOWERED |
| 8h<=15 tgt3R | 21 | 21 | 0.01 | 0.19 | -0.59..0.53 | 0.02 | 10 | -0.29 | -0.79..0.22 | UNDERPOWERED |
| 8h<=15 time10 | 21 | 21 | 1.06 | 0.29 | -0.61..0.71 | 0.01 | 10 | -0.30 | -0.82..0.28 | UNDERPOWERED |
| 12h<=25 tgt1R | 124 | 110 | 0.00 | 0.21 | -0.11..0.52 | 0.01 | 40 | 0.18 | -0.09..0.44 | FAIL |
| 12h<=25 tgt2R | 124 | 110 | -0.09 | 0.17 | -0.21..0.57 | 0.01 | 40 | 0.19 | -0.18..0.59 | FAIL |
| 12h<=25 tgt3R | 124 | 110 | -0.13 | 0.11 | -0.26..0.52 | 0.01 | 40 | 0.10 | -0.34..0.59 | FAIL |
| 12h<=25 time10 | 124 | 110 | -0.18 | 0.24 | -0.17..0.70 | 0.01 | 40 | 0.41 | -0.16..1.07 | FAIL |
| 12h<=20 tgt1R | 57 | 47 | -0.17 | 0.54 | 0.02..0.77 | 0.01 | 15 | 0.16 | -0.30..0.59 | FAIL |
| 12h<=20 tgt2R | 57 | 47 | -0.16 | 0.56 | 0.11..0.93 | 0.01 | 15 | 0.42 | -0.24..1.11 | FAIL |
| 12h<=20 tgt3R | 57 | 47 | -0.16 | 0.49 | 0.01..1.02 | 0.01 | 15 | 0.44 | -0.29..1.21 | FAIL |
| 12h<=20 time10 | 57 | 47 | -0.23 | 0.30 | -0.44..0.89 | 0.01 | 15 | 0.21 | -0.45..1.01 | FAIL |
| 12h<=15 tgt1R | 14 | 22 | -0.09 | 0.51 | -0.05..0.64 | 0.01 | 8 | 0.31 | -0.30..0.83 | UNDERPOWERED |
| 12h<=15 tgt2R | 14 | 22 | -0.17 | 0.28 | -0.21..0.42 | 0.01 | 8 | -0.10 | -0.68..0.65 | UNDERPOWERED |
| 12h<=15 tgt3R | 14 | 22 | -0.09 | 0.20 | -0.15..0.44 | 0.01 | 8 | -0.01 | -0.85..0.99 | UNDERPOWERED |
| 12h<=15 time10 | 14 | 22 | 0.17 | -0.05 | -0.49..0.64 | 0.01 | 8 | -0.25 | -0.86..0.50 | UNDERPOWERED |

## Best 3 cells (VALIDATION n >= 30, by mean R)
- 4h<=15 time10: n VAL 51, mean 0.61 R, CI -0.04..1.34, placebo p 0.01, day-cluster 19 days mean 0.28 (CI -0.35..1.09), DEV mean -0.39, week-block p 0.054 -> FAIL (not BH-significant)
- 12h<=20 tgt2R: n VAL 47, mean 0.56 R, CI 0.11..0.93, placebo p 0.01, day-cluster 15 days mean 0.42 (CI -0.24..1.11), DEV mean -0.16, week-block p 0.012 -> FAIL (not BH-significant)
- 12h<=20 tgt1R: n VAL 47, mean 0.54 R, CI 0.02..0.77, placebo p 0.01, day-cluster 15 days mean 0.16 (CI -0.30..0.59), DEV mean -0.17, week-block p 0.022 -> FAIL (not BH-significant)

## What the table says
- Nearly every VALIDATION mean is positive on 4h and 12h, but DEV (2020-2023) means are mostly negative (e.g. 4h<=20: -0.07 to -0.34, 12h<=20: about -0.17): the 2024+ gain does not appear in the earlier four years, so it reads as a regime effect (VALIDATION is 56 % bull) and not a stable rule.
- The operator's BTC observation does not scale: 4h<=12 pooled is 33 signals in six years over 20 coins (20 in VALIDATION, 8 distinct days); with daily RSI < 30: 24 signals, VALIDATION mean +0.60R (2R target) / +0.81R (3R) but CI -0.32..+1.40 and 7 distinct days. UNDERPOWERED. DEV 4h<=12 d<30 is also positive (+0.65R at 2R, n 8), the same sign in both splits, so this is the one cell family worth more data, not a pass.
- Only one cell is BH-significant: 8h<=15 tgt1R (n 21, mean +0.73R, 10 days, DEV mean +0.02); n < 30, so UNDERPOWERED. Its sibling exits (2R, 3R, time10) are weak, so it is likely noise within the 40-cell family.
- Week-block CI lower bound is above 0 for 8h<=20 tgt1R (just: -0.002 no), 12h<=20 tgt1R/2R/3R (0.02/0.11/0.01) but the BH 10 % filter over 40 cells rejects them (p 0.012-0.022) and the per-day-cluster CI for each includes 0. Dedupe by day cuts the effective sample: e.g. 12h<=20: 47 trades = 15 days.
- Placebo is not the discriminating test here: random same-week longs lose after costs so nearly every cell beats it (p = 0.01).

## Daily RSI band split, 2R target (descriptive, no CI): mean R / n, DEV then VAL
| TF, T | daily <30 DEV | <30 VAL | 30-40 DEV | 30-40 VAL | >40 DEV | >40 VAL |
|---|---|---|---|---|---|---|
| 4h <= 12 | 0.65 / 8 | 0.60 / 16 | 0.78 / 4 | 1.04 / 4 | -1.21 / 1 | - / 0 |
| 4h <= 15 | -0.02 / 21 | 0.40 / 26 | -0.03 / 17 | 0.47 / 21 | -1.11 / 2 | -0.01 / 4 |
| 4h <= 20 | -0.45 / 32 | -0.07 / 32 | -0.30 / 59 | 0.49 / 84 | -0.13 / 34 | 0.05 / 31 |
| 8h <= 15 | -0.08 / 16 | 0.29 / 18 | -0.09 / 4 | 0.07 / 3 | - / 0 | - / 0 |
| 8h <= 20 | -0.22 / 43 | 0.43 / 48 | 0.08 / 27 | 0.22 / 25 | -1.17 / 1 | 0.91 / 3 |
| 8h <= 25 | 0.07 / 47 | -0.03 / 37 | -0.18 / 109 | 0.02 / 106 | 0.13 / 18 | -0.30 / 11 |
| 12h <= 15 | -0.17 / 14 | 0.32 / 20 | - / 0 | -0.10 / 2 | - / 0 | - / 0 |
| 12h <= 20 | -0.29 / 47 | 0.53 / 37 | 0.27 / 9 | 0.66 / 10 | - / 0 | - / 0 |
| 12h <= 25 | -0.23 / 63 | 0.05 / 57 | 0.05 / 58 | 0.29 / 51 | 0.48 / 2 | 0.49 / 2 |

Daily RSI < 30 does not systematically beat 30-40 once n is large (4h<=20: -0.45 DEV / -0.07 VAL vs -0.30 / +0.49 for 30-40); the 'daily < 30' conditioner is only supported at 4h<=12 (n 8 + 16).

## Next best test
Pool 4h<=12 (and 8h<=15) signals with the stricter deep-extreme on more liquid coins / spot history back to 2017 and watch for the same sign across all years; the exit that works is the 2-3R target, not the time exit. Not a trade rule yet.

## Limits
No funding. 20 coins are highly correlated (week-block and day-cluster show it). Some R values explode when the signal bar is tiny. Stops on hourly lows; target fills at the target price. Cells share entries across exits, so BH over 40 is approximate. Trades without a full 20-bar forward window are dropped (the newest ones). Files: PRE_REG.md, htf_lib.py, study.py, test_htf.py, cells.csv, bands.csv, trades_4h12_daily_lt30.csv.
