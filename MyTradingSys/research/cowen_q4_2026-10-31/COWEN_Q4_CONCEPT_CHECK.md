# Cowen video bekghgecip8: does MTS already know this, is it used for edge, how to apply (2026-10-31)

Video: Benjamin Cowen, "Bitcoin: The Q4 Dump is Here", published 2026-10-30, 26:26. Extract: `extracts/processed/cowen/extract_bekghgecip8.md`
(40 quotes in sections W1..W10, verify_extract_quotes exit 0). Checked against trunk at 563ad5793 (2026-10-31).
Context already on trunk: `research/yt_feed_2026-10-31/COWEN_LEVELS_2026-10-31.md` (4 items from this video, 8 videos in all) and the CBP row for this video
(Benjamin, BEARISH, 6 quotes). The CBP scorecard rates Benjamin "thesis-only, 0 calls, NOT ENOUGH CALLS" (`research/cbp/SCORECARD_GPT.md:29`).

## 1. Concept by concept

| # | Concept (his words, section) | MTS knows it? | Used for edge? | Tested on the desk |
|---|---|---|---|---|
| 1 | Bull market support band = 20-week SMA and 21-week EMA; a bounce off it, then the final drop [W2, W6] | Only as text: COWEN_LEVELS and the CBP row. No code, no formula, no layer | NO | BOUNCE idea, 3 to 7 trades: NOT ENOUGH DATA (rows 1-4) |
| 2 | Two weekly closes below a prior range high (83k) = fake-out confirmed [W1] | Only as text (the 83k level in CBP) | NO | Not generalisable: one level, one event. Not tested |
| 3 | Everything else is at its band, Bitcoin is not: Bitcoin catches down [W2] | NO | NO | CATCHDOWN with ETH as the "everything else", 6 to 10 trades: NOT ENOUGH DATA (rows 10-12). 1 win in 10 trades in the 3 % version |
| 4 | Close below the 50-day starts the fake-out case, at least to the band (earlier video bWdXPK3Hlok) | NO | NO | FAKEOUT idea, 9 to 10 trades, +0.07 to +0.14 R, range spans zero: NOT ENOUGH DATA (rows 7-9) |
| 5 | Band given up at once with no support = the drop is over early [W7] | NO | NO | LOSE idea, 6 to 7 trades, -0.23 and +0.24 R: NOT ENOUGH DATA (rows 5-6) |
| 6 | Every midterm year has a Q1 low, a summer low and a Q4 low; the final low comes after the midterms [W3] | NO | NO | Cannot be tested. Three events: 2014 (he says "not as clean"), 2018, 2022. The desk window holds one of them |
| 7 | Rate-hike lag: Bitcoin holds a month and a half, then drops [W5] | NO | NO | Cannot be tested: two prior cases (2018, 2022) by his own count |
| 8 | Shape analogs: 2015 (-40 % in a day, a week on the 21-week EMA), 2020, FTX 2022 (-24 % in two days) and the SpaceX and Anthropic IPO chart [W6] | NO | NO | Cannot be tested: one case each, and the IPO date is his guess ("maybe November 19th") |
| 9 | Apathetic tops make bear markets prone to fake-outs in both directions [W8] | NO | NO | Cannot be tested: no defined rule, a handful of cycles |
| 10 | Equities rolling over in Q4 of a midterm year goes with Bitcoin dropping [W9] | NO | NO | Not testable on the desk: it holds no equity data. Three midterm years in any case |
| 11 | Day count: day 389 from the peak now, the 2014-15 bottom came on day 406 [W9] | NO | NO | Cannot be tested: one comparable cycle |
| 12 | How to act: DCA, preserve capital, keep cash for year end [W4, W10] | n/a: advice for an investor, not a trade rule | NO | Out of scope for a trading system |

## 2. Straight answers

- **Does MTS already know this?** Not in code or docs. The band, the midterm structure and the other ideas appear only in the Cowen extracts and the CBP store. Nothing in `backtest/`, the layers or FORMULAS.md reads a weekly average.
- **Are we using it to find edge?** No. Benjamin is a thesis-only CBP analyst: 0 scored calls, below the 56-call floor, so no weight and no layer.
- **Does the desk find an edge in the parts that can be tested?** No. All 12 settings finish NOT ENOUGH DATA: 3 to 10 trades each, the desk needs 30. The two-year window cannot rule on a cycle-level view. The one pattern worth a second look is CATCHDOWN, which won 1 of 10 trades at a 3 % gap and 0 of 6 at 8 %, but that is small and unproven.
- **Why so few trades?** His ideas fire a few times per year, and the band needs 21 completed weeks, so the first signal is June 2022. Cycle claims with n = 3 never pass a 30-trade floor, whatever the market does.
- **How to apply exactly, today?** As a context flag only, never a trigger. His reading of the band: 72k to 76k (bWdXPK3Hlok 00:06:02); price 77.3k on 2026-10-31, just above the top. Eagle_Eyes and the CBP dashboard may show: BTC vs band top 76k, the 83k line he calls lost, and his two scenarios (bounce then final drop after the midterms, or an early low). Say it is his thesis, not a layer.
- **What would settle it?** A pre-registered daily-bar event study on BTC from 2017-08 to 2024-06 (public Binance daily bars, no 1m needed): about 25 BOUNCE and LOSE events, enough to test the band with a 95 % range. Card: `cowen-bmsb-daily-event-study`.
- **Daily event study result (2026-10-31, card cowen-bmsb-daily-event-study, `event_study/RESULT.md`):** BTC daily bars 2017-08..2024-06, fees in, single run. NOT ENOUGH DATA for all four ideas (n 19 to 22, floor 30). BOUNCE n 21, -0.20 R (-0.74 .. +0.37); LOSE n 22, +0.69 R (+0.07 .. +1.30, placebo difference +0.02 .. +1.50, gain mostly 2018-2019); FAKEOUT n 20, +0.33 R (-0.28 .. +0.93); CATCHDOWN n 19, -0.40 R (-0.87 .. +0.08). No edge proven; LOSE is a lead only. No rule or layer added.

## 3. The study on the desk

`studies/cowen_bmsb.py` plugs the four testable ideas into the simulator (settings: idea, CATCHDOWN gap, level exit, stop in ATR, target, hold days, fees, dates). The band uses completed weeks only: a trader sees the unfinished week, the desk must not.
SOURCED: the band definition and the idea shapes (extract W2, W6, W7). OURS: the daily bars, the next-day entry, the ATR stop, the exit level, the 3 % gap, ETH as the other coin, the hold limit. Tests: `test_cowen_bmsb.py` (8, red before the study existed; band numbers worked out by hand).

First grid, BTC unless stated, development window 2022-04-01 to 2024-06-30, fees in:

| # | Setting | n | Net R per trade | 95 % range | Wins | Verdict |
|---|---|---|---|---|---|---|
| 1 | Bounce, exit after 2 closes below the band, 2 R target | 4 | +0.82 | -0.57 .. +1.99 | 50 % | NOT ENOUGH DATA |
| 2 | Bounce, no exit | 3 | +1.99 | +1.98 .. +1.99 | 100 % | NOT ENOUGH DATA |
| 3 | Bounce, stop 4 ATR, 3 R target, 60 days | 4 | +0.61 | -0.28 .. +2.99 | 25 % | NOT ENOUGH DATA |
| 4 | Bounce, ETH | 7 | +0.14 | -0.85 .. +1.24 | 43 % | NOT ENOUGH DATA |
| 5 | Band lost, short, 2 R target | 7 | -0.23 | -0.86 .. +0.61 | 29 % | NOT ENOUGH DATA |
| 6 | Band lost, short, no exit, 10 days | 6 | +0.24 | -0.59 .. +1.14 | 67 % | NOT ENOUGH DATA |
| 7 | Fake-out below the 50-day, target the band | 9 | +0.14 | -0.27 .. +0.53 | 56 % | NOT ENOUGH DATA |
| 8 | Fake-out below the 50-day, 2 R target | 9 | +0.07 | -0.45 .. +0.69 | 44 % | NOT ENOUGH DATA |
| 9 | Fake-out, ETH, target the band | 10 | +0.07 | -0.36 .. +0.58 | 40 % | NOT ENOUGH DATA |
| 10 | Catch-down, ETH at its band, BTC 3 % above, target the band | 10 | -0.37 | -0.72 .. +0.05 | 10 % | NOT ENOUGH DATA |
| 11 | Catch-down, same, 2 R target | 10 | -0.27 | -0.72 .. +0.34 | 10 % | NOT ENOUGH DATA |
| 12 | Catch-down, BTC 8 % above, target the band | 6 | -0.33 | -0.48 .. -0.18 | 0 % | NOT ENOUGH DATA |

Row 2 is three wins out of three with the exit switched off: a spread of 3 trades, not a result. Every row is in the ledger (`layer_lab/TRIALS.md`) and on the hosted page.

## 4. Noticed

- A first run of this grid used a band exit that ended every short after two days (FAKEOUT and CATCHDOWN shorts start above the band, so "closes above the band" fired at once). The exit now uses each idea's own level; the 12 flawed runs were discarded before shipping.
- The desk window ends 2024-06-30, so it can never show how his current call (the band at 72k to 76k) plays out. Today's band cannot be computed from the desk's data.
