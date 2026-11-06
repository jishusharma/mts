COUNTS: MATCH 18 | DIFF 1 | NOT_CHECKABLE 6 (25 numbers; board run 2026-11-06 ~12:44Z, recount ~12:45Z, origin/fast-track 959815d30)

# Audit: status_board.py numbers vs a fresh git / tasks count

Method (all OURS, run read-only; `git diff` of repo files is empty): board = `python scripts/dev/status_board.py` (`status_board.py:565-578` entry). Recount = separate commands: `TZ=UTC git log origin/fast-track --no-merges --since=9.days --date=format-local:%Y-%m-%d --format=%cd | Group-Object`; `tasks.py status`/`list --state`; a one-off python over `MyTradingSys/system/tasks/*.json`; `Select-String '"closed": "<day>'`; `sync.py claims`; `git worktree list`.
The board's trunk-commit source is `status_board.py:426` (`git log origin/fast-track --no-merges --since=9.days --format=%cI`), cards come from `status_board.py:401-408`.

| # | Board prints (quote) | Board | Recount command | Recount | Verdict |
|---|---|---|---|---|---|
| 1 | "Cards closed … Today" (`:442`, state=done, closed[:10]==today) | 30 | `Select-String '"closed": "2026-11-06'` in tasks/*.json | 30 | MATCH |
| 2 | "Cards closed … Yesterday" | 27 | same, 2026-11-05 | 27 | MATCH |
| 3 | "Commits on trunk … Today" (`:426,443`) | 141 | git log, UTC day 11-06 | 144 | DIFF (141 vs 144): origin/fast-track moved between runs (ref was `959815d30`, committer date 18:14:31+0530, after the board ran). Re-running the board's own `git_days()` later printed 144 = same as recount; a timing difference, not a counting bug |
| 4 | "Commits on trunk … Yesterday" | 152 | git log, 11-05 | 152 | MATCH |
| 5 | "Trunk commits per UTC day: 11-05" | 152 | git log, 11-05 | 152 | MATCH |
| 6 | "… 11-04" | 360 | git log, 11-04 | 360 | MATCH |
| 7 | "… 11-03" | 291 | git log, 11-03 | 291 | MATCH |
| 8 | "… 11-02" | 270 | git log, 11-02 | 270 | MATCH |
| 9 | "… 11-01" | 331 | git log, 11-01 | 331 | MATCH |
| 10 | "Open CRITICAL 14" (`count_open`) | 14 | one-off python, state not in done/dropped, weight==CRITICAL | 14 | MATCH |
| 11 | "open CRUCIAL 27" | 27 | same, CRUCIAL | 27 | MATCH |
| 12 | Headline "41 CRITICAL/CRUCIAL cards open" | 41 | 14 + 27 | 41 | MATCH |
| 13 | "parked (need review / no tries left) 14" (`:506` parses `tasks.py status`) | 14 | `tasks.py status` -> `parked=14` | 14 | MATCH (same source as board, so not independent of tasks.py; checked against cards only by that command) |
| 14 | "raw 17" | 17 | `tasks.py list --state raw` line count; `tasks.py status` raw 17 | 17 | MATCH |
| 15 | "blocked 37" | 37 | `tasks.py list --state blocked` lines; status blocked 37 | 37 | MATCH |
| 16 | "74 READY Claude card(s)" (`claude_ready`, lane not CODEX/GEMINI/OPUS/DSA*; rule is OURS, `:309`) | 74 | one-off python, same lane rule written separately | 74 | MATCH (rule itself OURS, not verified as right; `tasks.py status` says ready=83 incl. other lanes) |
| 17 | "Dedupe/cleanup commits today: 4" (`CLEAN_RE` `:166`, OURS regex) | 4 | git log 11-06 subjects matching the same words | 4 | MATCH (regex is a keyword guess: note "sync ship folds LAYERS regen … start retires released gateway trees" counts as cleanup; "retire" matches any subject) |
| 18 | "Worktrees: 31" | 31 | `git worktree list` lines | 31 | MATCH |
| 19 | "Stale claims (over 24 h): 4" | 4 | `sync.py claims` lines ending STALE | 4 (150h, 227h, 157h, 172h) | MATCH |
| 20 | "CI red 6 min" / "red now 5 min" (two board runs, 6 vs 5 min) | 5-6 | needs GitHub CI API (`ci_watch.fetch`), not git/tasks | - | NOT_CHECKABLE (also moved between two runs 1 min apart, as expected from a clock-based number) |
| 21 | "Gate wall time, median of last 5 ships: 10 s" | 10 | reads `runtime_data/gate_timing.jsonl`, not in git | - | NOT_CHECKABLE |
| 22 | "Ships running now: 1 / 2" | 1-2 | host process list, not in git | - | NOT_CHECKABLE |
| 23 | Budget %s per login (A 40/89, B 33/71, C 8/41) | - | from signals branch, not git log/tasks.py | - | NOT_CHECKABLE (board marks all three STALE, 4-18 h old) |
| 24 | Reverts count | not printed | git log subjects `^Revert` on 11-06 = 5 (OURS, for reference) | - | NOT_CHECKABLE: status_board.py prints no revert number (grep of the source for revert shows none in its printed sections) |
| 25 | Test-vs-code commit split | not printed | board has no such number | - | NOT_CHECKABLE: nothing printed to compare |

## Notes for d-ai-health-review-1104
- Every git/card number the board prints matched a separate recount; the one difference is a ref that advanced 3 commits between the two runs.
- Weak spots are definitions, not arithmetic: `claude_ready` lane filter and `CLEAN_RE` keywords (both OURS); "Commits on trunk" excludes merges (`--no-merges`).
- The reverts and test-vs-code numbers named in this card's title are NOT printed by the board; if the health review needs them, they must come from a new command.
- The prior attempt (`2026-11-05_gpt-audit-status-board-numbers-1104.md`) was BLOCKED because git was forbidden; this run had no such restriction.
