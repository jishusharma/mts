# Relay on two hosts, any account: rules, install, recovery (2026-10-12)

One App scheduled task per host, `mts-dispatcher`, fired by cron. On a KICK it IS the relay session (a session may not start
another one unattended: B164). The ritual it follows is `relay_session.md` in this folder, read from origin at run time, so
the ritual is changed in git, never per host. JIS-NB's own longer prompts are the `*.SKILL.md` files here (INSTALL.md).

Nothing is tied to an account. Sign a different account into either App: the same task keeps running, on that account's
budget, and `relay_runs.jsonl` records which account each handoff came from. If the task is missing (new machine, App reset,
an empty Scheduled list after a sign-in) tell any session on that host:
"recreate mts-dispatcher from scripts/sched/relay_prompts/TWO_HOST.md" (one `create_scheduled_task` call).

## mts-dispatcher prompt (generic; JIS-NUC runs exactly this)
```
MTS dispatcher AND relay worker (unattended, no operator; a cron run needs no approval). Idle ticks must cost almost
nothing: keep reasoning and output minimal, read no file a step does not name.
1. One Bash call in the repo folder you start in:
   git fetch -q origin fast-track && git show origin/fast-track:scripts/sched/relay.py > "$TEMP/mts_relay_kick.py" && python "$TEMP/mts_relay_kick.py" kick --peer-quiet-min <PEER_QUIET_MIN>
2. Output starts with IDLE: go to step 4 with MODE=IDLE.
3. Output starts with KICK: YOU are the relay session. Run `git show origin/fast-track:scripts/sched/relay_prompts/relay_session.md`
   and follow it exactly (one task, handoff, ship, free the lock). MODE=BUSY if you handed off with --go, else IDLE.
4. Re-pace: read ~/.claude/mts-dispatch-mode (missing = IDLE). Only if MODE differs: ToolSearch
   "select:mcp__scheduled-tasks__update_scheduled_task", update taskId mts-dispatcher cronExpression
   BUSY="<BUSY_CRON>" IDLE="<IDLE_CRON>", then write MODE to that file with python. Update refused: pace=BLOCKED, leave the file.
5. Final line: `dispatcher: relay=<KICK task result|IDLE reason|ERROR text>; pace=<BUSY|IDLE|unchanged|BLOCKED>`.
Never start other scheduled tasks. Never kill processes by image name. Never touch a folder holding .mts_live.
```

## How the two hosts share one queue
- `handoff` records host + signed-in account + session title in `MyTradingSys/system/relay_runs.jsonl` (same commit).
- A dispatcher stays IDLE while ANOTHER host wrote the current handoff under PEER_QUIET_MIN minutes ago. When that host
  goes quiet (credits out, machine off, App closed) the other one picks the chain up by itself.
- Move the work on purpose: `python scripts/sched/relay.py stop "<why>"` on the host to rest (host-local flag), `resume` later.
- Budget asymmetry, CORRECTED 2026-10-12 (the earlier line here had the two accounts swapped): the account with ~26% weekly
  left until Fri 2026-10-16 is jishu.sharma, signed in on JIS-NB (operator, said in the NB App: "this one ... around 26%
  weekly remaining", "more work on the other subscription"). jishu.awgp on JIS-NUC had used 4% of its week at
  2026-10-11T19:05Z (App usage card, resets 2026-10-18). So the NUC is the primary: it passes 0 and never yields; the NB
  passes 90 and yields while the NUC keeps handing off (Q31 applied on the NB 2026-10-12).
  The primary is whichever host's signed-in account has budget: swap the two numbers when that changes.
- Self re-pacing does not work: an unattended run's `update_scheduled_task` on its own cron is refused (NUC run
  2026-10-12, `pace=BLOCKED`). Each host keeps one fixed cron; step 4 of the generic prompt is dropped on the NUC.
- Both chains at once is safe (claims stop double work) but spends both budgets.

| Host | PEER_QUIET_MIN | BUSY_CRON | IDLE_CRON | state |
|---|---|---|---|---|
| JIS-NUC | 0 (primary: account has budget) | fixed `7,37 * * * *` | same | generic prompt without step 4; first unattended run 2026-10-12 shipped one task in 6 min |
| JIS-NB | 90 (applied 2026-10-12, Q31 done) | fixed `0 7-23 * * *` | n/a (no self-pacing: a run cannot edit its own schedule) | own prompt (mts-dispatcher.SKILL.md), yields to the NUC. 2026-10-12: a tick printing `IDLE peer <host>` (any host, `unknown` = handoff without a relay_runs row) ends after step 1, skipping inbox, refiner, housekeeping (host-local SKILL.md edit). Live crons verified: mts-dispatcher `0 7-23 * * *`, mts-dispatcher-night `0 0-6 * * *`, mts-relay-a/b manual only |

Find a relay chat later: `relay_runs.jsonl` gives host + account + session title; open that App on that account and search the title.
