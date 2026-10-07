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

## Done when
One copy of Dumps, the share points at it, and the live writer writes there.
