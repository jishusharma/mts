# RSI deep-buy Step H: layer confluence at the RSI low (card rsi-deep-confluence, SPEC s2 Step H, SHOT_REVIEW C5)

STATUS: vote table below was written BEFORE any outcome was computed (no confluence number existed when it was saved). Results are under "Result" at the end.

## Pre-registered vote table (one rule per voter, no tuning on outcomes)

Event = the Step F event (RSI14 of the event TF closes at or below level L in 10..40 step 5 after being 3+ above; fill = next bar open; known at the signal-bar close). Same-TF vote = the voter on the event TF at the signal bar. Higher-TF vote = the voter on each of the next TWO timeframes up the ladder 1m, 5m, 15m, 1h, 4h, 1d, read on the LAST COMPLETED bar at the signal-bar close time only. A voter value is +1 (long support), 0 (reading, no signal), -1 (against a long), or NA (not reporting: warm-up). NA is never turned into 0; an event is scored only when every voter of the scheme reports.

| id | layer (source) | where | rule | +1 | -1 | label |
|---|---|---|---|---|---|---|
| V_RSI | RSI family, higher-TF state band (`layers/rsi`, FORMULAS s1; rsi_series warm-up 200) | higher TFs only (the same-TF RSI is the event itself) | RSI14 of the last completed bar | <= 30 | >= 50 | bands OURS |
| V_BB | Bollinger position (FORMULAS s22: n=20, mult=2, population sd) | same + higher | close of the last completed bar vs bands | close < lower | close > upper | SOURCED defaults |
| V_KUR | Kurisko quad stochastic turn from oversold (`layers/kurisko/quad_rotation.py`, stoch (9,3),(14,3),(40,4),(60,10), level_lo from params) | same + higher | a long quad-rotation event stamped on any of the last 3 completed bars of that TF | event present | never (short mirror is NO-SOURCE) | 3 bars OURS |
| V_TAK | Positioning: taker-buy share of the bar (taker_buy_volume / volume, 1m tape columns) | same + higher | z of the last completed bar's share vs the previous 200 bars of that TF (mean and population sd of the 200 bars before it) | z >= 1 | z <= -1 | cut 1 and 200 OURS |
| V_SWP | Session levels: prior UTC day low/high swept and reclaimed (`layers/session_levels`, day levels) | same + higher | last completed bar vs the previous completed UTC day (prior-day low PDL, high PDH) | low < PDL and close > PDL | high > PDH and close < PDH | OURS |
| V_DIV | Divergence on the next TF up (SHOT_REVIEW C5): causal pivot divergence on RSI14 | HIGHER TFs only | close pivot confirmed 3 bars later (stamp = pivot + 3), adjacent-pivot pairing (P-adj; the P-anchor primary needs the episode machinery of Step I), price lower low with RSI higher low = bullish, price higher high with RSI lower high = bearish; adjacent pivots at most 100 bars apart; the most recent stamp within the last 20 completed bars of that TF decides | bullish | bearish | 3 bars, 20 bars OURS |

Voter count: 6 (cap 8). TFs: the event TF plus two above (cap 3).

## Layers with no usable bar-by-bar causal history here (listed, not zero-filled)

| layer | status |
|---|---|
| WaveTrend cross / oscillator agreement count (RSI, StochRSI, WaveTrend, SHOT_REVIEW C5) | NOT_IN_DATA until `wavetrend-data-inference` pins its inputs |
| Trendline / pitchfork support touch | NOT_IN_DATA (detectors are event/live modules; no stamped bar-by-bar history output) |
| Turn-of-candle, CryptoCred setups, Krown, wlow_bounce | NOT_IN_DATA (no stamped bar-by-bar history output; not replayed here) |
| Tom / Fabio order-flow layers | NOT_IN_DATA (Tom core BTC encoding STOPPED; Fabio needs trade-level data not on the kline tape) |
| Funding, open interest | NOT_IN_DATA (not on the 1m tape; OI forward-collected only) |
| Malkan 40/60 reclaim, StochRSI | not selected (voter cap; reclaim is an event table, not a per-bar state) |

## Scores and schemes (pre-registered)

- Same-TF score S = sum of the same-TF votes (V_BB, V_KUR, V_TAK, V_SWP; range -3..4). 4 buckets: S <= -1 -> 0; S = 0 -> 1; S = 1 -> 2; S >= 2 -> 3.
- Higher-TF score H = sum of all higher-TF votes over both TFs and 6 voters (range -12..12). 4 buckets: H <= -1 -> 0; 0 -> 1; 1..2 -> 2; >= 3 -> 3.
- Total T = S + H, buckets as H.
- Coverage = number of voters reporting; only full-coverage events are scored.
- Schemes (15): C_same, C_high, C_all; ADD1_<v> for each of the 6 voters (that voter's sum over its TFs, 3 states: <0, 0, >0); DROP1_<v> (T without voter v, buckets as T). Equal weights; no learned weights.
- Tests: 15 schemes x 4 RSI TF (1m, 5m, 15m, 1h) x 2 outcomes (price > fee at 60 min; RSI bounce b5 d3 within 60 bars) = 120, Holm over all 120.
- Predictor = Step F machinery: F0 = level-only walk-forward (k+1)/(n+2); a score cell (scheme, state, tf, level) is shrunk to F0 by empirical Bayes (m from DEV), cell with < 30 distinct past days returns F0. Keep rule: DEV delta log-loss > 0 and Holm p < 0.05, then VALIDATION delta > 0 (read once).
- Fee-net EV per day: per event net = open[fill+60 min] / open[fill] - 1 - 0.10%; per bucket: events, events per calendar day, mean net bps, EV per day (sum of net over events / calendar days of the period), against the level-only row (all scored events of the same TF and level).
- Questions answered: (1) monotonic in score? (bucket table), (2) layer moving odds most (ADD1 and DROP1 deltas), (3) higher vs same (C_high vs C_same), (4) a score above which EV is positive net (top bucket vs level-only), (5) mirror for highs: NOT RUN (exploratory per SPEC, does not block).
- Windows: DEV events open < 2024-07-01 (labels from 2023-01 for the Step F schemes are not used here; warm-up drops 2022 H1 where 4h/1d RSI is NA); VALIDATION events 2024-07-01..2025-06-30; HOLDOUT never read.

## Result

Data: BTCUSDT 1m. DEV = bar open < 2024-07-01 (`confluence_dev.csv`, written and frozen first, sha256 `a62f02e6bfef6a1e`). VALIDATION = events 2024-07-01..2025-06-30, read once (`confluence_val.csv`); its parameters (m, candidate list) come from the frozen DEV file. HOLDOUT (2025-07 onward) is refused by the loader and was never read. Generated by `confluence.py`; test: `test_confluence.py`. Descriptive, not a trading rule; the net-EV columns are an in-sample bucket description, not a fee-net edge claim.

**10 of 120 pre-registered confluence tests are kept** (DEV: delta log-loss > 0 and Holm p < 0.05 over all 120; then VALIDATION delta log-loss > 0). DEV candidates: 16. Everything else: level-only F0 is the answer.

delta = mean log-loss of level-only F0 minus mean log-loss of the score-conditioned prediction per scored event (positive = score better). t over distinct days; p_holm over the full grid.

### DEV candidates and their VALIDATION result

| RSI TF | outcome | scheme | DEV events | DEV days | DEV delta | DEV t | DEV p_holm | VAL delta | VAL t | verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| 1m | price | ADD1_V_BB | 90148 | 906 | +0.00045 | 3.80 | 0.0078 | -0.00006 | -0.30 | drop |
| 1m | price | ADD1_V_KUR | 90148 | 906 | +0.00037 | 3.53 | 0.0219 | +0.00019 | 0.79 | keep |
| 1m | price | ADD1_V_RSI | 90148 | 906 | +0.00314 | 7.76 | 0.0000 | +0.00010 | 0.15 | keep |
| 1m | price | C_all | 90148 | 906 | +0.00255 | 7.91 | 0.0000 | +0.00052 | 0.81 | keep |
| 1m | price | C_high | 90148 | 906 | +0.00259 | 7.76 | 0.0000 | +0.00050 | 0.75 | keep |
| 1m | price | DROP1_V_BB | 90148 | 906 | +0.00175 | 7.02 | 0.0000 | +0.00033 | 0.62 | keep |
| 1m | price | DROP1_V_DIV | 90148 | 906 | +0.00215 | 7.25 | 0.0000 | +0.00022 | 0.39 | keep |
| 1m | price | DROP1_V_KUR | 90148 | 906 | +0.00244 | 7.73 | 0.0000 | +0.00049 | 0.80 | keep |
| 1m | price | DROP1_V_RSI | 90148 | 906 | +0.00133 | 6.17 | 0.0000 | +0.00033 | 0.73 | keep |
| 1m | price | DROP1_V_SWP | 90148 | 906 | +0.00246 | 7.71 | 0.0000 | +0.00053 | 0.84 | keep |
| 1m | price | DROP1_V_TAK | 90148 | 906 | +0.00326 | 7.79 | 0.0000 | +0.00035 | 0.47 | keep |
| 5m | price | ADD1_V_KUR | 16666 | 899 | +0.00018 | 3.76 | 0.0093 | -0.00012 | -1.74 | drop |
| 5m | rsi | ADD1_V_SWP | 16666 | 899 | +0.00015 | 3.91 | 0.0052 | -0.00016 | -1.84 | drop |
| 5m | rsi | C_all | 16666 | 899 | +0.00016 | 3.33 | 0.0464 | -0.00017 | -1.47 | drop |
| 5m | rsi | DROP1_V_BB | 16666 | 899 | +0.00025 | 3.61 | 0.0167 | -0.00028 | -1.90 | drop |
| 5m | rsi | DROP1_V_KUR | 16666 | 899 | +0.00020 | 3.82 | 0.0073 | -0.00019 | -1.48 | drop |

### Same-TF score vs higher-TF score vs total (price outcome; positive delta = better than level-only)

| RSI TF | scheme | DEV delta | DEV t | VAL delta | VAL t |
|---|---|---|---|---|---|
| 1m | C_same | +0.00010 | 1.36 | -0.00003 | -0.27 |
| 1m | C_high | +0.00259 | 7.76 | +0.00050 | 0.75 |
| 1m | C_all | +0.00255 | 7.91 | +0.00052 | 0.81 |
| 5m | C_same | +0.00004 | 0.85 | +0.00007 | 0.45 |
| 5m | C_high | +0.00021 | 2.39 | +0.00017 | 0.82 |
| 5m | C_all | +0.00014 | 2.14 | -0.00003 | -0.21 |
| 15m | C_same | -0.00004 | -0.61 | -0.00008 | -0.55 |
| 15m | C_high | +0.00005 | 0.63 | -0.00026 | -1.59 |
| 15m | C_all | -0.00003 | -0.48 | -0.00013 | -0.95 |
| 60m | C_same | -0.00001 | -0.45 | -0.00001 | -0.19 |
| 60m | C_high | +0.00001 | 0.40 | +0.00006 | 0.62 |
| 60m | C_all | +0.00000 | 0.08 | +0.00006 | 0.69 |

### Add-one and drop-one by layer (price outcome, delta log-loss vs level-only)

ADD1 = the layer alone (its votes summed over the 3 TFs, 3 states); DROP1 = total score without the layer. A layer moves the odds most when its ADD1 delta is highest and its DROP1 delta falls furthest below C_all.

| layer | DEV 1m | VAL 1m | DEV 5m | VAL 5m | DEV 15m | VAL 15m | DEV 60m | VAL 60m | mean DEV |
|---|---|---|---|---|---|---|---|---|---|
| ADD1 V_RSI | +0.00314 | +0.00010 | +0.00046 | +0.00037 | +0.00001 | -0.00001 | -0.00002 | +0.00002 | +0.00090 |
| ADD1 V_BB | +0.00045 | -0.00006 | +0.00000 | -0.00003 | -0.00006 | +0.00024 | -0.00003 | +0.00003 | +0.00009 |
| ADD1 V_KUR | +0.00037 | +0.00019 | +0.00018 | -0.00012 | -0.00005 | -0.00005 | +0.00001 | +0.00005 | +0.00013 |
| ADD1 V_TAK | +0.00002 | -0.00005 | -0.00008 | -0.00021 | -0.00007 | -0.00002 | -0.00003 | -0.00004 | -0.00004 |
| ADD1 V_SWP | +0.00019 | -0.00016 | +0.00002 | +0.00015 | -0.00002 | +0.00004 | -0.00004 | +0.00000 | +0.00004 |
| ADD1 V_DIV | +0.00075 | +0.00038 | -0.00004 | +0.00006 | +0.00009 | -0.00002 | -0.00001 | -0.00002 | +0.00020 |

| layer | DEV 1m DROP1 minus C_all | DEV 5m DROP1 minus C_all | DEV 15m DROP1 minus C_all | DEV 60m DROP1 minus C_all |
|---|---|---|---|---|
| DROP1 V_RSI | -0.00122 | -0.00008 | +0.00011 | -0.00001 |
| DROP1 V_BB | -0.00080 | -0.00006 | -0.00003 | +0.00001 |
| DROP1 V_KUR | -0.00011 | -0.00001 | +0.00001 | +0.00000 |
| DROP1 V_TAK | +0.00071 | +0.00017 | -0.00001 | -0.00000 |
| DROP1 V_SWP | -0.00009 | -0.00004 | -0.00003 | -0.00001 |
| DROP1 V_DIV | -0.00040 | -0.00006 | -0.00000 | -0.00001 |

Layer with the highest mean DEV ADD1 delta (price outcome): **V_RSI** (+0.00090); lowest: V_TAK (-0.00004).

### Score buckets, all levels pooled, fee-net description (DEV; ALL = every covered event = level-only)

net = open 60 min after the fill / fill open - 1 - 0.10% fee. ev/day = sum of net over events / calendar days of the period (overlapping events of one RSI episode are all counted, so this describes the bucket, not a portfolio).

| RSI TF | scheme | bucket | events | days | P(price>fee) | P(RSI bounce) | mean net bp | ev/day bp |
|---|---|---|---|---|---|---|---|---|
| 1m | C_same | ALL | 90148 | 906 | 0.408 | 0.632 | -9.28 | -42.1 |
| 1m | C_same | 0 | 19328 | 906 | 0.385 | 0.597 | -9.76 | -9.5 |
| 1m | C_same | 1 | 49610 | 906 | 0.407 | 0.628 | -9.13 | -22.8 |
| 1m | C_same | 2 | 19628 | 906 | 0.429 | 0.667 | -9.15 | -9.0 |
| 1m | C_same | 3 | 1582 | 690 | 0.466 | 0.721 | -10.00 | -0.8 |
| 1m | C_high | ALL | 90148 | 906 | 0.408 | 0.632 | -9.28 | -42.1 |
| 1m | C_high | 0 | 50794 | 906 | 0.376 | 0.628 | -9.66 | -24.7 |
| 1m | C_high | 1 | 18034 | 900 | 0.426 | 0.631 | -8.96 | -8.1 |
| 1m | C_high | 2 | 17053 | 881 | 0.458 | 0.635 | -8.75 | -7.5 |
| 1m | C_high | 3 | 4267 | 570 | 0.509 | 0.664 | -8.32 | -1.8 |
| 1m | C_all | ALL | 90148 | 906 | 0.408 | 0.632 | -9.28 | -42.1 |
| 1m | C_all | 0 | 50195 | 906 | 0.376 | 0.621 | -9.61 | -24.2 |
| 1m | C_all | 1 | 16451 | 903 | 0.419 | 0.636 | -9.47 | -7.8 |
| 1m | C_all | 2 | 17836 | 894 | 0.458 | 0.643 | -8.61 | -7.7 |
| 1m | C_all | 3 | 5666 | 690 | 0.504 | 0.676 | -7.99 | -2.3 |
| 5m | C_same | ALL | 16666 | 899 | 0.454 | 0.663 | -9.18 | -7.7 |
| 5m | C_same | 0 | 2707 | 823 | 0.447 | 0.652 | -8.33 | -1.1 |
| 5m | C_same | 1 | 8790 | 896 | 0.453 | 0.658 | -9.85 | -4.4 |
| 5m | C_same | 2 | 4874 | 869 | 0.457 | 0.676 | -8.45 | -2.1 |
| 5m | C_same | 3 | 295 | 200 | 0.498 | 0.658 | -8.90 | -0.1 |
| 5m | C_high | ALL | 16666 | 899 | 0.454 | 0.663 | -9.18 | -7.7 |
| 5m | C_high | 0 | 8512 | 871 | 0.440 | 0.664 | -8.85 | -3.8 |
| 5m | C_high | 1 | 3473 | 715 | 0.434 | 0.661 | -11.22 | -2.0 |
| 5m | C_high | 2 | 3664 | 608 | 0.477 | 0.655 | -10.19 | -1.9 |
| 5m | C_high | 3 | 1017 | 260 | 0.558 | 0.680 | -1.31 | -0.1 |
| 5m | C_all | ALL | 16666 | 899 | 0.454 | 0.663 | -9.18 | -7.7 |
| 5m | C_all | 0 | 8084 | 879 | 0.441 | 0.664 | -8.76 | -3.6 |
| 5m | C_all | 1 | 3090 | 758 | 0.439 | 0.663 | -11.28 | -1.8 |
| 5m | C_all | 2 | 4082 | 672 | 0.466 | 0.651 | -10.20 | -2.1 |
| 5m | C_all | 3 | 1410 | 346 | 0.530 | 0.688 | -4.04 | -0.3 |
| 15m | C_same | ALL | 5414 | 806 | 0.481 | 0.672 | -9.53 | -2.6 |
| 15m | C_same | 0 | 722 | 451 | 0.438 | 0.677 | -12.01 | -0.4 |
| 15m | C_same | 1 | 2739 | 722 | 0.481 | 0.668 | -11.69 | -1.6 |
| 15m | C_same | 2 | 1859 | 631 | 0.494 | 0.673 | -5.35 | -0.5 |
| 15m | C_same | 3 | 94 | 66 | 0.574 | 0.702 | -10.55 | -0.0 |
| 15m | C_high | ALL | 5414 | 806 | 0.481 | 0.672 | -9.53 | -2.6 |
| 15m | C_high | 0 | 2855 | 654 | 0.483 | 0.671 | -10.80 | -1.5 |
| 15m | C_high | 1 | 977 | 351 | 0.487 | 0.673 | -4.52 | -0.2 |
| 15m | C_high | 2 | 1201 | 326 | 0.455 | 0.664 | -13.46 | -0.8 |
| 15m | C_high | 3 | 381 | 102 | 0.535 | 0.690 | -0.55 | -0.0 |
| 15m | C_all | ALL | 5414 | 806 | 0.481 | 0.672 | -9.53 | -2.6 |
| 15m | C_all | 0 | 2611 | 647 | 0.477 | 0.668 | -10.85 | -1.4 |
| 15m | C_all | 1 | 972 | 404 | 0.486 | 0.685 | -8.93 | -0.4 |
| 15m | C_all | 2 | 1297 | 390 | 0.467 | 0.658 | -12.12 | -0.8 |
| 15m | C_all | 3 | 534 | 148 | 0.528 | 0.700 | +2.07 | +0.1 |
| 60m | C_same | ALL | 1119 | 386 | 0.520 | 0.686 | -5.90 | -0.3 |
| 60m | C_same | 0 | 146 | 115 | 0.548 | 0.747 | -2.09 | -0.0 |
| 60m | C_same | 1 | 564 | 252 | 0.500 | 0.668 | -6.82 | -0.2 |
| 60m | C_same | 2 | 367 | 207 | 0.548 | 0.684 | -5.97 | -0.1 |
| 60m | C_same | 3 | 42 | 33 | 0.452 | 0.738 | -6.27 | -0.0 |
| 60m | C_high | ALL | 1119 | 386 | 0.520 | 0.686 | -5.90 | -0.3 |
| 60m | C_high | 0 | 720 | 280 | 0.500 | 0.675 | -8.41 | -0.3 |
| 60m | C_high | 1 | 166 | 81 | 0.542 | 0.711 | +1.40 | +0.0 |
| 60m | C_high | 2 | 193 | 85 | 0.565 | 0.684 | -6.75 | -0.1 |
| 60m | C_high | 3 | 40 | 23 | 0.575 | 0.800 | +13.05 | +0.0 |
| 60m | C_all | ALL | 1119 | 386 | 0.520 | 0.686 | -5.90 | -0.3 |
| 60m | C_all | 0 | 661 | 274 | 0.498 | 0.678 | -7.61 | -0.3 |
| 60m | C_all | 1 | 167 | 87 | 0.563 | 0.707 | -3.85 | -0.0 |
| 60m | C_all | 2 | 223 | 110 | 0.561 | 0.686 | -5.65 | -0.1 |
| 60m | C_all | 3 | 68 | 36 | 0.500 | 0.721 | +4.85 | +0.0 |

### Score buckets, all levels pooled, fee-net description (VALIDATION; ALL = every covered event = level-only)

net = open 60 min after the fill / fill open - 1 - 0.10% fee. ev/day = sum of net over events / calendar days of the period (overlapping events of one RSI episode are all counted, so this describes the bucket, not a portfolio).

| RSI TF | scheme | bucket | events | days | P(price>fee) | P(RSI bounce) | mean net bp | ev/day bp |
|---|---|---|---|---|---|---|---|---|
| 1m | C_same | ALL | 36045 | 364 | 0.424 | 0.625 | -7.96 | -786.5 |
| 1m | C_same | 0 | 7926 | 364 | 0.411 | 0.594 | -8.07 | -175.3 |
| 1m | C_same | 1 | 19505 | 364 | 0.426 | 0.621 | -8.14 | -434.9 |
| 1m | C_same | 2 | 7881 | 364 | 0.429 | 0.658 | -7.30 | -157.6 |
| 1m | C_same | 3 | 733 | 293 | 0.432 | 0.724 | -9.33 | -18.7 |
| 1m | C_high | ALL | 36045 | 364 | 0.424 | 0.625 | -7.96 | -786.5 |
| 1m | C_high | 0 | 20179 | 364 | 0.407 | 0.623 | -8.36 | -462.1 |
| 1m | C_high | 1 | 6725 | 361 | 0.425 | 0.629 | -8.78 | -161.8 |
| 1m | C_high | 2 | 7053 | 345 | 0.443 | 0.617 | -8.69 | -168.0 |
| 1m | C_high | 3 | 2088 | 238 | 0.512 | 0.654 | +0.92 | +5.3 |
| 1m | C_all | ALL | 36045 | 364 | 0.424 | 0.625 | -7.96 | -786.5 |
| 1m | C_all | 0 | 19927 | 364 | 0.406 | 0.618 | -8.61 | -469.9 |
| 1m | C_all | 1 | 6177 | 361 | 0.433 | 0.630 | -8.21 | -139.0 |
| 1m | C_all | 2 | 7312 | 358 | 0.435 | 0.625 | -8.81 | -176.6 |
| 1m | C_all | 3 | 2629 | 274 | 0.506 | 0.667 | -0.15 | -1.1 |
| 5m | C_same | ALL | 6959 | 357 | 0.441 | 0.630 | -7.53 | -143.6 |
| 5m | C_same | 0 | 1146 | 329 | 0.423 | 0.622 | -9.61 | -30.2 |
| 5m | C_same | 1 | 3526 | 355 | 0.442 | 0.619 | -7.47 | -72.2 |
| 5m | C_same | 2 | 2126 | 348 | 0.446 | 0.653 | -6.11 | -35.6 |
| 5m | C_same | 3 | 161 | 104 | 0.466 | 0.596 | -12.85 | -5.7 |
| 5m | C_high | ALL | 6959 | 357 | 0.441 | 0.630 | -7.53 | -143.6 |
| 5m | C_high | 0 | 3572 | 349 | 0.431 | 0.624 | -7.14 | -69.8 |
| 5m | C_high | 1 | 1376 | 283 | 0.428 | 0.632 | -10.10 | -38.1 |
| 5m | C_high | 2 | 1519 | 243 | 0.463 | 0.635 | -8.11 | -33.7 |
| 5m | C_high | 3 | 492 | 112 | 0.480 | 0.648 | -1.45 | -2.0 |
| 5m | C_all | ALL | 6959 | 357 | 0.441 | 0.630 | -7.53 | -143.6 |
| 5m | C_all | 0 | 3300 | 350 | 0.427 | 0.623 | -6.96 | -62.9 |
| 5m | C_all | 1 | 1345 | 305 | 0.448 | 0.624 | -9.65 | -35.6 |
| 5m | C_all | 2 | 1618 | 265 | 0.451 | 0.644 | -6.71 | -29.8 |
| 5m | C_all | 3 | 696 | 155 | 0.467 | 0.638 | -8.06 | -15.4 |
| 15m | C_same | ALL | 2254 | 325 | 0.450 | 0.634 | -6.72 | -41.5 |
| 15m | C_same | 0 | 271 | 177 | 0.472 | 0.624 | -5.77 | -4.3 |
| 15m | C_same | 1 | 1063 | 283 | 0.445 | 0.637 | -5.80 | -16.9 |
| 15m | C_same | 2 | 866 | 269 | 0.441 | 0.628 | -8.54 | -20.3 |
| 15m | C_same | 3 | 54 | 40 | 0.593 | 0.704 | -0.47 | -0.1 |
| 15m | C_high | ALL | 2254 | 325 | 0.450 | 0.634 | -6.72 | -41.5 |
| 15m | C_high | 0 | 1200 | 259 | 0.439 | 0.639 | -5.57 | -18.3 |
| 15m | C_high | 1 | 401 | 139 | 0.464 | 0.666 | -5.19 | -5.7 |
| 15m | C_high | 2 | 522 | 136 | 0.460 | 0.600 | -11.72 | -16.8 |
| 15m | C_high | 3 | 131 | 37 | 0.473 | 0.618 | -2.07 | -0.7 |
| 15m | C_all | ALL | 2254 | 325 | 0.450 | 0.634 | -6.72 | -41.5 |
| 15m | C_all | 0 | 1071 | 255 | 0.439 | 0.635 | -4.89 | -14.4 |
| 15m | C_all | 1 | 398 | 172 | 0.460 | 0.683 | -5.38 | -5.9 |
| 15m | C_all | 2 | 572 | 151 | 0.449 | 0.591 | -10.70 | -16.8 |
| 15m | C_all | 3 | 213 | 65 | 0.493 | 0.648 | -7.76 | -4.5 |
| 60m | C_same | ALL | 585 | 189 | 0.491 | 0.624 | -7.08 | -11.3 |
| 60m | C_same | 0 | 67 | 57 | 0.478 | 0.582 | -5.99 | -1.1 |
| 60m | C_same | 1 | 243 | 125 | 0.498 | 0.634 | -1.98 | -1.3 |
| 60m | C_same | 2 | 253 | 134 | 0.498 | 0.652 | -12.08 | -8.4 |
| 60m | C_same | 3 | 22 | 18 | 0.364 | 0.318 | -9.16 | -0.6 |
| 60m | C_high | ALL | 585 | 189 | 0.491 | 0.624 | -7.08 | -11.3 |
| 60m | C_high | 0 | 324 | 128 | 0.466 | 0.645 | -7.76 | -6.9 |
| 60m | C_high | 1 | 100 | 54 | 0.550 | 0.640 | +3.20 | +0.9 |
| 60m | C_high | 2 | 138 | 52 | 0.507 | 0.587 | -8.87 | -3.4 |
| 60m | C_high | 3 | 23 | 8 | 0.478 | 0.478 | -31.40 | -2.0 |
| 60m | C_all | ALL | 585 | 189 | 0.491 | 0.624 | -7.08 | -11.3 |
| 60m | C_all | 0 | 295 | 126 | 0.458 | 0.627 | -8.65 | -7.0 |
| 60m | C_all | 1 | 85 | 59 | 0.612 | 0.753 | +13.69 | +3.2 |
| 60m | C_all | 2 | 162 | 66 | 0.494 | 0.580 | -13.49 | -6.0 |
| 60m | C_all | 3 | 43 | 23 | 0.465 | 0.512 | -13.21 | -1.6 |

## Layers: causal history

| layer | causal history |
|---|---|
| V_RSI (higher-TF RSI band) | yes |
| V_BB Bollinger | yes |
| V_KUR Kurisko quad stochastic | yes |
| V_TAK taker-buy share | yes |
| V_SWP prior-day sweep | yes |
| V_DIV higher-TF divergence | yes |
| cryptocred | NOT_IN_DATA |
| funding | NOT_IN_DATA |
| krown | NOT_IN_DATA |
| open_interest | NOT_IN_DATA |
| oscillator_agreement_count | NOT_IN_DATA |
| pitchfork | NOT_IN_DATA |
| tom_fabio_orderflow | NOT_IN_DATA |
| trendline | NOT_IN_DATA |
| turn_of_candle | NOT_IN_DATA |
| wavetrend | NOT_IN_DATA |

Mirror for highs (short bias, question 5): not run (exploratory per SPEC Step G mirror rule; does not block). Standalone layers are mostly no-edge (LAYERS.md), so these votes are features of the state, not signals.


## Read

Ten tests pass the card's keep rule, all on the 1m price outcome. Read it honestly: VALIDATION t over days is below 1 for every kept test (C_all 0.81, C_high 0.75), against DEV t near 7.9, and the gains are a few 1e-4 nats per event, so no score is a material improvement over level-only F0. Almost all of the DEV gain on 1m comes from the higher-TF score, driven by the higher-TF RSI band (V_RSI has the highest mean DEV ADD1 delta). On 5m, 15m and 1h nothing survives VALIDATION (the five 5m candidates all turn negative). Higher-TF alignment carries the 1m signal and same-TF layers add little (compare C_same and C_high above). The bucket tables are in-sample descriptions; no fee-net edge is claimed. The mirror for highs was not run.
