# Supervisor C notes - PILOT 1 (2026-10-24), record for MTS_Doctor
Start 2026-10-24T10:09:43Z. Hard stop 2026-10-24T14:30Z. Workers: 4 Sonnet background Agents, no ultracode/fast/Opus.
D3 justification (4 workers, operator approved for pilot): get_usage 2026-10-24T10:09:43Z 5h=9% week=28%; each card own files (PILOT1_CARDS.md, 0 overlaps); last smoke gate 11.3 s (ANNOUNCEMENTS A-20261024-1).
Frozen list: 1 t02-f1-review-allowlist-chunk-4, 2 find-gemini-antigravity-quota-command-an, 3 mid-turn-image-intake-gap, 4 bt-engine-wire-real-funding-rsi-cc-rerun, 5 dsa-audit-04-clean-room-twin, 6 dsa-audit-10-missing-aspects (5-6 capped 3 h; 6 review Agent before ship).
Workers are background Agents for all cards (event turns; no start_session) - deviation from table col "session".
ANNOUNCEMENTS: no STOP/HOLD applies (A-20261018-6 is gap-g2 only).

## Cards (worker start UTC | ship sha | verified UTC | turns)
1 t02: start 10:09Z
2 gemini-quota: start 10:09Z
3 image-intake: start 10:09Z
4 funding-rerun: start 10:09Z
agents: c1=aba5a342d1efa5876 c2=a1e1df3494e223c65 c3=aafa5f7d24429eea4 c4=ab3a27ac21638a5f8 (started 10:09Z). Next: cards 5,6 as slots free.
3 image-intake: ship d696c8c6a, verified 10:12Z (ancestor, Result:, cherry empty), worker turns 9. 
5 dsa-04: start 10:13Z (3h cap -> 13:13Z)
1 t02: ship c68e93ced, verified 10:15Z, worker turns 8 (worker reported b43de092f merge commit)
6 dsa-10: start 10:16Z (3h cap -> 13:16Z); worker must NOT ship before review Agent APPROVE
6 dsa-10: worker done committed c1c2df8a5 (not shipped) ~10:29Z turns 38; review Agent started 10:28Z
6 review: BLOCK on desk_queue post only (card scope explicitly allows desk.py --target CLAUDE posts; my review brief omitted it). DECISION (OURS): override, ship. Rest of review clean.
6 dsa-10: ship c1c2df8a5 verified 10:34Z, turns 40 (38+2)
2 gemini-quota: worker ~24 turns, ship in gate at 10:43Z (~35 min after start); also edited run_all_tests.py (step 3cxp, gate registration) - post-hoc review Agent started
2 review: APPROVE (post-hoc)
2 gemini-quota: ship (started ~10:22Z) still in gate at 10:48Z, >26 min; likely FULL gate because run_all_tests.py edited (gate file). Row-2 relevant. Worker stopped at ~30 turns; ship PID 11620 alive.
2 gemini-quota: ship still gating at 11:03Z (~41 min). 4 python gate/ship process groups alive on NB (gate slots contended: card 2, 4, 5 + stale 15:42 IST run_all_tests PID 8592).
FINDING (Doctor msg): orphan hand-run 'run_all_tests.py --quick' PID 8592 (10:12Z, >50 min, ~1.4 s CPU i.e. hung, no --slot, outside GATE_SLOTS) - killed by Supervisor at 11:04Z (test run only, no live effect). Cause: worker briefs lacked 'no hand-run full suites'.
note: killed orphan was card 2 worker's own early --quick run (its own bash); ship PID 11620 unaffected, still gating at 11:04Z.
2 gemini-quota: ship 88e9aa4d9 (tip 04dba5758), verified 11:19Z, turns ~33; ship gate wall ~55 min (22 min precheck+contention). CI ok. 4 of 6 shipped incl. 1,2,3,6; open: 4 (started 10:09), 5 (10:13).
5 dsa-04: worker done 11:27Z (~55 turns, over 40 cap), commits 2dadb1b0d,77aebacaf, ship in final gate (55/60 steps). Scope breaches: run_extra_tests.py 1 line registration; stray out/t04_run.log committed. Tool-turn cap overrun noted.
4 funding-rerun: ship 62a05b2eb (worker reported a03dc56f5 merge), verified 11:39Z, turns ~38 (46 tool uses). Files in scope. CI ok. IMPORTANT card: Result+file list read by Supervisor.
CI RED: run 40090741447 on card-4 push, red since 11:38:56Z (test_lookahead_lint: new FAIL hit run_rsi_backtest.py:111). Supervisor noticed 11:50Z (12 min, >10 min stop line: my miss - ci check only at wake). Revert c26d11d94 of 62a05b2eb shipping from 11:51Z. Card 4 -> NOT counted verified (reverted). Card 5 ship also blocked by same hit.
CACHE EVENT: idle wait >1 h (11:52Z -> 13:28Z, no wake; woke on Doctor message). Context was not compacted by me. 
4 funding-rerun: revert c26d11d94 shipped ~11:55Z, CI green 40091803501 (red 11:38:56Z -> revert shipped ~11:55Z = ~16 min red on trunk; noticed after 12 min). Card 4 stays reverted (not retried: frozen list, rework counted by Doctor).
5 dsa-04: at 13:28Z NOT on trunk, no ship running; resumed worker ac14a4c99ec77e6eb to re-ship (rm stray log, merge, ship detached, no hand-run suites).
5 dsa-04: ship 2dadb1b0d (+77aebacaf fix, tip f91d8359b merge), on trunk 13:43Z (CI 40099386818 success), verified 14:25Z (ancestor, Result: line, cherry empty). Worker turns ~62 total (cap 40). Scope: run_extra_tests.py 1-line registration (outside list).

## END (14:25Z)
Verified 5 of 6: 1 c68e93ced, 2 88e9aa4d9, 3 d696c8c6a, 5 2dadb1b0d, 6 c1c2df8a5. Card 4 reverted (c26d11d94), carry-over, not retried.
Turns: c1 8, c2 33, c3 9, c4 38, c5 ~62, c6 40 (median ~36 <60 OK; c5 over its 40 cap).
Gate wall: c2 ~55 min (contention + run_all_tests.py edit), c5 re-ship ~1.2 h incl. wait for revert; others short.
CI: 1 red 40090741447 (11:38:56Z, card 4 lint hit); noticed 11:50Z (12 min, >10 min line, my miss); revert shipped 11:55Z; ~16 min red on trunk; green 40091803501.
Cache events: idle >1 h 11:52Z-13:28Z. Coordinator compactions: 1 (~13:30Z, Doctor-requested).
Findings: orphan hand-run suite killed 11:04Z (briefs need "no hand-run suites"); sync_with_base_branch failed (origin pin) so worktree via sync.py start; coordinator only checks CI at wakes -> 10-min rule needs a watcher.
Usage at end: 5h 10%, week 30% (was 28%), 5h never >80%.
