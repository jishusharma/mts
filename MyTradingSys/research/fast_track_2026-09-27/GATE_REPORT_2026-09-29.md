task | verdict | test | commit | note
096-audit-digest | PASS (2 small fixes) | scripts/worker/test_audit_digest.py 19/19 | d5d9b93 | fixed f['_id'] KeyError in render; added sort+cap in render_digest
095-audit-t0-checks | PASS | scripts/worker/test_audit_t0_checks.py 11/11 | 19448b3 | no changes
094-audit-rotation-backfill | PASS (2 small fixes) | scripts/worker/test_audit_rotation.py 21/21 | af3df38 | typo key AA6->A6; added NO FINDINGS to REPLY_FORMAT
093-tick-live-flagger | PASS (1 fix) | layers/tick/test_tick_flagger.py 19/19 | 004ed8e | replay checked wrong bounds_cache key (indicator,tf,side) so all readings skipped; now (tf,indicator)
092-tick-oi-extremes | PASS | layers/tick/test_tick_oi_extremes.py 13/13 | d7e64a8 | no changes; no backups needed (no prior file)
note | run_all_tests --quick: only Step 5b fails, on missing turn_of_candle module (.new unpromoted, unrelated to these tasks)
