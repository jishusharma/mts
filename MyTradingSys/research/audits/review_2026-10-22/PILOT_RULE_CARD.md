# Pilot rule card (one page) - plain session, 2026-10-22

You are a plain Sonnet session. No role, no Supervisor, no roster. These are your only rules; CLAUDE.md still loads, this card wins where they differ.

1. Start: `python scripts/dev/sync.py start <slug>`; work ONLY in the WORKTREE it prints.
2. Take cards in the order given. For each: `python scripts/dev/sync.py claim "<card>"`, do it, test it, then `python scripts/dev/sync.py ship --release <slug>`. One card at a time.
3. A new test must fail on the old code at least once (show the failing run).
4. Testnet only. Never read `.secrets/` or `.env`. Never commit runtime, order or account data (repo is PUBLIC).
5. Never touch the live tree, deploy, stop processes, or start sessions/agents/schedulers. Do not use start_session, Agent, Workflow, CronCreate, ScheduleWakeup.
6. No `git reset`/rebase/force-push, no bare `git stash`. Use `git -C <dir> <cmd>`, no chained `cd x && git`.
7. Commit body ends with `Result: <what works now / the number>`.
8. Do not ask "want me to?" for implied work. If blocked, report the exact blocked call and take the next card.
9. Never tell the operator about turn counts, context size or compaction.
10. After each card: one line to the operator: card, commit, test result. After the last card or 2 hours: stop and write `PILOT_RESULT.md` lines (cards shipped, minutes, blocks) into your final message.

Done = shipped to origin/fast-track and `sync.py where` shows a clean tree.
