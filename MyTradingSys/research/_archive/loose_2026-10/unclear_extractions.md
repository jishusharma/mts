# FILE: unclear_extractions.md
# READ ORDER: Reference only — NOT loaded at runtime
# PURPOSE: Track Tom extractions that are NOT ready for engine integration
# RULE: If an extraction lacks clear behavioral rules (what, when, how, invalidation), it stays HERE until validated.
# POLICY: Rule 35 — validate against 3 live snapshots before adding to compiled_engine.md.
# LAST UPDATED: 2026-08-29
# ---

# UNCLEAR EXTRACTIONS — MTS v4.2.0-p2
# Date: 2026-08-29
# Status: 1 extraction flagged. 0 integrations attempted.

---

## UE-001: Post-Breakdown Retest Rule

**Source:** AI-derived from htf_structure_audit_2026-08-28.md Gap analysis
**Tom Evidence:** INDIRECT — Tom discusses "breakout of balance" and "trading with trend after breakout" but does NOT define retest mechanics.
**What is missing:**
| Question | Status | Why It Blocks Integration |
|----------|--------|---------------------------|
| What TF tracks the breakdown? | UNKNOWN | Daily? 4H? Weekly? Determines flag persistence. |
| What defines "breakdown"? | UNKNOWN | Close below VAL? Wick below? 0.3%? 0.5%? Determines trigger. |
| What defines "retest"? | UNKNOWN | Price returns to broken level? Touches? Closes within X%? Determines entry. |
| Setup type on retest? | UNKNOWN | TC (trend continuation)? CT reversion? Different stops, targets, proof. |
| What invalidates the flag? | UNKNOWN | New session? Close back above? Time decay? Determines when rule turns off. |

**Why NOT in engine:** Without answers to all 5 questions, any engine rule would be AI interpolation, not Tom-validated. Per Rule 35: extract -> test 3 snapshots -> only add if it changes verdicts. Cannot test what is not defined.

**Action:** Revisit when new Tom extractions provide clarity on any of the 5 questions. Do NOT integrate until all 5 are answerable from extracted content.

---

## UE-002: [RESERVED — next unclear extraction goes here]

**Source:** 
**Tom Evidence:** 
**What is missing:**
**Why NOT in engine:** 
**Action:** 

---

# END
