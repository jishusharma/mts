# F4 RESULT: 8h look-alikes of the operator setup (BB squeeze-break + volume spike, RSI, StochRSI, CVD proxy), BTCUSDT spot

Pre-reg: f4/PRE_REG.md (commit 669a9b9d4, before the run). Run: `python MyTradingSys/research/fractals_2026-10-31/f4/run_f4.py <dir of BTCUSDT-1h-YYYY-MM.csv>` (output f4/output.md, trades f4/events.csv, percent only).
Window: Binance spot 1h klines 2017-08-17..2025-06-30 built into 8,584 complete 8h bars (5,705 valid signal bars); HOLDOUT 2025-07+ never loaded. All costs fees.BINANCE_TAKER both legs.

**Verdict: no tradable edge. No set passes the frozen rule. Continuation short is INCONCLUSIVE (about zero after fees), fade long FAILS (CI upper < 0 at all 3 horizons), the ANALOG selection is negative at 6 and 9 bars.** Honest negative; the samples (28-36 trades) are far too small to prove or rule out a 0.10 R edge.

| set | h (bars) | n | hit | net R/trade | month-boot 95% CI | half A / B | B1 random-matched-vol mean (p, Holm p) | verdict |
|---|---|---|---|---|---|---|---|---|
| RULE continuation short | 3 | 36 | 0.47 | +0.109 | [-0.18, +0.42] | +0.29 / -0.08 | -4.97 (0.041, 0.37) | INCONCLUSIVE |
| RULE continuation short | 6 | 36 | 0.42 | -0.115 | [-0.43, +0.20] | +0.08 / -0.31 | -4.97 (0.21, 1.0) | INCONCLUSIVE |
| RULE continuation short | 9 | 36 | 0.31 | -0.138 | [-0.48, +0.22] | +0.21 / -0.49 | -4.97 (0.24, 1.0) | INCONCLUSIVE |
| RULE fade long | 3 / 6 / 9 | 36 | 0.31 / 0.25 / 0.28 | -0.475 / -0.506 / -0.471 | upper -0.06 / -0.08 / -0.03 | both halves negative | -5.6 (p 0.81-0.85) | FAIL x3 |
| ANALOG (k = 20 neighbours choose side) | 3 | 33 | 0.42 | +0.020 | [-0.42, +0.39] | +0.02 / +0.02 | -5.30 (0.126, 1.0) | INCONCLUSIVE |
| ANALOG | 6 | 28 | 0.32 | -0.560 | [-1.23, +0.07] | -0.67 / -0.45 | -5.99 (0.83, 1.0) | NOT_DECIDABLE (n < 30) |
| ANALOG | 9 | 29 | 0.31 | -0.504 | [-1.27, +0.18] | +0.04 / -1.01 | -6.50 (0.79, 1.0) | NOT_DECIDABLE (n < 30) |

- RULE events: only 36 in 7.9 years (2 to 7 per calendar year). ANALOG: 306 breakdown-close queries, 104 answered (library >= 200 and 20 spaced neighbours), 28-33 trades after "the neighbours' better side must have mean net R > 0" and non-overlap.
- Power: sd of net R is 0.84-1.74, so 0.10 R needs 550-2,400 trades per set (harness.power_n). This study has 28-36. Everything is descriptive + forward log (d-flexible-min-n-per-case).
- B2 (random breakdown-close bars, same stop rule): mean -0.08 to -0.39 R. RULE continuation at 6 bars (-0.115) is no better than a random breakdown bar (p 0.52).
- Split A/B signs flip for continuation at 3, 6 and 9 bars: noise-sized.

**Deviation to read before trusting the B1 column.** B1 (the card's random-window baseline) is measured in R and the stop is the signal bar's own high/low. On a random bar that stop is often a few ticks away, so 1R is tiny and those trades have huge negative R (mean about -5 R). B1 in R is therefore not a usable null (it flatters every set) and the frozen Holm column inherits that. The frozen verdicts above do not depend on it: no set reaches PASS because the bootstrap CI includes zero or the halves disagree. I added one POST-HOC control, labelled in output.md and not in the pre-reg: the same random matched-vol draws in net % of entry. RULE continuation at 3 bars: +1.08 % per trade vs -0.125 % random (p 0.000); at 6 bars +0.07 % vs -0.13 % (p 0.25); at 9 bars +0.22 % vs -0.13 % (p 0.14); ANALOG p 0.30 / 0.97 / 0.88. The only hit is the 3-bar continuation in percent, n 36, chosen after seeing the data and not risk-matched (breakdown bars have wide stops): a lead for the forward log, not an edge.

## Splits (h = 6, descriptive, output.md)
- Phase (cowen_side x sma200_side, wsma10_phase, dd_bin; cycle_year listed only), family-wise harness.shift_null_test per labelling. RULE continuation: nothing flagged (p 0.51 / 0.17 / 0.24); below|below -0.31 R, deep drawdown -0.40 R. RULE fade: wsma10_phase flags below_down (-1.21 R, n 14, p 0.001), i.e. fading a breakdown under a falling weekly SMA10 loses; cowen and dd_bin not flagged. ANALOG: nothing flagged. It is the losing side of a rule that already fails, n 14: not a trading rule.
- Layers (entries 2022+, n 20 / 20 / 28): RSI-DIV-MTF fired in the 24 h before the signal: continuation -0.29 R (n 6) vs -0.23 (n 14); fade -1.16 vs -0.39; ANALOG -0.74 (n 9) vs -0.48 (n 19). Hurst regime cells hold 2-16 trades each (continuation H > 0.55: +0.73, n 2). Nothing decidable. Analyst-level proximity: NOT RUN, no point-in-time DEV list exists. OI: forward-logged only, never used.

## Decisions (OURS)
- DECISION: 1h klines from data.binance.vision (public) instead of the 1m store, because F:/MTS is absent on this host; same taker-buy column, 2017-08 on. Files kept outside the repo.
- DECISION: entry at the open after the signal bar, 1h-bar stop/target walk, stop first on a tie, no slippage (optimistic for stops).
- Caveats: vol-quintile edges for the baseline use all valid bars (full sample); one k, one L, one threshold set, no tuning.
- Tests: f4/test_f4.py (6; failed before f4lib.py existed): causal truncation of features, CVD proxy by hand on 3 bars, trade simulator by hand, RULE detector, planted +0.3 R shift detected and null not.
