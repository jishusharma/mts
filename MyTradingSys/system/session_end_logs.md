# SESSION END LOGS
# Purpose: Archive of all session end logs. Moved from 02a_CURRENT_STATUS.md to prevent bloat.
# Created: 2026-09-02
#

## SESSION END LOG

**Date:** 2026-09-01 (live snapshot + screenshot validation)
**Protocol:** I-07 (JSON Input) + I-03 (Research/Implementation)
**Actions completed:**
| # | Action | Result |
|---|--------|--------|
| 1 | Fresh DSA snapshot — BTCUSDT @ 78,124.5 | math_object_builder compiled successfully |
| 2 | Verdict generation | WAIT C- (40/100) — NO TRADE |
| 3 | 3m screenshot VVP-001 validation | 7/10 PASS. Cursor at historical 02:23 (FAIL). VP still VPVR (FAIL). |
| 4 | Post-drop analysis | Price fell ~$660 from 05:21 snapshot. C+ short at 78,866-78,947 never triggered — gapped down without rejection wick. No trade = no loss. |
| 5 | Flow assessment | CVD rising + trade_flow +22.9 + bid bias 2.23 = bullish recent shift on drop. Contradicts short. |
| 6 | US pre-open context | European session. US equity open in ~2.5h (13:30 UTC). Funding not extreme. |

**Verdict: WAIT C- (40/100)**
- Price at 4H VAH 78,126 — neutral, no directional edge
- Trigger: MISSING — no rejection wick
- R:R sanity: FAILS (0.22:1 gross)
- Flow: Bullish recent shift (CVD 1h rising + delta positive)
- Structure: Below VWAP, bearish, but consolidating
- Action: NO TRADE. Monitor for bounce from 78,107-78,126 or break below 77,775.

**Key learning:** The "recent_shift" principle (BUG #4 fix) correctly identified that falling price + rising CVD 1h + positive trade_flow = buyers absorbing sell-off, not continuation. Engine demoted short bias.

**Next session:** Monitor for trigger development. US open volatility in ~2.5h. Fix chart cursor + VP before next screenshot.

---

## SESSION END LOG

**Date:** 2026-09-01 (continuation — funding analysis + 1m screenshot)
**Protocol:** I-07 (JSON Input) + I-03 (Research/Implementation)
**Actions completed:**
| # | Action | Result |
|---|--------|--------|
| 1 | Funding data analysis (3 charts) | Extracted: BTC OI-weighted 0.0074%, 7-day $66.82M long vs $37.01M short (1.8:1), OI $16.45B. 24h data conflicting between sources. |
| 2 | Funding reconciliation | Chart 1 (detailed) = PRIMARY. Chart 2 (overview) = confirmation. 24h discrepancy noted: Chart 1 says shorts paid, Chart 2 says longs paid. |
| 3 | 1m screenshot validation | 10/11 PASS. VP missing from 1m (Fixed Range not visible). BB fully removed. VWAP, CVD Line, Net Delta, OI all present. |
| 4 | 1m price action analysis | Price peaked ~79,100-79,200 (above 4H VAH 78,997) then pulled back to 78,797.6. CVD falling, delta negative. Trigger UNCONFIRMED — no zoomed screenshot of peak. |
| 5 | Funding impact on C+ setup | +5 confidence. 7-day long dominance = strong supporting factor. Longs overcrowded = liquidation cascade potential on drop. |
| 6 | current_market_state.md updated | Added FUNDING section with all extracted values and assessment |

**Funding data summary:**
| Metric | Value | Assessment |
|--------|-------|------------|
| BTC OI-Weighted Rate | 0.0074% | Moderate positive — longs pay |
| 7-day long paid | $66.82M | **Strong signal — longs overcrowded** |
| 7-day short paid | $37.01M | Shorts not overcrowded |
| 7-day ratio | 1.8:1 | **Adds +5 confidence to short setup** |
| OI | $16.45B | Massive liquidation potential |
| 24h net (Chart 1) | -$3.54M (shorts pay) | Mixed — possible short covering |
| 24h net (Chart 2) | +$3.90M (longs pay) | Conflicting source |
| Current net | +$2.38M (longs pay) | Consistent with 7-day direction |

**1m screenshot findings:**
- Price: 78,797.6 (down from 78,920 JSON snapshot = -0.155%)
- VWAP: 78,246.1 (price 0.70% above)
- CVD: -3.471K (falling)
- Net Delta: -784.16 (negative)
- OI: 107.521K (flat)
- **Price peaked ~79,100-79,200 around 18:30-20:30** — above 4H VAH (78,997)
- **Then declined ~$400** to current level at 4H POC (78,801)
- **Trigger status: UNCONFIRMED** — peak may have had rejection wick, but no zoomed screenshot provided

**Verdict update:**
- If rejection wick confirmed at 18:30-20:30 peak: C+ → B/A, but entry (78,997+) missed by ~$200
- If no rejection: C+ remains — price needs to return to 4H VAH cluster for fresh trigger
- Current level (4H POC 78,801) = first support. If holds and bounces, no trade. If breaks below 4H VAL (78,705), balance breakdown.

**Action items:**
1. [ ] Add Fixed Range VP to 1m chart
2. [ ] Review 1m candles 18:30-20:30 for rejection wick confirmation
3. [ ] Set alert at 4H VAH cluster (78,997-79,128) for fresh trigger
4. [ ] Monitor 4H POC (78,801) — break below 78,705 = balance breakdown

**Next session:** Monitor for trigger development. If price returns to 78,997+, pull 3m/5m footprint for absorption/rejection.

---

## SESSION END LOG

**Date:** 2026-09-01 (continuation)
**Protocol:** I-07 (JSON Input) + I-03 (Research/Implementation)
**Actions completed:**
| # | Action | Result |
|---|--------|--------|
| 1 | Screenshot validation per VVP-001 v1.1.0 | 10/11 PASS. BB label persists but lines removed. VWAP, Fixed Range VP, CVD Line, Net Delta, OI all present. |
| 2 | JSON analysis — BTCUSDT @ 78,920.0 | C+ SETUP FORMING (65/100) — CT Short at 4H VAH cluster (78,997-79,128) |
| 3 | Delta computation | 10 changes, 8 structural. Price flat (-0.006%). Post-funding VAH jumped +195 pts to 79,128. |
| 4 | Zone identification | 3 valid short zones: 4H VAH (78,997), 5m high (79,040), post-funding VAH (79,128). Confluence +20. |
| 5 | R:R calculation | Stop 79,228.5 (1H swing high). Target 78,308.43 (prior day POC). Gross 2.97:1, NET 2.23:1. PASS. |
| 6 | Proof evaluation | 3 supporting, 2 contradicting, 2 missing. Book flipped to ask bias (0.87). Last 3 delta negative. CVD flat. |
| 7 | Trigger assessment | MISSING — no rejection wick. Bearish FVG at 78,945-78,950 (0.04% above price) = potential trigger zone. |
| 8 | Trading card generated | `mts/cards/BTCUSDT_2026-08-31_2204.md` |
| 9 | State file updated | `mts/runtime/current_market_state.md` — post-funding VAH updated to 79,128 |

**Screenshot validation results (5m):**
| Check | Status |
|-------|--------|
| Cursor at right edge | PASS |
| Timeframe visible | PASS |
| Price OHLC visible | PASS |
| VWAP present with bands | PASS |
| VP (Fixed Range) | PASS |
| CVD (line) | PASS |
| Net Delta | PASS |
| Open Interest | PASS |
| BB removed | PARTIAL — label shows but lines not visible |
| No CVD Candles | PASS |
| No RSI/BB | PARTIAL |

**Verdict: C+ — SETUP FORMING (65/100)**
- State: BALANCE (all VP shapes = B)
- Zone: 4H VAH / 5m swing high / post-funding VAH cluster
- R:R: 2.23:1 NET (PASS)
- Confluence: +20 (3 zones within 0.166%)
- Trigger: MISSING — alert at 78,997-79,128, monitor bearish FVG at 78,945-78,950
- Raw structure score: 96/100 (excellent) — capped to C+ by missing trigger

**Improvement from prior snapshot:**
- Book imbalance: 1.04 (bid bias) → 0.87 (ask bias) = now SUPPORTS short
- Trade flow: 73.4 (strong buying) → 3.7 (near zero) = neutral
- CVD: falling → flat = selling pressure stalled
- Last 3 delta: [positive, positive, positive] → [negative, negative, negative] = recent selling
- New bearish FVG at 78,945-78,950 (0.04% above price) = resistance

**Action items:**
1. Set alert at 4H VAH cluster (78,997-79,128)
2. Monitor bearish FVG at 78,945-78,950 — fill + reversal = trigger
3. Fix BB label persistence in CoinGlass
4. On alert: pull 3m/5m footprint for absorption/rejection

**Next session:** Monitor for trigger development at 4H VAH cluster.

---

## SESSION END LOG

**Date:** 2026-09-01
**Protocol:** I-07 (JSON Input) + I-03 (Research/Implementation)
**Actions completed:**
| # | Action | Result |
|---|--------|--------|
| 1 | Screenshot validation per VVP-001 v1.1.0 | 6/11 PASS, 5 FAIL. 3 chart fixes identified. |
| 2 | JSON analysis — BTCUSDT @ 78,924.5 | C+ SETUP FORMING (58/100) — CT Short at post-funding VAH cluster (78,933-78,997) |
| 3 | Delta computation | 10 structural changes detected. Price +0.66%. CVD flipped rising->falling. Trade flow flipped negative->positive. |
| 4 | Zone identification | 3 valid short zones: post-funding VAH, 5m swing high, 4H VAH. Confluence +20. |
| 5 | R:R calculation | Stop 79,228.5 (1H swing high). Target 78,028.19 (post-funding VAL). Gross 3.08:1, NET 2.31:1. PASS. |
| 6 | Proof evaluation | 2 supporting, 2 contradicting, 2 missing. CVD falling supports short. Trade flow positive + VWAP rising contradict. |
| 7 | Trigger assessment | MISSING — no rejection wick or failed breakout at VAH. Alert recommended. |
| 8 | Trading card generated | `mts/cards/BTCUSDT_2026-08-31_2127.md` (224 lines) |
| 9 | State file updated | `mts/runtime/current_market_state.md` — 70 lines, all structural data persisted |
| 10 | VVP-001 updated to v1.1.0 | Questionnaire decisions applied: CVD=Line, VP=Fixed Range, Liquidations=T3, RSI/BB removed. Section 2.6 added. |
| 11 | Chart Layout Guide created | `mts/research/chart_layout_implementation_guide.md` — step-by-step CoinGlass configuration |
| 12 | 03_FILE_INDEX.md updated | +2 files (card + guide), VVP status updated to v1.1.0 |

**Screenshot validation results:**
| Check | Status |
|-------|--------|
| Cursor at right edge | PASS |
| Timeframe visible | PASS |
| Price OHLC visible | PASS |
| VWAP present | PASS |
| VP (Fixed Range) | FAIL — VPVR still used |
| CVD (line) | FAIL — CVD Candles still used |
| Net Delta | PASS |
| Open Interest | PASS |
| BB removed | FAIL — "BB 20 2" visible |
| No CVD Candles | FAIL — CVD Candles present |
| No RSI/BB | FAIL — BB present |

**Chart fixes required before next screenshot:**
1. Switch VP from VPVR to Fixed Range
2. Switch CVD from Candles to Line
3. Remove BB from chart

**Verdict: C+ — SETUP FORMING (58/100)**
- State: BALANCE (all VP shapes = B)
- Zone: Post-funding VAH / 4H VAH / 5m swing high cluster
- R:R: 2.31:1 NET (PASS)
- Confluence: +20 (3 zones within 0.081%)
- Trigger: MISSING — alert at 78,933-78,997, wait for rejection
- Action: Set alert. Pull 15m footprint on approach. Look for absorption/rejection.

**Next session:** JISHU fixes 3 chart issues, uploads new screenshot. AI re-runs VVP-001 validation. If screenshot passes, monitor C+ setup for trigger development.
**Blocker:** None. Waiting on JISHU chart fixes.

---

## SESSION END LOG

**Date:** 2026-08-31
**Protocol:** I-05
**Actions completed:**
| # | Action | Result |
|---|--------|--------|
| 1 | Revalidate compiled_engine.md | 9 fabrications deleted, 20+ demoted, 4 orphaned references fixed, 41 [PRINCIPLE — NOT ALGORITHM] tags |
| 2 | Verify mts_math.py purity | 9 functions, zero side effects, all system parameters tagged |
| 3 | Run test_mts_math.py | 64/64 PASS — determinism, edge cases, all functions |
| 4 | Create math_object_builder.py | NEW — DSA snapshot → math_object compiler |
| 5 | Run test_math_object_builder.py | 34/34 PASS — determinism, schema, zone fields, R:R logic, confluence, hard stops |
| 6 | Update status files | 02a_CURRENT_STATUS.md, 00_START_HERE.md, 03_FILE_INDEX.md updated |
| 7 | Complete session-end checklist | All 7 sections passed |

**Math layer status:** ACTIVE — 98/98 tests pass. Architecture: DSA Snapshot → math_object_builder → math_object → AI Judgment Layer.
**Next session:** Paste JSON → math_object_builder compiles → judgment layer generates card. AI never recomputes math.
**Blocker:** None

---

**Date:** 2026-08-30
**Protocol:** I-05
**Actions completed:**
| # | Action | Result |
|---|--------|--------|
| 1 | Extract CryptoCred _ndAoizXy64 (Trade Management) | 13 rules, CT-047 to CT-059, PURE format |
| 2 | Extract CryptoCred XeQV2ECtZVQ (Risk Management) | 13 rules, CT-060 to CT-072, PURE format |
| 3 | Extract CryptoCred Yp0k8HD5xro (First Trouble Area) | 13 rules, CT-073 to CT-085, PURE format |
| 4 | Update cross_trader_integration_plan.md | CT-047 to CT-085 added, concept groups updated |
| 5 | Update 00_START_HERE.md | Status: Phase 1 COMPLETE, 7/7, 85 rules |
| 6 | Update 02a_CURRENT_STATUS.md | Task 7: Phase 1 COMPLETE |
| 7 | Revalidate all extracts | All PURE, zero prohibited content, cross-file consistent |

**Phase 1 status:** COMPLETE — 7/7 transcripts, 85 rules (CT-001 to CT-085)
**Next session:** Phase 3 Integration Planning (5-step check per rule vs compiled_engine.md)
**Blocker:** None

---

## NEXT SESSION STARTING PROMPT

**Date:** TBD
**Context to load:** 00_START_HERE.md → 01_AI_BEHAVIOR.md → 02a_CURRENT_STATUS.md
**Decision pending:** None
**New workflow:** Paste JSON → math_object_builder compiles → judgment layer generates card. OR upload screenshot with cursor at RIGHT EDGE + Fixed Range VP.
**Uploads needed:** NONE — all files in mirror.
**Canonical plan:** mts/research/cross_trader_integration_plan.md

### Immediate next actions (choose one):
| # | Action | Trigger |
|---|--------|---------|
| 1 | Paste fresh JSON snapshot | User says "snapshot" or pastes JSON |
| 2 | Upload screenshot (cursor at RIGHT EDGE, Fixed Range VP) | User uploads image |
| 3 | Create paper trade log template | User says "paper trade log" |
| 4 | Resume VVP-001 protocol revisions | User says "revise VVP" |

**Current market context:**
- Last price: 78,124.5 (10:47 UTC)
- Last verdict: WAIT C- (40/100) — NO TRADE
- C+ short setup at 78,866-78,947 NEVER TRIGGERED — price gapped down ~$660 without rejection wick
- Current: Consolidation at 78,000 below VWAP. Monitor 4H VAH 78,126 / bullish FVG 78,107-78,109 for bounce, or break below 77,775 for continuation.
- US equity open: ~2.5h away (13:30 UTC) — volatility injection expected

**Chart fixes still needed:**
1. Cursor at RIGHT EDGE (not historical candle)
2. VP switched from VPVR to Fixed Range
3. BB label removed from legend

**User says:** "Paste JSON or upload screenshot. I will validate chart layout first (cursor at right edge, VP=Fixed Range), then generate verdict. Say 'Go' when ready.

---

## SESSION END LOG

**Date:** 2026-09-03
**Protocol:** I-05 (System Maintenance)
**Actions completed:**
| # | Action | Result |
|---|--------|--------|
| 1 | Validated structural_simplification_research.md | 6 critical errors found in parallel session's research doc |
| 2 | Fixed 12 stale test count references | 03_FILE_INDEX, 04_BUGS, 06_CHECKLIST, session_end_logs, 02c_SIGNOFF, COMPILED_DECISIONS_TEST_PLAN |
| 3 | Added prevention rule | 00_START_HERE.md Mistake #16: "Hardcoding test counts in multiple files" |
| 4 | Proposed corrected 5-file plan | START + ENGINE + STATUS + DECISIONS + CHECKLIST (preserves constitution, modularity, append-only chains) |

**Key finding:** Research doc is 80% accurate but 3 errors would break the system: deleting constitution, merging 63KB engine into workflow guide, corrupting append-only decision chain.
**Next session:** Re-evaluation with fresh eyes. Core idea / problem / solution / validation.
**Blocker:** None.


---

**Date:** 2026-08-31 (Phase 3 session)
**Protocol:** I-05
**Actions completed:**
| # | Action | Result |
|---|--------|--------|
| 1 | Cross-Trader Phase 3: Integration Planning | 80 entries classified via 5-step check vs compiled_engine.md |
| 2 | Revalidation | 80/80 classifications confirmed. Zero reclassifications needed. |
| 3 | Update cross_trader_integration_plan.md | Phase 3 section appended. Status table updated. |
| 4 | Update 00_START_HERE.md | Status line: Phase 3 COMPLETE. Last session summary rewritten. |
| 5 | Update 02a_CURRENT_STATUS.md | Task 7: Phases 1-3 COMPLETE, Phase 4 READY. |
| 6 | Update 02c_SESSION_END_SIGNOFF.md | New signoff block appended (2026-08-31). |
| 7 | Update 04_NEXT_SESSION_PROMPT.md | Overwritten with Phase 4 protocol. |

**Phase 3 status:** COMPLETE — 28 CONFIRMED, 33 NEW, 5 GAP, 3 CONFLICT, 11 REJECT.
**Key finding:** Post-entry trade management is the engine's largest functional gap (14 of 33 NEW entries).
**Next session:** Phase 4 Integration. 33 NEW entries queued (P0-P3). 3 conflicts await user resolution. 5 GAP entries blocked on DSA.
**Blocker:** None for Phase 4 start. User confirmation needed for 3 conflict resolutions.


---

## SESSION END LOG

**Date:** 2026-08-31
**Protocol:** I-05
**Actions completed:**
| # | Action | Result |
|---|--------|--------|
| 1 | Execute VVP-001 test suite (20 tests, 5 sections) | COMPLETE — 54 evaluations: 31 PASS, 12 FAIL, 6 CANNOT TEST, 2 CANNOT CONFIRM, 3 NOT APPLICABLE |
| 2 | Archive screenshots to mts/research/ | 3 PNG files copied from temp/ |
| 3 | Write vvp_test_results_20260831.md | 326 lines, 14,938 chars — verified |
| 4 | Update 03_FILE_INDEX.md | +7 entries added to research table |
| 5 | Run 06_SESSION_END_CHECKLIST.md | All 7 sections PASSED |
| 6 | Update 00_START_HERE.md | Date, status, last session summary updated |

**VVP-001 test status:** Phase 1.0.0 COMPLETE. Critical finding: VWAP missing from all screenshots (Tier 1 essential). 6 issues logged, 4 protocol revisions recommended.
**Next session:** VVP-001 protocol revisions OR JISHU adds VWAP + zone markings and re-runs B1-B2, C1.
**Blocker:** None for session close.

---

## NEXT SESSION STARTING PROMPT

**Date:** TBD
**Context to load:** 00_START_HERE.md → 01_AI_BEHAVIOR.md → 02a_CURRENT_STATUS.md
**Decision pending:** None
**New workflow:** VVP-001 protocol revisions (4 recommended) OR re-run visual validation with VWAP + zone markings added.
**Uploads needed:** NONE — all files in mirror.
**Canonical plan:** mts/research/visual_validation_protocol_vvp001.md

### Immediate next actions (choose one):
| # | Action | Trigger |
|---|--------|---------|
| 1 | Revise VVP-001 per 4 recommendations in test results | User says "revise VVP-001" |
| 2 | Re-run B1-B2 + C1 with new screenshots (VWAP + zone markings) | User uploads new screenshots |
| 3 | Resume Phase 4 cross-trader integration | User says "continue Phase 4" |

**User says:** "Upload new screenshots with VWAP and zone markings. I will re-run the failed tests. Say 'Go' when ready."

---
---## SESSION END LOG — 2026-09-02 (Fix Session)## SESSION END LOG — 2026-09-02 (Fix Session)## SESSION END LOG — 2026-09-02 (Fix Session)
---

## SESSION END LOG

**Date:** 2026-09-02 (Complete Drift Fix Session)
**Protocol:** I-05 (System Maintenance)
**Actions completed:**
| # | Action | Result |
|---|--------|--------|
| 1 | Complete project audit | 9 discrepancies (D1-D9) identified across 6 system files |
| 2 | Fix D1/D4/D9 | 00_START_HERE.md updated to v4.2.0-p5, date 2026-09-02, price 78,784.5, Sep 1 session summary added |
| 3 | Fix D2 | 01_AI_BEHAVIOR.md updated to v4.2.0-p5, Phase 4 COMPLETE, 47/47 FRESH extracts, 98/98 tests |
| 4 | Fix D3/D5/D7 | 02a_CURRENT_STATUS.md updated to v4.2.0-p5, 13 cards listed, cross-trader status fixed |
| 5 | Fix D6 | mts_math.py: FUNDING fields added to diff_state(), update_state(), format_state(). 7 fields tracked. Tests pass. |
| 6 | Fix D8 | 4 session end logs moved from 02a to new file session_end_logs.md. 02a trimmed to ~7KB. |
| 7 | Update 02b_DECISIONS_LOG.md | D6+D8 completion entry appended. Last updated 2026-09-02. |
| 8 | Update 03_FILE_INDEX.md | session_end_logs.md and 04_NEXT_SESSION_PROMPT_DRIFT_FIX.md entries added. |
| 9 | Update 02c_SESSION_END_SIGNOFF.md | Session signoff appended. |

**Verdict:** All 9 discrepancies resolved. Project fully consistent at v4.2.0-p5.
**Next session:** Paste JSON snapshot or upload screenshot. Pipeline ready.
**Blocker:** None.
2026-09-09 14:19 UTC | BTCUSDT 78,911.8 | C+ WAIT / WATCH CT Long at 5m swing low / VWAP -1s (72/100) | Visual validation pending for support cluster 78,844-78,855

---

## SESSION CONTEXT MIGRATION - 2026-09-10

Superseded file: mts/runtime/btcusdt_market_session.md (deprecated)
Reason: SSOT violation - content absorbed into current_market_state.md
(Step 4 of 2026-09-10 session) and session_end_logs.md (this entry).

Preserved snapshot history (last 3 rows from deprecated file):
| # | Timestamp (UTC) | Price | Verdict | Score | Change Summary |
|---|-----------------|-------|---------|-------|----------------|
| 1 | 2026-09-07 10:31 | 79,387.9 | Scalp short VWAP -1s | 88 | Post-drop consolidation, pinned to weekly POC |
| 2 | 2026-09-07 11:39 | 79,378.5 | 5m swing high short | 95 | Speed exploded, FVG appeared, bearish momentum |
| 3 | 2026-09-07 13:20 | 79,584.1 | 4H VAH short | 81 | Short covering rally, no new OI, perp discount |

Preserved thesis (last entry, 2026-09-07, superseded):
Macro: Bearish, 20K rally to ~82K was bull trap (short covering), bottom
window Sep-Nov, final flush targets 44-50K. Micro: Holiday-thinned, short
covering bounce, real test when US reopens. Perp discount persists.
Invalidates if: Break above 80,536 with volume; long OI surge; daily CVD
curl up; perp basis flips to premium.

Status: The 80,536 invalidation level is no longer a current swing reference
as of 2026-09-10 (1H swing high = 79,737.3). Thesis was superseded by
downside continuation to 78,115.9 by 2026-09-10 07:53 UTC.


## 2026-09-10 - SPEED RESEARCH + DSA_TASK_013/014

Session summary written to `02a_CURRENT_STATUS.md`. Key outputs:
- Speed SSOT declared; both definitions tagged as proxies.
- `order_flow` block live in every snapshot (DSA_TASK_013).
- Per-instrument historical baseline live (DSA_TASK_014).
- BUG-007 fixed. 102/102 tests pass.
- Vocabulary mining Rule 36 + M-032 landed.
- Guest audit: 2 files bannered, 1 nested attribution noted.


## 2026-09-11 - FIXES + STATE UPDATER + DIVERGENCE MONITOR

See `02a_CURRENT_STATUS.md` session summary for details.

Key: 3 code fixes verified (BUG-007/008/009), DSA-HYG-001/006 live, DSA-HYG-002 live but unverified,
state updater built (closed ~23h drift), divergence monitor built, 6 AI research responses compared
across 2 cycles, 2 guest banners + 1 nested attribution.

Next: wire state updater into snapshot workflow, validate BUG-008 on 2 more snapshots,
investigate DSA-HYG-002 filter mismatch, build state-code emitter (A/B/C codes), Malkans research.
2026-09-11T19:24:16.209Z  A -> A>L  bearish=0 bullish=3  trigger=net_delta_1m,last_3_delta,price_vs_vwap
2026-09-11T19:24:39.458Z  A -> A>L  bearish=0 bullish=3  trigger=net_delta_1m,last_3_delta,price_vs_vwap
2026-09-11T19:27:16.211Z  A>L -> A  bearish=0 bullish=2  trigger=quiet-decay
2026-09-11T19:27:39.459Z  A>L -> L  bearish=0 bullish=3  trigger=net_delta_1m,last_3_delta,price_vs_vwap
2026-09-11T19:29:39.462Z  L -> A  bearish=1 bullish=0  trigger=quiet-decay
2026-09-11T19:36:16.214Z  A -> A>L  bearish=0 bullish=2  trigger=net_delta_1m,last_3_delta,volume_ratio,price_vs_vwap
2026-09-11T19:38:16.214Z  A>L -> A  bearish=2 bullish=0  trigger=quiet-decay
2026-09-11T19:41:39.461Z  A -> A>L  bearish=0 bullish=3  trigger=net_delta_1m,last_3_delta,volume_ratio,price_vs_vwap
2026-09-11T19:43:39.463Z  A>L -> A  bearish=1 bullish=0  trigger=quiet-decay
2026-09-11T19:49:39.463Z  A -> A>L  bearish=0 bullish=2  trigger=net_delta_1m,last_3_delta,volume_ratio,price_vs_vwap
2026-09-11T19:51:16.215Z  A -> A>L  bearish=0 bullish=3  trigger=net_delta_1m,last_3_delta,volume_ratio,price_vs_vwap
2026-09-11T19:53:16.217Z  A>L -> L  bearish=0 bullish=3  trigger=net_delta_1m,last_3_delta,volume_ratio,price_vs_vwap
2026-09-11T19:54:39.465Z  A>L -> L  bearish=0 bullish=3  trigger=net_delta_1m,last_3_delta,volume_ratio,price_vs_vwap
2026-09-11T19:56:39.464Z  L -> A  bearish=0 bullish=2  trigger=quiet-decay
2026-09-11T19:57:16.217Z  L -> A  bearish=1 bullish=1  trigger=quiet-decay
2026-09-12T05:58:36.801Z  A -> A>L  bearish=0 bullish=2  trigger=net_delta_1m,last_3_delta,price_vs_vwap
2026-09-12T06:00:36.803Z  A>L -> A  bearish=1 bullish=0  trigger=quiet-decay
2026-09-12T06:08:36.808Z  A -> A>L  bearish=0 bullish=2  trigger=net_delta_1m,last_3_delta,volume_ratio,price_vs_vwap
2026-09-12T06:10:36.803Z  A>L -> A  bearish=0 bullish=2  trigger=quiet-decay
2026-09-12T06:18:36.847Z  A -> A>L  bearish=0 bullish=2  trigger=net_delta_1m,last_3_delta,volume_ratio,price_vs_vwap
2026-09-12T06:20:36.879Z  A>L -> A  bearish=0 bullish=2  trigger=quiet-decay
2026-09-12T06:22:36.882Z  A -> A>L  bearish=0 bullish=2  trigger=net_delta_1m,last_3_delta,volume_ratio,price_vs_vwap
2026-09-12T06:24:36.883Z  A>L -> A  bearish=0 bullish=1  trigger=quiet-decay
2026-09-12T06:31:36.883Z  A -> A>L  bearish=0 bullish=4  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-12T06:33:36.882Z  A>L -> L  bearish=0 bullish=4  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-12T06:36:36.884Z  L -> A  bearish=0 bullish=2  trigger=quiet-decay
2026-09-12T06:38:36.883Z  A -> A>L  bearish=0 bullish=3  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-12T06:40:36.884Z  A>L -> L  bearish=0 bullish=4  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-12T06:50:36.883Z  L -> A  bearish=1 bullish=2  trigger=quiet-decay
2026-09-12T06:52:36.884Z  A -> A>L  bearish=1 bullish=2  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-12T06:54:36.884Z  A>L -> A  bearish=2 bullish=2  trigger=quiet-decay
2026-09-12T06:57:36.885Z  A -> A>S  bearish=2 bullish=1  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-12T06:59:36.885Z  A>S -> A  bearish=1 bullish=1  trigger=quiet-decay
2026-09-12T07:01:36.884Z  A -> A>L  bearish=1 bullish=2  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-12T07:05:36.886Z  A>L -> L  bearish=0 bullish=3  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-12T07:12:36.885Z  L -> A  bearish=1 bullish=2  trigger=quiet-decay
2026-09-12T07:20:36.907Z  A -> A>S  bearish=2 bullish=1  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-12T07:23:36.908Z  A>S -> A  bearish=1 bullish=1  trigger=quiet-decay
2026-09-12T07:25:36.908Z  A -> A>L  bearish=0 bullish=2  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-12T07:27:36.909Z  A>L -> A  bearish=0 bullish=1  trigger=quiet-decay
2026-09-12T07:30:36.908Z  A -> A>S  bearish=3 bullish=0  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-12T07:32:36.911Z  A>S -> S  bearish=4 bullish=0  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-12T07:40:36.909Z  S -> A  bearish=1 bullish=1  trigger=quiet-decay
2026-09-12T07:43:36.909Z  A -> A>S  bearish=2 bullish=0  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-12T07:46:36.910Z  A>S -> A  bearish=1 bullish=2  trigger=quiet-decay
2026-09-12T07:48:36.910Z  A -> A>S  bearish=2 bullish=0  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-12T07:50:36.910Z  A>S -> S  bearish=3 bullish=0  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-12T07:56:36.912Z  S -> A  bearish=1 bullish=1  trigger=quiet-decay
2026-09-12T07:58:36.912Z  A -> A>L  bearish=1 bullish=3  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-12T08:00:36.912Z  A>L -> L  bearish=1 bullish=3  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-12T08:02:36.913Z  L -> A  bearish=2 bullish=0  trigger=quiet-decay
2026-09-12T08:05:36.913Z  A -> A>L  bearish=1 bullish=3  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-12T08:14:36.916Z  A>L -> A  bearish=2 bullish=1  trigger=quiet-decay
2026-09-12T08:16:36.917Z  A -> A>L  bearish=0 bullish=3  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-12T08:18:36.922Z  A>L -> A  bearish=1 bullish=1  trigger=quiet-decay
2026-09-12T08:33:36.931Z  A -> A>S  bearish=2 bullish=0  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-12T08:35:36.932Z  A>S -> S  bearish=3 bullish=0  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-12T08:37:36.932Z  S -> A  bearish=1 bullish=2  trigger=quiet-decay
2026-09-12T08:39:36.933Z  A -> A>L  bearish=1 bullish=3  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-12T08:42:36.932Z  A>L -> A  bearish=1 bullish=2  trigger=quiet-decay
2026-09-12T08:45:36.932Z  A -> A>S  bearish=2 bullish=1  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-12T08:47:36.933Z  A>S -> A  bearish=2 bullish=1  trigger=quiet-decay
2026-09-12T08:49:36.933Z  A -> A>L  bearish=1 bullish=2  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-12T08:51:36.933Z  A>L -> L  bearish=0 bullish=4  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-12T08:55:36.933Z  L -> A  bearish=2 bullish=2  trigger=quiet-decay
2026-09-12T08:59:36.935Z  A -> A>L  bearish=0 bullish=4  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-12T09:01:36.934Z  A>L -> A  bearish=2 bullish=2  trigger=quiet-decay
2026-09-12T09:03:36.934Z  A -> A>L  bearish=0 bullish=3  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-12T09:05:36.933Z  A>L -> L  bearish=0 bullish=4  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-12T09:07:36.934Z  L -> A  bearish=1 bullish=2  trigger=quiet-decay
2026-09-12T09:11:36.935Z  A -> A>L  bearish=0 bullish=3  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-12T09:13:36.935Z  A>L -> A  bearish=2 bullish=2  trigger=quiet-decay
2026-09-12T09:15:36.936Z  A -> A>L  bearish=1 bullish=2  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-12T09:26:36.954Z  A>L -> A  bearish=1 bullish=2  trigger=quiet-decay
2026-09-12T09:28:36.954Z  A -> A>L  bearish=0 bullish=3  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-12T09:34:36.958Z  A>L -> A  bearish=1 bullish=2  trigger=quiet-decay
2026-09-12T09:36:36.956Z  A -> A>S  bearish=2 bullish=1  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-12T09:41:36.958Z  A>S -> A  bearish=0 bullish=2  trigger=quiet-decay
2026-09-12T09:43:36.958Z  A -> A>L  bearish=0 bullish=3  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-12T09:45:36.959Z  A>L -> A  bearish=0 bullish=1  trigger=quiet-decay
2026-09-12T09:48:36.958Z  A -> A>S  bearish=2 bullish=0  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-12T09:52:36.959Z  A>S -> A  bearish=2 bullish=0  trigger=quiet-decay
2026-09-12T09:57:36.960Z  A -> A>S  bearish=2 bullish=0  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-12T10:05:36.964Z  A>S -> A  bearish=1 bullish=1  trigger=quiet-decay
2026-09-12T10:07:36.962Z  A -> A>L  bearish=0 bullish=3  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-12T10:10:36.960Z  A>L -> L  bearish=0 bullish=3  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-12T10:28:15.850Z  L -> A  bearish=1 bullish=2  trigger=quiet-decay
2026-09-12T10:28:15.859Z  A -> A>L  bearish=1 bullish=2  trigger=net_delta_1m,volume_ratio,cvd_slope,price_vs_vwap
2026-09-12T10:28:15.865Z  A>L -> A  bearish=1 bullish=2  trigger=quiet-decay
2026-09-12T10:28:15.872Z  A -> A>L  bearish=1 bullish=2  trigger=net_delta_1m,volume_ratio,cvd_slope,price_vs_vwap
2026-09-12T10:28:15.878Z  A>L -> A  bearish=1 bullish=2  trigger=quiet-decay
2026-09-12T10:28:15.884Z  A -> A>L  bearish=1 bullish=2  trigger=net_delta_1m,volume_ratio,cvd_slope,price_vs_vwap
2026-09-12T10:28:15.891Z  A>L -> A  bearish=1 bullish=2  trigger=quiet-decay
2026-09-12T10:28:36.957Z  A -> A>L  bearish=1 bullish=2  trigger=net_delta_1m,volume_ratio,cvd_slope,price_vs_vwap
2026-09-12T10:30:36.957Z  A>L -> A  bearish=2 bullish=2  trigger=quiet-decay
2026-09-12T10:35:36.870Z  A -> A>S  bearish=2 bullish=1  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-12T10:37:36.804Z  A>S -> A  bearish=1 bullish=0  trigger=quiet-decay
2026-09-12T10:40:36.796Z  A -> A>S  bearish=3 bullish=1  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-12T10:43:36.795Z  A>S -> A  bearish=2 bullish=1  trigger=quiet-decay
2026-09-12T10:45:36.795Z  A -> A>L  bearish=1 bullish=2  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-12T10:47:36.796Z  A>L -> L  bearish=1 bullish=3  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-12T10:51:36.797Z  L -> L>S  bearish=3 bullish=0  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-12T10:53:36.797Z  L>S -> S  bearish=3 bullish=0  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-12T10:56:36.796Z  S -> A  bearish=2 bullish=0  trigger=quiet-decay
2026-09-12T11:03:36.795Z  A -> A>S  bearish=2 bullish=0  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-12T11:06:36.800Z  A>S -> A  bearish=1 bullish=1  trigger=quiet-decay
2026-09-12T11:08:36.796Z  A -> A>S  bearish=2 bullish=0  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-12T11:10:36.797Z  A>S -> A  bearish=2 bullish=0  trigger=quiet-decay
2026-09-12T11:18:36.796Z  A -> A>S  bearish=2 bullish=0  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-12T11:20:36.798Z  A>S -> S  bearish=3 bullish=0  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-12T11:25:36.795Z  S -> A  bearish=2 bullish=0  trigger=quiet-decay
2026-09-12T11:28:36.800Z  A -> A>S  bearish=2 bullish=0  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-12T11:30:36.809Z  A>S -> A  bearish=2 bullish=0  trigger=quiet-decay
2026-09-12T11:32:36.820Z  A -> A>S  bearish=3 bullish=0  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-12T11:34:36.820Z  A>S -> A  bearish=1 bullish=1  trigger=quiet-decay
2026-09-12T11:36:36.819Z  A -> A>L  bearish=1 bullish=2  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-12T11:38:36.819Z  A>L -> A  bearish=1 bullish=1  trigger=quiet-decay
2026-09-12T11:45:36.819Z  A -> A>L  bearish=1 bullish=2  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-12T11:47:36.820Z  A>L -> A  bearish=0 bullish=2  trigger=quiet-decay
2026-09-12T11:50:36.820Z  A -> A>L  bearish=0 bullish=2  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-12T11:53:36.820Z  A>L -> A  bearish=1 bullish=2  trigger=quiet-decay
2026-09-12T11:55:36.820Z  A -> A>L  bearish=0 bullish=3  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-12T11:57:36.820Z  A>L -> A  bearish=1 bullish=2  trigger=quiet-decay
2026-09-12T11:59:36.821Z  A -> A>L  bearish=1 bullish=2  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-12T12:01:36.821Z  A>L -> L  bearish=0 bullish=3  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-12T12:03:36.820Z  L -> A  bearish=0 bullish=2  trigger=quiet-decay
2026-09-12T12:06:36.821Z  A -> A>L  bearish=1 bullish=2  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-12T12:11:36.820Z  A>L -> A  bearish=1 bullish=1  trigger=quiet-decay
2026-09-12T12:15:36.822Z  A -> A>S  bearish=3 bullish=1  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-12T12:18:36.820Z  A>S -> A  bearish=1 bullish=1  trigger=quiet-decay
2026-09-12T12:20:36.820Z  A -> A>S  bearish=3 bullish=0  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-12T12:23:36.822Z  A>S -> A  bearish=2 bullish=0  trigger=quiet-decay
2026-09-12T12:29:36.829Z  A -> A>L  bearish=1 bullish=2  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-12T12:31:36.837Z  A>L -> A  bearish=1 bullish=2  trigger=quiet-decay
2026-09-12T12:33:36.842Z  A -> A>L  bearish=1 bullish=2  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-12T12:35:36.842Z  A>L -> A  bearish=1 bullish=2  trigger=quiet-decay
2026-09-12T12:39:36.842Z  A -> A>L  bearish=0 bullish=2  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-12T12:41:36.844Z  A>L -> L  bearish=0 bullish=3  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-12T12:44:36.842Z  L -> A  bearish=2 bullish=1  trigger=quiet-decay
2026-09-12T12:51:36.843Z  A -> A>S  bearish=2 bullish=1  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-12T12:53:36.842Z  A>S -> A  bearish=2 bullish=1  trigger=quiet-decay
2026-09-12T12:55:36.843Z  A -> A>S  bearish=2 bullish=1  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-12T13:02:22.213Z  A>S -> A  bearish=1 bullish=0  trigger=quiet-decay
2026-09-12T13:14:22.216Z  A -> A>L  bearish=0 bullish=3  trigger=net_delta_1m,last_3_delta,volume_ratio,price_vs_vwap
2026-09-12T13:17:22.217Z  A>L -> A  bearish=0 bullish=1  trigger=quiet-decay
2026-09-12T13:45:02.785Z  A -> A>L  bearish=0 bullish=2  trigger=net_delta_1m,last_3_delta,volume_ratio,price_vs_vwap
2026-09-12T13:47:02.786Z  A>L -> A  bearish=1 bullish=0  trigger=quiet-decay
2026-09-12T13:57:02.786Z  A -> A>L  bearish=0 bullish=2  trigger=net_delta_1m,last_3_delta,volume_ratio,price_vs_vwap
2026-09-12T14:00:02.786Z  A>L -> A  bearish=0 bullish=2  trigger=quiet-decay
2026-09-12T14:06:02.785Z  A -> A>L  bearish=0 bullish=2  trigger=net_delta_1m,last_3_delta,volume_ratio,price_vs_vwap
2026-09-12T14:14:14.951Z  A>L -> A  bearish=0 bullish=1  trigger=quiet-decay
2026-09-12T14:40:14.500Z  A -> A>L  bearish=0 bullish=2  trigger=net_delta_1m,last_3_delta,price_vs_vwap
2026-09-12T14:42:14.501Z  A>L -> A  bearish=0 bullish=2  trigger=quiet-decay
2026-09-12T14:46:14.503Z  A -> A>S  bearish=2 bullish=0  trigger=net_delta_1m,last_3_delta,price_vs_vwap
2026-09-12T14:48:14.503Z  A>S -> A  bearish=0 bullish=1  trigger=quiet-decay
2026-09-12T14:54:14.506Z  A -> A>L  bearish=0 bullish=3  trigger=net_delta_1m,last_3_delta,volume_ratio,price_vs_vwap
2026-09-12T14:56:14.504Z  A>L -> A  bearish=1 bullish=0  trigger=quiet-decay
2026-09-12T14:58:14.504Z  A -> A>S  bearish=2 bullish=0  trigger=net_delta_1m,last_3_delta,volume_ratio,price_vs_vwap
2026-09-12T15:00:14.506Z  A>S -> S  bearish=3 bullish=0  trigger=net_delta_1m,last_3_delta,volume_ratio,price_vs_vwap
2026-09-12T15:02:14.505Z  S -> A  bearish=0 bullish=1  trigger=quiet-decay
2026-09-12T15:06:14.505Z  A -> A>S  bearish=2 bullish=0  trigger=net_delta_1m,last_3_delta,volume_ratio,price_vs_vwap
2026-09-12T15:08:14.506Z  A>S -> A  bearish=0 bullish=1  trigger=quiet-decay
2026-09-12T15:13:14.505Z  A -> A>S  bearish=2 bullish=0  trigger=net_delta_1m,last_3_delta,volume_ratio,price_vs_vwap
2026-09-12T15:15:14.505Z  A>S -> A  bearish=1 bullish=0  trigger=quiet-decay
2026-09-12T15:24:14.506Z  A -> A>S  bearish=2 bullish=0  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-12T15:26:14.505Z  A>S -> A  bearish=2 bullish=0  trigger=quiet-decay
2026-09-12T15:38:14.521Z  A -> A>S  bearish=3 bullish=1  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-12T15:42:14.523Z  A>S -> A  bearish=2 bullish=1  trigger=quiet-decay
2026-09-12T15:44:14.524Z  A -> A>S  bearish=3 bullish=1  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-12T15:47:14.526Z  A>S -> A  bearish=1 bullish=2  trigger=quiet-decay
2026-09-12T15:49:14.526Z  A -> A>S  bearish=2 bullish=1  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-12T15:51:14.526Z  A>S -> S  bearish=3 bullish=0  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-12T15:56:14.526Z  S -> A  bearish=2 bullish=1  trigger=quiet-decay
2026-09-12T15:59:14.526Z  A -> A>S  bearish=4 bullish=0  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-12T16:01:14.526Z  A>S -> A  bearish=2 bullish=1  trigger=quiet-decay
2026-09-12T16:06:14.527Z  A -> A>S  bearish=4 bullish=0  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-12T16:13:14.528Z  A>S -> S  bearish=3 bullish=0  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-12T16:16:14.528Z  S -> A  bearish=2 bullish=1  trigger=quiet-decay
2026-09-12T16:25:14.528Z  A -> A>S  bearish=2 bullish=1  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-12T16:27:14.528Z  A>S -> S  bearish=3 bullish=0  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-12T16:35:14.542Z  S -> A  bearish=2 bullish=1  trigger=quiet-decay
2026-09-12T16:38:14.545Z  A -> A>S  bearish=2 bullish=1  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-12T16:44:14.548Z  A>S -> A  bearish=1 bullish=2  trigger=quiet-decay
2026-09-12T16:46:14.548Z  A -> A>S  bearish=2 bullish=1  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-12T16:48:14.548Z  A>S -> A  bearish=1 bullish=2  trigger=quiet-decay
2026-09-12T16:51:14.549Z  A -> A>L  bearish=1 bullish=2  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-12T16:53:14.549Z  A>L -> A  bearish=1 bullish=2  trigger=quiet-decay
2026-09-12T16:55:14.551Z  A -> A>L  bearish=1 bullish=2  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-12T16:57:14.550Z  A>L -> A  bearish=2 bullish=2  trigger=quiet-decay
2026-09-12T17:03:14.551Z  A -> A>S  bearish=2 bullish=1  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-12T17:06:14.552Z  A>S -> A  bearish=0 bullish=2  trigger=quiet-decay
2026-09-12T17:08:14.551Z  A -> A>L  bearish=0 bullish=3  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-12T17:10:14.550Z  A>L -> L  bearish=0 bullish=3  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-12T17:13:14.553Z  L -> A  bearish=1 bullish=2  trigger=quiet-decay
2026-09-12T17:15:14.552Z  A -> A>S  bearish=2 bullish=1  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-12T17:17:14.552Z  A>S -> S  bearish=4 bullish=1  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-12T17:19:14.554Z  S -> A  bearish=2 bullish=1  trigger=quiet-decay
2026-09-12T17:23:14.552Z  A -> A>S  bearish=2 bullish=0  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-12T17:25:14.553Z  A>S -> S  bearish=5 bullish=0  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-12T17:27:14.552Z  S -> A  bearish=2 bullish=1  trigger=quiet-decay
2026-09-12T17:30:14.560Z  A -> A>S  bearish=3 bullish=0  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-12T17:32:14.562Z  A>S -> S  bearish=4 bullish=0  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-12T17:36:14.567Z  S -> A  bearish=2 bullish=1  trigger=quiet-decay
2026-09-12T17:38:14.565Z  A -> A>S  bearish=2 bullish=1  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-12T17:40:14.566Z  A>S -> S  bearish=4 bullish=0  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-12T17:47:14.568Z  S -> A  bearish=2 bullish=1  trigger=quiet-decay
2026-09-12T17:49:14.570Z  A -> A>S  bearish=4 bullish=0  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-12T17:55:14.572Z  A>S -> A  bearish=2 bullish=1  trigger=quiet-decay
2026-09-12T17:58:14.571Z  A -> A>S  bearish=2 bullish=1  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-12T18:00:14.572Z  A>S -> S  bearish=3 bullish=0  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-12T18:08:14.574Z  S -> A  bearish=2 bullish=1  trigger=quiet-decay
2026-09-12T18:11:14.575Z  A -> A>S  bearish=4 bullish=0  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-12T18:13:14.575Z  A>S -> S  bearish=4 bullish=0  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-12T18:20:14.574Z  S -> A  bearish=2 bullish=1  trigger=quiet-decay
2026-09-12T18:23:14.575Z  A -> A>S  bearish=3 bullish=0  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-12T18:26:14.575Z  A>S -> S  bearish=3 bullish=0  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-12T18:29:14.578Z  S -> A  bearish=2 bullish=1  trigger=quiet-decay
2026-09-12T18:32:14.582Z  A -> A>S  bearish=2 bullish=1  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-12T18:34:14.583Z  A>S -> A  bearish=2 bullish=2  trigger=quiet-decay
2026-09-12T18:36:14.586Z  A -> A>S  bearish=3 bullish=0  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-12T18:39:14.588Z  A>S -> A  bearish=2 bullish=1  trigger=quiet-decay
2026-09-12T19:26:15.019Z  A -> A>S  bearish=2 bullish=0  trigger=net_delta_1m,last_3_delta,volume_ratio,price_vs_vwap
2026-09-12T19:28:15.019Z  A>S -> A  bearish=0 bullish=2  trigger=quiet-decay
2026-09-12T19:52:15.418Z  A -> A>S  bearish=2 bullish=0  trigger=net_delta_1m,last_3_delta,price_vs_vwap
2026-09-12T19:54:15.438Z  A>S -> A  bearish=0 bullish=1  trigger=quiet-decay
2026-09-12T20:16:14.860Z  A -> A>L  bearish=0 bullish=3  trigger=net_delta_1m,last_3_delta,volume_ratio,price_vs_vwap
2026-09-12T20:18:14.861Z  A>L -> L  bearish=0 bullish=3  trigger=net_delta_1m,last_3_delta,volume_ratio,price_vs_vwap
2026-09-12T20:20:14.861Z  L -> A  bearish=0 bullish=1  trigger=quiet-decay
2026-09-12T20:28:14.864Z  A -> A>L  bearish=0 bullish=2  trigger=net_delta_1m,last_3_delta,volume_ratio,price_vs_vwap
2026-09-12T20:36:14.862Z  A>L -> A  bearish=2 bullish=0  trigger=quiet-decay
2026-09-13T09:08:15.087Z  A -> A>L  bearish=0 bullish=2  trigger=net_delta_1m,last_3_delta,price_vs_vwap
2026-09-13T09:10:15.088Z  A>L -> A  bearish=0 bullish=1  trigger=quiet-decay
2026-09-13T09:12:15.087Z  A -> A>S  bearish=2 bullish=0  trigger=net_delta_1m,last_3_delta,volume_ratio,price_vs_vwap
2026-09-13T09:14:15.092Z  A>S -> A  bearish=0 bullish=1  trigger=quiet-decay
2026-09-13T09:16:15.103Z  A -> A>S  bearish=2 bullish=0  trigger=net_delta_1m,last_3_delta,volume_ratio,price_vs_vwap
2026-09-13T09:18:15.109Z  A>S -> A  bearish=1 bullish=0  trigger=quiet-decay
2026-09-13T09:22:15.109Z  A -> A>L  bearish=0 bullish=2  trigger=net_delta_1m,last_3_delta,volume_ratio,price_vs_vwap
2026-09-13T09:24:15.109Z  A>L -> A  bearish=1 bullish=2  trigger=quiet-decay
2026-09-13T09:26:15.109Z  A -> A>S  bearish=3 bullish=0  trigger=net_delta_1m,last_3_delta,volume_ratio,price_vs_vwap
2026-09-13T09:28:15.110Z  A>S -> A  bearish=1 bullish=1  trigger=quiet-decay
2026-09-13T09:32:15.109Z  A -> A>S  bearish=3 bullish=0  trigger=net_delta_1m,last_3_delta,volume_ratio,price_vs_vwap
2026-09-13T09:34:15.110Z  A>S -> S  bearish=4 bullish=0  trigger=net_delta_1m,last_3_delta,volume_ratio,price_vs_vwap
2026-09-13T09:36:15.109Z  S -> A  bearish=0 bullish=1  trigger=quiet-decay
2026-09-13T09:45:15.110Z  A -> A>S  bearish=2 bullish=0  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-13T09:47:15.112Z  A>S -> A  bearish=1 bullish=1  trigger=quiet-decay
2026-09-13T09:49:15.110Z  A -> A>L  bearish=1 bullish=3  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-13T09:51:15.112Z  A>L -> A  bearish=2 bullish=1  trigger=quiet-decay
2026-09-13T09:53:15.111Z  A -> A>S  bearish=3 bullish=0  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-13T09:57:15.111Z  A>S -> A  bearish=2 bullish=0  trigger=quiet-decay
2026-09-13T10:00:15.113Z  A -> A>L  bearish=0 bullish=5  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-13T10:02:15.113Z  A>L -> L  bearish=0 bullish=4  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-13T10:04:15.114Z  L -> A  bearish=1 bullish=2  trigger=quiet-decay
2026-09-13T10:07:15.112Z  A -> A>S  bearish=2 bullish=1  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-13T10:11:15.112Z  A>S -> A  bearish=1 bullish=1  trigger=quiet-decay
2026-09-13T10:14:15.115Z  A -> A>L  bearish=0 bullish=3  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-13T10:17:15.129Z  A>L -> L  bearish=0 bullish=3  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-13T10:20:15.133Z  L -> A  bearish=0 bullish=2  trigger=quiet-decay
2026-09-13T10:35:14.535Z  A -> A>L  bearish=0 bullish=2  trigger=net_delta_1m,last_3_delta,price_vs_vwap
2026-09-13T10:37:14.535Z  A>L -> A  bearish=0 bullish=2  trigger=quiet-decay
2026-09-13T10:43:14.535Z  A -> A>S  bearish=3 bullish=0  trigger=net_delta_1m,last_3_delta,volume_ratio,price_vs_vwap
2026-09-13T10:45:14.537Z  A>S -> S  bearish=4 bullish=0  trigger=net_delta_1m,last_3_delta,volume_ratio,price_vs_vwap
2026-09-13T10:47:14.537Z  S -> A  bearish=0 bullish=1  trigger=quiet-decay
2026-09-13T10:52:14.538Z  A -> A>S  bearish=4 bullish=0  trigger=net_delta_1m,last_3_delta,volume_ratio,price_vs_vwap
2026-09-13T10:54:14.539Z  A>S -> S  bearish=4 bullish=0  trigger=net_delta_1m,last_3_delta,volume_ratio,price_vs_vwap
2026-09-13T10:56:14.537Z  S -> A  bearish=2 bullish=0  trigger=quiet-decay
2026-09-13T10:59:14.537Z  A -> A>S  bearish=2 bullish=0  trigger=net_delta_1m,last_3_delta,volume_ratio,price_vs_vwap
2026-09-13T11:01:14.537Z  A>S -> A  bearish=0 bullish=1  trigger=quiet-decay
2026-09-13T11:10:14.538Z  A -> A>S  bearish=2 bullish=0  trigger=net_delta_1m,last_3_delta,volume_ratio,price_vs_vwap
2026-09-13T11:13:14.537Z  A>S -> S  bearish=4 bullish=0  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-13T11:17:14.548Z  S -> A  bearish=2 bullish=1  trigger=quiet-decay
2026-09-13T11:19:14.553Z  A -> A>L  bearish=1 bullish=2  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-13T11:21:14.555Z  A>L -> A  bearish=2 bullish=0  trigger=quiet-decay
2026-09-13T11:24:14.558Z  A -> A>S  bearish=2 bullish=0  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-13T11:26:14.558Z  A>S -> A  bearish=1 bullish=1  trigger=quiet-decay
2026-09-13T11:28:14.559Z  A -> A>L  bearish=1 bullish=2  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-13T11:30:14.560Z  A>L -> A  bearish=1 bullish=2  trigger=quiet-decay
2026-09-13T11:32:14.560Z  A -> A>L  bearish=1 bullish=2  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-13T11:34:14.561Z  A>L -> A  bearish=1 bullish=2  trigger=quiet-decay
2026-09-13T11:36:14.561Z  A -> A>L  bearish=0 bullish=4  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-13T11:38:14.563Z  A>L -> L  bearish=0 bullish=4  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-13T11:43:14.562Z  L -> A  bearish=1 bullish=2  trigger=quiet-decay
2026-09-13T11:45:14.564Z  A -> A>L  bearish=1 bullish=2  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-13T11:48:14.564Z  A>L -> A  bearish=1 bullish=2  trigger=quiet-decay
2026-09-13T11:50:14.562Z  A -> A>L  bearish=0 bullish=3  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-13T11:52:14.563Z  A>L -> L  bearish=0 bullish=4  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-13T11:55:14.562Z  L -> A  bearish=1 bullish=2  trigger=quiet-decay
2026-09-13T11:59:14.565Z  A -> A>L  bearish=0 bullish=3  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-13T12:01:14.565Z  A>L -> A  bearish=1 bullish=2  trigger=quiet-decay
2026-09-13T12:03:14.564Z  A -> A>L  bearish=1 bullish=2  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-13T12:05:14.565Z  A>L -> A  bearish=2 bullish=2  trigger=quiet-decay
2026-09-13T12:07:14.564Z  A -> A>L  bearish=0 bullish=3  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-13T12:09:14.565Z  A>L -> A  bearish=0 bullish=2  trigger=quiet-decay
2026-09-13T12:11:14.565Z  A -> A>L  bearish=1 bullish=3  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-13T12:13:14.564Z  A>L -> L  bearish=1 bullish=3  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-13T12:20:14.575Z  L -> A  bearish=1 bullish=2  trigger=quiet-decay
2026-09-13T12:22:14.578Z  A -> A>S  bearish=2 bullish=1  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-13T12:35:14.582Z  A>S -> A  bearish=1 bullish=2  trigger=quiet-decay
2026-09-13T12:41:14.583Z  A -> A>L  bearish=1 bullish=2  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-13T12:43:14.582Z  A>L -> A  bearish=2 bullish=2  trigger=quiet-decay
2026-09-13T12:45:14.583Z  A -> A>S  bearish=2 bullish=1  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-13T12:47:14.582Z  A>S -> A  bearish=0 bullish=2  trigger=quiet-decay
2026-09-13T12:49:14.583Z  A -> A>L  bearish=0 bullish=2  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-13T12:51:14.583Z  A>L -> A  bearish=1 bullish=1  trigger=quiet-decay
2026-09-13T12:55:14.583Z  A -> A>S  bearish=2 bullish=0  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-13T12:57:14.583Z  A>S -> S  bearish=3 bullish=0  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-13T13:02:14.584Z  S -> A  bearish=2 bullish=0  trigger=quiet-decay
2026-09-13T13:04:14.583Z  A -> A>S  bearish=3 bullish=0  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-13T13:07:14.585Z  A>S -> A  bearish=2 bullish=0  trigger=quiet-decay
2026-09-13T13:10:14.584Z  A -> A>S  bearish=2 bullish=0  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-13T13:12:14.585Z  A>S -> S  bearish=3 bullish=0  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-13T13:14:14.587Z  S -> A  bearish=2 bullish=1  trigger=quiet-decay
2026-09-13T13:17:14.596Z  A -> A>S  bearish=2 bullish=0  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-13T13:20:14.600Z  A>S -> A  bearish=2 bullish=0  trigger=quiet-decay
2026-09-13T13:22:14.605Z  A -> A>S  bearish=4 bullish=0  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-13T13:27:14.607Z  A>S -> S  bearish=3 bullish=0  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-13T13:31:14.610Z  S -> A  bearish=2 bullish=1  trigger=quiet-decay
2026-09-13T13:39:14.611Z  A -> A>S  bearish=2 bullish=0  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-13T13:41:14.610Z  A>S -> A  bearish=1 bullish=1  trigger=quiet-decay
2026-09-13T13:43:14.611Z  A -> A>L  bearish=1 bullish=3  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-13T13:45:14.611Z  A>L -> L  bearish=0 bullish=4  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-13T13:55:14.614Z  L -> A  bearish=1 bullish=2  trigger=quiet-decay
2026-09-13T13:58:14.612Z  A -> A>L  bearish=0 bullish=3  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-13T14:00:14.613Z  A>L -> A  bearish=1 bullish=2  trigger=quiet-decay
2026-09-13T14:03:14.613Z  A -> A>L  bearish=0 bullish=3  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-13T14:06:14.612Z  A>L -> L  bearish=0 bullish=3  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-13T14:19:14.626Z  L -> A  bearish=1 bullish=2  trigger=quiet-decay
2026-09-13T14:21:14.629Z  A -> A>L  bearish=0 bullish=3  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-13T14:23:14.629Z  A>L -> A  bearish=1 bullish=2  trigger=quiet-decay
2026-09-13T14:25:14.629Z  A -> A>L  bearish=1 bullish=2  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-13T14:27:14.631Z  A>L -> A  bearish=2 bullish=2  trigger=quiet-decay
2026-09-13T14:29:14.631Z  A -> A>L  bearish=0 bullish=4  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-13T14:31:14.631Z  A>L -> A  bearish=1 bullish=2  trigger=quiet-decay
2026-09-13T14:36:14.633Z  A -> A>L  bearish=0 bullish=3  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-13T14:38:14.634Z  A>L -> L  bearish=0 bullish=4  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-13T14:41:14.635Z  L -> A  bearish=1 bullish=2  trigger=quiet-decay
2026-09-13T14:43:14.635Z  A -> A>L  bearish=0 bullish=3  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-13T14:46:14.635Z  A>L -> L  bearish=0 bullish=3  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-13T14:49:14.639Z  L -> A  bearish=1 bullish=2  trigger=quiet-decay
2026-09-13T14:54:14.635Z  A -> A>L  bearish=1 bullish=2  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-13T14:56:14.637Z  A>L -> A  bearish=2 bullish=2  trigger=quiet-decay
2026-09-13T14:59:14.637Z  A -> A>L  bearish=0 bullish=3  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-13T15:03:14.637Z  A>L -> A  bearish=1 bullish=2  trigger=quiet-decay
2026-09-13T15:06:14.637Z  A -> A>L  bearish=1 bullish=2  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-13T15:08:14.638Z  A>L -> A  bearish=0 bullish=2  trigger=quiet-decay
2026-09-13T15:11:14.638Z  A -> A>S  bearish=2 bullish=1  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-13T15:13:14.638Z  A>S -> S  bearish=3 bullish=1  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-13T15:16:14.642Z  S -> A  bearish=2 bullish=1  trigger=quiet-decay
2026-09-13T15:18:14.643Z  A -> A>S  bearish=4 bullish=1  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-13T15:21:14.648Z  A>S -> A  bearish=2 bullish=1  trigger=quiet-decay
2026-09-13T15:23:14.648Z  A -> A>L  bearish=1 bullish=2  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-13T15:25:14.651Z  A>L -> L  bearish=1 bullish=3  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-13T15:27:14.652Z  L -> A  bearish=2 bullish=1  trigger=quiet-decay
2026-09-13T15:29:14.653Z  A -> A>S  bearish=4 bullish=1  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-13T15:32:14.654Z  A>S -> A  bearish=2 bullish=1  trigger=quiet-decay
2026-09-13T15:34:14.654Z  A -> A>L  bearish=1 bullish=2  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-13T15:36:14.656Z  A>L -> A  bearish=2 bullish=1  trigger=quiet-decay
2026-09-13T15:38:14.657Z  A -> A>S  bearish=3 bullish=1  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-13T15:40:14.657Z  A>S -> S  bearish=3 bullish=1  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-13T15:42:14.658Z  S -> A  bearish=1 bullish=2  trigger=quiet-decay
2026-09-13T15:45:14.659Z  A -> A>L  bearish=1 bullish=2  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-13T15:47:14.659Z  A>L -> A  bearish=2 bullish=1  trigger=quiet-decay
2026-09-13T15:51:14.660Z  A -> A>S  bearish=2 bullish=1  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-13T15:53:14.661Z  A>S -> A  bearish=2 bullish=1  trigger=quiet-decay
2026-09-13T15:55:14.661Z  A -> A>S  bearish=3 bullish=1  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-13T15:57:14.661Z  A>S -> S  bearish=3 bullish=1  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-13T15:59:14.662Z  S -> A  bearish=2 bullish=1  trigger=quiet-decay
2026-09-13T16:01:14.661Z  A -> A>L  bearish=1 bullish=2  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-13T16:13:14.663Z  A>L -> L  bearish=1 bullish=3  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-13T16:15:14.665Z  L -> A  bearish=2 bullish=1  trigger=quiet-decay
2026-09-13T16:21:14.670Z  A -> A>L  bearish=1 bullish=2  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-13T16:24:14.672Z  A>L -> A  bearish=1 bullish=2  trigger=quiet-decay
2026-09-13T16:26:14.674Z  A -> A>L  bearish=1 bullish=3  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-13T16:28:14.675Z  A>L -> L  bearish=1 bullish=3  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-13T16:30:14.676Z  L -> A  bearish=1 bullish=2  trigger=quiet-decay
2026-09-13T16:32:14.678Z  A -> A>L  bearish=1 bullish=2  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-13T16:37:14.680Z  A>L -> L  bearish=0 bullish=3  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-13T16:45:14.681Z  L -> A  bearish=1 bullish=2  trigger=quiet-decay
2026-09-13T16:52:14.681Z  A -> A>L  bearish=1 bullish=2  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-13T16:54:14.681Z  A>L -> L  bearish=0 bullish=3  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-13T17:15:14.686Z  L -> A  bearish=1 bullish=2  trigger=quiet-decay
2026-09-13T17:17:14.688Z  A -> A>L  bearish=1 bullish=2  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-13T17:21:14.692Z  A>L -> A  bearish=1 bullish=2  trigger=quiet-decay
2026-09-13T17:36:14.702Z  A -> A>L  bearish=1 bullish=2  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-13T17:38:14.702Z  A>L -> A  bearish=1 bullish=2  trigger=quiet-decay
2026-09-13T17:40:14.704Z  A -> A>S  bearish=2 bullish=1  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-13T17:42:14.704Z  A>S -> S  bearish=3 bullish=1  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-13T17:45:14.704Z  S -> A  bearish=1 bullish=2  trigger=quiet-decay
2026-09-13T17:47:14.705Z  A -> A>L  bearish=1 bullish=3  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-13T17:49:14.704Z  A>L -> L  bearish=1 bullish=3  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-13T17:51:14.705Z  L -> A  bearish=1 bullish=2  trigger=quiet-decay
2026-09-13T17:53:14.705Z  A -> A>S  bearish=2 bullish=1  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-13T17:55:14.706Z  A>S -> S  bearish=3 bullish=1  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-13T17:59:14.707Z  S -> A  bearish=2 bullish=1  trigger=quiet-decay
2026-09-13T18:02:14.707Z  A -> A>S  bearish=2 bullish=1  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-13T18:04:14.707Z  A>S -> A  bearish=2 bullish=1  trigger=quiet-decay
2026-09-13T18:09:14.708Z  A -> A>S  bearish=2 bullish=1  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-13T18:11:14.708Z  A>S -> S  bearish=3 bullish=1  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-13T18:15:14.712Z  S -> S>L  bearish=1 bullish=3  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-13T18:17:14.713Z  S>L -> L  bearish=1 bullish=3  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-13T18:19:14.716Z  L -> A  bearish=1 bullish=2  trigger=quiet-decay
2026-09-13T18:28:14.721Z  A -> A>L  bearish=0 bullish=3  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-13T18:34:14.725Z  A>L -> A  bearish=1 bullish=2  trigger=quiet-decay
2026-09-13T18:36:14.725Z  A -> A>L  bearish=0 bullish=3  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-13T18:38:14.725Z  A>L -> A  bearish=1 bullish=2  trigger=quiet-decay
2026-09-13T18:40:14.726Z  A -> A>L  bearish=0 bullish=2  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-13T18:42:14.727Z  A>L -> A  bearish=1 bullish=2  trigger=quiet-decay
2026-09-13T18:46:14.729Z  A -> A>S  bearish=2 bullish=1  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-13T18:48:14.729Z  A>S -> S  bearish=3 bullish=1  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-13T18:57:14.732Z  S -> A  bearish=2 bullish=1  trigger=quiet-decay
2026-09-13T19:01:14.731Z  A -> A>L  bearish=1 bullish=2  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-13T19:03:14.732Z  A>L -> L  bearish=1 bullish=3  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-13T19:05:14.731Z  L -> A  bearish=1 bullish=2  trigger=quiet-decay
2026-09-13T19:07:14.732Z  A -> A>L  bearish=1 bullish=4  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-13T19:18:14.737Z  A>L -> A  bearish=0 bullish=2  trigger=quiet-decay
2026-09-13T19:21:14.741Z  A -> A>L  bearish=1 bullish=2  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-13T19:26:14.743Z  A>L -> A  bearish=1 bullish=2  trigger=quiet-decay
2026-09-13T19:29:14.747Z  A -> A>L  bearish=0 bullish=2  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-13T19:31:14.747Z  A>L -> A  bearish=2 bullish=1  trigger=quiet-decay
2026-09-13T19:33:14.748Z  A -> A>S  bearish=3 bullish=1  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-13T19:36:14.749Z  A>S -> A  bearish=1 bullish=2  trigger=quiet-decay
2026-09-13T19:38:14.749Z  A -> A>S  bearish=2 bullish=1  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-13T19:41:14.750Z  A>S -> A  bearish=1 bullish=2  trigger=quiet-decay
2026-09-13T19:44:14.752Z  A -> A>L  bearish=1 bullish=2  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-13T19:47:14.751Z  A>L -> A  bearish=2 bullish=1  trigger=quiet-decay
2026-09-13T19:49:14.752Z  A -> A>L  bearish=1 bullish=2  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-13T19:51:14.752Z  A>L -> A  bearish=1 bullish=2  trigger=quiet-decay
2026-09-13T19:53:14.753Z  A -> A>S  bearish=2 bullish=1  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-14T08:42:22.580Z  A>S -> A  bearish=1 bullish=0  trigger=quiet-decay
2026-09-14T08:55:22.581Z  A -> A>S  bearish=2 bullish=0  trigger=net_delta_1m,last_3_delta,volume_ratio,price_vs_vwap
2026-09-14T09:02:15.726Z  A>S -> A  bearish=0 bullish=1  trigger=quiet-decay
2026-09-14T09:11:15.728Z  A -> A>S  bearish=2 bullish=0  trigger=net_delta_1m,last_3_delta,volume_ratio,price_vs_vwap
2026-09-14T09:15:15.733Z  A>S -> A  bearish=2 bullish=0  trigger=quiet-decay
2026-09-14T09:20:15.744Z  A -> A>S  bearish=2 bullish=0  trigger=net_delta_1m,last_3_delta,volume_ratio,price_vs_vwap
2026-09-14T09:24:15.749Z  A>S -> S  bearish=4 bullish=0  trigger=net_delta_1m,last_3_delta,volume_ratio,price_vs_vwap
2026-09-14T09:29:15.752Z  S -> A  bearish=0 bullish=1  trigger=quiet-decay
2026-09-14T09:40:15.754Z  A -> A>S  bearish=2 bullish=1  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-14T09:42:15.755Z  A>S -> A  bearish=1 bullish=2  trigger=quiet-decay
2026-09-14T09:46:15.755Z  A -> A>L  bearish=1 bullish=2  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-14T09:48:15.755Z  A>L -> L  bearish=1 bullish=4  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-14T09:50:15.756Z  L -> A  bearish=1 bullish=2  trigger=quiet-decay
2026-09-14T09:52:15.757Z  A -> A>L  bearish=0 bullish=5  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-14T09:54:15.755Z  A>L -> L  bearish=0 bullish=5  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-14T09:56:15.757Z  L -> A  bearish=1 bullish=2  trigger=quiet-decay
2026-09-14T09:58:15.759Z  A -> A>L  bearish=0 bullish=4  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-14T10:02:15.757Z  A>L -> A  bearish=1 bullish=1  trigger=quiet-decay
2026-09-14T10:05:15.758Z  A -> A>L  bearish=1 bullish=2  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-14T10:07:15.757Z  A>L -> A  bearish=2 bullish=1  trigger=quiet-decay
2026-09-14T10:18:15.768Z  A -> A>S  bearish=2 bullish=1  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-14T10:21:15.772Z  A>S -> A  bearish=2 bullish=1  trigger=quiet-decay
2026-09-14T10:24:15.776Z  A -> A>S  bearish=3 bullish=0  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-14T10:28:15.777Z  A>S -> S  bearish=3 bullish=0  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-14T10:34:15.779Z  S -> A  bearish=2 bullish=1  trigger=quiet-decay
2026-09-14T10:36:15.779Z  A -> A>S  bearish=2 bullish=1  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-14T10:39:15.780Z  A>S -> S  bearish=3 bullish=0  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-14T10:42:15.780Z  S -> A  bearish=2 bullish=1  trigger=quiet-decay
2026-09-14T10:45:15.781Z  A -> A>S  bearish=2 bullish=1  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-14T10:47:15.782Z  A>S -> A  bearish=2 bullish=2  trigger=quiet-decay
2026-09-14T10:49:15.780Z  A -> A>S  bearish=2 bullish=1  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-14T10:52:15.786Z  A>S -> S  bearish=4 bullish=0  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-14T10:57:15.782Z  S -> A  bearish=2 bullish=1  trigger=quiet-decay
2026-09-14T10:59:15.788Z  A -> A>S  bearish=2 bullish=1  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-14T11:01:15.782Z  A>S -> S  bearish=4 bullish=0  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-14T11:06:15.782Z  S -> A  bearish=2 bullish=1  trigger=quiet-decay
2026-09-14T11:09:15.782Z  A -> A>S  bearish=2 bullish=1  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-14T11:14:15.785Z  A>S -> S  bearish=3 bullish=0  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-14T11:19:15.793Z  S -> A  bearish=2 bullish=1  trigger=quiet-decay
2026-09-14T11:28:15.797Z  A -> A>S  bearish=2 bullish=1  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-14T11:30:15.800Z  A>S -> A  bearish=2 bullish=2  trigger=quiet-decay
2026-09-14T11:35:15.800Z  A -> A>S  bearish=3 bullish=1  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-14T11:40:15.800Z  A>S -> A  bearish=2 bullish=1  trigger=quiet-decay
2026-09-14T11:44:15.800Z  A -> A>L  bearish=1 bullish=2  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-14T11:47:15.802Z  A>L -> A  bearish=2 bullish=1  trigger=quiet-decay
2026-09-14T11:49:15.801Z  A -> A>S  bearish=3 bullish=1  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-14T11:51:15.801Z  A>S -> S  bearish=3 bullish=1  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-14T11:57:15.802Z  S -> A  bearish=2 bullish=1  trigger=quiet-decay
2026-09-14T12:00:15.805Z  A -> A>S  bearish=2 bullish=1  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-14T12:02:15.803Z  A>S -> S  bearish=3 bullish=1  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-14T12:04:15.804Z  S -> A  bearish=2 bullish=1  trigger=quiet-decay
2026-09-14T12:06:15.803Z  A -> A>S  bearish=4 bullish=0  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-14T12:08:15.807Z  A>S -> S  bearish=4 bullish=0  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-14T12:12:15.809Z  S -> A  bearish=2 bullish=1  trigger=quiet-decay
2026-09-14T12:15:15.804Z  A -> A>S  bearish=2 bullish=1  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-14T12:19:15.811Z  A>S -> A  bearish=2 bullish=1  trigger=quiet-decay
2026-09-14T12:22:15.813Z  A -> A>S  bearish=3 bullish=0  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-14T12:24:15.814Z  A>S -> A  bearish=1 bullish=2  trigger=quiet-decay
2026-09-14T12:26:15.815Z  A -> A>S  bearish=2 bullish=0  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-14T12:28:15.817Z  A>S -> A  bearish=0 bullish=2  trigger=quiet-decay
2026-09-14T12:32:15.818Z  A -> A>L  bearish=0 bullish=3  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-14T12:39:15.821Z  A>L -> A  bearish=1 bullish=2  trigger=quiet-decay
2026-09-14T12:41:15.821Z  A -> A>S  bearish=2 bullish=1  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-14T12:43:15.822Z  A>S -> A  bearish=1 bullish=2  trigger=quiet-decay
2026-09-14T12:46:15.822Z  A -> A>S  bearish=4 bullish=0  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-14T12:49:15.822Z  A>S -> S  bearish=3 bullish=0  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-14T13:01:15.826Z  S -> A  bearish=2 bullish=1  trigger=quiet-decay
2026-09-14T13:03:15.825Z  A -> A>S  bearish=3 bullish=0  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-14T13:05:15.825Z  A>S -> A  bearish=2 bullish=1  trigger=quiet-decay
2026-09-14T13:07:15.826Z  A -> A>S  bearish=4 bullish=0  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-14T13:11:15.826Z  A>S -> A  bearish=2 bullish=1  trigger=quiet-decay
2026-09-14T13:15:15.828Z  A -> A>S  bearish=2 bullish=1  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-14T13:17:15.831Z  A>S -> A  bearish=2 bullish=2  trigger=quiet-decay
2026-09-14T13:31:15.616Z  A -> A>L  bearish=0 bullish=3  trigger=net_delta_1m,last_3_delta,price_vs_vwap
2026-09-14T13:33:15.620Z  A>L -> A  bearish=0 bullish=2  trigger=quiet-decay
2026-09-14T13:36:15.620Z  A -> A>S  bearish=3 bullish=0  trigger=net_delta_1m,last_3_delta,volume_ratio,price_vs_vwap
2026-09-14T13:39:15.618Z  A>S -> A  bearish=1 bullish=1  trigger=quiet-decay
2026-09-14T13:42:15.619Z  A -> A>S  bearish=2 bullish=0  trigger=net_delta_1m,last_3_delta,volume_ratio,price_vs_vwap
2026-09-14T13:44:15.620Z  A>S -> A  bearish=0 bullish=2  trigger=quiet-decay
2026-09-14T13:46:15.620Z  A -> A>L  bearish=0 bullish=3  trigger=net_delta_1m,last_3_delta,volume_ratio,price_vs_vwap
2026-09-14T13:48:15.624Z  A>L -> L  bearish=0 bullish=3  trigger=net_delta_1m,last_3_delta,volume_ratio,price_vs_vwap
2026-09-14T13:52:15.621Z  L -> A  bearish=1 bullish=1  trigger=quiet-decay
2026-09-14T13:54:15.625Z  A -> A>S  bearish=2 bullish=1  trigger=net_delta_1m,last_3_delta,volume_ratio,price_vs_vwap
2026-09-14T13:56:15.624Z  A>S -> A  bearish=2 bullish=0  trigger=quiet-decay
2026-09-14T13:58:15.626Z  A -> A>S  bearish=3 bullish=0  trigger=net_delta_1m,last_3_delta,volume_ratio,price_vs_vwap
2026-09-14T14:00:15.625Z  A>S -> A  bearish=0 bullish=2  trigger=quiet-decay
2026-09-14T14:02:15.624Z  A -> A>L  bearish=0 bullish=3  trigger=net_delta_1m,last_3_delta,volume_ratio,price_vs_vwap
2026-09-14T14:05:15.625Z  A>L -> A  bearish=2 bullish=1  trigger=quiet-decay
2026-09-14T14:07:15.625Z  A -> A>S  bearish=3 bullish=1  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-14T14:09:15.625Z  A>S -> S  bearish=3 bullish=1  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-14T14:12:15.628Z  S -> A  bearish=2 bullish=1  trigger=quiet-decay
2026-09-14T14:16:15.633Z  A -> A>S  bearish=2 bullish=1  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-14T14:18:15.632Z  A>S -> A  bearish=1 bullish=2  trigger=quiet-decay
2026-09-14T14:22:15.634Z  A -> A>S  bearish=2 bullish=1  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-14T14:24:15.636Z  A>S -> S  bearish=3 bullish=1  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-14T14:27:15.637Z  S -> A  bearish=2 bullish=0  trigger=quiet-decay
2026-09-14T14:29:15.639Z  A -> A>L  bearish=1 bullish=2  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-14T14:31:15.644Z  A>L -> L  bearish=1 bullish=3  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-14T14:36:15.642Z  L -> A  bearish=1 bullish=2  trigger=quiet-decay
2026-09-14T14:46:15.646Z  A -> A>L  bearish=1 bullish=2  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-14T14:48:15.646Z  A>L -> A  bearish=2 bullish=2  trigger=quiet-decay
2026-09-14T14:51:15.650Z  A -> A>L  bearish=1 bullish=2  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-14T14:53:15.650Z  A>L -> A  bearish=2 bullish=2  trigger=quiet-decay
2026-09-14T14:56:15.648Z  A -> A>L  bearish=1 bullish=2  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-14T15:00:15.648Z  A>L -> A  bearish=1 bullish=1  trigger=quiet-decay
2026-09-14T15:02:15.648Z  A -> A>S  bearish=3 bullish=1  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-14T15:04:15.650Z  A>S -> S  bearish=3 bullish=0  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-14T15:07:15.649Z  S -> S>L  bearish=1 bullish=3  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-14T15:09:15.660Z  S>L -> L  bearish=1 bullish=3  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-14T15:11:15.650Z  L -> A  bearish=2 bullish=1  trigger=quiet-decay
2026-09-14T15:14:15.650Z  A -> A>L  bearish=1 bullish=2  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-14T15:16:15.659Z  A>L -> A  bearish=2 bullish=1  trigger=quiet-decay
2026-09-14T15:21:15.657Z  A -> A>S  bearish=2 bullish=1  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-14T15:23:15.656Z  A>S -> S  bearish=3 bullish=1  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-14T15:25:15.657Z  S -> A  bearish=2 bullish=1  trigger=quiet-decay
2026-09-14T15:32:15.663Z  A -> A>S  bearish=2 bullish=0  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-14T15:37:15.661Z  A>S -> A  bearish=1 bullish=2  trigger=quiet-decay
2026-09-14T15:39:15.667Z  A -> A>L  bearish=1 bullish=3  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-14T15:44:15.663Z  A>L -> A  bearish=0 bullish=2  trigger=quiet-decay
2026-09-14T15:49:15.664Z  A -> A>L  bearish=0 bullish=3  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-14T15:55:15.665Z  A>L -> A  bearish=1 bullish=2  trigger=quiet-decay
2026-09-14T16:00:15.666Z  A -> A>L  bearish=1 bullish=2  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-14T16:02:15.667Z  A>L -> A  bearish=2 bullish=1  trigger=quiet-decay
2026-09-14T16:04:15.669Z  A -> A>S  bearish=2 bullish=1  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-14T16:06:15.669Z  A>S -> A  bearish=1 bullish=2  trigger=quiet-decay
2026-09-14T16:14:15.667Z  A -> A>S  bearish=2 bullish=1  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-14T16:17:15.671Z  A>S -> A  bearish=1 bullish=2  trigger=quiet-decay
2026-09-14T16:19:15.677Z  A -> A>L  bearish=1 bullish=4  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-14T16:24:15.677Z  A>L -> A  bearish=2 bullish=1  trigger=quiet-decay
2026-09-14T16:26:15.678Z  A -> A>S  bearish=3 bullish=1  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-14T16:29:15.681Z  A>S -> A  bearish=1 bullish=1  trigger=quiet-decay
2026-09-14T16:33:15.683Z  A -> A>L  bearish=1 bullish=2  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-14T16:36:15.684Z  A>L -> A  bearish=1 bullish=2  trigger=quiet-decay
2026-09-14T16:38:15.686Z  A -> A>L  bearish=1 bullish=2  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-14T16:41:15.687Z  A>L -> A  bearish=0 bullish=2  trigger=quiet-decay
2026-09-14T16:47:15.692Z  A -> A>L  bearish=1 bullish=2  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-14T16:50:15.689Z  A>L -> A  bearish=2 bullish=1  trigger=quiet-decay
2026-09-14T16:55:15.690Z  A -> A>L  bearish=1 bullish=2  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-14T16:57:15.690Z  A>L -> A  bearish=2 bullish=1  trigger=quiet-decay
2026-09-14T16:59:15.690Z  A -> A>S  bearish=2 bullish=1  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-14T17:01:15.691Z  A>S -> A  bearish=2 bullish=2  trigger=quiet-decay
2026-09-14T17:03:15.690Z  A -> A>L  bearish=0 bullish=3  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-14T17:06:15.693Z  A>L -> A  bearish=1 bullish=2  trigger=quiet-decay
2026-09-14T17:08:15.691Z  A -> A>L  bearish=1 bullish=2  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-14T17:11:15.694Z  A>L -> A  bearish=2 bullish=2  trigger=quiet-decay
2026-09-14T17:15:15.695Z  A -> A>L  bearish=1 bullish=2  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-14T17:19:15.696Z  A>L -> A  bearish=1 bullish=2  trigger=quiet-decay
2026-09-14T17:21:15.698Z  A -> A>L  bearish=0 bullish=3  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-14T17:24:15.699Z  A>L -> L  bearish=0 bullish=4  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-14T17:26:15.701Z  L -> A  bearish=1 bullish=2  trigger=quiet-decay
2026-09-14T17:29:15.703Z  A -> A>L  bearish=1 bullish=2  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-14T17:31:15.707Z  A>L -> L  bearish=0 bullish=3  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-14T17:33:15.704Z  L -> A  bearish=1 bullish=2  trigger=quiet-decay
2026-09-14T17:36:15.707Z  A -> A>L  bearish=1 bullish=2  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-14T17:39:15.706Z  A>L -> A  bearish=1 bullish=2  trigger=quiet-decay
2026-09-14T17:41:15.710Z  A -> A>L  bearish=1 bullish=2  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-14T17:44:15.707Z  A>L -> A  bearish=1 bullish=2  trigger=quiet-decay
2026-09-14T17:46:15.709Z  A -> A>L  bearish=1 bullish=2  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-14T17:48:15.707Z  A>L -> A  bearish=0 bullish=2  trigger=quiet-decay
2026-09-14T17:55:15.710Z  A -> A>L  bearish=1 bullish=2  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-14T17:58:15.710Z  A>L -> A  bearish=2 bullish=1  trigger=quiet-decay
2026-09-14T18:02:15.720Z  A -> A>S  bearish=2 bullish=1  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-14T18:05:15.716Z  A>S -> A  bearish=2 bullish=1  trigger=quiet-decay
2026-09-14T18:07:15.717Z  A -> A>S  bearish=2 bullish=1  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-14T18:09:15.713Z  A>S -> A  bearish=1 bullish=1  trigger=quiet-decay
2026-09-14T18:12:15.715Z  A -> A>S  bearish=2 bullish=1  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-14T18:14:15.730Z  A>S -> A  bearish=1 bullish=1  trigger=quiet-decay
2026-09-14T18:18:15.720Z  A -> A>S  bearish=2 bullish=1  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-14T18:26:15.725Z  A>S -> A  bearish=1 bullish=2  trigger=quiet-decay
2026-09-14T18:28:15.732Z  A -> A>L  bearish=0 bullish=3  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-14T18:31:15.727Z  A>L -> L  bearish=0 bullish=3  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-14T18:41:15.734Z  L -> A  bearish=1 bullish=2  trigger=quiet-decay
2026-09-14T18:43:15.739Z  A -> A>L  bearish=0 bullish=3  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-14T18:45:15.734Z  A>L -> L  bearish=0 bullish=4  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-14T18:52:15.740Z  L -> A  bearish=1 bullish=2  trigger=quiet-decay
2026-09-14T18:57:15.743Z  A -> A>L  bearish=1 bullish=2  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-14T19:00:15.735Z  A>L -> A  bearish=1 bullish=2  trigger=quiet-decay
2026-09-14T19:03:15.741Z  A -> A>L  bearish=1 bullish=2  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-14T19:05:15.736Z  A>L -> A  bearish=2 bullish=2  trigger=quiet-decay
2026-09-14T19:08:15.736Z  A -> A>L  bearish=1 bullish=2  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-14T19:10:15.736Z  A>L -> A  bearish=2 bullish=2  trigger=quiet-decay
2026-09-14T19:13:15.737Z  A -> A>L  bearish=0 bullish=3  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-14T19:17:15.740Z  A>L -> A  bearish=1 bullish=2  trigger=quiet-decay
2026-09-14T19:21:15.753Z  A -> A>L  bearish=0 bullish=3  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-14T19:23:15.747Z  A>L -> A  bearish=1 bullish=2  trigger=quiet-decay
2026-09-14T19:25:15.746Z  A -> A>L  bearish=1 bullish=3  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-14T19:36:15.752Z  A>L -> A  bearish=2 bullish=1  trigger=quiet-decay
2026-09-14T19:38:15.758Z  A -> A>S  bearish=3 bullish=1  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-14T19:40:15.751Z  A>S -> S  bearish=3 bullish=1  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-14T19:42:15.753Z  S -> A  bearish=2 bullish=1  trigger=quiet-decay
2026-09-14T19:47:15.751Z  A -> A>S  bearish=2 bullish=1  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-14T19:49:15.749Z  A>S -> A  bearish=2 bullish=1  trigger=quiet-decay
2026-09-14T19:52:15.751Z  A -> A>S  bearish=2 bullish=1  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-14T19:54:15.756Z  A>S -> S  bearish=3 bullish=1  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-14T20:04:15.756Z  S -> A  bearish=2 bullish=1  trigger=quiet-decay
2026-09-14T20:06:15.754Z  A -> A>L  bearish=1 bullish=2  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-14T20:08:15.756Z  A>L -> A  bearish=1 bullish=2  trigger=quiet-decay
2026-09-14T20:10:15.756Z  A -> A>S  bearish=2 bullish=1  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-14T20:12:15.756Z  A>S -> A  bearish=1 bullish=2  trigger=quiet-decay
2026-09-14T20:16:15.772Z  A -> A>L  bearish=1 bullish=3  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-14T20:18:15.761Z  A>L -> L  bearish=1 bullish=4  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-14T20:21:15.765Z  L -> A  bearish=1 bullish=2  trigger=quiet-decay
2026-09-14T20:23:15.760Z  A -> A>L  bearish=0 bullish=4  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-14T20:26:15.764Z  A>L -> A  bearish=1 bullish=2  trigger=quiet-decay
2026-09-14T20:29:15.765Z  A -> A>L  bearish=1 bullish=2  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-14T20:31:15.771Z  A>L -> L  bearish=0 bullish=3  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-14T20:33:15.766Z  L -> A  bearish=1 bullish=2  trigger=quiet-decay
2026-09-14T20:35:15.767Z  A -> A>L  bearish=1 bullish=2  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-14T20:37:15.772Z  A>L -> L  bearish=0 bullish=3  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-14T20:46:15.771Z  L -> A  bearish=1 bullish=2  trigger=quiet-decay
2026-09-14T20:49:15.781Z  A -> A>L  bearish=1 bullish=2  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-14T20:51:15.784Z  A>L -> A  bearish=2 bullish=2  trigger=quiet-decay
2026-09-14T20:54:15.778Z  A -> A>L  bearish=0 bullish=3  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-14T20:56:15.777Z  A>L -> A  bearish=1 bullish=2  trigger=quiet-decay
2026-09-14T20:59:15.775Z  A -> A>S  bearish=3 bullish=1  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-14T21:01:15.772Z  A>S -> S  bearish=3 bullish=1  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-14T21:05:15.775Z  S -> A  bearish=1 bullish=2  trigger=quiet-decay
2026-09-14T21:07:15.776Z  A -> A>L  bearish=1 bullish=3  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-14T21:09:15.781Z  A>L -> L  bearish=1 bullish=3  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-14T21:11:15.778Z  L -> A  bearish=2 bullish=1  trigger=quiet-decay
2026-09-14T21:15:15.789Z  A -> A>S  bearish=2 bullish=1  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-14T21:17:15.782Z  A>S -> S  bearish=3 bullish=1  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-14T21:20:15.782Z  S -> A  bearish=1 bullish=2  trigger=quiet-decay
2026-09-14T21:22:15.788Z  A -> A>L  bearish=1 bullish=3  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-14T21:25:15.784Z  A>L -> A  bearish=2 bullish=1  trigger=quiet-decay
2026-09-14T21:27:15.789Z  A -> A>S  bearish=3 bullish=1  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-14T21:30:15.808Z  A>S -> A  bearish=2 bullish=1  trigger=quiet-decay
2026-09-14T21:32:15.788Z  A -> A>L  bearish=1 bullish=2  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-14T21:34:15.785Z  A>L -> A  bearish=1 bullish=2  trigger=quiet-decay
2026-09-14T21:38:15.793Z  A -> A>L  bearish=1 bullish=2  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-14T21:40:15.793Z  A>L -> A  bearish=1 bullish=2  trigger=quiet-decay
2026-09-14T21:46:15.798Z  A -> A>S  bearish=2 bullish=1  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-14T21:49:15.792Z  A>S -> A  bearish=2 bullish=1  trigger=quiet-decay
2026-09-14T21:52:15.793Z  A -> A>S  bearish=2 bullish=1  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-14T21:54:15.794Z  A>S -> S  bearish=3 bullish=0  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-14T21:57:15.798Z  S -> A  bearish=1 bullish=2  trigger=quiet-decay
2026-09-14T22:44:17.466Z  A -> A>L  bearish=0 bullish=2  trigger=net_delta_1m,last_3_delta,volume_ratio,price_vs_vwap
2026-09-14T22:46:17.466Z  A>L -> L  bearish=0 bullish=3  trigger=net_delta_1m,last_3_delta,volume_ratio,price_vs_vwap
2026-09-14T22:48:17.466Z  L -> A  bearish=0 bullish=1  trigger=quiet-decay
2026-09-14T22:54:17.465Z  A -> A>S  bearish=2 bullish=0  trigger=net_delta_1m,last_3_delta,volume_ratio,price_vs_vwap
2026-09-14T22:56:17.466Z  A>S -> A  bearish=0 bullish=1  trigger=quiet-decay
2026-09-14T23:02:17.467Z  A -> A>S  bearish=2 bullish=0  trigger=net_delta_1m,last_3_delta,volume_ratio,price_vs_vwap
2026-09-14T23:04:17.467Z  A>S -> S  bearish=3 bullish=0  trigger=net_delta_1m,last_3_delta,volume_ratio,price_vs_vwap
2026-09-14T23:09:17.466Z  S -> A  bearish=2 bullish=1  trigger=quiet-decay
2026-09-14T23:11:17.466Z  A -> A>S  bearish=2 bullish=1  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-14T23:13:17.465Z  A>S -> A  bearish=2 bullish=2  trigger=quiet-decay
2026-09-14T23:15:17.466Z  A -> A>S  bearish=3 bullish=0  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-14T23:18:17.473Z  A>S -> S  bearish=3 bullish=0  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-14T23:28:17.486Z  S -> A  bearish=2 bullish=2  trigger=quiet-decay
2026-09-14T23:30:17.487Z  A -> A>S  bearish=2 bullish=1  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-14T23:32:17.486Z  A>S -> S  bearish=4 bullish=0  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-14T23:34:17.486Z  S -> A  bearish=2 bullish=1  trigger=quiet-decay
2026-09-14T23:36:17.487Z  A -> A>S  bearish=3 bullish=0  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-14T23:38:17.487Z  A>S -> A  bearish=2 bullish=1  trigger=quiet-decay
2026-09-14T23:41:17.485Z  A -> A>S  bearish=2 bullish=1  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-14T23:43:17.488Z  A>S -> A  bearish=2 bullish=2  trigger=quiet-decay
2026-09-14T23:46:17.485Z  A -> A>S  bearish=3 bullish=0  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-14T23:49:17.487Z  A>S -> S  bearish=3 bullish=0  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-14T23:54:17.488Z  S -> A  bearish=2 bullish=1  trigger=quiet-decay
2026-09-14T23:58:17.487Z  A -> A>S  bearish=3 bullish=0  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-15T00:00:17.487Z  A>S -> A  bearish=1 bullish=1  trigger=quiet-decay
2026-09-15T00:02:17.487Z  A -> A>L  bearish=0 bullish=3  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-15T00:04:17.491Z  A>L -> A  bearish=1 bullish=1  trigger=quiet-decay
2026-09-15T00:06:17.487Z  A -> A>S  bearish=3 bullish=1  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-15T00:08:17.487Z  A>S -> A  bearish=2 bullish=1  trigger=quiet-decay
2026-09-15T00:14:17.487Z  A -> A>S  bearish=3 bullish=1  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-15T00:17:17.491Z  A>S -> A  bearish=2 bullish=1  trigger=quiet-decay
2026-09-15T00:19:17.500Z  A -> A>S  bearish=3 bullish=1  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-15T00:21:17.507Z  A>S -> S  bearish=4 bullish=1  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-15T00:23:17.509Z  S -> A  bearish=2 bullish=1  trigger=quiet-decay
2026-09-15T00:25:17.510Z  A -> A>S  bearish=4 bullish=1  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-15T00:28:17.510Z  A>S -> A  bearish=2 bullish=1  trigger=quiet-decay
2026-09-15T00:31:17.510Z  A -> A>L  bearish=1 bullish=2  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-15T00:35:17.509Z  A>L -> A  bearish=2 bullish=1  trigger=quiet-decay
2026-09-15T00:38:17.510Z  A -> A>S  bearish=2 bullish=1  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-15T00:40:17.510Z  A>S -> S  bearish=3 bullish=0  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-15T00:44:17.512Z  S -> A  bearish=2 bullish=1  trigger=quiet-decay
2026-09-15T00:48:17.511Z  A -> A>S  bearish=2 bullish=1  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-15T00:52:23.043Z  A>S -> A  bearish=2 bullish=1  trigger=quiet-decay
2026-09-15T10:29:22.076Z  A -> A>S  bearish=2 bullish=0  trigger=net_delta_1m,last_3_delta,price_vs_vwap
2026-09-15T10:31:22.079Z  A>S -> S  bearish=3 bullish=0  trigger=net_delta_1m,last_3_delta,price_vs_vwap
2026-09-15T10:33:22.086Z  S -> A  bearish=0 bullish=1  trigger=quiet-decay
2026-09-15T10:44:22.086Z  A -> A>L  bearish=0 bullish=2  trigger=net_delta_1m,last_3_delta,volume_ratio,price_vs_vwap
2026-09-15T10:46:22.085Z  A>L -> L  bearish=0 bullish=3  trigger=net_delta_1m,last_3_delta,volume_ratio,price_vs_vwap
2026-09-15T10:54:22.088Z  L -> A  bearish=1 bullish=0  trigger=quiet-decay
2026-09-15T10:59:22.090Z  A -> A>L  bearish=0 bullish=2  trigger=net_delta_1m,last_3_delta,volume_ratio,price_vs_vwap
2026-09-15T11:01:22.090Z  A>L -> A  bearish=0 bullish=2  trigger=quiet-decay
2026-09-15T11:05:22.088Z  A -> A>L  bearish=0 bullish=3  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-15T11:08:22.092Z  A>L -> L  bearish=0 bullish=3  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-15T11:14:22.089Z  L -> A  bearish=2 bullish=1  trigger=quiet-decay
2026-09-15T11:17:22.095Z  A -> A>L  bearish=0 bullish=2  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-15T11:21:22.093Z  A>L -> A  bearish=0 bullish=2  trigger=quiet-decay
2026-09-15T11:23:22.093Z  A -> A>S  bearish=2 bullish=1  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-15T11:25:22.099Z  A>S -> S  bearish=3 bullish=1  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-15T11:29:22.105Z  S -> A  bearish=1 bullish=2  trigger=quiet-decay
2026-09-15T11:31:22.107Z  A -> A>S  bearish=2 bullish=1  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-15T11:33:22.107Z  A>S -> S  bearish=3 bullish=1  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-15T11:36:22.111Z  S -> A  bearish=2 bullish=1  trigger=quiet-decay
2026-09-15T11:38:22.112Z  A -> A>S  bearish=4 bullish=0  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-15T11:40:22.114Z  A>S -> S  bearish=4 bullish=0  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-15T11:46:22.116Z  S -> A  bearish=2 bullish=1  trigger=quiet-decay
2026-09-15T11:48:22.116Z  A -> A>S  bearish=3 bullish=0  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-15T11:51:22.113Z  A>S -> A  bearish=2 bullish=1  trigger=quiet-decay
2026-09-15T11:54:22.116Z  A -> A>S  bearish=2 bullish=1  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-15T11:56:22.116Z  A>S -> A  bearish=2 bullish=2  trigger=quiet-decay
2026-09-15T12:01:22.116Z  A -> A>S  bearish=3 bullish=0  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-15T12:03:22.116Z  A>S -> S  bearish=4 bullish=0  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-15T12:08:22.118Z  S -> A  bearish=2 bullish=1  trigger=quiet-decay
2026-09-15T12:10:22.118Z  A -> A>S  bearish=3 bullish=0  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-15T12:12:22.118Z  A>S -> A  bearish=2 bullish=1  trigger=quiet-decay
2026-09-15T12:15:22.120Z  A -> A>S  bearish=3 bullish=0  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-15T12:18:22.117Z  A>S -> S  bearish=4 bullish=0  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-15T12:20:22.120Z  S -> A  bearish=2 bullish=1  trigger=quiet-decay
2026-09-15T12:22:22.119Z  A -> A>S  bearish=3 bullish=0  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-15T12:26:22.129Z  A>S -> A  bearish=2 bullish=1  trigger=quiet-decay
2026-09-15T12:28:22.136Z  A -> A>S  bearish=3 bullish=0  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-15T12:32:22.138Z  A>S -> S  bearish=3 bullish=0  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-15T12:41:22.143Z  S -> A  bearish=2 bullish=1  trigger=quiet-decay
2026-09-15T12:43:22.145Z  A -> A>S  bearish=2 bullish=1  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-15T12:45:22.147Z  A>S -> A  bearish=2 bullish=2  trigger=quiet-decay
2026-09-15T12:47:22.148Z  A -> A>S  bearish=2 bullish=1  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-15T12:50:22.147Z  A>S -> A  bearish=1 bullish=2  trigger=quiet-decay
2026-09-15T12:52:22.151Z  A -> A>L  bearish=1 bullish=3  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-15T12:56:22.147Z  A>L -> A  bearish=1 bullish=2  trigger=quiet-decay
2026-09-15T12:58:22.147Z  A -> A>S  bearish=3 bullish=1  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-15T13:10:22.148Z  A>S -> A  bearish=2 bullish=1  trigger=quiet-decay
2026-09-15T13:16:22.152Z  A -> A>L  bearish=0 bullish=2  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-15T13:18:22.151Z  A>L -> A  bearish=1 bullish=2  trigger=quiet-decay
2026-09-15T13:21:22.149Z  A -> A>L  bearish=0 bullish=2  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-15T13:23:22.153Z  A>L -> A  bearish=1 bullish=2  trigger=quiet-decay
2026-09-15T13:27:22.159Z  A -> A>L  bearish=1 bullish=2  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-15T13:29:22.156Z  A>L -> L  bearish=0 bullish=4  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-15T13:37:22.164Z  L -> L>S  bearish=4 bullish=0  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-15T13:39:22.162Z  L>S -> S  bearish=5 bullish=0  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-15T13:41:22.160Z  S -> A  bearish=2 bullish=2  trigger=quiet-decay
2026-09-15T13:43:22.159Z  A -> A>S  bearish=3 bullish=0  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-15T13:45:22.164Z  A>S -> A  bearish=2 bullish=1  trigger=quiet-decay
2026-09-15T13:47:22.162Z  A -> A>S  bearish=3 bullish=0  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-15T13:49:22.161Z  A>S -> A  bearish=2 bullish=1  trigger=quiet-decay
2026-09-15T13:51:22.169Z  A -> A>S  bearish=2 bullish=1  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-15T13:53:22.172Z  A>S -> A  bearish=2 bullish=2  trigger=quiet-decay
2026-09-15T13:56:22.169Z  A -> A>S  bearish=2 bullish=1  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-15T13:58:22.170Z  A>S -> A  bearish=2 bullish=2  trigger=quiet-decay
2026-09-15T14:02:22.171Z  A -> A>S  bearish=3 bullish=0  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-15T14:04:22.173Z  A>S -> S  bearish=4 bullish=0  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-15T14:10:22.172Z  S -> A  bearish=2 bullish=1  trigger=quiet-decay
2026-09-15T14:12:22.172Z  A -> A>S  bearish=3 bullish=0  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-15T14:14:22.177Z  A>S -> S  bearish=3 bullish=1  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-15T14:17:22.174Z  S -> A  bearish=2 bullish=1  trigger=quiet-decay
2026-09-15T14:20:22.173Z  A -> A>L  bearish=1 bullish=2  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-15T14:22:22.169Z  A>L -> A  bearish=1 bullish=2  trigger=quiet-decay
2026-09-15T14:25:22.181Z  A -> A>L  bearish=1 bullish=2  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-15T14:27:22.178Z  A>L -> A  bearish=2 bullish=0  trigger=quiet-decay
2026-09-15T14:30:22.181Z  A -> A>S  bearish=3 bullish=0  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-15T14:32:22.177Z  A>S -> S  bearish=4 bullish=0  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-15T14:37:22.187Z  S -> A  bearish=2 bullish=2  trigger=quiet-decay
2026-09-15T14:40:22.188Z  A -> A>S  bearish=4 bullish=0  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-15T14:43:22.197Z  A>S -> A  bearish=2 bullish=1  trigger=quiet-decay
2026-09-15T14:47:22.182Z  A -> A>S  bearish=3 bullish=0  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-15T14:51:22.196Z  A>S -> S  bearish=4 bullish=0  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-15T14:54:22.185Z  S -> A  bearish=2 bullish=1  trigger=quiet-decay
2026-09-15T14:57:22.200Z  A -> A>S  bearish=2 bullish=1  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-15T15:01:22.198Z  A>S -> S  bearish=3 bullish=0  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-15T15:03:22.196Z  S -> A  bearish=2 bullish=1  trigger=quiet-decay
2026-09-15T15:06:22.201Z  A -> A>S  bearish=3 bullish=0  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-15T15:09:22.188Z  A>S -> S  bearish=3 bullish=0  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-15T15:24:22.203Z  S -> A  bearish=2 bullish=1  trigger=quiet-decay
2026-09-15T15:26:22.205Z  A -> A>L  bearish=0 bullish=4  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-15T15:28:22.209Z  A>L -> A  bearish=1 bullish=2  trigger=quiet-decay
2026-09-15T15:34:22.218Z  A -> A>L  bearish=1 bullish=2  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-15T15:37:22.214Z  A>L -> A  bearish=1 bullish=1  trigger=quiet-decay
2026-09-15T15:39:22.211Z  A -> A>L  bearish=0 bullish=2  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-15T15:41:22.204Z  A>L -> A  bearish=0 bullish=2  trigger=quiet-decay
2026-09-15T15:43:22.214Z  A -> A>L  bearish=0 bullish=3  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-15T15:47:22.215Z  A>L -> L  bearish=0 bullish=3  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-15T15:55:22.219Z  L -> A  bearish=1 bullish=2  trigger=quiet-decay
2026-09-15T15:57:22.221Z  A -> A>L  bearish=0 bullish=3  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-15T16:00:22.218Z  A>L -> A  bearish=1 bullish=2  trigger=quiet-decay
2026-09-15T16:03:22.213Z  A -> A>L  bearish=0 bullish=3  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-15T16:05:22.218Z  A>L -> A  bearish=1 bullish=2  trigger=quiet-decay
2026-09-15T16:09:22.211Z  A -> A>S  bearish=3 bullish=1  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-15T16:11:22.219Z  A>S -> A  bearish=1 bullish=1  trigger=quiet-decay
2026-09-15T16:14:22.220Z  A -> A>S  bearish=2 bullish=1  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-15T16:17:22.225Z  A>S -> A  bearish=1 bullish=1  trigger=quiet-decay
2026-09-15T16:19:22.221Z  A -> A>S  bearish=2 bullish=0  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-15T16:22:22.219Z  A>S -> A  bearish=1 bullish=2  trigger=quiet-decay
2026-09-15T16:26:22.226Z  A -> A>S  bearish=2 bullish=1  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-15T16:28:22.221Z  A>S -> A  bearish=2 bullish=1  trigger=quiet-decay
2026-09-15T16:31:22.231Z  A -> A>S  bearish=2 bullish=1  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-15T16:33:22.231Z  A>S -> S  bearish=3 bullish=0  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-15T16:37:22.228Z  S -> A  bearish=1 bullish=1  trigger=quiet-decay
2026-09-15T16:40:22.236Z  A -> A>S  bearish=3 bullish=0  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-15T16:42:22.228Z  A>S -> S  bearish=4 bullish=0  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-15T16:44:22.236Z  S -> A  bearish=2 bullish=0  trigger=quiet-decay
2026-09-15T16:56:22.239Z  A -> A>L  bearish=0 bullish=2  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-15T16:58:22.234Z  A>L -> A  bearish=1 bullish=0  trigger=quiet-decay
2026-09-15T17:00:22.235Z  A -> A>S  bearish=2 bullish=0  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-15T17:02:22.239Z  A>S -> A  bearish=2 bullish=0  trigger=quiet-decay
2026-09-15T17:04:22.235Z  A -> A>S  bearish=3 bullish=0  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-15T17:06:22.234Z  A>S -> A  bearish=1 bullish=2  trigger=quiet-decay
2026-09-15T17:08:22.239Z  A -> A>S  bearish=3 bullish=0  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-15T17:11:22.237Z  A>S -> A  bearish=2 bullish=2  trigger=quiet-decay
2026-09-15T17:13:22.236Z  A -> A>S  bearish=3 bullish=0  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-15T17:15:22.240Z  A>S -> A  bearish=2 bullish=1  trigger=quiet-decay
2026-09-15T17:19:22.240Z  A -> A>S  bearish=2 bullish=1  trigger=net_delta_1m,last_3_delta,volume_ratio,cvd_slope,price_vs_vwap
2026-09-15T17:21:22.241Z  A>S -> A  bearish=2 bullish=2  trigger=quiet-decay
