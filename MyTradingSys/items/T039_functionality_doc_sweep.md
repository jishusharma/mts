# T039 - FUNCTIONALITY-DOC SWEEP

Register row: MyTradingSys/research/BUGS.md T039.
Convention: one item, one doc. Verbatim ask at top when available. Updates appended chronologically, newest last.

## VERBATIM ASK

No verbatim ask on record. Rule set by operator 2026-09-22, transcribed below from BUGS.md.

Title: Functionality-doc sweep. One item one doc, verbatim ask at top, chronological updates. Register holds state + pointer.

Sources to fold: dsa_developer_implementation_tasks.md L365; compiled_output_audit_20260915.md L104; ALERT_REDESIGN_PROPOSAL.md L87; what_is_next.md Stage 3; INDICATOR_IMPLEMENTATION_HANDOFF.md Phase 3.

Expiry 2026-10-06 (IN-FIX rule).

## STATE

2026-09-22 OPEN. Sweep executed 2026-09-22T18:00Z.
Created item docs for open register rows lacking one: B058, B059, B062, T034, T035, T037, T039.
Existing: B063, T040.
Enforcement (Build-Check addition: every OPEN row must have a matching items/ file) is a stated plan, not written.

## UPDATES (chronological, newest last)

### 2026-09-22T18:00Z - coordinator, session MTS-2026-09-22-1737Z

Sweep pass. Seven item docs created.

### 2026-09-23T15:30Z - coordinator, session MTS-2026-09-23-1445Z

Source-fold pass. Five T039 source locators folded:

| # | Source | Locator | Destination | Action |
|---|--------|---------|-------------|--------|
| 1 | dsa_developer_implementation_tasks.md | L366 | T044 | NEW item doc |
| 2 | compiled_output_audit_20260915.md | L104 | B063_divergence.md | appended fold note |
| 3 | ALERT_REDESIGN_PROPOSAL.md | L87 | T045 | NEW item doc |
| 4 | what_is_next.md Stage 3 | anchor L32 | T046 | NEW item doc |
| 5 | INDICATOR_IMPLEMENTATION_HANDOFF.md Phase 3 | anchor L217 | T034_positioning_states.md | appended fold note |

Distinct from the 2026-09-22T18:00Z pass: that pass created item docs for open register rows lacking one (B058, B059, B062, T034, T035, T037, T039). This pass folds five named source locators into their target items.
