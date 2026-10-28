# How context is loaded into a Supervisor session today (2026-10-28)

**Verdict in plain words:** a Supervisor session starts with about 6.4k tokens (about 25.8 KB) loaded for it before it does anything: CLAUDE.md and MEMORY.md (the app loads both), plus one big text the role-loader hook injects on the first prompt (role file, rules reminder, login hand-over). Everything else (STATUS, announcements, SUPER_SESSION Boot facts) the session reads itself by following the boot steps. Nothing hook-enforced limits context size; compaction is left to the app and the Supervisor rebuilds from files after it.

## 1. What loads, in order
1. **App auto-load (no hook):** `CLAUDE.md` (project) and `MEMORY.md` (user auto-memory index). CLAUDE.md says "never Read it" because it is already in context.
2. **SessionStart hooks** (.claude/settings.json:4-38): six scripts run; they inject short status lines only (tiny: see table 3). `role_loader.py hook` at SessionStart injects nothing on a fresh session; it only re-injects the role after resume/compaction (role_loader.py:509-518).
3. **First prompt `You are Supervisor. Login A.`** -> UserPromptSubmit hooks (settings.json:40-69). `role_loader.py` matches the role line, runs `git fetch`, and injects: header + banner order + RULES_ANSWER + the full `roles/supervisor.md` + the hand-over `handover/SUPERVISOR_<L>.md` read from origin/fast-track + CONFLICT_HINT (role_loader.py:426-431, 446-480, 434-443). Measured 10,707 B for login A.
4. **Session's own reads (boot steps in CLAUDE.md and roles/supervisor.md "Boot")**: STATUS.md, ACTIVE entries of ANNOUNCEMENTS.md, SUPER_SESSION.md "Boot facts"; NEXT_SESSION.md and LESSONS_DIGEST.md only when the task needs them. ROUTING.md is a pointer, read only per question.
5. **Later prompts:** role reminder (~230 chars) only every 6th prompt (role_loader.py:397, 487-503); mts_signal injects pending signals each prompt (measured 2,062 B at this moment, variable).

## 2. Measured sources (script: measure.py; output pasted from measure_output.txt)
```
| Source | Bytes | ~tokens (B/4) |
|---|---|---|
| CLAUDE.md (project instructions, auto-loaded) | 7168 | 1792 |
| MEMORY.md (auto-memory index, auto-loaded) | 7910 | 1977 |
| roles/supervisor.md (role_loader injects) | 7241 | 1810 |
| handover/SUPERVISOR_A.md (login hand-over, injected) | 1617 | 404 |
| handover/SUPERVISOR_B.md | 2349 | 587 |
| research/STATUS.md (boot step 2, read by session) | 11208 | 2802 |
| system/ANNOUNCEMENTS.md (boot step 2, whole file; ACTIVE part is read) | 10011 | 2502 |
| system/SUPER_SESSION.md (Boot facts section is read) | 22211 | 5552 |
| system/NEXT_SESSION.md (history, read on task pick) | 32650 | 8162 |
| system/LESSONS_DIGEST.md (live-path/backtest only) | 7819 | 1954 |
| system/ROUTING.md (boot step 2 pointer) | 18579 | 4644 |

| Hook event | Script | stdout bytes (fake sid; first prompt `You are Supervisor. Login A.`) |
|---|---|---|
| SessionStart | trunk_lag.py session-start | 338 |
| SessionStart | shot.py hook | 0 |
| SessionStart | mts_signal.py hook | 890 |
| SessionStart | ci_watch.py hook | 0 |
| SessionStart | c_drive_guard.py hook | 78 |
| SessionStart | role_loader.py hook | 0 |
| UserPromptSubmit | shot.py hook | 0 |
| UserPromptSubmit | mts_signal.py hook | 1601 |
| UserPromptSubmit | ci_watch.py hook | 0 |
| UserPromptSubmit | role_loader.py hook | 0 |
| UserPromptSubmit | trunk_lag.py hook | 0 |
```
Totals for a fresh Supervisor login A boot (bytes): auto-loaded 15,078 (CLAUDE.md + MEMORY.md); hook-injected ~10.7k (role file 7,241 + hand-over 1,617 + framing/rules/conflict text, rest); self-read STATUS 11,208 + ANNOUNCEMENTS 10,011 (whole file; only ACTIVE entries needed) + SUPER_SESSION 22,211 (only Boot facts needed; model may read all). Upper bound if every named file is read whole: ~66k B (~16k tokens). The hook cap is 10k per role: `role_loader` text is 10,707 B including the hand-over, i.e. the role file alone is under the cap (commit 220ec4619 "keep every role under the 10k hook cap").
Notes: hand-over is read from origin/fast-track (git show), not the working copy, so it can differ from the file on disk. MEMORY.md here is this machine's copy (JIS-NB); other machines differ. Hook stdout was measured by running each hook with a fake session id and a Supervisor first prompt; mts_signal and trunk_lag outputs depend on live state at run time.

## 3. Hooks (all from .claude/settings.json)
| Event | Script | settings.json line | Injects text? | Measured B |
|---|---|---|---|---|
| SessionStart | trunk_lag.py session-start | 9 | yes (lag notice) | 242 |
| SessionStart | shot.py hook | 14 | screenshot notices | 0 |
| SessionStart | mts_signal.py hook | 19 | pending signals (max 5 lines) | 900 |
| SessionStart | ci_watch.py hook | 24 | only on RED CI | 0 |
| SessionStart | c_drive_guard.py hook | 29 | disk warning | 78 |
| SessionStart | role_loader.py hook | 34 | re-inject role after resume/compaction only | 0 on fresh |
| UserPromptSubmit | shot.py, mts_signal.py, ci_watch.py, role_loader.py, trunk_lag.py hook | 45, 50, 55, 60, 65 | role text on first prompt; signals | 0 / 2,062 / 0 / 10,911 / 0 |
| PostToolUse (Bash) | mts_signal.py hook (async) | 77 | no | n/a |
| PostToolUse (Write/Edit) | preship.py hook-edit | 88 | warns once per rule per session | n/a |
| PostToolUse (Agent/Task/Workflow) | usage_reminder.py post | 98 | reminder | n/a |
| PreToolUse (Bash) | preship.py hook-commit | 126 | gate before commit | n/a |
| PreToolUse (Agent/Task/Workflow) | usage_reminder.py pre | 136 | reminder | n/a |
| Stop | stop_guard.py hook; mts_signal.py hook | 109; 114 | may block stop once per reason (stop_guard.py:78-116) | n/a |

role_loader.py is the only hook that loads role content: role matching (role_loader.py:64-83, 223-300), role-file fetch (`git_show`, 132-140), banner (112), per-login hand-over (206, 434-443). A prompt naming several roles loads none (role_loader.py:523-526).

## 4. Memory
Auto-memory (`MEMORY.md` index, 7,910 B here) is loaded by the app on every session start in this project; entries are one-line pointers, topic files are read only when the session decides. It is per-machine and per-user (not in the repo).

## 5. Compaction (what the repo says)
| Fact | Where |
|---|---|
| After compaction/resume the role is re-injected with "Session resumed/compacted: re-confirm the role" (only for an explicitly-named role, not a fallback-picked one) | scripts/dev/role_loader.py:509-518 |
| Supervisor rule: auto-compaction is the safety net, not the plan; rebuild from `plan`, never memory | MyTradingSys/system/roles/supervisor.md:57-58 |
| Rebuild after any compaction from the notes file `handover/SUPERVISOR_<L>.md`, card board, `git cherry`, `list_sessions {"linked": true}`; rotation via parent `clear_session` once context is over ~200K; compact before an idle wait over an hour when context is over ~100k | MyTradingSys/system/SUPER_SESSION.md:14 (D5) |
| Why: 10-15 audit, 68 compactions, 39 lost work | SUPER_SESSION.md:14 (rationale column) |
| No hook enforces a turn cap or context budget (turn_meter.py, model_guard.py removed 2026-10-24, 43d3bfc8f); auto-compaction fires at the window set by the MAIN checkout's settings.json; whether `autoCompactWindow` works in the desktop app is open (ROTATION_TEST part b) | MyTradingSys/system/WORKERS.md:33 (rule 5) |
| Policy lint: a role file may not contradict the ROLES.md "No compaction" policy | scripts/dev/role_loader.py:837-841 |
| A Supervisor "runs unattended and may auto-compact" | MyTradingSys/system/ROLES.md:41 |
| Card auto-compact-at-25-for-all-sessions is a planned change, not a fact yet | MyTradingSys/system/LOGIN_PLAN_2026-10-26.md:18 |

## 6. Gaps noticed
- Compaction behaviour in the app itself (what text survives) is not documented in the repo; only the recovery procedure is.
- Previous measurement (2026-10-21, MyTradingSys/research/context_load/REPORT.md) found hand-over docs were the cost; today NEXT_SESSION.md is still 32,650 B but is not on the Supervisor boot path.
- main checkout is 2031 commits behind (doctor WARN HOOK-REG), so hooks in main-checkout sessions may be stale (settings.json comes from the main checkout).
