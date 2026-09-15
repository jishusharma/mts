# NEXT SESSION PROMPT — MTS v4.2.0-p5
# Date: 2026-09-06
# Purpose: DSA_TASK_012 complete. Engine integration active. Ready for live trading.
# ---

## CONTEXT

MTS v4.2.0-p5. 129 files. 98/98 math tests pass. DSA_TASK_012 COMPLETE v1.3.2.
setup_candidates now emitted by DSA. math_object_builder reads it directly.
BUG #6 CLOSED. 14 trading cards generated. Architecture stable.

## YOUR TASK

1. JSON upload → math_object_builder reads setup_candidates → verdict card
2. Validate setup_candidates[0] against visual screenshot (VVP-001)
3. Confirm judgment layer uses setup_candidate preferentially
4. Monitor for any discrepancies during 2-week transition

## READ FIRST

1. `system/00_START_HERE.md`
2. `system/01_AI_BEHAVIOR.md`
3. `system/02a_CURRENT_STATUS.md`
4. `data/dsa_task_012_setup_candidates.md` (v1.3.2 spec)
5. `mts/runtime/math_object_builder.py` (v1.3.2 reader)

## CURRENT MARKET CONTEXT

- Last price: ~79,594.0 (2026-09-05 09:58 UTC)
- Last verdict: C+ — WAIT (67/100) — CT Short at PF VAH, proof_count 1, speed only
- DSA_TASK_012: COMPLETE. setup_candidates v1.3.2 live.
- BUG #6: CLOSED 2026-09-06.

---

## ARCHIVED PARALLEL SESSION PROMPTS

The following sections are preserved from stale parallel session prompts. They are retained for reference but are not active session instructions.

ot historical entries) to `06_SESSION_END_CHECKLIST.md` as a new section: `## SESSION SIGN-OFF TEMPLATE`. 3. Update `00_START_HERE.md` SESSION PROTOCOL: change end step from    `Read 06_SESSION_END_CHECKLIST.md` to    `Read 06_SESSION_END_CHECKLIST.md (includes sign-off template)`. 4. `02c_SESSION_END_SIGNOFF.md` becomes HISTORICAL — do not delete (append-only record), but update `03_FILE_INDEX.md` status from ACTIVE to HISTORICAL.  ## ACTION 4: Archive Audit Log  File: `system/02d_AUDIT_LOG.md`  Steps: 1. Move to `mts/archive/02d_AUDIT_LOG_ARCHIVED.md`. 2. Update `03_FILE_INDEX.md`: change status to ARCHIVED, update path. 3. Add entry to `02b_DECISIONS_LOG.md`: `2026-09-04: Archived 02d_AUDIT_LOG.md — stale since 2026-08-07, no references.`.  ## ACTION 5: Delete Duplicate Instructions  File: `system/00_PROJECT_INSTRUCTIONS.md`  Steps: 1. Verify it is identical to `system/00_START_HERE.md` (it should be — previous session confirmed this). 2. Delete `system/00_PROJECT_INSTRUCTIONS.md`. 3. Update `03_FILE_INDEX.md`: remove entry.  ## ACTION 6: Validation Test  Test: Generate a trading card from a fresh BTCUSDT JSON snapshot.  Steps: 1. Ask user for fresh JSON or screenshot. 2. Generate card using ONLY:    - `mts/runtime/compiled_engine.md`    - `mts/runtime/math_object_builder.py`    - `mts/cards/trading_card_generator.md` 3. Compare output with what the 17-file system would produce (use a recent card as reference). 4. If match → PASS. Log in `02b_DECISIONS_LOG.md`. 5. If mismatch → STOP. Do not proceed. Flag the discrepancy.  ## CONSTRAINTS  - Maximum 20 tool calls total (6 actions + validation). - If any action fails, STOP and report. Do not proceed to next action. - Do NOT create any new files except the archived audit log. - Do NOT modify `compiled_engine.md`, `math_object_builder.py`, or any condition file.  ## FILES YOU WILL TOUCH  | # | File | Action | |---|------|--------| | 1 | `system/00_START_HERE.md` | Add mistake #17, update end protocol | | 2 | `system/04_NEXT_SESSION_PROMPT.md` | Merge 3 variants into sections | | 3 | `system/04_NEXT_SESSION_PROMPT_BUGS.md` | DELETE | | 4 | `system/04_NEXT_SESSION_PROMPT_DSA008.md` | DELETE | | 5 | `system/04_NEXT_SESSION_PROMPT_DRIFT_FIX.md` | DELETE | | 6 | `system/06_SESSION_END_CHECKLIST.md` | Append signoff template | | 7 | `system/02c_SESSION_END_SIGNOFF.md` | Update index status to HISTORICAL | | 8 | `system/02d_AUDIT_LOG.md` | MOVE to archive | | 9 | `system/00_PROJECT_INSTRUCTIONS.md` | DELETE | | 10 | `system/03_FILE_INDEX.md` | Sync all changes | | 11 | `system/02b_DECISIONS_LOG.md` | Log decisions |  ## WHAT THE PREVIOUS SESSION CONCLUDED (For Reference Only)  Previous session's 6-action plan (this session executes it):  | # | Action | Why | |---|--------|-----| | 1 | Gate rule | Prevents future file sprawl | | 2 | Merge prompts | 4 variants, same purpose | | 3 | Merge signoff | Signoff is a filled checklist | | 4 | Archive audit | Stale since 2026-08-07 | | 5 | Delete duplicate | Identical to 00_START_HERE.md | | 6 | Card test | One test proves nothing broke |  Previous session's fresh-eyes Q1-Q4:  - Q1: MTS reads a BTCUSDT snapshot and outputs a trade setup card.  - Q2: No gate asks 'Does this already exist?' before creating files.  - Q3: Add gate rule + consolidate 4 redundant files. Do not touch working files.  - Q4: Generate card from fresh snapshot. Match = pass.  ---  # END

---

## ARCHIVED PARALLEL SESSION PROMPTS

The following sections are preserved from stale parallel session prompts. They are retained for reference but are not active session instructions.

---

## IF BUG HUNT MODE

_Content from `04_NEXT_SESSION_PROMPT_BUGS.md` (2026-08-31, v4.2.0-p3+2)_

## SESSION START — VALIDATION PHASE (MUST DO FIRST)

Before touching any bug, confirm the system baseline is stable:

1. **Read** `system/00_START_HERE.md` → `system/01_AI_BEHAVIOR.md` → `system/02a_CURRENT_STATUS.md`
2. **Verify math layer:** Run `mts/tests/test_mts_math.py` and `mts/tests/test_math_object_builder.py`
   - Expected: 98/98 PASS. If any FAIL → STOP. Report to main session immediately.
3. **Verify compiled_engine.md loads:** Read `mts/runtime/compiled_engine.md` lines 1-10. Confirm version says `v4.2.0-p3`.
4. **Confirm bug status:** Read `system/02a_CURRENT_STATUS.md` Section "BUGS". Verify BUG #4 and BUG #5 are still OPEN.
   - If either is marked CLOSED → STOP. Bug may already be fixed.
5. **Load test snapshot:** Read `data/test_snapshot_v4.2.0-p2_validation.json` to understand the data format.

**If all checks PASS → proceed to investigation.**
**If any check FAIL → STOP and report to main session.**

---

## BUG #4: CVD vs trade_flow Contradiction

### Problem Statement
CVD (cumulative) slope is "falling" but `trade_flow.net_delta` is positive.
- CVD is cumulative: falling = net selling pressure over the session.
- trade_flow.net_delta is recent: positive = net buying in recent candles.
- These CAN both be true (recent buyers vs session sellers), but the engine may misread this as "divergence" or "contradiction" when it's actually normal market behavior.

### Investigation Steps
1. Read `data/data_schema_v1.0.md` Section "DATA BLOCK — cvd" and "DATA BLOCK — trade_flow"
2. Read `data/sample_btc_snapshot.json` — find actual values for `cvd.slope`, `cvd.cvd_recent`, and `trade_flow.net_delta`
3. Read `mts/runtime/compiled_engine.md` — search for how CVD and trade_flow are used in state classification and proof evaluation
4. Trace: If `cvd.slope = "falling"` AND `trade_flow.net_delta > 0`:
   - What does the engine currently output?
   - Is this treated as "divergent" (unhealthy trend signal)?
   - Should it be treated as "recent shift" (transition signal)?
5. Check `mts/conditions/proof_requirements_formatted.md` for CVD/trade_flow proof rules

### Expected Fix Direction
- The engine should distinguish between:
  - **CVD slope (cumulative):** Session-level context. Falling = sellers controlled the session.
  - **trade_flow.net_delta (recent):** Current control. Positive = buyers currently aggressive.
  - **cvd_recent (1h/4h breakdown):** Bridge between cumulative and recent.
- A falling CVD + positive recent delta is NOT necessarily a contradiction. It's "session sellers exhausted, recent buyers stepping in."
- The engine may be over-weighting CVD slope in proof evaluation. Consider:
  - Demote CVD slope to "context" rather than "proof" when trade_flow disagrees
  - Or add a "recent shift" signal that prioritizes trade_flow + cvd_recent over cumulative CVD

### Output
- Document findings in `system/02b_DECISIONS_LOG.md` (append to TOP)
- If fix is simple (1-2 lines in compiled_engine.md), implement and validate with test snapshot
- If fix is complex, write `mts/research/bug_004_investigation.md` with full analysis and recommendations
- Update `system/02a_CURRENT_STATUS.md` bug status

---

## BUG #5: order_book_depth Identical Values

### Problem Statement
`order_book_depth_expanded` returns identical bid/ask depth values at all thresholds (0.1%, 0.2%, 0.5%, 1.0%). This makes the metric useless for detecting liquidity clustering.

### Investigation Steps
1. Read `data/data_schema_v1.0.md` Section "DATA BLOCK — order_book_depth"
2. Read `data/sample_btc_snapshot.json` — find `order_book_depth` values
3. Read `system/02a_CURRENT_STATUS.md` for BUG #5 details
4. Analyze: Is this a DSA computation bug or an exchange API limitation?
   - Binance `/fapi/v1/depth limit=100` at $78K covers only ~$93 range (0.12%)
   - If the API only returns 100 levels, thresholds smaller than 0.12% will all return the same data
   - Solution may require: smaller limit (e.g., limit=5000), OR different endpoint, OR client-side computation
5. Check if `bid_depth_1pct` and `ask_depth_1pct` are also identical in live snapshots

### Expected Fix Direction
- Option A: DSA changes API limit from 100 to 5000 (if Binance supports it)
- Option B: Engine changes — use `bid_ask_ratio` only (which is already computed from 1% depth) and drop expanded thresholds
- Option C: Document limitation — "order_book_depth_expanded requires API limit >= 1000. Current limit=100 covers ~0.12% at $78K. Values below this threshold are identical."

### Output
- Document findings in `system/02b_DECISIONS_LOG.md` (append to TOP)
- If DSA change needed, write `data/dsa_task_011_order_book_depth.md` with exact API spec
- If engine change needed, patch `compiled_engine.md` and validate
- Update `system/02a_CURRENT_STATUS.md` bug status

---

## SESSION END CHECKLIST

Before closing this session:
- [ ] Both bugs investigated with full trace
- [ ] Findings documented in 02b_DECISIONS_LOG.md
- [ ] If fixes applied: validated against test snapshot
- [ ] 02a_CURRENT_STATUS.md updated with bug status changes
- [ ] Any new files added to 03_FILE_INDEX.md
- [ ] Report back to main session: what was found, what was fixed, what remains

---
# END

---

## IF DSA TASK MODE

_Content from `04_NEXT_SESSION_PROMPT_DSA008.md` (2026-08-31, v4.2.0-p3+3)_

## SESSION START — VALIDATION PHASE (MUST DO FIRST)

Before designing any fields, confirm the GAP entries are still valid and blocked:

1. **Read** `system/00_START_HERE.md` → `system/01_AI_BEHAVIOR.md` → `system/02a_CURRENT_STATUS.md`
2. **Verify cross-trader status:** Read `mts/research/cross_trader_integration_plan.md` Section 3.6 (GAP ENTRIES)
   - Confirm 5 entries are listed: C01-E04, C02-E02, C06-E01, C07-E07, C10-E04
   - Confirm each has a "Missing DSA Field" entry
   - If any entry is marked INTEGRATED or CANCELLED → STOP. Status may have changed.
3. **Verify DSA_TASK_008 does not exist:** Check `data/` folder for `dsa_task_008_*.md`
   - If it exists → STOP. Read it instead of recreating.
4. **Verify data_schema_v1.0.md version:** Should be v1.2.0 or higher
   - If lower → STOP. Schema may need update first.

**If all checks PASS → proceed to field design.**
**If any check FAIL → STOP and report to main session.**

---

## GAP ENTRY 1: C01-E04 — Composite Profiles

### Source
The Flow Horse, Oy2Z-FQ77NM — "Most Traders Misread Volume Profile"

### Concept
Multiple days' volume profiles overlaid to find confluence zones. If 3 days' VAHs cluster at the same level, that level is stronger than a single day's VAH.

### Missing DSA Field
- `composite_profile.shape` — enum: "single", "overlapping", "stacked", "nested"
- `composite_profile.vah_cluster` — array of floats: clustered VAHs across N days
- `composite_profile.val_cluster` — array of floats: clustered VALs across N days
- `composite_profile.poc_cluster` — array of floats: clustered POCs across N days
- `composite_profile.overlap_count` — integer: how many days' profiles overlap at current price

### Design Questions
1. How many days of history needed? (Tom uses weekly for macro, daily for context — suggest 3-5 days)
2. What defines "cluster"? (suggest: levels within 0.2% of each other)
3. Can DSA compute this from existing daily VP data, or does it need new API?

### Output Spec
Write field specification with: name, type, description, computation logic, example, priority (P0/P1/P2)

---

## GAP ENTRY 2: C02-E02 — Extended Balance + High-Volume Break = Measured Move

### Source
CryptoCred, BHwoN7VPrBE — "Market Structure"

### Concept
If price balances for N days in a tight range, then breaks with high volume, the measured move target = range height projected from break point.

### Missing DSA Field
- `balance.duration_days` — integer: consecutive days with B-shaped VP
- `balance.range_size` — float: VAH - VAL (in price or %)
- `balance.range_size_pct` — float: range_size / current_price * 100
- `break_volume_ratio` — float: break candle volume / average volume of balance period
- `measured_move.target_up` — float: break_price + range_size
- `measured_move.target_down` — float: break_price - range_size

### Design Questions
1. What defines "extended"? (suggest: >= 3 days of B-shaped VP)
2. What defines "tight" range? (suggest: range_size_pct < 1.5%)
3. Is this a Tom-validated concept? (Check Tom transcripts — Tom uses "balance" but may not use "measured move")

### Output Spec
Write field specification. Flag if concept is NOT Tom-validated.

---

## GAP ENTRY 3: C06-E01 — Test Count Degradation

### Source
CryptoCred, inqHN8q57X4 — "Retests"

### Concept
Each time price revisits a zone, the zone weakens. First test = best test. Third+ test = zone likely to break.

### Missing DSA Field
- `zone.test_count` — integer: how many times price has tested this zone in last N candles
- `zone.visit_history` — array of objects: {timestamp, price_at_visit, outcome: "bounce"|"break"|"unresolved"}
- `zone.degradation_score` — float: 1.0 (first test) → 0.0 (broken). Formula: max(0, 1 - (test_count - 1) * 0.3)

### Design Questions
1. What timeframe for "test"? (suggest: 1h closes touching zone = 1 test)
2. What defines "touching"? (suggest: wick or body within 0.1% of zone)
3. Is this computable from existing swing high/low + VP data, or needs new tracking?

### Output Spec
Write field specification.

---

## GAP ENTRY 4: C07-E07 — Precedent: Historical Retest Behavior

### Source
CryptoCred, inqHN8q57X4 — "Retests"

### Concept
If an instrument historically respects retests (e.g., 80% of breaks retest within 24h), then missing a retest entry is higher opportunity cost.

### Missing DSA Field
- `instrument.retest_rate_30d` — float: % of breaks that retest within 24h (last 30 days)
- `instrument.retest_rate_90d` — float: same, 90 days
- `instrument.trend_retest_behavior` — enum: "respects" | "violates" | "mixed"
- `instrument.avg_retest_time_hours` — float: average hours between break and retest

### Design Questions
1. This is HIGHLY computationally expensive. Needs full trade history.
2. Is this a Tom concept? (Tom does NOT discuss historical retest rates — this is pure CryptoCred)
3. Should this be REJECTED instead of implemented? (Check Rule 34: cross-market concept research)

### Output Spec
Write field specification. STRONGLY consider recommending REJECT with justification.

---

## GAP ENTRY 5: C10-E04 — Fibonacci Pullback (0.618-0.786)

### Source
CryptoCred, Yp0k8HD5xro — "First Trouble Area"

### Concept
In a trending market, pullbacks often find support at 61.8% or 78.6% Fibonacci retracement of the last swing.

### Missing DSA Field
- `fibonacci.retracement_618` — float: 61.8% retracement of last swing
- `fibonacci.retracement_786` — float: 78.6% retracement of last swing
- `fibonacci.swing_high` — float: high of swing used for calculation
- `fibonacci.swing_low` — float: low of swing used for calculation
- `fibonacci.current_retracement` — float: where current price sits in the retracement (0.0 = at high, 1.0 = at low)

### Design Questions
1. Which swing to use? (suggest: last confirmed swing high/low on 1h or 4h)
2. Tom NEVER mentions Fibonacci in any extracted video. Is this a Tom concept?
3. Source note: CryptoCred explicitly says "personal preference, no fixed answer" for Fib levels.

### Output Spec
Write field specification. STRONGLY consider recommending REJECT or [PRINCIPLE — NOT ALGORITHM] with justification.

---

## CONSOLIDATED OUTPUT

### Step 1: Write DSA_TASK_008.md
Create `data/dsa_task_008_gap_fields.md` with:
- Executive summary: 5 GAP entries, which fields needed, priority ranking
- Per-entry field specification (use tables)
- Recommendation for each: IMPLEMENT / REJECT / DEFER
- Estimated implementation effort per field
- Dependencies on existing DSA infrastructure

### Step 2: Update data_schema_v1.0.md
If any fields are recommended for IMPLEMENTATION:
- Append new DATA BLOCK sections to `data/data_schema_v1.0.md`
- Follow existing format (field, type, description, example, visual validation needed)
- Increment schema version to v1.3.0

### Step 3: Update cross_trader_integration_plan.md
- Update Section 3.6: mark entries as UNBLOCKED (with field names) or PERMANENTLY BLOCKED (with reason)
- Update Phase 4 status table

### Step 4: Update status files
- Append entry to `system/02b_DECISIONS_LOG.md`
- Update `system/02a_CURRENT_STATUS.md` Task 7 with DSA_TASK_008 status
- Update `system/03_FILE_INDEX.md` with new files

---

## SESSION END CHECKLIST

Before closing this session:
- [ ] All 5 GAP entries analyzed with full field specifications
- [ ] DSA_TASK_008.md written and verified
- [ ] data_schema_v1.0.md updated (if any fields approved)
- [ ] cross_trader_integration_plan.md updated
- [ ] 02a_CURRENT_STATUS.md updated
- [ ] 02b_DECISIONS_LOG.md updated
- [ ] 03_FILE_INDEX.md updated with new files
- [ ] Report back to main session: which fields approved, which rejected, why

---
# END

---

## IF DRIFT FIX MODE

_Content from `04_NEXT_SESSION_PROMPT_DRIFT_FIX.md` (2026-09-02, v4.2.0-p5+1)_

## SESSION START — VALIDATION PHASE (MUST DO FIRST)1. **Read** `system/00_START_HERE.md` → `system/01_AI_BEHAVIOR.md` → `system/02a_CURRENT_STATUS.md`2. **Verify math layer:** Run `mts/tests/test_mts_math.py` and `mts/tests/test_math_object_builder.py`   - Expected: 98/98 PASS. If any FAIL → STOP. Report to main session immediately.3. **Confirm drift list:** Read this file. Verify all 9 discrepancies (D1–D9) still exist.   - If any are already fixed → SKIP that item. Do not re-fix.
---
# END
