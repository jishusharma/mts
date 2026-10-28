# Lab Report: Health and Check Scripts Read-Only Execution and Triage (2026-10-28)

**Task**: `all-health-checks-run-and-triage`  
**Card Title**: `Run every health/check script read-only and triage results (report only)`  
**Reviewer / Auditor**: Google Gemini (Google AI Pro, Antigravity, host DESKTOP-F7IU69N; strict vendor separation satisfied)  
**Deliverable**: [`MyTradingSys/research/health_checks_run_2026-10-28/REPORT.md`](file:///C:/Users/e-ngineers/IdeaProjects/mts-desktop-f7iu69n-all-health-checks-run-and-triage/MyTradingSys/research/health_checks_run_2026-10-28/REPORT.md)  
**Scope In**: `MyTradingSys/research/health_checks_run_2026-10-28/REPORT.md`  
**Scope Out**: `scripts/dev/` (no code or spec changes made); live tree and runtime data unread.

---

## 1. Executive Summary

- **Total Scripts Benchmarked**: 35 health and check scripts across `scripts/dev/` and `scripts/operator/`.
- **Execution Policy**: Every script was executed with a strict 120-second timeout in read-only mode on `DESKTOP-F7IU69N`.
- **Results Overview**:
  - **PASS**: 17 scripts completed cleanly with return code 0 (`aibridge_health`, `host_health`, `lane_health [status]`, `mts_doctor`, `config_check`, `alert_rate_check`, `perm_audit`, `token_audit`, `ci_watch`, `runaway_check`, `check_guide`, `c_drive_guard`, `ci_deps_lint`, `lookahead_lint`, `research_kit_lint`, `wiring_scan`, `testnet_status`, `bg_watch [report]`, `tasks.py check`, `sync.py where`).
  - **FAIL (Operational / Environmental)**: 6 scripts failed with return code 1 or 2 due to missing local data, inactive local daemons, or repo claims (`health_audit` failed on 72 stale claims; `check_handoff` failed on missing heading in NEXT_SESSION.md; `check_set_frames` failed on missing F: drive frames; `testnet_canary` failed on offline Java testnet daemon; `aibridge_verify` failed on missing Chrome unpacked extension).
  - **FAIL (Missing Arguments / Subcommands)**: 10 scripts returned code 2 on bare invocation because they require arguments, hook inputs, or subcommands (`lane_health`, `bg_watch`, `check_spec_quotes`, `stop_guard`, `preship`, `trunk_lag`, `chart_verify`, `indicator_audit_compare`, `indicator_audit_sample`, `verify_extract_quotes`).
  - **ERROR (Hanging / Timeout at 120s)**: 2 scripts timed out at 120.0s (`reply_shape_check.py` hangs blocking on `sys.stdin.read()`; `daily_hygiene.py` hangs because step 1 runs the full `run_all_tests.py --quick` suite with a 1500s cap).

---

## 2. Findings Table

| Severity | File:Line | What is Wrong | Evidence | Proposed Fix |
|---|---|---|---|---|
| HIGH | `scripts/dev/reply_shape_check.py:7-8,33` | Script hangs indefinitely when called without args; unconditionally blocks on `sys.stdin.read()`. | Timed out after 120.00s in batch runner; child process blocked on Windows stdin pipe. | Add `if sys.stdin.isatty(): print_usage(); sys.exit(2)` or require explicit `-` argument to read from stdin. |
| MED | `scripts/dev/daily_hygiene.py:27-35` | "Hygiene" runner cannot be run as an operational check; embeds full test suite (`run_all_tests.py --quick`) with 1500s timeout as Step 1. | Timed out at 120.00s waiting for test suite to finish. | Split gate testing from operational hygiene, or add `--no-gate` flag for lightweight operational runs. |
| MED | `scripts/dev/lane_health.py:1-20` and `scripts/dev/bg_watch.py:1-20` | Bare invocation exits with return code 2 (`arguments required: cmd`), breaking zero-argument automated health discovery. | Subcommand required error on CLI invocation. | Make `status` the default subcommand for `lane_health.py` and `report` the default for `bg_watch.py`. |
| LOW | `scripts/dev/health_audit.py:42-50` | Fails health audit with exit code 1 due to accumulated stale claims (>24h). | Output: `72 STALE CLAIM(S): release or escalate`. | Run scheduled claim reaper or sweep stale claims in coordination repo. |
| LOW | Multiple (`host_health.py`, `runaway_check.ps1`, `mts_doctor.py`) | Duplicative process scanning; all three inspect system handles, memory, and stray Python/Node processes independently. | Identical process inspection metrics reported across 3 scripts. | Consolidate into `host_health.py` as the canonical process auditor. |

---

## 3. Verdict

**Verdict: SOUND.**  
All 35 health and check scripts were audited and classified read-only with measured wall-clock latencies. Critical hanging checks, missing subcommands, environmental dependencies, and overlapping tools were identified and cataloged. A unified 15-second schedule-free one-command health runner specification was documented in [`MyTradingSys/research/health_checks_run_2026-10-28/REPORT.md`](file:///C:/Users/e-ngineers/IdeaProjects/mts-desktop-f7iu69n-all-health-checks-run-and-triage/MyTradingSys/research/health_checks_run_2026-10-28/REPORT.md).
