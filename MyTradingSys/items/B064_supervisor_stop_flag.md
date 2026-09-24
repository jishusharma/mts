# B064 - SUPERVISOR DOES NOT HONOR supervisor_stop.flag

Register row: MyTradingSys/research/BUGS.md B064 (OPEN, MED).
Opened: 2026-09-23 by MTS-2026-09-23-0430Z.

## VERBATIM ASK

No verbatim ask. Filed by coordinator at session close.

## DEFECT

supervisor_stop.flag was written at 05:48Z on 2026-09-23. Supervisor 3184 continued its cycle:
  05:48:36 | RESTART reason=wrapper_dead oldPid=0
  05:49:11 | ok wrapper=11988 snapAge=115s grace=True
  05:49:43 | ok wrapper=11988 snapAge=25s grace=True
  05:50:14 | ok wrapper=11988 snapAge=56s grace=False
  05:50:46 | ok wrapper=11988 snapAge=29s grace=False
  05:51:17 | ok wrapper=11988 snapAge=1s grace=False

Six cycles after the flag. Supervisor never read it. Direct Stop-Process -Id 3184 -Force was required.

## RELATIONSHIP TO B056

B056 was: supervisor does not check loop_stop.flag (the wrapper stop flag). B064 is a distinct flag.
B056 fix landed 2026-09-19 added loop_stop.flag check to loop-supervisor.ps1.
B064 shows supervisor_stop.flag is a separate flag that was never wired into the supervisor loop.

## FIX SHAPE (design only, not applied)

At top of each supervisor cycle, before the lock read:
  if (Test-Path .\runtime_data\supervisor_stop.flag) { log 'supervisor_stop flag present, exiting'; exit 0 }

Priority: same as B056. Do not wait for a stop flag plus polling. Check each cycle.

## STATUS

CLOSED 2026-09-23T10:34Z. Not reproducible. Check already present at loop-supervisor.ps1 L71. Controlled test passed. See update below.

### 2026-09-23T10:34Z - coordinator, session MTS-2026-09-23-0831Z

Reproduction attempt failed.
- Code read: loop-supervisor.ps1 line 71 already contains the exact fix shape (Test-Path StopFlag -> log -> exit 0).
- File mtime 2026-09-23 00:13 IST (2026-09-22 18:43Z), before the 05:48Z observation. No working-tree diff. Last commit touching the file is cd3dd79.
- Controlled test: started fresh supervisor PID 16480 at 10:34:01Z. Wrote runtime_data/supervisor_stop.flag at 10:34:10Z. PID exited within one cycle. Log: '2026-09-23 10:34:33 | stop flag present, exiting'.

Action: B064 CLOSED as non-reproducible against current code. If the cycle-ignores-flag behavior recurs, refile with timestamped log evidence.

# END
