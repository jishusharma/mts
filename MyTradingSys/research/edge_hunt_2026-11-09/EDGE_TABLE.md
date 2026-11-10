# Edge hunt 2026-11-09: the 15 trials in one table (T2 of PLAN_24H_2026-11-10)

**No trial passed. 8 FAIL, 5 INCONCLUSIVE, 2 not run as frozen trials (T07, T08).** No VALIDATION read was made, so no
testnet-forward card comes from this wave. Every number is copied from results/<worker>/RESULT.md (DEV split only; the
holdout was never loaded). Lead B, 2026-11-10. The 13 rows are also in research/VERDICTS.csv (study_dir edge_hunt_2026-11-09/...).

| Id | Hypothesis | n (DEV) | mean net R | SE | 95 % CI | Verdict |
|---|---|---|---|---|---|---|
| T01 | 7-star spinning top, BTC+ETH 4h/1d | 108 | -0.217 | 0.150 | -0.511..+0.077 | FAIL |
| T02 | 7-star MTF long | 7 | +1.058 | 1.012 | -0.93..+3.04 | INCONCLUSIVE |
| T03 | 5-star MTF long | 8 | +0.072 | 0.509 | -0.92..+1.07 | INCONCLUSIVE |
| T04 | first-touch sweep-reclaim fade PDH/PDL/PWH/PWL | 1150 | -0.221 | 0.043 | -0.305..-0.136 | FAIL |
| T05 | fast-in short-time level fade, BTC 15m | 300 | -0.086 | 0.081 | -0.245..+0.074 | FAIL |
| T06 | RSI14 cross of its SMA14, 4h BTC+ETH | 1322 | +0.048 | 0.040 | -0.029..+0.126 | INCONCLUSIVE |
| T09 | HTF support wick long, BTC 15m | 41 | -0.581 | 0.235 | -1.042..-0.120 | FAIL |
| T10 | HTF resistance wick short, BTC 15m | 47 | -0.804 | 0.215 | -1.226..-0.382 | FAIL |
| T11 | RSI 40/60 bounce with MTF confluence | 1588 | -0.146 | 0.042 | -0.228..-0.064 | FAIL |
| T12 | T11 against HTF bias | 1477 | -0.133 | 0.044 | -0.219..-0.047 | FAIL |
| T13 | confluence score 0-5 slope (score>=3 n=410 -0.163) | 13851 |  |  | slope +1.04, CI -0.91..+2.99 | INCONCLUSIVE |
| T14 | 1h level fade, balance phase | 358 | -0.232 | 0.071 | -0.371..-0.094 | FAIL |
| T15 | MLK-S1 4h RSI-40 long, accumulation/bull | 51 | +0.016 | 0.247 | -0.467..+0.500 | INCONCLUSIVE |
| T07 | Malkan 5-layer level short, BTC+ETH 4h | - | - | - | - | NOT RUN as a frozen trial |
| T08 | T07 mirrored as a long | - | - | - | - | NOT RUN |

## Notes
- T07 has no results folder. The nearest count is malkan_level_shorts_2026-11-09/REPORT.md (BTC 4h, 10 arms, not
  screened): the full 5-layer stack n=37, +0.13 R; the best arm (divergence 3-10 bars, close) n=126, +0.10 R, about 0.9 SE.
  It is not a trial verdict. It goes forward as the Malkan paper slot (T1), where the weekly E+/E- rule decides.
- T02 and T03 are too rare to test (about 1.2 and 1.4 events a year).
- T06 is the best leftover: +0.048 R, n=1322, CI includes 0; the long side alone is +0.105 R (p 0.055, Holm 0.83). It
  goes forward as the T06 paper slot (T1), not as a longer backtest.
- PLAN_24H section 1 said "9 FAIL, 4 INCONCLUSIVE"; the RESULT files give 8 and 5 (T13 is INCONCLUSIVE in its file).
