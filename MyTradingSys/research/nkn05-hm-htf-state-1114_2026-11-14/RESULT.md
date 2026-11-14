**VERDICT: FAIL. 0 of 3 primary cells pass VAL (2024+) fee-net at 12 bp. P1 (PC, weekly HM buy) = FAIL: n 239 coin-weeks / 24 weeks, net +0.167 R but week-cluster CI low -0.264 R, placebo p 0.545, and the buy-minus-sell 4-week gap is negative (-0.063, CI low -0.196). P2 = UNDERPOWERED-WEEKS (16 weeks), P3 = UNDERPOWERED (n 64). Overall FAIL. Any PASS would have carried UNVERIFIED-HM (TradingView check not done); none occurred.**

Study: NKN-05 (weekly Hilega-Milega "red line down" = buy state, post-fall turn cell PC), run 1, `study.py run`, runtime 1242 s, `results.json`, `run1.log`. Frozen design `PRE_REG.md`; no cell, parameter or horizon changed after the run. 22 cells, 3 primary.

## Context
Order of 2026-11-14: the rule is not tested blindly; the phase is the cell, never pooled. Regime: BTC cycle state from `phase_daily.csv` at the entry-Monday row (PC = label RELIEF or ACCUM-RANGE AND cycle BEAR or BASE; BULL weeks are controls only). Look-ahead poke on real data: the file's `close_used` equals the BTC close of d-1 on 100% of 2852 rows (lag 0: 5.0%), so no label shift was applied (`phase_shift_applied` 0). One BTC label is applied to all 20 alts (stated doubt). HM formula is OURS and unverified (UNVERIFIED-HM). Prices: 20 Binance spot coins, weekly bars resampled from 15m (resampler matches `binance_spot_htf` weekly for BTC and ETH, max relative difference 0.0). Fee 12 bp round trip taker (6 bp each leg); 6 bp maker is non-gating; no funding charge.

## Regime mix (signal weeks, before any verdict)
Regime mix: BTC cycle share of signal weeks, DEV BEAR 45.0% / BASE 40.6% / BULL 14.4%; VAL BEAR 33.8% / BASE 12.8% / BULL 53.4% (six phase labels in the table).

| split | BEAR | BASE | BULL | CAPITULATION | MARKDOWN | RELIEF | ACCUM-RANGE | MARKUP | DISTRIBUTION | PC weeks (spells) |
|---|---|---|---|---|---|---|---|---|---|---|
| DEV <2024 | 45.0% | 40.6% | 14.4% | 2.4% | 25.5% | 6.1% | 20.1% | 32.9% | 12.9% | 54 (21), 26.2% of weeks |
| VAL 2024+ | 33.8% | 12.8% | 53.4% | 0.0% | 21.6% | 2.7% | 16.2% | 29.7% | 29.7% | 28 (8), 18.9% of weeks |

VAL is mostly BULL cycle, so PC is thin on VAL: 8 BTC label spells. Effective sample size is distinct weeks and spells, not coin-weeks.

## Per-phase fee-net table (trade version: stop max(0.5%, 0.6 x weekly ATR14), 4-week time exit, taker 12 bp; R per trade)
| cell | phase / state | role | DEV n | DEV wks | DEV gross R | DEV net R | DEV wk-CI low | VAL n | VAL wks | VAL gross R | VAL net R | VAL wk-CI low |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| P1 | PC, HM buy (V0) | PRIMARY | 496 | 51 | +0.062 | +0.051 | -0.322 | 239 | 24 | +0.180 | +0.167 | -0.264 |
| P2 | PC, buy + BTC > SMA20 (V1) | PRIMARY | 311 | 45 | +0.137 | +0.125 | -0.356 | 117 | 16 | -0.097 | -0.111 | -0.533 |
| P3 | PC, V1 + daily RSI14>50 and close>SMA20 (V2) | PRIMARY | 213 | 37 | +0.115 | +0.103 | -0.420 | 64 | 14 | -0.207 | -0.222 | -0.621 |
| C4 | PC, HM sell state | control | 296 | 44 | +0.533 | +0.523 | -0.026 | 181 | 22 | +0.852 | +0.839 | -0.185 |
| C6 | PC, HM neutral | control | 126 | 43 | +0.275 | +0.265 | -0.175 | 60 | 17 | -0.206 | -0.217 | -0.628 |
| C5 | PC, all weeks (placebo base) | control | 918 | 54 | +0.243 | +0.232 | -0.127 | 480 | 24 | +0.385 | +0.373 | -0.204 |
| C7 | PC, buy, BTC <= SMA20 (alts) | control | 185 | 18 | -0.065 | -0.073 | -0.583 | 122 | 14 | +0.446 | +0.434 | -0.210 |
| C1 | MARKUP, buy | control | 837 | 72 | +0.626 | +0.612 | +0.108 | 673 | 44 | +0.629 | +0.614 | -0.112 |
| C2 | MARKDOWN, buy | control | 135 | 29 | -0.039 | -0.047 | -0.326 | 76 | 25 | -0.018 | -0.029 | -0.352 |
| C3 | DISTRIBUTION, buy | control | 93 | 22 | -0.314 | -0.325 | -0.706 | 156 | 29 | +0.362 | +0.348 | -0.274 |
| R0 | all labelled phases pooled, buy | reference | 1562 | 175 | +0.334 | +0.321 | +0.014 | 1144 | 122 | +0.456 | +0.441 | -0.004 |

Controls carry no verdict and are never pooled with the primary cells. Cost is about 0.012 R per trade because the stop distance is wide; the verdict is not a fee effect.

## Primary-cell gates on VAL
| cell | verdict | DEV buy-sell | VAL buy-sell (4w ret) | ev CI low | ev ex-best-5 | ev placebo p | ev BH q | tr coin-wk CI low | tr wk-CI low | tr 4-wk-block CI low (info) | tr ex-best-5 | tr placebo p | placebo mean R | tr BH q |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| P1 | FAIL | -0.097 | -0.063 | -0.196 | -0.123 | 0.385 | 0.923 | -0.039 | -0.264 | -0.410 | -0.268 | 0.545 | +0.179 | 0.710 |
| P2 | UNDERPOWERED-WEEKS | -0.051 | -0.107 | -0.246 | -0.180 | 0.262 | 0.923 | -0.401 | -0.533 | -0.585 | -0.634 | 0.500 | -0.101 | 0.756 |
| P3 | UNDERPOWERED | -0.062 | -0.106 | -0.261 | -0.183 | 0.594 | 0.923 | -0.549 | -0.621 | -0.488 | -0.635 | 0.874 | +0.000 | 0.756 |

What the numbers say, without extrapolation:
- P1 trade net is positive (+0.167 R, T1 met) but its CI includes zero, it is below the placebo of random PC coin-weeks on the same trade rules (placebo mean +0.179 R, p 0.545), and far below the HM SELL state in the same cell (C4 +0.839 R). The event-study gap buy minus sell is negative on both DEV (-0.097) and VAL (-0.063): the claimed direction is not seen.
- Layers V1 and V2 do not help: P2 and P3 VAL net R is negative and both are thin (16 and 14 weeks).
- Level split H-A2 (weekly SMA50, AT vs AWAY, buy minus sell 4-week gap): DEV AT -0.055 vs AWAY -0.111; VAL AT -0.330 (10 buy and 40 sell weeks) vs AWAY -0.023. No positive AT-over-AWAY gap on VAL; the VAL AT cell is tiny (descriptive only).
- Fresh holdout (8 coins, run once, descriptive): P1 VAL n 84, net -0.314 R, wk-CI low -0.679, placebo p 0.789. BTC alone P1 VAL n 12 (descriptor).
- Overlap: V1 keeps 55% and V2 keeps 26% of VAL PC buy weeks.

## Verification of results.json (independent recomputation)
`run1.log` last line equals `results.json` (overall FAIL; P1 FAIL, P2 UNDERPOWERED-WEEKS, P3 UNDERPOWERED; 1242 s). I rebuilt weekly bars, HM state, ATR, PC mask, trades and fee-net R from the raw 15m files with a separate pandas implementation (not study.py code) and compared.
| number | study.py | independent |
|---|---|---|
| P1 VAL n / weeks / mean 4w ret / gross R / net12 R | 239 / 24 / -0.0104 / 0.1803 / 0.1673 | 239 / 24 / -0.0104 / 0.1803 / 0.1673 |
| P2 VAL n / weeks / net12 R | 117 / 16 / -0.1110 | 117 / 16 / -0.1110 |
| C4 VAL n / mean 4w ret / net12 R | 181 / 0.0524 / 0.8392 | 181 / 0.0524 / 0.8392 |
| P1 VAL week-cluster net CI low (5000 draws) | -0.264 | -0.283 (own seed; same sign and size) |
| P1 VAL buy-sell diff / CI low | -0.0628 / -0.196 | -0.0628 / -0.195 |
| P1 DEV n / net12 R | 496 / 0.0510 | 497 / 0.0574 |
| P2 DEV n | 311 | 312 |

VAL numbers reproduce exactly. DEV differs by one coin-week in P1 and P2 (DEV is not a gating cell; its buy-sell sign is negative either way). Regime mix and PC coin-weeks (918 DEV, 560 VAL) match. Verdict logic checked against PRE_REG: UNDERPOWERED if n VAL < 100 or fewer than 20 distinct weeks; P2 (n 117, 16 weeks) = UNDERPOWERED-WEEKS, P3 (n 64) = UNDERPOWERED, P1 is powered and fails the gates (E1 CI low < 0, E2, E3, E5, T2, T3, T4, T5, T6; E4 DEV diff < 0). P3 was not recomputed independently; its n of 64 is below the 100 floor and a subset of P2, so its verdict does not depend on the exact value.

## Deviations, limits
- No code changes after the run. `pytest test_study.py`: 18 passed.
- PRE_REG already had `## Context`, `Regime mix` and the phase-specific cell design; no amendment was needed.
- TradingView check of the weekly HM was not done (UNVERIFIED-HM would apply to any PASS).
- One BTC label for all coins; survivorship (all coins listed today); overlapping 4-week holds make coin-week n an overstatement of independent evidence; VAL is 53% BULL cycle, so PC on VAL has only 8 label spells.
- Funding split (F1-F3) and level rows (L1-L6) are descriptive and in `results.json`.
