# AIBRIDGE LANE (MTS side)

Purpose. One page MTS reads to know what AIBridge is, how MTS uses it,
and what MTS never asks it to do. Replaces the retired Qwen NUC lane
mental model.

## What AIBridge is

A local bridge that lets a web AI assistant run PowerShell on this
machine through an allowlisted loopback agent.

Root:            F:\AIBridge
Entry docs:      F:\AIBridge\README.md, F:\AIBridge\SPEC.md
Status:          F:\AIBridge\ROADMAP.md
Layout:          F:\AIBridge\PROJECT_LAYOUT.md
Intro:           F:\AIBridge\docs\INTRODUCTION.md
Latest handoff:  F:\AIBridge\HANDOFF.md (dated copy beside it)
Open tasks:      F:\AIBridge\research\P3b-security-review-tasks.md
Security review: F:\AIBridge\research\P3b-security-review.md

Runtime:         F:\AIBridge\src\agent.ps1 on 127.0.0.1:7181
Config, allowlist, audit: same folder.
Extension:       F:\AIBridge\extension, Chrome MV3, loaded unpacked.

State 2026-10-01: P1, P2, P3a, P3b part 1 done. P3b part 2 blocked on
the Chrome extension ID. P4 and P5 pending.

How to resume bridge work: read HANDOFF.md, then
P3b-security-review-tasks.md, start at T11.

Bridge hard rules: loopback only, denials always win, audit every
request, no BOM, LF only, no emoji, read before write, no writes to
the MTS repo from an AIBridge session.

## What MTS uses it for

Surface tag: AIBRIDGE. Reads and command execution over loopback only.

Allowed MTS calls, allowlist on the MTS side:
- scripts\Build-Check.ps1
- python -m pytest MyTradingSys/tests/docs -q
- repository history: last N commits, short hashes only
- repository working state: short status, ahead/behind counts
- change summary: file, insertions, deletions
- latest commit summary: files touched, insertions, deletions
- Get-Content <path inside the MTS repo only>
- mts-loop status
- Get-Content runtime_data\loop_state.json

Not allowed, even though a shell could run them:
- python -m pytest MyTradingSys/tests -q  (full suite, exceeds soft cap)
- anything under scripts\core\ (mode.ps1, stop-day.ps1, start-trading-day.ps1)
- anything that writes into the MTS repo, commits, or stages .new
- anything in execution/ or layers/alerts/
- any HALT or restart action

Caps:
- Timeouts: 60 s soft, 300 s hard, per call.
- Output: 8 KB per call. Bridge truncates and marks.
- Session binding: AIBridge session ID equals the MTS session ID in
  MyTradingSys/system/sessions/<ID>.md. One key, not two.

## What MTS never asks AIBridge to build

No MTS-specific verb. No MTS schema. No MTS allowlist logic inside the
bridge. The bridge stays a loopback agent:
run(command, cwd, timeout) -> {stdout, stderr, rc}.
MTS supplies the allowlist, the timeout, the truncation, the audit key.
All MTS logic lives in MTS.

If a tuning need cannot be solved MTS-side, log it in this file and
hold it for the bridge operator. Do not raise a bridge change request
mid-development.

## How a bridge task goes out and comes back

1. DSA web chat composes an allowlisted command.
2. Loopback agent on 127.0.0.1:7181 executes it under the allowlist.
3. Output returns to DSA. Audit entry written on the bridge side.
4. If the result is a decision (not a read), DSA writes it into the
   MTS session record under the same session ID.
5. If the command would write to MTS, it is not allowed. The operator
   or supervisor performs the write on the desktop.

## Pointers

- SURFACE_POLICY.md section 1 (surface table)
- SURFACE_POLICY.md section 4 (lane names)
- CLAUDE.md work routing line
- Dumps/operator/context/DSA_HANDOFF.md section 14 (worker directive)
