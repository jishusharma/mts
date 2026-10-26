# B085 - Tom BT proof-5 pool skew unexplained

Status: OPEN. Severity: MED. Opened 2026-10-03.

## Defect

After the book_imbalance fix (13295c8), the proof-5 pool is still
215 short vs 105 long. The cause is not established.

## Evidence

- MyTradingSys/system/sessions/MTS-2026-10-02-1422Z-CLI-BLD-tom-diag.md
- MyTradingSys/research/_archive/loose_2026-10/TOM_BT_SHORT_DIAGNOSIS_2026-10-02.md
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

## 2026-10-04T12:15Z - hypothesis refuted

Read F:\MTS\data\tom_bt\allshorts.diag.jsonl (320 rows, 215 short / 105 long).

last_3_delta contradiction rate is comparable in both directions:
- 21 of 105 longs (20.0%) hit last_3_delta=neg,neg,neg vs LONG.
- 37 of 215 shorts (17.2%) hit last_3_delta=pos,pos,pos vs SHORT.

Not asymmetric. The last_3_delta guard fires at the same rate against longs
and shorts. It is not the driver of the 215:105 pool skew.

After the 13295c8 book_imbalance guard, the pool ratio at the survivor level
is closer to parity: 19 short survivors (8.8% of the short pool) and 9 long
survivors (8.6% of the long pool).

Where the skew actually lives: upstream, in the candidate pool composition,
not in math_object_builder's proof-direction guard. The 320 proof-5 rows are
pre-classified short/long by SetupCandidatesBuilder.java. The 2:1 short:long
ratio is baked in before proof-direction runs.

Action: close B085 (hypothesis refuted). File B131 for the candidate-pool
skew, which is a separate defect in a separate file.
