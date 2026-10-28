# Health and Check Scripts Comprehensive Triage Report (2026-10-28)

**Task**: `all-health-checks-run-and-triage`  
**Host**: `DESKTOP-F7IU69N`  
**Execution Environment**: Windows PowerShell / Python 3.14  
**Timeout Cap**: 120.0 seconds per script  
**Total Scripts Audited**: 35 scripts across `scripts/dev/` and `scripts/operator/`

---

## 1. Complete Triage Results Table

| Check | Command Executed | Result | Time | What It Guards |
|---|---|:---:|:---:|---|
| `aibridge_health` | `python scripts/dev/aibridge_health.py` | **PASS** | 0.12s | Probes local DSA AI Bridge HTTP server on `127.0.0.1:7181`. |
| `health_audit` | `python scripts/dev/health_audit.py` | **FAIL** | 15.44s | Multi-domain health: git fetch, 72h commit pace, CI, stale claims (>24h). Failed on 72 stale claims. |
| `host_health` | `python scripts/dev/host_health.py` | **PASS** | 3.48s | Preflight for `sync.py ship`: inspects running processes, CPU hogs, memory, and stray processes. |
| `lane_health` | `python scripts/dev/lane_health.py status` | **PASS** | 0.27s | Monitors GPT / Codex lane status, credit exhaustion, and heartbeat freshness. |
| `mts_doctor` | `python scripts/dev/mts_doctor.py` | **PASS** | 39.34s | Canonical read-only doctor: disk space, git health, branch state, worktrees, stray processes. |
| `config_check` | `python scripts/dev/config_check.py` | **PASS** | 0.28s | Validates JSON/YAML configuration schemas (`.claude/settings.json`, `.agents/hooks.json`). |
| `alert_rate_check` | `python scripts/dev/alert_rate_check.py` | **PASS** | 0.48s | Layer watchdog tracking hourly alert generation rates (identifies DEAD vs QUIET vs OK layers). |
| `perm_audit` | `python scripts/dev/perm_audit.py` | **PASS** | 0.30s | Audits filesystem and tool execution permissions in `.claude/settings*.json` for unattended runs. |
| `token_audit` | `python scripts/dev/token_audit.py` | **PASS** | 2.24s | Analyzes token consumption metrics across Claude session transcripts over the last 7 days. |
| `ci_watch` | `python scripts/dev/ci_watch.py` | **PASS** | 3.32s | Inspects GitHub Actions fast-track CI; warns if consecutive runs are failing. |
| `check_handoff` | `python scripts/dev/check_handoff.py` | **FAIL** | 0.10s | Linter for `MyTradingSys/system/NEXT_SESSION.md` format (prompts, headings, handoff block). |
| `runaway_check` | `powershell -NoProfile -File scripts/operator/runaway_check.ps1` | **PASS** | 2.67s | PowerShell watchdog measuring process memory handles, paged pool leaks, and runaway CPU. |
| `check_guide` | `python scripts/dev/check_guide.py` | **PASS** | 0.09s | Validates that `MTS_USER_GUIDE.md` stays synchronized with `mts.ps1` CLI parameters. |
| `check_set_frames` | `python scripts/dev/check_set_frames.py` | **FAIL** | 0.14s | Verifies disk presence of video frame captures referenced in Tom CHECK set trade recaps. |
| `check_spec_quotes` | `python scripts/dev/check_spec_quotes.py <spec>` | **FAIL** | 0.14s | Asserts quoted text in spec files appears verbatim in underlying transcripts. Requires spec argument. |
| `c_drive_guard` | `python scripts/dev/c_drive_guard.py` | **PASS** | 41.98s | Monitors free space on C: drive (>15 GB required) and cleans orphan %TEMP% git directories. |
| `stop_guard` | `python scripts/dev/stop_guard.py` | **FAIL** | 0.11s | Stop-hook guardrail preventing session exit with uncommitted files or unshipped commits. |
| `preship` | `python scripts/dev/preship.py` | **FAIL** | 0.11s | Targeted pre-flight test runner checking the rules most prone to ship gate failure. |
| `daily_hygiene` | `python scripts/dev/daily_hygiene.py` | **ERROR** | 120.00s | Scheduled multi-stage maintenance runner. Timed out because step 1 runs full `run_all_tests.py --quick`. |
| `ci_deps_lint` | `python scripts/dev/ci_deps_lint.py` | **PASS** | 12.11s | AST linter ensuring test file imports are installed in `.github/workflows/ci.yml`. |
| `lookahead_lint` | `python scripts/dev/lookahead_lint.py` | **PASS** | 38.35s | AST scanner for temporal lookahead patterns (forward indexing, next-bar access) in research scripts. |
| `research_kit_lint` | `python scripts/dev/research_kit_lint.py` | **PASS** | 1.10s | Detects research scripts that duplicate shared statistical logic (Holm, cluster corrections). |
| `reply_shape_check` | `python scripts/dev/reply_shape_check.py` | **ERROR** | 120.00s | Deterministic reply-shape linter. Timed out: blocks waiting for stdin EOF when called without args. |
| `wiring_scan` | `python scripts/dev/wiring_scan.py` | **PASS** | 12.22s | Reachability classifier categorizing all repo files into LIVE, TEST-ONLY, ORPHAN, or DEV-TOOL. |
| `trunk_lag` | `python scripts/dev/trunk_lag.py` | **FAIL** | 0.25s | UserPromptSubmit hook checking if active branch is behind origin/fast-track. Requires hook context. |
| `testnet_status` | `python scripts/dev/testnet_status.py` | **PASS** | 0.26s | Generates sanitized daily testnet health summary JSON file. |
| `testnet_canary` | `python scripts/dev/testnet_canary.py` | **FAIL** | 2.70s | Canary checking live trading stack processes and loops. Fails when local Java daemon is offline. |
| `aibridge_verify` | `python scripts/dev/aibridge_verify.py` | **FAIL** | 1.78s | Comprehensive 28-point contract verification of AIBridge. Fails on Chrome unpacked extension load. |
| `chart_verify` | `python scripts/dev/chart_verify.py` | **FAIL** | 0.38s | Recomputes indicator values against Binance klines. Requires positional arguments: symbol, tf, utc. |
| `indicator_audit_compare` | `python scripts/dev/indicator_audit_compare.py` | **FAIL** | 0.28s | Compares reviewer answers with engine indicators. Requires `--packets` and `--replies` args. |
| `indicator_audit_sample` | `python scripts/dev/indicator_audit_sample.py` | **FAIL** | 0.43s | Draws seeded samples for indicator audits. Requires subcommand `{fetch,draw}`. |
| `verify_extract_quotes` | `python scripts/dev/verify_extract_quotes.py` | **FAIL** | 0.18s | Verifies video extraction quotes match transcript text. Requires extraction file path argument. |
| `bg_watch` | `python scripts/dev/bg_watch.py report` | **PASS** | 0.15s | Identifies background tasks exceeding wall-time caps and aged raw cards. |
| `tasks_check` | `python scripts/dev/tasks.py check` | **PASS** | 23.61s | Linter validating task cards JSON schema, lane allocations, and claim states. |
| `sync_where` | `python scripts/dev/sync.py where` | **PASS** | 3.37s | Worktree inspector verifying clean states and unpushed commits across all active worktrees. |

---

## 2. Categorization & Flags

### A. Hanging / Blocking Checks (Critical Defects in CLI Design)
1. **`scripts/dev/reply_shape_check.py`**:
   - **Issue**: When invoked with no command-line arguments, line 7–8 unconditionally executes `sys.stdin.read()`. In non-interactive or batch environments where stdin is inherited but not closed, the process hangs indefinitely until the 120s timeout terminates it.
   - **Recommendation**: Add a tty check (`if sys.stdin.isatty(): return usage`) or require explicit `-` to read from stdin.
2. **`scripts/dev/daily_hygiene.py`**:
   - **Issue**: Although named "hygiene", it is a heavyweight multi-stage batch runner. Step 1 executes `python scripts/dev/run_all_tests.py --quick` with a 1500-second timeout. It cannot serve as a quick operational check.
   - **Recommendation**: Decouple test gate execution from operational hygiene checks.

### B. Missing Default Subcommand / Bare Invocation Failures
1. **`scripts/dev/lane_health.py`**: Exits with return code 2 (`error: the following arguments are required: cmd`). Should default to `status` when invoked without arguments.
2. **`scripts/dev/bg_watch.py`**: Exits with return code 2 (`error: the following arguments are required: cmd`). Should default to `report` when invoked without arguments.

### C. Hook-Specific Scripts (Not Intended for Standalone CLI Execution)
The following scripts are designed as event hooks for Claude Code (`.claude/settings.json`) or Antigravity (`.agents/hooks.json`) and expect hook payloads or CLI flags:
- `scripts/dev/stop_guard.py` (Claude Stop hook)
- `scripts/dev/trunk_lag.py` (Claude UserPromptSubmit hook)
- `scripts/dev/preship.py` (Pre-ship gate hook)

### D. Parameterized Verification Tools (Require Explicit Target Arguments)
The following scripts perform verification on specific files or entities and cannot run standalone without target parameters:
- `scripts/dev/check_spec_quotes.py` (requires spec path)
- `scripts/dev/verify_extract_quotes.py` (requires extract file path)
- `scripts/dev/chart_verify.py` (requires symbol, timeframe, timestamp)
- `scripts/dev/indicator_audit_compare.py` (requires `--packets` and `--replies`)
- `scripts/dev/indicator_audit_sample.py` (requires `{fetch,draw}`)

### E. Environment-Dependent / Local Host Failures
- `health_audit.py`: Exits 1 due to 72 stale claims (>24h old) in repository claims registry.
- `check_handoff.py`: Exits 1 because `MyTradingSys/system/NEXT_SESSION.md` is currently missing a fenced prompt block.
- `check_set_frames.py`: Exits 1 because referenced video frames on `F:/MTS/data/...` are absent on this host.
- `testnet_canary.py`: Exits 2 because the Java live trading daemon is not running on this development machine.
- `aibridge_verify.py`: Exits 1 on 1 check (`extension_loaded`) because the Chrome unpacked extension is not installed in the active user's Chrome profile.

### F. Duplicative / Overlapping Checks
- **Host & Process Health**: `scripts/dev/host_health.py`, `scripts/operator/runaway_check.ps1`, and `scripts/dev/mts_doctor.py` all independently scan process lists for stray Python/Node processes and high CPU/memory usage.
- **Worktree State**: `scripts/dev/stop_guard.py` re-implements logic that wraps `python scripts/dev/sync.py where`.
- **Config & Permissions**: `scripts/dev/config_check.py` and `scripts/dev/perm_audit.py` both inspect `.claude/settings*.json` and could be consolidated.

---

## 3. Proposed Schedule-Free One-Command Health Runner

Currently, an operator or session must remember multiple distinct scripts (`sync.py where`, `tasks.py check`, `config_check.py`, `mts_doctor.py`, `aibridge_health.py`, `ci_watch.py`).

We propose a unified, schedule-free, pure read-only health runner:  
**`python scripts/dev/health.py`** (or `python scripts/dev/sync.py health --fast`)

### Architecture & Specification:
1. **Execution Budget**: Maximum 15 seconds total wall-time.
2. **Read-Only Guarantee**: Zero writes to repository or runtime state.
3. **Fail-Closed Isolation**: Each check runs with a strict 5-second subprocess timeout; any hanging check is terminated without stalling the suite.
4. **Zero Parameters Required**: All sub-checks run with their default zero-argument inspection modes.
5. **Standardized Status Table Output**:
   - Check Name
   - Category (GIT, TASKS, HOST, CI, NETWORK, CONFIG)
   - Status (`OK` / `WARN` / `FAIL`)
   - Latency (ms)
   - Detail / Remediation line

### Sub-checks Included in Proposed Runner:
```python
HEALTH_SUITE = [
    ("worktree_hygiene", ["python", "scripts/dev/sync.py", "where"], 5),
    ("task_registry", ["python", "scripts/dev/tasks.py", "check"], 5),
    ("ci_pipeline", ["python", "scripts/dev/ci_watch.py"], 5),
    ("host_resources", ["python", "scripts/dev/host_health.py"], 5),
    ("lane_status", ["python", "scripts/dev/lane_health.py", "status"], 5),
    ("background_tasks", ["python", "scripts/dev/bg_watch.py", "report"], 5),
    ("config_schemas", ["python", "scripts/dev/config_check.py"], 5),
    ("claude_permissions", ["python", "scripts/dev/perm_audit.py"], 5),
    ("aibridge_status", ["python", "scripts/dev/aibridge_health.py"], 5),
    ("alert_rates", ["python", "scripts/dev/alert_rate_check.py"], 5),
]
```
