Changed files: `MyTradingSys/backtest/tom_dax_bt.py`, `MyTradingSys/backtest/test_tom_dax_bt.py`, `MyTradingSys/research/layer_lab/reports/2026-10-11_lab-audit-tom-dax-bt.md`, and this report. H3 red then green: 2 tests initially failed (1 FAIL + 1 ERROR); 6 session-null tests and all 53 harness tests now pass.

## Checked and changed

- Source: audit file legend at `2026-10-11_lab-audit-tom-dax-bt.md:9-21` and H3 at line 58; historical cited D:220-255 is now replaced by the session-null implementation. Read `PRE_REG_DAX.md:22`, `BACKTEST_FAILURES_RESEARCH.md:106-108`, `TOM_CORE_BT_REVIEW_2026-09-30.md:32-39`, and strategy simulator/scheduling in `tom_bt.py:179-244`.
- `tom_dax_bt.py:206-289`: session-end entry eligibility shares the existing real-bar touch simulator. Pending lifetime still counts elapsed minutes; positions retain the original hold clock and closure execution model.
- `tom_dax_bt.py:292-405`: explicit local session validation/loading, session bounds, original-opportunity selection and random limit draws. Entry/reference-open and stop/entry/target ratios preserve offset and geometry. Reference is the current submission bar's open, never a later bar. Seeds and draw accounting are returned even when there are no resolved fills.
- `tom_dax_bt.py:718-776`: shared strategy/null scheduler; filled positions and pending orders occupy one slot. Unresolved orders stay busy through the coverage end. `simulate` still excludes unresolved outcomes from resolved strategy output.
- `tom_dax_bt.py:782-905`, `1000-1030`, `1063`: reports require the owner-supplied `--null-session` JSON before data access, start from `T.signals` on period-isolated rows, and print session/source, seed, real counts and all draw counts. Strategy/stress/null use the same supplied session. Existing BTC implementation is unchanged and was not run.
- `test_tom_dax_bt.py:207-224`, `482-548`, `647-771`, `849-869`: synthetic closure integration, boundary-isolated report serialization, six H3 guards and real-minute drawing. Synthetic report serialization stubs git/hash probes and uses a temporary fixture report/registry only; its table rows remain contiguous.
- Audit report: added an H3 current-contract addendum at `2026-10-11_lab-audit-tom-dax-bt.md:160-168`. Original findings and original `PRE_REG_DAX.md` text are preserved.

All bar arrays and CSVs used here are generated fixtures. The winter/summer dates are timezone labels, not historical observations. No archive, snapshot, holdout or real outcome run was requested or evaluated; no real-data trial was performed and no trial ledger entry was created. The runner owns the ship gate. No git, sync, push or full gate command was executed.

## Findings

| Severity | File:line | Finding / classification | Evidence | Fix / disposition |
|---|---|---|---|---|
| HIGH | audit:58; old null implementation | MISMATCH before: UTC-day next-open entries, one-minute fill window, resolved-fill selection, no scheduling. | Red lifetime regression observed thirty `fill_window=1` calls; session regression raised unsupported `session` argument. | MATCH after: original variant opportunities, same local session, passive limit geometry, same touch/ran/no-fill model, lifetime and one-at-a-time scheduler. `tom_dax_bt.py:339`, `732`. |
| HIGH | `tom_dax_bt.py:306`, `782` | MATCH: absent/invalid session is rejected before report coverage/outcome reads. | Missing session, invalid timezone/time, equal endpoints and missing source are rejected by tests at `test_tom_dax_bt.py:647`. | Owner supplies frozen timezone/start/end/source addendum; no fallback session or production hours added. |
| MED | `tom_dax_bt.py:339`, `1009` | MATCH: opportunity/fill attrition and draw accounting remain visible without inference. | Synthetic 30-opportunity draw samples all 30, expires submitted passive orders unfilled, skips busy orders, and repeats exactly with seed 7; ran-only draws count as empty. Tests at `test_tom_dax_bt.py:691`, `727`. | Original versus eligible/outside-session opportunities; real and per-draw submitted, busy, filled, resolved, no-fill, ran, unresolved counts; requested/nonempty/empty draws and seed. P remains unavailable with fewer than 30 real resolved fills. |
| MED | `tom_dax_bt.py:206`, `732` | MATCH: session-end entry confinement and coverage-end scheduling. | Outside-session price touch cannot fill the pending order; unresolved 40-minute order in 20-minute coverage blocks the second signal. `test_tom_dax_bt.py:675`. | Submission and entry fill restricted to the window; order/hold clocks remain unchanged, positions may exit outside the window. |
| MED | audit M3; `tom_dax_bt.py:753` | NOT_IN_DATA: production session hours/source and trader provenance for inherited eight-bar management are not established by this card. | Audit M3 identifies the unsourced timeout; this build provides only configurable session inputs and synthetic fixture hours. | No tuning or new trader parameter. Report caveat preserves the distinction; the existing session/management owner must supply the sourced addendum before a production report. |

## Red then green

EXPECT from H3 and the method review: a 5m-zone order uses the same inherited 8 x 5 = 40 minute pending window as strategy; supplied local session bounds constrain entries; expired passive orders can remain unfilled; pending/live orders prevent overlapping submission.

Red command, before any product-code edits:

```powershell
$env:PYTHONPATH=(Get-Location).Path
python -B -m unittest MyTradingSys.backtest.test_tom_dax_bt.TestSessionNull -v
```

RESULT (2026-10-12, COD lab):

```text
test_null_preserves_order_lifetime ... FAIL
test_session_limits_expiry_and_one_at_a_time ... ERROR
TypeError: random_entry_null() got an unexpected keyword argument 'session'
AssertionError: False is not true : [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
Ran 2 tests in 0.004s
FAILED (failures=1, errors=1)
```

Green targeted command is identical, after implementation and additional guards:

```text
test_missing_or_invalid_session_refuses_before_data_read ... ok
test_null_preserves_order_lifetime ... ok
test_ran_short_geometry_and_original_opportunities ... ok
test_session_end_no_entry_fill_and_unresolved_order_blocks ... ok
test_session_limits_expiry_and_one_at_a_time ... ok
test_timezone_dst_and_overnight_sessions ... ok
Ran 6 tests in 0.035s
OK
```

Full harness command sets PYTHONPATH to the work tree and places temporary fixtures inside it:

```powershell
$env:PYTHONPATH=(Get-Location).Path
python -B -c "import tempfile,runpy; from pathlib import Path; tempfile.tempdir=str(Path('MyTradingSys/backtest').resolve()); runpy.run_path('MyTradingSys/backtest/test_tom_dax_bt.py',run_name='__main__')"
```

RESULT (2026-10-12, COD lab):

```text
.....................................................
Ran 53 tests in 0.275s
OK
wrote F:\MTS\mts-codex-lab\MyTradingSys\backtest\tmpuv2c4zu2\report.md (8 registry rows, 0s)
```

The last line is synthetic report-rendering test output; its temporary report and registry are removed by the fixture. It is not a research result or a production trial registration.

## Follow-up cards

None created. The existing session/management owner supplies the frozen sourced production addendum; this card does not establish readiness for a real outcome run.
