**VERDICT M2: FAIL. The maker entry fills 50% of fakeout fades and the filled trades lose -0.123 R net per trade on VALIDATION (gross -0.015 R): the limit at the broken level selects the worst fades (adverse selection -0.32 R), and the row does not beat the like-for-like placebo (p 0.42).**

Gates failed: 2 (mean net R > 0), 3 (CIs: trade [-0.202, -0.044], day [-0.214, -0.033]), 4 (placebo p 0.420), 5 (BH, worst case other rows p=1; fails regardless since p > 0.05), 6 (ex best 5 days -0.159). Gate 1 passes (n filled 1227). Not THIN (fill rate 50.1%).

## Context
Row M2 = NK3 type B fakeout fade, 1h, X1 (target 2R, time exit at close of bar +24), no blast filter, phase-fit direction (RANGE both ways, UP long, DOWN short), phase from daily ADX14+MA20 slope at D-1, exactly the original. Limit level L = the broken (fakeout) level: H of the 20-bar box for a failed up-break (fade = short, sell limit at H above the close), L for a failed down-break (buy limit below the close).

Regime mix: VAL coin-bars UP 24.8% / DOWN 35.1% / RANGE 40.1%; VAL signals RANGE 1374 / UP 513 / DOWN 561 (DEV: RANGE 1783 / UP 761 / DOWN 739). Matched direction only; no mismatched rows run.

## Baseline replication (original taker, next-open i.e. close of B+1 entry, 12 bp, all signals)
| split | n | mean net R (mine) | original RESULT | gross R (mine) |
|---|---|---|---|---|
| DEV | 3283 | -0.0122 | -0.012 (n 3283) | +0.093 |
| VAL | 2448 | -0.0337 | -0.034 (n 2448) | +0.093 |
Exact reproduction (original lib.py copied as orig_lib.py; independent re-run of its signals and sim).

## Maker model (limit at broken level, PRE_REG fill model, one 1h bar order life)
| | signals | fills | fill rate | gross R filled | net R filled | net R per signal (miss=0) | taker net R all | taker net R on filled subset | adverse sel. (orig gross filled - all) |
|---|---|---|---|---|---|---|---|---|---|
| DEV | 3283 | 1688 | 51.4% | +0.108 | +0.020 | +0.010 | -0.012 | -0.245 | -0.224 |
| VAL | 2448 | 1227 | 50.1% | -0.015 | -0.123 | -0.062 | -0.034 | -0.369 | -0.323 |

VAL exits: stop 796, target 379, time 52. Misses: 1221 no through-trade, 0 stop-before-fill. Fee R per filled trade 0.109 (maker entry 3 bp, target maker, stop taker). 1 overlapping maker position (same coin) flagged, left in.
Reading: the originals' gross +0.09 R is concentrated in the signals where price does NOT come back to the broken level; the half that does return is exactly where the fade is wrong (adverse selection -0.32 R VAL). DEV filled mean +0.020 is not significant (CI trade [-0.048, +0.088]) and flips negative on VALIDATION.

## Gates (VALIDATION)
| # | gate | value | pass |
|---|---|---|---|
| 1 | filled n >= 100 | 1227 | yes |
| 2 | mean net R > 0 | -0.1233 | no |
| 3 | CI low trade / day > 0 | -0.202 / -0.214 | no |
| 4 | placebo p < 0.05 | 0.420 (placebo mean -0.132, sd 0.039, 1000 draws) | no |
| 5 | BH q 0.05 over 6 rows | placebo p 0.420, cannot reject (computed with other five p=1; lead to recompute) | no |
| 6 | ex best-5 UTC days > 0 | -0.159 | no |

Placebo: random 1h bars, same coin, side and phase as each real VAL signal, limit at close shifted passively by an offset drawn from the real signals' (close - L) in ATR units (mean 0.47 ATR, p10 0.05, p90 1.00), stop% of the matched real signal, same simulate_maker; n filled 1227 per draw.

## Parameters
| item | value | label |
|---|---|---|
| signals, phase, box 20, width 1.5-4 ATR, fakeout test, K, X1 2R, +24 bars | as nk3 original | SOURCED (original study, itself part OURS) |
| limit level | broken level (box H / L) | OURS (PRE_REG) |
| stop distance | max(breakout-candle extreme to L, 0.6 ATR, 0.5% of L), measured from L; target 2R from L | OURS |
| fill model, fees, order life 60 x 1m | PRE_REG | OURS |

## Method notes and flags
- Only the entry-level mapping is new; nothing re-tuned. One-position-per-coin cooldown taken from the original taker exits (same signal set as the baseline); maker positions are not re-gated (1 overlap).
- Entry uses only 1m bars after the signal bar close; time exit at open of the 1m bar after close of bar e+24 (tested: TS_BARS = 25).
- Tick estimated per symbol from 1m data. Same-bar fill and stop resolve to stop; fill bar may credit the target (lib default fill_bar_target=True).
- Data: 15m from F:\MTS\data_cache\binance_spot (the original's cache); 1m from F:\MTS\data_cache\binance_1m.
- An earlier run mistakenly excluded blast-bar signals (n 1634) and was discarded; the baseline mismatch exposed it, the final numbers above use the original's all-signals set.
- Tests: test_study.py, 6 pass; the touch-fill test fails for a naive fill-on-touch variant (tick=0), and a pre-signal-bar fill test fails if earlier bars are read.
- Independent checker not run here (lead's job).
