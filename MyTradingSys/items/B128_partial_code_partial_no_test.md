# B128 - Audit PARTIAL (f): code partial or unwired, no test

Status: OPEN (receipt written 2026-10-07, updated 2026-10-08; 11 of 18 closed, residual rows named). Severity: MED. Opened 2026-10-04.
Session: MTS-2026-10-04-0856Z-APP-BLD-audit-reconcile-followup. References T037 (test coverage gap): MyTradingSys/items/T037_test_coverage_gap.md.

## Defect

Eighteen audit findings have code that is incomplete, unwired or only config/doc, with no test (or a test that does not cover the residual). Config and doc items are included because the audit rated them PARTIAL; they may need a non-test receipt.

Source: MyTradingSys/research/_archive/loose_2026-10/AUDIT_RECONCILE_2026-10-04.md PARTIAL rows. Java tests were not executed by C1; presence of a test is not proof it passes.

## Findings (18)

| finding | code | test | gap |
|---|---|---|---|
| RA-W2-N | MyTradingSys/backtest/tom_bt_report.py:174 | none | Registry row count code exists; N=3 dedupe basis and DSR calc not implemented, no test. |
| TC-W1-2 | mts.ps1:239-242 | none | Runner starts via guard verb; status block (mts.ps1:115-150) still has no runner line. |
| TC-W1-5 | MyTradingSys/execution/orphan_watchdog_cli.py:53 | MyTradingSys/execution/test_orphan_watchdog_cli.py:31 | CLI and tests exist; verified no 'orphan' in mts.ps1, so launcher/status verb still missing. |
| TC-W1-6 | MyTradingSys/backtest/layers/cryptocred/cc_structure.py:81 | none | Flag default False; live_layers.py:122 _cc_layer passes no flag; no test of filter_range_noise. |
| TC-W1-10 | scripts/dev/testnet_status.py:314 | scripts/dev/test_testnet_status.py:142 | Code and tests exist; scheduling unverified. Only CANARY_2026-10-02.md under research/testnet_status. |
| TC-W2-MDS | src/main/java/datafeed/MarketDataSnapshot.java:19 | src/test/java/datafeed/CvdAnchorDisplayOnlyTest.java:34 | Partial tests exist (CVD, historical) now; no snapshot field contract or OI delta-state test; T037 pom edit pending. |
| TC-W2-SCE | src/main/java/datafeed/StateCodeEmitter.java:349 | scripts/tools/VerifyStateCodeCvd.java:9 | Only CVD rollover covered by a verify tool outside src/test (B034/T028); state letters and counts untested. |
| TC-TOP5-3 | scripts/dev/alert_rate_check.py:23 | scripts/dev/test_alert_rate_check.py:39 | TF half done; consensus writer only staged .new, fire-N-alerts-count-N-rows acceptance absent. |
| TC-TOP5-4 | mts.ps1:239-242 | none | Runner started in guard verb; status prints neither runner nor watchdog; no mts test. |
| M29-02 | .gitignore:77-90 | none | Predates 10-01. Ignore rules present (*.pre_*, journal/, plans/*.json etc.); config, untestable by unit test. |
| M29-03 | MyTradingSys/backtest/layers/positioning/test_funding_cvd_fade.py:1 | none | Predates 10-01, open list. Four layer tests and OPUS_PREMAINNET_AUDIT.md now tracked; evidence is git ls-files, not code. |
| M29-11 | MyTradingSys/execution/auto_trader.py:76 | MyTradingSys/execution/test_auto_trader.py:240 | Predates 10-01. rsi:cross still maps direction->side regardless of level; code and test exist but the semantic risk stands. |
| M29-14 | MyTradingSys/system/LESSONS_LEARNED.md:104 | none | Predates 10-01. Documented as lesson only; new_plan.py:157 help is 'validity window'; flag not renamed. |
| M29-15 | MyTradingSys/execution/auto_trader.py:320 | none | Predates 10-01. Comment states t_close is bar open time; key name unchanged; no test. |
| M29-18 | CLAUDE.md:34-43 | none | Predates 10-01. Lessons F (LESSONS_LEARNED.md:76) and CLAUDE.md rules present; doc-only, no test. |
| M30-03 | .gitignore:92-93 | none | Predates 10-01. runtime/*.lock and .claude/settings.local.json ignored; config only. |
| M30-04 | MyTradingSys/research/fast_track_2026-09-27/bt_runs/TRIAL_REGISTRY.csv:1 | none | Predates 10-01, open. TRIAL_REGISTRY.csv tracked; tom_core_20260929/ still untracked; .gitkeeps ignored by .gitignore:95-96. |
| M30-11 | scripts/dev/cicd_run.py:790 | MyTradingSys/tests/test_cicd_run.py:307 | Predates 10-01, open. CI L6 checks owner/end in log; test covers only no-pause pass. Proposed file-content mechanism absent (auto_trader.py:618). |

## Fix shape

Follow-up sessions add the missing tests (derive them from the spec, not from existing code; each new test must fail on pre-change code at least once). Promotion of staged .new tests follows CLAUDE.md: back up to .pre_<tag>, rename, re-gate, commit. Items with no unit-testable surface (config, docs) need a different receipt such as a doc check; do not invent a test.

## Scope of this filing

Filing only. No code or test was written.

## Related

- T037 | MyTradingSys/items/T037_test_coverage_gap.md
- MyTradingSys/research/_archive/loose_2026-10/AUDIT_RECONCILE_2026-10-04.md
- MyTradingSys/system/sessions/MTS-2026-10-04-0856Z-APP-BLD-audit-reconcile-followup.md

## Receipt

Session MTS-2026-10-07-1002Z-APP-BLD-research-closeout, verdicts checked on disk after the live tree was fast-forwarded to 5053e2d.

| finding | verdict | evidence | disposition |
|---|---|---|---|
| TC-W1-2, TC-TOP5-4 | REFUTED | mts.ps1:154-173 prints the alert runner status; scripts/dev/test_mts_launcher.py | CLOSED |
| TC-W1-5 | REFUTED | mts.ps1:42 `orphans` verb, :44 `runner` verb | CLOSED |
| TC-W1-6 | CONFIRMED then fixed | new MyTradingSys/tests/test_b128_cc_range_noise_filter.py (3 pass). live_runner _cc_layer still passes no flag (default False) | CLOSED for the test; operator ruling 2026-10-08: flag stays off, neutrality test filed as B145 |
| TC-TOP5-3 | REFUTED | MyTradingSys/backtest/layers/consensus/writer.py and test_writer.py promoted (row-count test at test_writer.py:53-60); .new pair gone | CLOSED |
| M29-02, M30-03 | CONFIRMED (config) | .gitignore:77-90 and :93-94 hold the rules; doc check, no unit test applies | CLOSED |
| M29-03 | CONFIRMED | git ls-files lists positioning/test_funding_cvd_fade.py and research/fast_track_2026-09-27/review/OPUS_PREMAINNET_AUDIT.md | CLOSED |
| M29-18 | CONFIRMED (doc) | CLAUDE.md hard rules and LESSONS_LEARNED.md:76 | CLOSED |
| RA-W2-N | UNVERIFIED | tom_bt_report.py:174 counts registry rows; N=3 dedupe and DSR not implemented | OPEN: needs the DSR formula in FORMULAS.md first, then a test |
| TC-W2-MDS, TC-W2-SCE | UNVERIFIED | Java tests: Build-Check ran 147/147; no snapshot-field-contract, OI delta-state or state-letter test written this session | OPEN: write the Java tests (src/test only) |
| TC-W1-10 | UNVERIFIED | research/testnet_status has 10-01, 02, 03, 05, 07 only; no 10-04 or 10-06 | OPEN: scheduler gap, check the task on the desktop |
| M29-11 | CONFIRMED | auto_trader.py:75-78 rsi:cross direction->side; test exists, semantic risk stands | CLOSED 2026-10-08: operator ruling, rsi:cross now side-by-level (auto_trader.py CROSS_SIDE_BY_LEVEL: 40 down -> short, 60 up -> long, all else no side per MLK-R1); test_auto_trader.py::test_rsi_cross_side_by_level failed before, 91 pass; backup auto_trader.py.pre_rsicross; takes effect at the next auto_trader restart (supervisor) |
| M29-15 | CONFIRMED | auto_trader.py t_close key | CLOSED 2026-10-08: operator accepted the documented meaning (bar open time); one-line comment added in layer_signal, no rename |
| M29-14 | CONFIRMED | lesson only; new_plan.py:157 help text 'validity window', flag not renamed | OPEN: not covered by the 2026-10-08 rulings |
| M30-04 | CONFIRMED | bt_runs/tom_core_20260929/ still untracked; the Tom core rerun writes a fresh dir | OPEN: track after the Tom rerun |
| M30-11 | UNVERIFIED | cicd_run.py L6 owner/end check; file-content mechanism absent | OPEN |

Mutation caveat (operator ruling 2026-10-07): fail-first intent not satisfiable on already-correct code; kept as coverage tests, mutation coverage incomplete. Each new test was broken once in memory (checksum compare, filter flag, move-vs-copy) and caught.

Addendum 2026-10-08: F:\MTS\data\tom_snapshots_smoke moved to F:\MTS\data\_archive\smoke\2026-10-07\ (2026-09.jsonl.gz sha256_8=737621E3 lines=60; 2026-09.meta.json sha256_8=047A39D8 lines=1); the emptied source folder was left in place. Residual rows now: RA-W2-N, TC-W2-MDS, TC-W2-SCE, TC-W1-10, M29-14, M30-04, M30-11.
