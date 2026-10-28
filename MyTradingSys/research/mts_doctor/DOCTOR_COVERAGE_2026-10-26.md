# Doctor coverage of the 10-23..10-25 fixes (card doctor-checklist)

Sources: REPORT_2026-10-23/24/25.md, CI_RED_AND_FLOW_REVIEW_2026-10-25.md, `git log origin/fast-track --since=2026-10-23` (workflow and tooling fixes; feature and research commits are not fixes). Check names are the `mts_doctor.py` checklist.
Rule (A-20261024-1): a new check needs a measured regression; at most 3, only for a fix with check "none". Added here: 2 (STALE-CLAIMS, SCRATCH-TRACKED).

| Commit | Fix | Check | Decision |
|---|---|---|---|
| 94da8e585 | mixed role md + card json ship runs docs checks (CI red 5f12bc06c) | SIZE-HEADROOM (role budgets) | covered; the budget part is caught before it goes red |
| a702fafd1 | ship waits for CI of its own sha, prints CI RED | CI-REVERT | covered |
| 33490efb5 | ci.yml runs on task-card pushes | CI-REVERT | covered (a bad card now shows as red) |
| d65c2b35f, 7b2e84c45, e4e298e1d, c621676a2, 2a30cf473 | reverts after CI red | CI-REVERT | covered (red-to-green minutes) |
| 387ee31e9, dec473ccb | CLAUDE.md back under cap | SIZE-HEADROOM | covered |
| 2c9bbaf9c, 81d9f1617 | Lead role, supervisor.md budget | SIZE-HEADROOM | covered |
| e89ffc3c4 | ship_wall row, SHIP SLOW line | SHIP-TIME | covered |
| 092925c0c, 7b168e5fd, f7ccee4c6 | ship under 2 min, 60 s test deadline, --fix-ci fast gate | SHIP-TIME | covered |
| a6b7f53bd, fb139c57c | smoke gate budget (10-24) | SHIP-TIME | covered |
| 43d3bfc8f | hooks removed (10-24) | HOOK-REG | covered |
| 086a1b257 | trunk_lag counts the session folder | HOOK-REG (main checkout behind) | covered |
| f0fa135b7, 157c0572f, 059cc4f95 | c_drive_guard, tidy of shipped trees | DISK | covered |
| d71ea6da2 | context_gap measure | CONTEXT-GAP | covered |
| 5ffbd2337 | WAITING-ON-OPERATOR check | WAITING-ON-OPERATOR | covered |
| 8a2ca07bc | broadcast ack guard | BROADCAST | covered |
| b565b0a1d, 36300da1f | live mirror follows the owner | none | no measured regression; mirror refuses without owner (`live_mirror.py brief`) |
| bd0fcf941 | new look-ahead FAIL blocks ship | none | gate step 3la and preship rule are the check; CI-REVERT sees a miss |
| 5d9748041 | supervisor watchcheck NO WAKE SOURCE | none | exits 4 itself; one-off, no repeat measured |
| a1aafdb9e, 5a58dad44 | coordinator stalls, Lead replaces Doctor | none | design change, no metric |
| ce3b392f0, 73e4d30e9, 6102af295 | behavior eval scenario fixed after rename | none | CI-REVERT caught it; no new check |
| 9135c745c, c8aa7d9c8 | tasks.py stale-work stop | none | owned by `tasks.py lint` (CARD finding) |
| 92bd04e27 | leaked test card shipped.json removed | none | CARD lint covers card shape; one case |
| 2e4210942, a3f7dd0a8, 79f288d88 | tests that failed on NUC git / UNC / spawn count | none | one-offs found by CI, CI-REVERT sees them |
| 94a64d04a, ec2fa173e, bc50937c8, f02e34063, 70e615927 | test files registered in the gate (7 commits in 3 days) | none | the preship rule "test file not in the gate" blocks it before commit (test_gate_discovery_b150); a doctor check would repeat it |
| (reports: 18, 18, 22 stale claims) | stale claims counted in Part 2 only | **STALE-CLAIMS (new)** | measured 3 days running, never in the HEALTH line; WARN over 5 claims older than 24 h |
| f97ecc125, 4054f6f1f | PILOT3 scratch ship logs removed from the public repo | **SCRATCH-TRACKED (new)** | measured regression; WARN on tracked `_scratch*` or `*ship.log`. Fires today on `runtime_data/_scratch_*` (legacy, tracked): git rm is a follow-up card |
| b68a73130, 9d26d7eb9, fc950331b | runner tree refresh, machine rename | none | no regression measured |

Decisions (OURS): STALE-CLAIMS limit 5 (claims block a task for every login; reports show 18-22). SCRATCH-TRACKED pattern is narrow so it does not flag data files.
