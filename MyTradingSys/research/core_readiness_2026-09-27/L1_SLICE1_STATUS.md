# L1 File-Source Adapter — Slice 1 Status (2026-09-27)

## Files staged (repo, `.new` suffix, not committed, live path untouched)
- `src/main/java/datafeed/HistoricalSource.java.new` — new interface, `klines(tf, startMs, endMs, limit)` only (per slice scope; markKlines1m/oiAt/oiSeries/fundingSettledAt/bookImbalanceProxyAt deferred to the wiring slice).
- `src/main/java/datafeed/ArchiveHistoricalSource.java.new` — loads all `BTCUSDT-1m-*.csv` (daily+monthly, header optional, one malformed row in `2025-10.csv` skipped with a logged warning) from `Dumps/backtest/raw/klines` once into primitive arrays (533,730 valid 1m bars). Serves 1m by direct slice; 5m/15m/1h/4h/1d/1w by aggregation (open=first open, high=max, low=min, close=last close, volume/quote_volume/count/taker_buy_* = sum, close_time = periodStart+durMs-1), 1w aligned to Monday 00:00 UTC via `TemporalAdjusters`. Row format is the same 12-column array as `BinanceClient.klinesRange`.
- `src/test/java/datafeed/P0Gate.java.new` — standalone gate main (not JUnit, to keep REST calls/caching simple): 50 random asOf timestamps per TF in 2026-09-13..26, builds start/end/limit the same way `fetchMultiTimeframeAsOf` does, compares `ArchiveHistoricalSource.klines()` vs live REST `/fapi/v1/klines`. REST responses cached under `$HOME/p0_cache` (`p0_report.txt` has the full log).

## Gate P0 result: 350/350 matched (all 7 TFs, 50/50 each)
| TF  | matched/compared |
|-----|-------------------|
| 1w  | 50/50 |
| 1d  | 50/50 |
| 4h  | 50/50 |
| 1h  | 50/50 |
| 15m | 50/50 |
| 5m  | 50/50 |
| 1m  | 50/50 |

No mismatches in the final run. open_time/close_time/count compared exact; price/volume fields compared with tolerance `1e-8 * max(1, |value|)` (relative, not pure absolute — see note below).

## Two real findings surfaced while getting to 350/350 (not code bugs, kept for the record)
1. **Volume-sum fields need relative, not absolute, 1e-8 tolerance.** Aggregating up to 1440 archived 1m `quote_volume`/`taker_buy_quote_volume` values (each stored at ~5 decimal places) against pure-absolute 1e-8 initially failed 280/350 comparisons with diffs up to ~0.03 on values ~1e8 — i.e. relative error ~1e-10/1e-11, consistent with the archive CSV's own stored decimal precision, not a summation bug. Switched the gate's tolerance to `1e-8 * max(1,|value|)`.
2. **1w gate must drop the forming bar on both sides, same as `dropFormingBar` in the live path.** Live REST always reflects the *current* state of a not-yet-closed candle regardless of `startTime/endTime` filters. Several random `asOf` values (all within 2026-09-13..26) fell inside the calendar week that is *still open right now* (today is 2026-09-27), so REST kept returning a growing `count` for that week's bar across separate calls while the archive returned the frozen dump. Fixed by trimming any bar with `close_time > asOf` from both archive and REST results before comparing — mirroring `MarketDataSnapshot.dropFormingBar`. This is exactly risk R-L1-1 in `L1_ADAPTER_REVIEW.md` and confirms the wiring slice must call `dropFormingBar` on the archive source's output too.

## Not done (out of scope for this slice, per instructions)
- `RestHistoricalSource` wrapper and wiring into `fetchHistoricalSnapshot`/`fetchMultiTimeframeAsOf`/the three `klinesRange` call sites — next slice.
- Remaining `HistoricalSource` interface methods (`markKlines1m`, `oiAt`, `oiSeries`, `fundingSettledAt`, `bookImbalanceProxyAt`).
- P1/P1b/P2/look-ahead-canary gates (handoff-level, per L1_ADAPTER_REVIEW.md gate ordering).
- JUnit wrapper for P0 (kept as a plain `main` for this slice; can be ported to a `@Test` trivially — the comparison logic is already isolated in `compareRows`/`dropForming`).

## Exact next step
Wire `ArchiveHistoricalSource` into `MarketDataSnapshot.fetchMultiTimeframeAsOf` and the three `klinesRange` call sites (yesterday, prev-week, two-weeks-ago) behind a `HistoricalSource` parameter, applying `dropFormingBar` uniformly, then run P1 (regenerated vs archived live snapshots) per the handoff gate.

## Opus review addendum (2026-09-27 ~15:50Z) — the "one malformed row" was a DATA LOSS, now fixed
- `klines/BTCUSDT-1m-2025-10.csv` was TRUNCATED at 2025-10-04 14:46 UTC (5,207 lines instead of 44,641; last row cut
  mid-line). ~27 days of October 2025 were missing. The fetcher's "skip if already extracted" meant it was never
  re-fetched. Found by the Python loader's gap check (bt_data.check_gaps), not by P0 (P0 samples Sept 2026 only).
- Fixed: truncated file moved to `Dumps/backtest/_quarantine/`, month re-downloaded with SHA256 verify -> 44,641 lines.
  1m klines now 563,040 bars = exactly 391 days, ZERO gaps. markPriceKlines was missing 2026-06-29 inside the June
  monthly archive file; added the daily file (SHA256 verified) -> 563,040, zero gaps.
- REQUIRED for the wiring slice: ArchiveHistoricalSource must FAIL (not skip-and-warn) on a malformed row and must
  run a full 1m continuity check at load (L1_ADAPTER_REVIEW item 7: fail loudly). Re-run P0 and add a load-time
  assertion `bars == expected minutes` for the configured window. The 533,730 count above is stale.
- fetch_binance_archive.py follow-up (Sonnet): after extract, verify row count vs expected minutes for kline-type
  datasets and re-fetch on mismatch; "exists" must not mean "complete".

## Session 5 (Sonnet) addendum — fail-loudly + continuity check implemented, verified
Per the Opus review addendum's REQUIRED item: `ArchiveHistoricalSource.java.new` no longer skip-and-warns on a
malformed row -- it throws `IllegalStateException` immediately, and a full 1m continuity check now runs at load
time (every consecutive pair of bars must be exactly 60,000ms apart; a gap or zero rows loaded both throw with
the UTC timestamps / row count in the message).

Verified against the toolchain re-provisioned this session ($HOME/tools was gone -- re-downloaded Temurin 17 +
Maven 3.9.9 per the resume prompt fallback):
- `mvn compile` on the live tree: clean. The two staged files compile against the project classpath (Jackson,
  etc.) with `javac` in isolation too.
- Real archive load (`Dumps/backtest/raw`, symbol BTCUSDT): 563,040 bars, zero gaps -- matches the 391-day count
  in SESSION_4_HANDOFF exactly, confirms the fix does not false-positive on the already-fixed data.
- Synthetic gap test (one row deleted from a copy of the 2025-09-01 file): throws with the exact gap size and
  UTC boundary timestamps, as designed.
- Synthetic malformed-row test (`1,2,3` in place of a real row): throws with field count and offending line,
  instead of the old silent skip.

Not done yet (next step, larger and touches live call sites -- checking in with the operator before starting):
wiring `ArchiveHistoricalSource`/a `RestHistoricalSource` wrapper into `fetchHistoricalSnapshot` /
`fetchMultiTimeframeAsOf` / the three `klinesRange` call sites in `MarketDataSnapshot.java` (lines ~1017, 1041,
1053, 1220-1260), applying `dropFormingBar` uniformly, then running P1 (A3 harness, regenerated vs archived
live snapshots).


## Session 6 (T3 builder, 2026-09-30) addendum - adapter run end-to-end in a %TEMP% copy
- **Defect in the staged wiring:** `MarketDataSnapshot.java.new` switched the three range calls (yesterday 1m, prev-week 1h,
  two-weeks-ago 1h) in the LIVE `fetchSnapshot` (lines ~124-165) and left the same three in `fetchHistoricalSnapshot` on live REST
  (a slow network call per snapshot and a look-ahead). It also added `dropFormingBar` to the live path (behaviour change).
- **Proposed fix (not applied):** `src/main/java/datafeed/MarketDataSnapshot.java.archive_mode.new`, generated deterministically by
  `MyTradingSys/backtest/l1_patch_mds.py` from the staged .new: live path identical to the committed original, historical path wired
  with `dropFormingBar`, archive mode no longer calls live REST for `spot_perp_basis`/`oi_breakdown` (neutral node with
  `"source":"unavailable"`), `trade_flow.net_delta_*` + `cvd_trade_flow_aligned` filled from 1m klines with the live formula.
- Archive load: 2,491,200 bars 2022-01-01..2026-09-26 (`raw_1m_2022` + `raw`, merged copy on `F:\MTS\data\tom_raw\klines`), zero gaps.
- **P1 (regenerated vs 200 archived live snapshots, `p1_compare.py`):** 29 kline-derived fields x 200 = 5800/5800 equal
  (prices, daily/weekly/4h VP, VWAP, prior day, swings 5m/15m/1h, net_delta 1m..1h, cvd/vwap slope, cvd_trade_flow_aligned);
  rank-1 candidate identical 196/200, top-3 list identical 193/200. Proof nodes are identical except `book_imbalance`
  (not regenerable); `proof_count` differs because the archived live snapshots were produced before D4 (old counting of
  speed / finished-auction direction / book) - current-code counts on the same proof nodes match the regenerated ones.
- Parity replay (`ReplayScbSteps1to8`, README_REPLAY.md; README needs `ExecutionMathConstants.java` in the copy): PASS, 200 snapshots,
  473/473 candidates, 6622/6622 fields.
- Harness: `harness/java/TomSnapshotGen.java` (historical snapshot generator, 15-min cadence), `harness/java/SnapAt.java` (P1 helper).
