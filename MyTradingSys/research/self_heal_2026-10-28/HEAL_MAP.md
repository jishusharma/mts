# O1 Self-heal map (2026-10-28)

One row per `mts_doctor.py` check and per hook in `.claude/settings.json`. **Last count** = `research/mts_doctor/REPORT_2026-10-27.md`.
Class (DESIGN.md O1): **HEAL** = the machine fixes it, idempotent, reversible, and it touches no git history, live tree, runtime data or
others' uncommitted files. **CARD** = file or refresh one card, no duplicate. **OPERATOR** = only money, mainnet, going private,
deleting data or the live tree. A heal runs from a doctor run or `sync.py`, never a timer (SCHEDULING_POLICY.md).

## Doctor checks

| check | symptom (last count 10-27) | class | heal / action | trigger | test |
|---|---|---|---|---|---|
| STALE-CLAIMS | 58 claims over 24 h (limit 5) | **HEAL** | release a stale claim only when its work is already shipped (card in `done/shipped/released`, or the claim host's branch shows 0 commits ahead of trunk via `git cherry`); a fresh or unshipped claim stays with its owner | `mts_doctor.py --heal` | `test_mts_doctor_heal.py::test_heal_releases_a_stale_claim_whose_card_is_done` + the 4 claim tests |
| BROADCAST | 8 HIGH pending on jis-laptop (43-49 h, never acked) | **HEAL** | park a HIGH that a host with no session has sat on past 48 h (`expired` ack with the reason in the note), so `mts_signal.pending` drops it and the check reads OK; a host still seen in 24 h is left alone (its session may still ack) | `mts_doctor.py --heal` | `test_mts_doctor_heal.py::test_heal_expires_a_broadcast_pending_longer_than_its_window` + `test_expired_ack_quits_the_pending_loop` |
| HOOK-REG | main checkout 243 commits behind trunk (limit 50) | **HEAL** | print ONE exact recovery command (`git -C <main> pull --ff-only`, or `merge` when diverged) and name which hook copy is in use; a heal never moves the main checkout (shared session state / others' uncommitted work) | `mts_doctor.py --heal` | `test_mts_doctor_heal.py::test_heal_reports_one_ff_command_when_the_main_checkout_is_behind` + diverged + live-tree |
| HOOKS (Part 1) | 0 hook files differ from trunk | **HEAL** | same as HOOK-REG: the main-checkout heal prints the ff command; the hook copy is the main checkout's `.claude/settings.json` | `mts_doctor.py --heal` | covered by the HOOK-REG tests |
| CI-REVERT | 3 reds took 18/10/27 min to green (limit 10); trunk red since 66990cb0 | **CARD** | auto-revert a red trunk commit within 10 min — touches fast-track git history, so it is not a safe heal; file a SONNET card (twins checked: none) | `ci_watch.py` hook + 10 min timer in CLAUDE.md | — (card `ci-auto-revert-red-trunk`) |
| SIZE-HEADROOM | SURFACE_POLICY.md 3997/4096, builder.md 1474/1500, eagle_eyes.md 7067/7100 | **CARD** | move detail to a system/ doc (never raise the cap); doc edits are not idempotent-safe auto-heals | `mts_doctor.py` + a size-cap card | `test_integrity.py` / `test_role_budget.py` |
| WAITING-ON-OPERATOR | 5 cards open on the operator | **OPERATOR** | decide on the default and continue; a heal must not decide the operator's call | operator | — |
| DISK | OK (83 GB free) | **OPERATOR** | `c_drive_guard.py` + `declutter_backups.py --apply` (machine drive) when it WARNs | `c_drive_guard.py` hook | `test_c_drive_guard.py` |
| SHIP-TIME | unavailable on this machine (gate_timing.jsonl missing) | **OPERATOR** | no finding: a machine that has not recorded a ship; runs `record_ship_timing` on its next ship | `sync.py` / `run_all_tests.py` | `test_ship_time_guard.py` |
| CONTEXT-GAP | OK (1 row, no rise) | **CARD** | when the median unnamed-reads rises, refresh the start-prompt guidance | `context_gap.py measure` | `test_context_gap.py` |
| SCRATCH-TRACKED | OK | **CARD** | `git rm` the tracked scratch/ship-log (one-off commit, public-repo rule) | `mts_doctor.py` | `test_scratch*` |
| CONFLICT-OPEN | OK (1 open, limit 3) | **OPERATOR** | the operator picks the winner of a bug-conflict card, then the loser is fixed | operator | `test_tasks_conflict.py` |
| DEAD-REF / DUPLICATE / CARD / DUP-CARD / MEMORY / SKILL (Part 1) | 12 / 5 / 17 / 6 / 0 / 0 | **CARD** | per-report doc/card fixes (dedupe, refresh, drop the ref) — not a recurring safe auto-fix | `mts_doctor.py` | `test_mts_doctor.py` |

## Hooks in `.claude/settings.json` (18 registrations, 9 scripts)

| hook | event(s) | symptom it leaves | class | action | trigger | test |
|---|---|---|---|---|---|---|
| `trunk_lag.py` | SessionStart, UserPromptSubmit | a session starts on a lagging branch; feeds HOOK-REG | **HEAL** | the main-checkout heal prints the ff command to close the gap | hook + `--heal` | `test_trunk_lag.py` |
| `mts_signal.py` | SessionStart, UserPromptSubmit, PostToolUse(Bash), Stop | BROADCAST WARN pile-up (never-acked HIGHs) | **HEAL** | the broadcast-expire heal parks an unackable HIGH with the reason | hook + `--heal` | `test_mts_signal.py` + `test_mts_doctor_heal.py` |
| `ci_watch.py` | SessionStart, UserPromptSubmit | CI-REVERT WARN (red trunk not reverted in 10 min) | **CARD** | auto-revert card (touches git history) | hook | `test_ci_watch.py` |
| `c_drive_guard.py` | SessionStart | DISK WARN | **OPERATOR** | drive cleanup on the machine | hook | `test_c_drive_guard.py` |
| `shot.py` | SessionStart, UserPromptSubmit | no recent finding (screenshot capture) | **OPERATOR** | disk/data capture, machine choice | hook | — |
| `role_loader.py` | SessionStart, UserPromptSubmit | role banner / mis-load | **CARD** | a role-budget or loader card | hook | `test_role_budget.py` |
| `preship.py` | PostToolUse(Write\|Edit), PreToolUse(Bash) | a pre-ship hook gate misfires | **CARD** | a preship card | hook | `test_preship.py` |
| `usage_reminder.py` | PostToolUse(Agent\|Task\|Workflow), PreToolUse | a budget over-usage | **OPERATOR** | budget is an operator call | hook | `test_usage_reminder.py` |
| `stop_guard.py` | Stop | a stop is held with unshipped work | **CARD** | a stop-guard card | hook | `test_stop_guard.py` |

## Built this run (O1 top-3, all HEAL, all test-failed on pre-change code)

1. **STALE-CLAIMS** → `heal_release_shipped_claims` (release a stale claim whose work is shipped).
2. **BROADCAST** → `heal_expire_unackable_broadcasts` (park an unackable HIGH with the reason; terminal `expired` ack state in `mts_signal.py`).
3. **HOOK-REG / main checkout** → `heal_main_checkout` (print one exact recovery command + the hook copy in use; never moves the shared main checkout).

Run them: `python scripts/dev/mts_doctor.py --heal` (dry run, names the actions + writes `heal_log.jsonl`), `--apply` makes the
release/park real. The apply path is fail-soft: a lost push race (the `claims` branch is hot) defers that one item for the next run
instead of crashing the whole heal (idempotent retry).
