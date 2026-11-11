COUNTS: MATCH=7 DIFF=1 NOT_IN_DATA=2

# Audit Report: `scripts/dev/sync.py` Module Docstring vs Code (ship, ci, flags)

- **Card**: `gemini-doc-scan-sync-docstring-vs-code-1111`
- **Auditor**: Gemini 3.8 Flash (Low)
- **Date**: 2026-11-11
- **Scope In**:
  - `scripts/dev/sync.py` (read)
  - `scripts/dev/test_sync.py` (read)
  - `MyTradingSys/research/layer_lab/reports/2026-11-11_gemini-doc-scan-sync-docstring-vs-code-1111.md` (new)
- **Scope Out**: Read-only audit; no edits to source files, no live-tree edit, no deploy, no `.secrets` or `.env` read.

---

## 1. Summary of Scan

Ten testable claims from the `scripts/dev/sync.py` module docstring (lines 1-22), focusing on `ship`, CI flags, exit codes, gating tiers, second-ship note behavior, and commit trailers, were evaluated against implementation code in `scripts/dev/sync.py` and test cases in `scripts/dev/test_sync.py`.

- **MATCH (7)**:
  1. `--train` flag (off by default): pushes `queue/<host>/<slug>`, waits on train status file; exit 4 = ejected (`sync.py:1003,2388,2437-2451`).
  2. Second ship within 10 minutes prints a note only; `--again` still accepted (`sync.py:58,820-831,2379-2381`).
  3. Predecessor ticket wait with `--after <slug>` (`sync.py:1241-1273,2398-2403`).
  4. Non-blocking push return and `sync.py ci [sha]` (or `ship --wait-ci` / `SYNC_WAIT_CI=1`) up to 10 min wait (`sync.py:924-931,1102-1160,2385-2387,2457-2461`).
  5. CI verdict exit 3 on CI RED (`sync.py:931,1004,2461`).
  6. Commit trailer and body line `Result: <text>` commit mechanism (`sync.py:860-896,2404-2428`).
  7. Live-tree safeguard (`.mts_live` checkout never synced or shipped) (`sync.py:20,51,158-164,2422`).
- **DIFF (1)**:
  1. `--fix-ci` gate tier: docstring line 8 states `--fix-ci ships the fix through it with the full gate`, whereas code line 2375-2378 explicitly keeps the fast gate without setting `SYNC_FULL_GATE` ("Operator 2026-10-25: a fix must be the fastest ship, not the slowest. --fix-ci passes the red-CI block on the normal 2-minute fast gate...").
- **NOT_IN_DATA (2)**:
  1. `--no-ci-wait` flag in docstring: while implemented in CLI parsing (`sync.py:2386-2387,2394,2401`) and tested in `test_sync.py:2099-2107,2155`, `--no-ci-wait` is absent from the module docstring CLI usage specification on lines 6-9.
  2. `MTS-Session:` commit trailer handling: required by repo policy and mentioned in prompt context, but not parsed, generated, or enforced by `sync.py` (only `Result:` and `Next:` are handled by `sync.py:860-896`).

---

## 2. Detailed Clause Comparison Table

| # | Topic | `scripts/dev/sync.py` Docstring Claim & Citation | Code Implementation & Citation | Status | Audit Findings & Verification |
|---|---|---|---|---|---|
| 1 | `--train` Flag & Exit 4 | `scripts/dev/sync.py:6`: `"--train (off by default): push queue/<host>/<slug>, wait on the train status file (ship_train.py; exit 4 = ejected)"` | `scripts/dev/sync.py:1003`: `TRAIN_EJECT_EXIT = 4`; `scripts/dev/sync.py:2388`: `train = "--train" in argv # flag off by default`; `scripts/dev/sync.py:2437`: `train_ref = ship_train.queue_ref(...)`; `scripts/dev/sync.py:2451`: `return TRAIN_EJECT_EXIT if verdict == "ejected" else 0` | MATCH | SOURCED (`scripts/dev/sync.py:6`, `scripts/dev/sync.py:1003,2388,2437,2451`). Matches code implementation. |
| 2 | Second Ship Note & `--again` | `scripts/dev/sync.py:6`: `"a second ship within 10 min only prints a note (--again still accepted)"` | `scripts/dev/sync.py:58`: `SHIP_GAP_S = 600`; `scripts/dev/sync.py:829-830`: `if 0 <= age < SHIP_GAP_S: print(f"note: second ship from this tree {age:.0f} s after the last one; shipping anyway...")`; `scripts/dev/sync.py:2379-2381`: `if "--again" in argv: os.environ["SYNC_ALLOW_SECOND_SHIP"] = "1"` | MATCH | SOURCED (`scripts/dev/sync.py:6`, `scripts/dev/sync.py:58,820-831,2379-2381`, `scripts/dev/test_sync.py:323-345`). Code checks timestamp against 600 s (10 min), emits note, and silences via `--again`. |
| 3 | Docs-Only & Smoke Gate | `scripts/dev/sync.py:6`: `"docs-only ships run no gate; merge origin/fast-track, SMOKE gate (steps for the changed paths; live path = all; --full = all), push; CI runs the full suite behind"` | `scripts/dev/sync.py:440-445`: `run_gate(repo, files)` runs smoke gate (`--smoke`) and selects changed files; `scripts/dev/sync.py:805-813`: `run_docs_gate(repo, files)` runs docs checks only (no full local gate); `scripts/dev/sync.py:1439-1446`: dispatches to `call_gate(gate...)` or `docs_gate(...)` | MATCH | SOURCED (`scripts/dev/sync.py:6`, `scripts/dev/sync.py:440-445,805-813,1439-1446`, `scripts/dev/test_sync.py:1812-1816`). Docs ships bypass full offline gate; code ships run smoke gate with test selection. |
| 4 | Ordinary Code FAST Gate | `scripts/dev/sync.py:7`: `"ordinary code ships run the FAST gate (GATE_SPEED.md: ~60 s, tests chosen by import graph); a red CI blocks code ships until fixed"` | `scripts/dev/sync.py:455-456`: `if not os.environ.get("SYNC_NO_FAST"): cmd += ["--fast"]`; `scripts/dev/sync.py:983-992`: `enforce_ci(check)` raises `SyncError` when CI is red on code ships | MATCH | SOURCED (`scripts/dev/sync.py:7`, `scripts/dev/sync.py:455-456,983-992`, `scripts/dev/test_sync.py:1795-1806,1827-1831`). Code ships add `--fast` flag unless disabled, and red CI blocks code ships. |
| 5 | `--fix-ci` Gate Tier | `scripts/dev/sync.py:8`: `"--fix-ci ships the fix through it with the full gate"` | `scripts/dev/sync.py:2374-2378`: `if "--fix-ci" in argv: os.environ["SYNC_FIX_CI"] = "1"`; comment notes: `"Operator 2026-10-25: a fix must be the fastest ship, not the slowest. --fix-ci passes the red-CI block on the normal 2-minute fast gate (the X6 full gate made a one-commit revert wait 40+ min)"` | DIFF | SOURCED (`scripts/dev/sync.py:8`, `scripts/dev/sync.py:2374-2378`, `scripts/dev/test_sync.py:1832-1841`). Docstring claims `--fix-ci` runs the "full gate", but code explicitly runs the fast gate without setting `SYNC_FULL_GATE`. Test `test_fix_ci_flag_keeps_the_fast_gate` verifies `SYNC_FULL_GATE` is None. |
| 6 | `--after` Predecessor Wait | `scripts/dev/sync.py:8`: `"--after waits for predecessor order ticket"` | `scripts/dev/sync.py:1241-1273`: `wait_after(repo, slug, timeout=3600, poll=10.0)` waits for predecessor card/claim to ship or fail; `scripts/dev/sync.py:1411-1415`: `wait_after(repo, after_slug)`; `scripts/dev/sync.py:2398-2403`: parses `--after <slug>` | MATCH | SOURCED (`scripts/dev/sync.py:8`, `scripts/dev/sync.py:1241-1273,1411-1415,2398-2403`, `scripts/dev/test_sync.py:1470-1491`). Code waits up to 60 minutes for predecessor ticket before gating. |
| 7 | Non-Blocking Push & CI Wait (`--wait-ci` / `SYNC_WAIT_CI=1`) | `scripts/dev/sync.py:9`: `"after the push it returns at once; sync.py ci [sha] (or ship --wait-ci / SYNC_WAIT_CI=1) waits up to 10 min for the CI run of the sha"` | `scripts/dev/sync.py:924-931`: `ci_verb(repo, argv)`; `scripts/dev/sync.py:1102-1106`: `wait_own_ci(...) wait_s=CI_WAIT_S (600s)`; `scripts/dev/sync.py:2386`: `wait_ci = ("--wait-ci" in argv or bool(os.environ.get("SYNC_WAIT_CI"))) ...`; `scripts/dev/sync.py:2457-2461`: prints CI not awaited by default, waits when `wait_ci` is True | MATCH | SOURCED (`scripts/dev/sync.py:9`, `scripts/dev/sync.py:924-931,1102-1106,2386,2457-2461`, `scripts/dev/test_sync.py:2075-2091`). Ship returns immediately by default; `--wait-ci` or `SYNC_WAIT_CI=1` waits up to 600 s (10 min). |
| 8 | CI Verdict Exit 3 on Red | `scripts/dev/sync.py:9`: `"and prints CI RED at once (exit 3)"` | `scripts/dev/sync.py:1004`: `CI_RED_EXIT = 3`; `scripts/dev/sync.py:1150`: `print(f"CI RED {short}: {c}...")`; `scripts/dev/sync.py:2461`: `return CI_RED_EXIT if wait_own_ci(pushed...) == "red" else 0` | MATCH | SOURCED (`scripts/dev/sync.py:9`, `scripts/dev/sync.py:1004,1150,2461`, `scripts/dev/test_sync.py:2018,2063-2073`). Red CI verdict prints `CI RED` and exits with return code 3. |
| 9 | Commit Trailers & Result Line | `scripts/dev/sync.py:6,10`: `"[--result <text> [-m <subject>]] [--next <card-id | stage | END: reason>]"` and `"news [hours=24] # what shipped: feature + Result line per commit, no code"` | `scripts/dev/sync.py:860-896`: `commit_pending` formats body with `Result: <text>` and optional `Next: <tag>`; `scripts/dev/sync.py:902-921`: `check_route_tags` validates `Next:` trailer lines; `scripts/dev/sync.py:1491-1506`: `news` extracts `Result:` line | MATCH | SOURCED (`scripts/dev/sync.py:6,10`, `scripts/dev/sync.py:860-896,902-921,1491-1506,2404-2428`, `scripts/dev/test_sync.py:2160-2187,2366-2373`). Commit pending and ship CLI parse `--result` and `--next` trailers. |
| 10 | Live-Tree Protection Safeguard | `scripts/dev/sync.py:19-21`: `"The live tree (a checkout holding the gitignored marker file .mts_live) is never synced or shipped from: the running system imports it, so it changes only by the supervisor deploy"` | `scripts/dev/sync.py:51`: `LIVE_MARKER = ".mts_live"`; `scripts/dev/sync.py:158-164`: `refuse_live(repo)` raises `SyncError` if `LIVE_MARKER` is present; `scripts/dev/sync.py:1402,2422`: calls `refuse_live(repo)` | MATCH | SOURCED (`scripts/dev/sync.py:19-21`, `scripts/dev/sync.py:51,158-164,1402,2422`, `scripts/dev/test_sync.py:575-581`). Active refusal prevents syncing or shipping from a live checkout holding `.mts_live`. |
