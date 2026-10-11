# OI Divergence Backtest - 2026-10-10

Purpose: test price-vs-OI divergence as a directional signal over the full 28-day snapshot window.

Method: for each BTCUSDT snapshot take the nearest at or before T-60m.
price_delta = current_price now minus current_price 1h ago.
oi_pct = snapshot open_interest.change_1h_pct (1-hour OI percent change).

States (sign of price_delta, sign of oi_pct):
- confirm_long      (+ +) : price up, OI up. New longs.
- divergence_bearish(+ -) : price up, OI down. Short covering, weak rally.
- divergence_bullish(- +) : price down, OI up. New shorts.
- confirm_short     (- -) : price down, OI down. Long liquidation.
- flat_price        (0 *) : no price move.
- flat_oi           (* 0) : no OI move.
- neutral           (0 0) : both flat.

Rows joined: 21379
State counts: {'confirm_long': 2921, 'divergence_bearish': 4200, 'divergence_bullish': 3126, 'confirm_short': 3542, 'flat_price': 3, 'flat_oi': 7584, 'neutral': 3}
Horizons: 30m, 60m, 120m

Reading: mean is percent forward return. se is day-clustered standard error.

| state | horizon | n | days | mean pct | sd | se(day) |
|---|---|---|---|---|---|---|
| confirm_long | 30m | 2921 | 17 | +0.0172 | 0.3354 | 0.0364 |
| confirm_long | 60m | 2921 | 17 | +0.0242 | 0.5275 | 0.0673 |
| confirm_long | 120m | 2921 | 17 | +0.0382 | 0.7366 | 0.1049 |
| divergence_bearish | 30m | 4200 | 18 | -0.0110 | 0.3665 | 0.0462 |
| divergence_bearish | 60m | 4200 | 18 | -0.0036 | 0.4633 | 0.0725 |
| divergence_bearish | 120m | 4200 | 18 | +0.0366 | 0.5475 | 0.0875 |
| divergence_bullish | 30m | 3126 | 17 | +0.0324 | 0.2572 | 0.0317 |
| divergence_bullish | 60m | 3126 | 17 | +0.0634 | 0.3968 | 0.0653 |
| divergence_bullish | 120m | 3126 | 17 | +0.1185 | 0.7704 | 0.1699 |
| confirm_short | 30m | 3542 | 18 | +0.0215 | 0.3395 | 0.0286 |
| confirm_short | 60m | 3542 | 18 | +0.0146 | 0.4838 | 0.0515 |
| confirm_short | 120m | 3542 | 18 | +0.0253 | 0.6445 | 0.0886 |
| flat_price | 30m | 3 | 3 | +0.2578 | 0.2816 | 0.1626 |
| flat_price | 60m | 3 | 3 | +1.1631 | 1.4253 | 0.8229 |
| flat_price | 120m | 3 | 3 | +1.2220 | 1.7172 | 0.9914 |
| flat_oi | 30m | 7584 | 17 | +0.0087 | 0.3120 | 0.0286 |
| flat_oi | 60m | 7584 | 17 | +0.0160 | 0.4329 | 0.0555 |
| flat_oi | 120m | 7584 | 17 | +0.0275 | 0.6036 | 0.0982 |
| neutral | 30m | 3 | 3 | +0.1496 | 0.1043 | 0.0602 |
| neutral | 60m | 3 | 3 | +0.1480 | 0.0857 | 0.0495 |
| neutral | 120m | 3 | 3 | +0.2223 | 0.2254 | 0.1301 |

## Caveats

- Snapshot window 2026-09-12 to 2026-10-10. ~28 days.
- Lag uses nearest snapshot at or before T-60m.
- OI is the snapshot's own change_1h_pct, not an absolute OI level.
- Gauge-class fields. No verdict layer touched.
- Predecessor report: OI_DELTA_4STATE_BACKTEST_2026-09-21.md (9 days, 6362 rows).

