# Code dedupe audit: scripts/dev and its tests (2026-10-28)

Card `duplicate-code-and-tests-audit`, decision `d-dedupe-lean-no-contradiction` (OPERATOR_DECISIONS.md:1333). Audit only: nothing deleted, only this file written. Tree: trunk `8f50414e9`.

**Default rule applied (OURS, from the decision):** the copy in the module with most callers / the trunk behaviour wins; the loser is imported or deleted in the same change; a deletion needs `git grep -w <name>` to show no other caller and the tests to pass (failing-first or a passing run). Paths are under `scripts/dev/` unless stated. `git grep` = run in the audit worktree at trunk this turn; `count` = matching lines.

**Wiring checked before calling anything dead:** `.claude/settings.json` hooks (trunk_lag, shot, mts_signal, ci_watch, c_drive_guard, role_loader), `run_all_tests.py` (PYTEST_LAYER_PATHS 38-58, CI_FILE_S 897-), `extra_tests.tsv` (132 lines), `run_extra_tests.py` discovery, task-card `commands`, docs. `perm_hook.py` and `role_hook_launcher.py` are installed per machine into `~/.claude/settings.json` (UNATTENDED_PERMISSIONS.md:16-18), so a repo grep alone under-counts them.

Method (scripts kept in the session scratchpad, not shipped): AST walk of all 234 `scripts/dev/*.py` for identical or >0.8-similar function bodies across files, duplicated UPPER constants, functions whose name occurs once in the whole tree, scripts no other code file names; plus 282 test files for identical bodies, shared test-name sets, double registration.

## Ranked table (32 rows)

Ranking = risk of silent drift (live-path or safety text first), then lines saved. Choice column: KEEP A / KEEP B = which copy survives.

| # | Kind | Side A (file:line) | Side B (file:line) | Evidence (command -> count) | Keep / remove (default rule) | Proposed edit |
|---|---|---|---|---|---|---|
| 1 | constant vs literal | supervisor.py:729 `HEARTBEAT_MIN = 75` | supervisor.py:354 docstring `< 75 min`, :999 `"no heartbeat < 75 min"`, :1708 comment | `git grep -n "75 min" scripts/dev/supervisor.py` -> 3; `git grep -n HEARTBEAT_MIN scripts/dev/supervisor.py` -> 5 | KEEP A (the constant; :1054 already uses it) | :999 make it an f-string `{HEARTBEAT_MIN} min` (the only user-visible line; 354 and 1708 are prose, reword to "HEARTBEAT_MIN") |
| 2 | duplicated block (safety text) | testnet_canary.py:66-71 `_KW _ORDER _PLAN _DIGITS _TOKEN`, :74 `scrub()` | testnet_status.py:35-40, :43 `scrub()` | `git grep -n -E "^(_KW\|_PLAN\|_DIGITS\|_TOKEN\|BRAKE_FILES\|TS_FMT) *=" scripts/dev/testnet_canary.py scripts/dev/testnet_status.py` -> 12 (6+6, same regexes); both `scrub` bodies are the same 5 statements | KEEP testnet_status.py (has its own test: `grep -c scrub test_testnet_status.py` -> 3; canary test -> 0) | New `testnet_common.py` (or import from testnet_status): `scrub`, `_KW.._TOKEN`, `BRAKE_FILES`, `TS_FMT`; both scripts import. Redaction regexes must not drift (secrets path) |
| 3 | dead function | run_all_tests.py:307 `run_step` | none | `git grep -w -n run_step` -> 1 (def only) | REMOVE (gate runner, but no caller; steps go through the pool classes) | Delete def 307-~330; run `run_all_tests.py --quick` |
| 4 | dead function | role_loader.py:313 `explicit_role` (8 stmts) | none | `git grep -w -n explicit_role` -> 2 (def + a research md line) | REMOVE | Delete def; role_loader is a hook, so run `test_role_loader.py` plus a manual `role_loader.py hook` smoke |
| 5 | dead function | role_loader.py:204 `clean_prompt` | none | `git grep -w -n clean_prompt` -> 1 | REMOVE | Delete def |
| 6 | dead function | host_health.py:503 `ensure_policy` | none | `git grep -w -n ensure_policy` -> 1 | REMOVE | Delete def |
| 7 | dead function | indicator_audit_compare.py:84 `live_route_check` | none | `git grep -w -n live_route_check` -> 1 | REMOVE | Delete def |
| 8 | dead function | role_line.py:84 `is_role` | none | `git grep -w -n is_role` -> 1 | REMOVE | Delete def |
| 9 | dead function | c_drive_guard.py:217 `sync_script` | none | `git grep -w -n sync_script` -> 1 | REMOVE | Delete def (c_drive_guard is a SessionStart hook: run `test_c_drive_guard.py`) |
| 10 | dead function | make_layers_md.py:46 `family_ids` | none | `git grep -w -n family_ids` -> 1 | REMOVE | Delete def |
| 11 | helper x8 | utc-now: auto_deploy.py:288 `now`, cicd_run.py:91 `utc_now`, codex_run.py:102 `utc`, dsa.py:62 `utc_now`, lane_health.py:53 `utc`, live_owner.py:41 `_now`, mts_run.py:49 `utcnow`, mts_signal.py:160 `now` | identical AST body (`datetime.now(timezone.utc)`) | `git grep -n -E "def (utc\|utc_now\|utcnow\|now\|_now)\(\)" -- 'scripts/dev/*.py' ':!scripts/dev/test_*'` -> 10 (8 identical + desk.py:54, tasks.py:80 which return the ISO string) | KEEP traffic.py (already imported by supervisor; `UTC = timezone.utc` at :28) | Add `traffic.utcnow()`; replace the 8 defs with `from traffic import utcnow`. Tests patch `module.utc`: grep each test first (`git grep -n "\.utc\b\|utc_now" scripts/dev/test_*.py`) |
| 12 | helper x3 | desk.py:54 `now()` | tasks.py:80 `now()`, shot.py:124 `now_iso()` (same `strftime("%Y-%m-%dT%H:%M:%SZ")` body) | `git grep -n 'datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")' -- 'scripts/dev/*.py' ':!scripts/dev/test_*'` -> 9 lines | KEEP tasks.py (largest consumer) | Put `iso_now()` next to row 11's `utcnow()`; desk, shot import it |
| 13 | constant x3 | cicd_run.py:33 `TS_FMT` | testnet_canary.py:36, testnet_status.py:32 (same `"%Y-%m-%dT%H:%M:%SZ"`) | `git grep -n "^TS_FMT *=" scripts/dev` -> 3 | KEEP traffic.py/shared (with row 12) | One `TS_FMT`; three imports |
| 14 | helper x3 | lease.py:69 `_flags` | role_loader.py:119, traffic.py:32 (identical `CREATE_NO_WINDOW` one-liner) | `git grep -n "def _flags(" scripts/dev` -> 3; `git grep -n CREATE_NO_WINDOW -- 'scripts/dev/*.py' ':!scripts/dev/test_*'` -> 20 | KEEP traffic.py:32 | lease.py and role_loader.py `from traffic import _flags`; the other 17 inline uses stay (not a copy of a def) |
| 15 | helper x2 | run_all_tests.py:342 `gate_jobs()` | run_extra_tests.py:46 `jobs()` (identical 6 lines, same env knob) | `git grep -n MTS_GATE_JOBS scripts/dev/run_all_tests.py scripts/dev/run_extra_tests.py` -> 8 | KEEP run_all_tests.py `gate_jobs` | run_extra_tests imports it (or both call one `gate_jobs`); gate-live-path-adjacent: run `--quick` before ship |
| 16 | helper x2 (test + prod) | run_all_tests.py:386 inner `ids()` | test_ci_split.py:68 `ids()` (same recursive suite flatten) | `git grep -n "def ids(t)" scripts/dev` -> 2 | KEEP run_all_tests (production copy) | Lift `ids` to module level in run_all_tests; the test imports it. Keeps the test checking the real function, not a copy |
| 17 | helper x2 | supervisor.py:761 `_utc(s)` | successor_wake.py:107 `_parse(s)` (identical body, ISO -> datetime) | `git grep -n -E "def (_utc\|_parse)\(s" scripts/dev/supervisor.py scripts/dev/successor_wake.py` -> 2 | KEEP supervisor `_utc` (successor_wake is a newer sibling) | successor_wake imports `supervisor._utc`; check no import cycle (successor_wake.py:28 already mirrors `HANDOVER_REL`) |
| 18 | constant x3 | supervisor.py:756 `HANDOVER_REL` | role_loader.py:212, successor_wake.py:28 (same path template) | `git grep -n "^HANDOVER_REL *=" scripts/dev` -> 3 | KEEP supervisor.py | Others import it |
| 19 | constant x2 | role_loader.py:81 `PREFIX` regex | role_hook_launcher.py:28 (same pattern; launcher pre-filters before role_loader) | `git grep -n "^PREFIX *=" scripts/dev/role_loader.py scripts/dev/role_hook_launcher.py` -> 2 | KEEP role_loader.py. Caveat: role_hook_launcher is installed into `~/.claude` and must stay import-light | Do NOT import across: add a test asserting both strings are equal (`assertEqual(role_loader.PREFIX, role_hook_launcher.PREFIX)`) instead of a shared module |
| 20 | constant x12 | `TRUNK = "fast-track"` desk.py:40, dsa.py:32, lease.py:45, sync.py:41; `"origin/fast-track"` make_status.py:20, role_hook_launcher.py:23, role_loader.py:35, supervisor.py:41 (`TRUNK_REF`) and 4 more | 31 literal uses in 26 files | `git grep -n -E "^(TRUNK\|TRUNK_REF) *=" scripts/dev/*.py` -> 12; `git grep -n -E '"fast-track"\|"origin/fast-track"' -- 'scripts/dev/*.py' ':!scripts/dev/test_*'` -> 31 | KEEP sync.py:41 (owner of the branch rule) | Leave the 31 inline uses (rename churn, no drift seen); fold the 12 definitions into `sync.TRUNK` imports only inside a Builder batch that already touches those files |
| 21 | constant x5 | sync.py:42 `LIVE_MARKER = ".mts_live"` | desk.py:41, dsa.py:33, live_mirror.py:39, make_status.py:300; plus `is_live` dsa.py:113 and `is_live_tree` make_status.py:303 (same body) | `git grep -n "^LIVE_MARKER *=" scripts/dev` -> 5; `git grep -n -E "def (is_live\|is_live_tree)\(" scripts/dev` -> 6 (incl. 3 unrelated owners) | KEEP sync.py (also auto_deploy.Ops.is_live is the stated source, make_status.py:300 comment) | Import `LIVE_MARKER`; make_status `is_live_tree` and dsa `is_live` call one function |
| 22 | constant x3 | sync.py:46 `CLAIMS_DIR` | desk.py:230, dsa.py:36 (same string) | `git grep -n "^CLAIMS_DIR *=" scripts/dev` -> 3; literal `MyTradingSys/system/claims` in non-test code -> 7 lines | KEEP sync.py | Import; the other 4 literal lines are in docstrings/tests, leave |
| 23 | constant x2 | sync.py:43 `GATEWAY_MARKER` | dsa.py:35 | `git grep -n "^GATEWAY_MARKER *=" scripts/dev` -> 2 | KEEP sync.py | dsa imports |
| 24 | constant x2 | live_mirror.py:40 `LIVE_HOST_FILE` | supervisor.py:744 | `git grep -n "^LIVE_HOST_FILE *=" scripts/dev` -> 2 | KEEP live_mirror.py | supervisor imports (it already imports live_mirror helpers if any; else add) |
| 25 | constant x2 | cicd_run.py:43 `SUPERVISOR_LOG_REL` | wt_maint.py:35 | `git grep -n "^SUPERVISOR_LOG_REL *=" scripts/dev` -> 2 | KEEP cicd_run.py | wt_maint imports |
| 26 | constant x2 | desk.py:234 `STALE_CLAIM_H = 24` | mts_doctor.py:419 `STALE_CLAIM_H = 24  # same as sync.py STALE_HOURS` (comment admits the copy) | `git grep -n -E "^STALE_CLAIM_H\|^STALE_HOURS" scripts/dev/desk.py scripts/dev/mts_doctor.py scripts/dev/sync.py` -> 3 | KEEP sync.py `STALE_HOURS` (the named source) | desk and mts_doctor use `sync.STALE_HOURS`; delete the comment |
| 27 | constant x2 | codex_run.py:54 `WEEK_S` | mts_run.py:43 `WEEK_S` (`7 * 86400`) | `git grep -n "^WEEK_S *=" scripts/dev` -> 2 | KEEP codex_run | Import or inline `7 * 86400`; low value, batch with row 11 |
| 28 | constant x2 | ask_model.py:32 `AGY` | gemini_queue.py:19 `AGY` (same path) | `git grep -n "^AGY *=" scripts/dev` -> 2 | KEEP gemini_queue.py (the queue is the canonical Gemini entry, memory: all YouTube work via gemini_queue) | ask_model imports |
| 29 | helper x2 | declutter_backups.py:28 `sha256` | deploy_untrack_backup.py:38 `sha256` (same loop, 1 MiB chunks) | `git grep -n "def sha256(" scripts/dev` -> 2 | KEEP declutter_backups.py (has the doc-listed `--apply` command) | deploy_untrack_backup imports; or REMOVE deploy_untrack_backup if one-shot (check `git log -1 --format=%cs -- scripts/dev/deploy_untrack_backup.py` before) |
| 30 | helper x3 (store pattern) | desk.py:66 `save`, :78 `get` | tasks.py:117 `save`, :217 `get`; lane_health.py:134 `save` (0.84-0.91 similar, 4 stmts, one JSON file per record) | `git grep -n -E "def (save\|get)\(repo" scripts/dev/desk.py scripts/dev/tasks.py scripts/dev/lane_health.py` -> 5 | KEEP tasks.py (card store; the other two are small request/lane stores) | Not worth a shared module: leave and record here so nobody re-audits. DECISION (OURS): no edit |
| 31 | test helper x6 | test_lab_query.py:32 `put`, test_research_kit_lint.py:11, test_live_mirror.py:23, test_trace.py:24 (0.87-0.98 similar, write a file under a temp root); `sh(cwd,*args)` test_desk.py:15, test_mts_signal.py:19, test_stop_guard.py:14 (identical git runner) | test_live_owner.py:14 `put` is a different helper (keep) | `git grep -n "^def put(" -- 'scripts/dev/test_*.py'` -> 6; `git grep -n "^def sh(cwd" -- 'scripts/dev/test_*.py'` -> 6 lines (3 files x def+use) | KEEP none yet: new `scripts/dev/testkit.py` with `put`, `sh` | Add testkit, switch 7 files in one batch. Each switched test must still fail on pre-change code (rule: new tests fail once) so change imports only, no assertions |
| 32 | test split | MyTradingSys/tests/test_verdicts.py (128 lines, 7 pytest functions: backfill, check exit codes, csv LF, q72) | scripts/dev/test_verdicts.py (250 lines, 21 unittest cases: overrides, blocked studies, ledger count, power line) | `wc -l` both; `grep -c "def test"` -> 7 and 21; no shared test name (name-overlap scan found 0 file pairs sharing >=3 test names; 0 identical bodies >300 AST chars) | KEEP both: same subject, different cases, not duplicates | Move the 7 into scripts/dev/test_verdicts.py to leave one file per script (docs convention `test_<script>.py`); no assertion change |

## Scripts nothing calls (wiring checked)

None of the 234 scripts is both uncalled by code and undocumented except one. Scripts with no code-file caller (only docs/research name them), `git grep -l -w <name>` excluding self and its test:

| Script | Callers found | Verdict |
|---|---|---|
| run_argon_pipeline.py (293 lines, no test) | 1 line: LAYER_LAB.md:134 (list of helper CLIs) | Row 33 below |
| check_spec_quotes, eagle_gaps, prompt_contract, tom_holdout_split | docs + `research/shipping_speed_2026-10-19/*smoke.txt` timings; each has `test_<name>.py` | KEEP (documented manual tools, tested) |
| funnel_report, interview_feed, research_kit_lint | docs; listed in `research/mts_doctor/simplify_2026-10-24/DELETION_LIST.md:63` but no DECISIONS row approves it (`grep` of DECISIONS.md -> 0) | KEEP until a decision row exists; interview_feed is named in QUICK_ANSWERS.md:52 and RUN_MODEL.md:65 |
| soak_six_slots | DECISIONS.md row 21 (simplify 2026-10-24): "Keep; its test runs in CI only" | KEEP (recorded decision, newer than nothing contradicting) |
| perm_hook, role_hook_launcher | installed in `~/.claude/settings.json` per UNATTENDED_PERMISSIONS.md:16-18, not in repo settings | KEEP |
| reply_shape_check | new this week (staged), LAYER_LAB.md:134; health run `research/health_checks_run_2026-10-28/REPORT.md:56` reports it hangs 120 s | KEEP; fix the hang, do not delete (separate card, not filed here) |

| # | Kind | Side A | Side B | Evidence | Keep / remove | Proposed edit |
|---|---|---|---|---|---|---|
| 33 | uncalled script | run_argon_pipeline.py:1 (docstring: "End-to-end pipeline for card argon-blind-read-7-frames") | argon_blind_read.py:54 (the library it wraps; card JSON `MyTradingSys/system/tasks/argon-blind-read-7-frames.json:82` names results, not this script) | `git grep -l -w run_argon_pipeline` -> 1 file (LAYER_LAB.md, one list line); `ls scripts/dev/test_run_argon_pipeline.py` -> absent; `git log -1 --format=%cs -- scripts/dev/run_argon_pipeline.py` -> 2026-10-25 | REMOVE only after the card `argon-blind-read-7-frames` is done; today a card references the same flow, so KEEP until it closes | After the card state is `done`: delete the file and the LAYER_LAB.md:134 mention; `run_all_tests.py --quick` |

## Test registration and overlap (checked, no action)

| Check | Command | Result |
|---|---|---|
| Same test registered twice (extra_tests.tsv and run_all_tests.py PYTEST_LAYER_PATHS) | Python scan of both lists | 0 overlaps. Eight tsv paths also appear in `run_all_tests.py:899-906` only as `CI_FILE_S` timing keys, which is intended |
| Duplicate lines in `extra_tests.tsv` | `sort | uniq -d` equivalent | 0; every listed path exists |
| Identical test bodies across files (AST, >300 chars) | AST hash over 282 test files | 0 |
| Test files sharing >= 3 test names | name-set intersection | 0 pairs |
| Same file name in two dirs | basename scan | 1: `test_verdicts.py` (row 32) |
| Test with no same-name script (`test_X.py` without `X.py`) | `ls` | 19, all cover a group or a non-script subject (gate, registry, tf map); not duplicates |

Row count: 33 rows (32 in the main table, 1 in the uncalled-scripts table).

## Rule for the Builder batches (`apply-dedupe-audit-findings`, 10 rows each)

1. Batch A (dead functions, rows 3-10): independent, one commit, run `run_all_tests.py --quick`.
2. Batch B (time and subprocess helpers, rows 11-17): one commit; grep each test for the patched name first.
3. Batch C (constants, rows 1, 18-28): row 1 first (a user-visible string).
4. Batch D (rows 2, 29, 31, 32): needs a new module or file moves; row 2 touches redaction code, so keep a test that feeds a fake `api_key=...` through both scripts' `scrub` and asserts `[redacted]`.
5. Rows 19, 30 and 33 are record-only or deferred.
