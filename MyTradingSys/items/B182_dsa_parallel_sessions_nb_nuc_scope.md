# B182 - DSA AIBridge tasks run in parallel with NB/NUC scope kept

Opened 2026-10-11 | Status OPEN | Severity MED | FIXER: Claude | LOGGER: Claude
Source: Control Room inbox uatvl0nb0izontyg64lf (verbatim in system/OPERATOR_INBOX.md)

## Operator words

Design DSA AI Bridge tasks such that multiple sessions can run in parallel and complete tasks quickly. Make sure that their scope on NB and NUC are maintained.

## What

DSA tasks are serial today: one lane, one claim, one session. The operator wants several DSA sessions at once, each finishing fast, with NB/NUC scope intact.

## Fix shape

Review system/DSA_DELEGATION.md and desk.py lanes (DSA-NB, DSA-NUC). Split work into independent units with a per-host lane and disjoint file scope. Allow several DSA sessions at once. Claim and lock per task, not per lane. The refiner scopes it.

## Done when

Two DSA sessions run at the same time, each on a different task, no file collision, NB and NUC scope preserved. desk.py next --host returns a per-host task.
