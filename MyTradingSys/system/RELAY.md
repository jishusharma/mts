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
3. Overwrite NEXT_SESSION.md (queue, state, last commit). Build its TASK list from `python scripts/dev/tasks.py next --n 3` (each card's `brief` is the task text);
   no ready card, or `tasks.py status` says REFINE_NEEDED: the next task is the refiner session (TASK_REFINEMENT.md), never a vague builder task. Found follow-up work this session: `tasks.py new`. Then `python scripts/sched/relay.py handoff --file MyTradingSys/system/NEXT_SESSION.md --go`
   (more work, no operator question pending, no RED) or `--stop "<reason>"`; exit 2 = list failed the Task list standard below, fix and rerun. Commit and `sync.py ship`; `sync.py where` clean.
4. `python scripts/sched/relay.py gate --file ... --started-id <STARTED_ID>`. GO line names the task: fire it with the
   `run_scheduled_task` tool (load via ToolSearch). STOP: one line with the reason, end.

## Task list standard (operator 2026-10-10: "the tasks must be curated and scoped")
The list is the product: the chain runs exactly what it says. `relay.py handoff` runs `relay.py lint` and REFUSES (exit 2, file untouched) a bad list;
fix the list, run handoff again. Rules (code: scripts/sched/handoff_lint.py, tests: tests/test_relay.py LintTest):
- Prompt block <= 30 lines; no restated hard rule or state (CLAUDE.md and STATUS.md carry them).
- Tasks are `   Qn. <what>` lines. One task = one session (Sonnet, <= 15 tool turns, <= 6 lines): split anything bigger, e.g. one screenshot SET, one pre-registration.
- Every open task has `DONE when: <something a reviewer can observe>`, names the exact item (no "next open item", "follow-ups", "as needed", "etc."),
  and every path it names exists on origin. Output files that do not exist yet belong to an earlier task; the later one starts `Qn. (after Qm ...)`.
- A finished task is rewritten `Qn. DONE ...`. `--go` needs at least one open unblocked task; `--stop` is refused while one exists, so "queue empty" cannot be
  written while work waits. All tasks blocked: add the unblocking task (desk post, Control Room decision) first, then stop naming each blocker.
- Curating when the list runs low: read STATUS.md, `shot.py status`, `desk.py list --all`, items/INDEX.md and Control Room; cut each candidate to one
  session with a finish line BEFORE writing it. A candidate you cannot scope in one session becomes a scoping task ("write the next item as Qn").
- Host tag: `   Qn. host=JIS-NB <what>` (a machine name or `any`; absent = any). `kick` lints the committed handoff for its own host and prints
  `IDLE no unblocked task for host <name>` when every open task belongs to another host, so no session is launched just to find nothing runnable.
  `handoff` and `lint` ignore the host unless `--host` is given (a NUC session must still be able to hand a go to NB). The tag is not a model
  tag: OPUS-only work stays `(after ...)`.
- `python scripts/sched/relay.py lint --file MyTradingSys/system/NEXT_SESSION.md [--want stop]` checks without writing; it also fails when the file is over the size cap (12288 bytes), which `handoff` would otherwise only meet as a refusal.
- `relay.py begin` takes the first ready card of a builder lane (`tasks.CODE_LANES` without OPUS: HAIKU, SONNET) that no open claim holds; `tasks.py next` hides claimed cards too (`--all` shows them with the claimant).

## Turn meter (2026-10-14: the relay only saves tokens if sessions hand over)
The 15 tool / 5 operator turn cap is a hook, not prose: `scripts/dev/turn_meter.py` (PostToolUse, UserPromptSubmit, SessionStart in
.claude/settings.json) injects the hand-off instruction at the cap and every 5 tool turns after; a compact or clear resets the count.
Operator threads get the same nudge (seen 2026-10-14: one thread at 625k tokens re-read per turn). `turn_meter.py status` lists them.

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

## Queue awareness and lane routing (operator 2026-10-14: "relay running continuously, aware of how many tasks are queued, GPT and DSA for as much as possible")
The dispatcher ticks every 10 minutes (the App never overlaps two runs of one task), so a tick must be cheap and must know what is waiting.
- **QUEUE line.** `relay.py status --file MyTradingSys/system/NEXT_SESSION.md [--host H]` prints it, and `kick` prints it after every KICK/IDLE:
  `QUEUE total=6 runnable=0 | waiting: host=JIS-NUC 1, operator/JIS 0, DSA desk row 1, other blocked 1 | lane CODEX 0, lane DSA 0 | DONE 3 | look=0 | for JIS-NB`.
  Buckets are exclusive, parsed by `handoff_lint.parse_tasks` (the same parser lint uses), first match wins: DONE; `(after ...)` blocked, split by its text into
  operator/JIS (operator, JIS, decision, Control Room), DSA desk row (`desk row` or DSA), other blocked (a date, another task); open `lane=` tasks;
  open tasks of another host; the rest = `runnable` for this host (what a Claude session can take now).
- **Lane tag.** `Qn. lane=CODEX ...` (GPT / Codex Layer Lab on JIS-NUC, LAYER_LAB.md) or `Qn. lane=DSA ...` (AI Bridge run-and-report, DSA_DELEGATION.md), before or after
  `host=`. Use it only for work the lane can finish alone: DSA = copy-ready commands, an observable result; CODEX = an audit/build/run card. A bad lane value fails lint.
- **`relay.py route`** (T0, the dispatcher runs it before `kick`; `--file F` or `--git-ref REF:PATH`, `--root R`, `--no-ship`): for every open lane task not yet posted it files
  a desk row `--target DSA` (`desk.py` format) or a raw lane-CODEX task card (`tasks.py` format; the refiner sets kind/size/scope, then `tasks.py check`), each carrying
  `relay_key` = `<qn>-<hash of the task text>`. Posted once: the key is recorded in `~/.claude/mts-relay-routed.json` (host-local) AND is on the row/card itself (shipped via
  `sync.py ship`, so the other host sees it and answers `exists`). A failed post is not recorded and retries next tick. Edit the task text and it is a new key: it posts again.
- **Kick skips lane work.** A handoff whose open tasks are all lane tasks gives `IDLE no Claude-runnable task: open work is on lane CODEX (...) / DSA (...)`: no Claude session is paid for it.
- **Results come back as `look=`.** When the row is `done`/`failed` (or the card `done`) and its Qn is still open in the handoff, QUEUE shows `look=1 [Q60 desk done]` and `kick` wakes a
  session: it reads the row (`desk.py list --all`) or card (`tasks.py brief <id>`), spot-checks ONE claim, and rewrites the Qn as `DONE ...` (that clears the look).
  `codex_look=N` (JIS-NUC only) counts the lines under `codex_run.py status` NEEDS A LOOK; it is information, it does not wake kick.
- Dispatcher prompt: step 1 copies `relay.py` AND `handoff_lint.py` from origin to `$TEMP/mts_relay/`, runs `route`, then `kick`; the final `dispatcher:` line carries `route=` and `queue=`. Idle-tick economy is unchanged.
- Writing the task list: when curating, tag every task a lane can do alone (a re-run of an existing script, an inventory, a CODEX audit card) instead of leaving it for a Claude session.
- **No run row = not a peer (2026-10-14).** `kick --peer-quiet-min` waits only for a host named in a `relay_runs.jsonl` row. A handoff whose header was edited by hand (the Q64 tidy run wrote id 5f4d4fbe without a row) is owner `unknown` and no longer stalls this host for 90 min. Always write the header with `relay.py handoff`, never by hand: it also writes the row.
- **Older handoff_lint (2026-10-14).** The QUEUE code reads a `lane=` tag itself when the tree's `handoff_lint.py` predates it, and `status` prints `QUEUE ? (...)` instead of crashing, so a copied relay.py can never take the dispatcher down.
