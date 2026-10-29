## C1 Data coverage (DEV 2022-01-01..2024-06-30 UTC)
- kline 5m bars loaded: 262656 (expected 262656); metrics 5m rows loaded: 262528.
| month | metric rows | OI | top-acct | top-pos | global-acct | taker ratio |
|---|---|---|---|---|---|---|
| 2022-01 | 8928 | 100% | 3% | 3% | 40% | 3% |
| 2022-02 | 8064 | 100% | 0% | 0% | 100% | 0% |
| 2022-03 | 8928 | 99% | 0% | 0% | 100% | 0% |
| 2022-04 | 8640 | 100% | 0% | 0% | 100% | 0% |
| 2022-05 | 8928 | 100% | 14% | 14% | 100% | 71% |
| 2022-06 | 8640 | 100% | 79% | 79% | 100% | 100% |
| 2022-07 | 8928 | 100% | 0% | 0% | 100% | 100% |
| 2022-08 | 8928 | 100% | 0% | 0% | 100% | 100% |
| 2022-09 | 8640 | 100% | 0% | 0% | 100% | 100% |
| 2022-10 | 8928 | 100% | 0% | 0% | 100% | 100% |
| 2022-11 | 8640 | 100% | 0% | 0% | 100% | 100% |
| 2022-12 | 8928 | 100% | 56% | 56% | 100% | 100% |
| 2023-01 | 8928 | 100% | 100% | 100% | 100% | 100% |
| 2023-02 | 8064 | 100% | 100% | 100% | 100% | 100% |
| 2023-03 | 8928 | 100% | 100% | 100% | 100% | 100% |
| 2023-04 | 8640 | 100% | 100% | 100% | 100% | 100% |
| 2023-05 | 8928 | 100% | 100% | 100% | 100% | 100% |
| 2023-06 | 8640 | 100% | 100% | 100% | 100% | 100% |
| 2023-07 | 8928 | 100% | 100% | 100% | 100% | 100% |
| 2023-08 | 8928 | 100% | 100% | 100% | 100% | 100% |
| 2023-09 | 8637 | 100% | 100% | 100% | 100% | 100% |
| 2023-10 | 8928 | 100% | 100% | 100% | 100% | 100% |
| 2023-11 | 8640 | 100% | 100% | 100% | 100% | 100% |
| 2023-12 | 8928 | 100% | 100% | 100% | 100% | 100% |
| 2024-01 | 8928 | 100% | 100% | 100% | 100% | 100% |
| 2024-02 | 8227 | 100% | 100% | 100% | 100% | 100% |
| 2024-03 | 8928 | 100% | 100% | 100% | 100% | 100% |
| 2024-04 | 8640 | 100% | 100% | 100% | 100% | 100% |
| 2024-05 | 8928 | 100% | 100% | 100% | 100% | 100% |
| 2024-06 | 8640 | 100% | 100% | 100% | 100% | 100% |

Bars with each series non-null (all DEV bars, n = 262655): r 262655 (100%), D_b 262621 (100%), dOI 262384 (100%), dTA 170759 (65%), dTP 170757 (65%), dGA 257158 (98%)
Share of non-null 5m ratio changes that are exactly 0 (ratio unchanged between snapshots): dTA 0%, dTP 0%, dGA 0%

## C2 Alignment check (decides how a metrics snapshot maps to a kline bar)
| shift s (bars) | Spearman |price chg| vs |OI chg| | Spearman net delta share vs ln(taker ratio) |
|---|---|---|
| -1 | +0.240 (262383) | +0.209 (225656) |
| 0 | +0.331 (262384) | +0.851 (225659) |
| 1 | +0.260 (262383) | +0.045 (225657) |
| 2 | +0.218 (262382) | -0.012 (225655) |
Shift 0 = snapshot at create_time t belongs to the bar that opened at t-5min (A1). The row with the highest value is the alignment this archive follows.

## C3 Windows used (phase-day, weekdays; a window needs >=95% of its kline bars)
| phase | definition (OURS) | windows | with OI | with top-acct | with top-pos | with global-acct |
|---|---|---|---|---|---|---|
| Asia | 00:00-07:00 UTC | 650 | 650 | 422 | 422 | 637 |
| London | 07:00 UTC to 08:30 ET (EDT 12:30 UTC, EST 13:30 UTC) | 650 | 650 | 423 | 423 | 638 |
| PreOpen | 08:30-09:30 ET (the hour before the NYSE cash open) | 650 | 649 | 421 | 421 | 637 |
| USOpen | 09:30-11:30 ET (EDT 13:30-15:30 UTC, EST 14:30-16:30 UTC) | 650 | 649 | 422 | 422 | 637 |
| USPM | 11:30 ET to 21:00 UTC | 650 | 648 | 423 | 423 | 637 |
| Late | 21:00-24:00 UTC | 650 | 648 | 422 | 422 | 637 |
| USOpen (weekend control) | same clock hours, Sat/Sun UTC (no cash market) | 262 | 262 | 171 | 171 | 256 |

## T1 Co-movement per phase: Spearman rho of window changes (n windows); * = outside approx 95% null band 1.96/sqrt(n-3), no multiplicity correction
| pair | Asia | London | PreOpen | USOpen | USPM | Late | USOpen weekend ctrl |
|---|---|---|---|---|---|---|---|
| price chg vs net delta share | +0.73* (650) | +0.77* (650) | +0.74* (650) | +0.78* (650) | +0.78* (650) | +0.68* (650) | +0.70* (262) |
| price chg vs OI chg | +0.07 (650) | +0.18* (650) | +0.08* (649) | +0.11* (649) | +0.11* (648) | -0.03 (648) | +0.16* (262) |
| net delta share vs OI chg | +0.09* (650) | +0.12* (650) | +0.03 (649) | +0.14* (649) | +0.12* (648) | -0.01 (648) | +0.13* (262) |
| price chg vs top-acct L/S chg | -0.60* (422) | -0.67* (423) | -0.41* (421) | -0.74* (422) | -0.73* (423) | -0.32* (422) | -0.49* (171) |
| price chg vs top-pos L/S chg | -0.17* (422) | -0.14* (423) | -0.14* (421) | -0.37* (422) | -0.11* (423) | -0.10* (422) | -0.01 (171) |
| price chg vs global-acct L/S chg | -0.36* (637) | -0.48* (638) | -0.18* (637) | -0.54* (637) | -0.57* (637) | -0.03 (637) | -0.15* (256) |
| net delta share vs top-pos L/S chg | -0.00 (422) | +0.03 (423) | +0.01 (421) | -0.16* (422) | +0.02 (423) | +0.05 (422) | +0.10 (171) |
| OI chg vs top-pos L/S chg | -0.03 (422) | -0.18* (423) | -0.20* (421) | -0.13* (422) | -0.11* (423) | -0.17* (422) | -0.06 (171) |
| OI chg vs top-acct L/S chg | -0.07 (422) | -0.31* (423) | -0.16* (421) | -0.23* (422) | -0.20* (423) | -0.19* (422) | -0.31* (171) |
| top-acct L/S chg vs top-pos L/S chg | +0.25* (422) | +0.06 (423) | -0.04 (421) | +0.26* (422) | +0.04 (423) | -0.19* (422) | -0.13 (171) |
| global-acct L/S chg vs top-pos L/S chg | -0.12* (422) | +0.03 (423) | -0.12* (421) | +0.16* (422) | -0.04 (423) | -0.25* (422) | -0.13 (171) |

## T2 Co-movement at 5m bars, pooled within phase (weekdays): Spearman rho (n bars). Bars are autocorrelated, so * is not reliable here; read size, not stars
| pair | Asia | London | PreOpen | USOpen | USPM | Late |
|---|---|---|---|---|---|---|
| price chg vs net delta share | +0.73 (54600) | +0.73 (45657) | +0.74 (7800) | +0.76 (15584) | +0.73 (40137) | +0.72 (23400) |
| price chg vs OI chg | +0.03 (54581) | +0.03 (45642) | +0.03 (7788) | +0.03 (15563) | +0.03 (40032) | +0.04 (23328) |
| net delta share vs OI chg | +0.03 (54581) | +0.03 (45642) | +0.03 (7788) | +0.03 (15547) | +0.03 (40029) | +0.04 (23328) |
| price chg vs top-acct L/S chg | -0.00 (35443) | +0.02 (29665) | +0.01 (5052) | -0.10 (10115) | -0.03 (26028) | -0.01 (15192) |
| price chg vs top-pos L/S chg | +0.07 (35443) | +0.06 (29663) | +0.03 (5052) | +0.01 (10115) | +0.01 (26028) | +0.02 (15192) |
| net delta share vs top-pos L/S chg | +0.14 (35443) | +0.14 (29663) | +0.10 (5052) | +0.10 (10099) | +0.10 (26025) | +0.09 (15192) |
| OI chg vs top-pos L/S chg | -0.09 (35443) | -0.09 (29658) | -0.14 (5052) | -0.14 (10115) | -0.11 (26028) | -0.11 (15192) |
| top-acct L/S chg vs top-pos L/S chg | -0.10 (35443) | -0.12 (29654) | -0.15 (5052) | -0.09 (10115) | -0.13 (26028) | -0.16 (15192) |

## T3 Divergence counts per phase (weekday windows). Share = windows where the two signs differ; 50% = no relation (OURS reading)
| sign differs | Asia | London | PreOpen | USOpen | USPM | Late | USOpen weekend ctrl |
|---|---|---|---|---|---|---|---|
| price vs net delta | 151/650 = 23% | 119/650 = 18% | 124/650 = 19% | 119/650 = 18% | 133/650 = 20% | 160/650 = 25% | 52/262 = 20% |
| price vs OI | 306/650 = 47% | 304/650 = 47% | 312/649 = 48% | 305/649 = 47% | 322/648 = 50% | 327/648 = 50% | 119/262 = 45% |
| price vs top-pos L/S | 241/422 = 57% | 229/423 = 54% | 238/421 = 57% | 262/422 = 62% | 223/423 = 53% | 214/422 = 51% | 79/171 = 46% |
| price vs top-acct L/S | 303/422 = 72% | 312/423 = 74% | 262/421 = 62% | 332/422 = 79% | 317/423 = 75% | 265/422 = 63% | 114/171 = 67% |
| top-acct vs top-pos L/S | 170/422 = 40% | 201/423 = 48% | 208/421 = 49% | 176/422 = 42% | 220/423 = 52% | 243/422 = 58% | 101/171 = 59% |
| global-acct vs top-pos L/S | 239/422 = 57% | 202/423 = 48% | 225/421 = 53% | 192/422 = 45% | 230/423 = 54% | 242/422 = 57% | 96/171 = 56% |
| net delta vs OI | 311/650 = 48% | 307/650 = 47% | 338/649 = 52% | 294/649 = 45% | 289/648 = 45% | 322/648 = 50% | 117/262 = 45% |

### T3b Price/OI four states per phase (weekday windows; counts)
| phase | n | price up, OI up | price up, OI down | price down, OI up | price down, OI down |
|---|---|---|---|---|---|
| Asia | 650 | 213 | 107 | 199 | 131 |
| London | 650 | 267 | 78 | 226 | 79 |
| PreOpen | 649 | 218 | 98 | 214 | 119 |
| USOpen | 649 | 165 | 136 | 169 | 179 |
| USPM | 648 | 103 | 236 | 86 | 223 |
| Late | 648 | 119 | 241 | 86 | 202 |
| USOpen weekend ctrl | 262 | 79 | 54 | 65 | 64 |

## T4 Lead-lag at 5m bars within phase (weekdays). Spearman corr(x_t, y_t+k), same window only; k>0 = x leads y. as: rho at k=0; peak |rho| lag and value; n bars at k=0
| x -> y | Asia | London | PreOpen | USOpen | USPM | Late |
|---|---|---|---|---|---|---|
| net delta share -> price chg | rho0 +0.73; peak k=+0 rho +0.73; n=54600 | rho0 +0.73; peak k=+0 rho +0.73; n=45657 | rho0 +0.74; peak k=+0 rho +0.74; n=7800 | rho0 +0.76; peak k=+0 rho +0.76; n=15584 | rho0 +0.73; peak k=+0 rho +0.73; n=40137 | rho0 +0.72; peak k=+0 rho +0.72; n=23400 |
| net delta share -> OI chg | rho0 +0.03; peak k=+0 rho +0.03; n=54581 | rho0 +0.03; peak k=+0 rho +0.03; n=45642 | rho0 +0.03; peak k=+11 rho -0.06; n=7788 | rho0 +0.03; peak k=+0 rho +0.03; n=15547 | rho0 +0.03; peak k=+0 rho +0.03; n=40029 | rho0 +0.04; peak k=+0 rho +0.04; n=23328 |
| price chg -> OI chg | rho0 +0.03; peak k=+0 rho +0.03; n=54581 | rho0 +0.03; peak k=+0 rho +0.03; n=45642 | rho0 +0.03; peak k=+0 rho +0.03; n=7788 | rho0 +0.03; peak k=+0 rho +0.03; n=15563 | rho0 +0.03; peak k=+0 rho +0.03; n=40032 | rho0 +0.04; peak k=+0 rho +0.04; n=23328 |
| net delta share -> top-pos L/S chg | rho0 +0.14; peak k=+0 rho +0.14; n=35443 | rho0 +0.14; peak k=+0 rho +0.14; n=29663 | rho0 +0.10; peak k=+0 rho +0.10; n=5052 | rho0 +0.10; peak k=+0 rho +0.10; n=10099 | rho0 +0.10; peak k=+0 rho +0.10; n=26025 | rho0 +0.09; peak k=+0 rho +0.09; n=15192 |
| price chg -> top-pos L/S chg | rho0 +0.07; peak k=+0 rho +0.07; n=35443 | rho0 +0.06; peak k=+1 rho -0.06; n=29663 | rho0 +0.03; peak k=+1 rho -0.08; n=5052 | rho0 +0.01; peak k=+1 rho -0.08; n=10115 | rho0 +0.01; peak k=+1 rho -0.09; n=26028 | rho0 +0.02; peak k=+1 rho -0.08; n=15192 |
| price chg -> top-acct L/S chg | rho0 -0.00; peak k=+1 rho +0.11; n=35443 | rho0 +0.02; peak k=+5 rho -0.11; n=29665 | rho0 +0.01; peak k=+2 rho -0.13; n=5052 | rho0 -0.10; peak k=+2 rho -0.22; n=10115 | rho0 -0.03; peak k=+2 rho -0.14; n=26028 | rho0 -0.01; peak k=+5 rho -0.07; n=15192 |
| OI chg -> top-pos L/S chg | rho0 -0.09; peak k=+0 rho -0.09; n=35443 | rho0 -0.09; peak k=+0 rho -0.09; n=29658 | rho0 -0.14; peak k=+0 rho -0.14; n=5052 | rho0 -0.14; peak k=+0 rho -0.14; n=10115 | rho0 -0.11; peak k=+0 rho -0.11; n=26028 | rho0 -0.11; peak k=+0 rho -0.11; n=15192 |
| OI chg -> top-acct L/S chg | rho0 -0.06; peak k=+0 rho -0.06; n=35443 | rho0 -0.06; peak k=+0 rho -0.06; n=29664 | rho0 -0.06; peak k=-11 rho -0.08; n=5052 | rho0 -0.06; peak k=+0 rho -0.06; n=10115 | rho0 -0.07; peak k=+0 rho -0.07; n=26028 | rho0 -0.05; peak k=+0 rho -0.05; n=15192 |
| top-acct L/S chg -> top-pos L/S chg | rho0 -0.10; peak k=+0 rho -0.10; n=35443 | rho0 -0.12; peak k=+0 rho -0.12; n=29654 | rho0 -0.15; peak k=+0 rho -0.15; n=5052 | rho0 -0.09; peak k=-1 rho +0.09; n=10115 | rho0 -0.13; peak k=+0 rho -0.13; n=26028 | rho0 -0.16; peak k=+0 rho -0.16; n=15192 |
Lags run -12..+12 bars (+-60 min). A peak at k=0 means no lead is visible at 5m; a peak at |k|>=1 is a candidate lead only if its rho is clearly bigger than rho at k=0 (OURS rule: gap >= 0.05).

## T5 Stability of the US Open window co-movement by half-year (weekdays; Spearman, n)
| pair | 2022H1 | 2022H2 | 2023H1 | 2023H2 | 2024H1 |
|---|---|---|---|---|---|
| price chg vs net delta share | +0.85 (129) | +0.75 (131) | +0.88 (130) | +0.76 (130) | +0.74 (130) |
| price chg vs OI chg | +0.02 (129) | +0.06 (131) | +0.26 (130) | +0.12 (130) | +0.13 (129) |
| net delta share vs OI chg | +0.04 (129) | +0.09 (131) | +0.24 (130) | +0.13 (130) | +0.13 (129) |
| price chg vs top-pos L/S chg | n/a | n/a | -0.25 (130) | -0.32 (130) | -0.49 (129) |
| OI chg vs top-pos L/S chg | n/a | n/a | -0.11 (130) | -0.23 (130) | -0.16 (129) |

## T6 What each phase looks like (weekday windows; median |window price chg| in bp, median |net delta share|, median |OI chg| in bp, median window volume in BTC)
| phase | windows | median abs price chg bp | median abs net delta share | median abs OI chg bp | median volume BTC | share windows OI up | mean signed OI chg bp |
|---|---|---|---|---|---|---|---|
| Asia | 650 | 55 | 0.025 | 112 | 78337 | 63% | +47 |
| London | 650 | 52 | 0.023 | 122 | 82824 | 76% | +112 |
| PreOpen | 650 | 28 | 0.044 | 46 | 20648 | 67% | +23 |
| USOpen | 650 | 58 | 0.030 | 85 | 64473 | 51% | +6 |
| USPM | 650 | 67 | 0.024 | 146 | 102817 | 29% | -111 |
| Late | 650 | 36 | 0.035 | 72 | 31962 | 32% | -63 |

## T7 Carry-over between adjacent phases, same weekday: Spearman rho of window change in phase A vs the next phase B (n days)
| series | Asia->London | London->PreOpen | PreOpen->USOpen | USOpen->USPM | USPM->Late |
|---|---|---|---|---|---|
| price chg | +0.02 (650) | -0.06 (650) | -0.05 (650) | +0.07 (650) | -0.05 (650) |
| net delta share | +0.10* (650) | -0.05 (650) | -0.02 (650) | +0.13* (650) | +0.11* (650) |
| OI chg | +0.03 (650) | +0.03 (649) | +0.02 (649) | +0.06 (648) | +0.01 (648) |
| top-acct L/S chg | +0.24* (422) | +0.15* (421) | +0.20* (421) | +0.24* (422) | +0.29* (422) |
| top-pos L/S chg | -0.09 (422) | -0.04 (421) | -0.03 (421) | -0.01 (422) | -0.11* (422) |

## T8 Does the PreOpen state go with what the US Open window does? Spearman rho (n days), weekdays
| pair | rho (n) |
|---|---|
| PreOpen price chg -> USOpen price chg | -0.05 (650) |
| PreOpen net delta share -> USOpen price chg | -0.00 (650) |
| PreOpen OI chg -> USOpen price chg | +0.06 (649) |
| PreOpen top-pos L/S chg -> USOpen price chg | -0.07 (421) |
| PreOpen top-acct L/S chg -> USOpen price chg | +0.02 (421) |
| PreOpen net delta share -> USOpen net delta share | -0.02 (650) |
| PreOpen OI chg -> USOpen OI chg | +0.02 (649) |
| PreOpen OI chg -> USOpen net delta share | +0.02 (649) |
