# BLOCKED — lab-planted-error-trial

## What was checked

- Read scripts/dev/tasks.py, scripts/dev/lab_flow.py, MyTradingSys/research/layer_lab/TRIALS.md, and F:/codex_home/lab_runs/runs.jsonl.
- Checked archived, finished CODEX cards with a report path in their result. A candidate was retained only if its report exists, tasks.problems(card, tasks.load_all(...), tasks.registry(...)) is empty, lab_flow.gate(...) is empty, its scoped source fingerprint is accepted, and the count of exact card mentions in TRIALS equals matching card rows in runs.jsonl.
- Ran the candidate selection through scripts/dev/planted_error_trial.py.

## Finding

| Severity | Evidence | Result |
|---|---|---|
| HIGH | scripts/dev/planted_error_trial.py:30-48, 86-87; command python scripts/dev/planted_error_trial.py | BLOCKED: only 6 cards pass the clean-original filters; the task requires 10, so no valid 10-shadow trial can be produced. The six eligible ids are context-factors-v3-crossvendor-review, gptb-bb-top-reversal-event-table, gptb-funding-extreme-event-table, gptb-session-levels-event-table, krown-catalogue-gpt-audit, and lab-audit-tom-ledger-frames. |

The other finished CODEX cards examined fail at least one required condition, most commonly because their report is not identified by a report path in the task result or because their exact trial-row and runner-row counts differ. Substituting them would violate the requirement to skip non-clean originals. No shadow manifest or catch table is presented as a completed trial.

## Follow-up

The harness is fail-closed: run() raises when fewer than 10 clean originals are available. No tasks.py done command was run, as required for a blocked task. No follow-up card was created.
