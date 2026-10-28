# Dev Velocity Audit — 2026-09-27

Auditor pass over MTS repo + NUC queue. Read-only; no files modified, no scripts run beyond `ast.parse`/`diff`/`grep`/`du`/`wc` for evidence-gathering. All numbers below were measured this session unless marked (guess).

## Top 3 to do this week

1. **Fix the NUC verifier's false-BLOCKED bug** (Finding 1) — 3 already-written, syntactically-valid files (bt_data.py, bt_engine.py, bt_ladder.py) are sitting marked BLOCKED for a checker bug, not a code problem. One function edit reclaims them today.
2. **Add a compile/test gate before a NUC task can be marked DONE** (Finding 2) — task 014's reply was self-reported DONE with a real syntax error (`for i i in ...`) and a nonexistent stdlib call (`NormalDist().icdf`); nothing in `verify_one` catches this today.
3. **Unblock the 32-file `.new` backlog** (Finding 3) — nine hours of already-done work (execution/backtest/java) is waiting on one testnet run; a per-module promote path would let independent modules land without waiting on each other.

---

## Ranked findings

### 1. Verifier flags valid new-file output as "unknown file names" → false BLOCKED
- **Problem**: `scripts/worker/queue_tool.py::resolve_scope` refuses any SCOPE entry that isn't already on disk (`SCOPE entry not found on disk`, line ~224), so a task whose job is to *create* a file can never list that file in SCOPE. `verify_one`'s "file names the reply mentions that do not exist" check (lines ~460-479) then flags the task's own output path (mentioned in the model's own TASK/SUMMARY line) as an unknown reference. Confirmed on tasks **011, 012, 013** (`bt_data.py`, `bt_engine.py`, `bt_ladder.py`): all three verdicts are `STATUS: BLOCKED`, but `python3 -c "import ast; ast.parse(...)"` on all six proposal files (3 impl + 3 test) that got written to `.new` **parses clean, no syntax errors**. That's 3 of the 7 BLOCKED verdicts (43%) being a checker artifact, not a code defect.
- **Fix**: add an optional `PRODUCES:` header to the spec (paths that need not exist yet), and exempt those exact paths from the "unknown file names" check in `verify_one`. Smallest version: exempt any path that exactly equals a proposal's own `<<<FILE ...>>>` target — no new header needed.
- **Estimated saving**: reclaims ~3 backtest modules (bt_data/bt_engine/bt_ladder + their tests, already written) without re-running the NUC task — each retry runs ~200-1300s on the NUC (measured from verdict SUMMARY lines) plus a repack. Saves roughly 15-20 min of NUC wall time and a repack cycle per file, guess.
- **Effort**: S (one function, ~10 lines).
- **Who**: Sonnet (small, precise code change) or operator directly.
- **Risk**: low. Add a regression test (a spec whose task creates a new file) to `queue_tool.py`'s own tests so this doesn't silently regress.

### 2. No compile/test gate on NUC output — a real syntax bug shipped as "DONE"
- **Problem**: `verify_one` only checks (a) EXPECT text substrings, (b) referenced file names, (c) whether scope inputs changed, (d) writes the `.new` proposal. It never executes or even parses the code it verifies. Task **014-bt-stats** reply (`done/014-bt-stats.reply.json`) self-reports `STATUS: DONE` but contains `for i i in oos_indices` (duplicated token, `SyntaxError`) and calls `statistics.NormalDist().icdf(...)`, which doesn't exist (real method is `inv_cdf`). Task 014 has no `.verdict.txt` at all — it was never run through `verify_one`, so this bad version sat in `done/` unflagged until presumably a later manual/retry pass replaced the on-disk `bt_stats.py.new` with a fixed version (current `.new` parses clean).
- **Fix**: in `verify_one`, before deciding verdict, run `python3 -m py_compile` (or `ast.parse`) on every `.new` proposal that ends in `.py`, in a subprocess with no network and a short timeout; any failure forces `STATUS: BLOCKED` regardless of what the model claimed. Where a matching `test_*.py` exists in scope, optionally run it too (sandboxed, read-only against the `.new` file, never touching committed code) and record pass/fail counts in FINDINGS.
- **Estimated saving**: catches shippable-looking-but-broken code before the operator's own review time is spent on it; measured: this one bug would have cost a full manual review + fix cycle (task 014's own reply took 490-1318s NUC time on similar tasks, guess similar here) plus operator diff-review time. Also raises trust in the "DONE" label, which reduces re-verification the operator does by hand on every accepted verdict.
- **Effort**: S/M (subprocess call + timeout handling + verdict logic wiring).
- **Who**: Sonnet to write, operator to review (touches the trust boundary of what gets called DONE).
- **Risk**: low — the check only runs against staged `.new` files in isolation, never live files; doesn't weaken the operator-commits/.new-staging rule, it makes that staging cheaper to trust.

### 3. 32 active `.new` files piled up, all gated on one testnet run
- **Problem**: `find` for `*.new` outside `backup_session`/`archive` returns **32 files**, timestamped 2026-09-27 07:03 through 16:04 (9 hours) — full modules: `execution/` (executor, deribit_orders, plan_compiler, position_manager, reconciler, testnet suite x2), `backtest/bt/` (bt_data, bt_engine, bt_ladder, bt_stats + 4 matching tests), `src/main/java/datafeed/` (MarketDataSnapshot, ArchiveHistoricalSource, HistoricalSource, SetupCandidatesBuilder), plus `pom.xml.new`, `compiled_engine.md.new`, `BUGS.md.new`. Per the coordinator's seed note, these are all waiting on one testnet run before any of them commit — independent modules (e.g. the backtest module, which has nothing to do with testnet) are blocked by an unrelated dependency.
- **Fix**: decouple promotion by module. A module whose own tests pass (once Finding 5's runner exists) and that doesn't touch the exchange/testnet path (e.g. `backtest/bt/*`, the Java datafeed files) can promote independently; reserve the testnet-gate for `execution/*` and `execution/testnet/*` only, which do need it.
- **Estimated saving**: unblocks roughly half the pile (backtest + java datafeed, ~14 of 32 files) immediately without waiting on testnet scheduling; testnet-dependent files remain correctly gated. Guess: saves a multi-day wait for backtest work specifically, since testnet runs are comparatively rare/manual.
- **Effort**: M (a `promote.py` helper: diff + run relevant tests + backup + apply, one command per module; operator still runs `git commit`).
- **Who**: script, written by Sonnet, run by operator.
- **Risk**: low if scoped correctly — must keep the rule that only the operator commits; the script only stages/backs up, never commits.

### 4. SCOPE line parser rejects prose / not-yet-existing paths, forcing manual workarounds
- **Problem**: `resolve_scope` raises `Refused` on any SCOPE entry not already on disk, and (per the coordinator's seed note) also on any entry with trailing prose after the path. Confirmed workaround in spec **016-daily-loss-guard-calc.md**: its task body literally contains the line `Scope note (moved from SCOPE line): none beyond this spec - self-contained, no other file needed.` — i.e., the coordinator had already hit this exact refusal and hand-edited around it rather than the tool handling it.
- **Fix**: a small `lint_spec.py` (or a check built into `pack`) that, on refusal, tells the author exactly which token in the SCOPE line is the problem and suggests the fix, instead of a bare `Refused`. Pairs naturally with Finding 1's `PRODUCES:` field.
- **Estimated saving**: avoids the manual "notice refusal → edit spec by hand → repack" loop; seed note says 3 specs hit this. Guess: 5-10 min saved per refused spec.
- **Effort**: S.
- **Who**: Sonnet.
- **Risk**: none.

### 5. No single command runs all tests
- **Problem**: repo-wide search for `run_tests`/`run_all_tests` scripts returns nothing. The committed `pom.xml` has no `maven-surefire-plugin`/JUnit dependency at all (both only exist in the unapplied `pom.xml.new`); `src/test/java` currently has **0** files (the two Java tests, `CountSignalsD4Test.java` and `P0Gate.java`, exist only as `.new`). Python has 5 committed test files under `MyTradingSys/tests/` with no single invocation gluing them together, plus 4 more `test_bt_*.py` waiting as `.new`.
- **Fix**: one script, e.g. `scripts/run_all_tests.sh`, that runs `mvn -q test` (once `pom.xml.new`/the Java tests are applied) and `python3 -m unittest discover -s MyTradingSys/tests` and the bt tests, printing one pass/fail summary.
- **Estimated saving**: removes the "which tests do I run and how" step every session pays; is also a prerequisite for Finding 2 and Finding 3.
- **Effort**: S.
- **Who**: script (operator or Sonnet).
- **Risk**: none, purely additive.

### 6. JDK17 + Maven re-provisioned from scratch each session
- **Problem**: `SESSION_4_HANDOFF.md` records `JDK 17 + Maven 3.9.9 installed in the linked-computer shell ($HOME/tools, outside [repo])`; `SESSION_2_HANDOFF.md` records an earlier session's failed attempt (`"JDK" (jdk4py) ships a jlink runtime with java.compiler but not jdk.compiler — java runs, javac does not exist`). Two different sessions independently solved (or failed to solve) the same toolchain problem.
- **Fix**: a single `scripts/provision_jdk.sh` that installs the known-good JDK17+Maven combo in one command, referenced from the standard session-start doc, so this is one command instead of rediscovering the fix.
- **Estimated saving**: avoids repeating a session's worth of trial-and-error (SESSION_2's jdk4py dead end) in a future session; guess 15-30 min per session that needs a fresh environment.
- **Effort**: S.
- **Who**: script.
- **Risk**: none.

### 7. Handoff/session doc sprawl — 13 active handoff-style docs, each a re-read cost
- **Problem**: excluding the (gitignored) `backup_session/` archive, there are **13** active `*HANDOFF*`/`*SESSION*PROMPT*`/`*SESSION_RESUME*` files today: `DSA_SESSION_PROMPT.md`, `SESSION_2/3/4_HANDOFF.md`, `SESSION_HANDOFF_2026-09-27.md`, `NEXT_SESSION_HANDOFF.md`, `SESSION_RESUME.md`, `opus_handoff_context.md`, `INDICATOR_IMPLEMENTATION_HANDOFF.md`, plus 3 older ones. Every new cold AI session pays to re-read an unknown subset of these to reconstruct state.
- **Fix**: one generated `STATUS.md` assembled (by script) from short per-task fragments, read first by every new session; per-task handoffs become inputs to the generator, not permanent standalone docs.
- **Estimated saving**: hard to quantify without token-metering a real session start; guess several thousand tokens per cold session start, compounding across every model tier that starts cold.
- **Effort**: M (needs a naming convention + one-time consolidation + a small generator script).
- **Who**: script + operator (convention decision).
- **Risk**: needs care not to drop information during consolidation — archive, don't delete, superseded docs.

### 8. Large single reference files inflate scope/context per task
- **Problem**: `MyTradingSys/runtime/compiled_engine.md` is **69KB** (also queued as a 69KB `.new`); `MyTradingSys/runtime/live_session_journal.md` is **1440 lines**. Tasks that need to cite either currently do so via SCOPE line-ranges (e.g. task 005/006 scope `compiled_engine.md:36-44`), which is the right pattern but isn't standardized/documented anywhere as the default.
- **Fix**: write down the line-range-scoping pattern as the required default for these two files in the spec template/lint (Finding 4); periodically archive old `live_session_journal.md` entries out of the head of the file (append-only logs grow forever otherwise).
- **Estimated saving**: keeps per-task token cost close to what's actually needed instead of whole-file inclusion; already partly practiced, this just locks it in.
- **Effort**: S/M.
- **Who**: Sonnet/operator.
- **Risk**: low — archiving must preserve history, not delete it.

### 9. `backup_session/` sits inside the working repo folder at 134M / 9409 files
- **Problem**: `backup_session/` is gitignored (confirmed in `.gitignore`) but still lives inside the connected project folder, at **134M across 9409 files**. Every repo-wide `find`/`grep` an AI runs (including several in this audit) must remember to exclude it, or it wastes tool calls and tokens scanning irrelevant backup copies.
- **Fix**: move it to a sibling directory outside the AI-visible project root (e.g. up one level), or, if it must stay, make exclusion of it the hard default in any repo-scanning helper script rather than something each session has to know to add.
- **Estimated saving**: avoids repeated large listing/grep calls hitting 9000+ irrelevant files; guess a handful of wasted tool calls per session that does a broad search.
- **Effort**: S (a move, or a wrapper script default).
- **Who**: operator (move) or script (default exclude).
- **Risk**: confirm nothing currently reads `backup_session/` by its current relative path before moving it.

### 10. Cheap-model output needs a review gate for destructive commands
- **Problem**: per the coordinator's seed note, a Haiku-written runbook proposed `git reset --soft HEAD~2` as a "rollback" step — plausible-looking, not necessarily correct for the actual situation, and destructive-adjacent.
- **Fix**: any AI-authored runbook or rollback instruction that contains a git history-rewriting command (`reset`, `checkout --`, `clean -f`, `push --force`) gets flagged for mandatory Sonnet/Opus/operator review before being followed, never auto-run regardless of which model wrote it.
- **Estimated saving**: avoids a real chance of destroyed work; not a time saving so much as a loss-prevention measure.
- **Effort**: S (a checklist / review step, not code).
- **Who**: process convention, operator-enforced.
- **Risk**: none — this only adds a check.

### 11. Stale in-session state descriptions
- **Problem**: `live_session_journal.md` line 1329 reads "Loop is still running pre-fix code" — a snapshot-in-time claim with no visible freshness marker once read cold in a later session, matching the coordinator's seed note about a handoff claiming a task "still running" after it had actually finished.
- **Fix**: a tiny script that stamps a `last updated: <mtime>` banner at the top of state-carrying docs (or checks it against current time and warns if stale beyond N hours) before a new session treats the doc as current truth.
- **Estimated saving**: avoids a wrong assumption costing a wasted investigation into a "problem" that already resolved; hard to quantify, guess one wasted round-trip per occurrence.
- **Effort**: S.
- **Who**: script.
- **Risk**: none.

### 12. No visibility into NUC pass-rate trend
- **Problem**: today's real verdict tally (before Finding 1's fix) is **2 DONE / 1 PARTIAL / 7 BLOCKED out of 10 verified tasks** (task 014 never verified) — a 20% clean-pass rate, 70% BLOCKED. After correcting for Finding 1's 3 false BLOCKEDs, the *true* failure rate is closer to 4/10 (40%) BLOCKED. Nobody currently has this number without grepping `done/*.verdict.txt` by hand (as this audit did).
- **Fix**: a `queue_tool.py stats` subcommand that prints DONE/PARTIAL/BLOCKED counts and top failure reasons across `done/`, so the coordinator can see at a glance whether a given task shape (e.g. "write a new file from scratch") is worth sending to the NUC at all, or should go straight to Sonnet.
- **Estimated saving**: turns a manual grep-and-count exercise (this audit) into a one-command check; also a feedback signal to route future tasks to the right model tier and cut wasted NUC cycles on task shapes that reliably fail.
- **Effort**: S.
- **Who**: script.
- **Risk**: none.

---

## Uncertainties / things not verified
- Did not run the `.new` Python files or Java `.new` files (no execution, per instructions) — "parses clean" (`ast.parse`) is necessary but not sufficient evidence of correctness; a runtime/logic bug could still exist under Finding 1's reclaimed files.
- Did not confirm whether `Dumps/backtest` (806M) is itself dead weight or active raw-data cache — out of scope for a read-only pass without asking the operator what it's for.
- Estimated time/token savings are guesses unless a specific measured number (byte count, line count, file count, verdict tally) is cited — those numbers themselves are measured this session.
