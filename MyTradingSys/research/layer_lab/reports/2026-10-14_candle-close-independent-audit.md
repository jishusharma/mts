# Candle-close second-pass audit

FIX-FIRST: eight research/verification findings; no new performance trial.

Full findings, file:line evidence and reproducible checks: ../candle_close_2026-10-14/INDEPENDENT_AUDIT.md. Structured outputs: AUDIT_REPRODUCTIONS.json. Pre-run correction direction: NEXT_EXPERIMENT.md.

Main findings: phase labels do not establish bounded ranges/local trends; no joint phase-policy test or subgroup inference; first-event versus all-nearby control mismatch; one-hour price outcome insufficient for bottom/strategy claims; verifier omits phase/null/CI reconstruction; application ImportError can exit 0 with eight skipped tests. Synthetic rising/choppy counterexample and injected-import subprocess reproduce two issues. Existing raw tables have seven positive cost-screen phase cells, six under N=100 and none validated; pooled negatives do not settle phase applicability.

Scope checked: study.py, test_study.py, verify_result.py, METHOD.md, REPORT.md, DATA_AMENDMENT.md, CYCLE_DESIGN.md, complete phase/trend/4h tables, verification.json, trial log, initial ship log and current CI dependency declaration. No new raw price/holdout read. This audit is a second-pass review, not an independent-model replication.

Follow-up cards: candle-close-test-import-guard (ready); candle-close-phase-encounter-design (ready). Historical timestamp/read-only-array and workflow-push failures were fixed; current import/coverage issue remains open.
