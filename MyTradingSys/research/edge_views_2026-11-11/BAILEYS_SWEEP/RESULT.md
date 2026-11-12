# RESULT: Baileys sweep -> 15m BOS -> demand retest, with the daily trend (DEV only)

Frozen rule: PREREG.md (commit b4b9ef97c, before any trade was computed). Code: baileys_sweep.py; run: run_dev.py; raw output: dev_output.txt.
BTCUSDT 1m Binance perp, DEV 2022-02-01..2024-05-31; data to 2024-06-07 read only to finish open trades (VALIDATION untouched). Descriptive; no edge claim.

**Verdict: FAIL.** 321 trades, fee-net mean -0.324 R (t -3.38). Both DEV halves negative, both sides negative, every year negative.
Pass bar was mean > 0, t >= 2, both halves > 0.

Regime mix: DEV days with a long bias 51.4 % and short bias 48.6 % (832 days with SMA50); trades 164 long, 157 short; entries 141 in 2022, 138 in 2023, 42 in 2024 (to May).

## Numbers
```
n 321, win rate 23.7 %, mean net R -0.3236, mean net bp -21.8, t -3.38, max drawdown 111.36 R (sum of R, peak to trough)
gross mean R -0.0582; exits: stop 244, tp 75, cap 2
median risk 0.532 % of price
half 1 (before 2023-04-02): n 178 mean -0.2411 | half 2: n 143 mean -0.4262
| cut | n | mean | sum |
|---|---|---|---|
| year 2022 | 141 | -0.2091 | -29.4763 |
| year 2023 | 138 | -0.4400 | -60.7203 |
| year 2024 | 42 | -0.3256 | -13.6747 |
| long | 164 | -0.3759 | -61.6531 |
| short | 157 | -0.2689 | -42.2181 |
placebo (500 draws, seed 1): mean net R -0.2814, sd 0.0947, share of draws >= real mean 0.676
VERDICT_MECH: FAIL
```
Log sanity (entry fills vs 1m klines, last 5 trades) printed OK by trade_sanity.log_sanity; the exit is a stop/target price (not a bar open/close), so
exit prices were instead checked to lie inside their 15m bar's range: 0 of 321 outside.

## Reading (plain)
- Gross (before fee) mean is -0.058 R: win rate 23.7 % against 25 % needed at 3R, so the setup itself carries no gross edge on this mechanical stand-in.
- The fee then costs about 0.27 R per trade, because the median stop is only 0.53 % of price (10 bp round trip / 0.53 % risk). Tight demand-base stops make a 10 bp fee large in R.
- Placebo (random entries, same sides, same R%): -0.281 R; the real rule (-0.324) is no better (share of placebo draws at or above it: 0.676). The trend/sweep/BOS filters add nothing over random entries with the same stop and 3R rule.
- Trades WITH the daily trend, unlike the tested sweep fades (T04 -0.221 R n 1150; -0.106 R n 1,484), land in the same place: negative after fees.

## Corrections and decisions (OURS)
- PREREG named the DEV half split as 2023-03-17; the exact midpoint of 2022-02-01..2024-05-31 is 2023-04-02 and the code uses that. No effect on the verdict (both halves negative at either date).
- This is a mechanical proxy of a discretionary method (zone = lowest 15m bar's body top, pivots n=3, SMA50 bias). A different reading of "demand" or "clearly bullish" is a different rule; this test does not speak for Bailey's eye-drawn zones.
- Not run: VALIDATION (a FAIL does not earn it). Trial count: about 101.
- Tests: test_baileys_sweep.py (6 pass); the prefix-invariance test fails on the look-ahead-shifted variant (shift=1), as test_look_ahead_version_fails_prefix_invariance asserts.
