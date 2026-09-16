# Open Loops - Current Status

Written: 2026-09-16
Source: open-loops master file plus the runtime log and the session log.

## Open items

### Stop-day reports success when it stopped nothing

Last known: the script reported "stopped 2" when in fact no matching processes existed.
Current evidence: the script body was read this session. It counts processes before and after, but the count logic does not distinguish between "found and stopped" and "found nothing".
Status: needs a live reproduction to confirm.
Recommended action: add a distinct message for the zero case, then test.

### Alerts fire on every proof-count change

Last known: the alert trigger fires on any change in the proof count.
Current evidence: the specific line was located earlier in this session. Six of thirteen alerts in a single hour fired on this alone.
Status: open, no fix yet.
Recommended action: change the trigger to fire only when the count crosses a threshold, not on every change.

### Snapshots have unexplained multi-hour gaps

Last known: two gaps were observed on 14 September, one of twelve hours and one of four hours.
Current evidence: the runtime log shows the loop was not running during those windows.
Status: open.
Recommended action: confirm the loop was intentionally stopped during those windows, or add a watchdog.

### Missing alert numbers six through twelve

Last known: alert numbers jump from five to thirteen with no entries between.
Current evidence: the runtime log has no records for those numbers.
Status: open.
Recommended action: check whether the alert counter resets on restart. If it does, that explains the gap and the item can be closed as expected behavior.

### Runtime loop exits silently with no log entry

Last known: the loop stopped once with the finally block running and no error written.
Current evidence: the runtime log shows the loop resumed after a restart with no error line.
Status: open.
Recommended action: wrap the loop body so that any unhandled exit writes at least one line.

### Large one-time dump files may be unreferenced

Last known: thirteen dump files sit in the dumps folder, each over one hundred kilobytes.
Current evidence: a search this session found no active reference to any of them.
Status: open until 2026-09-21.
Recommended action: if no reader is found by that date, remove.

## What the runtime log shows right now

The last recorded cycle is cycle five hundred ninety. The loop is running. The most recent state is "in value area". The most recent verdict is "wait for reward-to-risk".

## What the session log shows right now

The most recent entries cover the consolidation of scripts into the new folder layout, the addition of the per-task discipline rule, and the creation of the dictionary. The session closed cleanly on the evening of 15 September.

## End