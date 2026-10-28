# B100 - EXEC_PROVENANCE_AUDIT verdict mismatch on E1b and E2

Status: CLOSED | Severity: MED | Opened 2026-10-04

## Defect

The audit's own verdict definitions (EXEC_PROVENANCE_AUDIT.md H1, line 5-6):

  SOURCED      = a quote supports the value.
  CONCEPT-ONLY = the trader names the idea, the number is ours.
  NO-SOURCE    = no idea behind it, or a role the trader never gives it.

E1b (Tom limit wait before cancel) carries Q03 yRv:19@5832:
  "rests the order and let the market decide" (no duration stated).

E2 (Tom time exit) carries Q09 kXh:19@1020, Q10 WSC:19@10798,
Q11 4Mo:19@21830 ("Speed Off"), Q12 4Mo:19@22013 (session end).

Both rows are labelled NO-SOURCE. Under the audit's own rules, a quote
that supports a trader idea with no number is CONCEPT-ONLY, not NO-SOURCE.

## Impact

The verdict label drives the fix path.

- NO-SOURCE -> remove or shadow (the parameter must go away).
- CONCEPT-ONLY -> MEASURE per Ruling 3 (accepted 2026-10-04).

E1b and E2 are already flagged MEASURE and already accepted by the
operator under Ruling 3. The audit reads as if those two values must be
removed instead. The two semantics collide on the same row.

## Fix shape

Reclassify E1b-T and E2-T from NO-SOURCE to CONCEPT-ONLY in the E1-E9
table. Keep the quotes. Keep the MEASURE flag and the Ruling 3 citation.
Re-run Build-Check. Update the audit header if the totals in H2 change.

## Evidence

- MyTradingSys/research/EXEC_PROVENANCE_AUDIT.md (H1 verdict defs, E1b/E2 rows)
- MyTradingSys/research/fast_track_2026-09-27/PROVENANCE_AUDIT_TOM.md (Q03, Q09-Q12)
- OPERATOR_RULINGS_2026-10-02.md (Ruling 3, accepted 2026-10-04)

## Receipt

2026-10-04: E1b-T and E2-T reclassified NO-SOURCE -> CONCEPT-ONLY in EXEC_PROVENANCE_AUDIT.md, H2 counts updated; commit "B100: reclassify E1b-T/E2-T to CONCEPT-ONLY" (MTS-2026-10-04-1121Z-APP-BLD-b100-verdict-labels).
## 2026-10-04T11:45Z - E2-T reverted

E2-T reverted from CONCEPT-ONLY back to NO-SOURCE. B100's filing claimed every quoted passage supports a Tom idea for the E2 row. The row's own text contradicts that: Q09 kXh:19@1020 and Q10 WSC:19@10798 are labelled Opposed to a hold-time rule, Q11 is an event exit, and Q12 ends the session. H1 line 7 defines NO-SOURCE as no idea behind it, or a role the trader never gives it. Tom never gives time exit that role. E1b-T remains CONCEPT-ONLY.
