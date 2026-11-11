counts: MATCH=6 DIFF=0 NOT_IN_DATA=0 (sum 6)

# Gemini Blind Read: scripts/dev/cbp_schedule.py against its docstring and test

- Date: 2026-11-11
- Card: `gemini-blind-read-cbp-schedule-docstring-1111`
- Scope In:
  - `scripts/dev/cbp_schedule.py` (read)
  - `scripts/dev/test_cbp_schedule.py` (read)
  - `MyTradingSys/research/layer_lab/reports/2026-11-11_gemini-blind-read-cbp-schedule-docstring-1111.md` (new)
- Scope Out: no edit to the source files; no live-tree edit, no deploy, no `.secrets` or `.env` read; read-only audit

## Summary Table

| Clause # | Docstring Clause Requirement | Implementation Status | Implementation Code (`scripts/dev/cbp_schedule.py`) | Test Verification (`scripts/dev/test_cbp_schedule.py`) |
|---|---|---|---|---|
| 1 | Operator-authorized CBP-only twice-daily Windows task installation/status/removal | MATCH | SOURCED `scripts/dev/cbp_schedule.py:1` `"""Install/status/remove the operator-authorized CBP-only twice-daily Windows task.`<br>SOURCED `scripts/dev/cbp_schedule.py:18` `TASK = "MTS-CBP-Ingestion"`<br>SOURCED `scripts/dev/cbp_schedule.py:94` `ap.add_argument("command", choices=("install", "run", "status", "remove", "check", "dry-run"))`<br>SOURCED `scripts/dev/cbp_schedule.py:103-106` calls `schtasks /Query` or `schtasks /Delete` for `status` / `remove`<br>SOURCED `scripts/dev/cbp_schedule.py:117-120` writes XML and runs `schtasks /Create /TN MTS-CBP-Ingestion /XML ... /F` for `install`<br>SOURCED `scripts/dev/cbp_schedule.py:75-76` enforces `claude_run` and `trading` are not present in XML | SOURCED `scripts/dev/test_cbp_schedule.py:1` `"""CBP task contract: UTC triggers, retry, one writer, fail-closed installation."""`<br>SOURCED `scripts/dev/test_cbp_schedule.py:20` calls `schedule.validate_task_xml(xml)`<br>SOURCED `scripts/dev/test_cbp_schedule.py:40-44` tests fail-closed `install` via `test_missing_data_never_registers_or_runs` |
| 2 | Install CLI command and home parameter syntax: `python scripts/dev/cbp_schedule.py install --home F:/CryptoScrapper` | MATCH | SOURCED `scripts/dev/cbp_schedule.py:3-4` `Install from a durable MTS checkout on the host holding CBP data:\n    python scripts/dev/cbp_schedule.py install --home F:/CryptoScrapper`<br>SOURCED `scripts/dev/cbp_schedule.py:94-97` CLI argument parsing supports `install` and `--home` (`home = (a.home or cbp.default_cbp_home()).resolve()`) | SOURCED `scripts/dev/test_cbp_schedule.py:42` tests CLI dispatch: `schedule.main(['install', '--home', str(tmp_path)])` |
| 3 | Weekday task times (OURS): Mon-Fri 05:00 and 20:00 UTC | MATCH | SOURCED `scripts/dev/cbp_schedule.py:5` `Task times (OURS): Mon-Fri 05:00 and 20:00 UTC`<br>SOURCED `scripts/dev/cbp_schedule.py:26` `WEEKDAY_TIMES = ("05:00", "20:00")`<br>SOURCED `scripts/dev/cbp_schedule.py:47` `triggers = "".join(trigger(DAYS[:5], t) for t in WEEKDAY_TIMES)` | SOURCED `scripts/dev/test_cbp_schedule.py:16-17` asserts StartBoundary contains `'2026-10-26T05:00:00Z', '2026-10-26T20:00:00Z'`<br>SOURCED `scripts/dev/test_cbp_schedule.py:18-19` asserts `weeks == [['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']] * 2 + ...`<br>SOURCED `scripts/dev/test_cbp_schedule.py:31-32` tests local IST day shift: `assert days[0] == ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']` (05:00 UTC = 10:30 IST) and `assert days[1] == ['Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']` (20:00 UTC = 01:30 IST) |
| 4 | Weekend task times (OURS): Saturday 05:30 UTC (11:00 IST), Sunday 16:30 UTC (22:00 IST) | MATCH | SOURCED `scripts/dev/cbp_schedule.py:5` `Saturday 05:30 UTC (11:00 IST), Sunday 16:30 UTC (22:00 IST).`<br>SOURCED `scripts/dev/cbp_schedule.py:27` `WEEKEND_TIMES = (("Saturday", "05:30"), ("Sunday", "16:30"))`<br>SOURCED `scripts/dev/cbp_schedule.py:48` `triggers += "".join(trigger((day,), t) for day, t in WEEKEND_TIMES)` | SOURCED `scripts/dev/test_cbp_schedule.py:16-17` asserts StartBoundary includes `'2026-10-26T05:30:00Z', '2026-10-26T16:30:00Z'`<br>SOURCED `scripts/dev/test_cbp_schedule.py:19` asserts weekend days `[['Saturday'], ['Sunday']]`<br>SOURCED `scripts/dev/test_cbp_schedule.py:33` asserts `days[2:] == [['Saturday'], ['Sunday']]` for IST (05:30 UTC / 11:00 IST, 16:30 UTC / 22:00 IST stay on the same day) |
| 5 | No trading process is started | MATCH | SOURCED `scripts/dev/cbp_schedule.py:6` `No trading process is started.`<br>SOURCED `scripts/dev/cbp_schedule.py:75-76` `if "claude_run" in xml or "trading" in xml.lower(): raise ValueError("task XML must remain CBP-only")`<br>SOURCED `scripts/dev/cbp_schedule.py:125-126` only executes `scripts/dev/cbp_run.py --force`, strictly dedicated to CBP ingestion | SOURCED `scripts/dev/test_cbp_schedule.py:20` executes `schedule.validate_task_xml(xml)` verifying task XML contains no trading processes |
| 6 | Existing Claude login of signed-in user is used | MATCH | SOURCED `scripts/dev/cbp_schedule.py:6` `The signed-in user's existing Claude login is used.`<br>SOURCED `scripts/dev/cbp_schedule.py:53-54` Task XML principal specifies `<Principal id="Author"><LogonType>InteractiveToken</LogonType><RunLevel>LeastPrivilege</RunLevel></Principal>` (runs under interactive user session token, without storing credentials)<br>SOURCED `scripts/dev/cbp_schedule.py:87-88` `if not shutil.which("claude"): raise ValueError("claude executable unavailable to this user")` verifies signed-in user's Claude CLI is present | SOURCED `scripts/dev/test_cbp_schedule.py:15` and `scripts/dev/test_cbp_schedule.py:20` validate XML generation and schema compliance with interactive execution |

## Detailed Clause Verification

### Clause 1: Operator-authorized CBP-only Windows task management
- **Docstring**: SOURCED `scripts/dev/cbp_schedule.py:1` (`Install/status/remove the operator-authorized CBP-only twice-daily Windows task.`)
- **Code**:
  - `TASK = "MTS-CBP-Ingestion"` (SOURCED `scripts/dev/cbp_schedule.py:18`)
  - Subcommands `install`, `run`, `status`, `remove`, `check`, `dry-run` supported in `main()` (SOURCED `scripts/dev/cbp_schedule.py:94`)
  - Subcommands invoke `schtasks /Query` and `schtasks /Delete` (SOURCED `scripts/dev/cbp_schedule.py:104-106`) or `schtasks /Create` with XML (SOURCED `scripts/dev/cbp_schedule.py:120`).
  - Validation guarantees CBP-only execution (SOURCED `scripts/dev/cbp_schedule.py:75-76`).
- **Test**: SOURCED `scripts/dev/test_cbp_schedule.py:1` docstring and line 20 (`schedule.validate_task_xml(xml)`).
- **Verdict**: MATCH.

### Clause 2: Command Invocation and Home Directory Specification
- **Docstring**: SOURCED `scripts/dev/cbp_schedule.py:3-4` (`Install from a durable MTS checkout on the host holding CBP data: python scripts/dev/cbp_schedule.py install --home F:/CryptoScrapper`)
- **Code**:
  - CLI argument `--home` accepted as `Path` (SOURCED `scripts/dev/cbp_schedule.py:95`), defaulting to `cbp.default_cbp_home()` (SOURCED `scripts/dev/cbp_schedule.py:97`).
  - Home directory paths are passed into XML execution args (`run --home <home>`) (SOURCED `scripts/dev/cbp_schedule.py:36`).
- **Test**: SOURCED `scripts/dev/test_cbp_schedule.py:24` checks `'run --home "F:/CBP data"' in root.find('.//t:Arguments', ns).text`, and lines 40-44 test missing data behavior on `--home`.
- **Verdict**: MATCH.

### Clause 3: Weekday Schedule (Mon-Fri 05:00 and 20:00 UTC)
- **Docstring**: SOURCED `scripts/dev/cbp_schedule.py:5` (`Task times (OURS): Mon-Fri 05:00 and 20:00 UTC`)
- **Code**:
  - `WEEKDAY_TIMES = ("05:00", "20:00")` (SOURCED `scripts/dev/cbp_schedule.py:26`).
  - `task_xml()` builds weekday triggers over `DAYS[:5]` for each time in `WEEKDAY_TIMES` (SOURCED `scripts/dev/cbp_schedule.py:47`).
  - Accounts for host timezone shift (`utcoffset`) so UTC times crossing local midnight shift day of week properly (SOURCED `scripts/dev/cbp_schedule.py:34-46`).
- **Test**: SOURCED `scripts/dev/test_cbp_schedule.py:16-19` validates UTC boundary times and days `['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']`. SOURCED `scripts/dev/test_cbp_schedule.py:31-32` verifies IST shift for 20:00 UTC -> Tuesday-Saturday.
- **Verdict**: MATCH.

### Clause 4: Weekend Schedule (Sat 05:30 UTC / 11:00 IST, Sun 16:30 UTC / 22:00 IST)
- **Docstring**: SOURCED `scripts/dev/cbp_schedule.py:5` (`Saturday 05:30 UTC (11:00 IST), Sunday 16:30 UTC (22:00 IST).`)
- **Code**:
  - `WEEKEND_TIMES = (("Saturday", "05:30"), ("Sunday", "16:30"))` (SOURCED `scripts/dev/cbp_schedule.py:27`).
  - `triggers += "".join(trigger((day,), t) for day, t in WEEKEND_TIMES)` (SOURCED `scripts/dev/cbp_schedule.py:48`).
  - Neither 05:30 UTC nor 16:30 UTC crosses local midnight into the next day under IST (+05:30), matching 11:00 IST and 22:00 IST respectively.
- **Test**: SOURCED `scripts/dev/test_cbp_schedule.py:16-19` and SOURCED `scripts/dev/test_cbp_schedule.py:33` (`assert days[2:] == [['Saturday'], ['Sunday']]`).
- **Verdict**: MATCH.

### Clause 5: No Trading Process Started
- **Docstring**: SOURCED `scripts/dev/cbp_schedule.py:6` (`No trading process is started.`)
- **Code**:
  - `validate_task_xml()` rejects any XML containing `"trading"` or `"claude_run"`: `if "claude_run" in xml or "trading" in xml.lower(): raise ValueError("task XML must remain CBP-only")` (SOURCED `scripts/dev/cbp_schedule.py:75-76`).
  - Task action executes `scripts/dev/cbp_run.py --force` (SOURCED `scripts/dev/cbp_schedule.py:125-126`), which handles video fetching and analyst processing only.
- **Test**: SOURCED `scripts/dev/test_cbp_schedule.py:20` verifies validation passes for valid CBP tasks and checks subprocess targets in line 51 (`cbp_run.py --force`).
- **Verdict**: MATCH.

### Clause 6: Signed-in User's Existing Claude Login Used
- **Docstring**: SOURCED `scripts/dev/cbp_schedule.py:6` (`The signed-in user's existing Claude login is used.`)
- **Code**:
  - Task XML uses `<LogonType>InteractiveToken</LogonType>` and `<RunLevel>LeastPrivilege</RunLevel>` (SOURCED `scripts/dev/cbp_schedule.py:53-54`), meaning it runs within the interactive logged-in user context rather than as an unattended service account with separate credentials.
  - Preflight checks `shutil.which("claude")` in user's PATH (SOURCED `scripts/dev/cbp_schedule.py:87-88`).
- **Test**: SOURCED `scripts/dev/test_cbp_schedule.py:20` validates the task XML structure.
- **Verdict**: MATCH.
