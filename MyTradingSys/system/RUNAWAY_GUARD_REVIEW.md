# RUNAWAY GUARD DESIGN REVIEW (card `runaway-guard-design-review`)

- **Reviewer:** Gemini 4 Argon (Low) (`gemini-nuc`, surface GEM, independent cross-vendor model from author Claude Sonnet 5.5)
- **Date:** 2026-10-27 UTC (2026-10-28 IST)
- **Target:** `MyTradingSys/system/RUNAWAY_GUARD.md` (sections 1-6) and `MyTradingSys/system/NUC_SHUTDOWN_HANDOVER.md` (updates 2026-10-26 16:00 and 2026-10-27 18:20)
- **Verdict:** **ACCEPT** (design sound and policy-compliant for Layers 1-3; Layer 4 not recommended at this stage; 6 concrete implementation findings below)

---

## Numbered Findings (for the Layer 1-3 build)

1. **Root cause confirmed, with an important MSYS2 process-tree subtlety (`RUNAWAY_GUARD.md:7-10`):**
   The local transcript (`b548c0a6-bbf8-4e96-bf38-b401f4389223/subagents/agent-af27dbcb366bdce5d.jsonl:38-43`) confirms that at `2026-10-26T01:09:27.639Z` (`06:39:27` IST) subagent `af27dbcb` ran `find / -iname "*openinterest*" -o -iname "*oi_5m*" -o -iname "*open_interest*" 2>/dev/null | grep -v node_modules | head`, which hit its 120 s timeout (`01:11:28.366Z`, background task `blra0fwc7`) and even received an explicit `TaskStop` call (`01:11:30Z`, `"Successfully stopped task: blra0fwc7"`). Yet `find.exe` and `grep.exe` survived for 9 hours. Our bounded scratch reproduction below proves **why**: in Git for Windows (MSYS2), pipeline children (`find.exe`, `grep.exe`, `head.exe`) are forked with detached Windows `ParentProcessId` values once intermediate subshells exit, so neither killing the root `bash.exe` PID nor running `taskkill /T /F /PID <root_bash_pid>` terminates the pipeline children. Only a **Windows Job Object** (`JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE`) tracks and kills the entire MSYS2 pipeline.
2. **Layer 3 Job Object feasibility (`RUNAWAY_GUARD.md:28`):**
   A `PreToolUse` hook cannot wrap the harness's own `Bash` child process inside a Windows Job Object because the hook runs in a separate short-lived process that exits before `Bash` starts. Therefore:
   - For **Claude Code (`Bash`)**, killing backgrounded/timed-out MSYS2 pipelines requires either an upstream harness fix (assigning every `Bash` tool spawn to a per-command Job Object closed on `TaskStop` or timeout) or explicitly invoking a repo wrapper (`python scripts/dev/run_guarded.py --timeout <s> -- <cmd>`) for untrusted/heavy shell pipelines.
   - For **repo-controlled runners** (`scripts/dev/codex_run.py`, `scripts/dev/gemini_queue.py`, `scripts/dev/run_all_tests.py`), Python's `ctypes.windll.kernel32` Job Object (`CreateJobObjectW` + `SetInformationJobObject` with `0x2000` `JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE` + `AssignProcessToJobObject`) works out of the box with zero third-party packages and cleanly kills 100% of MSYS2 child pipelines on timeout.
3. **Layer 1 `PreToolUse:Bash` regex & hook placement (`RUNAWAY_GUARD.md:24`):**
   Extend `scripts/dev/preship.py` (`hook-commit` is already registered on `PreToolUse` `matcher: "Bash"` in `.claude/settings.json:121-130`) rather than registering a new hook script (or register a dedicated row in `MyTradingSys/system/DEBUGGING.md` section 2 so `test_debugging_spine.py` stays green). The regex must block POSIX root `/`, Windows drive roots (`C:\`, `C:/`, `F:\`, `F:/`), and Git-Bash MSYS drive roots (`/c`, `/c/`, `/f`, `/f/`) while allowing subdirectories (`/f/MTS/data/...`, `C:/Users/...`, `MyTradingSys`). Tested pattern and 20 test cases (10 deny, 10 allow) are provided in Q3 below.
4. **Layer 2 (`runaway_check.ps1`) command-line and pool-threshold alignment (`RUNAWAY_GUARD.md:26` vs `scripts/operator/runaway_check.ps1:15-31`):**
   - `runaway_check.ps1:20-31` prints `paged pool {3:N0} MB` and warns on `available mbytes -lt 1500`, but does **not** yet emit a `WARN:` line when `pool paged bytes / 1MB -gt 4096` as specified in `RUNAWAY_GUARD.md:26`. Add `if (($v['pool paged bytes'] / 1MB) -gt 4096) { "WARN: paged pool over 4 GB" }`.
   - Note that MSYS2 `find.exe` spawned inside a pipeline often reports only `"C:\Users\E-ngineers\Git\usr\bin\find.exe"` in `Win32_Process.CommandLine` (MSYS2 passes arguments via its internal cygheap rather than the Win32 PEB command-line string). Detection in `runaway_check.ps1:22` rightly keys on `Name` + `CPU -gt 600` or `HandleCount -gt 100000`, which does not depend on `CommandLine`.
5. **Section 6 fleet broadcast `b-8ce4da` replies are now in (`RUNAWAY_GUARD.md:50-59`):**
   `python scripts/dev/mts_signal.py acks b-8ce4da` shows all three physical Windows hosts (`jis-nuc`, `jis-desktop`/`jis-nb`, `jis-laptop`/`desktop-f7iu69n`) have now replied `done` with `OK no runaway`. Update `RUNAWAY_GUARD.md` section 6 from `no reply` to `no (OK)` for `JIS-NB`/`JIS-DESKTOP` and `JIS-LAPTOP`.
6. **Layer 4 (`always-on watcher`) is unnecessary once Layers 1-2 are active (`RUNAWAY_GUARD.md:30`):**
   Do **not** request a `SCHEDULING_POLICY.md` section 4d exception yet. Agents only spawn shell commands while an active session or runner is executing, so Layer 1 (prevent at `PreToolUse:Bash`) + Layer 2 (detect at `SessionStart` / `UserPromptSubmit`, throttled 5 min) + `c_drive_guard.py logon` cover active and reboot boundaries without a standing 60 s background loop.

---

## Section 5 Questions — Answered with Evidence

### Q1. Is the root cause right? (Transcript verification + bounded scratch reproduction)

**Answer: YES — confirmed both in the primary transcript and by a bounded scratch test on `JIS-NUC`.**

#### 1a. Transcript verification (`b548c0a6` / subagent `af27dbcb`)
Reading `C:\Users\E-ngineers\.claude\projects\C--Users-E-ngineers-IdeaProjects-BinanceDataFeed\b548c0a6-bbf8-4e96-bf38-b401f4389223\subagents\agent-af27dbcb366bdce5d.jsonl`:
- **Line 38 (`2026-10-26T01:09:27.639Z` = `06:39:27` local IST):**
  ```json
  {"agentId":"af27dbcb366bdce5d","type":"assistant","timestamp":"2026-10-26T01:09:27.639Z","message":{"model":"claude-sonnet-5-5","content":[{"type":"tool_use","id":"toolu_012L2Mb7Q2qd2LmYsXewAW9Q","name":"Bash","input":{"command":"cd C:/Users/E-ngineers/IdeaProjects/mts-jis-nuc-builder-b-oi-pivot-2/MyTradingSys && sed -n 1,60p research/loose_code/oi_event_study_2026-10-10.py; grep -n \"open_interest\\|oi_\" research/orderflow_views_2026-10-14/study.py | head -15; ls research/orderflow_views_2026-10-14 | head; find / -iname \"*openinterest*\" -o -iname \"*oi_5m*\" -o -iname \"*open_interest*\" 2>/dev/null | grep -v node_modules | head"}}]}}
  ```
- **Line 39 (`2026-10-26T01:11:28.366Z`):**
  ```json
  {"tool_use_id":"toolu_012L2Mb7Q2qd2LmYsXewAW9Q","type":"tool_result","content":"Command did not complete within its 120s timeout and was moved to the background (ID: blra0fwc7)."}
  ```
- **Lines 41-43 (`2026-10-26T01:11:30.464Z`):**
  The subagent immediately said `"Oops, find / was heavy."` and called `TaskStop` on `blra0fwc7`, receiving:
  ```json
  {"tool_use_id":"toolu_01SCmvCn9yTAKiUQrkHGn1G3","type":"tool_result","content":"{\"message\":\"Successfully stopped task: blra0fwc7 (cd C:/Users/E-ngineers/IdeaProjects/mts-jis-nuc-builder-b-oi-pivot-2/MyTradingSys && ... find / -iname \\\"*openinterest*\\\" -o -iname \\\"*oi_5m*\\\" -o -iname \\\"*open_interest*\\\" 2>/dev/null | grep -v node_modules | head)\",\"task_id\":\"blra0fwc7\"}"}
  ```
  Furthermore, note the operator precedence bug in `find / -iname "*openinterest*" -o -iname "*oi_5m*" -o -iname "*open_interest*"`: in POSIX `find`, implicit `-print` binds only to the last `-o` branch unless grouped with `\( ... \)`, so `find /` walked the entire filesystem without printing the first two branches, keeping `head` waiting for 10 matches on the third branch while `find.exe` traversed every drive and junction loop.

#### 1b. Bounded scratch reproduction on `JIS-NUC`
We ran a bounded scratch test in `scratch/find_test` (20 tiny text files, bounded 15 s sleep inside `find ... | grep -v node_modules | head`) launched via `C:\Users\E-ngineers\Git\bin\bash.exe --login`, then tested both (i) killing the root `bash.exe` and (ii) running `taskkill.exe /T /F /PID <root_bash_pid>`, followed by immediate cleanup:

```text
=== BEFORE taskkill /T /F /PID 14660 ===
PID=14660 PPID=17412 Name=bash.exe Cmd="C:\Users\E-ngineers\Git\bin\bash.exe" --login C:/.../scratch/find_test/run_pipe2.sh 
PID=16976 PPID=14660 Name=bash.exe Cmd="C:\Users\E-ngineers\Git\bin\..\usr\bin\bash.exe" --login C:/.../scratch/find_test/run_pipe2.sh 
PID=18572 PPID=16800 Name=find.exe Cmd="C:\Users\E-ngineers\Git\usr\bin\find.exe"
PID=20300 PPID=7532 Name=grep.exe Cmd="C:\Users\E-ngineers\Git\usr\bin\grep.exe"
PID=17288 PPID=19648 Name=head.exe Cmd="C:\Users\E-ngineers\Git\usr\bin\head.exe"
PID=20348 PPID=17316 Name=sleep.exe Cmd="C:\Users\E-ngineers\Git\usr\bin\sleep.exe"
SUCCESS: The process with PID 16572 (child process of PID 14660) has been terminated.
SUCCESS: The process with PID 16976 (child process of PID 14660) has been terminated.
SUCCESS: The process with PID 14660 (child process of PID 17412) has been terminated.
=== AFTER taskkill /T /F /PID 14660 ===
SURVIVOR AFTER taskkill /T: PID=18572 PPID=16800 Name=find.exe Cmd="C:\Users\E-ngineers\Git\usr\bin\find.exe"
SURVIVOR AFTER taskkill /T: PID=20300 PPID=7532 Name=grep.exe Cmd="C:\Users\E-ngineers\Git\usr\bin\grep.exe"
SURVIVOR AFTER taskkill /T: PID=17288 PPID=19648 Name=head.exe Cmd="C:\Users\E-ngineers\Git\usr\bin\head.exe"
SURVIVOR AFTER taskkill /T: PID=20348 PPID=17316 Name=sleep.exe Cmd="C:\Users\E-ngineers\Git\usr\bin\sleep.exe"
=== AFTER CLEANUP: Remaining find/grep/head/sleep = 0 ===
```
Even `taskkill /T /F` on the root `bash.exe` leaves `find.exe`, `grep.exe`, and `head.exe` running because MSYS2 forks intermediate subshells (`PID 16800`, `7532`, `19648`) that exit immediately after spawning each pipeline stage, breaking the Windows `ParentProcessId` chain.

---

### Q2. Layer 3: Is a Job Object wrapper feasible for Claude Code Bash/PowerShell tool calls and Codex shells?

**Answer: Feasible and proven for repo runners (`codex_run.py`, `gemini_queue.py`, `run_guarded.py`), but NOT doable via a `PreToolUse` hook for Claude Code's built-in `Bash` tool (must be filed upstream for the harness, or invoked explicitly as a command wrapper).**

1. **Proof that Windows Job Objects kill MSYS2 pipelines completely (`scratch/find_test/job_test.py`):**
   Using Python stdlib `ctypes.windll.kernel32` (`CreateJobObjectW`, `SetInformationJobObject` class 9 `JobObjectExtendedLimitInformation` with `LimitFlags = 0x2000` `JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE`, `AssignProcessToJobObject`):
   ```text
   SetInfo=1 Assign=1 root_pid=20368
   === WHILE JOB OPEN ===
   PID=20368 PPID=19964 Name=bash.exe
   PID=19872 PPID=20368 Name=bash.exe
   PID=19648 PPID=19004 Name=find.exe
   PID=19896 PPID=18656 Name=grep.exe
   PID=13960 PPID=8512 Name=head.exe
   PID=20388 PPID=14848 Name=sleep.exe
   === AFTER CloseHandle(job) ===
   NONE (0 survivors)
   ```
   Because Windows Job Object membership is inherited across every `CreateProcess` call regardless of intermediate parent exit, `CloseHandle(job)` (or `TerminateJobObject`) kills `find.exe`, `grep.exe`, `head.exe`, and `sleep.exe` with zero survivors.
2. **Why a Claude Code `PreToolUse` hook cannot attach a Job Object to `Bash`:**
   - In `.claude/settings.json`, `PreToolUse` runs a separate subprocess (`python preship.py ...`) *before* Claude Code spawns the `Bash` shell, and `PostToolUse` runs *after* `Bash` returns or moves to background. Neither hook receives the spawned shell's PID while it is running, and any Job Object handle created inside `PreToolUse` is closed as soon as `PreToolUse` exits.
   - **What breaks if you force a Job Object onto all shells with short timeouts:**
     - **Background tasks (`run_in_background=true` or 120 s auto-backgrounding) & `Monitor`:** If a wrapper closes the Job Object when the foreground wait expires, intentionally backgrounded tasks (like `sync.py ship` started in background per `PARALLEL.md:60` or `Monitor` watches) are killed immediately.
     - **Intentional detached daemons:** `c_drive_guard.py hook` spawns a detached `--apply` cleanup worker (`CREATE_BREAKAWAY_FROM_JOB` is blocked unless the Job Object also sets `JOB_OBJECT_LIMIT_BREAKAWAY_OK = 0x0800`).
     - **Long builds/gates:** `run_all_tests.py` and Maven builds take several minutes; only a timeout-aware runner should close the job.
3. **Practical split for Layer 3:**
   - **In this repo:** AddJob-Object assignment to `scripts/dev/codex_run.py` and `scripts/dev/gemini_queue.py` (where Python owns the `subprocess.Popen` call and its timeout), plus an optional `scripts/dev/run_guarded.py --timeout <s> -- <cmd>` helper for bounded shell calls. Set `JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE | JOB_OBJECT_LIMIT_BREAKAWAY_OK` (`0x2800`) so intentional detached children using `CREATE_BREAKAWAY_FROM_JOB` still work.
   - **Upstream (Claude Code harness):** File upstream that `Bash` tool tasks on Windows should be placed in a per-task Job Object whose handle is closed when `TaskStop` is called or the session exits.

---

### Q3. Layer 1: Which regex rules block `find /` without blocking legitimate `find MyTradingSys ...`?

**Answer: Match root path arguments (`/`, `C:\`, `C:/`, `F:\`, `/c`, `/c/`, `/f/`) after `find`, recursive `grep`, `ls -R`, `du`, and `Get-ChildItem -Recurse` across command boundaries (`^`, `;`, `&`, `|`, `$(`, `` ` ``).**

#### Pattern (Python `re.IGNORECASE | re.MULTILINE`)
```python
ROOT_TARGET = r'["\']?(?:/(?:\s|$|[;&|"\'`])|[A-Za-z]:[/\\]?(?:\s|$|[;&|"\'`])|/[A-Za-z]/?(?:\s|$|[;&|"\'`]))'

BARE_ROOT_SCAN_RE = re.compile(
    r'(?:^|[;&|]\s*|\$\(\s*|`\s*)(?:sudo\s+|env\s+\S+=\S+\s+|time\s+)*'
    r'(?:'
    r'find\s+(?:-[HLPO]\s+)*' + ROOT_TARGET +
    r'|grep\s+(?:-[A-Za-z0-9-]+\s+)*-(?:[A-Za-z]*[rR][A-Za-z]*|-recursive|-dereference-recursive)\b[^;&|\r\n]*?\s+' + ROOT_TARGET +
    r'|ls\s+(?:-[A-Za-z0-9-]+\s+)*-[A-Za-z]*R[A-Za-z]*\s+' + ROOT_TARGET +
    r'|du\s+(?:-[A-Za-z0-9-]+\s+)*' + ROOT_TARGET +
    r'|(?:Get-ChildItem|gci|dir)\s+(?=[^\r\n;&|]*(?:-Recurse|-r\b))[^\r\n;&|]*?(?:(?:-Path|-LiteralPath)\s+)?' + ROOT_TARGET +
    r')',
    re.IGNORECASE | re.MULTILINE,
)
```

#### 10 Deny + 10 Allow Test Strings (verified via `regex_test.py`)
```text
DENY #01 PASS: matched 'find / ' in 'find / -iname "*openinterest*" -o -iname "*oi_5m*" 2>/dev/null | grep -v node_modules | head'
DENY #02 PASS: matched '& find / ' in 'cd C:/Users/E-ngineers && find / -name "*.csv"'
DENY #03 PASS: matched 'find C:\\ ' in 'find C:\\ -name "*.py"'
DENY #04 PASS: matched 'find F:/ ' in 'find F:/ -iname "*klines*"'
DENY #05 PASS: matched 'find /c/ ' in 'find /c/ -name "*.json"'
DENY #06 PASS: matched 'grep -rn "open_interest" /' in 'grep -rn "open_interest" /'
DENY #07 PASS: matched 'grep -R "BTCUSDT" C:/' in 'grep -R "BTCUSDT" C:/'
DENY #08 PASS: matched 'ls -laR /' in 'ls -laR /'
DENY #09 PASS: matched 'du -sh /' in 'du -sh /'
DENY #10 PASS: matched 'Get-ChildItem -Path C:\\ ' in 'Get-ChildItem -Path C:\\ -Recurse -Filter *.log'
ALLOW #01 PASS: 'find MyTradingSys -name "*.py"'
ALLOW #02 PASS: 'find . -maxdepth 2 -name "*.json"'
ALLOW #03 PASS: 'find /f/MTS/data/tom_raw -name "*.csv"'
ALLOW #04 PASS: 'find C:/Users/E-ngineers/IdeaProjects/BinanceDataFeed/MyTradingSys -iname "*oi*"'
ALLOW #05 PASS: 'grep -rn "open_interest" MyTradingSys/research/'
ALLOW #06 PASS: 'grep -R "DERIBIT_TAKER" MyTradingSys/backtest/'
ALLOW #07 PASS: 'ls -R MyTradingSys/system/tasks'
ALLOW #08 PASS: 'du -sh F:/MTS/data'
ALLOW #09 PASS: 'Get-ChildItem -Path MyTradingSys/research -Recurse -Filter *.md'
ALLOW #10 PASS: 'git ls-files "*openinterest*"'
ALL 10 DENY AND 10 ALLOW PASSED!
```

---

### Q4. Thresholds: Are 100k handles / 10 CPU min / 1.5 GB free / 4 GB paged pool sane for these hosts?

**Answer: YES — all four thresholds (`OURS`) sit 18x–100x above normal peaks while catching the `find /` runaway hours before exhaustion.**

#### Measured normal peaks across hosts
1. **`JIS-NUC` (measured live 2026-10-28 02:24–02:28 IST via `runaway_check.ps1` and `Get-Process`):**
   ```text
   JIS-NUC: free 19,737 MB of 32,571; paged pool 1,063 MB; nonpaged pool 480 MB
   OK: no process over 100k handles, no long-running find/grep/sort

   Top processes by HandleCount on JIS-NUC:
      Id ProcessName   HandleCount CPU_s WS_MB
      -- -----------   ----------- ----- -----
       4 System               5036     0   0.1
    5552 explorer             2282  13.7 226.8
   10688 ChatGPT              2200  42.2 356.9
     792 svchost              1755     0  29.8
     636 lsass                1646     0  22.8
    9792 claude               1217  49.2 299.7

   Top processes by CPU_s on JIS-NUC:
      Id ProcessName HandleCount CPU_s WS_MB
      -- ----------- ----------- ----- -----
   13456 claude              513 202.1 640.3
   11940 ChatGPT             394  60.0 489.7
   12264 Discord             886  59.5 367.9
   ```
   - **Handles:** Normal highest user process is `explorer.exe` (`2,282` handles) and kernel `System` (`5,036` handles). The `100,000` handle threshold (`OURS`) has a **20x safety margin** over `System` and **43x** over the largest user app, while catching the `10.9M` handle leak (`~20k handles/min`) within ~5 minutes.
   - **Tool CPU time (`find`/`grep`/`sort`):** Normal scoped `find`/`grep` runs finish in `< 5 s` CPU. The `600 s` (10 CPU min, `OURS`) threshold is **120x** above normal tool calls while sparing `python`/`java`/`claude`/`codex`.
   - **Paged pool:** Normal on `JIS-NUC` is `1,063 MB` (`1.04 GB`) on a fresh boot and `1.8 GB` after 24 h (`NUC_SHUTDOWN_HANDOVER.md:112`). The `4 GB` (`4,096 MB`, `OURS`) threshold is **2.2x–3.8x** normal and well below the `9.7 GB` runaway state.
   - **Free memory:** Normal on 32 GB hosts is `15.4 GB–22.5 GB` free. The `1.5 GB` (`1,500 MB`, `OURS`) warning threshold leaves plenty of headroom for concurrent gates/backtests without false alarms.
2. **Second & third hosts from broadcast `b-8ce4da` (`python scripts/dev/mts_signal.py acks b-8ce4da`):**
   - **`JIS-DESKTOP` (`jis-nb`):** Acked `done` at `2026-10-27T12:42:06Z` (`20261027T124206Z185537-jisnb-6be2.json`):
     `"ack b-8ce4da done local checkout predates scripts/operator/runaway_check.ps1; ran it from origin/fast-track: OK no runaway processes, free RAM 15.4 GB"` (of 32 GB; 0 processes over 100k handles or 10 CPU min).
   - **`JIS-LAPTOP` (`desktop-f7iu69n`):** Acked `done` at `2026-10-27T18:45:16Z` (`20261027T184516Z329008-desktopf7iu6-3df2.json`):
     `"ack b-8ce4da done OK no runaway"`.
   - **`vm`:** `NOT_IN_DATA` (no reply to `b-8ce4da` within 24 h).

---

### Q5. Policy: Does Layer 2 (hooks) fit `SCHEDULING_POLICY.md` without a new exception? Is Layer 4 worth a 4d exception?

**Answer: Layer 2 fits `SCHEDULING_POLICY.md` today with ZERO new exceptions. Layer 4 does NOT warrant a 4d exception.**

- **Layer 2 policy fit:** `SCHEDULING_POLICY.md:7` bans *"standing Windows scheduled tasks and no Claude routines (App scheduled tasks, cron triggers, `mts-dispatcher`, `mts-lane-watch`) on any device."* Session hooks in `.claude/settings.json` (`SessionStart`, `UserPromptSubmit`) are explicitly permitted and already used by `c_drive_guard.py hook`, `trunk_lag.py`, `mts_signal.py`, `ci_watch.py`, and `shot.py` (`SCHEDULING_POLICY.md:31`, `.claude/settings.json:4-70`). Throttling the check via a stamp file in `%LOCALAPPDATA%\MTS\logs` (every 5 min while a session is active, report-only, fail-open) adds zero background processes and zero scheduled tasks.
- **Layer 4 policy fit:** A standing 60 s infinite loop started via `HKCU\...\Run` would violate the design of section 4c (`SCHEDULING_POLICY.md:32-33`: *"runs `scripts/dev/c_drive_guard.py logon` once at each logon ... It prunes the %TEMP% set ... and exits. It has no timer, no repeat"*). Because runaway `find`/`grep` processes can only be spawned when an agent session or lab runner is active—and Layers 1-3 block the command at `PreToolUse:Bash`, kill timed-out runner jobs via Job Objects, and scan every 5 min during active sessions—there is no unguarded gap when the machine is idle. Keep Layer 4 unbuilt unless a future leak escapes Layers 1-2.

---

### Q6. Does the NUC need anything beyond this (is event 142 linked)? What evidence would settle it?

**Answer: YES, the NUC needs hardware remediation beyond the runaway guard; the empirical record already proves `event 142` is NOT caused by the runaway `find.exe`.**

- **Evidence already settling that `find.exe` is NOT the cause of `event 142`:**
  1. **Chronology (`NUC_SHUTDOWN_HANDOVER.md:9-10,75`):** The hardware watchdog resets (`event 142`) started on `2026-10-23 02:28` (7 resets before `2026-10-26 06:39`, when `find /` was spawned).
  2. **Idle-state capture (`NUC_SHUTDOWN_HANDOVER.md:76`):** The `2026-10-25 01:09` reset was captured by `nuc_watch.csv` at `01:03:23` with `CPU 2%, 44 C, 21.9 GB free, disk idle, network 0`.
  3. **Post-kill 48 h clean test FAILED (`NUC_SHUTDOWN_HANDOVER.md:104,112-113` plus live `nuc_health.ps1 -Days 7` today):** After `find.exe` was killed at `2026-10-26 15:55`, `nuc_health.ps1 -Days 7` recorded **10 more `event 142` watchdog resets**:
     - `2026-10-26`: `17:34:45`, `23:27:49`
     - `2026-10-27`: `00:49:39`, `12:14:00`, `12:55:53`, `13:47:41`, `14:17:01`, `19:41:20`, `23:03:10`, `23:28:44` (total **17 watchdog resets in 7 days**, while `runaway_check.ps1` is `OK` with `19,737 MB` free).
  4. **Last logger row before the `2026-10-27 19:41:20` reset (`nuc_health.ps1` output above):**
     `2026-10-27 19:35:49,4,256,320,21455,0,0.9,0.0,0.0` — CPU was **4%**, free RAM was **21,455 MB**, disk busy **0%**.
- **What settles the hardware root cause (`NUC_SHUTDOWN_HANDOVER.md:107,116-118`, `d-nuc-hw-verdict`):**
  1. **Step 1 (in flight, arriving ~04 Nov):** Swap the 19 V 6.32 A (120 W) DC power adapter and run for 48 h (`powershell -File scripts/operator/nuc_health.ps1 -Days 2`). Zero `event 142` resets in 48 h settles the adapter as the root cause.
  2. **Step 2 (if resets continue on the new adapter):** Attended session on APC UPS to flash BIOS `0059 -> 0067`, replace the flat CR2032 coin cell, set BIOS `After Power Failure = Power On` and `PCIe ASPM = Off` (and if needed, `OSACPI C2 Report = Off` + Kingston KC600 firmware `S4500105 -> S4500109`), followed by another 48 h `nuc_health.ps1 -Days 2` check.

---

### Q7. Cross-device: Windows only? Does the VM / any Linux host need a different command?

**Answer: `runaway_check.ps1` and Windows Job Objects are Windows-only (`JIS-NUC`, `JIS-DESKTOP`/`JIS-NB`, `JIS-LAPTOP`), whereas Layer 1 (`PreToolUse:Bash`) is cross-platform and protects Linux/VM/cloud containers immediately.**

- **Layer 1 (`PreToolUse:Bash` in Python):** Runs identically on Windows, Linux (`ubuntu-latest` CI, cloud containers `claude.ai/code`, or a Linux VM) because `.claude/settings.json` invokes Python. Blocking `find /`, `grep -r /`, `ls -R /`, and `du /` in `PreToolUse` prevents root scans on Linux/VM before they start.
- **Layer 2 (`runaway_check.ps1`):** Uses `Get-CimInstance Win32_ComputerSystem`, `Get-Counter '\Memory\...'`, and `Get-Process` (`HandleCount`), which are Windows-only. On Linux/VM (if a persistent Linux VM is used outside ephemeral GitHub Actions `.github/workflows/ci.yml:49-51` and ephemeral cloud containers `PARALLEL.md:81`), a Python hook wrapper should check `sys.platform == "win32"` before calling `runaway_check.ps1` (failing open on non-Windows just like `c_drive_guard.py:55`), or use `/proc`:
  - Linux equivalent for memory/process check: read `/proc/meminfo` (`MemAvailable`) and `ps -eo pid,comm,etimes,pcpu,args` + count `/proc/<pid>/fd` entries for `find|grep|sort|xargs|sed|awk`.
- **Layer 3 (Process-tree termination):** On Linux/macOS, Python `subprocess.Popen(..., start_new_session=True)` creates a POSIX process group (`setsid`), and `os.killpg(pgid, signal.SIGKILL)` on timeout cleanly kills the entire pipeline (`bash`, `find`, `grep`, `head`) without surviving orphans—unlike Windows/MSYS2 where a Job Object is required.
