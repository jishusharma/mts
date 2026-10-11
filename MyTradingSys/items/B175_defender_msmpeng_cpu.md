# B175 - MsMpEng (Defender) holds ~0.94 core on JIS-NB

Source: Control Room inbox zu2mah3eiu13xkno2q9n, 2026-10-11T14:13Z (verbatim in OPERATOR_INBOX.md).
Operator wants the fix executed, no more diagnostic rounds. Already done by DSA: ESET removed, 23 path + 6 process exclusions, ScanAvgCPULoadFactor 10 (scheduled scans only, not real-time).

## Why this was filed, not executed (unattended pickup)
Host-level, hard-to-reverse changes (kill pid 3200, WMI repository reset + reboot, Group Policy, Dev Drive with moving IdeaProjects/.m2/.gradle) need the operator. A reboot drops AIBridge and Chrome; the live loop owns java. CLAUDE.md: builders never stop/restart live processes. Operator's own constraint: confirm before killing pid 3200; only mode.ps1/stop-day.ps1 after the operator says so.

## Proposed order (recommended: option 1 then 5)
1. Identify pid 3200 (read-only: command line, parent, start time). If a stray Maven run, operator confirms, then stop that PID only.
2. Add extension exclusions (.class .jar .pyc .obj .dcu) via Add-MpPreference: low risk, no reboot.
3. Dev Drive + Performance Mode (structural fix): needs operator-run admin steps and a downtime window; move IdeaProjects, .m2, .gradle; the live tree path changes, so supervisor must plan it.
4. WMI repository reset (stale ESET entry): cosmetic for CPU, needs reboot; do last.
5. Disable file hash computation by Group Policy: low yield, skip unless 1-3 fail.

Done when: MsMpEng average CPU < 0.3 core over 120 s on a quiet loop, measured the same way as the report (CPU seconds delta).
