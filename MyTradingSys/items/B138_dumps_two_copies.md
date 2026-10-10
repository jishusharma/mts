# B138 - Dumps exist as two copies (C: and F:) after the move

Opened 2026-10-06. Status OPEN.

## Problem
- Dumps was moved from C: to F:, leaving two copies.
- The share still points at the C: copy.
- Replacing the C: copy with a junction to F: is blocked because a live writer holds files in the C: copy.

## Risk
Readers and writers can see different copies, so the C: and F: contents drift apart.

## Next steps
1. Identify the live writer (process and path) and which copy it writes to.
2. Supervisor stops or restarts the writer (builders must not touch live processes; see CLAUDE.md hard rules).
3. Reconcile the two copies, then replace the C: copy with a junction to F: (or repoint the share to F:).

## Decision landed (2026-10-10, MTS-2026-10-10-1137Z-DSA-COO on JIS-NUC)

Canonical: C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed\Dumps (the C: tree). Already reflected in DEVICES.md sec 6 (2026-10-06).
Stale copy: F:\MTS\Dumps. Do not write to it. Readers on the desktop use C:.
Share \\JIS-NB\MTS-Queue stays on the C: copy; no repoint.
Junction / physical swap: deferred to a supervisor-owned quiet window, same window as any working-tree move. Script is ready: scripts\dev\move_dumps_to_F.ps1 (dry run by default, -Apply renames the old folder, never deletes). Not run from this session; the NUC cannot pause the desktop writer.
Operator action owed: none until a supervisor window opens; then run move_dumps_to_F.ps1 -Apply and re-check the share.

## Done when
One copy of Dumps, the share points at it, and the live writer writes there.
