# T038 - VERDICT HAS NO CONTEXT-BUCKET GATE

Register row: MyTradingSys/research/BUGS.md T038.
Note: T038 sits in the BUGS table in BUGS.md, not the TASKS table. ID prefix is T but the row is filed under bugs. Recorded as-is. Do not renumber.
Convention: one item, one doc. Verbatim ask at top when available. Updates appended chronologically, newest last.

## VERBATIM ASK

No verbatim ask on record (opened 2026-09-19). Row title and evidence transcribed below from BUGS.md.

Title: Verdict has no context-bucket gate; engine fires in buckets with no measured edge.

Evidence: runtime_data/outcome_labels.json n=4418, 2026-09-12 to 2026-09-19.

2026-09-19 analysis: day-corrected forward returns grouped by price_vs_va + cvd_slope. Buckets with n>400 (in_va rising n=1166, in_va falling n=1406, in_va flat n=442, above_vah rising n=508, above_vah falling n=436) all sit within +/-0.12% of zero at 120m horizon. One candidate signal: below_val falling n=221 rel +0.26% (ratio 0.64 sigma). Sample likely clusters on 2-3 days; effective n unverified.
Recommendation: defer fix until labels reach ~21000 (3-4 weeks at current rate), then split by context AND day AND hour. No code change now.

## STATE

2026-09-22 OPEN. MED severity. Deferred by recommendation. No code change until label count reaches ~21000.

## UPDATES (chronological, newest last)

### 2026-09-22T18:00Z - coordinator, session MTS-2026-09-22-1737Z

Item doc created during T039 functionality-doc sweep. Caught by new Build-Check enforcement rule (every OPEN row must have a matching items/ file).
