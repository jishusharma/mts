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
| CVD (cumulative) | DSA snapshot `cvd.value`, `cvd.slope` | data_schema_v1.2.0.md В§"DATA BLOCK вЂ” cvd (UPDATED)" | Session-anchored 00:00 UTC |
| CVD (recent) | DSA snapshot `cvd.cvd_recent.delta_1h / delta_4h / slope_1h / slope_4h` | data_schema_v1.2.0.md В§"cvd_recent object fields" | Recent-window decomposition |
| CVD (CoinGlass) | CoinGlass CVD panel | heatmap_field_map.md В§2b | Anchors at leftmost visible bar вЂ” never compare numerically to DSA |
| Volume Delta (per-bar) | CoinGlass Volume Delta panel; DSA `trade_flow.net_delta_1m` | heatmap_field_map.md В§2b; data_schema_v1.2.0.md В§"trade_flow" | DSA field name `net_delta_*` matches CoinGlass "Volume Delta", NOT their "Net Delta" |
| Volume Delta (multi-window) | DSA `trade_flow.net_delta_5m / 15m / 1h` | data_schema_v1.2.0.md В§"trade_flow" | Sum of last N bars |
| Net Delta (CoinGlass) | CoinGlass Net Delta panel | heatmap_field_map.md В§2b | POSITIONING family, not flow. Best proxy: Net Longs в€’ Net Shorts (T3). Do NOT cross-validate with DSA CVD by sign |
| Open Interest | DSA `open_interest.direction`, `.change_1h_pct` | data_schema_v1.2.0.md В§"DATA BLOCK вЂ” open_interest"; heatmap_field_map.md В§2 | Direction from DSA; magnitude CoinGlass context |
| OI breakdown (retail/whale L/S) | DSA `oi_breakdown.retail.long_short_ratio`, `oi_breakdown.whale.long_short_ratio` | data_schema_v1.2.0.md В§"oi_breakdown" | Proxy вЂ” account/position ratio, not absolute OI |
| Funding rate | DSA `funding.current_rate`, `funding.extreme` | data_schema_v1.2.0.md В§"funding" | Extreme = crowded side |
| Spot/perp basis | DSA `spot_perp_basis.basis_pct`, `.direction` | data_schema_v1.2.0.md В§"spot_perp_basis" | Premium = longs pay |
| Book imbalance | DSA `conditions.book_imbalance`, `order_book_depth.bid_ask_ratio` | data_schema_v1.2.0.md В§"order_book_depth" | bid_ask_ratio |
| Volume Profile | DSA `weekly_vp`, `daily_vp`, `post_funding_vp`, `intraday_4h_vp` | data_schema_v1.2.0.md В§VP blocks; heatmap_field_map.md В§1 | Approximated from 1m OHLCV вЂ” may deviate 0.2-0.5% from CoinGlass VPVR |
| VWAP | DSA `vwap.price`, `.slope`, `.bands` | data_schema_v1.2.0.md В§"vwap" | HLC3 source, session anchor. Sigma bands are screener invention, NOT Tom |
| Liquidation clusters | DSA `liquidation_clusters.*` | heatmap_field_map.md В§2 | DEPRECATED 2026-09-12 вЂ” emits 0.0/false unconditionally. Do not use |
| Trade flow (all windows) | DSA `trade_flow.net_delta_1m / 5m / 15m / 1h` | data_schema_v1.2.0.md В§"trade_flow (updated 2026-09-11)" | вЂ” |
| Order flow speed | DSA `order_flow.trades_ratio`, `.volume_ratio`, `.speed_state` | data_schema_v1.2.0.md В§"order_flow" | DSA_TASK_013 |
| State code | MyTradingSys/mts/runtime/state_code.json | state_machine_design_2026-09-11.md В§5 | Emitted every 60s by Java child. `signals.cvd_slope` may diverge from snapshot `cvd.slope` (aggTrade vs kline) |

## CROSS-CATEGORY WARNINGS

Three family confusions that recur:

1. **Flow vs Positioning.** CVD and Volume Delta are flow. Net Long/Short and CoinGlass "Net Delta" are positioning. Never cross-validate by sign вЂ” they measure different participant behaviors.
2. **Anchor mismatch.** DSA CVD anchors at 00:00 UTC. CoinGlass CVD anchors at leftmost visible bar. Values are not comparable unless anchors match.
3. **Same name, different source.** `cvd.slope` (snapshot, kline-based) vs `signals.cvd_slope` (state_code.json, aggTrade-based). Named differently on purpose. Do not equate.

## MAINTENANCE

When a session resolves a field-level question:
1. Update the authority file with the definition.
2. Add or update the row above.
3. Do not duplicate content вЂ” the row links, the authority file defines.
4. If a field has no authority, set the cell to `[NO EVIDENCE]` and open an L-item.

# END


## PLAIN LANGUAGE RULE (added 2026-09-16)

When giving the user an update, or when providing information:
- No internal codes. No letters, no numbers, no hashes, no byte counts
  unless the count itself is the point.
- No shorthand invented in a session. If a thing has a name, use its
  full name.
- Plain sentences first. Tables only when the table saves reading.
- Any term used twice in a session must exist in this dictionary or be
  replaced with a plain phrase.

## CORE TERMS (added 2026-09-16)

These were undefined before this entry.

| term | plain meaning |
|---|---|
| MTS | MyTradingSys, the decision system in this repo |
| DSA | dropped. Use "session" or "session prompt". |
| | dropped. Write "one sourced PowerShell session in the project root". |
| nrr | net reward to risk. Spell it out in logs and cards. |
| pd | prior day bias. Spell it out in logs and cards. |
| apparatus | dropped in favor of "the runtime loop". |
| L-items | dropped in favor of "open loops". |
| A / B / E | dropped. Name the actual file or folder. |

## END OF ADDITIONS
