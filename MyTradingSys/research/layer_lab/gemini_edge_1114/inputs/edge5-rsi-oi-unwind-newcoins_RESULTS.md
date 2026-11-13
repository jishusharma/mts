# RESULT: RSI-extreme OI-unwind and dADX cells on 40 new coins (edge5-rsi-oi-unwind-newcoins-1113)

**Verdict: A FAIL, B UNDERPOWERED (and FRAGILE), C UNDERPOWERED (and negative). No cell passes. The parent's two layer cells do not carry over to new coins.**

Pre-reg: PRE_REG.md (committed 7145d9708 before any outcome). Code: fetch.py, study.py, rsi_grid_lib.py (parent, unchanged), test_study.py (3 pass). Data: Bybit v5, 40 USDT perps (all 40 produced klines and OI), 1h history from each coin's listing (2021-05 to 2026-11), last trade entry 2026-11-05 (7 day forward window). Cost per trade: 2 x 5 bp taker + 2 bp slippage = 12 bp round trip, charged on entry and divided by stop distance. Exit +2R, 72 h cap, stop first on ambiguous bars. The whole new-coin set is the test set.

Regime mix: BTC daily close vs 200d SMA (bull > +5 %, bear < -5 %), from the parent: 2020-2023 bull 51 % / bear 40 % / range 10 %; 2024-now bull 56 % / bear 30 % / range 15 %. New coins list mostly 2023-2025, so 87 % of cell A trades are 2024+ (199 of 270) and the 2021-2023 bear/range share is thin (71 trades).

| cell | n | days | win% | base mean R | cell mean R net | trade CI | day CI | placebo p | per-year (n, mean R) | without best 5 days | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A: 1h, OI 24h <= -3 %, +2R | 270 | 149 | 42.6 | -0.004 (1h base n 738, win 39.3) | +0.025 | [-0.131, +0.188] | [-0.195, +0.254] | 0.321 | 2021 6, +0.65; 2022 25, -0.30; 2023 40, -0.21; 2024 62, -0.01; 2025 68, +0.26; 2026 69, +0.03 | best 5 days = 587 % of total R (total R tiny); without them n 239, -0.139 | FAIL |
| B: 4h, daily ADX 20-25, +2R | 41 | 30 | 58.5 | +0.050 (4h base n 226, win 47.3) | +0.214 | [-0.135, +0.576] | [-0.127, +0.577] | 0.168 | 2022 2, +1.03; 2023 5, +0.42; 2024 10, +0.02; 2025 18, +0.19; 2026 6, +0.17 | best 5 days = 123 % of total R; without them n 34, -0.060 | UNDERPOWERED (n < 60, days < 40), FRAGILE |
| C: A and US session (13-20 UTC open) | 98 | 61 | 33.7 | -0.004 | -0.141 | [-0.397, +0.136] | [-0.492, +0.206] | 0.851 | 2021 3, +0.91; 2022 4, -1.09; 2023 15, -0.60; 2024 26, -0.18; 2025 22, -0.05; 2026 28, +0.09 | n 82, -0.434 (best-5 share undefined: total R <= 0) | UNDERPOWERED (n < 100), negative |

2024-onward means: A n 199, +0.095; B n 34, +0.136; C n 76, -0.043. Unfiltered 2024-onward base: 1h +0.027, 4h +0.110. Day-cluster one-sided p (share of resampled means <= 0): A 0.445, B 0.111, C 0.800; Bonferroni threshold 0.0167, none met.

OI coverage: every coin's OI history starts at its kline listing date (2021-05 AAVE ... 2025-11 JCT/PIEVERSE); 1 of 738 1h base signals lacked OI. Cell A reached 38 coins, B 22 coins, C 32 coins.

Reading: cell A is the parent's candidate (parent n 180, +0.24R before slippage); on new coins it shrinks to +0.025R with a CI centred near zero and a mean of -0.14R once the five best days are removed, i.e. no edge once costs are paid. B's +0.21R rests on 41 trades and turns negative without its best 5 days; underpowered, not evidence. C (the extra US-session filter) is worse than the base. Every 1h cell is within noise of the unfiltered 1h rule (-0.004R). Limits as pre-registered: survivorship of the turnover-ranked universe, no funding, flat 2 bp slippage (small coins likely worse), overlapping trades across correlated coins.
