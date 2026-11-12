# RESULT: value-area re-entry (R1) and two consecutive daily POC shifts (R2), BTC DEV only

Frozen rules: PREREG.md (commit 1ee8db2a2, 2026-11-12 14:46 IST, before any trade was computed). Code: va_poc.py; run: run_dev.py; raw output: dev_output.txt; tests: test_va_poc.py (12 pass).
BTCUSDT 1m Binance perp, DEV 2022-02-01..2024-05-31; data to 2024-06-07 read only to finish open R1 trades and R2 exits (VALIDATION untouched). Volume profile from 1m bars is an OURS approximation. Descriptive; no edge claim.

Regime mix: DEV days with a 50-day SMA: 51.4 % close above, 48.6 % below (832 days, counted in the PREREG without any trade); R1 trades 440 long / 442 short; R2 signals 229 up-shift / 192 down-shift (horizon 1); entries by year in the tables below.

| Rule | n | mean net | t | half 1 / half 2 | placebo mean (share >= real) | Verdict |
|---|---|---|---|---|---|---|
| R1 value-area re-entry | 882 | -0.2146 R | -3.23 | -0.193 / -0.233 | -0.2786 R (0.146) | **FAIL** |
| R2 two POC shifts, 1 day (primary) | 421 | +4.45 bp | 0.29 | +13.6 / -5.3 bp | -9.04 bp (0.162) | **INCONCLUSIVE** |
| R2 two POC shifts, 3 days (secondary, non-overlapping) | 215 | -2.30 bp | -0.06 | +13.7 / -19.1 bp | -8.13 bp (0.436) | **FAIL** |

Pass bar (PREREG): mean > 0, t >= 2, both DEV halves > 0; n < 30 = INCONCLUSIVE.

## Numbers (copied from dev_output.txt)
```
## R1 value-area re-entry (net R)
n 882, win rate 33.6 %, mean net R -0.2146, t -3.23, max drawdown 203.78 R (sum, peak to trough)
gross mean R 0.0515; exits: stop 558, tp 265, cap 59; median risk 0.488 % of price, median target distance 1.199 %
half 1 (before 2023-04-02): n 409 mean -0.1931 | half 2: n 473 mean -0.2331
| cut | n | mean | sum |
| year 2022 | 327 | -0.1395 | -45.6254 |
| year 2023 | 399 | -0.2140 | -85.3914 |
| year 2024 | 156 | -0.3733 | -58.2340 |
| long | 440 | -0.1265 | -55.6807 |
| short | 442 | -0.3022 | -133.5700 |
placebo (500 draws, seed 1): mean net R -0.2786, sd 0.0571, share of draws >= real mean 0.146
## R2 horizon 1 (net bp)
n 421, win rate 44.2 %, mean net bp 4.4524, t 0.29, max drawdown 4845.71 bp (sum, peak to trough)
half 1: n 218 mean 13.5721 | half 2: n 203 mean -5.3412
| year 2022 | 175 | 4.8657 | 851.5005 |
| year 2023 | 168 | -7.8555 | -1319.7250 |
| year 2024 | 78 | 30.0344 | 2342.6826 |
| long | 229 | 16.7657 | 3839.3407 |
| short | 192 | -10.2338 | -1964.8826 |
placebo (500 draws, seed 1): mean net bp -9.0386, sd 14.0543, share of draws >= real mean 0.162
## R2 horizon 3 (net bp)
n 215, win rate 46.0 %, mean net bp -2.2997, t -0.06, max drawdown 7640.31 bp (sum, peak to trough)
half 1: n 110 mean 13.7159 | half 2: n 105 mean -19.0780
| year 2022 | 87 | -33.3290 | -2899.6197 |
| year 2023 | 91 | -9.2906 | -845.4430 |
| year 2024 | 37 | 87.8547 | 3250.6235 |
| long | 108 | 49.4046 | 5335.6971 |
| short | 107 | -54.4873 | -5830.1363 |
placebo (500 draws, seed 1): mean net bp -8.1309, sd 33.6068, share of draws >= real mean 0.436
```
Log sanity (entry fills, and R2 exit fills, vs 1m klines, last 5 trades) printed OK from trade_sanity.log_sanity for all three runs; R1 exits are stop/target prices, checked to lie inside their 15m bar range: 0 of 882 outside.

## Reading (plain)
- R1: gross mean is +0.052 R (win 33.6 %, target is about 2.5x the stop), so before fees there is a little; the 10 bp fee costs about 0.27 R because the median stop is only 0.49 % of price. Net -0.215 R with t -3.2, both halves, every year and both sides negative. Real is slightly better than the placebo (-0.279 R; 14.6 % of draws are at or above it) but still negative: the value-area re-entry adds no fee-net edge. Shorts are worse (-0.30 R) than longs (-0.13 R).
- R2 (primary, 1 day): +4.5 bp net, t 0.29, positive only in half 1 (+13.6 bp), negative in half 2 (-5.3 bp); 2023 negative. The long side (+16.8 bp) carries it and the short side (-10.2 bp) loses; that is the bull drift of the span, not a shift effect (the placebo mean is -9 bp: drift near zero minus the 10 bp fee, direction matched). INCONCLUSIVE by the bar (t < 2, half 2 negative).
- R2 3-day: -2.3 bp, t -0.06, same long/short split (+49 / -54 bp). FAIL. No horizon passes.

## Decisions and caveats (OURS)
- Volume profile is built from 1m bars by typical price (not trade-level); bin width 0.05 % of the day close. A different bin width or profile construction is a different rule. Neither rule is the analyst's own method; a discretionary read of "failed breakout" or "shift" may differ.
- R2 signals use strictly increasing/decreasing POC price; bin-to-bin noise (width changes daily with the close) can create small shifts. Not tuned.
- Max drawdown for R2 is the sum of bp per signal, not a compounded equity curve.
- Not run: VALIDATION (neither rule earns it). Trial count: about 103 (R1 ~102, R2 ~103; R2 horizon 3 is secondary, not a separate trial).
- Tests: test_va_poc.py, 12 pass; a mutant of va_poc.profile (close-only price, 50 % value-area share) fails 2 of them.
