**VERDICT: FAIL, 0 of 2 DEV-chosen cells pass VAL (2024+) fee-net at 12 bp; best cell by day-CI low: NK2-core / MARKUP / C4_oi24h <=-3%, n 1081, net -0.021 R, day CI low -0.175.**

Regime mix: (days per phase, label from BTC through the prior close). DEV 2019-2023 (1826 days): CAPITULATION 52d (2.9%), MARKDOWN 434d (23.8%), RELIEF 154d (8.4%), ACCUM-RANGE 333d (18.2%), MARKUP 605d (33.1%), DISTRIBUTION 248d (13.6%). VAL 2024-2026-11-13 (1048 days): CAPITULATION 6d (0.6%), MARKDOWN 198d (18.9%), RELIEF 34d (3.2%), ACCUM-RANGE 156d (14.9%), MARKUP 321d (30.6%), DISTRIBUTION 333d (31.8%).
Signals (trades) per phase, registered stop basis, 12 bp sequence:
| rule | split | CAPITULATION | MARKDOWN | RELIEF | ACCUM-RANGE | MARKUP | DISTRIBUTION |
|---|---|---|---|---|---|---|---|
| NK2-core | DEV | 1016 | 7846 | 2439 | 5782 | 10383 | 4218 |
| NK2-core | VAL | 101 | 4077 | 654 | 3144 | 6833 | 6914 |
| NK2-deep | DEV | 71 | 708 | 221 | 424 | 819 | 291 |
| NK2-deep | VAL | 5 | 399 | 90 | 237 | 570 | 684 |
| NK3-A | DEV | 293 | 2468 | 766 | 1723 | 3311 | 1316 |
| NK3-A | VAL | 20 | 1301 | 256 | 990 | 2422 | 2454 |
| NK3-B | DEV | 133 | 1126 | 403 | 854 | 1398 | 605 |
| NK3-B | VAL | 22 | 653 | 117 | 505 | 1182 | 1112 |

## Context
Phase table: `F:\MTS\data_cache\mts_brains\phase_daily.csv` (shared; a sibling worker's builder wrote the file, my own build of the same spec agreed on 2874 of 2874 days from 2019-01-01, so the shared file is used as is), 30 random days re-computed from truncated data in `test_phase_csv_matches_recompute_30_days`. Six phases and thresholds are spec s1 (OURS, not tuned); cycle state SOURCED from the cycle-conditioned PRE_REG. CAPITULATION is below 5% of DEV days (2.9%), so it is reported and never supplies a cell. Context layers C1-C8: spec s2, one layer per cell. Sanity windows (recorded, not retuned): see PRE_REG.md.
Rules: NK2-core (P, S1/R1 triggers), NK2-deep (S2, S3 long; R2, R3 short; NEW), NK3-A (breakout retest), NK3-B (fakeout fade). 1h bars, 20 Binance spot coins, taker 12 bp (6 bp per leg on entry and exit notional), spot-equivalent, no funding charge. NK2 uses the close-basis stop (NK 'stop on closing basis', NEW for this study family), NK3 the intraday stop; Step A shows the other basis in `alt net`.

## Step A: per-phase table, phase-appropriate vs opposite direction
Every phase is its own row; nothing is pooled across phases. `role` marks the phase-appropriate direction (ACCUM-RANGE is both). Net R is mean fee-net R per trade at 12 bp; gross R and cost R before/after the fee; `alt net` is the same set on the other stop basis.

### VAL (2024+, descriptive, after the freeze)
| rule | phase | dir | role | n | days | gross R | cost R | net R | alt net R |
|---|---|---|---|---|---|---|---|---|---|
| NK2-core | CAPITULATION | long | appropriate | 47 | 5 | -0.070 | 0.070 | -0.140 | -0.113 |
| NK2-core | CAPITULATION | short | opposite | 54 | 5 | -0.270 | 0.076 | -0.345 | -0.530 |
| NK2-core | MARKDOWN | long | opposite | 1997 | 197 | 0.039 | 0.105 | -0.066 | -0.093 |
| NK2-core | MARKDOWN | short | appropriate | 2080 | 192 | 0.048 | 0.107 | -0.059 | -0.093 |
| NK2-core | RELIEF | long | appropriate | 342 | 33 | 0.168 | 0.144 | 0.024 | -0.072 |
| NK2-core | RELIEF | short | opposite | 312 | 34 | -0.093 | 0.144 | -0.237 | -0.096 |
| NK2-core | ACCUM-RANGE | long | both | 1548 | 156 | -0.085 | 0.128 | -0.213 | -0.188 |
| NK2-core | ACCUM-RANGE | short | both | 1596 | 154 | 0.046 | 0.131 | -0.084 | -0.063 |
| NK2-core | MARKUP | long | appropriate | 3435 | 314 | -0.024 | 0.096 | -0.120 | -0.137 |
| NK2-core | MARKUP | short | opposite | 3398 | 317 | 0.019 | 0.100 | -0.082 | -0.046 |
| NK2-core | DISTRIBUTION | long | opposite | 3403 | 329 | -0.159 | 0.107 | -0.266 | -0.219 |
| NK2-core | DISTRIBUTION | short | appropriate | 3511 | 327 | 0.177 | 0.110 | 0.067 | 0.038 |
| NK2-deep | CAPITULATION | short | opposite | 5 | 1 | -0.206 | 0.089 | -0.295 | -1.089 |
| NK2-deep | MARKDOWN | long | opposite | 216 | 62 | 0.291 | 0.113 | 0.178 | 0.126 |
| NK2-deep | MARKDOWN | short | appropriate | 183 | 66 | 0.450 | 0.113 | 0.336 | 0.202 |
| NK2-deep | RELIEF | long | appropriate | 43 | 9 | -0.280 | 0.143 | -0.423 | -0.301 |
| NK2-deep | RELIEF | short | opposite | 47 | 14 | 0.733 | 0.158 | 0.575 | 0.482 |
| NK2-deep | ACCUM-RANGE | long | both | 119 | 45 | -0.000 | 0.139 | -0.139 | -0.212 |
| NK2-deep | ACCUM-RANGE | short | both | 118 | 50 | -0.093 | 0.142 | -0.235 | -0.142 |
| NK2-deep | MARKUP | long | appropriate | 265 | 82 | -0.133 | 0.109 | -0.242 | -0.231 |
| NK2-deep | MARKUP | short | opposite | 305 | 125 | -0.056 | 0.114 | -0.171 | -0.085 |
| NK2-deep | DISTRIBUTION | long | opposite | 388 | 101 | -0.119 | 0.114 | -0.233 | -0.173 |
| NK2-deep | DISTRIBUTION | short | appropriate | 296 | 114 | -0.143 | 0.138 | -0.281 | -0.181 |
| NK3-A | CAPITULATION | long | appropriate | 18 | 5 | 0.167 | 0.130 | 0.036 | 0.256 |
| NK3-A | CAPITULATION | short | opposite | 2 | 2 | 0.500 | 0.086 | 0.414 | 0.037 |
| NK3-A | MARKDOWN | long | opposite | 671 | 140 | -0.128 | 0.158 | -0.286 | -0.370 |
| NK3-A | MARKDOWN | short | appropriate | 630 | 138 | -0.063 | 0.147 | -0.210 | -0.266 |
| NK3-A | RELIEF | long | appropriate | 163 | 32 | -0.010 | 0.187 | -0.197 | -0.023 |
| NK3-A | RELIEF | short | opposite | 93 | 27 | 0.023 | 0.198 | -0.175 | 0.073 |
| NK3-A | ACCUM-RANGE | long | both | 523 | 125 | 0.036 | 0.176 | -0.140 | -0.165 |
| NK3-A | ACCUM-RANGE | short | both | 467 | 119 | 0.122 | 0.180 | -0.058 | -0.091 |
| NK3-A | MARKUP | long | appropriate | 1334 | 268 | 0.161 | 0.147 | 0.014 | 0.002 |
| NK3-A | MARKUP | short | opposite | 1088 | 220 | -0.006 | 0.143 | -0.150 | -0.161 |
| NK3-A | DISTRIBUTION | long | opposite | 1193 | 241 | -0.000 | 0.159 | -0.159 | -0.145 |
| NK3-A | DISTRIBUTION | short | appropriate | 1261 | 242 | 0.125 | 0.151 | -0.026 | -0.056 |
| NK3-B | CAPITULATION | long | appropriate | 18 | 2 | -0.167 | 0.096 | -0.262 | 0.225 |
| NK3-B | CAPITULATION | short | opposite | 4 | 4 | -0.250 | 0.168 | -0.418 | 0.147 |
| NK3-B | MARKDOWN | long | opposite | 352 | 115 | 0.003 | 0.116 | -0.113 | -0.070 |
| NK3-B | MARKDOWN | short | appropriate | 301 | 126 | 0.174 | 0.123 | 0.051 | 0.146 |
| NK3-B | RELIEF | long | appropriate | 44 | 22 | 0.390 | 0.167 | 0.223 | 0.438 |
| NK3-B | RELIEF | short | opposite | 73 | 24 | -0.090 | 0.171 | -0.262 | -0.290 |
| NK3-B | ACCUM-RANGE | long | both | 238 | 93 | -0.013 | 0.136 | -0.149 | -0.295 |
| NK3-B | ACCUM-RANGE | short | both | 267 | 109 | 0.143 | 0.142 | 0.001 | 0.040 |
| NK3-B | MARKUP | long | appropriate | 631 | 182 | -0.023 | 0.106 | -0.130 | -0.096 |
| NK3-B | MARKUP | short | opposite | 551 | 216 | 0.100 | 0.120 | -0.020 | -0.101 |
| NK3-B | DISTRIBUTION | long | opposite | 595 | 200 | -0.077 | 0.121 | -0.199 | -0.305 |
| NK3-B | DISTRIBUTION | short | appropriate | 517 | 194 | 0.176 | 0.130 | 0.046 | 0.063 |

### DEV (<=2023, used for selection)
| rule | phase | dir | role | n | days | gross R | cost R | net R | alt net R |
|---|---|---|---|---|---|---|---|---|---|
| NK2-core | CAPITULATION | long | appropriate | 509 | 49 | 0.133 | 0.043 | 0.090 | 0.117 |
| NK2-core | CAPITULATION | short | opposite | 507 | 50 | -0.014 | 0.040 | -0.054 | -0.043 |
| NK2-core | MARKDOWN | long | opposite | 4055 | 425 | -0.060 | 0.100 | -0.160 | -0.108 |
| NK2-core | MARKDOWN | short | appropriate | 3791 | 424 | -0.007 | 0.102 | -0.109 | -0.096 |
| NK2-core | RELIEF | long | appropriate | 1181 | 135 | 0.049 | 0.084 | -0.034 | -0.050 |
| NK2-core | RELIEF | short | opposite | 1258 | 143 | -0.046 | 0.088 | -0.134 | -0.081 |
| NK2-core | ACCUM-RANGE | long | both | 2903 | 319 | -0.167 | 0.117 | -0.284 | -0.212 |
| NK2-core | ACCUM-RANGE | short | both | 2879 | 316 | 0.034 | 0.121 | -0.087 | -0.039 |
| NK2-core | MARKUP | long | appropriate | 5090 | 551 | 0.050 | 0.081 | -0.031 | -0.035 |
| NK2-core | MARKUP | short | opposite | 5293 | 546 | -0.108 | 0.088 | -0.195 | -0.118 |
| NK2-core | DISTRIBUTION | long | opposite | 2053 | 217 | 0.099 | 0.086 | 0.013 | 0.024 |
| NK2-core | DISTRIBUTION | short | appropriate | 2165 | 218 | -0.089 | 0.089 | -0.178 | -0.150 |
| NK2-deep | CAPITULATION | long | appropriate | 48 | 9 | -0.377 | 0.039 | -0.416 | -0.116 |
| NK2-deep | CAPITULATION | short | opposite | 23 | 10 | -0.288 | 0.058 | -0.347 | -0.354 |
| NK2-deep | MARKDOWN | long | opposite | 408 | 108 | -0.348 | 0.092 | -0.441 | -0.320 |
| NK2-deep | MARKDOWN | short | appropriate | 300 | 141 | 0.033 | 0.107 | -0.074 | -0.045 |
| NK2-deep | RELIEF | long | appropriate | 88 | 28 | -0.321 | 0.095 | -0.416 | -0.367 |
| NK2-deep | RELIEF | short | opposite | 133 | 66 | -0.085 | 0.091 | -0.176 | -0.162 |
| NK2-deep | ACCUM-RANGE | long | both | 218 | 89 | -0.060 | 0.105 | -0.164 | -0.178 |
| NK2-deep | ACCUM-RANGE | short | both | 206 | 94 | -0.094 | 0.126 | -0.219 | -0.192 |
| NK2-deep | MARKUP | long | appropriate | 306 | 110 | -0.093 | 0.081 | -0.173 | -0.151 |
| NK2-deep | MARKUP | short | opposite | 513 | 242 | -0.211 | 0.097 | -0.307 | -0.212 |
| NK2-deep | DISTRIBUTION | long | opposite | 131 | 45 | -0.209 | 0.102 | -0.311 | -0.195 |
| NK2-deep | DISTRIBUTION | short | appropriate | 160 | 78 | -0.233 | 0.107 | -0.339 | -0.255 |
| NK3-A | CAPITULATION | long | appropriate | 141 | 33 | -0.212 | 0.068 | -0.280 | -0.119 |
| NK3-A | CAPITULATION | short | opposite | 152 | 28 | -0.222 | 0.072 | -0.294 | -0.346 |
| NK3-A | MARKDOWN | long | opposite | 1262 | 322 | 0.032 | 0.139 | -0.107 | -0.123 |
| NK3-A | MARKDOWN | short | appropriate | 1206 | 280 | 0.044 | 0.131 | -0.088 | -0.077 |
| NK3-A | RELIEF | long | appropriate | 431 | 114 | -0.033 | 0.136 | -0.169 | -0.237 |
| NK3-A | RELIEF | short | opposite | 335 | 93 | 0.057 | 0.119 | -0.062 | -0.046 |
| NK3-A | ACCUM-RANGE | long | both | 916 | 253 | -0.093 | 0.162 | -0.256 | -0.279 |
| NK3-A | ACCUM-RANGE | short | both | 807 | 210 | 0.127 | 0.158 | -0.031 | 0.002 |
| NK3-A | MARKUP | long | appropriate | 1949 | 465 | 0.095 | 0.129 | -0.033 | 0.019 |
| NK3-A | MARKUP | short | opposite | 1362 | 343 | 0.192 | 0.118 | 0.075 | 0.000 |
| NK3-A | DISTRIBUTION | long | opposite | 704 | 163 | 0.076 | 0.130 | -0.054 | -0.070 |
| NK3-A | DISTRIBUTION | short | appropriate | 612 | 147 | 0.054 | 0.122 | -0.068 | -0.094 |
| NK3-B | CAPITULATION | long | appropriate | 66 | 20 | 0.033 | 0.056 | -0.023 | -0.048 |
| NK3-B | CAPITULATION | short | opposite | 67 | 23 | 0.481 | 0.047 | 0.434 | 0.410 |
| NK3-B | MARKDOWN | long | opposite | 567 | 230 | -0.021 | 0.113 | -0.134 | -0.134 |
| NK3-B | MARKDOWN | short | appropriate | 559 | 253 | 0.098 | 0.111 | -0.013 | -0.031 |
| NK3-B | RELIEF | long | appropriate | 207 | 80 | 0.177 | 0.093 | 0.084 | 0.104 |
| NK3-B | RELIEF | short | opposite | 196 | 87 | -0.075 | 0.098 | -0.173 | -0.393 |
| NK3-B | ACCUM-RANGE | long | both | 453 | 181 | -0.054 | 0.121 | -0.175 | -0.262 |
| NK3-B | ACCUM-RANGE | short | both | 401 | 182 | 0.205 | 0.142 | 0.063 | -0.019 |
| NK3-B | MARKUP | long | appropriate | 671 | 287 | 0.131 | 0.090 | 0.041 | 0.053 |
| NK3-B | MARKUP | short | opposite | 727 | 351 | 0.004 | 0.097 | -0.094 | -0.167 |
| NK3-B | DISTRIBUTION | long | opposite | 272 | 112 | 0.212 | 0.096 | 0.117 | 0.009 |
| NK3-B | DISTRIBUTION | short | appropriate | 333 | 141 | 0.075 | 0.102 | -0.027 | -0.061 |

### Does the phase-appropriate direction beat the opposite one? (day-clustered difference)

VAL:
| rule | phase | appropriate n | opposite n | appropriate net R | opposite net R | diff | se | z |
|---|---|---|---|---|---|---|---|---|
| NK2-core | CAPITULATION | 47 | 54 | -0.140 | -0.345 | 0.205 | 0.892 | 0.23 |
| NK2-core | MARKDOWN | 2080 | 1997 | -0.059 | -0.066 | 0.007 | 0.125 | 0.06 |
| NK2-core | RELIEF | 342 | 312 | 0.024 | -0.237 | 0.261 | 0.296 | 0.88 |
| NK2-core | MARKUP | 3435 | 3398 | -0.120 | -0.082 | -0.038 | 0.101 | -0.38 |
| NK2-core | DISTRIBUTION | 3511 | 3403 | 0.067 | -0.266 | 0.333 | 0.106 | 3.15 |
| NK2-deep | MARKDOWN | 183 | 216 | 0.336 | 0.178 | 0.158 | 0.226 | 0.70 |
| NK2-deep | RELIEF | 43 | 47 | -0.423 | 0.575 | -0.998 | 0.424 | -2.36 |
| NK2-deep | MARKUP | 265 | 305 | -0.242 | -0.171 | -0.071 | 0.191 | -0.37 |
| NK2-deep | DISTRIBUTION | 296 | 388 | -0.281 | -0.233 | -0.048 | 0.203 | -0.24 |
| NK3-A | MARKDOWN | 630 | 671 | -0.210 | -0.286 | 0.076 | 0.110 | 0.69 |
| NK3-A | RELIEF | 163 | 93 | -0.197 | -0.175 | -0.022 | 0.271 | -0.08 |
| NK3-A | MARKUP | 1334 | 1088 | 0.014 | -0.150 | 0.164 | 0.090 | 1.82 |
| NK3-A | DISTRIBUTION | 1261 | 1193 | -0.026 | -0.159 | 0.133 | 0.097 | 1.36 |
| NK3-B | MARKDOWN | 301 | 352 | 0.051 | -0.113 | 0.163 | 0.148 | 1.10 |
| NK3-B | RELIEF | 44 | 73 | 0.223 | -0.262 | 0.485 | 0.390 | 1.25 |
| NK3-B | MARKUP | 631 | 551 | -0.130 | -0.020 | -0.110 | 0.128 | -0.86 |
| NK3-B | DISTRIBUTION | 517 | 595 | 0.046 | -0.199 | 0.245 | 0.132 | 1.85 |

DEV:
| rule | phase | appropriate n | opposite n | appropriate net R | opposite net R | diff | se | z |
|---|---|---|---|---|---|---|---|---|
| NK2-core | CAPITULATION | 509 | 507 | 0.090 | -0.054 | 0.143 | 0.341 | 0.42 |
| NK2-core | MARKDOWN | 3791 | 4055 | -0.109 | -0.160 | 0.051 | 0.103 | 0.49 |
| NK2-core | RELIEF | 1181 | 1258 | -0.034 | -0.134 | 0.100 | 0.166 | 0.60 |
| NK2-core | MARKUP | 5090 | 5293 | -0.031 | -0.195 | 0.164 | 0.075 | 2.20 |
| NK2-core | DISTRIBUTION | 2165 | 2053 | -0.178 | 0.013 | -0.191 | 0.126 | -1.52 |
| NK2-deep | CAPITULATION | 48 | 23 | -0.416 | -0.347 | -0.069 | 0.638 | -0.11 |
| NK2-deep | MARKDOWN | 300 | 408 | -0.074 | -0.441 | 0.366 | 0.191 | 1.92 |
| NK2-deep | RELIEF | 88 | 133 | -0.416 | -0.176 | -0.239 | 0.278 | -0.86 |
| NK2-deep | MARKUP | 306 | 513 | -0.173 | -0.307 | 0.134 | 0.168 | 0.80 |
| NK2-deep | DISTRIBUTION | 160 | 131 | -0.339 | -0.311 | -0.028 | 0.277 | -0.10 |
| NK3-A | CAPITULATION | 141 | 152 | -0.280 | -0.294 | 0.014 | 0.194 | 0.07 |
| NK3-A | MARKDOWN | 1206 | 1262 | -0.088 | -0.107 | 0.019 | 0.090 | 0.22 |
| NK3-A | RELIEF | 431 | 335 | -0.169 | -0.062 | -0.108 | 0.161 | -0.67 |
| NK3-A | MARKUP | 1949 | 1362 | -0.033 | 0.075 | -0.108 | 0.080 | -1.36 |
| NK3-A | DISTRIBUTION | 612 | 704 | -0.068 | -0.054 | -0.013 | 0.117 | -0.11 |
| NK3-B | CAPITULATION | 66 | 67 | -0.023 | 0.434 | -0.457 | 0.386 | -1.18 |
| NK3-B | MARKDOWN | 559 | 567 | -0.013 | -0.134 | 0.121 | 0.111 | 1.09 |
| NK3-B | RELIEF | 207 | 196 | 0.084 | -0.173 | 0.257 | 0.182 | 1.41 |
| NK3-B | MARKUP | 671 | 727 | 0.041 | -0.094 | 0.135 | 0.101 | 1.33 |
| NK3-B | DISTRIBUTION | 333 | 272 | -0.027 | 0.117 | -0.144 | 0.164 | -0.88 |

### Pivot level table (NK2; S1/S2/S3 long, R1/R2/R3 short, P both; close-basis stop; trades by trigger level)

VAL, phase-appropriate-direction trades only:
| rule | level | n | days | gross R | cost R | net R |
|---|---|---|---|---|---|---|
| NK2-core | S1 | 1561 | 338 | -0.067 | 0.108 | -0.175 |
| NK2-core | P | 8943 | 1005 | 0.047 | 0.109 | -0.061 |
| NK2-core | R1 | 2055 | 470 | 0.154 | 0.126 | 0.028 |
| NK2-deep | S3 | 99 | 51 | -0.142 | 0.121 | -0.263 |
| NK2-deep | S2 | 328 | 128 | -0.101 | 0.121 | -0.222 |
| NK2-deep | R2 | 449 | 204 | 0.054 | 0.131 | -0.077 |
| NK2-deep | R3 | 148 | 95 | 0.032 | 0.133 | -0.101 |

DEV, phase-appropriate-direction trades only:
| rule | level | n | days | gross R | cost R | net R |
|---|---|---|---|---|---|---|
| NK2-core | S1 | 2482 | 602 | -0.010 | 0.091 | -0.101 |
| NK2-core | P | 13677 | 1655 | -0.008 | 0.097 | -0.106 |
| NK2-core | R1 | 2359 | 671 | -0.037 | 0.104 | -0.141 |
| NK2-deep | S3 | 168 | 85 | -0.172 | 0.084 | -0.256 |
| NK2-deep | S2 | 492 | 221 | -0.120 | 0.089 | -0.208 |
| NK2-deep | R2 | 516 | 281 | -0.019 | 0.113 | -0.132 |
| NK2-deep | R3 | 150 | 107 | -0.245 | 0.114 | -0.359 |

## Step B: DEV selection
| rule | cells scored | n>=150 and >=40 days | of those: DEV mean > 0 | lower 90% bound > 0 |
|---|---|---|---|---|
| NK2-core | 120 | 106 | 16 | 1 |
| NK2-deep | 120 | 22 | 1 | 0 |
| NK3-A | 120 | 76 | 12 | 0 |
| NK3-B | 120 | 46 | 20 | 1 |

Kept cells (frozen in commit `ff5c77ffa9`): 2.

## Step C: the DEV-chosen cells on VAL (run once)
| cell (rule / phase / layer bucket / dir) | DEV n / net R | VAL n | days | win % | break-even win % | gross R | fee R | net R 12bp | day CI 95% | ex-best-5 net R | placebo mean / p | BH q | maker 6bp net R | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| NK2-core / MARKUP / C4_oi24h <=-3% / long | 574 / 0.172 | 1081 | 275 | 45.5 | 46.2 | 0.058 | 0.079 | -0.021 | -0.175 .. 0.129 | -0.103 | 0.057 / p 0.899 | 0.833 | 0.008 (n 1059, fill 0.98) | FAIL |
| NK3-B / MARKUP / C8_session asia / long | 262 / 0.339 | 247 | 92 | 33.2 | 38.5 | -0.043 | 0.104 | -0.147 | -0.428 .. 0.149 | -0.401 | -0.099 / p 0.720 | 0.833 | -0.160 (n 236, fill 0.96) | FAIL |

DEV cells that passed VAL: 0 of 2. DEV net vs VAL net (shrinkage): NK2-core C4_oi24h 0.172 -> -0.021; NK3-B C8_session 0.339 -> -0.147

Control rows on VAL (12 bp net R, n):
| cell | the cell | opposite direction | same bucket, other 5 phases | unconditional rule (same direction) |
|---|---|---|---|---|
| NK2-core / MARKUP / C4_oi24h <=-3% | -0.021 (n 1081) | 0.010 (n 707) | -0.121 (n 2031) | -0.165 (n 10772) |
| NK3-B / MARKUP / C8_session asia | -0.147 (n 247) | 0.015 (n 221) | -0.096 (n 455) | -0.144 (n 1878) |

## Useful trades now (descriptive only, no advice)
Phase label for BTC (applied to ETH and all coins) from the latest closed data: MARKDOWN (label day 2026-11-13). Provisional label for the next day using the partial 2026-11-13 bar (82 of 96 bars): MARKDOWN.
| closed day | label for the next day | BTC close | SMA50 | SMA200 | W200 | cycle state |
|---|---|---|---|---|---|---|
| 2026-11-04 | ACCUM-RANGE | 80504 | 82064 | 73231 | 67521 | BASE |
| 2026-11-05 | DISTRIBUTION | 76088 | 82061 | 73243 | 67563 | BASE |
| 2026-11-06 | DISTRIBUTION | 75772 | 82048 | 73242 | 67605 | BASE |
| 2026-11-07 | DISTRIBUTION | 75868 | 81948 | 73240 | 67647 | BASE |
| 2026-11-08 | DISTRIBUTION | 74851 | 81820 | 73223 | 67688 | BASE |
| 2026-11-09 | DISTRIBUTION | 75368 | 81704 | 73209 | 67730 | BASE |
| 2026-11-10 | DISTRIBUTION | 73796 | 81448 | 73191 | 67770 | BASE |
| 2026-11-11 | DISTRIBUTION | 74015 | 81204 | 73172 | 67810 | BASE |
| 2026-11-12 | MARKDOWN | 71460 | 80945 | 73137 | 67848 | BEAR |

BTC latest closed 1h bar 2026-11-13T19:00:00.000: phase MARKDOWN; C1_rsi4h <=40; C2_wt1d <=-53; C3_bbpb4h mid; C4_oi24h NO-DATA; C5_funding NO-DATA; C6_taker_div24h NO-DATA; C7_rv7_60 mid; C8_session us

ETH latest closed 1h bar 2026-11-13T19:00:00.000: phase MARKDOWN; C1_rsi4h <=40; C2_wt1d <=-53; C3_bbpb4h mid; C4_oi24h NO-DATA; C5_funding NO-DATA; C6_taker_div24h NO-DATA; C7_rv7_60 mid; C8_session us

Kept cells active at this reading: none.

## Data coverage
First and last available date per coin and series (data.binance.vision). Funding monthly files end at the last full month, so C5 has no bucket for later signals; OI daily files start 2020-09 at the earliest and per listing. Signals before a layer's first date have no bucket for that layer.
| coin | spot 1h klines (C6) | funding (C5) | open interest (C4) |
|---|---|---|---|
| ADA | 2019-01-01 .. 2026-11-12 | 2020-01-19 .. 2026-10-31 | 2021-12-01 .. 2026-11-12 |
| ALGO | 2019-06-22 .. 2026-11-12 | 2020-06-01 .. 2026-10-31 | 2021-12-01 .. 2026-11-12 |
| ATOM | 2019-04-29 .. 2026-11-12 | 2020-02-06 .. 2026-10-31 | 2021-12-01 .. 2026-11-12 |
| AVAX | 2020-09-22 .. 2026-11-12 | 2020-09-22 .. 2026-10-31 | 2021-12-01 .. 2026-11-12 |
| BCH | 2019-11-28 .. 2026-11-12 | 2020-01-01 .. 2026-10-31 | 2021-12-01 .. 2026-11-12 |
| BNB | 2019-01-01 .. 2026-11-12 | 2020-02-10 .. 2026-10-31 | 2021-12-01 .. 2026-11-12 |
| BTC | 2019-01-01 .. 2026-11-12 | 2020-01-01 .. 2026-10-31 | 2020-09-01 .. 2026-11-12 |
| DOGE | 2019-07-05 .. 2026-11-12 | 2020-07-10 .. 2026-10-31 | 2021-12-01 .. 2026-11-12 |
| DOT | 2020-08-18 .. 2026-11-12 | 2020-08-20 .. 2026-10-31 | 2021-12-01 .. 2026-11-12 |
| ETC | 2019-01-01 .. 2026-11-12 | 2020-01-16 .. 2026-10-31 | 2021-12-01 .. 2026-11-12 |
| ETH | 2019-01-01 .. 2026-11-12 | 2020-01-01 .. 2026-10-31 | 2021-12-01 .. 2026-11-12 |
| FIL | 2020-10-15 .. 2026-11-12 | 2020-10-16 .. 2026-10-31 | 2021-12-01 .. 2026-11-12 |
| LINK | 2019-01-16 .. 2026-11-12 | 2020-01-17 .. 2026-10-31 | 2021-12-01 .. 2026-11-12 |
| LTC | 2019-01-01 .. 2026-11-12 | 2020-01-09 .. 2026-10-31 | 2021-12-01 .. 2026-11-12 |
| NEAR | 2020-10-14 .. 2026-11-12 | 2020-10-14 .. 2026-10-31 | 2021-12-01 .. 2026-11-12 |
| SOL | 2020-08-11 .. 2026-11-12 | 2020-09-13 .. 2026-10-31 | 2021-12-01 .. 2026-11-12 |
| TRX | 2019-01-01 .. 2026-11-12 | 2020-01-15 .. 2026-10-31 | 2021-12-01 .. 2026-11-12 |
| UNI | 2020-09-17 .. 2026-11-12 | 2020-09-17 .. 2026-10-31 | 2021-12-01 .. 2026-11-12 |
| XLM | 2019-01-01 .. 2026-11-12 | 2020-01-19 .. 2026-10-31 | 2021-12-01 .. 2026-11-12 |
| XRP | 2019-01-01 .. 2026-11-12 | 2020-01-06 .. 2026-10-31 | 2021-12-01 .. 2026-11-12 |

## Tests
```
== env NORMAL=1
17 passed in 19.02s
== env STUDY_BUG=1
FAILED test_study.py::test_phase_lag_causal - AssertionError: (17266, 0, 5)
FAILED test_study.py::test_bar_phase_matches_truncated_btc - AssertionError: ...
FAILED test_study.py::test_signals_truncation_invariant - assert np.False_
3 failed, 14 passed in 16.70s
== env PHASE_LAG=0
FAILED test_study.py::test_phase_lag_causal - AssertionError: (17266, 0, 5)
1 failed, 16 passed in 17.99s
== env STUDY_BUG=2
FAILED test_study.py::test_context_layer_ignores_future_bars[0] - AssertionEr...
FAILED test_study.py::test_context_layer_ignores_future_bars[1] - AssertionEr...
FAILED test_study.py::test_context_layer_ignores_future_bars[2] - AssertionEr...
3 failed, 14 passed in 18.91s

```

## Reading and caveats

- **What failed.** DEV found 2 cells with a positive lower 90% bound out of 480 cells (4 rules x 120 cells; CAPITULATION cannot supply cells): NK2-core MARKUP long when OI fell 3% or more in 24h, and NK3-B MARKUP long in the Asia session. NK2-deep and NK3-A produced none. On VAL both turned negative: DEV net +0.172 R became -0.021 R (n 1081, day CI -0.175 .. +0.129, ex-best-5 -0.103, placebo p 0.90) and +0.339 R became -0.147 R (n 247, day CI -0.428 .. +0.149, ex-best-5 -0.401, placebo p 0.72). 2 kept cells out of about 480 correlated cells is what chance alone gives with a 5% tail, and 0 of 2 survived.
- **Phase alone does not rescue the NK rules.** In Step A the phase-appropriate direction is not reliably better than the opposite one. Where it wins on VAL (NK2-core DISTRIBUTION short z 3.15, NK3-B DISTRIBUTION z 1.85, NK3-A MARKUP z 1.82) the same phase had the opposite sign or no difference on DEV (NK2-core DISTRIBUTION z -1.52, NK3-A MARKUP z -1.36, NK3-B DISTRIBUTION z -0.88); the DEV winners (NK2-core MARKUP z 2.20, NK2-deep MARKDOWN z 1.92) are not wins on VAL (z -0.38, 0.70). One phase, DISTRIBUTION for NK2-core short, is positive net on VAL (+0.067 R, n 3511, 327 days) and negative on DEV (-0.178 R). In rows with n >= 1000 gross R is between -0.17 and +0.19 R against a cost of 0.08 to 0.19 R, so the fee decides most rows.
- **Untested NK items.** S2/S3 long and R2/R3 short (NK-deep) are net negative on both periods at every level (VAL S3 -0.26, S2 -0.22, R2 -0.08, R3 -0.10 R; DEV -0.26, -0.21, -0.13, -0.36): the claim that S3/R3 are "strong" reactions is not supported as a fee-net edge. The close-basis stop (NK2) versus the intraday stop (alt net column) changes a row by a few hundredths to 0.1 R in either direction, with no systematic winner.
- **Maker row is optimistic.** The fill model (limit at the trigger close, traded through by the next bar) fills 96-98% of the signals, because the next bar nearly always trades below its own previous close, so the maker rows (NK2 cell +0.008 R at 6 bp, NK3-B cell -0.160 R) are sensitivity numbers only and carry the stop-at-maker-fee simplification.
- **Data limits that shape the cells.** Spot 15m signals run 2019-2026; open interest (C4) starts 2021-12-01 for 19 coins and 2020-09-01 for BTC, so every C4 cell uses DEV signals from 2021-12 on, about two years. Funding (C5) files end 2026-10-31. Taker klines and OI end 2026-11-12, so the latest BTC and ETH bars carry NO-DATA for C4, C5 and C6 (today block). No layer fell under the 150-signal NO-DATA bar for any rule. Phase labels, sanity windows and day mix: PRE_REG.md.
- **Provenance.** Spot 15m files were read from `F:\MTS\data_cache\binance_spot` (read-only, sibling-written, keys `t` or `ts` handled in code); cross-checks for BTC: the `binance` venue array equals it on 275620 of 275620 bars (max close difference 0.0), and the 1h bars rebuilt from it equal the downloaded 1h klines on 68873 of 68876 common bars (3 bars differ by up to 0.15% in close: 2020-12-21, 2021-04-23, 2021-12-24; ETH and SOL show 2-3 such bars as well). The shared phase table was overwritten by a sibling worker's builder with a different column layout; `mts_phase.read_phase_csv` reads both layouts, and my own build of the same spec matched on 2874 of 2874 days from 2019-01-01. Execution is spot-equivalent with no funding charge. The code commit was made before any trade outcome was computed (`ff5c77ffa9`), the frozen cells before any VAL statistic (cells_frozen.json commit), and `study.py val` ran once.
- **What this does and does not say.** It says that these NK1h pivot and breakout rules, even inside six MTS phases and eight context buckets chosen on 2019-2023 only, have no fee-net edge in 2024-26. It does not say anything about CAPITULATION (6 VAL days, 52 DEV days), about 15m, about the NK trail exit or the Bollinger blast filter (not tested here), or about the phase labels being right.

