# MTS-2026-10-03-1444Z-CLI-BLD-tf4-execution-proven
surface: App (Claude Win App, Code mode; the ID says CLI because the dispatcher names every picked session CLI-BLD) | host: JIS-NB | account: none | model: claude-sonnet-5-5 as reported by the runtime (the prompt and row 1.6 asked for Opus) | role: BLD | branch: fast-track | branch_alias: none
predecessor: MTS-2026-10-03-1329Z-CLI-BLD-tf3-fabio-v3-live | lanes: none (no subagents, no workers)
started: 2026-10-03 (first clock read 15:27Z; the 14:44Z in the ID is the prompt compose time) | ended: 2026-10-03 15:45Z | status: closed | commits: the commit history --grep "MTS-Session: MTS-2026-10-03-1444Z-CLI-BLD-tf4-execution-proven" (the audit file also sits in 9d43d03, see T5)
handoff: supervisor inbox via this record. TF5 (row 1.7) and TF6 (row 1.8) are now pickable (blocker 1.6 LANDED). Before composing TF5: operator Ruling 3 (MEASURED values for CONCEPT-ONLY rows) is still open; the audit flags E1b, E2, E4 as MEASURE.

## Scope
BUILD_PIPELINE.md row 1.6 (TF4): execution provenance audit, Tom + Fabio, read-only. Output MyTradingSys/research/EXEC_PROVENANCE_AUDIT.md.
No code, config, plan, HALT or trade touched; no process stopped or restarted. Writes: research/EXEC_PROVENANCE_AUDIT.md, runtime/BUILD_PIPELINE.md row 1.6,
system/03_FILE_INDEX.md (2 rows), this record. Nothing under execution/ or layers/alerts/ (one-session-per-area rule: proposals only).

## T0 PASS
- Read: TOM_FABIO_REVIEW (s1.2, s3), PROVENANCE_AUDIT_TOM, FABIO_PROVENANCE_AUDIT, OPERATOR_RULINGS, CLAUDE.md, auto_trader.py, position_manager.py, new_plan.py, executor.py (entry wait), plan_compiler.py (size, stop, targets), auto_trader_config.json, SetupCandidatesBuilder.java and math_object_builder.py (stop/target/runner), start-trading-day.ps1 (card), runner_min_distance.json and its R2 session record, FABIO_V3_SPEC s5/s7, 5 Tom v2 extracts, EXTRACTION_ROUND2 s5.1, SUPERVISOR_LOG origin lines.
- Pipeline row: BUILD_PIPELINE.md:45. Effective live config merged AT defaults + CFG, run this session.
## T1 PASS
- Deliverable written: 24 table rows (E1-E9 for Tom and Fabio, E10 one sub-row per v2 extract), H4 cross-check, H5 ranked fixes, H6 not audited, Appendix B evidence, Appendix A 52 quotes.
## T2 PASS
- verify_extract_quotes.py: 5 v2 extracts PASS (21 + 13 + 10 + 8 + 7 = 59 anchors OK); EXEC_PROVENANCE_AUDIT.md PASS (52 OK, 0 problems). Table/appendix cross-check: every cited Qnn in the appendix, none unused, short locations match.
- pick_task.parse_pipeline + skip_reason on the edited pipeline (no queue write): 1.6 LANDED; 1.7 and 1.8 pickable.
- Spot-check of the review: E1 (5 of 6 no_fill), E2 (40 min time exit), runner_skipped (3 + 2) all match disk. Its E2 wording "closes before target" is true but the target was not reached later (n=1).
## T3 PASS
- No quote failed verify; none substituted; none dropped as NO-SOURCE for a failed check. Rows with no quote say NO-SOURCE with the search pattern and counts (Appendix B.4).
## T4 PASS
- Row 1.6 set LANDED with a CLOSED note; file index rows added; this record; commit on fast-track, prefix "TF4: ".
## T5 MISSED (deviations)
1. Model: the runtime reports Sonnet 5.5; the prompt and row 1.6 say Opus.
2. Session ID carries CLI and the compose time 14:44Z; the surface is the App and the first clock read was 15:27Z. The record was created after T0 had started, not at boot.
3. H1-H6 read as section labels: H1 is the title, H2-H6 are `##` headings with those labels; two extra sections, Appendix B (evidence) and Appendix A (quotes, the gate input; listed after B).
4. The table has 24 rows, not 10: sub-rows E1a/E1b and E8a/E8b where one parameter has two separately sourced values, and a -T/-F row per parameter; no E5-F row (no Fabio runner).
5. The task's E1-E10 differ from the review's E1-E8 in section 1.2; the id map is in the audit header (review E4, E6-E8 are not execution parameters).
6. Not disk-only: ran live-code functions in memory (tom_signal, runner_split, plan_compiler.compile_plan; nothing written) and made 3 public ticker reads (test.deribit.com, fapi.binance.com; no credentials, no orders) for the basis in B.2.
7. Review figures are out of date: 9 Tom attempts to 15:27Z (review: 6), runner_skipped 3 size + 5 no node (review: 3 + 2). Both versions are in the audit.
8. Full offline gate (run_all_tests.py) not run: docs-only commit; the gate used was the quote verifier plus the pipeline parse.
9. Another session's commit 9d43d03 swept the in-progress audit file (about 15:40Z, before four small wording and cite edits) into its own commit. History not touched; the final text is in the TF4 commit.
10. Extract defect found, not fixed (read-only): extracts/v2/tom/kXhIAug0Gh8_v2.md:65 labels trade 1 "entered ... before" proof; rows 6-7 and the transcript say proof first.
11. TF5 row 1.7 cites Ruling 1 for testnet size 20; the audit says Ruling 2. Row 1.7 not edited (not this session's row).
12. Not measured: cause of the 5 "no RUNNER_TARGET" attempts, the Deribit testnet book, queue position; Java not executed. E1 cause is stated as consistent with the data, not established.
13. Quote ids Q38, Q39 do not exist (labels are stable, not a count). Position L-lim-1003-1357 was open during the audit and was not touched (time exit due about 15:57Z).
