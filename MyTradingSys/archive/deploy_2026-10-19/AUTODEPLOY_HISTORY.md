# AutoDeploy Historical Documentation (Archived 2026-10-19)

> **RETIRED 2026-10-17 per SCHEDULING_POLICY.md.**  
> Scheduled tasks (`MTS-AutoDeploy`, `MTS-DailyHygiene`, `MTS-Supervisor`, `MTS-CodexLab`) are stopped across all devices.  
> Deploy runs manually by the operator or named coordinator following `MyTradingSys/system/DEPLOY_RUNBOOK.md`.  
> This file preserves the historical design and internals of `scripts/dev/auto_deploy.py`.

---

## 1. Historical Automated Deploy Workflow (2026-10-10 to 2026-10-17)

Between 2026-10-10 and 2026-10-17, deployments ran via Windows Task Scheduler task `MTS-AutoDeploy` (every 15 min) running `python scripts/dev/auto_deploy.py` on the host holding `.mts_live`. Code reached the live tree only from `origin/green/fast-track` (gated on GitHub Actions CI).

### Step-by-step Execution Order (Historical)

1. Check for `.mts_live`: If missing, exit with `NOT_LIVE`.
2. `git fetch origin green/fast-track`. Failure returned `STOP_FETCH`.
3. Check HEAD SHA: If equal, return `UP_TO_DATE`. If HEAD not an ancestor of target, return `STOP_NOT_FF`. A tracked dirty file returned `STOP_DIRTY`.
4. **Gate Candidate:** Tested in detached worktree (`../mts-deploy-gate`) using `python scripts/dev/run_all_tests.py --quick`. Failure returned `STOP_RED`. Gate timeout was 2700 s (`MTS_DEPLOY_GATE_TIMEOUT`).
5. **Runtime State Preservation (B152):** Copy `MyTradingSys/runtime/orderflow_live/_state.json` to `runtime_data/deploy_backup/<stamp>/_state.json` before merge, restoring it if removed.
6. `git merge --ff-only origin/green/fast-track`: If untracked conflicts existed, returned `STOP_MERGE` (clearing only machine CI cards).
7. **Process Restart:** Restarted affected processes via `RESTART_MAP`:
   - Execution / auto_trader -> `auto_trader.py`
   - Daily loss / kill switch -> `daily_loss_monitor.py`
   - Backtest / alerts / layers -> `layers.alerts.live_runner_cli`
   - `position_manager.py` was NEVER killed.
8. **Java Compile Notification:** `src/main/java` changes listed under `java_pending`.

---

## 2. CI Starvation Fallback (2026-10-10)

`ci.yml` previously cancelled running jobs on new pushes, causing `green/fast-track` to stall during high push bursts. Fixed on 2026-10-16 via `ci-nowin-conc` by setting `cancel-in-progress: ${{ github.ref != 'refs/heads/fast-track' }}`. When `origin/green/fast-track` lagged `origin/fast-track` by > 90 min, `auto_deploy.py` gated and fast-forwarded `origin/fast-track` directly in a throwaway worktree.

---

## 3. Daily Hygiene Task (`MTS-DailyHygiene`)

Ran daily at 06:30 via `scripts/dev/daily_hygiene.py` (quick gate, `sync.py where`, declutter dry run, STATUS update) writing `MyTradingSys/runtime/sched/hygiene_latest.md`.

---

## 4. Zero-Cost Idle Ticks (Q41 Design, 2026-10-12)

Designed to run `git fetch -q origin fast-track` + `relay.py kick` on Windows Task Scheduler to wake dispatcher sessions without burning LLM start tokens. Retired along with all scheduled tasks under `SCHEDULING_POLICY.md`.
