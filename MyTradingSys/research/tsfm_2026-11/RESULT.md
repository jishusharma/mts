# RESULT tsfm-zero-shot-vs-analog: Chronos-Bolt-small zero-shot on BTC perp 4h/8h, DEV 2022-01-01..2024-06-30

Verdict: FAIL on 4h, INCONCLUSIVE on 8h (frozen rule, PRE_REG.md, one run, DEV only). No fee-net edge. FAIL means stop: Chronos-Bolt-small zero-shot (ctx 256, horizon 1 bar, long if median forecast > 14 bp) as a fee-net long signal on BTC 4h and 8h DEV 2022-01..2024-06; it says nothing about TimesFM (not run), shorts, other horizons or 2024-07+ data.

Run: `<venv python> MyTradingSys/research/tsfm_2026-11/run_tsfm.py --split DEV` (venv outside repo; torch 2.15.0+cpu, chronos-forecasting 2.3.2). Raw: results.json. Cost 14 bp RT subtracted per trade; HOLDOUT/VALIDATION never loaded (splits.assert_dev_only).

## Verdict arms
| arm | n | mean net % | se | cost | verdict |
|---|---|---|---|---|---|
| Chronos long 4h | 1921 | -0.1084 | 0.0207 | 0.14 | FAIL |
| Chronos long 8h | 1073 | -0.0913 | 0.0496 | 0.14 | INCONCLUSIVE |

(se = half-width of the week-block bootstrap CI / 1.96.)

| bar | forecast bars | trades | hit | net R/trade [95% CI] | net %/trade [CI] | always-long net % | random-bars net % (p) | verdict |
|---|---|---|---|---|---|---|---|---|
| 4h | 5216 | 1921 | 0.420 | -0.097 [-0.133, -0.061] | -0.108 [-0.148, -0.068] | -0.132 | -0.132 (0.128) | FAIL |
| 8h | 2480 | 1073 | 0.432 | -0.058 [-0.122, +0.003] | -0.091 [-0.192, +0.005] | -0.126 | -0.125 (0.171) | INCONCLUSIVE |

## Calibration (1-bar log-return quantiles, 9 levels)
| bar | mean pinball Chronos | pinball Gaussian (trailing sd) | 80 % interval coverage (target 0.80) |
|---|---|---|---|
| 4h | 0.003254 | 0.002984 | 0.868 |
| 8h | 0.004596 | 0.004233 | 0.873 |

- Chronos pinball is 9 % worse than a zero-drift Gaussian with trailing sd on both bar sizes; its 80 % interval covers 87 % (too wide, under-confident).
- The long flag beats "always long" by about 0.02-0.03 pp but is no better than random bars (p 0.13 / 0.17, Holm threshold 0.05/108 = 0.00046): the apparent edge is the 14 bp round trip minus a negative drift period.
- Both runs have n above the 519-trade power line; the 4h CI is entirely below zero.
- Side by side: F3 (1h analogs) and F4 (8h look-alikes) also found no edge (F4: 28-36 trades, INCONCLUSIVE/FAIL); the foundation model shows the same null with 30-60x more trades.

## Decisions (OURS)
- TimesFM not run (extra install and weights; time-box). Only Chronos-Bolt-small.
- Shuffle control implemented as random-bar draws of the same trade count (equivalent to permuting the flags, long only); direction-random control omitted (no shorts in rule).
- R = net log return / DEV sd of 1-bar log return of that bar size.
- F3/F4 not re-run; compared by published verdicts.
