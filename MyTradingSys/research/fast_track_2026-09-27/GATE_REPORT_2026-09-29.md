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
note | run_all_tests --quick: Step 5b fails only on missing turn_of_candle module (.new unpromoted, unrelated to these tasks)
