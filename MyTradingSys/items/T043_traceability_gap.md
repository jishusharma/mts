# T043 - SOURCE-TO-CODE TRACEABILITY MECHANISM ABSENT

Register row: MyTradingSys/research/BUGS.md T043.
Opened: 2026-09-23 by MTS-2026-09-23-0831Z. Severity HIGH.

## THE PATTERN

Five hand-authored layers: transcript -> extract -> condition file -> compiled_engine.md -> code (Java/Python/PS1). No layer references the layer above by ID. Drift is silent. The gap is rediscovered each session.

## EVIDENCE OF PRIOR DISCOVERY

- MyTradingSys/research/_archive/loose_2026-10/EXTRACTION_TO_ALERT_AUDIT_2026-09-19.md L10: Phase 4 landed in the engine document only. Zero traceability links exist from the engine document to Java, to Python runtime, to the watch script, or to the verdict script. Audit was a one-time pass. No mechanism followed.
- MyTradingSys/system/COMPILED_DECISIONS.md A5 (2026-08-30): Compiled engine 93% compileable. 55 functions mapped. 51 = deterministic compiled code. 2 = AI-only visual flags. 2 = hybrid. Mapping was a one-time pass.
- MyTradingSys/tests/compiled_code_opportunities.md: Status ACTIVE v4.2.0-p5, dated 2026-08-30. Artifact of the A5 pass. Not refreshed since.
- MyTradingSys/methodology/extraction.md: 4-phase lifecycle defined. Safeguards 1-5. No mechanism enforces any of it.
- MyTradingSys/system/01_AI_BEHAVIOR.md Rules 31-36: validation rules defined. Not machine-enforced.

## CONSEQUENCE

Every session that asks is rule X correctly implemented must re-derive from disk by hand. No artifact answers. Audits become prose, not gates.

## PROBLEM STATEMENT

Two layers, different cadences:
1. Source integrity: code vs doc; doc vs source quote.
2. Applicability: does the rule input data exist in the current snapshot.

## FIX SHAPE

1. Establish derivation direction.
2. Pick one slice. Recommendation: hard stops (7 rows, highest consequence).
3. Audit the slice fully.
4. Decide doc-matrix vs runtime self-report after the slice.

## STATUS

WONTFIX, closed 2026-09-23-1445Z (BUGS.md receipt: "Gate rejected
2026-09-23-1445Z; traceability mechanism not implemented as a gate.").
This item doc was never updated to match at the time - found and synced
2026-09-26 while checking the 2026-09-25 PROJECT_VISION.md.new layer-freeze
draft, whose second freeze condition ("until T043 closes") assumed an
un-synced status. See that draft for the live question this raises.

# END
