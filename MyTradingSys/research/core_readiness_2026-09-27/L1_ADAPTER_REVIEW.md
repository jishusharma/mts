# L1 FILE-SOURCE ADAPTER — design review (Opus 5.5, 2026-09-27)
Scope: SESSION_3_HANDOFF §4 step 2. Reviewed against MarketDataSnapshot.java (historical path lines ~960-1275)
and CORE_READINESS_PLAN F7. Verdict: GO with the constraints below. Builder: Sonnet (Java), tests first.

## What the historical path does today (verified in source)
- Klines: `fetchMultiTimeframeAsOf` -> REST `client.klinesRange(tf, asOf - limit*dur, asOf)` + `dropFormingBar`. Time-bounded, no look-ahead. Also `klinesRange` for yesterday (1m), prev week / two weeks (1h).
- Zeroed/defaulted (F7): book_imbalance 0.0, funding 0.0/extreme false, oi_trend "flat", open_interest block flat, trade_flow net_delta_* 0.0, cvd_trade_flow_aligned false, order_book_depth 0.0.
- LIVE data injected into a past snapshot (look-ahead, F7): `spot_perp_basis` and `buildOiBreakdown(symbol)` (line ~1190). liquidation clusters: static "not available" note.
- Threaded fetch with `f.get(30s)` swallowing failures -> a timeframe can silently be missing.

## Design (minimal, live path untouched)
1. `interface HistoricalSource { JsonNode klines(tf, startMs, endMs, limit); JsonNode markKlines1m(startMs, endMs);
   OptionalDouble oiAt(tMs); List<double[]> oiSeries(fromMs, toMs); OptionalDouble fundingSettledAt(tMs);
   OptionalDouble bookImbalanceProxyAt(tMs); }` with two implementations: `RestHistoricalSource` (wraps
   BinanceClient, today's behaviour) and `ArchiveHistoricalSource(Path rawRoot)`.
   Only `fetchHistoricalSnapshot` / `fetchMultiTimeframeAsOf` / the three `klinesRange` calls switch to the source.
   `fetchSnapshot` (LIVE) is not modified — A3 replay + core_invariants must show live output byte-identical.
2. Archive source loads 1m klines ONCE into primitive arrays (t,o,h,l,c,v,tbv,count) indexed by minute; every
   snapshot slices, never re-reads CSV. Higher TFs (5m,15m,1h,4h,1d,1w) are AGGREGATED from 1m with Binance
   alignment (UTC; 1w starts Monday 00:00). Row format identical to REST (12-column arrays) so downstream code
   is unchanged. dropFormingBar semantics preserved: include a bar only if close_time < asOf.
3. As-of rules: metrics row usable iff create_time <= asOf; funding: last SETTLED rate <= asOf (live uses the
   current-period estimate -> label `funding.source = "settled_proxy"`); bookDepth: latest row <= asOf, proxy.
4. Fields with no raw source are emitted as JSON null with a sibling `"source":"unavailable"` — NEVER 0.0/"flat":
   spot_perp_basis (unless spot klines are added to L0 — data.binance.vision has them; recommended, cheap),
   liquidation clusters, order_book_depth top-of-book. oi_breakdown from metrics long/short ratios where the
   field maps 1:1, else unavailable.
   REQUIRED audit before trusting L2: every consumer of these fields must treat null as "no signal"
   (fail-closed). Known: countSignals uses `bookImbalance != 0.0` after `.asDouble()` -> null reads as 0.0 ->
   not counted: safe. verdict.py / build_mo_cli / math_object_builder: Sonnet greps and lists each read.
5. Derivable exactly from 1m klines (fill instead of zero): trade_flow net_delta_{1m,5m,15m,1h} =
   sum(2*tbv - v); cvd series; oi_trend / change_1h_pct from 5m metrics; speed proxy from kline `count`
   (trades/min) — label `"source":"kline_count_proxy"` (speed no longer counts toward proof after D4: low impact).
6. Every regenerated snapshot carries `"source_manifest"`: mode=archive, raw files + SHA256 used, adapter version.
   Output is deterministic (no thread pool in archive mode, stable key order) -> re-runs are byte-identical.
7. Fail loudly: a missing 1m minute inside the lookback -> snapshot marked `"data_gap": true` and excluded from
   L2 (no silent partial windows like today's swallowed timeouts).

## Gates (in order; do not skip)
- P0 aggregation parity: for 50 random timestamps per TF on 2026-09-13..26, archive-aggregated TF bars == REST
  klines (all 12 columns; volumes to 1e-8). Unit-tested.
- P1 (handoff): regenerated vs archived live snapshots, Tom core steps 1-8: 100% candidates and fields
  (A3 harness; today's numbers 2149/2149 candidates, 30086/30086 fields since golden boundary).
- P1b: F7 fields — report per-field agreement of the now-filled flow fields vs archived live snapshots
  (trade_flow deltas, oi_trend, funding sign). Not a hard 100% gate (live uses different windows); thresholds set
  by operator from the report.
- P2 (handoff): bookDepth proxy sign agreement with archived book_imbalance.
- Look-ahead canary (BACKTEST_PROTOCOL §3): truncate raw data at t+0 for 20 random t -> identical snapshots.

## Risks / open
- R-L1-1 Live klines REST vs archive can differ by late trade corrections -> P0 decides; if any bar differs,
  archive wins for backtest (it is the settled record) and the diff is logged.
- R-L1-2 Funding estimate vs settled rate: funding_extreme may fire at different times. Documented as proxy.
- R-L1-3 Cadence: live snapshots are ~0.5-1/min. Generate at every 1m close (525k/yr); with in-memory slices
  this is minutes of CPU. `--step-minutes` flag for quick runs.
