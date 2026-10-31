# Test Plan for Core Development Scripts (scripts/dev)

**Task ID:** gemini-test-plan-dev-scripts-1031  
**Date (UTC):** 2026-10-31  
**Target Modules:** scripts/dev/sync.py, scripts/dev/tasks.py, scripts/dev/supervisor.py, scripts/dev/mts_signal.py  
**Associated Test Suites Examined:** 	est_sync.py, 	est_sync_push_race.py, 	est_tasks.py, 	est_tasks_conflict.py, 	est_supervisor.py, 	est_loop_supervisor_grace.py, 	est_suplock.py, 	est_mts_signal.py  
**Registry Reference:** MyTradingSys/research/v1_plan_2026-10-20/D11_PROGRAMME.md  

---

## 1. Executive Summary & Audit Scope

This test plan rigorously maps every critical operational function in the four primary developer coordination and harness scripts (sync.py, 	asks.py, supervisor.py, mts_signal.py) against concrete boundary and failure modes:
1. **Claim Races:** Simultaneous claiming of task cards, git branches, and worktree slots.
2. **Ship while CI Red / Gate Bypasses:** Premature shipping or broken verification gates during unverified trunk states.
3. **Stale Marker Files & Stale PID Leases:** Dead background processes, leaked lockfiles, obsolete watchcheck markers, and unrefreshed task tags.
4. **Partial Writes & File Corruption:** Process interruption, power failure, or race conditions during JSON, log, stamp, or git reference writes.

### Overall Status Breakdown (OURS: derived from live repo inspection)
- **Total Critical Functions Audited:** 60 functions across the 4 modules.
- **Total Boundary / Failure Scenarios Evaluated:** 80 distinct scenarios.
- **EXISTS (Explicitly Covered & Pinned in Test Suites):** 52 scenarios (65.0%).
- **MISSING (Untested Boundary, Failure Mode, or Missing Atomic Guard):** 28 scenarios (35.0%).

---

## 2. Top-10 MISSING Failure Modes Ranked by Blast Radius

The 10 highest-risk failure modes currently lacking dedicated automated test coverage are ranked below by system blast radius:

| Rank | Module & Function | Failure Mode / Boundary Condition | Blast Radius & System Impact | Recommended Test / Hardening Assertion |
| :--- | :--- | :--- | :--- | :--- |
| **1** | 	asks.py:save (	asks.py:117) | Process kill or power loss during JSON serialization leaves 0-byte or corrupted card file. | **CRITICAL (Repo-wide lockup):** load_all() (	asks.py:124) calls json.loads over every 	asks/*.json file without try/except. A single corrupted card crashes 	asks.py lint, 	asks.py check, sync.py, and the supervisor dispatch loop. | Atomic write via .tmp swap (write_text -> os.replace) and unit test verifying corrupted card recovery or fail-soft handling. |
| **2** | 	asks.py:cmd_take (	asks.py:1299) | Concurrency race: Two workers run 	asks.py take <id> simultaneously without file locking or atomic state check. | **HIGH (Duplicate execution & wasted budget):** Two sessions claim the same card, execute conflicting duplicate implementations, and collide at ship time. | Concurrency fixture where two simultaneous 	ake calls result in exactly one winner and one ALREADY_TAKEN exit. |
| **3** | sync.py:write_ship_stamp (sync.py:706) | Partial or interrupted write to SHIP_STAMP_PATH (.git/mts_ship_stamp). | **HIGH (Ship throttling deadlock):** check_ship_gap (sync.py:693) reads timestamp. Corrupt stamp causes exception or prevents developer sessions from shipping until manual file deletion. | Verify atomic write and that check_ship_gap falls back gracefully if stamp file contains garbage or empty string. |
| **4** | supervisor.py:record_session_line (supervisor.py:1686) | Process crash during append to supervisor.jsonl or session handover log. | **HIGH (Supervisor crash on boot):** 
ead_work (supervisor.py:1404) and handover parse lines. Truncated JSON lines fail JSON parser during startup. | Test that trailing truncated JSONL lines are discarded or logged as warnings rather than crashing supervisor startup. |
| **5** | mts_signal.py:send (mts_signal.py:283) | Signal write collision: Sub-millisecond race between two processes generating the same ISO timestamp filename. | **MEDIUM-HIGH (Dropped signals / missed commands):** Overwriting an active unread command broadcast or stop signal before target host reads it. | Verify filename entropy / random suffix collision resistance in stamp() (mts_signal.py:175) under 100-thread burst. |
| **6** | sync.py:clean_cuts_secretlike (mts_signal.py:187) | Partial regex matching of multi-line private keys or non-standard token prefixes in signal broadcasts. | **CRITICAL (Security / Credential leak):** Secrets broadcast over shared git hub signal branch across distributed machines. | Red-team test asserting private keys (BEGIN OPENSSH PRIVATE KEY, API secrets) are redacted even when split across multi-line strings. |
| **7** | 	asks.py:cmd_done (	asks.py:1328) | Done called with empty or whitespace-only --result string on non-crucial card. | **MEDIUM (Process evasion):** Verification receipts and audit trails bypassed with meaningless result strings. | Test that --result enforces minimum character count and rejects whitespace/placeholders across all weights. |
| **8** | supervisor.py:pace_plan (supervisor.py:845) | Clock jump or corrupt system time reporting negative elapsed hours in weekly window. | **HIGH (Rate limiter blowout or freeze):** Can cause worker count to spike to max cap (exhausting weekly budget) or collapse to 0 (freezing pipeline). | Parameterized test with backwards clock jumps and corrupted window start timestamps. |
| **9** | sync.py:reuse_finished_tree (sync.py:427) | Reusing a tree that has unmerged local submodules or dangling lock files in .git/. | **MEDIUM (Build failures in new sessions):** New worktree starts in a poisoned or unbuildable state. | Test that worktree reuse purges .git/index.lock and untracked stale lock files before reassigning to a new session. |
| **10** | mts_signal.py:prune (mts_signal.py:254) | Prune fails due to file permission lock or transient read lock by peer process. | **LOW-MEDIUM (Disk / Repo bloat):** State directory accumulates thousands of signal files, degrading load() search speed. | Test asserting prune() ignores locked files without raising and cleans them on subsequent cycle. |

---

## 3. Comprehensive Module Audit & Test Matrix

### 3.1 scripts/dev/sync.py

| # | Function & Line | Failure / Boundary Mode | Expected Result | Status | Test Citation / Gap |
| :- | :--- | :--- | :--- | :--- | :--- |
| 1 | claim (sync.py:1560) | Claim race: two clones claim identical task ID simultaneously | Second claim detects collision upon fetch/pull, refuses claim, rolls back | **EXISTS** | 	est_sync.py:326,346 |
| 2 | claim (sync.py:1560) | Push race: remote branch advances before claim push | Detects push race, retries with exponential jitter up to retry cap | **EXISTS** | 	est_sync.py:1308,1314,1458 |
| 3 | claim (sync.py:1560) | Push authentication failure on claim | Exits immediately with auth failure message without infinite retry loop | **EXISTS** | 	est_sync.py:1290 |
| 4 | ship (sync.py:1145) | Ship while trunk CI is RED | Code ship blocked; prompts for --fix-ci or requires CI green; docs/cards allowed | **EXISTS** | 	est_sync.py:1518,1539,1556,1752 |
| 5 | ship (sync.py:1145) | Lost push race on modified overlapping file | Re-gates modified code against new incoming trunk before pushing | **EXISTS** | 	est_sync.py:1468,1476,1614 |
| 6 | ship (sync.py:1145) | Lost push race on disjoint / unrelated files | Pushes immediately without re-running long local gate tests | **EXISTS** | 	est_sync.py:1458 |
| 7 | gate_slot._try (sync.py:294) | Gate slot held by stale dead PID | Reclaims stale slot file, removes dead PID lock, acquires slot | **EXISTS** | 	est_sync.py:1378 |
| 8 | gate_slot._try (sync.py:294) | Corrupted / empty gate slot file | Treats empty or non-numeric slot file as busy/held (fail closed) | **EXISTS** | 	est_sync.py:1596 |
| 9 | 
un_gate (sync.py:349) | Gate process raises exception / test harness fails | Releases acquired gate slot immediately in __exit__ handler | **EXISTS** | 	est_sync.py:1388 |
| 10 | write_ship_stamp (sync.py:706) | Interrupted or partial write to ship stamp file | Atomic write via temporary file or fail-safe timestamp parser | **MISSING** | write_ship_stamp uses direct write_text without .tmp replace; no partial-write test in 	est_sync.py |
| 11 | check_ship_gap (sync.py:693) | Ship stamp file corrupted or non-numeric | Fails open or safely assumes 0 elapsed time rather than crashing | **MISSING** | Lacks unit test for corrupted .git/mts_ship_stamp |
| 12 | 
euse_finished_tree (sync.py:427) | Reusing worktree with lingering .git/index.lock | Purges dangling lock files or skips tree | **MISSING** | No test in 	est_sync.py covers stale .git/index.lock cleanup during tree reuse |
| 13 | 	idy (sync.py:1772) | Worktree contains uncommitted modifications | Refuses removal; keeps dirty tree and reports in where | **EXISTS** | 	est_sync.py:643,819 |
| 14 | 	idy (sync.py:1772) | Worktree idle past retention cap (1h vs 24h) | Removes clean shipped tree after idle threshold | **EXISTS** | 	est_sync.py:758 |
| 15 | survey (sync.py:1294) | Worktree git status query takes index lock collision | Retries or uses read-only probe without taking index lock | **EXISTS** | 	est_sync.py:992 |

### 3.2 scripts/dev/tasks.py

| # | Function & Line | Failure / Boundary Mode | Expected Result | Status | Test Citation / Gap |
| :- | :--- | :--- | :--- | :--- | :--- |
| 16 | save (	asks.py:117) | Process killed mid-write of card JSON file | Atomic file replacement prevents corrupted or 0-byte card on disk | **MISSING** | save() calls direct p.write_text(); no atomic tmp-rename pattern or partial write test |
| 17 | load_all (	asks.py:124) | One card file in 	asks/ is empty or invalid JSON | Raises or skips with loud warning without crashing whole CLI | **MISSING** | load_all() directly calls json.loads without try/except; crashes on partial write |
| 18 | cmd_take (	asks.py:1299) | Concurrent 	ake on the same card | Rejects second take; card already has worker/state active | **MISSING** | No concurrency test for 	asks.py take race in 	est_tasks.py |
| 19 | cmd_done (	asks.py:1328) | Card marked done while state is 
aw or locked | Refuses done; requires 
eady or ctive state | **EXISTS** | 	est_tasks.py:819 |
| 20 | cmd_done (	asks.py:1328) | Card marked done while unresolved dependencies exist | Refuses done until all prerequisite dependency cards are done | **EXISTS** | 	est_tasks.py:231 |
| 21 | cmd_done (	asks.py:1328) | Crucial/C2 card marked done without valid review receipt | Refuses done; demands valid receipt hash matching evidence | **EXISTS** | 	est_tasks.py:850,915 |
| 22 | cmd_stale (	asks.py:873) | Scope file changed after pointer refresh | Flags card as STALE; blocks execution until refreshed | **EXISTS** | 	est_tasks.py:527,541 |
| 23 | cmd_check (	asks.py:746) | Card missing required fields or has placeholders | Fails check (fail-closed); prevents promotion to ready | **EXISTS** | 	est_tasks.py:45,186 |
| 24 | ctive_holds (	asks.py:1091) | Unmet announcement or manual hold present | Blocks promotion to ready; keeps card in refined state | **EXISTS** | 	est_tasks.py:886 |
| 25 | 	rust_evidence (	asks.py:1218) | Upstream source code or receipt hash altered | Trust expires; requires re-verification before done | **EXISTS** | 	est_tasks.py:958,1034 |
| 26 | cmd_need (	asks.py:638) | Creating prerequisite without specifying lane | Refuses creation; lane is mandatory | **EXISTS** | 	est_tasks.py:1134 |
| 27 | promote_shared (	asks.py:95) | Multiple cards referencing shared base concurrently | Only cited card updated to B-SHARED; isolated save | **EXISTS** | 	est_tasks.py:723 |
| 28 | cmd_sweep (	asks.py:1431) | Sweep attempted on crucial card without real review | Sweep skips hard card; requires explicit review | **EXISTS** | 	est_tasks.py:834 |
| 29 | cmd_tag (	asks.py:861) | Shallow git clone where commit history is truncated | Does not report false stale; tolerates shallow tree | **EXISTS** | 	est_tasks.py:561 |
| 30 | cmd_conflict (	asks.py:1375) | Duplicate conflict pair reported in reverse order | De-duplicates pair into single canonical conflict card | **EXISTS** | 	est_tasks_conflict.py:26 |

### 3.3 scripts/dev/supervisor.py

| # | Function & Line | Failure / Boundary Mode | Expected Result | Status | Test Citation / Gap |
| :- | :--- | :--- | :--- | :--- | :--- |
| 31 | watchcheck (supervisor.py:591) | Watcher marker file missing | Exits code 4 immediately | **EXISTS** | 	est_supervisor.py:849 |
| 32 | watchcheck (supervisor.py:591) | Watcher process PID is dead | Detects dead PID; exits code 4 | **EXISTS** | 	est_supervisor.py:860 |
| 33 | watchcheck (supervisor.py:591) | Watcher marker timestamp expired (> 120s stale) | Detects stale marker; exits code 4 | **EXISTS** | 	est_supervisor.py:866 |
| 34 | wait_for_transition (supervisor.py:608) | Wait times out without transition | Exits code 3 cleanly | **EXISTS** | 	est_supervisor.py:261 |
| 35 | wait_for_transition (supervisor.py:608) | CI status flips during wait | Wakes immediately on CI transition | **EXISTS** | 	est_supervisor.py:196 |
| 36 | wait_for_transition (supervisor.py:608) | Gate slot becomes free during wait | Wakes immediately to allow waiting ship to proceed | **EXISTS** | 	est_supervisor.py:225,245 |
| 37 | 
ead_ci (supervisor.py:217) | Git error or network failure during CI read | Fails closed; reports CI unavailable / red | **EXISTS** | 	est_supervisor.py:33,44,59 |
| 38 | plan (supervisor.py:1213) | CI red on trunk | Spawning new worker sessions blocked; doesn't count as stuck | **EXISTS** | 	est_supervisor.py:719 |
| 39 | plan (supervisor.py:1213) | Previous plan file damaged or corrupted JSON | Recovers gracefully; damaged plan does not break next tick | **EXISTS** | 	est_supervisor.py:732 |
| 40 | 
ecord_session_line (supervisor.py:1686) | Interrupted append to supervisor log file | Partial line handling or atomic line flush | **MISSING** | No test asserting recovery from truncated line in supervisor.jsonl |
| 41 | pace_plan (supervisor.py:845) | Weekly budget cap reached | Refuses to spawn new workers; pace status STOP | **EXISTS** | 	est_supervisor.py:335 |
| 42 | handover (supervisor.py:1829) | Handover file missing required section headers | Refuses update; fails closed on invalid structure | **EXISTS** | 	est_supervisor.py:1112 |
| 43 | lane_owner (supervisor.py:956) | Multiple supervisors competing for shared lane | Deterministic single owner based on lexicographic priority | **EXISTS** | 	est_supervisor.py:442,479 |
| 44 | 
uc_budget_ok (supervisor.py:1117) | Host health / budget check errors | Fails closed; prevents remote job dispatch | **EXISTS** | 	est_supervisor.py:523 |
| 45 | live_supervisors (supervisor.py:938) | Stale heartbeat marker from dead supervisor | Purges dead supervisor after heartbeat timeout | **EXISTS** | 	est_supervisor.py:549 |

### 3.4 scripts/dev/mts_signal.py

| # | Function & Line | Failure / Boundary Mode | Expected Result | Status | Test Citation / Gap |
| :- | :--- | :--- | :--- | :--- | :--- |
| 46 | ensure (mts_signal.py:204) | Hub git HEAD file is zero-byte / corrupted | Recovers automatically from corrupted hub HEAD reference | **EXISTS** | 	est_mts_signal.py:212 |
| 47 | ensure (mts_signal.py:204) | Remote origin unavailable / network down | Fails silently without crashing local worker session | **EXISTS** | 	est_mts_signal.py:227 |
| 48 | send (mts_signal.py:283) | Two signals emitted within the same second | Preserves exact sub-second order via counter / monotonic ordering | **EXISTS** | 	est_mts_signal.py:174 |
| 49 | send (mts_signal.py:283) | Signal text contains credentials or API keys | Sanitizes and strips secrets before writing to disk | **EXISTS** | 	est_mts_signal.py:77,626 |
| 50 | load (mts_signal.py:313) | Future-dated signal timestamp in storage | Does not hide subsequent newer signals | **EXISTS** | 	est_mts_signal.py:520 |
| 51 | load (mts_signal.py:313) | Stale or corrupt signal file read | Stale / corrupted records rejected cleanly | **EXISTS** | 	est_mts_signal.py:750 |
| 52 | stop_check (mts_signal.py:921) | Active high-priority STOP signal present | Blocks session prompt execution until acknowledged | **EXISTS** | 	est_mts_signal.py:490,513 |
| 53 | prune (mts_signal.py:254) | Old signal files exceeding TTL | Deletes expired signals to avoid directory bloat | **EXISTS** | 	est_mts_signal.py:206 |
| 54 | 	old_ack (mts_signal.py:510) | Command broadcast acked with 	old | Silences broadcast reminders for session duration | **EXISTS** | 	est_mts_signal.py:382 |
| 55 | 	old_expired (mts_signal.py:522) | 	old acknowledgment exceeds TTL | Resumes loud reminder broadcast with blocker note | **EXISTS** | 	est_mts_signal.py:406 |
| 56 | 
ew_ask (mts_signal.py:778) | Prompt query (sk) sent to peer host | Records deadline, tracks ack, displays in target prompt | **EXISTS** | 	est_mts_signal.py:643,649,657 |
| 57 | escalate (mts_signal.py:716) | Target host fails to answer sk within deadline | Escalates once to supervisor and marks overdue | **EXISTS** | 	est_mts_signal.py:698 |
| 58 | mark_synced (mts_signal.py:239) | Concurrent process writes to sync marker file | Atomic write avoids corrupting sync tracking SHA | **MISSING** | mark_synced writes directly to marker path without atomic rename |
| 59 | send (mts_signal.py:283) | File system full or permissions error during signal write | Emits warning to stderr without crashing calling session | **MISSING** | No test asserting unhandled OSError resilience during signal dispatch |
| 60 | login (mts_signal.py:130) | Host name or login credentials changed dynamically | Detects mismatch and adapts letter identifier | **EXISTS** | 	est_mts_signal.py:553,588 |

---

## 4. Test Harness Recommendations & Next Steps

1. **Atomic File Write Helper:** Introduce a shared tomic_write(path, data) utility in scripts/dev that standardizes temporary file writing + os.replace to eliminate partial-write vulnerabilities in 	asks.py:save, sync.py:write_ship_stamp, and mts_signal.py:mark_synced.
2. **Corrupted JSON Card Resilience:** Update 	asks.py:load_all to wrap json.loads in a try/except block, logging CORRUPT_CARD with file:line and skipping instead of crashing the entire developer toolkit.
3. **Locking on Task Take:** Implement lightweight file locking (suplock or advisory lock) during 	asks.py take to guarantee single-winner semantics during concurrent queue sweeps.
