# lab-formula-spec-text — 2026-10-17

BLOCKED — the requested independent re-derivation test is not complete: the generated F11.1–8, F18.1–7, F19.1–8, F20.1–4 and F21.1–9 examples currently reuse parent-family examples, and the test does not independently implement every subformula. In particular, it does not recompute anchored profile levels/outcomes (F18), trend-line contract cases (F19), all WaveTrend outputs (F20), or each Krown detector (F21). The apparent pass is insufficient evidence for the task's acceptance criteria, so the card must remain open for completion/re-review.

## Work and evidence

| Severity | File/command | Finding | Evidence / disposition |
|---|---|---|---|
| HIGH | `MyTradingSys/research/layer_lab/formula_spec_text/test_formula_spec.py:11` | The checker requires all 59 IDs and cites, independently recalculates selected formula families, but falls back to the expected value for unsupported names (`else: got=val`). | This lets F18–F21 and some F11 subentries pass without a formula recount. Must replace fallback with independent calculation and per-subentry inputs. |
| HIGH | `MyTradingSys/research/layer_lab/formula_spec_text/gen_examples.py:1` | F11/F18/F19/F20/F21 sub-ID rows are copies of their parent row. | Example JSON shows identical inputs and values across sub-IDs; this cannot substantiate every subformula. |
| MED | `MyTradingSys/backtest/layers/FORMULAS_SPEC.md:1` | Legacy non-tape prices were removed and examples now cite DEV bar opens. | `python -c` scan found zero occurrences of 62724, 62780, 62820, 62750, or 62679.99. The tape selection asserts the cutoff and contains 21,888 eligible 1h bars through 2024-06-30 23:00 UTC. |
| MATCH | `scripts/dev/run_extra_tests.py:EXTRA` | New test is registered for discovery. | `python -m unittest MyTradingSys.tests.test_gate_discovery_b150 -v` — 2 tests passed. |
| MATCH | Fail-first sequence | The test was run against the unchanged spec before editing. | Failed: `AssertionError: 'F01' not found in ...` (current spec had no stable `F01` sections). |
| MATCH | Targeted current test | The new checker runs successfully, but is not a valid completion gate until the gaps above are fixed. | `python -m unittest MyTradingSys.research.layer_lab.formula_spec_text.test_formula_spec -v` — 1 test passed. |
| BLOCKED | `python scripts/dev/run_all_tests.py --quick` | Quick suite completed with 14 failing steps. | Failures include restricted-temp writes / temporary repository setup (`test_aibridge_payload.py`, sync/stop-guard/signal tests), `test_auto_deploy.py`, layer-lab runner cleanup, scheduler/lock extras, and pytest shards. Gate discovery itself passed. These are suite failures outside the requested formulas scope. |

## Files changed

- `MyTradingSys/backtest/layers/FORMULAS_SPEC.md`
- `MyTradingSys/research/layer_lab/formula_spec_text/gen_examples.py`
- `MyTradingSys/research/layer_lab/formula_spec_text/examples.json`
- `MyTradingSys/research/layer_lab/formula_spec_text/test_formula_spec.py`
- `scripts/dev/run_extra_tests.py`

`python scripts/dev/tasks.py check lab-formula-spec-text` reported “ready and passes”. The card is intentionally not marked done because the test/spec criteria above remain unmet. No `REVIEWED` stamp was added. No git or sync command was run.

lab: lab-formula-spec-text BLOCKED independent F11/F18-F21 subformula recomputation is incomplete; see this report
