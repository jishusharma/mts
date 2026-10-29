# Gemini `bg_watch.py` cross-review

**Verdict: SOUND.** The cap mapping, completion handling, TaskStop recognition, and bounded `until` command matched the card’s expected behavior in independent synthetic checks. No code or spec changes were made.

## Cap table

The source documents operator targets and defines local caps at `scripts/dev/bg_watch.py:16-29`; `kind_of()` maps commands at lines 41-75. Direct calls to `kind_of()` produced:

| Kind | Expected cap | Observed | Result |
|---|---:|---:|---|
| probe | 2 min | 2 min | Match |
| NUC / SSH | 5 min | 5 min | Match |
| worker (Agent/Task) | 45 min | 45 min | Match |
| ship | 20 min | 20 min | Match |
| poll-loop | 10 min | 10 min | Match |
| tests | 20 min | 20 min | Match |
| Gemini queue | 45 min | 45 min | Match |
| generic command | 10 min | 10 min | Match |
| watcher `supervisor.py wait --timeout 3000` | timeout + 5 = 3005 min | 3005 min | Match |
| watcher without explicit timeout | 3000 s default + 5 min = 55 min | 55 min | Match |

## Synthetic `report_lines()` fixtures

Created six isolated JSONL transcripts in a temporary directory. Each background Bash call used a synthetic ID and a start timestamp; the `report_lines()` call used a fixed clock. Only the transcript file’s mtime was refreshed so it passed the active-session filter. The temporary directory was removed automatically after the run.

| Case | Expected | Actual | Result |
|---|---|---|---|
| Running command, 20 min old | Report stalled; command cap is 10 min | `STALLED-BG command bgabc123 20m > cap 10m ...` | Match |
| Completion notice in user message | No report | No report lines | Match |
| Completion notice in `queued_command` attachment | No report | No report lines | Match |
| `TaskStop` for the background ID | No report | No report lines | Match |
| Running command, 5 min old | No report; below 10 min cap | No report lines | Match |
| Completion notice quoted inside a tool result | Still report; quoted result is not a completion signal | `STALLED-BG command bgabc123 20m > cap 10m ...` | Match |

The matching rule is explicit in `_notified()` and `open_tasks()` (`bg_watch.py:85-141`): notices are read from a user message or queued-command attachment, while tool-result content is excluded; a `TaskStop` tool call records the task ID as done.

## `until` CLI

Ran the actual CLI in subprocesses against temporary files, with `--timeout 3 --interval 1`:

| File condition | Expected exit | Actual exit | Result |
|---|---:|---:|---|
| Pattern already present | 0 | 0 | Match |
| Existing file without the pattern | 124 after deadline | 124 after 3 seconds | Match |

`wait_until()` implements this deadline behavior at `bg_watch.py:198-210`; CLI parsing and exit propagation are at lines 227-239.

## Findings

| Severity | File:line | Evidence | Proposed fix |
|---|---|---|---|
| None | — | All cap mappings, six fixture outcomes, and both CLI exit codes matched their documented expectations. | None |

## Verification limits

This was a read-only behavior audit using synthetic transcript files and existing code. No live Claude transcript, background task, or running process was inspected or changed. No product tests were run; the card’s specified synthetic checks were run directly.
