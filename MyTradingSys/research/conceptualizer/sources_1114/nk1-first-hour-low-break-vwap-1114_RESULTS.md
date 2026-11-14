VERDICT: FAIL. NK first-hour low-break + close-back + near-VWAP, 20 Binance spot coins, 5m, context-matched, fee-net: 0 of 12 primary VALIDATION rows pass all gates; best row S_NY E3 sess-end maker6 mean net R -0.029 (n=9560).

Pre-registered in PRE_REG.md (committed before any outcome). DEV <= 2023-12-31, VALIDATION >= 2024-01-01. Coins loaded: 20 (BTC ETH BNB XRP ADA LTC TRX LINK XLM DOGE ETC BCH SOL DOT AVAX ATOM UNI VET NEO ZEC). Signals: 71001 coin-session-side triggers.

## Matched rows, VALIDATION (matched direction by phase; fee-net; R = max(structural, 0.5% of price, 0.6 ATR14-5m))

| Session | Exit | Fee | n DEV / VAL | win % | mean net R | fee/R | R % | CI low trade | CI low day | placebo p | placebo mean R | ex-best-5 | BH | gates failed | PASS |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| S_UTC | E1 band | 12bp | 12681 / 10705 | 39.0 | -0.226 | 0.22 | 0.59 | -0.236 | -0.242 | 1.000 | -0.160 | -0.230 | no | mean,cl,tr,plc,bh,ex5 | no |
| S_UTC | E1 band | 6bp maker | 12162 / 10241 | 57.0 | -0.117 | 0.11 | 0.59 | -0.128 | -0.135 | 1.000 | -0.054 | -0.122 | no | mean,cl,tr,plc,bh,ex5 | no |
| S_UTC | E2 prior-day | 12bp | 12681 / 10705 | 28.2 | -0.258 | 0.22 | 0.59 | -0.292 | -0.320 | 1.000 | -0.212 | -0.290 | no | mean,cl,tr,plc,bh,ex5 | no |
| S_UTC | E2 prior-day | 6bp maker | 12162 / 10241 | 28.6 | -0.152 | 0.11 | 0.59 | -0.186 | -0.215 | 1.000 | -0.105 | -0.186 | no | mean,cl,tr,plc,bh,ex5 | no |
| S_UTC | E3 sess-end | 12bp | 12681 / 10705 | 22.0 | -0.236 | 0.22 | 0.59 | -0.280 | -0.322 | 1.000 | -0.181 | -0.288 | no | mean,cl,tr,plc,bh,ex5 | no |
| S_UTC | E3 sess-end | 6bp maker | 12162 / 10241 | 22.7 | -0.123 | 0.11 | 0.59 | -0.166 | -0.207 | 1.000 | -0.067 | -0.173 | no | mean,cl,tr,plc,bh,ex5 | no |
| S_NY | E1 band | 12bp | 15503 / 9852 | 45.4 | -0.213 | 0.20 | 0.66 | -0.225 | -0.235 | 1.000 | -0.139 | -0.219 | no | mean,cl,tr,plc,bh,ex5 | no |
| S_NY | E1 band | 6bp maker | 14935 / 9560 | 58.7 | -0.109 | 0.10 | 0.66 | -0.120 | -0.131 | 1.000 | -0.039 | -0.115 | no | mean,cl,tr,plc,bh,ex5 | no |
| S_NY | E2 prior-day | 12bp | 15503 / 9852 | 34.7 | -0.163 | 0.20 | 0.66 | -0.194 | -0.234 | 1.000 | -0.135 | -0.204 | no | mean,cl,tr,plc,bh,ex5 | no |
| S_NY | E2 prior-day | 6bp maker | 14935 / 9560 | 35.5 | -0.059 | 0.10 | 0.66 | -0.092 | -0.129 | 1.000 | -0.036 | -0.100 | no | mean,cl,tr,plc,bh,ex5 | no |
| S_NY | E3 sess-end | 12bp | 15503 / 9852 | 28.2 | -0.136 | 0.20 | 0.66 | -0.177 | -0.229 | 0.995 | -0.100 | -0.191 | no | mean,cl,tr,plc,bh,ex5 | no |
| S_NY | E3 sess-end | 6bp maker | 14935 / 9560 | 29.2 | -0.029 | 0.10 | 0.66 | -0.070 | -0.125 | 0.995 | +0.000 | -0.084 | no | mean,cl,tr,plc,bh,ex5 | no |

DEV mean net R (same rows, descriptive): S_UTC E1 band t -0.180; S_UTC E1 band m -0.079; S_UTC E2 prior-day t -0.049; S_UTC E2 prior-day m +0.045; S_UTC E3 sess-end t -0.046; S_UTC E3 sess-end m +0.051; S_NY E1 band t -0.217; S_NY E1 band m -0.113; S_NY E2 prior-day t -0.181; S_NY E2 prior-day m -0.075; S_NY E3 sess-end t -0.130; S_NY E3 sess-end m -0.021

## Control rows (mismatched direction in UP/DOWN days; VALIDATION; descriptive, never in the verdict)

| Session | Exit | Fee | n | mean net R | CI low day |
|---|---|---|---|---|---|
| S_UTC | E1 band | 12bp | 4797 | -0.220 | -0.246 |
| S_UTC | E1 band | 6bp | 4581 | -0.112 | -0.140 |
| S_UTC | E2 prior-day | 12bp | 4797 | -0.265 | -0.361 |
| S_UTC | E2 prior-day | 6bp | 4581 | -0.157 | -0.252 |
| S_UTC | E3 sess-end | 12bp | 4797 | -0.304 | -0.416 |
| S_UTC | E3 sess-end | 6bp | 4581 | -0.194 | -0.311 |
| S_NY | E1 band | 12bp | 4290 | -0.188 | -0.219 |
| S_NY | E1 band | 6bp | 4156 | -0.087 | -0.119 |
| S_NY | E2 prior-day | 12bp | 4290 | -0.112 | -0.229 |
| S_NY | E2 prior-day | 6bp | 4156 | -0.017 | -0.133 |
| S_NY | E3 sess-end | 12bp | 4290 | -0.036 | -0.224 |
| S_NY | E3 sess-end | 6bp | 4156 | +0.058 | -0.130 |

## Context
Phase for each day from data known at the prior close: 20-day MA slope (5-day lag) plus ADX(14) >= 20 with DI direction, else RANGE. Longs in UP, shorts in DOWN, fades both ways in RANGE are the primary rows; the opposite direction in UP/DOWN is the control table.

Regime mix: share of coin-days by phase, and share of coin-days with close above the own 200-day SMA.

| Split | UP | DOWN | RANGE | bull (>200d SMA) | flag |
|---|---|---|---|---|---|
| DEV | 32% | 32% | 36% | 46% | mixed |
| VALIDATION | 25% | 36% | 39% | 44% | mixed |

## Matched VALIDATION by phase (taker 12bp, mean net R, n)

| Session | Exit | Phase | n | mean net R |
|---|---|---|---|---|
| S_UTC | E1 band | UP | 1834 | -0.248 |
| S_UTC | E1 band | DOWN | 2819 | -0.207 |
| S_UTC | E1 band | RANGE | 6052 | -0.227 |
| S_UTC | E2 prior-day | UP | 1834 | -0.322 |
| S_UTC | E2 prior-day | DOWN | 2819 | -0.201 |
| S_UTC | E2 prior-day | RANGE | 6052 | -0.265 |
| S_UTC | E3 sess-end | UP | 1834 | -0.317 |
| S_UTC | E3 sess-end | DOWN | 2819 | -0.181 |
| S_UTC | E3 sess-end | RANGE | 6052 | -0.238 |
| S_NY | E1 band | UP | 1884 | -0.219 |
| S_NY | E1 band | DOWN | 2406 | -0.204 |
| S_NY | E1 band | RANGE | 5562 | -0.215 |
| S_NY | E2 prior-day | UP | 1884 | -0.292 |
| S_NY | E2 prior-day | DOWN | 2406 | -0.074 |
| S_NY | E2 prior-day | RANGE | 5562 | -0.158 |
| S_NY | E3 sess-end | UP | 1884 | -0.292 |
| S_NY | E3 sess-end | DOWN | 2406 | +0.014 |
| S_NY | E3 sess-end | RANGE | 5562 | -0.149 |

## BTC today (descriptive, no advice)

- Data ends 2026-11-13 20:55 UTC (last closed 5m bar). Prior UTC day (2026-11-12): H 74217, L 71113, C 71460.
- Phase for UTC day 2026-11-13 (rule from the prior close): DOWN.
- S_UTC (open 00:00 UTC), 12 of 12 first-hour bars in: opening-range low 71300 / high 71514; low broken in hour: yes (bar 3); high broken in hour: no; session VWAP 71084, last close 71124.
- S_NY (open 14:30 UTC), 12 of 12 first-hour bars in: opening-range low 68891 / high 69488; low broken in hour: yes (bar 4); high broken in hour: no; session VWAP 68928, last close 68639.

## Labels
SOURCED (NK): low break early in the session (first 10 min, sometimes 30), close back up, entry near VWAP without waiting for an exact touch, all inside the first hour, no big candle, stop = low breaks or 1h under VWAP. OURS: crypto sessions (00:00 UTC, NY cash open), opening-range low = first 3 bars, near-VWAP tolerance 0.1%, big-candle cutoff 2.5x, min stop 0.5% / 0.6 ATR, three exits, session lengths (12h UTC, NY close), 5-day-slope phase rule, placebo design, fees 12bp / 6bp.

Placebo: random entry bar b3..b12 on the same coin-session and side, same R in price terms, same exit machinery, 200 draws (maker rows use 6bp fee with open-entry placebo). Bootstrap: 5000 resamples, seed 1114, cluster = UTC date.
