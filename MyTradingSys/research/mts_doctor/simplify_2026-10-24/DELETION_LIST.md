# Deletion list (simplification session, 2026-10-24)

Covers BRIEF section 3 items 1-9. Callers were checked on this tree (equals origin/fast-track at write time) with a word-boundary scan of every tracked
non-doc file (scripts, tests, `.claude/settings.json`, `.github`, ps1, json registries), not a name grep alone. Lines = `wc -l`.
Ship order is (a) to (e) as the operator asked; item numbers are the BRIEF's. Nothing in BRIEF section 4 is touched.

## Items 1-2: smoke gate obeys its budget; local `--full` only for the live path (ship a)
| What | Lines | Callers / why | Replaced by | Risk |
|---|---|---|---|---|
| `gate_impact.plan_budget`: "direct tests are never deferred" rule (gate_impact.py:153-167) | edit, about -3/+8 | only `run_all_tests.apply_fast` (run_all_tests.py:804) | direct units also fill the budget cheapest first; any unit at or above `SLOW_FILE_S` (30 s) is deferred to CI | low: a deferred test still runs in CI shards before deploy. Changes `test_gate_impact` expectation `test_direct_files_are_always_kept_even_over_budget` |
| 3xt estimate `EXTRA_FILE_S = 4` for every extra file (run_all_tests.py:795) | edit | `apply_fast` | `TEST_FILE_SECONDS.get(name, EXTRA_FILE_S)`; add `test_soak_six_slots.py: 150` (card `soak-six-slots-smoke-cap`) | low |
| Fallback "step failed in smoke, so run `--full`" for non-live paths | doc only (CLAUDE.md/GATE_SPEED mention) | sessions' habit; `gate_select.FULL_RE` unchanged | smoke result is the local verdict, CI the rest | low |

Card `gate-impact-direct-obeys-budget` item "estimates from measured gate_timing medians" is not done: that is new code, the freeze forbids it. `TEST_FILE_SECONDS` entries are the one-line equivalent.

## Item 3: steps dropped from the LOCAL gate, CI keeps them (ship b)
Steps 3k (sync parallel ship tests), 5b (layer tests), 4f (layer + live-writer), 4 (shard 1/5), 3dk (desk board), 3ad (auto-deploy), 3bk (backup snapshot).
| What | Lines | Callers | Replaced by | Risk |
|---|---|---|---|---|
| a `LOCAL_SKIP` tuple in `run_all_tests.py` consulted when the run is not a `--shard` run | about +6 | `sync.py ship` calls `run_all_tests.py` (no shard flag); CI `.github/workflows/ci.yml` calls `--shard K/N` | CI shards run the same steps before `mark-green` | medium: 5b and 4f are live-path layer tests, so a live-path ship loses a local pre-check. They stay in all 15 CI shards and green-only deploy blocks a red tip. Operator may veto 5b/4f only |

Gate time before/after is measured in ship (a)/(b) commit bodies.

## Item 4: steps 3sg, 3sig go with their hook
`test_stop_guard.py` (3sg) tests `stop_guard.py`, which BRIEF item 7 keeps, so **3sg stays**. `test_mts_signal.py` (3sig) tests `mts_signal.py`, which is a
SessionStart/UserPromptSubmit/PostToolUse/Stop hook and part of item 9 (signals/budget/exhaust): **3sig waits for the operator's item 9 answer**. No step is removed under item 4 now.

## Item 5: remove four hooks (ship c)
settings.json entries to drop: turn_meter x4 (SessionStart, UserPromptSubmit, PostToolUse, PreToolUse `*`), model_guard x1 (PreToolUse matcher list), offer_guard x1 and prereq_guard x1 (Stop).
| File | Lines | Callers (code) | Replaced by | Risk |
|---|---|---|---|---|
| scripts/dev/turn_meter.py | 484 | settings.json (4 entries); `boot_probe.maybe_spawn` is called from it; test_turn_meter.py, test_usage_bounds.py, test_boot_probe.py, test_hook_settings.py, test_hook_bench.py (fixture strings only); `mts_doctor.HOOK_FILES` names it; `run_all_tests.TEST_FILE_SECONDS` row; role_line.py docstring | nothing: it is warn-only since 10-23 and enforced nothing | low. `mts_doctor.HOOK_FILES` must drop the name (one line) |
| scripts/dev/model_guard.py | 598 | settings.json (1); test_model_guard.py, test_usage_bounds.py, test_role_loader.py (`import model_guard`, one test `test_loader_and_model_guard_agree...`), test_hook_bench.py (fixtures); role_loader.py and sync.py mention it in comments | nothing (warn-only). Open B200 closes | low. Remove one role_loader test and fixture names in test_hook_bench |
| scripts/dev/offer_guard.py | 120 | settings.json (1); test_offer_guard.py; run_extra_tests.py:22; prereq_guard.py imports nothing from it | nothing | low |
| scripts/dev/prereq_guard.py | 135 | settings.json (1); test_prereq_guard.py; run_extra_tests.py:21; strings in preship.py:78,96 (rule origin text) and tasks.py:604 docstring | nothing; the card `depends_on` field stays, only the session-end block goes | low |
| scripts/dev/boot_probe.py | 188 | only `turn_meter` (spawner) and test_boot_probe.py | none; its only trigger is gone | low (a signal nobody reads once the hook is gone) |
| scripts/dev/role_line.py | 85 | role_loader.py and turn_meter.py | **kept**: role_loader still uses it | - |
| tests: MyTradingSys/tests/test_turn_meter.py 531, test_model_guard.py 374, test_usage_bounds.py 206, test_boot_probe.py 129; scripts/dev/test_offer_guard.py 60, test_prereq_guard.py 71 | 1,371 | pytest shards / run_extra_tests list | go with their scripts | low; edits to test_hook_settings (MUST_BE_SYNC pair), test_hook_bench, test_role_loader |
Total about -1,900 lines with tests and doc lines in ARCHITECTURE/DEBUGGING/WORKERS/SUPERVISOR/MTS_DOCTOR/TRAFFIC_BUSTERS that name these hooks (history files, research reports and thinker notes are left as records).

## Item 6: trunk_lag, role_loader SubagentStart (ship d)
| What | Lines | Callers | Replaced by | Risk |
|---|---|---|---|---|
| trunk_lag.py: "87 behind" for a tree equal to trunk. Reproduced this session: tree "88 behind" while `git merge origin/fast-track` says Already up to date. Cause to be confirmed in code: it counts against the main checkout / uses a stale ref, not this tree's HEAD | 270 (fix or cut) | settings.json SessionStart + UserPromptSubmit; test_trunk_lag.py; run_extra_tests.py:23 | one-line fix to count `HEAD..origin/fast-track`; if not one line, drop the SessionStart fetch and keep the prompt hook | low |
| role_loader.py SubagentStart settings entry | 1 settings line | duplicates SessionStart + UserPromptSubmit | none; test_hook_settings may list it | low-medium: a subagent that needs a role banner loses it; CLAUDE.md step 5a is about sessions. Checked before removal |

## Item 7: keep
stop_guard, ci_watch, c_drive_guard, role_loader (shrink only), preship. No row.

## Item 8: scripts whose only caller is a doc (ship e)
Inventory lists 15. Static check on this tree shows 10 do have a code caller; they stay.
| Script | Lines | Real code caller found | Verdict |
|---|---|---|---|
| gq_after_reset.py | 8 | none (docs: handoff_history, REPORT_2026-10-18) | **delete**, no test |
| wait_pid.py | 16 | none (`coord_overhead.py` only filters the tool name "wait_pid") | **delete**, no test |
| worker_cost_report.py | 161 | none (docs: DEBUGGING.md x4) | **delete**; remove 4 doc lines in DEBUGGING.md; no test |
| soak_six_slots.py + test_soak_six_slots.py | 437 + test | run_extra_tests.py:32 (extra test list) only; doc: research/thinker/2026-10-22_six_slots.md | **delete both**: the test is the 135-164 s step-3xt timeout; one-off soak study. Operator may veto (it is not in the brief list) |
| deploy_untrack_backup.py | 200 | imported by MyTradingSys/tests/test_generated_files_untracked.py:16 | keep (test needs it) |
| traffic_report.py | 37 | imported by health_audit.py:17 | keep |
| task_state.py | 171 | imported by tasks.py:34 | keep |
| config_check.py | 56 | named in gate_select.py:35 FULL_RE group | keep |
| relay_board.py | 204 | codex_pack, codex_run, make_control_room, test_lane_health | keep (item 9 territory) |
| research_kit_lint, lab_query, interview_feed, funnel_report, indicator_audit_sample, wt_maint | 90/162/126/146/143/306 | each has a test in run_extra_tests / run_all_tests; research_kit_lint is BRIEF section 4 (never cut) | keep; moving to archive is not a deletion that lowers risk |
Net: -185 lines of scripts plus soak_six_slots/test about -600, and one 3xt timeout source.

## Item 9: multi-device and multi-login machinery
relay (relay_board 204, check_handoff), signals/budget/exhaust (mts_signal 930, exhaust 76, token_audit, traffic*), nuc_wake 105, cloud_setup 63, lane_health 469, about 3k lines.
**Operator decides** whether one machine is the plan. Nothing here is touched. Steps 3sig and 3lh would go with them.
