# REPORT: 4h / 8h / 12h RSI(14) <= 12 + daily RSI < 30 + next candle closes higher (edge4-rsi-4h-le12-daily-lt30-1113)

**Result: UNDERPOWERED.** VALIDATION n by cell 0..12; largest-n VALIDATION cell 4h 3R: n=12, fee-net mean 0.814 R, CI [n/a, n/a], P1 placebo p=0.029, BH=True. 0 of 12 cells PASS. Rule: `PRE_REG.md` (frozen before any outcome).

Regime mix: BTC daily close vs 200d SMA (bull > +5%, bear < -5%, else range), share of days: DEV bull 57% / bear 34% / range 9%; VAL bull 62% / bear 11% / range 27%; RECENT bull 36% / bear 54% / range 10%.

Round-trip cost 0.0012 (2 x fees.BINANCE_TAKER + fees.SLIPPAGE_RT_S13), no funding; stop = signal-candle low; entry at the close of the confirming candle; 12-bar cap after entry; 20 Bybit perps from listing (2020-03 on).

## Pooled all-period (descriptive, the card's headline)
| TF | exit | n | mean net R | 95% CI | win % | mean net % |
|---|---|---|---|---|---|---|
| 4h | 1R | 35 | 0.166 | [-0.127, 0.375] | 65.7 | 1.97 |
| 4h | 2R | 35 | 0.245 | [-0.298, 0.667] | 60.0 | 2.73 |
| 4h | 3R | 35 | 0.235 | [-0.304, 0.685] | 57.1 | 2.60 |
| 4h | time | 35 | 0.097 | [-0.428, 0.568] | 54.3 | 2.26 |
| 8h | 1R | 18 | -0.152 | [n/a, n/a] | 44.4 | -0.07 |
| 8h | 2R | 18 | -0.024 | [n/a, n/a] | 44.4 | 0.01 |
| 8h | 3R | 18 | 0.143 | [n/a, n/a] | 44.4 | 0.38 |
| 8h | time | 18 | -0.047 | [n/a, n/a] | 44.4 | -0.02 |
| 12h | 1R | 7 | 0.028 | [n/a, n/a] | 71.4 | 2.91 |
| 12h | 2R | 7 | 0.017 | [n/a, n/a] | 71.4 | 2.17 |
| 12h | 3R | 7 | 0.017 | [n/a, n/a] | 71.4 | 2.17 |
| 12h | time | 7 | 0.017 | [n/a, n/a] | 71.4 | 2.17 |

## By split (CI only at n >= 30; P1 = coin/split-matched random bars with only 'next closes higher'; P2 = same restricted to daily RSI < 30; p = share of placebo means >= observed)
| TF | exit | split | n | mean net R | 95% CI | win % | P1 mean R | P1 p | P2 mean R | P2 p | BH10 (VAL) | PASS (VAL) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 4h | 1R | DEV | 19 UNDERPOWERED | 0.116 | [n/a, n/a] | 57.9 | -0.184 | 0.075 | -0.093 | 0.175 |  |  |
| 4h | 1R | VAL | 12 UNDERPOWERED | 0.391 | [n/a, n/a] | 83.3 | -0.135 | 0.039 | 0.043 | 0.099 | yes | no |
| 4h | 1R | RECENT | 4 UNDERPOWERED | -0.276 | [n/a, n/a] | 50.0 | -0.214 | 0.600 | -0.193 | 0.595 |  |  |
| 4h | 2R | DEV | 19 UNDERPOWERED | 0.051 | [n/a, n/a] | 47.4 | -0.152 | 0.261 | -0.050 | 0.359 |  |  |
| 4h | 2R | VAL | 12 UNDERPOWERED | 0.643 | [n/a, n/a] | 83.3 | -0.077 | 0.030 | 0.034 | 0.056 | yes | no |
| 4h | 2R | RECENT | 4 UNDERPOWERED | -0.026 | [n/a, n/a] | 50.0 | -0.176 | 0.411 | -0.200 | 0.371 |  |  |
| 4h | 3R | DEV | 19 UNDERPOWERED | -0.128 | [n/a, n/a] | 42.1 | -0.151 | 0.454 | -0.103 | 0.528 |  |  |
| 4h | 3R | VAL | 12 UNDERPOWERED | 0.814 | [n/a, n/a] | 83.3 | -0.071 | 0.029 | 0.044 | 0.036 | yes | no |
| 4h | 3R | RECENT | 4 UNDERPOWERED | 0.224 | [n/a, n/a] | 50.0 | -0.158 | 0.278 | -0.150 | 0.289 |  |  |
| 4h | time | DEV | 19 UNDERPOWERED | -0.338 | [n/a, n/a] | 36.8 | -0.025 | 0.665 | -0.037 | 0.691 |  |  |
| 4h | time | VAL | 12 UNDERPOWERED | 0.776 | [n/a, n/a] | 83.3 | -0.049 | 0.094 | -0.052 | 0.080 | yes | no |
| 4h | time | RECENT | 4 UNDERPOWERED | 0.126 | [n/a, n/a] | 50.0 | -0.029 | 0.319 | -0.013 | 0.317 |  |  |
| 8h | 1R | DEV | 12 UNDERPOWERED | -0.028 | [n/a, n/a] | 50.0 | -0.152 | 0.324 | -0.035 | 0.471 |  |  |
| 8h | 1R | VAL | 0 UNDERPOWERED | n/a | [n/a, n/a] | n/a | n/a | n/a | n/a | n/a | no | no |
| 8h | 1R | RECENT | 6 UNDERPOWERED | -0.402 | [n/a, n/a] | 33.3 | -0.178 | 0.680 | -0.195 | 0.698 |  |  |
| 8h | 2R | DEV | 12 UNDERPOWERED | -0.001 | [n/a, n/a] | 50.0 | -0.124 | 0.353 | -0.038 | 0.447 |  |  |
| 8h | 2R | VAL | 0 UNDERPOWERED | n/a | [n/a, n/a] | n/a | n/a | n/a | n/a | n/a | no | no |
| 8h | 2R | RECENT | 6 UNDERPOWERED | -0.069 | [n/a, n/a] | 33.3 | -0.042 | 0.463 | -0.072 | 0.491 |  |  |
| 8h | 3R | DEV | 12 UNDERPOWERED | 0.082 | [n/a, n/a] | 50.0 | -0.101 | 0.327 | -0.013 | 0.385 |  |  |
| 8h | 3R | VAL | 0 UNDERPOWERED | n/a | [n/a, n/a] | n/a | n/a | n/a | n/a | n/a | no | no |
| 8h | 3R | RECENT | 6 UNDERPOWERED | 0.265 | [n/a, n/a] | 33.3 | -0.043 | 0.296 | 0.099 | 0.379 |  |  |
| 8h | time | DEV | 12 UNDERPOWERED | -0.028 | [n/a, n/a] | 50.0 | -0.026 | 0.411 | -0.003 | 0.419 |  |  |
| 8h | time | VAL | 0 UNDERPOWERED | n/a | [n/a, n/a] | n/a | n/a | n/a | n/a | n/a | no | no |
| 8h | time | RECENT | 6 UNDERPOWERED | -0.084 | [n/a, n/a] | 33.3 | 0.039 | 0.465 | 0.035 | 0.542 |  |  |
| 12h | 1R | DEV | 3 UNDERPOWERED | -0.295 | [n/a, n/a] | 66.7 | -0.139 | 0.494 | -0.132 | 0.520 |  |  |
| 12h | 1R | VAL | 1 UNDERPOWERED | 0.992 | [n/a, n/a] | 100.0 | -0.056 | 0.017 | 0.355 | 0.069 | no | no |
| 12h | 1R | RECENT | 3 UNDERPOWERED | 0.029 | [n/a, n/a] | 66.7 | -0.135 | 0.440 | -0.057 | 0.433 |  |  |
| 12h | 2R | DEV | 3 UNDERPOWERED | -0.295 | [n/a, n/a] | 66.7 | -0.058 | 0.641 | -0.108 | 0.611 |  |  |
| 12h | 2R | VAL | 1 UNDERPOWERED | 0.476 | [n/a, n/a] | 100.0 | -0.052 | 0.324 | 0.382 | 0.445 | no | no |
| 12h | 2R | RECENT | 3 UNDERPOWERED | 0.175 | [n/a, n/a] | 66.7 | -0.089 | 0.306 | 0.088 | 0.419 |  |  |
| 12h | 3R | DEV | 3 UNDERPOWERED | -0.295 | [n/a, n/a] | 66.7 | -0.027 | 0.573 | -0.056 | 0.540 |  |  |
| 12h | 3R | VAL | 1 UNDERPOWERED | 0.476 | [n/a, n/a] | 100.0 | -0.179 | 0.233 | 0.390 | 0.462 | no | no |
| 12h | 3R | RECENT | 3 UNDERPOWERED | 0.175 | [n/a, n/a] | 66.7 | -0.060 | 0.482 | 0.112 | 0.472 |  |  |
| 12h | time | DEV | 3 UNDERPOWERED | -0.295 | [n/a, n/a] | 66.7 | 0.216 | 0.476 | -0.056 | 0.476 |  |  |
| 12h | time | VAL | 1 UNDERPOWERED | 0.476 | [n/a, n/a] | 100.0 | -0.123 | 0.195 | 0.098 | 0.391 | no | no |
| 12h | time | RECENT | 3 UNDERPOWERED | 0.175 | [n/a, n/a] | 66.7 | 0.120 | 0.292 | 0.078 | 0.359 |  |  |

## BTC alone (descriptive, all periods)
| TF | exit | n | mean net R |
|---|---|---|---|
| 4h | 1R | 8 | 0.398 |
| 4h | 2R | 8 | 0.244 |
| 4h | 3R | 8 | 0.320 |
| 4h | time | 8 | -0.229 |
| 8h | 1R | 3 | -1.128 |
| 8h | 2R | 3 | -1.128 |
| 8h | 3R | 3 | -1.128 |
| 8h | time | 3 | -1.128 |
| 12h | 1R | 2 | -1.067 |
| 12h | 2R | 2 | -1.067 |
| 12h | 3R | 2 | -1.067 |
| 12h | time | 2 | -1.067 |

## Signals per coin (RSI<=12, daily<30, next closes higher; before the one-position rule and the 12-bar-walk validity filter)
| coin | 4h | 8h | 12h |
|---|---|---|---|
| BTC | 9 | 3 | 2 |
| ETH | 4 | 4 | 0 |
| SOL | 0 | 1 | 0 |
| XRP | 2 | 1 | 1 |
| DOGE | 1 | 0 | 0 |
| BNB | 2 | 1 | 0 |
| ADA | 3 | 2 | 1 |
| LINK | 1 | 0 | 0 |
| LTC | 2 | 1 | 1 |
| AVAX | 1 | 0 | 0 |
| DOT | 0 | 0 | 1 |
| ATOM | 3 | 1 | 0 |
| TRX | 1 | 0 | 0 |
| BCH | 1 | 0 | 0 |
| ETC | 3 | 1 | 1 |
| UNI | 1 | 1 | 0 |
| NEAR | 0 | 0 | 0 |
| FIL | 5 | 1 | 0 |
| XLM | 0 | 1 | 0 |
| AAVE | 0 | 0 | 0 |

Limitations: no funding charge; 8h built from 4h pairs; stops and targets assumed taker with 2 bp slippage in total (real stop slippage in a selloff is larger); long only; Bybit data begins 2020-03 (BTC) to 2022 (newer coins).

## Reading
- The rule is rare: 35 signals on 4h, 18 on 8h, 7 on 12h in total over 20 coins (one position per coin). VALIDATION (2024-07..2025-06) has 12 / 0 / 1 trades, so no cell reaches n >= 30 and the plan pass rule cannot be met: **UNDERPOWERED, not "no edge"**.
- Descriptive only: the 4h VALIDATION cells are strongly positive (12 trades, 83% win, +0.39 / +0.64 / +0.81 R at 1R / 2R / 3R, beats P1 placebo at p ~ 0.03) but DEV (19 trades) is flat to negative (+0.12 / +0.05 / -0.13 / -0.34 R) and RECENT (4 trades) mixed. Pooled all-period 4h 2R: 35 trades, +0.245 R, CI [-0.30, +0.67] straddles zero. The VALIDATION edge also does not clearly beat the P2 (daily < 30 only) placebo (p 0.04-0.10), so it cannot be credited to the 4h RSI <= 12 itself.
- 8h and 12h: nothing readable (n 18 and 7 in total; 8h has no VALIDATION trades).
- Next, if wanted: a wider census (RSI <= 15/20 or all 20+ more coins) to get n >= 30 per split would need a new pre-registration; it is not part of this card.
