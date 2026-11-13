# Ship re-measure, first reading (2026-11-13)

Follows SHIP_ARCH_REVIEW_2026-11-12.md ("after rows 1-2, re-measure for 7 days"). **This is a first reading on about 19 hours of
after-data, not the 7-day verdict.** Change commit 7a23bdd16, committed 2026-11-12T18:43:39Z (00:13 IST 11-13). Tool:
`scripts/dev/ship_timing_report.py` (read-only). AFTER = 11-12T18:43:39Z to 11-13T14:00:44Z. BEFORE = the 7 days ending 11-12T18:43:39Z.

## Read this first: the ship counts are not comparable
The review counted 243 ships in 7 days from 50 work trees. Only 28-29 trees still have a `gate_timing.jsonl`, so BEFORE shows 60 ships
(a floor, and biased to the trees that survived). BEFORE ship minutes (40.8) therefore say nothing about the review's 2,736. Compare
the review's own numbers to the review's target, not to this BEFORE column. CI and git numbers come from GitHub and git, so they are complete.
Fix for 11-20: the per-machine log `~/.mts/gate_timing.jsonl` (written since the change) survives retired trees; it holds ship rows, not wall rows.

## Before vs after vs target
| Measure | Review (7 d) | BEFORE here (partial) | AFTER (19 h) | Target |
|---|---|---|---|---|
| Ships seen | 243 | 60 | 26 | about 35 a day |
| Pass / fail | not given | 53 / 7 | 20 / 6 | - |
| Median / p90 wall (min) | not given | 0.18 / 1.89 | 0.49 / 6.71 | under 2 |
| Ships under 2 min | 45 of 69 a day | 54 of 60 | 21 of 26 | most |
| Ships of 5 min or more | 57 | 2 | 4 (40.8 min, 73 % of ship time) | 0 |
| Minutes in ships that then failed | 1,690 | 25.7 | 45.0 (all 6 failures, 4 of them 7-16 min) | low |
| Total ship minutes | 2,736 (391 a day) | 40.8 (partial) | 55.7 in 19 h | 35-70 a day |
| Gate mode recorded per ship | no | no (0 of 60) | 8 of 26 (all smoke); 18 empty | all |
| Slot wait in ship rows (min) | 0 (bug) | NOT MEASURED | 1.3 over 26 ships | about 3 a day |
| wait.log wait since adoption (full / fast) | 381 / 3 a day | 383 / 90 in 7 d | after 11-13T00:30Z: 5.9 min, longest 88 s, no full | small |
| CI runs red / green on trunk | 26 red of 91 | 144 / 537 | 12 / 75 | few |
| Red-trunk minutes (episodes) | about 40 each | 1,534 (62) | 68.8 (4) | low |
| CI median run (min) | 4.5 | 5.8 | 4.7 | 4.5 |
| Admin + merge share of trunk commits | 39 % | 42.9 % (451 admin, 760 merge of 2,820) | 40.9 % (10 admin, 113 merge of 301) | lower |

## Per change
| # | Change | Verdict | Number |
|---|---|---|---|
| 1 | tools/ and unknown paths go to the fast gate | holding (mode), not yet in time | 0 full-mode ships since 00:30Z; the adx ships logged "fast smoke: 3 file(s)". But a fast ship still took 10.6 min (adx-measure, 13:29Z) and 7.1 min (13:59Z): step 3la ran 248 s on a loaded box, near its 240 s ceiling |
| 2 | Live-path ships: fast gate + execution tests + static suite | cannot tell yet | 0 ships recorded with a live mode in the window; nothing exercised it |
| 3 | Card lint, review stamp, Next card name warn only | cannot tell yet | gate_reason still lists steps 3tl,3x,3dl as always-run; no CI red in the window was traced to a card lint (causes of the 4 episodes not individually read) |
| 4 | Test list auto-discovery, 3gd gone | NOT holding | 3gd is gone from the gate, but an unregistered test (test_cotrade_close.py, 627330d8e) turned CI red; reverted d89eb9ca2; another agent is fixing. CI reds 12 in the window, 4 episodes, 68.8 min |
| 5 | Root junk never staged | cannot tell yet | no gate.log or run.out ship was looked for; NOT MEASURED |
| 6 | Timing log: mode, reason, slot wait; tests off wait.log | partly holding | 0 test-tree rows in wait.log after 00:30Z (holding). Mode/reason on 8 of 26 ships; 18 rows empty (cause not checked, probably no-gate docs ships). Defect: the 637 s failed ship (adx-measure 13:29Z) logged `run_s` 0 and `gate_s` 0, so phases cannot show where its 10.6 min went |
| 7 | Route tag rides the ship commit, no empty admin commits | holding for admin, not for merges | admin commits 16 % of trunk commits BEFORE (451 of 2,820), 3 % AFTER (10 of 301). Merge commits rose 27 % to 38 %; change 7 does not touch them |
| 8 | Coordinator plan timing row | cannot tell yet | no `*-plan-timing.jsonl` under ~/.mts on this machine; NOT MEASURED |

## Other facts checked
- Research ship europe-high-fade-full-1113, 13:50Z: failed after 16.3 min in smoke mode (steps 4e, 3dl, 3pc, 4t) on a loaded machine. Smoke mode did not make it fast.
- Stale `index.lock` after failed ships: reported twice by the caller, not measured by this tool.
- Of the 26 after-ships 6 failed (23 %); BEFORE 7 of 60 (12 %). Small samples.

## Method limits
Definitions: "admin" = non-merge commit with no files or a subject starting "route tag", "TASK:", "desk task". "Red minutes" = first red run start to the
next green run finish. wait.log rows from temp trees (tmp*) are test runs. All wait.log pre-change "full" rows after 18:43Z are from trees that had not pulled the change.

## Re-run on 2026-11-20 for the real 7-day reading
```
cd C:\Users\E-ngineers\IdeaProjects\<your work tree> && git fetch origin && python scripts/dev/ship_timing_report.py --since 2026-11-12T18:43:39Z --until 2026-11-19T18:43:39Z
```
Run it once more with `--since 2026-11-05T18:43:39Z --until 2026-11-12T18:43:39Z` for BEFORE on the same machine. Card: ship-remeasure-7day-1120.
