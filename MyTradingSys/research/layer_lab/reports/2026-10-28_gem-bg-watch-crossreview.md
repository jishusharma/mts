# Cross-Review Report: bg_watch.py

- **Reviewer:** Gemini (Antigravity session, JIS-NUC)
- **Target:** `scripts/dev/bg_watch.py` (Claude-built)
- **Reference card:** `gemini-bg-watch-crossreview`
- **Date:** 2026-10-30

## 1. Per-Kind Caps & Notice-Matching Rules

### Cap Table (`scripts/dev/bg_watch.py:29`)
```python
CAPS = {"probe": 2, "nuc": 5, "poll-loop": 10, "tests": 20, "ship": 20, "gemini": 45, "worker": 45, "command": 10}
```
All targets stated in docstring lines 15-16 (`probe 2`, `NUC verb 5`, `worker 45`, `ship 20`, `tests 20`, `poll-loop 10`) match exactly.
Watchers dynamically compute `supervisor.py wait --timeout S` + 5 min (`scripts/dev/bg_watch.py:46-52`).

### Notice-Matching Rules (`scripts/dev/bg_watch.py:85-98`)
- Completion notice parsed via `_notified(d)`:
  - User message: `d.get("message").get("content")` containing `<task-notification>` and `<task-id>([a-z0-9]+)</task-id>`.
  - Queued command attachment: `d.get("attachment").get("prompt")` containing `<task-notification>` and `<task-id>([a-z0-9]+)</task-id>`.
  - Tool results (e.g. `grep` output quoting a notice) are explicitly ignored as they arrive as `tool_result` without root `<task-notification>`.
- Explicit stop via `TaskStop` tool use (`scripts/dev/bg_watch.py:118-119`):
  - Adds `inp.get("task_id")` or `inp.get("shell_id")` to `done`.

## 2. Synthetic Transcript Fixtures (6 Cases)

Tested using synthetic transcript `.jsonl` files in isolated scratch directories with `bg_watch.report_lines`:

| Fixture # | Scenario | Age / Cap | Expected Classification | Actual Classification | Result |
|---|---|---|---|---|---|
| 1 | Running task over cap | 60m / 45m (worker) | STALLED | STALLED (`STALLED-BG worker agt0001 60m > cap 45m`) | PASS |
| 2 | Finished by user message notice | 80m (finished 60m ago) | NOT STALLED | NOT STALLED (no stalled lines) | PASS |
| 3 | Finished by queued_command attachment | 90m (finished 30m ago) | NOT STALLED | NOT STALLED (no stalled lines) | PASS |
| 4 | Stopped via `TaskStop` tool use | 70m (stopped 10m ago) | NOT STALLED | NOT STALLED (no stalled lines) | PASS |
| 5 | Young running task | 5m / 20m (tests) | NOT STALLED | NOT STALLED (no stalled lines) | PASS |
| 6 | Notice quoted inside tool result (grep) | 40m / 10m (poll-loop) | STALLED | STALLED (`STALLED-BG poll-loop bpoll006 40m > cap 10m`) | PASS |

All 6 fixtures matched expected behavior.

## 3. Exit Code Verification (`bg_watch.py until`)

Verified via subprocess invocation:
- **Matching pattern:** `python scripts/dev/bg_watch.py until --file <tempfile> --pattern MATCHING_PATTERN --timeout 3`
  - Exit code: `0`
- **Non-matching pattern (timeout):** `python scripts/dev/bg_watch.py until --file <tempfile> --pattern NON_EXISTENT_PATTERN --timeout 3 --interval 1`
  - Exit code: `124` (matches POSIX standard timeout exit code convention)

## 4. Findings Table

| Severity | File:Line | Evidence | Proposed Fix |
|---|---|---|---|
| None | `scripts/dev/bg_watch.py` | Implementation strictly complies with specifications and docstring contracts. | No code changes required. |

## 5. Verdict

**SOUND**
