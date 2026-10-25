# VPIN Proxy - 2026-10-10

Pre-registration: research/_archive/loose_2026-10/PRE_REG_VPIN_PROXY_2026-10-10.md
Input: 1m kline volume and taker_buy_volume. Not true VPIN (aggTrades archive empty).
Bucket V=2500 BTC. Rolling 50 buckets. Spike = VPIN above 180-day 90th percentile.

Spikes: 2530
Baseline bars: 580260

## Pooled

| measure | spike mean | baseline mean | diff | t (Welch) |
|---|---|---|---|---|
| abs_1h | +0.4812 | +0.2965 | +0.1847 | +17.14 |
| abs_4h | +0.7976 | +0.6026 | +0.1950 | +12.69 |
| adv_60 | +0.7722 | +0.4576 | +0.3146 | +18.31 |

## Per regime

| regime | measure | spike n | spike mean | baseline mean | diff | t |
|---|---|---|---|---|---|---|
| trend_up | abs_1h | 480 | +0.4151 | +0.2965 | +0.1185 | +3.64 |
| trend_up | abs_4h | 480 | +0.6184 | +0.6026 | +0.0158 | +0.49 |
| trend_up | adv_60 | 480 | +0.7822 | +0.4576 | +0.3245 | +4.42 |
| trend_down | abs_1h | 1732 | +0.4903 | +0.2965 | +0.1938 | +16.69 |
| trend_down | abs_4h | 1732 | +0.8455 | +0.6026 | +0.2429 | +12.85 |
| trend_down | adv_60 | 1732 | +0.7637 | +0.4576 | +0.3061 | +22.82 |
| range | abs_1h | 318 | +0.5316 | +0.2965 | +0.2351 | +7.88 |
| range | abs_4h | 318 | +0.8071 | +0.6026 | +0.2045 | +4.83 |
| range | adv_60 | 318 | +0.8037 | +0.4576 | +0.3461 | +10.48 |

## Walk-forward folds

Fold 1: spikes 843
  abs_1h: mean +0.5599 diff +0.2633 t +10.67
  adv_60: mean +0.9548 diff +0.4972 t +10.90
Fold 2: spikes 1686
  abs_1h: mean +0.4942 diff +0.1977 t +13.76
  adv_60: mean +0.8176 diff +0.3600 t +14.71
Fold 3: spikes 2530
  abs_1h: mean +0.4812 diff +0.1847 t +17.14
  adv_60: mean +0.7722 diff +0.3146 t +18.31

