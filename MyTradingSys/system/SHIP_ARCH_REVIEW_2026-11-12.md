# Ship system review: one optimized design (2026-11-12)

Operator order 2026-11-12 ~17:00Z: work takes too long to reach trunk; are we over-complicated, do we need this system, what do
practical teams do. Read-only review (Fable, login C, desktop). Nothing here is applied: every row needs the operator's yes.
Follows ARCH_REVIEW_2026-11-10.md and uses its deduction method.

## 1. Verdict
**Yes, over-complicated, in one place: the full test suite runs on the desktop before a push.** Everything else is cheap.

| Fact (measured) | Number |
|---|---|
| Ships today under 2 min | 45 of 69 |
| Ships today of 5 min or more | 13, holding 754 of 812 minutes (93 %) |
| 7 days: ships of 5 min or more | 57 of 243, holding 2,601 of 2,736 minutes (95 %) |
| 7 days: minutes spent in ships that then failed | 1,690 (62 % of all ship time) |
| Full suite on the desktop today (passing runs) | 44 to 132 min; 9 min on a quiet machine |
| The same suite on CI (91 runs, 22 h, both OSes) | median 4.5 min, p90 5.9 min |
| Slow ships that really touched the live path | 5 of 57 (369 min, 14 %) |
| Slow ships sent to the full suite by an unknown, non-live path | 32 of 57 (1,438 min, 55 %) |
| Wait for a gate slot today | full gates 381 min (longest 77), fast gates 3 min |

The desktop does in 44-132 min what CI does in 4.5 min, and CI does it again anyway. The live tree is protected three more
times after the local gate (CI on both OSes, green marker, a second full run on the live box before a deploy), so the local
full run adds waiting, not safety. Do we need the system? Yes: ship command, fast gate, CI, green-only deploy. Not the local full run.

## 2. The deduction formula
Score = V - C, in minutes per day.
- C = wall minutes the piece adds per day: queue + run + re-runs after its own failures (tokens where measured).
- V = incidents only this piece prevents per day x minutes one incident costs. A red trunk costs about 40 min
  (28 min blocked code ships: 94.6 h over 202 episodes, 11-10 review; plus a 10 min revert). A catch that a later layer
  also makes within 5 min is worth only that gap. A live trading defect is not priced: the last check before live always stays.
- Keep when V > C. Change when V > 0 and C can fall without losing V. Cut when V <= C and it is not the last check before live.

## 3. Scores
7-day averages (11-06 to 11-12, 243 ships, 50 timing logs) unless marked "today".

| # | Piece | C (min/day) | V (evidence) | Verdict |
|---|---|---|---|---|
| 1 | Local full suite for unknown non-live paths (fail closed) | 205 | 0: such a file cannot reach live; CI catches the rest in 4.5 min. 27 ships were `MyTradingSys/tools/live_aid`, 1 a stray root `gate.log` | CUT (falls to the fast gate) |
| 2 | Local full suite for real live-path files | 53 (one ship took 196 min) | at most 17: 3 of 5 failed, each a red trunk avoided; live safety added: none (3 later layers) | CHANGE: fast gate + execution tests |
| 3 | Fast gate (import map, 30 s budget, must-pass 3xm and 3la) | about 1 per ship | 3xm and 3la came from 19 of 26 red runs and 5 reverts | KEEP |
| 4 | CI, 15 legs, both OSes, behind the push | 0 waiting | the only thing that moves the green marker | KEEP |
| 5 | Green-only deploy, by hand, second full run on the live box | per deploy only | last check before live | KEEP |
| 6 | Gate slot queue (2 per machine) | today 381 full, 3 fast | stops the 240 s timeouts when 4-6 suites share 8 CPUs (11-10) | KEEP; cost falls to about 3 once rows 1-2 land |
| 7 | Card lint 3tl and review stamp, in gate and CI | 30 run time + reds (53 s median in every code ship) | 0 code defects; today a stamp ending in "." turned CI red | CHANGE: warn only |
| 8 | `Next:` must name an existing card | 1 refused ship today | 0 defects; the line itself is the operator's 11-04 order | CHANGE: line required, missing card warns |
| 9 | Test-list check 3gd (hand-kept list of 393 files) | 4 failed ships today, one after 81 min in the queue | 0 once the list is auto-discovered (11-10 row 11) | CUT with auto-discovery |
| 10 | PRE_REG context lint 3pc, verdict override test 3vd | seconds | operator's 11-04 order; 3vd caught lost hand corrections (revert 2832ce995) | KEEP, blocking |
| 11 | Red-CI block on the next code ship, revert in 10 min | small | stops piling work on a red trunk | KEEP |
| 12 | Admin and merge commits on trunk | 195 of 504 commits in 24 h (39 %): 92 admin, 103 merges | none for the code; each is a push that can lose a race | CHANGE (11-10 row 9) |
| 13 | Coordinator layer: plan run every 10 min, raw-to-ready cards, planner passes | tokens NOT MEASURED; 237 open operator questions nobody reads | claims stop two sessions editing one file (seconds, keep) | CHANGE later, measure one day first |
| 14 | Ship timing log | 0 | cannot say why a ship went full; `wait_s` is always 0 | FIX (below) |

Why the numbers are this bad: every desktop step runs 3-5x slower than alone (step 3xt median 1,072 s against 311 s; shard 4g
676 s against 156 s) because 8 logical CPUs sit at 100 % with a queue of 19-74. Failed ships then repeat the whole run.
The `wait_s` bug: `ship` only times the `--after` wait (sync.py ship, `wait_s`); the slot wait happens inside run_all_tests and
is counted as run time. The real wait is only in the temp `wait.log`, which keeps 200 lines and also receives rows from test runs.

## 4. Target design
| Stage | Design | Time |
|---|---|---|
| Docs, data, cards | no local gate (as today) | 10 s |
| Code off the live path, and any unknown path that no live module imports | fast gate: cheap always-steps, tests the import map reaches inside the 30 s budget, must-pass 3xm and 3la | under 2 min |
| Live path (execution, runtime, sched, src, live writers, or live code imports the change) | the same fast gate plus the 61 execution tests (17 s) and the static suite, both must-pass | under 2 min, 4 min ceiling |
| CI | unchanged: whole suite, 15 legs, both OSes, 4.5 min behind the push; card and format lints print, never fail | 0 waiting |
| Red CI | unchanged: author reverts within 10 min; two red runs block the next code ship | - |
| Deploy | unchanged: by hand, from the green marker only, full run on the live box first | - |
| Coordination | claims stay; 2-slot pool stays; `ship --full` stays for anyone who wants it by hand | - |

Expected: about 35 ships a day at 1-2 min each = 35-70 min a day, against 391 min a day now (about 85 % less).
What practical teams do is the same split: seconds-to-a-minute checks before the push, the full suite on CI, a quick revert when
trunk goes red (trunkbaseddevelopment.com: about 1 min is fast, 10 min is slow). A merge queue is the other common answer, but
GitHub offers it only to organization-owned repositories, so it is not open to this repo; 11-10 row 12 (pull-request auto-merge) stays parked.

## 5. Against the Supervisor's proposal
| Supervisor item | This review |
|---|---|
| 1. Local gate always fast, 2 min cap; full suite on CI only; deploys green-only | AGREE, two additions: live-path ships always run the execution tests and static suite locally (about 25 s); 2 min is a target, must-pass steps keep their 240 s ceiling and are never skipped |
| 2. Paperwork checks warn instead of block | AGREE for card lint, review stamp, `Next:` card name, 3gd. DIFFER for 3pc, 3vd, 3xm, 3la: they stay blocking (real catches, or the operator's own order) |
| 3. Remove the 2-slot queue | DIFFER: keep it. With no full gates in it the wait is about 3 min a day, and it is the one thing that stops load timeouts. Re-read wait.log after 7 days |
| 4. Later: trim coordinator and planner layer | AGREE in direction; no token numbers exist, so measure one day first. Start with the empty admin commits, which are measured |

## 6. Against the 11-10 review
- Row 3 (one queue per machine) was right about timeouts. Its accepted cost, "a fast gate can wait behind a full gate", was
  381 min today. The queue is fine; 45-130 min jobs do not belong in it.
- 11-10 rejected "changed-path selection in full mode" and listed "full gate mode for live-path files" as must-not-cut. Slot
  wait was not measured then, and unknown paths were not split from live paths. Today: live path is 14 % of the slow minutes
  and has three later layers. This review reverses that one item: the full suite stays mandatory before live (CI + live-box
  run), but not on the desktop before a push. The other must-not-cut items stand.

## 7. Change list (in order)
| # | Change | Saves | Risk |
|---|---|---|---|
| 1 | gate_select: `MyTradingSys/tools/` becomes a known code folder; an unknown path off the live list goes to the fast gate, not full | about 205 min/day (about 500 today) | low: cannot reach live; CI runs everything 4.5 min later |
| 2 | Live-path ships: fast gate + execution tests + static suite locally; full suite on CI only | about 53 min/day; ends the 196 min ship | medium: trunk red about 5 min more often on live-path changes (5 such ships in 7 days); live tree unaffected |
| 3 | Card lint, review stamp, `Next:` card name: warn only, out of the CI fail set | about 30 min/day run time, plus about 40 min per red avoided | low: a malformed card reaches trunk and is skipped by the planner |
| 4 | Test list becomes auto-discovery; 3gd goes | 4 failed ships today (about 95 min) | low |
| 5 | Root junk (`gate.log`, `run.out`) is never staged | 44 min per case | none |
| 6 | Timing log: real slot wait in the ship row, gate mode and reason in the ship row, test runs stop writing to wait.log | 0 now; the next review takes minutes | none |
| 7 | Route tag rides in the ship commit; no empty admin commits; no LAYERS.md regenerate per ship | about 90 pushes/day, fewer lost push races | low |
| 8 | Coordinator: measure tokens per plan run for one day, then drop the forced 10 min plan run and the raw-to-ready step for cards the operator dictated | not measured | medium: an idle worker is noticed later |

Rows 1, 3, 5, 6 are small and independent. Row 2 changes a must-not-cut item of 11-10 and needs the operator's explicit yes.
After rows 1-2, re-measure for 7 days before touching the slot queue.

## Sources
- Data: `runtime_data/gate_timing.jsonl` in 50 trees (ship_wall rows), `%TEMP%/mts_gate_slots/wait.log` (44 rows, 41 real),
  `gh run list --branch fast-track --limit 100`, `git log origin/fast-track`, gate_select.explain over each slow ship's files.
- Not measured: tokens per coordinator loop; cause of 9 slow ships whose commit could not be read (395 min); what the 5
  failed live-path full runs actually caught.
- Outside: trunkbaseddevelopment.com (committing straight to the trunk; continuous integration), GitHub merge queue
  announcement 2023-07-12 (organization-owned repositories only).
