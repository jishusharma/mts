# Auction-context event census (card auction-context-event-census-1108, 2026-11-08)

**Result: the classifier does not pay as a standalone entry. Over 7y of 1h data FAST_REJECTION fades are -0.087 R fee-net per trade (gate-pass n=1871, SE 0.022); on the 5m window the only positive cell is n=10 (+0.089 R, SE 0.312, noise). KNIFE_SKIP does not protect anything measurable (7y counterfactual fade -0.115 R, n=152, SE 0.078, about the same as the non-knife fades).** Status: descriptive census, not a strategy claim, no layer change.

Reproduce: `python MyTradingSys/research/tom_fabio_course_correction_2026-11-07/auction_census.py <cache_dir> > out.md` (public Bybit/Binance market data, fetched and cached; the tables below are that output, unedited). Tests: `python -m pytest MyTradingSys/research/tom_fabio_course_correction_2026-11-07/test_auction_census.py -q` (7 passed).

## Context
- Regime: none gated, because the card asks for every event the classifier fires on; regime reported as a split (Regime mix line below) and htf with/against.
- Phase: none, because the classifier has no phase input yet.
- Session: none, because not part of the classifier; not split here.
- Entry: close of the bar on which the verdict first fires (zero lookahead: classifier sees bars[t-59..t]; outcome from t+1..t+H).

## Method
- Window A: 5m, Bybit linear BTCUSDT, 2026-10-03 00:00 .. 2026-11-07 12:40 UTC, 10233 bars (the same count as CENSUS_5m header; parsed from the fetch, first line of the output).
- Window B: 1h, Binance SPOT BTCUSDT, 2019-11-08 .. 2026-11-07 (7y, 61788 bars fetched from 2019-10-20). This laptop has no F: drive; the 7y data came from the public API instead. The literal request "daily bars" was NOT RUN: `btc_cycles_2026-11/btc_daily.csv` has no volume or open, and the classifier needs volume (rel_vol >= 2.0) and cannot form a volume profile from daily H/L/C. Daily bars give the bias only. 1h is the coarsest bar that carries volume; the classifier thresholds then count hours (6 bars = 6 h, not 30 m), which is a deviation.
- Levels per UTC day from bars that closed before the day: prior-day VAL/VAH (compute_volume_profile, spread_range, bin = 0.067% of prior close, 70% share), prior-day low/high (PDL/PDH), prior-week low/high (PWL/PWH, last full ISO week). The approach must start inside the level (close 12 bars earlier on the inside).
- One event per level per cooldown (48 bars on 5m, 12 on 1h): the first bar on which the verdict is in {FAST_REJECTION, WEAK_REJECTION, REJECTED_KNIFE_SKIP, ACCEPTED, STALE_REJECTION}. ACCEPTED with trade_bias balance_hold is reported as ACCEPTED_HOLD (no trade).
- Trades: fades (FAST/WEAK/KNIFE): enter the close, stop = sweep extreme (structural beyond the wick), target 1R, horizon H=24 bars, open trades marked at the last close. KNIFE rows are the counterfactual of the fade the classifier tells you to skip. ACCEPTED: continuation, stop = the level, target 1R, H=24. Stop wins a same-bar tie.
- Fee-net R = gross R - fee_r, fee_r = 10 bps round trip / stop distance in bps. "all" = every event; "gate-pass" = fee_r <= 0.25 only (the audit's own rule). Events overlap in time and across six levels, so SE is a lower bound on the real uncertainty.

## Parameter labels
| Parameter | Value | Label |
|---|---|---|
| round-trip taker fee | 10 bps | SOURCED (fees.py via auction_context.DEFAULT_TAKER_RT_BPS) |
| fee_r gate | <= 0.25 R | SOURCED (d-stops-follow-trade-1106, DEFAULT_MAX_FRICTION_R) |
| rel_vol >= 2.0, knife 2% drop and <25% bounce, reclaim <= 3 bars | inside classifier | knife SOURCED to wick_census.py (itself OURS); rel_vol 2.0 OURS |
| acceptance 6 bars | classifier | SOURCED to accept80.py on 2x30m, OURS on 5m and 1h |
| window 60 bars, setup-back 12, cooldown 48/12, H=24, R=1 | this script | OURS |
| stop = sweep extreme with no buffer, accepted stop = level | this script | OURS |
| htf bias = prior-day close vs SMA20; regime band +-2% | this script | OURS |
| levels set (VA, PD, PW) and 0.067% profile bin | this script | OURS |

DECISION (OURS): the 7y leg uses Binance spot 1h in place of the missing local daily/F: data; spot vs perp differences are not corrected.

## Output (command output, unedited)

# bars: bybit 5m fetched 14107 from 2026-09-20; census window bars 10233 2026-10-03 00:00 .. 2026-11-07 12:40 UTC
### A. 5m window 2026-10-03..11-07 (Bybit linear BTCUSDT)

Events by verdict x level (parsed from the event list):

| verdict | VAL | VAH | PDL | PDH | PWL | PWH | total |
|---|---|---|---|---|---|---|---|
| FAST_REJECTION | 17 | 12 | 16 | 16 | 5 | 1 | 67 |
| WEAK_REJECTION | 3 | 5 | 2 | 0 | 1 | 0 | 11 |
| REJECTED_KNIFE_SKIP | 0 | 0 | 1 | 1 | 1 | 0 | 3 |
| ACCEPTED | 12 | 14 | 15 | 6 | 8 | 1 | 56 |
| ACCEPTED_HOLD | 5 | 13 | 1 | 6 | 4 | 0 | 29 |
| STALE_REJECTION | 6 | 6 | 5 | 1 | 0 | 1 | 19 |

Forward result by verdict (FAST/WEAK/KNIFE = fade the sweep; ACCEPTED = continuation, stop at the level; KNIFE is the counterfactual of the skipped fade):

| verdict | events | simulated | tgt/stop/open (all) | gross R | fee R | net R +-SE (all) | gate-pass n (tgt/stp/open) | net R (gate-pass) | SE |
|---|---|---|---|---|---|---|---|---|---|
| FAST_REJECTION | 67 | 67 | 28/38/1 | -0.152 | 0.925 | -1.077 +-0.215 | 10 (6/3/1) | +0.089 | 0.312 |
| WEAK_REJECTION | 11 | 11 | 5/6/0 | -0.091 | 1.317 | -1.408 +-0.322 | 0 | +nan | nan |
| REJECTED_KNIFE_SKIP | 3 | 3 | 2/1/0 | +0.333 | 0.300 | +0.034 +-0.653 | 0 | +nan | nan |
| ACCEPTED | 56 | 56 | 24/27/5 | -0.057 | 0.722 | -0.780 +-0.218 | 15 (6/5/4) | -0.106 | 0.238 |

By level family (VA edges vs prior-day extremes vs prior-week extremes):

| verdict / family | events | simulated | tgt/stop/open (all) | gross R | fee R | net R +-SE (all) | gate-pass n (tgt/stp/open) | net R (gate-pass) | SE |
|---|---|---|---|---|---|---|---|---|---|
| FAST_REJECTION / VA | 29 | 29 | 13/16/0 | -0.103 | 1.307 | -1.410 +-0.420 | 2 (1/1/0) | -0.188 | 1.031 |
| FAST_REJECTION / PD | 32 | 32 | 13/18/1 | -0.161 | 0.691 | -0.852 +-0.223 | 6 (3/2/1) | -0.066 | 0.417 |
| FAST_REJECTION / PW | 6 | 6 | 2/4/0 | -0.333 | 0.330 | -0.664 +-0.473 | 2 (2/0/0) | +0.831 | 0.044 |
| WEAK_REJECTION / VA | 8 | 8 | 4/4/0 | +0.000 | 1.427 | -1.427 +-0.443 | 0 | +nan | nan |
| WEAK_REJECTION / PD | 2 | 2 | 1/1/0 | +0.000 | 1.323 | -1.323 +-0.437 | 0 | +nan | nan |
| WEAK_REJECTION / PW | 1 | 1 | 0/1/0 | -1.000 | 0.429 | -1.429 +-nan | 0 | +nan | nan |
| REJECTED_KNIFE_SKIP / VA | 0 | 0 | - | - | - | - | - | - | - |
| REJECTED_KNIFE_SKIP / PD | 2 | 2 | 1/1/0 | +0.000 | 0.313 | -0.313 +-0.959 | 0 | +nan | nan |
| REJECTED_KNIFE_SKIP / PW | 1 | 1 | 1/0/0 | +1.000 | 0.274 | +0.726 +-nan | 0 | +nan | nan |
| ACCEPTED / VA | 26 | 26 | 11/15/0 | -0.154 | 0.784 | -0.938 +-0.302 | 4 (3/1/0) | +0.300 | 0.517 |
| ACCEPTED / PD | 21 | 21 | 11/5/5 | +0.276 | 0.697 | -0.421 +-0.407 | 7 (2/1/4) | -0.010 | 0.280 |
| ACCEPTED / PW | 9 | 9 | 2/7/0 | -0.556 | 0.605 | -1.160 +-0.411 | 4 (1/3/0) | -0.679 | 0.531 |

By htf bias alignment of the trade (with = long in bull / short in bear; bias = prior-day close vs SMA20, OURS):

| verdict / align | events | simulated | tgt/stop/open (all) | gross R | fee R | net R +-SE (all) | gate-pass n (tgt/stp/open) | net R (gate-pass) | SE |
|---|---|---|---|---|---|---|---|---|---|
| FAST_REJECTION / with | 31 | 31 | 15/15/1 | -0.005 | 0.877 | -0.883 +-0.292 | 3 (1/1/1) | -0.271 | 0.578 |
| FAST_REJECTION / against | 36 | 36 | 13/23/0 | -0.278 | 0.967 | -1.244 +-0.313 | 7 (5/2/0) | +0.243 | 0.384 |
| WEAK_REJECTION / with | 5 | 5 | 2/3/0 | -0.200 | 1.774 | -1.974 +-0.491 | 0 | +nan | nan |
| WEAK_REJECTION / against | 6 | 6 | 3/3/0 | +0.000 | 0.937 | -0.937 +-0.348 | 0 | +nan | nan |
| REJECTED_KNIFE_SKIP / with | 3 | 3 | 2/1/0 | +0.333 | 0.300 | +0.034 +-0.653 | 0 | +nan | nan |
| REJECTED_KNIFE_SKIP / against | 0 | 0 | - | - | - | - | - | - | - |
| ACCEPTED / with | 32 | 32 | 16/14/2 | +0.074 | 0.540 | -0.465 +-0.221 | 9 (4/4/1) | -0.110 | 0.347 |
| ACCEPTED / against | 24 | 24 | 8/13/3 | -0.233 | 0.966 | -1.199 +-0.404 | 6 (2/1/3) | -0.100 | 0.328 |

Event days with at least one event: 34. Events by regime (bull/bear/range on the event day): bull=15, bear=88, range=82, n/a=0.

Regime mix (window days, prior-day close vs SMA20 +-2%, OURS): bull 5/36 / bear 18/36 / range 13/36

# bars: binance 1h 61788 from 2019-10-20

### B. 7y 1h (Binance spot BTCUSDT 2019-11-08..2026-11-07)

Events by verdict x level (parsed from the event list):

| verdict | VAL | VAH | PDL | PDH | PWL | PWH | total |
|---|---|---|---|---|---|---|---|
| FAST_REJECTION | 426 | 391 | 553 | 480 | 144 | 154 | 2148 |
| WEAK_REJECTION | 449 | 534 | 274 | 353 | 27 | 54 | 1691 |
| REJECTED_KNIFE_SKIP | 17 | 22 | 38 | 60 | 18 | 23 | 178 |
| ACCEPTED | 914 | 1081 | 452 | 601 | 211 | 296 | 3555 |
| ACCEPTED_HOLD | 64 | 68 | 25 | 18 | 11 | 22 | 208 |
| STALE_REJECTION | 1248 | 1124 | 130 | 147 | 137 | 135 | 2921 |

Forward result by verdict (FAST/WEAK/KNIFE = fade the sweep; ACCEPTED = continuation, stop at the level; KNIFE is the counterfactual of the skipped fade):

| verdict | events | simulated | tgt/stop/open (all) | gross R | fee R | net R +-SE (all) | gate-pass n (tgt/stp/open) | net R (gate-pass) | SE |
|---|---|---|---|---|---|---|---|---|---|
| FAST_REJECTION | 2148 | 2148 | 947/965/236 | -0.010 | 0.154 | -0.164 +-0.021 | 1871 (835/800/236) | -0.087 | 0.022 |
| WEAK_REJECTION | 1691 | 1691 | 853/799/39 | +0.028 | 0.272 | -0.244 +-0.028 | 1158 (599/520/39) | -0.072 | 0.029 |
| REJECTED_KNIFE_SKIP | 178 | 178 | 79/85/14 | -0.041 | 0.153 | -0.194 +-0.074 | 152 (69/69/14) | -0.115 | 0.078 |
| ACCEPTED | 3555 | 3555 | 1484/1667/404 | -0.057 | 0.540 | -0.597 +-0.186 | 2798 (1203/1191/404) | -0.096 | 0.018 |

By level family (VA edges vs prior-day extremes vs prior-week extremes):

| verdict / family | events | simulated | tgt/stop/open (all) | gross R | fee R | net R +-SE (all) | gate-pass n (tgt/stp/open) | net R (gate-pass) | SE |
|---|---|---|---|---|---|---|---|---|---|
| FAST_REJECTION / VA | 817 | 817 | 368/337/112 | +0.036 | 0.143 | -0.107 +-0.035 | 725 (329/284/112) | -0.039 | 0.035 |
| FAST_REJECTION / PD | 1033 | 1033 | 463/482/88 | -0.023 | 0.166 | -0.189 +-0.031 | 879 (403/388/88) | -0.096 | 0.032 |
| FAST_REJECTION / PW | 298 | 298 | 116/146/36 | -0.091 | 0.140 | -0.230 +-0.055 | 267 (103/128/36) | -0.186 | 0.058 |
| WEAK_REJECTION / VA | 983 | 983 | 500/454/29 | +0.042 | 0.246 | -0.204 +-0.033 | 708 (359/320/29) | -0.084 | 0.037 |
| WEAK_REJECTION / PD | 627 | 627 | 318/302/7 | +0.026 | 0.316 | -0.290 +-0.051 | 393 (213/173/7) | -0.037 | 0.050 |
| WEAK_REJECTION / PW | 81 | 81 | 35/43/3 | -0.119 | 0.253 | -0.372 +-0.120 | 57 (27/27/3) | -0.160 | 0.132 |
| REJECTED_KNIFE_SKIP / VA | 39 | 39 | 16/19/4 | -0.094 | 0.145 | -0.239 +-0.159 | 35 (15/16/4) | -0.152 | 0.163 |
| REJECTED_KNIFE_SKIP / PD | 98 | 98 | 47/49/2 | -0.017 | 0.172 | -0.189 +-0.103 | 81 (41/38/2) | -0.075 | 0.111 |
| REJECTED_KNIFE_SKIP / PW | 41 | 41 | 16/17/8 | -0.049 | 0.114 | -0.163 +-0.142 | 36 (13/15/8) | -0.170 | 0.150 |
| ACCEPTED / VA | 1995 | 1995 | 807/980/208 | -0.090 | 0.604 | -0.694 +-0.288 | 1542 (654/680/208) | -0.116 | 0.024 |
| ACCEPTED / PD | 1053 | 1053 | 444/481/128 | -0.043 | 0.584 | -0.628 +-0.311 | 838 (360/350/128) | -0.090 | 0.032 |
| ACCEPTED / PW | 507 | 507 | 233/206/68 | +0.043 | 0.197 | -0.154 +-0.048 | 418 (189/161/68) | -0.030 | 0.045 |

By htf bias alignment of the trade (with = long in bull / short in bear; bias = prior-day close vs SMA20, OURS):

| verdict / align | events | simulated | tgt/stop/open (all) | gross R | fee R | net R +-SE (all) | gate-pass n (tgt/stp/open) | net R (gate-pass) | SE |
|---|---|---|---|---|---|---|---|---|---|
| FAST_REJECTION / with | 867 | 867 | 377/404/86 | -0.040 | 0.147 | -0.187 +-0.034 | 756 (334/336/86) | -0.117 | 0.035 |
| FAST_REJECTION / against | 1281 | 1281 | 570/561/150 | +0.010 | 0.158 | -0.148 +-0.028 | 1115 (501/464/150) | -0.066 | 0.028 |
| WEAK_REJECTION / with | 834 | 834 | 428/391/15 | +0.044 | 0.283 | -0.239 +-0.042 | 573 (296/262/15) | -0.076 | 0.041 |
| WEAK_REJECTION / against | 857 | 857 | 425/408/24 | +0.013 | 0.261 | -0.248 +-0.036 | 585 (303/258/24) | -0.068 | 0.041 |
| REJECTED_KNIFE_SKIP / with | 56 | 56 | 25/24/7 | -0.000 | 0.174 | -0.174 +-0.131 | 46 (20/19/7) | -0.111 | 0.140 |
| REJECTED_KNIFE_SKIP / against | 122 | 122 | 54/61/7 | -0.060 | 0.144 | -0.204 +-0.090 | 106 (49/50/7) | -0.117 | 0.095 |
| ACCEPTED / with | 2153 | 2153 | 917/996/240 | -0.047 | 0.532 | -0.579 +-0.266 | 1719 (755/724/240) | -0.084 | 0.023 |
| ACCEPTED / against | 1402 | 1402 | 567/671/164 | -0.073 | 0.553 | -0.626 +-0.236 | 1079 (448/467/164) | -0.113 | 0.029 |

Event days with at least one event: 2538. Events by regime (bull/bear/range on the event day): bull=4340, bear=3428, range=2933, n/a=0.

Regime mix (7y days, same rule, OURS): bull 1032/2557 / bear 830/2557 / range 695/2557

Per-year FAST_REJECTION (gate-pass) net R, 7y 1h:

| year | n gate-pass | net R |
|---|---|---|
| 2019 | 53 | -0.111 |
| 2020 | 266 | -0.082 |
| 2021 | 208 | -0.079 |
| 2022 | 262 | -0.183 |
| 2023 | 313 | -0.054 |
| 2024 | 296 | -0.048 |
| 2025 | 266 | -0.056 |
| 2026 | 207 | -0.120 |

Regime mix: 5m window days bull 5/36, bear 18/36, range 13/36; 7y days bull 1032/2557, bear 830/2557, range 695/2557 (rule above, OURS). The 5m window is a bear-dominated 5 weeks (the same weeks as the wick census) and says nothing about a bull regime; the 7y leg is mixed.

## Reading
- Counts (5m window): FAST_REJECTION 67, WEAK 11, KNIFE_SKIP 3, ACCEPTED 56 (+29 hold), STALE 19. Hit rate of the 67 fades: 28 target / 38 stop / 1 open = 42% target first, in line with the wick census 43% (CENSUS_5m).
- Fees are the story on 5m: mean fee_r of the 67 FAST_REJECTION trades is 0.925 R because wick stops are 5-15 bps; only 10 of 67 pass the 0.25 R gate.
- 7y 1h: FAST_REJECTION 2148 events, 947 target / 965 stop / 236 open, gross -0.010 R, net -0.164 R all, -0.087 R gate-pass. Every year 2019..2026 is negative (-0.048 to -0.183). htf with (-0.117) vs against (-0.066): no with-trend edge for fades; ACCEPTED with -0.084 vs against -0.113 gate-pass: also nothing.
- KNIFE_SKIP: 3 events on 5m, 178 on 1h; counterfactual fade net -0.115 R gate-pass, not worse than the others beyond noise, so the skip is neutral, not proven protective.
- Not shown here and not claimed: any filter on top (session, divergence, confluence, sweep size), maker entry, limit-order fills, perp funding. The classifier alone is a label, not an edge.

## Noticed
- The audit's "4 winners" are not representative: the 5m window has 67 FAST_REJECTION events and 42% win.
