# B147 - attribution of the Tom backtest row drop 120,892 -> 90,699 and the loss of proof-5 rows (2026-10-10)

Question (AUDIT_CLOSEOUT_2026-10-07.md:66 "not yet attributed"): the old run on 2022-01-20..2026-09-26 history kept 120,892 of 164,257 evaluated
15-minute snapshots and had 320 rows at proof 5 and 19 SETUP_FORMING (all short); the 2026-10-06 rerun kept 90,699 and has proof {3: 13,666; 4: 331; 5: none}.
The rerun blamed "history has no book/funding/OI proofs"; the old run had the same history, so that cannot be the cause.

## Evidence (all counted from the old run files on this host, F:/MTS/data/tom_snapshots/*.meta.json and F:/MTS/data/tom_bt/*.rows.jsonl)
- Snapshots evaluated 164,257 in both runs (same grid). Old kept 120,892 (73.6 %), new kept 90,699 (55.2 %): 30,193 snapshots lost every candidate.
- In the old rows, the candidate's stop is exactly zone x 1.002 (short) or x 0.998 (long) in **97,504 of 120,892 rows (80.7 %)**: the 0.2 % fallback
  stop of SetupCandidatesBuilder (A03) that applied when no swing lay beyond the zone.
- Of the 320 old proof>=5 rows, **287 carry that fallback stop**; of the 19 old SETUP_FORMING rows, **17 do**.
- Commit 0c34a2d (2026-10-06 14:28Z, "remove NO-SOURCE stop fallback/floor, T3 ruling") deleted the fallback and the 0.1 % floor: a candidate with no swing
  beyond the zone now returns no stop and is dropped (fail closed). SetupCandidatesBuilderStopT3Test pins this. The rerun used HEAD Java, so every
  snapshot whose only candidates relied on the fallback disappeared, and with them most of the proof-5 rows.
- B131 (4f9290e) removed the book-imbalance slot from the proof count (max 7 -> 6). F-BT-01 attributes the remaining 2 of 19 signals to that.

## Attribution
| Effect | Cause | Size |
|---|---|---|
| kept 120,892 -> 90,699 (-30,193 snapshots) | stop fallback removed (0c34a2d): candidates without a swing beyond the zone are dropped | fallback stop in 80.7 % of old kept rows; exact per-snapshot diff needs regenerated snapshots |
| 320 proof-5 rows -> 0 | same: 287 of 320 were fallback-stop candidates; the rest lost a point to B131 | 287 / 320 |
| 19 SETUP_FORMING -> 0 | 17 of 19 fallback-stop candidates; 2 lost the book-imbalance proof point | 17 + 2 |

So the 19 old "live rule" signals were mostly built on an unsourced stop. The honest statement for the Tom live rule is **insufficient N (0 signals under
sourced stops)**, not "no edge" and not an edge. The old 17 fallback-stop signals must not be cited as evidence for the live rule.

## Not done here (needs the Java snapshot generator and its staged overlays, which live on JIS-NB)
1. Regenerate snapshots with HEAD Java and diff against the old ones to confirm 90,699 and give the exact per-snapshot split.
2. B135: rerun tom_bt_diag.py on the regenerated rows (long/short counts at proof>=5 under sourced stops).
3. DSR/PBO for Tom (trial count honest, registry rows are variants of one run).
Desk task posted for JIS-NB with the commands (see B147 item receipt).
