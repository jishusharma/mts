# Sonnet review, 2026-11-11 (read-only; no other reviewer's file opened)

Path keys (all under MyTradingSys/): BIBLE = research/mts_bible/BIBLE.md; EE = research/eagle_eyes_picture_2026-10-28/; TF = research/tom_fabio_course_correction_2026-11-07/; LA = research/live_aid_review_2026-11-11/; EH = research/edge_hunt_2026-11-09/EDGE_TABLE.md; VA = research/value_area_acceptance_2026-11-05/RESULT.md; ADX = research/adx_di_2026-11/; OD = system/OPERATOR_DECISIONS.md; ST = research/STATUS.md.
Tags: every number has file:line. NOT_IN_DATA = not found in the files read. No price forecasts.

## C1. What has been learned

### 7 lessons that still hold
| # | Lesson | Number, n | file:line |
|---|---|---|---|
| L1 | Cost wall: no intraday family clears fees. Best gross effect ever measured 3.8 bp vs a 14 bp round trip; 0 of 40 fee-net layer rows carry a PASS | 3.8 bp vs 14 bp; 0 of 40 | EE/PICTURE_AND_PLAN.md:19; ST:7 |
| L2 | Stop width decides fees: on 15m the median stop is 39.5 bps, so a taker round trip costs about 0.25 R; before fees the fade earns +0.064 R (SE 0.077), after Deribit-maker fees -0.106 R | n 1,484 | TF/CENSUS_5M15M_1109.md:21-25 |
| L3 | Levels say where price goes first, not which way it ends: held-retest highs/lows taken within 24 h 72% vs 57-61% control (n ~700 each); US-window rally gives back and takes the window low first 64% (n 137); pre-open spike round trip, low first 63% vs high first 16% (n 125) | see left | EE/BACKTEST_CANDIDATES.md:33, :23, :46 |
| L4 | Order flow with no location is continuation: b99 big-trade absorption reversed only 18% vs 27% baseline (n 2,175); fast approach into a 1h swing continued 56.3% (n 887) | n 2,175; 887 | TF/AUDIT_AND_COURSE_CORRECTION.md:39, :24 |
| L5 | Stacking readings adds nothing in Live Aid's own record: 4+ of 6 readings agree = 51% right after 1h (n 144 of 759 IDEA flags), against = 49%; 58% of flags are followed by an opposite flag within 30 min | n 759 (+1,262 setups) | LA/RESULT.md:21-23; LA/tables.md:24 |
| L6 | Bible structure (context, not trigger): five of six cycle turns are textbook double tops/bottoms; drops shrink (-85, -84, -78, -54 % so far); the next candle after a textbook shape is a coin flip (n 20-100 per shape) | 5 of 6; n 20-100 | BIBLE:13, :26, :29 |
| L7 | OI/CVD/squeeze readings give size, not side: pre-US 15m squeeze up 29 / down 29 / sideways 43% (n 192); after a flush the OI path says who is trapped, 4h up 53/56/55% vs base 52% (n 18/9/22); taker delta separates how often a move is undone (14-19% vs 26-30%), not direction (21,855 hourly events) | see left | EE/BACKTEST_CANDIDATES.md:24, :31; EE/SCENARIO_LEDGER.md:25-30 |
Bible caveat that still stands: the 200-week SMA sat within 1-11% of the low at 3 of 4 bottoms: n = 4, "anecdote" (BIBLE:61). The two-clock bottom question (July low vs due now) is open until 2026-11-16 (BIBLE:34-36, :72).

### 3 most important tested-and-refuted ideas
| # | Idea | Result | file:line |
|---|---|---|---|
| R1 | Tom/Fabio plain-auction fades (four hand-picked winning days; later the 15m session+ladder+node/BE rule). Fixed brackets, node exits, session, ladder, 5m, 15m, 1h: all negative | 15m H1 n 1,484 net -0.106 R (t -1.4), taker -0.358 (t -5.2); 5m n 1,579 -0.339; 1h gate-pass n 1,871 -0.087 (SE 0.022). The four-trade proof graded "WRONG as evidence" | TF/CENSUS_5M15M_1109.md:3, :54, :78; TF/AUCTION_CENSUS_1108.md:3; TF/POSTMORTEM_OPUS.md:23 |
| R2 | Dalton "80% rule" and "77% acceptance continuation" as a trade basis | 80% rule is 44% [40-49], n 493; the 77% is a half-VA-width touch, no placebo (n 300); census ACCEPTED at 1R = -0.096 R (n 2,798) | VA:9-17; TF/POSTMORTEM_OPUS.md:24-25 |
| R3 | Indicator triggers (RSI divergence + confirm, WaveTrend dots, RSI 40/60 + MTF confluence, first-touch sweep fades) | C20: 36 variants, 0 positive out-of-sample; C27 WT dots net -0.09 to -0.63%; edge hunt 15 trials: 0 pass, 8 FAIL, 5 INCONCLUSIVE (T04 n 1,150 -0.221 R; T11 n 1,588 -0.146 R) | EE/BACKTEST_CANDIDATES.md:27, :36; EH:3, :10, :16 |

## C2. Which trades should MTS take now (ranked by evidence, not by wish)
Nothing has a PASS (ST:7 "0 of 40"; EH:3 "No trial passed"). Ranking = least-bad evidence that can run on testnet under phase-first.
| Rank | Trade (direction, session/time, trigger) | Confluence (readings that must agree) | Evidence number, n | Asked by operator? |
|---|---|---|---|---|
| 1 | SHORT at a marked 4h level, any session: RSI divergence (3-10 bars, close to close) at the level | Malkan 5-layer stack (OURS): level + divergence + RSI 40/60 state + 4h/1d bias + band (stack listed in malkan_level_shorts READING) | full stack n 37 +0.13 R; best arm n 126 +0.10 R, ~0.9 SE; not a trial verdict, not screened (EH:28-30) | YES. OD:2093-2095 (operator asked how his five marked 4h shorts become tradable; all 5 reached >= 1R). Data: weak |
| 2 | LONG 4h, RSI14 crosses above its SMA14, BTC+ETH | RSI cross only (T06); add nothing until a dose-response shows it | n 1,322 +0.048 R (SE 0.040, CI -0.029..+0.126); long side +0.105 R, p 0.055, Holm 0.83 (EH:15, :30-31) | NO. Data-supported lead only (paper slot) |
| 3 | LONG at the cycle bottom, daily/weekly (cycle-bottom long, 2x leverage default) | cycle window (BIBLE:34-36) + 200-week SMA zone + weekly close holds above 60,000 (BIBLE:35, :64) | n = 4 cycles, no fee-net test; NO EVIDENCE as a trade rule (BIBLE:61 "anecdote") | YES in direction: OD:1807 "MTS aims at leveraged directional trades, not carry"; OD:1812-1816 phase-first; card cycle-bottom-long-testnet-trade-1106 (OPEN) |
| 4 | LONG/SHORT 4h Krown S8 (frozen R6 rule) | Krown S8 only | E2 INCONCLUSIVE (EE/PICTURE_AND_PLAN.md:18); related T15 4h RSI-40 long n 51 +0.016 R CI -0.467..+0.500 (EH:26) | YES. OD:2089-2092 "start it" (testnet forward until it fails) |
| 5 | LONG 15m WaveTrend buy dot with 2h trend up | WT dot + 2h trend up | C30 H2 validation n 22, +0.220% fee-net, CI -0.120..+0.560, Holm p 0.218: INCONCLUSIVE; random entries beaten 30/30 (EE/C30_VALIDATION.md:11-14) | NO (operator asked WT in the dashboard, OD:2183-2186; not a trade) |
Not ranked, data says NO: range-edge fades in the current 75.4-80.9k range (the operator's claim, TF/POSTMORTEM_OPUS.md:53): T14 1h level fade, balance phase, n 358, -0.232 R, FAIL (EH:20); T04 first-touch sweep fade n 1,150 -0.221 R (EH:10); Live Aid IDEA flags 47% right, n 759 (LA/RESULT.md:17). Tom swing (trend + trendline pullback, wide stops): NO EVIDENCE, never tested (OD:2143, card tom-swing-trendline-extract-1109).
Operator-wanted vs data-supported: he wants #1, #3, #4 and level-touch ideas flashed (OD:2180, :2188-2192); the data supports none to PASS and mildly leans to #1 and #2 only.
Cost note: wide structural stops are the one lever that survives fees (0.15 R at 64 bps, TF/AUDIT:11), but the same rule on 7 years loses (R1). Testnet-forward is the only test left that costs nothing.

## C3. ADX/DI and volume profile (value area, POC)
### ADX/DI
| Question | Measured | file:line |
|---|---|---|
| Is the formula right? | VERIFIED-TV: 2 historical daily bars match to 0.01 on all 6 values; last bar off 0.80/0.69 (partial-row artefact). 2d buckets unverified (TV paywall) | ADX/TV_CROSSCHECK.md:3, :7, :31 |
| Do 2d DI crosses call anything? | Whipsaw within 3 bars: DEV 32.1% (56 crosses), VALIDATION 46.7% (15), recent 50.0% (17). Lowest whipsaw cell DEV red, ADX 20-40, falling: 17.6% (n 17) but VALIDATION same cell 100% (n 4) | ADX/CENSUS.md:31, :55, :79, :21, :46 |
| CCU claim "consolidate 1-3 weeks, then fall straight down"? | Not supported: after 35 red crosses the low comes within 1-3 bars in 37.1% (median -3.6%), 21-30 bars in 20% | ADX/CENSUS.md:83-89 |
| Does it add to Live Aid ideas? | Barely: ADX 15m agrees 50% (n 234) vs against 46% (n 263); 1h 49% (n 296) vs 45% (n 264); in-sample, no fees | LA/tables.md:36-38 |
| In the 6-reading stack | no lift (51% with 4+ agreeing) | LA/RESULT.md:21-23 |
Use: CONTEXT label only (trend strength / regime), never a trigger or gate until a fee-net test. Depth numbers in the census are the extreme within 30 bars, biased up by construction (ADX/SPEC.md:17). Unmeasured: 1h/4h crosses (no kline file, ADX/CENSUS.md:5), ADX as a gate on any rank 1-5 trade, 2d buckets vs TradingView, fee-net return of any DI cross.

### Volume profile (value area, POC)
| Question | Measured | file:line |
|---|---|---|
| Does price return to value? | Outside VA then 2x30m back inside, reaches far edge same day 44% [40-49], n 493 (not 80%); accepted below VAL then to POC 42% (n 300) | VA:9-11 |
| Acceptance continuation | 77% = half-VA-width, plain volatility; census ACCEPTED -0.096 R n 2,798 | VA:10, :15-17 |
| Resting limits at prior D/W/M POC/VAH/VAL | 0 of 48 streams pass, mean net -0.08 to -0.22 R; tom_vp 0 of 20 cells | TF/AUDIT_AND_COURSE_CORRECTION.md:34-35 |
| Return to POC after break of rolling-24h VA | 57.2% vs 55.8% placebo (p 0.28) | TF/AUDIT_AND_COURSE_CORRECTION.md:36 |
| Live today | only yesterday's value levels as lines; no live today-VA/POC; value-area 80% rule and acceptance live on other tabs, Home does not use them | LA/RESULT.md:44-48 |
Use: LEVEL LIST only (where to look: PDH/PDL, prior VAH/VAL/POC), as context with its base rate shown; drop it as a trigger. Unmeasured: NY-session profile (cards tf-ny-session-va-profile-1109, POSTMORTEM_OPUS.md:55 and :117), developing-day VA/POC, weekly 70% VA (Tom), POC as a magnet against a placebo, LVN traverse, VA edges inside a phase, any VA event with delta (the census klines carry none, POSTMORTEM_OPUS.md:22).

## NEXT: top 5 actions (ordered)
1. Ship live-aid-flag-log-1111 (prio 1 already, OD:2282); done when every flashed IDEA/SETUP is a row (time, level, readings, 1h outcome) and the daily review can reproduce LA/tables.md without replay.js.
2. Start the three testnet-forward slots that already have a frozen rule (Malkan level short, T06 RSI cross, Krown S8 4h) with the logged fields in POSTMORTEM_OPUS.md:71 and the kill rule (30 trades, net R <= 0 vs -0.087 null); done when each has one logged testnet order or a written reason.
3. Build the NY-session value area + delta-at-level log (tf-ny-session-va-profile-1109, tf-delta-at-level-testnet-log-1109); done when one week of events carries session, level type, delta, with/against 1M bias.
4. Record what is unrecorded: heatmap bands/forceOrder history and net longs/shorts (BACKTEST_CANDIDATES.md:12, :13, :29 NOT_IN_DATA); done when a named host stores 30 days and BANDS_LEDGER.csv (13 rows, last 11-01) scores bands against price.
5. Add a placebo for the 77% acceptance claim and value-area-rates-into-base-rates-1111; done when Home shows VA/POC state with its n and placebo, or the claim is deleted.

# D2 (Sonnet only): Eagle Eyes said vs done
Status key: DONE = sha or result file; OPEN = card id in system/tasks/; LOST = no result, no live card. Sources: A = PICTURE_AND_PLAN s5/s6/s8, B = OPERATOR_POINTERS s1/s3, C = BACKTEST_CANDIDATES, D = LIVE_AID_REQUIREMENTS. Method: `git log --oneline -i --grep` over 6,000 commits, scan of 205 open + archived cards. Quality limit: matching is by name/keywords; a LOST can hide under another name.
| ID | Recommendation | Status | Evidence |
|---|---|---|---|
| A1 | Carry sealed read, go private on carry; carry mainnet path (ranks 1, 6) | DONE (by decision) | OD:1806-1810 carry dropped 11-06; sealed window never read |
| A2 | Fix F-GAP-1 (stop missing after restart) | DONE | d7f1c493f, 0f1f46644 |
| A3 | Read laptop live state as counts (rank 3) | DONE (tool only) | live_mirror.py brief (CLAUDE.md); the 7-day count table NOT_IN_DATA |
| A4 | Alert Dock, one window, 3-card cap, snooze (rank 4, s6) | LOST | spec only 3399af49d; successor card alerts-v2-on-both-screens-one-alert-feed dropped by D7 S0 10-30 ("revive by a new card") |
| A5 | E1 counts-only power screen, 4h-and-up families (rank 5) | DONE (part) | EH:15,26; malkan_level_shorts_2026-11-09/REPORT.md; OPEN krown-dev-event-study |
| A6 | Operator trade journal with layer state, kept private (rank 7, G3) | LOST | execution/journal holds auto plans only; cotrade b6f7515ca journals testnet orders |
| A7 | Align live exits with backtested bracket (rank 8, G8) | LOST | gap-g8-deribit-parity is venue basis, not exits |
| A8 | Record flow series on a named host (rank 9, G4) | DONE (part) + OPEN | orderflow_live 282d95e35; metrics card done; OPEN live-aid-oi-poller-all-venues-1110 |
| A9 | Heatmap / forceOrder history | LOST | BACKTEST_CANDIDATES.md:12 NOT_IN_DATA; BANDS_LEDGER.csv 13 hand rows |
| A10 | Choose 2-3 Tom setups to alert first (s8) | OPEN | setup-review-with-operator |
| B1 | Divergence on every TF + roll-over | DONE | b58d13a0a; C20, C23 |
| B2 | Verify price-vs-CVD claim | DONE | 98223ee41 (U7: price drift 63% vs CVD 59%) |
| B3 | Explain CVD vs net delta per candle | DONE | EE/FLOW_STATE_PAIRS_1M.md |
| B4 | Classify OI squeeze/cover/new, odds per TF | DONE | C24 oi_after_flush (BACKTEST_CANDIDATES.md:31) |
| B5 | Top-trader long/short by phase | DONE | b2010203f; metrics-oi-toptrader card |
| B6 | Net longs/shorts (new/open) by phase | LOST | history NOT_IN_DATA (BACKTEST_CANDIDATES.md:13, :29); no card |
| B7 | Liquidation heatmap trust ledger (R08/R09) | LOST | design 8804c7ff6, card closed 10-28, 13 rows, no score |
| B8 | BB dance defined and tested | DONE | 48e51ff6e (n 11,051); BB-mid rule OPEN bb-mid-reject-candle-rule-test |
| B9 | RSI layer on Malkan's rules only | DONE | ST:24; malkan_rsi_2026-10-31/MALKAN_RULES |
| B10 | VWAP research | OPEN | vwap-as-a-level-research-tom-fabio-analysts-web; vwap-below-flush-causal-test |
| B11 | Levels with confluence, level patterns | DONE | C15 level_approach (10,822 events) |
| B12 | Footprint per-bar delta cross-check | OPEN | lab-verify-footprint-vs-indicator-delta (report 5425345a2) |
| B13 | WaveTrend module on dashboard | DONE | cdd5dd2dc |
| B14 | One bias per TF, agreement | DONE | b58d13a0a; ST:44 mtf lead-lag |
| B15 | Context per day/session | DONE | eh-o2-phase-lens (n 358 FAIL) |
| B16 | Pitchfork / ABCD structure layer | OPEN | pitchfork-live-4h-bars-too-few; pitchfork-engine-implement-hagopian-fail |
| B17 | Take-profit support, in-trade one screen (R01-R06) | DONE | levelstory.js (OD:2188-2192); Live Aid Home |
| B18 | Watch top-trader at 1, 3, 5 min | LOST | Binance keeps 30 days; no card names it |
| C1 | Lower low at BB, layers agree, split by agreement | LOST | closest LA/tables.md:24, different trigger |
| C2 | Burst bar near band, three OI/delta cases | DONE | FLOW_STATE_PAIRS_1M.md (n 160/128/177) |
| C3 | Ride upper-mid band N bars | LOST | no result |
| C4-C5 | WT lower highs; WT <= -55 cross up | DONE | C28-C30; wt30_sequence n 304 |
| C6 | Heatmap spike rejection | LOST | needs recorder (= A9) |
| C7 | Top-trader ratio steps lead/lag | LOST | data in metrics archive now, no study |
| C8, C10 | Double high / double low on 15m (WT, RSI) | LOST | pattern_book is daily only |
| C9 | 15m WT <= -60 | DONE (part) | wt_15m_30m_1110 (OD:2185-2186) |
| C11 | 1m RSI <= 15 + CVD burst | LOST | no result |
| C12 | Daily up candle, perp vs spot delta | LOST | green_neg_delta.py is intraday, other question |
| C13 | Daily WT bear cross analogs | DONE | daily_wt_rsi_analogs.py (n 17) |
| C14 | First pullback after OI breakout | LOST | break_retest.py is a 1m range-low study |
| C15-C18 | Level approach; US rally fade; pre-US squeeze; BB pierce | DONE | result files cited in BACKTEST_CANDIDATES.md:22-25 |
| C19 | Top-trader accounts vs positions split | LOST | status raw, no card |
| C20-C21, C23-C26 | Div switch; lower-pierce; daily div/mid; Stoch; retest | DONE | rows 27, 28, 30-33 |
| C22 | Volume/positioning around a lower-band drop | LOST | status idea, no card |
| C26b | Six-state price x OI tile measured | DONE | anticipation_map_2026-11-05 (21,855 events, EE/SCENARIO_LEDGER.md:23-30) |
| C27a | SQUEEZE mirror of C24 | LOST | no card (event-sweep-squeeze-sequence-study-1111 is event days, OPEN) |
| C27b-C30 | WT dots, context, lower TF, +div; validation | DONE | C30_VALIDATION.md H2 INCONCLUSIVE n 22 |
| C31-C34 | Daily BB-edge short; weekly; day-shape; spot cost re-score | DONE | 07e1e7a17, 666b1dbff, 2fb21b89c |
| C35 | First daily WT cross from below -53 entry study | LOST | "no card yet", none found |
| C36 | 1m WT+RSI turn on 5m/15m + live flag | LOST | no result |
| C37 | US-open round trip conditioned on OI + mirror | LOST | no result |
| C38 | ETHBTC rule rerun on BTC 4h, then 1D | LOST | no result |
| D1 | Per-TF indicator state rows | DONE | cdd5dd2dc, b58d13a0a |
| D2 | Base rate for THIS state with n | OPEN | live-aid-board-rates-1111; value-area-rates-into-base-rates-1111 |
| D3 | Levels in play + hit probability | DONE | levelstory.js (OD:2188) |
| D4 | Clock, minutes to US open | DONE | f20eeed04 |
| D5 | Record of what Live Aid flashed (asked 11-11) | OPEN | live-aid-flag-log-1111 (LA/RESULT.md:47) |
Counts (57 table rows; grouped rows count once): DONE 29, OPEN 6, LOST 22. Rows marked "DONE (part)" (A3, A5, A8, C9) are counted DONE; A1 is DONE by decision, not by work.

## The 5 LOST items that matter most
1. A6 operator trade journal (private): the only way to turn his discretionary method into a testable rule; nobody owns it.
2. A9 + B7 + B6 + B18 flow/heatmap/net-position recorders: five asks rest on data that is not stored (30-day Binance limit); 13 hand rows is the whole heatmap record.
3. A7 live exits vs backtested bracket: any future testnet verdict is meaningless if live exits differ (97% time exits, PICTURE_AND_PLAN.md:66).
4. C35 + C37 + C38 follow-ups: the three "Next:" lines from 11-03 that were never carded (daily WT entry study, US-open OI condition, BTC 4h rerun).
5. A4 Alert Dock: the operator's first direct ask (alerts not visible) was dropped by the roadmap cut; Live Aid level-touch alerts (22d131daf) cover only levels.
