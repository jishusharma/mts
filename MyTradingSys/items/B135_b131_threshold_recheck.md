# B135 - B131 follow-up: ps1 proof-count thresholds and allshorts parity re-run

Status: OPEN. Severity: LOW. Opened 2026-10-05.
Filed by: 
MTS-2026-10-04-1325Z-DSA-COO

## Defect

B131 (commit 4f9290e, 2026-10-05) removed book_imbalance from
SetupCandidatesBuilder.countSignals. Two follow-ups were named in the
B131 session reply (T5 MISSED) and were not done:

1. start-trading-day.ps1 reads score.proof_count at L185, gates on -lt 3
   (L225) and -lt 5 (L227), and alerts on crossing 5 (L578). The max
   reachable count dropped from 7 to 6. The composition of counts shifted
   (shorts lost a guaranteed +1; longs lost nothing). Thresholds may fire
   at different rates than before.

2. The base-rate diag (F:/MTS/data/tom_bt/allshorts.diag.stdout.txt) was
   not re-run against the fixed build to confirm proof-5 pool parity.

## Evidence

- 4f9290e: SetupCandidatesBuilder.java L575-580 removed.
- SetupCandidatesBuilderRulesTest.java proofCountFourOfSixIgnoresBookImbalance
  and proofCountFiveOfSixIgnoresBookImbalance added.
- B131 reply T5: "The ps1 tier thresholds ... are untouched. They now see
  a max proof_count of 6, with one fewer reachable slot. Re-check them."
- B131 reply T5: "I did not re-run the allshorts diag to confirm proof-5
  parity."

## Fix shape

Read-only first: re-run the diag against the current build, tabulate the
proof-count distribution by direction, compare to the pre-fix numbers
(proof 4 balanced, proof 5 2:1 short). Then decide whether L225/L227/L578
need retuning or hold. If a code edit is needed, one file
(start-trading-day.ps1), test must fail on pre-change at least once.

## File set

scripts/core/start-trading-day.ps1 (if a code edit is needed).
F:/MTS/data/tom_bt/allshorts.diag.stdout.txt (read-only, diag re-run).

2026-10-10: not closed. Old allshorts diag (320 proof>=5 rows, 19 SETUP_FORMING all short) was built mostly on the removed 0.2 pct fallback stop (287 of 320, 17 of 19), so it cannot be the parity baseline. The re-run needs snapshots regenerated with HEAD Java: desk task 20261009-205714-b147-b135-regenerate-tom-snapshots-with- (JIS-NB). Then read L225/L227/L578 against the new base rate.

# END
