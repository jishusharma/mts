COUNTS: MATCH=5 DIFF=0 NOT_IN_DATA=0

# Independent Gemini Blind Read: `scripts/dev/run_all_tests.py` vs 5b Balancing Claims

- **Card**: `gemini-blind-read-balance-modules-1111`
- **Date**: 2026-11-11 UTC
- **Reader**: Gemini (`gemini-3.8-flash-low`, JIS-NUC throwaway worktree `gemini-q/gemini-blind-read-balance-modules-1111`)
- **Scope In (read-only)**:
  - `scripts/dev/run_all_tests.py` (`balance_modules`, `split_modules`, `exec_layer_chunks`)
  - `scripts/dev/test_run_all_tests.py`
  - `MyTradingSys/research/layer_lab/reports/2026-11-11_gemini-blind-read-balance-modules-1111.md` (this report)
- **Scope Out Respected**:
  - No edits to source files; no live-tree edit; no deploy; no `.secrets` or `.env` read; read-only audit.
  - Zero push; no `sync.py ship`.
- **Target Clauses**:
  1. Chunks are filled longest-cost-first into the least-loaded job
  2. `balance_modules([])` returns no chunks
  3. A module missing from the cost table gets a defined default cost
  4. No two chunks share a module
  5. A failing chunk fails the step

---

## 1. Clause Audit Table

| # | Clause / Claim Description | Status | Target Code & Test References (`file:line` & Quote) | Audit Analysis & Verification Notes (SOURCED / OURS) |
|---|---|---|---|---|
| 1 | Chunks are filled longest-cost-first into the least-loaded job | `MATCH` | `scripts/dev/run_all_tests.py:421-425` (`bins = [[0.0, i, []] for i in range(n)]`; `for m in sorted(modules, key=lambda m: (-costs.get(m, LAYER_DEFAULT_S), m)):`; `b = min(bins, key=lambda b: (b[0], b[1]))`; `b[0] += costs.get(m, LAYER_DEFAULT_S)`; `b[2].append(m)`); `scripts/dev/test_run_all_tests.py:108-117` (`test_balanced_chunks_beat_round_robin_on_synthetic_costs`) | SOURCED (`scripts/dev/run_all_tests.py:421-425`): Implements deterministic Longest Processing Time (LPT) greedy multi-processor scheduling. Modules are sorted descending by cost (`-costs.get(m, LAYER_DEFAULT_S)`), breaking ties deterministically by module name `m`. Each module is appended to the bin with minimal accumulated cost `b[0]` (ties broken by bin index `b[1]`), and `b[0]` is incremented by the module cost. Tested and verified in `scripts/dev/test_run_all_tests.py:108-117` where synthetic costs produce span `<= 120.0` beating round-robin. |
| 2 | `balance_modules([])` returns no chunks | `MATCH` | `scripts/dev/run_all_tests.py:418-419` (`modules = list(modules)`; `if not modules: return [] # nothing to run: no process (a bare unittest would discover the whole repo)`); `scripts/dev/test_run_all_tests.py:134-140` (`def test_empty_module_list_spawns_nothing_and_passes(self): ... self.assertEqual(rat.balance_modules([], 4), []) ... ok, _ = rat.exec_layer_chunks([], 4); self.assertTrue(ok)`) | SOURCED (`scripts/dev/run_all_tests.py:418-419`, `scripts/dev/test_run_all_tests.py:134-140`): `balance_modules` checks `if not modules:` and explicitly returns empty list `[]`. In `exec_layer_chunks`, `chunks = balance_modules([], jobs)` produces `chunks = []`, so `procs = []`, `outs = []`, and `ok = all(...)` evaluates to `True` without spawning any subprocess. Mocked and verified in `test_run_all_tests.py:134-140` with `Popen` patched to assert if called. |
| 3 | A module missing from the cost table gets a defined default cost | `MATCH` | `scripts/dev/run_all_tests.py:410` (`LAYER_DEFAULT_S = 1.5 # OURS`); `scripts/dev/run_all_tests.py:422,424` (`costs.get(m, LAYER_DEFAULT_S)`); `scripts/dev/run_all_tests.py:396-397` (`# modules not listed cost LAYER_DEFAULT_S. Only used to balance chunks...`) | SOURCED (`scripts/dev/run_all_tests.py:410,422,424`): Constant `LAYER_DEFAULT_S = 1.5` is explicitly defined and passed as default to `costs.get(m, LAYER_DEFAULT_S)` both when sorting modules and when accumulating bin weights. Unlisted modules reliably receive cost `1.5` seconds. |
| 4 | No two chunks share a module | `MATCH` | `scripts/dev/run_all_tests.py:426-430` (`pos = {m: i for i, m in enumerate(modules)}`; `chunks = [sorted(b[2], key=lambda m: pos[m]) for b in bins if b[2]]`; `if sorted(m for c in chunks for m in c) != sorted(modules): raise RuntimeError("balance_modules lost or duplicated a module")`; `return chunks`); `scripts/dev/test_run_all_tests.py:118-126` (`self.assertEqual(len(flat), len(set(flat)), jobs)`) | SOURCED (`scripts/dev/run_all_tests.py:426-430`, `scripts/dev/test_run_all_tests.py:118-126`): Each module `m` from `modules` is appended to exactly one bin `b[2]`. The function explicitly asserts `sorted(m for c in chunks for m in c) != sorted(modules)` and raises `RuntimeError("balance_modules lost or duplicated a module")` if any module is duplicated across chunks or lost. `test_run_all_tests.py:124` confirms `len(flat) == len(set(flat))` for all job counts `(1, 2, 4, 7, 10000)`. |
| 5 | A failing chunk fails the step | `MATCH` | `scripts/dev/run_all_tests.py:441-447` (`def passed(p, o): return p.returncode == 0 or (p.returncode == 5 and "NO TESTS RAN" in o)`; `ok = all(passed(p, o) for p, o in zip(procs, outs))`; `if ok: return True, "\n".join(outs)`; `keep = [o if os.environ.get("CI") else "\n".join(o.splitlines()[-15:]) for p, o in zip(procs, outs) if not passed(p, o)]`; `return False, "\n".join(keep)`); `scripts/dev/test_run_all_tests.py:128-132` (`test_failing_module_in_balanced_chunk_fails_step`), `145-148` (`test_chunk_with_missing_module_still_fails`) | SOURCED (`scripts/dev/run_all_tests.py:441-447`, `scripts/dev/test_run_all_tests.py:128-132,145-148`): `ok = all(passed(p, o) for p, o in zip(procs, outs))` requires every concurrent chunk process to pass. If any chunk process fails (`returncode != 0` and not code 5 with `"NO TESTS RAN"`), `ok` evaluates to `False`, and `exec_layer_chunks` returns `False, "\n".join(keep)`. Verified by unit tests in `scripts/dev/test_run_all_tests.py:128-132` and `145-148`. |

---

## 2. Synthesis and Cross-Module Collisions Note

- **Sibling-module collisions check**: As claimed in ship commit `5b609656cf16` (`"no sibling-module name collisions across layer dirs"`), layer test discovery passes full dotted module names (`MyTradingSys.backtest.layers.<dir>.<mod>`) into `unittest` arguments. Chunks partitioned by `balance_modules` maintain unique full dotted module paths, preventing module-name collisions across layer subdirectories.
- **Verification Result**: All 5 clauses confirmed `MATCH` against committed implementation in `scripts/dev/run_all_tests.py` and unit tests in `scripts/dev/test_run_all_tests.py`.
