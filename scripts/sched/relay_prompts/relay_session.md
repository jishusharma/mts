# Relay session prompt (canonical, host- and account-agnostic)

`relay.py tick` prints this file after `TICK KICK` and the dispatcher session follows it itself. Change the relay ritual here, in git; never in a host's SKILL.md.

You are one MTS relay session: ONE task, then hand over. No operator is present; never ask, never wait.
CLAUDE.md is already in your context: do not read it, RELAY.md or the whole NEXT_SESSION.md. Keep reasoning and output short.
TURN CAP (B172, measured 2026-10-12): a session starts at ~65k tokens and every turn re-reads that. Finish the task or reach
step 4 within 15 tool turns; use `| tail -20` / `--quiet`, no `ls`/`head` probes. Past 15 turns: commit, ship,
`handoff --go` with the remainder in the task line.
MODEL: the routine's App setting decides it (JIS-NB: Haiku 5.5 since 2026-10-14; the dispatcher guard only stops opus). A card's
HAIKU/SONNET lane says how much checking it needs, not which model runs it: take it and run the tests it names; if its brief
leaves a design choice open, `begin --skip <card>` and take the next.

0. Meter first: call `get_usage` (App tool) and record it: `python scripts/sched/budget.py write --weekly-all-pct <all-models %> --weekly-resets-at <ISO UTC reset> --five-hour-pct <5h %>` (the gate reads ~/.claude/mts-budget.json; no get_usage: skip, go on).
1. Run the `NEXT:` line tick printed (`relay.py begin --root <repo folder>`; without it: `python scripts/sched/relay.py begin`
   from the repo folder you start in). One call: relay worktree `../mts-relay` (fast-forwarded), `sync.py start`, first ready
   non-OPUS card no claim holds, claim, and that card's brief (the card is the whole brief). Work ONLY in the `worktree:` path it
   prints (`git -C <path> ...`); never in a folder that holds `.mts_live`. `BEGIN FAILED: <reason>`: reply that one line,
   `handoff --stop "<reason>"` and end (do not repair other sessions' files).
   LOOK: if the TICK line's `queue=` shows `look=N [Qn desk|card done|failed]`, a lane finished Qn and nobody has read it; that read
   IS your task (the same KICK repeats until the Qn is rewritten). Read the row (`desk.py list --all`) or the card
   (`tasks.py brief <id>`), spot-check ONE claim, rewrite the Qn as `DONE ...` in step 3. A `worktree:` line followed by
   `BEGIN FAILED: no ready ...` is fine here: edit in that path, no `--stop`. A card `begin` claimed stays unworked: `sync.py release <card>`.
2. Otherwise run the card: ONE task only; never an OPUS card.
3. After the task (or when nothing is ready): open NEXT_SESSION.md in your worktree only now and EDIT the block (mark the item
   DONE, put the next step in its line). Do not append `## Update` sections: the outcome goes in the commit body `Result:` line.
4. `python scripts/sched/relay.py handoff --file MyTradingSys/system/NEXT_SESSION.md --go --session "<this session's title>"`
   when another unblocked non-OPUS task remains, else `--stop "<reason>"`. Commit (body carries `Result:`),
   `python scripts/dev/sync.py ship --release <slug>`, `sync.py where`.
5. Do NOT start another scheduled task: the App asks a human to approve a session starting another one, so unattended launch
   chains die (B164). Instead free the launch lock with the `UNLOCK:` command tick printed (`python <worktree>/scripts/sched/relay.py
   unlock` if there is none) so the next tick starts the next handoff at once. Skip this after `--stop`.
6. Reply with one line: task, result, go/stop, and the ship proof: `git cherry origin/fast-track <sha>` printed nothing
   (a non-empty line = not shipped; say so). End.

Blocked call or a failure you cannot fix in two tries: `handoff --stop "<exact reason>"`, ship, end.
