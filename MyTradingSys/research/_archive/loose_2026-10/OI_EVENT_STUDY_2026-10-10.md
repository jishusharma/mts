# OI Divergence Event Study - 2026-10-10

Method: event study. Single asset (BTCUSDT).
Event bearish_div: 1h price change > +0.30% AND OI 1h change < 0.
Event bullish_div: 1h price change < -0.30% AND OI 1h change > 0.
Forward return measured at 30m, 60m, 120m from the label file.
Abnormal return = raw forward return minus the unconditional mean at the same horizon.
Dedup: at least 60 minutes between events of the same type.

Baseline unconditional means: 30m=+0.0116, 60m=+0.0202, 120m=+0.0439

## bearish_div (n=66)

| horizon | n | days | raw mean | abn mean | sd | se(day) | t |
|---|---|---|---|---|---|---|---|
| 30m | 66 | 17 | -0.0247 | -0.0363 | 0.4711 | 0.0557 | -0.65 |
| 60m | 66 | 17 | -0.0401 | -0.0602 | 0.5641 | 0.0575 | -1.05 |
| 120m | 66 | 17 | -0.0328 | -0.0767 | 0.6644 | 0.0876 | -0.88 |

## bullish_div (n=48)

| horizon | n | days | raw mean | abn mean | sd | se(day) | t |
|---|---|---|---|---|---|---|---|
| 30m | 48 | 15 | +0.0828 | +0.0711 | 0.2957 | 0.0583 | +1.22 |
| 60m | 48 | 15 | +0.1002 | +0.0801 | 0.3802 | 0.0821 | +0.98 |
| 120m | 48 | 15 | +0.2111 | +0.1672 | 0.7583 | 0.1861 | +0.90 |

## Caveats

- Snapshot window 2026-09-12 to 2026-10-10. ~28 days.
- OI signal is the snapshot change_1h_pct, quantized to 0.01.
- Baseline is unconditional mean forward return over the same window.
- Day-clustered se. t is abn mean / se.
- Predecessor: OI_DIVERGENCE_2026-10-10.md (state table, no edge).

