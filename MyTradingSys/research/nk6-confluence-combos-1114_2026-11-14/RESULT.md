VERDICT: FAIL - no combination passes (all 33 combos negative net of 12 bp on VALIDATION; best net L2&L3&L5 -0.112R)

Study nk6-confluence-combos-1114: five NK layers as 15m booleans, agreement counted in the phase direction, every single/pair/triple + count buckets, 20 Binance spot coins, DEV <= 2023-12-31, VALIDATION >= 2024-01-01. PRE_REG.md committed before any outcome (sha cc7de58ca). Trade: entry next open, stop max(1 ATR, 0.5%), target 2R, 24-bar time exit, fee 12 bp taker primary.

## Context
Phase for each UTC day from the prior daily close: UP = ADX(14)>=20, +DI>-DI, SMA20 rising 5d; DOWN = mirror; else RANGE. Primary rows trade only the phase-matched direction (RANGE = both). Control rows (opposite direction in UP/DOWN) are shown for comparison only.

Regime mix: DEV bars (all coins): UP 31% / RANGE 36% / DOWN 32%. VAL bars: UP 25% / RANGE 40% / DOWN 35%.
Phase of VAL trades: n=1 UP 18% / RANGE 56% / DOWN 26%; n>=4 UP 18% / RANGE 57% / DOWN 24%.

## Matched-row table (VALIDATION, 12 bp taker, phase-matched)
Fee col = mean fee as a fraction of R. Gross = mean R before fees. BH q over 66 primary rows (33 combos x 12/6 bp). Pass = all gates.

| combo | n DEV | n VAL | win % | mean net R | gross R | fee/R | CI lo trade | CI lo day | placebo p | BH q | ex-best-5 | 6 bp mean | control mean | pass |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| L1 | 57131 | 43774 | 35.1 | -0.188 | 0.018 | 0.21 | -0.201 | -0.209 | 0.029 | 1.000 | -0.193 | -0.085 | -0.185 | no |
| L2 | 111898 | 77108 | 34.3 | -0.205 | -0.002 | 0.20 | -0.214 | -0.220 | 0.816 | 1.000 | -0.209 | -0.103 | -0.191 | no |
| L3 | 107190 | 76236 | 34.8 | -0.197 | 0.008 | 0.21 | -0.207 | -0.212 | 0.299 | 1.000 | -0.201 | -0.095 | -0.205 | no |
| L4 | 262177 | 178725 | 34.2 | -0.204 | -0.003 | 0.20 | -0.210 | -0.218 | 0.925 | 1.000 | -0.208 | -0.104 | -0.191 | no |
| L5 | 39173 | 28311 | 33.6 | -0.235 | -0.039 | 0.20 | -0.251 | -0.267 | 1.000 | 1.000 | -0.244 | -0.137 | -0.159 | no |
| L1&L2 | 22307 | 17236 | 35.4 | -0.174 | 0.030 | 0.20 | -0.193 | -0.204 | 0.006 | 1.000 | -0.184 | -0.072 | -0.162 | no |
| L1&L3 | 24145 | 19465 | 35.4 | -0.182 | 0.025 | 0.21 | -0.202 | -0.209 | 0.029 | 1.000 | -0.190 | -0.079 | -0.205 | no |
| L1&L4 | 51869 | 40195 | 35.2 | -0.181 | 0.025 | 0.21 | -0.195 | -0.204 | 0.003 | 1.000 | -0.188 | -0.078 | -0.176 | no |
| L1&L5 | 4817 | 3190 | 34.8 | -0.190 | 0.005 | 0.20 | -0.235 | -0.264 | 0.320 | 1.000 | -0.237 | -0.092 | -0.192 | no |
| L2&L3 | 46105 | 33553 | 34.8 | -0.191 | 0.014 | 0.20 | -0.205 | -0.211 | 0.089 | 1.000 | -0.197 | -0.088 | -0.189 | no |
| L2&L4 | 104601 | 72461 | 34.3 | -0.202 | 0.001 | 0.20 | -0.211 | -0.219 | 0.656 | 1.000 | -0.207 | -0.101 | -0.197 | no |
| L2&L5 | 13532 | 9191 | 34.4 | -0.206 | -0.010 | 0.20 | -0.233 | -0.249 | 0.636 | 1.000 | -0.221 | -0.108 | -0.139 | no |
| L3&L4 | 106102 | 75877 | 34.8 | -0.193 | 0.012 | 0.21 | -0.202 | -0.210 | 0.075 | 1.000 | -0.197 | -0.090 | -0.198 | no |
| L3&L5 | 8803 | 6188 | 35.0 | -0.182 | 0.013 | 0.20 | -0.215 | -0.232 | 0.102 | 1.000 | -0.201 | -0.085 | -0.182 | no |
| L4&L5 | 30504 | 22730 | 33.3 | -0.242 | -0.048 | 0.19 | -0.258 | -0.277 | 1.000 | 1.000 | -0.251 | -0.145 | -0.165 | no |
| L1&L2&L3 | 9324 | 7744 | 35.6 | -0.166 | 0.038 | 0.20 | -0.197 | -0.204 | 0.012 | 1.000 | -0.181 | -0.064 | -0.183 | no |
| L1&L2&L4 | 19977 | 15628 | 35.5 | -0.166 | 0.038 | 0.20 | -0.188 | -0.200 | 0.003 | 1.000 | -0.176 | -0.064 | -0.167 | no |
| L1&L2&L5 | 2128 | 1306 | 36.2 | -0.143 | 0.048 | 0.19 | -0.216 | -0.253 | 0.045 | 1.000 | -0.222 | -0.048 | -0.147 | no |
| L1&L3&L4 | 21358 | 17445 | 35.3 | -0.182 | 0.026 | 0.21 | -0.202 | -0.212 | 0.041 | 1.000 | -0.190 | -0.078 | -0.197 | no |
| L1&L3&L5 | 1690 | 1108 | 35.9 | -0.151 | 0.043 | 0.19 | -0.229 | -0.266 | 0.090 | 1.000 | -0.226 | -0.054 | -0.218 | no |
| L1&L4&L5 | 3578 | 2506 | 34.2 | -0.208 | -0.014 | 0.19 | -0.260 | -0.295 | 0.606 | 1.000 | -0.265 | -0.111 | -0.190 | no |
| L2&L3&L4 | 40892 | 30029 | 35.0 | -0.186 | 0.019 | 0.20 | -0.201 | -0.211 | 0.025 | 1.000 | -0.193 | -0.083 | -0.193 | no |
| L2&L3&L5 | 2991 | 1996 | 37.6 | -0.112 | 0.084 | 0.20 | -0.173 | -0.193 | 0.003 | 1.000 | -0.152 | -0.014 | -0.174 | no |
| L2&L4&L5 | 9063 | 6558 | 34.5 | -0.208 | -0.012 | 0.20 | -0.240 | -0.257 | 0.677 | 1.000 | -0.227 | -0.110 | -0.134 | no |
| L3&L4&L5 | 7219 | 5211 | 34.5 | -0.198 | -0.004 | 0.19 | -0.233 | -0.253 | 0.414 | 1.000 | -0.219 | -0.101 | -0.183 | no |
| n=1 | 294279 | 199807 | 34.4 | -0.201 | -0.001 | 0.20 | -0.207 | -0.213 | 0.742 | 1.000 | -0.204 | -0.101 | -0.191 | no |
| n=2 | 197496 | 138497 | 34.4 | -0.201 | 0.000 | 0.20 | -0.208 | -0.215 | 0.680 | 1.000 | -0.205 | -0.101 | -0.194 | no |
| n=3 | 73088 | 54406 | 34.8 | -0.192 | 0.012 | 0.20 | -0.203 | -0.212 | 0.076 | 1.000 | -0.197 | -0.090 | -0.190 | no |
| n>=4 | 11667 | 9208 | 35.4 | -0.169 | 0.033 | 0.20 | -0.195 | -0.207 | 0.017 | 1.000 | -0.183 | -0.068 | -0.165 | no |
| n=1+VWAP | 188746 | 125928 | 34.5 | -0.192 | 0.009 | 0.20 | -0.199 | -0.208 | 0.032 | 1.000 | -0.198 | -0.091 | -0.192 | no |
| n=2+VWAP | 131966 | 91768 | 34.6 | -0.192 | 0.011 | 0.20 | -0.201 | -0.209 | 0.074 | 1.000 | -0.197 | -0.090 | -0.198 | no |
| n=3+VWAP | 49607 | 37673 | 35.3 | -0.177 | 0.029 | 0.21 | -0.191 | -0.201 | 0.001 | 1.000 | -0.184 | -0.074 | -0.196 | no |
| n>=4+VWAP | 7763 | 6665 | 35.2 | -0.175 | 0.028 | 0.20 | -0.208 | -0.227 | 0.063 | 1.000 | -0.193 | -0.074 | -0.143 | no |

## Heat table: mean net R (12 bp, VALIDATION). Diagonal = single layer, off-diagonal = pair

| | L1 | L2 | L3 | L4 | L5 |
|---|---|---|---|---|---|
| L1 | -0.188 | -0.174 | -0.182 | -0.181 | -0.190 |
| L2 | -0.174 | -0.205 | -0.191 | -0.202 | -0.206 |
| L3 | -0.182 | -0.191 | -0.197 | -0.193 | -0.182 |
| L4 | -0.181 | -0.202 | -0.193 | -0.204 | -0.242 |
| L5 | -0.190 | -0.206 | -0.182 | -0.242 | -0.235 |

Triples (mean net R / gross R): L1&L2&L3 -0.166/0.038; L1&L2&L4 -0.166/0.038; L1&L2&L5 -0.143/0.048; L1&L3&L4 -0.182/0.026; L1&L3&L5 -0.151/0.043; L1&L4&L5 -0.208/-0.014; L2&L3&L4 -0.186/0.019; L2&L3&L5 -0.112/0.084; L2&L4&L5 -0.208/-0.012; L3&L4&L5 -0.198/-0.004

Count buckets (mean net R, n VAL): n=1 -0.201 (n=199807); n=2 -0.201 (n=138497); n=3 -0.192 (n=54406); n>=4 -0.169 (n=9208); n=1+VWAP -0.192 (n=125928); n=2+VWAP -0.192 (n=91768); n=3+VWAP -0.177 (n=37673); n>=4+VWAP -0.175 (n=6665)

## Reading
- Fees are about 0.20R per trade (stop floor 0.5% of price); at a 2R target the break-even win rate on a gross-zero edge is above 33% only after fees. Win rate is 33-38% in every row, i.e. the layers alone move the gross edge by at most 0.084R (L2&L3&L5).
- Gross R rises slightly with agreement (n=1 -0.001, n=2 0.000, n=3 0.012, n>=4 0.033) but never covers the fee: best net row is L2&L3&L5 at -0.112R; at 6 bp best is still negative.
- Several rows show placebo p < 0.05 (e.g. L1&L4, L2&L3&L5, n=3+VWAP), meaning they beat random phase-matched entries, but random entries are themselves -0.20R net, so beating placebo is not an edge. None clears mean>0, CI, BH or ex-best-5.
- Phase-matched rows are no better than control (opposite-direction) rows in DEV or VAL: phase direction adds nothing measurable here on 15m entries.
- 6 bp maker row assumes every limit fills (optimistic) and is still negative everywhere.

## BTC today (descriptive only)
- Data to 2026-11-13T20:15:00.000 UTC (partial 2026-11-13 day), close 68942, session VWAP 69218 (price below).
- Phase label for 2026-11-14: DOWN (ADX 25.7, +DI 9.8, -DI 35.1, SMA20 76743). Daily phase counts 11-13 as the closed day only in labelling for 11-14.
- 11-13 H/L/C 71514 / 67568 / 68942; standard pivots for 11-14: P 69341, R1 71115, S1 67169. Price is under P, above S1.
- Layers active on the last bar: none (long [False, False, False, False, False], short [False, False, False, False, False]). A DOWN-phase setup would need shorts on a rejection at P / R1 or first-hour reclaim down; nothing here tested to pay after fees.

## Parameters
SOURCED: RSI 30/70 re-cross, standard pivots P/S1/R1, breakout-retest-fakeout concept, Hilega state meaning (red under green = buy). OURS: first-hour = UTC 00:00-01:00, K=4 window, RSI9/EMA3/WMA21, 20-bar breakout window, 6-bar retest window, ADX 20/SMA20 phase, stop/target/time exit, fees, placebo design.

Files: study.py, run.py, make_result.py, test_study.py (causality test passes on real code, fails under STUDY_BUG=1), fetch.py, results.json. Data: F:\MTS\data_cacheinance_spot (note: sibling workers share this cache and overwrite files with key `t`; study.load accepts both).
