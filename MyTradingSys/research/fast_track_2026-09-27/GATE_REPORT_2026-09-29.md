task | verdict | test | commit | note
096-audit-digest | PASS (2 small fixes) | scripts/worker/test_audit_digest.py 19/19 | d5d9b93 | fixed f['_id'] KeyError in render; added sort+cap in render_digest
095-audit-t0-checks | PASS | scripts/worker/test_audit_t0_checks.py 11/11 | 19448b3 | no changes
094-audit-rotation-backfill | PASS (2 small fixes) | scripts/worker/test_audit_rotation.py 21/21 | af3df38 | typo key AA6->A6; added NO FINDINGS to REPLY_FORMAT
093-tick-live-flagger | PASS (1 fix) | layers/tick/test_tick_flagger.py 19/19 | 004ed8e | replay checked wrong bounds_cache key (indicator,tf,side) so all readings skipped; now (tf,indicator)
092-tick-oi-extremes | PASS | layers/tick/test_tick_oi_extremes.py 13/13 | d7e64a8 | no changes; no backups needed (no prior file)
091-tick-extremes | PASS (1 fix) | layers/tick/test_tick_extremes.py 17/17 | 2740f40 | fixed gap_tiers to allow non-increasing values (ties) instead of strictly decreasing
0985-trade-costs | PASS | layers/positioning/test_trade_costs.py 9/9 | 6e2d0db | no changes; no backups needed (no prior file)
0986-funding-cvd-fade | PASS | layers/positioning/test_funding_cvd_fade.py 11/11 | fdb5407 | no changes; no backups needed (no prior file)
0987-session-momentum | PASS | layers/session/test_session_momentum.py 7/7 | d6c1956 | no changes; no backups needed (no prior file)
0988-turn-of-candle | HOLD | N/A | N/A | NUC reply cut off at 3072 tokens, no proposal; needs repack with larger OUTPUT_TOKENS
101-fabio-0ky-b | HOLD | N/A | N/A | waiting on chunk a (100 BLOCKED); could not verify quotes without full video
102-fabio-0jm | HOLD | N/A | N/A | BLOCKED: GPS line missing, proposal outside scope; needs repack
103-fabio-8cwk | HOLD | verify_extract_quotes.py | N/A | quote verification failed: 9 quotes missing/misphrased in transcript (R1,R2,R3,R4,R5,R6,R7,R8,R9)
104-fabio-faw-a | HOLD | N/A | N/A | BLOCKED: reply cut off at 2048 tokens; needs repack with larger OUTPUT_TOKENS
105-fabio-faw-b | HOLD | verify_extract_quotes.py | N/A | quote verification failed: 10 quotes missing/misphrased (R1-R10); also awaiting chunks 104+106
note | run_all_tests --quick: Step 5b fails only on missing turn_of_candle module (.new unpromoted, unrelated to these tasks)
bt_rsi | PASS (1 fix) | bt/test_bt_rsi.py 13/13 + test_bt_rsi_edge.py 11/11 | d30a57c | seed divided by count of nonzero moves instead of period (FORMULAS.md 1 known bug); 11 edge tests; existing tests did not catch it; Step 4 pytest now collects bt_rsi + prob_table tests
prob_table | PASS (2 fixes) | backtest/test_prob_table.py 12/12 + test_prob_table_edge.py 9/9 | 8614eaa | build_table now skips records with ts None; evaluate averaged log-loss over len(test) instead of scored records (halved loss when a test record was skipped); 9 edge tests
fabio_escalation (088) | PASS (2 fixes) | layers/fabio/test_fabio_escalation.py 4/4 + test_fabio_escalation_edge.py 10/10 | a408fa6 | relative import from .cc_structure (wrong package) -> absolute; a later record bar closing under the level was recorded as a second absorption so escalation never fired (now only first absorption recorded); empty bars raises ValueError by codebase convention
cc_retest / cc_structure test updates | NO PROMOTE | live test_cc_retest + test_cc_structure + test_cc_setups 20/20 | N/A | .new tests differ from live only by a loader header that imports nonexistent cc_*.py.new modules (fail with FileNotFoundError); cc modules already promoted; leave or delete the .new files
0989-turn-of-candle-r2 | PASS | layers/turn_of_candle/test_turn_of_candle.py 7/7 + test_turn_of_candle_edge.py 29/29 | 5392309 | fixed event detection logic (was checking next minute instead of current); 29 edge tests cover empty/single/boundaries/errors
extract_nuc_files | HOLD | N/A | N/A | needs spec-derived test
106-fabio-faw-c | HOLD | N/A | N/A | PARTIAL: only proposal was outside scope (extract_FawPrRUGNpk_3of3.md), not written; repack
108-fabio-lqv-b | HOLD | N/A | N/A | PARTIAL: only proposal outside scope (extract_LQvv5xgy_ik_second-half.md), not written; repack
109-fabio-sta | HOLD | verify_extract_quotes.py (scratch copy of inline reply) | N/A | NUC said DONE but gave no FILE block; inline extract fails 5/5 NO-TRANSCRIPT (GPS lacks transcript path?); repack or stage by hand
110-fabio-fzl | HOLD | N/A | N/A | PARTIAL: only proposal outside scope (extract_fZlNGWvd2Ko.md), not written; repack
111-fabio-jas | HOLD | verify_extract_quotes.py (scratch) | N/A | DONE but no FILE block; all 8 quotes NO-TRANSCRIPT; repack or stage by hand
formula_audit (audit/formula_audit.py.new) | HOLD | N/A | N/A | needs spec-derived test (no test_formula_audit.py, no NUC spec found)
bt_stats | HOLD | test_bt_stats.py | N/A | ImportError: cannot import wilson, bootstrap_mean_ci, etc.; .new file incomplete (only sharpe function, 103 bytes vs 3421 live)
