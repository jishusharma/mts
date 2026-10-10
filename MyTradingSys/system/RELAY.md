# RELAY - how one session starts the next with no operator input (operator ask 2026-10-10)

Why: a long task in one session re-reads a growing context every turn. A short session that commits, writes the
handoff and hands over to a fresh session costs far less (SHORT SESSIONS rule in CLAUDE.md). This makes the hand-over automatic.

## Pieces
| Piece | Role |
|---|---|
| `system/NEXT_SESSION.md` | the handoff (committed, so every machine/account sees it). Carries a header `<!-- relay: go\|stop depth=N id=xxxx -->` |
| `scripts/sched/relay.py` | `handoff` stamps the header, `gate` decides GO/STOP and names the task to fire |
| App scheduled tasks `mts-relay-a`, `mts-relay-b` | ad-hoc (no schedule). Each run = a new App session with the relay prompt. Alternate by depth parity: a task cannot be re-run while its own run is in progress |
| `~/.claude/mts-relay-stop`, `-lock.json`, `-log.jsonl` | per-host stop flag, 20-minute double-launch lock, event log |

## The loop (every relay session)
1. Worktree from `origin/fast-track` (never the live tree), `sync.py start`, read the header id as STARTED_ID.
2. Do ONE task from NEXT_SESSION.md (claim, work, tests, commit, `sync.py ship`, `sync.py release`).
3. Overwrite NEXT_SESSION.md (queue, state, last commit). Then `python scripts/sched/relay.py handoff --file MyTradingSys/system/NEXT_SESSION.md --go`
   (more work, no operator question pending, no RED) or `--stop "<reason>"`. Commit and `sync.py ship`; `sync.py where` clean.
4. `python scripts/sched/relay.py gate --file ... --started-id <STARTED_ID>`. GO line names the task: fire it with the
   `run_scheduled_task` tool (load via ToolSearch). STOP: one line with the reason, end.

## Brakes (all fail closed)
- no header, header says stop, or the id did not change (the handoff was not rewritten: would replay the same task) -> STOP
- depth cap 6 chain links counted from the chain base (`handoff --reset-depth`, or `kick`, which records the base); a runaway chain is bounded
- operator: `python scripts/sched/relay.py stop "<why>"` halts every host-local chain at its next gate; `... resume` clears it
- a session that hits a blocker, RED hygiene it cannot fix, or an operator decision it needs writes `--stop` with the reason
- the lock is keyed by handoff id (2026-10-10): the same id launched twice = double fire = STOP, a new id is always allowed (the old 20-minute clock killed the chain when a short session handed over after 15 min); no relay for live-path/Java restarts (those stay desk tasks)
- App scheduled tasks run only while the Claude app is open; if it is closed the task runs on next launch

## Operator controls
Start the chain: any session (or the operator) runs `handoff --go --reset-depth` then the gate and fires `mts-relay-a`.
Stop it: `relay.py stop "<why>"`. Look: `relay.py status --file MyTradingSys/system/NEXT_SESSION.md`; log `~/.claude/mts-relay-log.jsonl`.

## Dispatcher (operator ask 2026-10-10: "a scheduled worker who starts the Sonnet agent to pick up the tasks asap")
Nothing used to START a chain except a session or the operator, so tasks sat. App scheduled task `mts-dispatcher` (every 30 min,
App must be open) is a timer, not a builder: it runs `python scripts/sched/relay.py kick` (reads the handoff from origin/fast-track),
on `KICK task=mts-relay-a|b` it runs that task, and when the Control Room Inbox has an item with status `new` it runs `mts-control-room`.
`kick` prints IDLE (exit 1) when: stop flag, no header, header says stop, any launch under 45 min ago (chain is moving), or the same
handoff id launched under 3 h ago (a session is on it; after 3 h a retry fires, claims stop a double). Log: `~/.claude/mts-relay-log.jsonl`
(`kick` / `idle` events). Its model is the App default; to make it Haiku set the model in the task's settings (the task tool cannot).
Stop everything: `relay.py stop "<why>"` (the dispatcher honours the flag).
