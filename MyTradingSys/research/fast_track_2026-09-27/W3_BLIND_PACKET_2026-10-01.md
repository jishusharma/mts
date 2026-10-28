# W3 BLIND PACKET 2026-10-01 (for a reader who has NOT seen PROVENANCE_AUDIT_TOM.md)

Written by MTS-2026-10-01-1604Z-CLD-ANA-revalidate-tom-fabio. Purpose: let a clean second reader re-derive the 74 provenance verdicts
for Cohen's kappa (threshold 0.6). The packet is the first reader's table with the Tom-source, verdict and impact columns removed;
the "claimed source" column is kept because it is part of the rule text.

Reader conditions (all required, or the kappa is not valid):
1. Do not open PROVENANCE_AUDIT_TOM.md, AUDIT_REVIEW_2026-10-01.md, REVALIDATION_REQUEST_2026-10-01.md, HANDOFF_FOR_CLAUDE_2026-10-01.md,
   REVALIDATION_ACTIONS_2026-10-01.md, or any file under extracts/ that names a TOM verdict before you finish.
2. Search the raw transcripts yourself: raw_transcripts_canonical/<id>_raw.txt (Tom's ids: the 57 ids found in the filenames under extracts/fresh/ and extracts/processed/tom/ and in
   research/TOM_VERBATIM_INDEX.md, by this session's count; or search all 102 files and mark the speaker). A quote counts only if it states the idea or the number.
3. Use these definitions, and only these (first reader's, verbatim): TOM-SOURCED = a quote supports the value. TOM-CONCEPT-ONLY = Tom names
   the idea, the code measures it by proxy, the number is ours. NO-SOURCE = no Tom idea behind it, or it plays a role (veto, gate, cap)
   Tom never gives it. DATA-PLUMBING = no trading meaning.
4. Write one line per row to a CSV `id,verdict` (verdict spelled as above) and run:
   `python scripts/dev/kappa_check.py first.csv second.csv` (first.csv = the 74 verdicts from PROVENANCE_AUDIT_TOM.md section 2-6, copied by the operator).
5. Report kappa and the list of disagreeing rows. kappa < 0.6 means the headline 36 NO-SOURCE is reader-dependent.

| id | file:line | what it is | value | claimed source |
|---|---|---|---|---|
| A01 | SCB:44; MDS:24,553-565 | Share of volume in the value area | 0.70 | - |
| A02 | SCB:45,201,493-506; MTH:78; MOB:344 | Zones this close count as confluence | 0.3% | CE:158,250 |
| A03 | SCB:46,119-124 | Stop closer than this to the zone is replaced by zone x1.002 / x0.998 | 0.1% -> 0.2% | comment 'v1.3.3 floor', 'Rule 32: 100 of 750 candidates' |
| A04 | SCB:113,116,123 | Fallback stop when no swing lies beyond the zone | 0.2% | comment |
| A05 | SCB:111-117 | Stop at the swing extreme beyond the zone | swing | CE:150,423; MOB:186-199 'Tom principle' |
| A06 | SCB:476-483; MOB:186-198 | Swing timeframe used for the stop | weekly 1h; daily/4h/prior-day 15m; vwap/fvg/5m 5m; default 15m | MOB:186-196 |
| A07 | SCB:126-147 | Target pool: POC weekly/daily/4h/prior day; opposite VAL/VAH; prior-day low/high; VWAP | list | CE:424 |
| A08 | SCB:150 | Minimum target distance | 2.0 x stop | comment '2x stop filter' |
| A09 | SCB:151 | Maximum target distance | 3.5 x stop | - |
| A10 | SCB:153-175 | Target = NEAREST pool level inside [2.0, 3.5]R, else candidate dropped | nearest | - |
| A11 | SCB:183; MTH:74-75 | Gross R:R >= 1.5 or candidate removed | 1.5 | CE:154,231,414-418 ('Tom never lowers R:R minimum') |
| A12 | SCB:182; ExecutionMathConstants.java:34; MTH:70-72; CE:153,429 | Friction: net = gross x 0.75 | 25% | CE:429 'System rule (Tom never addresses slippage)' |
| A13 | SCB:184; VRD:110-111; PS1:169,204; CE:397,426 | Net R:R >= 2.0 ('2:1 NET') or verdict WAIT_RR | 2.0 | CE:426 and entry_timing_triggers.md:65,730 cite qLnQan0KGmQ |
| A14 | SCB:201 | Confluence bonus to score | +10 | CE:159,251 say no numeric bonus |
| A15 | SCB:213-218 | Score 50 + 7 x proofs + bonus, cap 95; bands B>=70, C+>=55, C>=40 | 50/7/95/70/55/40 | CE:442 'Tom does not use numeric scoring bands' |
| A16 | SCB:222-225,307-349 | Tie-break by zone TF rank | weekly 10, daily 9, 4h 7, vwap 6, prior-day 5, 1h 4, 15m 3, 5m 2, fvg 1, naked 11 | SCB:18; CE:136 |
| A17 | SCB:47,51,229 | Output cap 3; needs 20 one-minute bars | 3; 20 | - |
| A18 | SCB:66-75; MTH:43-49; MTH:16-22; SCB:239-244 | Tier: <=0.1% trigger_ready, <=cap conditional, beyond cap dropped; at_zone substate 0.1% | 0.1% | CE:164,238; CE:280 '0.1% is a system invention... Tom does not specify exact thresholds' |
| A19 | SCB:428-437; MTH:25-40; CE:206-215 | Distance caps by zone type | weekly 0.5%; daily/pf/4h/prior-day 0.4%; 1h swing 0.5%; 15m/5m swing 0.3%; vwap, bands, fvg 0.2%; default 0.4% | CE:206-215 'Rationale' column |
| A20 | SCB:283-303 | In value area: short if price above POC, long if below, both at POC | rule | CE:170-200 |
| A21 | SCB:287-289 | Above VAH: shorts AND longs offered | rule | CE:172-174 says SHORTS only |
| A22 | SCB:290-291 | Below VAL: LONGS ONLY, no short of any kind | rule | CE:173 (no quote) |
| A23 | SCB:263-281 | 'balance' only if VWAP flat/sideways AND CVD flat AND price in VA | rule | CE:26-49 |
| A24 | SCB:278-279 | 'trend_healthy' when outside VA (or CVD 'aligned') | rule | CE:27 |
| A25 | SCB:277,442,444-456 | trend_unhealthy = CVD 'divergent' (never emitted); 'transition' (never produced); POC zones set up only in trend_unhealthy; VAH/swing-high: ct_short only, blocked in trend_healthy | rule | CE:42-46 admits unreachable (B063); CE:108-110 |
| A26 | SCB:448-450,470-472 | VAL/swing-low: ct_long never blocked by state. prior_day_close: ct_short and ct_long in any state | rule | CE:109,116 |
| A27 | SCB:458-466 | VWAP and +-1s/+-2s bands: scalp both ways in balance; tc_long in trend_healthy; no tc_short | rule | CE:111 |
| A28 | SCB:467-469 | FVG zone: no setup (exit only) | rule | CE:112 |
| A29 | SCB:305-349,366-383 | Zone list: weekly/daily/4h VP, prior-day VP and close, VWAP+bands, 1h/15m/5m swings, FVG, naked POCs (rank 11) | list | CE:106-135 |
| P01 | SCB:652-692 | Rejection wick: a bar in last 20 touches the zone, closes back through | 20 bars | CE:335 |
| P02 | SCB:673-676,549 | Wick quality STRONG (>80%/<20% body), MODERATE (>50%/<50%), else WEAK; all count | 0.8/0.2/0.5 | - |
| P03 | SCB:694-718 | Absorption: last 10 bars within 0.1%, volume >2.0x mean20, range <0.3 ATR14, delta opposite candle; strong >5x | 10; 0.1%; 2.0; 0.3; 5 | CE:332 |
| P04 | SCB:720-735 | Finished auction: /delta/ >3.0x mean (20 bars), next bar reverses, next /delta/ <0.5x | 20; 3.0; 0.5 | CE:334 'Zero on one side' |
| P05 | SCB:737-765 | Delta flip: 1m delta changes sign within 0.1% of zone, last 20 bars | 20; 0.1% | CE:331 |
| P06 | SCB:767-779 | Volume spike: last 1m volume >2.0x mean of 240 bars, close within 0.1% | 2.0; 240; 0.1% | CE:64-72 (KEe_CWHyuSg T4) |
| P07 | SCB:781-802,609 | Speed: min(10, 3 x ATR14/ATR prior20 + 2 x run of bars >1.5x mean); picking up >5; regimes 3/6/10 | 3;2;1.5;5 | CE:236 '[CRYPTO HACK - PROXY, NOT TOM]' |
| P08 | SCB:804-816 | CVD aligned: session CVD slope agrees with 1m net delta (1h slope tiebreak) | rule | CE:336-360 |
| P09 | SCB:561-566,819 | Book counts if bid/ask >1.5 (long) or <0.67 (short); 0.0 ignored | 1.5 / 0.67 | - |
| P10 | SCB:547-567 | Proof count: one point each of 7, equal weights, speed excluded | max 7 | CE:328-346 weights (unused) |
| M01 | MDS:522-524,144,1066 | Profile bin: max(50 bins, range/5); fixed 10.0 post-funding | ~$5 / $10 | MDS:144 '[SCREENER] ... no citation' |
| M02 | MDS:48-101 | Windows: daily = since 00:00 UTC; weekly = since Monday 00:00 UTC; 4h = last UTC 4h block; prior day = previous UTC day | UTC | zone_identification_rules.md:529 gap |
| M03 | MDS:570-578 | Shape TWOPEAK if 2nd-highest bin > 0.6 x POC bin | 0.6 | CE:30 'TWOPEAK (bell) = Balance'; MDS:574-577 'NOT Tom's B' |
| M04 | MDS:579-586 | Else D if left/right volume ratio in (0.8, 1.2), else P | 0.8/1.2 | - |
| M05 | MDS:595-613 | HVN/LVN: smoothing max(3, bins/20), local extrema, top 3 | 3; /20; 3 | CE:333 |
| M06 | MDS:618-646 | VWAP from 00:00 UTC; slope = 2nd-half mean vs 1st-half mean; +-0.05% -> rising/falling else flat | 0.0005 | - |
| M07 | MDS:650-653 | VWAP bands +-1, +-2 volume-weighted sigma | 1, 2 | entry_timing_triggers.md:748 '[CRYPTO HACK] untested' |
| M08 | MDS:658-688 | CVD slope: mean of last 20 session-CVD points vs prior 20; > +-2% -> rising/falling (needs 40) | 0.02; 20/20 | - |
| M09 | MDS:694-699 | cvd_recent 1h (60 bars), 4h (240): /delta/ > 0.001 base units | 0.001 | - |
| M10 | MDS:704-736 | Swing levels: lookback 1w 2, 1d 7, 4h 3, 1h 24, 15m 16, 5m 12 bars; last close-pivot else extreme | 2/7/3/24/16/12 | - |
| M11 | MDS:737; SCB:335-349,102-109 | Swing 'stale' if swing_high < price or swing_low > price; stale swings leave the zone list and force the 0.2% stop | rule | comment B065 |
| M12 | MDS:199-214 | Book ratio = bid/ask notional within +-1% of price, 100 levels; fetch failure leaves 0.0 | 1%; 100; 0.0 | - |
| M13 | MDS:283-289 | price_vs_va, price_vs_poc from the developing daily profile | rule | CE:170-178 |
| M14 | MDS:246,259-283,922-952 | Context flags: speed_picking_up (15 vs 45 bars, 1.5x); volume_spike_at_level (48 5m bars, $1, 2x); rejection_wick_at_zone (wick >2x body, +-0.1%) | 1.5; 2; 2 | CE:236 (speed 'CRYPTO HACK'); CE:64-72 |
| B01 | MOB:395-396 | Short vetoed if book imbalance > 3.0 | 3.0 | comment BUG-008 (MOB:388) |
| B02 | MOB:389,402-403 | Long vetoed if book imbalance < 0.33; missing key defaults 1.0 | 0.33 | BUG-008 |
| B03 | MOB:393,400 | Finished-auction direction veto | rule | BUG-008 |
| B04 | MOB:397,404 | last_3_delta all positive (short) / all negative (long) veto | 3 bars | BUG-008 |
| B05 | MOB:186-270,358-363 | Legacy zone stop/target (nearest POC/VWAP; swing TF default 5m); top flag reads SCB net_rr_sanity | rule | 'Tom principle' |
| B06 | MTH:52-67 | Trigger validity: CT/TC/scalp only at_zone (0.1%); BO only beyond | rule | CE:282-300 |
| B07 | MTH:332-345,463-495; PS1:654-695 | Scalp popup gate: VWAP slope sideways/flat AND speed_picking_up False AND funding_reset_window False (missing = suppress); STATE copy of A23-A25 | 3 tests | CE:404-408 'Funding reset windows... NOT hard stops' |
| V01 | VRD:110-121; PS1:204-215 | Order: net R:R fail WAIT_RR; tier ignore WAIT_FAR; conditional WAIT_TRIGGER; then proof bands | order | CE:439-463 |
| V02 | VRD:116-121; PS1:210-215 | proof <3 WAIT_PROOF; 3-4 WATCH; >=5 SETUP_FORMING | 3 / 5 | CE:450-452 '[SYSTEM]... Tom gives no numeric proof bands' |
| V03 | VRD:122-125; PS1:217-224 | Contradiction: SETUP_FORMING -> WATCH; proof-dir error -> WAIT_PROOF (fail closed) | rule | B071 |
| V04 | VRD:129-132; PS1:226-240 | Broken-value: below_val + CVD falling + long (above_vah + rising + short) -> WAIT_RR | rule | comment |
| V05 | VRD:133-137; PS1:242-246 | Flow veto: long + CVD falling (short + rising) -> WAIT_PROOF | rule | B058 part C |
| V06 | VRD:89-107 | 'mode' floor/ceiling within 0.15% (display only since D1(a)); top = rank <=3 (VRD:76) | 0.0015; 3 | B058; D3 |
| V07 | PS1:30-33,554,604,608 | Thresholds: price move prep 0.30% / armed 0.15% / live 0.10%; proof crossing 5; STOP NEAR and TARGET NEAR 0.15% | 0.3/0.15/0.10; 5; 0.15 | - |
| V08 | PS1:534-542,560-569,614-621 | Verdict/STATE changes need 2 cycles; cooldown 180 s any, 900 s per setup/zone | 2; 180 s; 900 s | B058 part D |
| V09 | PS1:155,559-569,623-628 | Popup if SETUP_FORMING/CONFIRMED and changed, or reason STATE, ADVERSE, STOP NEAR, TARGET NEAR; STATE text = vp_shape/price_vs_va | rule | - |
| V10 | PS1:589-600,630-652 | ADVERSE FLOW popup on state_code L/S; open position suppresses WATCH and same-direction SETUP_FORMING, elevates opposite | rule | B062 |
| V11 | PS1:572-584,500-516 | state_code older than 90 s; position file older than 86400 s ignored | 90 s; 86400 s | - |
| V12 | VRD:110-125; CE:442-459 | Verdict labels WAIT_RR/FAR/TRIGGER/PROOF, WATCH, SETUP_FORMING, SETUP_CONFIRMED (unreachable) | labels | CE:442-459 |
| K01 | CE:427 | 'CT target R:R 3:1 example (Tom's profit-securing level)' | 3:1 | BVpYGKz9PBU |
| K02 | CE:231 | 'Tom never lowers R:R minimum for any condition' | claim | - |

