---
name: mts-relay-b
description: Ad-hoc relay: a fresh session runs the committed NEXT_SESSION.md handoff, then hands over to mts-relay-a.
---

MTS relay session (task B of the A/B pair; you hand over to mts-relay-a). Your working folder is the LIVE tree C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed: never edit or commit there.
1. Make a worktree: `git -C C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed fetch origin fast-track`, then `git -C C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed worktree add ..\mts-relay-<UTCstamp> -b jisnb/relay-<UTCstamp> origin/fast-track`. Work only there.
2. Read CLAUDE.md, MyTradingSys/system/RELAY.md, then MyTradingSys/system/NEXT_SESSION.md. STARTED_ID = the id=... in its `<!-- relay: ... -->` header line. If the header says stop, report that in one line and end.
3. Run the fenced block in NEXT_SESSION.md exactly (ONE task, claim/work/ship/release). Model Sonnet; subagents only if clearly needed.
4. Hand over per RELAY.md: overwrite NEXT_SESSION.md, `python scripts/sched/relay.py handoff --file MyTradingSys/system/NEXT_SESSION.md --go` (or `--stop "<reason>"` when blocked, an operator question is pending, hygiene is RED and unfixed, or the queue is empty), commit, `python scripts/dev/sync.py ship`, `sync.py where` clean.
5. `python scripts/sched/relay.py gate --file MyTradingSys/system/NEXT_SESSION.md --started-id <STARTED_ID>`. If it prints `RELAY GO ... task=<id>`: load run_scheduled_task via ToolSearch and run exactly that task id. If STOP: end with the reason in one line.
Hard rules in CLAUDE.md apply (testnet only, no secrets, no live-tree edits, no restarts/HALT/orders).

Output caps (B172): pipe long command output through `| tail -20`, use `--quiet` flags, no `ls`/`head` probes; finish within 15 tool turns.
