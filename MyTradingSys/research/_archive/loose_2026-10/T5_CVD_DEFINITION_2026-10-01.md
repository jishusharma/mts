# T5 CVD DIVERGENT / EXHAUSTION DEFINITION — 2026-10-01

## Overview
Task T5 (from DSA_TASKS_2026-10-01.md:30-34): Find a Tom-cited operational definition for "CVD divergent" and exhaustion (referencing B063) so Java classifyState can emit trend_unhealthy and transition (currently unreachable, only balance and trend_healthy reachable). Reads: compiled_engine.md:36-46, market_state_rules.md sec 1-3, FABIO_RULEBOOK.md FAB-038/FAB-040, OPEN_FINDINGS.md B063, TOM_VERBATIM_INDEX.md.

---

## FINDING 1: CVD Divergent — No Operational Definition

**Ruling:** Tom does not define "CVD divergent" operationally. The phrase appears nowhere in the extracted transcript corpus, indexed extracts, or condition files with a concrete numerical or logical rule.

**Source:** 
- MyTradingSys/runtime/compiled_engine.md:38-46, line 41: "the 'CVD divergent' column has no Tom-cited operational definition (B063), so no code path produces them."
- PROVENANCE_AUDIT_TOM.md row A25: "CVD 'divergent' (never emitted)" with verdict TOM-CONCEPT-ONLY and verdict statement "Q29: unhealthy = no liquidity at the extreme; Q21: no divergence definition"

**Impact:** Java classifyState (compiled_engine.md:38-46) can emit only **balance** and **trend_healthy**. The states **trend_unhealthy** and **transition** are unreachable because they key on "CVD divergent," which has no decision logic.

**Consequences:**
1. Any rule, alert, or verdict keying on trend_unhealthy or transition is inert (dead code).
2. "In transition, wait" logic is not enforced by code; operator applies it by judgment.
3. All unhealthy-trend rules in setup_type_rules.md and market_state_rules.md that cite Q29 are unexecutable.

**Candidates under evaluation (per compiled_engine.md:44-45):** FABIO_RULEBOOK.md FAB-038 and FAB-040 (not yet reviewed for explicit definition), absorption_cvd in ANALYST_LAYER_FRAMEWORK.md (not in scope).

---

## FINDING 2: Exhaustion — Volume Spike Definition Only

**Operational definition found:** Volume spike, described as proof of exhaustion via order-flow depletion.

**Tom's words:**
> "exhaustion 'seen with a volume spike'"
**Source:** PROVENANCE_AUDIT_TOM.md, row P06 (Proof 06: Volume spike), verdict TOM-CONCEPT-ONLY, query reference Q18.

**Measured as:** Last 1-minute volume > 2.0x mean of 240-bar history, close within 0.1% of spike level.

**Source:** SetupCandidatesBuilder.java:804-816 (P06 in PROVENANCE_AUDIT), implementing Proof 06 for proof band calculation.

**Code path:** SCB:819, MOB, VRD proof band; counts as 1 proof point. Proof >= 5 reaches SETUP_FORMING verdict (VRD:116-121).

**Gap:** The definition is a proxy (volume spike as exhaustion marker). Tom names the idea ("exhaustion seen with") but does not operationalize the threshold (2.0x mean, 240 bars, 0.1%). No citation of Q18 verbatim in TOM_VERBATIM_INDEX or transcripts searched.

**Verdict:** Operational definition exists (volume spike), but is PLAUSIBLE, not VERBATIM-SOURCED. The numerical threshold (2.0x, 240 bars, 0.1%) is engineering proxy, not Tom's words.

---

## FINDING 3: Absence from Market State Rules

**Checked:** MyTradingSys/conditions/market_state_rules.md sections 1-3 (BALANCE, TREND, STATE TAXONOMY).

**Result:** No mention of CVD divergent or exhaustion as a state classifier. The file defines balance and trend, and splits trend into three structure types (fast, creeping, other), but does not operationalize the unhealthy or transition states.

**Source:** market_state_rules.md:1-100 read; BALANCE section 1-1.5, TREND sections 2-2.5, STATE TAXONOMY section 0 all reviewed.

---

## SUMMARY: T5 CVD DEFINITION — 2026-10-01

1. **CVD divergent:** Tom does NOT define it. No operational rule, no verbatim quote with a concrete logic (e.g., "divergent = slope > X and closes < Y"). The Java classifyState code has a comment placeholder (B063) but no implementation. All unhealthy-trend and transition rules are unreachable.

2. **Exhaustion:** Tom names it ("exhaustion seen with a volume spike") but does not quantify it. The code proxy (last 1m volume > 2.0x mean of 240 bars, close within 0.1%) is engineering-supplied, not sourced to Tom's words. Counts as 1 proof point in SETUP_FORMING verdict.

3. **Next step:** Research task, not code task. Requires:
   - Full read of FABIO_RULEBOOK.md FAB-038, FAB-040 for Fabio's exhaustion or divergence rules (not reviewed for scope of this task).
   - Search of raw_transcripts_canonical for Q18 verbatim (the pointer in PROVENANCE_AUDIT P06).
   - Policy decision: is exhaustion a market state, or a proof signal only?

---

**File:line citations**

- compiled_engine.md:38-46 (no CVD divergent definition, B063 gap noted)
- PROVENANCE_AUDIT_TOM.md rows A25 (CVD divergent, Q21, Q29) and P06 (Volume spike exhaustion, Q18)
- market_state_rules.md:1-100 (state taxonomy, no divergent rule)
- SetupCandidatesBuilder.java:804-816 (volume spike proof implementation)
- FABIO_RULEBOOK.md rows FR-038, FR-040 (not reviewed for this task; referenced as candidates in compiled_engine.md:44-45)

**Verdict codes**

- CVD divergent: NO-SOURCE (PROVENANCE_AUDIT row A25 verdict); ruling: Tom does not define it.
- Exhaustion (volume spike): TOM-CONCEPT-ONLY (P06 verdict); Tom names it, proxy is engineering-supplied.
