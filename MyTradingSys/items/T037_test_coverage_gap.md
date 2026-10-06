# T037 - TEST COVERAGE GAP

Register row: MyTradingSys/research/BUGS.md T037.
Convention: one item, one doc. Verbatim ask at top when available. Updates appended chronologically, newest last.

## VERBATIM ASK

No verbatim ask on record (opened 2026-09-19). Row title and evidence transcribed below from BUGS.md.

Title: Test coverage gap: 8 engine files untested. Build-Check covers Java compile, 125 math tests, 5 doc rules only.

Evidence: AUDIT_2026-09-17_TRACKER.md, "5 Java files + 3 Python files have ZERO test coverage". Java untested: MarketDataSnapshot, SetupCandidatesBuilder, StateCodeEmitter, ExtraSetupBuilder, SetupScreener. Python untested: update_market_state, quad_classify, regime_classifier. B050 and B051 are the class of defect this gap allows.

## STATE

2026-10-04 CLOSED. Tests written for all 8 files; MarketDataSnapshot bodies filled.

## UPDATES (chronological, newest last)

### 2026-09-22T18:00Z - coordinator, session MTS-2026-09-22-1737Z

Item doc created during T039 functionality-doc sweep.

### 2026-10-04 - MTS-2026-10-04-1045Z-APP-BLD-t037-test-coverage

2026-10-04 MTS-2026-10-04-1045Z-APP-BLD-t037-test-coverage: 5 Java + 3 Python engine files now tested (mvn -q test 108 run/15 skipped skeleton, pytest 54 new/promoted); Build-Check full tier runs mvn -q test; 14/14 mutants killed in scratch copy; MarketDataSnapshot body tests still skeleton (BinanceClient seam needed). pom.xml already had junit-jupiter + surefire (no pom edit owed; the BLOCKED cell was stale).

### 2026-10-04 - MTS-2026-10-04-2005Z-APP-BLD-t037-msnap

2026-10-04 MTS-2026-10-04-2005Z-APP-BLD-t037-msnap: MarketDataSnapshotTest 21 tests, 0 skipped (seam b: reflection on private field client + StubClient; MarketDataSnapshot.java untouched); added buildStructure (6 tf blocks, stale flags), buildOiBreakdown (null ratio, changes), buildSpotPerpBasis, dropFormingBar; mvn -q test 128 run/0 failed; 4 mutants killed in scratch copy; run_all_tests --quick PASS.
Notes: historical-snapshot test pins the B075 intended behaviour (null + UNAVAILABLE, no live calls, session attached); the old skeleton comment said 0.0 and is stale. Root key set comes from the old class comment list because data_schema_v1.2.0.md predates session/session_timing/spot_perp_basis/oi_breakdown. save*Snapshot tests write ZZTEST_* files under runtime_data/snapshots (gitignored) and delete them; Java cannot redirect the relative path to a temp dir.
