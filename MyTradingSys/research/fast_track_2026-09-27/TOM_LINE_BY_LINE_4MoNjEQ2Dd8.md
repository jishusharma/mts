# TOM LINE BY LINE - 4MoNjEQ2Dd8 ("$2,350 in 40 Minutes"), plus why alerts are one shape and never long

Opus analyst, 2026-09-30, cloud sandbox (repo + internet only; no F: drive, no live logs beyond what is committed, no exchange).
Read only on code. Nothing in execution/, layers/alerts/ or DSA_SESSION_PROMPT.md was touched. Scratch proofs:
`scratchpad/opus_tom/{asym.py,shape.py,enum.py,parse_lm.py}` (session scratch dir, not in repo).
Abbreviations: MDS = src/main/java/datafeed/MarketDataSnapshot.java, SCB = src/main/java/datafeed/SetupCandidatesBuilder.java,
V = MyTradingSys/backtest/verdict.py, MOB = MyTradingSys/runtime/math_object_builder.py,
STD = scripts/core/start-trading-day.ps1 (live Compute-Verdict and popups), CE = MyTradingSys/runtime/compiled_engine.md.

## 0. Direct answer

1. Backtest "all 19 SETUP_FORMING are short" is a data bug, not Tom. Archive snapshots write `bid_ask_ratio = 0.0` (MDS:1169).
   MOB:389 reads it as book imbalance 0.0 and MOB:402-403 flags every LONG top candidate "ask-heavy vs LONG" (0.0 < 0.33).
   V:122-123 then turns proof 5 into WATCH. A short is only contradicted above 3.0, so shorts pass. At WATCH level the same
   run has 2450 long vs 2399 short signals (TOM_CORE_BT.md:299-300), so the candidate stage is symmetric. Reproduced below (A2).
2. Live has the same trap whenever the depth fetch fails (MDS:213-214, ratio defaults to 0.0). But live longs do happen: the
   committed live log runtime_data/live_monitor.txt (2026-09-19 23:18 to 09-20 09:31) has 24 long and 12 short SETUP_FORMING rows.
3. TWOPEAK is computed on almost every day. MDS:570-578 compares the POC bin with the second-highest bin, which is usually
   the bin next to the POC, not a second peak. It is printed as `STATE:` on every verdict line and alert card (STD:155, 265, 278).
   STATE changes also fire popups (STD:559-569, 628). So most popups read "TWOPEAK/...". Synthetic days: 60/60 TWOPEAK. Live log: 577/577.

---

# PART A - How a Tom alert is produced, and where longs and shapes die

## A1. Pipeline, end to end (file:line)
| step | what happens | file:line |
|---|---|---|
| 1 snapshot | daily/weekly/4h VP (poc/vah/val/shape, hvns/lvns for daily), VWAP + bands, CVD slope (rising/falling/flat only), trade flow, swings, book ratio | MDS:143, 486-616, 618-656, 658-700, 200-214 |
| 1a conditions | price_vs_va, price_vs_poc, vp_shape, vwap_slope, cvd_slope | MDS:283-297 (live), 1107-1111 (archive) |
| 2 state | balance / trend_healthy only (see A2.d) | SCB:263-281 |
| 3 directions | above_vah: short+long; below_val: long only; in_va: side of POC | SCB:283-303 |
| 4 zones | weekly/daily/4h VP, VWAP + bands, prior day, 1h/15m/5m swings, FVG, naked POC | SCB:305-391 |
| 5 tier | trigger_ready <= 0.1%, conditional <= cap, else dropped | SCB:66-75, 428-437 |
| 6 setup type | zone x direction x state | SCB:439-474 |
| 7 stop | swing of mapped TF, else 0.2% fallback; floor 0.1% resets to 0.2% | SCB:111-124, 476-483 |
| 8 target | nearest VP level / prior-day extreme / VWAP in [2.0, 3.5] x risk, else candidate dropped | SCB:126-175 |
| 9 R:R | net = gross via ExecutionMathConstants; keep gross >= 1.5 | SCB:177-196 |
| 10 proofs | 7 one-minute proofs; count | SCB:547-567, 624-822 |
| 11 rank | score = 50 + 7 x proof + confluence; top 3 kept | SCB:211-257 |
| 12 proof direction | contradiction if FA / book / last_3_delta oppose top candidate | MOB:383-407 |
| 13 verdict | WAIT_RR / WAIT_FAR / WAIT_TRIGGER / WAIT_PROOF / WATCH / SETUP_FORMING, then 4 downgrades | STD:150-256 (live); V:65-139 (port) |
| 14 popup | fires on 2-cycle-confirmed verdict change to SETUP_FORMING, or STATE / ADVERSE / STOP / TARGET NEAR | STD:532-569, 623-629 |
| 15 card | VERDICT, WHY, STATE (= vp_shape/price_vs_va), SETUP, ZONE, ENTRY=zone price, STOP, TARGET, proofs | STD:269-318 |
| 16 trade | auto_trader parses card; side from setup suffix; needs SETUP_FORMING/CONFIRMED, net >= 2, ordered stop/entry/target | MyTradingSys/execution/auto_trader.py:103-160 (read only) |

## A2. Q1 - Which paths can produce a long, and what kills them

**a. Reachable setup types.** I enumerated SCB:263-303 and :439-474 over every combination of price_vs_va, price_vs_poc,
vwap_slope and cvd_slope that MDS can emit (enum.py):

| price location | reachable setup types |
|---|---|
| in_va, above POC | ct_short, scalp_short |
| in_va, below POC | ct_long, scalp_long |
| above_vah | ct_long (VAL/swing low), tc_long (VWAP), ct_short (prior_day_close only) |
| below_val | ct_long, tc_long - **no short of any kind** |

- The branches at SCB:446 and :449 are not bugs. They are the side mapping: VAH/swing high gives a short and VAL/swing low
  gives a long.
- The asymmetry is elsewhere:
  - `tc_short` does not exist (SCB:464 has only `tc_long`).
  - below_val emits only longs (SCB:290-291). So in a breakdown the engine offers longs into a falling market. Two downgrades
    then kill them: V:129-130 ("broken below_val + CVD falling vs LONG") and V:133-137 (flow contradiction).
  - above_vah emits shorts only at prior_day_close. The VAH branch returns null in trend_healthy (SCB:445), and
    above_vah is always trend_healthy.
- Net effect: longs are structurally available in-value and in uptrends. Shorts are missing in downtrends. This does not
  explain "no longs" by itself.

**b. The long-killer (backtest, proven).**
- Archive snapshots set `order_book_depth.bid_ask_ratio = 0.0` (MDS:1169). SCB copies it into the proof JSON (SCB:619, 819).
- countSignals skips 0.0 correctly (SCB:561).
- MOB:389 reads that 0.0 as a real ratio. MOB:402-403 marks every long top candidate "ask-heavy vs LONG".
- V:122-123 caps proof 5 at WATCH. Shorts are contradicted only when the ratio is > 3.0 (MOB:395), so 0.0 never touches them.
- Synthetic test (asym.py): identical candidates, proof 5, net 2.5, trigger_ready, last_3 mixed:

| book | dir | proof_dir | verdict |
|---|---|---|---|
| 0.0 (archive / failed fetch) | long | contradiction | WATCH (proof 5 contradicted) |
| 0.0 | short | aligned | SETUP_FORMING |
| 1.0 | long | aligned | SETUP_FORMING |
| 1.0 | short | aligned | SETUP_FORMING |

- This also explains TOM_CORE_BT_REVIEW H1: the 301 lost proof-5 rows must include every long.
- TOM_CORE_BT.md:6 says the missing book "never counts". It also actively vetoes longs.

**c. Live.**
- MDS:213-214 sets the ratio to 0.0 when the depth call throws or ask depth is 0. The same veto then applies to longs.
- The committed log shows the book at 0.0 is not constant live. Of 607 snapshot blocks in live_monitor.txt:
  - 44 have a book < 0.33
  - 131 are in 0.33-0.67
  - 218 are in 0.67-1.5
  - 128 are in 1.5-3
  - 78 are > 3
- 577 unique verdict lines (parse_lm.py):

| verdict | long | short |
|---|---|---|
| SETUP_FORMING | 24 | 12 |
| WATCH | 129 | 85 |
| WAIT_RR | 116 | 132 |

- proof_dir contradiction: long 113 of 304, short 149 of 273.
- So in that window the engine produced longs. The operator's "no longs" must be checked against the desktop apparatus log (A4).
- The popup gate needs a verdict to repeat on 2 cycles (STD:534-541). SETUP_FORMING flickers with proof 4/5. Only 2 long and
  2 short SETUP_FORMING episodes lasted 2 or more cycles in that log. So longs rarely reach a popup, and shorts rarely do either.

**d. Dead code that is not side-specific.**
- classifyState tests cvd_slope == "divergent" / "aligned" (SCB:277, 279). buildCvd emits only rising/falling/flat (MDS:681-688).
- So trend_unhealthy is unreachable, and POC zones never become setups (SCB:451-457).
- CE:38-46 already admits that only balance and trend_healthy are reachable.

**e. Proofs are mostly direction-blind.**
- absorption (SCB:694-718), delta_flip (:737-765), volume_spike (:767-779) and cvd_aligned (:804-816) count the same for
  long and short.
- cvd_aligned means "CVD slope agrees with 1m delta", not "flow agrees with the trade".
- Only finished_auction and book are directional (SCB:551-566).
- So proof 5 is mostly "activity at the zone", and the side comes from a single price-vs-VA lookup (SCB:283-303).

## A3. Q2 - Why the label is always TWOPEAK
- MDS:570-573 sets `secondPeakVol` to the largest bin value below the POC bin's value, anywhere in the profile. The profile is
  triangular-weighted over 50 or more bins of about $5 (MDS:524, 538-547), so the bin next to the POC is almost always > 0.6 x max.
  MDS:578 then returns TWOPEAK.
- D and P are reachable only if the second-largest bin is < 60% of the POC bin. That practically never happens.
- A port of MDS:508-587 (shape.py), 20 synthetic 1440-bar days each:
  - balanced day: 20/20 TWOPEAK, second-bin/max 0.92-1.00
  - trend day: 20/20 TWOPEAK, 0.90-1.00
  - two-distribution day: 20/20 TWOPEAK, 0.84-1.00
- Live log: 577 of 577 verdict lines read TWOPEAK (492 in_va, 58 below_val, 27 above_vah).
- Other shapes are computed but meaningless:
  - "P" covers both P and b (MDS:586 uses ratio outside 0.8-1.2 in either direction).
  - No b or Tom-B is emitted (CE:332).
  - regime_classifier.py:31-32 treats "D" as a DOWN vote, but in MDS "D" means balanced.
- The label is always printed:
  - `$state = "$($cond.vp_shape)/$($cond.price_vs_va)"` (STD:155) is in every verdict line (STD:265) and card (STD:278).
  - A state change is a popup reason by itself (STD:559-569, 628).
  - Since vp_shape never changes, every STATE popup is a price_vs_va flip written as "TWOPEAK/in_va -> TWOPEAK/above_vah".
- CE:30 maps TWOPEAK to "Balance", so docs that read the card see a balance market every day.

## A4. Q3 - Minimal diagnosis on the desktop (read-only counts)
1. **Archive, F: tom_snapshots.** For every snapshot whose top candidate (rank <= 3) has proof_count >= 5, log the verdict
   after each gate in V:110-137. Tabulate reason x direction. Also count `order_book_depth.bid_ask_ratio == 0.0` and
   `proof_direction_details` containing "ask-heavy vs LONG".
   - Expected: 100% of archive rows have ratio 0.0, and every long proof-5 row carries "book_imbalance=0.0 ask-heavy vs LONG".
2. **Same rows, counterfactual.** Treat book as absent when `order_book_depth.confidence == "LOW"` or the ratio is 0.0.
   - Count long vs short SETUP_FORMING.
   - Pass: longs become non-zero and about as common as shorts.
   - This is the test for a fix in MOB:389-405. Do not edit MOB in place (the live loop imports it via build_mo_cli.py).
3. **Live apparatus_log.txt, parsed by '|' fields (never with cut or head).**
   - Count verdict x setup suffix (_long/_short).
   - Count `pd=contradiction` by direction.
   - Count "ALERT #" lines by reason class (verdict / STATE / ADVERSE / STOP NEAR / TARGET NEAR / price).
   - Count popups whose verdict is SETUP_FORMING by direction.
   - Expected: most popups are STATE changes; long SETUP_FORMING exists but is rarely confirmed on 2 cycles.
4. **Live snapshots.** Count `bid_ask_ratio == 0.0` (failed depth fetch) and the share of long top candidates that
   happen at that moment.
5. **Shape.** Across F: snapshots, count conditions.vp_shape values (expected about 100% TWOPEAK).
   Log the ratio of second-highest bin to max next to it. A real second peak needs a local maximum separated by a valley
   (for example a smoothed profile with 2 local maxima and a trough below 0.7 x the smaller one). That is a spec task for FORMULAS.md
   first, not a code edit.

---

# PART B - One Tom transcript, line by line: 4MoNjEQ2Dd8

## B0. Why this one
- It is one live session with continuous commentary (22,120 characters, one line in raw_transcripts_canonical/4MoNjEQ2Dd8_raw.txt).
- It is a LONG, the side the engine never delivers.
- It shows every trade phase: entry at a location before the reaction, stop, target, retest, adds, three to four partials,
  structural stop moves, and a discretionary exit.
- yRvMW6lgN1o (done) is a set-and-forget short. This one is the managed long, so the two cover each other.
- MISSING_PIECES skipped it for length.
- Other candidates:
  - kXhIAug0Gh8 is a stop-placement lecture around one losing long (9 KB).
  - k0zm5NYn0IQ is a short thesis.
  - RwQBdF9TSvc is conceptual.
- Instrument is not stated.
  - The extract asserts DAX from the ~25,600 levels.
  - The transcript names the NASDAQ twice, once as the market that "will keep running", and uses the S&P as a comparison.
  - Unresolved here. All distances below are in ticks as Tom states them.
- The transcript was machine-translated (Tom says so), so single words ("covered", "bid", "82", "16") can be wrong.
  Decisions are read from sequences, not from single words.
- No timestamps: position = % through the text, and GPS = thirds.

## B1. Running log (every passage, in order)
Pos = % of the transcript. Eng = does our engine have it: Y (yes), P (partial), N (no). Fragments in quotes are verbatim.

| # | pos | Tom looks at | decision | information used | Eng (where) |
|---|---|---|---|---|---|
| 1 | 0-3 | intro, "I translated this video with AI" | none | - | - |
| 2 | 3 | a "wonderful price area" | ENTRY LONG already placed or taken; stop "below the last low"; TP "above the highs" | location, last swing low, prior highs | location P (SCB:305-391, no such zone type); stop Y (SCB:115); TP above highs N (SCB:127-147 has no swing highs or equal highs as targets) |
| 3 | 3-4 | "a beautiful ledge" at the top | target rationale: liquidity above equal highs will be taken | equal-highs liquidity | N (zone_identification_rules.md:534 lists it as a gap) |
| 4 | 4-6 | "rejection", "liquidity at the top"; yesterday's profile: tail, back into value, rejection at POC, pullback | thesis for the long | prior-day profile shape, open vs value, re-entry into value, POC reaction | prior-day levels Y (SCB:327-330); tail / open location / re-entry N |
| 5 | 6-7 | "the value high up here" (around 644) | target = value high / ledge | VAH | Y as a level (SCB:139-143), but the target window [2.0, 3.5]R (SCB:150-151) decides, not Tom |
| 6 | 7-9 | "very large riskreward ratio", "nothing to do" | wait; no management in the dead zone | R:R | Y (SCB:177-184) |
| 7 | 9-10 | absorption at the bottom, "aggressive buying keeps happening" | hold; proof arrives AFTER entry | absorption, aggressive market buys at the level | P (SCB:694-718 absorption is 1m and direction-blind); timing inverted: V:116-121 needs proof 5 BEFORE any entry |
| 8 | 10-12 | dynamic view: today's POC above; volume below and above, "empty space" between | expect a move through the gap while the lower volume holds | HVN / LVN layout, today's POC | hvns/lvns computed (MDS:143, 594-613) but unused by SCB and MOB; N as logic |
| 9 | 13-14 | "once again, we're at the level and buying aggressively"; S&P "holding its ground", buying tails; "above the PC and power is coming in" | retest confirms; POC reclaimed | retest, intermarket, POC reclaim | N (no retest counter, no intermarket, no POC-reclaim state) |
| 10 | 14-16 | switch to 1-minute; add plan | ADD planned "at the breakout" if speed is kept | speed, breakout level | speed computed but not counted (SCB:559, 781-802); adds N |
| 11 | 16-18 | "below the business zone", "4:1" | stop confirmed structurally | business-zone low | P (swing low only) |
| 12 | 18-21 | "still below the absorption volume here" | the level above (absorption volume) is the breakout trigger for the aggressive part | where volume was absorbed | N (absorption is a boolean at the zone, not a price level) |
| 13 | 21-24 | order book: "big order at 25,600"; room to 644 / 640, "careful" there | waits; marks 600 as step, 640 as caution | resting large orders, VAH | N (only bid_ask_ratio within 1%, MDS:200-214) |
| 14 | 24-25 | "this step I just mentioned with the big order. And boom" | big order taken = go | order consumed | N |
| 15 | 25-27 | volume pumped in "but it's being absorbed", "still a seller here" | REJECT scalper exit; plan first partial at value high 640 | absorption against him, trader type | N (no partial logic) |
| 16 | 27-30 | recap of business-zone construction; "momentum is fading"; "the long side is still to be favored"; volume at top = accepted | HOLD | sequence open, crash, back in, acceptance, pullback, confirmation | N as a sequence |
| 17 | 30-34 | "what happens if the market drops below that level"; low volume area; scalpers out; "we wait" | HOLD as intraday swing / breakout trader | LVN, trader type | N |
| 18 | 34-36 | "Liquidity is coming back in", "The 600 is being cleared again", buyers pile in, sellers above | HOLD | flow at the step | P (delta only) |
| 19 | 36-37 | "100 ticks risk. We've got 161 on the clock" | open profit = 1.6R | risk vs open P&L | N (no open-R tracking in engine) |
| 20 | 37-39 | countdown; "Big order. This time it's the 620"; needs "a closing price" | HOLD if the bar closes above, else "close out one contract" | 620 order, bar close | N (no close-conditioned management) |
| 21 | 39-42 | "we're above the high"; selling but buyers dominate; S&P | hold "above this level", else close | reaction above the high, intermarket | N |
| 22 | 42-46 | "Another nice order at the top"; "too much rotation up there" | PARTIAL 1 (~$1,200); stop left in place | rotation near the top, orders | N |
| 23 | 46-51 | why he holds: range held + LVN; liquidity decreasing where he sold; 620 and 600 = large-order levels | invalidation = below 600-620 ("game over") | order levels as stop reference | N |
| 24 | 51-55 | "We now adjust our stop"; below = back in today's value; above = "out of control" | STOP MOVE 1 to below the step | today's VA, accumulated liquidity | today's VA Y (MDS:283-288); stop logic N (MTS_USER_GUIDE.md:151 forbids trailing) |
| 25 | 55-57 | back at 620; S&P "still hasn't taken out the tops"; "closed above here" | HOLD | intermarket lag, close above | N |
| 26 | 57-62 | lesson: stop only where "the opposite" is expected; personality; "swing high at 82"; NASDAQ | stop rule; "we won't lose anything" | invalidation-based stop | N; CE:679-696 (12.10) is CryptoCred-sourced, not Tom |
| 27 | 62-64 | "taken profits twice now" | PARTIAL 2 (not narrated separately) | - | N |
| 28 | 64-68 | LVN being filled; "last buying area ... As long as that holds, it's not critical"; delta decreasing | REJECT adding in the LVN; invalidation = below last buying area | LVN, last aggressive-buy area, delta | N |
| 29 | 68-70 | "no reason to sell"; above 620 "cool", below may test 600 | ADD 1: "buying yet another significant position" | steps 600/620 | N |
| 30 | 70-74 | "our last position now ... all or nothing"; "broke through liquidity ... on the downside and now wants to move back up"; "stop-loss is really tight" | ADD 2 (last); binary thesis | sweep below, fair prices above, tight stop | N |
| 31 | 74-77 | S&P at its volume step, NASDAQ aggressive; conditional partial; absorption; "above 660" | ready to close a short-term piece if the S&P fails its step | intermarket step | N |
| 32 | 77-80 | "attack on the 59", aggressive selling; speed low; 5-minute close | PARTIAL 3: "take a few ticks off" at 620 | 5m close, speed | N |
| 33 | 80-84 | "can't lose anything anymore"; lesson: order book, absorption, big orders; above 620 "sky's is the limit" | HOLD runner | - | N |
| 34 | 84-85 | "placed an order too early" | admitted error (add order before the breakout) | - | - |
| 35 | 85-89 | 15-minute close; higher-TF level from yesterday not made; big order above; back at 620, selling | HOLD, watching the higher-TF close | 15m close, prior-day high area | N |
| 36 | 89-91 | "now it's 1845", no higher closes | time-of-day pressure on the thesis | clock, closes | N (session_timing exists in the snapshot; no management use) |
| 37 | 91-95 | trail: last significant 5m volume at 603 | STOP MOVE 2 to 603 | 5m volume by price (last HVN on the 5m profile) | N |
| 38 | 95-96 | "118 contracts ... a big order and it just ate that up"; speed up; "take out another position" | PARTIAL 4 (wording ambiguous) | order consumed, speed | N |
| 39 | 96-98 | stop "below the last trades price area 16"; "Last attempt" | STOP MOVE 3; time limit on the runner | last traded area | N |
| 40 | 98-100 | "Speed Off", "being sold off", "I'm out"; $2,360; lunch break | EXIT on speed fade at the top; end session | speed, time of day | N |

## B2. Verbatim anchors (checked with verify_extract_quotes.py)

> "Here we have a wonderful price area where I'm looking for a long entry and that's why I'm now The stop loss goes below the last low here and my take-profit is set above the highs."
**Source GPS: 4MoNjEQ2Dd8 | BEGIN**

> "Because up here, we've formed a beautiful ledge and I expect the market will take those out."
**Source GPS: 4MoNjEQ2Dd8 | BEGIN**

> "If we look at yesterday's profile here, we formed a nice buying tail down here after the market opened, then moved back into value, saw rejection at the PC, and are now making the pullback."
**Source GPS: 4MoNjEQ2Dd8 | BEGIN**

> "here you can really see nicely how the market was absorbed at the bottom. And the question now is will it hold this level or break down through it."
**Source GPS: 4MoNjEQ2Dd8 | BEGIN**

> "there's volume down here and there's volume up there. In between there's a bit of an empty space and as long as we hold these volumes here for me, the probability is there that the market can shoot upwards."
**Source GPS: 4MoNjEQ2Dd8 | BEGIN**

> "If we continue to move steadily up and carefully maintain the current speed, I'll add to the position again at the breakout."
**Source GPS: 4MoNjEQ2Dd8 | BEGIN**

> "Stop loss as mentioned below the bid below the business zone."
**Source GPS: 4MoNjEQ2Dd8 | BEGIN**

> "So, there's still a seller here at 25,600. You can see that really well for the scalpers. Now would be the right time to exit. But I don't want to scalp."
**Source GPS: 4MoNjEQ2Dd8 | BEGIN**

> "The market opened lower, then crashed down, came back in, formed acceptance, then made a nice pull back to the business zone. And here it confirmed it again and showed us that there are aggressive buyers."
**Source GPS: 4MoNjEQ2Dd8 | BEGIN**

> "Right now, you can already see 100 ticks risk. We've got 161 on the clock."
**Source GPS: 4MoNjEQ2Dd8 | MIDDLE**

> "up here we absolutely need to get a closing price now. then I'll keep the position. Otherwise, I'd just close out one contract right away"
**Source GPS: 4MoNjEQ2Dd8 | MIDDLE**

> "So, let's close out a position. We're happy with that. We'll leave the stop loss down here for because I just saw that there's too much rotation up there."
**Source GPS: 4MoNjEQ2Dd8 | MIDDLE**

> "Those were the two price levels where I saw large orders sitting down here. Sorry here exactly 620 and 600."
**Source GPS: 4MoNjEQ2Dd8 | MIDDLE**

> "I moved the stop loss to a price range where I simply expect the opposite of my long position. And before that, it doesn't make sense to move the stop-loss."
**Source GPS: 4MoNjEQ2Dd8 | MIDDLE**

> "we won't lose anything here anymore even if the market stops us out."
**Source GPS: 4MoNjEQ2Dd8 | MIDDLE**

> "we're in the low volume area. That means it's doing nothing other than filling this empty price area with liquidity now."
**Source GPS: 4MoNjEQ2Dd8 | MIDDLE**

> "Here we're buying our last position now and just saying all or nothing. Either it breaks out upwards now or it turns around and it's over."
**Source GPS: 4MoNjEQ2Dd8 | END**

> "I see here that the last time there was significant trading volume on the 5-minut chart was at 603. And if it drops below that, things will break down, of course."
**Source GPS: 4MoNjEQ2Dd8 | END**

> "I'm moving my stop loss up now below the last trades price area 16."
**Source GPS: 4MoNjEQ2Dd8 | END**

> "Now it's being sold off again for now. That's why I'm out now, I think."
**Source GPS: 4MoNjEQ2Dd8 | END**

## B3. Trade block (reconstruction)
| field | reading |
|---|---|
| state (day) | Opened lower, below the prior value. A buying tail formed after the open, price moved back into value, was rejected at the POC, and is now pulling back. Today's POC is above price. |
| location | The "business zone": where price "formed acceptance" after re-entering value, above the buying tail. Tom names no VP number for it. |
| side | LONG |
| leading signal | Re-entry into value after a failed move lower (buying tail), plus the pullback |
| trigger / entry | In at the location BEFORE the confirmation (passage 2). Absorption and aggressive buying are then observed at the level (7, 9). |
| order type | not stated for the entry. Adds are orders at the breakout ("placed an order too early", 34). |
| initial stop | "below the last low" / "below the business zone" (2, 11). About 100 ticks at passage 19. If NQ (0.25 tick): 25 pts, about 0.10% of 25,600. If FDAX (0.5): 50 pts, about 0.20%. Inference, not stated. |
| target | "above the highs" / the ledge, and the value high around 640-644. "4:1" (11). Liquidity-based, not the nearest level in a window. |
| management | Partials at resistance/rotation (22, 27, 32, 38). Stop moved only to a level where "the opposite" is expected: the 600-620 order/volume step (24), then 603 (37), then the last trade area (39). Adds only after the steps hold (29, 30), never in the LVN (28). Every hold is phrased as "as long as" some level holds. |
| exit | Runner closed when speed died at the top ("Speed Off", 40). The lunch break ends the session. |
| rejects | Scalping the first resistance (15). Adding in the LVN (28). Moving the stop before an "opposite" level exists (26). Holding without a close above the step (20). |
| information sources | Prior-day and today's profile (tail, value, POC, VAH), HVN/LVN, order book large orders (600, 620, 118 contracts), delta/aggression, absorption, market speed, 1m/5m/15m closes, S&P and NASDAQ, clock |
| outcome | "$2,360" claimed. Risk in money is not stated, so R is unknown. Open profit 1.6R at passage 19. |
| horizon | intraday swing / breakout, about 40 min |

## B4. How the existing extract captured it (extracts/fresh/extract_4MoNjEQ2Dd8_fresh.md)
**Dropped**
- The ORDER of events. Entry at the location comes first, then proof. The rule table cannot say that he entered before the proof, which is
  the single biggest contradiction with V:116-121.
- The chain of "as long as" invalidations. Each hold has a price condition (volumes held, above 600/620, above the last
  buying area, above 603). They appear as scattered codes, never as the stop-management rule.
- The rejections of passages 15, 28 and 26 as decisions. 3.3 keeps one fragment with "[add/scalp prematurely]" guessed.
- The day-state sequence (open below value, tail, back into value) as the trigger for a LONG, and the POC reclaim (passage 9).
- Three of the four partials and both stop moves after the first, as dated steps.

**Distorted**
- T1.4 "Order Book Reading for Target Projection". The 600 order was a SELLER to be absorbed ("still a seller here at 25,600"),
  then a step, then the stop reference ("large orders sitting down here"). It is a management level, not a target projector.
- T3.2 reads 161 as potential reward. It is open profit "on the clock" against 100 ticks risk.
- Section 5 puts the 603 trail (passage 37, at 92%) before the adds (passages 29-30, at 70%).
- GPS tags are wrong for 5 of 7 quotes I checked:
  - "absorbed at the bottom" is at 10%, tagged MIDDLE.
  - "business zone was constructed" is at 29%, tagged MIDDLE.
  - "moved the stop loss ... opposite" is at 58%, tagged END.
  - "low volume area ... filling" is at 66%, tagged END.
  - "trading personality" is at 59%, tagged END.
  - The verifier reports 35 NO-GPS lines (format), so these were never machine-checked.
- Asset "DAX" is stated as fact. The transcript never names the traded instrument, and it names the NASDAQ.
- Gap 7.12 says the trade has no IDEA + PROOF. It has both: idea = the prior-day profile story, proof = absorption and
  aggressive buying at the level.
- conditions/entry_timing_triggers.md:250-270 files it as TC Trigger A with "Trend established (VWAP trending, VPOC
  trending)". Tom never says trend. It is a return-into-value long after a failed move lower, and our CT/TC/BO/scalp taxonomy has
  no slot for it.

**Atomized**
- 45 in-vivo codes and 27 tier rules, each carrying one quote.
- The setup is spread over T1.1, T1.2, T1.3 and codes 8-12.
- Management is spread over T1.5, T1.6, T1.8, T1.11, T4.5 and T5.2.
- No row can be implemented alone, and no row says when it applies.

**What the pipeline did with it**
- The concepts reached conditions/ as prose: ledge at setup_type_rules.md:411-416, partial on rotation at
  risk_protocol.md:394-400, volume step flagged as undefined at zone_identification_rules.md:535, order book as "not zones" at
  :537.
- None reached code. SCB has no ledge, business zone, tail, volume step or order-level input, and no management.

## B5. Patterns (recurring decision sequence)
**S1 - Location-first entry (both sides).**
1. Day story from the profile: open location vs prior value, tail, re-entry, POC reaction.
2. Location = the acceptance area of that story.
3. Enter AT the location with the stop behind the structure (last low, business zone).
4. Target = liquidity beyond the obvious highs or lows (ledge, equal highs), with VAH/VAL as waypoints.
5. Proof (absorption, aggressive buying) is read AFTER entry, as a hold-or-abort check.
- The mirror for shorts is the yRvMW6lgN1o sell limit "below the last volume step".

**S2 - Step ladder management.**
1. Name the next steps: order levels or volume steps (600, 620, 640).
2. Each step taken on a closing price earns a hold. Rejection or rotation at a step earns a partial.
3. The stop moves only to a step that has held, where "the opposite" is expected. Adds happen only after a step holds, never
   inside an LVN.
4. Exit when speed dies at a step, or on the clock.

**S3 - Every hold is conditional.**
- The thesis is always phrased as long as <level> holds.
- The level is the invalidation. That is the stop rule, not a separate one.

## B6. Information Tom uses that we do not compute
1. Open location vs prior value, the tail after the open, re-entry into value (failed auction). Nothing in MDS:283-297.
2. The acceptance area ("business zone") as a zone. SCB:305-391 has only fixed VP levels, swings, VWAP and FVG.
3. Equal highs/lows ("ledge") and swing extremes beyond VAH/VAL as targets. SCB:127-147.
4. Step levels from volume by price on the management TF (last significant 5m volume, 603). The daily HVN/LVN exist
   (MDS:594-613) but nothing reads them.
5. Resting large orders and their consumption. Only a 1% bid/ask ratio exists (MDS:200-214), and archive cannot rebuild it.
6. Speed as a hold/add/exit input. It is computed (SCB:781-802) but excluded from proof (SCB:559) and unused after entry.
7. Close-conditioned decisions on 1m/5m/15m bars at a step.
8. Intermarket confirmation (S&P, NASDAQ). There is no BTC equivalent in the engine. Do not invent one; mark it not portable.
9. Open-trade state: open R, partials taken, stop stage, adds. The engine is stateless per snapshot, and the plan rules are
   fixed-stop (MTS_USER_GUIDE.md:151).

## B7. Missing pieces and where each should live (proposals only; builders stage `.new`, gates first)
| # | piece | should live at | notes |
|---|---|---|---|
| M1 | book = 0.0 treated as a real ratio vetoes all longs in archive and on failed live fetches | MOB:389-405 (skip when `order_book_depth.confidence == "LOW"` or ratio == 0); MDS:213-214 (emit null + LOW on failure) | live-imported file: stage `.new`; needs a restart-state test and an API-error test (CLAUDE.md) |
| M2 | shape label is not a shape | MDS:569-587; spec first in backtest/layers/FORMULAS.md | real peak/valley test; P vs b split; stop printing shape in STATE until fixed (STD:155) |
| M3 | return-to-value setup (open outside value, tail, re-entry, pullback to acceptance), long and short | new setup type in SCB:439-474; conditions in MDS:283-297 | symmetric by construction |
| M4 | acceptance zone ("business zone") | SCB:305-391 zone list | needs a FORMULAS definition from Tom quotes (acceptance = time/volume at price after re-entry) |
| M5 | liquidity targets (ledge / equal highs, swing beyond VA) and no 3.5R cap | SCB:127-171 | also MISSING_PIECES section 2 (target window) |
| M6 | entry at location, proof as hold/abort | V:116-121 and STD:210-216 (read only here) | the verdict needs an ARMED-at-location state before proof |
| M7 | Tom's own management: partial at step rotation, stop to held step, add only after a step holds, exit on speed fade or clock | new management spec + sim.py; plan rules at MTS_USER_GUIDE.md:151 | execution/ is claim-only; the builder brief must repeat the live-system rule |
| M8 | directional proofs | SCB:547-567, 804-816 | cvd_aligned should mean flow in the trade direction |
| M9 | shorts below VAL / tc_short | SCB:283-303, 458-466 | symmetry: below_val currently emits only longs |
| M10 | trend_unhealthy unreachable (cvd_slope vocabulary) | SCB:277-279 vs MDS:681-688 | CE:38-46 already records it; needs a Tom-cited definition |
