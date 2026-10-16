# WIRING W3 - all layers on testnet (operator 2026-10-16)

Calibration / data source only. No layer here is claimed to have an edge. Live runs the OLD code until the next AutoDeploy;
operator: HALT clear + review_by 2026-10-23.

## New testnet sources (6) + 1 re-sized
| source prefix | registry key | tf | emits | size / max loss |
|---|---|---|---|---|
| layer:rsi_divergence: | rsi_divergence\|rsi_divergence\|1h | 1h | both sides (event side) | 20 / 2 |
| layer:bb_top_reversal: | bb_top_reversal\|bb_top_reversal\|15m | 15m | short | 20 / 2 |
| layer:session_levels: | session_levels\|session_levels\|1m | 1m | both | 20 / 2 |
| layer:candle_close: | candle_close\|candle_close\|1m | 1m | both | 20 / 2 |
| layer:levels: | levels\|confluence\|1m | 1m | both (Q79) | 20 / 2 |
| layer:wlow_bounce: | wlow_bounce\|bbrsi60\|1h | 1h | long, flag `WLOW_EMIT_LONG` (ON) | 20 / 2 |
| layer:cryptocred:failed_msb: (existing) | - | 15m/1h | - | 200 / 4 (= sr_flip 15m) |

Real source keys are `layer:<layer>:<sub>:<tf>`, e.g. `layer:levels:confluence:1m`. Each has a `pre_pipeline_sources` entry
(reason "grandfathered testnet calibration, operator 2026-10-16 all-layers direction; not an edge claim", review_by 2026-10-23).

## DECISION (OURS)
- DECISION (OURS): one registry key per layer (adapters emit both sides on the event), not the per-sub keys the W1a handoff proposed.
- DECISION (OURS): no new accounts; the new sources share the catch-all `layer:` account jishu_21. `layer:cryptocred:failed_msb:` also
  gets a grandfather entry (behaviour-neutral; keeps the config test "grandfather list == size_overrides + accounts" true).
- DECISION (OURS): 1m adapters need days of history but the runner fetches 100 bars. Added `HistoryStore` (live_runner_cli.py): pages
  public Binance klines forward, fails closed (error / gap / short / bars not equal to the runner's -> no events). Needs: session_levels
  2900 bars, candle_close 10200, levels 24480 (17 d). Cold start is ~25 requests once per process; then one small request per bar.
  Symbol is the runner default BTCUSDT; another `--symbol` fails the overlap check (silent layer, stderr line).
- DECISION (OURS): confirm_lag_bars 0 for all new keys (rsi_divergence/bb_top first-appearance lag measured on synthetic data: actionable
  events appear at lag 0; older-t events are history and the core drops them).
- DECISION (OURS): wlow ON event carries `side: long`, `sampling: true`, no `collection_only`; the forward jsonl log is unchanged.
- bigtrade kline replay (`fires_kline.B2_KEYS`) lists all six new keys as not replayable (history beyond 99 bars / own fetch).
  `alert_rate_check.py` replays the bare adapter (`fn.raw`) on its long window.
- bigtrade (e992e17f) skipped as instructed.
- Tests: `test_w3_wiring.py` (26; 20 fail on the pre-change files). Restart = fresh HistoryStore equals old; API errors fail closed;
  source without pre_pipeline entry is rejected (UNREG); wlow flag OFF side-less. Non-trade balance moves: this change touches no
  balance/PnL code, so none apply.
- Wiring-registry: removed the 3 W1a/W2a WIRE entries plus 8 entries the wiring scan reported STALE after wiring.
