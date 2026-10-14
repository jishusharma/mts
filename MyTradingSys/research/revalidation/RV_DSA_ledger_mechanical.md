VERDICT: FIX-FIRST

# RV-DSA Tom ledger mechanical check + layer index path audit

Date 2026-10-14 UTC. Host JIS-NUC. Read only, no edit.

## Check 1 mechanical
rows 37 (header excluded)
ISO-parseable date per row 0. The date column is empty on all 37 rows.
date vs trade_date_status leak 0 (no row carries a date value).
same-group trade_date_inferred splits 0.
geometry per ENTRY row 0 violations.
group counts vs TOM_LEDGER_CANONICAL_GROUPS.csv all 12 match (T1 5, T2 3, T2b 4, T3 4, T3b 4, T4 3, T5 4, T6 3, T7 2, T8 1, T11 2, T12 2 = 37).
frame pointers 0 missing; three bare filenames resolve under frames, the sheet pointer under sheets.

## Layer index path audit
92 real paths across layer_index.json and layer_map.json. 5 flagged strings are prose/globs not paths (fabio_v3.py, fabio_of_model.py, run_v3_l3.py, orderflow_bars.py, matrix_q33.py); each real file exists. 0 missing real paths.

## Findings
ID | sev | where | wrong | fix
L-1 | MED | TOM_TRADE_LEDGER.csv date column | empty on every row while trade_date_status describes a date | populate only where status is a real date, or drop the column
L-2 | LOW | prompt already-known (a) | false | record the refutation

## Known-finding check
(a) date prose for T9/T10/T11 and ISO for T5/T6/T7: REFUTED, date empty on all rows.
(b) T6 2026-06-02 vs T10 2026-06-08: NOT_IN_DATA, both tdi empty.
(c) T11 UNRESOLVED vs T11-x 2026-09-01: NOT_IN_DATA, both tdi 2026-08-31.
(d) T1 initial stop 24485: CONFIRMED, text '24485(moved)'.
(e) T12-m1 side holds stop_tighten: CONFIRMED.

## Not checked
Checks 2-4 (provenance, repair fidelity, header counts) not run; card asked check 1 plus the path audit.
