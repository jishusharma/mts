# B080 dsa_worker hourly-cap misfires on stale pace entries

Opened 2026-10-01. Status CLOSED 2026-10-03. Severity MED.

## Symptom

2026-09-30 19:07Z: worker reported `paced: hourly-cap` and stalled for 5.5 hours, though the pace file had 13 entries all 5.7-28.7 hours old and none inside the 1-hour window the code filters on. Killing the worker and moving `dsa_pace.json` aside unblocked it immediately.

## Code

`scripts/worker/dsa_worker.py` L162-176. Pacing check:
```
times = [t for t in self._finished_times() if t > now - 86400] + [now]
...
if sum(1 for t in times if t > now - 3600) >= self.cfg["max_per_hour"]:
    return "hourly-cap"
```

## Not yet diagnosed

Whether `self.clock()` drift, timezone mismatch, or a comparison bug. The 1-hour filter should have returned 0 on stale entries. Not reproduced in isolation.

## Workaround

Move `Dumps/workers/NUC-QUEUE/dsa_pace.json` aside and restart the worker. Two steps, safe.

## Next step

Reproduce with a synthetic pace file, or add a unit test with `clock()` injected.
