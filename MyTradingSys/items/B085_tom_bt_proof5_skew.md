# B085 - Tom BT proof-5 pool skew unexplained

Status: OPEN. Severity: MED. Opened 2026-10-03.

## Defect

After the book_imbalance fix (13295c8), the proof-5 pool is still
215 short vs 105 long. The cause is not established.

## Evidence

- MyTradingSys/system/sessions/MTS-2026-10-02-1422Z-CLI-BLD-tom-diag.md
- MyTradingSys/research/TOM_BT_SHORT_DIAGNOSIS_2026-10-02.md
- F:\MTS\data\tom_bt\allshorts.diag.jsonl row 2: proof-5 long,
  proof_dir aligned, proof_dir_all contradiction,
  pd_details [last_3_delta=neg,neg,neg vs LONG], verdict WAIT_RR.
  This long was suppressed by last_3_delta, not by book_imbalance.
  So a second contradiction path affects longs and not shorts.

## Fix

Determine whether last_3_delta contradiction is intentional
(Tom-sourced) or an asymmetric guard. If intentional, document it.
If not, file a companion to B084.

## Receipt

-

# END
