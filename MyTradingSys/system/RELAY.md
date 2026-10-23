# RELAY - hand-over rules (the relay loop itself is RETIRED)

> RETIRED 2026-10-17 (SCHEDULING_POLICY.md): nothing runs `tick`/`kick`, no dispatcher task exists; the operator or a coordinator starts every session.
> STILL LIVE: **Task list standard** (`relay.py handoff`/`lint` check NEXT_SESSION.md). Pieces, The loop, Brakes, Tick and queue = how the retired loop worked, reference only. History: `archive/relay_2026-10-15/`.

## Pieces (retired loop)
| Piece | Role |
|---|---|
| `system/NEXT_SESSION.md` | the handoff, committed; header `<!-- relay: go\|stop depth=N id=xxxx -->`, its first fenced block is the task list |
| `scripts/sched/relay.py` | `tick begin brief handoff unlock lint route kick status stop resume` |
| App task `mts-dispatcher` (RETIRED, deleted) | was cron `*/10 * * * *`, Haiku; stub `relay_prompts/mts-dispatcher.SKILL.md`. On KICK it was the relay session (B164) |

## The loop (retired; `relay_prompts/relay_session.md`)
`tick` (`TICK NOOP` = reply, stop) -> `begin` (worktree `../mts-relay`, claim, brief) -> ONE task in <= 15 tool turns -> edit the NEXT_SESSION.md block -> `handoff --go` (or `--stop "<reason>"`) -> `sync.py ship`, `where` clean -> `unlock` (not after `--stop`).
Next tasks come from `python scripts/dev/tasks.py next --n 3` (a card's `brief` is the task text). No ready card, or `tasks.py status` says REFINE_NEEDED: the next task is the refiner (TASK_REFINEMENT.md), never a vague builder task.

## Task list standard (operator 2026-10-10: "the tasks must be curated and scoped")
`relay.py handoff` runs `relay.py lint` and REFUSES (exit 2, file untouched) a bad list. Code: sched/handoff_lint.py.
- Block <= 30 lines, no restated hard rule or state (CLAUDE.md and STATUS.md carry them); file <= 12288 bytes (old `## ` sections move to `handoff_history/`: edit the block, never append `## Update`).
- Tasks are `   Qn. <what>` lines. One task = one session (<= 15 tool turns, <= 6 lines): split anything bigger.
- Every open task has `DONE when: <something a reviewer can observe>`, names the exact item (lint rejects "next open item", "as needed", "etc.") and every path it names exists on origin; a task that needs an earlier task's output starts `Qn. (after Qm ...)`.
- A finished task is rewritten `Qn. DONE ...`. `--go` needs one open unblocked task; `--stop` is refused while one exists. All blocked: add the unblocking task first, then `--stop` naming each blocker.
- Curating when the list runs low: read STATUS.md, `shot.py status`, `desk.py list --all`, items/INDEX.md and Control Room; cut each candidate to one session with a finish line BEFORE writing it. A candidate you cannot scope in one session becomes a scoping task (write the next item as Qn).
- Tags right after `Qn.`, either order, one of each: `host=<machine|any>` (absent = any; `handoff`/`lint` ignore it unless `--host`; `kick` says `IDLE no unblocked task for host X` when every open task is another host's; OPUS-only work stays `(after ...)`) and `lane=CODEX` (GPT / Codex Layer Lab, JIS-NUC) or `lane=DSA` (AI Bridge). Operator 2026-10-14, "GPT and DSA for as much as possible": when curating, tag every task a lane can do alone (a re-run of an existing script, an inventory, a CODEX audit card) instead of leaving it for a Claude session. A bad lane value fails lint.
- `relay.py lint --file <handoff> [--want stop]` checks without writing. Write the header with `handoff` only: it also writes the `relay_runs.jsonl` row.
- `begin` takes a HAIKU or SONNET card (`tasks.CODE_LANES` minus OPUS) that no open claim holds (`tasks.py next` hides claimed cards; `--all` shows them).

## Brakes (retired loop; all fail closed)
- no header, header says stop, no task this host can run, or only lane work left -> `kick` IDLE; `handoff --stop` ends a chain
- a launch under 45 min old, or the same handoff id launched under 1 h ago (a session is on it) -> IDLE; `unlock` frees it; after 1 h an unrewritten id retries
- operator: `relay.py stop "<why>"` halts every tick on that host, `relay.py resume` clears it; log `~/.claude/mts-relay-log.jsonl`
- a session that hits a blocker, RED hygiene it cannot fix, or an operator decision it needs writes `--stop` with the reason; no relay for live-path/Java restarts (desk tasks)

## Tick and queue (retired loop, operator 2026-10-14)
`relay.py tick` was the idle path: fetch, `route`, `kick`, the QUEUE line, prompt drift check, hourly refiner status, daily housekeeping; ONE line out, `TICK NOOP | <why> | ..` or `TICK KICK ..`.
- **QUEUE line** (tick, `kick`, `status`): task counts by why they wait (exclusive buckets, first match wins, `handoff_lint.parse_tasks`): DONE; `(after ..)` blocked; open `lane=` tasks; another host's; the rest = `runnable` here.
- **`route`** files each open lane task once, as a desk row `--target DSA` or a raw lane-CODEX card, keyed `relay_key` = `<qn>-<hash of the text>` (edited text = new key; the other host answers `exists`).
- **Results come back as `look=`**: the row is `done`/`failed` (or the card `done`) and its Qn is still open -> `look=1 [Q60 desk done]` and `kick` wakes a session: relay_session.md makes that read its task: row (`desk.py list --all`) or card (`tasks.py brief <id>`), spot-check ONE claim, rewrite the Qn as `DONE ...`. `codex_look=N` (JIS-NUC) counts `codex_run.py status` NEEDS A LOOK lines: information only, it does not wake kick.
- **Peers**: `kick --peer-quiet-min N` waited only for a host named in a `relay_runs.jsonl` row (TWO_HOST.md).
