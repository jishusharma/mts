Verdict: T13=INCONCLUSIVE (DEV screen failed: slope +1.04 net R per score point, day-clustered SE 0.99, 95 % CI -0.91..+2.99, n=13851; score >= 3 group n=410, mean net R -0.163 +-0.087; VALIDATION not read)

## Answer in plain words
Stacking the operator's reasons does not make a fee-net fade at a 1h/4h swing level pay. More reasons do slightly better: the score >= 3 group loses 0.16 R per trade, against 0.31-0.34 R for scores 0-2. But every score level up to 3 loses money after fees. The pre-registered slope is positive, but its CI is very wide and includes 0. One BTC 1h event on 2024-06-07 drives that slope: score 0, a 0.001 bp stop, and fee_r of 8604 R. The slope therefore says nothing about confluence. The second screen condition (score >= 3 mean net R > 0) fails on its own: -0.163, CI -0.334..+0.008. The trial is not screened in, so VALIDATION was never loaded. It is INCONCLUSIVE, not FAIL, because the rule calls FAIL only for a DEV slope <= 0. Score 4 (n=37) is the only positive cell (+0.27 R, CI -0.35..+0.89), and that n is far too small to mean anything. Next step: END for this trial. A wider-stop or maker-entry stack is a new hypothesis for a new wave, not a re-cut of T13.

## Count pass (DEV, before any return; `python confluence_score.py count`)
Events at level touches: 13862 (BTC 1h 6218, BTC 4h 1117, ETH 1h 5454, ETH 4h 1073).

| Score | 0 | 1 | 2 | 3 | 4 | 5 | >= 3 |
|---|---|---|---|---|---|---|---|
| DEV events | 3857 | 6730 | 2865 | 370 | 37 | 3 | **410** (>= 30: the trial is testable) |

Layer firing rate: S1 sweep 36.2 %, S2 line confluence 5.0 %, S3 divergence 14.0 %, S4 RSI-MA trigger 7.1 %, S5 HTF 36.8 %.

Events per year and side (short / long): 2017 325/258, 2018 812/926, 2019 1028/1010, 2020 1180/859, 2021 902/879, 2022 991/1054, 2023 1337/1211, 2024 (H1) 583/507.

Regime mix: 358 weeks: bull 72 (20%) | bear 0 (0%) | range 223 (62%) | n/a 63 (18%) (research_kit.regime_tag, BTC, DEV weeks 2017-08..2024-06; n/a = SMA200/monthly RSI warm-up; 0 bear weeks is the known label gap, PLAN s1).

## DEV primary test (T13): OLS of net R on score, SE clustered by UTC day (2459 days)
| n | intercept | slope | SE | 95 % CI | one-sided p | MDE (80 %) | screen |
|---|---|---|---|---|---|---|---|
| 13851 | -1.99 | +1.037 | 0.995 | -0.913..+2.987 | 0.149 | 2.79 | FAIL (CI lower <= 0; score >= 3 mean < 0) |

Censored: 10 trades past the DEV end, 1 event with stop distance 0 (skipped). Exits: stop 9770, target 3314, time 767. Stop width p10/p50/p90: 25 / 64 / 200 bps.

## DEV cells (score_cells.csv; R per trade)
| Cut | n | hit (net>0) | gross R | fee_r | funding R | net R | SE | 95 % CI | MDE |
|---|---|---|---|---|---|---|---|---|---|
| all | 13851 | 0.280 | -0.076 | 0.886 | -0.003 | -0.959 | 0.622 | -2.18..+0.26 | 1.74 |
| score=0 | 3854 | 0.272 | -0.077 | 2.532 | -0.005 | -2.604 | 2.234 | -6.98..+1.77 | 6.26 |
| score=1 | 6722 | 0.276 | -0.083 | 0.260 | -0.002 | -0.341 | 0.021 | -0.38..-0.30 | 0.06 |
| score=2 | 2865 | 0.291 | -0.080 | 0.231 | -0.001 | -0.310 | 0.031 | -0.37..-0.25 | 0.09 |
| score=3 | 370 | 0.319 | +0.042 | 0.245 | -0.005 | -0.198 | 0.088 | -0.37..-0.03 | 0.25 |
| score=4 | 37 | 0.405 | +0.432 | 0.161 | +0.002 | +0.270 | 0.314 | -0.35..+0.89 | 0.88 |
| score=5 | 3 | 0.000 | -1.000 | 0.159 | +0.005 | -1.165 | 0.043 | - | - |
| **score>=3** | 410 | 0.324 | +0.070 | 0.237 | -0.004 | **-0.163** | 0.087 | -0.334..+0.008 | 0.24 |
| tf=1h | 11664 | 0.282 | -0.069 | 1.023 | -0.002 | -1.090 | 0.739 | -2.54..+0.36 | 2.07 |
| tf=4h | 2187 | 0.270 | -0.112 | 0.154 | -0.006 | -0.260 | 0.035 | -0.33..-0.19 | 0.10 |
| short | 7151 | 0.271 | -0.087 | 1.497 | -0.013 | -1.571 | 1.203 | -3.93..+0.79 | 3.37 |
| long | 6700 | 0.289 | -0.065 | 0.233 | +0.008 | -0.306 | 0.025 | -0.35..-0.26 | 0.07 |

Per year (DEV): net R 2017 -0.213 (n 583), 2018 -0.341 (1737), 2019 -0.335 (2038), 2020 -0.350 (2039), 2021 -0.275 (1781), 2022 -0.362 (2045), 2023 -0.369 (2548), 2024H1 -8.33 (1080; the 8604 R fee outlier). Every year is negative. The per-year slope is positive in 2018-2021 (2021: +0.151, CI +0.045..+0.258) and negative in 2017, 2022 and 2023.

## Exploratory (cannot promote)
- Leave-one-layer-out slopes (net R): drop S1 +0.95, S2 +1.08, S3 +1.05, S4 +1.08, S5 +0.85; every CI includes 0. All of them carry the same outlier.
- Per TF slope: 1h +1.23 (SE 1.20); 4h +0.074 (SE 0.043, CI -0.010..+0.158). Per symbol: BTC +1.91 (SE 1.85), ETH +0.023 (SE 0.028). Per side: short +1.89 (SE 1.88), long +0.078 (SE 0.029, CI +0.021..+0.135).
- `python confluence_score.py explore`. The slope on GROSS R (no costs) is +0.015 (SE 0.019, CI -0.022..+0.052). Before fees, the score barely moves the outcome. With stops of 25 bps or more (cut chosen after seeing the outlier, so exploratory only), the net slope is +0.047 (SE 0.020, CI +0.008..+0.087). Most of that comes from fee_r falling as the score rises (0.21 -> 0.14 R), because high-score events have wider stops. It is not a better hit rate. Even then score 3 nets -0.024 R (n=332) and score 4 nets +0.37 R (n=35, CI -0.26..+1.00).
- Largest fee_r events: BTC 1h 2024-06-07 11:00 (score 0, stop 0.001 bp, fee_r 8604); BTC 1h 2019-05-05 20:00 (0.38 bp, 31.7); ETH 1h 2018-10-02 09:00 (0.44 bp, 27.4).

## Context
- Regime: none as a gate (all regimes pooled). Regime mix line above (research_kit.regime_tag).
- Phase: none as a gate. S5 (daily/weekly RSI turning at 60/40) is the only HTF layer, and it is scored, not gated.
- Session: none, because 1h/4h touches are taken around the clock.
- Entry: signal bar, at the close of the event bar (taker). No retest.

## Method and data
- Data: Binance spot klines, BTCUSDT and ETHUSDT 1h and 4h, 2017-08-17..2024-06-30, from the shared cache F:/MTS/Dumps/backtest/spot_2017 (outside the repo). 12h and 1d are resampled from 1h, and 1w from 1d (Monday 00:00 UTC). A resampled value is used only at or after its period end (test_resample_and_asof_no_lookahead). HOLDOUT was never loaded. The loader refuses any month past the split end (test_split_refusal, test_loader_drops_rows_past_split_end).
- Costs: regime A = 2 x fees.BINANCE_TAKER + fees.SLIPPAGE_RT_S13 = 12 bps round trip, fee_r = 0.0012 / stop fraction. Funding comes from the USD-M fundingRate archive (eh_s3_conf cache; data.binance.vision returned 404 for 2019-09..2019-12, so funding is **0 before 2020-01**, not 2019-09). A short receives positive funding.
- Wave-2 inputs: the eh-s1, eh-s3 and eh-h5 results had not shipped. The layers were implemented from their brief text (PRE_REG "Layer definitions"). I saw none of their DEV results.
- Tests: the first run, before the code existed, ended with `1 error in 0.57s` (ModuleNotFoundError: confluence_score). The final run passes: `30 passed`.

## DECISION (OURS) list
1. Every fill listed in PRE_REG "OURS fills" (pivot ties, level death on a close, nearest-level choice, S3 recency of 6 bars, S5 "falling" reading, stop = max(6-bar extreme, level), overlap allowed, Holm at the strictest step 0.05/15).
2. Verdict wording: the slope is positive but the screen failed, so the rule gives INCONCLUSIVE, not FAIL. The fee outlier is reported, not removed: the frozen rule has no stop floor (PLAN s5 "no floor").
3. Funding starts 2020-01 (archive availability), not 2019-09 as the brief assumed.
4. The `explore` mode (gross-R slope, stop >= 10/25 bps cuts) was added after the DEV run. It is labelled exploratory and cannot promote.
5. No VALIDATION read: dev_screen.json records screen=false, and `val` mode refuses to run.

## Noticed
- The brief's stop rule ("extreme of the last 6 bars beyond the level", no floor) produced stops down to 0.001 bp on 1h. One event with fee_r 8604 R swamps any OLS on net R. A dose-response test on net R needs a stop floor or a median/robust slope fixed in advance. A later wave should pre-register that.
- The score is confounded with stop width: high-score events (sweeps, divergences) have wider stops, so fee_r falls with the score even though gross R barely changes.
- The fetch_binance_archive.py call with `--symbols BTCUSDT,ETHUSDT --datasets fundingRate` wrote only the BTC files. A second ETH-only call reported "skip 66" and wrote nothing, so ETH funding was read from the eh_s3_conf cache.
