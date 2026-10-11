# MTS-2026-10-03-1714Z-CLI-BLD-tf7-fabio-golden-sce
surface: CLI
host: JIS-NB
account: A
model: claude-sonnet-5-5
role: BLD
branch: fast-track
branch_alias: none
predecessor: MTS-2026-10-03-1659Z-CLI-BLD-tf6-tom-golden-scena
lanes: none (no subagents)
started: 2026-10-03 17:14Z
ended: 2026-10-03 (commit carrying the MTS-Session trailer)
status: closed
commits: the commit with prefix "TF7: "
handoff: none; no live-imported file touched, nothing to promote

## Scope
BUILD_PIPELINE row 1.9 (TF7): Fabio golden-scenario translation tests (L2) on v3. New file only:
MyTradingSys/backtest/layers/fabio/v3/tests/test_fabio_golden.py (the row says v3/tests/; the package lives at
MyTradingSys/backtest/layers/fabio/v3). No live process imports it; no .new needed. No execution/ or layers/alerts/ edit.

## T0 facts (from disk)
- Row 1.9 BUILD_PIPELINE.md:48 QUEUED, blocker 1.3; row 1.3 LANDED (PYTEST_LAYER_PATHS in scripts/dev/run_all_tests.py:15-20).
- v3 already holds S5D / model D / E_opp / E_own / S9 (signals.py:325-367, models.py:231-260, manage.py:164-186), so most of the
  fZl missing pieces M1, M2, M4, M8 are implemented; the tests assert the translation, not the old gap list.

## Result
20 tests: 18 pass, 2 KNOWN GAP (skip with reason, strict env lists them): g10 (D28: 3 entries are one record; adds are
decision helpers only, README) and g19 (D18/M3: S8(b) exits on S2 == -s although the sellers are the absorbed side).
Fixtures are our reconstruction in normalised units (no trader trade has a BTC date). Expected numbers hand-derived in comments.
Fail-first: file absent = collection error; 4 source mutants (opp_stop best, S4 in S5, model-D structural stop, S8(a)) each
turned a named test red, sources restored (diff against HEAD empty for them).
Gate: python scripts/dev/run_all_tests.py --quick = ALL TESTS PASSED.

## T5 deviations
- Path: the row names v3/tests/; actual package path above.
- Not translatable, no test: D09/M9 re-pivot (no code path), D13 cross-session day P&L (no state in run()), D21/M10 big trades
  by price (not in the bars), D27 exit by day type (ex-post only), D18 buyers wall (needs L2).
- 0jM5Y31YJak / 8CWKfoSJu3c are covered through FABIO_TRADE_MODEL.md section 1 steps (TM2-TM8), not their transcripts.
- Working tree had unrelated dirty files (heartbeats, orderflow_live, session_log.json, .new deletions); not staged.
