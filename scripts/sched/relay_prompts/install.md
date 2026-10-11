# Relay tasks on a host: install and recover (any host, any account)

The relay is three App scheduled tasks per host. Their text is below; the logic they run is in git
(`relay_session.md`, `scripts/sched/relay.py`). Nothing is tied to an account: sign a different account into the App
and the same tasks keep working, on that account's budget. If the tasks are ever missing (new machine, App profile
reset, a sign-in that shows an empty Scheduled list) say to any session on that host:
"recreate the relay tasks from scripts/sched/relay_prompts/install.md" - it calls `create_scheduled_task` three times.

Check: `list_scheduled_tasks` shows `mts-relay-a`, `mts-relay-b`, `mts-dispatcher`.
Per-host values: PEER_QUIET_MIN and the dispatcher cron (table at the end).

## mts-relay-a and mts-relay-b (ad-hoc, no schedule, identical text)
```
MTS relay session (unattended, no operator). In the repo folder run `git fetch -q origin fast-track` then
`git show origin/fast-track:scripts/sched/relay_prompts/relay_session.md` and follow that file exactly.
If either command fails, reply with the error in one line and end.
```

## mts-dispatcher (cron per host)
```
MTS dispatcher tick (a timer, not a builder; unattended). Do exactly this, nothing else, no file reads:
1. In the repo folder, one Bash call:
   git fetch -q origin fast-track && git show origin/fast-track:scripts/sched/relay.py > "$TEMP/mts_relay_kick.py" && python "$TEMP/mts_relay_kick.py" kick --peer-quiet-min <PEER_QUIET_MIN>
2. Output starts with IDLE: reply with that line and end.
3. Output starts with KICK ... task=<name>: load mcp__scheduled-tasks__run_scheduled_task with ToolSearch, run <name>,
   reply "KICK <name>" and end.
4. Anything else: reply with the first line of the error and end.
```

## How the two hosts share one queue
- Whoever wrote the current handoff is recorded in `MyTradingSys/system/relay_runs.jsonl` (host, account, session title).
- A dispatcher stays IDLE while ANOTHER host wrote the handoff under PEER_QUIET_MIN minutes ago. When that host goes
  quiet (credits out, machine off, App closed) the other one starts the chain by itself after PEER_QUIET_MIN.
- Move the work on purpose: `python scripts/sched/relay.py stop "<why>"` on the host to rest (host-local flag),
  `... resume` to bring it back. The other host picks up after its PEER_QUIET_MIN.
- Both chains running at once is safe (claims stop double work) but spends both budgets.
- A chain that is running fires its own next session (gate); the dispatcher only starts a chain, so it can be slow.

| Host | PEER_QUIET_MIN | dispatcher cron (local time) | note |
|---|---|---|---|
| JIS-NUC | 90 | `7 * * * *` (hourly) | created 2026-10-12 |
| JIS-NB | 90 (add the flag to its kick line) | adaptive, host-local prompt | NB's own prompts: copy them here when shipped |

Find a relay chat later: `relay_runs.jsonl` gives host + account + session title; open that App, that account, search the title.
