# Pilot 1b notes (coordinator, login C, JIS-NB, started 14:28Z, stop 18:30Z)

## Frozen card list (14:40Z) - max 4 Sonnet workers, one card each, disjoint files
| Id | Card | Worker | Files | State |
|---|---|---|---|---|
| W1 | wavetrend-data-inference (~30 turns) | Sonnet Agent | research/wavetrend_2026-10-17/ (new manifest + inference files), backtest/research_kit.py | needs Lab_Guy ACCEPT |
| R1 | rsi-deep-econ-floor (~12 turns) then R2 rsi-deep-depth-map (serial, same folder) | Sonnet Agent | research/rsi_deep_buy_2026-10-19/ econ_floor.py, ECON_FLOOR.csv, ECON_FLOOR.md | needs Lab_Guy ACCEPT |
| S1 | sim-dashboard-v1 (new, ~20 turns) | Sonnet Agent | research/sim_desk/artifact/ only (not desk.py, studies/) | ready |
| H1 | habib-holdout-prereg-draft (new, ~8 turns) | Sonnet Agent | research/habib_plan_imbalance_2026-10-20/PRE_REG_HABIB_PLANS.md | ready |
| LAST | tasks.py done x4 (Haiku Agent, serial): confluence-s0-registry, confluence-s1-context-counts, wavetrend-audit-c1-disposition, malkan-gfs-btc-htf-prereg | Haiku | tasks/*.json, LAYERS.md | after verify on trunk |
Not mine: bt-engine-wire-real-funding-rsi-cc-rerun, Krown K1 GPT audit (yt-burn), Krown S2 (Doctor).

## Decisions
- 14:30Z DECISION (OURS): gate fix (card ship-gate-let-a-new-look-ahead-fail-reac, claim JIS-NB 1h old) not on origin/fast-track at boot; background poller waits; no worker starts before it lands.
- 14:35Z new cards S1/H1 created via tasks.py new+fill; B-SHARED rewrite of argon-blind-read-7-frames.json restored.
- S1 card worker field = session (tasks.py rule); I still run it as an Agent per the brief.

## Reports sent to Doctor
(none yet)

## Findings
- 14:50Z FINDING: S1 and H1 workers were started as Agents in the coordinator's tree (no own worktree); risk: one ship carries the other's files (counts toward row 4). Rule from Doctor 14:58Z: commit only own paths, ship one at a time, W1/R1 get their own worktree (`isolation: worktree`).
- 14:50Z gate poller #1 timed out at 20 min (no gate commit); poller #2 running.
- 15:08Z gate fix bd0fcf941 on trunk. W1 was already shipped by another host (4463a42e7); W1b started for manifest json.
- 15:21Z FINDING: editing scripts/dev/run_extra_tests.py to register a new test makes sync.py ship run mode=FULL gate (shards 570-690 s, 25+ min with 3 ships at once). S1 and W1b gates killed at 15 min by workers; H1 ship (tree) ran on.
- 15:21Z Lab_Guy ACCEPT R1 (second pass); R1 worker started, own worktree.
- 15:25Z ROW-2 EVIDENCE (Doctor rule): (1) registering a new test in run_extra_tests.py forces the FULL gate (S1, W1b); (2) parallel full gates saturate JIS-NB (100% CPU, 19 python procs, shards 570-690 s). New rule: ONE ship at a time; queue behind `git cherry` empty; no hand-kills (report >30 min). W1b and S1 re-ships wait for H1 ship to land. Doctor cards the run_extra_tests trigger (not me).
- 15:55Z R1 shipped 073019dfa but test_econ_floor.py is NOT registered in run_extra_tests (CI does not run it). Fix rides with the W1b re-ship (same full gate). Queue: H1+S1+notes (running) -> W1b+econ_floor registration -> LAST (Haiku, 4 tasks.py done).
- 15:55Z Workers: S1 a51fee2549362525e (done, rides in H1 ship), H1 a222affb5251a2ee6, W1b a4fe8a80a80993a26, R1 a0b560d9cdadeae82 (done), LAST a5155e6d5be914a82, Lab_Guy ab3f25fc37f0c6a63 (done). R2 rsi-deep-depth-map still raw.

## STATE SNAPSHOT (write-up for rebuild after compaction)
Written ~16:00Z by coordinator (login C, JIS-NB, tree .claude/worktrees/eager-gates-f17471, branch claude/eager-gates-f17471).
Stop 18:30Z. Report to Doctor (local_bf48e37d-ceba-4d0e-94fe-330458b891ac) at 16:30Z, 17:30Z and at stop: one line per card (state, sha, turns) + blockers. At stop: notes shipped, `git cherry` 0.
Rules now: ONE ship at a time (queue behind `git cherry` empty); no hand-killing gates (report >30 min); workers in own worktrees; commit exact paths only; wake rule = every turn ends with a live background wait.
Gate fix bd0fcf941 on trunk ~15:08Z.

### Workers (Agent ids; use SendMessage to resume)
| Card | Agent id | Worktree/branch | State |
|---|---|---|---|
| Lab_Guy stamps (W1, R1 x2) | ab45c523f063a571e, ab3f25fc37f0c6a63 | read-only | done: W1 ACCEPT, R1 ACCEPT |
| W1 wavetrend-data-inference | (other host) | - | DONE 4463a42e7 (no manifest json) |
| W1b manifest json + test registrations | a4fe8a80a80993a26 | worktrees/agent-a4fe8a80a80993a26, worktree-agent-a4fe8a80a80993a26, commit 3f7053e | waiting (loop) for H1 ship to land, then merges, registers test_econ_floor too, ships once |
| R1 rsi-deep-econ-floor | a0b560d9cdadeae82 | agent-a0b560d9cdadeae82 | DONE 073019dfa (H1 verdict: no TF dead; 1m abs30/20/rel dead; 60m abs20 lead) |
| S1 sim-dashboard-v1 | a51fee2549362525e | built in coordinator tree, commit 0b13455c5 | built, 4 tests; rides in the running tree ship; Doctor publishes index.html afterwards |
| H1 habib-holdout-prereg-draft | a222affb5251a2ee6 | coordinator tree, commit e65a368db | ship running (carries H1+S1+notes, tree sha 2f5cd1215) since ~15:35Z |
| LAST tasks.py done x4 (Haiku) | a5155e6d5be914a82 | agent-a5155e6d5be914a82, commit fb20945f1 | waiting to ship after W1b lands (input_manifest.json on trunk) |
| R2 rsi-deep-depth-map | - | - | not started; card raw, needs refine + Lab_Guy stamp; only if time |

### Ship queue
1) tree ship (H1+S1+notes) running -> 2) W1b -> 3) LAST. After all land: one last notes ship from my tree (`sync.py ship --again` only if <10 min since a ship from this tree; else plain ship).

### Background tasks of mine
Watcher bq92vcvq5 (cherry e65a368db empty, 19 min per run; re-arm when it expires). Poller for gate fix finished.

### Measurements so far (row evidence)
- Row 2: S1/W1b registered tests in run_extra_tests.py -> FULL gate; 3 parallel gates saturated JIS-NB (100% CPU); gate runs of S1 and W1b killed at 15 min by workers (my brief rule), tree ship ran >50 min incl. slot wait. R1 smoke gate passed first run.
- Row 3: CI green on all pilot ships so far (latest checked 15:39Z). No reverts.
- Row 4 (rework): S1/H1 shared my tree (logged finding); S1+W1b gate kills; W1b manifest generator month-slice bug fixed in W1b (name[11:18]).
- Cards moved: W1 done (other host), R1 done; H1/S1/W1b/LAST pending ship.

### Next steps
1. When tree ship lands: check CI (`gh run list --branch fast-track --limit 1`), verify `git cherry origin/fast-track e65a368db 0b13455c5` empty.
2. Check W1b ships, then LAST ships (Haiku asked to verify each of confluence-s0-registry, confluence-s1-context-counts, wavetrend-audit-c1-disposition, malkan-gfs-btc-htf-prereg before done).
3. Optional R2: refine rsi-deep-depth-map, Lab_Guy, worker after queue empty (serial, same folder as R1).
4. Spot-check one claim (Haiku re-runs R1 test or count). Reports at 16:30Z/17:30Z/stop. Final notes ship, git cherry 0.
