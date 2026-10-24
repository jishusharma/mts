# STATION CLEANUP

Station = one device with one login (operator 2026-10-23, d-station-term). Every cleanup that touches a station is listed here: what runs, when, what it may delete, where its log is, and what each station has answered. Nothing here is a scheduled task (SCHEDULING_POLICY.md), except the one allowed worktree job in section 2.

## 1. Stations

Seen by `python scripts/dev/mts_signal.py who --hours 72` on 2026-10-24. Answers come from the roll call (signal "CLEANUP ROLL CALL", 2026-10-24): each station replies `STATION <device>/<login> cleanup: ...` (`mts_signal.py send`). Copy each answer into the table; NOT CAPTURED until it arrives.

| Station | Last seen | C: free (roll call) | MTS scheduled tasks / HKCU Run | Restart cleanup (section 4) |
|---|---|---|---|---|
| JIS-NB / C | 2026-10-24 (this checkout) | 12.8 GB on 2026-10-24 (guard dry run) | no MTS task (`Get-ScheduledTask`, 2026-10-24); no MTS Run value | not registered: primary checkout blocked by local changes (section 6) |
| JIS-NUC / B | 12 min before the roll call | NOT CAPTURED | NOT CAPTURED | NOT CAPTURED |
| DESKTOP-F7IU69N / A | 75 min | NOT CAPTURED | NOT CAPTURED | NOT CAPTURED |
| DESKTOP-F7IU69N / C | 31 h | NOT CAPTURED | NOT CAPTURED | NOT CAPTURED |
| vm / B | 21 h | NOT CAPTURED (which device runs the `vm` host: NOT CAPTURED) | NOT CAPTURED | NOT CAPTURED |
| JIS-NB / B, JIS-NUC / A | not seen in 72 h (HOW_MTS_RUNS.md, 2026-10-15 snapshot) | NOT CAPTURED | NOT CAPTURED | NOT CAPTURED |

## 2. Every cleanup, by mechanism

| Mechanism | Runs when | Deletes | Log / report | Code |
|---|---|---|---|---|
| SessionStart hook `c_drive_guard.py hook` | every Claude session start; acts only when C: has < 15 GB free (OURS) | the prune set (section 3), detached | one warning line in the session | `.claude/settings.json`, `scripts/dev/c_drive_guard.py` |
| Logon run `MTSTempGuard` (HKCU Run, section 4) | every logon, so every restart with auto sign-in; prunes whatever the free space | the same prune set | `%LOCALAPPDATA%\MTS\logs\c_drive_guard.log`, one line per logon | `scripts/dev/c_drive_guard.py logon` |
| Worktree job `MTS-WorktreeMaint-<device>` | 07:15 daily (the one allowed standing task, SCHEDULING_POLICY.md section 4b) | finished worktrees and merged local branches; never uncommitted or unshipped work | `Dumps/worktree_report.txt` (gitignored), one line in SUPERVISOR_LOG | `scripts/dev/wt_maint.py` (DEVICES.md section 8b) |
| Retention | by hand, weekly (RETENTION_POLICY.md) | repo backup and staging files listed in RETENTION_POLICY.md | stdout | `scripts/dev/retention.py` |
| Backup archive | by hand | moves, never deletes, backups to `Dumps/_archive/` | stdout | `scripts/dev/declutter_backups.py --apply` |
| Operator: Windows Disk Cleanup or Explorer | by hand | anything the operator picks | none | DISK_CARE.md |
| Claude app `vm_bundles` (JIS-NB: a junction to `F:\ClaudeVM\vm_bundles`, 11.8 GB on F:, not C:) | never automatic | nothing; app-owned image | none | DEVICES.md section 6, DISK_CARE.md |

## 3. The prune set (`c_drive_guard.py`)

An entry is pruned only when nothing under it is newer than its age limit. Age limits are OURS (judgement): 24 h for `%TEMP%` prefixes, 72 h for Claude session scratch under `%TEMP%\claude`. Locked files and reparse points (junctions, symlinks) are never pruned and never walked.

Prefix, who writes it (checked by grep 2026-10-24):

| Prefix in `%TEMP%` | Writer |
|---|---|
| `tmp*` | Python `tempfile` default names (tests, tools) |
| `mts_s4_`, `mts_xt_`, `mts_snapat_` (and other `mts_*` scratch) | `run_all_tests.py:183`, `run_extra_tests.py:177,212`, `shot.py:731` |
| `staged_tests_` | `run_staged_tests.py:24` |
| `gate_timing_test_` | `test_run_all_tests.py:17` |
| `gate_budget_test_` | `tests/test_gate_budget.py:27` |
| `aibridge_selftest_` | `aibridge/tests/agent_live_selftest.py:44` |
| `dsa_tpl_` | `test_dsa.py:92` |
| `e2e_a2_` | `research/role_flow_2026-10-23/e2e/e2e_a2.py:9` |
| `dsa-boot-` | `dsa.py:371` |
| `cicd_ps_` | `cicd_run.py:355` |
| `lab_query_` | `test_lab_query.py:58` |
| `soak6_` | `soak_six_slots.py:190` |
| `r2_`, `rmd_`, `kill_switch_cli_`, `pytest-of-` | older writers, owner not re-checked 2026-10-24 |
| `claude\<project>\<session>` | Claude session scratch and background-task output (72 h) |

Never pruned, even when the name matches: any entry with a `.git` inside (`desk-*` from `desk.py:104` is a `git worktree` under `%TEMP%`; a crashed post leaves its commits there, so leftovers are for a person to check, not for the guard). Junctions and symlinks are never followed, including a junction under `%TEMP%\claude`.

Never pruned (state other code reads): `mts_roles` (role injection records, `role_loader.py:320`), `mts_host_health` (`host_health.py:63`), `mts_gate_slots` (`sync.py:184`), `mts_relay` (`scripts/sched/dispatch_gate.py:55`).

Never touched by any cleanup: the repo and its worktrees (except the job in section 2), `.secrets`, `.env`, F:, the live tree `.mts_live`, `runtime_data/`, anything younger than its age limit.

## 4. Restart cleanup (operator yes 2026-10-24; install sent as broadcast b-10b3d8, HIGH)

The operator asked for cleanup on every restart without a scheduler, and said yes to the logon run on every station. Registration is per station, as each one acks. Mechanism: a per-user Run value `MTSTempGuard` in `HKCU\Software\Microsoft\Windows\CurrentVersion\Run`. Windows runs it at logon, `conhost --headless` (no window), it prunes once and exits. It has no timer and no repeat, and it needs no admin rights. It is not a scheduled task. The same launch already runs the Antigravity daemon on JIS-NUC (DEVICES.md section 7).

Install once per station, from the primary checkout (a git worktree is refused, because tidy removes worktrees and the run would then point at nothing):

```bash
python scripts/dev/c_drive_guard.py install
```

```bash
python scripts/dev/c_drive_guard.py status
```

```bash
python scripts/dev/c_drive_guard.py uninstall
```

## 5. Roll-call answer format

`python scripts/dev/mts_signal.py send "STATION <device>/<login> cleanup: C free <GB>; would prune <n>; prefixes <top 3>; tasks <none|list>; other junk <path size>"`

A signal is at most 200 characters (repo is public: no paths with account names, no runtime data).

## 6. Status log

- 2026-10-24: inventory and this page. `c_drive_guard.py`: prefixes added (section 3), state dirs excluded, logon run added. Stations asked (roll call). JIS-NB/C: no MTS scheduled task; `wt_maint.py status` says the worktree job is NOT INSTALLED here, which contradicts DEVICES.md section 8b (fixed there).
- 2026-10-24, later: reviewers found a junction under `%TEMP%\claude` that the shipped guard would follow (outside `%TEMP%`), `desk-*` git worktrees it would prune, and an unguarded directory scan. Fixed: junctions never followed, `.git` fails closed, `desk-` removed from the prefixes, scans never raise (tests: junction and worktree tests fail on the shipped version). The fix is the first commit after `df160f3fc`.
- 2026-10-24, operator yes: fix on fast-track as `2ab5145ff`. Install broadcast `b-10b3d8` (HIGH) to every station. JIS-NB: told, not registered (primary 105 behind fast-track with 67 local changes, not ours; left alone; operator decides). Laptop, NUC and `vm`: acks pending (`mts_signal.py acks b-10b3d8`).
- 2026-10-24, correction: `vm_bundles` was reported as 11.8 GB on C:. It is a junction to F:, so the 11.8 GB is on F:. The C: loss since 2026-10-10 (32.4 GB free then, 11.8 GB now) is not the VM image; pagefile 4.75 to 9 GB, Windows folder 23.7 to 25.2 GB, worktrees 4.8 to 5.0 GB account for about 6 GB. The rest is not measured (shadow storage needs an elevated shell).
- Open: the other stations' answers; tests that leave their own `%TEMP%` dirs behind (follow-up: each test should remove its own scratch).
