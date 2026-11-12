# RESULT: four untested value-area rules on BTC DEV (PREREG.md, committed before this run, unchanged)

Card btc-test-of-untested-rules-acceptance-re. DEV 2022-02-01..2024-05-31 only; VALIDATION never loaded (the loader stops at the 2024-05 file, asserted in run_dev.py). Data: D:/MTS_data/binance_aggtrades/reduced 15m bars (read only). Fee 10 bp round trip. Placebo 500 draws, seed 1.
Regime mix: DEV 2022-02-01..2024-05-31 (BTC daily close 38,680 -> 67,578, +75 %); 832 DEV days with a 50-day SMA, 51.4 % close above it and 48.6 % below (same descriptive count as the PREREG, no trade involved).
Method note: 8 gaps in the 15m series (days with fewer than 96 bars are skipped as profile days); log sanity checks entry opens against the 1m klines with a 0.002 % tolerance because the reduced 15m open is the first aggtrade (a one-tick difference, 0.1 USD, showed on one B entry at 0.002 %). Trades whose cap would run past the loaded data are dropped (censored).

## Verdicts in plain words
| rule | n | mean net bp | t | halves | placebo >= real | verdict |
|---|---|---|---|---|---|---|
| A acceptance then edge retest (long/short edge retest after 8 closes) | 139 | -28.78 | -2.75 | -21.2 / -37.7 | 0.978 | FAIL: accepted edges hold more often (58.6 % vs 46.7 %) but buying the hold loses money after fees and does worse than random entries |
| B return to liquidity, fade to prior POC | 885 | -12.18 | -3.90 | -12.6 / -11.8 | 0.736 | FAIL: price revisits the POC within 6 h in 44.3 % of exits, but the 1:1 fade is net negative and no better than placebo |
| C thin close pulls to POC | 462 | -2.64 | -0.40 | -8.8 / +4.1 | 0.074 | FAIL (mean <= 0): thin days touch the POC less often next day (72.0 %) than other days (78.3 %); the trade is near zero, better than placebo (-10.9) only because fees dominate random entries; first half negative |
| D naked weekly POC | 50 | +4.54 | 0.06 | -40.3 / +66.5 | 0.346 | INCONCLUSIVE: no edge; 75.0 % touch within 4 weeks versus 80.9 % for the mirror level, so a naked POC is touched no more often than a random level |

Counts as trials ~104..107; none passes, none earns VALIDATION. Each rule's descriptive finding matches the video's own caveat on D ("not an edge in itself").

## Raw output (run_dev.py, dev_output.txt)

```
## A acceptance then edge retest (BB3c8visnkI R4)
n 139, win rate 35.3 %, mean net bp -28.78, t -2.75, max drawdown 4022.2 bp (sum, peak to trough)
hold share accepted events: n 237, share 0.586; non-accepted events: n 2303, share 0.467
half 1 (before 2023-04-02): n 75 mean -21.19 | half 2: n 64 mean -37.69
| cut | n | mean | sum |
|---|---|---|---|
| year 2022 | 56 | -10.1666 | -569.3275 |
| year 2023 | 60 | -34.0165 | -2040.9911 |
| year 2024 | 23 | -60.4595 | -1390.5696 |
| long | 67 | -36.6305 | -2454.2460 |
| short | 72 | -21.4811 | -1546.6422 |
placebo (500 draws, seed 1): mean net bp -9.83, sd 9.58, share of draws >= real mean 0.978
VERDICT_MECH: FAIL
## B return to liquidity, fade to prior POC (BB3c8visnkI R5)
n 885, win rate 45.6 %, mean net bp -12.18, t -3.90, max drawdown 11525.6 bp (sum, peak to trough)
revisit share within 24 bars: n 938, share 0.443; exits: stop 340, tp 264, cap 281
half 1 (before 2023-04-02): n 420 mean -12.64 | half 2: n 465 mean -11.77
| cut | n | mean | sum |
|---|---|---|---|
| year 2022 | 324 | -12.0459 | -3902.8768 |
| year 2023 | 382 | -13.9339 | -5322.7472 |
| year 2024 | 179 | -8.6929 | -1556.0287 |
| long | 434 | -11.5559 | -5015.2719 |
| short | 451 | -12.7858 | -5766.3808 |
placebo (500 draws, seed 1): mean net bp -10.56, sd 2.60, share of draws >= real mean 0.736
VERDICT_MECH: FAIL
## C thin close pulls to POC (YkclL6xgu-s R5)
n 462, win rate 52.4 %, mean net bp -2.64, t -0.40, max drawdown 3601.0 bp (sum, peak to trough)
touch share next day, THIN days: n 496, share 0.720; other days: n 337, share 0.783; exits: stop 192, tp 218, cap 52
half 1 (before 2023-04-02): n 241 mean -8.82 | half 2: n 221 mean 4.10
| cut | n | mean | sum |
|---|---|---|---|
| year 2022 | 186 | -7.1678 | -1333.2138 |
| year 2023 | 189 | -0.6954 | -131.4341 |
| year 2024 | 87 | 2.8092 | 244.4011 |
| long | 212 | -5.4286 | -1150.8535 |
| short | 250 | -0.2776 | -69.3933 |
placebo (500 draws, seed 1): mean net bp -10.91, sd 5.65, share of draws >= real mean 0.074
VERDICT_MECH: FAIL
## D naked weekly POC (ODdF0Bn_KSc R6)
n 50, win rate 56.0 %, mean net bp 4.54, t 0.06, max drawdown 3942.3 bp (sum, peak to trough)
touch rate within 4 weeks: n 68, share 0.750; mirror-level touch rate: n 68, share 0.809; median MFE over 96 bars 162.4 bp (descriptive); log sanity skipped: fill is a limit at the POC, not a bar open
half 1 (before 2023-04-02): n 29 mean -40.33 | half 2: n 21 mean 66.51
| cut | n | mean | sum |
|---|---|---|---|
| year 2022 | 23 | 16.6137 | 382.1148 |
| year 2023 | 19 | -66.6362 | -1266.0886 |
| year 2024 | 8 | 138.8938 | 1111.1502 |
| long | 21 | 38.6261 | 811.1484 |
| short | 29 | -20.1370 | -583.9721 |
placebo (500 draws, seed 1): mean net bp -12.69, sd 41.74, share of draws >= real mean 0.346
VERDICT_MECH: INCONCLUSIVE
```
