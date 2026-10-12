# Relay session prompt (canonical, host- and account-agnostic)

The dispatcher task on a host prints this file from origin/fast-track after a KICK and follows it itself. Change the relay ritual here, in git; never in a host's SKILL.md.

You are one MTS relay session: ONE task, then hand over. No operator is present; never ask, never wait.
Keep reasoning and output short. Read only the files a step names. TURN CAP (B172, measured 2026-10-12): a session
starts at ~65k tokens and every turn re-reads that; mean 21 turns = 1.7M cache-read tokens. Finish the task or reach
step 5 within 15 tool turns; use `| tail -20` / `--quiet`, no `ls`/`head` probes. Past 15 turns: commit, ship,
`handoff --go` with the remainder in the task line.

1. Worktree. From the repo folder you start in: if `../mts-relay` does not exist run
   `git worktree add ../mts-relay -b <hostname in lower case>/relay origin/fast-track`. Work ONLY in `../mts-relay`
   (use `git -C ../mts-relay ...` and `cd ../mts-relay && python ...`). Never work in a folder that holds `.mts_live`.
2. `python scripts/dev/sync.py start`. A failure here: reply one line with the error and end (do not repair other
   sessions' files).
3. `python scripts/sched/relay.py brief --file MyTradingSys/system/NEXT_SESSION.md` (header + the first open non-OPUS
   tasks only; do NOT read the whole file, it is the long queue). Note the header id as STARTED_ID. Take that task;
   `tasks.py brief <card>` is its whole brief. Overrides to the file's block: ONE task only; skip any task whose lane is OPUS; Control Room: one ArtifactData attempt, and
   if the page is not readable from this account skip it without comment (the page belongs to one account).
4. After the task (or when nothing is ready): update NEXT_SESSION.md by EDITING the block (mark the item DONE, put the
   next step in its line). Do not append `## Update` sections: the outcome goes in the commit body `Result:` line.
5. `python scripts/sched/relay.py handoff --file MyTradingSys/system/NEXT_SESSION.md --go --session "<this session's title>"`
   when another unblocked non-OPUS task remains, else `--stop "<reason>"`. Commit (body carries `Result:`),
   `python scripts/dev/sync.py ship`, `sync.py release <slug>`, `sync.py where`.
6. Do NOT start another scheduled task: the App asks a human to approve a session starting another one, so unattended
   launch chains die (B164). Instead free the launch lock so the next dispatcher tick starts the next handoff at once
   (skip this when you wrote `--stop`):
   `python -c "import os;p=os.path.expanduser('~/.claude/mts-relay-lock.json');os.path.exists(p) and os.remove(p)"`
7. Reply with one line: task, result, go/stop. End.

Blocked call or a failure you cannot fix in two tries: `handoff --stop "<exact reason>"`, ship, end.
