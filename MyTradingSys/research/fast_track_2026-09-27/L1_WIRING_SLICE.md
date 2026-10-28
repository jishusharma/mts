# L1 Wiring Slice — call-site wiring of ArchiveHistoricalSource/RestHistoricalSource

Status: staged as `.new` files, not committed. Branch + P1/P1b/P2/A3 gate still required before merge (greenlight condition).

## Files (all `.new`, live path untouched)
- `src/main/java/datafeed/RestHistoricalSource.java.new` (32 lines, new) — wraps `BinanceClient.klinesRange`,
  the exact pre-slice REST call, behind `HistoricalSource`. IOException -> `UncheckedIOException` (interface
  has no `throws` clause, see Open questions).
- `src/main/java/datafeed/MarketDataSnapshot.java.new` (1503 vs 1468 lines; diff: 5 removed / 40 added).

## What changed, per call site
1. **Constructor** (~line 28): added `archiveRawRoot` field (default `null` in the existing no-arg
   constructor) + a new `MarketDataSnapshot(Path archiveRawRoot)` overload, + `historicalSource(symbol)`
   helper (returns a per-symbol cached `ArchiveHistoricalSource` when `archiveRawRoot != null`, else a
   fresh `RestHistoricalSource`). **This is the explicit switch**: default (no-arg) construction is
   byte-identical to before; archive mode is opt-in only via the new constructor. `fetchSnapshot` (live) does
   not call `historicalSource()` and is unmodified.
2. **`fetchHistoricalSnapshot`, "yesterday" 1m klines** (was line 1017) — `client.klinesRange(...)` ->
   `historicalSource(symbol).klines(...)`, plus a new `dropFormingBar(yesterdayKlines, yesterdayEndUtc...)`
   call (previously absent here).
3. **`fetchHistoricalSnapshot`, prev-week 1h klines** (was line 1041) — same substitution +
   `dropFormingBar(prevWeekKlines, prevWeekSunday...)`.
4. **`fetchHistoricalSnapshot`, two-weeks-ago 1h klines** (was line 1053) — same substitution +
   `dropFormingBar(twoWeekKlines, twoWeekSunday...)`.
5. **`fetchMultiTimeframeAsOf`** (was line 1234) — `client.klinesRange(...)` -> `historicalSource(symbol).klines(...)`;
   `dropFormingBar` was already present here. The lambda's `catch (IOException ex)` was changed to
   `catch (RuntimeException ex)` (see Open questions) — otherwise `mvn compile` fails with "exception
   java.io.IOException is never thrown in body of corresponding try statement", since neither
   `HistoricalSource` implementation declares a checked `throws`.

The three `dropFormingBar` additions (#2-#4) implement `L1_SLICE1_STATUS.md`'s session-5 addendum finding #2:
`ArchiveHistoricalSource.klines()` for a multi-bar TF can emit a not-yet-closed period at the range's end
boundary; `dropFormingBar` must run on archive output the same way it already does in `fetchMultiTimeframeAsOf`.
For REST/default mode this is a no-op in practice (REST never returns a bar closing after the requested
`endTime`), so live/default behaviour is unchanged; it only takes effect when archive mode is active or if a
future REST response ever behaves otherwise.

## Build/test
`mvn -q clean test` — PASS (JDK 21 toolchain, `maven.compiler.source/target=17`; no compile errors, no test
failures; the module has no JUnit `@Test`s wired to these classes yet, so `test` = `test-compile` + 0 executed).
Run in a scratch copy in the cloud container (device has no `mvn`), with all four `.new` files swapped in and
one `clean` before compiling, per instructions. `mvn -q clean test-compile` was also run standalone and passes.

## Gates the operator must run (in order, per `L1_ADAPTER_REVIEW.md` §Gates)
- **P0** (already done, `L1_SLICE1_STATUS.md`): 350/350 matched, prior slice. Not re-run here (no
  aggregation-logic change in this slice).
- **P1** (handoff-level, this slice's actual purpose): regenerated (archive-mode `fetchHistoricalSnapshot`)
  vs. archived-live snapshots, Tom core steps 1-8, target 100% candidates/fields parity — via the A3 replay
  harness:
  - Single-shot: `.\MyTradingSys\research\core_readiness_2026-09-27\harness\java\run_replay.ps1 [-SinceMs <ms>]`
  - Batched (session 5's variant, for large snapshot counts — Windows argv length):
    `.\MyTradingSys\research\core_readiness_2026-09-27\harness\java\run_replay_argfile.ps1 [-SinceMs <ms>] [-BatchSize 100]`
    — runs `ReplayScbSteps1to8` in `BatchSize`-file chunks, prints per-batch RESULT lines, "A3 OVERALL: PASS/FAIL".
  Both harness scripts currently replay against whatever's in `runtime_data\snapshots\`; regenerating those
  snapshots in archive mode first (construct `new MarketDataSnapshot(archiveRawRoot)` instead of `new
  MarketDataSnapshot()` at the call site, e.g. in `HistoricalScreening.java` / a small driver) is on the
  operator/next-slice, not done here — out of this slice's scope ("nothing more").
- **P1b**: F7 field agreement report (trade_flow deltas, oi_trend, funding sign) vs archived live snapshots —
  no existing script found under this repo's `.md`/`.ps1`/`.py` tree; operator-authored report per
  `L1_ADAPTER_REVIEW.md` (not a hard 100% gate, thresholds set by operator).
- **P2**: bookDepth proxy sign agreement — same status as P1b, no existing script found.
- **Look-ahead canary** (`BACKTEST_PROTOCOL.md` §3): truncate raw data at t+0 for 20 random signal times,
  verdicts must be byte-identical. No existing script found under this repo tree; operator to build per protocol.

## Branch commands (operator)
```
git checkout -b l1-wiring-slice
git add src/main/java/datafeed/RestHistoricalSource.java.new \
        src/main/java/datafeed/MarketDataSnapshot.java.new \
        src/main/java/datafeed/HistoricalSource.java.new \
        src/main/java/datafeed/ArchiveHistoricalSource.java.new \
        MyTradingSys/research/fast_track_2026-09-27/L1_WIRING_SLICE.md
# review diffs, run P1/P1b/P2/canary, THEN rename .new -> live and commit:
mv src/main/java/datafeed/RestHistoricalSource.java.new src/main/java/datafeed/RestHistoricalSource.java
mv src/main/java/datafeed/MarketDataSnapshot.java.new src/main/java/datafeed/MarketDataSnapshot.java
mv src/main/java/datafeed/HistoricalSource.java.new src/main/java/datafeed/HistoricalSource.java
mv src/main/java/datafeed/ArchiveHistoricalSource.java.new src/main/java/datafeed/ArchiveHistoricalSource.java
mvn clean test   # STANDING LESSON: always clean after .new renames
git add -A && git commit -m "L1 adapter: wire ArchiveHistoricalSource/RestHistoricalSource into historical call sites"
```

## Rollback
Nothing is committed or renamed by this slice. To discard: delete the four `.new` files and this doc; the
live tree (`MarketDataSnapshot.java`, `HistoricalSource.java`, `ArchiveHistoricalSource.java`) is untouched.
If already renamed+committed on the branch: `git checkout main -- src/main/java/datafeed/MarketDataSnapshot.java`
and `git rm` the three added files, or `git revert` the wiring commit; `fetchSnapshot` (live) was never touched
so nothing outside `fetchHistoricalSnapshot`/`fetchMultiTimeframeAsOf` needs any rollback attention.

## Open questions
1. **Checked -> unchecked exception change.** `HistoricalSource.klines()` (authored in the prior slice) has no
   `throws` clause. `RestHistoricalSource` therefore wraps `IOException` as `UncheckedIOException`
   (`RuntimeException`, NOT an `IOException` subtype). The three explicit call sites in
   `fetchHistoricalSnapshot` (a method declared `throws IOException`) now propagate a REST failure as an
   unchecked exception instead of the checked `IOException` a caller might be catching
   (`HistoricalScreening.java`, `saveHistoricalSnapshot`) — was not able to find any existing `catch
   (IOException)` around these specific call sites to confirm real impact, but flagging since it's a real
   behavioural change on the error path (not the happy path). Fixing this cleanly means adding `throws
   IOException` to the interface, which is out of this slice's scope per instructions.
2. **No driver wires archive mode into a runnable entry point.** Per review item 1, only the `HistoricalSource`
   switch inside `MarketDataSnapshot` was requested; no `Main.java`/`HistoricalScreening.java` CLI flag was
   added to actually select `new MarketDataSnapshot(archiveRawRoot)` at runtime, so P1/P1b/P2 regeneration
   needs that plumbed in first (or done ad hoc) before those gates can run.
3. **P1b / P2 / canary scripts:** none found under this repo's research tree; operator needs to point me (or
   the next slice) at them if they exist elsewhere, or they need authoring.
