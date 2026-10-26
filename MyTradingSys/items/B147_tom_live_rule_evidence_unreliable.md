# B147 - Tom live-rule evidence is unreliable: rerun shows 0 SETUP_FORMING signals but the older run on the same history had 19 (all short); the 'history lacks data' explanation is contradicted; holdout read twice; the Oct-7 run is not on HEAD

Status: IN-FIX. Severity: HIGH. Opened 2026-10-09.
Session: MTS-2026-10-09-APP-ANA-major-gaps-audit. Source: research/_archive/loose_2026-10/AUDIT_MAJOR_GAPS_2026-10-09.md (audit revalidated by four read-only workers; no code edited).

## Defect

Tom live-rule evidence is unreliable: rerun shows 0 SETUP_FORMING signals but the older run on the same history had 19 (all short); the 'history lacks data' explanation is contradicted; holdout read twice; the Oct-7 run is not on HEAD.

## Evidence

- Worker recomputation from F:\MTS\data\tom_bt\*.rows.jsonl (120,892 rows): 320 rows at proof 5 and 19 SETUP_FORMING, all short. The rerun (TOM_CORE_BT_RERUN_2026-10-06_full.md:12-14) has rows 90,699 and proof histogram {3: 13,666; 4: 331; 5: none}. The report blames missing book/funding/OI, but the old run had the same history and produced 19 signals and 17 fills. AUDIT_CLOSEOUT_2026-10-07.md:66 says the row drop is 'not yet attributed'.
- H1 (all-short) is not resolved: B131 is CLOSED on a code change plus unit tests only; B135 (post-fix parity re-run of the diag) is OPEN. No post-fix long/short measurement of the LIVE rule exists; only proof>=3 sensitivity variants show parity.
- bt_runs/tom_core_20260929/FROZEN.md (added by f2e7229) says holdout 'run once, this run', and the Oct-7 report reads the same 2026-06-26.. holdout again: used twice. The Oct-7 run directory bt_runs/tom_core_20261007 exists only on origin/research/agenda-2026-10-06 (7aa01cd), not on HEAD, yet the report cites its FROZEN.md. F:\MTS has no tom_bt_2026-10-07 data, so the rerun numbers cannot be recomputed here.
- TRIAL_REGISTRY.csv at HEAD has 20 data rows, not the 36 the report cites (the other 16 are on the unmerged branch). tom_bt_report.py:197 n_trials = lines-1; lines 329-330 only print that DSR 'would need >= 100 trades'; no DSR or multiple-testing correction is computed for Tom (Bonferroni only for 8 Fabio-tag comparisons, none survive). Registry rows count variants of one run, not independent hypotheses.
- Fabio v3 P2: A/B/D have 0 OOS trades (not evaluable), C negative (-0.1038 over 79 days, recomputed from F:\MTS\data\fabio_v3_bt\dayR.json). research/_archive/loose_2026-10/P2_FABIO_V3_HOLDOUT_STATUS.md wrongly says the 2026-06-26.. holdout was read once on 2026-10-04; PRE_REG_FABIO_V3.md:28 says it was not read. SUPERVISOR_LOG.md:269 still says 'P4 8h window PASS', void since the corrected run (075e1c5).

## Fix shape

(1) Attribute the row drop 120,892 -> 90,699 and the loss of proof-5 rows (diff the two snapshot generators); until done the live rule has NO valid backtest, say 'insufficient N'. (2) Close B135: re-run the allshorts diag after B131 and report long vs short counts for the live rule. (3) Merge or archive the research/agenda branch so the Oct-7 run is on HEAD; state in FROZEN.md that the holdout has been read twice and treat it as burned for Tom. (4) Count trials honestly and apply DSR/PBO for Tom as for Fabio v3. (5) Correct P2_FABIO_V3_HOLDOUT_STATUS.md and the SUPERVISOR_LOG P4 PASS line.

## Related

- MyTradingSys/research/_archive/loose_2026-10/AUDIT_MAJOR_GAPS_2026-10-09.md

## Receipt

2026-10-09 consolidate session: done (3) bt_runs/tom_core_20261007/FROZEN.md + 36-row TRIAL_REGISTRY.csv copied from research/agenda-2026-10-06 (branch itself not merged); (5) P2_FABIO_V3_HOLDOUT_STATUS corrected, SUPERVISOR_LOG correction appended; holdout recorded as burned for Tom. Still open: (1) attribution of the 120,892 to 90,699 row drop (F-BT-01 attributes 19 old signals: 7 candidates gone, 12 lost one proof point), (2) B135 long/short re-run, (4) DSR/PBO for Tom.

2026-10-10: part (1) attributed from the old run files: kept 120,892 of 164,257; 97,504 rows (80.7 pct) carried the exact +/-0.2 pct fallback stop; 287 of 320 proof>=5 rows and 17 of 19 SETUP_FORMING rows did. 0c34a2d removed that fallback (candidate dropped when no swing lies beyond the zone) and B131 removed one proof slot, which is the whole drop. So the 19 old signals are not evidence for the live rule; the statement is insufficient N. Doc: research/_archive/loose_2026-10/B147_ROW_DROP_ATTRIBUTION_2026-10-10.md. Still open: (a) exact per-snapshot regeneration with HEAD Java, (2) B135 long/short diag under sourced stops, (4) DSR/PBO for Tom: desk task 20261009-205714-b147-b135-regenerate-tom-snapshots-with- (JIS-NB, staged overlays live there).

2026-10-10 (JIS-NB desk run): (a) done: snapshots regenerated with HEAD Java cceff62, 90,295 kept; 37,798 of 40,401 lost snapshots (93.6 pct) had an old fallback-stop top candidate; old proof>=5 320 (280 fallback by the 0.011 tolerance used in the script; the 287 above used a looser match), new 0; old SETUP_FORMING 19 (17 fallback), new 0. (2) done: B135 diag n=0 under sourced stops. (4) DSR/PBO moot at N=0 signals. Doc: research/_archive/loose_2026-10/B147_ROW_DROP_EXACT_2026-10-10.md. Item closed.

# END
