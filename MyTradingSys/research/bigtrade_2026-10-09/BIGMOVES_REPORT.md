# BIGMOVES REPORT (big-move ground truth, backtest A)

Generated 2026-10-09 06:05 by report_bigmoves.py from bigmoves_stats.json. Code: MyTradingSys/backtest/bigtrade/bigmoves.py. Data store: F:\MTS\data\bigtrade.

## 1. Coverage actually found

Merged 1m BTCUSDT klines: 2022-01-01 00:00 .. 2026-10-07 23:59 UTC, 2507040 bars (= 1741 days x 1440), 0 gaps (0 missing minutes), 0 OHLC inconsistencies.

| source | bars | first | last | new | duplicates of earlier source | conflicting duplicates |
|---|---|---|---|---|---|---|
| C:/Users/E-ngineers/IdeaProjects/BinanceDataFeed/Dumps/backtest/raw_1m_2022/klines | 1928160 | 2022-01-01 00:00 | 2025-08-31 23:59 | 1928160 | 0 | 0 |
| C:/Users/E-ngineers/IdeaProjects/BinanceDataFeed/Dumps/backtest/raw/klines | 578880 | 2025-09-01 00:00 | 2026-10-07 23:59 | 578880 | 0 | 0 |
| F:/MTS/data/tom_raw/klines | 2491200 | 2022-01-01 00:00 | 2026-09-26 23:59 | 0 | 2491200 | 0 |

tom_raw is a subset (0 minutes it has that the main archive lacks, 0 conflicting values) and ends earlier, so it does not extend coverage (F-BT-06). The daily files 2025-09-01..07 duplicate the monthly 2025-09 file (10,080 identical rows, kept once).

Zero-volume bars: 308, flat OHLC: 308, on 8 days: 2022-05-01 (29), 2022-05-28 (35), 2023-09-12 (19), 2023-11-10 (99), 2024-10-28 (89), 2025-01-14 (2), 2025-01-29 (17), 2025-08-29 (18) (F-BT-05). They are kept as real clock minutes.

| TF | closed bars | first open | last close | time gaps | bars with partial minutes | all-zero-volume bars | zero-range bars | ATR SMA/Wilder p5 / p50 / p95 |
|---|---|---|---|---|---|---|---|---|
| 4h | 10446 | 2022-01-01 00:00 | 2026-10-08 00:00 | 0 | 0 | 0 | 0 | 0.768 / 0.989 / 1.188 |
| 1h | 41784 | 2022-01-01 00:00 | 2026-10-08 00:00 | 0 | 0 | 1 | 1 | 0.751 / 0.984 / 1.212 |
| 15m | 167136 | 2022-01-01 00:00 | 2026-10-08 00:00 | 0 | 0 | 13 | 13 | 0.783 / 0.972 / 1.216 |
| 5m | 501408 | 2022-01-01 00:00 | 2026-10-08 00:00 | 0 | 0 | 55 | 55 | 0.810 / 0.975 / 1.198 |

## 2. Analysis settings (not trading parameters)

- ATR(14) Wilder on the bar's own TF, strictly causal, defined from bar index 14 (TR[0] undefined). Plain-SMA ATR is stored beside it (labels_*.csv `atr_sma`) because MTS core uses SMA (FORMULAS.md section 12; F-BT-07).
- Legs: ATR zigzag, r in [1.5, 2.0] (reversal needed to confirm a pivot, x ATR at the pivot bar), leg size threshold k in [3, 5, 8] (x ATR at the leg start bar). A leg is flagged (r, k) when it exists in the r-zigzag and its size is >= k.
- 'N bars either side' (PLAN section 3) is implemented as the zigzag condition itself: the pivot extreme is not exceeded from the previous pivot until a reversal of r x ATR. The pivot bar can never confirm its own reversal; equal extremes keep the earlier bar; the last unconfirmed swing is not a leg. No fixed fractal width was used; the share of pivots that also pass a +-2 bar fractal test is in section 7.
- Times are bar CLOSE times. dur_bars = end pivot bar - start pivot bar. Forward labels: entry = next bar open, window H in [24, 96] bars, unit = ATR at the decision bar.

## 3. Legs per year (flagged legs, by year of leg start)

**4h**

| r | k | 2022 | 2023 | 2024 | 2025 | 2026 | total |
|---|---|---|---|---|---|---|---|
| 1.5 | 3 | 133 | 165 | 155 | 150 | 118 | 721 |
| 1.5 | 5 | 43 | 52 | 50 | 46 | 37 | 228 |
| 1.5 | 8 | 11 | 15 | 10 | 11 | 6 | 53 |
| 2.0 | 3 | 121 | 148 | 133 | 142 | 109 | 653 |
| 2.0 | 5 | 45 | 57 | 58 | 52 | 41 | 253 |
| 2.0 | 8 | 16 | 16 | 17 | 11 | 9 | 69 |

**1h**

| r | k | 2022 | 2023 | 2024 | 2025 | 2026 | total |
|---|---|---|---|---|---|---|---|
| 1.5 | 3 | 583 | 609 | 604 | 599 | 470 | 2865 |
| 1.5 | 5 | 177 | 205 | 204 | 198 | 146 | 930 |
| 1.5 | 8 | 48 | 56 | 42 | 39 | 32 | 217 |
| 2.0 | 3 | 540 | 554 | 546 | 551 | 419 | 2610 |
| 2.0 | 5 | 199 | 219 | 216 | 220 | 168 | 1022 |
| 2.0 | 8 | 63 | 66 | 67 | 58 | 49 | 303 |

**15m**

| r | k | 2022 | 2023 | 2024 | 2025 | 2026 | total |
|---|---|---|---|---|---|---|---|
| 1.5 | 3 | 2418 | 2562 | 2413 | 2447 | 1914 | 11754 |
| 1.5 | 5 | 711 | 819 | 726 | 725 | 598 | 3579 |
| 1.5 | 8 | 166 | 220 | 149 | 165 | 125 | 825 |
| 2.0 | 3 | 2224 | 2331 | 2184 | 2257 | 1733 | 10729 |
| 2.0 | 5 | 827 | 938 | 863 | 858 | 683 | 4169 |
| 2.0 | 8 | 226 | 272 | 220 | 238 | 185 | 1141 |

**5m**

| r | k | 2022 | 2023 | 2024 | 2025 | 2026 | total |
|---|---|---|---|---|---|---|---|
| 1.5 | 3 | 7532 | 8273 | 7827 | 8109 | 6133 | 37874 |
| 1.5 | 5 | 2222 | 2621 | 2221 | 2464 | 1944 | 11472 |
| 1.5 | 8 | 539 | 636 | 503 | 527 | 430 | 2635 |
| 2.0 | 3 | 6977 | 7598 | 7186 | 7466 | 5675 | 34902 |
| 2.0 | 5 | 2607 | 2993 | 2693 | 2880 | 2233 | 13406 |
| 2.0 | 8 | 731 | 834 | 726 | 757 | 589 | 3637 |

2026 is Jan to 2026-10-07 only; 2022 starts 2022-01-01 (ATR needs 14 bars first).

## 4. Leg size distribution (size in ATR at the start bar; all legs of the r-zigzag, not only big ones)

| TF | r | legs | p10 | p25 | p50 | p75 | p90 | p99 | max | median dur (bars) |
|---|---|---|---|---|---|---|---|---|---|---|
| 4h | 1.5 | 1674 | 1.70 | 2.06 | 2.74 | 3.92 | 5.61 | 11.39 | 20.75 | 5.0 |
| 4h | 2.0 | 1044 | 2.25 | 2.66 | 3.39 | 4.95 | 7.13 | 15.61 | 29.63 | 7.0 |
| 1h | 1.5 | 7059 | 1.68 | 2.01 | 2.67 | 3.81 | 5.49 | 10.50 | 34.07 | 4.0 |
| 1h | 2.0 | 4234 | 2.23 | 2.61 | 3.46 | 4.93 | 7.06 | 14.63 | 34.07 | 7.0 |
| 15m | 1.5 | 29189 | 1.69 | 2.01 | 2.66 | 3.77 | 5.36 | 10.77 | 47.87 | 4.0 |
| 15m | 2.0 | 17397 | 2.22 | 2.61 | 3.43 | 4.90 | 6.95 | 13.96 | 83.41 | 7.0 |
| 5m | 1.5 | 91292 | 1.70 | 2.02 | 2.70 | 3.83 | 5.39 | 10.80 | 62.31 | 4.0 |
| 5m | 2.0 | 55663 | 2.23 | 2.63 | 3.48 | 4.92 | 6.96 | 13.62 | 104.87 | 7.0 |

## 5. How much of the price travel sits inside big legs

legs path = sum of |ln(p_end/p_start)| over big legs / same over every leg of that r. bar travel = sum of bar-to-bar |ln(close ratio)| inside big legs / over all bars. time = share of bars inside big legs.

| TF | r | k | big legs | legs path | bar travel | time |
|---|---|---|---|---|---|---|
| 4h | 1.5 | 3 | 721 | 60.9% | 66.7% | 61.2% |
| 4h | 1.5 | 5 | 228 | 26.9% | 30.7% | 25.0% |
| 4h | 1.5 | 8 | 53 | 8.5% | 9.3% | 6.4% |
| 4h | 2.0 | 3 | 653 | 76.7% | 81.2% | 78.7% |
| 4h | 2.0 | 5 | 253 | 40.5% | 45.4% | 41.8% |
| 4h | 2.0 | 8 | 69 | 15.1% | 15.8% | 13.3% |
| 1h | 1.5 | 3 | 2865 | 59.4% | 64.1% | 54.4% |
| 1h | 1.5 | 5 | 930 | 26.6% | 29.1% | 20.7% |
| 1h | 1.5 | 8 | 217 | 8.6% | 9.2% | 5.2% |
| 1h | 2.0 | 3 | 2610 | 76.9% | 81.0% | 75.3% |
| 1h | 2.0 | 5 | 1022 | 41.1% | 44.2% | 36.2% |
| 1h | 2.0 | 8 | 303 | 16.4% | 17.2% | 12.4% |
| 15m | 1.5 | 3 | 11754 | 58.9% | 63.0% | 54.7% |
| 15m | 1.5 | 5 | 3579 | 25.8% | 27.8% | 19.4% |
| 15m | 1.5 | 8 | 825 | 8.3% | 8.7% | 4.9% |
| 15m | 2.0 | 3 | 10729 | 76.5% | 79.6% | 74.9% |
| 15m | 2.0 | 5 | 4169 | 41.1% | 43.1% | 35.3% |
| 15m | 2.0 | 8 | 1141 | 15.7% | 16.0% | 11.0% |
| 5m | 1.5 | 3 | 37874 | 59.9% | 64.4% | 58.5% |
| 5m | 1.5 | 5 | 11472 | 25.9% | 27.9% | 21.2% |
| 5m | 1.5 | 8 | 2635 | 8.6% | 9.0% | 5.2% |
| 5m | 2.0 | 3 | 34902 | 77.4% | 80.8% | 77.7% |
| 5m | 2.0 | 5 | 13406 | 41.1% | 43.3% | 37.2% |
| 5m | 2.0 | 8 | 3637 | 15.9% | 16.2% | 11.3% |

## 6. Big legs a human would call tradable (duration > 3 bars)

| TF | r | k | big legs | dur > 3 bars | share | median dur (bars) |
|---|---|---|---|---|---|---|
| 4h | 1.5 | 3 | 721 | 584 | 81.0% | 7.0 |
| 4h | 1.5 | 5 | 228 | 205 | 89.9% | 10.0 |
| 4h | 1.5 | 8 | 53 | 48 | 90.6% | 10.0 |
| 4h | 2.0 | 3 | 653 | 564 | 86.4% | 10.0 |
| 4h | 2.0 | 5 | 253 | 241 | 95.3% | 15.0 |
| 4h | 2.0 | 8 | 69 | 67 | 97.1% | 19.0 |
| 1h | 1.5 | 3 | 2865 | 2151 | 75.1% | 6.0 |
| 1h | 1.5 | 5 | 930 | 774 | 83.2% | 8.0 |
| 1h | 1.5 | 8 | 217 | 194 | 89.4% | 8.0 |
| 1h | 2.0 | 3 | 2610 | 2156 | 82.6% | 9.0 |
| 1h | 2.0 | 5 | 1022 | 935 | 91.5% | 12.0 |
| 1h | 2.0 | 8 | 303 | 289 | 95.4% | 14.0 |
| 15m | 1.5 | 3 | 11754 | 8865 | 75.4% | 6.0 |
| 15m | 1.5 | 5 | 3579 | 2927 | 81.8% | 8.0 |
| 15m | 1.5 | 8 | 825 | 718 | 87.0% | 8.0 |
| 15m | 2.0 | 3 | 10729 | 8918 | 83.1% | 9.0 |
| 15m | 2.0 | 5 | 4169 | 3732 | 89.5% | 12.0 |
| 15m | 2.0 | 8 | 1141 | 1072 | 94.0% | 14.0 |
| 5m | 1.5 | 3 | 37874 | 29372 | 77.6% | 7.0 |
| 5m | 1.5 | 5 | 11472 | 9801 | 85.4% | 8.0 |
| 5m | 1.5 | 8 | 2635 | 2310 | 87.7% | 9.0 |
| 5m | 2.0 | 3 | 34902 | 29571 | 84.7% | 9.0 |
| 5m | 2.0 | 5 | 13406 | 12286 | 91.6% | 12.0 |
| 5m | 2.0 | 8 | 3637 | 3414 | 93.9% | 13.0 |

## 7. Audit of the legs (independent re-check against the raw bars)

pivot_not_bar_extreme must be 0. interior_more_extreme_bar = a whipsaw bar strictly inside a leg that spiked past a pivot and still extended the swing (intrabar order unknown, so the zigzag cannot move the pivot). pivot_bar_engulfs_leg = the pivot bar's own opposite extreme goes beyond the other pivot (one bar as long as the whole leg). size_below_r must be 0.

| TF | subset | legs | pivot_not_bar_extreme | interior_more_extreme_bar | pivot_bar_engulfs_leg | size_below_r |
|---|---|---|---|---|---|---|
| 4h | all legs | 1930 | 0 | 9 | 166 | 0 |
| 4h | r=1.5 k=3 | 721 | 0 | 4 | 15 | 0 |
| 4h | r=1.5 k=8 | 53 | 0 | 0 | 0 | 0 |
| 4h | r=2.0 k=3 | 653 | 0 | 2 | 11 | 0 |
| 4h | r=2.0 k=8 | 69 | 0 | 0 | 0 | 0 |
| 1h | all legs | 8173 | 0 | 41 | 737 | 0 |
| 1h | r=1.5 k=3 | 2865 | 0 | 23 | 83 | 0 |
| 1h | r=1.5 k=8 | 217 | 0 | 4 | 0 | 0 |
| 1h | r=2.0 k=3 | 2610 | 0 | 11 | 74 | 0 |
| 1h | r=2.0 k=8 | 303 | 0 | 5 | 0 | 0 |
| 15m | all legs | 33790 | 0 | 135 | 2481 | 0 |
| 15m | r=1.5 k=3 | 11754 | 0 | 75 | 346 | 0 |
| 15m | r=1.5 k=8 | 825 | 0 | 11 | 6 | 0 |
| 15m | r=2.0 k=3 | 10729 | 0 | 36 | 297 | 0 |
| 15m | r=2.0 k=8 | 1141 | 0 | 11 | 8 | 0 |
| 5m | all legs | 105235 | 0 | 242 | 6657 | 0 |
| 5m | r=1.5 k=3 | 37874 | 0 | 125 | 854 | 0 |
| 5m | r=1.5 k=8 | 2635 | 0 | 19 | 21 | 0 |
| 5m | r=2.0 k=3 | 34902 | 0 | 62 | 725 | 0 |
| 5m | r=2.0 k=8 | 3637 | 0 | 16 | 23 | 0 |

| TF | r | pivots | pass +-2 bar fractal | share |
|---|---|---|---|---|
| 4h | 1.5 | 1675 | 1476 | 88.1% |
| 4h | 2.0 | 1045 | 989 | 94.6% |
| 1h | 1.5 | 7060 | 6079 | 86.1% |
| 1h | 2.0 | 4235 | 3954 | 93.4% |
| 15m | 1.5 | 29190 | 25503 | 87.4% |
| 15m | 2.0 | 17398 | 16289 | 93.6% |
| 5m | 1.5 | 91292 | 80633 | 88.3% |
| 5m | 2.0 | 55664 | 52682 | 94.6% |

Big legs (flagged k=3, r=1.5) that start within 28 bars after a maintenance-flat bar (their ATR unit is depressed): 4h 0, 1h 3, 15m 9, 5m 21.

## 8. Reading (derived from the tables above)

- Big legs are frequent enough to study: at k=5 (r=1.5) there are 228 on 4h, 930 on 1h, 3,579 on 15m and 11,472 on 5m over 4.76 years, spread evenly by year
  (1h: 177, 205, 204, 198 and 146 for 9 months of 2026). At k=8 the counts drop to 53 / 217 / 825 / 2,635.
- Big legs are not where most of the travel is. Legs of at least 3 ATR (r=1.5) hold 63-67 % of bar-to-bar travel in 54-61 % of the bars; legs of at least 5 ATR hold
  28-31 % of the travel in 19-25 % of the bars; legs of at least 8 ATR hold about 9 % in about 5 %. A layer that only fires inside k=8 legs sees a small slice of the market.
- Tradability: 75-81 % of k=3 legs last more than 3 bars at r=1.5 (83-86 % at r=2.0); at k=8 it is 87-91 % (r=1.5) and 94-97 % (r=2.0). The remaining short legs are spikes
  of 1-3 bars that no layer on that TF can enter after the fact.
- Leg audit: no pivot is off its bar extreme and no leg is smaller than its r. A whipsaw bar inside a leg (intrabar order unknown) occurs in 0.3-1.9 % of big legs
  (5m r=1.5 k=3: 125 of 37,874; 1h r=1.5 k=8: 4 of 217), and 86-95 % of pivots also pass a +-2 bar fractal test.
- Units: the SMA/Wilder ATR ratio is 0.97-0.99 at the median but 0.75-1.22 between the 5th and 95th percentile, so stop_dist_atr must name its ATR kind (F-BT-07).
- Open: legs for 1m are not built, so turn_of_candle 1m cannot be scored (F-BT-08).
