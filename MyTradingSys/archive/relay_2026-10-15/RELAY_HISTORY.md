# RELAY history - text moved out of system/RELAY.md on 2026-10-15

RELAY.md now holds only what is true today. This file keeps the retired text verbatim (old RELAY.md line numbers in brackets), for the
record of why things are the way they are. Nothing here is an instruction. What replaced it: `relay.py tick` (one call per dispatcher
run), `relay.py begin` + `relay_prompts/relay_session.md` (the KICK ritual), `relay.py unlock` (frees the lock); `relay.py gate`, the
`mts-relay-a/b` tasks and `run_scheduled_task` launching are gone. The dispatcher prompt that ran 2026-10-14 (6644 B, never in git) is
`mts-dispatcher.SKILL.md.installed_2026-10-14` beside this file.

## The launch design that never worked unattended (old Pieces rows, loop step 4, operator start) [9-12, 20-21, 55]
| `system/NEXT_SESSION.md` | the handoff (committed, so every machine/account sees it). Carries a header `<!-- relay: go\|stop depth=N id=xxxx -->` |
| `scripts/sched/relay.py` | `handoff` stamps the header, `gate` decides GO/STOP and names the task to fire |
| App scheduled tasks `mts-relay-a`, `mts-relay-b` | ad-hoc (no schedule). Each run = a new App session with the relay prompt. Alternate by depth parity: a task cannot be re-run while its own run is in progress |
| `~/.claude/mts-relay-stop`, `-lock.json`, `-log.jsonl` | per-host stop flag, 20-minute double-launch lock, event log |
4. `python scripts/sched/relay.py gate --file ... --started-id <STARTED_ID>`. GO line names the task: fire it with the
   `run_scheduled_task` tool (load via ToolSearch). STOP: one line with the reason, end.
Start the chain: any session (or the operator) runs `handoff --go --reset-depth` then the gate and fires `mts-relay-a`.

## Old brakes that only `gate` enforced [48, 51]
- depth cap 6 chain links counted from the chain base (`handoff --reset-depth`, or `kick`, which records the base); a runaway chain is bounded
- the lock is keyed by handoff id (2026-10-10): the same id launched twice = double fire = STOP, a new id is always allowed (the old 20-minute clock killed the chain when a short session handed over after 15 min); no relay for live-path/Java restarts (those stay desk tasks)
(`kick` re-recorded the chain base on every KICK, so the depth cap never fired in the dispatcher flow; `gate` was removed 2026-10-15 and
the depth in the header is now a counter only.)

## Dispatcher (operator ask 2026-10-10: "a scheduled worker who starts the Sonnet agent to pick up the tasks asap")
Nothing used to START a chain except a session or the operator, so tasks sat. App scheduled task `mts-dispatcher` (every 30 min,
App must be open) is a timer, not a builder: it runs origin/fast-track's relay.py `kick` (copied to %TEMP%/mts_relay_kick.py with `git show`, because the live tree's relay.py lags origin and had no `kick`: B164) (reads the handoff from origin/fast-track),
on `KICK task=mts-relay-a|b` it runs that task, and when the Control Room Inbox has an item with status `new` it runs `mts-control-room`.
`kick` prints IDLE (exit 1) when: stop flag, no header, header says stop, any launch under 45 min ago (chain is moving), or the same
handoff id launched under 3 h ago (a session is on it; after 3 h a retry fires, claims stop a double). Log: `~/.claude/mts-relay-log.jsonl`
(`kick` / `idle` events). Its model is the App default; to make it Haiku set the model in the task's settings (the task tool cannot).
Stop everything: `relay.py stop "<why>"` (the dispatcher honours the flag).

## Launch never happened (B164, 2026-10-10 09:27Z -> 12:30Z)
The gate writes its lock BEFORE the App starts the next task. An unattended session could not approve `run_scheduled_task`, so
mts-relay-b never ran and the dispatcher idled 3 h on "session still on it". Fixes: `mcp__scheduled-tasks__run_scheduled_task`
is in ~/.claude/settings.json allow (host-local); STALE_H 3 -> 1; `kick` IDLE lines carry `lock=<utc> task=<id>` and the dispatcher
checks list_task_runs: no run since the lock = rescue-launch it.

### Correction 2026-10-10 12:50Z: allow rules do NOT fix it
Dispatcher runs are bypassPermissions yet `run_scheduled_task` from inside a scheduled session still needs a human click.
So no session may launch another. The cron-fired mts-dispatcher is now the worker: on KICK it runs the relay task itself and
deletes ~/.claude/mts-relay-lock.json at the end, so the next 30-min tick starts the next handoff. mts-relay-a/b remain for manual use.
Chain latency <= 30 min. Prompt is host-local (~/.claude/scheduled-tasks/mts-dispatcher/SKILL.md; backup SKILL.md.bak_20261010).

## Two hosts, any account (2026-10-12, card relay-two-host-standby)
Every host runs an `mts-dispatcher` App task that is also the relay worker; its text and the recovery steps are in `scripts/sched/relay_prompts/TWO_HOST.md`,
the session ritual in `scripts/sched/relay_prompts/relay_session.md` (hosts hold a stub that reads it from origin).
- Nothing is keyed to an account. Sign either account into either App: the tasks run on that account's budget.
- `handoff` appends host + signed-in account + session title to `system/relay_runs.jsonl` (ships with the handoff commit):
  that is where to look up which App and account holds a relay chat.
- `kick --peer-quiet-min N`: IDLE while ANOTHER host wrote the current handoff under N minutes ago; after N minutes of
  silence the other host starts the chain. Rest a host on purpose with `relay.py stop "<why>"` on it.
- `handoff` keeps NEXT_SESSION.md under 12 KB (`MTS_RELAY_MAX_BYTES`): old `## ` sections move to `system/handoff_history/<date>.md`.
  Edit the block, do not append `## Update` sections.

## Queue awareness: bullets replaced by `tick` [107, 109, 110]
- Dispatcher prompt: step 1 copies `relay.py` AND `handoff_lint.py` from origin to `$TEMP/mts_relay/`, runs `route`, then `kick`; the final `dispatcher:` line carries `route=` and `queue=`. Idle-tick economy is unchanged.
- **No run row = not a peer (2026-10-14).** `kick --peer-quiet-min` waits only for a host named in a `relay_runs.jsonl` row. A handoff whose header was edited by hand (the Q64 tidy run wrote id 5f4d4fbe without a row) is owner `unknown` and no longer stalls this host for 90 min. Always write the header with `relay.py handoff`, never by hand: it also writes the row.
- **Older handoff_lint (2026-10-14).** The QUEUE code reads a `lane=` tag itself when the tree's `handoff_lint.py` predates it, and `status` prints `QUEUE ? (...)` instead of crashing, so a copied relay.py can never take the dispatcher down.

## Standing directives condensed back into RELAY.md (review fix 2026-10-15) [32-33, 39, 90, lane tag, 106, 108]
Old text, verbatim. The directives live on in RELAY.md (Task list standard, Tick and queue); this is the unabridged wording.
- Curating when the list runs low: read STATUS.md, `shot.py status`, `desk.py list --all`, items/INDEX.md and Control Room; cut each candidate to one
  session with a finish line BEFORE writing it. A candidate you cannot scope in one session becomes a scoping task ("write the next item as Qn").
- `relay.py begin` takes the first ready card of a builder lane (`tasks.CODE_LANES` without OPUS: HAIKU, SONNET) that no open claim holds; `tasks.py next` hides claimed cards too (`--all` shows them with the claimant).
## Queue awareness and lane routing (operator 2026-10-14: "relay running continuously, aware of how many tasks are queued, GPT and DSA for as much as possible")
- **Lane tag.** `Qn. lane=CODEX ...` (GPT / Codex Layer Lab on JIS-NUC, LAYER_LAB.md) or `Qn. lane=DSA ...` (AI Bridge run-and-report, DSA_DELEGATION.md), before or after
  `host=`. Use it only for work the lane can finish alone: DSA = copy-ready commands, an observable result; CODEX = an audit/build/run card. A bad lane value fails lint.
  `codex_look=N` (JIS-NUC only) counts the lines under `codex_run.py status` NEEDS A LOOK; it is information, it does not wake kick.
- Writing the task list: when curating, tag every task a lane can do alone (a re-run of an existing script, an inventory, a CODEX audit card) instead of leaving it for a Claude session.
