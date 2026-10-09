# DEPLOY RUNBOOK (live tree on JIS-NB, supervisor only)

Builders never deploy by hand. The supervisor (or `scripts/dev/auto_deploy.py`, the scheduled job) runs these steps in order and stops on the first failure.
Code reaches the live tree only from `green/fast-track` (the SHA CI tested), never from an untested tip.

1. Stop only the processes whose files change (loop-supervisor revives them within ~1 min).
2. **Copy the untracked runtime state first** (B152): `MyTradingSys/runtime/orderflow_live/_state.json` is written by the recorder and
   was untracked by af91b21. A `git merge --ff-only` aborts when the recorder has modified it, or deletes it when the target commit
   drops it. Without it `orderflow_live.py` restarts at the current minute and the minutes since the last write are never fetched.
   Copy it to `runtime_data/deploy_backup/<stamp>/_state.json` before the merge and copy it back after.
3. `git fetch origin green/fast-track`, then `git merge --ff-only origin/green/fast-track`. Not fast-forwardable = stop and report.
4. Run the offline gate (`python scripts/dev/run_all_tests.py --quick`). Red = stop; the previous commit stays deployed (`git reset` is never used: the
   deploy has not moved HEAD past a failing gate because the merge is undone with `git merge --abort` / checkout of the old files).
5. Java changes need `mvn compile` and a JVM restart: leave them for a window and say so.
6. Restore `_state.json`, restart the stopped processes, confirm `runtime_data/live_runner.log` advances.
