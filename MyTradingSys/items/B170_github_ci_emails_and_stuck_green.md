# B170 - GitHub emails every failed CI run; green/fast-track stuck

Status: OPEN (filed 2026-10-10). Severity LOW.
Source: BUGS.md row B170; Control Room inbox pqven951datsaeozt2wl.

## Verbatim ask

Every failed CI - fast-track run sends an email; green/fast-track is stuck at 24197c4 while fast-track is 6e66d5b.

## State

A session has no gh CLI and the token has no workflow scope, so neither the notification setting nor the workflow can be changed from here. Operator: GitHub > Settings > Notifications > Actions > untick Email (or Watch > Custom > unticked Actions). The real fix is system/ci_concurrency_fix.patch applied with a workflow-scope token; until then auto_deploy.py uses its own gate.

## Updates

- 2026-10-12: item file created by session MTS-2026-10-12-1403Z-DSA-COO to satisfy the Build-Check rule that every OPEN row has a matching items/ file. State copied from the BUGS.md row.
