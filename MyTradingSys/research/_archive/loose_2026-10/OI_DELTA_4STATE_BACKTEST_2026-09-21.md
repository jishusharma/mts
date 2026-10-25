# OI Delta 4-state Backtest - 2026-09-21

Purpose: compare two classifier inputs for the same four-state OI classifier.

- delta_state (volume-delta school): sign of trade_flow.net_delta_1h
- delta_state_price (price school): current_price[now] minus current_price[nearest snapshot at or before T-60m]

Rows joined: 6362
Horizons: 30m, 60m, 120m

State counts, volume-delta school: {'aggressive_long': 926, 'aggressive_short': 1019, 'rekt_long': 1325, 'rekt_short': 1200, 'neutral': 1892}
State counts, price school: {'aggressive_long': 936, 'aggressive_short': 1009, 'rekt_long': 1065, 'rekt_short': 1460, 'neutral': 1892}

Reading: mean is percent forward return. se is day-clustered standard error (std of daily means over sqrt days).

## Volume-delta school (nd1h sign)

| state | horizon | n | days | mean pct | sd | se(day) |
|---|---|---|---|---|---|---|
| aggressive_long | 30m | 926 | 8 | +0.1024 | 0.4698 | 0.0781 |
| aggressive_long | 60m | 926 | 8 | +0.1705 | 0.6614 | 0.0929 |
| aggressive_long | 120m | 926 | 8 | +0.3060 | 0.8231 | 0.1199 |
| aggressive_short | 30m | 1019 | 8 | +0.0332 | 0.2700 | 0.0313 |
| aggressive_short | 60m | 1019 | 8 | +0.1645 | 0.5808 | 0.0981 |
| aggressive_short | 120m | 1019 | 8 | +0.5236 | 1.1877 | 0.3086 |
| rekt_long | 30m | 1325 | 9 | -0.0057 | 0.3069 | 0.0486 |
| rekt_long | 60m | 1325 | 9 | -0.0322 | 0.4418 | 0.0791 |
| rekt_long | 120m | 1325 | 9 | -0.0778 | 0.5972 | 0.0973 |
| rekt_short | 30m | 1200 | 9 | +0.0268 | 0.3117 | 0.1294 |
| rekt_short | 60m | 1200 | 9 | +0.0538 | 0.3367 | 0.1362 |
| rekt_short | 120m | 1200 | 9 | +0.0173 | 0.3915 | 0.1420 |
| neutral | 30m | 1892 | 9 | +0.0820 | 0.4165 | 0.0517 |
| neutral | 60m | 1892 | 9 | +0.1198 | 0.5873 | 0.0770 |
| neutral | 120m | 1892 | 9 | +0.2370 | 0.6757 | 0.1321 |

## Price school (close delta over 60m)

| state | horizon | n | days | mean pct | sd | se(day) |
|---|---|---|---|---|---|---|
| aggressive_long | 30m | 936 | 8 | +0.0897 | 0.4729 | 0.0743 |
| aggressive_long | 60m | 936 | 8 | +0.2070 | 0.7118 | 0.0993 |
| aggressive_long | 120m | 936 | 8 | +0.4572 | 0.9479 | 0.1365 |
| aggressive_short | 30m | 1009 | 8 | +0.0444 | 0.2646 | 0.0338 |
| aggressive_short | 60m | 1009 | 8 | +0.1306 | 0.5190 | 0.1106 |
| aggressive_short | 120m | 1009 | 8 | +0.3854 | 1.1104 | 0.3275 |
| rekt_long | 30m | 1065 | 9 | +0.0106 | 0.3316 | 0.0568 |
| rekt_long | 60m | 1065 | 9 | -0.0142 | 0.4901 | 0.0960 |
| rekt_long | 120m | 1065 | 9 | -0.0830 | 0.6617 | 0.1276 |
| rekt_short | 30m | 1460 | 9 | +0.0091 | 0.2926 | 0.1091 |
| rekt_short | 60m | 1460 | 9 | +0.0254 | 0.3125 | 0.1049 |
| rekt_short | 120m | 1460 | 9 | +0.0042 | 0.3619 | 0.1075 |
| neutral | 30m | 1892 | 9 | +0.0820 | 0.4165 | 0.0517 |
| neutral | 60m | 1892 | 9 | +0.1198 | 0.5873 | 0.0770 |
| neutral | 120m | 1892 | 9 | +0.2370 | 0.6757 | 0.1321 |

## Caveats

- Snapshot window 2026-09-13 to 2026-09-22. Hard cap.
- Price lag uses nearest snapshot at or before T-60m.
- Gauge-class fields. No verdict layer touched.
- Sample clusters on few days; se is day-clustered to reflect that. See BUGS T038.

