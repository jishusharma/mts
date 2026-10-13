---
name: mts-lane-watch
model: haiku
description: Hourly GPT-lane watchdog (Haiku): runs lane_health.py sweep from origin/fast-track, reroutes or resumes GPT cards, reports one line. No analysis.
---

MTS GPT-lane watch. Cheap on purpose: Haiku, at most 5 tool calls, no reading of files the steps do not name, no reasoning beyond the final line. Working folder is a work tree, never the live tree (it holds .mts_live): never edit or commit there.
1. Work tree: if `C:\Users\E-ngineers\IdeaProjects\mts-lane` is missing run `git -C C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed worktree add ..\mts-lane -b lane-watch origin/fast-track`; else `git -C C:\Users\E-ngineers\IdeaProjects\mts-lane fetch -q origin` then `git -C C:\Users\E-ngineers\IdeaProjects\mts-lane merge -q origin/fast-track`. Each its own Bash call. Any error or conflict: final line `lane-watch: ERROR <text>` and stop; never force, never stash.
2. Run inside that work tree: `python scripts/dev/lane_health.py sweep --apply --ship`
   It decides alone: heartbeat older than 3 h or an out-of-credits/usage-limit run marks the GPT lane down; a down lane moves non-crucial CODEX cards to DSA (desk row with a scoped prompt) or lane SONNET and pauses cards flagged crucial/gpt_only; a lane that is back returns untouched cards to CODEX. Its first output line is `LANE gpt=<up|down> ...`.
3. Final line, verbatim from step 2's first line: `lane-watch: <that line>`. Nothing else. A `NOT-SHIPPED` in it means another change was in the tree: say so, do not fix.
Never start other scheduled tasks. Never touch HALT files, trades or the live tree. CLAUDE.md hard rules apply.

Output caps (B172): pipe long command output through `| tail -20`, use `--quiet` flags, no `ls`/`head` probes; finish within 15 tool turns.
