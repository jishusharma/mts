BLOCK

# GPT cross-vendor review of StateCodeEmitter backfill

Reviewed e4bcc09fd3a3df2f8cb78dd1aec030264f06aa43 on JIS-NUC, UTC 2026-10-20 (operator local date 2026-10-21). The four Java files are unchanged between that commit and this review checkout. Read-only review; production sources were not edited. Two HIGH defects prevent approval. This completes the review, not the fixes or deployment.

Contract: `MyTradingSys/system/card_specs/state-code-accumulator-backfill.md`, steps 2-4 and done_when a-f; background audit: `MyTradingSys/research/audits/state_cvd_vwap_audit_2026-10-18.md`. Parameters and synthetic fixture choices here are OURS; no trader parameter claim is made.

## Findings

| Severity | File:line | Scenario and evidence | Proposed fix / card |
|---|---|---|---|
| HIGH | src/main/java/datafeed/StateCodeEmitter.java:181-182,367-369 | MISMATCH: the T>=M filter is applied only to ticks already pending at completion. A delayed pre-M tick arriving after completion goes straight into the valid accumulator, despite already being represented by klines. Synthetic probe: 330 bars, CVD=1320, volume=3300; deliver T=M-1, buy quantity=2 after backfill; published CVD=1322, volume=3302, valid=true. The seam contract must hold regardless of which side of the HTTP completion a delayed frame arrives on. | Persist the accepted boundary and exclude older ticks from session sums for the active connection/day; keep rolling signal-buffer handling separate. Add post-completion boundary tests. `statecode-late-seam-tick`. |
| HIGH | src/main/java/datafeed/StateCodeEmitter.java:423-432,510-511,637-641 | MISMATCH: validity is copied under BUFFER_LOCK, but publication occurs later without checking or serializing the epoch. A socket close after snapshot invalidates the object, then the old emit publishes a fresh timestamp and valid=true. Deterministic probe invokes the real close callback at the existing emit logging boundary, before writeStateJson: expected false, actual true, state=A. A retained L/S would likewise be published as valid. | Serialize invalidation and final publication; an epoch check alone before an unlocked write still races. Publish INVALID promptly on disconnect/startup and prevent an older emit overwriting it. `statecode-invalid-publish-race`. |
| MED | src/test/java/datafeed/StateCodeEmitterTest.java:412-442,532-557,577-596 | NOT_IN_DATA: errors and manual retries are tested, but no test changes day or connection DURING source.fetch, and none exercises the production requestBackfill retry scheduler. Current rollover test changes the day before a later call, not during it. Close/ring test emits INVALID before recovery, so it does not prove epoch clearing when no intermediate emit occurs. | Add deterministic latch/injected-clock tests for day_rolled_during_backfill, reconnected_during_backfill, scheduled retry recovery and close/reopen without intermediate emit. `statecode-backfill-race-coverage`. |

## Required scenario matrix

| Scenario | Outcome / evidence |
|---|---|
| 1 Restart with stale restored sums | MATCH: restartReplacesStaleRestoredSumsWithBackfill; restoreStateFromDisk:689-705 restores state only, not sums. Published totals replace restored totals. |
| 2 Reconnect seam, connect vs M | MATCH for buffered ticks: reconnectGapSeamIsExact and backfillWaitsForAMinuteBoundaryAfterTheConnect. M must exceed connect+5 seconds (:313-318). MISMATCH for late pre-M ticks after completion: HIGH finding above. |
| 3 HTTP error, timeout, short list, bad rows and retry | MATCH for synchronous outcomes: backfillErrorsFailClosedAndRecover covers IOException, SocketTimeoutException, short/long count, null, duplicate/non-monotonic open time, malformed array, and recovery. :331-355 checks count, timestamps and numeric fields. Source BinanceClient:18-20 sets connect/read timeouts; :101-108 rejects HTTP errors and parses JSON. NOT_IN_DATA for an actual scheduled retry and explicit malformed numeric/NaN tests; see MED follow-up. |
| 4 Day rollover VALID and INVALID | MATCH: dayRolloverContinuousResetsAndInvalidRebackfillsNewDay proves continuous first-tick reset and a new-day backfill while invalid. :362 rejects a day change during fetch by inspection; NOT_IN_DATA for a test reaching this rejection. |
| 5 INVALID window / downstream readers | MATCH for correctly published INVALID: :639 emits INVALID; :661-665 nulls sums; :668-673 nulls unavailable signals. scripts/core/start-trading-day.ps1:663-667 matches only ^L/^S, so suppresses adverse-flow alerts. This is fail-closed for invalid signal use, not a guarantee of continued adverse-flow protection. :645-649 checks timestamp age only and does not escalate fresh INVALID. live_mirror.py:67 copies the whole file; check_live_health.py:34 checks freshness only. rg of scripts, execution and Java found display readers printing state, not treating INVALID as a directional state; regime in live_mirror.py:345 is only a brief key, not a state classifier. No automatic order/exit guarantee is asserted. HIGH publication race breaks the producer guarantee. |
| 6 Locks, backfill/WS and CVD ring | MATCH: BUFFER_LOCK serializes pending replay with onMessage; connectEpoch rejects an obsolete fetch (:361); accEpoch changes at invalidation/completion (:268,371), and emit clears ring on epoch change (:440). closeInvalidatesAndClearsTheCvdRing passes. MISMATCH: publication is outside that lock, reproduced above. NOT_IN_DATA: in-flight reconnect and recovery-without-intermediate-emit tests. |
| 7 vwap_anchor_utc <= as_of | MATCH: MarketDataSnapshot.java:862 now uses UTC day truncation. liveSession_vwapAnchorIsUtcDayStartAndNeverInTheFuture passes. The anchor is now the day start used for daily bars rather than the NY-open label. |
| Continuous sums / non-trade / replay control | MATCH: continuousStreamSumsEqualPlainTickSums, nonTradeMessageLeavesSumsUnchanged, replayFixtureCvdMatchesKlinesWithinTenthOfABtc all pass. Replay is synthetic; no real-data or holdout accuracy claim. |

## Validation and reproducibility

`mvn -q test -Dtest=StateCodeEmitterTest,MarketDataSnapshotTest` exited 0. Parsed complete Surefire reports: StateCodeEmitterTest 28 tests, MarketDataSnapshotTest 22 tests, zero failures/errors/skips. These passing tests do not cover the two reproduced defects. No new repository tests were added because this is a read-only audit.

Standalone probe source: `MyTradingSys/research/layer_lab/state_backfill_review.java.txt`. Copy to a temporary directory as StateBackfillReview.java; compile with javac `-cp` equal to the java.class.path property from `target/surefire-reports/TEST-datafeed.StateCodeEmitterTest.xml`, `-d` the temporary directory. Run `datafeed.StateBackfillReview` with that directory prepended to the same classpath. Used the bin/java.exe and bin/javac.exe under the Surefire java.home property. All inputs are synthetic, no network, no live file access. Results:

```text
LATE_PRE_M: expectedCvd=1320 actual=1322.0 expectedVolume=3300 actual=3302.0 valid=true
CLOSE_BEFORE_PUBLISH: expectedValid=false actual=true state="A"
```

The second probe schedules the close callback synchronously at an existing logging boundary to reproduce an allowed ordering, rather than depending on thread timing. It does not modify production code.

Follow-up cards (lane JIS-NB): `statecode-late-seam-tick`, `statecode-invalid-publish-race`, `statecode-backfill-race-coverage`. They require fixes/tests on their assigned lane and a fresh independent review before deploy.

Queue inventory: this was the only open CODEX card with boolean crucial=true or gpt_only=true. Other matching GPT cards were already done; OPUS-only foundational cards remain outside this assignment. CI status query returned UNKNOWN (gh unavailable/offline/not authenticated); no claim of remote CI green is made. Local ship gates provide separate validation.
