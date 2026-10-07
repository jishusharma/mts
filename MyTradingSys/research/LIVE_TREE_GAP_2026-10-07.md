# LIVE TREE GAP VERDICT - 2026-10-07

Session: MTS-2026-10-07-1000Z-APP-ANA-whea-htf (Track A). Analysis only; no live file, process or HALT touched.
Compared: live tree `C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed` @ 3a64f3d against `origin/fast-track` @ 0b8072e (fetched this session).

## A1. Gap

`git log --oneline 3a64f3d..origin/fast-track` = 43 commits (cloud PR merges #2 #4 #5 #6 #7 #8 #10 #11 #15 #16 #17 #18, P1/P2/P4
research notes, registry rows B136 close, CI workflow). `git diff --name-status -M` = 49 paths: 30 added, 15 modified, 4 renamed (corrected at validation; first version said 38/8/3).

## A2. Classification

Bucket (i) = a file the running loop, supervisor, wrapper, scheduler tick or live alert runner executes or imports.
I did not trust path names alone: the live Python layer runner (`backtest/layers/alerts/live_runner_cli.py`, `live_layers.py`,
`live_runner_core.py`) imports `MyTradingSys.backtest.layers.{rsi,fabio}.*`, and `htf_context_live.py` imports
`...fabio.v3.signals`. So `backtest/layers/` is partly live. The scheduler tick (`MTS-Scheduler-Tick`, every ~15 min, fresh
process each time) runs `scripts/sched/tick.py`, which launches `autogo.py --tick` as a subprocess (tick.py:34; corrected at validation, it is not an import).

| Bucket | Paths |
|---|---|
| (i) touches a live-imported module/package | `scripts/sched/autogo.py` (run by tick.py as a subprocess); `MyTradingSys/backtest/layers/fabio/__init__.py` (new file inside the package the live runner imports) |
| (i-adjacent), in a live-imported tree but not imported by any live process (grep over alerts/, scripts/live, scripts/core) | `fabio/fabio_v3.py`, `fabio_v3_exec.py`, `fabio_v3_signals.py` (new); `consensus/writer.py`, `consensus/test_writer.py`, `rsi/observation.py`, `rsi/test_observation.py` (renamed from `.new`, i.e. promoted); `fabio/v3/tests/*` (6 modified tests) |
| (ii) everything else | `.github/workflows/ci.yml`; `DSA_SESSION_PROMPT.md`, `MTS_USER_GUIDE.md`; `mts.ps1` (operator launcher, referenced only by scripts/load.ps1, check_guide.py, write_device_files.py, not by any scheduled-task action or .vbs launcher); `scripts/dev/*`; `scripts/p1_*`, `scripts/debug_p1.py`, `scripts/p4_complete.py`; `MyTradingSys/tests/*`; `MyTradingSys/runtime/test_update_market_state.py` (test); all `MyTradingSys/research/*`, `system/sessions/*` |
| Not touched by the diff | `src/main/java/datafeed/`, `MyTradingSys/execution/`, `MyTradingSys/backtest/layers/alerts/`, `scripts/live/`, `scripts/core/`, any non-test `MyTradingSys/runtime/*.py|json`, `htf_context_live.py`, the supervisor/wrapper scripts |

## A3. What the running loop does differently after a pull

1. `scripts/sched/autogo.py` `pid_alive` (5 lines). The change adds a Linux `/proc/<pid>/stat` zombie check after `os.kill(pid, 0)`.
   The function returns earlier on `os.name == "nt"` (autogo.py:65-69, `tasklist` branch). On this Windows host the changed lines
   are unreachable. Behaviour after a pull: identical. (The tick would import the new file on its next 15-minute start; nothing is cached.)
2. `fabio/__init__.py` (docstring only, 1 line). It turns `layers/fabio/` from a namespace package into a regular package.
   `layers/` and `layers/rsi/` have no `__init__.py`, so imports of the form `MyTradingSys.backtest.layers.fabio.<module>` resolve as
   before. Already-running processes (live runner, pythonw htf writer) have their modules loaded and do not re-read it. A restart would
   import it with no effect. Not exercised on this host: I did not import it from a clean interpreter against the post-pull tree.
   CI (c02b2dd, a946f64) ran the offline gate on ubuntu and windows green on the merged tip, which covers the import path.
3. The three `fabio_v3*.py` files re-export the `v3` package. No live module imports them.
4. `consensus/writer.py`, `rsi/observation.py` were `.new` staging files and are now promoted. Grep of the live runner, alerts and
   scripts/live shows no import of either. They run only if someone wires them.
5. `mts.ps1` adds the `runner` and `orphans` verbs and status lines. Operator-invoked; the `.vbs` task launchers do not call it.

No bucket (i) change alters live behaviour on this host.

## A4. Verdict

**Pull NOT needed for live safety or function.** Justifying files: the only two bucket (i) paths are `autogo.py` (Windows branch
unchanged) and `fabio/__init__.py` (docstring). Everything else is research, tests, docs, CI, or an operator launcher.
Reasons to pull anyway, none urgent: tests/gate parity with CI (`run_all_tests.py` step 3h), `mts runner|orphans` verbs, the
promoted `.new` modules.
If a pull is done: do it with the loop up (a fast-forward touches no file the Java loop or auto_trader imports), expect the
live tree's modified `runtime/oi_live/*.csv`, `session_log.json` and untracked runtime files to be unaffected (none of them is in
the 49-path list; incoming adds no path that exists untracked in the live tree). Restart nothing; only the supervisor restarts anything.
Caveat: pre-pull `git status` in the live tree shows 3 modified tracked runtime files; use `git pull --ff-only` and stop if it refuses.

## Validation

validated 2026-10-07 on JIS-NUC (session MTS-2026-10-07-1000Z-APP-ANA-whea-htf, follow-up): re-cloned origin, `git rev-list --count 3a64f3d..0b8072e` = 43, `git diff --name-status -M` = 49 paths (A 30, M 15, R 4).
autogo.py diff re-read: change is after the `os.name == "nt"` return, unreachable on Windows. fabio/__init__.py = 1 docstring line. Live
runner (`alerts/live_layers.py`, `live_runner_cli.py`, `live_runner_core.py`) and `htf_context_live.py` import rsi_core, rsi_events, rsi_ma,
malkan_40_60, fabio_escalation, fabio_volume_fvg, fabio_cvd_absorption, orderflow_live, v3.day_gates, v3.engine, v3.signals; none of these is
in the 49 paths (v3 changes are tests only). No import of consensus.writer, rsi.observation or fabio_v3*.py. Verdict unchanged: pull not needed.
