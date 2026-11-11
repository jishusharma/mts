# Four-model review, Supervisor's own copy (Fable, login C), 2026-11-11

Operator order 2026-11-11 ~15:30Z: review the Bible, what Eagle Eyes learned as observer, the latest understanding of
which trades to take, and the new ADX/DI and volume-profile readings; four models answer the same three tasks, then compare.
Written before reading the other three files. Descriptive; no edge claim; no forecast. Paths are under `MyTradingSys/`.

## C1. What has been learned

Holds (7):
| # | Lesson | Number | Source |
|---|---|---|---|
| 1 | BTC runs a four-year cycle with shrinking drops; bottoms print 363-406 days after the peak | drops -85, -84, -78, -54 %; n = 4 cycles | research/mts_bible/BIBLE.md:8-13 |
| 2 | Tops and bottoms are double shapes; 2026 low has the 2022 shape (second low lower) | 5 of 6 turns found by the detector | BIBLE.md:18-26 |
| 3 | Two clocks disagree (depth says July was the low, cycle says a low is due by 11-16); breaks on a weekly close under 60,000 | S008 scores 2026-11-16 | BIBLE.md:32-36, 51 |
| 4 | The 200-week average is a floor zone, not a floor | within 1-11 % of the low at 3 of 4 bottoms | BIBLE.md:61 |
| 5 | Intraday setups die on cost when the stop is tight: fee is 1.2-2.8 R on 5-8 bp stops | net -2.912 R (n 2,880); gross +0.08..+0.16 R turned to -1.42 R | research/tom_fabio_course_correction_2026-11-07/AUDIT_AND_COURSE_CORRECTION.md:14, 32, 37 |
| 6 | A level is where to look, never an order: touching a level is a coin flip; order flow away from a major level is continuation | 0 of 48 streams; aggressor continues 55-65 % (n 2,175 / 887) | AUDIT_AND_COURSE_CORRECTION.md:17, 24, 35 |
| 7 | Acceptance beyond value tends to extend the same day; the "80 % rule" is 44 % on BTC | 77 % half-width drift (n 300, no placebo); 44 % (n 493) | research/value_area_acceptance_2026-11-05/RESULT.md:9-15 |

Also from Eagle Eyes (not a number, a method): the operator reads a stack, not one indicator (multi-timeframe sets 60 shots,
RSI 57, BB 41, levels/VP 28); "the behavior must be consistent for the context"
(research/eagle_eyes_picture_2026-10-28/OPERATOR_POINTERS.md:42, 47). Eagle's own A/B maps were right 2 of 3
(SCENARIO_LEDGER.md, "Running count"): too few to mean anything.

Refuted (3):
| # | Idea | Number | Source |
|---|---|---|---|
| 1 | Fade a fast rejection at a value-area / prior-day level, even with session + higher-timeframe gates and node exits | -0.106 R (n 1,484, t -1.4), taker -0.358 R; gross +0.064 R | tom_fabio_course_correction_2026-11-07/CENSUS_5M15M_1109.md:3, 17-24 |
| 2 | Stacking readings (confluence count) makes a flag more right | 51 % with 4+ of 6 agreeing vs 49 % against; score slope CI -0.91..+2.99 (n 13,851) | research/live_aid_review_2026-11-11/RESULT.md:22-23; research/edge_hunt_2026-11-09/EDGE_TABLE.md:19 |
| 3 | First-touch sweep-reclaim, level fades, wick entries, RSI 40/60 bounce | T04 -0.221 R (n 1,150); T09 -0.581; T10 -0.804; T11 -0.146 (n 1,588); 0 of 15 trials passed | EDGE_TABLE.md:3, 12-18 |

## C2. Which trades to take now

What he asked for: leveraged directional trades, not carry (system/OPERATOR_DECISIONS.md:1807); patterns valid in the current
phase go to testnet and run until they fail (OPERATOR_DECISIONS.md:1812-1816); a short flashed at the day's high when the bias
is down (OPERATOR_DECISIONS.md:2175 item 3); wait for the close when many analyst calls sit at a level (2188 block).

| Rank | Trade | Trigger and readings that must agree | Evidence | Verdict |
|---|---|---|---|---|
| 1 | Krown S8 4h (frozen rule) | already frozen in FORWARD_PREREG.md | backtest INCONCLUSIVE; forward slot started 11-09 (OPERATOR_DECISIONS.md:2091) | run on testnet, read weekly; the readout has no E+/E- column yet (system/PLAN_24H_2026-11-10.md:17) |
| 2 | RSI14 cross of its average, 4h, long side | 4h close cross; long only | +0.105 R long side, p 0.055; both sides +0.048 R, n 1,322, CI includes 0 | paper slot, not built (EDGE_TABLE.md:30-31; PLAN_24H_2026-11-10.md:56) |
| 3 | Malkan level short, 4h (divergence 3-10 bars at a level) | level + RSI divergence on closes | +0.10 R, n 126, 0.9 SE; 5-layer stack +0.13 R, n 37 | paper slot, not deployed (EDGE_TABLE.md:26-28) |
| 4 | Acceptance continuation: 2 x 30m closes below yesterday's value low, with the weekly/monthly candle red | acceptance + higher-timeframe bias + stop of 40 bp or more | drift 77 % (n 300) but as a 1R trade -0.096 R (n 2,798) | NOT a trade yet; needs the placebo and a wider-target test (value_area_acceptance RESULT.md:15) |
| 5 | Cycle-bottom long (the Bible trade) | weekly close holds 60,000 and the 200-week average; window passes 11-16 | n = 4 cycles, anecdote | position idea for the operator, not a system trade; S008 decides on 11-16 |

Fades at levels (the thing Live Aid flashes 71 times a day) have NO supporting evidence and five failed tests.

## C3. ADX/DI and volume profile

| Reading | Measured | Use | Unmeasured |
|---|---|---|---|
| ADX/DI 2-day cross | formula matches TradingView to 0.01 on 2 of 3 bars (research/adx_di_2026-11/TV_CROSSCHECK.md:3). 88 crosses since 2020; whipsaw within 3 bars 32 % DEV, 47 % VAL, 50 % recent; the "consolidate 1-3 weeks then fall" claim: the low sits in bars 1-3 in 37 % of red crosses (n 35) (CENSUS.md:31, 55, 79, 83-89) | context only, on the daily/2-day chart. The cleanest cell (red cross, ADX under 20: 0 of 3 whipsaw in VAL) is n = 3 | 1h and 4h crosses (no data on the machine, CENSUS.md:5); ADX as a trend/range switch for which setup to allow |
| ADX/DI 15m and 1h on Live Aid | agreeing with a flag: 50 % / 49 % right; against: 46 % / 45 % (n 234-296) (live_aid_review tables.md:35-38) | display only; it does not improve a flag | whether ADX level (not direction) separates range days from trend days |
| Prior-day value area | 80 % rule = 44 % (n 493); acceptance drift 77 % (n 300, no placebo); as an entry it loses (CENSUS_5M15M_1109.md) | location and state (inside / accepted outside), never a trigger | placebo for the 77 %; today's developing value area and POC are not on the page (live_aid_review RESULT.md:48); NY-session profile shipped 11-09, unscored |
| Volume profile nodes as targets | node + break-even exit: -0.106 R, 656 of 1,063 stops at break-even (CENSUS_5M15M_1109.md) | not as an exit rule | whether low-volume gaps speed the move (no test) |

## NEXT: top 5 actions
1. Live Aid writes every flag it shows to a log (card live-aid-flag-log-1111). Done when a day of flags is on disk with the readings at that moment.
2. Run the three forward slots properly: Krown S8 readout gets E+/E- columns; Malkan level short and the 4h RSI cross get their paper loggers. Done when one weekly table lists all three with trade counts.
3. Stop flashing level fades as IDEA / SETUP; show level state plus one bias line. Done when Home shows at most one direction and the 58 % flip-within-30-min rate is re-measured from the log.
4. Run the two missing measurements before any confluence rule: placebo for the 77 % acceptance drift; ADX on 1h/4h as a range-vs-trend switch (does it change which side of acceptance works). Done when both have a RESULT with n and a placebo row.
5. Score S008 on 2026-11-16 and append the reading to the Bible. Done when BIBLE.md has a dated section 7.

Own view on the question behind the ask: the evidence says confluence by counting does not work here. What has not been tested
is confluence as a sequence (higher-timeframe bias, then acceptance or rejection at a named level, then timing), scored on trades
with stops of 40 bp or more. That needs the flag log first.
