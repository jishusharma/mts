# T3 STOP RULE RULING — 2026-10-01

## Overview
Task T3 (from DSA_TASKS_2026-10-01.md:18-22): Rule which single stop definition matches Tom's "below last low / above last high." Three implementations currently disagree. PROVENANCE_AUDIT A03/A04 mark the 0.2% fallback NO-SOURCE. Reads: math_object_builder.py:226-250, SetupCandidatesBuilder.java:100-125, ExtraSetupBuilder.java:36-40, PROVENANCE_AUDIT_TOM.md A03/A04, transcript 3o1VVsfBmmU raw text.

---

## FINDING 1: Tom's Stop Rule (Longs)

**Tom's exact words:**
> "my stop loss belongs below the last liquidity."

**Source:** 
- 3o1VVsfBmmU raw transcript (video ID used in TASK 1 extract)
- Verbatim index: TOM-072 | risk_protocol.md | "my stop loss belongs below the last liquidity."

**Interpretation:** For a long entry, the stop sits below the last liquidity level the market tested. "Last liquidity" refers to the swing low (the most recent significant low the market found, below which liquidity is sparse).

**For shorts (mirrored):** Tom does NOT explicitly state the mirrored rule. Code assumes "stop above last high," but this is UNQUOTED.

**Source:** PROVENANCE_AUDIT_TOM.md row A05: "Q09: a short stop 'doesn't belong above the high'" — but this is a negative statement (what it DOESN'T do), not a definition of what it DOES.

---

## FINDING 2: Three Implementations Disagree

### Implementation 1: Python (math_object_builder.py:248-255)

**Logic:**
```
Long (is_above = False):
  if swing_low is not None and swing_low < zone_price:
    stop = swing_low
  else:
    stop = None (no fallback; candidate not viable)

Short (is_above = True):
  if swing_high is not None and swing_high > zone_price:
    stop = swing_high
  else:
    stop = None
```

**Match to Tom:** ✓ YES. Matches "below last low" (long) via swing_low. No fallback. Returns None if no swing exists (candidate is rejected).

**Verdict:** PYTHON IS CORRECT. Uses swing-based stop, no unsourced fallback.

---

### Implementation 2: Java SetupCandidatesBuilder.java (SCB:100-125)

**Logic:**
```
Short:
  if (swingHigh > zonePrice) 
    c.stop = swingHigh;
  else 
    c.stop = zonePrice * 1.002;  // [A03: 0.2% fallback — NO-SOURCE]

Long:
  if (swingLow < zonePrice) 
    c.stop = swingLow;
  else 
    c.stop = zonePrice * 0.998;  // [A04: 0.2% fallback — NO-SOURCE]

// v1.3.3 minimum stop-distance floor:
if (Math.abs(zonePrice - c.stop) < minStopDist) 
  c.stop = "short".equals(c.direction) ? zonePrice * 1.002 : zonePrice * 0.998;  // [A03: floor 0.1% → reset to 0.2%]
```

**Match to Tom:** ✗ PARTIAL. Swing-based logic matches. The 0.2% fallback contradicts Tom: PROVENANCE_AUDIT A03/A04 mark it NO-SOURCE. The floor (0.1% -> 0.2%) overwrites Tom-size stops. (Tom's stops ~0.04% on ES per Q10, Q11.)

**Provenance audit impact:** 
- A03: "Stops closer than 0.1% trigger fallback to 0.2%. NO-SOURCE. Overwrites Tom-size stops."
- A04: "Fallback stop when no swing exists = 0.2%. NO-SOURCE."
- PROVENANCE_AUDIT summary rank 3: "A03 0.1% stop floor reset to 0.2%. Removes Tom-size stops (12 ticks is about 0.04%)."

**Verdict:** JAVA SCB HAS BUGS. (1) The 0.2% fallback when no swing exists is unsourced (NO-SOURCE A04). (2) The floor (0.1%) is unsourced (NO-SOURCE A03) and overwrites legitimate tight stops from Tom. The fallback should be removed (candidate rejected, like Python) or decision escalated to operator for Tom-quoted rule.

---

### Implementation 3: Java ExtraSetupBuilder.java (36-40, Momentum/Scalp)

**Logic:**
```
Short:
  stop = previousHigh(klines1m);  // Last 1m bar high

Long:
  stop = previousLow(klines1m);   // Last 1m bar low
```

**Match to Tom:** ✗ NO. Uses 1-minute bar extremes, not swing-based structure. This is a crypto/scalp proxy (tight stops for fast exits), not Tom's rule. Tom's rule is swing-based ("last liquidity" = structure).

**Provenance:** No Tom quote cited. ExtraSetupBuilder is for momentum_long/short setups (likely later addition for scalp layer). Not in original Tom core.

**Verdict:** JAVA EXTRASETUPBUILDER MISMATCHES. Not swing-based. Is it intentional for momentum trades, or a layering error? If intentional, it needs explicit sourcing (a Tom quote justifying 1m bar stops for momentum). If unintentional, delete it.

---

## FINDING 3: Discrepancies Identified

| Aspect | Python | Java SCB | Java ESB |
|--------|--------|----------|---------|
| Stop rule | swing_low/high | swing_low/high | previousLow/High (1m) |
| Tom match | ✓ YES | ⚠ PARTIAL (wrong fallback) | ✗ NO |
| Fallback when no swing | None (reject) | 0.2% (unsourced) | N/A (1m bars always exist) |
| NO-SOURCE flags | 0 | 2 (A03, A04) | 1 (no Tom source cited) |

**Short stop contradiction:** PROVENANCE_AUDIT A05 notes "Every short stop is above a high (MP 2.2 'CONTRADICTS Tom')." This suggests Tom does NOT state the mirrored short rule, so code assuming "above high" is unquoted.

---

## RULING: Which Single Stop Rule to Keep

**Single truth:** Swing-based stop, Tom's words: "stop below the last liquidity" (long) and mirrored (short above last high, unquoted but structurally sound).

**Implementation to keep:** **Python (math_object_builder.py:248-255)** is the canonical stop rule. It matches Tom's logic, rejects candidates if no swing exists (correct fail-closed behavior), and has zero unsourced constants.

**Implementations to delete:**
1. **Java SetupCandidatesBuilder.java (SCB:100-125) — KEEP the swing logic, but DELETE the 0.2% fallback (lines 119-124, A03/A04).** The fallback is NO-SOURCE and overwrites Tom-size stops. Option: (a) delete the fallback and reject candidates without swings (Python behavior), or (b) escalate to operator to provide a Tom-quoted fallback rule.

2. **Java ExtraSetupBuilder.java (36-40) — DELETE entirely or rewrite.** The 1m bar stop does not match Tom's swing-based rule. If this is intentional for momentum_long/short setups, add a comment citing the decision and the setup type (layer, not Tom core). If unintentional, delete these two lines and use swing-based stop like the others.

---

## IMPLEMENTATION PLAN

### Phase 1: Remove NO-SOURCE Fallback (SCB)
- Delete SCB lines 119-124 (0.2% fallback when no swing exists) and lines 125-128 (floor reset to 0.2%).
- Change to: `if (...) { c.stop = swing; } else { return None; }` (Python behavior).
- Consequence: Fewer candidates survive (no fallback); R:R drops on tight-zone entries.

### Phase 2: Reconcile ExtraSetupBuilder
- Option A: Delete lines 36-40 (remove 1m bar stop). ExtraSetupBuilder will inherit parent swing-based stop.
- Option B: Rewrite lines 36-40 to call swing-based stop logic (same as SCB). Add comment: "Momentum setup uses swing-based stop for consistency."
- Option C: Keep 1m bar stop but add comment: "ExtraSetupBuilder momentum layer uses 1m bar extremes per [OPERATOR DECISION, 2026-XX-XX], not Tom swing-based rule."

### Phase 3: Code Path Test
After consolidation:
- Math_object_builder.py remains canonical (no change).
- SetupCandidatesBuilder.java uses swing (fallback removed).
- ExtraSetupBuilder.java uses swing OR is deleted.
- All three return None / reject candidate if no swing exists.
- Test: run on 3-5 snapshots where swing_low/high are stale; verify candidates rejected (not fallback).

---

## SUMMARY: T3 STOP RULING — 2026-10-01

1. **Tom's rule:** Stop below last liquidity (long); by structure, above last high (short, unquoted).

2. **Single canonical stop:** Swing-based (swing_low for long, swing_high for short). Python (math_object_builder.py) is correct implementation.

3. **Two implementations disagree:**
   - Java SCB: Has unsourced 0.2% fallback + floor (NO-SOURCE A03/A04). **Action: Remove fallback and floor; reject candidates without swings.**
   - Java ExtraSetupBuilder: Uses 1m bar stops (not swing). **Action: Delete OR rewrite to swing-based + document decision.**

4. **Outcome:** All three paths converge on swing-based stop. No fallback, no floor. Candidates rejected if no swing exists (Python behavior).

---

**File:line citations**

- math_object_builder.py:248-255 (swing-based stop, no fallback) — CANONICAL
- SetupCandidatesBuilder.java:100-125 (swing + fallback + floor; fallback NO-SOURCE A03/A04)
- ExtraSetupBuilder.java:36-40 (1m bar stop; not swing-based, no Tom source)
- PROVENANCE_AUDIT_TOM.md rows A03, A04 (0.2% fallback/floor NO-SOURCE), A05 (swing rule), A06 (swing TF selection)
- TOM_VERBATIM_INDEX.md TOM-072 (stop below last liquidity)
- 3o1VVsfBmmU raw_transcripts_canonical (stop quote in video)
- risk_protocol.md (rule documentation, cites TOM-072)

**Verdict codes**

- Python swing logic: TOM-SOURCED (Q07, Q08 structure; no percent, but logic matches)
- Java SCB fallback: NO-SOURCE (A03, A04)
- Java ESB 1m bar: NO-SOURCE (no Tom quote cited; momentum layer unvetted)
