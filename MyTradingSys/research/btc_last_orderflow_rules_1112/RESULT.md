# RESULT: BTC last untested order-flow rules (btc-last-orderflow-rules-1112), DEV 2022-02-01 .. 2024-05-31

**All five arms FAIL on DEV: none reaches the bar (mean net > 0, t >= 2, both halves > 0). R11d has n 158 < 180 (INSUFFICIENT_N, also negative). VALIDATION was not read. No fee-net edge from these rules.**

PREREG.md was frozen and shipped before this file (commit 1e2b0a436, 2026-11-12 18:09:38 +05:30; on trunk as 41630902). Code `rules.py`, tests `test_rules.py` (19 pass; every rule has a wrong-rule test that must fail), look-ahead lint: no FAIL hit in this folder. Fee 0.10 % round trip, 60-minute hold, entry at the next 1m open. Data: 1m klines only (delta = 2 x taker_buy - volume, the same quantity as aggTrades summed by aggressor side; aggTrades not needed, not read).
Regime mix: DEV days bull 301, bear 136, range 355, n/a 59 (90-day return +-20 %). Each arm's own event mix is in the last table column.

## Verdict arms
| arm | n (L/S) | mean net % | sd | t | half 1 / half 2 (net %) | share pos | placebo mean (p1..p99) | placebo percentile | verdict | Regime mix |
|---|---|---|---|---|---|---|---|---|---|---|
| R8a trend-down no extreme -> short | 4272 (0/4272) | -0.0953 | 0.586 | -10.63 | -0.0777 (n 2223) / -0.1144 (n 2049) | 32.8 % | -0.1043 (-0.1215..-0.0859) | 86.8 | FAIL | bear 761 bull 1415 n/a 257 range 1839 |
| R8b trend-down sell extreme -> long | 710 (710/0) | -0.0648 | 0.888 | -1.94 | -0.0461 (n 410) / -0.0904 (n 300) | 51.3 % | -0.0957 (-0.1432..-0.0467) | 92.8 | FAIL | bear 157 bull 203 n/a 55 range 295 |
| R5 open inside prior VA, fade first edge touch | 496 (246/250) | -0.1173 | 0.777 | -3.36 | -0.1276 (n 214) / -0.1095 (n 282) | 48.8 % | -0.1003 (-0.1601..-0.0398) | 24.8 | FAIL | bear 70 bull 179 n/a 29 range 218 |
| R11p breakout, volume persists, with the break | 546 (288/258) | -0.0739 | 0.599 | -2.88 | -0.0830 (n 262) / -0.0655 (n 284) | 35.9 % | -0.1000 (-0.1545..-0.0476) | 85.8 | FAIL | bear 87 bull 203 n/a 34 range 222 |
| R11d breakout, volume dries up, with the break | 158 (74/84) | -0.1423 | 0.447 | -4.00 | -0.0994 (n 79) / -0.1853 (n 79) | 29.1 % | -0.0996 (-0.2112..+0.0055) | 15.0 | INSUFFICIENT_N | bear 23 bull 53 n/a 10 range 72 |

Rules: y67l86cSqb8 R8 (short in a falling market until selling delta is big; R8b is OURS reading of the extreme as the end), 9IliXww64uM R5 (open inside prior-day value, fade the edge, both sides) and R11 (breakout whose volume persists, traded with the break). SOURCED or OURS for every parameter is in PREREG.md.

## Reading
- R8a (short, no sell extreme): n 4272, gross about +0.005 %, net -0.095 %, t -10.6. The trend-down state carries no hour-ahead drift on BTC, so the fee is the whole loss. Placebo percentile 86.8: not different from random same-hour shorts.
- R8b (long after a sell extreme): n 710, net -0.065 %, t -1.94, both halves negative, placebo percentile 92.8.
- R8 descriptive (the quote's "before vs the extreme"), mean gross of a short in trend-down hours: after a sell extreme n 710, -0.035 %; without an extreme n 7725, +0.002 %. A small rebound follows extremes, as the author reads it, but about 0.035 % gross cannot pay 0.10 %.
- R5: n 496 (246 long, 250 short), net -0.117 %, t -3.36, both halves negative, placebo percentile 24.8: fading the prior-day value-area edge loses at least as much as random. Descriptive: of 532 days that open inside the prior value area only 5.1 % stay inside it all day (days opening outside: 0.0 % of 319); at this value-area width (70 %, 0.05 % bins, OURS) "stay inside for the rest of the day" is not what BTC does.
- R11p: n 546, net -0.074 %, t -2.88, both halves negative, placebo percentile 85.8. R11d (dry-up group): n 158 < 180, net -0.142 %, INSUFFICIENT_N. Persisting volume loses less than dry-up, but both are below the fee: prior-day value-area breakouts do not continue on average within an hour.
- The per-year and long/short rows show the loss is spread across every cut, not hidden in one.

## Per-year and long/short (trade_sanity.year_side_lines, net %)

R8a trend-down no extreme -> short

| cut | n | mean | sum |
|---|---|---|---|
| year 2022 | 1819 | -0.0724 | -131.6947 |
| year 2023 | 1766 | -0.1086 | -191.7297 |
| year 2024 | 687 | -0.1219 | -83.7602 |
| long | 0 | nan | 0.0000 |
| short | 4272 | -0.0953 | -407.1845 |

R8b trend-down sell extreme -> long

| cut | n | mean | sum |
|---|---|---|---|
| year 2022 | 342 | -0.0416 | -14.2289 |
| year 2023 | 255 | -0.0536 | -13.6746 |
| year 2024 | 113 | -0.1604 | -18.1204 |
| long | 710 | -0.0648 | -46.0239 |
| short | 0 | nan | 0.0000 |

R5 open inside prior VA, fade first edge touch

| cut | n | mean | sum |
|---|---|---|---|
| year 2022 | 164 | -0.0803 | -13.1686 |
| year 2023 | 244 | -0.1659 | -40.4897 |
| year 2024 | 88 | -0.0514 | -4.5198 |
| long | 246 | -0.1028 | -25.2960 |
| short | 250 | -0.1315 | -32.8821 |

R11p breakout, volume persists, with the break

| cut | n | mean | sum |
|---|---|---|---|
| year 2022 | 208 | -0.0535 | -11.1316 |
| year 2023 | 233 | -0.1000 | -23.2919 |
| year 2024 | 105 | -0.0564 | -5.9170 |
| long | 288 | -0.0920 | -26.5029 |
| short | 258 | -0.0536 | -13.8376 |

R11d breakout, volume dries up, with the break

| cut | n | mean | sum |
|---|---|---|---|
| year 2022 | 60 | -0.1101 | -6.6072 |
| year 2023 | 73 | -0.0976 | -7.1272 |
| year 2024 | 25 | -0.3501 | -8.7531 |
| long | 74 | -0.1862 | -13.7795 |
| short | 84 | -0.1037 | -8.7080 |

Log sanity: for each arm `trade_sanity.log_sanity` matched the last five fills to their 1m klines (entry at the bar open, exit at the bar close), printed by `python rules.py`.

## Not done / limits
- DEV only; one fixed 60-minute hold (a 240-minute hold failed the power gate in PREREG). These are the rules as frozen, not every reading of them.
- The verdict registry was not touched (no `verdicts.py backfill`, no hand edit).
- Phase gate is each rule's own state (down-trend, open inside value, fresh breakout); no cycle-phase split beyond the regime mix.
- Raw numbers: `results.json`, written by `rules.py`.
