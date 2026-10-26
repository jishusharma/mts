# OPS_CHANGE_CHECK - reach test for any change to start, hook, broadcast or role mechanisms
Evidence: NUC 2026-10-26 (commit bbd808f4a, screenshot 3c19a6836b52). A change "works" only when it reaches the machine and session it targets.
Applies to: scripts/dev/role_*, mts_signal.py, sync.py, hooks, roles/*.md. Answer all 8 before ship; each has a one-line pass proof.

1. Stale checkout? Pass: the target checkout is at origin/fast-track (`git -C <dir> rev-list HEAD..origin/fast-track --count` is 0, or the change carries its own pull step).
2. Target session open? Pass: `mts_signal.py who` lists the target, or the change works with no session open (picked up on next start).
3. Message length cap? Pass: any signal text is <= 200 characters (TEXT_MAX, scripts/dev/mts_signal.py:70); longer detail lives in a repo file the signal names.
4. Who wakes it? Pass: a named actor (hook, coordinator, operator turn) starts the step; no scheduler (SCHEDULING_POLICY.md).
5. Dirty tree? Pass: the step works with uncommitted changes present (backed-up file committed first, or paths untouched).
6. First-reply proof? Pass: the first reply after the change quotes the banner or line it should produce (e.g. `ROLE LOADED: ...`).
7. Writes outside the session folders (e.g. F:/)? Pass: every path written is inside the checkout or the scratchpad; out-of-folder writes prompt even in Bypass.
8. Target checkout diverged (local unpushed commits)? Pass: `git rev-list origin/fast-track..HEAD` is empty on the target, else the step merges origin/fast-track and does not rely on ff-only.

Commit body line (one per commit touching those paths): `Reach: Q1-Q8 ok|n/a <why>`
Example: `Reach: Q1-Q8 ok` or `Reach: Q1-Q8 ok, Q2 n/a no session needed`.
Gate enforcement at ship: card ops-change-checklist-ship-gate.
