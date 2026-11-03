# Unblock MTS week 11-04 to 11-10 (coordinator login C, JIS-NB). Overwrite each session.

| Move | State | sha | Blocked on |
|---|---|---|---|
| 1 S1 sign | signed 11-04 (d-s1-defaults-1104), D7 Now moved, GO_LIVE_BAR revision block written | 11c2703d + this ship | Items 1-6 of the bar still read old text; block says it wins |
| 2 S3 runs | PASS guard already built (test_pass_needs_verdict.py, 12 green; board line stale). lc-validation ready; rsi-deep chain noted; broadcast b-934a3f to login B | cc7a93e0 | B ack with VERDICTS row; rsi-deep-prereg then rsi-deep-engine must ship before rsi-deep-run-dev |
| 3 S2 cards | M1 state-code backfill was already on trunk (41 tests green), card closed. M4 s2-uptime-heartbeat-jis-nb built, 7 tests, on trunk (git cherry empty) | b9cc5d3b8 | card still refined (needs Lab_Guy stamp before tasks.py done); wire `uptime_heartbeat.py beat` + check first beat after deploy |
| 4 Declutter | 20 stale claims released (4 left, all new); 1157 operator-question rows archived to ~/.claude/operator_questions_archive_2026-11-04.jsonl, 0 pending; Home rebuild not yet taken | cc7a93e0 | mts-home-rebuild-1103: take after 12:00Z 11-05 if B has not shipped, then republish mts_home |
| 5 Freeze | held; no new pages, docs or tools | - | - |
