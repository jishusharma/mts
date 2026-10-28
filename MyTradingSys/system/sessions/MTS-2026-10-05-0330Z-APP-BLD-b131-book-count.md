# MTS-2026-10-05-0330Z-APP-BLD-b131-book-count

surface:      APP (Claude Code Win App)
host:         JIS-NB
account:      pro
model:        Sonnet 5.5
role:         BLD
branch:       fast-track
started_utc:  2026-10-05T03:30Z
ended_utc:    2026-10-05T04:00Z
status:       returned
commits:      4f9290e

task:         B131 fix shape A (drop book_imbalance from proof count)
result:       SetupCandidatesBuilder.java L575-580 removed; six remaining
              slots (wick, absorption, finished_auction, delta_flip,
              volume_spike, cvd). Two new tests in
              SetupCandidatesBuilderRulesTest.java. Three CountSignalsD4Test
              tests flipped to expect the new behavior. mvn -q test 130 run,
              0 failures. B131 CLOSED.
deviations:   CountSignalsD4Test.java edited (not in the brief); rule table
              now 21 tests not 16; ps1 thresholds L225/L227/L578 not checked
              (filed as B135); allshorts diag not re-run (filed as B135);
              no session record written by the session.
cost:         not captured.
recorded_by:  
MTS-2026-10-04-1325Z-DSA-COO
# END
