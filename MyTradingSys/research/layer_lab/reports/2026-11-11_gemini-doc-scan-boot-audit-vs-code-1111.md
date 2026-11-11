COUNTS: MATCH=8 DIFF=0 NOT_IN_DATA=0

# Audit Report: `scripts/dev/boot_audit.py` Docstring vs Code and Test

- **Card**: `gemini-doc-scan-boot-audit-vs-code-1111`
- **Auditor**: Gemini 3.8 Flash (Low)
- **Date**: 2026-11-11
- **Scope In**:
  - `scripts/dev/boot_audit.py` (read)
  - `scripts/dev/test_boot_audit.py` (read)
  - `MyTradingSys/research/layer_lab/reports/2026-11-11_gemini-doc-scan-boot-audit-vs-code-1111.md` (new)
- **Scope Out**: Read-only audit; no edits to source files, no live-tree edit, no deploy, no `.secrets` or `.env` read.

---

## 1. Summary of Scan

Evaluated 8 testable clauses from the module docstring of `scripts/dev/boot_audit.py` (lines 1-16) against implementation code in `scripts/dev/boot_audit.py` and unit tests in `scripts/dev/test_boot_audit.py`.

Audit outcome across 8 claims:
- **MATCH (8)**: Implementation and test coverage precisely verify all 8 documented claims:
  1. Default CLI execution (`python scripts/dev/boot_audit.py`) outputs a table of every boot/logon item with owner and verdict (report only).
  2. `--json` CLI execution prints the collected boot/logon item rows as formatted JSON.
  3. `--fix` CLI execution acts on MTS-owned items only: REMOVE -> delete, DELAY -> logon delay + no catch-up start.
  4. KEEP verdict applies to authorised MTS items or Windows / operator / third-party owned items, and `--fix` never touches these.
  5. DELAY verdict applies to needed but unapproved MTS items (specifically `AIBridge-Agent`), configuring a 3-minute logon delay (`PT3M`) with no boot catch-up start.
  6. REMOVE verdict applies to unauthorised MTS tasks or Run values, which are deleted by `--fix`.
  7. Owner is MTS only for names matching `MTS_TASK_RE` / `MTS_RUN_VALUES` or commands matching repo script patterns (`MTS_CMD_RE` / `REPO_CMD_RE`); third-party items that are known heavy are flagged ASK.
  8. Windows boot-time events (Diagnostics-Performance event 100) report the boot duration numbers, or state that an administrator is required if unreadable.
- **DIFF (0)**: None.
- **NOT_IN_DATA (0)**: None.

---

## 2. Clause Comparison Table

| # | Documented Claim in `boot_audit.py` Docstring | Code & Test Implementation | Status | Audit Findings & Verification |
|---|---|---|---|---|
| 1 | `scripts/dev/boot_audit.py:4`: `python scripts/dev/boot_audit.py table of every boot/logon item with owner and verdict (report only)` | `scripts/dev/boot_audit.py:203-212,228,232-233`: `render(rows)` builds tabular output with columns `kind`, `item`, `owner`, `verdict`, and `detail / reason`; `main()` invokes `collect()` and prints `render(rows)` without `--fix` or `--json`; `scripts/dev/test_boot_audit.py:14-17` | MATCH | SOURCED (`scripts/dev/boot_audit.py:4,203-212,228,232-233`, `scripts/dev/test_boot_audit.py:14-17`). Default CLI runs in report mode, rendering kind, item, owner, and verdict. |
| 2 | `scripts/dev/boot_audit.py:6`: `python scripts/dev/boot_audit.py --json the same rows as JSON` | `scripts/dev/boot_audit.py:223,229-230`: `ap.add_argument("--json", action="store_true")`; `if a.json: print(json.dumps([{k: v for k, v in r.items() if k != "raw"} for r in rows], indent=1))` | MATCH | SOURCED (`scripts/dev/boot_audit.py:6,223,229-230`). Passing `--json` serializes collected rows excluding internal `"raw"` dict directly to JSON. |
| 3 | `scripts/dev/boot_audit.py:5`: `python scripts/dev/boot_audit.py --fix act on MTS-owned items only: REMOVE -> delete, DELAY -> logon delay + no catch-up start` | `scripts/dev/boot_audit.py:170-179,182-200,234-242`: `plan_fix()` only processes `r["owner"] == "MTS"`; generates `remove_task`/`remove_run` for REMOVE and `delay_task` for DELAY; `apply_fix()` executes deletions and delay configurations; `scripts/dev/test_boot_audit.py:46-51,53-55` | MATCH | SOURCED (`scripts/dev/boot_audit.py:5,170-179,182-200,234-242`, `scripts/dev/test_boot_audit.py:46-51,53-55`). `--fix` operates strictly on MTS-owned items, executing task unregistration, registry value deletion, and logon delay setting. |
| 4 | `scripts/dev/boot_audit.py:9`: `KEEP authorised MTS item, or Windows / operator / third-party owned. --fix never touches these.` | `scripts/dev/boot_audit.py:40-41,43-44,48-49,171-172,177`: `classify()` assigns `KEEP` to non-MTS or authorised MTS tasks/runs; `plan_fix()` skips non-MTS items (`if r["owner"] != "MTS": continue`) and does not generate actions for `KEEP`; `scripts/dev/test_boot_audit.py:21-23,32-34,38-43,46-51` | MATCH | SOURCED (`scripts/dev/boot_audit.py:9,40-41,43-44,48-49,171-172,177`, `scripts/dev/test_boot_audit.py:21-23,32-34,38-43,46-51`). KEEP items are excluded from modification by `--fix`. |
| 5 | `scripts/dev/boot_audit.py:10-11`: `DELAY ours and needed but not authorised in the policy (AIBridge-Agent: open policy question): starts 3 min after logon, and a missed run is not caught up at boot.` | `scripts/dev/boot_audit.py:25,29,45-46,135,177-178,194-197`: `DELAY_ISO = "PT3M"`; `DELAY_TASK_RE = re.compile(r"^AIBridge-Agent$")`; sets logon trigger delay to `DELAY_ISO` and `Settings.StartWhenAvailable = $false`; `scripts/dev/test_boot_audit.py:29-30,46-51,53-55` | MATCH | SOURCED (`scripts/dev/boot_audit.py:10-11,25,29,45-46,135,177-178,194-197`, `scripts/dev/test_boot_audit.py:29-30,46-51,53-55`). Configures exactly `PT3M` (3 minutes) logon delay and disables catch-up on boot (`StartWhenAvailable = False`). |
| 6 | `scripts/dev/boot_audit.py:12`: `REMOVE ours and not authorised (any other MTS-* task or Run value): deleted by --fix.` | `scripts/dev/boot_audit.py:47,50,175-176,184-193`: Unrecognised MTS tasks and Run values receive verdict `REMOVE`; `plan_fix()` queues `remove_task` and `remove_run`; `apply_fix()` unregisters the scheduled task or deletes the registry value; `scripts/dev/test_boot_audit.py:25-28,35-37,46-51` | MATCH | SOURCED (`scripts/dev/boot_audit.py:12,47,50,175-176,184-193`, `scripts/dev/test_boot_audit.py:25-28,35-37,46-51`). Verified by unit tests for tasks and registry Run values. |
| 7 | `scripts/dev/boot_audit.py:13-14`: `Owner is MTS only for names in MTS_TASK_RE / MTS_RUN_VALUES or a command that runs a repo script; everything else is never modified. Third-party items that are known heavy are flagged ASK (the operator's call, not ours).` | `scripts/dev/boot_audit.py:26-27,30-33,38-41,134,140,144,149,207-209`: Matches `MTS_TASK_RE`/`MTS_CMD_RE` for tasks, `MTS_RUN_VALUES`/`REPO_CMD_RE` for runs; non-MTS items matched by `HEAVY_RE` set `ask=True` and render with `*`; `scripts/dev/test_boot_audit.py:38-43,58-62` | MATCH | SOURCED (`scripts/dev/boot_audit.py:13-14,26-27,30-33,38-41,134,140,144,149,207-209`, `scripts/dev/test_boot_audit.py:38-43,58-62`). Non-MTS heavy items receive `ask=True` and are excluded from action in `plan_fix()`. |
| 8 | `scripts/dev/boot_audit.py:15`: `The Windows boot-time events (Diagnostics-Performance 100, 101-110) need an administrator; without one the audit says so.` | `scripts/dev/boot_audit.py:120-126,233`: `boot_times()` executes `Get-WinEvent` for LogName `Microsoft-Windows-Diagnostics-Performance/Operational` with Id 100; on exception catches and returns `"UNREADABLE: no boot events visible to this user (log empty or needs an administrator): ..."` | MATCH | SOURCED (`scripts/dev/boot_audit.py:15,120-126,233`). Handled via PowerShell try/catch block formatting boot timing metrics or returning unreadable error message naming administrator requirement. |
