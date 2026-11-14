# RESULT nk4-hilega-milega-recon-1114

**VERDICT: FAIL. No row passes any gate. All 12 matched rows (3 tf x raw/confirmed x 12bp/6bp) have negative mean net R on VALIDATION (-0.09R to -0.23R), CI lows below zero, placebo p 0.58 to 1.00. Fee alone is 0.07-0.24R. HM state flip (OURS reconstruction) has no gross edge: net R is about -fee.**

Rule: NK Hilega Milega (cmH38Uo4sYM). Formula never given by NK; RSI9 / EMA3 / WMA21 reconstruction and all exits/stops are OURS (see PRE_REG.md). SOURCED: tf 5/10/15m, RSI14 on 15m, 30/70 zones. Data: Binance spot 5m (data.binance.vision), 20 coins, 2019 onward; DEV to 2023-12-31, VAL from 2024-01-01.

## Matched rows, VALIDATION (long in UP, short in DOWN, both in RANGE)

| tf | filter | cost | n DEV | n VAL | win % | mean net R | CI lo trade | CI lo day | placebo p | ex-best-5 | BH | fee R (med) | PASS |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 5m | raw (control) | 12bp | 1489597 | 989789 | 21.5 | -0.219 | -0.220 | -0.223 | 0.947 | -0.220 | False | 0.240 | False |
| 5m | raw (control) | 6bp | 1489597 | 989789 | 27.4 | -0.109 | -0.110 | -0.112 | 0.934 | -0.110 | False | 0.120 | False |
| 5m | confirmed | 12bp | 12442 | 9259 | 21.3 | -0.226 | -0.237 | -0.240 | 0.867 | -0.231 | False | 0.240 | False |
| 5m | confirmed | 6bp | 12442 | 9259 | 27.1 | -0.125 | -0.136 | -0.140 | 1.000 | -0.130 | False | 0.120 | False |
| 10m | raw (control) | 12bp | 749163 | 500782 | 23.9 | -0.197 | -0.199 | -0.203 | 1.000 | -0.199 | False | 0.212 | False |
| 10m | raw (control) | 6bp | 749163 | 500782 | 28.6 | -0.101 | -0.103 | -0.107 | 1.000 | -0.103 | False | 0.106 | False |
| 10m | confirmed | 12bp | 6449 | 4932 | 28.1 | -0.194 | -0.216 | -0.230 | 0.581 | -0.218 | False | 0.170 | False |
| 10m | confirmed | 6bp | 6449 | 4932 | 31.9 | -0.109 | -0.131 | -0.142 | 0.934 | -0.132 | False | 0.085 | False |
| 15m | raw (control) | 12bp | 503268 | 337423 | 25.1 | -0.176 | -0.178 | -0.183 | 1.000 | -0.178 | False | 0.168 | False |
| 15m | raw (control) | 6bp | 503268 | 337423 | 29.0 | -0.091 | -0.094 | -0.098 | 1.000 | -0.094 | False | 0.084 | False |
| 15m | confirmed | 12bp | 17010 | 12897 | 29.6 | -0.192 | -0.205 | -0.215 | 1.000 | -0.200 | False | 0.143 | False |
| 15m | confirmed | 6bp | 17010 | 12897 | 33.0 | -0.116 | -0.129 | -0.137 | 1.000 | -0.124 | False | 0.072 | False |

## Control rows: mismatched direction (short in UP, long in DOWN), VALIDATION

| tf | filter | cost | n VAL | win % | mean net R |
|---|---|---|---|---|---|
| 5m | raw | 12bp | 425345 | 22.1 | -0.216 |
| 5m | raw | 6bp | 425345 | 27.6 | -0.109 |
| 5m | conf | 12bp | 4140 | 25.0 | -0.169 |
| 5m | conf | 6bp | 4140 | 30.0 | -0.077 |
| 10m | raw | 12bp | 214465 | 24.5 | -0.189 |
| 10m | raw | 6bp | 214465 | 28.8 | -0.098 |
| 10m | conf | 12bp | 2295 | 32.2 | -0.127 |
| 10m | conf | 6bp | 2295 | 36.4 | -0.052 |
| 15m | raw | 12bp | 144505 | 25.7 | -0.164 |
| 15m | raw | 6bp | 144505 | 29.4 | -0.085 |
| 15m | conf | 12bp | 5729 | 33.1 | -0.124 |
| 15m | conf | 6bp | 5729 | 36.0 | -0.057 |

Mean net R DEV for matched rows is also negative (-0.08 to -0.21; see results.json). Mismatched controls are about as bad as matched: phase gives no directional help.

## Context
Daily phase from data to prior close: MA20 5-day slope + ADX(14)>=20 with DI direction, else RANGE. Day-weighted over 20 coins.

Regime mix: DEV coin-days NA 820 / UP 9902 / DOWN 10100 / RANGE 11296 (UP 32%, DOWN 32%, RANGE 36%); VAL coin-days UP 5084 / DOWN 7163 / RANGE 8157 (UP 25%, DOWN 35%, RANGE 40%).

## Why it fails
- The HM state flips constantly: median hold 10 min on 5m, 40 min on 10m, 90 min on 15m (confirmed rows 10-135 min). Win rate 21-33%.
- Min stop floor (max(1.5 ATR, 0.5%)) makes fee 0.24R at 12bp on 5m, 0.14-0.17R on confirmed 10m/15m. Gross R is about zero (net + fee), so fees decide.
- The 15m RSI14 30/70 + all-tf agree confirm cuts trades 100x but does not lift gross R; the 6bp maker row is still negative.
- Placebo (random same-coin, same-phase, same-hold entries) does as well or better.

## BTC today (descriptive only, no advice)
Data ends 2026-11-13T00:00:00.000 UTC (last complete day 2026-11-12). Close 71460. Next-day phase label: DOWN (below MA20 77340). HM state 5m/10m/15m: 1/1/1 (buy=1). 15m RSI14 43.8 (last 3 bars 35.8 to 43.8; not in the 30/70 zone). ATR14 15m 212. Prev day high 74217, low 71113; 7d high 76416 low 71113; 30d high 84898 low 71113. Today's setup would be: HM buy state with RSI14 mid-range, so no confirmed signal.

## Method notes
Pre-registered (PRE_REG.md, sha 86e164fab). Entry next 5m open after signal bar close; stop intrabar (gap fills at open); exit on HM state loss or 48 signal bars. Placebo: 300 draws, trade set subsampled to 20000 if larger (5m/10m/15m raw), seed 11. BH over 24 rows using one-sided day-cluster bootstrap p. Wilder smoothing via pandas ewm (adjust=False). Gaps in 5m data forward-filled. Tests: test_study.py (3 pass; causality and no-edge tests fail under STUDY_BUG=1, third test confirms that). Raw data in F:\MTS\data_cacheinance; results.json holds all numbers.
