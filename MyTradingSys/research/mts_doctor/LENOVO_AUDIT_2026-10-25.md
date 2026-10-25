# Lenovo audit 2026-10-25 (read-only second check)

Do the shipped commits do what their Result lines say? Checked on disk in a fresh worktree off trunk.

- c540fc3d8 (mainnet path s3): CONFIRMED. MAINNET_PATH s3 now records the operator NO of 2026-10-25 and marks the old stop list "not adopted"; card layer-review-after-simulator.json exists, state raw. No layer demoted by this commit (only the doc and one card changed).
- 8971d69e6 (re-land CLAUDE.md/supervisor.md): CONFIRMED for the checkable claims. CLAUDE.md is 7156 B, keeps the `5b` budget line and the `exhaust.py plan` line; supervisor.md still has its Read first paths. The 132-test claim was not re-run here (laptop has no global git identity; not needed for the size/line checks).
- f581b9d20 (merge, START_HERE.txt 32+/84-): no Result line (merge commit). File is 52 lines on trunk and was shortened only; no behaviour to check.

No discrepancies found.
