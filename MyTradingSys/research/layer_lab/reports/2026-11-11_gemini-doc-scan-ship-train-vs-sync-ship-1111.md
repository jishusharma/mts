COUNTS: MATCH=5 DIFF=2 NOT_IN_DATA=3

# Audit Report: `SHIP_TRAIN.md` vs `sync.py ship` & Tests

- **Card**: `gemini-doc-scan-ship-train-vs-sync-ship-1111`
- **Auditor**: Gemini 3.8 Flash (Low)
- **Date**: 2026-11-11
- **Scope In**:
  - `MyTradingSys/system/SHIP_TRAIN.md` (read)
  - `scripts/dev/sync.py` (ship path; read)
  - `scripts/dev/test_sync.py` and `scripts/dev/test_ship_train.py` (read)
  - `MyTradingSys/research/layer_lab/reports/2026-11-11_gemini-doc-scan-ship-train-vs-sync-ship-1111.md` (new)
- **Scope Out**: Read-only audit; no source edits, no live tree edits, no deploy, no `.secrets` or `.env` read.

---

## 1. Summary of Scan

Ten testable claims from `SHIP_TRAIN.md` covering queued ships, batching, push rules, gating, CI-wait, signals, and cutover flags were evaluated against `scripts/dev/sync.py`, `scripts/dev/ship_train.py`, and test suites `scripts/dev/test_sync.py` and `scripts/dev/test_ship_train.py`.

- **MATCH (5)**:
  1. Queued ref push format (`queue/<host>/<slug>`) implemented in `sync.py` and `ship_train.py`.
  2. `--train` flag status polling replacing CI wait on the ship client.
  3. Exit code 4 upon train ejection (`TRAIN_EJECT_EXIT = 4`).
  4. Red batch bisect and ejection logic without auto-revert (`ship_train.py`).
  5. Local smoke gate maintained prior to push.
- **DIFF (2)**:
  1. Default push target: `SHIP_TRAIN.md:94` cutover specifies flipping `--train` to default and adding break-glass `--direct`; in `sync.py:2388` the `--train` flag remains off by default, and `--direct` is not implemented.
  2. CI-wait mechanism: `SHIP_TRAIN.md:77,108` specifies status file replaces X7 wait; in `sync.py:2386,2457-2461` the `--wait-ci` / `wait_own_ci` direct trunk CI wait mechanism remains active for default ships.
- **NOT_IN_DATA (3)**:
  1. Train workflow batch runner `train.yml` (`SHIP_TRAIN.md:74,91`): does not exist in the repository (`.github/workflows/train.yml` is absent).
  2. One-shot failed shard retry in CI workflow (`SHIP_TRAIN.md:76,85,90`): not implemented in `sync.py` or `.github/workflows/ci.yml`.
  3. Ordered batch composition prioritizing docs/data before code (`SHIP_TRAIN.md:75,84`): no batch queue sorter exists in client or workflow code.

---

## 2. Detailed Clause Comparison Table

| # | Topic | `SHIP_TRAIN.md` Claim & Citation | Code Implementation & Citation | Status | Audit Findings & Verification |
|---|---|---|---|---|---|
| 1 | Push Ref Format | `SHIP_TRAIN.md:73`: `"sync.py ship keeps the local smoke gate, then pushes queue/<host>/<slug> (not fast-track). The ref name is the blame record (author is useless)."` | `scripts/dev/sync.py:2437`: `train_ref = ship_train.queue_ref(git(repo, "rev-parse", "--abbrev-ref", "HEAD").stdout.strip())`; `scripts/dev/ship_train.py:30-37`: `queue_ref(branch, host)` returns `queue/<host>/<slug>` | MATCH | SOURCED (`SHIP_TRAIN.md:73`, `scripts/dev/sync.py:2437`, `scripts/dev/ship_train.py:30-37`, `scripts/dev/test_ship_train.py:16-20`). Code formats the ref exactly as `queue/<host>/<slug>` and pushes to `extra_kw={"push_ref": train_ref}`. |
| 2 | Status Wait & Polling | `SHIP_TRAIN.md:77`: `"Status in a small file on the mts-signals branch so ship --wait replaces X7."` and `SHIP_TRAIN.md:92`: `"sync.py ship --train pushes the queue ref and waits on the status file (replaces X7 for it)"` | `scripts/dev/sync.py:2445`: `verdict = ship_train.wait_status(train_ref, since=train_since)`; `scripts/dev/ship_train.py:122-138`: `wait_status` polls `train/<host>__<slug>.json` on `mts-signals` | MATCH | SOURCED (`SHIP_TRAIN.md:77,92`, `scripts/dev/sync.py:2445`, `scripts/dev/ship_train.py:122-138`, `scripts/dev/test_ship_train.py:86-96`). `sync.py ship --train` polls `mts-signals` branch for verdict (`landed` or `ejected`). |
| 3 | Ejection Exit Code | `SHIP_TRAIN.md:85`: `"batch cap 4, one shard retry before ejecting, ejected ship is signalled, never auto-reverted."` | `scripts/dev/sync.py:1003`: `TRAIN_EJECT_EXIT = 4`; `scripts/dev/sync.py:2451`: `return TRAIN_EJECT_EXIT if verdict == "ejected" else 0` | MATCH | SOURCED (`SHIP_TRAIN.md:85`, `scripts/dev/sync.py:1003,2451`, `scripts/dev/test_ship_train.py:144-147`). Ejection from train yields explicit exit code 4 without automated revert on git trunk. |
| 4 | Red Batch Bisect & Eject | `SHIP_TRAIN.md:76`: `"Red: run each ref alone on the tip in parallel, eject the failing ones, re-run the rest; each ejected ref gets an mts_signal to its host/slug with the failing test id and a link."` | `scripts/dev/ship_train.py:55-68`: `bisect_batch(refs, run_ref, run_batch)` maps `run_ref` across pool (cap 4) and isolates failing refs; `scripts/dev/ship_train.py:76-81`: `signal_eject` sends note to target host | MATCH | SOURCED (`SHIP_TRAIN.md:76`, `scripts/dev/ship_train.py:55-68,76-81`, `scripts/dev/test_ship_train.py:33-75`). Logic isolates failing refs in parallel, signals host with test ID and link, and reruns green subset together. |
| 5 | Smoke Gate Retention | `SHIP_TRAIN.md:73`: `"sync.py ship keeps the local smoke gate, then pushes queue/<host>/<slug>"` and `SHIP_TRAIN.md:114`: `"Not removed: the local smoke gate (keeps most bad ships off the queue)"` | `scripts/dev/sync.py:1441`: `call_gate(gate, repo, files)`; `scripts/dev/sync.py:440-446`: `run_gate(repo, files)` runs smoke gate `--quick --precheck --fail-fast --slot --record --smoke --fast` | MATCH | SOURCED (`SHIP_TRAIN.md:73,114`, `scripts/dev/sync.py:440-446,1441`, `scripts/dev/test_sync.py:270-272`). Local smoke gate is invoked during `sync.py ship` before pushing to `push_ref`. |
| 6 | Default Push Target & Cutover Flag | `SHIP_TRAIN.md:94`: `"Card 5 ship-train-cutover: flip default, add --direct, remove the redundant checks ... live-tree deploy still manual"` | `scripts/dev/sync.py:2388`: `train = "--train" in argv # flag off by default: the push goes to the trunk exactly as before`; `scripts/dev/sync.py:1464`: `dest = push_ref or TRUNK` | DIFF | SOURCED (`SHIP_TRAIN.md:94`, `scripts/dev/sync.py:1464,2388`). `SHIP_TRAIN.md` specifies train as default with `--direct` break-glass. The live codebase has `--train` off by default, pushes to trunk (`fast-track`), and has no `--direct` flag. |
| 7 | Direct CI Wait vs Status File | `SHIP_TRAIN.md:108`: `"X7 wait_own_ci / ci_watch polling | replaced by the status file | card 3/5"` | `scripts/dev/sync.py:2386`: `wait_ci = ("--wait-ci" in argv or bool(os.environ.get("SYNC_WAIT_CI"))) ...`; `scripts/dev/sync.py:2461`: `return CI_RED_EXIT if wait_own_ci(pushed...) == "red" else 0` | DIFF | SOURCED (`SHIP_TRAIN.md:108`, `scripts/dev/sync.py:2386,2461`, `scripts/dev/test_sync.py:2077-2083`). `wait_own_ci` (polling GitHub Actions runs directly) remains active for trunk ships and is not deprecated or replaced on the primary ship path. |
| 8 | Workflow Train Runner | `SHIP_TRAIN.md:74`: `"2. Workflow train.yml on push to queue/**, one run at a time. It lists ALL queue refs, orders them, builds candidate = fast-track tip + each ref merged"` | Missing: `.github/workflows/train.yml` does not exist in repository | NOT_IN_DATA | SOURCED (`SHIP_TRAIN.md:74,126`). File search for `.github/workflows/*train*` returned 0 results. Card 2 (`ship-train-runner`) is not yet landed. |
| 9 | One-Shot Failed Shard Retry | `SHIP_TRAIN.md:76`: `"(reused via workflow_call; a failed shard reruns once before it counts)"` and `SHIP_TRAIN.md:90`: `"one-shot rerun of failed shards in ci.yml"` | Missing in `.github/workflows/ci.yml` and `scripts/dev/sync.py` | NOT_IN_DATA | SOURCED (`SHIP_TRAIN.md:76,90`). Card 1 (`ship-train-flake-floor`) shard rerun mechanism does not exist in CI or sync execution scripts. |
| 10 | Ordered Batch Composition (Docs First) | `SHIP_TRAIN.md:75`: `"3. Order (optimal = cheapest to verify first, riskiest last): docs/data-only refs first on a 1-2 min lane ... code refs next, oldest first; refs touching live-path or .github/ alone, last. Batch cap 4."` | Missing: No queue ref sorting/ordering scheduler exists in `scripts/dev/ship_train.py` or `scripts/dev/sync.py` | NOT_IN_DATA | SOURCED (`SHIP_TRAIN.md:75`). `ship_train.py` executes batches passed to it, but lacks logic to list and order `queue/**` remote refs into lanes. |
