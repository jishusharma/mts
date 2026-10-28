# HEATMAP FIELD MAP
# Version: 1.0.0 | Date: 2026-09-13
# Purpose: Map CoinGlass heatmap reads to DSA JSON fields. Context only.
# Authority: VVP-002 Section B. Never a trigger. Never overrides Tier 1.
# Every field path below is from data_schema_v1.2.0. No invented fields.

## 1. WHAT THE HEATMAP SHOWS (VISUAL)

- Cluster price: nearest visible cluster above and below current_price.
- Density: qualitative (thick / medium / thin). No numeric threshold — DSA does not emit density.
- Thin zones: areas of low or missing heatmap color.
- Color convention (CoinGlass, not Tom): typically distinguishes long-liq vs short-liq concentration. Do not translate colors into JSON fields; DSA does not emit color.
- Methodology: CoinGlass heatmap is a black-box leverage-estimation model (methodology undisclosed); Glassnode (Hyperliquid on-chain positions) is the transparent comparator. Both remain context-only per § 5.

## 2. DSA FIELDS THAT CORROBORATE (exact paths)

| Heatmap read | DSA field | Notes |
|--------------|-----------|-------|
| Cluster formation / buildup | open_interest.direction | rising + cluster = positioning build |
| Cluster unwind | open_interest.direction | falling + cluster = unwind |
| Magnitude of buildup | open_interest.change_1h_pct | percent change |
| Crowded side | funding.current_rate, funding.extreme | extreme funding = crowded side |
| Premium/discount context | spot_perp_basis.basis_pct, spot_perp_basis.direction | premium = longs pay, discount = shorts pay |
| Liquidation clusters | liquidation_clusters.nearest_above.price, liquidation_clusters.nearest_below.price, liquidation_clusters.warning | DEPRECATED 2026-09-12 — emits 0.0 / false unconditionally. Treat as not-live. |

## 2b. COINGLASS PANELS — CVD, VOLUME DELTA, NET DELTA (added 2026-09-15)

Authority: `MyTradingSys\market_data\data_schema_v1.2.0.md` §"trade_flow" lines 519-575.
This section is a pointer, not a duplicate. If the schema changes, that file wins.

Three distinct CoinGlass concepts, three different things:

| CoinGlass label | Category | What it measures | DSA equivalent |
|---|---|---|---|
| Cumulative Volume Delta (CVD) | Flow, cumulative | taker buy − taker sell, accumulated | `cvd.value`, `cvd.slope` (session-anchored 00:00 UTC) |
| Volume Delta (per-bar) | Flow, per-bar | taker buy − taker sell for one bar | `trade_flow.net_delta_1m` (DSA name differs) |
| Net Delta (chart panel) | Positioning | Long Opens − Long Closes / Short Opens − Short Closes — NOT flow | No direct DSA field. Closest: `oi_breakdown.retail.long_short_ratio` and `oi_breakdown.whale.long_short_ratio` (proxy) |

Naming warning: DSA `net_delta_*` is NOT CoinGlass "Net Delta." It matches CoinGlass "Volume Delta" summed over N bars. Confirmed schema v1.2.0 lines 533-539.

**The common question: why can CVD be positive while Net Delta is negative?**
They are different categories. Flow (CVD, Volume Delta) and positioning (Net Delta) are orthogonal. CVD positive + Net Delta negative = aggressive buying over the session while positioning skews short. That is the distribution signature — buyers lifting offers while new shorts open above. Not a contradiction.

**Anchor warning (schema lines 545-575):** DSA CVD anchors at 00:00 UTC. CoinGlass Cum CVD anchors at the leftmost visible bar. Same moment, different values. Never compare numerically unless both anchors match. Directional sign may differ by offset — do not cross-validate by sign.
## 3. DSA FIELDS THAT DO NOT EXIST

The following would be needed to fully corroborate a heatmap but are not emitted:

| Missing field | Status | Why |
|---------------|--------|-----|
| Heatmap cluster price (exact) | NOT EMITTED | Visual only |
| Heatmap cluster density | NOT EMITTED | Visual only |
| Heatmap color per cluster | NOT EMITTED | Visual only |
| Liquidation cluster price (live) | DEPRECATED | Endpoint 404, see 02a_CURRENT_STATUS |
| Liquidation cluster size | DEPRECATED | Same |

Do NOT infer these from any other field.

## 4. CROSS-CHECK RULE (VVP-002 Section B.3, B.5)

1. Read heatmap clusters visually.
2. For each cluster, check open_interest.direction and funding.extreme on the same timeframe label.
3. If DSA confirms (OI rising + funding extreme on the crowded side) → corroboration. Heatmap adds confidence to a setup already validated by Tier 1 indicators. No verdict change.
4. If DSA contradicts → tag per VVP-002 Section G exact string. Do not override Tier 1.
5. liquidation_clusters.* MUST be reported as NOT LIVE. If any value is non-zero, flag as unexpected and report — do not act.

## 5. HARD RULES

- Heatmap is context only. Never a trigger. (VVP-002 B.5)
- Never overrides any VVP-001 Section 4 Tier 1 read.
- Never overrides any VVP-001 Section 3.4 priority hierarchy decision.
- If heatmap and Tier 1 disagree, Tier 1 wins.

# END
