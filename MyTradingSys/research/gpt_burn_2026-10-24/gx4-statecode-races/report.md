# GX4 statecode race fixes

## Validation

Tests were added before the production fix. On current code, the requested command failed with both regressions:

```text
[ERROR] datafeed.StateCodeEmitterTest.closeBetweenEmitSnapshotAndPublishCannotRepublishValidState -- expected: <false> but was: <true>
[ERROR] datafeed.StateCodeEmitterTest.latePreBoundaryTickAfterBackfillDoesNotChangeSessionSums -- expected: <1320.0> but was: <1322.0>
[ERROR] Tests run: 52, Failures: 2, Errors: 0, Skipped: 0
```

Command: `mvn -q test '-Dtest=StateCodeEmitterTest,MarketDataSnapshotTest'`.

After the fixes and extended seam cases, the same command exited 0. Parsed complete Surefire XML reports:

```text
StateCodeEmitterTest: 31 tests, 0 failures, 0 errors, 0 skipped
MarketDataSnapshotTest: 22 tests, 0 failures, 0 errors, 0 skipped
```

The seam fixture is independently calculated from its bars: each bar has volume 10 and taker buy base 7, so CVD per bar is `2*7-10 = 4`; 330 bars give CVD 1320 and volume 3300. A buy quantity 2 at T=M−1 is already covered by those bars and must add zero; at T=M it adds CVD 2 and volume 2 exactly once. The test checks initial backfill, reconnect, and a UTC midnight boundary.

## Findings and fixes

| Severity | File:line | What was wrong | Reproduction / result |
|---|---|---|---|
| HIGH | `src/main/java/datafeed/StateCodeEmitter.java:183` | After backfill, every incoming tick was added to the session sums. The accepted backfill boundary M was not retained, so a delayed T<M tick duplicated kline history. The emitter now stores M at :369 and only accumulates a same-day tick when T>=M; a new UTC day clears the old boundary at :235. | `mvn -q test '-Dtest=StateCodeEmitterTest,MarketDataSnapshotTest'`; before fix expected CVD 1320, actual 1322 (and volume would be 3302). Regression now checks T=M−1 and T=M before and after reconnect and at midnight. |
| HIGH | `src/main/java/datafeed/StateCodeEmitter.java:518-527` | The emitter copied `accValid` and sums under `BUFFER_LOCK`, then wrote the snapshot later with no epoch reconciliation. A close between snapshot and file write let the older emit overwrite the disconnect with a valid state and non-null sums/signals. Final validity reconciliation and JSON publication now occur under `BUFFER_LOCK`; an epoch mismatch nulls the accumulator signals and writes INVALID/null sums. | Test triggers `onStreamClosed` synchronously while the existing emit log line is written, between snapshot and JSON publication. Before fix: expected valid=false, actual true. After fix: INVALID and null sums/signals. |

## Restart, reset, and API error coverage

- Restart with stale restored sums is covered by existing `restartReplacesStaleRestoredSumsWithBackfill`; accumulator sums are seeded by backfill instead of restored values.
- Midnight reset is covered by the new late seam test and existing `dayRolloverContinuousResetsAndInvalidRebackfillsNewDay`.
- Injected HTTP-style `IOException`/timeout and malformed/short backfill cases are covered by `backfillErrorsFailClosedAndRecover`; the existing test verifies INVALID and later recovery.
- Not covered: an actual Binance HTTP/API response in a live request, the production scheduled retry timer firing, or reconnect/day rollover occurring while `KlineSource.fetch` is blocked. Those require a controlled asynchronous fetch/scheduler harness or network/API integration fixture.

Final source and test copies are `StateCodeEmitter.java` and `StateCodeEmitterTest.java` in this output folder. Complete latest Maven output is retained as `after-test-output.txt`.

Result: Both statecode race regressions are fixed; all 53 requested tests pass.
