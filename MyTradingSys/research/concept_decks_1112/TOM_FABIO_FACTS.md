# Tom/Fabio layer: fact sheet for the slide deck (2026-11-12, read-only)

Conventions
- Paths are relative to the repo root (worktree .claude/worktrees/xenodochial-murdock-64dbb7). R = MyTradingSys/research. L = MyTradingSys/backtest/layers.
- SOURCED = the trader's own words or number, with file. OURS = our parameter, our choice or our measured result. NOT_SEEN = looked for, not found.
- No account, order or position data appears here. All results are on public market data.
- Quote timestamps: Tom caption files carry NO clock times (one long line, line 19; position = BEGIN/MIDDLE/END third). Fabio files built from .vtt or ASR carry [m:ss]. "Extract file" says which verified extract holds the quote.
- Quote verification: quotes below are copied from CONCEPTS.md (machine-checked against transcripts, exit 0 per its header), TOM_VERBATIM_INDEX.md, SETUP_CATALOG.md and orderflow_extracts_1112 (gate: scripts/dev/verify_extract_quotes.py). I did not re-run the checker. Ledger status per video: R/extraction_ledger_2026-10/EXTRACTION_LEDGER.csv (PASS/FAIL noted where it matters).
- Who: Tom = Tom Vorwald (DAX/index futures, Volume Profile + footprint, German channel + EN channel). Fabio = Fabio Valentini (NQ/ES, NY session, order flow). Speaker of video 9IliXww64uM is contested (SETUP_CATALOG.md:1247 says Fabio; R/fabio_cvd_2026-10-30/CVD_CONCEPTS.md:37-40 says Andrea Cimi).

---------------------------------------------------------------------------------------------------------------------------------------

## 0. ONE-PARAGRAPH STATE OF PLAY (for the title/summary slide)

- 12 iterations of Tom/Fabio encodings (Java + Python) tested Sep-Nov 2026: 0 fee-net edge anywhere (R/tom_fabio_course_correction_2026-11-07/AUDIT_AND_COURSE_CORRECTION.md Executive Summary).
- Two independent reviews of the Nov-7 "course correction" (Fable, Opus post-mortem, 2026-11-09) agree: arithmetic right, method not what the traders do (R/tom_fabio_course_correction_2026-11-07/REVIEW_FABLE.md, POSTMORTEM_OPUS.md).
- Final pre-registered test of the last untested exit (15m, London/NY, HTF ladder, node-to-node exit + break-even): n = 1,484, net -0.106 R (Deribit maker fees), -0.358 R (all taker); gross +0.064 R, SE 0.077 (R/tom_fabio_course_correction_2026-11-07/CENSUS_5M15M_1109.md).
- Operator decision 2026-11-12: take ONLY the order-flow idea from Tom/Fabio, read BTC on its own clocks (MyTradingSys/system/OPERATOR_DECISIONS.md:2331-2335). The BTC-native order-flow families tested after that also all FAIL (section E rows E30-E35).
- What is still untested (cannot say "no edge" about it): footprint-level absorption at real per-price data, the NY-session value area on BTC, Tom's swing method (pre-reg only), adds/trail management, live forward results.

---------------------------------------------------------------------------------------------------------------------------------------

## A. CONCEPTS (8)

### A1. Context first: trend vs balance decides the setup family  (TOM)
- Teaches: before any trade, read whether the market is in trend or balance; different setups for each; ~70% of the time it is balance (his statistic, unverified). Higher-timeframe profiles give money-flow direction; "idea, then proof, then clean risk math".
- Quote (SOURCED): "Whether it's trend or balance because I have to use different setups there and that is absolutely crucial." Video Ld1dhjGdTCA (Tom, 13-point daily planning lecture), position MIDDLE, line 19, TOM-065. Extract file: extracts/v2/tom/Ld1dhjGdTCA_v2.md. CAUTION: ledger marks that v2 extract quotes_verified = FAIL; the line itself is machine-checked in R/tom_fabio_concepts_2026-10-29/CONCEPTS.md:32.
- Second quote: "First, you have an idea. Second, you have proof that it's really time now to implement the idea. And third, you have a really clean risk management so that the math is on your side." zQTbdEweG3c (Tom), line 19, TOM-068 (R/tom_fabio_concepts_2026-10-29/CONCEPTS.md:29; ledger PASS via tom_correlation_trick_2026-10-26/EXTRACT.md).
- Sketch: three stacked panels: a flat box labelled BALANCE (counter-trade at edges), a staircase labelled TREND (pullback continuation), a boxed "SORTING OUT after big move = WAIT" between them; arrow "pick setup family" to a trade-plan card.

### A2. The map: value area, POC, "return to value" (70/30)  (TOM; Fabio uses the same levels)
- Teaches: volume profile of the prior session; 70% of volume = value area; price leaves value and usually (his claim ~70%) returns to the POC; the edges and POC are where reactions happen; empty areas get filled.
- Quote (SOURCED): "where high volume occurs, we often see a reaction when a market returns there." NkQeOVDTAec (Tom), line 19, TOM-182 (R/tom_fabio_concepts_2026-10-29/CONCEPTS.md:40). Video title not recorded in any extract.
- 70/30 claim (SOURCED): "only the case about 30% of the time and the other 70% he will try and strive to run back here" (extracts/processed/tom/extract_BB3c8visnkI.md:38, quoted in R/tom_fabio_review_2026-10-31/SETUP_REVIEW.md section 2.2). Note: R/analyst_video_status_1112/STATUS.md lists BB3c8visnkI among "Tom extracts with no transcript on disk"; re-verification pending.
- Sketch: prior-day profile histogram on the left (POC bar, VAH/VAL lines), today's candles on the right poking above VAH then arrow back to POC; label "his claim 70%; BTC measured 57-63% with a placebo of 47-59%" (see E6, E7).

### A3. Acceptance vs rejection (failed auction / fast rejection)  (TOM + FABIO)
- Teaches: a probe beyond a level means nothing until you see what price does: fast rejection back inside (speed matters) = failed auction, trade back toward value; real acceptance (time/closes beyond) = new fair price, go with it. Not "quick spikes" but "real acceptance".
- Tom quote (SOURCED): "The market showed me that there is rejection up here. And the market also showed me that the speed with which it rejected this is promising for me." k0zm5NYn0IQ (Tom, DAX spike-fade session), MIDDLE, line 19, TOM-010. Extract file: extracts/v2/tom/CATALOG_DELTA_v1batch1.md (ledger PASS, 8 quotes).
- Tom quote 2 (SOURCED): "Not with quick spikes but with real acceptance." qLnQan0KGmQ, line 19, TOM-019 (CONCEPTS.md:51; ledger PASS).
- Fabio quote (SOURCED): "you have a negative delta with a positive price action. That's a very clear divergence in market pressure. There was an effort from seller that is not having any follow through. And the 5-minute was about to close right over here and that was my signal for the entry." 9IliXww64uM, raw lines 239-246, [8:28] (R/setup_catalog_2026-10-15/SETUP_CATALOG.md:1260; speaker contested, see header).
- Sketch: two candle strips. Left "FAST REJECTION": wick above a horizontal line, close back below within 1-3 bars, green tick. Right "ACCEPTANCE": 2+ closes above the line, retest holds, arrow continues. Caption "same level, two outcomes; the proof decides".

### A4. Absorption and effort vs result (order flow)  (FABIO; Tom calls it "proof")
- Teaches: big aggressive volume/delta with little price result = a large passive side absorbing ("punch to the wall"); hidden pressure = CVD runs while price is flat in balance; absorption at a level, then aggression that is rewarded, then absorbed again = the setup that made him the most money.
- Tom quote (SOURCED): "It means that there is a very large buyer here who is absorbing everything that's being sold." y67l86cSqb8 ("The BEST Trading Indicator? World Champions reveal the secret CVD Strategy", Trade the Traders channel, speaker unnamed), MIDDLE, TOM-025. Extract file: R/orderflow_extracts_1112/extract_y67l86cSqb8.md (R3 requires a technical level: "Because if I also have a strong technical level here, then I know there was an exhaustion here, which means an extremum.", MIDDLE).
- Fabio quote (SOURCED): "the result of the price for a pressure in by delta was almost zero. So this is a confirmation that the buyers are punching a wall and I want to be short in this position." 0jM5Y31YJak ("Top 3 trades from the competition"), body line 4 (CONCEPTS.md:124; ledger PASS via setup_catalog_2026-10-15/EXTRACTION_CRITICAL_GAPS_2026-10-18.md).
- Fabio quote 2 (SOURCED, ASR): "the trade that in 2025 gave me the most amount of money is the test of this level with" Is1HvdfQm5c, [20:10] (SETUP_CATALOG.md:1238; ledger PASS 225 quotes) followed at line 140-142 by "absorption at the top ... aggression that is rewarded ... buyers again absorbed".
- Sketch: a candle with a huge green delta bar under it but a tiny body at a level (bubble chart), label EFFORT with big arrow, RESULT with tiny arrow; second panel: CVD line making a lower low while price is flat = "absorption".

### A5. Low-volume zones (LVN) and node-to-node targets  (FABIO for LVN; TOM for node targets)
- Teaches: price crosses a low-volume node fast and market comes back to rebalance it before continuing; LVN is a ceiling/floor inside a trend, not a fade level. Tom: after acceptance, target = the next high-volume price; set TP a few points short of the obvious level.
- Fabio quote (SOURCED): "Usually, the market like to rebalance the low volume node before continuing in the direction of the trend." Pz8f0wWW12M ("The Only Orderflow Guide You'll Ever Need"), lines 518-520 (CONCEPTS.md:110; ledger PASS 6 quotes via EXTRACTION_CRITICAL_GAPS).
- Tom quote (SOURCED): "if it accepts new prices, then it looks for the next high volume price and that is your target." qLnQan0KGmQ, END, TOM-018 (ledger PASS).
- Tom quote 2 (SOURCED): "I would rather set my take profit a few points away from this range because often it is exactly the case that such levels that everyone sees ... are not hit at first." l8RZrBfzvp4 line 13, TOM-262.
- Sketch: profile with two fat HVN humps and a thin waist (LVN). Price arrow jumps through the waist, a dotted retrace back into the waist ("rebalance"), then continues to the second hump labelled TARGET (stop a few points short).

### A6. Trade build: tiny structural stop, big reward, fast break-even, adds from profit  (BOTH)
- Teaches: stop at the invalidation (beyond last liquidity/swing for Tom; "super small" above the absorbed area for Fabio); win rate only 30-40% paid by R of 3 to 4.5+; break-even immediately when the other side fails; trail aggressively; add in profit only.
- Tom quote (SOURCED): "my stop loss belongs below the last liquidity." 3o1VVsfBmmU (Tom lecture, matrix), MIDDLE, TOM-072 (ledger PASS 39 quotes; extracts/v2/tom/3o1VVsfBmmU_v2.md).
- Tom R quote (SOURCED): "even with a hit rate of 30 to 40% you have an average riskreward ratio of greater than three" BVpYGKz9PBU, MIDDLE, TOM-091 (ledger: BVpYGKz9PBU v2 extract quotes_verified FAIL; line machine-checked in CONCEPTS.md:72).
- Fabio quote (SOURCED, ASR): "to jump in with a super small stop loss okay you can cover yourself above the area and shoot for a 1 to 4.5" Is1HvdfQm5c, raw line 145, [21:14] (SETUP_CATALOG.md:1243).
- Fabio mgmt (SOURCED): "I will be really fast in putting my position to break even if this level failed" fZlNGWvd2Ko:43-45; "I'm only risking the profit of the day" fZlNGWvd2Ko:60-61 (CONCEPTS.md:136-137).
- SOURCED numbers: Fabio NQ stops 0.014-0.061% of price (15.75, 8.88, 3.38 points; R/fabio_transfer/FABIO_TRADE_LEDGER.md "F1/F3 numbers"); win rate 30-35% (Is1HvdfQm5c:244-245).
- Sketch: a long-thin trade box: tiny red stop strip, long green target strip labelled "1 : 4.5"; below a staircase of stop moves "BE -> trail" and a pyramid "adds only with the day's profit".

### A7. Session and timing  (FABIO: NY only; TOM: DAX cash, lunch is dead)
- Teaches: trade only when volume is there: Fabio trades NY session for US indices, volatile days only; Tom DAX cash session, thin lunch hour, opening range size matters.
- Fabio quote (SOURCED): "I only trade in the New York session for US indices because it's where the majority of the volume get traded" Pz8f0wWW12M lines 655-658 (CONCEPTS.md:103).
- Fabio quote 2 (SOURCED): "This is not common. You need volatility to do these kind of trades. And unfortunately, volatility is not there every day." 8CWKfoSJu3c ("20R in one NQ session", NASDAQ short, one-trade commentary), lines 84-88 (ledger PASS 9 quotes; extracts/processed/fabio_valentini/8CWKfoSJu3c/extract_8CWKfoSJu3c.md).
- Tom quote (SOURCED): "And during lunchtime, there's usually relatively little volume in the market." wPMiyJXL0zU, line 19, TOM-029.
- SOURCED number: Fabio IB (initial balance) = first 30 minutes of US open (LQvv5xgy_ik, SETUP_REVIEW.md:178-180).
- Sketch: a 24-hour clock ring; one arc highlighted "NY cash 13:30-20:00 UTC"; a faded arc "London: profile not so valuable (Pz8f0wWW12M:655-660)"; BTC runs all 24h, no cash open.

### A8. Tom's swing method: boundary breakout on daily closes  (TOM, newest video)
- Teaches (video M7ompiwv5co, "The Easiest Way to Start Trading (Swing Trading for Beginners)", Tom Vorwald, EN upload 2026-11-04): wait for daily closing prices; mark the sideways boundary; breakout with volume expansion; stop below the last sideways phase; target the next high-liquidity area; trade only if RRR >= 1.5; take 200-300 trades to judge.
- Quote (SOURCED): "wait for daily closing prices, we can trade much, much more patiently" (R/tom_swing_2026-11-09/extract_M7ompiwv5co.md:41; extract committed b9c4bf568 per OPERATOR_DECISIONS.md:2334). Other: "I would always place the risk below the last sideways phase at the latest" (:62); "only if that is ... at least greater than 1.5 or so" (:77).
- Sketch: daily candles in a box (rubber band), breakout candle with volume bar taller than the 20-bar average, stop under the box low, target arrow to the next HVN, label "wide stop 300-800 bps so a 10 bps fee is 0.015-0.04 R (OURS arithmetic, PRE_REG.md s2)".

---------------------------------------------------------------------------------------------------------------------------------------

## B. OUR RULE PER CONCEPT (what we actually coded)

### B1. Context first (A1)
- Rule (one line): old Java engine classifies state from VWAP slope + CVD slope + price vs value area, and filters setups by state; new ladder labels HTF bias from monthly colour vs 20-month SMA, weekly streak, prior-day VA.
- Code: src/main/java/datafeed/SetupCandidatesBuilder.java classifyState (:285-307) and determineSetupType (:464-499); R/tom_fabio_course_correction_2026-11-07/auction_context.py evaluate_forming_candle, build_mtf_context.
| Parameter | Value | Label |
|---|---|---|
| state thresholds (VWAP/CVD slope) | various | NO-SOURCE per comment :284 (CONCEPTS.md:188) |
| trend vs balance as setup splitter | concept | SOURCED (TOM-065) |
| monthly SMA length | 20 | OURS (auction_context.py evaluate_forming_candle sma_len=20) |
| census HTF bias = prior-day close vs daily SMA20, band +-2% | 20 / 2% | OURS (AUCTION_CENSUS_1108.md parameter table) |
| elapsed-fraction tau, P_keep colour probability | formula | OURS (auction_context.py p_close_colour) |
| 1M/1w/1d ladder idea ("trend from VPOC and value areas") | concept | SOURCED idea (TOM-053 Ld1dhjGdTCA), every threshold OURS (REVIEW_FABLE.md c) |

### B2. Value-area map and return to value (A2)
- Rule: prior UTC-day 70% value area; event = first 5m close outside VA; outcome = a later 5m bar same UTC day touches prior-day POC (count study); trade variants RETURN/FADE/ACCEPT in the desk.
- Code: MyTradingSys/backtest/vp_return_to_value.py analyse_day, study, near_band_primary; MyTradingSys/backtest/vp_pivot_probe.py build_profile, _value_area; R/sim_desk/studies/tom_vp.py; auction_context.compute_volume_profile.
| Parameter | Value | Label |
|---|---|---|
| value area share | 70% | SOURCED (TOM-277; extract_BB3c8visnkI) |
| "70% return" claim | 70% | SOURCED claim, measured 57.2% (E6) |
| profile period | UTC day / Monday-week | OURS (he uses cash session; NOT_IN_DATA for BTC) (R/tom_transfer_2026-10-11/vp_return/RESULT.md:71) |
| bin | 10 USD (FORMULAS s18) / 50 USD (auction_context, v3) / 0.067% of price (census) | OURS |
| signal bars | 5m | OURS |
| stop (desk trade) | 1 x ATR14(1h) | OURS (tom_vp.py DEFAULT stop_atr 1.0) |
| target (desk) | POC | SOURCED in kind (return to equilibrium, TOM-279) |
| pivot-anchored profile "last major high to last major low" | concept | SOURCED (sQ_biBKhPVU, FORMULAS.md:418); n in {2,3,5}, k, R=1 ATR, H=48x5m OURS |

### B3. Acceptance vs rejection (A3)
- Rule (auction_context): at a level, FAST_REJECTION = probe beyond then reclaim within 1-4 bars with rel_vol >= 2.0 and not a knife approach; ACCEPTED = consecutive closes beyond; STALE_REJECTION if reclaim > 3 bars ago. Live Aid levelstory: ACCEPTED = 2 closes beyond (15m).
- Code: auction_context.py classify_level_interaction (:570), is_knife_approach (:526), build_auction_trade_plan (:821); R/tom_fabio_course_correction_2026-11-07/auction_census.py (census); R/value_area_acceptance_2026-11-05/accept80.py; MyTradingSys/tools/live_aid/levelstory.js story().
| Parameter | Value | Label |
|---|---|---|
| acceptance = two consecutive 30m closes beyond VA | 2 x 30m = 12 x 5m | count OURS; "Dalton" idea (accept80.py:5) |
| acceptance in auction_context | 6 bars (6x5m = 30 min; on 1h = 6 h) | OURS, was MISLABELLED "SOURCED to accept80" (REVIEW_FABLE.md c, defect card census-acceptance-threshold-mislabel-1109) |
| rel_vol threshold | >= 2.0 | OURS (wick_census.py origin) |
| reclaim window | <= 3 bars (max_bars_since_reclaim 3) | OURS ("speed" is SOURCED TOM-010, no number) |
| knife approach | 2% drop, < 25% bounce, 12 bars | OURS |
| fee gate | fee_r <= 0.25 R (stop >= ~40 bps at 10 bps RT) | SOURCED as an OPERATOR decision d-stops-follow-trade-1106; OURS vs the traders |
| minimum net RR | >= 1.20 | OURS |
| stop | sweep extreme (+5 bps buffer in plan) | SOURCED in kind (TOM-072, Is1HvdfQm5c:144), buffer OURS |
| levelstory: touch 0.0005, near 0.003, wick 0.5, relVol 1.5, bbNear 0.1, look 3 | as listed | OURS, untested (levelstory.js header P) |
| census cooldown | 48 bars (5m) / 12 (1h), H=24 bars, R=1 | OURS |

### B4. Absorption / effort vs result (A4)
- Rule: Fabio v3 S3 effort-vs-result z-score over L=60 1m bars, big-trade push (99th/99.9th pct of prior 30 days), failed auction S5D, Model D enters after absorption + aggression; kline-only proxies: CVD lower-low absorption, escalation breakout.
- Code: L/fabio/v3/signals.py effort_result (:251), _effort (:232), net_big (:292), big_push (:300), failed_auction (:325), defended_level (:361), pressure (:223); L/fabio/v3/models.py model_d_trade (:231), scan_model_d (:427); L/fabio/fabio_cvd_absorption.py; L/fabio/fabio_escalation.py; R/fabio_cvd_2026-10-30/cvd_u7_u8.py; R/btc_of_level_auction_1112/b1.py (absorption at level); R/btc_orderflow_map_1112/events.py, prints.py.
| Parameter | Value | Label |
|---|---|---|
| balance k_bal | 0.8 ; POC band 0.25 R | NS-fixed = OURS (signals.py:27, header P02) |
| pressure drift q | 0.25 | OURS |
| S3 L / r_abs / r_ctl | 60 / 0.25 / 1.0 | OURS ("0 of 8 grid rows SOURCED", FABIO_V3_SOURCING_2026-10-02.md:52 cited in SETUP_REVIEW.md:134) |
| z_hi (S3) | grid (e.g. 2.5) | OURS |
| big trade = 99th/99.9th pct of prior 30 d aggTrade size | 99 / 99.9, 30 d | OURS (data-defined) |
| absorption threshold in his words | "UNDEFINED (almost zero)" | SOURCED as undefined (FABIO_RULEBOOK.md:152) |
| BTC A2 prints rule: |delta5| top 2%, 5m move < 0.1%, trade against delta | 2% / 0.1% | OURS (btc_orderflow_map_1112 PREREG) |
| B1 level event: PDH/PDL/VAH/VAL, absorption vs same flow away from level | - | OURS |
| delta | 2 x taker_buy - volume | exact aggressor delta at bar level (FABIO_OF_REPORT.md fee/limits note) |

### B5. LVN and node targets (A5)
- Rule: v3 LVN = bin <= 0.5 x median in a 50 USD profile; Model A = pullback to the nearest LVN after balance + pressure + breakout; Tom engine target = nearest POC/HVN passing net R floor; thin-zone T1/T2 BTC tests.
- Code: L/fabio/v3/signals.py lvn_levels (:158), select_lvn (:172); models.py model_a_trade (:89), scan_model_a (:274); SetupCandidatesBuilder.java:142-160 (targets) and MarketDataSnapshot.java:678-683 (LVN computed, never consumed); auction_context.compute_volume_profile lvn_ratio 0.25 (contiguous bins); R/btc_thin_zone_retest_1112/rules.py.
| Parameter | Value | Label |
|---|---|---|
| LVN fraction | 0.5 x median (v3) / 0.25 (auction_context) | OURS both (P35 NS-fixed) |
| Model A retrace >= 25% of leg before LVN touch | 25% | OURS; spec says "not in these transcripts" (FABIO_V3_SPEC.md:226, SETUP_REVIEW.md:134) |
| target = next high-volume node | concept | SOURCED (TOM-018) |
| "a few points short" of the level | concept | SOURCED (TOM-262); our offset not coded |
| T1 thin-zone: profile previous 7 UTC days, 0.05% log buckets | 7 d / 0.05% | OURS (btc_thin_zone_retest_1112/RESULT.md Notes) |

### B6. Trade build (A6)
- Rule: Tom engine: stop beyond swing extreme, target nearest node, limit at zone (8-bar order life); Fabio v3: stop = max(f x entry, structural), cap Dmax; maker entry; break-even/trail helpers; plan builder with fee gate; testnet-forward logger (context only).
- Code: models.py d_and_stop (:38); L/fabio/v3/manage.py; MyTradingSys/backtest/tom_bt.py; auction_context.build_auction_trade_plan; R/auction_forward_2026-11-09/forward_log.py; MyTradingSys/backtest/fees.py (FEES_DERIBIT: maker 0 entry/target, taker 5 bps stop/timeout).
| Parameter | Value | Label |
|---|---|---|
| hit rate 30-40% at R > 3 | 30-40%, R 3 / 4.5 | SOURCED (TOM-091; Is1HvdfQm5c:245) |
| Fabio NQ stop | 0.014-0.061% | SOURCED measured from his videos (FABIO_TRADE_LEDGER.md) |
| our stop floor f (v3) | 0.3% / 0.5% | OURS, 5-8x wider than his (SETUP_REVIEW.md:132); the older 0.15% floor retired by d-stops-follow-trade-1106 |
| round-trip taker fee | 10 bps | SOURCED (fees.py) |
| slippage RT | 2 bps (FORMULAS s13) vs 4 bps in code | OURS (mismatch open, CENSUS_5M15M_1109.md Notes) |
| Tom engine proof counts | 3 WATCH / 5 SETUP_FORMING | OURS (backtest/verdict.py:121-126) while Tom says "many, many parameters" (TOM-139) |
| 8-bar order life / time exit | 8 bars | OURS (not Tom's words; CONCEPTS.md:79) |
| forward logger: WAIT_BARS 3, MIN_TARGET_R 2.5, BE at +1R, half off at POC, MAX_HOLD_BARS 48 | as listed | OURS (forward_log.py header) |
| forward logger kill rule | 30 gate-pass fades, net R <= 0 | OURS/decision, null -0.087 R (REVIEW_FABLE.md d) |
| forward range | 75,400-80,900 | SOURCED to our Bible (R/mts_bible/BIBLE.md:28), OURS vs the traders |

### B7. Session and timing (A7)
- Rule: v3 runs only in the NY window (13:30/14:30 UTC + 390 min) with a day gate; IVB Model C = first 30 min range break; census session blocks; NY-session profile function exists but is not used in the census.
- Code: L/fabio/v3/day_gates.py (ny_open_utc, WINDOW_BARS, ENTRY_CUTOFF); models.py model_c (:194); auction_context.ny_session_window / prior_ny_session_profile (:344,:355); R/sim_desk/studies/fabio_v3.py.
| Parameter | Value | Label |
|---|---|---|
| NY-only | yes | SOURCED (Pz8f0wWW12M:655-658) |
| IB length | 30 min | SOURCED (LQvv5xgy_ik) |
| IB mid stop / edge target / one try per day / S4 push m in {5,15} | as listed | OURS (FABIO_V3_SPEC.md:126-129) |
| census UTC blocks asia 00-07, london 07-13, ny 13-21, late 21-24 | as listed | OURS (PRE_REG_5M15M_1109.md Context) |
| UTC-day levels instead of cash session | - | OURS; BTC has no cash session |

### B8. Swing (A8)
- Rule: pre-registered only. Breakout close beyond boundary/trendline on 4h and 1d, volume > 20-bar SMA, stop below last sideways phase, target prior HVN or measured move, RRR >= 1.5, fee 10 bps + 2 bps slippage. NOT RUN.
- Code: none run. Prerequisite code trendline_core.py has 3 FIX-FIRST gaps (R/tom_swing_2026-11-09/PRE_REG.md s4). Specification: R/tom_swing_2026-11-09/PRE_REG.md.
| Parameter | Value | Label |
|---|---|---|
| 1d closes, hold several days to 1-2 weeks, RRR >= 1.5, 200-300 trades | as listed | SOURCED (extract_M7ompiwv5co.md:38,41,77,80) |
| 4h arm, k=3 pivots, 5-bar consolidation, 20-bar volume SMA | as listed | OURS |
| stop width 3-8% (300-800 bps) | assumption | OURS arithmetic, unmeasured |

---------------------------------------------------------------------------------------------------------------------------------------

## C. FIDELITY PER CONCEPT (matches / simplified / distorted)

Legend: MATCH = same rule as the trader; SIMPLIFIED = reasonable proxy of his rule; DISTORTED = tested thing is not his thing. Course-correction findings cited as CC = R/tom_fabio_course_correction_2026-11-07/{AUDIT_AND_COURSE_CORRECTION, REVIEW_FABLE, POSTMORTEM_OPUS}.md.

| # | Concept | Grade | How (specific) | Evidence |
|---|---|---|---|---|
| C1 | Context first | SIMPLIFIED -> DISTORTED in code | Tom decides trend vs balance by counting closing prices (TOM-039 MISSING) and HTF profiles; Java uses 1m VWAP/CVD slope with unsourced thresholds. Ladder (1M/1w/1d) was absent from Java and Fabio v3; auction_context adds it but uses it only to size (full_with_htf vs scalp), never as a gate (AC:890-898). Census found no with/against gap: with -0.117 vs against -0.066 R (gate-pass) | CONCEPTS.md:188; POSTMORTEM s1 C3b; REVIEW_FABLE.md a |
| C2 | Value area map | SIMPLIFIED (count) / DISTORTED (trade) | Tom's profile is the cash session (DAX 9-12 etc.); BTC has none, we used UTC day. Fabio: cash-session profile, prior-session VAL. Bin/period OURS. The NY-session profile analogue exists in code (prior_ny_session_profile) but was never run in a test | POSTMORTEM s2 "Value area" row; vp_return/RESULT.md:71 |
| C3 | Acceptance/rejection | DISTORTED | (1) trader uses discretion: footprint/delta at the level, speed read by eye, no number; we use fixed thresholds (rel_vol 2.0, reclaim <=3 bars, 6-bar acceptance). (2) Acceptance threshold half of the accept80 sourced duration (6x5m vs 12x5m) and 6 h on 1h bars. (3) Entry: trader uses a limit at zone or a pullback after proof; census enters at market on the close of the firing bar, up to 3 bars after reclaim. (4) Census klines carry NO delta (delta defaults to 0), so absorption = wick shape + rel_vol only. (5) "77%" was misread as a win rate: it is a half-VA-width same-day drift, descriptive, no fees, no placebo. (6) classifier built for 5m/15m, first tested on 1h where 6 bars = 6 h | REVIEW_FABLE.md c; POSTMORTEM s1 C5b, C7, s2 "Entry trigger"; RESULT.md value_area_acceptance:10,13 |
| C4 | Absorption/effort-result | DISTORTED (proxy) | Fabio reads per-price footprint + big-trade bubbles + CVD inside a bar at a level; we have (a) kline taker delta at bar level (no price-level detail), (b) real footprint only from Binance aggTrades from 2024-12 onward on F:, and (c) live footprint writer stopped 2026-10-03 (edge_hunt_2026-11-09/PLAN.md:28). Heat-map/L2 walls, reload, icebergs: MISSING (34 of 97 rulebook rows need L2, FABIO_OF_REPORT.md:138). CVD absorption code accepts ANY higher low (no "same level" test); CVD never resets per session; escalation fires on a record bar with no break test | SETUP_REVIEW.md s3.6 and s5 rows 8-9; CONCEPTS.md:211-216 |
| C5 | LVN / node targets | DISTORTED | Fabio's LVN is a pivot inside a trend ("rebalance before continuing"), but Model A/B treat it as a pullback/fade level; volume-FVG test spread each bar's volume uniformly so it could not produce his "lowest volume bin in value area". Java computes LVN but never consumes it; snapshot lists only 3 highest HVN / 3 lowest LVN (possible defect, CONCEPTS.md:275). Targets: fixed 1R in census (OURS) vs Tom's node-to-node; node+BE exit tested later (E21) | CONCEPTS.md G findings 5-6; POSTMORTEM s2 "Target" |
| C6 | Trade build | DISTORTED (largest) | Payoff shape never matched: traders 30-40% hit at R >= 3 with BE/trail/adds; census used symmetric 1R bracket, 24-bar horizon. Stops: Fabio 0.014-0.061% vs our floor 0.3-0.5% (5-8x wider) or, in the fee-gate world, >= 40 bps; Tom DAX 0.08-0.26%. On 10 bps taker BTC perps a 5-8 bps stop pays 1.2-2.8 R in fees: this is exactly why a 1-tick stop copied from index futures fails (RESCORE.md: gross +0.079..+0.155 R becomes net -1.423 R). Adds are never executed by any engine (v3/README.md:39; position_manager.py has no pyramid). Fable showed 2R and 3R targets do not rescue the 1h label (-0.035/-0.023 R) | RESCORE.md; POSTMORTEM s2; REVIEW_FABLE.md a, cross-check |
| C7 | Session/timing | DISTORTED (absent in most tests) | Fabio trades NY only; the first census had no session at all, and the 12-16 UTC block (US open) was the WORST cell for fades (-0.180 R, n=526). v3 does gate to NY but only on data since 2024-12 (IS 2024-12-02..2025-12-31, OOS 2026-01-01..06-25). BTC trades 24/7: index-futures clocks (cash open, close, settlement) are not carried to BTC per operator 2026-11-12 | REVIEW_FABLE.md a "Session" row; OPERATOR_DECISIONS.md:2331-2333 |
| C8 | Swing | NOT TESTED | Only a pre-registration; every earlier Tom test was intraday 5m-1h, where 10 bps fees on 5-40 bps stops decide. Trendline layer blocked at FIX-FIRST | OPERATOR_DECISIONS.md:2141-2143; tom_swing_2026-11-09/PRE_REG.md |

Cross-cutting fidelity facts
- Instrument: Tom/Fabio trade index futures (DAX, ES, NQ) with ~0.5-1 bps round-trip cost (OURS estimate, RECALL_DAX.md:51); BTC perp = 10 bps taker round trip (SOURCED fees.py). Stops that cost < 0.15 R on futures cost 1.2-2.8 R here (AUDIT root cause 1).
- Data: our DAX tests ran on CFD candles with delta forced to 0 (backtest/dax_data.py:100-106), so Tom's own order-flow proofs could never fire (R/tom_dax_what_is_proven_2026-10-13/REPORT.md).
- Date hygiene: most Tom/Fabio numbers were measured on VALIDATION/HOLDOUT dates; nothing was promoted, but HOLDOUT 2025-07+ is spent for the VP level-touch and Fabio order-flow families (SETUP_REVIEW.md s0, s4 item 1).
- Anecdote fitting: the four Oct-Nov winner trades in AUDIT Part 3 were hand-picked and the unit tests replay the same Nov-6 bars; same 5m window holds 67 FAST_REJECTION events, 28 target / 38 stop / 1 open (POSTMORTEM C6, C11; AUCTION_CENSUS_1108.md).
- Docs-vs-code contradictions (12 listed): SETUP_REVIEW.md section 5 (e.g. Model B uses a rolling 1m balance, not prior-day value + 5m close).

---------------------------------------------------------------------------------------------------------------------------------------

## D. SUPPORT LAYERS (what confirms/filters Tom/Fabio, wired or not)

| Support | What it does | Wired into Tom/Fabio? | Evidence |
|---|---|---|---|
| Tom <-> Fabio cross-gate | none: Fabio v3 may import only stdlib/orderflow_bars/siblings (test_b127_fabio_v3_isolation); Tom core never filtered by layers (test_layer_boundaries.py:3-9); consensus module is observation-only, nothing reads its rows back | NOT WIRED (by design; needs operator ruling) | R/tom_fabio_guidance_2026-10-12/GUIDANCE_AUDIT.md |
| tom_bt fabio_tag | tags a Tom signal when a same-side Fabio event closed within n bars; "DESCRIPTIVE ONLY, Never a filter" | descriptive | GUIDANCE_AUDIT.md (backtest/tom_bt.py:280-290) |
| CBP context (analyst calls) | analyst levels are Context, never signals (memory note); Live Aid verdict board + watch list use them | context in Live Aid only; not an input to any Tom/Fabio engine | MyTradingSys/tools/live_aid/REQUIREMENTS.md R13, R14 |
| HTF ladder (1M/1w/1d) | htf_bias, tau, P_close_colour, SMA20 regime | in auction_context + Live Aid timeframe strip (1M added 2026-11-07); used for sizing tier, NOT a gate; census gate arm tested it (E21: ladder gate helps slightly on 15m, -0.14 to -0.11 R) | AUDIT Part 4; CENSUS_5M15M_1109.md Notes |
| Regime gate / phase | PRE_REG `## Context` + `Regime mix:` is mandatory since 11-04; phase = the Bible range 75.4-80.9k (forward logger only) | gate in forward_log (range bounds), not in census/engines; "bear gate never fires on BTC" (memory note, not re-verified here) | LESSONS_DIGEST.md:33; forward_log.py header |
| Levels (prior D/W/M, session) | levels = where to look; blind touches = 0.00 R (vp_pivot_probe 0/48) | levels feed census + Live Aid level_registry.js; in Live Aid as "At the level" | PHASE2_RESULT.md; levelstory.js |
| Footprint / CVD | per-price footprint (10 USD bins, 1 min) from aggTrades via orderflow_live.py; 27 columns, b99/b999 big-trade columns | v3 uses it (shadow/collection only in live_runner_cli.py:126-137, 200-237); live writer stopped 2026-10-03; Legend 12h footprint check pending (no Chrome profile): footprint_12h_1112/CHECK.md | CONCEPTS.md:207,215; edge_hunt PLAN.md:28 |
| htf_context_live | Fabio 4H balance context, separate layer "nothing here gates Tom" | NOT WIRED to gate; the .py.new copies hardcode UNAVAILABLE | htf_context_live.py:3; STATUS.md:38-39; AUDIT root cause 2 |
| OI / long-short ratio / funding | in Java snapshot (MarketDataSnapshot.java:342,405,1541-1562); no Tom/Fabio gate uses them; Live Aid "What the money is doing" tile reads OI per venue | context only | GUIDANCE_AUDIT.md; REQUIREMENTS.md R16 |
| Sessions | NY window gate in v3; session blocks in census; session label in snapshot (MarketDataSnapshot.java:938-991) | v3 yes, census split only | CONCEPTS.md:201 |
| Scenario ledger (Context rows) | every map/base case logged then scored; Tom/Fabio-flavoured rows e.g. S004 (accepted below VAL, 80% rule 44%), S006/S007 (US prep inside 11-05 VA), S021 (VAL 74,300 / VAH 75,350 accept) | logged by hand; scoring column NA for context rows; S004 outcome DOWN, S021 outcome DOWN | R/eagle_eyes_picture_2026-10-28/scenario_ledger.csv |
| Meta-label panel | tested whether BBWP, D1 trend, Cowen band, funding sign, session, RSI, WaveTrend, relative volume filter Tom VP fade / Fabio Model C stand-in | tested, nothing separates (E14) | R/meta_label_tom_fabio_2026-10-31/output.md |

Not wired at all (concept needed, nothing consumes): Bollinger bands, RSI 40-60 regime, vol squeeze as Tom/Fabio inputs (all NO-SOURCE: Tom names BB only to say they mislead, S7 in SOURCED_RULES.md); OI / long-short ratio / funding as direction filter (0 hits in 113 transcripts).

---------------------------------------------------------------------------------------------------------------------------------------

## E. TESTS (fee-net unless stated; R = research dir)

Verdict key: PASS = lower CI/pre-reg bar above 0 fee-net; FAIL = pre-reg bar missed or CI below 0; INCON = inconclusive / n too small / descriptive; DESC = descriptive, no fee-net claim.

### E.1 Tom (value area, level touch, spike fade)
| ID | Study | Date | n | Fee-net result | Verdict | Lesson |
|---|---|---|---|---|---|---|
| E1 | Old Java engine watch_episode (TOM_CORE_BT 0929) | 2026-09 | 4,417 filled | gross -0.07 R, net -0.30 R (CI -0.34..-0.25); random null "at least as good" | FAIL | Our caricature of Tom, not Tom; matched 0 of 7 of his DAX entries (SETUP_REVIEW.md s2.1; REPORT.md DAX) |
| E1b | Same, live rule only | 2026-09 | 17 filled | net -0.19 R, CI -0.76..+0.46 | INCON | too few trades |
| E2 | Old engine rerun, no stop floor (TOM_CORE_BT_RERUN 1007) | 2026-10 | 2,880 (>=1 proof) | gross -0.145 R, fee 2.76 R, net -2.912 R, median stop 8.2 bps; at >=5 proofs 13-17 trades in 4.7 y | FAIL | tiny stops + 10 bps fee = fee-trap; proof starvation (AUDIT table row 1) |
| E3 | Tom DAX recall v1/v2 | 2026-10-13 | 7 entries / 5 sessions | v1 0 of 7; v2 idea alone 4 of 5 (random 0.3%), with >=1 proof 2 of 5 (random 15.7%) | INCON | candles find his days, not his entries; no P&L ever run on DAX; delta forced to 0 (tom_dax_what_is_proven REPORT.md) |
| E4 | tom_vp.py Python VP engine, 5 symbols x 4 variants | 2026-10 | 20 cells | 0 of 20 beat random-entry null (p >= 0.088); BTC strict -0.399 R/trade (as cited by AUDIT, not re-checked) | FAIL | no HTF context, no acceptance vs rejection split |
| E5 | vp_pivot_probe PHASE2 (POC/VAH/VAL touch, prior D/W/M) | 2026-10-09 | 48 streams, >= 1,055 each | taker net -0.185..-0.248 R, maker -0.10..-0.16, gross -0.042..+0.010; 0 of 48 beat placebo; best weekly POC +0.032 (CI -0.003..0.065); all years 2022-26 negative | FAIL | a level is where to look, never a blind limit; reads VALIDATION+HOLDOUT dates |
| E6 | VP return-to-value COUNT (DEV 2022-01..2024-06) | 2026-10-11 | 871 events | real 57.2% (CI 53.9..60.7) vs placebo 46.8%, +10.4 pp (CI 6.4..14.4); near-band placebo 55.8% vs real 55.0% (-0.8 pp, CI -5.2..3.7). Count, NO fee/stop/target | DESC | his 70% is above the CI; pooled excess comes from far-shifted bands (vp_return/RESULT.md via SETUP_REVIEW.md s2.2) |
| E7 | Near-band placebo as PRIMARY, fresh 2020-2021 | 2026-11-01 | 352 real / 353 placebo | real 63.4% (CI 58.2..68.2) vs near placebo 58.9% (CI 53.8..64.0), diff +4.4 pp (CI -0.3..8.9); far bands |d|>=2 +21.1 pp | FAIL (pre-reg) | positive but sub-significant for near bands; says nothing about cash-session profiles (R/tom_v2_gross_first_2026-11/RESULT.md) |
| E8 | sim-desk tom_vp prior_day RETURN / FADE / ACCEPT, DEV 2022-04..2024-06, stop 1 ATR, target POC | 2026-10-31 | 1,054 / 1,765 / 1,420 | -0.224 R (-0.300..-0.148) / -0.238 R / -0.202 R (n6) | FAIL | the only DEV-clean fee-net Tom trade numbers; all negative (layer_lab/TRIALS.md rows 2026-10-31) |
| E8b | sim-desk tom_vp prior_week RETURN / ACCEPT | 2026-10-31 | 148 / 365 | -0.172 R / +0.081 R (-0.206..+0.385) | INCON | not enough data (TRIALS.md) |
| E9 | sim-desk tom_spike_level (spike fade), BOTH sides, 6x5m push >= 4 ATR | 2026-11-04 | 1,399 | -0.222 R (-0.269..-0.176) | FAIL | TRIALS.md |
| E10 | Tom "correlation trick" TOM-CTX-DIV (H1 DAX vs ES/Nikkei/BTC; H2 BTC vs ES/DXY), hold 3d | 2026-10-29 | DEV 35 / 52; VALIDATION 8 / 16 | -110 / -72 bps DEV; -93 / -19 bps VALIDATION; shuffled-basket placebo: 100% / 59% of draws at or above real | FAIL (NOT-ADD) | no cross-market information (R/tom_correlation_trick_2026-10-26/RESULT.md) |
| E11 | Tom meta-label panel: Tom VP daily value-area fade, best third by filter | 2026-10-31 | 1,812 filled (608 top third) | best third -0.277 R vs random third -0.265; placebo p 1.000; OOF AUC 0.474 | FAIL | no filter (BBWP, D1 trend, Cowen band, funding, session, RSI, WaveTrend, rel vol) separates winners (meta_label_tom_fabio_2026-10-31/numbers.json, output.md) |
| E12 | Q33 matrix (BB-outside, LVN traverse/reject, FVG, sweep-void), 15m-4h, all-taker | 2026-10-12 | 336 cells; 186 with n >= 300 | median gross +0.0003%; 0 of 186 positive at 60 min; T2 LVN traverse -0.104/-0.115%, T2b LVN reject -0.102/-0.114% | FAIL | every trigger is a coin flip before fees (R/tom_fabio_guidance_2026-10-12/MATRIX_REPORT.md) |

### E.2 Fabio (order flow, v3, proxies)
| ID | Study | Date | n | Fee-net result | Verdict | Lesson |
|---|---|---|---|---|---|---|
| E13 | Fabio L1 kline proxies (CVD absorption, escalation, volume FVG), 2022-01..2026-09, 0.10% RT | 2026-10 | 109-16,999 events per cell | 0 cells survive with PBO < 0.5; best escalation 1h +0.113%, n 182, PBO 0.756; FVG real ~ random-bin control | FAIL | proxies only; fixed horizon h=5 (FABIO_L1_REPORT.md; SETUP_REVIEW.md s3.6) |
| E14 | Fabio OF conditional model (aggTrades, 90 days 2026-07-01..09-28) | 2026-09-30 | per variant pooled n (balance_fade mkt: 2,306) | 0 of 64 true-flow variants net-positive OOS n >= 30 | FAIL | report SUPERSEDED (legacy fees); one regime, 90 days (FABIO_OF_REPORT.md) |
| E15 | RESCORE with plan stops + current Deribit fees | 2026-11-06 | balance_fade all/mkt: 2,306 per variant; ny/mkt: 655 | PLAN tight: gross +0.079 R, net -1.423 R (median stop 7.3 bp); ny mkt gross +0.037, net -1.324; OLD 0.15% floor -0.561; 0 of 16 variants net>0 OOS | FAIL | positive-ish gross destroyed by 1-tick stop geometry (L/fabio/RESCORE.md) |
| E16 | Fabio v3 L3 pre-registered grid, Models A-D | 2026-10-31 | A: 12 IS days / 0 OOS; D: 8 IS / 0 OOS; B: 42 IS + 4 OOS fills scored 0 R "unmanaged"; C OOS 79 trade days | C OOS mean -0.1038 R/day (CI -0.2087..-0.0053) at 2 bps; 0 bps -0.0802, 5 bps -0.1391; A, B, D "never fire" (S1 balance true in ~3.1% of 1m windows) | FAIL (C), INCON (A,B,D) | over-gating makes the engine deaf; scoring bug hid B as 0 (SETUP_REVIEW.md s3, FABIO_V3_L3_NOT_MEASURED.md) |
| E16b | v3 IS rerun with fixed Model B (IS only) | 2026-11-08 | 266 IS windows | mean net R/window A +0.0061 (1 nonzero window), B +0.0038 (2), C -0.0141 (142), D +0.00006 (1) | INCON | A/B/D rest on 1-2 trades (FABIO_V3_L3_NOT_MEASURED.md) |
| E17 | sim-desk fabio_v3 price-only Model C / B, DEV | 2026-10-31 | C: 518 / 515; B: 155 / 64 / 19 | C m15 push OFF f0.5% +0.062 R (-0.135..+0.268) NOT ENOUGH DATA; C 2R target -0.074; B N60 -0.448 R FAILED, N120 -0.445 FAILED | FAIL (B), INCON (C) | Model B "price-only" loses; Model C CI spans 0 |
| E18 | Fabio meta-label stand-in (Model C price-only) | 2026-10-31 | 518 | best third -0.003 R vs random +0.029; D1 trend down +0.196 (post-hoc), BBWP expansion +0.396 (n 81, post-hoc) | INCON | post-hoc cells among 21; leads at most (meta_label output.md) |
| E19 | CVD claims U7/U8 on BTC 1m taker delta, DEV 2022-01..2024-06, descriptive | 2026-11-05 | U8: 1,469 divergence vs 1,439 control | U8 reversal in 4h: 28.5% divergence vs 31.5% matched control; low breaks MORE (65.4% vs 59.2%); U7: CVD adds +6 pp / -5 pp beyond price direction | DESC (fails the claim) | bar-level delta, not a footprint (fabio_cvd_2026-10-30/RESULT.md) |
| E20 | Large-trade absorption, level-approach prep | 2026-10-30 / 11-05 | 2,175 / 887 | b99 absorption reversed 18% vs 27% baseline (stall, not reversal); fast approach into 1h swing continued 56.3% | DESC | order flow without location = continuation (AUDIT table row last) |

### E.3 Plain auction context (Argon classifier and follow-ups)
| ID | Study | Date | n | Fee-net result | Verdict | Lesson |
|---|---|---|---|---|---|---|
| E21 | value_area_acceptance (accept80) | 2026-11-05 | R: 493; A: 300 days (2024-12-02..2026-09-28, 666 days) | R: back inside then far VA edge 44% (CI 40..49); A: accepted below VAL then half-VA-width lower same day 77% (72..81), back to POC 42%. No fees, no placebo | DESC | Dalton "80% rule" is 44% on BTC; 77% is NOT a win rate (R/value_area_acceptance_2026-11-05/RESULT.md) |
| E22 | Auction census 1h, 7y (Binance spot, 2019-11..2026-11) | 2026-11-08 | FAST_REJECTION 2,148 events (1,871 gate-pass); ACCEPTED 2,798 gate-pass; KNIFE counterfactual 152 | FAST gate-pass net -0.087 R (SE 0.022), gross -0.010 R at median 96 bps stop; ACCEPTED -0.096 R; KNIFE fade -0.115 R (SE 0.078); every year 2019-2026 negative (-0.048..-0.183) | FAIL | classifier alone carries no direction on 1h at 1R; Fable reproduced byte for byte, 50/50 rows recomputed (R/tom_fabio_course_correction_2026-11-07/AUCTION_CENSUS_1108.md, REVIEW_FABLE.md) |
| E22b | Census 5m window 2026-10-03..11-07 | 2026-11-08 | FAST 67 (28 target / 38 stop / 1 open); gate-pass 10 | all-events net -1.077 R (mean fee 0.925 R); gate-pass +0.089 R, SE 0.312 | INCON | fee trap on 5m; n=10 is noise |
| E22c | Fable recompute with 2R / 3R targets, 1h | 2026-11-09 | 1,871 | -0.035 R (SE 0.029) / -0.023 R (SE 0.033) | FAIL | target size alone does not rescue the label (REVIEW_FABLE.md cross-check) |
| E23 | Census 5m/15m, session x ladder gate, bracket vs node+BE, 3 fee arms (pre-reg, kill line frozen before run) | 2026-11-09 | H1 (15m, fades, london+ny, ladder, node+BE): 1,484 | Deribit net -0.106 R (SE 0.078, t -1.4); taker -0.358 R (SE 0.068); taker+slip -0.527 R; gross +0.064 R; exits target 313 / stop 1,063 (656 at BE) / time 108; median stop 39.5 bps; median node target 2.1 R. 15m ungated bracket 5,493: -0.162 R; 5m H1-equivalent 1,579: -0.339 R | FAIL | node+BE beats 1R bracket on 15m (-0.11 vs -0.20 R) but not zero; the last untested exit joins the closed list (CENSUS_5M15M_1109.md, PRE_REG_5M15M_1109.md) |
| E23b | E23 post-hoc splits (about 30 cells, leads only) | 2026-11-09 | 15m 2026: 170; rally_in_macro_bear: 226; range_1024 phase: 5 | 2026 +0.568 R (SE 0.596); rally_in_macro_bear +0.158 R (SE 0.448); range_1024 +2.369 R (n 5); London -0.015 (SE 0.177) vs NY -0.168 (SE 0.053) | INCON | post-hoc, reported not judged; seeds for the context-only testnet run |
| E24 | eh-h3 first-touch sweep-and-reclaim of prior D/W high/low (T04), DEV 2020-01..2024-06 | 2026-11-10 | 1,150 | -0.221 R (CI -0.305..-0.136); gross +0.05 R; 36% hit at 2R; fees 0.27 R | FAIL | edge_hunt_2026-11-09/results/eh-h3-first-touch-sweep/RESULT.md |
| E25 | eh-s2 wick at HTF level + context (T09 long, T10 short), maker limit | 2026-11-10 | 41 / 47 | -0.581 R / -0.804 R; gross -0.29 / -0.46 R; target hit 5% / 4% | FAIL (power-adequate) | sweep extreme is retaken after fill (eh-s2-wick-level-context/RESULT.md) |
| E26 | eh-h4 speed-in + time-at-level (T05) | 2026-11-10 | 300 | -0.086 R (SE 0.081, CI -0.245..+0.074); gross +0.115 R; mean fee 0.20 R on ~60 bps stops; descriptive: fast/time>2 continues 65.7% | FAIL | fast-in touches that linger continue (eh-h4 RESULT.md) |
| E27 | eh-o1 confluence dose-response (T13) | 2026-11-10 | 13,851 events; score >= 3: 410 | score>=3 -0.163 R (SE 0.087); slope +1.04 (CI -0.91..+2.99) driven by one 0.001 bp-stop event | INCON | stacking reasons does not make fades pay (eh-o1 RESULT.md) |
| E28 | Pre-US failed-break short, 10 USD-M symbols, DEV | 2026-11 | 1,393 | -2.47 bps of K (SE 4.39, t -0.56); win 60.7% | FAIL | R/pre_us_failed_break_10sym_2026-11/RESULT.md |
| E29 | Live Aid level story on history (15m, 180 d, DESC) | 2026-11-10 | ideas n 2,852 | ideas right 49%; net of 10 bp negative in almost every bucket; REJECTED turn >=5 +0.67 first 90 d -> 0.39 last 90 d | DESC | "coin flip so far" is printed on the card (R/level_story_1110/RESULT.md; OPERATOR_DECISIONS.md:2191) |

### E.4 BTC-native order-flow families (after 2026-11-12 decision), DEV 2022-02-01..2024-05-31, fee 10 bp RT
| ID | Study | n | Fee-net result | Verdict | Lesson |
|---|---|---|---|---|---|
| E30 | Four value-area rules (btc_untested_rules_1112): A acceptance then edge retest | 139 | -28.78 bp, t -2.75; accepted edges hold 58.6% vs 46.7% yet buying the hold loses; placebo >= real 0.978 | FAIL | holding is real, edge is not |
| E31 | B return to liquidity (fade to prior POC) / C thin close pulls to POC / D naked weekly POC | 885 / 462 / 50 | B -12.18 bp (t -3.90); C -2.64 bp (t -0.40, better than placebo -10.9, first half negative); D +4.54 bp (t 0.06; touch 75.0% vs mirror 80.9%) | FAIL / FAIL / INCON | revisit POC 44.3% in 6 h but 1:1 fade net negative |
| E32 | Order-flow map: clocks (24 h buckets, funding windows, weekdays), prints A1/A2, events A3, level B1/B2 | clocks 851 days; A1 204; A2 15 / 170; A3 819; B1 524; B2 480 | best clock h22 long -5.22 bp (gross +4.78); A1 -9.19 bp (z60 +0.12); A3 funding extreme -7.5 bp; B1 absorption at PDH/PDL/VAH/VAL -13.6 bp vs away -9.1 (level adds nothing, at-minus-away -4.5 bp); B2 unfinished auction at 24h extreme -15.8 bp (15m -11.3) | FAIL (A2 INSUFFICIENT_N) | no cell passes; no paper slot (btc_orderflow_map_1112/RESULT.md) |
| E33 | Last order-flow rules: R8a trend-down short / R8b sell extreme long / R5 open inside VA fade / R11p breakout vol persists / R11d vol dries | 4,272 / 710 / 496 / 546 / 158 | -0.0953% (t -10.6) / -0.0648% (t -1.94) / -0.1173% (t -3.36) / -0.0739% (t -2.88) / -0.1423% | all FAIL (R11d INSUFFICIENT_N) | R5: only 5.1% of 532 days opening inside VA stay inside all day (btc_last_orderflow_rules_1112/RESULT.md) |
| E34 | Thin-zone pass-through T1 / accepted-breakdown retest T2 | 4,892 / 71 | T1 -9.71 bp (t -25.6; gross 0.29 bp; 87% hit the one-bucket stop); T2 +3.68 bp (t 0.35; half A +13.01 n 21, half B -0.24 n 50; placebo band -38.9..20.5) | FAIL / FAIL | T2 positive mean but second half not positive (btc_thin_zone_retest_1112/RESULT.md) |
| E35 | Footprint 12h vs Legend check | - | pending: chart profile not connected | NOT RUN | footprint_12h_1112/CHECK.md |

### E.5 Not run / waiting
- Tom swing 4h/1d count: PRE_REG only (R/tom_swing_2026-11-09/PRE_REG.md; target n >= 200 per 4h cell, >= 100 per 1d cell).
- NY-session value area on BTC, delta-at-level testnet log, phase-scoped testnet-forward (forward_log.py exists, context-only): cards tf-ny-session-va-profile-1109, tf-delta-at-level-testnet-log-1109, tf-testnet-forward-range-phase-amend-1109 (POSTMORTEM_OPUS.md "Cards").
- Fabio order flow at real footprint with his management (adds, trail): NOT_SEEN as a dedicated test (CONCEPTS.md G5).

Headline counts (only what the files state): 0 Tom or Fabio setup has a fee-net out-of-sample pass (SETUP_REVIEW.md header); census 1h n=1,871 net -0.087 R; census 15m H1 n=1,484 net -0.106 R; v3 Model C OOS -0.1038 R/day.

---------------------------------------------------------------------------------------------------------------------------------------

## F. OPERATOR IDEAS (failed vs promising)

Sources: MyTradingSys/system/OPERATOR_DECISIONS.md (line refs), R/four_model_review_2026-11-11/COMPARE.md, R/edge_hunt_2026-11-09/PLAN.md.

### F.1 Failed (tested, no fee-net edge)
| Idea (his words, short) | Date | Test | Result |
|---|---|---|---|
| "Orderflow is real, Tom is not lying; apply the core idea on the BTC chart by eye" (OD q11, :361) | 2026-10-13 | TOM_ON_BTC plan, then blind chart marks | G3 blind marks dropped (he rejects candle-only TAKE/SKIP, d-tom-btc-no-human-reader :1551); DAX tests could not read order flow (delta 0) |
| Tom correlation trick (DAX vs ES/Nikkei/BTC divergence) | 2026-10-26 | E10 | NOT-ADD; DEV -110 bps, VALIDATION -93 bps |
| "Acceptance / Dalton 80% rule: is MTS capturing it?" | 2026-11-05 | E21 | 44% on BTC, not 80% |
| In a range band-to-band repeats (BB range-to-range) | 2026-11-04 | R/bb_range_to_range_2026-11-04/RESULT.md | move to the opposite band completes about 1 in 5, vs about 1 in 3 needed on a 2:1 bracket; gross ~0 |
| Pre-US failed break fade, 10 symbols | 2026-11 | E28 | -2.47 bps, t -0.56 |
| "Naked Tom/Fabio trades by session on the everyday chart; I do not accept before/after fees" (OD :2291) | 2026-11-11 | COMPARE.md s4 (arithmetic) | his fee arithmetic right for a winner; losers still pay the fee; break-even win rate 85% (100 USD move, market) / 54% (1,000 USD move); entries at levels are right ~47-51% (COMPARE.md:29-46) |
| "Take only the order-flow idea, BTC on its own clocks" (OD :2331-2335) | 2026-11-12 | E30-E34 | all FAIL on DEV; no paper slot |
| Live Aid "At the level" weights (BB, wick, volume, CVD, OI) (OD :2188-2191) | 2026-11-10 | E29 | ideas right 49% (n 2,852); weights do not separate outcomes |
| "Why did 7 agents not find an edge?" (OD :2130) | 2026-11-09 | eh-f1 DESIGN.md | 1R setups win 42-50%, 2-3R setups 29-39%: both sit at zero after fees |

### F.2 Looked promising (leads only, none validated)
| Idea / cell | Source | Number | Status |
|---|---|---|---|
| Range-edge fades in the current 75.4-80.9k phase are the operator's own claim | POSTMORTEM_OPUS.md s2-3; forward_log.py | context-only testnet run, kill after 30 gate-pass fades net <= 0 | running design; no result in files |
| Rally inside macro bear, 15m fades | CENSUS_5M15M_1109.md Notes | +0.158 R, SE 0.448, n 226 | post-hoc lead among ~30 cells |
| 2026, 15m, session+ladder, node+BE | same | +0.568 R, SE 0.596, n 170 | post-hoc; other years negative |
| Weekly ACCEPT (prior-week value) | TRIALS.md 2026-10-31 | +0.081 R (-0.206..+0.385), n 365 | NOT ENOUGH DATA |
| T2 accepted-breakdown retest | E34 | +3.68 bp, t 0.35, n 71; long rows +9.4 bp (n 35) | FAIL (second half not positive) |
| Reclaim at close, stop on a close back beyond the level (4h) | edge_hunt PLAN.md:25 | net +0.271%, CI -0.253..+0.805, n 114 | POWER (leans positive) |
| Malkan 4h level short (not Tom/Fabio) | COMPARE.md:14 | +0.10 R, n 126 | forward slot; included as comparison |
| Fabio Model C stand-in, trend-down day / BBWP expansion | E18 | +0.196 R (n 241), +0.396 R (n 81) | post-hoc, one of 21 cells |
| Range laddering (martingale idea: fixed risk over 3-4 levels, one invalidation) | OD :1830-1832 | none | written proposal only, no code |
| Tom swing breakout on daily closes | OD :2141-2143; PRE_REG.md | fee drag 0.015-0.04 R at 300-800 bps stops (arithmetic) | not run |
| Delta at level, NY-session value area | POSTMORTEM_OPUS.md cards | none | cards waiting |

---------------------------------------------------------------------------------------------------------------------------------------

## G. SIM VERIFY: click paths (what exists, what does not)

Two surfaces: Simulator ("sim desk", live Python server) and Live Aid (single HTML page). Plus the static simulator artifact. Source docs: R/sim_desk/GUIDED_SESSION_PLAN_2026-11-10.md, R/sim_desk/DESIGN.md, MyTradingSys/tools/live_aid/STEPS.md.

### G.0 Open
- Sim desk: `python MyTradingSys/research/sim_desk/desk.py` (opens browser, prints address). DEV window only 2022-04-01..2024-06-30 (banner "DEV window only"). Page: study chips + "Study" dropdown; settings form; Run; numbers strip (win rate, profit factor, max DD, gross/fee/net); breakdown table (year, side, 4-hour UTC block); clickable trade list with candle chart; CONDITIONS panel (side, UTC hour window, EMA trend, ATR percentile, weekday, "layer B fired within N bars"); Monte Carlo band; compare A vs B (GUIDED_SESSION_PLAN s2).
- Static artifact (no server): research/sim_desk/artifact/index.html, built by artifact/build_artifact.py. Tabs: Families | News | Tom | Fabio | Malkan | Krown | Bollinger | RSI | WaveTrend | 11-09 census | Verdict grid | Charts | Comments (build_artifact.py:706). Tom and Fabio tabs list every test whose title/family contains "tom"/"fabio" (build_artifact.py:502-504). One Verdict grid cell per test.
- Live Aid: double-click MyTradingSys/tools/live_aid/live_aid.html in Chrome/Edge (needs live_aid_indicators.js beside it) (STEPS.md:7). Tabs: Home | Money | News | US open | In trade | Now ... (live_aid.html:123).

### G.1 Per concept
| Concept | Surface | Click path | What to look for |
|---|---|---|---|
| A1 Context | Live Aid | Home tab, timeframe strip (adds 1M: monthly colour, last 3 months, flip, CVD, Bollinger position, close-colour probability) | forming 1M candle colour vs open; text in the "What the indicators say" card. Backtest of the ladder as a gate: sim desk CONDITIONS panel EMA trend/ATR band is generic; no Tom-specific ladder gate documented |
| A2 Value area | Sim desk | Study = tom_vp; anchor = prior_day; setup = RETURN; target = POC; shift OFF; stop 1.0 ATR; Run | filled n 1,054, mean net R -0.224 (-0.300..-0.148); breakdown by year/side/4h block; open 5 worst losers and 5 best winners; the page labels every number box "(trader)" or "(ours)" (tom_vp.py header) |
| A2 variant | Sim desk | same study, setup = FADE (edge touch from inside, close back in) | n 1,765, -0.238 R |
| A3 Acceptance | Sim desk | Study = tom_vp, setup = ACCEPT, accept_n 3 / 6 / 12, shift OFF or WITH | n 1,640 / 1,420 / 1,180: -0.250 / -0.202 / -0.264 R (TRIALS.md). Weekly anchor: prior_week ACCEPT n 365 +0.081 R NOT ENOUGH DATA |
| A3 Acceptance (live) | Live Aid | Home tab, "At the level" card | state per nearest level above/below: APPROACHING / TESTING / REJECTED / BREAKING / ACCEPTED / FAILED BREAK; evidence chips (wick, BB 15m, relative volume, taker delta, absorbed touch, OI, WaveTrend 15m); "valid / void" line; IDEA flash when levels agree; amber "MIXED: levels disagree, no idea"; expected honesty line "coin flip so far" (levelstory.js, home.js:310-320, E29) |
| A3 census | Static page | tab "11-09 census" | one row per tested study with colour verdict chip, n, mean net R, one-line why; no new backtest (census_1109.py header). Includes the 5m/15m census |
| A4 Absorption | Sim desk | NOT DOCUMENTED as a desk study: the v3 absorption (S3) needs delta that starts 2024-12-02, after the DEV window (fabio_v3.py header, "LEFT OUT and shown on the page: Models A and D"). Use Live Aid "At the level" card absorption chip instead | "Fabio absorption = aggressive delta into the level that cannot close through" (levelstory.js header); 15m completed closes only |
| A5 LVN / nodes | Sim desk / Live Aid | NOT DOCUMENTED: no desk study for LVN; the BTC thin-zone test (E34) exists only as RESULT + results/btc-thin-zone-and-breakdown-retest-prereg-1112.json (Families tab card) | - |
| A6 Trade build | Sim desk | in tom_vp or fabio_v3 study change stop_atr, target = R with target_r 2.0, fee fields, slippage box (default 0.02% OURS) and rerun; use "Compare" | fee share of the loss is the point: guided session step 1: "this rule loses N R per trade, M of it fees" (GUIDED_SESSION_PLAN s3). Management (BE move, trail, adds): not on the desk (fabio_v3.py header lists "break-even moves (manage.py)" as left out) |
| A7 Session | Sim desk | Study = fabio_v3, model = C (IVB) or B, NY window 13:30/14:30 UTC + 390 min; read breakdown "4-hour UTC block" | C m15 f0.5% +0.062 R n 518 NOT ENOUGH DATA; B N60 -0.448 R n 155 FAILED. Conditions panel "UTC hour window" for any study |
| A8 Swing | none | NOT DOCUMENTED (pre-reg only) | - |

### G.2 Guided session (60-90 min, one idea, Sonnet guide + operator clicks)
Six steps (GUIDED_SESSION_PLAN_2026-11-10.md s3): 0 open desk, 1 one run (filled trades, mean net R, share of loss that is fees), 2 where it loses (worst/best cell with >= 30 trades), 3 look at 5 worst + 5 best trades and tag them (trend against, no level, late entry, news hour), 4 one filter with the expectation written BEFORE the run, 5 verdict (PARK / NEEDS DATA / CANDIDATE: >= 0.25 R, >= 30 trades, above luck line), 6 write 5-line note. Item 4 on its watch list is "Tom/Fabio 5m and 15m census" (s7). Not documented: any Tom/Fabio concept-by-concept walk-through beyond this generic plan.

---------------------------------------------------------------------------------------------------------------------------------------

## H. GAPS (concept vs implementation), ranked

| Rank | Gap | Concept | Why it matters | Evidence |
|---|---|---|---|---|
| 1 (TOP 3) | No real footprint / delta at the level in any decision test. Census klines have delta = 0; DAX CFD delta 0; v3 footprint exists only from 2024-12 and its models almost never fire; live footprint writer stopped 2026-10-03; Legend cross-check pending | A4 (Fabio's whole trigger) and Tom's "proof" | The traders choose entries by order flow; we measured candle shapes. Absorption at a first-touch HTF level with a fast reclaim is exactly what the census could not see | POSTMORTEM C5b; AC:604,620,636; REPORT.md DAX; edge_hunt PLAN.md:28; footprint_12h_1112/CHECK.md |
| 2 (TOP 3) | Payoff shape and management never replicated: 30-40% hit at R >= 3, BE-fast, aggressive trail, adds from profit. No engine executes adds; census used 1R/24-bar; stops 5-8x wider (v3 f 0.3-0.5%) or >= 40 bps fee gate vs his 0.014-0.061% | A6 | The right-tail R is cut in every test; fee gate may drop the traders' real trade. Counter-evidence: Fable 2R/3R still -0.035/-0.023 R, and node+BE still -0.11 R, so this alone may not rescue it | POSTMORTEM s1 C1b, s2 Target/Management; v3/README.md:39; E22c, E23 |
| 3 (TOP 3) | Context frame wrong: no cash-session / NY-session value area on BTC in any test; UTC-day levels; session absent from census (12-16 UTC worst); HTF ladder used for sizing only; phase not split (7y pool averages trends and ranges); entry at market instead of limit/pullback | A1, A2, A7 | Tom/Fabio fade in balance and join in trend; pooled sample mixes both. prior_ny_session_profile exists but is untested | REVIEW_FABLE.md a (session cells), POSTMORTEM s2, s3, s4 "Phase-first" |
| 4 | Fabio v3 over-gated: S1 balance holds in 3.1% of 1m windows; Models A and D have 0 OOS days; 0 of 8 grid rows SOURCED; 25% retrace "not in transcripts" | A4, A5 | engine deaf; results rest on 1-2 trades per model | SETUP_REVIEW.md s3, E16 |
| 5 | Java VAL short has a direction but no setup type (determineSetupType returns null for shorts at val zones :482); VAH health check removed instead of made symmetric; LVN computed but unused; no acceptance logic | A3, A5 | breakdown-continuation shorts (Tom's accepted-below-value) cannot become candidates | REVIEW_FABLE.md c J1/J2; CONCEPTS.md G findings 3-4 |
| 6 | Labels: acceptance 6 bars labelled SOURCED (is OURS, half the 2x30m sourced duration); "77%" misread as win rate; "Dalton 80%" is 44% on BTC; mostly-unlabelled thresholds; FORMULAS.md has no s28/29 independent re-derivation basis for some parts | A3 | wrong anchor carried into the census; 4 reviewers checked arithmetic not method | POSTMORTEM s1 C7-C10; REVIEW_FABLE.md defect cards |
| 7 | Slippage mismatch: FORMULAS.md s13 says 2 bps RT, code default 4 bps; funding omitted (fee_r understated ~20%) | A6 | direction favours strategy, so no-edge stands, but numbers are not exact | CENSUS_5M15M_1109.md Notes; REVIEW_FABLE.md b |
| 8 | Date hygiene: most Tom/Fabio numbers on VALIDATION/HOLDOUT era; HOLDOUT 2025-07+ spent for VP level-touch + Fabio OF families; Tom DAX never run with order flow | all | no clean fresh window left for those families | SETUP_REVIEW.md s0, s4 |
| 9 | Tom swing method untested; trendline_core.py has 3 FIX-FIRST gaps | A8 | the only Tom method with fee-friendly stop geometry | tom_swing PRE_REG.md s4 |
| 10 | Cross-guidance Tom <-> Fabio not wired by design; no pair tracking of agreement; Bollinger/RSI/OI/L-S inputs have no source from either trader | D | no data on whether agreement helps | GUIDANCE_AUDIT.md gap list |

TOP 3 FIDELITY GAPS: (1) order flow never read at real per-price level (footprint/delta absent from all decision tests); (2) payoff + management shape (R>=3, BE/trail/adds, tiny structural stop) not replicated; (3) wrong context frame (no NY-session profile, no session/phase split, ladder never a gate, market entry vs limit).

---------------------------------------------------------------------------------------------------------------------------------------

## I. KEY NUMBERS CHEAT-SHEET (for slides; every number from a file above)
| Number | Meaning | Label |
|---|---|---|
| 0 / 48, 0 / 20, 0 / 186 | streams / cells / matrix cells beating null (vp_pivot_probe, tom_vp, Q33) | OURS result |
| 10 bps | BTC perp round-trip taker fee | SOURCED (fees.py) |
| 1.22-2.76 R | fee per trade at 5-8.2 bps stops | OURS arithmetic (AUDIT root cause 1) |
| +0.079 -> -1.423 R | Fabio plan-stop gross -> net (balance_fade, all, mkt) | OURS (RESCORE.md) |
| 3.1% | share of 1m windows where Fabio v3 S1 balance holds | OURS (v3 B141) |
| 12 IS / 0 OOS | Model A trade days | OURS |
| -0.1038 R/day | v3 Model C OOS (79 trade days), CI -0.2087..-0.0053 | OURS |
| 57.2% vs 46.8% | return-to-POC real vs placebo, n 871 | OURS count; his claim 70% SOURCED |
| 44% | Dalton 80% rule on BTC, n 493 | OURS |
| 77% | accepted below VAL then half-VA-width lower same day, n 300 (NOT a win rate) | OURS descriptive |
| -0.087 R | auction census 1h, 7y, gate-pass n 1,871, SE 0.022 | OURS |
| -0.106 R / -0.358 R | 15m H1 Deribit / taker, n 1,484 | OURS |
| 30-40% at R > 3 ; 1 : 4.5 ; 30-35% | traders' stated hit rate / payoff | SOURCED (TOM-091; Is1HvdfQm5c:144-145,245) |
| 0.014-0.061% | Fabio NQ stop as share of price | SOURCED (measured from his videos) |
| 70% | value area share | SOURCED (TOM-277) |
| 18% vs 27% | b99 absorption reversal vs baseline, n 2,175 | OURS descriptive |
| 49% | Live Aid level-story ideas right, n 2,852 | OURS descriptive |
