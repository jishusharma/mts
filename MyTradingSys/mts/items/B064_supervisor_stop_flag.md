# B064 - SUPERVISOR DOES NOT HONOR supervisor_stop.flag

Register row: MyTradingSys/mts/research/BUGS.md B064 (OPEN, MED).
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
  if (Test-Path .\data\supervisor_stop.flag) { log 'supervisor_stop flag present, exiting'; exit 0 }

Priority: same as B056. Do not wait for a stop flag plus polling. Check each cycle.

## STATUS

OPEN. Fix design only. Not landed. Fix is one block edit to scripts/core/loop-supervisor.ps1.

# END