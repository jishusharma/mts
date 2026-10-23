# End-to-end test checklist, 2026-10-22

Goal: the super session decides, and the work then runs to the end in the background with no operator clicks. The Supervisor plans it, Builders build it, the Codex CLI worker runs lab cards, every result is shipped and checked, and a hand-over is appended.
Pass = every row PASS, 0 operator clicks, and the whole flow ends inside 60 minutes.

## A. Offline checks (no live sessions)
| # | Check | How | Pass when |
|---|---|---|---|
| A1 | Full gate | `sync.py ship` | ALL TESTS PASSED, CI green |
| A2 | Every hook runs, exits 0 and stays within budget | `hook_bench.py -n 3` | tool call ≤ 0.5 s, prompt ≤ 0.8 s, stop ≤ 1.0 s |
| A3 | Hooks on disk = hooks on trunk | `mts_doctor.py` hook_drift row | no drift |
| A4 | Role loader: a file path never scores; a Supervisor brief gets no fallback role (8b4ea32a) | `test_role_roster.py` | pass |
| A5 | Codex tick survives a merge left in progress (d15c4e55) | `test_codex_run.py` | pass |
| A6 | Lab lane_state clash resolves itself and the lab merges trunk before shipping (today) | `test_codex_run.py` | pass |
| A7 | NEXT_SESSION.md may not drop blocks | `tests/docs/test_next_session_keeps_blocks.py` | pass |
| A8 | Ship gate on a 339-file diff (020f3c45) | `run_all_tests` env-limit test | pass |
| A9 | shot.py finds archived cards (3a9d8faa) | its test | pass |
| A10 | Preship catches errors at edit and at commit (ec426fd0) | its tests, plus one live edit of a `system/*.md` in C | rule fires at edit |
| A11 | prereq hook puts pre-run to-dos in the queue, not in front of the operator (86d3cec0) | its tests | pass |
| A12 | model_guard blocks a wrong-model spawn | its tests | pass |

## B. Codex CLI worker (no Claude session)
| # | Check | Pass when |
|---|---|---|
| B1 | `codex_run.py status` | no STALLED, no unshipped commit, lane up |
| B2 | `codex_run.py tick` runs one real card | one row in runs.jsonl, outcome DONE or BLOCKED with a report |
| B3 | The result ships to trunk on its own | the lab commit is on origin/fast-track, no lab.hold |
| B4 | Settings used match the card | model_used = card model, effort_used = card effort |
| B5 | A second tick right after | clean refresh, no merge error |

## C. Live flow (super session to Supervisor to workers)
| # | Check | Pass when |
|---|---|---|
| C1 | This session files one small real card and starts a Supervisor with a brief | Supervisor session starts and no card waits on a click |
| C2 | Supervisor boot | role banner = Supervisor; supervisor.py plan printed; right transit time (UTC now ± 2 min) |
| C3 | Supervisor starts a Builder with a brief | Builder banner = Builder (not Thinker or any fallback) |
| C4 | Supervisor runs the Codex tick if CODEX cards are ready | `RUN codex_run.py tick` acted on, B2 to B4 hold |
| C5 | Builder ships through `sync.py ship` | fail-first test, ALL TESTS PASSED, on trunk |
| C6 | Supervisor rechecks the Builder's claims (Haiku recheck), with numbers re-run, not repeated | its transcript shows the recheck command and its output |
| C7 | Hand-over | one new `## ` block appended to NEXT_SESSION.md, no block dropped (A7 guard) |
| C8 | Hooks seen live | turn_meter rows written; Stop guard and prereq guard ran without blocking; no hook timeout lines |
| C9 | Operator clicks | 0 |
| C10 | Wall time | card filed to hand-over shipped ≤ 60 min |

## Result, 2026-10-22 (run 2 passed)
- A: PASS. 460 tests pass. All 20 hooks are timed and within budget (tool call 0.23 s, prompt 0.11 s, stop 0.13 s). Hook drift in the main checkout was fixed by moving it to trunk; its old state is saved on the local branch `jis-nuc/main-checkout-salvage-20261022`.
- B: PASS after 4 fixes:
  - a stale MERGE_HEAD was left behind (d15c4e55)
  - lane_state.json clashed with trunk (37d3f029)
  - the lab marked itself down on a stale heartbeat (ship after 37d3f029)
  - the lab's own ship was refused by the 10-minute guard (65c6fd31)

  lab-formula-spec-text then ran 373 s on gpt-6-luna/medium, the model and effort the card asks for. It ended BLOCKED, with a report, and shipped. The 5 cards that had been moved off the lane are back on CODEX.
- C, run 1: FAIL.
  - The Supervisor's start_session calls for its Builders waited on an operator approval. The app asks when a session that another session started starts a session.
  - Its worktree was cut from the stale `main` (2026-10-02), so it ran 20-day-old hooks.
  - Fixed: model_guard now denies a start_session from a started session and points to background Agents (59882977), and origin/HEAD now points to fast-track.
- C, run 2: PASS. 0 clicks, 0 approvals, 12.7 min. 2 cards shipped (4d7af480+ecd83de0, ab82fc75). The Supervisor rechecked both itself by rerunning the tests. The hand-over only appended (no block dropped). The transit line was right (17:20Z = the 5 h reset minus 20 min, not a bug). The card 2 test fails on the old bench (3 failed), checked by the super session.

## Still open
- The ship guard needed `--again` twice in run 2: once for a Builder, and once because the Supervisor's empty ship counted as a ship.
- A Builder edited `run_extra_tests.py`, which is outside its card's scope (the gate needs every new test registered). The card template should list that file in scope.
- 3 published pages are stale (mts_control_room, mts_layer_map, mts_home).
