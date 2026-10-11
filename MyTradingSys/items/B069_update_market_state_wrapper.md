# B069 - STATE_UPDATE_WARN under wrapper

Register row: MyTradingSys/research/BUGS.md B069.
Opened: 2026-09-25 by session MTS-2026-09-24-1100Z.

## THE DEFECT

update_market_state.py exits 0 when run directly from the operator shell.
It exits 1 when run by the loop wrapper via cmd.exe /c with output
redirected to NUL. The wrapper logs STATE_UPDATE_WARN exit=1.

## EVIDENCE

start-trading-day.ps1 L422-427:
  $umsCmd = 'python "' + $R + '\MyTradingSys\runtime\update_market_state.py" > NUL 2>&1'
  $rc = Invoke-WithTimeout -File "cmd.exe" -ArgList @("/c", $umsCmd) -TimeoutSec 30 -Tag "update_market_state" -WorkDir $R
  if ($rc -ne 0) { Log-Line ("STATE_UPDATE_WARN exit=" + $rc) }

2026-09-24T18:40:15Z: direct run, exit=0, wrote current_market_state.md.
2026-09-24T18:40:16Z: wrapper log, STATE_UPDATE_WARN exit=1.
Same second. Same file. Different exit code.

The traceback is discarded because stderr is redirected to NUL.

## NOT YET DIAGNOSED

Candidate causes, unconfirmed:
- cmd.exe /c with redirection swallows a genuine Python exception and
  cmd.exe itself returns 1 when the inner command exits non-zero.
- The script may read stdin or use a resource not available when launched
  from a hidden cmd.exe under pwsh 7 with a stripped PATH.
- The first-run path (before state exists) may take a branch that fails
  only when current_market_state.md is in a specific state.

## FIX SHAPE (proposed, not landed)

Change the wrapper to capture stderr to a file:
  $umsCmd = 'python "' + $R + '\MyTradingSys\runtime\update_market_state.py" 2>>"' + $R + '\runtime_data\state_update.err.txt"'
Then run once with the loop running and read the err file.
That names the traceback and the line.

## STATE

2026-09-25 OPEN. Cosmetic only: the state update is not read by the
verdict function on a cycle-by-cycle basis; current_market_state.md is
already being written by other paths. But the WARN line is noise and
the underlying failure has not been seen.

# END

2026-10-04: wrapper already sent stderr to runtime_data/ums.log (not NUL); now the log line carries exit=N and the ums.log tail on failure, so log and exit code agree. Pinned by test_b074_rule_order.py::test_b069_* (fails pre-change). Root cause of the original exit=1 NOT reproduced (ums.log from the last run is clean); item stays open for that. Session MTS-2026-10-04-1034Z-APP-BLD-b074-b069-wrapper.
