# State machine CVD/VWAP vs klines audit (2026-10-18, read-only)

Card: state-machine-vwap-cvd-vs-klines (absorbs audit-state-code-cvd-and-vwap-anchor; rows L-13/L-14 of MyTradingSys/research/screenshots/2026-10-15_BTCUSDT_set_7f3698134541.md).
DECISION (OURS): one audit covers both mismatches; no code edited.

## Mechanism (quoted)
- StateCodeEmitter keeps session_cvd / session_cum_pv / session_cum_vol from its OWN aggTrade websocket, summed tick by tick: StateCodeEmitter.java:179-189 (reset at UTC day change :181-183).
- After a JVM restart the three sums are restored from state_code.json (StateCodeEmitter.java:470-474, B057) and only ticks received after the restart are added. Nothing backfills ticks missed while the process was down; the file is written every 60 s (EMIT_PERIOD_SEC, :46), so ticks since the last write are lost too. A websocket drop (onClose -> scheduleReconnect, :152-168) also has no backfill: same gap path.
- The snapshot CVD (cvd.value) is a different source: kline taker delta 2*takerBuyBase - volume (MarketDataSnapshot.java:224-239, buildCvd), so it always matches the archive. Snapshot VWAP (buildVwap, MarketDataSnapshot.java:688-708) uses typical price (H+L+C)/3 times kline volume; the emitter uses trade price*qty. These differ in definition by a small, bounded amount (below).

## Control test (today, no gap)
mirror state_code.json 2026-10-17T20:25:14Z (session_day_start_ms 1792195200000 = 10-17 00:00Z) vs Binance fapi 1m klines 10-17 00:00Z..20:25Z (1225 closed bars, recomputed independently):
| quantity | state_code.json | klines | diff |
|---|---|---|---|
| volume BTC | 30163.775 | 30163.367 | +0.41 (0.001%) |
| CVD BTC | -1758.02 | -1760.29 | +2.27 |
| VWAP | 81498.00 (cum_pv/cum_vol) | 81498.00 quote-volume VWAP; 81498.44 typical-price VWAP | 0.00 / -0.44 |
So with no gap the accumulator is exact; the typical-price definition costs about 0.44 USD, not tens.

## Mismatch rows
| id | observation | cause | evidence |
|---|---|---|---|
| M1 (L-13, CVD) | 10-15 12:41Z session_cvd -6549.7 vs klines -6182.3 (diff -367.4 BTC) | Missed ticks (restart or WS reconnect without backfill) between the day start and 12:41Z. Exact restart time UNKNOWN: runtime_data/_mirror/runtime_data/live_runner.log and supervisor_log.txt hold only the last 3000/1000 lines, none from 10-15. | control test shows the emitter is exact when continuous; the same-day file shares the 00:00Z start (:L-13), so a reset cannot explain it; a bias of -367 BTC means the missed window was net-buying, so missed ticks are the only mechanism left in the code (:179-189, :470-474). |
| M2 (VWAP 10-12) | 10-12 13:08Z cum_pv/cum_vol 83498.0 on 53825 BTC vs klines VWAP 83577.0 on 73527 BTC | Same cause: 19702 BTC (26.8%) of the day's volume never entered the sums (restart without backfill). The VWAP differs because the missing hours traded higher; it is a partial-session VWAP presented as session VWAP. | volume deficit is far above the 0.001% control; typical-price vs trade-price definition explains <1 USD (control), not 79. Figures 83498.0/53825/83577.0/73527 are quoted from the card text (the 10-12 klines window was not re-pulled in this audit; the control test above is the recomputed evidence). |
| M3 (L-14, vwap_anchor_utc) | session.vwap_anchor_utc 2026-10-15T13:30:00Z (and 10-12T13:30:00Z) while now is 12:43Z / 13:09Z | A label bug, not a data bug: MarketDataSnapshot.java:832-836,861 builds NY 09:30 of TODAY converted to UTC (13:30Z in EDT) and writes it as vwap_anchor_utc, but the VWAP itself is built from dailyBars = UTC 00:00 bars (:93, :208). The label names the US-open anchor used for session high/low/IB (:838-857), not the VWAP anchor, and is in the future for 00:00-13:30Z. | value fit 00:00Z in L-14 (81104.6 vs 81108.29); TOM_ON_BTC.md:107-109 lists the anchor question already. |

## Consumers
| field | read by | effect |
|---|---|---|
| session_cvd, session_cum_pv, session_cum_vol | StateCodeEmitter itself: computeCvdSlope (:228, :342), computePriceVsVwap (:229) -> 5-signal vote -> state letter A.. in state_code.json | a gap shifts the CVD series (slope is a difference, so a one-off offset hurts only at the gap) and shifts price-vs-VWAP permanently for the day. Grep (src/, scripts/, MyTradingSys excluding research/archive/tasks) finds no other reader of these keys. |
| state_code.json (whole file) | scripts/dev/live_mirror.py:67 (copies it), scripts/sched/check_live_health.py:34 (freshness only, 300 s) | no use of the three fields |
| vwap_anchor_utc | no code reader found; emitted in the snapshot JSON (MarketDataSnapshot.java:861) that DSA/LLM prompts and screenshot reviews read | only misleads a human/LLM reader |
| snapshot cvd.value, vwap.price | engine snapshots (klines based), correct | unaffected |
Not checked: DSA prompt templates that print the snapshot (text search only, no exhaustive prompt audit).

## Follow-up cards (not built here; live-path fix goes to JIS-NB with a CRITICAL review slot)
1. state-code-accumulator-backfill: on restore and on WS reconnect, re-seed session_cvd/cum_pv/cum_vol from fapi aggTrades (or 1m klines taker data) from the last saved tick time to now; fail closed (flag the accumulators INVALID in state_code.json) if backfill fails. Test: restart with a gap, non-trade clock, API error.
2. snapshot-vwap-anchor-label: write the true VWAP anchor (UTC day start, = session_start_utc) as vwap_anchor_utc, or rename the NY-open stamp to ny_open_utc; test that the stamp is never later than as_of.
