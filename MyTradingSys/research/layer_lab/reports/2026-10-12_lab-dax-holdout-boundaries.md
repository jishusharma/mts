Changed `MyTradingSys/backtest/tom_dax_bt.py`, `MyTradingSys/backtest/test_tom_dax_bt.py`, and the H2 audit addendum; requested H2 regressions RED (3 failures) -> GREEN; full harness 47 tests OK.

# DAX H2: clean split enforcement and development outcome isolation

Card: `lab-dax-holdout-boundaries`. Date: 2026-10-12. Surface: COD. Build completed using synthetic fixtures only.

## What was checked and changed

- Source finding: `MyTradingSys/research/layer_lab/reports/2026-10-11_lab-audit-tom-dax-bt.md:15-22` (file legend), `:57` (H2 evidence and proposed fix). Read its cited historical implementation blocks before editing. The original line numbers refer to the audited version, not this larger implementation.
- Source boundary evidence: `MyTradingSys/research/tom_transfer_2026-10-11/PRE_REG_DAX.md:25-26`, `BACKTEST_FAILURES_RESEARCH.md:78-87`, `TOM_TRADE_LEDGER.csv:10-14,29,32-35`; dates and management exposure support consuming an owner-defined clean split. The ledger's uncertainty is not resolved by this build.
- `MyTradingSys/backtest/tom_dax_bt.py:339-418`: validates the required three-key manifest, handles forward dates and embargo, slices complete minute bars, and filters timestamps before parsing development OHLC. `:435-443`: exclusive durable holdout reservation. `:596-617`: counts actual row envelopes before selecting development payloads. `:658-689`: period-bounded simulation. `:701-808`: independently bounded strategy/stress/null periods and full-development accounting. `:832-840`: same-split full-development authorization; `:842-879` and `:957`: required CLI path and report contract.
- `MyTradingSys/backtest/test_tom_dax_bt.py:235-243`: existing missing-download test now supplies a synthetic manifest so it still reaches its intended coverage gate. `:482-628`: seven H2 tests: the two requested red-first regressions and five additional synthetic guards.
- Appended an H2 enforcement addendum to the original audit report; preserved its historical findings and PRE_REG_DAX.md text.
- This report and the task card result are the delivery records. No shared engine, Java, runtime, live path, split-owner file, or pre-registration was edited. No git, sync, ship, release, full quick gate, market backtest or recall command was run.

Synthetic range: four minute bars with timestamps H-120 through H+60, where H = 2026-04-11 00:00 UTC. These timestamps label fabricated prices; they are not historical observations. Other fixtures use manifest dates through 2026-11-01 to verify forward labels without loading market data. No strategy-performance trial occurred; TRIALS.md was not changed.

## Findings and evidence

| Severity | File:line | Claim | Evidence | Fix / remaining scope |
|---|---|---|---|---|
| HIGH | `tom_dax_bt.py:701`, `:658` | MATCH: development outcomes are isolated | Old fixture filled at H-60, `fill_i=1`, and exited on H, `exit_i=2`, reason target. New fixture produces no resolved crossing outcome across two shifts and all variants. | Complete bars stop at H minus embargo; unresolved orders are dropped. Stress uses the same cutoff; null gets the same isolated period bars at `:785`. |
| HIGH | `tom_dax_bt.py:339`, `:957` | MATCH: absent/invalid manifest refuses reporting | Old test reached coverage access; new absent-manifest test raises before either coverage or archive access. Invalid UTC, overlapping exposure/embargo, negative/boolean/NaN embargo are rejected. | Caller must supply the owner's clean manifest. No fallback dates are used by reporting. |
| HIGH | `tom_dax_bt.py:596`, `:762` | MATCH: holdout counts describe actual rows | Old report account returned 0 for two synthetic holdout rows. New account returns 2 across two arms; real JSONL-envelope fixture counts dev=1, embargo=1, holdout=2 while holdout payload keys are absent. | Counts use timestamp envelopes, independent of fills, variants and arms; excluded payloads are not selected. |
| HIGH | `tom_dax_bt.py:435`, `:704`, `:832` | MATCH: reservation precedes outcome evaluation | Synthetic archive-loading failure leaves a marker with holdout_rows=2 and the split identity. A second read refuses. Partial report and month restriction refuse authorization. | Exclusive create, flush and fsync preserve the consumed-read reservation on failure. Full-development token is emitted only after coverage/accounting checks. |
| LOW | `tom_dax_bt.py:376`, `:385` | MATCH: non-minute embargo cannot admit a straddling bar | With a 30-second embargo, H-60..H is excluded, leaving only H-120..H-60. Malformed synthetic holdout-price text is never parsed. | Retain only complete minute bars within the permitted interval. |
| MED | `system/tasks/tom-holdout-clean-split.json:7`, `:33-39` | NOT_IN_DATA: owner cleanliness evidence is not produced here | Existing owner card requests clean dates and ledger design/check lists; this build consumes its interface only. | Owner must supply the actual three-key manifest. H7 scientific readiness and H8 immutable run identity remain separate; this build establishes neither strategy readiness nor an edge. |

Embargo and order-boundary handling are evaluation protocol, not new trader parameters. `design_end_utc` means latest design exposure; require design_end < holdout_start and design_end + embargo <= holdout_start. Development ends strictly before holdout_start - embargo. Periods simulate separately, resetting their schedules; no development position carries into holdout. Standalone historical helper labels remain available, but the report entry points always require a manifest.

## Red-then-green verification

Commands executed with PYTHONPATH set to the work-tree root:

```powershell
$env:PYTHONPATH=(Get-Location).Path
python -B -m unittest MyTradingSys.backtest.test_tom_dax_bt.TestHoldoutBoundaries -v
python -B MyTradingSys/backtest/test_tom_dax_bt.py
```

EXPECT: the requested tests fail on the existing code; after the fix, no development fill/exit uses H or a later bar, a missing manifest refuses before data access, and holdout_rows is 2 rather than 0.

RESULT (2026-10-12, COD lab), before implementation, requested tests only:

```text
test_absent_manifest_refuses_before_data_read ... FAIL
AssertionError: coverage read before manifest
test_development_outcomes_never_touch_holdout_and_count_real_rows [outcome isolation] ... FAIL
AssertionError: True is not false
Evidence in failing trade: t=1775865540.0, filled=True, reason=target,
fill_i=1, exit_i=2, gross_r=1.0, period=dev
test_development_outcomes_never_touch_holdout_and_count_real_rows [actual row count] ... FAIL
AssertionError: 0 != 2
Ran 2 tests in 0.055s
FAILED (failures=3)
```

RESULT (2026-10-12, COD lab), final targeted run (the five later guards are additional verification, not claimed as pre-change behavioral repros):

```text
test_absent_manifest_refuses_before_data_read ... ok
test_development_outcomes_never_touch_holdout_and_count_real_rows ... ok
test_full_dev_guard_and_failed_read_remains_reserved ... ok
test_invalid_manifest_and_forward_boundary ... ok
test_pending_orders_dropped_and_resolved_dev_kept_in_stress ... ok
test_prices_after_cutoff_not_parsed_and_partial_minute_excluded ... ok
test_real_row_envelopes_counted_without_loading_holdout_payload ... ok
Ran 7 tests in 0.049s
OK
```

RESULT (2026-10-12, COD lab), final complete authorized test file:

```text
...............................................
Ran 47 tests in 0.123s
OK
```

The runner performs its own shipping gate after this file-only session. The full quick gate was intentionally not run in the sandbox.

## Follow-up cards created

None. Existing `tom-holdout-clean-split` owns the actual manifest and ledger split. Existing H7/H8 cards own broader readiness and immutable trial identity.
