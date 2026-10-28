# MTS DICTIONARY
# Version: 1.0.0 | Date: 2026-09-15
# Authority: this file points. Named authority file defines. Do not duplicate.
# Boot-read: listed in SESSION_MANIFEST.json boot_supplemental.
# Rule 52: before answering any field-level question, read this file first.
# Maintained by: any session that resolves a field-level question. Rule 51 applies.
## HOW TO USE

1. Field question arrives.
2. Look up the field name below.
3. Read the authority file at the named section.
4. If authority is [NO EVIDENCE], open an L-item and stop.

## CANONICAL FIELDS

| Field | Source(s) | Authority | Notes |
|---|---|---|---|
| CVD (cumulative) | DSA snapshot `cvd.value`, `cvd.slope` | data_schema_v1.2.0.md §"DATA BLOCK — cvd (UPDATED)" | Session-anchored 00:00 UTC |
| CVD (recent) | DSA snapshot `cvd.cvd_recent.delta_1h / delta_4h / slope_1h / slope_4h` | data_schema_v1.2.0.md §"cvd_recent object fields" | Recent-window decomposition |
| CVD (CoinGlass) | CoinGlass CVD panel | heatmap_field_map.md §2b | Anchors at leftmost visible bar — never compare numerically to DSA |
| Volume Delta (per-bar) | CoinGlass Volume Delta panel; DSA `trade_flow.net_delta_1m` | heatmap_field_map.md §2b; data_schema_v1.2.0.md §"trade_flow" | DSA field name `net_delta_*` matches CoinGlass "Volume Delta", NOT their "Net Delta" |
| Volume Delta (multi-window) | DSA `trade_flow.net_delta_5m / 15m / 1h` | data_schema_v1.2.0.md §"trade_flow" | Sum of last N bars |
| Net Delta (CoinGlass) | CoinGlass Net Delta panel | heatmap_field_map.md §2b | POSITIONING family, not flow. Best proxy: Net Longs − Net Shorts (T3). Do NOT cross-validate with DSA CVD by sign |
| Open Interest | DSA `open_interest.direction`, `.change_1h_pct` | data_schema_v1.2.0.md §"DATA BLOCK — open_interest"; heatmap_field_map.md §2 | Direction from DSA; magnitude CoinGlass context |
| OI breakdown (retail/whale L/S) | DSA `oi_breakdown.retail.long_short_ratio`, `oi_breakdown.whale.long_short_ratio` | data_schema_v1.2.0.md §"oi_breakdown" | Proxy — account/position ratio, not absolute OI |
| Funding rate | DSA `funding.current_rate`, `funding.extreme` | data_schema_v1.2.0.md §"funding" | Extreme = crowded side |
| Spot/perp basis | DSA `spot_perp_basis.basis_pct`, `.direction` | data_schema_v1.2.0.md §"spot_perp_basis" | Premium = longs pay |
| Book imbalance | DSA `conditions.book_imbalance`, `order_book_depth.bid_ask_ratio` | data_schema_v1.2.0.md §"order_book_depth" | bid_ask_ratio |
| Volume Profile | DSA `weekly_vp`, `daily_vp`, `post_funding_vp`, `intraday_4h_vp` | data_schema_v1.2.0.md §VP blocks; heatmap_field_map.md §1 | Approximated from 1m OHLCV — may deviate 0.2-0.5% from CoinGlass VPVR |
| VWAP | DSA `vwap.price`, `.slope`, `.bands` | data_schema_v1.2.0.md §"vwap" | HLC3 source, session anchor. Sigma bands are screener invention, NOT Tom |
| Liquidation clusters | DSA `liquidation_clusters.*` | heatmap_field_map.md §2 | DEPRECATED 2026-09-12 — emits 0.0/false unconditionally. Do not use |
| Trade flow (all windows) | DSA `trade_flow.net_delta_1m / 5m / 15m / 1h` | data_schema_v1.2.0.md §"trade_flow (updated 2026-09-11)" | — |
| Order flow speed | DSA `order_flow.trades_ratio`, `.volume_ratio`, `.speed_state` | data_schema_v1.2.0.md §"order_flow" | DSA_TASK_013 |
| State code | MyTradingSys/runtime/state_code.json | state_machine_design_2026-09-11.md §5 | Emitted every 60s by Java child. `signals.cvd_slope` may diverge from snapshot `cvd.slope` (aggTrade vs kline) |

## CROSS-CATEGORY WARNINGS

Three family confusions that recur:

1. **Flow vs Positioning.** CVD and Volume Delta are flow. Net Long/Short and CoinGlass "Net Delta" are positioning. Never cross-validate by sign — they measure different participant behaviors.
2. **Anchor mismatch.** DSA CVD anchors at 00:00 UTC. CoinGlass CVD anchors at leftmost visible bar. Values are not comparable unless anchors match.
3. **Same name, different source.** `cvd.slope` (snapshot, kline-based) vs `signals.cvd_slope` (state_code.json, aggTrade-based). Named differently on purpose. Do not equate.

## MAINTENANCE

When a session resolves a field-level question:
1. Update the authority file with the definition.
2. Add or update the row above.
3. Do not duplicate content — the row links, the authority file defines.
4. If a field has no authority, set the cell to `[NO EVIDENCE]` and open an L-item.

# END
