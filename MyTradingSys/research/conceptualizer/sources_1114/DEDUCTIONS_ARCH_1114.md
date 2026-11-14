# "Deductions Architecture": where it stands (read 2026-11-14, origin/fast-track)

**What he meant (best reading, not certain):** the dev-system architecture review whose method is a "deduction formula" (Score = V - C, minutes per day; cut a piece when its value is no more than its cost). He asked for it on 2026-11-10: "a Fable session which will look into the optimizations and deductions from the architectural point of view" (OPERATOR_DECISIONS.md, 11-10 11Z). "Deductions" there means cuts/removals. The 11-13 voice line is likely the same thing, or a mishearing of "Detections" (the Conceptualizer); the Conceptualizer is a different project (concept pages per trader), so I ruled it second.

## What exists (documents)
| File (under MyTradingSys/system/) | What it holds |
|---|---|
| ARCH_REVIEW_2026-11-10.md | 12 ordered cuts (delete doc-wording tests, set-based count tests, one gate queue, hook trimming, stale STATUS, closed cards, test-list autodiscovery, PR auto-merge trial), "must not be cut" list, 2-week order |
| SHIP_ARCH_REVIEW_2026-11-12.md | The V-C formula, scored 14 pieces, target design: fast gate (under 2 min) locally, full suite on CI only, deploy green-only; 8-row change list |
| OPERATOR_DECISIONS.md (11-12 ~18:10Z) | He said "yes all 8" to the ship-architecture change list (including reversing the 11-10 must-not-cut on the full local suite for live-path ships) |

## What is wired (done on trunk)
- Ship changes 1-8 applied by Gemini in commit 7a23bdd16 (gate_select fast path, live-path fast gate plus execution tests, lint warn-only, timing log, no junk staging).
- Test-list auto-discovery landed after two revert cycles (a2df4a0c3 reverted, re-landed 11-13 21:15 IST).
- Ship timing report re-landed (ship_timing_report.py); his measure: local ship 9 s to 2.4 min (was 17-27 min); CI median 4 min.
- 11-13 18:42Z: gate parity work (0b5e71980) makes the ship gate run the CI-only checks (3pc, 3x, 4e, layer_map, extra_tests.tsv).

## What is missing / open
- Independent Claude review of changes 1-8 is still a request, not a stamp: research/audits/SHIP_CHANGES_1_8_REVIEW_REQUEST_2026-11-13.md (8 findings; e.g. 3gd removal unverified, `lint --warn` may demote more than paperwork, LAYERS.md regenerate and wait.log changes not seen in the diff).
- 35 of 57 trunk runs were red in 4 h on 11-13 (4 breaks, each a check CI runs that the local gate did not). Next step if red persists: the "ship train" cards (ship-train-*).
- 11-10 rows not confirmed done: 7 (worktree removal), 8 (move 434 closed cards), 9 (STATUS.md regeneration, route-tag riding in the commit), 10 (docs move), 12 (PR auto-merge trial, parked: merge queue is org-only).
- Change 8 (coordinator layer: measure tokens per plan run for one day, then drop the forced 10 min plan run) not started; no token numbers exist.
- 7-day re-measure after changes 1-2 is due before touching the slot queue (he said "start the 7-day re-measure" at 13:55Z).
- I did not verify each change against code on disk; status is from commit messages and the docs above.
