# ECON_FLOOR: Stage 0 economic-floor kill test (RSI deep-buy)

BTCUSDT 1m, DEV only (bars opened before 2024-07-01; loader refuses later bars). RSI14 Wilder on 1m/15m/1h. Fee 0.10% round trip (SOURCED backtest/fees.py, 2 x BINANCE_TAKER). Fill = next bar open, exit = open h bars later. Episode = RSI <= level after >= level+3 (h=3, OURS). Relative level = trailing-90d 2nd percentile (causal, refreshed daily-block). Baseline = mean forward return of all bars in the same UTC-hour x trailing-vol tercile cell. CI = day-clustered 95%; week-block CI shown for stress clustering. Data: 1313280 1m bars from 30 monthly files, 0 time gaps.

## H1 verdict

**1m: NOT DEAD**
- abs30: dead; best horizon 16 bars, mean (gross - baseline) 0.0095%, upper day-clustered 95% CI 0.0163% vs fee 0.10%
- abs20: dead; best horizon 4 bars, mean (gross - baseline) 0.0204%, upper day-clustered 95% CI 0.0345% vs fee 0.10%
- abs10: inconclusive; best horizon 4 bars, mean (gross - baseline) 0.0504%, upper day-clustered 95% CI 0.1778% vs fee 0.10%
- rel_p2_90d: dead; best horizon 16 bars, mean (gross - baseline) 0.0117%, upper day-clustered 95% CI 0.0209% vs fee 0.10%

**15m: NOT DEAD**
- abs30: inconclusive; best horizon 16 bars, mean (gross - baseline) 0.0290%, upper day-clustered 95% CI 0.1294% vs fee 0.10%
- abs20: inconclusive; best horizon 1 bars, mean (gross - baseline) 0.0168%, upper day-clustered 95% CI 0.1461% vs fee 0.10%
- abs10: inconclusive; best horizon 1 bars, mean (gross - baseline) 0.4258%, upper day-clustered 95% CI 1.7066% vs fee 0.10%
- rel_p2_90d: dead; best horizon 1 bars, mean (gross - baseline) 0.0063%, upper day-clustered 95% CI 0.0502% vs fee 0.10%

**60m: NOT DEAD**
- abs30: inconclusive; best horizon 4 bars, mean (gross - baseline) 0.0240%, upper day-clustered 95% CI 0.1912% vs fee 0.10%
- abs20: alive; best horizon 16 bars, mean (gross - baseline) 0.5705%, upper day-clustered 95% CI 1.9571% vs fee 0.10%
- abs10: n/a (2 episodes, too few for a CI)
- rel_p2_90d: inconclusive; best horizon 4 bars, mean (gross - baseline) 0.0580%, upper day-clustered 95% CI 0.3053% vs fee 0.10%

Study-level: not all TFs dead, the study is not stopped by H1. Class meaning: dead = upper CI below fee; inconclusive = mean below fee but the CI is too wide to exclude it (low n); alive = mean at or above fee.

## Per-TF gross forward return (event minus matched baseline), % of price

| TF | level | h | n events | n days | gross % | baseline % | diff % | CI hi day % | CI hi week % | MDE 80% % |
|---|---|---|---|---|---|---|---|---|---|---|
| 1m | abs30 | 1 | 12176 | 822 | 0.0053 | 0.0000 | 0.0053 | 0.0076 | 0.0077 | 0.0033 |
| 1m | abs30 | 4 | 12176 | 822 | 0.0080 | 0.0001 | 0.0079 | 0.0118 | 0.0122 | 0.0056 |
| 1m | abs30 | 16 | 12176 | 822 | 0.0099 | 0.0004 | 0.0095 | 0.0163 | 0.0166 | 0.0098 |
| 1m | abs20 | 1 | 2007 | 701 | 0.0053 | 0.0000 | 0.0052 | 0.0151 | 0.0152 | 0.0141 |
| 1m | abs20 | 4 | 2007 | 701 | 0.0205 | 0.0001 | 0.0204 | 0.0345 | 0.0352 | 0.0201 |
| 1m | abs20 | 16 | 2007 | 701 | 0.0202 | 0.0006 | 0.0196 | 0.0450 | 0.0438 | 0.0362 |
| 1m | abs10 | 1 | 148 | 117 | -0.0244 | -0.0000 | -0.0244 | 0.0768 | 0.0748 | 0.1445 |
| 1m | abs10 | 4 | 148 | 117 | 0.0504 | -0.0000 | 0.0504 | 0.1778 | 0.1720 | 0.1819 |
| 1m | abs10 | 16 | 148 | 117 | 0.0395 | 0.0003 | 0.0392 | 0.2544 | 0.2388 | 0.3074 |
| 1m | rel_p2_90d | 1 | 8151 | 822 | 0.0049 | 0.0000 | 0.0049 | 0.0081 | 0.0083 | 0.0046 |
| 1m | rel_p2_90d | 4 | 8151 | 822 | 0.0117 | 0.0001 | 0.0116 | 0.0174 | 0.0179 | 0.0083 |
| 1m | rel_p2_90d | 16 | 8151 | 822 | 0.0122 | 0.0005 | 0.0117 | 0.0209 | 0.0222 | 0.0131 |
| 15m | abs30 | 1 | 752 | 440 | -0.0178 | -0.0004 | -0.0174 | 0.0142 | 0.0111 | 0.0451 |
| 15m | abs30 | 4 | 752 | 440 | 0.0122 | 0.0004 | 0.0118 | 0.0722 | 0.0658 | 0.0863 |
| 15m | abs30 | 16 | 752 | 440 | 0.0397 | 0.0107 | 0.0290 | 0.1294 | 0.1232 | 0.1435 |
| 15m | abs20 | 1 | 147 | 118 | 0.0163 | -0.0005 | 0.0168 | 0.1461 | 0.1375 | 0.1848 |
| 15m | abs20 | 4 | 147 | 118 | -0.0240 | -0.0011 | -0.0229 | 0.1468 | 0.1342 | 0.2425 |
| 15m | abs20 | 16 | 147 | 118 | 0.0260 | 0.0113 | 0.0148 | 0.2770 | 0.2732 | 0.3747 |
| 15m | abs10 | 1 | 10 | 10 | 0.4237 | -0.0021 | 0.4258 | 1.7066 | 1.6770 | 1.8297 |
| 15m | abs10 | 4 | 10 | 10 | 0.2272 | 0.0093 | 0.2178 | 1.6812 | 1.6871 | 2.0905 |
| 15m | abs10 | 16 | 10 | 10 | -0.0312 | 0.0637 | -0.0949 | 1.7227 | 1.7566 | 2.5966 |
| 15m | rel_p2_90d | 1 | 474 | 291 | 0.0054 | -0.0009 | 0.0063 | 0.0502 | 0.0479 | 0.0628 |
| 15m | rel_p2_90d | 4 | 474 | 291 | -0.0090 | -0.0004 | -0.0086 | 0.0828 | 0.0805 | 0.1306 |
| 15m | rel_p2_90d | 16 | 474 | 291 | -0.0209 | 0.0089 | -0.0298 | 0.1087 | 0.0809 | 0.1978 |
| 60m | abs30 | 1 | 221 | 175 | -0.0027 | 0.0022 | -0.0048 | 0.1015 | 0.1078 | 0.1520 |
| 60m | abs30 | 4 | 221 | 175 | 0.0346 | 0.0106 | 0.0240 | 0.1912 | 0.1907 | 0.2389 |
| 60m | abs30 | 16 | 221 | 175 | -0.0662 | 0.0464 | -0.1125 | 0.2670 | 0.2563 | 0.5422 |
| 60m | abs20 | 1 | 46 | 36 | 0.0792 | -0.0002 | 0.0794 | 0.3160 | 0.3181 | 0.3379 |
| 60m | abs20 | 4 | 46 | 36 | 0.1712 | 0.0256 | 0.1455 | 0.5463 | 0.5251 | 0.5725 |
| 60m | abs20 | 16 | 46 | 36 | 0.6479 | 0.0774 | 0.5705 | 1.9571 | 1.8312 | 1.9809 |
| 60m | rel_p2_90d | 1 | 127 | 105 | 0.0558 | 0.0004 | 0.0554 | 0.2136 | 0.2199 | 0.2260 |
| 60m | rel_p2_90d | 4 | 127 | 105 | 0.0666 | 0.0085 | 0.0580 | 0.3053 | 0.2935 | 0.3532 |
| 60m | rel_p2_90d | 16 | 127 | 105 | -0.0145 | 0.0544 | -0.0689 | 0.4290 | 0.3928 | 0.7114 |

## Bounce, adverse move and lower-low odds (from the fill price)

| TF | level | h | P(lower low than fill) | P(close >= fill+fee) | median MFE % | median MAE % |
|---|---|---|---|---|---|---|
| 1m | abs30 | 1 | 0.899 | 0.120 | 0.043 | -0.033 |
| 1m | abs30 | 4 | 0.944 | 0.313 | 0.082 | -0.069 |
| 1m | abs30 | 16 | 0.969 | 0.556 | 0.145 | -0.129 |
| 1m | abs20 | 1 | 0.930 | 0.221 | 0.070 | -0.057 |
| 1m | abs20 | 4 | 0.957 | 0.443 | 0.127 | -0.108 |
| 1m | abs20 | 16 | 0.974 | 0.620 | 0.196 | -0.181 |
| 1m | abs10 | 1 | 0.953 | 0.324 | 0.113 | -0.092 |
| 1m | abs10 | 4 | 0.980 | 0.493 | 0.188 | -0.150 |
| 1m | abs10 | 16 | 0.986 | 0.628 | 0.283 | -0.191 |
| 1m | rel_p2_90d | 1 | 0.904 | 0.139 | 0.049 | -0.036 |
| 1m | rel_p2_90d | 4 | 0.945 | 0.345 | 0.091 | -0.075 |
| 1m | rel_p2_90d | 16 | 0.968 | 0.574 | 0.157 | -0.137 |
| 15m | abs30 | 1 | 0.991 | 0.428 | 0.231 | -0.262 |
| 15m | abs30 | 4 | 0.999 | 0.684 | 0.378 | -0.441 |
| 15m | abs30 | 16 | 1.000 | 0.806 | 0.678 | -0.698 |
| 15m | abs20 | 1 | 1.000 | 0.401 | 0.274 | -0.415 |
| 15m | abs20 | 4 | 1.000 | 0.565 | 0.390 | -0.630 |
| 15m | abs20 | 16 | 1.000 | 0.728 | 0.601 | -1.017 |
| 15m | abs10 | 1 | 1.000 | 0.500 | 0.411 | -0.514 |
| 15m | abs10 | 4 | 1.000 | 0.700 | 0.668 | -0.663 |
| 15m | abs10 | 16 | 1.000 | 0.800 | 0.668 | -1.250 |
| 15m | rel_p2_90d | 1 | 0.992 | 0.454 | 0.256 | -0.268 |
| 15m | rel_p2_90d | 4 | 0.998 | 0.671 | 0.409 | -0.470 |
| 15m | rel_p2_90d | 16 | 1.000 | 0.789 | 0.690 | -0.806 |
| 60m | abs30 | 1 | 1.000 | 0.543 | 0.444 | -0.440 |
| 60m | abs30 | 4 | 1.000 | 0.729 | 0.694 | -0.703 |
| 60m | abs30 | 16 | 1.000 | 0.792 | 1.278 | -1.544 |
| 60m | abs20 | 1 | 1.000 | 0.565 | 0.582 | -0.604 |
| 60m | abs20 | 4 | 1.000 | 0.848 | 1.064 | -1.116 |
| 60m | abs20 | 16 | 1.000 | 0.913 | 1.600 | -1.787 |
| 60m | rel_p2_90d | 1 | 1.000 | 0.528 | 0.444 | -0.442 |
| 60m | rel_p2_90d | 4 | 1.000 | 0.756 | 0.817 | -0.765 |
| 60m | rel_p2_90d | 16 | 1.000 | 0.843 | 1.432 | -1.610 |

## RSI minimum to price minimum lag (hindsight, descriptive; episode window up to 200 bars)

| TF | level | episodes | median lag bars | p90 lag bars | median price-min vs close at RSI-min % |
|---|---|---|---|---|---|
| 1m | abs30 | 13452 | 0.0 | 1.0 | -0.037 |
| 1m | abs20 | 2236 | 0.0 | 1.0 | -0.069 |
| 1m | abs10 | 158 | 0.0 | 0.0 | -0.141 |
| 1m | rel_p2_90d | 8151 | 0.0 | 1.0 | -0.039 |
| 15m | abs30 | 849 | 0.0 | 2.0 | -0.289 |
| 15m | abs20 | 170 | 0.0 | 1.0 | -0.406 |
| 15m | abs10 | 11 | 0.0 | 0.0 | -0.495 |
| 15m | rel_p2_90d | 474 | 0.0 | 1.0 | -0.325 |
| 60m | abs30 | 253 | 0.0 | 2.0 | -0.528 |
| 60m | abs20 | 51 | 0.0 | 1.0 | -0.948 |
| 60m | rel_p2_90d | 127 | 0.0 | 1.0 | -0.620 |

## C12: RSI trough close to first close at RSI 40/50/60 (hindsight trough, descriptive; search capped at 5000 bars)

Fee multiple = move / 0.10%. Not a tradeable entry (the trough is known only afterwards).

| TF | level | target | share reached | median move % | mean move % | median fee multiple | share >= 1 fee |
|---|---|---|---|---|---|---|---|
| 1m | abs30 | RSI 40 | 1.000 | 0.104 | 0.116 | 1.04 | 0.516 |
| 1m | abs30 | RSI 50 | 1.000 | 0.130 | 0.119 | 1.30 | 0.583 |
| 1m | abs30 | RSI 60 | 1.000 | 0.174 | 0.124 | 1.74 | 0.631 |
| 1m | abs20 | RSI 40 | 1.000 | 0.147 | 0.146 | 1.47 | 0.584 |
| 1m | abs20 | RSI 50 | 1.000 | 0.170 | 0.155 | 1.70 | 0.599 |
| 1m | abs20 | RSI 60 | 1.000 | 0.204 | 0.166 | 2.04 | 0.627 |
| 1m | abs10 | RSI 40 | 1.000 | 0.176 | 0.197 | 1.76 | 0.595 |
| 1m | abs10 | RSI 50 | 1.000 | 0.187 | 0.190 | 1.87 | 0.570 |
| 1m | abs10 | RSI 60 | 1.000 | 0.213 | 0.212 | 2.13 | 0.582 |
| 1m | rel_p2_90d | RSI 40 | 1.000 | 0.109 | 0.123 | 1.09 | 0.532 |
| 1m | rel_p2_90d | RSI 50 | 1.000 | 0.132 | 0.123 | 1.32 | 0.579 |
| 1m | rel_p2_90d | RSI 60 | 1.000 | 0.173 | 0.127 | 1.73 | 0.623 |
| 15m | abs30 | RSI 40 | 1.000 | 0.509 | 0.567 | 5.09 | 0.856 |
| 15m | abs30 | RSI 50 | 1.000 | 0.656 | 0.588 | 6.56 | 0.795 |
| 15m | abs30 | RSI 60 | 1.000 | 0.833 | 0.481 | 8.33 | 0.753 |
| 15m | abs20 | RSI 40 | 1.000 | 0.567 | 0.522 | 5.67 | 0.682 |
| 15m | abs20 | RSI 50 | 1.000 | 0.607 | 0.509 | 6.07 | 0.706 |
| 15m | abs20 | RSI 60 | 1.000 | 0.629 | 0.124 | 6.29 | 0.647 |
| 15m | abs10 | RSI 40 | 1.000 | 1.097 | 1.258 | 10.97 | 0.636 |
| 15m | abs10 | RSI 50 | 1.000 | 1.122 | 1.417 | 11.22 | 0.727 |
| 15m | abs10 | RSI 60 | 1.000 | 0.645 | 0.291 | 6.45 | 0.727 |
| 15m | rel_p2_90d | RSI 40 | 1.000 | 0.498 | 0.518 | 4.98 | 0.810 |
| 15m | rel_p2_90d | RSI 50 | 1.000 | 0.600 | 0.545 | 6.00 | 0.762 |
| 15m | rel_p2_90d | RSI 60 | 1.000 | 0.798 | 0.492 | 7.98 | 0.728 |
| 60m | abs30 | RSI 40 | 1.000 | 0.899 | 0.802 | 8.99 | 0.850 |
| 60m | abs30 | RSI 50 | 1.000 | 1.288 | 0.922 | 12.88 | 0.775 |
| 60m | abs30 | RSI 60 | 1.000 | 1.631 | 0.736 | 16.31 | 0.727 |
| 60m | abs20 | RSI 40 | 1.000 | 0.989 | 0.919 | 9.89 | 0.706 |
| 60m | abs20 | RSI 50 | 1.000 | 1.420 | 0.714 | 14.20 | 0.686 |
| 60m | abs20 | RSI 60 | 1.000 | 1.947 | 1.295 | 19.47 | 0.725 |
| 60m | rel_p2_90d | RSI 40 | 1.000 | 0.926 | 1.100 | 9.26 | 0.858 |
| 60m | rel_p2_90d | RSI 50 | 1.000 | 1.289 | 1.236 | 12.89 | 0.795 |
| 60m | rel_p2_90d | RSI 60 | 1.000 | 1.859 | 1.281 | 18.59 | 0.756 |

## Notes and decisions

- 1m time gaps in DEV: 0
- 60m abs10: only 2 episodes, no CI
- DECISION (OURS): TF verdict = dead only if EVERY level with a CI has upper bound below fee at its best horizon (best = max mean diff). Hard to kill by design; low-n levels stay inconclusive.
- DECISION (OURS): the first stress-cluster idea (merge consecutive event days) collapses to one cluster on BTC, so a 7-day block CI is reported next to the day CI. Verdict uses the day CI as the card says.
- DECISION (OURS): matched baseline is the cell mean of all bars (UTC hour x trailing-vol tercile, causal vol cuts), a deterministic stand-in for random matched bars; it uses future bars of the sample only as a benchmark, never in a decision.
- DECISION (OURS): first 200 bars per TF are dropped (RSI warm-up); the relative level starts after 90 days of history, so 2022-01..03 has no relative events.
- CAUTION: 'alive' = best of three horizons picked on its own mean (selection bias) with its CI lower bound far below the fee (60m abs20: 36 days, 46 episodes, one crash-heavy sample). It is a lead for Stage 1, not an edge.
- Horizons are bars of the TF (1m: 1/4/16 minutes; 15m: 15/60/240 min; 1h: 1/4/16 hours). The 0.10% fee is a hard floor in price terms on every TF.
- Overlap: episodes inside one hour or one crash are not independent; days (and weeks) are the unit of evidence. No VALIDATION or HOLDOUT bar was read.
