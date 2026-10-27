# CoinGlass BTCUSDT 30m OI/panel stack — near-dup, closed 2026-10-27
Prior: cset_2026-10-27_coss_multi_tf.md
Shot: 90dcd58fdb90 (30m). This is the 2nd 30m frame from the 15:51Z multi-TF set; its values are the same 30m the set already read under df0d0a3a182b.
Operator: loose-end shot from the multi-TF set, now closed to clear the overdue queue.

## Read (dup of df0d0a3a182b in the multi-TF set)
| metric | value on this 30m | set df0d value |
|---|---|---|
| RSI(14) | 65.67 (SMA 54.58) | 65.67 |
| StochRSI K | 94.50 (SMA 84.58) | 94.50 |
| OI (candles) | 97.25K / 96.95K | 96.95K (last closed) |
| CVD | -7.95K / -7.89K | -7.95K |
| Net Delta | -10.33K | -10.33K |
| price | 80,548 above 80,250 | same |

Same 30m, one bar later (OI/CVD ticked ~0.3K). No new information; the multi-TF verdict stands (30m StochRSI overbought, all TFs agree up).

## Claim row
| id | class | claim | data check |
|---|---|---|---|
| 90dcd58fdb90 | MATCH | 30m RSI 65.67, StochRSI K 94.50, OI 96.95K, price above 80,250 — identical to df0d0a3a182b | dup frame; values match the multi-TF set's 30m row; OI/CVD digits chart-only (NOT_IN_DATA on the set's OI/CVD row) |

## Disposition
Near-dup of df0d0a3a182b, closed to clear the overdue queue; no new falsifier tested.
