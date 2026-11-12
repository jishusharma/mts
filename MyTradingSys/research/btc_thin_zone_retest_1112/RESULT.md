# RESULT: BTC thin-zone pass-through (T1) and accepted-breakdown retest (T2), DEV 2022-02-01 .. 2024-05-31

PREREG.md (commit b69268402) was committed before any trade was simulated; rule code and tests (d7a10b848) too. Parameters unchanged since; one run. Fee 10 bp round trip, entry at the next 1m open, no look-ahead. VALIDATION never opened. No edge claim, no forecast.
Regime mix: bull 35%, bear 16%, range 42%, n/a 7% of 851 DEV days (btc_orderflow_map_1112/CLOCKS.md); entries T1 {'n/a': 338, 'range': 1889, 'bear': 866, 'bull': 1799}, T2 {'range': 46, 'bear': 2, 'bull': 23}.
Trial count: about 100 earlier studies + these 2 marked cells = about 102 tries. Missing 1m bars in DEV: 0.

## Verdicts
**T1 thin-zone pass-through: FAIL.** 4892 trades, fee-net mean -9.71 bp, t -25.6. Gross mean is 0.29 bp, so there is no move to pay the 10 bp fee from; 87% of trades hit the one-bucket stop. Both DEV halves negative. The placebo with the same geometry gives -9.60 bp, the real mean is inside its 1-99% band: not separable from random timing.
**T2 accepted-breakdown retest: FAIL.** 71 trades, fee-net mean 3.68 bp, t 0.35 (needs 2). Half A +13.01 bp (n 21), half B -0.24 bp (n 50): the second half is not positive. The real mean is inside the placebo 1-99% band [-38.9, 20.5] (placebo mean -10.3); long rows +9.4 bp (n 35), short rows -1.9 bp (n 36), neither tested alone. Gross 13.7 bp. n is above 30 so the verdict is FAIL, not INCONCLUSIVE; with sd 89 bp the sample is still thin for a small effect.

## Table (net bp per trade, after the 10 bp fee)
| Idea | n | win rate | mean | median | t | max drawdown (bp, cum.) | DEV halves (n / mean) | placebo mean [1%, 99%] | verdict |
|---|---|---|---|---|---|---|---|---|---|
| T1 thin zone | 4892 | 11.1% | -9.71 | -16.75 | -25.65 | 47480 | A 2431 / -9.81; B 2461 / -9.60 | -9.60 [-10.41, -8.80] | FAIL |
| T2 breakdown retest | 71 | 56.3% | 3.68 | 29.25 | 0.35 | 903 | A 21 / 13.01; B 50 / -0.24 | -10.28 [-38.89, 20.47] | FAIL |

Exit mix: T1 {'stop': 4272, 'time': 359, 'target': 261}; T2 {'stop': 28, 'time': 5, 'target': 38}. Dropped / skipped: T1 {'no_node': 7379, 'bad_geometry': 0, 'no_entry_bar': 0, 'busy': 1195, 'missing_bar': 0}; T2 {'no_retest': 72, 'reclaimed': 66, 'bad_geometry': 0, 'no_entry_bar': 0, 'busy': 3, 'missing_bar': 1}.

## Log sanity (trade_sanity.log_sanity path, run before any metric; last 5 trades each, T1 then T2)
Entry price equals the entry bar open on the 1m candles for all 10. Time exits are checked against the bar close; stop/target fills are not an open or close, so for them the check is that the fill price lies inside the exit bar's high-low (OURS adaptation of the helper, which only tests open/close).
```
Log sanity (last 5 trades vs 1m klines; entry/exit px vs bar open/close):
  OK   long  entry 2024-05-29 16:55 px 67672.70 | kline o 67672.70 c 67628.10 | ok   exit 2024-05-29 16:59 px 67624.11 | kline o 67645.00 c 67596.10 | ok
  OK   long  entry 2024-05-29 18:00 px 67658.60 | kline o 67658.60 c 67624.70 | ok   exit 2024-05-29 18:00 px 67624.11 | kline o 67658.60 c 67624.70 | ok
  OK   long  entry 2024-05-29 18:45 px 67467.60 | kline o 67467.60 c 67479.40 | ok   exit 2024-05-29 18:45 px 67421.59 | kline o 67467.60 c 67479.40 | ok
  OK   long  entry 2024-05-29 19:05 px 67474.10 | kline o 67474.10 c 67482.10 | ok   exit 2024-05-29 19:44 px 67421.59 | kline o 67449.90 c 67406.30 | ok
  OK   long  entry 2024-05-29 21:00 px 67516.30 | kline o 67516.30 c 67521.00 | ok   exit 2024-05-29 21:08 px 67455.30 | kline o 67465.50 c 67441.70 | ok
Log sanity (last 5 trades vs 1m klines; entry/exit px vs bar open/close):
  OK   long  entry 2024-04-09 08:00 px 70444.10 | kline o 70444.10 c 70334.40 | ok   exit 2024-04-09 08:09 px 69660.30 | kline o 69733.20 c 69841.40 | ok
  OK   short entry 2024-04-27 15:00 px 63101.80 | kline o 63101.80 c 63067.20 | ok   exit 2024-04-28 02:53 px 64029.20 | kline o 63976.20 c 63990.00 | ok
  OK   short entry 2024-05-09 04:00 px 61647.50 | kline o 61647.50 c 61659.70 | ok   exit 2024-05-09 10:58 px 60843.60 | kline o 60902.80 c 60869.10 | ok
  OK   long  entry 2024-05-14 07:00 px 62014.60 | kline o 62014.60 c 62009.90 | ok   exit 2024-05-14 12:30 px 61250.45 | kline o 61932.00 c 61382.90 | ok
  OK   short entry 2024-05-20 02:00 px 66494.00 | kline o 66494.00 c 66474.60 | ok   exit 2024-05-20 04:34 px 66757.25 | kline o 66731.30 c 66853.20 | ok
```

## Per-year and long/short rows (trade_sanity.year_side_lines; mean and sum in net bp)
T1
| cut | n | mean | sum |
|---|---|---|---|
| year 2022 | 1982 | -9.7390 | -19302.6918 |
| year 2023 | 1940 | -9.6660 | -18751.9972 |
| year 2024 | 970 | -9.7163 | -9424.8306 |
| long | 2452 | -9.6495 | -23660.5465 |
| short | 2440 | -9.7619 | -23818.9732 |

T2
| cut | n | mean | sum |
|---|---|---|---|
| year 2022 | 13 | 25.7699 | 335.0092 |
| year 2023 | 44 | -3.8815 | -170.7856 |
| year 2024 | 14 | 6.9230 | 96.9217 |
| long | 35 | 9.3933 | 328.7665 |
| short | 36 | -1.8784 | -67.6211 |

## Notes
- T1 profile: previous 7 UTC days, 0.05% log buckets; the target search found no node within 5% for 7379 triggers (all dropped, counted above), mostly breakouts above the weekly range.
- Tests: test_rules.py, 7 synthetic checks; the look-ahead shift versions of T1 and T2 fail the entry-bar contract (caught).
- Raw numbers: result_raw.json (no prices, no account data). Run: python MyTradingSys/research/btc_thin_zone_retest_1112/run.py (2 min, F: data).
