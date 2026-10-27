# EXEC_PROVENANCE_AUDIT - Tom + Fabio execution parameters (TF4, pipeline row 1.6)

Session: MTS-2026-10-03-1444Z-CLI-BLD-tf4-execution-proven (App, Code mode, branch fast-track). Written 2026-10-03.
Read-only: no code, config, plan, HALT file or trade was touched, and the live testnet system kept running. Every number was read from disk or run this session ([disk], [run]).
Task rows: runtime/BUILD_PIPELINE.md:45 (row 1.6); research/_archive/loose_2026-10/TOM_FABIO_REVIEW_2026-10-03.md section 1.2 (table :43-52) and section 3 (:87).
Id map: audit E1-E3 = review E1-E3 (entry order type, time exit, runner at size 10). E4-E9 are further execution rows (50/50 rule, runner distance, max age, break-even, stop, target). E10 = review E5 (entry before proof). Review E4, E6, E7, E8 are not execution parameters (H6).
Verdicts, same definitions as research/fast_track_2026-09-27/PROVENANCE_AUDIT_TOM.md:5: SOURCED = a quote supports the value. CONCEPT-ONLY = the trader names the idea, the number or trigger is ours. NO-SOURCE = no idea behind it, or a role the trader never gives it.
Flags (last column): KEEP = stays as the testnet collection default (operator Rulings 1-2, OPERATOR_RULINGS_2026-10-02.md). CHANGE = a default change is proposed (Ruling 2: apply a default and flag it). MEASURE = the value should come from a pre-registered measurement (Ruling 3 accepted 2026-10-04, MEASURED label, testnet only). REMOVE@LIVE = must be sourced or removed before any live use.
Short names: AT = MyTradingSys/execution/auto_trader.py. PM = .../position_manager.py. NP = .../new_plan.py. EX = .../executor.py. PC = .../plan_compiler.py. DO = .../deribit_orders.py. CFG = .../auto_trader_config.json (live values; AT:54-77 DEFAULT_CONFIG is overridden key by key at AT:601-603). SCB = src/main/java/datafeed/SetupCandidatesBuilder.java. MOB = MyTradingSys/runtime/math_object_builder.py. PS1 = scripts/core/start-trading-day.ps1. RMD = MyTradingSys/system/runner_min_distance.json. NRF = MyTradingSys/system/net_rr_floor.json. SL = research/fast_track_2026-09-27/SUPERVISOR_LOG.md. V2/<id> = extracts/v2/tom/<id>_v2.md (decision-log row N is at line 23+N). Video ids in the table are the first three letters (yRv, kXh, 4Mo, tS6, UrZ, WSC, k0z, UOB, qLn, BVp, 0j = 0jM5Y31YJak, fZ, 8C, Faw); full ids and verbatim text are in Appendix A, location style T/<id>:<line>@<char> or :<line>-<line> as in PROVENANCE_AUDIT_TOM.md:188. Qnn are stable labels, not a count.
Live values at the time of reading (AT defaults merged with CFG, run this session): tom size_usd 10, max_loss_usd 5, hours 1.0, max_hold_bars 8, max_age_seconds 300, runner_leg_pct 50, verdicts SETUP_FORMING / SETUP_CONFIRMED / WAIT_RR. layers size_usd 10, max_loss_usd 2, stop_pct 1.0, targets "2", max_age_bars 2.0, hours 1.0, max_hold_bars 8. net_rr floor 1.25 (NRF:2). Runner min distance 0.25 (RMD:2).

## H2 ONE-PARAGRAPH ANSWER

Of 24 audited rows (19 execution parameters, 5 entry-before-proof sub-rows) 1 parameter row is SOURCED, 7 are CONCEPT-ONLY and 11 are NO-SOURCE (counts by script, H3 note). The one SOURCED value is Tom's order type: he enters with a limit order that rests at a level (Q01, Q04, Q05). The numbers that decide whether an execution lives are NO-SOURCE: the 600 s limit wait (E1b), the 8-bar time exit, which runs from 40 minutes to 32 hours depending on the zone name (E2), the 10 USD size that makes a 50/50 runner impossible (E3), the 50/50 share (E4), the 0.25 % runner distance (E5), the age limits (E6), a break-even-after-leg-1 rule that Tom's own trade contradicts (E7), and the 0.2 % stop that 8 of 9 Tom plans carry (E8b). Live counts have moved since the review: 9 Tom attempts to 15:27Z, not 6; 7 limits never filled, 2 filled, 0 were split, 0 carried break-even. E1 is the main loss: six long limits sat 0.2-55.6 USD below the market at placement, the Binance 1m data traded through only one of them, and Deribit testnet trades 12-19 USD above Binance at the three ticker reads (and at least 29-42 USD above at the two fills), a basis the zone prices do not carry. Review E5 (entry before proof) holds for 1 of 7 Tom entries in the five v2 extracts; 5 enter after proof and 1 is not stated, and all 9 live attempts came at proof 5, so the chain is not reversed. Fabio: no execution parameter has a Fabio quote for order type, time exit, size, target value or stop value; the live Fabio path is the generic layer bracket (market, 1 % stop, 2 % target, 8-bar exit, 10 USD) and v3 places no order. Fix order: E1 (basis-aware limit price, configurable wait), E3 (size 20 and a split guard), E2 (one flat time exit by config), then carry E8b to engine rows A03/A04.

## H3 AUDIT TABLE

Columns: id | parameter | code file:line | current value | quote with file:line, or NO-SOURCE | verdict | testnet default FLAG. The suffix -T is the Tom path, -F the Fabio path. There is no E5-F row: the Fabio path has no runner.

| id | parameter | code file:line | current value | quote (file:line) or NO-SOURCE | verdict | testnet default FLAG |
|---|---|---|---|---|---|---|
| E1a-T | Tom entry order type and price at the zone | AT:210-212 (`--entry limit --price` card ENTRY); PS1:317 (ENTRY = top.zone.price); PC:112-117 (BUY snaps down, SELL up, tick 0.5); EX:408-410 (placed with no post_only; DO:308 default False) | plain limit at the zone price (the level, not the market), left on the book until filled or cancelled. All 9 Tom plans on disk are `-lim-` plans | Q01 yRv:19@1211; Q04 yRv:19@10311; Q05 kXh:19@4674 (= V2/kXh:43; "placed before the touch: yes" V2/kXh:80); Q02 yRv:19@5374 (limit "right below the last volume step"). Not stated for the A1 video: V2/4Mo:25 and :84 (order type "unknown") | SOURCED (type: 2 Tom trades in 2 videos, yRvMW6lgN1o and kXhIAug0Gh8). The price = engine zone price is only CONCEPT-ONLY (Q02 names a profile level, not our zone list) | KEEP limit-at-zone |
| E1b-T | Tom limit wait before cancel; alert age at order time | EX:125 (DEFAULT_MAX_ENTRY_SECONDS = 600), EX:419-422 (deadline = min(600 s, plan validity end)), EX:453-457 (cancel at deadline); AT:336 (executor run without --max-entry-seconds, option exists at EX:541); AT:57 + CFG:17 (plan validity 1.0 h); AT:193-194 (alert older than 300 s rejected) | wait 600 s then cancel, no chase, no re-peg. An order can go out 300 s after the alert TIME, so up to 900 s from the engine's read to the cancel | NO-SOURCE. Nearest: Q03 yRv:19@5832 (rests the order and "let the market decide", no duration); Q08 4Mo:19@18589 (an order placed too early is an admitted error) | CONCEPT-ONLY | CHANGE: pass --max-entry-seconds from a config key (AT:336, key beside AT:57); value MEASURE (Ruling 3). Live: 7 of 9 attempts ended no_fill (B.1) |
Rationale (B100, 2026-10-04): the quotes above name the trader idea and the number is ours, which is CONCEPT-ONLY under the H1 definitions (line 7); the fix path is MEASURE per Ruling 3, not remove or shadow.
| E1-F | Fabio entry order type | AT:286 (layer path `--entry market`) for layer:fabio:* routed to jishu_3 (CFG:4); v3 shadow rows carry shadow_side and no side, so AT:225-232 maps nothing (backtest/layers/alerts/live_runner_cli.py:126-131, :219-231); v3 simulator fills FABIO_V3_SPEC.md:139-141, entry grid {rest, confirm} :239-242 | market, 10 USD (CFG:20); v3 places no order | Q52 Faw:321-327 (enter at the breakout; order type not stated); Q46 0j:4@3148 (P08: act on the close of the confirmation candle, timing not type). 0 order-type statements for his own entries in 8 Fabio transcripts (B.4) | CONCEPT-ONLY (entry at the break, after confirmation; type unknown) | KEEP market 10 USD (Ruling 2); REMOVE@LIVE. Nothing to fix until v3 emits a side |
| E2-T | Tom time exit: max_hold_bars and which zone TF sets it | AT:57 (max_hold_bars 8), AT:215-219 (minutes = 8 x zone TF; zone TF from the card ZONE name, AT:134-136; no match -> 15m); PM:229-237 (plan field max_hold_minutes), PM:542-549 (fires when elapsed > limit), PM:339-383 (market close, then cancel stop and targets); origin SL:176 (2026-09-29, supervisor decision) | 8 bars. Measured with the live code (B.3): 5m zone 40 min, 15m 120, 1h 480, 4h_* 1920 min (32 h), weekly/daily/prior_day/vwap_band/fvg/naked zones (no TF prefix) 120. On disk: 5 plans 40 min, 4 plans 120 | NO-SOURCE: 0 hold-time rules in 58 transcripts of the Tom set (B.4; the one hit is unrelated). Opposed: Q09 kXh:19@1020; Q10 WSC:19@10798. Tom exits on an event: Q11 4Mo:19@21830 (V2/4Mo:73, "Speed Off"); the only clock statement ends the session: Q12 4Mo:19@22013 | NO-SOURCE | CHANGE: set tom.max_hold_minutes (config only; AT:215-216 already wins over the bar rule) to one flat value; value MEASURE (Ruling 3); REMOVE@LIVE unless sourced. n=1 check (B.5): the one closed Tom trade time-exited at 40.03 min (+0.054 % gross), the target was never reached and holding would have hit the stop about 5 h 45 min later: the time exit is not shown harmful |
Rationale (DSA 2026-10-04, correcting B100 over-reach): the row's own evidence says 0 hold-time rules in 58 Tom transcripts, Q09/Q10 are Opposed, Q11 is an event exit, Q12 ends the session. H1 line 7 defines NO-SOURCE as no idea behind it, or a role the trader never gives it. Tom never gives time exit that role. Reverted from CONCEPT-ONLY.
| E2-F | Fabio time exit | AT:66 + AT:289-290 (layers max_hold_bars 8 x alert tf); Fabio L1 runs 15m -> 120 min (TOM_FABIO_REVIEW:35); v3 simulator: S8(a) 15 bars (P13), window-end exit (FABIO_V3_SPEC.md:167, :224) | 8 bars of the signal TF | NO-SOURCE for the count. Fabio exits on an event: Q44 8C:5-6 (P15); Q45 fZ:144-146 (P16). The NY window: Q47 8C:7-8 (P33, session only; 390 and 330 are NS-fixed) | NO-SOURCE | KEEP (Ruling 2); REMOVE@LIVE. Event exits exist only in the v3 simulator |
| E3-T | Tom size and runner leg at the 10 USD Deribit minimum (50/50 feasibility) | CFG:10 (tom.size_usd 10; the AT:57 default 200 is overridden); AT:156-158 (near leg floors to 10; split refused if either leg < 10); PC:47, PC:82-100 (SIZE_INCREMENT 10; round_size floors, CompileError below 10); exchange minimum: execution/testnet/t050_phase3.py:33 ("min_trade_amount 10"), SL:181 | size 10 -> runner_split returns "size 10 too small for a 50/50 split". Run this session: size 20 -> "50@0.476,50@1.19"; size 30 -> accepted, but both legs compile to 10 (PC:266), so 10 USD of the position has no target. Live since R2: 3 of 8 attempts logged "size 10 too small", 5 "no RUNNER_TARGET" | NO-SOURCE (10 is the exchange minimum, not a Tom number). Tom sizes from the stop: Q22 tS6:19@8786, which contradicts a fixed size | NO-SOURCE | CHANGE: size_usd 10 -> 20 (CFG:10). Authority is Ruling 2; TF5 row 1.7 cites Ruling 1, which is about net_rr. Add a guard so a split is refused when the legs do not sum to the size (AT:156-158) |
| E3-F | Fabio size | CFG:20 (layers.size_usd 10); AT:286-287 (single target, no split); v3: add cap q1 FABIO_V3_SPEC.md:216 (P25) | 10 USD, one leg | NO-SOURCE: P25 has no quote (FABIO_PROVENANCE_AUDIT_2026-10-01.md:82). Fabio scales by adding, not by splitting an exit: Q43 fZ:152-154 (P22) | NO-SOURCE | KEEP 10 (Ruling 2) |
| E4-T | 50/50 split rule (runner_leg_pct) | AT:57-62 (runner_leg_pct 50; comment "NO-SOURCE testnet default"), AT:142-161; NP:55-67 (parse_targets "50@a,50@b"); PC:262-274 | 50 % of size at TARGET, 50 % at RUNNER_TARGET. 0 of 9 plans split | Tom banks part and keeps the rest: Q19 4Mo:19@9787 (one position closed, V2/4Mo:45); Q20 4Mo:19@21211; V2/4Mo:39 (row 16, planned partial); Q23 BVp:19@13118 (first profits at 3:1); Q21 4Mo:19@17819 ("all bonus"). No share is stated; his partials are one contract of several | CONCEPT-ONLY | KEEP 50 (Ruling 2); MEASURE once runner trades exist (Q34 UOB:7@5492: decide from your own key figures) |
| E4-F | Fabio partial exits | none in the live path (AT:286-290 single bracket); v3: stop ratchet then "take other profit" (FABIO_V3_SPEC.md:209, P18) | none live | Q49 fZ:132-134 (P18); Q52 Faw:321-327 (first, second and third take profit); no share stated | CONCEPT-ONLY | KEEP; nothing live |
| E5-T | Runner minimum distance 0.25 % | RMD:2-3; runtime/runner_min_distance.py:14-25; MOB:270-273, :277-301 (loop :299); SCB:59, :457-490; pinned by src/test/java/datafeed/RunnerMinDistanceTest.java:16 and execution/test_r2_runner_exit.py:314-391 | runner = next volume node at least 0.25 % of the target price beyond TARGET; none -> single target. Live since R2: 5 of 8 attempts had no RUNNER_TARGET (cause not measured) | NO-SOURCE for the number: RMD:3 and sessions/MTS-2026-10-02-2055Z-CLI-SUP-r2-promote.md:26-43 set it by measurement (1057 snapshot candidates; runner gaps 0.087 % for 86 %, >= 0.5 % for 14 %; any value 0.10-0.50 gives the same split) and 12 bp round-trip friction. Parent concept, a runner at the next node: Q09 kXh:19@1020; Q28 qLn:19@7547 | NO-SOURCE (parent concept CONCEPT-ONLY) | KEEP 0.25 (Ruling 2; RMD:3 says re-fit after the first live runner trades); blocked by E3 |
| E6-T | Tom alert max age | AT:57 (max_age_seconds 300), AT:193-194 (stale alert rejected) | 300 s | NO-SOURCE: no quote about alert age. Nearest: V2/tS6:27 (row 4, "far too late in the move", about entry timing, not an alert clock) | NO-SOURCE | KEEP (Ruling 2). With E1b an order can rest until 900 s after the engine's read |
| E6-F | Layer max_age_bars (all layers, incl. Fabio L1) | AT:65 (default 1.2), CFG:22 (2.0), AT:259-284 (age from bar close > max_age_bars x bar); origin SL:181 (collection config 2026-09-29) | 2.0 bars | NO-SOURCE: no Fabio or Tom quote | NO-SOURCE | KEEP (Ruling 2); REMOVE@LIVE |
| E7-T | Tom break-even rule (stop to entry after leg 1) | AT:213-214 (flag only when a split exists); NP:109-110, :160-162; PM:27-34, :252-267, :285-293, :385-416, :609-614 (first target fully filled AND position shrank -> stop trigger = average entry, snapped toward profit, once) | stop to the average entry after the first leg fills. Never exercised: 0 of 9 plans carry breakeven_after_first_target | NO-SOURCE: 0 "stop to entry/zero" statements in 58 Tom transcripts (B.4; the 9 "break even" hits are hit-rate arithmetic). The concept is borrowed from Fabio (AT:60-61), not Tom's words. Tom keeps the stop after his first partial: Q13 4Mo:19@9838 (V2/4Mo:46); moves it only to structure: Q15 4Mo:19@12762, Q14 4Mo:19@12857, Q16 kXh:19@3358; sometimes does not trail: Q17 k0z:19@7033. After two partials "we won't lose anything here anymore": Q18 4Mo:19@13675 (trade-level, the stop is not at entry) | NO-SOURCE (opposed by Q13 and Q14) | KEEP (Ruling 2); test the variant "stop stays structural after leg 1" in TF6/R7; REMOVE@LIVE unless sourced |
| E7-F | Fabio break-even and stop ratchet | none in the live path (no BE in the layer bracket, AT:286-290); v3: dist be_k {1.0, 2.0} (P21) and E_opp stop to BE on an event (P17), FABIO_V3_SPEC.md:149-155, :208, :212 | none live | Q40 0j:4@4095 (P21); Q41 fZ:113-115 (P17: an event, the sellers got stopped again); Q53 fZ:43-45 (BE if the level fails); Q48 fZ:67-68 (P19: lower the risk by the stop); Q54 8C:73-75 (trail once in profit) | CONCEPT-ONLY (the concept is his, the trigger is an event; ours is a leg fill) | KEEP; align the trigger in TF7 if v3 ever trades |
| E8a-T | Tom stop at the structural level | SCB:104 (cites TOM-072..074), SCB:117-121 (swing beyond the zone); MOB:255-259; NP:103 + AT:206 (stop sent as % of entry, 3 decimals); PC:194-202 (fixed % from the entry, snapped toward entry); EX:17 (stop_market, trigger = mark) | stop at the last swing beyond the zone, sent as a fixed % | Q24 4Mo:19@763 (V2/4Mo:26); Q36 kXh:19@7441; Q27 kXh:19@7067 (a tight stop in the wrong range is his admitted error). Short side contested: Q26 tS6:19@5809 (V2/tS6:33) and V2/WSC:36 put it above, Q25 yRv:19@6182 says it "doesn't belong above the high" (PROVENANCE_AUDIT_TOM.md A05, F5) | CONCEPT-ONLY (long side matches, short side contested) | KEEP (engine row A05) |
| E8b-T | Tom 0.2 % fallback stop and 0.1 % floor | SCB:48 (MIN_STOP_PCT 0.001), SCB:118, :121 (fallback 0.2 %), SCB:126-129 (a stop closer than 0.1 % is replaced by 0.2 %) | 8 of 9 Tom plans carry a stop of exactly 0.2 %, 1 carries 0.137 % (B.3). Targets 2.19-2.69 % in 8 of 9, i.e. 10.9R-19.6R | NO-SOURCE: engine rows A03, A04 (PROVENANCE_AUDIT_TOM.md:25-26). Tom's own stops are 12 and 10 ticks: Q50 yRv:19@8864; Q51 3o1:19@5649 | NO-SOURCE | Not a TF5 item: A03/A04 need an operator decision (remove the fallback or source it); carry to the engine queue |
| E8-F | Fabio stop (layer bracket) | AT:64 + AT:287 (stop_pct 1.0); NP:103; v3: structural stop +1 tick (P32), floor f {0.3 %, 0.5 %} (P31), FABIO_V3_SPEC.md:222-223 | fixed 1.0 % stop | NO-SOURCE for 1.0 % and for P31 (no quote, FABIO_PROVENANCE_AUDIT_2026-10-01.md:88). Concept: Q42 fZ:45-46 (P32); Q52 Faw:321-327 (stop below the reload level) | NO-SOURCE (structural rule CONCEPT-ONLY, not live) | KEEP 1.0 % (Ruling 2); REMOVE@LIVE |
| E9-T | Tom target selection at execution | AT:206-212 (TARGET sent as % of entry; whole size or leg 1), PC:262-274 (reduce-only limit, snapped toward entry), PS1:317-323; upstream pick MOB:261-301 and SCB:132-149, :457-490: nearest volume node (POC weekly/daily/4h/prior-day, HVN weekly/daily/4h) whose net R:R clears NRF:2 (1.25), else the farthest node (R1 rule, WHY_ENGINE_SILENT_2026-10-03.md:34-36) | one resting limit at the node; 10.9R or more in 8 of 9 plans (B.3) | Q28 qLn:19@7547 (TOM-018, conditions/entry_timing_triggers.md:368-370; TOM-102, conditions/risk_protocol.md:370-371); Q29 tS6:19@6115 ("last largest volumes", tension with nearest, F2); Q30 4Mo:19@810; Q04 yRv:19@10311 (the exit was also a limit order); Q31 UrZ:7@8924 (never delete the target) | CONCEPT-ONLY (the node set is Tom's; picking the nearest node that clears a net_rr floor is ours, and 1.25 is a testnet value, Ruling 1) | KEEP (Ruling 2, D1-D2); MEASURE in R7 |
| E9-F | Fabio target (layer bracket) | AT:64 + AT:287 (targets "2" = +2 %); v3 model B edge target (P36), FABIO_V3_SPEC.md:227 | fixed +2 % | NO-SOURCE for 2 %. Concept: Q52 Faw:321-327 (first take profit at the major liquidity areas, second and third at other resting liquidity); P36 is CONCEPT-ONLY (FABIO_PROVENANCE_AUDIT_2026-10-01.md:93) | NO-SOURCE | KEEP 2 % (Ruling 2); REMOVE@LIVE |
| E10-1 | Entry before proof: 4MoNjEQ2Dd8 (trade 1) | decision-log rows V2/4Mo:25 (row 2 ENTRY, pos 3), :30-31 (rows 7-8 PROOF (AFTER), pos 8 and 10), :66 (row 43 ERROR), trade block :83-84; EXTRACTION_ROUND2_2026-10-01.md:22 (A1). Code chain: proof gate before the order (SETUP_FORMING needs proof >= 5, PROVENANCE_AUDIT_TOM.md:104 V02) | ENTRY BEFORE PROOF: 1 entry, order type unknown | Q07 4Mo:19@669 (looking for a long entry at the price area, proofs read afterwards); Q08 4Mo:19@18589 (an order placed too early, "not a big deal") | SOURCED | no code change (H4) |
| E10-2 | Entry before proof: kXhIAug0Gh8 (4 trades) | V2/kXh:29-30 (rows 6-7: PROOF (BEFORE) then ENTRY, both pos 27), :43 (row 20, limit placed in advance, proof not stated), :47 (row 24, after two reactions), :52 (row 29, re-entry after buyer stability), :37 (row 14, more proof after); trade blocks :65, :80, :87, :97 | 3 of 4 entries after proof, 1 not stated, 0 before. Defect in the extract: the trade-1 block :65 says "entered BEFORE or AFTER proof: before", which by EXTRACTION_METHOD_V2.md:60,84 means entered before proof, but rows 6-7 and the transcript order (rejection, then "And so I opened my position here") say proof first | Q37 kXh:19@2395; Q05 kXh:19@4674 (limit in advance) | SOURCED (proof first) | no code change; the :65 label is wrong (not fixed here: read-only) |
| E10-3 | Entry before proof: tS6ZEiHj8gQ (2 trades) | V2/tS6:32 (row 9 ENTRY after the consolidation), :41 (row 18 ENTRY after rows 16-17, :39-40, PROOF (BEFORE)); rejects :26 (row 3), :30 (row 7), :46 (row 23); trade blocks :59, :73 | 2 of 2 entries after proof; early and peak entries rejected | Q32 tS6:19@3618; Q33 tS6:19@4888 | SOURCED (proof first) | no code change |
| E10-4 | Entry before proof: UrZ4vpHJ97g (no trade) | V2/UrZ:18 (n_trades 0), :40 (row 17 ENTRY is an illustration with no proof content), :27 (row 4 REJECT: no entry without a target in advance) | no trade and no statement about the order of proof and entry | NO-SOURCE (nothing to quote) | NO-SOURCE | none |
| E10-5 | Entry before proof: WSCIURybK3U (no trade) | V2/WSC:18 (n_trades 0), :29 (row 6 ENTRY illustration), :26 (row 3 LESSON), :25 (row 2 REJECT shorting "here, here, here") | no trade; general rule: wait for a real setup | Q35 WSC:19@1948 | CONCEPT-ONLY (the idea is Tom's, no order sequence is given) | none |

Count by script over the table rows above [run: python, verdict cell = first word of column 6]: parameter rows E1-E9 (19): SOURCED 1 (E1a-T), CONCEPT-ONLY 7 (E1-F, E1b-T, E4-T, E4-F, E7-F, E8a-T, E9-T), NO-SOURCE 11 (E2-T, E2-F, E3-T, E3-F, E5-T, E6-T, E6-F, E7-T, E8b-T, E8-F, E9-F). Tom rows 11: SOURCED 1, CONCEPT-ONLY 4, NO-SOURCE 6. Fabio rows 8: CONCEPT-ONLY 3 (E1-F, E4-F, E7-F), NO-SOURCE 5. E10 rows (5): SOURCED 3 (E10-1, E10-2, E10-3), CONCEPT-ONLY 1 (E10-5), NO-SOURCE 1 (E10-4).

## H4 ENTRY-BEFORE-PROOF CROSS-CHECK (review E5, EXTRACTION_ROUND2_2026-10-01.md:22 row A1)

Question: the v2 extract of 4MoNjEQ2Dd8 has the entry before the absorption proof, and our chain demands proof first. Does that order hold in the other four v2 extracts?

| extract | entries | proof first | entry first | not stated | rows (V2/<id>) |
|---|---|---|---|---|---|
| 4MoNjEQ2Dd8 | 1 | 0 | 1 | 0 | :25, :30-31, :83 |
| kXhIAug0Gh8 | 4 | 3 | 0 | 1 | :29-30, :43, :47, :52 |
| tS6ZEiHj8gQ | 2 | 2 | 0 | 0 | :32, :41 |
| UrZ4vpHJ97g | 0 (illustration) | - | - | - | :40 |
| WSCIURybK3U | 0 (illustration) | - | - | - | :29 |
| total | 7 | 5 | 1 | 1 | |

Reading:
1. One of seven Tom entries is entry-first. That does not support reversing the chain. Tom names both orders himself: Q06 qLn:19@4652 ("the very brave ones just buy here, but you can also wait until the proof arrives") makes the early entry the brave variant and the wait for proof the standard one.
2. The live chain is proof-first: all 9 Tom attempts came from alerts whose proof count reached 5 in that cycle (runtime_data/apparatus_log.txt: "ALERT #84, #85, #86, #87, #92, #105, #113, #114, #115 ... proof N -> 5").
3. A1 is still a real second Tom pattern (a resting order placed in advance: 4Mo trade 1, kXh trade 2), and it interacts with E1. SETUP_FORMING needs proofs that happen at the zone (rejection wick, absorption within 0.1 % of the zone, PROVENANCE_AUDIT_TOM.md P01 and P03), so the alert fires after the touch, and a limit at the zone price is then a retest order. Six of the six long no-fills that have price data were placed 0.2-55.6 USD below the market (B.1). Tom's in-advance order is placed before the touch. This is a hypothesis consistent with B.1, not a measured cause.
4. Proposal: no change to the chain. Log a shadow variant (no order): a limit at the zone while the verdict is WAIT_PROOF or WAIT_TRIGGER and price is inside the distance cap, so L3 can measure it. Add 4Mo trade 1 as a TF6 golden scenario; the chain says WAIT_PROOF, Tom entered; list it as a translation gap, not hidden.
Limits: 7 entries from 3 videos, one extractor, no kappa. "Proof" in the extracts is Tom's words (rejection, overhang, absorption, lower volume, B profile, buyer stability); the code's proof is a 7-point proxy count. The two are not the same object.

## H5 RANKED FIX LIST (nothing here was applied; execution/ stays with the supervisor)

All live-path changes: staged as `.new`, with tests for restart/reset state, non-trade balance moves and API errors, failing closed (CLAUDE.md). Supervisor promotes and restarts.
1. E1 (7 of 9 attempts no_fill). (a) Price the limit on the venue: parse the card's PRICE line (written at PS1:292; AT:108 CARD_FIELD and AT:121-139 parse_tom_alert do not read it), read the Deribit mark at placement (DO:438 get_ticker, already used by PM:399) and place zone + (mark - card PRICE); if the ticker cannot be read, refuse the entry (fail closed). Touches AT:108, :121-139, :206-212. (b) Make the wait a config key and pass it: AT:57 (new key), AT:336 (--max-entry-seconds; EX:541 already accepts it); value MEASURE (Ruling 3). (c) No change to EX:125, EX:419-457.
2. E3 (blocks the only path that exercises E4, E5, E7). CFG:10 size_usd 10 -> 20; guard in AT:156-158 so a split is refused unless both legs are multiples of 10 and sum to the size (size 30 leaves 10 USD without a target, B.3). Authority: Ruling 2 (not Ruling 1).
3. E2. CFG: set tom.max_hold_minutes (AT:215-216 already overrides the bar rule); remove the TF scaling at AT:134-136 and AT:217-219 so a 4h zone cannot hold the one Tom slot for 32 h (AT:578-581 skips every signal while a slot is busy). Value MEASURE.
4. E8b. Operator decision on SCB:48, :117-129 and the Python mirror MOB:255-259 (remove the 0.2 % fallback and the 0.1 % floor, or source them). Not TF5.
5. E7. No code change; add the variant "stop stays structural after leg 1" to TF6/R7 (PM:609-614 is the path), because Q13 and Q14 oppose the default.
6. E10. No chain change; add the shadow variant and the 4Mo golden scenario (TF6); correct the trade-1 label at V2/kXh:65.
7. E4, E5, E6, E9. Keep. Revisit E4 and E5 after 30 filled runner trades (TOM_FABIO_REVIEW:66, n >= 30 per core).
8. Fabio. Nothing to fix: v3 places no order. If v3 gets a side, rows E1-F, E2-F, E3-F, E8-F and E9-F are the generic bracket and stay NO-SOURCE; write a v3 order mapping first (TF7, TF8).

## H6 NOT AUDITED, AND WHY

- Review E4 (SETUP_CONFIRMED unreachable, WAIT_PROOF/WAIT_TRIGGER stops, B076): engine verdict chain, audited as V01-V12 in PROVENANCE_AUDIT_TOM.md.
- Review E6 (v3 silent) closed by TF3 (Saturday); E7 (gate) closed by TF1; E8 (B072, B073, B070): engine and live-path bugs with their own rows (4.x).
- Execution safety limits (size multiple of 10, 10,000 USD total, 500 USD loss, one position, HALT, daily loss; PROVENANCE_AUDIT_TOM.md section 7 X1-X8): listed there as not judged; only the 10 USD minimum is touched here (E3).
- Mainnet path, kill switch, daily-loss monitor, reconciler, orphan watchdog: no trader parameter in them.
- Layers other than Fabio L1 (turn_of_candle, rsi, cryptocred, positioning, session): they share AT:259-291, so E2-F, E6-F, E8-F and E9-F apply to them in form, but their own trader quotes are LY1.
- Fabio order of proof and entry: no v2-format Fabio extract exists; the line-by-line fZlNGWvd2Ko extract was not read for this.
- Cause of the 5 "no RUNNER_TARGET" attempts (the 0.25 % filter or no node beyond the target): the node lists were not reconstructed.
- Cause of the E1 misses: not established. B.1 and B.2 show a distance, a one-tick miss and a basis; the Deribit testnet order book was not replayed (no history on disk), so queue position and testnet liquidity are untested.
- Negative evidence (E2, E7, E1-F) is relative to the patterns in B.4 over the Tom set as defined at EXTRACTION_ROUND2_2026-10-01.md:10 (it may contain a non-Tom speaker) and the 8 Fabio ids; a trader may say it in words the patterns miss.
- One reader, no second reader, no kappa (the Tom audit had kappa 0.446, W3_KAPPA_REPORT_2026-10-01.md). The quote gate checks that text is verbatim and where it sits, not that it supports the verdict.
- Not run: the Java code (read, not executed); the full offline gate (docs-only commit, see the session record).

## APPENDIX B EVIDENCE

### B.1 Tom limit placement against the market (9 attempts; compiled limit price from the journal intent event; Binance 1m OHLC from runtime/orderflow_live/*.csv, 10-02 = TF3 backfill, no rows on 10-03 before 03:01Z; window = 600 s after the order was placed)
"Must move" = USD the market had to move to reach the limit at placement. "Margin" = USD the Binance 1m extreme went through the limit (+) or fell short of it (-) in the window.

| plan | side | limit | placed (UTC) | Binance 1m open | must move | margin | result |
|---|---|---|---|---|---|---|---|
| L-lim-1002-1954 | LONG | 84090.5 | 10-02 19:54:40 | 84146.1 | 55.6 | -55.5 | no_fill |
| L-lim-1002-2214 | LONG | 84479.5 | 10-02 22:14:35 | 84479.7 | 0.2 | -0.2 | no_fill |
| L-lim-1002-2235 | LONG | 84481.5 | 10-02 22:35:45 | 84499.1 | 17.6 | +29.7 | no_fill |
| L-lim-1002-2353 | LONG | 84482.5 | 10-02 23:53:35 | 84515.4 | 32.9 | -0.2 | no_fill |
| L-lim-1003-0046 | LONG | 84525.0 | 10-03 00:46:39 | no data | - | - | no_fill |
| S-lim-1003-0635 | SHORT | 84611.0 | 10-03 06:35:47 | 84608.5 | 2.5 | +8.8 | filled at 84650.5 |
| L-lim-1003-1200 | LONG | 84622.5 | 10-03 12:00:50 | 84634.2 | 11.7 | -9.1 | no_fill |
| L-lim-1003-1211 | LONG | 84634.0 | 10-03 12:11:35 | 84655.9 | 21.9 | -17.2 | no_fill |
| L-lim-1003-1357 | LONG | 84867.5 | 10-03 13:57:53 | 84835.8 | -31.7 (market already below the limit) | +136.9 | filled at 84864.5 |

Reading: of the 6 long no-fills with data, the market traded through one (2235, by 29.7 on Binance, unfilled on Deribit), missed two by 0.2 USD (2214, 2353: one tick), and never came within 9-55 USD of three (1954, 1200, 1211). Alerts fired at proof 5, after the touch (H4 point 3).

### B.2 Deribit testnet against Binance (public ticker reads at 15:32:34Z, 15:32:37Z, 15:32:41Z, no credentials)
Deribit test last minus Binance futures last: +11.6, +15.5, +19.2 USD (Deribit index 84790.96 against Binance 84774.40 at the first read). Lower bounds from the two fills: the short filled at 84650.5 against a Binance open of 84608.5 (basis at least +42); the long filled at 84864.5 against 84835.8 (at least +29, minute open, so approximate). A positive basis puts every long limit placed from Binance-derived zones further below the Deribit market and brings every short limit closer. Five observations, not a series.

### B.3 Tom plans on disk (execution/plans/*-lim-*.json) and live-code measurements
All 9 plans: breakeven_after_first_target absent; single target; validity 1.0 h.

| plan | stop % | target % | target / stop | max_hold min | outcome |
|---|---|---|---|---|---|
| L-lim-1002-1954 | 0.2 | 2.661 | 13.3 | 120 | no_fill |
| L-lim-1002-2214 | 0.2 | 2.189 | 10.9 | 40 | no_fill |
| L-lim-1002-2235 | 0.2 | 2.186 | 10.9 | 40 | no_fill |
| L-lim-1002-2353 | 0.2 | 2.185 | 10.9 | 40 | no_fill |
| L-lim-1003-0046 | 0.137 | 2.691 | 19.6 | 120 | no_fill |
| S-lim-1003-0635 | 0.2 | 0.844 | 4.2 | 40 | filled, time_exit at 40.03 min, net -0.0048 USD (trade_ledger.jsonl) |
| L-lim-1003-1200 | 0.2 | 2.572 | 12.9 | 120 | no_fill |
| L-lim-1003-1211 | 0.2 | 2.558 | 12.8 | 40 | no_fill |
| L-lim-1003-1357 | 0.2 | 2.276 | 11.4 | 120 | filled, open at 15:27Z, time exit due about 15:57Z |

runner_skipped in auto_trades.jsonl: alert #84 predates R2 (no field); #85, #86, #87 "size 10 too small for a 50/50 split"; #92, #105, #113, #114, #115 "no RUNNER_TARGET".
Live-code measurements, run this session through AT.tom_signal, AT.runner_split and PC.compile_plan on synthetic cards (nothing written): ZONE 5m_swing_low -> --max-hold-minutes 40; 15m_swing_low 120; 1h_swing_low 480; 4h_val and 4h_poc 1920; daily_val, weekly_poc, prior_day_val, vwap_band_+1, fvg, naked_poc_2026-10-01 120. runner_split at size 10 -> (None, reason), at 20, 30 and 200 -> "50@0.476,50@1.19". compile_plan with targets 50/50: size 10 CompileError (5 floors to 0), size 20 targets 10 + 10, size 30 targets 10 + 10 on a 30 position.

### B.4 Negative searches (normalized transcript text, case-insensitive; Tom set = 58 ids, Fabio set = fZlNGWvd2Ko, 0jM5Y31YJak, 8CWKfoSJu3c, jasv3L-d8ZE, LQvv5xgy_ik, StaphlRH8NQ, 0KyIEdvVKMQ, FawPrRUGNpk)
- Tom hold time: `time[- ]stop|time[- ]based exit|after (\d+|a few|five|ten|fifteen|twenty|thirty) (minutes|candles|bars)|max(imum)? holding|hold(ing)? (time|period)|how long (do|should|to) (you )?(hold|stay|keep)|(exit|close)[a-z ]{0,25}(after|within) [a-z0-9 ]{0,12}(minutes|bars|candles)` -> 1 hit in 1 transcript (sQ_biBKhPVU, "holding periods" of market participants, unrelated).
- Tom break-even: `break[- ]?even|breakeven|stop (loss )?(to|at) (zero|my entry|the entry|entry)|move (the|my) stop (loss )?(to|up to) (the )?(entry|zero)` -> 9 hits in 6 transcripts (3JqMyzE8jIQ, UrZ4vpHJ97g x3, WSCIURybK3U x2, hQ8sOq67x5o, k0zm5NYn0IQ, zAwEX_tRUfE); all are hit-rate or draw-down arithmetic.
- Tom stop moves: `risk[- ]free|riskless|stops us out|stopped out anymore|lose anything|(move|moved|moving|trail|trailing|adjust|raise|raising|tighten|tightening)( up)? (my |the |our )?stop` -> 14 hits in 6 transcripts (4MoNjEQ2Dd8 x8, T6hDJcHrVBM, UOBgXV20yCM x2, k0zm5NYn0IQ, kXhIAug0Gh8, n7ZSkjb7JXs); none moves a stop to the entry price; the moves are to structure or volume (Q14, Q15, Q16, T6hDJcHrVBM "market acceptance", n7ZSkjb7JXs "above the last major trades").
- Tom limit orders: `limit order` -> 17 hits in 10 transcripts; the Tom entries with an order type are yRvMW6lgN1o (5 hits, Q01-Q04) and kXhIAug0Gh8 (Q05).
- Fabio order type: `limit order|market order|stop order|pending order|limit buy|limit sell|\bresting\b|at market|market price` -> 0 hits in 7 transcripts; 27 hits in FawPrRUGNpk, all read: order-flow theory (aggressive market orders against resting passive liquidity), none states his own entry order type; the one trade-management hit is Q52.
- Fabio break-even and trail: hits in fZlNGWvd2Ko (Q41, Q53), 0jM5Y31YJak (Q40), jasv3L-d8ZE ("also put stop loss to zero"), 8CWKfoSJu3c (Q54, "stop loss to stopping profit"), FawPrRUGNpk ("put your position to break even"): the BE concept is Fabio's in 5 of 8 transcripts, always event-triggered.

### B.5 Time exit, n=1 counterfactual (S-lim-1003-0635)
Entry 84650.5 short, stop 84780.0, target 0.844 % below the plan entry (about 83896), exit at 84605.0 at 07:15:48Z by time exit (+0.054 % gross, net -0.0048 USD after 0.0102 USD fees). Binance 1m after the exit: the low in the next 2 h was 84501.2 (target never reached); the stop level was first touched at 12:18-12:20Z (basis 0 to -40 USD), about 5 h 45 min after entry. Holding would have cost about -0.2 %. One trade; no claim beyond it.

## APPENDIX A QUOTES (verbatim; machine-checked by scripts/dev/verify_extract_quotes.py)

> "In this trade, I entered with a limit order and simply had a sell order here."
Q01 **Source GPS: yRvMW6lgN1o | BEGIN** T/yRvMW6lgN1o:19@1211

> "I said I would place a limit order specifically right below the last volume step of the corresponding price profile of the volume profile"
Q02 **Source GPS: yRvMW6lgN1o | MIDDLE** T/yRvMW6lgN1o:19@5374

> "We placed our limit order and then we let the market decide what would happen next."
Q03 **Source GPS: yRvMW6lgN1o | MIDDLE** T/yRvMW6lgN1o:19@5832

> "Both were done with limit orders. So you could have basically ignored the market"
Q04 **Source GPS: yRvMW6lgN1o | END** T/yRvMW6lgN1o:19@10311

> "placed another limit order here in case it picked me up again and it did"
Q05 **Source GPS: kXhIAug0Gh8 | MIDDLE** T/kXhIAug0Gh8:19@4674

> "Sure, the very brave ones just buy here, but you can also wait until the proof arrives."
Q06 **Source GPS: qLnQan0KGmQ | MIDDLE** T/qLnQan0KGmQ:19@4652

> "Here we have a wonderful price area where I'm looking for a long entry and that's why I'm now"
Q07 **Source GPS: 4MoNjEQ2Dd8 | BEGIN** T/4MoNjEQ2Dd8:19@669

> "I placed an order too early because I expected the breakout to happen"
Q08 **Source GPS: 4MoNjEQ2Dd8 | END** T/4MoNjEQ2Dd8:19@18589

> "letting the trades that are running continue to run, that is a great art"
Q09 **Source GPS: kXhIAug0Gh8 | BEGIN** T/kXhIAug0Gh8:19@1020

> "they very often exit their trades much too early"
Q10 **Source GPS: WSCIURybK3U | END** T/WSCIURybK3U:19@10798

> "That's why I'm out now, I think."
Q11 **Source GPS: 4MoNjEQ2Dd8 | END** T/4MoNjEQ2Dd8:19@21830

> "lunch break is coming up, so I'm ending the session"
Q12 **Source GPS: 4MoNjEQ2Dd8 | END** T/4MoNjEQ2Dd8:19@22013

> "We'll leave the stop loss down here"
Q13 **Source GPS: 4MoNjEQ2Dd8 | MIDDLE** T/4MoNjEQ2Dd8:19@9838

> "And before that, it doesn't make sense to move the stop-loss."
Q14 **Source GPS: 4MoNjEQ2Dd8 | MIDDLE** T/4MoNjEQ2Dd8:19@12857

> "I moved the stop loss to a price range where I simply expect the opposite of my long position."
Q15 **Source GPS: 4MoNjEQ2Dd8 | MIDDLE** T/4MoNjEQ2Dd8:19@12762

> "I decided to also trail the stop loss to the high."
Q16 **Source GPS: kXhIAug0Gh8 | MIDDLE** T/kXhIAug0Gh8:19@3358

> "Trailing the stop loss is something a lot of people like to do. In this case, I don't do that"
Q17 **Source GPS: k0zm5NYn0IQ | BEGIN** T/k0zm5NYn0IQ:19@7033

> "we won't lose anything here anymore even if the market stops us out"
Q18 **Source GPS: 4MoNjEQ2Dd8 | MIDDLE** T/4MoNjEQ2Dd8:19@13675

> "let's close out a position. We're happy with that."
Q19 **Source GPS: 4MoNjEQ2Dd8 | MIDDLE** T/4MoNjEQ2Dd8:19@9787

> "Let's take out another position."
Q20 **Source GPS: 4MoNjEQ2Dd8 | END** T/4MoNjEQ2Dd8:19@21211

> "whatever happens above that is all bonus for us now"
Q21 **Source GPS: 4MoNjEQ2Dd8 | END** T/4MoNjEQ2Dd8:19@17819

> "I always determine my position size in direct accordance with my stop-loss level."
Q22 **Source GPS: tS6ZEiHj8gQ | END** T/tS6ZEiHj8gQ:19@8786

> "if I secure my initial profits at a riskreward ratio of precisely 3:1"
Q23 **Source GPS: BVpYGKz9PBU | END** T/BVpYGKz9PBU:19@13118

> "The stop loss goes below the last low here"
Q24 **Source GPS: 4MoNjEQ2Dd8 | BEGIN** T/4MoNjEQ2Dd8:19@763

> "It doesn't belong above the high. Why is that?"
Q25 **Source GPS: yRvMW6lgN1o | MIDDLE** T/yRvMW6lgN1o:19@6182

> "you have to place your risk above this level"
Q26 **Source GPS: tS6ZEiHj8gQ | MIDDLE** T/tS6ZEiHj8gQ:19@5809

> "I definitely placed my stop loss in a price range that was not smart at the time."
Q27 **Source GPS: kXhIAug0Gh8 | END** T/kXhIAug0Gh8:19@7067

> "if it accepts new prices, then it looks for the next high volume price and that is your target."
Q28 **Source GPS: qLnQan0KGmQ | END** T/qLnQan0KGmQ:19@7547

> "the profit target should be where the last largest volumes occurred"
Q29 **Source GPS: tS6ZEiHj8gQ | MIDDLE** T/tS6ZEiHj8gQ:19@6115

> "my take-profit is set above the highs"
Q30 **Source GPS: 4MoNjEQ2Dd8 | BEGIN** T/4MoNjEQ2Dd8:19@810

> "which is why you must never ever delete this predefined target unless in the meantime you've used other mathematical approaches for yourself"
Q31 **Source GPS: UrZ4vpHJ97g | MIDDLE** T/UrZ4vpHJ97g:7@8924

> "it really does not make much sense to just short somewhere around here"
Q32 **Source GPS: tS6ZEiHj8gQ | MIDDLE** T/tS6ZEiHj8gQ:19@3618

> "But, the probability of getting stopped out is then high."
Q33 **Source GPS: tS6ZEiHj8gQ | MIDDLE** T/tS6ZEiHj8gQ:19@4888

> "why exactly was it that I didn't let my trade run there? Well, very simple answer. If you're active as a trader and use such a strategy for yourself, and you have your key figures, then use them."
Q34 **Source GPS: UOBgXV20yCM | MIDDLE** T/UOBgXV20yCM:7@5492

> "wait for a real setup so that you have reference values"
Q35 **Source GPS: WSCIURybK3U | BEGIN** T/WSCIURybK3U:19@1948

> "I then placed my stop loss below the last swing low again."
Q36 **Source GPS: kXhIAug0Gh8 | END** T/kXhIAug0Gh8:19@7441

> "here you can see it wonderfully that the market simply had rejection up here. And I could then dynamically recognize that there was simply an absolute selling overhang. And so I opened my position here."
Q37 **Source GPS: kXhIAug0Gh8 | BEGIN** T/kXhIAug0Gh8:19@2395

> "the market exploded in my direction and I put my stop loss to break even"
Q40 **Source GPS: 0jM5Y31YJak | MIDDLE** T/0jM5Y31YJak:4@4095

> "stop loss to zero. Why? Because we already saw that the sellers got stopped again"
Q41 **Source GPS: fZlNGWvd2Ko | MIDDLE** T/fZlNGWvd2Ko:113-115

> "if this level failed, this one become the new pivot"
Q42 **Source GPS: fZlNGWvd2Ko | BEGIN** T/fZlNGWvd2Ko:45-46

> "we loaded the first one here, then we reloaded here, then we reloaded here"
Q43 **Source GPS: fZlNGWvd2Ko | END** T/fZlNGWvd2Ko:152-154

> "take back control, I want to be out of the market"
Q44 **Source GPS: 8CWKfoSJu3c | BEGIN** T/8CWKfoSJu3c:5-6

> "all these aggression and a failed auction and this is the reason I closed my trade"
Q45 **Source GPS: fZlNGWvd2Ko | END** T/fZlNGWvd2Ko:144-146

> "confirmation from price was exactly this candle"
Q46 **Source GPS: 0jM5Y31YJak | MIDDLE** T/0jM5Y31YJak:4@3148

> "I scalp the NASDAQ during the New York session"
Q47 **Source GPS: 8CWKfoSJu3c | BEGIN** T/8CWKfoSJu3c:7-8

> "buyers failed again. So I want to lower my risk"
Q48 **Source GPS: fZlNGWvd2Ko | MIDDLE** T/fZlNGWvd2Ko:67-68

> "sellers took control but stopped on these big trades. So I can take other profit"
Q49 **Source GPS: fZlNGWvd2Ko | END** T/fZlNGWvd2Ko:132-134

> "with a stop-loss up here, we now have a risk of 12 ticks. We have a profit of 97 ticks."
Q50 **Source GPS: yRvMW6lgN1o | END** T/yRvMW6lgN1o:19@8864

> "my stop loss in this case let's say is 10 ticks and my profit run in this case let's say is 70 ticks. That makes a riskreward ratio of seven."
Q51 **Source GPS: 3o1VVsfBmmU | MIDDLE** T/3o1VVsfBmmU:19@5649

> "you can enter at the breakout protected below the reload level and you can run the setups with the first take profit on the major liquidity areas and the second and third take profit on other resting liquidity area"
Q52 **Source GPS: FawPrRUGNpk | BEGIN** T/FawPrRUGNpk:321-327

> "I will be really fast in putting my position to break even if this level failed"
Q53 **Source GPS: fZlNGWvd2Ko | BEGIN** T/fZlNGWvd2Ko:43-45

> "This is an aggressive trailing stop that I take when we have already a nice floating profit."
Q54 **Source GPS: 8CWKfoSJu3c | BEGIN** T/8CWKfoSJu3c:73-75

# END
