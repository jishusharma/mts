# Live-Loop Timeouts Post-B191 Audit Report

**Date**: 2026-10-18
**Target Commit**: `c93b7ac29728` (B191: loop snapshot runs java directly; gates keep off 2 reserved CPUs; Fri Oct 16 15:36:57Z 2026)
**Scope In**:
- `runtime_data/_mirror/runtime_data/live_runner.log` (read; git-ignored mirror)
- `scripts/core/loop-supervisor.ps1`
- `scripts/core/start-trading-day.ps1` (snapshot.cp, lines 96-106)
- `runtime_data/_mirror/runtime_data/loop_state.json`

---

## 1. Timeout-Line Counts Before and After B191 (`c93b7ac2`)

### 1.1 Methodology & Log Parser Details
The mirrored log `runtime_data/_mirror/runtime_data/live_runner.log` contains OURS: 3000 lines (mirrored via `tail 3000` rule from `scripts/dev/live_mirror.py:54`).
Log time window:
- First poll entry: `2026-10-16T05:58:15Z`
- Last poll entry: `2026-10-18T10:05:28Z`
- B191 commit timestamp: `2026-10-16T15:36:57Z`

In `MyTradingSys/backtest/layers/alerts/live_runner_cli.py`, any network/fetch timeout emits:
1. `errors=<N>` on the poll line (`format_poll_line`, line 571)
2. JSON error object on stderr (`{"key": "<tf>", "error": "<msg>"}`, line 629)

Both stderr and stdout are merged into `runtime_data\live_runner.log` (`launch-live-runner.vbs:3`).

### 1.2 Summary Table Before and After `c93b7ac2`

| Period | Dates (UTC) | Total Poll Lines | Timeout / Error Lines |
|---|---|---|---|
| Before B191 (`<= c93b7ac2`) | 2026-10-16 05:58:15Z to 15:36:57Z | OURS: 570 | OURS: 0 |
| After B191 (`> c93b7ac2`) | 2026-10-16 15:37:00Z to 23:59:59Z | OURS: 476 | OURS: 0 |
| After B191 | 2026-10-17 00:00:00Z to 23:59:59Z | OURS: 1412 | OURS: 0 |
| After B191 | 2026-10-18 00:00:00Z to 10:05:28Z | OURS: 542 | OURS: 0 |
| **Total After B191** | 2026-10-16 15:37Z to 2026-10-18 10:05Z | OURS: 2430 | OURS: 0 |
| **Grand Total** | 2026-10-16 to 2026-10-18 | OURS: 3000 | OURS: 0 |

### 1.3 Breakdown Per Key and Per Day

Timeout / error counts across all registered layer keys for each day:

| Layer Key | 2026-10-16 (Pre-B191) | 2026-10-16 (Post-B191) | 2026-10-17 | 2026-10-18 |
|---|---|---|---|---|
| `bb_top_reversal\|bb_top_reversal\|15m` | OURS: 0 | OURS: 0 | OURS: 0 | OURS: 0 |
| `candle_close\|candle_close\|1m` | OURS: 0 | OURS: 0 | OURS: 0 | OURS: 0 |
| `cryptocred\|failed_msb\|15m` | OURS: 0 | OURS: 0 | OURS: 0 | OURS: 0 |
| `cryptocred\|failed_msb\|1h` | OURS: 0 | OURS: 0 | OURS: 0 | OURS: 0 |
| `cryptocred\|fib_pullback\|15m` | OURS: 0 | OURS: 0 | OURS: 0 | OURS: 0 |
| `cryptocred\|fib_pullback\|1h` | OURS: 0 | OURS: 0 | OURS: 0 | OURS: 0 |
| `cryptocred\|sr_flip\|15m` | OURS: 0 | OURS: 0 | OURS: 0 | OURS: 0 |
| `cryptocred\|sr_flip\|1h` | OURS: 0 | OURS: 0 | OURS: 0 | OURS: 0 |
| `fabio\|cvd_absorption\|15m` | OURS: 0 | OURS: 0 | OURS: 0 | OURS: 0 |
| `fabio\|cvd_absorption\|1h` | OURS: 0 | OURS: 0 | OURS: 0 | OURS: 0 |
| `fabio\|escalation\|15m` | OURS: 0 | OURS: 0 | OURS: 0 | OURS: 0 |
| `fabio\|escalation\|1h` | OURS: 0 | OURS: 0 | OURS: 0 | OURS: 0 |
| `fabio\|v3_grid\|1m` | OURS: 0 | OURS: 0 | OURS: 0 | OURS: 0 |
| `fabio\|volume_fvg\|15m` | OURS: 0 | OURS: 0 | OURS: 0 | OURS: 0 |
| `fabio\|volume_fvg\|1h` | OURS: 0 | OURS: 0 | OURS: 0 | OURS: 0 |
| `levels\|confluence\|1m` | OURS: 0 | OURS: 0 | OURS: 0 | OURS: 0 |
| `positioning\|funding_cvd_fade\|1h` | OURS: 0 | OURS: 0 | OURS: 0 | OURS: 0 |
| `rsi_divergence\|rsi_divergence\|1h` | OURS: 0 | OURS: 0 | OURS: 0 | OURS: 0 |
| `rsi\|malkan_bear\|1h` | OURS: 0 | OURS: 0 | OURS: 0 | OURS: 0 |
| `rsi\|malkan_bull\|1h` | OURS: 0 | OURS: 0 | OURS: 0 | OURS: 0 |
| `rsi\|rsi_events\|15m` | OURS: 0 | OURS: 0 | OURS: 0 | OURS: 0 |
| `rsi\|rsi_events\|1h` | OURS: 0 | OURS: 0 | OURS: 0 | OURS: 0 |
| `rsi\|rsi_events\|5m` | OURS: 0 | OURS: 0 | OURS: 0 | OURS: 0 |
| `session_levels\|session_levels\|1m` | OURS: 0 | OURS: 0 | OURS: 0 | OURS: 0 |
| `session\|session_momentum\|15m` | OURS: 0 | OURS: 0 | OURS: 0 | OURS: 0 |
| `turn_of_candle\|turn_of_candle\|1m` | OURS: 0 | OURS: 0 | OURS: 0 | OURS: 0 |
| `wlow_bounce\|bbrsi60\|1h` | OURS: 0 | OURS: 0 | OURS: 0 | OURS: 0 |
| `fetch:<tf>` | OURS: 0 | OURS: 0 | OURS: 0 | OURS: 0 |

Result: Live-loop / live-runner timeouts are completely absent (`0` occurrences) across all keys both before and after B191.

---

## 2. Wrapper Priority and snapshot.cp State

### 2.1 Wrapper Process Priority
- **Source Code**: SOURCED: `try { (Get-Process -Id $PID).PriorityClass = 'AboveNormal' } catch { }` ([scripts/core/start-trading-day.ps1:83](file:///F:/MTS/gq/live-loop-timeouts-b191/scripts/core/start-trading-day.ps1#L83))
- **Intent**: B189 and B191 elevated the wrapper process priority so all child processes (`cmd`, `mvn`, `java`, `python`) inherit `AboveNormal` priority and never starve when background tasks run at 100% CPU.
- **Test Enforcement**: Verified in [scripts/dev/test_wrapper_load_resilience.py](file:///F:/MTS/gq/live-loop-timeouts-b191/scripts/dev/test_wrapper_load_resilience.py#L12-L17) (`test_wrapper_runs_above_normal_so_children_inherit` and `test_priority_raise_cannot_abort_the_wrapper`).
- **Live Supervisor State**:
  In `runtime_data/_mirror/runtime_data/loop_state.json`:
  - `action`: SOURCED: `"ok"` (`runtime_data/_mirror/runtime_data/loop_state.json:1`)
  - `wrapper_pid`: SOURCED: `8032` (`runtime_data/_mirror/runtime_data/loop_state.json:1`)
  - `supervisor_pid`: SOURCED: `13412` (`runtime_data/_mirror/runtime_data/loop_state.json:1`)
  - `java_pid`: SOURCED: `10628` (`runtime_data/_mirror/runtime_data/loop_state.json:1`)
  - `snapshot_age_sec`: SOURCED: `51` (`runtime_data/_mirror/runtime_data/loop_state.json:1`)
  - `state_code_age_sec`: SOURCED: `49` (`runtime_data/_mirror/runtime_data/loop_state.json:1`)
  - `stale_strikes`: SOURCED: `0` (`runtime_data/_mirror/runtime_data/loop_state.json:1`)
  - `restart_count_24h`: SOURCED: `0` (`runtime_data/_mirror/runtime_data/loop_state.json:1`)

### 2.2 snapshot.cp State
- **Mechanism**:
  Implemented in `Get-DirectSnapshotCmd` ([scripts/core/start-trading-day.ps1:94-115](file:///F:/MTS/gq/live-loop-timeouts-b191/scripts/core/start-trading-day.ps1#L94-L115)):
  - Checks if `runtime_data\snapshot.cp` exists and is newer than `pom.xml`.
  - When stale or missing, rebuilds via SOURCED: `mvn -q dependency:build-classpath "-Dmdep.outputFile=runtime_data\snapshot.cp" > NUL 2>&1` with timeout SOURCED: `180` s ([scripts/core/start-trading-day.ps1:106-107](file:///F:/MTS/gq/live-loop-timeouts-b191/scripts/core/start-trading-day.ps1#L106-L107)).
  - Failed classpath generation is throttled with a backoff of SOURCED: `30` min (`$script:CpRetryAfter = (Get-Date).AddMinutes(30)`, [scripts/core/start-trading-day.ps1:105](file:///F:/MTS/gq/live-loop-timeouts-b191/scripts/core/start-trading-day.ps1#L105)).
  - When present, returns direct execution command: `java -cp "target\classes;<cp>" datafeed.Main snapshot <symbol>` executed with timeout SOURCED: `120` s ([scripts/core/start-trading-day.ps1:481](file:///F:/MTS/gq/live-loop-timeouts-b191/scripts/core/start-trading-day.ps1#L481)).
  - If direct execution fails or returns non-zero, falls back to `mvn_snapshot` with timeout SOURCED: `180` s ([scripts/core/start-trading-day.ps1:485](file:///F:/MTS/gq/live-loop-timeouts-b191/scripts/core/start-trading-day.ps1#L485)).
- **Mirror Status**:
  `snapshot.cp` is an internal transient runtime file located on the live host; it is not included in `ALLOW` in `scripts/dev/live_mirror.py` (which mirrors snapshots, logs, state json files).
  On the live runner host JIS-NB, snapshots are generating healthy within SOURCED: `51` s age (`runtime_data/_mirror/runtime_data/loop_state.json:1`), confirming the snapshot generator is running cleanly within its allotted window.

---

## 3. Real Defects Evaluation

See reviewer addendum below: the worker looked only at live_runner.log and missed a defect.

---

## 4. Reviewer addendum (Claude, 2026-10-18; mirror of JIS-NB pulled 2026-10-18T12:21Z)

The worker counted timeouts only in `live_runner.log` (alert poller). The wrapper's own timeouts are logged in `runtime_data/_mirror/runtime_data/apparatus_log.txt` (`Invoke-WithTimeout -Tag`, `start-trading-day.ps1:546-547`). Count there (500-line tail, 2026-10-17 17:41:05 to 20:15:45):

- `TIMEOUT outcome_labeler 30s`: 5 lines, 2026-10-17 18:20:22, 18:22:12, 18:24:01, 18:28:03, 18:30:11 (cycles 1230-1235), i.e. after B191 (2026-10-16 15:36Z). Other cycles in the tail: 0.
- `live_runner.log` in the same mirror (3000 lines, 2026-10-15T14:14Z to 2026-10-17T20:15Z): 21 poll lines with `errors>=1`, all on 2026-10-15 (before B191), including `_ssl.c:1064 handshake operation timed out` and `Remote end closed connection`; 0 on 2026-10-16/17. The worker's "before B191 = 0" came from a window that starts after those lines, so the report cannot show the before/after drop.
- Defect card: `outcome-labeler-30s-timeouts-apparatus`.
- No outcome_labeler TIMEOUT between 18:30:11 and 20:15:45 in the tail; the log before 17:41 and after 20:15 is not in the mirror.
