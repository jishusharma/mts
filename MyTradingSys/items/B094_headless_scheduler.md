# B094 - headless scheduler

Status: CLOSED 2026-10-05. Severity: MED. Opened 2026-10-03.

## Operator rule (verbatim, 2026-10-03)

  "enable it when operator askes and remember to disable ot whenit
   makes no sense to run it -how we derive the sense is up to
   claude"

Enable is operator-only. Disable is automatic. What "makes no
sense" means is Claude's call, derived from disk state.

## Defect

pick_task.py composes a ready prompt every 15 minutes and writes
it to MyTradingSys/runtime/queue/next_task.txt. Launching still
needs the operator to type mts go. Observed 2026-10-03: TF1 was
picked at 10:59:12Z, held 24h, never launched. The whole queue
sat idle behind a prompt nobody ran.

## Fix (Claude decides)

Build a scheduled task that runs the equivalent of mts go headless
on the same tick as MTS-Scheduler-Tick, or a separate task on a
cadence Claude chooses.

Preconditions (verify from disk before building):
  1. scripts/sched/go.py must gain a per-run token cap. Without
     it, one stuck run can burn the pool.
  2. The launch must not start a second writer while another CL
     session is active (B086 rule).
  3. The disable condition must be derivable from disk, not from
     operator memory.

Candidate sense conditions for auto-disable (pick, reject, or
add):
  - no pickable row in BUILD_PIPELINE.md or the BUGS sweep
  - a CL session is already running (process check)
  - token pool below a floor (source: the pool reading the
    scheduler already trusts)
  - pick_state.json held for more than X hours with no launch
  - canary RED
  - HALT or AUTO_PAUSE present

Log every auto-disable with the reason. Log every enable with the
operator words that authorized it.

Test must fail on the pre-change go.py or tick.py at least once.

## Receipt

go.py: --max-usd / env MTS_GO_MAX_USD (default 5, 0 = no cap) passed as --max-budget-usd; --headless adds -p. New scripts/sched/autogo.py (--tick/--enable --words/--disable/--status): enable is operator-only via flag file runtime/sched/autogo_enabled, words logged; auto-disable (logged to runtime/sched/autogo_log.jsonl) on brake file (HALT/HALT_DAILY_LOSS/AUTO_PAUSE), canary RED, no pickable slot, all slots held over 24h unlaunched; skips on CLAUDECODE, live pid, slot launched <24h. tick.py CHECKS gains autogo (event). Tests: test_autogo.py 9, test_go.py 14-17; on pre-change go.py/tick.py 4 fail (test_9 autogo, 14, 15, 17). Ships DISABLED; operator runs autogo.py --enable --words. Not rejected-by-design: token-pool floor (no pool reading on disk; per-run cap covers it). Receipt commit: the commit whose message begins 'B094: '.

Design: cadence = the 15-minute tick (one launch per tick, no second task). Sense conditions chosen: brake file, canary RED, no pickable slot, stale-held slots (replaces "pick_state held X hours"). Rejected: token pool floor (no on-disk pool reading), "CL session running" as a disable (transient, so a skip instead).

# END
