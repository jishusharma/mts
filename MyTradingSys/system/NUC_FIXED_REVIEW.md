# NUC-hang workarounds after the restart fix (review, operator 2026-11-01)

Operator 2026-11-01: JIS-NUC restarts are fixed. One row per workaround. Rule used (OURS): REVERT only what is NUC-only and
removable without a per-host step; KEEP generic guards and anything whose host install cannot be verified from a laptop tree
(no DEVICES/registry read, no F: drive here). Not edited: gemini_queue NOPROMPT+lock, RUNAWAY_GUARD checks, mts_signal broken-clone repair.

| Item | File | Decision | Reason |
|---|---|---|---|
| 4d logon wake (MTSLogonWake Run value) | SCHEDULING_POLICY.md:35-36, scripts/dev/logon_wake.py | KEEP | It resumes the Supervisor after any logon (Windows update, power loss), not only NUC hangs. Which hosts installed it is not readable from here (ISSUES_REGISTER R2 shows A and C never did); an `uninstall` broadcast on an unverified host list is a guess. Revisit when a host roll-call lists the Run values. |
| 4b3 text naming 4d | SCHEDULING_POLICY.md (4b3) | KEEP | Follows 4d; 4b3 `--wake` stays for the app-closed case. |
| 4c logon guard (MTSTempGuard, c_drive_guard.py) | SCHEDULING_POLICY.md:38 | KEEP | Temp cleanup on every logon, all hosts; nothing NUC-specific. |
| NUC_HARVEST no-push rule | NUC_HARVEST.md:3 | KEEP | A credential-prompt hang on `git push`, not the restart fault; not verified fixed. |
| NUC hang test hold | RUNAWAY_GUARD.md:34 | REVERT | Doc-only hold on a single-variable hang test that is over. Sentence removed; "the guard reads, it does not tune" stays. |
| ISSUES_REGISTER R2, I7; SUPER_SESSION:109 | research/nuc_restart_2026-10-28/ISSUES_REGISTER.md, SUPER_SESSION.md | KEEP (history) | 4d is kept, so these stay true; session-log line is history. |

No host Run value is removed, so no `logon_wake.py uninstall` broadcast is sent.
