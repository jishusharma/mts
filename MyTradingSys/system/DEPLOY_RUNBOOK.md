# DEPLOY RUNBOOK (live tree on JIS-NB)

> **RETIRED 2026-10-17, see SCHEDULING_POLICY.md.** MTS-AutoDeploy, MTS-DailyHygiene, MTS-Supervisor, MTS-CodexLab and the other scheduled tasks below are stopped: deploy by the manual fallback or a coordinator-run step. Registration and zero-cost-tick sections are history.

Since 2026-10-10 the deploy runs by itself: scheduled task `MTS-AutoDeploy` (every 15 min) runs `python scripts/dev/auto_deploy.py` on the host
that holds `.mts_live`. Builders never deploy by hand while it works (fallback: "Manual fallback" below) and never stop or restart processes. Code reaches the live tree only from
`origin/green/fast-track`, the SHA CI gated on ubuntu AND windows (.github/workflows/ci.yml, job `mark-green`), never from an untested tip.

What the job does, in order; it stops at the first failure and writes the reason to `MyTradingSys/runtime/sched/auto_deploy_last.json`
(+ one line in `auto_deploy.log`, gitignored, per host):

1. `.mts_live` missing = `NOT_LIVE`, nothing changed (the job is harmless on every other host).
2. `git fetch origin green/fast-track`. Failure = `STOP_FETCH`.
3. Same SHA as HEAD = `UP_TO_DATE`. HEAD not an ancestor of the target = `STOP_NOT_FF` (never reset, rebase or force; a human decides).
   A tracked file that another session edited and the deploy would change = `STOP_DIRTY` (never merge or stash over someone's edits).
4. **Gate the candidate** in a throwaway detached worktree (`../mts-deploy-gate`): `python scripts/dev/run_all_tests.py --quick`.
   Red = `STOP_RED`; the live tree is untouched; the same SHA is not re-gated until a newer green SHA appears (`RED_KNOWN`).
   `auto_deploy_last.json` then holds `gate_failed`: the failing step blocks of that run (test names, assertion), so a red gate can be traced without a rerun.
   Gate time limit: 2700 s (env `MTS_DEPLOY_GATE_TIMEOUT`, seconds); an idle host needs ~290 s, but 2026-10-16 04:45Z the old 1500 s limit ended STOP_RED
   with `gate_tail ['timed out']` while parallel sessions held the CPUs at 100%. A timed-out gate keeps what it printed (`gate_tail` = its last 6 non-empty lines,
   the reason says `timed out after <N>s`), and every gated result records `gate_secs` (rounded elapsed): watch it creep up before it times out.
   Keep long CPU jobs (watchers, polling scripts, transcription) off the host around the :00/:15/:30/:45 gate runs. Live tree runs the older auto_deploy.py until its next deploy.
5. **Copy the untracked runtime state first** (B152): `MyTradingSys/runtime/orderflow_live/_state.json` is written by the recorder and was untracked by
   af91b21. A `git merge --ff-only` aborts when the recorder has modified it, or deletes it when the target commit drops it; without it
   `orderflow_live.py` restarts at the current minute and the minutes since the last write are never fetched. The copy goes to
   `runtime_data/deploy_backup/<stamp>/_state.json` and is put back if the merge removed the file.
6. `git merge --ff-only origin/green/fast-track`. An untracked file in the live tree that the merge would create makes git refuse (`STOP_MERGE`). Only a machine-generated
   CI card (`MyTradingSys/system/tasks/ci-<sha>.json`, same bytes as the incoming file or the shape `ci_red_card.py` writes) is copied to
   `runtime_data/deploy_backup/<stamp>/untracked/<path>` and removed (`untracked_cleared` in the result); any other untracked clash stays `STOP_MERGE`
   (checked before the gate and again after it, nothing removed). 2026-10-16: `make_status.py` filed such a card in the live tree and the deploy stopped;
   it no longer files the card there (`CI card: not filed (live tree)`).
7. Restart only what changed (`RESTART_MAP` in auto_deploy.py): execution/auto_trader*, executor, deribit_orders ... -> `auto_trader.py`;
   daily_loss_monitor, mainnet_pnl, kill_switch, deribit_orders -> `daily_loss_monitor.py`; backtest/layers/alerts and the layer packages, bt/, fees -> `layers.alerts.live_runner_cli` (module name: the runner runs with -m, no .py in its command line).
   loop-supervisor revives them in about a minute. **position_manager is never killed** (it guards an open position; new managers load the new code).
8. Java (`src/main/java`, `pom.xml`) is listed under `java_pending` in the result: it needs `mvn compile` and a JVM restart window, which the job does not do.

Read the last result any time: `python -c "import json;print(open('MyTradingSys/runtime/sched/auto_deploy_last.json').read())"` on the live host.
`python scripts/dev/auto_deploy.py --check` decides and reports without changing anything.

Register (once per host, as the logged-in user): `powershell -File scripts/sched/register_cicd_tasks.ps1 -Trigger` (add `-SkipDeploy` on hosts that are not the live tree).

## CI starvation fallback (2026-10-10)
ci.yml used to cancel the running push job on every new push, so during a burst `green/fast-track` stopped advancing (it sat at
24197c4 for a day; runs 38825243976 and 38824936295 were cancelled 2026-10-16). Fixed 2026-10-16 (ci-nowin-conc): `cancel-in-progress` is
`${{ github.ref != 'refs/heads/fast-track' }}`, so the run in progress on fast-track finishes and `mark-green` publishes its SHA (GitHub keeps only
the newest pending run, runs go one at a time in push order, so green never moves backwards; every marked SHA was a fast-track head and fast-track is
never rewritten). PR and other-ref runs are still cancelled when superseded. `scripts/dev/test_ci_red_card.py` (CiConcurrency) pins it; the old
`system/ci_concurrency_fix.patch` is superseded. `auto_deploy.py` keeps its fallback as a safety net: when `origin/green/fast-track` is older than
90 min and is an ancestor of `origin/fast-track`, it gates and fast-forwards `origin/fast-track` instead. The local gate in the throwaway
worktree is the safety; red still stops.

## Daily hygiene (moved here from CLAUDE.md 2026-10-11)
Task `MTS-DailyHygiene` (06:30) runs `scripts/dev/daily_hygiene.py` (quick gate, `sync.py where`, declutter DRY run, STATUS) ->
`MyTradingSys/runtime/sched/hygiene_latest.md`, which STATUS.md embeds: a session reads its STATUS/GATE lines at boot and fixes a
RED before new work. Registered by the same `register_cicd_tasks.ps1` call as the deploy job. Never deploy by hand while the job works.

## Manual fallback (only if MTS-AutoDeploy is down; moved from CLAUDE.md 2026-10-15)
Operator pre-authorised "just do it" 2026-10-09. If other sessions have uncommitted edits in the live tree, do NOT merge or stash there.
`git -C <live> checkout origin/fast-track -- <only the changed live-path files>`, run their tests, kill only the process that imports them;
`loop-supervisor` restarts it in about a minute. position_manager is never killed (it guards an open position). Java needs `mvn compile`
and a restart window: leave it and say so. Builders never stop or restart anything else, touch HALT files or open trades.
"Supervisor" in these docs means the Windows task `MTS-Supervisor` (starts at logon, revives dead processes); it deploys nothing.
Only `MTS-AutoDeploy`, or this fallback while it is down, changes the live tree.

## Deploying the "untrack generated files" commit (2026-10-20, card move-live-host-generated-files-status-md, coordinator by hand)
Commit 1 of the card runs `git rm --cached` on AUDIT_DIGEST.md, T0_CHECKS.md, runtime/BUILD_REPORT.md, runtime/oi_live/*.csv and
research/htf_context/*.jsonl|*_summary.json (STATUS.md stays tracked; `oi_recorder.py`, `htf_context_live.py` are code and stay). A tree that fast-forwards to it
LOSES those files (the live runner and `check_live_health.py` READ the oi_live and htf_context ones), and a dirty tracked copy makes the merge refuse. So, in the live tree
(`<live>` = the folder holding `.mts_live`; nothing is stopped or restarted; builders never run this):
1. `python scripts/dev/deploy_untrack_backup.py backup <live>`: copies the files to `runtime_data/deploy_backup/<stamp>/untrack/` with a sha256 MANIFEST.json and verifies the copies. Note `<stamp>`.
2. `python scripts/dev/deploy_untrack_backup.py reset <live> <stamp>`: refuses unless step 1 verifies, then `git checkout --` on the still-tracked dirty ones only.
3. `git -C <live> merge --ff-only <target>` (the gated green SHA that holds commit 1). The files disappear here; keep steps 3-4 back to back (the recorders re-create their files on the next write).
4. `python scripts/dev/deploy_untrack_backup.py restore <live> <stamp>`: puts back every missing file, sha256-verified against the manifest; a file a recorder already re-created is never overwritten: it prints PROBLEM ... KEPT-NEWER and exits 1; merge it by hand from the backup dir (append the backup rows to the new file). `reset` refreshes each dirty file's backup copy right before its `git checkout --`, so rows appended since step 1 are not lost.
5. `git -C <live> status --porcelain` must be empty (the files are ignored now); `python scripts/sched/check_live_health.py` must not say RED for oi_1m / htf_context.
6. Tell the builder: commit 2 (remove `GENERATED_RE`, `LIVE_INPUT_RE` and the regenerate branch in `auto_deploy.py`) may ship only after step 5 is clean in the live tree.
Since this commit `make_status.py` in the live tree writes `runtime_data/STATUS_live.md` (ignored) and never the tracked STATUS.md. Tests: `MyTradingSys/tests/test_generated_files_untracked.py` (temp repos only).

## Scheduled-task catch-up after the nightly power-off (2026-10-14, JIS-NB)
JIS-NB is off ~02:00-10:30 IST, so the daily tasks (06:30-09:10) never run on time. `StartWhenAvailable` alone does not catch up: it fires
~3 min after boot while no user is logged on and Task Scheduler drops it (event 332, principal ENG\jis Interactive/Limited), no retry.
Logon sessions are ready ~2.5 min after logon event 7001, so the fix is a logon trigger delayed 10 min. Scripts (write-only here, the
operator-side session runs them as the logged-in user):
- `scripts\sched\add_logon_catchup.ps1` - dry run by default (reads tasks, prints the plan); `-Apply` adds the delayed logon trigger and turns
  StartWhenAvailable on for MTS-DailyHygiene, MTS-Make-Status, MTS-Alert-Rate-Check, MTS-Audit-Rotation, MTS-Audit-Digest, MTS-Declutter-Backups,
  MTS-Orphan-Watchdog, MTS-Retention, `MTS testnet status`, MTS-CDriveCare (Retention and testnet status had it off). Skips a missing task or one that
  already has a logon trigger; keeps actions/principal; touches no other task. Effect to expect: each job also starts at every logon.
- `scripts\sched\register_cicd_tasks.ps1 -Repo <live tree>` - new `-Repo` lets a worktree copy register tasks that point at the live tree;
  MTS-DailyHygiene now registers with both its 06:30 trigger and the delayed logon trigger (a re-run keeps the catch-up).
- `scripts\sched\register_live_mirror.ps1 -Repo <live tree> [-Apply]` - MTS-LiveMirror every 5 min at :01 :06 :11 ... (clear of AutoDeploy :00/:15/:30/:45
  and Backup :07/:22/:37/:52) running `live_mirror.py publish`; refuses a repo without `.mts_live`; dry run by default.
- `scripts\core\mode.ps1` re-registers MTS-Supervisor with BOTH triggers (far-future Once + AtLogOn delay PT1M30S) and `-AllowStartIfOnBatteries
  -DontStopIfGoingOnBatteries -MultipleInstances IgnoreNew -ExecutionTimeLimit 0`. The logon trigger is the stack's only boot recovery and used to
  be lost on every mode.ps1 run; the default 72 h limit would also have killed the supervisor.
- Tests: `scripts/dev/test_sched_scripts.py` (static reads of the .ps1 files plus the dry-run/refusal paths on Windows; gated via run_extra_tests).
  Never run `install_backup_task.ps1` or `register_cicd_tasks.ps1` to "test" them: they have no dry run and register for real.

## JIS-NUC notes (2026-10-11, from NUC session 1414Z)
- NUC tree: `C:\Users\E-ngineers\IdeaProjects\mts-dsa` (worktree of `...\BinanceDataFeed\.git`). `F:\MTS\repo` is NOT a git repo there (only `MyTradingSys\` and `scripts\`
  copies); desk tasks 20261011-140307 and 20261011-140621 name it by mistake: read it as the mts-dsa tree. Codex trees: `F:\MTS\mts-codex` (Codex app project,
  hand-started) and `F:\MTS\mts-codex-lab` (unattended MTS-CodexLab, branch `jis-nuc/codex-lab`; LAYER_LAB.md).
- `MTS-AutoDeploy` must never exist on the NUC (live tree is JIS-NB only). It was found registered there on 2026-10-11, almost certainly from an earlier run of
  `register_cicd_tasks.ps1` without `-SkipDeploy`; unregistered. On the NUC always pass `-SkipDeploy`.
- The NUC needs `tzdata` (Python 3.14 has none; tom_dax_recall uses ZoneInfo Europe/Berlin). `cloud_setup.py` GATE_DEPS and ci.yml now both carry it.
- `MTS-NUC-Worker` showed Disabled on the NUC: whether intended is open (desk task posted).

## Quick-gate speed (B178, 2026-10-12, JIS-NUC)
- `run_all_tests.py` runs independent steps `MTS_GATE_JOBS` at a time (default min(4, CPUs); `MTS_GATE_JOBS=1` = one step at a time in
  definition order, the old behaviour), also Step 5b and the extra tests; steps 3ly, 3af, 3x, 3ms, 3mg and Maven run serially after the
  pool; each finished step prints its block with `Elapsed:` and a progress count. Quick gate 677 s -> 289 s on JIS-NB.
  Step 5b module list: `split_modules` partitions `find_layer_modules()` and `test_quick_gate_runs_every_layer_module` fails if one is dropped.
  Largest steps on JIS-NUC (warm): step 4 pytest 51 s, 3xt 26 s, 3k 16 s, 3dk 10 s; step 4 is the next cut (xdist or per-path processes).
- Always-run steps `3gd` (B150: every test file is gated) and `3dl` (`ci_deps_lint.py`, ~5 s): no gated test may hard-import (also through a sibling module) a package the `pip install` line of ci.yml lacks; fix = add it to that line and `cloud_setup.GATE_DEPS`, or guard it (try/except ImportError, find_spec flag, `pytest.importorskip`).
- MTS-Backup moved to :07/:22/:37/:52 (`install_backup_task.ps1`, offset 7 min past midnight + 15 min repeat) so it no longer
  starts in the same minute as MTS-AutoDeploy (:00/:15/:30/:45). Not re-registered by this session; on each host run
  `powershell -File scripts\dev\install_backup_task.ps1 -Repo <path>` (the tree the task runs from today: runtime_data\launch-backup.vbs names it).
  The GitHub repo is PUBLIC (2026-10-11), so snapshots go to the local bare repo, git remote `backup` (F:\MTS_backup.git). The installer now passes
  `--remote backup` and refuses a repo with no `backup` remote; `backup_snapshot.py` defaults to `backup` and refuses origin (by name or same URL)
  unless `--allow-origin`. Before this, re-running the installer would have pushed uncommitted/untracked snapshots to the public origin.
  Re-running replaces the live task's `wscript launch-backup.vbs` action with `pythonw.exe` directly (also windowless).

## Zero-cost idle ticks (Q41 design, 2026-10-12, JIS-NUC) - NOT BUILT, B164 untested
- Measured: one idle `relay.py kick` (git ref origin/fast-track, no model) = 0.8 s wall, ~0 CPU, 0 tokens. An idle App
  dispatcher tick is a full model session (~65k-token context per CLAUDE-relay measurement B172), so 48 ticks/day are 48 model starts.
- Design: Windows Task Scheduler job `MTS-RelayKick` every 30 min runs `git fetch -q origin fast-track` + `relay.py kick`
  (no model). IDLE: exit, log only. KICK: write `~/.claude/mts-relay-pending.json` and run the existing dispatcher prompt once
  (the App task is the only thing that may run a session: B164, a session cannot launch another and an external process
  cannot approve the App's click).
- Open risk (B164): whether an external timer can start an App scheduled task unattended is NOT TESTED here. A test needs the
  App open and a human in reach for the first launch; an unattended session cannot run it. Until it is tested, keep the App
  cron dispatcher as is (it also covers the no-timer case) and do not remove it.
- Cheap interim cut that needs no new mechanism: lengthen the App dispatcher cadence when STATUS shows an empty queue, and
  let the dispatcher's step 1 stay one Bash call (already so).

