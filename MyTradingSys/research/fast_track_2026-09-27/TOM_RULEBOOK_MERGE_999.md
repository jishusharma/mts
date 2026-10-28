# TOM RULEBOOK MERGE PROPOSAL - DSA task 999 (redo)
Proposal only. No Tom logic or existing rule file edited. Built 2026-09-30.

## 1. Which file is the Tom master
**Master = the six files in MyTradingSys/conditions/** (risk_protocol, zone_identification_rules, entry_timing_triggers, setup_type_rules, market_state_rules, session_timing_rules). Why:
- TOM_VERBATIM_INDEX.md:4-5 says it only points to quotes; "every derived rule in MyTradingSys/conditions/ carries [TOM-NNN]". So the index is a pointer table, the rules live in conditions/.
- extracts/processed/tom/CONSOLIDATED_RULES.md is a filtered sentence dump of 19 videos (no rule ids, generated 2026-08-01).
- runtime/compiled_engine.md is derived from the six files (its header: "ALL decision tables from 6 condition files"). CRITICAL, read only; used below just to locate engine text.
- Neither new video (zAwEX_tRUfE, WQ_OAdz-PJ8) appears in any of these (grep count 0), so all 16 are genuinely unmerged.
- No rule has a single numeric id. "Existing rule id" below = section number + TOM-NNN where present.

## 2. Proposal table (16 rules)
Key: MATCH = same idea already in master (partial if noted); NEW = no master rule; CONFLICT = opposing text. File prefix: RP=risk_protocol.md, ZI=zone_identification_rules.md, ET=entry_timing_triggers.md, ST=setup_type_rules.md, MS=market_state_rules.md (all under MyTradingSys/conditions/); CE=MyTradingSys/runtime/compiled_engine.md.

| new id | one line | src | matches existing | conflict? | note |
|---|---|---|---|---|---|
| T-WQ_OAdz-PJ8-R1 | High-volume ranges attract price, hold big orders | WQ_OAdz-PJ8 MIDDLE | MATCH ZI 2.2 (ZI:49, TOM-182); MS:46 (TOM-035) | no | Adds "large participants place orders there"; no logic change |
| T-WQ_OAdz-PJ8-R2 | Low-volume node: higher chance of snag, counter-trade zone | WQ_OAdz-PJ8 MIDDLE | MATCH (partial) ZI 7.1 (ZI:392-393) | no | ZI 7.1 says bounce, not "counter-trade"; ZI 7.2 (ZI:401) calls LVN a liquidity-fill transition. Tension, not opposition; R6 resolves it (fast zone + acceptance = continuation) |
| T-WQ_OAdz-PJ8-R3 | Impulse then sideways acceptance: likely retrace same path | WQ_OAdz-PJ8 END | NEW (nearest ZI 6.4, ZI:343) | no | ZI 6.4 is about FVG retests only; R3 generalises to any impulse+acceptance |
| T-WQ_OAdz-PJ8-R4 | Draw key levels on HTF, transfer to LTF | WQ_OAdz-PJ8 END | MATCH ZI 5.4 (ZI:290, TOM-199) | no | Also ZI workflow step 8 (ZI:495) |
| T-WQ_OAdz-PJ8-R5 | P profile = B profile mirrored; same logic reversed | WQ_OAdz-PJ8 END | NEW (nearest MS:50,53 define B and P separately) | no | Master never states the mirror symmetry |
| T-WQ_OAdz-PJ8-R6 | Fast run through illiquid zone, return: initially continues | WQ_OAdz-PJ8 MIDDLE | NEW (nearest ZI 6.4, ZI:343) | no | Raw transcript: holds "because these market participants here defend their subsequently created acceptance"; i.e. conditional on acceptance. Extract drops that condition; keep it |
| T-WQ_OAdz-PJ8-R7 | Volume profile is enough; footprint optional | WQ_OAdz-PJ8 END | NEW (meta) | no | Not a trade rule. Nearest ET:747 gap 10 (footprint-only trigger unspecified). Suggest do not merge as a rule |
| T-zAwEX_tRUfE-R1 | Read prior-day profile, locate price vs equilibrium first | zAwEX_tRUfE BEGIN | MATCH (partial) ZI 3.5 (ZI:135-137, TOM-188) | no | Method to locate equilibrium not given (extract "Unclear") |
| T-zAwEX_tRUfE-R2 | Market first seeks equilibrium; initial targets at its boundary | zAwEX_tRUfE BEGIN | MATCH MS:27 | no | "not prior highs" is an extract gloss, not in the quote |
| T-zAwEX_tRUfE-R3 | 1m trade from below can target upper equilibrium edge | zAwEX_tRUfE BEGIN | MATCH (partial) ZI 2.5 (ZI:76-78) | no | Different anchor (prior-day VA edge vs underlying-TF VPOC) |
| T-zAwEX_tRUfE-R4 | Longer runs only after clear acceptance above level | zAwEX_tRUfE MIDDLE | MATCH ET:368 and ST:404 | no | Same "accepts new prices" logic |
| T-zAwEX_tRUfE-R5 | Stop below last low on 1m often gives R:R<1 | zAwEX_tRUfE MIDDLE | MATCH-topic RP 2.3 (RP:84, TOM-074) | **CONFLICT (soft, scope)** | See section 3 |
| T-zAwEX_tRUfE-R6 | Mark prior-day VAH as the decisive 1m boundary | zAwEX_tRUfE MIDDLE | MATCH ZI 3.1/3.5 (ZI:94-96, 135); ET:189 | no | |
| T-zAwEX_tRUfE-R7 | Confirmed break of equilibrium gives predictable run | zAwEX_tRUfE END | MATCH ZI 3.3 (ZI:117, TOM-186) | no | Adds R:R improvement claim |
| T-zAwEX_tRUfE-R8 | Exit quickly if market re-accepts old equilibrium | zAwEX_tRUfE END | MATCH (concept) RP 2.6 (RP:107-109, TOM-077) | **CONFLICT (engine, not Tom list)** | See section 3. Master has no "exit on re-acceptance" rule; RP 2.6 is the nearest (structural invalidation) |
| T-zAwEX_tRUfE-R9 | Define level before session, wait for it, do not chase | zAwEX_tRUfE END | MATCH ET:189 (trigger A step 1) ; RP 7.4 (RP:478) | no | RP 7.4 is about monster moves, related only |

## 3. Conflicts, quoted both sides

### 3a. R5 vs stop-below-last-low (scope conflict, not a contradiction of Tom's rule)
- New (extract_zAwEX_tRUfE.md:95): "most traders on the 1-minute chart take the risk below the last low. That is the risk"
- Master (risk_protocol.md:84): "The stop loss goes below the last low here"
- Also risk_protocol.md:70: "my stop loss belongs below the last liquidity."
- Engine (compiled_engine.md:150): "stop = below last liquidity (swing_low for longs, swing_high for shorts)"
- Raw transcript (raw_transcripts_canonical/zAwEX_tRUfE_raw.txt): "The risk-reward ratio is somewhere in the range of 0.8 here, yeah. So, that means for such a trade, you need a win rate of at least a good 60%". The 0.8 and 60% are from the transcript but not in the extract quote; the extract rule (R5) quotes only the premise. Reading: Tom criticises last-low stops on a 1m scalp with a capped target (equilibrium edge), because R:R ~0.8. He does not say the rule is wrong for swing/5m trades (RP 2.3 comes from 4MoNjEQ2Dd8, a 5m trade with target above highs). Proposal: do NOT change RP 2.3; add a scope note: last-low stop applies when target distance supports R:R above 1; on 1m with target at equilibrium edge it does not. Operator decision needed.
- Gap this fills: setup_type_rules.md:554 "Scalp stop placement. Tom asks "where do I give up on my trade?" (43JaKHRvxHk) but does not answer for scalpers." R8 is Tom's partial answer for the equilibrium-breakout scalp: the invalidation is re-acceptance of the old equilibrium, not the last low.

### 3b. R8 vs engine exit/stop model (engine conflict)
- New (extract_zAwEX_tRUfE.md:116): "you're out relatively quickly down here if the market accepts the old equilibrium again"
- Engine (compiled_engine.md:626): "**This is a signal, not an automatic exit.** The judgment layer must evaluate: Is this a genuine structural break or a stop-run? Context matters."
- Engine stop (src/main/java/datafeed/SetupCandidatesBuilder.java:112-113): "if (swingHigh > zonePrice) c.stop = swingHigh;" / "else c.stop = zonePrice * 1.002; // fallback 0.2% above"; long side lines 115-116 mirror it. Lines 122-123 reset any stop tighter than MIN_STOP_PCT to the same 0.2%.
- Tom's stop placement, master (risk_protocol.md:91): "It doesn't belong above the high." and (risk_protocol.md:98-99) "we like to use footprint charts. for example, so we can easily identify" (next line: "the perfect level where we should abandon our trading idea").
- Reading: R8 makes the exit condition a market-structure event (re-acceptance of the old equilibrium), which can trigger well inside the swing extreme. Engine's stop sits AT the swing extreme (short: the swing high itself, Java:112) or a 0.2% offset from the zone (Java:113), with fixed stop and no discretionary exit (MTS_USER_GUIDE.md:151 per MISSING_PIECES). So R8 supports the prior finding that the engine stop is not Tom's stop: Tom's invalidation is a structural/volume level (RP 2.5, 2.6, 2.8, 2.9 game-over level), and the 0.2% fallback has no Tom source (no percent stop anywhere in conditions/).
- Precision: the engine stop is at, not above, the high. "doesn't belong above the high" is therefore not literally violated by Java:112; the conflict is with WHERE Tom puts it (volume-based level inside the range, RP:98-99), plus the fallback. yRvMW6lgN1o context (short trade): "Because the probability of a strong acceleration above the high is always high. And that's why we take a deeper look into the markets here and see where the largest volumes occurred."
- Not proposed: any change to Tom logic or engine code. Builder follow-up (SetupCandidatesBuilder is not execution/ or layers/alerts/ but is imported by live code paths: supervisor must route): add a re-acceptance invalidation and a volume-level stop as a separate layer/variant, backtested against the 0.2% stop.

### 3c. Non-conflicts checked
- R2 vs ZI 7.2 (LVN = liquidity fill) and R6 vs R2: tension only; R6 raw text conditions on acceptance.
- R3/R6 vs ZI 6.4 ("on the first attempt it tends to hold, on the second attempt it will most likely not hold."): consistent (R6 = first return, R3 = later retrace). Keep together.

## 4. Counts
NEW 4 (WQ R3, R5, R6, R7), MATCH 12 (of which CONFLICT-flagged 2: zAwEX R5 soft scope conflict vs master RP 2.3; zAwEX R8 conflict vs engine exit/stop model). Clean MATCH 10. Suggested merge: add the 4 NEW and the R5/R8 scope notes to conditions/ under operator approval; R7 is meta, suggest skip.

## 5. Also
- DSA_BACKLOG.md:16 ticks 999; this file is the missing output. A DSA_GATE_LOG row is still absent (not edited by me).
- Quotes from extracts verified against extract files; raw transcript quotes against raw_transcripts_canonical.
