COUNTS: MATCH=7 DIFF=3 NOT_IN_DATA=0

# Audit Report: `MyTradingSys/system/MTS_DOCTOR.md` (Flags and Check Names) vs `mts_doctor.py` and Tests

- **Card**: `gemini-doc-scan-mts-doctor-flags-vs-code-1111`
- **Auditor**: Gemini 3.8 Flash (Low)
- **Date**: 2026-11-11
- **Scope In**:
  - `MyTradingSys/system/MTS_DOCTOR.md` (read)
  - `scripts/dev/mts_doctor.py` (read)
  - `scripts/dev/test_mts_doctor.py` (read)
  - `MyTradingSys/research/layer_lab/reports/2026-11-11_gemini-doc-scan-mts-doctor-flags-vs-code-1111.md` (new)
- **Scope Out**: Read-only audit; no edits to source files, no live-tree edit, no deploy, no `.secrets` or `.env` read.

---

## 1. Summary of Scan

Evaluated 10 testable claims from `MyTradingSys/system/MTS_DOCTOR.md` covering CLI execution flags, checklist check names, status reporting semantics, and check definitions against `scripts/dev/mts_doctor.py` and `scripts/dev/test_mts_doctor.py`.

Audit outcome across 10 claims:
- **MATCH (7)**:
  1. Default CLI `--hours 72` flag and output destination `MyTradingSys/research/mts_doctor/REPORT_<utc date>.md` (`MTS_DOCTOR.md:8` vs `mts_doctor.py:29,1008-1009,1043-1044,1059`).
  2. `--no-process` execution flag disables network calls and limits execution to AI health and local checks (`MTS_DOCTOR.md:9` vs `mts_doctor.py:861-862,870-877,1012-1019,1062,1075`).
  3. Report Line 1 format strictly outputs `HEALTH: GREEN` or `HEALTH: <n> WARN: <names>`, with check states `OK` / `WARN` / `unavailable: <why>` without failing or editing (`MTS_DOCTOR.md:13` vs `mts_doctor.py:881-884,887-890,1026` and `test_mts_doctor.py:274-281`).
  4. Checklist check `SIZE-HEADROOM` verifies files against size caps with 3% headroom (`MTS_DOCTOR.md:16` vs `mts_doctor.py:368,386-412` and `test_mts_doctor.py:158-170`).
  5. Checklist check `CI-REVERT` verifies red runs on fast-track recovered within 10 min and trunk is not red now (`MTS_DOCTOR.md:17` vs `mts_doctor.py:369,423-452` and `test_mts_doctor.py:176-194`).
  6. Checklist check `HOOK-REG` verifies main checkout registration of `role_loader` and `ci_watch` and under 50 commits behind trunk (`MTS_DOCTOR.md:19` vs `mts_doctor.py:371,373,527-545` and `test_mts_doctor.py:245-267`).
  7. Checklist check `DISK` checks for 15 GB free space on repo drive (`MTS_DOCTOR.md:20` vs `mts_doctor.py:372,547-556` and `test_mts_doctor.py:269-272`).
- **DIFF (3)**:
  1. Checklist check `SHIP-TIME` (`MTS_DOCTOR.md:18` vs `mts_doctor.py:370,484-524` and `test_mts_doctor.py:216-234`): `MTS_DOCTOR.md:18` claims "ship and gate wall time, 72 h, max under 15 min", whereas `mts_doctor.py:484` specifies default `hours=24` (not 72 h), `SHIP_MAX_S = 120` seconds (2 min) for ship wall median or p90 (`mts_doctor.py:370,522-523`), and no 15 min threshold is implemented.
  2. Checklist check names list (`MTS_DOCTOR.md:14-22` vs `mts_doctor.py:375,856-877`): `MTS_DOCTOR.md:14-22` defines a checklist table of only 7 checks (`SIZE-HEADROOM`, `CI-REVERT`, `SHIP-TIME`, `HOOK-REG`, `DISK`, `STALE-CLAIMS`, `SCRATCH-TRACKED`). `mts_doctor.py:375` defines 16 checklist checks in `CHECK_NAMES` (`SIZE-HEADROOM`, `CI-REVERT`, `SHIP-TIME`, `HOOK-REG`, `DISK`, `CONTEXT-GAP`, `WAITING-ON-OPERATOR`, `BROADCAST`, `STALE-CLAIMS`, `SCRATCH-TRACKED`, `CONFLICT-OPEN`, `ASK-GAPS`, `SUPERVISOR-IDLE`, `OF-RESTARTS`, `OF-STALE`, `GIT-HUNG`), leaving 9 checks undocumented in `MTS_DOCTOR.md`'s Checklist table.
  3. CLI argparse options (`MTS_DOCTOR.md:8-9` vs `mts_doctor.py:1058-1065`): `MTS_DOCTOR.md:8-9` documents only `python scripts/dev/mts_doctor.py [--hours 72]` and `--no-process`, but fails to document the CLI flags `--heal`, `--apply`, `--memory`, and `--out` implemented in `mts_doctor.py:1058-1065` (though `--heal` and `--apply` are briefly mentioned in header docstrings).
- **NOT_IN_DATA (0)**: None; all 10 evaluated claims have corresponding code or definitions in `mts_doctor.py` and `test_mts_doctor.py`.

---

## 2. Clause Comparison Table

| # | Documented Claim in `MTS_DOCTOR.md` | Code & Test Implementation | Status | Audit Findings & Verification |
|---|---|---|---|---|
| 1 | `MTS_DOCTOR.md:8`: `python scripts/dev/mts_doctor.py [--hours 72]` writes `MyTradingSys/research/mts_doctor/REPORT_<utc date>.md` | `scripts/dev/mts_doctor.py:29,1008-1009,1043-1044,1059`: `OUT_REL = "MyTradingSys/research/mts_doctor"`; `ap.add_argument("--hours", type=int, default=72)`; writes `REPORT_<day>.md`; `scripts/dev/test_mts_doctor.py:53` | MATCH | SOURCED (`MyTradingSys/system/MTS_DOCTOR.md:8`, `scripts/dev/mts_doctor.py:29,1008-1009,1043-1044,1059`, `scripts/dev/test_mts_doctor.py:53`). Flag `--hours` defaults to 72, destination directory is `MyTradingSys/research/mts_doctor`, and file is `REPORT_<day>.md`. |
| 2 | `MTS_DOCTOR.md:9`: `--no-process = AI health only (no network)` | `scripts/dev/mts_doctor.py:861-862,870-877,1012-1019,1062,1075`: skips `health_audit.build` and returns `"unavailable", "skipped (--no-process, no network)"` for network checks; `scripts/dev/test_mts_doctor.py:36,51` | MATCH | SOURCED (`MyTradingSys/system/MTS_DOCTOR.md:9`, `scripts/dev/mts_doctor.py:861-862,870-877,1012-1019,1062,1075`, `scripts/dev/test_mts_doctor.py:36,51`). `--no-process` bypasses external queries and executes only local repo checks. |
| 3 | `MTS_DOCTOR.md:13`: `Line 1 is HEALTH: GREEN or HEALTH: <n> WARN: <names>. Each check is OK / WARN / unavailable: <why>; none fails or edits.` | `scripts/dev/mts_doctor.py:881-884,887-890,1026`: `health_line` formats `HEALTH: GREEN` or `HEALTH: <n> WARN: ...`; `scripts/dev/test_mts_doctor.py:274-281` | MATCH | SOURCED (`MyTradingSys/system/MTS_DOCTOR.md:13`, `scripts/dev/mts_doctor.py:881-884,887-890,1026`, `scripts/dev/test_mts_doctor.py:274-281`). Status format matches exactly; checks return `OK` / `WARN` / `unavailable`. |
| 4 | `MTS_DOCTOR.md:16`: `SIZE-HEADROOM`: `CLAUDE.md and each role file keep 3% under their cap (caps read from the tests)` | `scripts/dev/mts_doctor.py:368,386-412`: `HEADROOM_MIN_PCT = 3`; imports `SIZE_CAPS` from `test_integrity.py` and `BUDGET` from `test_role_budget.py`; `scripts/dev/test_mts_doctor.py:158-170` | MATCH | SOURCED (`MyTradingSys/system/MTS_DOCTOR.md:16`, `scripts/dev/mts_doctor.py:368,386-412`, `scripts/dev/test_mts_doctor.py:158-170`). Headroom threshold is 3% and caps are loaded dynamically from test files without hardcoding. |
| 5 | `MTS_DOCTOR.md:17`: `CI-REVERT`: `red runs on fast-track went green within 10 min; trunk is not red now (red now: python scripts/dev/ci_revert.py prints the revert plan...)` | `scripts/dev/mts_doctor.py:369,423-452`: `CI_FIX_MIN = 10`; warns if red streak > `CI_FIX_MIN` or red now; suggests `ci_revert.py`; `scripts/dev/test_mts_doctor.py:176-194` | MATCH | SOURCED (`MyTradingSys/system/MTS_DOCTOR.md:17`, `scripts/dev/mts_doctor.py:369,423-452`, `scripts/dev/test_mts_doctor.py:176-194`). Evaluates GitHub workflow runs, flagging streaks taking >10 minutes to turn green and active red trunk status. |
| 6 | `MTS_DOCTOR.md:18`: `SHIP-TIME`: `ship and gate wall time, 72 h, max under 15 min (runtime_data/gate_timing.jsonl)` | `scripts/dev/mts_doctor.py:370,484-524`: `SHIP_MAX_S = 120`; `def ship_time(log, now=None, hours=24)`; warns if `max(_median(ships), _p90(ships)) > SHIP_MAX_S`; `scripts/dev/test_mts_doctor.py:216-234` | DIFF | SOURCED (`MyTradingSys/system/MTS_DOCTOR.md:18`, `scripts/dev/mts_doctor.py:370,484-524`, `scripts/dev/test_mts_doctor.py:216-234`). Doc claims 72 h window and max under 15 min threshold, but code uses `hours=24` window and `SHIP_MAX_S = 120`s (2 min) for median/p90 ship wall time. |
| 7 | `MTS_DOCTOR.md:19`: `HOOK-REG`: `main checkout registers role_loader and ci_watch and is under 50 commits behind trunk` | `scripts/dev/mts_doctor.py:371,373,527-545`: `HOOKS_BEHIND_MAX = 50`; `HOOK_NAMES = ("role_loader", "ci_watch")`; `scripts/dev/test_mts_doctor.py:245-267` | MATCH | SOURCED (`MyTradingSys/system/MTS_DOCTOR.md:19`, `scripts/dev/mts_doctor.py:371,373,527-545`, `scripts/dev/test_mts_doctor.py:245-267`). Validates that both hooks are present in `.claude/settings.json` and main checkout is <= 50 commits behind trunk. |
| 8 | `MTS_DOCTOR.md:20`: `DISK`: `15 GB free on the repo drive` | `scripts/dev/mts_doctor.py:372,547-556`: `DISK_MIN_GB = 15`; warns if free GB < `DISK_MIN_GB`; `scripts/dev/test_mts_doctor.py:269-272` | MATCH | SOURCED (`MyTradingSys/system/MTS_DOCTOR.md:20`, `scripts/dev/mts_doctor.py:372,547-556`, `scripts/dev/test_mts_doctor.py:269-272`). Checks disk usage against the 15 GB lower bound threshold. |
| 9 | `MTS_DOCTOR.md:14-22`: Checklist table enumerates 7 checks (`SIZE-HEADROOM`, `CI-REVERT`, `SHIP-TIME`, `HOOK-REG`, `DISK`, `STALE-CLAIMS`, `SCRATCH-TRACKED`) | `scripts/dev/mts_doctor.py:375,856-877`: `CHECK_NAMES` defines 16 checks: adds `CONTEXT-GAP`, `WAITING-ON-OPERATOR`, `BROADCAST`, `CONFLICT-OPEN`, `ASK-GAPS`, `SUPERVISOR-IDLE`, `OF-RESTARTS`, `OF-STALE`, `GIT-HUNG`; `scripts/dev/test_mts_doctor.py:280,364,378,386,410` | DIFF | SOURCED (`MyTradingSys/system/MTS_DOCTOR.md:14-22`, `scripts/dev/mts_doctor.py:375,856-877`, `scripts/dev/test_mts_doctor.py:280,364,378,386,410`). The doc checklist table lists 7 checks, while code registers 16 checks in `CHECK_NAMES` and executes them in `checklist()`. |
| 10 | `MTS_DOCTOR.md:8-9`: CLI options documented as `python scripts/dev/mts_doctor.py [--hours 72]` and `--no-process` | `scripts/dev/mts_doctor.py:1058-1065`: `ap.add_argument` defines `--hours`, `--memory`, `--out`, `--no-process`, `--heal`, and `--apply` | DIFF | SOURCED (`MyTradingSys/system/MTS_DOCTOR.md:8-9`, `scripts/dev/mts_doctor.py:1058-1065`). `MTS_DOCTOR.md:8-9` omits `--heal`, `--apply`, `--memory`, and `--out` from the CLI usage synopsis. |
