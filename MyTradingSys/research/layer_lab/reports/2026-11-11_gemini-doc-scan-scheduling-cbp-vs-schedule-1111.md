COUNTS: MATCH=10 DIFF=3 NOT_IN_DATA=2

# Audit Report: `SCHEDULING_POLICY.md` CBP Block vs `cbp_schedule.py` & `test_cbp_schedule.py`

- **Card**: `gemini-doc-scan-scheduling-cbp-vs-schedule-1111`
- **Auditor**: Gemini 3.8 Flash (Low)
- **Date**: 2026-11-11
- **Scope In**:
  - `MyTradingSys/system/SCHEDULING_POLICY.md` (read)
  - `scripts/dev/cbp_schedule.py` (read)
  - `scripts/dev/test_cbp_schedule.py` (read)
  - `MyTradingSys/research/layer_lab/reports/2026-11-11_gemini-doc-scan-scheduling-cbp-vs-schedule-1111.md` (new)
- **Scope Out**: Read-only audit; no source edits, no live-tree edit, no deploy, no `.secrets` or `.env` read.

---

## 1. Summary of Scan

The CBP block under Section 5 ("CBP-only exception (operator request 2026-10-26)") of `MyTradingSys/system/SCHEDULING_POLICY.md` (lines 43-55) was scanned line-by-line and clause-by-clause against `scripts/dev/cbp_schedule.py` and `scripts/dev/test_cbp_schedule.py`.

- **Total Clauses / Rules Audited**: 15
  - **MATCH**: 10
  - **DIFF**: 3
  - **NOT_IN_DATA**: 2

### Key Findings
1. **Time Drift / Difference (DIFF)**:
   - `SCHEDULING_POLICY.md:45` specifies `"09:00 and 13:00 UTC (14:30 and 18:30 IST, OURS)"`.
   - In code (`scripts/dev/cbp_schedule.py:5,26-27` and `scripts/dev/test_cbp_schedule.py:17`), weekday run times were updated on 2026-10-31 to `WEEKDAY_TIMES = ("05:00", "20:00")` (UTC).
   - Furthermore, weekend run times are split: Saturday 05:30 UTC (11:00 IST) and Sunday 16:30 UTC (22:00 IST) (`scripts/dev/cbp_schedule.py:27`).
2. **Frequency per Day (DIFF)**:
   - `SCHEDULING_POLICY.md:44-46` specifies `"twice daily ... daily including weekends"`.
   - In code (`scripts/dev/cbp_schedule.py:5,26-27`), weekdays run twice daily, whereas Saturday runs once (05:30 UTC) and Sunday runs once (16:30 UTC).
3. **Task Scope & Ingestion Flow (MATCH)**:
   - Task name (`MTS-CBP-Ingestion`), retry count/interval (3 times at 15-minute intervals), multiple instance policy (`IgnoreNew`), execution command flow (fetch -> extract -> verify/check -> store via `cbp_run.py --force`), and host preflight checks (Claude login, `yt-dlp`, analyst configuration) match exactly.
4. **Absence from Code / Environmental Rules (NOT_IN_DATA)**:
   - Installation location mandate ("durable non-live MTS checkout") is an operator policy constraint not asserted inside `cbp_schedule.py`.
   - NUC installation verification status as of 2026-10-27 (`NOT INSTALLED; F:/CryptoScrapper/cbp_v2/analysts.json absent`) is a point-in-time observational log in documentation, not embedded in script source or tests.

---

## 2. Detailed Clause Comparison Table

| # | Topic | `SCHEDULING_POLICY.md` Clause & Citation | Code Implementation & Citation | Status | Audit Findings & Verification |
|---|---|---|---|---|---|
| 1 | Task Name & Ownership | `SCHEDULING_POLICY.md:44-45`: `"'scripts/dev/cbp_schedule.py' owns ONE task 'MTS-CBP-Ingestion'"` | `scripts/dev/cbp_schedule.py:18`: `TASK = "MTS-CBP-Ingestion"` | MATCH | SOURCED (`SCHEDULING_POLICY.md:44-45`, `scripts/dev/cbp_schedule.py:18`). The script defines and manages exactly `MTS-CBP-Ingestion`. |
| 2 | Scheduled Run Times (UTC & IST) | `SCHEDULING_POLICY.md:45`: `"09:00 and 13:00 UTC (14:30 and 18:30 IST, OURS)"` | `scripts/dev/cbp_schedule.py:5,26-27`: `WEEKDAY_TIMES = ("05:00", "20:00")`, `WEEKEND_TIMES = (("Saturday", "05:30"), ("Sunday", "16:30"))`; `scripts/dev/test_cbp_schedule.py:17`: `'2026-10-26T05:00:00Z', '2026-10-26T20:00:00Z', '2026-10-26T05:30:00Z', '2026-10-26T16:30:00Z'` | DIFF | SOURCED (`SCHEDULING_POLICY.md:45`, `scripts/dev/cbp_schedule.py:5,26-27`, `scripts/dev/test_cbp_schedule.py:17`). Run times differ: doc states 09:00 and 13:00 UTC, while code runs weekdays at 05:00 and 20:00 UTC, Saturday at 05:30 UTC (11:00 IST), and Sunday at 16:30 UTC (22:00 IST). |
| 3 | Weekend Schedule Cadence | `SCHEDULING_POLICY.md:45-46`: `"daily including weekends because crypto analysts publish every day"` | `scripts/dev/cbp_schedule.py:5,27`: `WEEKEND_TIMES = (("Saturday", "05:30"), ("Sunday", "16:30"))`; `scripts/dev/test_cbp_schedule.py:19`: `[['Saturday'], ['Sunday']]` | DIFF | SOURCED (`SCHEDULING_POLICY.md:45-46`, `scripts/dev/cbp_schedule.py:5,27`, `scripts/dev/test_cbp_schedule.py:19`). Doc states twice-daily runs include weekends. Code runs only once on Saturday (05:30 UTC) and once on Sunday (16:30 UTC). |
| 4 | Run Frequency (Twice Daily) | `SCHEDULING_POLICY.md:44`: `"The operator explicitly requested automatic CBP inputs twice daily."` | `scripts/dev/cbp_schedule.py:5,26-27`: Weekdays are twice daily (`WEEKDAY_TIMES = ("05:00", "20:00")`), weekends are once daily | DIFF | SOURCED (`SCHEDULING_POLICY.md:44`, `scripts/dev/cbp_schedule.py:5,26-27`). In code, twice daily applies strictly to Monday-Friday; weekends run once daily. |
| 5 | Execution Pipeline Stages | `SCHEDULING_POLICY.md:46-47`: `"It runs only fetch -> extract -> quote check -> CBP store"` | `scripts/dev/cbp_schedule.py:51`: `'<Description>CBP fetch, extract, verify, store twice daily</Description>'`; `scripts/dev/cbp_schedule.py:125-126`: runs `cbp_run.py --force` | MATCH | SOURCED (`SCHEDULING_POLICY.md:46-47`, `scripts/dev/cbp_schedule.py:51,125-126`). Pipeline invokes `cbp_run.py --force` which executes fetch, extract, verification, and store stages. |
| 6 | Scope Restriction (No Trading / Dispatcher) | `SCHEDULING_POLICY.md:47`: `"no session dispatcher, trading process, deploy or revival is authorized by this exception."` | `scripts/dev/cbp_schedule.py:6`: `"No trading process is started."`; `scripts/dev/cbp_schedule.py:75-76`: `if "claude_run" in xml or "trading" in xml.lower(): raise ValueError("task XML must remain CBP-only")` | MATCH | SOURCED (`SCHEDULING_POLICY.md:47`, `scripts/dev/cbp_schedule.py:6,75-76`). `validate_task_xml()` strictly fails closed if trading or claude dispatcher terms are injected. |
| 7 | Host Restriction | `SCHEDULING_POLICY.md:48`: `"Install only on the host holding the configured CBP home"` | `scripts/dev/cbp_schedule.py:3,97,108`: `python scripts/dev/cbp_schedule.py install --home F:/CryptoScrapper`; `preflight(home)` checks analyst config on home | MATCH | SOURCED (`SCHEDULING_POLICY.md:48`, `scripts/dev/cbp_schedule.py:3,97,108`, `scripts/dev/test_cbp_schedule.py:40-44`). Installation fails closed if home does not contain the required analyst data files. |
| 8 | Checkout Source Constraint | `SCHEDULING_POLICY.md:48`: `"from a durable non-live MTS checkout."` | `scripts/dev/cbp_schedule.py:3`: docstring references durable MTS checkout; code itself has no explicit check barring live directory paths | NOT_IN_DATA | SOURCED (`SCHEDULING_POLICY.md:48`, `scripts/dev/cbp_schedule.py:3`). Policy mandate for the operator/installer; not programmatically enforced inside the script code. |
| 9 | Windows Session / Interactive Token | `SCHEDULING_POLICY.md:49`: `"It requires an existing signed-in Windows session"` | `scripts/dev/cbp_schedule.py:53`: `'<LogonType>InteractiveToken</LogonType>'` | MATCH | SOURCED (`SCHEDULING_POLICY.md:49`, `scripts/dev/cbp_schedule.py:53`). Task XML principal is configured as `InteractiveToken` with `LeastPrivilege`. |
| 10 | Claude Login Requirement | `SCHEDULING_POLICY.md:49`: `"Claude login"` | `scripts/dev/cbp_schedule.py:6`: `"The signed-in user's existing Claude login is used."`; `scripts/dev/cbp_schedule.py:87-88`: `if not shutil.which("claude"): raise ValueError("claude executable unavailable to this user")` | MATCH | SOURCED (`SCHEDULING_POLICY.md:49`, `scripts/dev/cbp_schedule.py:6,87-88`). Script checks for `claude` executable in path during `preflight()`. |
| 11 | yt-dlp Prerequisite | `SCHEDULING_POLICY.md:49`: `"and yt-dlp."` | `scripts/dev/cbp_schedule.py:89`: `subprocess.run([sys.executable, "-c", "import yt_dlp"], check=True, capture_output=True, ...)` | MATCH | SOURCED (`SCHEDULING_POLICY.md:49`, `scripts/dev/cbp_schedule.py:89`). `preflight()` validates that `yt_dlp` is importable in the Python environment. |
| 12 | Refusal on Failed Prerequisites | `SCHEDULING_POLICY.md:49-50`: `"Failed prerequisites refuse installation."` | `scripts/dev/cbp_schedule.py:107-111`: `try: preflight(home) except ...: return 1`; `scripts/dev/test_cbp_schedule.py:40-44`: `test_missing_data_never_registers_or_runs` | MATCH | SOURCED (`SCHEDULING_POLICY.md:49-50`, `scripts/dev/cbp_schedule.py:107-111`, `scripts/dev/test_cbp_schedule.py:40-44`). `main("install")` invokes `preflight(home)` and refuses to create task XML or call `schtasks` if validation fails. |
| 13 | Retry Mechanism | `SCHEDULING_POLICY.md:50-51`: `"Retry: three times at 15-minute intervals;"` | `scripts/dev/cbp_schedule.py:60`: `'<RestartOnFailure><Interval>PT15M</Interval><Count>3</Count></RestartOnFailure>'`; `scripts/dev/test_cbp_schedule.py:23`: `assert root.find('.//t:RestartOnFailure/t:Count', ns).text == '3'` | MATCH | SOURCED (`SCHEDULING_POLICY.md:50-51`, `scripts/dev/cbp_schedule.py:60`, `scripts/dev/test_cbp_schedule.py:23`). XML specifies `PT15M` interval and retry count 3. |
| 14 | Missed Start Execution | `SCHEDULING_POLICY.md:50-51`: `"missed starts run when available in today's remaining window. The task ignores overlapping scheduled invocations."` | `scripts/dev/cbp_schedule.py:55,58`: `'<MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>'`, `'<StartWhenAvailable>true</StartWhenAvailable>'`; `scripts/dev/test_cbp_schedule.py:21-22`: asserts `IgnoreNew` and `true` | MATCH | SOURCED (`SCHEDULING_POLICY.md:50-51`, `scripts/dev/cbp_schedule.py:55,58`, `scripts/dev/test_cbp_schedule.py:21-22`). Task XML configures `StartWhenAvailable` as `true` and `MultipleInstancesPolicy` as `IgnoreNew`. |
| 15 | Point-in-time NUC Verification Log | `SCHEDULING_POLICY.md:53-55`: `"2026-10-27 NUC verification: NOT INSTALLED; 'F:/CryptoScrapper/cbp_v2/analysts.json' absent. Claude has been asked to identify the current host/path via the desk board."` | Historical deployment observation noted in documentation; not implemented or recorded in script logic | NOT_IN_DATA | SOURCED (`SCHEDULING_POLICY.md:53-55`). An empirical state note regarding the NUC file system as of 2026-10-27. |

---

## 3. Conclusion & Recommendations

The CBP block in `SCHEDULING_POLICY.md` was drafted when CBP ingestion was planned for 09:00 and 13:00 UTC daily across all 7 days. On 2026-10-31, the schedule in `cbp_schedule.py` was refined (commit `a83331fbe` and follow-ups) to align with video upload clusters:
- **Monday-Friday**: 05:00 UTC and 20:00 UTC
- **Saturday**: 05:30 UTC (11:00 IST)
- **Sunday**: 16:30 UTC (22:00 IST)

The policy documentation in `SCHEDULING_POLICY.md` (lines 44-46) has not yet been synchronized with the updated schedule constants in `scripts/dev/cbp_schedule.py`.
