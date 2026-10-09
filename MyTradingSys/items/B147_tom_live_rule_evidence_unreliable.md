# B147 - Tom live-rule evidence is unreliable: rerun shows 0 SETUP_FORMING signals but the older run on the same history had 19 (all short); the 'history lacks data' explanation is contradicted; holdout read twice; the Oct-7 run is not on HEAD

Status: OPEN. Severity: HIGH. Opened 2026-10-09.
Session: MTS-2026-10-09-APP-ANA-major-gaps-audit. Source: research/AUDIT_MAJOR_GAPS_2026-10-09.md (audit revalidated by four read-only workers; no code edited).

## Defect

Tom live-rule evidence is unreliable: rerun shows 0 SETUP_FORMING signals but the older run on the same history had 19 (all short); the 'history lacks data' explanation is contradicted; holdout read twice; the Oct-7 run is not on HEAD.

## Evidence

- Worker recomputation from F:\MTS\data\tom_bt\*.rows.jsonl (120,892 rows): 320 rows at proof 5 and 19 SETUP_FORMING, all short. The rerun (TOM_CORE_BT_RERUN_2026-10-06_full.md:12-14) has rows 90,699 and proof histogram {3: 13,666; 4: 331; 5: none}. The report blames missing book/funding/OI, but the old run had the same history and produced 19 signals and 17 fills. AUDIT_CLOSEOUT_2026-10-07.md:66 says the row drop is 'not yet attributed'.
- H1 (all-short) is not resolved: B131 is CLOSED on a code change plus unit tests only; B135 (post-fix parity re-run of the diag) is OPEN. No post-fix long/short measurement of the LIVE rule exists; only proof>=3 sensitivity variants show parity.
- bt_runs/tom_core_20260929/FROZEN.md (added by f2e7229) says holdout 'run once, this run', and the Oct-7 report reads the same 2026-06-26.. holdout again: used twice. The Oct-7 run directory bt_runs/tom_core_20261007 exists only on origin/research/agenda-2026-10-06 (7aa01cd), not on HEAD, yet the report cites its FROZEN.md. F:\MTS has no tom_bt_2026-10-07 data, so the rerun numbers cannot be recomputed here.
- TRIAL_REGISTRY.csv at HEAD has 20 data rows, not the 36 the report cites (the other 16 are on the unmerged branch). tom_bt_report.py:197 n_trials = lines-1; lines 329-330 only print that DSR 'would need >= 100 trades'; no DSR or multiple-testing correction is computed for Tom (Bonferroni only for 8 Fabio-tag comparisons, none survive). Registry rows count variants of one run, not independent hypotheses.
- Fabio v3 P2: A/B/D have 0 OOS trades (not evaluable), C negative (-0.1038 over 79 days, recomputed from F:\MTS\data\fabio_v3_bt\dayR.json). research/P2_FABIO_V3_HOLDOUT_STATUS.md wrongly says the 2026-06-26.. holdout was read once on 2026-10-04; PRE_REG_FABIO_V3.md:28 says it was not read. SUPERVISOR_LOG.md:269 still says 'P4 8h window PASS', void since the corrected run (075e1c5).

## Fix shape

(1) Attribute the row drop 120,892 -> 90,699 and the loss of proof-5 rows (diff the two snapshot generators); until done the live rule has NO valid backtest, say 'insufficient N'. (2) Close B135: re-run the allshorts diag after B131 and report long vs short counts for the live rule. (3) Merge or archive the research/agenda branch so the Oct-7 run is on HEAD; state in FROZEN.md that the holdout has been read twice and treat it as burned for Tom. (4) Count trials honestly and apply DSR/PBO for Tom as for Fabio v3. (5) Correct P2_FABIO_V3_HOLDOUT_STATUS.md and the SUPERVISOR_LOG P4 PASS line.

## Related

- MyTradingSys/research/AUDIT_MAJOR_GAPS_2026-10-09.md

## Receipt

2026-10-09 consolidate session: done (3) bt_runs/tom_core_20261007/FROZEN.md + 36-row TRIAL_REGISTRY.csv copied from research/agenda-2026-10-06 (branch itself not merged); (5) P2_FABIO_V3_HOLDOUT_STATUS corrected, SUPERVISOR_LOG correction appended; holdout recorded as burned for Tom. Still open: (1) attribution of the 120,892 to 90,699 row drop (F-BT-01 attributes 19 old signals: 7 candidates gone, 12 lost one proof point), (2) B135 long/short re-run, (4) DSR/PBO for Tom.

# END
