# AUDIT CLOSEOUT 2026-10-07

Session: MTS-2026-10-07-1002Z-APP-BLD-research-closeout. Verdicts are from disk on 2026-10-07 after the live tree was fast-forwarded to 5053e2d.

## Part 0: Build-Check scope
- BUILD_REPORT.md never lost the Java lines. The tracked file read 2026-10-03 20:34Z (Java compile, 237 math), written before commit 7563de7 (2026-10-04) added "Java tests:" to scripts/Build-Check.ps1. A fresh full run 2026-10-07 10:05Z: Java compile PASS, Java tests 147/147, Math 345/345, Doc 5/5, STATUS PASS.
- The 237 to 345 delta is stale file vs current collection (pytest MyTradingSys/tests --ignore=docs collects 348 with this session's tests). No file removed, no path dropped. The copies in mts-research, mts-registry and BinanceDataFeed.registry still hold the 2026-10-03 report.

## Part 1: inventory
All 13 source paths exist. Rows were reached through AUDIT_RECONCILE_2026-10-04.md (which carries the other nine documents' findings) and the three item docs; the nine other audit documents were not re-read line by line this session.

| source | reached | verdict summary |
|---|---|---|
| AUDIT_RERUNS_2026-10-06.md | full | 4 reruns resolved this session, see Part 2 |
| AUDIT_RECONCILE_2026-10-04.md | PARTIAL rows (B127/B128 31 rows) | 21 closed on disk (12 + 9), 10 residual named in the item receipts |
| B120 / B127 / B128 | full | receipts written |
| EXEC_PROVENANCE_AUDIT, LAYER_PROVENANCE_AUDIT, PROVENANCE_AUDIT_TOM | cited rows only (C14, C15, C19, C23, P06, A03) | CONFIRMED NO-SOURCE, feed B142-B144 |
| FORMULA_AUDIT, WIRING_MAINTENANCE_AUDIT, W3_KAPPA_REPORT, REVALIDATION_ACTIONS, TWO_CORES_READINESS | via reconcile rows only | UNVERIFIED beyond those rows |

## Part 2: why stuck (not CLOSED)
| item | blocker | last session left | smallest next action |
|---|---|---|---|
| T055 C1 funding_cvd_fade FAIL | was: run used 12 months of funding. Now FAIL on full funding (OOS -0.0453%) | 10-06 reruns not valid | none; closes under the T055 rule. File: T055_BT_RERUN_FULLFUNDING_2026-10-07.md |
| T055 C2 session_momentum FAIL | same | same | none; FAIL (Sharpe 0.0084, 1 positive OOS year) |
| CryptoCred fill bias | was code + rerun | fix committed, rerun pending | done: all FAIL. UNVERIFIED removed |
| Tom core BT | was disk path + merge | PC run unfinished | done: TOM_CORE_BT_RERUN_2026-10-06.md; open: why live rule 19 signals -> 0 |
| 5 NO-SOURCE items | operator decision (keep flagged) | review never scheduled | separate remove-or-replace session; rows B117, B118, B142, B143, B144 (B116 closed 10-06) |
| B120 | operator (W3-5) + doc work | filing only | W3-5 ruling; Sonnet doc pass for the rest |
| B127 | Java test + doc reclass (RA-W4-A11) | filing only | write SetupCandidatesBuilder test: grossRR < 1.5 candidate kept |
| B128 | Java tests, DSR spec, scheduler, operator decisions | filing only | see receipt table |
| CLOUD_INBOX note 1 | none | OPEN | DONE on disk; Cloud removes at next boot |
| CLOUD_INBOX note 2 | doc task 1 | OPEN | operator: supersede or reconstruct TWO_CORES_FIX_PASS_2026-10-02.md |

## Operator decisions
- B120 W3-5 | W3_BLIND_PACKET_2026-10-01.md:14 | Does DATA-PLUMBING mean "no trading meaning" or "no Tom idea"? (parked)
- CLOUD_INBOX note 2 task 1 | system/CLOUD_INBOX.md | Mark TWO_CORES_FIX_PASS_2026-10-02.md SUPERSEDED by the merged PRs, or reconstruct it from git history?
- B127 RA-W4-A11 | PROVENANCE_AUDIT_TOM.md row A11 | Reclassify the gross 1.5 R:R advisory flag to CONCEPT-ONLY?
- B128 TC-W1-6 | live_layers.py:122 | Enable classify_msb(filter_range_noise=True) in the live _cc_layer? (default stays False)
- B128 M29-11 | execution/auto_trader.py:75-78 | Should rsi:cross map side by level, not by direction?
- B128 M29-14/15 | auto_trader.py:311,320 | Rename the t_close key, or accept the documented meaning?
- F:\MTS\data\tom_snapshots_smoke | F: | Archive the 2026-09-01 smoke output?
- Research branch | mts-research 7aa01cd | Push the research commits (4c74cd7, 2aa75cc, b3dbe74, merge 5334975, 7aa01cd) to origin?

## Fixes made (all with tests)
- run_t055.load_data clips bars to funding coverage (failed before the fix, 26 pass).
- tom_bt_report.adapter_line prefers the promoted adapter files (crash fix; test added).
- Coverage tests: test_b127_fetch_archive_funding (6), test_b127_declutter_backups (3), test_b127_fabio_v3_isolation (2), test_b128_cc_range_noise_filter (3). Fail-first intent not satisfiable on already-correct code; kept as coverage tests, mutation coverage incomplete.
