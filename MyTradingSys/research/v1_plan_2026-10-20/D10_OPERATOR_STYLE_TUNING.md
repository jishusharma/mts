# D10. Tuned to the operator's way of working (2026-10-20, after the operator's note on D1-D9)

Operator's ask, in his words: minimum work, lean architecture, minimalistic approach, fast-track solutions built in,
optimisation and economy, execution performance, high accuracy with consistency, faster scripts, a multi-device
multi-login coordinated system, and no gates that do not belong on a personal ambitious project.

## What his commands and rules say (RESULT, from USER.md and OPERATOR_DECISIONS.md operator notes)
- Runs PowerShell by hand; batch commands, one block one task; reads batched, never one per turn.
- "Standard operations done without asking"; "Any gate Claude needs, Claude builds"; "Commit and push on the operator's word".
- Dislikes rule proliferation ("one line in apparatus_fixes.md and move on"), invented caps and budgets, premature done, re-asking.
- Decisions on record: "remove completely - no more schedulers in any device"; "do everything end to end, do not wait";
  "no stale trees left behind, lower cost, same performance"; "we need to close things"; "all artifacts associated with
  the jishu.sharma a/c (main GitHub)"; "flexibility to run any a/c on any machine".

## What the process costs today (RESULT, measured on this session's two ships, 2026-10-20)
| Item | Number | Source |
|---|---|---|
| Docs-only ship, wall time | 1,025 s and 1,027 s (17 min each) for 12 markdown files | ship logs, "Gate mode: docs (7 steps)" |
| of which targeted pytest (step 4t) | 985 s and 870 s: test_cicd_run, test_gate_budget, test_lease, test_relay, test_relay_queue, none of which read the files changed | same logs; the same 108 tests pass in 305 s when run alone |
| of which task-card lint (step 3tl) | 107 s and 128 s, on a change that touched no card | same |
| First ship failed | the word STALE in a hand-over sentence tripped a banner regex; 17 min lost, then 17 min to re-ship | test_integrity.py:138 |
| Trunk commits since 2026-10-13 | 3,772: Merge 1,239 (33 %), claim 538 (14 %), release 477 (13 %) = 60 % plumbing | git log origin/fast-track --since 2026-10-13 |
| Process tooling | sync.py 1,321 lines, run_all_tests.py 1,081, tasks.py 1,389 = 3,791 lines, plus 60 gate steps | wc -l |
| CI | runs the full suite on every push anyway; fast-track is not branch-protected; green/fast-track is the deploy pointer | ci.yml, TRAFFIC_BUSTERS B9 |

So the local gate duplicates CI for everything except the live path, and it costs 17 minutes per docs ship on the
machine that also runs the testnet. That is the gate that does not belong on this project.

## The tuning (six changes; each replaces rules, none adds one)
1. Gate by path, three tiers, decided by gate_select from the diff (the selector exists; only its table changes):
   - docs, research, cards, pages: NO local gate. Commit, fetch, merge, push. CI is the gate; a red run opens the one
     ci-<sha> card that already exists. EXPECT: docs ship 17 min -> under 1 min.
   - code outside the live path: only the test files that import the changed module, 240 s cap, then push. CI runs the rest.
   - live path (execution/, live writers, deploy): today's quick gate, unchanged. Accuracy stays where money is.
2. Claims leave git. A claim is a line in .mts_claims/<slug> pushed to a side branch (same mechanism as the lane-heartbeat
   side branch, B17), or skipped entirely for new-file work (B16). No claim or release commit ever lands on trunk.
   EXPECT: 27 % of trunk commits gone, and with them most of the merge-commit races (33 %).
3. One ship per task (B3) becomes the only way sync.py ship runs: a second ship from the same tree within 10 minutes
   is refused with the reason printed. Hand-over is a commit, not a ship.
4. Card lint runs only when the diff touches system/tasks/; the banner regex and size caps run only on files in the
   diff. A doc that no one changed cannot fail a ship.
5. Turn caps apply to unattended workers, not to a session the operator is driving. The operator's own words end a session.
6. Freeze the process tooling: no new gate step, no new lint, no new rule doc until v1 ships. A failure gets one line in
   apparatus_fixes.md (USER.md) and, if it repeats, one test. Lines of process code are a measure on STATUS.md, read weekly.

## Multi-device, multi-login, coordinated (the operating model, one paragraph)
Machines hold trees; logins hold budget; cards hold work. Any login opens any machine, runs sync.py start <slug> (a
worktree), takes the next ready card, commits locally per work unit (cheap, no gate), ships once at the end (tier by path),
and leaves a hand-over block of at most 40 lines. One super session per machine at a time is the coordinator; it dispatches
from the one card list and stops when the operator says. No scheduler, no routine, no login-named lane. Artifacts publish
from jishu.sharma only. Check-in rhythm: local commit every work unit, ship per task, trunk read by STATUS.md.

## What stays strict (accuracy with consistency)
Fee-net OOS with CI > 0 before anything trades; holdout read once; pre-registration before any outcome read; live-path
tests that fail on old code; CI full suite on every push; deploy only from green/fast-track; testnet only. These are the
gates that make the number true. Everything else was a gate on paperwork.

## Measures (replace D8's table; read weekly from STATUS.md)
| Measure | Today | Target |
|---|---|---|
| docs ship wall time | 17 min | < 1 min |
| code ship wall time (non-live) | unmeasured | < 5 min |
| plumbing share of trunk commits | 60 % | < 10 % |
| lines of process tooling (sync, tasks, run_all_tests) | 3,791 | not growing |
| ready cards | 48 | <= 15 |

## Decisions added
q-v1-gate-tiers, q-v1-claims-off-git, q-v1-turn-caps (DECISIONS_PROPOSED.md). Defaults: yes. One S0 card implements
changes 1-4 in gate_select and sync.py with tests that fail on the old code; change 5 is a line in WORKERS.md;
change 6 is a line in CLAUDE.md.
