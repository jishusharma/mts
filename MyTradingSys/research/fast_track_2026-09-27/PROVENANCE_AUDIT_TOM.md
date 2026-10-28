# PROVENANCE AUDIT - Tom core path (2026-09-30)

Read only; no repo file edited. Files: SetupCandidatesBuilder.java (SCB), MarketDataSnapshot.java (MDS, only parts feeding candidates, proofs, shapes, state), math_object_builder.py (MOB), mts_math.py (MTH), backtest/verdict.py (VRD), runtime/compiled_engine.md (CE), start-trading-day.ps1 (PS1, what fires), MTS_USER_GUIDE.md section 4.
Rule (CLAUDE.md 'Provenance'): a parameter, gate, threshold or label stays only with a Tom quote and file:line. Searched: MyTradingSys/conditions/*.md, research/TOM_VERBATIM_INDEX.md, extracts/fresh/* (52), extracts/processed/tom/**, raw_transcripts_canonical (59 Tom ids). A quote is cited by id (Qnn) and printed in the last section, where verify_extract_quotes.py checks it. Short names: MP = MISSING_PIECES_2026-09-30.md, AH = ANGLE_HYPOTHESES.md, LBL = TOM_LINE_BY_LINE_4MoNjEQ2Dd8.md, REV = TOM_CORE_BT_REVIEW_2026-09-30.md, BT = TOM_CORE_BT.md (all in this folder).
Verdicts: TOM-SOURCED = a quote supports the value. TOM-CONCEPT-ONLY = Tom names the idea, the code measures it by proxy, the number is ours. NO-SOURCE = no Tom idea behind it, or it plays a role (veto, gate, cap) Tom never gives it. DATA-PLUMBING = no trading meaning. A '-' in the Tom column means nothing found; text after it is the nearest Tom content.

## 1. Summary by verdict

| verdict | rows |
|---|---|
| TOM-SOURCED | 2 |
| TOM-CONCEPT-ONLY | 34 |
| NO-SOURCE | 35 |
| DATA-PLUMBING | 3 |
| total | 74 |

None of the numbers that decide whether a Tom trade exists (stop floor and fallback, target window, net R:R gate, proof bands, book veto, distance caps, below-VAL rule) has a Tom quote. Only the 70% value area is TOM-SOURCED (plus one example row). The '2:1 net' rule cited to qLnQan0KGmQ is not in that video (A13).

## 2. A. SetupCandidatesBuilder.java (SCB): zones, stop, target, R:R, state, setup types

| id | file:line | what it is | value | claimed source | Tom source | verdict | impact |
|---|---|---|---|---|---|---|---|
| A01 | SCB:44; MDS:24,553-565 | Share of volume in the value area | 0.70 | - | Q17 (68.2 or 70%) | TOM-SOURCED | Sets every VAH/VAL and price_vs_va. |
| A02 | SCB:45,201,493-506; MTH:78; MOB:344 | Zones this close count as confluence | 0.3% | CE:158,250 | Q25: overlaps are nodes, VA highs, several POCs in one price range; no percent | TOM-CONCEPT-ONLY | Feeds only the +10 bonus (A14). |
| A03 | SCB:46,119-124 | Stop closer than this to the zone is replaced by zone x1.002 / x0.998 | 0.1% -> 0.2% | comment 'v1.3.3 floor', 'Rule 32: 100 of 750 candidates' | - (Tom's stops: 12 ticks Q10, 10 ticks Q11, about 0.04% on ES) | NO-SOURCE | Overwrites Tom-size stops. AH E-003 case A: Tom's trade scaled by percent is dropped. MP 0.2. |
| A04 | SCB:113,116,123 | Fallback stop when no swing lies beyond the zone | 0.2% | comment | - (Q07: structure, no percent) | NO-SOURCE | Median stop is 0.200% in all 4 backtest variants (BT:84,331,461): the test measures this constant (REV; MP 0.2). |
| A05 | SCB:111-117 | Stop at the swing extreme beyond the zone | swing | CE:150,423; MOB:186-199 'Tom principle' | Q07, Q08: long stop below last low/liquidity. Q09: a short stop 'doesn't belong above the high'. Q31 | TOM-CONCEPT-ONLY | Long side matches. Every short stop is above a high (MP 2.2 'CONTRADICTS Tom'). |
| A06 | SCB:476-483; MOB:186-198 | Swing timeframe used for the stop | weekly 1h; daily/4h/prior-day 15m; vwap/fvg/5m 5m; default 15m | MOB:186-196 | Q30, Q43: levels are carried to smaller charts; no pairs | TOM-CONCEPT-ONLY | Fixes stop width, so which levels fit the window (A08-A10). |
| A07 | SCB:126-147 | Target pool: POC weekly/daily/4h/prior day; opposite VAL/VAH; prior-day low/high; VWAP | list | CE:424 | Q03, Q12, Q44 (next/last largest volume; VWAP for scalps); none for prior-day high/low | TOM-CONCEPT-ONLY | Fixed list; Tom picks the node by eye. FVG and single prints are never targets (CE:425 says single prints are). |
| A08 | SCB:150 | Minimum target distance | 2.0 x stop | comment '2x stop filter' | - (Q05: minimum comes from his hit rate; Q46, Q04 give 2:1 as an example) | NO-SOURCE | Drops candidates whose nearest level is under 2R. |
| A09 | SCB:151 | Maximum target distance | 3.5 x stop | - | - (Tom: 8.1R Q10, 7R Q11, 3:1+ Q35, Q36) | NO-SOURCE | Tom's 12/97-tick trade cannot be produced (AH E-003 A,B; MP 0.1, 2.2). |
| A10 | SCB:153-175 | Target = NEAREST pool level inside [2.0, 3.5]R, else candidate dropped | nearest | - | - (Q03, Q12 name the next node, no window) | NO-SOURCE | WAIT_RR in 80,847 of 120,892 rows (BT:14); nearest-first turns a passing farther level into WAIT_RR (REV). |
| A11 | SCB:183; MTH:74-75 | Gross R:R >= 1.5 or candidate removed | 1.5 | CE:154,231,414-418 ('Tom never lowers R:R minimum') | - (risk_protocol.md:626; Q05) | TOM-CONCEPT-ONLY | Redundant with A08. CE:231 credits Tom with a rule no quote gives. RECLASSIFIED 2026-10-08 (operator, MTS-2026-10-07-1002Z-APP-BLD-research-closeout, B127 RA-W4-A11): the gross 1.5 drop was removed, SetupCandidatesBuilder.java:153 keeps rrSanity as an advisory output flag only (never drops a candidate), so it is a concept-only advisory (CE:154 'Tom never lowers R:R minimum'). |
| A12 | SCB:182; ExecutionMathConstants.java:34; MTH:70-72; CE:153,429 | Friction: net = gross x 0.75 | 25% | CE:429 'System rule (Tom never addresses slippage)' | Q06: fees enter his break-even hit rate; no number | TOM-CONCEPT-ONLY | Flat 25% ignores stop width; at 0.2% stop fees are 0.22-0.23R (BT:84; MP 0.2). |
| A13 | SCB:184; VRD:110-111; PS1:169,204; CE:397,426 | Net R:R >= 2.0 ('2:1 NET') or verdict WAIT_RR | 2.0 | CE:426 and entry_timing_triggers.md:65,730 cite qLnQan0KGmQ | - qLnQan0KGmQ read in full: no '2:1', no minimum (Q01, Q02 only). Nearest Tom 2:1: Q46, Q04, each an example followed by 'what is my hit rate' | NO-SOURCE | MISCITED. With A12 needs gross >= 2.67; A09 caps 3.5: band [2.67, 3.5]R (MP 2.2). |
| A14 | SCB:201 | Confluence bonus to score | +10 | CE:159,251 say no numeric bonus | - | NO-SOURCE | Changes which candidate is 'top'. |
| A15 | SCB:213-218 | Score 50 + 7 x proofs + bonus, cap 95; bands B>=70, C+>=55, C>=40 | 50/7/95/70/55/40 | CE:442 'Tom does not use numeric scoring bands' | - | NO-SOURCE | Only rank 1 feeds VRD:76 and the auto-trader. |
| A16 | SCB:222-225,307-349 | Tie-break by zone TF rank | weekly 10, daily 9, 4h 7, vwap 6, prior-day 5, 1h 4, 15m 3, 5m 2, fvg 1, naked 11 | SCB:18; CE:136 | Q43: higher time frame first; no table | TOM-CONCEPT-ONLY | Equal scores only. |
| A17 | SCB:47,51,229 | Output cap 3; needs 20 one-minute bars | 3; 20 | - | n/a | DATA-PLUMBING | None. |
| A18 | SCB:66-75; MTH:43-49; MTH:16-22; SCB:239-244 | Tier: <=0.1% trigger_ready, <=cap conditional, beyond cap dropped; at_zone substate 0.1% | 0.1% | CE:164,238; CE:280 '0.1% is a system invention... Tom does not specify exact thresholds' | - (Q47: he rests limit orders in advance) | NO-SOURCE | conditional -> WAIT_TRIGGER (VRD:114-115); beyond cap never a candidate. |
| A19 | SCB:428-437; MTH:25-40; CE:206-215 | Distance caps by zone type | weekly 0.5%; daily/pf/4h/prior-day 0.4%; 1h swing 0.5%; 15m/5m swing 0.3%; vwap, bands, fvg 0.2%; default 0.4% | CE:206-215 'Rationale' column | - | NO-SOURCE | Drops zones. MTH:39 doubles caps on speed; CE:222 says 'No fixed cap doubling'. |
| A20 | SCB:283-303 | In value area: short if price above POC, long if below, both at POC | rule | CE:170-200 | Q13: short up here, long down here. No POC-side gating | TOM-CONCEPT-ONLY | Hides VAH shorts below POC and VAL longs above it. |
| A21 | SCB:287-289 | Above VAH: shorts AND longs offered | rule | CE:172-174 says SHORTS only | - (Q39: above value the market is 'a bit out of control') | NO-SOURCE | Only short left is prior_day_close (A26); rest are longs (LBL A2a). |
| A22 | SCB:290-291 | Below VAL: LONGS ONLY, no short of any kind | rule | CE:173 (no quote) | - (Q14: below a value level 'very often it accelerates') | NO-SOURCE | Longs into breakdowns, then vetoed (V04, V05). CE:231-232 says counter-trend is INVALID in acceleration. |
| A23 | SCB:263-281 | 'balance' only if VWAP flat/sideways AND CVD flat AND price in VA | rule | CE:26-49 | Q28 (balance vs trend by quick watch), Q15, Q40 (sideways VWAP); no CVD condition | TOM-CONCEPT-ONLY | Sets CT eligibility. Uses thresholds M06, M08. |
| A24 | SCB:278-279 | 'trend_healthy' when outside VA (or CVD 'aligned') | rule | CE:27 | - (Q29: unhealthy = no liquidity at the extreme) | NO-SOURCE | Above VAH always trend_healthy, which blocks VAH shorts (A25). 'aligned' never emitted (MDS:682-688). |
| A25 | SCB:277,442,444-456 | trend_unhealthy = CVD 'divergent' (never emitted); 'transition' (never produced); POC zones set up only in trend_unhealthy; VAH/swing-high: ct_short only, blocked in trend_healthy | rule | CE:42-46 admits unreachable (B063); CE:108-110 | Q13 (short up here); Q29, Q21 (no divergence definition); market_state_rules.md:290 avoids CT 'without proof' in healthy trend | TOM-CONCEPT-ONLY | Dead code: POC zones never set up. VAH shorts vanish above VAH (blocked outright). |
| A26 | SCB:448-450,470-472 | VAL/swing-low: ct_long never blocked by state. prior_day_close: ct_short and ct_long in any state | rule | CE:109,116 | Q13 (long down here); Q32 (yesterday's close = rejection) | TOM-CONCEPT-ONLY | Longs survive every state, shorts do not. |
| A27 | SCB:458-466 | VWAP and +-1s/+-2s bands: scalp both ways in balance; tc_long in trend_healthy; no tc_short | rule | CE:111 | Q15: scalp only if VWAP sideways; Q51: TC with trending VWAP; no sigma (Q16) | TOM-CONCEPT-ONLY | No short TC below VWAP in a downtrend. |
| A28 | SCB:467-469 | FVG zone: no setup (exit only) | rule | CE:112 | Q27: exit point in some scenarios | TOM-CONCEPT-ONLY | FVG never trades or targets. |
| A29 | SCB:305-349,366-383 | Zone list: weekly/daily/4h VP, prior-day VP and close, VWAP+bands, 1h/15m/5m swings, FVG, naked POCs (rank 11) | list | CE:106-135 | Q49, Q13, Q07, Q16; Q42 (naked POC is a target) | TOM-CONCEPT-ONLY | Naked POC zones set up nothing (A25). |

## 3. B. Proofs (SCB detectProofs; counted SCB:547-567)

| id | file:line | what it is | value | claimed source | Tom source | verdict | impact |
|---|---|---|---|---|---|---|---|
| P01 | SCB:652-692 | Rejection wick: a bar in last 20 touches the zone, closes back through | 20 bars | CE:335 | Q53; no bar count | TOM-CONCEPT-ONLY | 1 point. |
| P02 | SCB:673-676,549 | Wick quality STRONG (>80%/<20% body), MODERATE (>50%/<50%), else WEAK; all count | 0.8/0.2/0.5 | - | - | NO-SOURCE | A WEAK wick is a full point. |
| P03 | SCB:694-718 | Absorption: last 10 bars within 0.1%, volume >2.0x mean20, range <0.3 ATR14, delta opposite candle; strong >5x | 10; 0.1%; 2.0; 0.3; 5 | CE:332 | Q20: large buyer absorbing; no numbers | TOM-CONCEPT-ONLY | 1 point. |
| P04 | SCB:720-735 | Finished auction: /delta/ >3.0x mean (20 bars), next bar reverses, next /delta/ <0.5x | 20; 3.0; 0.5 | CE:334 'Zero on one side' | Q19, Q45: zero volume on one side of the footprint at the extreme; code is a delta proxy | TOM-CONCEPT-ONLY | 1 point, only if the exhausted side opposes the trade (SCB:554). |
| P05 | SCB:737-765 | Delta flip: 1m delta changes sign within 0.1% of zone, last 20 bars | 20; 0.1% | CE:331 | Q37: aggressive sellers plus falling cumulative delta; no 1m sign rule | TOM-CONCEPT-ONLY | 1 point. |
| P06 | SCB:767-779 | Volume spike: last 1m volume >2.0x mean of 240 bars, close within 0.1% | 2.0; 240; 0.1% | CE:64-72 (KEe_CWHyuSg T4) | Q18: exhaustion 'seen with a volume spike'; no multiple | TOM-CONCEPT-ONLY | 1 point. |
| P07 | SCB:781-802,609 | Speed: min(10, 3 x ATR14/ATR prior20 + 2 x run of bars >1.5x mean); picking up >5; regimes 3/6/10 | 3;2;1.5;5 | CE:236 '[CRYPTO HACK - PROXY, NOT TOM]' | Q41, Q23; entry_timing_triggers.md:739 'no numerical threshold' | TOM-CONCEPT-ONLY | Not counted since D4 (SCB:559). |
| P08 | SCB:804-816 | CVD aligned: session CVD slope agrees with 1m net delta (1h slope tiebreak) | rule | CE:336-360 | Q37; Q21: never trade cumulative-delta divergence alone | TOM-CONCEPT-ONLY | 1 point. |
| P09 | SCB:561-566,819 | Book counts if bid/ask >1.5 (long) or <0.67 (short); 0.0 ignored | 1.5 / 0.67 | - | - (Q22: Tom reads single large orders, not an aggregate ratio) | NO-SOURCE | 1 point. A third threshold pair (see B01, B02). |
| P10 | SCB:547-567 | Proof count: one point each of 7, equal weights, speed excluded | max 7 | CE:328-346 weights (unused) | Q33, Q34: idea plus proof, wait for proof; no count or weight | TOM-CONCEPT-ONLY | Feeds V02. Offline max 6 (BT:14). |

## 4. C. MarketDataSnapshot.java (MDS)

| id | file:line | what it is | value | claimed source | Tom source | verdict | impact |
|---|---|---|---|---|---|---|---|
| M01 | MDS:522-524,144,1066 | Profile bin: max(50 bins, range/5); fixed 10.0 post-funding | ~$5 / $10 | MDS:144 '[SCREENER] ... no citation' | - | DATA-PLUMBING | Resolution of POC/VAH/VAL. |
| M02 | MDS:48-101 | Windows: daily = since 00:00 UTC; weekly = since Monday 00:00 UTC; 4h = last UTC 4h block; prior day = previous UTC day | UTC | zone_identification_rules.md:529 gap | Q49: daily, weekly, intraday profiles of futures sessions; no 4h, no UTC day | TOM-CONCEPT-ONLY | Daily VA is partial early in the UTC day. 4h profile has no Tom match. |
| M03 | MDS:570-578 | Shape TWOPEAK if 2nd-highest bin > 0.6 x POC bin | 0.6 | CE:30 'TWOPEAK (bell) = Balance'; MDS:574-577 'NOT Tom's B' | - (Tom's shapes: B Q24, Q50, and P) | NO-SOURCE | AH E-002: any profile wider than ~1 bin reads TWOPEAK (live 577/577). Printed as STATE on every card and popup (V09). classifyState ignores it. |
| M04 | MDS:579-586 | Else D if left/right volume ratio in (0.8, 1.2), else P | 0.8/1.2 | - | - (Q50: P and B are drawn shapes) | NO-SOURCE | Label only; 'B' never emitted (CE:331). |
| M05 | MDS:595-613 | HVN/LVN: smoothing max(3, bins/20), local extrema, top 3 | 3; /20; 3 | CE:333 | Q55, Q54 | TOM-CONCEPT-ONLY | Not read by SCB, MOB, VRD: no trade effect. |
| M06 | MDS:618-646 | VWAP from 00:00 UTC; slope = 2nd-half mean vs 1st-half mean; +-0.05% -> rising/falling else flat | 0.0005 | - | Q15, Q40: sideways VWAP; no threshold | TOM-CONCEPT-ONLY | 'flat' gates balance (A23), scalp zones (A27, B07). |
| M07 | MDS:650-653 | VWAP bands +-1, +-2 volume-weighted sigma | 1, 2 | entry_timing_triggers.md:748 '[CRYPTO HACK] untested' | Q16: price ranges from VWAP; no width | TOM-CONCEPT-ONLY | Band zones at 0.2% cap. |
| M08 | MDS:658-688 | CVD slope: mean of last 20 session-CVD points vs prior 20; > +-2% -> rising/falling (needs 40) | 0.02; 20/20 | - | Q37, Q21; no threshold | TOM-CONCEPT-ONLY | Drives A23, V04, V05, P08. |
| M09 | MDS:694-699 | cvd_recent 1h (60 bars), 4h (240): /delta/ > 0.001 base units | 0.001 | - | - | NO-SOURCE | Unit-dependent; tiebreak in P08 (SCB:810-815). |
| M10 | MDS:704-736 | Swing levels: lookback 1w 2, 1d 7, 4h 3, 1h 24, 15m 16, 5m 12 bars; last close-pivot else extreme | 2/7/3/24/16/12 | - | Q07, Q08 (last low/liquidity); no lookback | TOM-CONCEPT-ONLY | These are the stops (A05). |
| M11 | MDS:737; SCB:335-349,102-109 | Swing 'stale' if swing_high < price or swing_low > price; stale swings leave the zone list and force the 0.2% stop | rule | comment B065 | - | NO-SOURCE | Trending days get A04's fallback. |
| M12 | MDS:199-214 | Book ratio = bid/ask notional within +-1% of price, 100 levels; fetch failure leaves 0.0 | 1%; 100; 0.0 | - | - (Q22) | NO-SOURCE | AH E-001: failed fetch vetoes every long (B02). Archive mode writes 0.0 (MDS:1169). |
| M13 | MDS:283-289 | price_vs_va, price_vs_poc from the developing daily profile | rule | CE:170-178 | Q39, Q13 | TOM-CONCEPT-ONLY | See M02. |
| M14 | MDS:246,259-283,922-952 | Context flags: speed_picking_up (15 vs 45 bars, 1.5x); volume_spike_at_level (48 5m bars, $1, 2x); rejection_wick_at_zone (wick >2x body, +-0.1%) | 1.5; 2; 2 | CE:236 (speed 'CRYPTO HACK'); CE:64-72 | Q41, Q18; none for the wick flag | TOM-CONCEPT-ONLY | speed doubles caps in MOB path (MTH:39) and suppresses scalp popups (B07). |

## 5. D. math_object_builder.py (MOB), mts_math.py (MTH)

| id | file:line | what it is | value | claimed source | Tom source | verdict | impact |
|---|---|---|---|---|---|---|---|
| B01 | MOB:395-396 | Short vetoed if book imbalance > 3.0 | 3.0 | comment BUG-008 (MOB:388) | - (Q22) | NO-SOURCE | SETUP_FORMING capped at WATCH (V03). |
| B02 | MOB:389,402-403 | Long vetoed if book imbalance < 0.33; missing key defaults 1.0 | 0.33 | BUG-008 | - | NO-SOURCE | AH E-001: 0.0 (archive or failed fetch) vetoes every long; 19 of 19 SETUP_FORMING in BT are short (BT:55; LBL 0.1). |
| B03 | MOB:393,400 | Finished-auction direction veto | rule | BUG-008 | Q19, Q45 | TOM-CONCEPT-ONLY | Same downgrade. |
| B04 | MOB:397,404 | last_3_delta all positive (short) / all negative (long) veto | 3 bars | BUG-008 | - | NO-SOURCE | Same downgrade. |
| B05 | MOB:186-270,358-363 | Legacy zone stop/target (nearest POC/VWAP; swing TF default 5m); top flag reads SCB net_rr_sanity | rule | 'Tom principle' | Q03, Q07 | TOM-CONCEPT-ONLY | Advisory fields; top flag repeats A13. |
| B06 | MTH:52-67 | Trigger validity: CT/TC/scalp only at_zone (0.1%); BO only beyond | rule | CE:282-300 | - | TOM-CONCEPT-ONLY | Fills zone_math only. |
| B07 | MTH:332-345,463-495; PS1:654-695 | Scalp popup gate: VWAP slope sideways/flat AND speed_picking_up False AND funding_reset_window False (missing = suppress); STATE copy of A23-A25 | 3 tests | CE:404-408 'Funding reset windows... NOT hard stops' | VWAP sideways: Q15 (alone TOM-SOURCED). Speed, funding: - | NO-SOURCE | Suppresses scalp popups; funding test contradicts CE:404-408. |

## 6. E. verdict.py (VRD), start-trading-day.ps1 (PS1): what fires; compiled_engine.md (CE)

| id | file:line | what it is | value | claimed source | Tom source | verdict | impact |
|---|---|---|---|---|---|---|---|
| V01 | VRD:110-121; PS1:204-215 | Order: net R:R fail WAIT_RR; tier ignore WAIT_FAR; conditional WAIT_TRIGGER; then proof bands | order | CE:439-463 | - (Q33: idea plus proof) | NO-SOURCE | A13 hides everything below it. |
| V02 | VRD:116-121; PS1:210-215 | proof <3 WAIT_PROOF; 3-4 WATCH; >=5 SETUP_FORMING | 3 / 5 | CE:450-452 '[SYSTEM]... Tom gives no numeric proof bands' | - (Q34: wait for proof, no count) | NO-SOURCE | Only SETUP_FORMING fires/auto-trades. 320 rows reach proof 5, 19 end SETUP_FORMING (BT:14; REV H1). |
| V03 | VRD:122-125; PS1:217-224 | Contradiction: SETUP_FORMING -> WATCH; proof-dir error -> WAIT_PROOF (fail closed) | rule | B071 | - (fail-closed is engineering safety) | NO-SOURCE | With B01-B04 kills longs when book = 0.0. |
| V04 | VRD:129-132; PS1:226-240 | Broken-value: below_val + CVD falling + long (above_vah + rising + short) -> WAIT_RR | rule | comment | Q14, Q39: below value price accelerates; no veto | TOM-CONCEPT-ONLY | Kills A22's longs. |
| V05 | VRD:133-137; PS1:242-246 | Flow veto: long + CVD falling (short + rising) -> WAIT_PROOF | rule | B058 part C | - (Q18, Q37: Tom counter-trades after proof) | NO-SOURCE | CVD usually rises into a VAH: CT shorts vetoed. |
| V06 | VRD:89-107 | 'mode' floor/ceiling within 0.15% (display only since D1(a)); top = rank <=3 (VRD:76) | 0.0015; 3 | B058; D3 | - | NO-SOURCE | None (display). |
| V07 | PS1:30-33,554,604,608 | Thresholds: price move prep 0.30% / armed 0.15% / live 0.10%; proof crossing 5; STOP NEAR and TARGET NEAR 0.15% | 0.3/0.15/0.10; 5; 0.15 | - | - | NO-SOURCE | STOP/TARGET NEAR popups fire without an actionable verdict. |
| V08 | PS1:534-542,560-569,614-621 | Verdict/STATE changes need 2 cycles; cooldown 180 s any, 900 s per setup/zone | 2; 180 s; 900 s | B058 part D | - | NO-SOURCE | Delays and suppresses popups. |
| V09 | PS1:155,559-569,623-628 | Popup if SETUP_FORMING/CONFIRMED and changed, or reason STATE, ADVERSE, STOP NEAR, TARGET NEAR; STATE text = vp_shape/price_vs_va | rule | - | - | NO-SOURCE | TWOPEAK (M03) toggles STATE popups (LBL 0.3). |
| V10 | PS1:589-600,630-652 | ADVERSE FLOW popup on state_code L/S; open position suppresses WATCH and same-direction SETUP_FORMING, elevates opposite | rule | B062 | - (Q48: Tom adds to a position at the breakout); state_code not audited | NO-SOURCE | Suppresses same-direction alerts. |
| V11 | PS1:572-584,500-516 | state_code older than 90 s; position file older than 86400 s ignored | 90 s; 86400 s | - | n/a | DATA-PLUMBING | Freshness. |
| V12 | VRD:110-125; CE:442-459 | Verdict labels WAIT_RR/FAR/TRIGGER/PROOF, WATCH, SETUP_FORMING, SETUP_CONFIRMED (unreachable) | labels | CE:442-459 | - | NO-SOURCE | Names. |
| K01 | CE:427 | 'CT target R:R 3:1 example (Tom's profit-securing level)' | 3:1 | BVpYGKz9PBU | Q36, Q35 | TOM-SOURCED | Example only; not in code. |
| K02 | CE:231 | 'Tom never lowers R:R minimum for any condition' | claim | - | - (Q05, Q46) | NO-SOURCE | See A11, A13. |

## 7. Execution-safety candidates (MTS_USER_GUIDE.md section 4 'Plan rules'; not judged)

The operator decides whether these are exempt. Listed as written.

| id | file:line | rule | value |
|---|---|---|---|
| X1 | MTS_USER_GUIDE.md:149 | Size | multiples of 10 USD; total at most 10,000 USD |
| X2 | MTS_USER_GUIDE.md:150 | Max loss per plan | at most 500 USD |
| X3 | MTS_USER_GUIDE.md:151 | Stop | fixed % from entry; no trailing, no breakeven (also a trade-management rule) |
| X4 | MTS_USER_GUIDE.md:152 | Plans at once | one; refused if a position or order is open |
| X5 | MTS_USER_GUIDE.md:153 | Validity | a plan trades only inside its time window |
| X6 | MTS_USER_GUIDE.md:99-103,128 | Defaults and limit wait | size 100, stop 2.0%, targets 2,5 %, max loss 50 USD, 2 h; limit entries wait up to 10 min |
| X7 | MTS_USER_GUIDE.md:173-177 | Auto-trader sizing | Tom setups: limit at zone, 200 USD, max loss 25 USD; layers: market, stop 1%, target 2%, 100 USD, max loss 10 USD; one trade at a time |
| X8 | MTS_USER_GUIDE.md:189 | Daily loss brake | over 500 USD: close all, pause the day |

Pointers only for X3: risk_protocol.md 'Do NOT move stop prematurely' (4MoNjEQ2Dd8 END); Tom trails a stop in kXhIAug0Gh8 MIDDLE; CE:679-695 (12.10).

## 8. NO-SOURCE items ranked by impact on Tom trades

| rank | rows | item | impact |
|---|---|---|---|
| 1 | A10, A08, A09 | Target window 2.0-3.5R, nearest-level pick | Kills Tom's 8.1R trade; 80,847 of 120,892 rows WAIT_RR; nothing past 3.5R is seen. |
| 2 | A13, A12 | Net R:R >= 2.0 after flat 25%, cited to qLnQan0KGmQ | Miscited; leaves the band [2.67, 3.5]R. Tom's gate is his own hit rate (Q05). |
| 3 | A03 | 0.1% stop floor reset to 0.2% | Removes Tom-size stops (12 ticks is about 0.04%). |
| 4 | A04, M11 | 0.2% fallback stop | Median stop in every variant; the test measures a constant. |
| 5 | V02 | Proof bands 3 and 5 (5 of 7, equal weight) | Only SETUP_FORMING fires; 19 signals in 4.7 years. |
| 6 | B01, B02, M12 | Book veto 3.0/0.33 with 0.0 default | Every long at proof 5 becomes WATCH when book is 0.0; 19 of 19 short. |
| 7 | A22, V04, V05 | No shorts below VAL; broken-value and flow vetoes | Longs into breakdowns, then vetoed; Tom: breaks accelerate (Q14). |
| 8 | A18, A19 | 0.1% tier and caps 0.2-0.5% | Drop zones; WAIT_TRIGGER, WAIT_FAR. |
| 9 | A24, A21 | trend_healthy outside VA; above-VAH offers longs | Blocks VAH shorts above VAH; contradicts CE:172. |
| 10 | M03, M04, V09 | TWOPEAK 0.6 and D/P 0.8-1.2 labels | No trade effect; every STATE popup reads TWOPEAK (AH E-002). |
| 11 | A14, A15 | +10 bonus; score 50/7/95, bands | Chooses the 'top' candidate. |
| 12 | P02, P09, B04, M09 | Weak wick counts; book 1.5/0.67; last-3 veto; 0.001 CVD unit | Inflate or veto the proof count. |
| 13 | V07, V08, V10, B07 | Popup thresholds, cooldowns, debounce, scalp gate, position suppression | Decide which alerts reach the operator. |
| 14 | A11, K02 | Gross >= 1.5; 'Tom never lowers R:R minimum' | Redundant; unsupported claim. |

## 9. TOM-CONCEPT-ONLY: what Tom says, and a Tom-sourced replacement

'Gives no number' means: needs a Tom-sourced rule or removal (operator decision).

| rows | what Tom says | replacement |
|---|---|---|
| A02 | Q25: overlaps = nodes, VA highs, several POCs in one price range | Gives no number. Drop 0.3% and the bonus. |
| A05, M10 | Q07, Q08: long stop below last low/liquidity. Q09: short stop not above the high, at the largest-volume level | Stop at the highest-volume node inside the range (Q09, needs volume-at-price); long below the last low. Ticks or percent not given. |
| A06 | Q30, Q43: carry levels to a smaller chart | Gives no TF pairs. |
| A07 | Q03, Q12, Q44: next/last largest high-volume price; VWAP for scalps | Nearest HVN or POC in trade direction, VWAP for scalps. Remove prior-day high/low and the window. |
| A12 | Q06: fees enter the break-even hit rate | Charge the real fee in R (fee / stop width) instead of 25%. Tom gives no fee. |
| A16 | Q43: higher time frame first | Keep the order, drop the numeric ranks. |
| A20, A26 | Q13: short up here, long down here; Q32: yesterday's close | VAH short and VAL long symmetrically; no POC-side gating. |
| A23, B07 | Q28, Q15, Q40: balance vs trend by quick watch; sideways VWAP | Gives no number; needs a Tom-sourced rule or hand labelling. Drop the CVD-flat term. |
| A25 | Q13; Q29, Q21: no divergence definition; CT needs proof | CT needs proof, not a state block; unhealthy trend has no rule yet. |
| A27 | Q15, Q51: scalp only with sideways VWAP; TC with trending VWAP | Keep scalp-in-sideways; add tc_short; drop sigma bands (no width, Q16). |
| A28, A29 | Q27: FVG is an exit; Q42: naked POC is a target | Targets only. |
| M02, M13 | Q49: daily, weekly, intraday profiles | Gives no UTC or 4h definition; operator must fix the session. |
| P01 | Q53: rejection | Keep; drop the 20-bar window. |
| P03 | Q20: a large buyer absorbing | Needs order-book or footprint data; 1m proxy has no Tom number. |
| P04 | Q19, Q45: zero volume on one side at the extreme | Zero bid or ask at the extreme price per bar (aggTrades); relabel the delta proxy. |
| P05, P08, M08 | Q37, Q21: cumulative delta; never alone | Gives no number. |
| P06, M14 | Q18: exhaustion with a volume spike; Q41, Q23: speed | Give no multiple or speed number (entry_timing_triggers.md:739). |
| P07 | Q41, Q23 | Gives no number. |
| P10 | Q33, Q34: idea plus proof | No count: proof as an operator yes/no until a Tom rule exists. |
| M05 | Q55, Q54: volume nodes | No trade effect; keep as data. |
| M06, M07 | Q15, Q40, Q16: sideways VWAP; price ranges from VWAP | Gives no slope or width. |
| B03, B05, B06 | Q19, Q45, Q03, Q07 | As the rows above. |
| V04 | Q14, Q39: below value, price accelerates | Trade with the break (CE:224-232 says so); no number given. |

## 10. Not audited

MDS open interest, funding, session timing, liquidation, alignment check, FvgCalculator; NakedPocTracker; ArchiveHistoricalSource (gitignored); state_code/quad_classify (V10). Line numbers are from the working tree of 2026-09-30.

## 11. Quotes (verbatim; T/ = raw_transcripts_canonical/<id>_raw.txt, line@char)

> "You have to know the risk of reward ratio very good."
Q01 **Source GPS: qLnQan0KGmQ | BEGIN** T/qLnQan0KGmQ:19@135

> "even if we're only right every second or third time with such a trade, we have a huge risk reward ratio"
Q02 **Source GPS: qLnQan0KGmQ | END** T/qLnQan0KGmQ:19@7073

> "if it accepts new prices, then it looks for the next high volume price and that is your target."
Q03 **Source GPS: qLnQan0KGmQ | END** T/qLnQan0KGmQ:19@7547

> "roughly a little more than 2 to one. And now comes the crucial part. How high does your hit rate need to be in order to make money with this?"
Q04 **Source GPS: k0zm5NYn0IQ | END** T/k0zm5NYn0IQ:19@18828

> "you have to know your hit rate, and then through your hit rate and the minimum usable risk-reward ratio, you can know, I have to trade at least up to here"
Q05 **Source GPS: 43JaKHRvxHk | END** T/43JaKHRvxHk:19@8040

> "If we had a riskreward ratio of 1: one, you would need at least 51% without order fees just to break even."
Q06 **Source GPS: 3JqMyzE8jIQ | MIDDLE** T/3JqMyzE8jIQ:0@0

> "Then I immediately know all right my stop loss belongs below the last liquidity."
Q07 **Source GPS: 3o1VVsfBmmU | MIDDLE** T/3o1VVsfBmmU:19@6014

> "The stop loss goes below the last low here and my take-profit is set above the highs."
Q08 **Source GPS: 4MoNjEQ2Dd8 | BEGIN** T/4MoNjEQ2Dd8:19@763

> "It doesn't belong above the high. Why is that?"
Q09 **Source GPS: yRvMW6lgN1o | MIDDLE** T/yRvMW6lgN1o:19@6182

> "with a stop-loss up here, we now have a risk of 12 ticks. We have a profit of 97 ticks."
Q10 **Source GPS: yRvMW6lgN1o | END** T/yRvMW6lgN1o:19@8864

> "my stop loss in this case let's say is 10 ticks and my profit run in this case let's say is 70 ticks. That makes a riskreward ratio of seven."
Q11 **Source GPS: 3o1VVsfBmmU | MIDDLE** T/3o1VVsfBmmU:19@5649

> "the profit target should be where the last largest volumes occurred."
Q12 **Source GPS: tS6ZEiHj8gQ | MIDDLE** T/tS6ZEiHj8gQ:19@6115

> "And that means for me, I can definitely look for short trades up here and long trades down here."
Q13 **Source GPS: BVpYGKz9PBU | BEGIN** T/BVpYGKz9PBU:19@3814

> "what happens when the market falls below such a level. Very often it accelerates at first."
Q14 **Source GPS: YmygDgtoxO8 | MIDDLE** T/YmygDgtoxO8:19@7189

> "Only if the VWAP is currently oriented sideways, and I can't assume a maximally brutal breakout now or a trend day from the market open, then I can use this whole model for myself."
Q15 **Source GPS: 43JaKHRvxHk | END** T/43JaKHRvxHk:19@6887

> "You can define so-called price ranges from the VWAP where you expect a reaction."
Q16 **Source GPS: 43JaKHRvxHk | MIDDLE** T/43JaKHRvxHk:19@5124

> "As a rule, you use 68.2 or 70% of all trades of the day and say that where 70% of the highest trading volume occurred is the so-called value area."
Q17 **Source GPS: aursfDVYzUk | MIDDLE** T/aursfDVYzUk:0@0

> "absolute exhaustion is seen with a volume spike, or a lot of volume is suddenly generated at one price level"
Q18 **Source GPS: KEe_CWHyuSg | END** T/KEe_CWHyuSg:0@0

> "Such a finished auction. So, a completed auction, this gives you the overview that the market was done here."
Q19 **Source GPS: oa8kxSLLkAo | BEGIN** T/oa8kxSLLkAo:19@5111

> "It means that there is a very large buyer here who is absorbing everything that's being sold."
Q20 **Source GPS: y67l86cSqb8 | MIDDLE** T/y67l86cSqb8:19@6249

> "Never combine such a divergence based solely on cumulative data divergence."
Q21 **Source GPS: rFPCtOcfUMI | END** T/rFPCtOcfUMI:0@0

> "big orders in the book, so large thick orders, where I already know that the probability is very high that it will drive the market further up."
Q22 **Source GPS: -dMWA_bbm3o | END** T/-dMWA_bbm3o:0@0

> "And now look at the speed. This is crucial."
Q23 **Source GPS: 4MoNjEQ2Dd8 | END** T/4MoNjEQ2Dd8:19@20568

> "here is a B profile and that shows me that there is weakness in the market."
Q24 **Source GPS: BVpYGKz9PBU | MIDDLE** T/BVpYGKz9PBU:19@5746

> "These are interesting overlap levels."
Q25 **Source GPS: YmygDgtoxO8 | END** T/YmygDgtoxO8:19@10251

> "When can you use such fair value gaps as counter trading ideas? When should you rather use them only as exit points?"
Q27 **Source GPS: 3JqMyzE8jIQ | BEGIN** T/3JqMyzE8jIQ:0@0

> "are we currently more in balance or are we more in a trend right now? You can pinpoint that by counting closing prices"
Q28 **Source GPS: 3o1VVsfBmmU | BEGIN** T/3o1VVsfBmmU:19@786

> "The idea was that this trend isn't entirely healthy."
Q29 **Source GPS: zQTbdEweG3c | END** T/zQTbdEweG3c:19@7814

> "And these support resist levels, I simply transfer them into my smaller charts."
Q30 **Source GPS: -dMWA_bbm3o | MIDDLE** T/-dMWA_bbm3o:0@0

> "most traders on the 1-minute chart take the risk below the last low."
Q31 **Source GPS: zAwEX_tRUfE | MIDDLE** T/zAwEX_tRUfE:0@0

> "here for example was yesterday's closing price. This is where the market ended for yesterday."
Q32 **Source GPS: rrHj24GSR6M | END** T/rrHj24GSR6M:0@0

> "And you always need two things, the idea and the proof."
Q33 **Source GPS: qLnQan0KGmQ | END** T/qLnQan0KGmQ:19@7726

> "Sure, the very brave ones just buy here, but you can also wait until the proof arrives."
Q34 **Source GPS: qLnQan0KGmQ | MIDDLE** T/qLnQan0KGmQ:19@4652

> "even with a hit rate of 30 to 40% you have an average riskreward ratio of greater than three"
Q35 **Source GPS: BVpYGKz9PBU | END** T/BVpYGKz9PBU:19@14525

> "if I secure my initial profits at a riskreward ratio of precisely 3:1"
Q36 **Source GPS: BVpYGKz9PBU | END** T/BVpYGKz9PBU:19@13118

> "If you then see aggressive sellers there and the cumulative delta drops, then that's also an entry signal for a reversal."
Q37 **Source GPS: rFPCtOcfUMI | END** T/rFPCtOcfUMI:0@0

> "as long as we're above it the market is, let's say, a bit out of control."
Q39 **Source GPS: 4MoNjEQ2Dd8 | MIDDLE** T/4MoNjEQ2Dd8:19@11925

> "the VWAP can be very sideways oriented."
Q40 **Source GPS: 43JaKHRvxHk | END** T/43JaKHRvxHk:19@8364

> "The speed is picking up. Look at what's being bought here. And now comes the breakout."
Q41 **Source GPS: 4MoNjEQ2Dd8 | END** T/4MoNjEQ2Dd8:19@21044

> "I can analyze naked PC's for myself."
Q42 **Source GPS: YopZ5ZDmMFw | MIDDLE** T/YopZ5ZDmMFw:0@0

> "So I move to a higher time frame and look at this price area"
Q43 **Source GPS: 3o1VVsfBmmU | MIDDLE** T/3o1VVsfBmmU:19@5107

> "if I were to only ever take the trade up to the VWAP, I can already see those are very modest profit targets."
Q44 **Source GPS: 43JaKHRvxHk | END** T/43JaKHRvxHk:19@6130

> "there was only one side of the price with a number greater than zero."
Q45 **Source GPS: oa8kxSLLkAo | BEGIN** T/oa8kxSLLkAo:19@4927

> "riskreward ratio of let's say about it's twice as big 2:1 yeah but now I also need to know what is my hit rate"
Q46 **Source GPS: 3JqMyzE8jIQ | MIDDLE** T/3JqMyzE8jIQ:0@0

> "Both were done with limit orders. So you could have basically ignored the market"
Q47 **Source GPS: yRvMW6lgN1o | END** T/yRvMW6lgN1o:19@10311

> "I'll add to the position again at the breakout."
Q48 **Source GPS: 4MoNjEQ2Dd8 | BEGIN** T/4MoNjEQ2Dd8:19@3613

> "I now have the opportunity to establish my business zones using the intraday profiles."
Q49 **Source GPS: -dMWA_bbm3o | MIDDLE** T/-dMWA_bbm3o:0@0

> "such a B profile is always the first sign for me that there has definitely been strong and aggressive selling here."
Q50 **Source GPS: rFPCtOcfUMI | MIDDLE** T/rFPCtOcfUMI:0@0

> "You should then definitely only look for a trend continuation setup here."
Q51 **Source GPS: 43JaKHRvxHk | MIDDLE** T/43JaKHRvxHk:19@4748

> "That's a rejection too. That's a simple rejection."
Q53 **Source GPS: rFPCtOcfUMI | END** T/rFPCtOcfUMI:0@0

> "where high volume occurs, we often see a reaction when a market returns there."
Q54 **Source GPS: NkQeOVDTAec | BEGIN** T/NkQeOVDTAec:19@2647

> "Then in addition there are the so-called low volume areas, low volume nodes."
Q55 **Source GPS: YmygDgtoxO8 | MIDDLE** T/YmygDgtoxO8:19@5398

