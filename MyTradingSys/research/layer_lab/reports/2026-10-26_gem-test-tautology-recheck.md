# Lab Report: Re-check of GPT Test-Tautology Findings (2026-10-28)

**Task**: `gem-test-tautology-recheck`  
**Card Title**: `[GEMINI] Check GPT's test-tautology findings 1-2 and every cited file:line`  
**Producer**: GPT `gpt-6-luna` ([`MyTradingSys/research/gpt_burn_2026-10-24/gx-test-tautology/report.md`](file:///C:/Users/e-ngineers/IdeaProjects/mts-desktop-f7iu69n-gem-test-tautology-recheck/MyTradingSys/research/gpt_burn_2026-10-24/gx-test-tautology/report.md))  
**Reviewer**: Google Gemini (Google AI Pro, Antigravity, host DESKTOP-F7IU69N; vendor separation MET)  
**Files Audited**:
- `MyTradingSys/backtest/layers/alerts/test_live_runner_v3_shadow.py` (lines 56–60, 96–103, 114–129)
- `MyTradingSys/research/gpt_burn_2026-10-24/gx-test-tautology/report.md`
- All source files cited in Findings 1–10 (19 file:line range citations checked)

*Constraint adherence*: In accordance with the task brief, report mutation counterfactual text was not run as live mutations. Source inspections confirmed test structure, injected stubs, assertion patterns, and file:line existence.

---

## 1. Executive Summary

1. **Findings 1 & 2 Confirmed**:
   - In [`test_live_runner_v3_shadow.py:56-60`](file:///C:/Users/e-ngineers/IdeaProjects/mts-desktop-f7iu69n-gem-test-tautology-recheck/MyTradingSys/backtest/layers/alerts/test_live_runner_v3_shadow.py#L56-L60), `make_registry` explicitly injects `run_fn=lambda win, cfg: dict(STUB_SIGNAL)` into the Fabio v3 layer builder.
   - Both [`test_b_shadow_signal_produces_zero_orders`](file:///C:/Users/e-ngineers/IdeaProjects/mts-desktop-f7iu69n-gem-test-tautology-recheck/MyTradingSys/backtest/layers/alerts/test_live_runner_v3_shadow.py#L96-L103) (lines 96–103) and [`test_c_source_signal_flows_as_ordinary_layer`](file:///C:/Users/e-ngineers/IdeaProjects/mts-desktop-f7iu69n-gem-test-tautology-recheck/MyTradingSys/backtest/layers/alerts/test_live_runner_v3_shadow.py#L114-L129) (lines 114–129) invoke `alerts_for()`, which instantiates the registry via `make_registry()`.
   - Consequently, **neither test ever invokes `engine.run`** from Fabio v3. The tests exercise exclusively the routing, auto-trader dispatch, and shadow filtering of canned dictionary structures (`STUB_SIGNAL`), leaving the actual Fabio signal generation logic unexercised in these runner test cases.

2. **File:Line Citations Verification**:
   - Every file:line reference across all 10 findings in `gx-test-tautology/report.md` was verified against the repository codebase.
   - Total citations checked: **19 file:line ranges across 8 distinct files**.
   - **Mismatches found: 0 of 19 (100% verified)**.

---

## 2. Detailed Verification of Findings 1 & 2

### Finding 1: Fabio Source Route Test Bypasses Fabio Signal Engine
- **Target**: [`test_live_runner_v3_shadow.py:56-60, 114-129`](file:///C:/Users/e-ngineers/IdeaProjects/mts-desktop-f7iu69n-gem-test-tautology-recheck/MyTradingSys/backtest/layers/alerts/test_live_runner_v3_shadow.py#L56-L60)
- **Code Inspection**:
  ```python
  56: def make_registry(decisions, grid=SMALL_GRID):
  57:     fn = cli.make_fabio_v3_layer(grid=grid, decisions=decisions, fixed={"g": "off", "entry_mode": "confirm",
  58:                                                                         "mgmt": "event"},
  59:                                  run_fn=lambda win, cfg: dict(STUB_SIGNAL), flow_fn=lambda bars: bars)
  60:     return build_registry([{"layer": "fabio", "sub": "v3_grid", "tf": "1m", "fn": fn, "params_id": "test",
  61:                             "confirm_lag_bars": 0}])
  ```
- **Execution Path**:
  `test_c_source_signal_flows_as_ordinary_layer` calls `alerts_for(ALL_SOURCE)`, which builds the runner using `make_registry(ALL_SOURCE)`. When `runner.poll_once()` runs, it calls `fn(window, cfg)`, which executes the injected lambda `lambda win, cfg: dict(STUB_SIGNAL)`.
- **Verdict**: **CONFIRMED**. Real Fabio v3 signal generation (`engine.run`) is bypassed completely.

### Finding 2: Shadow Zero-Order Test Also Bypasses Fabio Signal Engine
- **Target**: [`test_live_runner_v3_shadow.py:56-60, 96-103`](file:///C:/Users/e-ngineers/IdeaProjects/mts-desktop-f7iu69n-gem-test-tautology-recheck/MyTradingSys/backtest/layers/alerts/test_live_runner_v3_shadow.py#L96-L103)
- **Code Inspection**:
  `test_b_shadow_signal_produces_zero_orders` calls `alerts_for(ALL_SHADOW)`, which similarly invokes `make_registry(ALL_SHADOW)` with the identical `run_fn=lambda win, cfg: dict(STUB_SIGNAL)`.
- **Verdict**: **CONFIRMED**. The test verifies that shadow signals suppress `plan_args` at the auto-trader boundary, but relies on a mocked/stubbed dictionary rather than testing integration with `engine.run`.

---

## 3. Comprehensive File:Line Existence Audit (All 10 Findings)

| Finding # | Severity | File Path | Cited Lines | Exists? | Description / Verified Content |
|---|---|---|---|---|---|
| 1 | HIGH | `MyTradingSys/backtest/layers/alerts/test_live_runner_v3_shadow.py` | 56–60 | YES | `def make_registry(decisions, grid=SMALL_GRID):` injects `run_fn=lambda win, cfg: dict(STUB_SIGNAL)` |
| 1 | HIGH | `MyTradingSys/backtest/layers/alerts/test_live_runner_v3_shadow.py` | 114–129 | YES | `test_c_source_signal_flows_as_ordinary_layer` consumes stubbed registry |
| 2 | HIGH | `MyTradingSys/backtest/layers/alerts/test_live_runner_v3_shadow.py` | 56–60 | YES | Injected stub in `make_registry` |
| 2 | HIGH | `MyTradingSys/backtest/layers/alerts/test_live_runner_v3_shadow.py` | 96–103 | YES | `test_b_shadow_signal_produces_zero_orders` consumes stubbed registry |
| 3 | HIGH | `MyTradingSys/backtest/layers/fabio/v3/tests/test_fabio_golden.py` | 55–66 | YES | `def known_gap(ref):` converts `AssertionError` to `SkipTest` unless strict |
| 3 | HIGH | `MyTradingSys/backtest/layers/fabio/v3/tests/test_fabio_golden.py` | 362–363 | YES | `@known_gap(...)` decorator on G19 seller absorption test |
| 4 | HIGH | `MyTradingSys/backtest/layers/fabio/v3/tests/test_fabio_golden.py` | 55–66 | YES | `def known_gap(ref):` decorator definition |
| 4 | HIGH | `MyTradingSys/backtest/layers/fabio/v3/tests/test_fabio_golden.py` | 247–248 | YES | `@known_gap(...)` decorator on G10 reload/trade-record test |
| 5 | HIGH | `MyTradingSys/backtest/layers/promotion/test_promote.py` | 108–114 | YES | `test_recompute_matches_manifest_numbers` checks only `ci_low < mean < ci_high` |
| 5 | HIGH | `MyTradingSys/backtest/layers/promotion/promote.py` | 69–78 | YES | `def recompute_oos(path):` computes bootstrap bounds |
| 5 | HIGH | `MyTradingSys/backtest/layers/promotion/promote.py` | 242–250 | YES | Promotion gate compares `ci_low` against tolerance |
| 6 | LOW | `MyTradingSys/backtest/layers/alerts/test_live_runner_of_feed.py` | 102–120 | YES | `test_layer_emits_from_files_through_registry` injects stub lambda returning `SIGNAL` |
| 7 | LOW | `MyTradingSys/backtest/layers/test_run_bracket_grid.py` | 210–215 | YES | `test_pbo_and_verdict_consistent` evaluates consistency against same `decide` |
| 7 | LOW | `MyTradingSys/backtest/layers/run_bracket_grid.py` | 99 | YES | `def decide(...)` gate signature |
| 7 | LOW | `MyTradingSys/backtest/layers/run_bracket_grid.py` | 109–156 | YES | `def run_layer(...)` implementation calling `decide(...)` |
| 8 | HIGH | `MyTradingSys/backtest/layers/alerts/test_live_runner_layers.py` | 113–123 | YES | `test_touch_fires_with_side` derives expectation from returned `ev[0]["level"]` |
| 8 | HIGH | `MyTradingSys/backtest/layers/alerts/live_layers.py` | 58–63 | YES | Volume FVG layer level and touch detection |
| 9 | LOW | `MyTradingSys/backtest/layers/alerts/test_live_runner_cli.py` | 79–87 | YES | `test_is_a_build_registry_result` re-feeds default entries to builder |
| 10 | LOW | `MyTradingSys/backtest/layers/alerts/test_live_runner_wiring.py` | 78–90 | YES | `test_once_prints_flushed_poll_line_and_polls_1m` patches `poll_once` with `fake_poll` |

**Summary**: 19 of 19 citations exist exactly as specified (0 mismatches).

---

## 4. Findings Summary Table

| Severity | File:Line | What is wrong / Tautology identified | Evidence | Proposed Fix |
|---|---|---|---|---|
| HIGH | `alerts/test_live_runner_v3_shadow.py:56-60, 114-129` | Source test passes canned stub, never executing `engine.run`. | Line 59 passes `run_fn=lambda win, cfg: dict(STUB_SIGNAL)`. | Add an integration test case passing real Fabio engine to verify end-to-end signal production. |
| HIGH | `alerts/test_live_runner_v3_shadow.py:56-60, 96-103` | Shadow guard test uses canned stub signal, bypassing engine calculation. | Line 59 injects lambda; `test_b_shadow_signal_produces_zero_orders` relies on stub. | Keep unit guard test as is, but document scope or pair with an end-to-end test using real `engine.run`. |
| HIGH | `fabio/v3/tests/test_fabio_golden.py:55-66, 362-363` | `@known_gap` catches `AssertionError` and skips G19 test unless strict mode is enabled. | Lines 55–66: `except AssertionError as exc: raise unittest.SkipTest(...)`. | Require strict mode in release CI or track open known gaps with explicit skip markers. |
| HIGH | `fabio/v3/tests/test_fabio_golden.py:55-66, 247-248` | G10 assertion failures are caught and converted to test skips by default. | Lines 247–248 decorated with `@known_gap`. | Same as above: ensure CI enforces strict mode for regressions. |
| HIGH | `promotion/test_promote.py:108-114` | Confidence interval test asserts only `ci_low < mean < ci_high` without pinned expected values. | Lines 111–114 assert ordering and self-comparison across re-runs. | Compare bootstrap CI bounds against pre-computed golden values for fixed test data. |
| LOW | `alerts/test_live_runner_of_feed.py:102-120` | Live flow test passes always-signaling lambda, bypassing decision logic. | Line 106: `run_fn=lambda w, c: {"verdict": "SIGNAL", ...}`. | Maintain explicit documentation that test is scoped to file feed ingestion only. |
| LOW | `test_run_bracket_grid.py:210-215` | Test asserts verdict consistency by re-calling `G.decide` with the same arguments. | Line 214 calls `G.decide(..., pbo=res["pbo"]) == res["verdict"]`. | Include test cases with known synthetic inputs producing deterministic expected verdicts. |
| HIGH | `alerts/test_live_runner_layers.py:113-123` | Expected side is computed from detector's own returned level `ev[0]["level"]`. | Line 119: `expected = "long" if ev[0]["level"] > 100.0 else "short"`. | Assert side against the true expected level predetermined by the input candles fixture. |
| LOW | `alerts/test_live_runner_cli.py:79-87` | Reconstructs registry from output of default registry using same builder. | Lines 81–86 copy entries and assert equality of keys. | Assert exact handler mappings against an independently defined specification dictionary. |
| LOW | `alerts/test_live_runner_wiring.py:78-90` | CLI test patches `poll_once` with `fake_poll`, testing only CLI plumbing. | Line 79 patches `alerts.live_runner.poll_once`. | Document boundary: test validates CLI parsing and formatting, not poll behavior. |

---

## 5. Verdict

**Verdict: SOUND.**  
GPT's audit findings in `gx-test-tautology/report.md` are accurate, fully verified against the codebase, and technically sound:
1. `test_live_runner_v3_shadow.py:56-60` injects `run_fn=lambda win, cfg: dict(STUB_SIGNAL)`, confirming that neither `:96-103` nor `:114-129` executes `engine.run`.
2. All 19 file:line range citations across the 10 reported findings exist in the codebase with **0 mismatches**.
