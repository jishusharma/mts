# CI/CD PIPELINE DESIGN - 2026-10-03

Session: MTS-2026-10-03-0500Z-CL-BLD-cicd-pipeline (surface CLI desktop, branch fast-track)
Written: 2026-10-03T05:15Z. Disk HEAD at write time: 1dd9aca.
Operator ask (verbatim): "Prefer simple accurate design that unblocks AI on Disk and Cloud."
Operator directive (verbatim): "No step in the CI CD to stop."
Companion: MyTradingSys/research/_archive/loose_2026-10/WORK_REVIEW_2026-10-03.md (Task 1: what the pipeline carries).
This note changes no code. Everything marked NEW is a file for a later builder; nothing marked NEW exists yet.

## 0. WHAT EXISTS ON DISK TODAY (read this session)

| Piece | State |
|---|---|
| scripts/Build-Check.ps1 (297 lines) | Java compile (L25, `mvn -q -DskipTests compile`), math tests (L36, pytest MyTradingSys/tests ignoring docs), doc tests (L50), in-flight .new list, BOM scan (py/json/ps1 only) + Cyrillic scan (0x0400-0x04FF only), BUGS.md validation, INDEX cross-checks, dispatch checks. Writes MyTradingSys/runtime/BUILD_REPORT.md; STATUS line at L279. Exit code: none set (always 0) |
| scripts/dev/run_all_tests.py | execution tests (43 names), static suite, guide checks, alert-rate, testnet status, extract-quote tests, DSA worker tests, backtest/layers test_*.py (found by rglob), pytest MyTradingSys/tests, `mvn test` unless --quick |
| MyTradingSys/tests/docs/test_integrity.py | test_1..test_5 (110 lines). test_2 at L31 |
| scripts/tools/verify_rule_citations.ps1 | conditions/*.md + compiled_engine.md tags vs research/TOM_VERBATIM_INDEX.md; exit 1 on fail |
| scripts/dev/verify_extract_quotes.py | extracts quoted verbatim + GPS position |
| scripts/sched/ (tick.py + 5 detectors) | scheduled task MTS-Scheduler-Tick (Ready). Exit 0 OK / 1 WARN / 2 RED; 24 h debounce by state hash; reports to research/sched_reports/ (gitignored). Build-Check and run_all_tests are NOT wired (tick.py L29 comment) |
| scripts/core/shared-functions.ps1 | Write-NoBom (L23), Write-NoBomLines, Test-HasBom. Build-Check defines its own Write-TextNoBom (L7) and inline BOM test instead of using them |
| pom.xml (2745 bytes, 77 lines) | okhttp 4.12.0, jackson 2.16.0, Java-WebSocket 1.5.6, slf4j-nop, junit-jupiter 5.10.2 (test), surefire 3.2.5, exec 3.1.0, jar plugin 3.3.0, Java 17. Main class datafeed.Main |
| Maven | D:\tools\apache-maven-3.9.14\bin on PATH (desktop only) |
| Git hooks, CI config | none: .git/hooks has only samples; core.hooksPath unset; no .github/ |
| Critical-file list | DSA_SESSION_PROMPT.md:156-165 (nine files). No hash baseline file anywhere |
| Tags | last-snapshot (moved by gitsnap, scripts/load.ps1:87). checkpoint-alerts, checkpoint-alerts-v2, checkpoint-session-close, v5.0.0-init |
| Remote | origin = github.com/jishusharma/mts (branches main, cloud/work, claude/quirky-knuth-y2u3ij) |

Facts that correct the brief:
- test_2_no_forbidden_refs does NOT scope to items/ and system/ only. It scans every .md/.py/.ps1/.java/.txt under MyTradingSys/ except paths
  containing archive, monitor_, __pycache__, .pytest_cache, *.old/.new/.bak, and except the research/ top folder (L48-49). Eight phrases (L33-40). Files outside MyTradingSys/ (scripts/, src/) are not scanned.
  Consequence: this note and WORK_REVIEW (research/) are exempt; the 03_FILE_INDEX rows (system/) are not and carry no listed phrase.
- Build-Check "Math tests: PASS 161/161" prints passed/passed; it never shows a failed count. It cannot show a drop in test count.
- Build-Check -DskipTests means the five JUnit classes in src/test/java never run in that gate (they run only in run_all_tests.py without --quick).
- gitsnap = `git add -A; git commit; git tag -f last-snapshot` (load.ps1:87). gitundo = `git reset --hard last-snapshot` (L89).
  At session start the tag sat at 1b7a9a1, 22 commits behind HEAD 86313de. gitundo then would have discarded 22 commits. During this session HEAD moved to 1dd9aca
  (a stage-everything close commit) and swept runtime churn into history (pm_heartbeats/*.json, orderflow_live/*.csv, _state.json, session_log.json, BUILD_REPORT.md).
- git config core.autocrlf = input. Some critical files are committed LF but live as CRLF in the working tree (compiled_engine.md: work sha256 1d52f2e4 vs
  HEAD blob bytes 7e1753c0; mts_math.py d45e51d0 vs 4b325167), others are CRLF in both (DSA_SESSION_PROMPT.md ee9493b6 both). A raw sha256 of the working file therefore
  does not equal the committed bytes. Compare git blob ids (`git hash-object <path>` vs `git rev-parse HEAD:<path>`): they agree here (compiled_engine.md dda0d7b89c01 both).

## 1. DESIGN RULES (the whole design in eight lines)

1. One entry point, NEW: scripts/dev/cicd_run.py (Python, runs on desktop and in a cloud checkout). It calls the existing tools; it replaces none of them.
2. No stage is conditional on another stage's result. Every stage runs, records PASS / WARN / FAIL / SKIP / CRASH, and the next stage runs.
3. The runner never halts, kills, restarts, commits, pushes, merges, deletes or touches HALT / AUTO_PAUSE / open trades. All stages are read-only on repo state except writing receipts.
4. Exit code is data, not a brake: 0 = all PASS/SKIP, 1 = any WARN, 2 = any FAIL/CRASH (the tick.py convention). Nothing in the pipeline reads the exit code to stop anything.
5. Release verdict is one printed line: `RELEASE: READY | READY-WITH-WARN <n> | NOT-READY <stage ids>`. It is advisory. The commit stays the operator's action;
   CLAUDE.md "never commit on Build-Check FAIL" stays the operator's rule, the pipeline just states it plainly.
6. Receipts: a RUN file per run, a WARN.jsonl line per failure, a pasted block in the session record (committed). Section 2.9.
7. Hash baseline compares git blob ids, never raw working-tree sha256 (CRLF). Section 2.5.
8. Python files start with `import sys; sys.dont_write_bytecode = True`; files are written with newline='\n', encoding utf-8, no BOM; timestamps are UTC `%Y-%m-%dT%H:%M:%SZ`;
   PowerShell writes go through Write-NoBom (shared-functions.ps1:23). Subprocess pytest runs with PYTHONDONTWRITEBYTECODE=1 and `-p no:cacheprovider`.

Tension named, not hidden: SURFACE_POLICY section 0 says irreversible or outward-facing actions stop for the operator. The pipeline contains none of those, so "no step stops"
and "operator stops for irreversible acts" do not collide. Those acts are listed in 2.10.

## 2. STAGES (order, runner, receipt)

| Stage | Runner (file) | Writes receipt to | Runner state |
|---|---|---|---|
| 2.1 intake | scripts/dev/intake_sweep.py | MyTradingSys/runtime/cicd/INTAKE.md (rewritten each run) | NEW |
| 2.2 pre-commit | scripts/dev/cicd_run.py --profile precommit (calls 2.3-2.6 on the change set) | MyTradingSys/runtime/cicd/RUN_<utc>.md | NEW |
| 2.3 build | scripts/Build-Check.ps1 + scripts/dev/run_all_tests.py, called by cicd_run.py | BUILD_REPORT.md (STATUS L279) + RUN row | exists |
| 2.4 contract | verify_rule_citations.ps1, Build-Check checks, test_integrity.py, cicd_run.py static checks | RUN rows | partly exists |
| 2.5 artifact | cicd_run.py stage `artifact` reading MyTradingSys/system/critical_files.json | RUN rows | NEW + baseline NEW |
| 2.6 live-path | cicd_run.py stage `livepath` | RUN rows | NEW |
| 2.7 release | operator, new `gitrelease` function in scripts/load.ps1 | the commit + session record block | NEW |
| 2.8 post-close | cicd_run.py --profile postclose, started by scripts/sched/check_cicd.py on the tick | RUN file + WARN.jsonl | NEW |
| 2.9 failure handling | every stage | WARN.jsonl, tick digest | NEW |

Receipt directory: MyTradingSys/runtime/cicd/ (NEW). Add to .gitignore: `MyTradingSys/runtime/cicd/*` and `!MyTradingSys/runtime/cicd/.gitkeep`.
RUN row format (pipe separated, one line per check): `STAGE|CHECK|STATUS|DETAIL|SECONDS`. WARN.jsonl line: `{"utc","run","stage","check","severity","detail","path"}`; append only.

### 2.1 Task intake

Sweep every source named in Task 1 in one pass (scripts/dev/intake_sweep.py, NEW):
BUGS.md rows; items/INDEX.md rows; BUILD_PIPELINE.md rows (registry ids and slugs); apparatus_fixes.md OPEN + NEEDS OPERATOR bullets;
NEXT_SESSION_HANDOFF.md OPEN QUEUE bullets; Dumps/operator/context/DSA_HANDOFF.md section 10; OPERATOR_DIRECTIVE_*.md (presence and size; directives are constraints, not rows);
BUILD_REPORT.md "In-flight .new files" list (staged work awaiting promotion is pending work); MyTradingSys/system/sessions/*.md with status open.
Per id it records which sources carry it and each source's status, then flags: ID-ONLY-IN-ONE-SOURCE, STATUS-DISAGREE, STALE-VS-GIT (pipeline says QUEUED but git log
carries the id with a landed subject), PIPELINE-LOCAL (R4-T1, R4-T2, R4-T3, R4-D, R5, R6, R7 and 0.x rows; reported, never an orphan).
Today's run would report: 6 ids only in INDEX (T053-T058), 4 status disagreements (T062, B077, B078, B079), 14 stale pipeline rows (WORK_REVIEW 1.2),
and handoff-only items with no id (Tom spec, classify_msb, MISSING_PIECES read).

Registry choice: ONE registry, MyTradingSys/research/BUGS.md. Reason: it already declares itself the single source (line 3), Build-Check already validates it
(L135-197), and the three hand-kept copies drifted into 14 stale rows and 10 id/status disagreements today; one writable table plus read-only views cannot drift.
- Every other source drains into BUGS.md by appending a row (BUGS rule 3). New work found in a handoff, apparatus_fixes bullet or pipeline row gets an id on first sight (next free: B084, T063; a concurrent session took B083 at about 05:15Z, see WORK_REVIEW section 8).
- items/INDEX.md stays hand-kept for its one-line state, but the sweep compares its status token to BUGS.md every run (the missing INDEX -> BUGS direction).
- BUILD_PIPELINE.md stores order and wave only for registry rows; status for a registry id is read from BUGS.md at report time. Pipeline-local slugs keep their own status.
- Multiple registries plus a reconciliation step was rejected: it keeps all three drift sources and adds a fourth artifact to maintain.
The sweep prints proposed rows (`--propose`); the AI session appends them. It does not wait for approval.

Operator-blocked rows (B070 friction value, R4-D, B063, T046) are tagged BLOCKED-ON-OPERATOR in INTAKE.md, skipped by the build order and logged once per 24 h (tick debounce); the flow continues to the next row.

### 2.2 Pre-commit gate (operator desktop)

Existing checks first:
| Check | Where | Pass criterion |
|---|---|---|
| Java compile | Build-Check L25 | mvn exit 0 |
| Math tests | Build-Check L36 | pytest exit 0 and a "N passed" line (161 at 04:21:28Z) |
| Doc tests | Build-Check L50 | exit 0, 5 passed |
| BOM, Cyrillic | Build-Check L102-132 | 0 hits (scope: runtime py/json, scripts ps1; Cyrillic also md in research, runtime, conditions, system) |
| BUGS validation, INDEX, files cross-check, dispatches | Build-Check L135-277 | all OK |
| Full offline suite | run_all_tests.py | "ALL TESTS PASSED" |
| Rule citations | verify_rule_citations.ps1 | exit 0 |
| Extractions | verify_extract_quotes.py <file> | exit 0 (only when an extract is in the change set) |
Missing checks (named as missing; NEW in cicd_run.py unless noted):
- M1 Java tests in the Build-Check gate (change `-DskipTests compile` to `mvn -q test`; no pom edit needed; this is T037).
- M2 test-count floor: compare "N passed" to the previous RUN receipt; WARN on a drop (Build-Check hides it).
- M3 Python execution/static check on every changed .py: `compile(open(f,'rb').read(), f, 'exec')` (no bytecode written) plus a PowerShell parse of every changed .ps1
  ([System.Management.Automation.Language.Parser]::ParseFile). Reason: LESSONS_LEARNED A (a comment swallowed three dict keys; nothing executed the file).
- M4 fail-before evidence: the session record must carry a T3 line naming the test and its result on pre-change code (CLAUDE.md gate). Cannot be proven mechanically; the stage checks the line exists and WARNs if absent.
- M5 changed-file map: from `git status --short` minus the dirty allowlist (2.7), decide which of 2.3-2.6 apply (path triggers: execution/ and layers/alerts/ -> 2.6; critical list -> 2.5; src/**/*.java -> Java tests; items/ system/ -> contract).
- M6 hook (optional): scripts/dev/install_hooks.ps1 (NEW) copies a pre-commit hook that runs cicd_run.py --profile precommit and ALWAYS exits 0, so it informs and never blocks.
Verdict mapping for RELEASE: any FAIL in 2.3, 2.4 or 2.5 (artifact DRIFT not covered by a baseline update in the same change set), or a 2.6 row FAIL on a live-path change -> NOT-READY. WARN rows -> READY-WITH-WARN.

### 2.3 Build gate

Run from repo root, desktop:
1. `mvn -q -DskipTests compile` (Build-Check L25; mvn resolves through D:\tools\apache-maven-3.9.14\bin). Pass: exit 0.
2. `mvn -q test` (run_all_tests.py step 5; becomes Build-Check's Java step per M1). Pass: exit 0; surefire reports under target/surefire-reports. Classes today: CountSignalsD4Test, ExtraSetupBuilderFvgTest, HistoricalSnapshotNoLiveCallsTest, NetRRConstantTest, NetRrFloorTest (P0Gate.java.new is staged, not run).
   Caution: both write target/, which the live loop's per-cycle mvn also uses (start-trading-day.ps1 spawns `mvn snapshot` each cycle). Build-Check already does this today; run it, do not run two at once, and never delete target/.
3. `python -m pytest MyTradingSys/tests --ignore=MyTradingSys/tests/docs -q` (Build-Check L36). Pass: exit 0 and N >= previous N.
4. `python -m pytest MyTradingSys/tests/docs -q`. Pass: exit 0, 5 passed (test_3 version consistency and test_4 SIZE claim within 1.0 KB of 03_FILE_INDEX.md actual size are in this set).
5. `python scripts/dev/run_all_tests.py` (use --quick when mvn is absent). Pass: "ALL TESTS PASSED".
6. Not found in any runner: tests/test_worker_prefix_hash.py (repo-root tests/). Add `python -m pytest tests -q` as a RUN check (T5).
Receipt: BUILD_REPORT.md for Build-Check items (STATUS: PASS|FAIL at L279) and one RUN row per command above with exit code, count, seconds. The RUN file, not BUILD_REPORT.md, is the authoritative fresh result.

### 2.4 Contract gate

| Check | Script | State |
|---|---|---|
| Rule-citation verify | scripts/tools/verify_rule_citations.ps1 | exists; PowerShell, so SKIP in a cloud checkout without pwsh (named gap: no Python port) |
| BOM check | Build-Check L102-132 (py/json/ps1 in listed dirs) | exists; gap: no BOM scan of .md, nor of execution/, backtest/, src/. NEW: scan every changed file with Test-HasBom logic |
| Non-ASCII check | Build-Check counts Cyrillic only | gap: no general non-ASCII scan. NEW: report non-ASCII count per changed file (DSA_SESSION_PROMPT.md:150 already asks for it) |
| Forbidden phrases | MyTradingSys/tests/docs/test_integrity.py::test_2_no_forbidden_refs (L31) | exists; real scope in section 0 (not items/system only). Pipeline adds nothing; it reports test_2's own hit lines |
| Registry contract | Build-Check Bugs/Index (OPEN needs items file; CLOSED needs receipt; IN-FIX over 14 days) | exists; gap: INDEX -> BUGS and status agreement (intake sweep, 2.1) |
| File-index row for every new file | CLAUDE.md gate | gap. NEW: every file added under MyTradingSys/ in the change set has a 03_FILE_INDEX.md row; test_4 SIZE header refreshed when rows are added |
| Session record + trailer | SURFACE_POLICY section 4 | gap. NEW: a record exists for the session ID, has status/started/model (same fields check_sessions.py reads) |
Receipt: RUN rows `contract|<check>|<status>|<detail>`.

### 2.5 Artifact gate (critical-file hashes)

Critical files (DSA_SESSION_PROMPT.md:156-165), by path:
MyTradingSys/runtime/compiled_engine.md; DSA_SESSION_PROMPT.md; MyTradingSys/system/01_AI_BEHAVIOR.md; MyTradingSys/runtime/mts_math.py;
MyTradingSys/runtime/math_object_builder.py; scripts/core/start-trading-day.ps1; scripts/core/mode.ps1; scripts/core/stop-day.ps1; MyTradingSys/PROJECT_VISION.md.
Proposed additions (single-source thresholds and build input read by live code): MyTradingSys/system/net_rr_floor.json; MyTradingSys/system/runner_min_distance.json; pom.xml.

Baseline file: none exists on disk (searched system/, runtime/, research/; only research/_archive/loose_2026-10/_SESSION_20260913_HASHES.md, a one-off, and tests/test_worker_prefix_hash.py, a one-file check).
It must be created as MyTradingSys/system/critical_files.json (NEW) and hold, per file:
`{"path","blob" (40-hex git blob id from git hash-object),"sha256_8" (first 8 hex of working-tree bytes, the form used in BUGS receipts),"eol" ("CRLF"|"LF"),"approved_by" (session ID),"approved_commit" (short sha or "pending")}` plus `updated_utc`.
Seed values observed 2026-10-03 (OBSERVED, not approved; first approval is the operator's):

| path | blob (12) | work sha256_8 | eol |
|---|---|---|---|
| MyTradingSys/runtime/compiled_engine.md | dda0d7b89c01 | 1d52f2e4 | CRLF (977 CR) |
| DSA_SESSION_PROMPT.md | 1e8f2381243e | ee9493b6 | CRLF (357 CR) |
| MyTradingSys/system/01_AI_BEHAVIOR.md | e7618d64c608 | dd54759c | CRLF (517 CR) |
| MyTradingSys/runtime/mts_math.py | 0b0bb42fc367 | d45e51d0 | CRLF (528 CR) |
| MyTradingSys/runtime/math_object_builder.py | 6f880c366bc9 | d1876da6 | CRLF (467 CR) |
| scripts/core/start-trading-day.ps1 | 742247da1d7d | 1679e96e | CRLF (841 CR) |
| scripts/core/mode.ps1 | 570edff90b1d | 05dbfa1a | CRLF (149 CR) |
| scripts/core/stop-day.ps1 | 4ebabbb0bc08 | 15486b3e | CRLF (38 CR) |
| MyTradingSys/PROJECT_VISION.md | d478e6122aa5 | 41e44e49 | CRLF (206 CR) |
| MyTradingSys/system/net_rr_floor.json (proposed) | 9f18137397b2 | - | - |
| MyTradingSys/system/runner_min_distance.json (proposed) | 4d7c5fbc3d91 | - | - |
| pom.xml (proposed) | 282ddaed04ee | - | - |
(CR counts are lines containing CR from grep -c; that equals total lines only if the whole file is CRLF. Not checked for mixed endings.)

Which hashes must match what:
- A. Pre-commit: `git hash-object <path>` of the working file == baseline.blob for every critical file NOT in the change set. A critical file in the change set must come with a
  baseline update in the same change set (new blob, new sha256_8, approved_by = this session); otherwise DRIFT-UNAPPROVED (FAIL).
- B. Post-commit: `git rev-parse HEAD:<path>` == baseline.blob.
- C. Cloud: same as B on the pushed ref (blob ids are identical on any machine; raw sha256 is not).
- D. Live-import drift (desktop, report only): a live-imported file whose mtime is newer than its running process's start time (Get-CimInstance Win32_Process CreationDate) is listed; restart is the supervisor's job.
The existing "hash, edit, hash, diff" routine (NEXT_SESSION_HANDOFF.md:74) is the human side of A; the baseline makes it checkable.
Receipt: RUN rows `artifact|<path>|MATCH|DRIFT|DRIFT-UNAPPROVED|NO-BASELINE`.

### 2.6 Live-path gate

Trigger files (any one in the change set turns the gate on):
1. Everything under MyTradingSys/execution/ except `.secrets/` (never opened), `*.pre_*` backups, __pycache__, and runtime state (journal/, plans/, halt_history/, pm_heartbeats/, *_state.json, *.jsonl, AUTO_PAUSE).
   Code today: auto_trader.py, executor.py, position_manager.py, deribit_orders.py, deribit_client.py, deribit_read.py, kill_switch.py, risk_guard.py, daily_loss_guard.py, daily_loss_monitor.py,
   orphan_watchdog.py, orphan_watchdog_cli.py, reconciler.py, journal.py, plan_compiler.py, new_plan.py, pm_heartbeat.py, mainnet_plan_check.py, mainnet_pnl.py, soak_report.py, auto_trader_config.json.
2. MyTradingSys/backtest/layers/alerts/ (live_runner_cli.py) per CLAUDE.md "execution/ or layers/alerts/".
3. Order-state readers and writers outside execution/. Discovery rule (cicd_run.py re-runs it every time): files under the repo (excluding archive, backup_session, _archive, Dumps, *.pre_*, test_*) that match
   `AUTO_PAUSE|HALT_|halt_history|private/(buy|sell|edit|cancel)|stop_market|trade_ledger|auto_trader_state|pm_heartbeat`. Today that returns mts.ps1, scripts/dev/testnet_canary.py, scripts/dev/testnet_status.py
   (run_all_tests.py and research/.../repro_ft2.py match but only reference names).
4. The live loop, imported or compiled every cycle: scripts/core/*.ps1, runtime_data/launch-*.vbs, src/main/java/datafeed/*.java, runtime/math_object_builder.py, mts_math.py, build_mo_cli.py, update_market_state.py,
   system/net_rr_floor.json, system/runner_min_distance.json.
Gate checks (all evidence-existence checks; each writes a row, none blocks):
- L1 one writer: SUPERVISOR_LOG.md (research/fast_track_2026-09-27/) names this session ID against the area, and no other session record with status open names the same area. Missing -> WARN.
- L2 staging: the file is `<file>.new`, or the session record says no running process imports it. In-place edit of a file a running process imports (python/PowerShell command lines from Get-CimInstance) -> FAIL. CLAUDE.md is stricter than SURFACE_POLICY.md L19 ("Builders edit live. Gate before commit. Stage .new only when the running system imports the file mid-session", changed by 5c8f83b); the stricter CLAUDE.md rule is applied here and the conflict is flagged for the operator (T5).
- L3 four-step proof: hash before, edit, hash after, diff read (NEXT_SESSION_HANDOFF.md:74 "hash, edit, hash, diff"; for live files the handoff adds stage .new, proof, restart). Evidence = baseline update (2.5) plus a session-record line. The longer DSA proof procedure was removed in 5c8f83b, so only this short form is on disk.
- L4 required tests (CLAUDE.md): the change set holds a test touching the changed module and the test text covers restart/reset state, non-trade balance moves (deposit, transfer, funding) and API errors (URLError, HTTP). Keyword scan per class; a missing class -> WARN naming it. Fail-closed on safety checks is reviewed by L5.
- L5 Opus review: the session record carries `review: <session ID>`; none -> WARN. The record template (sessions/README.md) has no review field today; add it (NEW). The review itself is a human/AI step, never run by the pipeline.
- L6 AUTO_PAUSE: if MyTradingSys/execution/AUTO_PAUSE exists, SUPERVISOR_LOG holds its owner and expected end; absent or overdue -> WARN (CLAUDE.md "each wake clears or escalates"). The pipeline never creates or removes the file.
- L7 restart evidence, checked at post-close (2.8): SUPERVISOR_LOG has a "restarted <process> <utc>" line after the commit. Only the supervisor restarts; builders do not.
- L8 touch list: the change set contains none of halt_history/, journal/, plans/, pm_heartbeats/, AUTO_PAUSE (they are runtime state).
Receipt: RUN rows `livepath|L1..L8|<status>`.

### 2.7 Release gate

- What moves from working tree to committed: the change set only, by explicit pathspec (`git add -- <paths>`), listed in the session record. Never `git add -A`, never `git commit -a`
  (LESSONS_LEARNED 2026-10-02: a stage-all silently deleted 7 tracked .new files; HEAD 1dd9aca just swept runtime churn the same way).
- Dirty allowlist (excluded from every dirty check and never in a pathspec): MyTradingSys/runtime/BUILD_REPORT.md, MyTradingSys/runtime/session_log.json, MyTradingSys/execution/pm_heartbeats/,
  MyTradingSys/runtime/orderflow_live/, MyTradingSys/research/testnet_status/ (daily files are committed deliberately, not swept), plus everything gitignored.
  Recommended .gitignore additions: MyTradingSys/execution/pm_heartbeats/ and MyTradingSys/runtime/orderflow_live/ (both now tracked by 1dd9aca; the operator untracks with `git rm --cached -r`).
- BUILD_REPORT.md: tracked, rewritten by Build-Check and the loop, always modified between sessions. Handling: allowlisted; read only for its STATUS line (L279) and age; the RUN receipt is the fresh result;
  the committed evidence is the block pasted into the session record. Cloud sees the committed copy only, which is a snapshot and may be stale.
- Tags: `last-snapshot` moves only after a successful release commit, to that commit (the B052 guard in gitsnap already refuses to move it when the commit fails).
  Replace gitsnap with `gitrelease <session ID> "<subject>" <paths...>` (NEW, scripts/load.ps1): explicit pathspec, commit with trailer, then `git tag -f last-snapshot`.
  gitundo (`reset --hard last-snapshot`) is only safe when the tag equals HEAD; the post-close check (2.8) warns whenever it does not (it was 22 commits behind at session start).
  Other tags (checkpoint-*, v5.0.0-init) are never moved by the pipeline.
- Who runs it: the operator. This session and every builder session only prepare the change set and print the command.
- Commit message: subject `<id>: <what>. Paths: <list>` (the form of recent commits), blank line, trailer `MTS-Session: <ID>` (SURFACE_POLICY.md:86; present on 86313de and the DSA close commits).
- Push: operator only (outward-facing, SURFACE_POLICY section 0). Cloud sees nothing until it happens.

### 2.8 Post-close check

Runs after the operator commits. Trigger: scripts/sched/check_cicd.py (NEW detector for the existing tick) notices HEAD differs from the last verified HEAD and runs
`cicd_run.py --profile postclose`. The profile is fast (no mvn, no full pytest) so it is safe on the tick clock; tick.py L29 records that the heavy runners were not wired because their runtime was unverified.
Checks:
- P1 drift: `git status --short` minus the dirty allowlist is empty. Anything else = DRIFT row (forgotten file, or runtime output not ignored).
- P2 artifact: HEAD blob == baseline for every critical file (2.5-B).
- P3 registry: intake sweep reruns; every BUGS row closed in this commit has a receipt whose hex token resolves (`git cat-file -e <hash>^{commit}`).
- P4 session: record exists, status closed, `commits:` populated, trailer ID on HEAD matches the record.
- P5 file index: files added in HEAD under MyTradingSys/ each have a 03_FILE_INDEX.md row; test_4 SIZE claim within 1.0 KB.
- P6 tag: last-snapshot == HEAD (informational; WARN when it lags, since gitundo would discard the gap).
- P7 live-import drift (2.5-D) and the L7 restart evidence (2.6).
- P8 BUILD_REPORT.md STATUS line and age (information only).

### 2.9 Failure handling

Every failure does the same four things and then the run continues:
1. stdout line `WARN|FAIL <stage>/<check>: <detail>`.
2. a row in MyTradingSys/runtime/cicd/RUN_<utc>.md.
3. one line appended to MyTradingSys/runtime/cicd/WARN.jsonl (append only, never edited, never deleted).
4. check_cicd.py includes new WARN.jsonl hashes in the next sched digest; the tick already debounces a repeated identical hash for 24 h (tick.py DEBOUNCE).
Special cases:
- stage raises: caught, row `CRASH`, last 20 traceback lines in the RUN file, next stage runs.
- tool missing (mvn, powershell, python module): row `SKIP` with the reason; not a FAIL.
- command exit code non-zero: FAIL row with exit code and the last lines of output (CLAUDE.md: never conclude from truncated output; the full output goes to RUN_<utc>.out.txt).
- receipt cannot be written: print the row to stdout and continue; stdout is the last-resort receipt.
- timeouts: none defined by the operator, so none invented; the runner records wall seconds per command and kills nothing.
- repeated failure: same hash -> one digest line per 24 h; no counters, no thresholds.
Where each failure lands: RUN_<utc>.md (row), WARN.jsonl (line), research/sched_reports/tick_<utc>.md (digest, gitignored), session record (pasted summary at close, committed).

### 2.10 What does NOT belong in this pipeline

| Item | Why |
|---|---|
| Stop, start, restart of any process; HALT or AUTO_PAUSE files; open trades | supervisor-only (CLAUDE.md); irreversible |
| Mainnet anything; testnet order placement | T050 phases are manual testnet runs, not CI; mainnet is out by hard rule |
| Reading `.secrets/`, `.env`, keys | hard rule |
| Commit, push, merge, rebase, reset, force-move of any ref except the post-commit `last-snapshot` the operator's own function moves | operator action; outward-facing |
| Long backtests and parameter sweeps (R4-T3) | they are queue tasks with results; the pipeline checks the result file exists, not the run |
| Web or YouTube research | rate limits and the playbook Part I gate (LESSONS D) |
| Budget gates, token caps, spend refusals | operator correction 2026-10-02: never refuse work for budget |
| Qwen / NUC lanes | decommissioned 2026-10-01 |
| DSA prompt-conformance checks | purged in 5c8f83b |
| A hosted CI service (GitHub Actions) | new cloud dependency the operator did not name; it would see pushed refs only, with no runtime_data, no .secrets, no loop, no Windows PowerShell 5.1 behavior |
| Opus review and Tom-citation judgment | human/AI judgment; the pipeline checks the record of it |
| Tuning any strategy parameter | provenance rule: sourced or NO-SOURCE, never tuned. Measuring under OPERATOR-EXPERIMENT is a task, not a gate |

## 3. WHO RUNS WHAT (coordinator, cloud session, worker)

| Actor | Has | Runs | Cannot |
|---|---|---|---|
| Desktop coordinator (CLI session) | disk, shell, Maven, PowerShell, live tree | all stages, profile desktop / precommit / postclose; prints the commit command | commit, push, restart live processes |
| Cloud session (CLD) | a checkout of pushed refs, shell, no LAN | profile cloud: 2.1 intake, 2.4 static + doc tests, 2.5 blob compare via `git rev-parse <ref>:<path>`, 2.6 static diff checks, Python offline tests; Java only if JDK + Maven exist in its container (not assumed) | see section 4 |
| Worker (no shell, no disk; DSA chat, subagent text, queue lanes) | text in, text out | nothing; its reply is a payload | write receipts, run tests |
Worker output enters at 2.1 (proposed rows) and is checked by the coordinator before it reaches disk: spot-check one concrete claim per report (CLAUDE.md), read the diff before merging a change,
tests written from the spec by a Sonnet-or-higher session, extractions through verify_extract_quotes.py, the request checklist matched item by item (LESSONS B, F). Worker checks are the coordinator's checks; a worker never "passes" a stage.
The worker brief carries the same T0-T5 contract and names the exact output path (LESSONS 2026-10-01: a read-only brief once produced a result that existed only in chat).

## 4. CLOUD: WHAT IT CAN AND CANNOT VERIFY

The ask names "Disk and Cloud". Cloud here means the Claude cloud sessions on branch cloud/work (SURFACE_POLICY table: "pushed git refs only; no LAN, no gitignored files"). No hosted CI is added.
Cloud can verify, from pushed refs: blob ids of critical files; registry reconcile (BUGS, INDEX, pipeline are committed); doc tests; Python tests that need no network and no gitignored data;
commit trailer and session record on the branch; file-index rows for added files; diff-based live-path static checks; whether the branch is merged (`git cherry`, not a three-dot diff).
Cloud cannot verify: anything under runtime_data/, Dumps/, `.secrets/`; any `*.new` file (gitignored); running processes, scheduled tasks, the supervisor; testnet or Deribit; Java compile or tests unless its container has JDK 17 + Maven;
PowerShell 5.1 behavior (BOM from Set-Content) and verify_rule_citations.ps1 without pwsh; the CRLF bytes of a Windows working tree; BUILD_REPORT freshness (a committed snapshot only); that anything was promoted or restarted.
So cloud proves "the pushed content is internally consistent and its hashes match the baseline". Disk proves "it runs here". Neither replaces the other; the RUN block pasted into the session record is what carries desktop evidence to the cloud.
Cloud sessions commit and push between batches (LESSONS 2026-10-02) and run `cicd_run.py --profile cloud` before each push, writing the result into their session record.

## 5. T0-T5 CONTRACT

T0 questions answered before design:
- Where are the task sources? 11 files read (WORK_REVIEW section 0). Only one OPERATOR_DIRECTIVE_*.md exists.
- What does "no step stops" mean beside "never commit on Build-Check FAIL"? The pipeline never halts; the release verdict is advisory; the commit stays the operator's.
- Is there any CI config or hook? No (.git/hooks samples only, no .github/).
- Does a hash baseline exist? No. What bytes are hashed? Git blob ids, because core.autocrlf=input makes raw sha256 differ between working tree and committed bytes.
- Is test_2 scoped to items/ and system/? No; everything under MyTradingSys/ except research/ and archive-type paths.
- Who writes BUILD_REPORT.md? Build-Check.ps1 (L289-293), and the loop per NEXT_SESSION_HANDOFF.md:67. Not independently traced.
T1 file shape. This session: new MyTradingSys/research/_archive/loose_2026-10/CICD_PIPELINE_2026-10-03.md and WORK_REVIEW_2026-10-03.md; two rows in MyTradingSys/system/03_FILE_INDEX.md (and the SIZE header number so test_4 stays green);
one session record MyTradingSys/system/sessions/MTS-2026-10-03-0500Z-CL-BLD-cicd-pipeline.md (CLAUDE.md requires registering the session). No code, no config edited.
Downstream (NEW, for builders): scripts/dev/cicd_run.py; scripts/dev/intake_sweep.py; scripts/dev/test_cicd_run.py (tests from this spec, fail-before required);
MyTradingSys/system/critical_files.json; scripts/sched/check_cicd.py; scripts/dev/install_hooks.ps1 (optional); `gitrelease` in scripts/load.ps1; `.gitignore` lines (cicd receipts, pm_heartbeats, orderflow_live);
Build-Check.ps1 Java step (M1); sessions/README.md `review:` field; a row per new file in 03_FILE_INDEX.md.
Suggested build order (no stop between): intake_sweep -> critical_files.json + artifact stage -> Build-Check Java step -> cicd_run skeleton with receipts -> contract extras -> livepath -> check_cicd -> gitrelease.
T2 output shape: reply of at most 10 lines plus two receipts (path, line count, sha256). The full review and design are on disk.
T3 not applicable: no code changed.
T4 disk verification, operator-run, after this session:
- `Get-FileHash -Algorithm SHA256 MyTradingSys\research\_archive\loose_2026-10\CICD_PIPELINE_2026-10-03.md, MyTradingSys\research\_archive\loose_2026-10\WORK_REVIEW_2026-10-03.md` must equal the receipts in the reply.
- `python -c "import sys;[print(p, open(p,'rb').read(3)==b'\xef\xbb\xbf', b'\r' in open(p,'rb').read()) for p in sys.argv[1:]]" MyTradingSys/research/_archive/loose_2026-10/CICD_PIPELINE_2026-10-03.md MyTradingSys/research/_archive/loose_2026-10/WORK_REVIEW_2026-10-03.md` must print False False for both (no BOM, LF).
- `Select-String -Path MyTradingSys\system\03_FILE_INDEX.md -Pattern 'CICD_PIPELINE_2026-10-03|WORK_REVIEW_2026-10-03'` returns two rows.
- `python -m pytest MyTradingSys/tests/docs -q` prints 5 passed (test_4 SIZE, test_2 phrases).
Downstream change proof once built: `python scripts/dev/cicd_run.py --profile desktop` ends with a `RELEASE:` line and writes MyTradingSys/runtime/cicd/RUN_<utc>.md; `Select-String -Path MyTradingSys\runtime\cicd\RUN_*.md -Pattern '\|FAIL\|'` lists every failure; the tests in test_cicd_run.py fail on a tree without the module and pass with it.
T5 MISSED (could not verify, and why):
- Not run: Build-Check.ps1, run_all_tests.py, mvn, the doc tests. Reason: mvn compile writes target/, shared with the live loop; counts quoted are from BUILD_REPORT.md 04:21:28Z. T4 above is where the operator runs them.
- "Four-step proof" is not defined verbatim on disk; I mapped it to "hash, edit, hash, diff" (NEXT_SESSION_HANDOFF.md:74) after 5c8f83b removed the DSA proof procedure. If the operator means another four steps, L3 changes.
- CLAUDE.md (never edit an imported file in place; stage .new) and SURFACE_POLICY.md L19 (builders edit live) disagree. Gate L2 follows CLAUDE.md. Needs an operator ruling.
- Who triggers the loop's BUILD_REPORT.md rewrite: not traced beyond Build-Check.ps1 and the handoff note.
- Whether the cloud container has JDK 17, Maven or pwsh: unknown, so Java and the .ps1 verifier are SKIP-by-default in profile cloud.
- Mixed line endings inside critical files: CR-line counts only, no CRLF-vs-LF per-line audit.
- tests/test_worker_prefix_hash.py: not found in either runner; left as a named gap, not confirmed unrun.
- core.hooksPath unset and no hooks installed on this machine; the laptop (LAP) checkout was not inspected.

# END
