# B082 MTS-QwenFeeder points at a missing script

Opened 2026-10-01. Status CLOSED 2026-10-01. Severity MED.

## Symptom

Scheduled task MTS-QwenFeeder is Disabled and returns LastTaskResult=1. It points at scripts/worker/qwen_feeder.cmd.

## Evidence

- Target path: C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed\scripts\worker\qwen_feeder.cmd
- File absent from disk this session.
- File absent from origin/main (ls-tree).
- File absent from origin/cloud/work (ls-tree).
- File absent from all commit history (searched the full ref history).
- Task State: Disabled. LastRunTime 2026-09-29 23:51. LastTaskResult 1.

## Consequence

Nothing dispatches to the NUC Qwen queue from this task. The NUC worker is fed by other means (queue_tool.py pack by hand or by the DSA lane supervisor).

## Resolution options

1. Write scripts/worker/qwen_feeder.cmd and re-enable the task.
2. Delete the task.
3. Leave as-is and note that it is a stale reference.

## Decision

2026-10-01: task deleted; Qwen decommissioned.
