Verdict: T05=FAIL (DEV screen failed: n=300, mean net R -0.086 +- 0.081 SE, CI95 [-0.245, +0.074], MDE80 0.228 R; mean <= 0 and CI upper below MDE, so FAIL; VALIDATION not read, per the screen rule)

## Answer in plain words
The frozen T05 cell (fast in + reclaim within 3 bars + at most 2 bars within 0.2 % of the level, fade at the prior-day high or low, stop at the extreme, 2R or 96 bars, both sides pooled, BTC 15m, DEV 2020-01-01..2024-06-30) loses money after costs on DEV: mean net R -0.086, with a day-clustered SE of 0.081. Its CI excludes any edge as large as the 0.23 R MDE, so this is a fail, not an underpowered maybe. It is negative in every DEV year (2020 -0.14, 2021 -0.11, 2022 -0.06, 2023 -0.03, 2024 H1 -0.02, all with wide CIs). Gross R is +0.115; the costs (mean fee_r 0.20 R on stops of about 60 bps) take the mean below zero.

The descriptive 2x2 (exploratory, cannot promote) shows the direction of the WICKS_NOTE s5 contrast: fast-in touches that do not spend time at the level ("fast/time<=2") continue 47.5 % of the time, while fast-in touches that do spend time there ("fast/time>2") continue 65.7 % of the time and lose -0.48 R on average. The only cell with a positive mean is fast/time<=2 (+0.054 R, n=240), but it uses time measured over t..t+7 (bars after the entry, descriptive only), it is not the frozen trade-time cell, and it is not a screened result. It does not justify a testnet card.

## Context
- Regime: research_kit.regime_tag reported as the mix line below; not a gate for T05.
- Phase: none for T05 (all phases tested, mix reported).
- Session: none (daily-level rule, no session gate in the brief).
- Entry: reclaim close (taker) at the first bar in t..t+3 with the close strictly back inside (PDL, PDH).

Regime mix: 234 weeks: bull 37 (16%) | bear 0 (0%) | range 132 (56%) | n/a 65 (28%) (DEV Monday weeks; n/a = before 200 daily closes or 15 monthly closes; research_kit tags; 0 bear weeks as in the repo's known note).

## Counts (no returns)
- Touches (first bar beyond PDH or PDL per UTC day, DEV): 1275 (high 2020 161 / 2021 165 / 2022 145 / 2023 142 / 2024H1 79; low 105 / 144 / 151 / 121 / 62).
- Skipped days: no_break 366, both_sides 1, no_prior_day 1, gap 0, lookback_outside 0.
- Reclaim within 3 bars: 867 touches; no reclaim 408.
- Fast cut-off (66.67th percentile of speed-in over all 1275 DEV touches): 0.08679781992469922 % per bar (frozen before returns, PRE_REG).
- Censored by the split end: 0 on DEV.

## T05 (DEV, the one screened cell)
| n | hit (target before stop) | mean gross R | mean fee_r | mean funding R | mean net R | SE (day cluster) | CI95 | MDE80 | p one-sided |
|---|---|---|---|---|---|---|---|---|---|
| 300 | 0.337 | +0.115 | 0.202 | -0.0004 | -0.086 | 0.081 | [-0.245, +0.074] | 0.228 | 0.85 |

Per-year, DEV (net R, n, SE):
| year | n | mean net R | SE | CI95 |
|---|---|---|---|---|
| 2020 | 65 | -0.140 | 0.168 | [-0.470, +0.190] |
| 2021 | 104 | -0.106 | 0.138 | [-0.376, +0.164] |
| 2022 | 73 | -0.056 | 0.173 | [-0.396, +0.284] |
| 2023 | 34 | -0.032 | 0.241 | [-0.504, +0.440] |
| 2024 (H1) | 24 | -0.018 | 0.281 | [-0.568, +0.532] |

## Exploratory 2x2 (DEV, touches with a reclaim within 3 bars; time over t..t+7, descriptive; cannot promote)
| cell | n | reversal rate (target before stop) | continuation rate | mean net R |
|---|---|---|---|---|
| fast / time<=2 | 240 | 0.367 | 0.475 | +0.054 |
| fast / time>2 | 67 | 0.269 | 0.657 | -0.475 |
| slow / time<=2 | 323 | 0.368 | 0.474 | -0.054 |
| slow / time>2 | 237 | 0.300 | 0.578 | -0.474 |

Continuation = price reaches the level plus 1 stop distance (R) before the 2R target within 96 bars (path-based, ignores the stop; DECISION (OURS) below).

## VALIDATION
Not read. The DEV screen failed (dev_passed.json = false), so VALIDATION was refused by the code, as the brief requires.

## Reproduce
`speed_time.py count`, `speed_time.py dev` (writes trades and summaries to the F: cache, not the repo). Tests: `python -m pytest test_speed_time.py -q` (12 pass). First run before the code existed: `ERROR ... 1 error in 1.14s` (ModuleNotFoundError: speed_time).

## DECISION (OURS)
1. Data start 2020-01-01, not 2019-09. The archive returned 404 for BTCUSDT 15m klines 2019-09..2019-12 (monthly and daily, checked). DEV = 2020-01-01..2024-06-30.
2. DEV definition uses the brief's "data start", not repo splits.py DEV_START (2022-01-01). The split boundary 2024-07-01 and HOLDOUT 2025-07-01 match splits.py.
3. One touch per UTC day: the first 15m bar beyond PDH or PDL. The brief's "close 12 bars earlier inside" is read as close[t-12] strictly inside (PDL, PDH); if it fails, the day has no touch (counted as lookback_outside = 0 in this data).
4. Reclaim: first bar in t..t+3 whose close is strictly inside, k = 0 allowed.
5. Fee: 12 bps round trip (10 bps taker per fees.py DERIBIT_TAKER plus 2 bps slippage from the brief). FORMULAS.md s13 is not in this worktree; the slippage amount is the brief's value.
6. Funding sign: longs pay positive funding, shorts receive it (standard convention; FORMULAS s13 not found). Mean funding effect in this cell is -0.0004 R, immaterial.
7. Continuation definition in the 2x2 (see above) is OURS and descriptive.
8. The 2x2 time measure uses bars after the entry (t..t+7), which the brief allows for descriptive use only; the frozen T05 cell uses trade-time (t..r) only.
9. Holm threshold 0.05/15 is the conservative first step (not used: no VALIDATION read).
10. Entry at the reclaim close at the close price (taker), no extra fill model; a time-stop exits at the close of bar r+96.

## Noticed
- The archive has no BTCUSDT 15m before 2020-01; this is a data fact, not a result.
- The T05 cell is almost the same as "fast in + reclaim": time_trade <= 2 holds for 300 of 307 fast reclaim touches, because the reclaim comes within 3 bars. The time-at-level filter barely bites in the frozen cell. The sharper contrast is the descriptive time measure, which is not the frozen rule.
- The worktree is at C:/Users/E-ngineers/IdeaProjects/mts-jis-nb-eh-h4-speed-time-at-level (sync start printed it); the run_cmd tool does not run shell pipes or `;`, so commands were single calls.
- F:/MTS/Dumps cache holds the 15m klines and fundingRate CSVs (not committed).
