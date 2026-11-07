# Plan: ADX/DI crosses, volume at levels, the Sep-15 low (CBP update, 2026-11-07, Lead C)

Status: PROPOSAL for discussion with the operator. Nothing below is started. Analyst calls are context, never signals
(cbp-is-the-context-source). Every parameter below is OURS unless a quote gives it.

## 1. What the sources say (read 2026-11-07 12:30Z, captions in the canonical store)

| Source | Video | What he says (SOURCED) |
|---|---|---|
| CCU (Steve) | AnAx1PanZm4, 2026-11-05, "WARNING: HISTORY IS REPEATING", 2-day chart, ADX+DI | Red DI above green = "sellers are in control"; a red cross is "rare". Three steps after a red cross: "1-3 weeks of consolidation", "falling straight to the bottom", "the market consolidates and then changes trend". His three cases: Oct 2025 (about 36 % from the cross, "a little over a month"), Jan 2026 (about 37 %, "a little less than a month", "the strongest trend in the last few years" on ADX), May 2026 (26 % from the cross, 30 % swing to swing). "These dips aren't getting stronger, they're getting a little weaker." The 11-05 cross: "less than 24 hours later the lines crossed back"; three possibilities; "watch which signal will actually be confirmed". ADX (yellow) = trend strength: "if it rises very high, it means that the trend strength is very powerful". No numeric threshold anywhere. |
| Michael Pizzino | WHH4qSfCCyM, 2026-11-06 (already in the CBP store as 6 rows) | BTC "still holding above its low from September 15"; higher low "around $77,800" is the first step back to "the 80,000 range"; "if the level of 75 thousand does not hold" then 71-73k, "even a little lower"; below those with "lower highs on higher timeframes" the 57-58k lows "would be at risk". Volume: on gold he wants "significantly lower volumes" on the dip; an "anomalous bar ... huge volume" can change a trend. No BTC volume number. |
| Krown | e2-KjJdWbgM, 2026-11-05 (in the store) | 75,000 weekly close = line in the sand; 73,300 / 70,800 / 68,100 / 65,700 below; 81,900 reclaim ends the downtrend. No 11-06 or 11-07 video at 12:30Z. |

## 2. The Sep-15 low, measured (Bybit spot; Binance in brackets)

| | Low | When |
|---|---|---|
| Sep-15 low | 74,961 (74,968) | 2026-09-15 |
| Nov-6 low | 74,871 (74,888) | 2026-11-06 15:00 UTC, 1h candle |
| Break | 90 USD = 0.12 % | daily close 11-06: 75,848; 11-07 12:00Z: 76,007 |

Reading (OURS): a sweep of the low, not a breakdown, until a daily close under 74,900 and a lower high under 77,800
(Michael's line) print. The weekly close (Mon 00:00 UTC) decides Krown's 75,000 line. Michael's 11-06 video was recorded
before the 15:00 UTC break, so his "still holding" is one day stale; his conditional (lower highs on higher timeframes
after the break) is the one to watch. Bible clocks unchanged: the bottom read breaks only on a weekly close under 60,000
or a new low under 57,800.

## 3. The plan: measure first, phase first, nothing enters a layer before its measurement

| # | Piece | What is measured | Inputs that exist | Lands in |
|---|---|---|---|---|
| M1 | ADX/DI engine | Wilder DI+, DI-, ADX(14) as a new FORMULAS.md section, computed independently, test fails on old code; 2d/1d/4h/1h via tf_resample (2d bucket exists) | timeframe/tf_resample.py | backtest/layers/adx/ |
| M2 | Cross census | every 2d DI cross 2020-2026 (DEV+VALIDATION, HOLDOUT sealed): bars to the next swing low, depth %, whipsaw rate (cross back within 1-3 bars). Checks Steve's 3 cases against ALL cases | research/btc_cycles_2026-11/btc_daily.csv | research/adx_di_2026-11/ |
| M3 | Fake-out filter = ADX state at the cross | ADX level bucket (<20, 20-40, >40) and slope (falling from a high vs rising) at the cross; whipsaw rate and depth per bucket. H1 (operator's visual): a cross while ADX falls from a high is exhaustion, weaker follow-through | M1 | same |
| M4 | Timeframe cascade | lead of 1h/4h/1d crosses before each 2d cross (bars), and the share of LTF crosses that reach a 2d cross within N bars. Answers "do lower timeframes confirm the 2d" | M1 | same |
| M5 | Volume at Tom/Fabio levels | at every touch of a POC, value-area edge or FAB real-FVG: relative volume (RVadj) and taker delta at the touch, then reaction vs acceptance, by 15m/1h/4h, split by phase (trend vs balance). Levels, not events: the 10-09 volume study tested events (NO-EDGE) and never levels | fabio_volume_fvg.py, alerts/live_levels_confluence.py (FORMULAS 18.1 POC), 1m data on F:/MTS | fabio lane, G2 context column |
| M6 | CBP indicator rows | CCU to actionable=partial; the extractor gets a `conditions` field (indicator-state claims) so "2d DI red cross 11-04, flipped 11-05" is stored and scored like a level | cbp_run.py, cbp_v2/analysts.json | S4 CBP module |
| M7 | Visual read | Gemini low-effort pass over the CCU chart frames (ADX value at each of the 3 crosses, quotes verified) | gemini_queue.py on the NUC (NUC has 11 unacked broadcasts: it needs a session) | research/adx_di_2026-11/ |
| M8 | Monday wave | `cbp_run.py --force` Sun 20:00Z and Mon 06:00Z by the coordinator (no scheduler): Krown, Michael, Cowen, Qriptal rows before the open | cbp_run.py | CBP store |

Rule for going live (phase-first-testnet-forward): any M2-M5 pattern valid in the current phase (post-sweep bounce inside a
2d downtrend) goes to testnet as a flag/alert first, runs until it fails; no long backtest gate, no core.

## 4. Fit with the roadmap (D7)
- S3 run list: item 7 "ADX/DI 2d cross census" (new sourced hypothesis, so allowed; RSI deep-buy stays parked).
- S4 CBP module: M6 and M8.
- Fabio G2 live validation: M5 is a context column, not a filter (Tom/Fabio stay as sourced).
- No new gate, no scheduler, no core.

## 5. Budget and who runs it
Login C week at 61 % against the 60 % cap (reset 2026-11-10T20Z). M1-M4 fit one api_job.py Sonnet credit job (one
script, local daily data) or one Sonnet session after the reset. M5 is a Sonnet session after the reset (1m data). M6-M8
are Haiku. M7 needs the NUC awake.

## 6. Questions for the operator (defaults in brackets)
1. M1-M4 now on the API credit [yes, api_job Sonnet] or after the Monday reset?
2. M5 scope: Tom POC/value edges and FAB real-FVG [both] or FAB only?
3. CCU to actionable=partial for indicator rows [yes]?
4. Depth of the cascade: 1h/4h/1d [all three] or 4h/1d only?
