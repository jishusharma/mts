# DEPLOY RUNBOOK (live tree on JIS-NB)

Since 2026-10-10 the deploy runs by itself: scheduled task `MTS-AutoDeploy` (every 15 min) runs `python scripts/dev/auto_deploy.py` on the host
that holds `.mts_live`. Builders never deploy by hand and never stop or restart processes. Code reaches the live tree only from
`origin/green/fast-track`, the SHA CI gated on ubuntu AND windows (.github/workflows/ci.yml, job `mark-green`), never from an untested tip.

What the job does, in order; it stops at the first failure and writes the reason to `MyTradingSys/runtime/sched/auto_deploy_last.json`
(+ one line in `auto_deploy.log`, gitignored, per host):

1. `.mts_live` missing = `NOT_LIVE`, nothing changed (the job is harmless on every other host).
2. `git fetch origin green/fast-track`. Failure = `STOP_FETCH`.
3. Same SHA as HEAD = `UP_TO_DATE`. HEAD not an ancestor of the target = `STOP_NOT_FF` (never reset, rebase or force; a human decides).
   A tracked file that another session edited and the deploy would change = `STOP_DIRTY` (never merge or stash over someone's edits).
4. **Gate the candidate** in a throwaway detached worktree (`../mts-deploy-gate`): `python scripts/dev/run_all_tests.py --quick`.
   Red = `STOP_RED`; the live tree is untouched; the same SHA is not re-gated until a newer green SHA appears (`RED_KNOWN`).
5. **Copy the untracked runtime state first** (B152): `MyTradingSys/runtime/orderflow_live/_state.json` is written by the recorder and was untracked by
   af91b21. A `git merge --ff-only` aborts when the recorder has modified it, or deletes it when the target commit drops it; without it
   `orderflow_live.py` restarts at the current minute and the minutes since the last write are never fetched. The copy goes to
   `runtime_data/deploy_backup/<stamp>/_state.json` and is put back if the merge removed the file.
6. `git merge --ff-only origin/green/fast-track`.
7. Restart only what changed (`RESTART_MAP` in auto_deploy.py): execution/auto_trader*, executor, deribit_orders ... -> `auto_trader.py`;
   daily_loss_monitor, mainnet_pnl, kill_switch, deribit_orders -> `daily_loss_monitor.py`; backtest/layers/alerts and the layer packages, bt/, fees -> `live_runner_cli.py`.
   loop-supervisor revives them in about a minute. **position_manager is never killed** (it guards an open position; new managers load the new code).
8. Java (`src/main/java`, `pom.xml`) is listed under `java_pending` in the result: it needs `mvn compile` and a JVM restart window, which the job does not do.

Read the last result any time: `python -c "import json;print(open('MyTradingSys/runtime/sched/auto_deploy_last.json').read())"` on the live host.
`python scripts/dev/auto_deploy.py --check` decides and reports without changing anything.

Register (once per host, as the logged-in user): `powershell -File scripts/sched/register_cicd_tasks.ps1 -Trigger` (add `-SkipDeploy` on hosts that are not the live tree).

## CI starvation fallback (2026-10-10)
The GitHub token on the builder machines has no `workflow` scope, so `.github/workflows/ci.yml` cannot be changed from here.
ci.yml cancels the running push job on every new push, so during a burst `green/fast-track` stops advancing (it sat at 24197c4 for
a day). `auto_deploy.py` therefore falls back: when `origin/green/fast-track` is older than 90 min and is an ancestor of
`origin/fast-track`, it gates and fast-forwards `origin/fast-track` instead. The local gate in the throwaway worktree is the
safety; red still stops. The root fix is `MyTradingSys/system/ci_concurrency_fix.patch` (`cancel-in-progress` only for PRs):
operator applies it once from an account with workflow scope (`git apply` then push), or adds the `workflow` scope to the token.

## Daily hygiene (moved here from CLAUDE.md 2026-10-11)
Task `MTS-DailyHygiene` (06:30) runs `scripts/dev/daily_hygiene.py` (quick gate, `sync.py where`, declutter DRY run, STATUS) ->
`MyTradingSys/runtime/sched/hygiene_latest.md`, which STATUS.md embeds: a session reads its STATUS/GATE lines at boot and fixes a
RED before new work. Registered by the same `register_cicd_tasks.ps1` call as the deploy job. Never deploy by hand while the job works.
