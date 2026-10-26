# RUNAWAY PROCESS GUARD (card `runaway-process-leak`, priority 1, JIS-NUC 2026-10-26)

Status: DESIGN FOR REVIEW. Nothing here is installed. No setting on any device is changed by this file.

## 1. What happened (evidence, JIS-NUC)
- 2026-10-26 06:39:28 local: a Git-Bash `find.exe` + `grep.exe` pair started. By 15:50 `find.exe` had used 33,000 CPU seconds (9 h of one core), held **10.9 million handles**, paged pool was 9.7 GB, **available memory 0 MB of 32 GB**, CPU temperature averaged 96-99 C (max 100 C, 517 min at 95 C or more). Stopped by hand at ~15:55; memory back to 19 GB free.
- Spawner found in the local Claude transcripts (session b548c0a6, subagent af27dbcb, a Sonnet general-purpose Agent of builder `b-oi-pivot`), 01:09:27 UTC = 06:39:27 local:
  `find / -iname "*openinterest*" -o -iname "*oi_5m*" -o -iname "*open_interest*" 2>/dev/null | grep -v node_modules | head`
  The shell tool returned "Command did not complete" after about 2 min. The tool gave up on the command but **the find.exe it had started was left running as an orphan** (parent gone). `find /` in Git Bash walks every mounted drive (C:, F:, junction loops, backups); with `| head` it never exits cleanly while still walking.
- So two defects: (a) an agent ran a whole-drive `find /`; (b) a timed-out shell call does not kill its child tree. (b) is the general bug: any command can leak.
- Link to the NUC hangs is NOT proven. The 7 watchdog resets (event 142) started 10-23, before this process. A leaking process can still starve or hang a box, and a pegged core also keeps the CPU out of deep idle states, which may have hidden an idle-time hang (see NUC_SHUTDOWN_HANDOVER.md, update 2026-10-26 16:00).

## 2. What to find out on EVERY device (investigation, read-only, no cleanup)
Run on each machine (JIS-NB, JIS-NUC, JIS-DESKTOP, JIS-LAPTOP, vm) and reply to broadcast b-88e04d with the output:
1. `powershell -File scripts/operator/runaway_check.ps1` (after merging origin/fast-track; the one-liner in the broadcast works before that). Reports: free memory, paged/nonpaged pool, any process over 100k handles, any find/grep/sort/xargs/sed/awk/tail/cat/head/less over 10 CPU minutes.
2. History: `powershell -File scripts/operator/nuc_health.ps1 -Days 7` counts event 142 / 41 hard resets (works on any Windows host).
3. Spawner hunt, this machine only: search `%USERPROFILE%\.claude\projects\**\*.jsonl` (and `subagents\`) for shell commands that start `find /`, `find C:`, `find F:`, `grep -r /`, `du /`, `ls -R /` and a following "Command did not complete" result. Report session id, time, command; do not edit or delete transcripts.
4. Codex lab / Gemini / Selenium workers: the same check by hand for their shells (they do not write Claude transcripts).
5. Record per device: runaway seen yes/no, when, which command, free memory at worst. One line each in this file, section 6.

## 3. Design to review: three layers, cheapest first
Policy fit (SCHEDULING_POLICY.md): no standing scheduled tasks, no routines. Allowed today: session hooks (settings.json), the HKCU Run logon entry (4c), the two named exceptions. A permanent background scanner is a NEW exception and needs the operator's explicit yes (a new section 4d).

**Layer 1 - prevent (no process, no policy change).** A PreToolUse hook on Bash/PowerShell for agent sessions: block, with a one-line reason, commands matching a root scan: `find /`, `find C:\`, `find F:\`, `grep -r` or `-R` rooted at `/` or a drive root, `ls -R /`, `du /`, `Get-ChildItem -Recurse` rooted at a drive root. Message: "scan a named folder, e.g. `git ls-files` or `find MyTradingSys -name ...`". Add the same rule to CLAUDE.md "Hard rules" and AGENTS.md (Codex). Fail open on hook errors (a broken hook must not block work).

**Layer 2 - detect at session events (no standing process).** Reuse the c_drive_guard `hook` pattern: a SessionStart / UserPromptSubmit hook (throttled to once per 5 min per host) runs a read-only scan: processes over 100k handles, or find/grep/sort over 10 CPU min, or free memory under 1.5 GB, or paged pool over 4 GB. Output: one warning line in the session, and one `mts_signal.py send` line to the other hosts (`RUNAWAY <host>: <name> pid <n> ...`). Report only; no kill. Cost: a few hundred ms, only when a session is active. Gap: nothing is scanned while no session runs (accepted by policy).

**Layer 3 - stop the leak at the source.** A wrapper for agent shell calls that runs each command in a Windows Job Object with kill-on-close, so a timed-out call kills its whole child tree. This is the real fix for defect (b). It may belong in the Claude Code / Codex harness, not this repo; review should say whether we can do it with `scripts/dev` wrappers (e.g. a `run_guarded.ps1` that starts the command in a job and waits with a timeout) or must file it upstream.

**Layer 4 (needs operator exception) - always-on watcher.** A tiny logon-started loop (HKCU Run, like `MTSTempGuard`, no admin, no scheduled task) that samples every 60 s and, for processes in an ALLOWLIST of tool names (find, grep, sort, xargs, sed, awk) only, stops them when over 30 CPU minutes AND over 1 million handles; everything else is reported, never killed (never claude, python, java, node, a trading process, a build). Log to `%LOCALAPPDATA%\MTS\logs\runaway_guard.log` (outside the repo, never committed). Uninstall command. Recommend: do NOT build this until Layers 1-3 are reviewed; ask the operator for 4d only if the review says 1-3 leave a real gap.

## 4. Safety rules for any version
- Report first; kill only the allowlist; never a live-tree, trading, Java, Python, claude or Codex process.
- No new scheduled task, no routine, no admin, no reboot, no change to power/BIOS/NUC settings. The NUC hang test (single variable) must not be disturbed: the guard reads, it does not tune.
- Runtime data stays out of the repo (public repo): logs on C:\ under `%LOCALAPPDATA%\MTS\logs`.
- Every detector has a test that FAILS on a fake runaway (a helper process holding >100k handles or a looping `find`) and PASSES on a clean host. Thresholds are OURS, not sourced; label them so.
- Fail open: if the scan errors, say nothing and never block a session.

## 5. Review requested (independent, another model; card `runaway-guard-design-review`)
The reviewer must answer, with evidence, not opinion:
1. Is the root cause right? Verify from the transcript that the find was `find /` and that the shell tool timeout left the process running (try on a scratch host: run `find /` in an agent shell call, let it time out, check if find.exe survives).
2. Layer 3: is a Job Object wrapper feasible for Claude Code Bash/PowerShell tool calls and Codex shells? What exact hook or wrapper, which events, and what breaks (background tasks, Monitor, long builds)?
3. Layer 1: which regex rules block `find /` without blocking legitimate `find MyTradingSys ...`? Give the pattern and 10 allow/deny test strings.
4. Thresholds: handle count, CPU minutes, memory, pool. Are 100k handles / 10 CPU min / 1.5 GB free / 4 GB paged pool sane for these hosts (32 GB NUC, laptops)? Measure normal peaks on two hosts first.
5. Policy: does Layer 2 (hooks) fit SCHEDULING_POLICY.md without a new exception? Is Layer 4 worth a 4d exception?
6. Does the NUC need anything beyond this (is event 142 linked)? Say what evidence would settle it.
7. Cross-device: Windows only? Does the VM / any Linux host need a different command?
Reviewer returns ACCEPT / CHANGES with a numbered list. Nothing is built until the review is back.

## 6. Per-device results (fill in; one line each)
| Device | Runaway seen | When / command | Worst free MB | Checked by |
|---|---|---|---|---|
| JIS-NUC | yes | 10-26 06:39 `find /` from builder b-oi-pivot subagent; 9 h, 10.9M handles, 0 MB free | 0 | B 10-26 |
| JIS-NB | ? | | | |
| JIS-DESKTOP | ? | | | |
| JIS-LAPTOP | ? | | | |
| vm | ? | | | |
