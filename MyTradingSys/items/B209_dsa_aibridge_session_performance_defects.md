# B209 - DSA and AIBridge performance defects seen in one working session

Filed: 2026-10-30 by DSA on JIS-NB.
Status: CLOSED
Priority: MED
Fixer: Claude
Logger: Claude

## Why

Each item cost turns or hid a real failure during a normal build task.

## Items

1. Duplicate worktree block in one reply; second failed on existing branch.
2. Boot lists include closed history; output split over 6 parts, each needing a reply.
3. Result cmd line did not match the block sent.
4. task=mts-gate reported PASS on a gate whose log said FAILED: 2 step(s).
5. Read-only blocks stamped kind=write.
6. Two blocks in one batch returned the same cmd and swapped output.
7. -Filter with a character class returned nothing where -match returned 22 files.

## Suggested fixes

Prompt section 3 step 1: one worktree block per reply.
tasks.py list and desk.py list: open-only by default, --all to opt in.
task mode: exit non-zero when any step FAILs; never print PASS over FAILED.
Kind is derived from the command, not from the extension default.
Add a contract test that replays a 6-block batch and asserts block-to-result identity.
