# RESULT: deep RSI extreme + confirming candle, event table and grid (edge3-rsi-deep-extreme-grid-1113)

**Verdict: FAIL / UNDERPOWERED.** 0 of 60 pre-registered pooled cells PASS (verdicts: {'UNDERPOWERED': 48, 'FAIL': 12}). BH 10% significant on VALIDATION: 14 (of which 0 have VALIDATION n >= 30; the rest are UNDERPOWERED). No edge claim.
Regime mix: BTC daily close vs 200d SMA (bull > +5%, bear < -5%): DEV bull 57% / bear 34% / range 9%; VALIDATION bull 62% / bear 11% / range 27%; RECENT bull 36% / bear 54% / range 10%.
Universe: BTC ETH SOL BNB XRP DOGE ADA LINK AVAX LTC, Bybit linear 1h/1D from listing; fees 2 x BINANCE_TAKER (fees.py), no slippage, no funding; entry = close of the confirming bar, stop = signal-bar low; net R per trade; week-block bootstrap (2000), placebo 100 draws. Trades need 168 h of forward data, so the last 7 days are excluded from tested trades.

## Today's trade, the operator's example (checked first)
BTC 1h bar opened 2026-11-13 05:00Z: red, close 68106.7, RSI(14) 9.17, low 67468.4, daily RSI (last closed) 29.6. Next 1h bar (06:00Z) green, close 69034.8 at 07:00Z = entry (confirm yes). Stop = 67468.4, 2.27 % away. All match his numbers.
State at run time (last closed 1h bar opened 16:00 Z, 10 bars after entry): **NOT stopped**; best high since entry 70187.0 = **+0.74R**; worst low since entry 68073.3; last close 68666.3 = -0.24R. (Not in any statistics: its 168 h window is not complete.)

## A. Event counts (first touch, re-arm above 30), episodes / confirm-yes, all coins
| coin | 1h<=10 | 1h<=12 | 1h<=15 | 1h<=20 | 4h<=10 | 4h<=12 | 4h<=15 | 4h<=20 | 8h<=10 | 8h<=12 | 8h<=15 | 8h<=20 | 12h<=10 | 12h<=12 | 12h<=15 | 12h<=20 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| BTC | 5/4 | 8/5 | 27/20 | 113/78 | 3/2 | 6/4 | 10/5 | 25/11 | 1/0 | 2/1 | 6/5 | 12/4 | 0/0 | 2/1 | 4/3 | 10/4 |
| ETH | 6/3 | 10/6 | 32/19 | 94/54 | 2/1 | 5/4 | 11/6 | 30/14 | 1/1 | 3/2 | 5/3 | 13/7 | 0/0 | 0/0 | 4/4 | 10/8 |
| SOL | 1/1 | 6/3 | 16/9 | 75/47 | 0/0 | 0/0 | 6/3 | 20/9 | 0/0 | 1/1 | 2/0 | 14/10 | 0/0 | 0/0 | 3/2 | 7/5 |
| BNB | 5/4 | 10/6 | 24/16 | 86/56 | 2/2 | 4/4 | 8/6 | 22/9 | 1/1 | 1/1 | 4/3 | 11/6 | 0/0 | 0/0 | 4/3 | 8/7 |
| XRP | 5/4 | 7/4 | 19/14 | 82/62 | 1/1 | 2/1 | 10/6 | 28/22 | 0/0 | 1/0 | 3/2 | 13/8 | 0/0 | 1/1 | 2/2 | 9/7 |
| DOGE | 4/3 | 8/5 | 29/21 | 102/72 | 0/0 | 2/2 | 6/6 | 27/15 | 0/0 | 0/0 | 3/3 | 13/7 | 0/0 | 0/0 | 1/0 | 9/7 |
| ADA | 3/3 | 6/4 | 16/6 | 70/39 | 1/1 | 3/2 | 7/5 | 18/11 | 1/1 | 2/1 | 3/2 | 9/6 | 0/0 | 1/0 | 2/1 | 7/5 |
| LINK | 5/4 | 8/4 | 17/10 | 76/44 | 0/0 | 1/1 | 5/3 | 22/14 | 0/0 | 0/0 | 2/1 | 10/5 | 0/0 | 0/0 | 2/2 | 3/2 |
| AVAX | 4/3 | 7/5 | 19/13 | 71/43 | 0/0 | 1/1 | 5/5 | 28/18 | 0/0 | 0/0 | 2/1 | 11/8 | 0/0 | 0/0 | 2/2 | 5/4 |
| LTC | 5/4 | 8/3 | 19/10 | 83/50 | 0/0 | 2/2 | 6/6 | 19/7 | 0/0 | 1/1 | 3/3 | 8/6 | 0/0 | 1/1 | 1/1 | 7/6 |
| ALL | 43/33 | 78/45 | 218/138 | 852/545 | 9/7 | 26/21 | 74/51 | 239/130 | 4/3 | 11/7 | 33/23 | 114/67 | 0/0 | 5/3 | 25/20 | 75/55 |

BTC row by row: events_btc.csv (all 234 BTC episodes, TF x T). The T<=15 rows follow; fields: stop % = (entry - signal low)/entry; mfe/mae = max favourable/adverse move from entry over 24 h; +1R/+2R = target before stop within 72 h; brk_h = hours until the signal low broke (blank = not within 7 d); ret = forward return from entry; (blank forward fields = window incomplete, i.e. today).

### BTC episodes, T <= 12 (all TF)
| tf | T | day | rsi | dRSI | cf | stop% | mfe24% | mae24% | +1R | +2R | +3R | brk_h | r24% | r72% | r7d% | rsi@pk |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 10 | 2020-06-11 16 | 9.3 | 58.0 | yes | 2.8 | 1.9 | -1.5 | neither | neither | neither | 84.0 | -0.4 | 0.1 | 0.3 | 44.9 |
| 1 | 10 | 2021-12-04 05 | 8.5 | 38.3 | no | 13.9 |  |  |  |  |  |  |  |  |  |  |
| 1 | 10 | 2023-03-09 20 | 9.1 | 37.7 | yes | 1.0 | 1.4 | -3.4 | target | stop | stop | 3.0 | -0.7 | 5.2 | 23.2 | 80.4 |
| 1 | 10 | 2023-08-17 21 | 5.9 | 37.7 | yes | 9.7 | 0.8 | -4.5 | neither | neither | neither |  | -2.7 | -2.2 | -2.5 | 22.7 |
| 1 | 10 | 2026-11-13 05 | 9.2 | 29.6 | yes | 2.3 |  |  |  |  |  |  |  |  |  |  |
| 1 | 12 | 2020-06-11 16 | 9.3 | 58.0 | yes | 2.8 | 1.9 | -1.5 | neither | neither | neither | 84.0 | -0.4 | 0.1 | 0.3 | 44.9 |
| 1 | 12 | 2021-12-04 05 | 8.5 | 38.3 | no | 13.9 |  |  |  |  |  |  |  |  |  |  |
| 1 | 12 | 2022-06-13 14 | 11.1 | 33.1 | yes | 3.0 | 4.1 | -10.5 | target | stop | stop | 7.0 | -2.5 | -9.4 | -10.5 | 30.7 |
| 1 | 12 | 2022-08-19 11 | 11.1 | 49.0 | yes | 1.3 | 0.6 | -3.6 | stop | stop | stop | 7.0 | -1.4 | -1.5 | 0.5 | 56.7 |
| 1 | 12 | 2023-03-09 20 | 9.1 | 37.7 | yes | 1.0 | 1.4 | -3.4 | target | stop | stop | 3.0 | -0.7 | 5.2 | 23.2 | 80.4 |
| 1 | 12 | 2023-08-17 21 | 5.9 | 37.7 | yes | 9.7 | 0.8 | -4.5 | neither | neither | neither |  | -2.7 | -2.2 | -2.5 | 22.7 |
| 1 | 12 | 2026-01-31 18 | 11.4 | 33.6 | no | 2.6 |  |  |  |  |  |  |  |  |  |  |
| 1 | 12 | 2026-11-13 03 | 11.2 | 29.6 | no | 0.1 |  |  |  |  |  |  |  |  |  |  |
| 4 | 10 | 2022-11-09 20 | 9.8 | 24.4 | yes | 5.5 | 11.2 | -1.0 | target | target | neither |  | 4.2 | 3.3 | 1.0 | 41.0 |
| 4 | 10 | 2023-03-10 08 | 9.7 | 29.4 | yes | 2.3 | 3.4 | -1.2 | target | target | target |  | 0.3 | 20.0 | 32.1 | 77.6 |
| 4 | 10 | 2023-08-17 20 | 5.7 | 21.0 | no | 8.3 |  |  |  |  |  |  |  |  |  |  |
| 4 | 12 | 2022-05-09 20 | 11.4 | 24.6 | yes | 2.1 | 6.6 | -1.7 | target | target | target | 33.0 | 1.8 | -0.3 | -1.0 | 30.4 |
| 4 | 12 | 2022-11-09 20 | 9.8 | 24.4 | yes | 5.5 | 11.2 | -1.0 | target | target | neither |  | 4.2 | 3.3 | 1.0 | 41.0 |
| 4 | 12 | 2023-03-10 00 | 11.0 | 29.4 | no | 0.9 |  |  |  |  |  |  |  |  |  |  |
| 4 | 12 | 2023-08-17 12 | 11.3 | 37.7 | no | 0.1 |  |  |  |  |  |  |  |  |  |  |
| 4 | 12 | 2026-02-05 20 | 11.8 | 15.8 | yes | 2.9 | 11.8 | -0.3 | target | target | target |  | 10.5 | 11.1 | 3.7 | 48.1 |
| 4 | 12 | 2026-06-03 00 | 10.9 | 21.8 | yes | 2.7 | 0.4 | -8.7 | stop | stop | stop | 12.0 | -5.4 | -9.2 | -8.2 | 25.3 |
| 8 | 10 | 2023-08-18 00 | 9.5 | 21.0 | no | -0.5 |  |  |  |  |  |  |  |  |  |  |
| 8 | 12 | 2023-08-17 16 | 10.1 | 21.0 | no | 8.4 |  |  |  |  |  |  |  |  |  |  |
| 8 | 12 | 2026-06-05 08 | 11.1 | 18.4 | yes | 1.7 | 0.8 | -2.6 | stop | stop | stop | 5.0 | -0.3 | 3.3 | 4.1 | 36.3 |
| 12 | 12 | 2023-08-18 00 | 12.0 | 21.0 | no | -0.3 |  |  |  |  |  |  |  |  |  |  |
| 12 | 12 | 2026-06-04 00 | 11.3 | 18.7 | yes | 3.9 | 0.2 | -7.5 | stop | stop | stop | 7.0 | -4.4 | -0.9 | -0.4 | 30.9 |

### BTC episodes, T = 15 (all TF)
| tf | T | day | rsi | dRSI | cf | stop% | mfe24% | mae24% | +1R | +2R | +3R | brk_h | r24% | r72% | r7d% | rsi@pk |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 15 | 2020-03-28 03 | 14.9 |  | yes | 1.3 | 2.2 | -2.5 | target | stop | stop | 13.0 | 0.5 | 3.6 | 8.9 | 67.7 |
| 1 | 15 | 2020-05-10 00 | 13.5 | 71.0 | yes | 6.4 | 2.1 | -5.2 | neither | neither | neither |  | 0.0 | 2.6 | 8.7 | 54.2 |
| 1 | 15 | 2020-06-11 16 | 9.3 | 58.0 | yes | 2.8 | 1.9 | -1.5 | neither | neither | neither | 84.0 | -0.4 | 0.1 | 0.3 | 44.9 |
| 1 | 15 | 2021-04-18 03 | 13.2 | 54.3 | yes | 7.9 | 4.3 | -3.2 | neither | neither | neither | 117.0 | 3.8 | 1.1 | -9.4 | 50.1 |
| 1 | 15 | 2021-09-07 14 | 14.1 | 68.5 | no | -0.4 |  |  |  |  |  |  |  |  |  |  |
| 1 | 15 | 2021-11-26 11 | 13.1 | 46.8 | yes | 1.2 | 1.8 | -1.4 | stop | stop | stop | 11.0 | 0.7 | 4.8 | 4.6 | 77.1 |
| 1 | 15 | 2021-12-04 04 | 12.7 | 38.3 | no | -2.6 |  |  |  |  |  |  |  |  |  |  |
| 1 | 15 | 2022-03-04 22 | 14.1 | 54.8 | yes | 1.6 | 1.2 | -1.4 | target | stop | stop | 35.0 | 0.6 | -2.9 | -1.0 | 53.7 |
| 1 | 15 | 2022-05-05 19 | 15.0 | 48.6 | yes | 2.6 | 0.6 | -3.4 | stop | stop | stop | 17.0 | -1.1 | -6.1 | -21.5 | 24.7 |
| 1 | 15 | 2022-06-13 11 | 14.8 | 33.1 | no | 0.9 |  |  |  |  |  |  |  |  |  |  |
| 1 | 15 | 2022-06-14 01 | 14.6 | 24.2 | yes | 3.3 | 9.0 | -1.1 | target | target | stop | 27.0 | 2.1 | -4.4 | -5.1 | 43.2 |
| 1 | 15 | 2022-08-19 06 | 14.5 | 49.0 | no | 3.6 |  |  |  |  |  |  |  |  |  |  |
| 1 | 15 | 2022-09-19 05 | 14.6 | 41.4 | yes | 0.9 | 6.6 | -0.5 | target | target | target | 63.0 | 4.9 | 1.6 | 1.3 | 63.6 |
| 1 | 15 | 2022-10-13 12 | 14.8 | 44.4 | yes | 1.9 | 8.3 | -0.2 | target | target | target |  | 6.7 | 3.8 | 4.1 | 74.2 |
| 1 | 15 | 2023-03-09 20 | 9.1 | 37.7 | yes | 1.0 | 1.4 | -3.4 | target | stop | stop | 3.0 | -0.7 | 5.2 | 23.2 | 80.4 |
| 1 | 15 | 2023-06-05 18 | 13.2 | 47.9 | yes | 0.4 | 6.2 | -1.2 | stop | stop | stop | 2.0 | 5.6 | 3.5 | 0.7 | 73.9 |
| 1 | 15 | 2023-06-10 05 | 13.8 | 45.3 | yes | 0.3 | 2.4 | -0.8 | target | target | stop | 11.0 | 1.0 | 2.1 | 4.4 | 66.2 |
| 1 | 15 | 2023-08-17 15 | 13.9 | 37.7 | yes | 0.3 | 0.4 | -13.4 | target | stop | stop | 2.0 | -7.4 | -6.8 | -6.6 | 18.0 |
| 1 | 15 | 2023-12-11 02 | 14.9 | 74.0 | yes | 5.2 | 0.4 | -5.0 | neither | neither | neither |  | -1.4 | 0.9 | -2.9 | 74.2 |
| 1 | 15 | 2024-08-05 06 | 14.4 | 33.2 | yes | 7.1 | 6.9 | -5.9 | target | neither | neither |  | 6.3 | 8.6 | 11.4 | 62.2 |
| 1 | 15 | 2025-01-27 01 | 13.7 | 54.9 | no | -0.1 |  |  |  |  |  |  |  |  |  |  |
| 1 | 15 | 2025-10-10 21 | 13.4 | 60.1 | yes | 11.0 | 1.1 | -3.6 | neither | neither | neither |  | -2.2 | 1.7 | -5.8 | 66.6 |
| 1 | 15 | 2025-12-01 04 | 14.6 | 39.4 | yes | 0.4 | 1.6 | -2.6 | target | target | stop | 7.0 | 1.2 | 8.1 | 6.2 | 66.1 |
| 1 | 15 | 2026-01-31 17 | 13.2 | 33.6 | no | -0.1 |  |  |  |  |  |  |  |  |  |  |
| 1 | 15 | 2026-02-23 01 | 14.5 | 36.6 | yes | 0.8 | 2.8 | -2.1 | target | target | target | 15.0 | -1.0 | 5.4 | 2.3 | 76.1 |
| 1 | 15 | 2026-06-02 15 | 13.4 | 30.4 | yes | 0.5 | 0.8 | -2.9 | target | stop | stop | 3.0 | -2.0 | -8.9 | -8.9 | 22.5 |
| 1 | 15 | 2026-11-13 03 | 11.2 | 29.6 | no | 0.1 |  |  |  |  |  |  |  |  |  |  |
| 4 | 15 | 2022-05-09 16 | 13.2 | 31.9 | no | -0.8 |  |  |  |  |  |  |  |  |  |  |
| 4 | 15 | 2022-06-13 12 | 14.7 | 33.1 | no | 2.7 |  |  |  |  |  |  |  |  |  |  |
| 4 | 15 | 2022-08-19 20 | 13.9 | 32.9 | yes | 1.8 | 1.1 | -1.9 | stop | stop | stop | 18.0 | 0.3 | 0.5 | -4.4 | 39.1 |
| 4 | 15 | 2022-11-08 16 | 13.3 | 54.9 | yes | 9.4 | 0.2 | -16.6 | stop | stop | stop | 18.0 | -14.3 | -8.0 | -8.9 | 19.4 |
| 4 | 15 | 2023-03-09 20 | 12.7 | 29.4 | no | 0.1 |  |  |  |  |  |  |  |  |  |  |
| 4 | 15 | 2023-08-17 12 | 11.3 | 37.7 | no | 0.1 |  |  |  |  |  |  |  |  |  |  |
| 4 | 15 | 2024-06-24 16 | 13.1 | 33.2 | yes | 2.1 | 3.6 | -0.1 | target | neither | neither |  | 2.5 | 2.3 | 4.3 | 44.4 |
| 4 | 15 | 2024-08-05 08 | 14.6 | 33.2 | yes | 6.8 | 4.3 | -3.2 | target | neither | neither |  | 3.9 | 9.4 | 10.9 | 58.7 |
| 4 | 15 | 2026-02-05 16 | 13.9 | 22.9 | no | -3.6 |  |  |  |  |  |  |  |  |  |  |
| 4 | 15 | 2026-06-02 12 | 13.3 | 30.4 | yes | 0.4 | 0.9 | -3.1 | stop | stop | stop | 1.0 | -2.8 | -10.4 | -7.8 | 12.5 |
| 8 | 15 | 2022-05-09 16 | 13.1 | 24.6 | yes | 5.0 | 2.5 | -4.7 | stop | stop | stop | 29.0 | -3.1 | -4.6 | -3.9 | 26.3 |
| 8 | 15 | 2022-11-09 16 | 12.4 | 24.4 | yes | 7.6 | 8.7 | -3.0 | target | neither | neither |  | 3.9 | 0.1 | -0.9 | 35.0 |
| 8 | 15 | 2023-03-10 00 | 15.0 | 29.4 | yes | 1.2 | 3.4 | -1.2 | target | target | target |  | 0.3 | 20.0 | 32.1 | 71.8 |
| 8 | 15 | 2023-08-17 16 | 10.1 | 21.0 | no | 8.4 |  |  |  |  |  |  |  |  |  |  |
| 8 | 15 | 2026-02-05 16 | 12.1 | 15.8 | yes | 4.0 | 10.7 | -0.6 | target | target | neither |  | 5.0 | 8.6 | 2.1 | 41.2 |
| 8 | 15 | 2026-06-02 16 | 14.8 | 21.8 | yes | 1.5 | 0.4 | -8.7 | stop | stop | stop | 8.0 | -5.4 | -9.2 | -8.2 | 16.8 |
| 12 | 15 | 2023-03-10 00 | 15.0 | 29.4 | yes | 3.0 | 2.6 | -1.9 | target | target | target |  | 1.5 | 19.7 | 35.9 | 67.8 |
| 12 | 15 | 2023-08-17 12 | 12.5 | 21.0 | no | 8.6 |  |  |  |  |  |  |  |  |  |  |
| 12 | 15 | 2026-02-05 12 | 12.9 | 15.8 | yes | 6.5 | 7.7 | -0.8 | target | neither | neither |  | 2.0 | 3.5 | 0.8 | 37.8 |
| 12 | 15 | 2026-06-02 12 | 14.1 | 21.8 | yes | 1.3 | 0.3 | -8.5 | stop | stop | stop | 4.0 | -6.8 | -9.4 | -9.0 | 12.9 |

## Stop distance % (confirm-yes events), 10-coin pooled and BTC
| scope | tf | T | n | p25 | median | p75 | worst |
|---|---|---|---|---|---|---|---|
| 10-coin | 1 | 10 | 33 | 2.27 | 9.66 | 14.15 | 60.30 |
| 10-coin | 1 | 12 | 45 | 1.67 | 3.90 | 10.56 | 60.30 |
| 10-coin | 1 | 15 | 138 | 1.15 | 2.28 | 6.38 | 55.31 |
| 10-coin | 1 | 20 | 545 | 1.00 | 1.67 | 3.06 | 51.59 |
| 10-coin | 4 | 10 | 7 | 2.22 | 4.67 | 8.45 | 13.86 |
| 10-coin | 4 | 12 | 21 | 2.94 | 3.78 | 6.01 | 62.49 |
| 10-coin | 4 | 15 | 51 | 2.32 | 3.95 | 9.65 | 62.49 |
| 10-coin | 4 | 20 | 130 | 2.17 | 3.98 | 7.78 | 62.49 |
| 10-coin | 8 | 10 | 3 | 9.77 | 13.26 | 14.31 | 15.35 |
| 10-coin | 8 | 12 | 7 | 2.14 | 6.27 | 14.31 | 16.57 |
| 10-coin | 8 | 15 | 23 | 4.49 | 8.58 | 12.93 | 19.12 |
| 10-coin | 8 | 20 | 67 | 4.30 | 9.89 | 15.32 | 62.96 |
| 10-coin | 12 | 12 | 3 | 10.21 | 16.48 | 16.66 | 16.85 |
| 10-coin | 12 | 15 | 20 | 4.58 | 6.42 | 14.49 | 23.88 |
| 10-coin | 12 | 20 | 55 | 4.53 | 7.45 | 12.45 | 46.45 |
| BTC | 1 | 10 | 4 | 1.95 | 2.53 | 4.50 | 9.66 |
| BTC | 1 | 12 | 5 | 1.25 | 2.78 | 2.98 | 9.66 |
| BTC | 1 | 15 | 20 | 0.74 | 1.44 | 3.74 | 10.98 |
| BTC | 1 | 20 | 78 | 0.57 | 1.12 | 2.02 | 10.25 |
| BTC | 4 | 10 | 2 | 3.09 | 3.88 | 4.67 | 5.46 |
| BTC | 4 | 12 | 4 | 2.51 | 2.80 | 3.57 | 5.46 |
| BTC | 4 | 15 | 5 | 1.76 | 2.08 | 6.81 | 9.37 |
| BTC | 4 | 20 | 11 | 1.88 | 2.86 | 4.06 | 9.37 |
| BTC | 8 | 12 | 1 | 1.66 | 1.66 | 1.66 | 1.66 |
| BTC | 8 | 15 | 5 | 1.53 | 3.96 | 5.03 | 7.64 |
| BTC | 8 | 20 | 4 | 2.84 | 4.40 | 6.86 | 9.89 |
| BTC | 12 | 12 | 1 | 3.94 | 3.94 | 3.94 | 3.94 |
| BTC | 12 | 15 | 3 | 2.17 | 3.01 | 4.76 | 6.52 |
| BTC | 12 | 20 | 4 | 5.24 | 5.46 | 6.56 | 9.40 |

## B. Pooled cells (60). VALIDATION decides; DEV and RECENT shown
Cells with VALIDATION n >= 30: 12 of 60. Best 5 and worst 5 of those by VALIDATION mean net R:
| tf | T | exit | DEV_n | DEV_mean | VAL_n | VAL_mean | VAL_lo | VAL_hi | VAL_win | VAL_plac_mean | VAL_plac_p | REC_n | REC_mean | bh_sig | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 4 | 20 | tgt3 | 68 | -0.294 | 32 | 0.585 | -0.482 | 1.638 | 0.594 | -0.158 | 0.010 | 29 | 0.732 | False | FAIL |
| 4 | 20 | rsi50 | 68 | -0.317 | 32 | 0.515 | -0.531 | 1.586 | 0.562 | 0.379 | 0.188 | 29 | 1.009 | False | FAIL |
| 4 | 20 | time24 | 68 | -0.131 | 32 | 0.457 | -0.223 | 1.155 | 0.750 | -0.099 | 0.010 | 29 | 0.487 | False | FAIL |
| 4 | 20 | tgt2 | 68 | -0.237 | 32 | 0.412 | -0.441 | 1.254 | 0.625 | -0.179 | 0.010 | 29 | 0.444 | False | FAIL |
| 4 | 20 | time72 | 68 | -0.316 | 32 | 0.408 | -0.549 | 1.307 | 0.594 | -0.259 | 0.010 | 29 | 1.095 | False | FAIL |
| 1 | 20 | tgt2 | 330 | -0.208 | 92 | -0.145 | -0.476 | 0.242 | 0.337 | -0.273 | 0.139 | 117 | -0.028 | False | FAIL |
| 1 | 20 | rsi50 | 330 | -0.175 | 92 | -0.178 | -0.637 | 0.432 | 0.293 | -0.279 | 0.267 | 117 | 0.095 | False | FAIL |
| 1 | 20 | time24 | 330 | -0.165 | 92 | -0.183 | -0.678 | 0.472 | 0.272 | -0.301 | 0.218 | 117 | -0.228 | False | FAIL |
| 1 | 20 | tgt3 | 330 | -0.188 | 92 | -0.217 | -0.636 | 0.296 | 0.272 | -0.262 | 0.307 | 117 | -0.021 | False | FAIL |
| 1 | 20 | tgt1 | 330 | -0.186 | 92 | -0.232 | -0.493 | 0.080 | 0.435 | -0.249 | 0.416 | 117 | -0.135 | False | FAIL |

Cells with VALIDATION n < 30 (UNDERPOWERED, shown for completeness, top 8 by mean):
| tf | T | exit | DEV_n | DEV_mean | VAL_n | VAL_mean | VAL_lo | VAL_hi | VAL_win | VAL_plac_mean | VAL_plac_p | REC_n | REC_mean | bh_sig | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 4 | 15 | rsi50 | 23 | -0.465 | 15 | 1.086 | 0.123 | 2.164 | 0.733 | 0.467 | 0.059 | 13 | 0.150 | True | UNDERPOWERED |
| 4 | 15 | tgt3 | 23 | -0.133 | 15 | 0.872 | 0.117 | 1.679 | 0.800 | -0.191 | 0.010 | 13 | 0.274 | True | UNDERPOWERED |
| 12 | 15 | rsi50 | 8 | 0.002 | 3 | 0.841 | 0.841 | 0.841 | 1.000 | 0.837 | 0.475 | 9 | -0.200 | True | UNDERPOWERED |
| 4 | 15 | tgt2 | 23 | -0.264 | 15 | 0.828 | 0.127 | 1.446 | 0.867 | -0.160 | 0.010 | 13 | 0.117 | True | UNDERPOWERED |
| 12 | 15 | time72 | 8 | 0.584 | 3 | 0.816 | 0.816 | 0.816 | 1.000 | 0.313 | 0.010 | 9 | 0.068 | True | UNDERPOWERED |
| 12 | 15 | tgt3 | 8 | 0.141 | 3 | 0.816 | 0.816 | 0.816 | 1.000 | 0.313 | 0.010 | 9 | 0.068 | True | UNDERPOWERED |
| 12 | 15 | tgt1 | 8 | 0.141 | 3 | 0.816 | 0.816 | 0.816 | 1.000 | 0.312 | 0.010 | 9 | 0.496 | True | UNDERPOWERED |
| 12 | 15 | tgt2 | 8 | 0.016 | 3 | 0.816 | 0.816 | 0.816 | 1.000 | 0.313 | 0.010 | 9 | 0.330 | True | UNDERPOWERED |

By exit, mean across the 10 combos (pooled, n-weighted not applied; descriptive): 
| exit | DEV_mean | VAL_mean | REC_mean |
|---|---|---|---|
| rsi50 | -0.005 | 0.425 | 0.116 |
| tgt1 | 0.003 | 0.208 | 0.161 |
| tgt2 | -0.037 | 0.292 | 0.112 |
| tgt3 | -0.048 | 0.317 | 0.167 |
| time24 | -0.134 | 0.217 | 0.109 |
| time72 | 0.323 | 0.325 | 0.244 |

BTC alone (descriptive, tiny n), cells with VALIDATION n >= 3:
| tf | T | exit | DEV_n | DEV_mean | VAL_n | VAL_mean | REC_n | REC_mean |
|---|---|---|---|---|---|---|---|---|
| 1 | 20 | tgt1 | 50 | -0.278 | 13 | -0.030 | 13 | -0.605 |
| 1 | 20 | tgt2 | 50 | -0.397 | 13 | 0.047 | 13 | -0.759 |
| 1 | 20 | tgt3 | 50 | -0.297 | 13 | 0.235 | 13 | -0.605 |
| 1 | 20 | rsi50 | 50 | -0.525 | 13 | 0.659 | 13 | -0.932 |
| 1 | 20 | time24 | 50 | -0.427 | 13 | 0.460 | 13 | -0.714 |
| 1 | 20 | time72 | 50 | -0.071 | 13 | 0.873 | 13 | -0.772 |
| 4 | 20 | tgt1 | 5 | -0.238 | 3 | 0.299 | 3 | -1.044 |
| 4 | 20 | tgt2 | 5 | -0.193 | 3 | 0.537 | 3 | -1.044 |
| 4 | 20 | tgt3 | 5 | -0.493 | 3 | 0.870 | 3 | -1.044 |
| 4 | 20 | rsi50 | 5 | -0.120 | 3 | 1.027 | 3 | -1.044 |
| 4 | 20 | time24 | 5 | -0.232 | 3 | 0.392 | 3 | -1.044 |
| 4 | 20 | time72 | 5 | -0.493 | 3 | 0.658 | 3 | -1.044 |
| 8 | 20 | tgt1 | 1 | -1.039 | 3 | -0.127 | 0 |  |
| 8 | 20 | tgt2 | 1 | -1.039 | 3 | -0.127 | 0 |  |
| 8 | 20 | tgt3 | 1 | -1.039 | 3 | -0.127 | 0 |  |
| 8 | 20 | rsi50 | 1 | -1.039 | 3 | 0.196 | 0 |  |
| 8 | 20 | time24 | 1 | -1.039 | 3 | -0.156 | 0 |  |
| 8 | 20 | time72 | 1 | -1.039 | 3 | -0.127 | 0 |  |

Full table: cells.csv. Daily-RSI band split (descriptive, no CI): cells_bands.csv. Pooled by daily-RSI band, exit +2R and time72, all combos with T=20 (mean net R / n):
| tf | exit | band | DEV | VAL | REC |
|---|---|---|---|---|---|
| 1 | tgt2 | <=20 | 0.93 / 3 |  / 0 | -1.06 / 1 |
| 1 | tgt2 | 20-25 | -0.45 / 5 |  / 0 | 0.14 / 5 |
| 1 | tgt2 | 25-30 | -0.14 / 13 | 1.35 / 3 | 0.93 / 3 |
| 1 | tgt2 | 30-40 | -0.15 / 110 | 0.04 / 37 | 0.33 / 42 |
| 1 | tgt2 | >40 | -0.25 / 197 | -0.37 / 52 | -0.29 / 66 |
| 1 | time72 | <=20 | -1.07 / 3 |  / 0 | -1.06 / 1 |
| 1 | time72 | 20-25 | -0.12 / 5 |  / 0 | 1.68 / 5 |
| 1 | time72 | 25-30 | -0.60 / 13 | 2.01 / 3 | 1.03 / 3 |
| 1 | time72 | 30-40 | 0.08 / 110 | 0.77 / 37 | -0.29 / 42 |
| 1 | time72 | >40 | -0.29 / 197 | -0.44 / 52 | -0.51 / 66 |
| 4 | tgt2 | <=20 |  / 0 |  / 0 | 1.48 / 3 |
| 4 | tgt2 | 20-25 | -0.56 / 4 |  / 0 | -1.03 / 1 |
| 4 | tgt2 | 25-30 | -0.32 / 8 | -1.05 / 4 | -0.33 / 5 |
| 4 | tgt2 | 30-40 | -0.18 / 33 | 0.61 / 23 | 0.31 / 11 |
| 4 | tgt2 | >40 | -0.24 / 23 | 0.65 / 5 | 0.85 / 9 |
| 4 | time72 | <=20 |  / 0 |  / 0 | 2.58 / 3 |
| 4 | time72 | 20-25 | -0.56 / 4 |  / 0 | -1.03 / 1 |
| 4 | time72 | 25-30 | -0.51 / 8 | -1.05 / 4 | -0.33 / 5 |
| 4 | time72 | 30-40 | -0.23 / 33 | 0.72 / 23 | 1.54 / 11 |
| 4 | time72 | >40 | -0.34 / 23 | 0.14 / 5 | 1.08 / 9 |
| 8 | tgt2 | <=20 |  / 0 |  / 0 |  / 0 |
| 8 | tgt2 | 20-25 | -0.48 / 8 |  / 0 | -0.05 / 3 |
| 8 | tgt2 | 25-30 | -0.17 / 17 | 0.04 / 8 | -0.34 / 3 |
| 8 | tgt2 | 30-40 | -0.08 / 13 | 0.28 / 10 | -0.22 / 3 |
| 8 | tgt2 | >40 | -1.14 / 1 |  / 0 | 1.28 / 1 |
| 8 | time72 | <=20 |  / 0 |  / 0 |  / 0 |
| 8 | time72 | 20-25 | -0.48 / 8 |  / 0 | 0.49 / 3 |
| 8 | time72 | 25-30 | -0.17 / 17 | 0.04 / 8 | -0.34 / 3 |
| 8 | time72 | 30-40 | 0.24 / 13 | 0.28 / 10 | -0.22 / 3 |
| 8 | time72 | >40 | -1.14 / 1 |  / 0 | 1.28 / 1 |
| 12 | tgt2 | <=20 | -1.01 / 2 |  / 0 | 0.37 / 3 |
| 12 | tgt2 | 20-25 | -0.03 / 12 | -1.02 / 1 | -0.37 / 3 |
| 12 | tgt2 | 25-30 | -0.39 / 14 | 0.41 / 7 | -1.03 / 2 |
| 12 | tgt2 | 30-40 | 0.65 / 3 | 1.12 / 6 | 1.95 / 1 |
| 12 | tgt2 | >40 |  / 0 |  / 0 |  / 0 |
| 12 | time72 | <=20 | -1.01 / 2 |  / 0 | 0.04 / 3 |
| 12 | time72 | 20-25 | -0.01 / 12 | -1.02 / 1 | -0.37 / 3 |
| 12 | time72 | 25-30 | -0.39 / 14 | 0.41 / 7 | -1.03 / 2 |
| 12 | time72 | 30-40 | 1.40 / 3 | 1.12 / 6 | 2.33 / 1 |
| 12 | time72 | >40 |  / 0 |  / 0 |  / 0 |

## C. Layers on pooled confirm-yes events, T=20 (n per cell; THIN = n < 30). win1R = share reaching +1R before the stop within 72 h; mean R = net R of the +2R-target exit
| tf | layer | level | n | THIN | win1R | mean_R_tgt2 |
|---|---|---|---|---|---|---|
| 1 | daily trend | above 200d SMA | 152 |  | 0.428 | -0.130 |
| 1 | daily trend | below 200d SMA | 336 |  | 0.411 | -0.159 |
| 1 | daily ADX>=25 & -DI>+DI | yes | 191 |  | 0.450 | -0.090 |
| 1 | daily ADX>=25 & -DI>+DI | no | 342 |  | 0.392 | -0.197 |
| 1 | OI over last 4 bars | fell | 358 |  | 0.416 | -0.119 |
| 1 | OI over last 4 bars | rose/flat | 178 |  | 0.410 | -0.234 |
| 1 | signal volume >=2x 20-bar mean | yes | 435 |  | 0.391 | -0.147 |
| 1 | signal volume >=2x 20-bar mean | no | 104 |  | 0.500 | -0.205 |
| 1 | session of signal bar | Asia 0-8 | 187 |  | 0.433 | -0.173 |
| 1 | session of signal bar | Europe 8-16 | 139 |  | 0.360 | -0.399 |
| 1 | session of signal bar | US 16-24 | 213 |  | 0.427 | 0.012 |
| 1 | weekend | Sat/Sun | 96 |  | 0.438 | -0.052 |
| 1 | weekend | Mon-Fri | 443 |  | 0.406 | -0.181 |
| 4 | daily trend | above 200d SMA | 36 |  | 0.500 | 0.205 |
| 4 | daily trend | below 200d SMA | 88 |  | 0.455 | 0.088 |
| 4 | daily ADX>=25 & -DI>+DI | yes | 64 |  | 0.469 | -0.065 |
| 4 | daily ADX>=25 & -DI>+DI | no | 65 |  | 0.446 | 0.217 |
| 4 | OI over last 4 bars | fell | 92 |  | 0.500 | 0.129 |
| 4 | OI over last 4 bars | rose/flat | 37 |  | 0.351 | -0.051 |
| 4 | signal volume >=2x 20-bar mean | yes | 105 |  | 0.448 | 0.100 |
| 4 | signal volume >=2x 20-bar mean | no | 24 | THIN | 0.500 | -0.021 |
| 4 | session of signal bar | Asia 0-8 | 42 |  | 0.429 | 0.091 |
| 4 | session of signal bar | Europe 8-16 | 33 |  | 0.455 | 0.133 |
| 4 | session of signal bar | US 16-24 | 54 |  | 0.481 | 0.033 |
| 4 | weekend | Sat/Sun | 27 | THIN | 0.370 | -0.083 |
| 4 | weekend | Mon-Fri | 102 |  | 0.480 | 0.120 |
| 8 | daily trend | above 200d SMA | 11 | THIN | 0.364 | -0.102 |
| 8 | daily trend | below 200d SMA | 51 |  | 0.235 | -0.134 |
| 8 | daily ADX>=25 & -DI>+DI | yes | 41 |  | 0.293 | -0.302 |
| 8 | daily ADX>=25 & -DI>+DI | no | 26 | THIN | 0.269 | 0.233 |
| 8 | OI over last 4 bars | fell | 51 |  | 0.196 | -0.101 |
| 8 | OI over last 4 bars | rose/flat | 16 | THIN | 0.562 | -0.074 |
| 8 | signal volume >=2x 20-bar mean | yes | 63 |  | 0.302 | -0.056 |
| 8 | signal volume >=2x 20-bar mean | no | 4 | THIN | 0.000 | -0.702 |
| 8 | session of signal bar | Asia 0-8 | 28 | THIN | 0.286 | 0.319 |
| 8 | session of signal bar | Europe 8-16 | 13 | THIN | 0.538 | -0.471 |
| 8 | session of signal bar | US 16-24 | 26 | THIN | 0.154 | -0.350 |
| 8 | weekend | Sat/Sun | 14 | THIN | 0.143 | -0.220 |
| 8 | weekend | Mon-Fri | 53 |  | 0.321 | -0.061 |
| 12 | daily trend | above 200d SMA | 6 | THIN | 0.333 | 0.386 |
| 12 | daily trend | below 200d SMA | 45 |  | 0.333 | 0.027 |
| 12 | daily ADX>=25 & -DI>+DI | yes | 32 |  | 0.312 | -0.121 |
| 12 | daily ADX>=25 & -DI>+DI | no | 20 | THIN | 0.400 | 0.426 |
| 12 | OI over last 4 bars | fell | 37 |  | 0.351 | 0.309 |
| 12 | OI over last 4 bars | rose/flat | 18 | THIN | 0.333 | -0.380 |
| 12 | signal volume >=2x 20-bar mean | yes | 51 |  | 0.314 | 0.053 |
| 12 | signal volume >=2x 20-bar mean | no | 3 | THIN | 0.667 | -0.023 |
| 12 | session of signal bar | Asia 0-8 | 31 |  | 0.355 | 0.400 |
| 12 | session of signal bar | Europe 8-16 | 24 | THIN | 0.333 | -0.325 |
| 12 | session of signal bar | US 16-24 | 0 | THIN |  |  |
| 12 | weekend | Sat/Sun | 9 | THIN | 0.444 | 0.228 |
| 12 | weekend | Mon-Fri | 46 |  | 0.326 | 0.055 |

Missing feature values (events with no value, summed over TF): OI over last 4 bars: 3, daily ADX>=25 & -DI>+DI: 9, daily trend: 65, session of signal bar: 0, signal volume >=2x 20-bar mean: 1, weekend: 0. OI history begins mid-2020 (BTC) and later for newer coins.

## D. Where to sell: confirm-yes events, T=20, by daily trend (max favourable move is raw, from the entry close, stop ignored)
| tf | trend | n | THIN | med_stop_pct | med_mfe24_pct | med_mfe24_R | med_mfe72_pct | med_mfe72_R | reach_1R | reach_2R | reach_3R | new_low_7d |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | above 200d SMA | 152 |  | 1.880 | 2.314 | 1.155 | 3.603 | 1.810 | 0.428 | 0.224 | 0.145 | 0.783 |
| 1 | below 200d SMA | 336 |  | 1.508 | 2.871 | 1.671 | 4.282 | 2.633 | 0.411 | 0.271 | 0.188 | 0.842 |
| 1 | all | 539 |  | 1.673 | 2.731 | 1.439 | 4.342 | 2.209 | 0.412 | 0.250 | 0.173 | 0.822 |
| 4 | above 200d SMA | 36 |  | 4.156 | 4.194 | 1.001 | 4.865 | 1.715 | 0.500 | 0.278 | 0.083 | 0.667 |
| 4 | below 200d SMA | 88 |  | 3.941 | 4.239 | 0.914 | 6.464 | 1.244 | 0.455 | 0.239 | 0.205 | 0.580 |
| 4 | all | 129 |  | 4.006 | 4.011 | 0.970 | 6.086 | 1.311 | 0.457 | 0.240 | 0.163 | 0.620 |
| 8 | above 200d SMA | 11 | THIN | 2.967 | 4.215 | 1.004 | 5.232 | 1.727 | 0.364 | 0.091 | 0.091 | 0.545 |
| 8 | below 200d SMA | 51 |  | 10.370 | 5.278 | 0.565 | 7.180 | 0.646 | 0.235 | 0.020 | 0.020 | 0.392 |
| 8 | all | 67 |  | 9.890 | 5.067 | 0.571 | 6.887 | 0.678 | 0.284 | 0.045 | 0.045 | 0.418 |
| 12 | above 200d SMA | 6 | THIN | 5.005 | 3.498 | 0.738 | 8.247 | 1.827 | 0.333 | 0.333 | 0.167 | 0.333 |
| 12 | below 200d SMA | 45 |  | 7.453 | 4.257 | 0.573 | 7.506 | 0.929 | 0.333 | 0.044 | 0.000 | 0.378 |
| 12 | all | 55 |  | 7.453 | 4.187 | 0.667 | 8.538 | 0.945 | 0.345 | 0.091 | 0.018 | 0.400 |

reach_kR = share where +kR was touched before the signal low within 72 h; new_low_7d = share where the signal low was broken within 7 days (the 'downtrend, sell it' case).

## Limits
No slippage or funding; R-multiples explode when the signal-bar range is tiny (fees / stop distance); 10 coins are highly correlated (week-block bootstrap partly handles that); daily-band and layer splits are small-n; T=20 is the superset of deeper first touches only approximately because first touch is defined per threshold; the live trade is excluded from statistics.
