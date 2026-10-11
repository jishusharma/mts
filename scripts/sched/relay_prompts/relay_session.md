# Relay session prompt (canonical, host- and account-agnostic)

App tasks `mts-relay-a` and `mts-relay-b` on every host hold a 3-line stub that prints this file from
origin/fast-track and follows it. Change the relay ritual here, in git; never in a host's SKILL.md.

You are one MTS relay session: ONE task, then hand over. No operator is present; never ask, never wait.
Keep reasoning and output short. Read only the files a step names.

1. Worktree. From the repo folder you start in: if `../mts-relay` does not exist run
   `git worktree add ../mts-relay -b <hostname in lower case>/relay origin/fast-track`. Work ONLY in `../mts-relay`
   (use `git -C ../mts-relay ...` and `cd ../mts-relay && python ...`). Never work in a folder that holds `.mts_live`.
2. `python scripts/dev/sync.py start`. A failure here: reply one line with the error and end (do not repair other
   sessions' files).
3. Read `MyTradingSys/system/NEXT_SESSION.md`. Note the header id as STARTED_ID. Run its fenced block as written,
   with these overrides: ONE task only; skip any task whose lane is OPUS; Control Room: one ArtifactData attempt, and
   if the page is not readable from this account skip it without comment (the page belongs to one account).
4. After the task (or when nothing is ready): update NEXT_SESSION.md by EDITING the block (mark the item DONE, put the
   next step in its line). Do not append `## Update` sections: the outcome goes in the commit body `Result:` line.
5. `python scripts/sched/relay.py handoff --file MyTradingSys/system/NEXT_SESSION.md --go --session "<this session's title>"`
   when another unblocked non-OPUS task remains, else `--stop "<reason>"`. Commit (body carries `Result:`),
   `python scripts/dev/sync.py ship`, `sync.py release <slug>`, `sync.py where`.
6. `python scripts/sched/relay.py gate --file MyTradingSys/system/NEXT_SESSION.md --started-id <STARTED_ID>`.
   `RELAY GO ... task=<name>`: load `mcp__scheduled-tasks__run_scheduled_task` with ToolSearch and run that task.
   `RELAY STOP`: nothing more.
7. Reply with one line: task, result, GO/STOP. End.

Blocked call or a failure you cannot fix in two tries: `handoff --stop "<exact reason>"`, ship, end.
