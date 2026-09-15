# BUG #4 INVESTIGATION — CVD vs trade_flow Contradiction
# Date: 2026-08-31
# Status: INVESTIGATED — Fix direction identified, engine patch ready
# Investigator: Parallel Session (Bug Hunt)

---

## 1. PROBLEM STATEMENT

CVD (cumulative) slope is "falling" but `trade_flow.net_delta` is positive.
- CVD is cumulative: falling = net selling pressure over the session.
- trade_flow.net_delta is recent: positive = net buying in recent candles.
- These CAN both be true (recent buyers vs session sellers), but the engine may misread this as "divergence" or "contradiction" when it is actually normal market behavior.

## 2. DATA ANALYSIS

### 2.1 Schema Design (Already Anticipated)
`data_schema_v1.0.md` explicitly states:
> "Resolves CVD/trade_flow contradictions. Recent flow reflects current market control; cumulative reflects session context."

The `cvd_recent` block was added specifically for this purpose (DSA_TASK_003):
- `slope_1h`: 1h CVD slope
- `slope_4h`: 4h CVD slope
- `delta_1h`: 1h CVD delta
- `delta_4h`: 4h CVD delta

### 2.2 Sample Snapshot Evidence
`sample_btc_snapshot.json` (2026-08-22):
- `cvd.slope`: "falling"
- `cvd.last_3_delta`: ["negative", "positive", "negative"]
- `trade_flow.net_delta`: -1.954 (negative — aligned with CVD in this snapshot)

`test_snapshot_v4.2.0-p2_validation.json` (2026-08-29):
- `cvd.slope`: "rising"
- `cvd.last_3_delta`: ["positive", "positive", "negative"]
- `trade_flow.net_delta`: 0.734 (positive — aligned with CVD in this snapshot)

**Neither snapshot shows the actual contradiction.** The bug is a LOGIC bug: the engine's proof evaluation does not distinguish between cumulative CVD and recent trade_flow when they DO disagree.

### 2.3 Engine Logic Trace

**compiled_engine.md Section 4 (Proof Types) — Current:**

| Type | Source In JSON |
|------|---------------|
| Sellers present | `cvd.slope`, `last_3_delta` |
| Buyers present | `cvd.slope`, `last_3_delta` |

**Problem:** The proof table references ONLY `cvd.slope` and `cvd.last_3_delta` for directional flow proof. It does NOT reference `trade_flow.net_delta`.

**compiled_engine.md Section 4 [PRINCIPLE] — Current:**
> "When cvd_slope and trade_flow.net_delta disagree in direction... this is a caution flag — requires contextual judgment, not an algorithmic resolution."

**Problem:** This is marked [PRINCIPLE — NOT ALGORITHM], meaning it provides guidance but does not change verdicts. When `conditions.cvd_trade_flow_aligned = false`, the engine has no rule for how to resolve it.

### 2.4 JSON Workflow Trace (01_AI_BEHAVIOR.md Section 14.2 Step 5)
The proof gate checks:
- CVD direction from `cvd.slope`, `cvd.divergence`
- Book pressure from `order_book_depth.bid_ask_ratio`
- It does NOT check `trade_flow.net_delta` or `cvd_recent`

## 3. ROOT CAUSE

1. **Proof table under-references trade_flow.** `trade_flow.net_delta` is not listed as a proof source.
2. **cvd_recent is unused in proof evaluation.** The `cvd_recent` block (1h/4h breakdown) exists in schema but is not referenced in the proof gate.
3. **cvd_trade_flow_aligned is a blunt boolean.** When `false`, the engine treats it as a generic "caution" with no resolution path.
4. **Cumulative CVD is over-weighted.** Session-level CVD slope is treated as primary proof, but recent flow (trade_flow) may be more relevant for imminent entry decisions.

## 4. FIX DIRECTION

### 4.1 Update Proof Table
Add `trade_flow.net_delta` and `cvd_recent.slope_1h` as sources for Sellers/Buyers present proof.

### 4.2 Add "Recent Shift" Resolution Rule
When `cvd.slope` and `trade_flow.net_delta` disagree:
1. Check `cvd_recent.slope_1h`
2. If `cvd_recent.slope_1h` aligns with `trade_flow.net_delta` → signal = "recent_shift" (transition signal, NOT contradiction)
3. If `cvd_recent.slope_1h` aligns with `cvd.slope` → signal = "cumulative_dominant" (session sellers still in control)
4. If `cvd_recent` is "flat" → signal = "pause" (no directional edge from flow)

### 4.3 Demote Cumulative CVD in Proof Weight
When trade_flow disagrees with cumulative CVD:
- Cumulative CVD slope becomes "context" (background session pressure)
- trade_flow + cvd_recent becomes "proof" (current market control)

### 4.4 Engine Patch (compiled_engine.md)
- Update Proof Types table: add trade_flow.net_delta and cvd_recent sources
- Update CVD/Trade Flow Context principle: add recent_shift resolution
- Add note: "Recent shift = session sellers exhausted, recent buyers stepping in. NOT a contradiction."

## 5. VALIDATION PLAN

1. Create synthetic test snapshot with:
   - `cvd.slope = "falling"`
   - `trade_flow.net_delta = 0.8` (positive)
   - `cvd_recent.slope_1h = "rising"`
   - `cvd_recent.slope_4h = "falling"`

2. Run through math_object_builder + judgment layer
3. Expected: Engine recognizes "recent_shift" signal, does NOT flag as contradiction
4. Expected: Proof evaluation uses trade_flow + cvd_recent, not just cumulative CVD

## 6. IMPACT ASSESSMENT

| Scenario | Before Fix | After Fix |
|----------|-----------|-----------|
| Falling CVD + positive trade_flow + rising cvd_recent | Treated as "caution/divergence" | Treated as "recent shift — buyers taking control" |
| Falling CVD + positive trade_flow + falling cvd_recent | Treated as "caution/divergence" | Treated as "cumulative dominant — sellers still in control" |
| Rising CVD + negative trade_flow + falling cvd_recent | Treated as "caution/divergence" | Treated as "recent shift — sellers taking control" |

## 7. FILES TO MODIFY

| File | Action |
|------|--------|
| `mts/runtime/compiled_engine.md` | Patch Section 4 proof table + CVD/Flow context principle |
| `system/02a_CURRENT_STATUS.md` | Update BUG #4 status to CLOSED |
| `system/02b_DECISIONS_LOG.md` | Append findings |

## 8. BUG #5 CORRECTION (2026-09-03)

During the same deep re-evaluation, BUG #5 (order_book_depth expanded identical values) was found to be **NOT a real engine bug**.

**Why:** The engine only ever referenced `bid_ask_ratio` for order book proof. Expanded thresholds (0.1%, 0.2%, 0.5%) were never in the schema field list (only `bid_depth_1pct`, `ask_depth_1pct`, `bid_ask_ratio` exist) and were never referenced in compiled_engine.md proof evaluation.

**The prior "fix" was documentation theater:** Adding a "limitation" note to compiled_engine.md falsely implied the engine was constrained by DSA limit=100. The engine was correctly designed — it never needed expanded thresholds.

**Correct action taken:**
1. Removed false "Order Book Depth Limitation" [PRINCIPLE] block from compiled_engine.md
2. Replaced schema note with clean statement: engine uses bid_ask_ratio only
3. Reclassified BUG #5 from CLOSED to RECLASSIFIED in 00_START_HERE.md
4. Added process rule to COMMON MISTAKES: trace data field → engine reference → verdict impact before filing any bug

**Process lesson:** Both bugs #4 and #5 trace to the same failure: schema-first development without engine trace. #4 was real because the data WAS needed but engine wasn't using it. #5 was not real because the data was NEVER needed. The mandatory trace before bug filing is now documented.

---
# END
