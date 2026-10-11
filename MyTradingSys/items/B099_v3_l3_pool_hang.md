# B099 - run_v3_l3.py OOS pass hangs in ProcessPoolExecutor, no fail-closed path to the parent

Status: FIXED (stall handling); original cause UNKNOWN | Severity: MEDIUM | Opened 2026-10-04 | Found by: MTS-2026-10-03-1759Z-CLI-BLD-tf8-fabio-v3-histori

## Observed
- `python -m MyTradingSys.backtest.layers.fabio.run_v3_l3` (parent PID 18840, 7 workers = `os.cpu_count() - 1`, run_v3_l3.py:163) wrote two lines to
  `F:/MTS/data/fabio_v3_bt/run.log` and then nothing more:
  `IS windows 266, OOS windows 120, skipped {'closed': 22, 'short': 31, 'thr0': 1}`
  `selection frozen: {'A': 'A|N60|p0.05|f0.003|rest|g0.8', 'B': 'B|N60|z2|f0.003|rest', 'C': 'C|m5|f0.005|rest|g0.8', 'D': 'D|N240|p0.05|f0.003|rest'}`
- `selection.json` was written (end of the IS phase, before any OOS window ran: the pre-registered order held). `results.json`, `dayR.json`, `tables.md` never appeared.
- Operator report (not re-verified by this session): the OOS pass hung, the parent was killed from outside, no children were alive afterwards.
  Reading: a worker died or stalled during phase 2 and the parent never learned of it.

## Shape
- `run_cells` (run_v3_l3.py:109-118) feeds every day to `pool.map(_run_day, ..., chunksize=2)` (:113) with no timeout and no per-task result check.
- One pool serves all phases (:163; used at :165, :175, :181-182, :184). One stuck or dead worker stalls the whole `map` iteration forever.
- `_run_day` catches `Exception` per job (a crash becomes 0 R tagged `error:*`), but a worker killed at process level (OOM, kill, hard fault) raises nothing
  in the parent while it waits. No wall-clock bound, no heartbeat, no per-phase progress line: the hang is silent.
- Cause NOT established. Unverified candidates: worker memory (each task pickles a 390-bar window, 20 prior range lists and the job list),
  host contention with the live stack (B098 traced the CPU spike to this pool), an engine input that loops.
  The IS pass (266 days x 112 cells + variants) completed, so the engine ran to completion on IS windows.

## Fix shape (not done; operator said no re-run)
1. Phase progress lines to run.log (phase, windows done) so a stall shows as a stall.
2. `as_completed` / per-phase wall-clock bound; on timeout or `BrokenProcessPool` write a `FAILED` marker and exit non-zero (fail closed: no partial OOS read as a result).
3. Write each phase day-R to disk as it completes so a re-run resumes from the frozen selection.
4. Find the cause of the stall first (one OOS day serial, then `--days-limit`, then a pool).
A re-run is a new trial row (PRE_REG_FABIO_V3.md stop rule). `selection.json` stays frozen; no OOS number exists.

## Fix applied 2026-10-04 (run_v3_l3.py, tests test_b099_*)
- run_cells: per-day futures, TASK_TIMEOUT 900 s, RunFailed on timeout or BrokenProcessPool, FAILED marker + non-zero exit, progress every 20 windows,
  slow-window lines (> 120 s), per-phase disk cache (phase_*.json), IS must reproduce the frozen selection.json.
- 2 tests (stalled pool, dead pool) fail closed; they did not exist before (RunFailed absent).
- Re-run 18:37Z-18:50Z: all phases completed, no slow window, no FAILED, selection reproduced. results.json written.
- The original hang did NOT recur and its cause is still unknown (no slow-window or error line to point at). If it recurs, FAILED and run.log name the phase and window.
