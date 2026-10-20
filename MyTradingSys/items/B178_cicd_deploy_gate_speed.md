# B178 - operator: CI/CD end-to-end speed - deploy gate runs the full layer suite as one cold call; backup_snapshot competes for disk

Source: Control Room inbox 3nk95q0pnm8hwyf26yvm, unmrdo3l1z9i5jmzqw85 (verbatim in MyTradingSys/system/OPERATOR_INBOX.md), picked up 2026-10-11 by the unstick session: the cloud poller had marked these in_progress/needs_local but nothing was recorded, filed or carded.

## Plan
Merged with inbox unmrdo3l1z9i5jmzqw85. Fix 1 (auto_deploy run-lock) is ALREADY on fast-track (auto_deploy.py acquire_lock). Remaining: (2) warm persistent gate worktree and/or per-module layer tests in run_all_tests.py --quick, measured before/after (baseline ~15 min for 11 files); (3) stagger backup_snapshot.py off the deploy window. Keep every gate step: speed must not drop a test.
