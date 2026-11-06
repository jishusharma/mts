# RESULT: H3 NY-open low (set at open+120..150, held >= 30 min), 10-symbol DEV count (BLOCKED)

Context:
- Regime: none, count-only; no regime filter and no returns read.
- Phase: NY-day low over [00:00Z, open+180 min) set at open+120..150 min and held through open+180 (OURS rule of `../h3_ny_open_low_2026-10/BLOCKED.md`); DEV 2022-01-01..2024-06-30 (splits.py).
- Session: NY (open 13:30 UTC in US DST else 14:30, `day_gates.ny_open_utc`).
- Entry: none; no entry or outcome is defined or read.
Regime mix: NOT_IN_DATA (count-only, no regime tagging run)

| Symbol | usable days | events |
|---|---|---|
| BTCUSDT | 650 | 30 |
| ETHUSDT, SOLUSDT, XRPUSDT, LTCUSDT, BNBUSDT, ADAUSDT, DOGEUSDT, AVAXUSDT, LINKUSDT | NOT_IN_DATA | NOT_IN_DATA |

Only BTC 1m DEV klines are on disk (F:/MTS/data/tom_raw, bigtrade/spot_raw); the 9 other symbols have no 1m file for 2022-2024 anywhere under F:/MTS/data, so they are not counted and not padded. Pooled n = 30 (BTC). The earlier BTC count was 35 (`h3_ny_open_low_2026-10`); here 30 under the exact code in `count_10sym.py` (first bar at the day low, window must hold every minute); the difference is a tie/gap convention, not an outcome. Only bar times and lows were read.
Gate: `prereg_gate.py --n 30 --sd 1.5 --sd-source research/h3_ny_open_low_2026-10/BLOCKED.md --cost 0.14 --m auto` -> m 222, MDE 1.240 + cost 0.14 = 1.380 vs 0.30, n needed 1803, exit 1 BLOCK. Even if all 10 symbols matched BTC (n 300, hypothetical): MDE+cost 0.532, still BLOCK.
VERDICT: BLOCKED. Next: END: 1803 events needed vs 30 on disk; fetch 1m DEV for 9 symbols would give at most ~300; a wider event definition must be pre-registered as a new card.
