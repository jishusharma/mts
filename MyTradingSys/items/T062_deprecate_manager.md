# T062 - Deprecate the mts-manager

Status: CLOSED
Opened: 2026-10-02
Severity: MED
Receipt: Archived by MTS-2026-10-03-2230Z-CLI-SUP-small-cleanups; paths _archive/mts-manager-2026-10-03/

## Operator statement (verbatim, 2026-10-02)

"Depricate manager. Add this task to backlog."

## What is being deprecated

- scripts/manager/mts-manager.ps1 (13-line PowerShell wrapper)
- scripts/manager/claude_manager.py (348 lines, the manager logic)
- MyTradingSys/research/CLAUDE_MANAGER_SPEC.md (174 lines, spec)

## Why

The manager classifies a task string with Haiku, routes it by type to a fixed model tier, composes a 20-line brief, and launches a child via claude -p. The brief is fixed at claude_manager.py L152-163 and includes a rule line: "do not touch execution/ or layers/alerts/ live files". That rule blocks the live-path tasks the current batch needs handled, so those tasks must be hand-composed as CL prompts.

Three more reasons from the 2026-10-02 read:

- The manager takes one string per go call, cap 3 children. It cannot take the eight-task list.
- No usage percent was entered today, so every go call would fail-closed to the queue (claude_manager.py L124-135).
- DSA-composed CL prompts already deliver the same shape (session id, read-first list, brief, gates). The manager is a duplicate path.

## What replaces it

DSA composes CL prompts to screen. Routing per SURFACE_POLICY 3b. The mandatory prompt lines live in CLAUDE.md.

## What to do when this lands

1. Move scripts/manager/mts-manager.ps1 and scripts/manager/claude_manager.py to _archive/ (backup, not delete).
2. Mark CLAUDE_MANAGER_SPEC.md as deprecated at the top (do not delete; it is the historical record of the routing design).
3. Remove the manager line and the operator verbs line from SURFACE_POLICY section 3b.
4. Remove the mts-manager verbs from any command menu that lists them.
5. Regenerate BUILD_REPORT.md; confirm no orphan reference to the deprecated paths remains in any live .md, .py, .ps1.

## References

- scripts/manager/mts-manager.ps1 L1-13
- scripts/manager/claude_manager.py L1-23 (docstring, pipeline), L152-163 (brief), L257+ (cmd_go)
- MyTradingSys/research/CLAUDE_MANAGER_SPEC.md L1-174
