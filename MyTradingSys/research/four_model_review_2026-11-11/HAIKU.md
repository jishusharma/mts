# Four-model review, HAIKU reviewer, 2026-11-11

Read-only. Paths are relative to `BinanceDataFeed/MyTradingSys/` unless stated. Tags: SOURCED = read in a file (file:line); OURS = my arithmetic; NOT_IN_DATA = not found by grep. Other reviewers' files not read.
Path note: `tools/live_aid` is `MyTradingSys/tools/live_aid`, not `BinanceDataFeed/tools`.

## C1. What has been learned

### Lessons that still hold (7)
| # | Lesson | Number, n | Where |
|---|---|---|---|
| L1 | Intraday families are dead on cost | best gross 3.8 bp/trade vs 14 bp round trip (DEV) | PICTURE_AND_PLAN.md:19 |
| L2 | No fee-net PASS in the layer set | 0 of 40 fee-net rows carry a surviving PASS | research/STATUS.md:7 |
| L3 | Textbook candle shapes are a coin flip for the next candle | 1d, n 20-100 per shape | research/mts_bible/BIBLE.md:29 |
| L4 | The 80% value rule does not hold on BTC | 44% [40-49], n=493 | value_area_acceptance_2026-11-05/RESULT.md:13 |
| L5 | Taker delta separates how often a move is undone, not its side | undone 14-19% vs 26-30%; direction 42-49%; n=21,855 DEV hours | eagle_eyes_picture_2026-10-28/SCENARIO_LEDGER.md:25-29 |
| L6 | Stacking the six live readings adds nothing | 4+ agree: idea 51%, against 49% (n 144 / 288) | live_aid_review_2026-11-11/tables.md:22,25 |
| L7 | Where price goes first is learnable; the direction after is not | window low first 64% (n=137); 24h close up 52% | eagle_eyes_picture_2026-10-28/BACKTEST_CANDIDATES.md:23 |

### Ideas tested and refuted (top 3)
| # | Idea | Result, n | Where |
|---|---|---|---|
| R1 | Tom/Fabio 15m auction fade (node exit, break-even, session + HTF ladder) | net -0.106 R Deribit (t -1.4); -0.358 R taker (t -5.2); gross +0.064 R; n=1,484; kill line failed on all three tests | tom_fabio_course_correction_2026-11-07/CENSUS_5M15M_1109.md:3 |
| R2 | RSI divergence plus confirmation (C20), 15m | 36 variants, 0 positive out of sample (-0.06 to -0.17%/trade) | eagle_eyes_picture_2026-10-28/BACKTEST_CANDIDATES.md:27 |
| R3 | WaveTrend dot plus bullish divergence exit (C30) on its pre-registered window | H1 30m: n=35, mean -0.066%, FAIL; H2 15m with 2h trend up: n=22, +0.22%, CI -0.12..+0.56, Holm p 0.218, INCONCLUSIVE | eagle_eyes_picture_2026-10-28/C30_VALIDATION.md:7-8 |

Note: the C30 "LEAD" row (n=88, 80% win) is a 2022-2024-06 in-sample figure, superseded by the validation above (BACKTEST_CANDIDATES.md:39).

## C2. Which trades MTS should take now (ranked by evidence)

Operator asks, quoted from `system/OPERATOR_DECISIONS.md`:
- :1680 (d-context-retest-1104): "buy on retests after the dot combined with rsi confluence ... then sessions also matter" and "take those calls and start trading those on testnet".
- :1812-1816 (d-phase-first-method-1106): "A pattern visible in the current phase goes to the testnet at once and keeps trading until it stops working".
- :1725 (d-rsi-40-60-line-behaviour-1104): RSI 40/60 line behaviour across timeframes. Its RESULT.md exists but is outside my read list: NOT_READ.

| Rank | Trade type | Direction, session, trigger, confluence | Evidence (n) | Asked for? | Data supports? |
|---|---|---|---|---|---|
| 1 | Daily BB band-walk short in a 50-day downtrend | short; entry under prior close; stop prior high; target BB mid | fee-net +1.02 R, 73% reach mid, n=15; unfiltered -0.32 R, n=150 (eagle .../C31_HALVES.md Rule A table; BACKTEST_CANDIDATES.md:40). 14 of 15 trades in 2022-23 | Partly (operator teaching 11-03) | Lead only; UNDERPOWERED, parked (C31_HALVES.md:3) |
| 2 | WaveTrend dot buy + RSI confluence, 2h trend up | long; 30m or 15m chart; session tag required by operator | H1 FAIL n=35; H2 INCONCLUSIVE n=22 (C30_VALIDATION.md:7-8) | Yes (:1680) | NO: failed or unconfirmed |
| 3 | Weekly band-to-band long | long; any week above prior close; stop 3-week low; target BB mid | 79%, +1.15 R, n=24 in 3.5 years (BACKTEST_CANDIDATES.md:41, watch list) | Yes ("from one end to another", :1680) | Too few: NO EVIDENCE at n=24 |
| 4 | US-open sweep then retake | side not set; first hour sweep of 13:30-14:25 low | sweep first 63% vs high 16% (n=125); 15:30Z median -0.07%, up 45% (BACKTEST_CANDIDATES.md:46) | Not asked | Sweep yes, direction NO EVIDENCE |
| 5 | Live Aid level fade (rejected or failed break) | fade at a level, 1h horizon | last-week low 72% (n=18); yesterday low 40% (n=50); all level types 40-60% (tables.md:114,116) | Yes ("why no long from the lows", live_aid_review_2026-11-11/RESULT.md:3) | NO EVIDENCE (n too small or near 50%) |

Summary: nothing in the list passes a fee-net out-of-sample test. Rank 1 is the only positive number, and it is one regime with 15 trades.

## C3. ADX/DI and volume profile

### ADX/DI
| Question | Measured | Source |
|---|---|---|
| Whipsaw within 3 bars after a 2d DI cross | DEV 32.1% (n=56); VAL 46.7% (n=15); recent 50.0% (n=16) | research/adx_di_2026-11/CENSUS.md:31,55,79 |
| Lowest whipsaw bucket | DEV red, ADX 20-40, falling: 17.6% (n=17). Same bucket in VAL: 100% (n=4). Not stable | CENSUS.md:21,45 |
| CCU claim "1-3 weeks then a fall" | red crosses, low at 1-3 bars: 37.1% (n=35). Bins 4-7 and 8-12 do not give his 7-10 bar window: exact share NOT_IN_DATA | CENSUS.md:85-87 |
| ADX on the live page, 15m agrees vs against | idea 50% vs 46% (n 234 / 263); setup 52% vs 49% (n 515 / 227) | tables.md:35-36, 63-64 |
| Trend vs range for idea fades | ADX>=20 50% vs ADX<20 47% (n 334 / 172) | tables.md:78-79 |
| Platform check vs TradingView | header says VERIFIED-TV; body says PARTIAL, 7 of 9 cells; the two misses are the 11-06 bar. 2d bars not checked (paywall) | TV_CROSSCHECK.md:3 vs :31 |

Use: ADX is a regime label (context) at best. It is not a gate or trigger (no measured lift; <=4 points). The setup board counts it as a side vote (`tools/live_aid/setup_board.js:30`), which has no measurement behind it.
Unmeasured: ADX on 15m, 1h, 4h as used on the page (the census used 2d only, CENSUS.md:5); cascade table (c) on 1h and 4h (CENSUS.md:188, 1d vs 2d only); any pre-registered rule.

### Volume profile and value area
| Question | Measured | Source |
|---|---|---|
| 80% rule (re-entry reaches far edge) | 44% [40-49], n=493 | value_area_acceptance_2026-11-05/RESULT.md:9,13 |
| Acceptance below VAL extends half a width | 77%, n=300; no placebo yet | RESULT.md:10,15 |
| Back to POC after acceptance below VAL | 42%, n=300 | RESULT.md:11 |
| Live Aid idea by level state | ACCEPTED 43% (n=253); REJECTED 49% (n=290) | tables.md:14-16 |
| Auction census using volume nodes (15m) | no edge, net -0.106 R (R1 above) | CENSUS_5M15M_1109.md:3 |

Use: value area is context (where price sits relative to value). Not a gate or trigger until the 77% has a placebo. POC as a target: no measured hit rate (NOT_IN_DATA).
Unmeasured: placebo for the 77% (RESULT.md:15); POC hit rate; NY-session value area (NOT_IN_DATA: grep for NY / New York / session value in tools/live_aid, backtest/layers and research/tom_fabio_course_correction_2026-11-07 found no computation).

## D3. Haiku mechanical tasks

### (a) Wiring table
| Item | Computed in | On Live Aid page | Used by setup board | Test file | Written to a log |
|---|---|---|---|---|---|
| ADX/DI 14 Wilder (live) | `tools/live_aid/indread.js:21` adx(); `:84-85` cells.adx | yes: `tools/live_aid/home.js:174` indCard; row list `indread.js:13`; page loads it `live_aid.html:387`, `:1063` | yes: `home.js:317-325` boardInputs passes adx; `setup_board.js:30` adx_di | `tools/live_aid/test_indread.py:32-38` (hand values); `test_setup_board.py:40-43` | no (no storage key for ADX; only premarket and liq keys at `live_aid.html:419,810`) |
| ADX/DI Python (research) | `backtest/layers/adx/adx.py:7` adx_di(); `:44` crosses | no | no | `backtest/layers/adx/test_adx.py:15,33` | research output only (`research/adx_di_2026-11/CENSUS.md`) |
| Prior-day VA, 1m volume 70% (Live Aid panel) | `tools/live_aid/live_aid_indicators.js:793` valueArea(); `:810` vaPriorDay() | yes: panel `live_aid.html:262-265`; render `:903-914` | no: `home.js:317-327` never sets `va`; `setup_board.js:31` reads it; comment `home.js:314` says unwired | `tools/live_aid/test_live_aid.py:845,865` | no |
| Prior-day VA, time at price, 1h bars | `tools/live_aid/daily_playbook.py:135` value_area() | levels via `playbook_data.js` (generated) and label map `home.js:13`, `level_registry.js:11` | no | `tools/live_aid/test_daily_playbook.py:116` | writes `playbook_data.js` (`daily_playbook.py:40,408`), a data file, not a log |
| Prior-day VA, 50-dollar bins, 0.7 (TF strip) | `tools/live_aid/tf_strip.js:62` valueArea(); `:103-104` | TF rows built `live_aid.html:1606-1607` (display path not fully traced) | no | `tools/live_aid/test_spec_tf_strip.py:20` (contract, existence) | no |
| Prior-day VA, research (Python) | `research/value_area_acceptance_2026-11-05/accept80.py`; `research/tom_fabio_course_correction_2026-11-07/auction_context.py:212-220` | no | no | `tools/live_aid/test_live_aid.py:814-849` imports accept80 | no |
| NY-session value area | NOT_IN_DATA (grep, see C3) | NOT_IN_DATA | NOT_IN_DATA | NOT_IN_DATA | NOT_IN_DATA |

Two prior-day value-area definitions run side by side (1m volume in `live_aid_indicators.js:793`, time at price in `daily_playbook.py:135`). Their numbers are not compared on any page (NOT_IN_DATA).

### (b) Scenario ledger count (parsed with python -I, `research/eagle_eyes_picture_2026-10-28/scenario_ledger.csv`, 24 rows S001-S024)
| Measure | Count | Note |
|---|---|---|
| Total rows | 24 | CSV rows 2-25 |
| Directional calls (likely UP or DOWN) | 4 (DOWN 3, UP 1) | S001, S002, S005, S009 |
| Right (HIT) | 3 | S002, S005, S009 |
| Wrong (MISS) | 1 | S001 |
| NA (likely NONE, or BOTH/NEITHER) | 16 | |
| Unscored (score blank) | 4 | S008 (window to 11-16); S022, S023, S024 (window to 11-11 21:00Z, open at 15:33Z read) |

Hand table `SCENARIO_LEDGER.md` (10-29 to 10-30, 7 rows, lines 10-16): 3 counted, 2 right, 1 wrong (its own tally, line 17). Combined directional total: 7 scored, 5 right, 2 wrong. n=7 is too small for any hit-rate claim.

## NEXT: top 5 actions
1. Correct the TV cross-check verdict: make `TV_CROSSCHECK.md:3` agree with the body (PARTIAL, 7 of 9, line 31). Done when both lines say the same and the 11-06 bar is re-read after 00:00Z.
2. Remove `adx_di` from the setup-board side vote (`setup_board.js:30`) or pre-register its test on 15m and 1h. Done when the vote is off, or a pre-reg with a pass rule exists and its result is in RESULT.md.
3. Wire or drop the value_area layer: `home.js:317-327` never passes `va`, so `setup_board.js:31` never fires. Done when a page test shows value_area in board output, or it is removed from `setup_board.js:12`.
4. Pick one prior-day value-area definition for the page (`live_aid_indicators.js:793` vs `daily_playbook.py:135`) and test they agree on one fixture. Done when one test passes and the other is labelled as a different measure.
5. Run the placebo for the 77% acceptance claim (RESULT.md:15). Done when the placebo result is written into RESULT.md with its n.

Noticed: TV_CROSSCHECK header and body disagree (VERIFIED-TV vs PARTIAL); value_area layer never reaches the setup board; two value-area definitions on the same page.
