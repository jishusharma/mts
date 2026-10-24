# Pilot report: super sessions 1b and 2 (MTS_Doctor, 2026-10-25 ~20:50Z)

Plan and pass rows: `PILOT_super_session_2026-10-24.md`. Sources: `PILOT1B_NOTES.md`, `system/handover/SUPERVISOR_C.md`, git cherry, gate times in those notes, `get_usage`.

## Score
| Row | Pass line | Pilot 1b (4 workers, 14:28-18:30Z) | Pilot 2 (6 workers, 18:48Z-, ended early 20:50Z) |
|---|---|---|---|
| 1 Cards shipped | 5 of 6 | PASS 7 shipped (W1, W1b, R1, R2, S1, H1, LAST) | PASS 13 shipped, cherry 0 each |
| 2 Gate median < 2 min | median | FAIL: registering a test in run_extra_tests.py forces the FULL gate; 3 parallel gates hit 100% CPU; one ship > 50 min | NEAR: 35 s-3m23 typical, median ~2.5 min; Argon ~20 min (registration), T05 29 min (push race) |
| 3 CI | <= 1 red | PASS 0 red | PASS 0 red, 0 reverts |
| 4 Rework | 0 | FAIL: 2 workers shared the coordinator tree; 2 gate kills; R1 test not registered | 2 lint false positives cost a failed ship each (fixed: lookahead lint card shipped) |
| 5 Cost | 5 h < 80% | PASS | PASS: 5 h 13% -> 42%; week 34% -> 38% (whole fleet incl. sim-v2, Fable, Doctor) |
| 6 Worker turns median < 60 | median | PASS | PASS median ~20; 3 over the 40 cap (T07 55, T05 41, T09 40) |
| 7 Operator turns 0 | 0 | PASS | FAIL: rotation needed the operator (Remote Control off; /compact by hand) |
| 8 Machine slow | none reported | FAIL in effect (100% CPU on parallel full gates) | PASS after the one-ship-at-a-time rule |

## What we learned (each has a fix or card)
1. **Card supply is the bottleneck, not workers.** Pilot 2 ran out of ready cards at 20:35Z, two hours early; 6 workers ran only ~20 min, then 1-3. Three cards were already done on trunk (stale). Fix: a refine pass before each run (10 p1 cards are raw today).
2. **One ship at a time** works: gates fell from 50+ min to ~2.5 min median. Keep it.
3. **Test registration forces the full gate** (20-50 min). Card `registering-a-test-in-scripts-dev-run-ex` (raise to p1).
4. **Rotation:** operator /compact works (232K -> 93K, 250K -> 97K). `clear_session` is refused while any wake, ship or Remote Control is live (3 refusals). Use compact; keep clear for idle sessions.
5. **YouTube on Claude fails** (HTTP 429, 0 of 3). Rule now: all YouTube goes to Gemini on the NUC.
6. **NUC claim push hangs** (`gemini_queue` claim, 30 min, killed). Overnight jobs use the no-claim runner; card `gemini-queue-claim-release-push-hangs-fo` (raise to p1).
7. Review stamp A-20261018-5 blocks `tasks.py done` for T05/T06/T07/T09: work is on trunk, cards stay open.

## Findings with live impact (from pilot 2 audits)
- **T09-F1: live volume_fvg trades the opposite side** (0 of 24 agree). Testnet only, no money at risk, but every volume_fvg trade is wrong.
- T09-F2: live uses one 1%/2%/8-bar bracket for all layers; none was tested with it.
- T09-F3: live RSI trades events no test covered.
- T05: with a fair (distance-matched) random-line control, all 12 LC1 level families DROP; 8 published KEEPs do not survive.
- T09-F5: funding/CVD fade 1h, DEV: +0.050 R non-overlapping, CI crosses 0: not an edge yet.

## Next pilot
Pilot 3 (Haiku on mechanical cards) only after: (a) 12+ ready cards refined, (b) the registration gate fix. Same pass rows, plus weekly % per verified card.
