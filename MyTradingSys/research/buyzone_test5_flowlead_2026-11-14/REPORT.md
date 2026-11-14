# REPORT: Test 5, large-trade flow lead test, BTC

Rules frozen in `PRE_REG.md` (committed before any outcome). Code `flow.py`, `run_test5.py`, `fetch_flow.py`, `fetch_cb.py`; tests `test_flow.py`. Data: Binance public aggTrades (spot + USD-M futures, BTCUSDT) reduced to large-trade sums, Binance spot 1d price, Coinbase BTC-USD 1d; host caches, never committed. A LEAD-signal test: no trade result is claimed, nothing here is a trade instruction.

**Verdict: KILL.** Primary = all phases, VAL, next-24 h, top vs bottom flow quintile, both cutoffs.

| cutoff | VAL n | VAL spread bp | 95% CI bp | shuffle band bp | shuffle pct | DEV n | DEV spread bp | pass |
|---|---|---|---|---|---|---|---|---|
| ALL1M | 1046 | 32.6 | [-7.92, 75.06] | [-40.97, 37.64] | 95.2 | 365 | 8.32 | False |
| ALL5M | 1046 | 4.81 | [-29.0, 39.14] | [-33.59, 34.93] | 62.0 | 365 | -1.41 | False |

## Coverage and regime mix

Flow days used: 1411, 2023-01-01 to 2026-11-11. Dropped: {'no_flow': 0, 'no_phase': 0, 'no_ret24': 1}. Regime mix: share of flow days per phase per split.

| split | n | UP | BASE | RANGE | DOWN | POSTPEAK_BEAR | max one-year share |
|---|---|---|---|---|---|---|---|
| DEV | 365 | 72.6% | 1.4% | 16.2% | 0.0% | 9.9% | 1.0 |
| VAL | 1046 | 57.4% | 0.0% | 16.3% | 10.9% | 15.4% | 0.35 |
| RECENT | 499 | 36.9% | 0.0% | 10.6% | 20.2% | 32.3% | 0.631 |

Regime mix: DEV, VAL and RECENT shares above; a split with max one-year share above 0.85 is ONE-YEAR and cannot carry a PASS alone.

## Quintile table, next-24 h return (bp), all phases

| feature | split | n | Q1 | Q2 | Q3 | Q4 | Q5 | spread bp | CI bp | shuffle pct | Spearman |
|---|---|---|---|---|---|---|---|---|---|---|---|
| ALL1M | DEV | 365 | 24.19 | 15.18 | 50.19 | 25.25 | 32.51 | 8.32 | [-73.92, 88.6] | 63.9 | -0.036 |
| ALL1M | VAL | 1046 | -13.53 | 16.51 | 39.38 | -8.66 | 19.07 | 32.6 | [-7.92, 75.06] | 95.2 | -0.002 |
| ALL1M | RECENT | 499 | -17.33 | 26.64 | 24.49 | -45.82 | 1.93 | 19.25 | [-31.25, 69.54] | 75.2 | -0.041 |
| ALL5M | DEV | 365 | 7.73 | 47.1 | 61.97 | 24.22 | 6.31 | -1.41 | [-72.49, 69.48] | 48.4 | -0.054 |
| ALL5M | VAL | 1046 | 2.42 | -5.49 | 30.01 | 34.21 | 7.22 | 4.81 | [-29.0, 39.14] | 62.0 | -0.003 |
| ALL5M | RECENT | 499 | -14.32 | 29.66 | 47.24 | 16.53 | -13.3 | 1.02 | [-42.24, 43.9] | 49.1 | -0.034 |
| SPOT1M | DEV | 365 | 65.24 | 42.49 | nan | 24.7 | -1.04 | -66.28 |  |  | -0.112 |
| SPOT1M | VAL | 1046 | 22.8 | 52.44 | nan | -21.91 | 0.17 | -22.63 |  |  | -0.034 |
| SPOT1M | RECENT | 499 | 21.59 | 15.05 | nan | -30.08 | -23.02 | -44.61 |  |  | -0.049 |
| FUT1M | DEV | 365 | 26.97 | 14.3 | 51.11 | 3.71 | 51.24 | 24.27 | [-74.23, 118.86] | 61.8 | -0.029 |
| FUT1M | VAL | 1046 | -15.02 | 7.95 | 40.6 | 3.38 | 17.96 | 32.98 | [-9.68, 76.92] | 94.7 | -0.000 |
| FUT1M | RECENT | 499 | -18.62 | 24.06 | 41.51 | -49.17 | 1.53 | 20.15 | [-32.28, 71.93] | 75.1 | -0.040 |
| SPOT5M | DEV | 365 | 258.69 | nan | nan | nan | 28.2 | -230.48 |  |  | -0.051 |
| SPOT5M | VAL | 1046 | 22.52 | nan | nan | nan | 6.92 | -15.6 |  |  | -0.001 |
| SPOT5M | RECENT | 499 | -12.15 | nan | nan | nan | -5.1 | 7.05 |  |  | 0.018 |
| FUT5M | DEV | 365 | 10.69 | 51.11 | 53.79 | 22.08 | 9.65 | -1.04 | [-70.78, 67.41] | 46.8 | -0.051 |
| FUT5M | VAL | 1046 | 1.95 | -3.02 | 12.28 | 37.96 | 7.28 | 5.33 | [-28.35, 38.86] | 62.7 | -0.003 |
| FUT5M | RECENT | 499 | -15.2 | 48.58 | 25.97 | 6.42 | -12.06 | 3.14 | [-39.26, 45.41] | 53.4 | -0.034 |
| PREM | DEV | 365 | 33.16 | 24.83 | -25.01 | 70.77 | 43.56 | 10.4 | [-81.25, 105.84] | 43.7 | -0.028 |
| PREM | VAL | 1046 | -2.58 | -13.4 | 54.19 | 14.5 | 27.79 | 30.37 | [-21.9, 79.92] | 89.6 | 0.039 |
| PREM | RECENT | 499 | -12.76 | -7.01 | 84.57 | -11.54 | -28.0 | -15.24 | [-72.11, 42.07] | 34.4 | 0.033 |

## 72 h (stride 3, offsets 0/1/2 as replicates), all phases

| feature | split | offset | n | spread bp | Spearman |
|---|---|---|---|---|---|
| ALL1M | DEV | 0 | 122 | 283.17 | 0.248 |
| ALL1M | DEV | 1 | 121 | 172.65 | 0.059 |
| ALL1M | DEV | 2 | 122 | 27.08 | 0.043 |
| ALL1M | VAL | 0 | 348 | 0.27 | -0.005 |
| ALL1M | VAL | 1 | 348 | 96.64 | 0.061 |
| ALL1M | VAL | 2 | 348 | -20.36 | -0.085 |
| ALL5M | DEV | 0 | 122 | 227.9 | 0.191 |
| ALL5M | DEV | 1 | 121 | 14.82 | -0.040 |
| ALL5M | DEV | 2 | 122 | -20.55 | -0.002 |
| ALL5M | VAL | 0 | 348 | -54.54 | -0.040 |
| ALL5M | VAL | 1 | 348 | 102.32 | 0.092 |
| ALL5M | VAL | 2 | 348 | -49.56 | -0.050 |

## Concurrent check (Spearman of flow with the SAME day's return)

| feature | DEV | VAL |
|---|---|---|
| ALL1M | 0.767 | 0.642 |
| ALL5M | 0.571 | 0.460 |

## Per phase, ALL1M, next-24 h, spread bp (n)

| split | UP | BASE | RANGE | DOWN | POSTPEAK_BEAR |
|---|---|---|---|---|---|
| DEV | -31.75 (265) | nan (5) UNDERPOWERED | 61.22 (59) UNDERPOWERED | None (0) UNDERPOWERED | 518.55 (36) UNDERPOWERED |
| VAL | 12.96 (600) | None (0) UNDERPOWERED | 113.67 (171) | 71.24 (114) | 2.05 (161) UNDERPOWERED |
| RECENT | -10.09 (184) | None (0) UNDERPOWERED | 12.55 (53) UNDERPOWERED | 84.87 (101) | 2.05 (161) UNDERPOWERED |

## Fee-net rows (descriptive, bp per trade, next-24 h, all phases; no trade claimed)

| feature | split | fee | long Q5 | short Q1 | two-leg spread (2 x fee) |
|---|---|---|---|---|---|
| ALL1M | DEV | 12 bp | 20.51 | -36.19 | -15.68 |
| ALL1M | DEV | 6 bp | 26.51 | -30.19 | -3.68 |
| ALL1M | VAL | 12 bp | 7.07 | 1.53 | 8.6 |
| ALL1M | VAL | 6 bp | 13.07 | 7.53 | 20.6 |
| ALL1M | RECENT | 12 bp | -10.07 | 5.33 | -4.75 |
| ALL1M | RECENT | 6 bp | -4.07 | 11.33 | 7.25 |
| ALL5M | DEV | 12 bp | -5.69 | -19.73 | -25.41 |
| ALL5M | DEV | 6 bp | 0.31 | -13.73 | -13.41 |
| ALL5M | VAL | 12 bp | -4.78 | -14.42 | -19.19 |
| ALL5M | VAL | 6 bp | 1.22 | -8.42 | -7.19 |
| ALL5M | RECENT | 12 bp | -25.3 | 2.32 | -22.98 |
| ALL5M | RECENT | 6 bp | -19.3 | 8.32 | -10.98 |

Quintile edges (bp, from DEV): ALL1M [-70.01, -19.06, 15.87, 61.39]; ALL5M [-18.79, -2.37, 3.35, 16.25]; SPOT1M [-5.87, 0.0, 0.0, 8.92]; FUT1M [-81.07, -23.51, 18.34, 73.26]; SPOT5M [0.0, 0.0, 0.0, 0.0]; FUT5M [-20.89, -3.63, 3.92, 19.06]; PREM [-0.73, 1.21, 2.74, 5.34]

PREM = Coinbase BTC-USD close vs Binance BTCUSDT close, bp; mixes the USD-USDT basis with the premium. Binance futures aggTrades come from the public data dump; the brief's Bybit caveat concerns funding and OI, not used here.
