# RESULT: Tom's return-to-value on the prior NY cash-session value area (BTC, ETH, SOL)

**Verdict: FAIL. 0 of 12 cells pass. Price that re-enters the prior NY-session value reaches the OPPOSITE edge only about 40% of the time (his claim 70-80%), and no cell has a fee-net edge on VALIDATION.**

Slug edge4-ny-session-value-1113. Pre-registered in PRE_REG.md (committed before any outcome). Code: fetch_1m.py, study.py, report.py, test_ny_session_value.py, spot_check.py.

## Window, data, rule (state of the run)
- Profile window = prior NY cash session via `auction_context.prior_ny_session_profile` (the previously unused function): 13:30-20:00 UTC in US daylight time, 14:30-21:00 UTC in winter (code `_us_dst`: 2nd Sunday March to 1st Sunday November). Weekdays only; Monday uses Friday; US holidays not modelled; sessions < 90% bars skipped.
- Data: Binance spot 1m klines (data.binance.vision monthly archive), 2020-01-01 (SOL 2020-09-01) to 2026-10-31. BTCUSDT: 3,591,915 bars, 1781 sessions, 1334 open outside prior value; ETHUSDT: 3,591,914 bars, 1781 sessions, 1311 open outside prior value; SOLUSDT: 3,241,455 bars, 1608 sessions, 1258 open outside prior value. No monthly file missing. Spot volume as weight.
- Costs: 5 bp taker + 1 bp slippage per side = 12 bp round trip (fees.py BINANCE_TAKER; the order said 4 bp/side, this is 2 bp/side harsher). Stop at session extreme + 1 bp; trades with stop < 10 bp skipped.
- DEV to 2023-12-31, VALIDATION 2024-01-01 to 2026-10-31. Pooled over three coins, bootstrap by session date (5000), placebo 500 draws, BH 10% over 12 cells.
- Independent check: `spot_check.py` recomputed one prior-session value area (BTC 2024-03-12) without the repo code; VAL/VAH/POC identical to the cent.

## 1. Plain count (Tom's claim): setup = open outside prior value, two 30m closes back inside; reach = price touches the opposite edge before session end (stop ignored)

| cell | n DEV | reach % DEV | n VAL | reach-other-edge % VAL | reach before stop % VAL |
|---|---|---|---|---|---|
| all / skip30 / long | 218 | 39.9 | 180 | 35.6 | 35.0 |
| all / skip30 / short | 278 | 39.9 | 233 | 43.3 | 41.6 |
| all / no-skip / long | 229 | 39.7 | 182 | 35.2 | 33.0 |
| all / no-skip / short | 289 | 40.5 | 244 | 44.7 | 42.6 |
| balanced / skip30 / long | 123 | 43.1 | 101 | 33.7 | 32.7 |
| balanced / skip30 / short | 160 | 44.4 | 150 | 47.3 | 45.3 |
| balanced / no-skip / long | 125 | 44.0 | 102 | 33.3 | 30.4 |
| balanced / no-skip / short | 165 | 44.2 | 155 | 48.4 | 46.5 |
| trending / skip30 / long | 95 | 35.8 | 79 | 38.0 | 38.0 |
| trending / skip30 / short | 118 | 33.9 | 83 | 36.1 | 34.9 |
| trending / no-skip / long | 104 | 34.6 | 80 | 37.5 | 36.2 |
| trending / no-skip / short | 124 | 35.5 | 89 | 38.2 | 36.0 |

Supplementary descriptive counts (NOT pre-registered cells; both splits, pooled sides and coins):

| split | sessions opening outside value | any 1m touch of value % | setup (skip30) n / % of those | setup reaches POC % | setup reaches OTHER EDGE % |
|---|---|---|---|---|---|
| DEV | 2244 | 42.1 | 496 / 22.1 | 67.5 | 39.9 |
| VAL | 1659 | 44.2 | 413 / 24.9 | 69.5 | 40.0 |

Read: his 70% is reproduced for the return to the POC (about 68-70% once two 30m closes are back inside value), not for the opposite edge (about 40%). The trade targets the opposite edge, so the claim the trade needs is the 40%, not the 70%. This POC split was added after seeing the numbers: descriptive, it is not a tested edge.

## 2. Trade result, fee-net, VALIDATION

| cell | n VAL | reach-other-edge % | mean R net | 95% CI | mean R DEV | win % | placebo mean / p95 | beats placebo | BH 10% | verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| all / skip30 / long | 180 | 35.6 | 0.001 | [-0.122, 0.148] | -0.056 | 47.2 | -0.124 / -0.091 | yes | no | FAIL |
| all / skip30 / short | 233 | 43.3 | -0.103 | [-0.195, -0.006] | -0.054 | 45.1 | -0.174 / -0.148 | yes | no | FAIL |
| all / no-skip / long | 182 | 35.2 | -0.099 | [-0.187, -0.010] | -0.078 | 45.1 | -0.125 / -0.086 | no | no | FAIL |
| all / no-skip / short | 244 | 44.7 | -0.114 | [-0.210, -0.018] | -0.055 | 46.7 | -0.193 / -0.165 | yes | no | FAIL |
| balanced / skip30 / long | 101 | 33.7 | 0.037 | [-0.155, 0.291] | -0.065 | 47.5 | -0.092 / -0.041 | yes | no | FAIL |
| balanced / skip30 / short | 150 | 47.3 | -0.074 | [-0.193, 0.056] | -0.030 | 49.3 | -0.177 / -0.142 | yes | no | FAIL |
| balanced / no-skip / long | 102 | 33.3 | -0.088 | [-0.209, 0.029] | -0.047 | 47.1 | -0.098 / -0.034 | no | no | FAIL |
| balanced / no-skip / short | 155 | 48.4 | -0.099 | [-0.212, 0.014] | -0.052 | 51.6 | -0.189 / -0.151 | yes | no | FAIL |
| trending / skip30 / long | 79 | 38.0 | -0.044 | [-0.174, 0.075] | -0.044 | 46.8 | -0.157 / -0.120 | yes | no | FAIL |
| trending / skip30 / short | 83 | 36.1 | -0.157 | [-0.292, -0.022] | -0.087 | 37.3 | -0.168 / -0.123 | no | no | FAIL |
| trending / no-skip / long | 80 | 37.5 | -0.112 | [-0.246, 0.016] | -0.116 | 42.5 | -0.161 / -0.121 | yes | no | FAIL |
| trending / no-skip / short | 89 | 38.2 | -0.140 | [-0.298, 0.018] | -0.059 | 38.2 | -0.203 / -0.159 | yes | no | FAIL |

Pass needs all of: n >= 30, mean > 0, CI lower bound > 0, beats placebo p95, BH 10%. 'Beats placebo' alone is weak here: placebo entries at random times inside value lose about 0.1-0.2 R, so the setup timing beats random entry yet still does not make money.

## 3. Per coin, descriptive (both sides, all days)

| coin | variant | n DEV | mean R DEV | n VAL | reach % VAL | mean R VAL |
|---|---|---|---|---|---|---|
| BTCUSDT | skip30 | 184 | -0.149 | 144 | 40.3 | -0.095 |
| BTCUSDT | no-skip | 193 | -0.161 | 146 | 41.8 | -0.128 |
| ETHUSDT | skip30 | 170 | 0.041 | 123 | 43.1 | -0.037 |
| ETHUSDT | no-skip | 177 | 0.000 | 128 | 43.8 | -0.079 |
| SOLUSDT | skip30 | 142 | -0.047 | 146 | 37.0 | -0.039 |
| SOLUSDT | no-skip | 148 | -0.019 | 152 | 36.8 | -0.111 |

## Regime mix
Regime mix: BTC UTC days, close vs 200-day SMA (band 5%): DEV bull 54.0% / bear 37.0% / range 9.0%; VALIDATION bull 56.4% / bear 29.8% / range 13.8%.
Setups (skip30, all coins) by that label: DEV bull 46.6% / bear 34.1% / range 11.3% (n/a 8.1% = first 200 days, no SMA), balanced-day share 57.1% of 496; VALIDATION bull 59.3% / bear 26.6% / range 14.0%, balanced share 60.8% of 413.
VALIDATION is a bull-leaning window (BTC above its 200d SMA most days); short cells are fading that, long cells riding it.

## Limits
- Spot volume, not perp; US holidays treated as sessions; 30m closes taken from 1m closes; fills at the close with fixed 1 bp slippage; stop gaps inside a 1m bar not modelled.
- Balanced-day rule (inside day OR small opening range) and the 5 bp bin, 10 bp min stop, 1 bp buffer are OURS.
- 12 cells share the same sessions (long/short disjoint, regimes overlap), so cells are not independent.
