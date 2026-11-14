**T9 weekly-trend pullback long: FAIL (first failing bar 2) KILL a_val_mean_le0+b_placebo [FRAGILE bar 7; FRAGILE bar 8; FRAGILE dev-only positive]; VAL n 103 trades / 54 weeks, net -0.035 R (CI -0.716..+0.608), DEV net +5.061 R.**

Regime mix: DEV trades by BTC smoothed state: BASE 49% BEAR 0% BULL 51% (calendar Mondays: BASE 42% BEAR 45% BULL 13%); VAL trades: BASE 10% BEAR 0% BULL 90% (calendar Mondays: BASE 14% BEAR 30% BULL 56%). BEAR is gated out by construction.

| row | DEV | VAL |
|---|---|---|
| trades | 133 | 103 |
| entry weeks | 45 | 54 |
| gross R mean | +5.246 | +0.036 |
| net R mean (primary) | +5.061 | -0.035 |
| net R mean, 3R-capped | -0.063 | -0.453 |
| fee in R (mean) | +0.008 | +0.010 |
| net % per trade (mean) | +0.7046 | -0.0395 |
| gross % per trade (mean) | +0.7470 | -0.0290 |
| net R, flat-funding sensitivity (uncovered at 1 bp per 8h) | +5.056 | -0.038 |
| week-level sd of net R | +31.683 | +3.805 |
| independent 4-week blocks | 24 | 24 |
| funding NOT_IN_DATA trades | 7 | 1 |
| net % per day in position (pooled) | +0.0163 | -0.0011 |
| bootstrap 95% CI (4-wk moving block, 2000, seed 1114) | -0.332..+14.978 | -0.716..+0.608 |
| basket net % per day (same weeks) | +0.0046 | +0.0004 |

## Pass bars (PRE_REG)

| bar | result | numbers |
|---|---|---|
| 1 power (VAL n>=30, weeks>=20) | PASS | n 103, weeks 54 |
| 2 VAL mean>0 and CI low>0 | FAIL | -0.035, CI low -0.716 |
| 3 DEV mean>0 | PASS (uncapped, outlier-driven) | +5.061 (n 133); DEV 3R-capped net -0.063 R; DOGE +425 R, ANKR +76 R, FTM +37 R |
| 4 placebo same-window | FAIL | real -0.035, draws mean -0.045, p97.5 +0.838, excess +0.010, p 0.478, rank 52.3 pct, n 103 skipped 0 |
| 4g placebo global (not a bar) | - | real -0.035, draws mean -0.149, p97.5 +0.853, p 0.290, rank 71.1 pct |
| 5 ex-best-5 weeks, 3R-capped | FAIL | -0.644 (n 96); uncapped -0.650 |
| 6 in-position net daily >= basket | FAIL | VAL strategy -0.00107 vs basket +0.00040; DEV +0.01626 vs +0.00461 |
| 7 top-3 coin removal | FAIL | AAVE: -0.248; AAVE+BCH: -0.425; AAVE+BCH+OCEAN: -0.545 |
| 8 leave-one-year-out (VAL) | FAIL | -2024: -0.648; -2025: +0.473; -2026: -0.025 ; pooled all positive: True |
| 9 rows by state and year | printed | tables.md |

Passed bars: 1, 3. Failed bars: 2, 4, 5, 6, 7, 8.
Kill criteria fired: a_val_mean_le0, b_placebo.
Holm: per-study p 0.7286; family (9 cells) worst case 1.0000.

## Robustness rows

- VAL ex-ENDED trades: -0.035; ex-LUNA/FTT coins: -0.035 (DEV: +5.061 / +5.061). Survivorship: hindsight universe, longs biased UP.
- exit reasons VAL: {'CAP': 22, 'STOP': 71, 'TREND': 10}; DEV: {'CAP': 45, 'STOP': 82, 'TREND': 6}.
- same-coin overlapping trades: 19; ENDED exits: 0; funding NOT_IN_DATA trades: 8 (zero funding charged).
- DEV-only positive flag: True. Baseline days used: {'DEV': 636, 'VAL': 717}.

Tables by year, BTC state, exit reason and coin: tables.md. Numbers: results.json.

## Adversarial check

Flag: MINOR. Final verdict: FAIL (first failing bar 2), kills a_val_mean_le0 + b_placebo; FRAGILE on bars 7 and 8; DEV-only positive.

- Checker recomputed 3 VAL trades (BCH, AAVE, TRX) from raw klines: match to better than 1e-10 relative.
- Independent full re-implementation gives the same 236 (coin, entry date) pairs; max net R relative difference 5e-11; VAL n 103 mean -0.034706, DEV n 133 mean +5.060878.
- Order clean: PRE_REG, code, tests frozen in 3f4f49cc before outcomes (ea3df0fb); only change was escaping a % in a label format string (t9_run.py line 179), no rule or parameter.
- Spec fidelity and look-ahead: no undisclosed deviation, no look-ahead found; placebo is like-for-like (103 of 103 real trades had candidates).
- Verdict re-derived from PRE_REG bars matches: failed 2, 4, 5, 6, 7, 8; kill c did not fire.
- Bar 3 PASS rests on three outlier trades and bull drift (DEV 3R-capped net -0.063 R); annotated in the bar table.
- Power: measured VAL week-level sd is 3.8 R, far above the gate's 1.0 R floor (D1), so the true MDE is larger than the printed 0.581 R and n needed is far above 93.
- Funding is NOT_IN_DATA (zero charged) for 8 trades; disclosed, flat-funding sensitivity stays negative.
