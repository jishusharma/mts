# WaveTrend 15m / 30m event read (operator 2026-11-10, 21Z chat)

**Result: plain WaveTrend crosses on 15m and 30m are a coin flip (50 %). Three shapes tilt price 5-10 bp on 15m. That is at or below the 0.10 % round-trip fee, so they set the context, not a trade by themselves.** This is a descriptive count: no PRE_REG, no holdout, not a trading claim. It agrees with wt_extreme_cross_2026-11 (bounce excess smaller than fees) and wt_mtf_nesting (FAIL).

| Field | Value |
|---|---|
| Data | Binance spot BTCUSDT, 2026-05-13 to 2026-11-10 (180 days) |
| Bars | 17,280 on 15m, 8,640 on 30m |
| WaveTrend | LazyBear: n1 10, n2 21, wt2 = 4-bar SMA, hot/cold 53 (SOURCED) |
| Script | `wt_events.py` |

| Event (15m) | n | Up after 2 h | Up after 4 h | Median at 4 h |
|---|---|---|---|---|
| All bars (baseline) | 17,280 | 50.2 % | 50.4 % | about 0 |
| Any up cross | 1,295 | 49.9 % | 51.3 % | +0.9 bp |
| Up cross from oversold (wt1 ≤ -53) | 165 | 53.3 % | 50.9 % | +1.6 bp |
| Down cross from overbought (wt1 ≥ 53), "kicked down at 60" | 156 | 44.9 % | 45.5 % | -6.9 bp |
| Zero-line hold: up cross at wt1 -15 to +5 after wt1 ≥ 20 within 12 bars | 101 | 53.5 % | 56.4 % | +7.4 bp |
| Oscillator higher low: up cross below 0, higher than the last one | 384 | 55.7 % | 57.0 % | +9.7 bp |

On 30m the same shapes are weaker or flip, with smaller samples:
- Zero-line hold: n 49, up 34.7 % at 4 h.
- Higher low: n 198, up 51.5 % at 4 h.

Use them on 15m. Read 30m only as the bigger swing.

OURS: the zero-hold band (-15 to +5, recent ≥ 20) and the higher-low rule. They are not tuned, but five shapes were looked at, so treat these as leads to test.
