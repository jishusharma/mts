# GPT audit: tests that can stay green under relevant defects

Task: `gx-test-tautology`  
Date: 2026-10-24  
Scope: `MyTradingSys/backtest/layers/` tests only. Ranked by closeness to producing or authorizing a trade.  
Method: source inspection of test setup, assertions, and the called implementation seams. Mutations below are counterfactual descriptions, not applied. I did not edit existing files or run the tests with mutations. Each command reproduces the cited test when the described mutation is present. Commands are read-only apart from the test's own temporary fixtures.

## Findings

1. **Fabio source route test bypasses Fabio's signal engine** — **HIGH**

   **File:line:** `MyTradingSys/backtest/layers/alerts/test_live_runner_v3_shadow.py:56-60,114-129`.
   `make_registry` injects `run_fn=lambda win, cfg: dict(STUB_SIGNAL)` into the layer. The source test then proves that this canned signal reaches `auto_trader.layer_signal` and becomes `plan_args`; it does not prove that the actual Fabio engine emits a valid signal, side, entry, stop, or target. A regression in `engine.run` can therefore leave this test green while routing a fabricated signal toward the testnet planning path.
   **Planted mutation:** make `engine.run` return `{"verdict": "IDLE"}` for every input. The injected `run_fn` bypasses it, so the assertion on the fake signal's plan args remains unchanged.
   **Reproduce:** `python -m pytest -q MyTradingSys/backtest/layers/alerts/test_live_runner_v3_shadow.py::TestSourceSignal::test_c_source_signal_flows_as_ordinary_layer`

2. **Shadow zero-order test also bypasses Fabio's signal engine** — **HIGH**

   **File:line:** `MyTradingSys/backtest/layers/alerts/test_live_runner_v3_shadow.py:56-60,96-103`.
   This is a useful check of the collection-only guard in the runner/auto-trader seam, but the event originates from the same canned `STUB_SIGNAL`, not `engine.run`. It cannot detect a broken Fabio signal calculation that emits a wrong signal or no signal.
   **Planted mutation:** make `engine.run` return a malformed result or always return `IDLE`. The stub still feeds the shadow guard, which still strips `side` and prevents `plan_args`; this test passes.
   **Reproduce:** `python -m pytest -q MyTradingSys/backtest/layers/alerts/test_live_runner_v3_shadow.py::TestShadowSignal::test_b_shadow_signal_produces_zero_orders`

3. **G19 known-gap assertion failures become skips by default** — **HIGH**

   **File:line:** `MyTradingSys/backtest/layers/fabio/v3/tests/test_fabio_golden.py:55-66,362-363`.
   `known_gap` catches `AssertionError` and calls `SkipTest` whenever `MTS_FABIO_GOLDEN_STRICT` is not `1`. G19 asserts that heavy seller absorption is held; an implementation that exits instead fails the assertion but reports the test as skipped, not failed, under the ordinary environment.
   **Planted mutation:** change the absorption management branch so G19 exits immediately. The assertion fails, the decorator converts it to a skip, and the default test run stays green.
   **Reproduce:** `python -m pytest -q MyTradingSys/backtest/layers/fabio/v3/tests/test_fabio_golden.py::GoldenScenarios::test_g19_in_trade_consolidation_with_heavy_seller_absorption_is_still_held`

4. **G10 reload/trade-record known-gap assertion failures become skips by default** — **HIGH**

   **File:line:** `MyTradingSys/backtest/layers/fabio/v3/tests/test_fabio_golden.py:55-66,247-248`.
   The same decorator means this test does not fail by default when the engine violates the expected single trade record across a first load and two reloads. This is a state and duplicate-entry control scenario.
   **Planted mutation:** on each reload, append a second trade record for the same position. The G10 assertion fails but becomes a skip unless strict mode is enabled.
   **Reproduce:** `python -m pytest -q MyTradingSys/backtest/layers/fabio/v3/tests/test_fabio_golden.py::GoldenScenarios::test_g10_first_load_plus_two_reloads_are_one_trade_record`

5. **Promotion CI test does not check the recomputed confidence interval** — **HIGH**

   **File:line:** `MyTradingSys/backtest/layers/promotion/test_promote.py:108-114`; gate consumer: `MyTradingSys/backtest/layers/promotion/promote.py:69-78,242-250`.
   The test independently checks the row count and mean, but only checks that the returned lower bound is below the mean and the upper bound above it. Repeating `recompute_oos` and asserting determinism compares the function to itself. A wrong-but-ordered interval can pass even though the promotion gate consumes the lower bound.
   **Planted mutation:** return the correct `n` and mean but use a confidence interval much narrower than the specified bootstrap interval, while keeping `lo < mean < hi`. All assertions at this test pass; the wrong interval is not compared to an independently derived expected value here.
   **Reproduce:** `python -m pytest -q MyTradingSys/backtest/layers/promotion/test_promote.py::Gates::test_recompute_matches_manifest_numbers`

6. **File-to-layer test injects an always-signaling engine stub** — **LOW**

   **File:line:** `MyTradingSys/backtest/layers/alerts/test_live_runner_of_feed.py:102-120`.
   The test covers order-flow file reading and registry wiring, but passes a `run_fn` that always returns a canned signal. A defect in Fabio's decision logic will not affect its collection-only assertions. The file itself documents this test's feed focus; this is a coverage boundary to keep explicit.
   **Planted mutation:** change the production Fabio decision engine to always return `IDLE`. The injected lambda still returns `SIGNAL`, so the file-feed test remains green.
   **Reproduce:** `python -m pytest -q MyTradingSys/backtest/layers/alerts/test_live_runner_of_feed.py::TestLiveFlow::test_layer_emits_from_files_through_registry`

7. **Backtest PBO/verdict assertion recomputes verdict with the same gate** — **LOW**

   **File:line:** `MyTradingSys/backtest/layers/test_run_bracket_grid.py:210-215`; implementation uses the same `decide` at `MyTradingSys/backtest/layers/run_bracket_grid.py:99,109-156`.
   The test checks only that PBO is in its legal numeric range, then calls `G.decide` again on the reported values and compares that result with `run_layer`'s verdict. If PBO is wrong but in range, and `run_layer` uses that same wrong PBO with `decide`, this consistency assertion passes. Other tests exercise `decide` thresholds, but this case is not an independent PBO or end-to-end verdict oracle.
   **Planted mutation:** make `compute_pbo` return `0.0` for every sufficiently long grid. The result remains in range; both the stored verdict and the test's recomputed verdict use that value and agree.
   **Reproduce:** `python -m pytest -q MyTradingSys/backtest/layers/test_run_bracket_grid.py::TestRunLayer::test_pbo_and_verdict_consistent`

8. **Volume FVG side expectation is computed from the detector's own returned level** — **HIGH**

   **File:line:** `MyTradingSys/backtest/layers/alerts/test_live_runner_layers.py:113-123`; implementation: `MyTradingSys/backtest/layers/alerts/live_layers.py:58-63`.
   The test derives `mid` from `ev[0]["level"]`, then computes its expected side from that same returned level. The detector also derives its side from its chosen level. A bad level can therefore move the expected side along with the actual side, while the test never checks the independently expected FVG price or event timestamp.
   **Planted mutation:** choose a wrong profile level (for example, use the upper boundary instead of the midpoint) and use it for both the touch and side calculation. The test's `expected` uses the mutated returned level, so its side assertion still passes.
   **Reproduce:** `python -m pytest -q MyTradingSys/backtest/layers/alerts/test_live_runner_layers.py::TestVolumeFvg::test_touch_fires_with_side`

9. **Default-registry test reconstructs output with the same registry builder** — **LOW**

   **File:line:** `MyTradingSys/backtest/layers/alerts/test_live_runner_cli.py:79-87`.
   `test_is_a_build_registry_result` takes entries from `build_default_registry` and feeds their fields to `build_registry`, then compares key sets. This is a self-consistency check: a wrong layer function or parameter identifier can be copied into the reconstruction and still pass. The neighboring test pins several keys, but neither assertion verifies the expected callable/parameter mapping for every entry.
   **Planted mutation:** assign a wrong callable to one default entry while retaining its layer/sub/timeframe/params id. The reconstruction uses that same wrong callable and produces the same keys.
   **Reproduce:** `python -m pytest -q MyTradingSys/backtest/layers/alerts/test_live_runner_cli.py::TestBuildDefaultRegistry::test_is_a_build_registry_result`

10. **CLI poll test replaces the poller with a fake** — **LOW**

   **File:line:** `MyTradingSys/backtest/layers/alerts/test_live_runner_wiring.py:78-90`.
   `poll_once` is patched with `fake_poll`; assertions cover CLI arguments, stdout, and return code only. A regression in the real poller's fresh-event filtering or layer invocation cannot fail this CLI test. The test is scoped to CLI dispatch, but should not be counted as evidence that poll behavior works.
   **Planted mutation:** make the real `poll_once` return no alerts for every poll. The patched fake still supplies its predetermined result, so this test passes.
   **Reproduce:** `python -m pytest -q MyTradingSys/backtest/layers/alerts/test_live_runner_wiring.py::TestObservability::test_once_prints_flushed_poll_line_and_polls_1m`

## Notes on ranking and scope

The first six findings touch the closest signal/order seams or explicit trade-state scenarios. The remaining findings concern gates and backtest validation that can influence which layer is considered promotable. LOW findings identify a real mutation blind spot in that test; several are deliberately narrow unit tests, so they should not be treated as proof that the named subsystem is broken. The WaveTrend and Kurisko golden generators were inspected: they independently implement their stated formulas and do not import the tested layer modules, so they are not reported as same-code golden tautologies.

No planted mutation was applied because the task prohibits editing existing code and tests. The counterfactuals above identify the exact mutation and why the cited test still passes (or skips) without modifying the worktree.

Result: 10 mutation-resistant test gaps ranked by proximity to trade execution; two Fabio golden scenarios silently skip assertion failures unless strict mode is enabled.