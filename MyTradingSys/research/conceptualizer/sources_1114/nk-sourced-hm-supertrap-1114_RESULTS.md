# RESULT nk-sourced-hm-supertrap-1114 (2026-11-14; rules frozen in PRE_REG.md, commit 9c4da5a14, before any outcome)

**VERDICT: NO PASS. 0 of 78 gated rows (26 variants x UP/DOWN/RANGE) pass every gate on VALIDATION (>= 2024-01-01, 12 bp). NK's Hilega Milega state as he states it (30m trend, 5m entry, right side of the session VWAP) earns about zero gross and loses 0.21 to 0.28 R per trade net in every phase; the daily-frame positional version is the only family with a positive mean (RANGE days +0.15 to +0.16 R, 4 rows pass every gate except Benjamini-Hochberg), and the gap rule / Supertrap on crypto is mostly too rare to test (n < 100 in 41 of 54 phase rows) and negative where it can be tested. The power gate said BLOCK before the run (MDE 0.36 R), so a NO PASS is not proof of no edge.**

| What | Result (VALIDATION, 12 bp, per phase) |
|---|---|
| A intraday, 30m/5m, 4 variants | UP -0.25 to -0.28, DOWN -0.21 to -0.27, RANGE -0.24 to -0.28 R; n 38,000 to 66,000 per row; gross -0.005 to -0.012 R (zero); fee/R 0.22 to 0.37 eats it; at 6 bp still -0.08 to -0.15 R. Both VWAP anchors and the 50-line filter change nothing. DEV agrees (-0.23 to -0.32). |
| A positional, daily trend / 30m entry, 4 variants | UP +0.09 to +0.10 R (CI low -0.02 to -0.04, fails); DOWN -0.04 to -0.06 R; RANGE +0.15 to +0.16 R (n 1,309 to 1,442, 522 to 550 day clusters, CI low -0.004 to +0.008, placebo p 0.005, ex-best-5 +0.002 to +0.015, per-trade CI low +0.04 to +0.05): 3 of the 4 pass every gate except BH (p 0.020 to 0.029 vs the 0.0006 first-rank cut); the 4th also misses the day-cluster CI by 0.004. DEV same sign (+0.13 to +0.19). It is long-side (+0.3 R long, 0.0 R short), and removing the best 5 days takes +0.16 to about +0.01: a few days carry it. |
| B Supertrap (first candle >= 50% outside BB, VWAP stop) | n < 100 in every phase and source (1 to 81); no verdict. UNDERPOWERED rows swing between -1.3 and +1.8 R. His "< 5 fails in 1000" claim cannot be tested on crypto with this event definition. |
| B gap rule (15 min close + retest), with and without prev-day H/L | Only the CME-weekend proxy (th 0.5), the 13:30 session (th 0.75) and the 00:00 session (th 0.5, plain gap rule) reach n >= 100: CME UP +0.07, RANGE +0.21 / +0.30 R with CI low -0.8 to -0.9 (66 to 86 day clusters); DOWN -0.37; 13:30 session -0.08 to -0.46 R and 00:00 session -0.13 to -0.42 R in every phase. Nothing passes; placebo p 0.005 to 0.010 only says entries beat random ones on gross, not that they pay 12 bp at 0.35 fee/R. |

## Context
Regime: BTC close vs the 200-week SMA (1400 daily closes, BTC 1d from 2017-08; flag exists from 2021-06-16): BULL / BEAR reported as the second cut, never pooled. BTC is 5.3% above the SMA now (71,460 vs 67,848).
Phase: daily UP / DOWN / RANGE per coin from the prior close (ADX14 >= 20 with DI and SMA20 slope). Every table below is one phase.
Session: 24/7 crypto; VWAP anchored 00:00 UTC (U) or 13:30 UTC (N); events at Sunday 23:00, 00:00 and 13:30 UTC.
Entry: state-conjunction rising edge for A; first-candle / 15-minute breakout + retest for B (details PRE_REG.md).
Regime mix: VALIDATION window 20,404 coin-days (20 coins): UP 24.9% / DOWN 35.1% / RANGE 40.0%; cycle BULL 97.8% / BEAR 2.2% (456 coin-days). DEV window 32,118 coin-days (820 unlabelled): UP 31.6% / DOWN 32.3% / RANGE 36.1% of the labelled days; cycle NA 13,558 (before 2021-06-16) / BULL 12,220 / BEAR 6,340. VALIDATION is almost all BULL cycle, so the BEAR-cycle cut has only the intraday rows (n 3.4k to 3.6k: -0.37 to -0.45 R) and no positional or B row with n >= 100.

## Per-phase tables (all 26 variants; n >= 100 shown, the rest listed under UNDERPOWERED)
Gates: n >= 100, mean > 0, per-trade CI low > 0, day-cluster CI low > 0, placebo p < 0.05, BH (q 0.05, family 78), ex-best-5-days > 0. "fails:" lists the gates missed; placebo is only run when n >= 100 and mean > 0 (n/a otherwise).

### UP days (VALIDATION >= 2024-01-01, 12 bp net R per trade; columns: n, mean net R at 12 bp, gross R (= 2 x 6bp mean - 12bp mean), day-cluster CI low, ex-best-5-days mean, median fee/R, mean at 6 bp, DEV n / mean, long n/mean, short n/mean, placebo p, BH, gates)

| Variant | n | mean R | gross R | CI day lo | ex5 | fee/R | 6bp mean | DEV n / mean | long | short | placebo p | BH | gates |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A 00:00 VWAP, 1d/30m, RSI>50 filter | 633 | +0.098 | +0.114 | -0.027 | -0.006 | 0.01 | +0.106 | 1101 / +0.120 | 277/+0.19 | 356/+0.03 | 0.005 | no | fails: ci_day,bh,ex5 |
| A 13:30 VWAP, 1d/30m, RSI>50 filter | 647 | +0.093 | +0.108 | -0.039 | -0.009 | 0.01 | +0.101 | 1130 / +0.115 | 288/+0.18 | 359/+0.02 | 0.010 | no | fails: ci_day,bh,ex5 |
| A 00:00 VWAP, 1d/30m, no 50 filter | 788 | +0.093 | +0.109 | -0.023 | +0.010 | 0.01 | +0.101 | 1551 / +0.020 | 273/+0.20 | 515/+0.04 | 0.020 | no | fails: ci_day,bh |
| A 13:30 VWAP, 1d/30m, no 50 filter | 826 | +0.085 | +0.101 | -0.023 | +0.003 | 0.01 | +0.093 | 1634 / +0.012 | 295/+0.18 | 531/+0.03 | 0.020 | no | fails: ci_day,bh |
| B cme th0.5 gap rule | 155 | +0.074 | +0.382 | -0.808 | -0.926 | 0.35 | +0.228 | 262 / +0.242 | 114/-0.23 | 41/+0.93 | 0.010 | no | fails: ci_trade,ci_day,bh,ex5 |
| A 13:30 VWAP, 30m/5m, RSI>50 filter | 37925 | -0.245 | -0.008 | -0.285 | -0.264 | 0.22 | -0.127 | 77778 / -0.256 | 18793/-0.27 | 19132/-0.22 | n/a | no | fails: mean_pos,ci_trade,ci_day,placebo,bh,ex5 |
| A 00:00 VWAP, 30m/5m, RSI>50 filter | 38680 | -0.254 | -0.012 | -0.291 | -0.272 | 0.23 | -0.133 | 77877 / -0.248 | 19153/-0.29 | 19527/-0.22 | n/a | no | fails: mean_pos,ci_trade,ci_day,placebo,bh,ex5 |
| A 00:00 VWAP, 30m/5m, no 50 filter | 43017 | -0.270 | -0.005 | -0.310 | -0.290 | 0.29 | -0.137 | 86571 / -0.263 | 20997/-0.30 | 22020/-0.24 | n/a | no | fails: mean_pos,ci_trade,ci_day,placebo,bh,ex5 |
| A 13:30 VWAP, 30m/5m, no 50 filter | 41958 | -0.277 | -0.019 | -0.316 | -0.297 | 0.27 | -0.148 | 87310 / -0.293 | 20885/-0.30 | 21073/-0.26 | n/a | no | fails: mean_pos,ci_trade,ci_day,placebo,bh,ex5 |
| B cme th0.5 gap rule+PDHL | 104 | -0.389 | -0.086 | -0.961 | -1.034 | 0.35 | -0.237 | 193 / +0.353 | 73/-0.73 | 31/+0.42 | n/a | no | fails: mean_pos,ci_trade,ci_day,placebo,bh,ex5 |
| B s1330 th0.75 gap rule | 330 | -0.413 | -0.160 | -0.693 | -0.657 | 0.25 | -0.287 | 614 / +0.010 | 206/-0.35 | 124/-0.52 | n/a | no | fails: mean_pos,ci_trade,ci_day,placebo,bh,ex5 |
| B s0000 th0.5 gap rule | 108 | -0.415 | -0.191 | -0.984 | -1.076 | 0.20 | -0.303 | 219 / -0.186 | 76/-0.31 | 32/-0.67 | n/a | no | fails: mean_pos,ci_trade,ci_day,placebo,bh,ex5 |
| B s1330 th0.75 gap rule+PDHL | 281 | -0.460 | -0.202 | -0.750 | -0.751 | 0.25 | -0.331 | 535 / -0.028 | 178/-0.40 | 103/-0.56 | n/a | no | fails: mean_pos,ci_trade,ci_day,placebo,bh,ex5 |

UNDERPOWERED (n < 100, no verdict): B cme th0.5 Supertrap n=27 mean -1.30; B cme th1 Supertrap n=4 mean -0.88; B cme th1 gap rule n=69 mean -0.56; B cme th1 gap rule+PDHL n=48 mean -0.41; B s0000 th0.5 Supertrap n=55 mean +1.82; B s0000 th0.5 gap rule+PDHL n=47 mean -0.84; B s0000 th1 Supertrap n=2 mean +1.62; B s0000 th1 gap rule n=15 mean -0.96; B s0000 th1 gap rule+PDHL n=6 mean -1.11; B s1330 th0.75 Supertrap n=58 mean -0.69; B s1330 th1.5 Supertrap n=9 mean -1.21; B s1330 th1.5 gap rule n=62 mean -0.37; B s1330 th1.5 gap rule+PDHL n=56 mean -0.31

### DOWN days (VALIDATION >= 2024-01-01, 12 bp net R per trade; columns: n, mean net R at 12 bp, gross R (= 2 x 6bp mean - 12bp mean), day-cluster CI low, ex-best-5-days mean, median fee/R, mean at 6 bp, DEV n / mean, long n/mean, short n/mean, placebo p, BH, gates)

| Variant | n | mean R | gross R | CI day lo | ex5 | fee/R | 6bp mean | DEV n / mean | long | short | placebo p | BH | gates |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A 13:30 VWAP, 1d/30m, RSI>50 filter | 886 | -0.039 | -0.026 | -0.140 | -0.132 | 0.01 | -0.032 | 1170 / +0.133 | 423/+0.01 | 463/-0.09 | n/a | no | fails: mean_pos,ci_trade,ci_day,placebo,bh,ex5 |
| A 00:00 VWAP, 1d/30m, RSI>50 filter | 870 | -0.041 | -0.028 | -0.144 | -0.136 | 0.01 | -0.035 | 1162 / +0.134 | 417/+0.02 | 453/-0.10 | n/a | no | fails: mean_pos,ci_trade,ci_day,placebo,bh,ex5 |
| A 13:30 VWAP, 1d/30m, no 50 filter | 1184 | -0.061 | -0.048 | -0.147 | -0.138 | 0.01 | -0.055 | 1646 / +0.094 | 709/-0.04 | 475/-0.09 | n/a | no | fails: mean_pos,ci_trade,ci_day,placebo,bh,ex5 |
| A 00:00 VWAP, 1d/30m, no 50 filter | 1145 | -0.063 | -0.051 | -0.150 | -0.142 | 0.01 | -0.057 | 1622 / +0.097 | 690/-0.04 | 455/-0.10 | n/a | no | fails: mean_pos,ci_trade,ci_day,placebo,bh,ex5 |
| B s1330 th0.75 gap rule+PDHL | 197 | -0.082 | +0.203 | -0.667 | -0.615 | 0.29 | +0.061 | 225 / +0.097 | 88/+0.47 | 109/-0.53 | n/a | no | fails: mean_pos,ci_trade,ci_day,placebo,bh,ex5 |
| B s1330 th0.75 gap rule | 216 | -0.146 | +0.139 | -0.659 | -0.650 | 0.29 | -0.004 | 255 / +0.139 | 104/+0.28 | 112/-0.54 | n/a | no | fails: mean_pos,ci_trade,ci_day,placebo,bh,ex5 |
| A 13:30 VWAP, 30m/5m, RSI>50 filter | 51227 | -0.206 | +0.046 | -0.250 | -0.226 | 0.25 | -0.080 | 76378 / -0.233 | 25660/-0.20 | 25567/-0.21 | n/a | no | fails: mean_pos,ci_trade,ci_day,placebo,bh,ex5 |
| A 00:00 VWAP, 30m/5m, RSI>50 filter | 53143 | -0.235 | +0.024 | -0.278 | -0.256 | 0.27 | -0.105 | 77241 / -0.227 | 26614/-0.24 | 26529/-0.23 | n/a | no | fails: mean_pos,ci_trade,ci_day,placebo,bh,ex5 |
| A 13:30 VWAP, 30m/5m, no 50 filter | 56888 | -0.239 | +0.035 | -0.283 | -0.262 | 0.32 | -0.102 | 84978 / -0.264 | 28918/-0.24 | 27970/-0.24 | n/a | no | fails: mean_pos,ci_trade,ci_day,placebo,bh,ex5 |
| A 00:00 VWAP, 30m/5m, no 50 filter | 59304 | -0.266 | +0.017 | -0.308 | -0.288 | 0.34 | -0.124 | 85273 / -0.239 | 29794/-0.27 | 29510/-0.26 | n/a | no | fails: mean_pos,ci_trade,ci_day,placebo,bh,ex5 |
| B cme th0.5 gap rule | 105 | -0.368 | -0.028 | -0.992 | -1.115 | 0.40 | -0.198 | 204 / +1.079 | 53/-0.87 | 52/+0.14 | n/a | no | fails: mean_pos,ci_trade,ci_day,placebo,bh,ex5 |

UNDERPOWERED (n < 100, no verdict): B cme th0.5 Supertrap n=21 mean -0.23; B cme th0.5 gap rule+PDHL n=83 mean -0.29; B cme th1 Supertrap n=9 mean +1.03; B cme th1 gap rule n=20 mean +0.34; B cme th1 gap rule+PDHL n=19 mean +0.43; B s0000 th0.5 Supertrap n=30 mean -0.67; B s0000 th0.5 gap rule n=84 mean -0.30; B s0000 th0.5 gap rule+PDHL n=35 mean +0.26; B s0000 th1 Supertrap n=1 mean -1.38; B s0000 th1 gap rule n=12 mean -1.02; B s0000 th1 gap rule+PDHL n=4 mean -0.77; B s1330 th0.75 Supertrap n=71 mean +0.62; B s1330 th1.5 Supertrap n=6 mean -1.25; B s1330 th1.5 gap rule n=19 mean -0.31; B s1330 th1.5 gap rule+PDHL n=19 mean -0.31

### RANGE days (VALIDATION >= 2024-01-01, 12 bp net R per trade; columns: n, mean net R at 12 bp, gross R (= 2 x 6bp mean - 12bp mean), day-cluster CI low, ex-best-5-days mean, median fee/R, mean at 6 bp, DEV n / mean, long n/mean, short n/mean, placebo p, BH, gates)

| Variant | n | mean R | gross R | CI day lo | ex5 | fee/R | 6bp mean | DEV n / mean | long | short | placebo p | BH | gates |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| B cme th0.5 gap rule+PDHL | 152 | +0.301 | +0.605 | -0.905 | -1.023 | 0.38 | +0.453 | 140 / +0.100 | 44/+0.34 | 108/+0.29 | 0.005 | no | fails: ci_trade,ci_day,bh,ex5 |
| B cme th0.5 gap rule | 184 | +0.214 | +0.517 | -0.794 | -0.870 | 0.36 | +0.365 | 194 / +0.806 | 57/+0.30 | 127/+0.17 | 0.010 | no | fails: ci_trade,ci_day,bh,ex5 |
| A 00:00 VWAP, 1d/30m, no 50 filter | 1309 | +0.163 | +0.180 | +0.000 | +0.007 | 0.01 | +0.171 | 1840 / +0.188 | 638/+0.33 | 671/+0.00 | 0.005 | no | fails: bh |
| A 00:00 VWAP, 1d/30m, RSI>50 filter | 1420 | +0.161 | +0.178 | +0.008 | +0.015 | 0.01 | +0.169 | 2120 / +0.135 | 686/+0.31 | 734/+0.03 | 0.005 | no | fails: bh |
| A 13:30 VWAP, 1d/30m, no 50 filter | 1347 | +0.154 | +0.171 | -0.004 | +0.002 | 0.01 | +0.163 | 1915 / +0.174 | 656/+0.32 | 691/-0.01 | 0.005 | no | fails: ci_day,bh |
| A 13:30 VWAP, 1d/30m, RSI>50 filter | 1442 | +0.154 | +0.170 | +0.003 | +0.009 | 0.01 | +0.162 | 2166 / +0.129 | 703/+0.29 | 739/+0.02 | 0.005 | no | fails: bh |
| B s0000 th0.5 gap rule | 153 | -0.129 | +0.137 | -0.708 | -0.731 | 0.29 | +0.004 | 128 / -0.354 | 80/+0.00 | 73/-0.27 | n/a | no | fails: mean_pos,ci_trade,ci_day,placebo,bh,ex5 |
| A 13:30 VWAP, 30m/5m, RSI>50 filter | 58266 | -0.242 | +0.020 | -0.278 | -0.261 | 0.28 | -0.111 | 86761 / -0.292 | 29111/-0.25 | 29155/-0.23 | n/a | no | fails: mean_pos,ci_trade,ci_day,placebo,bh,ex5 |
| A 00:00 VWAP, 30m/5m, RSI>50 filter | 59811 | -0.248 | +0.022 | -0.284 | -0.265 | 0.29 | -0.113 | 87300 / -0.285 | 29702/-0.27 | 30109/-0.23 | n/a | no | fails: mean_pos,ci_trade,ci_day,placebo,bh,ex5 |
| A 13:30 VWAP, 30m/5m, no 50 filter | 64132 | -0.272 | +0.011 | -0.312 | -0.292 | 0.35 | -0.130 | 96036 / -0.316 | 32363/-0.29 | 31769/-0.25 | n/a | no | fails: mean_pos,ci_trade,ci_day,placebo,bh,ex5 |
| A 00:00 VWAP, 30m/5m, no 50 filter | 66089 | -0.276 | +0.015 | -0.315 | -0.295 | 0.37 | -0.131 | 95517 / -0.293 | 32791/-0.29 | 33298/-0.26 | n/a | no | fails: mean_pos,ci_trade,ci_day,placebo,bh,ex5 |
| B s1330 th0.75 gap rule | 379 | -0.397 | -0.105 | -0.804 | -0.822 | 0.31 | -0.251 | 402 / +0.014 | 222/-0.26 | 157/-0.58 | n/a | no | fails: mean_pos,ci_trade,ci_day,placebo,bh,ex5 |
| B s1330 th0.75 gap rule+PDHL | 340 | -0.408 | -0.119 | -0.849 | -0.890 | 0.31 | -0.263 | 357 / +0.065 | 209/-0.22 | 131/-0.71 | n/a | no | fails: mean_pos,ci_trade,ci_day,placebo,bh,ex5 |

UNDERPOWERED (n < 100, no verdict): B cme th0.5 Supertrap n=33 mean -1.11; B cme th1 Supertrap n=15 mean -0.85; B cme th1 gap rule n=75 mean +1.19; B cme th1 gap rule+PDHL n=68 mean +1.28; B s0000 th0.5 Supertrap n=48 mean -0.42; B s0000 th0.5 gap rule+PDHL n=69 mean -0.11; B s0000 th1 Supertrap n=2 mean -1.21; B s0000 th1 gap rule n=24 mean -0.62; B s0000 th1 gap rule+PDHL n=9 mean +0.35; B s1330 th0.75 Supertrap n=81 mean +0.35; B s1330 th1.5 Supertrap n=5 mean -0.02; B s1330 th1.5 gap rule n=59 mean +0.38; B s1330 th1.5 gap rule+PDHL n=58 mean +0.41

### Best VAL row per phase (highest mean net R at 12 bp, n >= 100)

| Phase | Variant | n | mean R | CI day lo | CI trade lo | ex5 | placebo p | BH | gates |
|---|---|---|---|---|---|---|---|---|---|
| UP | A 00:00 VWAP, 1d/30m, RSI>50 filter | 633 | +0.098 | -0.027 | +0.000 | -0.006 | 0.005 | no | fails: ci_day,bh,ex5 |
| DOWN | A 13:30 VWAP, 1d/30m, RSI>50 filter | 886 | -0.039 | -0.140 | -0.113 | -0.132 | n/a | no | fails: mean_pos,ci_trade,ci_day,placebo,bh,ex5 |
| RANGE | B cme th0.5 gap rule+PDHL | 152 | +0.301 | -0.905 | -0.582 | -1.023 | 0.005 | no | fails: ci_trade,ci_day,bh,ex5 |

### Cycle cut (BTC vs 200-week SMA), VALIDATION, descriptive, n >= 100 only

| Cycle | Variant | n | mean R 12bp | CI day lo | 6bp mean |
|---|---|---|---|---|---|
| BEAR | A 00:00 VWAP, 30m/5m, RSI>50 filter | 3430 | -0.370 | -0.494 | -0.227 |
| BEAR | A 00:00 VWAP, 30m/5m, no 50 filter | 3630 | -0.372 | -0.510 | -0.222 |
| BEAR | A 13:30 VWAP, 30m/5m, RSI>50 filter | 3347 | -0.411 | -0.513 | -0.270 |
| BEAR | A 13:30 VWAP, 30m/5m, no 50 filter | 3613 | -0.449 | -0.561 | -0.301 |
| BULL | B cme th1 gap rule+PDHL | 135 | +0.557 | -0.736 | +0.685 |
| BULL | B s0000 th0.5 Supertrap | 132 | +0.465 | -0.649 | +0.599 |
| BULL | B cme th1 gap rule | 164 | +0.352 | -0.767 | +0.484 |
| BULL | B s1330 th0.75 Supertrap | 206 | +0.172 | -0.457 | +0.332 |
| BULL | A 00:00 VWAP, 1d/30m, RSI>50 filter | 2862 | +0.094 | -0.018 | +0.101 |
| BULL | A 13:30 VWAP, 1d/30m, RSI>50 filter | 2910 | +0.089 | -0.015 | +0.097 |
| BULL | A 00:00 VWAP, 1d/30m, no 50 filter | 3175 | +0.069 | -0.020 | +0.077 |
| BULL | A 13:30 VWAP, 1d/30m, no 50 filter | 3285 | +0.065 | -0.032 | +0.072 |
| BULL | B cme th0.5 gap rule | 441 | +0.037 | -0.644 | +0.194 |
| BULL | B s1330 th1.5 gap rule+PDHL | 130 | +0.031 | -0.750 | +0.144 |
| BULL | B s1330 th1.5 gap rule | 137 | -0.018 | -0.704 | +0.093 |
| BULL | B cme th0.5 gap rule+PDHL | 336 | -0.043 | -0.808 | +0.112 |
| BULL | A 13:30 VWAP, 30m/5m, RSI>50 filter | 144071 | -0.226 | -0.254 | -0.100 |
| BULL | A 00:00 VWAP, 30m/5m, RSI>50 filter | 148204 | -0.242 | -0.270 | -0.113 |
| BULL | B s0000 th0.5 gap rule+PDHL | 150 | -0.244 | -0.925 | -0.123 |
| BULL | B s0000 th0.5 gap rule | 343 | -0.253 | -0.618 | -0.127 |
| BULL | A 13:30 VWAP, 30m/5m, no 50 filter | 159365 | -0.257 | -0.286 | -0.121 |
| BULL | A 00:00 VWAP, 30m/5m, no 50 filter | 164780 | -0.269 | -0.299 | -0.128 |
| BULL | B s1330 th0.75 gap rule+PDHL | 808 | -0.335 | -0.583 | -0.197 |
| BULL | B s1330 th0.75 gap rule | 914 | -0.335 | -0.567 | -0.197 |


## Which BTC phase is active now (descriptive only, no forecast)
Cache ends with the 2026-11-12 23:55 UTC bar, so "now" is the state at the 2026-11-12 close; the phase below is the label for 2026-11-13 (from the 11-12 close).
| Item | Value |
|---|---|
| Daily phase | DOWN (ADX14 >= 20, DI- > DI+, SMA20 slope negative); close 71,460 vs SMA20 77,340 |
| Cycle flag | BULL, thin: 5.3% above the 200-week SMA 67,848 |
| HM state (RSI9 / EMA3 / WMA21) | 5m BUY (55.5 / 52.5 / 43.7), 30m BUY (35.7 / 33.9 / 32.3), daily SELL (25.0 / 28.9 / 34.7) |
| Session VWAP | close below both: 00:00 anchor 72,416, 13:30 anchor 71,783 (NK: never buy below VWAP, so the intraday long leg is off) |
| Previous day range | 71,113 to 74,217 |
| What the study says about this phase | every DOWN row with n >= 100 is negative: intraday -0.21 to -0.27 R, positional -0.04 to -0.06 R, B -0.08 to -0.37 R (best -0.039, A positional 13:30 anchor) |

## Notes and limits
- Frozen first: PRE_REG.md, study.py, run.py and test_study.py were committed together (9c4da5a14) before run.py ran; make_result.py only formats results.json.
- Tests: 16 pass; with STUDY_BUG=1 (one-bar look-ahead in the states, bands and entry closes) the causal-prefix and no-edge tests fail (random-walk t = 44), proven in `test_bug_is_caught`.
- Data deviation: the 5m files were copied byte for byte from the shared bulk-data cache (same fetch code, ends 2026-11-12 23:55 UTC; EOS ends 2025-05) into `<local-path>` because a fresh pull ran at about 6 minutes per 100 files. BTC 1d for the cycle flag was pulled fresh into the same folder.
- OURS choices that could be wrong, not NK's: both lines (RSI and EMA3) must sit above the WMA21 for a buy state (neutral otherwise); exit when the trend-frame state is no longer his direction; 5m entry only (10m, 3m, 15m scalp frames not run); positional = daily trend with 30m entry; BB(20, 2); candle RANGE not body for the 50%; Sunday 23:00 UTC / Friday 22:00 UTC as the CME proxy applied to all 20 coins; 20:00 UTC as the prior session close; gap thresholds in daily ATR (0.5 / 1.0 / 0.75 / 1.5); stop buffer 0.1 ATR and floors 0.6 ATR5m or 0.3% (positional 1.5 ATR daily or 1%); 72-bar exit for B. A variant of his rule outside these choices is not covered.
- Power: prereg_gate.py gave BLOCK (MDE 0.364 R + cost 0.4 R vs 0.30 R); B rows are mostly n < 100, so absence of a pass there means untested, not failed.
- Best row per phase is the best of 26 variants and carries selection bias; no row passes, so none is a candidate. The positional RANGE near-miss is four near-duplicate rows (anchor and 50-line change little), i.e. about one hypothesis, with BH over a conservative 78-row family; one confirmation on data not yet seen would be the only fair next step.
