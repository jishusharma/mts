# DEBUGGING - one place to start when something in the dev system goes wrong

Symptom -> first command (read-only) -> where the state lives -> owner. Run from your own worktree. Every command here
only reads; a fix goes through a card or `sync.py ship`, never by hand on the live tree. Map of what calls what:
ARCHITECTURE.md. Test `MyTradingSys/tests/docs/test_debugging_spine.py` fails when a script or path named here is gone.

## 0. Do this first (30 s)
1. `python scripts/dev/mts_doctor.py --hours 24`: AI health (dead refs, duplicates, cards, skills, boot cost).
2. `python scripts/dev/ci_watch.py`: is CI red? A red line means fix CI first (`ci-<sha>` card; `scripts/dev/ci_red_card.py --apply` files it).
3. `python scripts/dev/sync.py news 24`: what shipped in the last day (feature + Result line per commit).
4. `python scripts/dev/sync.py health`: stale or overlapping claims, orphan worktrees, branches never shipped.

## 1. Ship and gate
| Symptom | Command | State | Owner |
|---|---|---|---|
| ship refused / gate red | re-read the full `sync.py ship` output; `python scripts/dev/run_all_tests.py --quick` | `runtime_data/gate_timing.jsonl` (per step), gate record in the worktree git dir | the shipping session |
| gate picked the wrong tests | `python scripts/dev/gate_select.py`; `python scripts/dev/gate_impact.py` | GATE_SPEED.md | MTS_Doctor |
| CI red on fast-track | `python scripts/dev/ci_watch.py`; `python scripts/dev/ci_red_card.py` (dry run; `--apply` files the card) | `~/.claude/mts-ci-watch.json` | whoever takes the `ci-<sha>` card |
| work seems lost | `python scripts/dev/sync.py where --all` | every worktree | the session that made it |
| claim blocks you | `python scripts/dev/sync.py claims` | `MyTradingSys/system/claims/` | claim holder; `sync.py release <slug>` |
| new code is not wired | `python scripts/dev/wiring_scan.py --check` | `MyTradingSys/system/wiring_registry.json` | the shipping session |

## 2. Hooks (.claude/settings.json)
A hook never blocks the turn. shot, turn_meter and mts_signal log their own errors to a `hook_errors.log` in their state folder;
the others fail silently, so run it by hand to see the error: `echo {} | python scripts/dev/<script> hook` (it may bump that hook's own counter).
| Hook | Script | State |
|---|---|---|
| role not loaded / wrong role | `python scripts/dev/role_loader.py check`, then `verify` | `%TEMP%/mts_roles/<session>.json`; roles from origin/fast-track |
| turn count wrong | `scripts/dev/turn_meter.py` | `~/.claude/mts-turn-meter/` (`hook_errors.log`) |
| stop refused | `scripts/dev/stop_guard.py` | `~/.claude/mts-stop-guard.json` |
| stop refused: pre-run items for the operator | `scripts/dev/prereq_guard.py` (`tasks.py need`) | `~/.claude/mts-prereq-guard.json` |
| stop refused: reply ends asking the operator's leave ("want me to") | `scripts/dev/offer_guard.py` (`MTS_OFFER_GUARD=off`) | `~/.claude/mts-offer-guard.json` |
| commit denied / edit note `PRESHIP` | `python scripts/dev/preship.py check` (rules: its RULES table) | `~/.claude/mts-preship-*.json` |
| broadcast nobody reacted to | `python scripts/dev/mts_signal.py acks [<id>]` (hosts vs none/told/done); resend with `broadcast "<text>" --prio high --cmd "<command>"` | branch `mts-signals` | the sending session |
| signal / git windows flash | `scripts/dev/mts_signal.py` | `~/.claude/mts-signals`, branch `mts-signals` |
| screenshot not picked up | `scripts/dev/shot.py` | `~/.claude/uploads/manifest.jsonl` |
| worker spawn refused | `scripts/dev/model_guard.py` | WORKERS.md (the rule it enforces) |
| C: drive warning | `scripts/dev/c_drive_guard.py` | none |

## 3. Cards, desk, lanes
| Symptom | Command | State | Owner |
|---|---|---|---|
| card will not dispatch | `python scripts/dev/tasks.py brief <id>`; `python scripts/dev/tasks.py dispatch` (`check` is not read-only: it can demote) (ranked snapshot, read-only) | `MyTradingSys/system/tasks/<id>.json` | Session_Planner |
| what did X lead to | `python scripts/dev/trace.py <study or card or layer>` | research/, tasks/, layer_index.json | none (report only) |
| desk row unanswered | `python scripts/dev/desk.py list`; `python scripts/dev/desk.py sweep` (dry-run proposals) | `MyTradingSys/system/desk_queue/` | the row's target |
| GPT lab idle or down | `python scripts/dev/codex_run.py status`; `python scripts/dev/lane_health.py status` | CODEX_START.md, LAYER_LAB.md | Lab_Guy |
| DSA bridge fault | `python scripts/dev/aibridge_health.py` | AIBRIDGE_LANE.md | operator (bridge limits) |

## 4. Live testnet system (read only: never stop, start, deploy or touch HALT)
| Symptom | Command | State | Owner |
|---|---|---|---|
| is live healthy | `python scripts/dev/live_mirror.py brief` (quote `mirror@<utc>`) | LIVE_MIRROR.md | Supervisor |
| recorder stopped / process dropped | `python scripts/sched/check_live_health.py` | `runtime_data/live_runner.log` | Supervisor |
| deploy did not land | read `MyTradingSys/runtime/sched/auto_deploy_last.json` | DEPLOY_RUNBOOK.md | desk row `--target JIS-NB` or the coordinator deploy (hand deploy) |
| trading halted | read `MyTradingSys/execution/HALT` (never edit) | `MyTradingSys/execution/halt_history/` | operator |

## 5. Cost and waste
| Symptom | Command | Owner |
|---|---|---|
| sessions too expensive | `python scripts/dev/token_audit.py`; `python scripts/dev/worker_cost_report.py` | MTS_Doctor |
| coordination overhead | `python scripts/dev/traffic_report.py` | Traffic controller |
| repo health score | `python scripts/dev/health_audit.py` | MTS_Doctor |
| boot cost per role | `python scripts/dev/mts_doctor.py` (BOOT-COST rows); ARCHITECTURE.md section 3 | MTS_Doctor |

## 6. Escalation
Anything off: report -> independent audit -> fix (CLAUDE.md). A fault you cannot fix becomes a card
(`python scripts/dev/tasks.py new "<title>"`) with the symptom, the command you ran and its full output path.
