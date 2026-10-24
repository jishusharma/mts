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
