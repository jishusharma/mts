# B127 - Audit PARTIAL (e): code exists, test missing or only staged

Status: CLOSED 2026-10-08 (13 of 13 rows have a disposition; A11 reclassified by operator ruling, no Java test written). Severity: MED. Opened 2026-10-04.
Session: MTS-2026-10-04-0856Z-APP-BLD-audit-reconcile-followup. References T037 (test coverage gap): MyTradingSys/items/T037_test_coverage_gap.md.

## Defect

Thirteen audit findings have working or present code but no collected test: either none exists, or the test is staged as .new and not collected by the runner.

Source: MyTradingSys/research/_archive/loose_2026-10/AUDIT_RECONCILE_2026-10-04.md PARTIAL rows. Java tests were not executed by C1; presence of a test is not proof it passes.

## Findings (13)

| finding | code | test | gap |
|---|---|---|---|
| RA-W4-A11 | src/main/java/datafeed/SetupCandidatesBuilder.java:133-134 | none | Gross 1.5 drop removed per comment; PROVENANCE_AUDIT_TOM.md row A11 not reclassified; no test. |
| RA-W6-FABIO | MyTradingSys/backtest/layers/alerts/live_runner_cli.py:136 | none | FABIO_V3_DECISIONS marks all grid params SHADOW; no test of that decision map. |
| TC-W1-4 | mts.ps1:233-234 | none | guard verb and status line (mts.ps1:141 area) exist; no test located for launcher. |
| TC-W2-SS | src/main/java/datafeed/SetupScreener.java:15 | none | No test references SetupScreener; code exists. |
| TC-W2-UMS | MyTradingSys/runtime/update_market_state.py:1 | none | No test imports it; B069 OPEN. |
| TC-W2-QC | MyTradingSys/runtime/quad_classify.py:38 | MyTradingSys/runtime/test_quad_classify.py.new:1 | Test only staged .new (not collected); pure-function tests not promoted. |
| TC-W2-RC | MyTradingSys/runtime/regime_classifier.py:18 | MyTradingSys/runtime/test_regime_classifier.py.new:61 | Test only staged .new (not collected); not promoted. |
| TC-TOP5-2 | MyTradingSys/backtest/layers/fabio/v3/engine.py:111 | MyTradingSys/backtest/layers/fabio/v3/tests/test_models_engine.py:1 | Module exists; acceptance 'disable Tom, Fabio unchanged' test not found. |
| TC-TOP5-5 | MyTradingSys/runtime/quad_classify.py:38 | MyTradingSys/runtime/test_quad_classify.py.new:1 | Tests staged only (.new); promotion plus break-once check pending; same state as TC-W2-QC. |
| M29-01 | scripts/dev/declutter_backups.py:95 | none | Predates 10-01 (T057 OPEN). Tool exists; Dumps/_archive/2026-09-29/MANIFEST.csv has 163 rows; no test for it. |
| M30-01 | scripts/dev/declutter_backups.py:98 | none | Predates 10-01. --exclude flag exists; Dumps/_archive/2026-09-30 present; no test for the tool. |
| M30-02 | scripts/dev/declutter_backups.py:98 | none | Predates 10-01. 32 backups archived (Dumps/_archive/2026-10-03/MANIFEST.csv); 6 .pre_tf5 files remain in execution/. |
| B103-F2 (fetch 2020+ funding data) | MyTradingSys/backtest/fetch_binance_archive.py:15 | none | Fetcher supports fundingRate; 80 monthly files 2020-01..2026-08 now in gitignored Dumps; no test. |

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
| RA-W4-A11 | CONFIRMED | SetupCandidatesBuilder.java:153 `c.rrSanity = c.grossRR >= 1.5` advisory only; no Java test; PROVENANCE_AUDIT_TOM.md A11 not reclassified | CLOSED 2026-10-08: operator ruling reclassified A11 to TOM-CONCEPT-ONLY (PROVENANCE_AUDIT_TOM.md:33, summary 34/35). Optional later: Java test that grossRR<1.5 is kept |
| RA-W6-FABIO | REFUTED | backtest/layers/alerts/test_live_runner_v3_shadow.py:141 asserts all FABIO_V3_DECISIONS are SHADOW | CLOSED |
| TC-W1-4 | REFUTED | scripts/dev/test_mts_launcher.py:1,22-25 (runner/orphans verbs) | CLOSED |
| TC-W2-SS | REFUTED | src/test/java/datafeed/SetupScreenerTest.java | CLOSED |
| TC-W2-UMS | REFUTED | MyTradingSys/tests/test_t037_update_market_state.py | CLOSED |
| TC-W2-QC, TC-W2-RC, TC-TOP5-5 | REFUTED | MyTradingSys/tests/test_quad_classify.py, test_regime_classifier.py promoted; .new copies gone | CLOSED |
| TC-TOP5-2 | CONFIRMED then fixed | new MyTradingSys/tests/test_b127_fabio_v3_isolation.py (2 pass); pending_test_fabio_v3.py with only the import changed to the v3 package: 64 pass, 2 fail (T50, X01), both check the old flat fabio_v3*.py file layout, not behaviour | CLOSED; T50/X01 are layout-specific and do not apply to the package |
| M29-01, M30-01, M30-02 | CONFIRMED then fixed | new MyTradingSys/tests/test_b127_declutter_backups.py (3 pass): move not delete, manifest row with sha256, --exclude, dry run | CLOSED for the tool; the 6 .pre_tf5 files in execution/ remain, they are in the live area and need the supervisor |
| B103-F2 | CONFIRMED then fixed | new MyTradingSys/tests/test_b127_fetch_archive_funding.py (6 pass): URL, monthly plan, checksum accept/reject, 404 | CLOSED |

Mutation caveat (operator ruling 2026-10-07): fail-first intent not satisfiable on already-correct code; kept as coverage tests, mutation coverage incomplete. Each new test was broken once in memory (checksum compare, filter flag, move-vs-copy) and caught.
Gate: MyTradingSys/tests collection, see the Build-Check line in the session record.
