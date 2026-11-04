# WT extreme cross vs a volatility-matched baseline, BTCUSDT + ETHUSDT USD-M futures (DEV only)

Regime mix: BTCUSDT 130 weeks: bull 25 (19%) | bear 0 (0%) | range 105 (81%) | n/a 0 (0%); ETHUSDT 130 weeks: bull 11 (8%) | bear 0 (0%) | range 119 (92%) | n/a 0 (0%)

**Verdict: VOLATILITY-ONLY. The HTF-against / prior-trend bounce excess is the ATR state, not WaveTrend: matched against bars of the
same ATR(14) decile, the 4 focal POOL buy cells are -0.010 % (t -3.2), -0.010 % (t -2.4), +0.013 % (t 0.3), -0.046 % (t -1.0);
0 of 4 pass Holm, all have >= 269 days. Fee-net at 0.10 % rt is below zero in 161 of 162 cells (-0.203 to -0.025 %); the one above,
ETH 15m sell prior_trend HTF with (n 242, 89 days), is +0.026 % (t 0.3) and -0.014 % at 0.14 %.**

Card `ms-wt-extreme-cross-volmatch-eth`; PRE_REG.md (frozen before any return). Code `study.py`, tests `test_volmatch.py` (4 tests, all 4
failed on the stub first), cells `dev_cells.csv` (162 rows: BTC / ETH / POOL x tf x side x prior-day tag x HTF), `summary.json`.

## Context

- Window: DEV event closes in [2022-01-01, 2024-07-01), BTCUSDT and ETHUSDT USD-M futures 1m (F:/MTS/data/tom_raw/klines), resampled
  5m / 15m. Loader raises on an end after DEV_END; `splits.assert_dev_only` on every scored bar. VALIDATION / HOLDOUT not read.
- Descriptive: no survivor rule, no trade claim. Cost from fees.py (2 x BINANCE_TAKER = 0.10 % rt) and the source's 0.14 %.

## BTC reproduction (futures vs the shipped spot study, buy -50 / sell +40, all tags)

| tf | side | spot n (source) | futures n | spot unmatched excess (t) | futures unmatched excess (t) |
|---|---|---|---|---|---|
| 1m | buy | 15936 | 15935 | +0.013 (3.7) | +0.013 (3.7) |
| 1m | buy, HTF against | 7434 | 7433 | +0.033 (5.4) | +0.033 (5.4) |
| 5m | buy, HTF against | 1422 | 1422 | +0.105 (4.3) | +0.105 (4.3) |
| 15m | buy, HTF against | 477 | 476 | +0.207 (3.7) | +0.211 (3.7) |
| 15m | buy, prior_trend | 244 | 243 | +0.232 (3.3) | +0.238 (3.3) |

Futures reproduce the source within 1 event per cell, so the matched column below reads against the same events.

## Focal cells (PRE_REG verdict rule, POOL buy, Holm m = 4)

| tf | split | n | days | unmatched excess % (t) | matched excess % (t) | one-sided p | Holm |
|---|---|---|---|---|---|---|---|
| 1m | HTF against | 15208 | 875 | +0.045 (8.6) | -0.010 (-3.2) | 0.999 | no |
| 1m | prior_trend | 8203 | 458 | +0.044 (6.1) | -0.010 (-2.4) | 0.992 | no |
| 15m | HTF against | 964 | 506 | +0.251 (5.6) | +0.013 (0.3) | 0.371 | no |
| 15m | prior_trend | 512 | 269 | +0.223 (4.1) | -0.046 (-1.0) | 0.840 | no |

## Per symbol and pooled (day tag all unless named; net = 10-bar close-to-close minus cost)

| sym | tf | side | split | n | days | unmatched excess % (t) | matched excess % (t) | net @0.10 % | net @0.14 % |
|---|---|---|---|---|---|---|---|---|---|
| BTC | 1m | buy | HTF all | 15935 | 912 | +0.013 (3.7) | -0.011 (-6.1) | -0.101 | -0.141 |
| BTC | 1m | buy | HTF against | 7433 | 437 | +0.033 (5.4) | -0.012 (-3.4) | -0.112 | -0.152 |
| BTC | 1m | buy | prior_trend | 3967 | 224 | +0.038 (4.8) | -0.012 (-3.0) | -0.112 | -0.152 |
| BTC | 15m | buy | HTF against | 476 | 256 | +0.211 (3.7) | +0.020 (0.4) | -0.080 | -0.120 |
| BTC | 15m | buy | prior_trend | 243 | 132 | +0.238 (3.3) | -0.010 (-0.2) | -0.039 | -0.079 |
| ETH | 1m | buy | HTF all | 16110 | 912 | +0.016 (3.3) | -0.016 (-5.9) | -0.102 | -0.142 |
| ETH | 1m | buy | HTF against | 7775 | 438 | +0.057 (6.7) | -0.008 (-1.6) | -0.105 | -0.145 |
| ETH | 1m | buy | prior_trend | 4236 | 234 | +0.049 (4.2) | -0.008 (-1.2) | -0.106 | -0.146 |
| ETH | 15m | buy | HTF against | 488 | 250 | +0.290 (4.1) | +0.007 (0.1) | -0.085 | -0.125 |
| ETH | 15m | buy | prior_trend | 269 | 137 | +0.210 (2.6) | -0.078 (-1.1) | -0.025 | -0.065 |
| POOL | 1m | buy | HTF all | 32045 | 1824 | +0.014 (4.8) | -0.014 (-8.3) | -0.102 | -0.142 |
| POOL | 1m | sell | HTF all | 53138 | 1824 | -0.008 (-3.7) | -0.016 (-15.5) | -0.102 | -0.142 |
| POOL | 5m | buy | HTF against | 2948 | 803 | +0.117 (6.4) | -0.023 (-1.7) | -0.104 | -0.144 |
| POOL | 5m | buy | prior_trend | 1498 | 419 | +0.131 (5.2) | -0.017 (-0.9) | -0.086 | -0.126 |
| POOL | 5m | sell | HTF all | 10277 | 1807 | -0.024 (-3.8) | -0.046 (-9.9) | -0.103 | -0.143 |
| POOL | 15m | buy | HTF all | 1906 | 1003 | +0.063 (2.4) | -0.080 (-3.5) | -0.092 | -0.132 |
| POOL | 15m | buy | HTF with | 942 | 497 | -0.130 (-6.4) | -0.175 (-9.7) | -0.101 | -0.141 |
| POOL | 15m | sell | HTF all | 3336 | 1391 | -0.012 (-0.7) | -0.052 (-3.7) | -0.094 | -0.134 |

All 162 rows (every tf x side x HTF x prior-day tag) are in `dev_cells.csv`.

## Reading

1. Every unmatched excess the source reported (+0.03 to +0.25 %) collapses to -0.05 .. +0.02 % once the baseline comes from bars of
   the same ATR decile, on both symbols. The "bigger bounce against the HTF / after a trend day" is the bigger bar range of those states.
2. Matched excess is mostly NEGATIVE on the all-tag cells (POOL 1m buy -0.014 %, t -8.3; 15m buy -0.080 %, t -3.5): the cross bar
   bounces slightly LESS than a random bar of the same volatility.
3. ETH behaves like BTC in every focal cell (same signs, similar sizes), so this is not a BTC-only reading.
4. Fee-net: 1 of 162 cells is above zero at 0.10 % (ETH 15m sell prior_trend HTF with, +0.026 %, t 0.3, 89 days) and none at 0.14 %.

Next: END: the WT extreme cross carries no bounce beyond volatility on BTC or ETH DEV; no target-exit PRE_REG, no layer change.
