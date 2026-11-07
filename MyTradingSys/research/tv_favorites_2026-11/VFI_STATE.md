# VFI state, BTCUSDT (Bybit linear public klines), last 90 days - descriptive, n printed, no verdict

Generated 2026-11-07 15:18Z. Engine: layers/vfi/vfi.py, FORMULAS s32, LazyBear defaults length 130, coef 0.2, vcoef 2.5, stdev 30, smoothing 3 (SOURCED). Sign and zero cross use the raw vfi. The last bar of each series is partial and excluded. TradingView check by Lead C is pending (FORMULAS s32.1 lists what to compare).

## 1d: n = 90 bars with a defined vfi (2026-08-09 00:00Z to 2026-11-06 00:00Z), 360 bars fetched in total
- vfi > 0 on 38 of 90 bars = 42.2%; last vfi +8.518 (smoothed +10.983)
- zero crosses in the window n = 6; last 5 (raw vfi sign change; close move over the next 12 bars):
  - 2026-08-27 00:00Z  vfi -1.734 -> +0.133 (up)  next-12-bar move -2.22%
  - 2026-08-28 00:00Z  vfi +0.133 -> -2.363 (down)  next-12-bar move +0.58%
  - 2026-10-04 00:00Z  vfi -0.816 -> +0.641 (up)  next-12-bar move -5.67%
  - 2026-10-08 00:00Z  vfi +0.666 -> -0.736 (down)  next-12-bar move +1.56%
  - 2026-10-09 00:00Z  vfi -0.736 -> +1.436 (up)  next-12-bar move +1.79%

## 15m: n = 8640 bars with a defined vfi (2026-08-09 15:15Z to 2026-11-07 15:00Z), 8910 bars fetched in total
- vfi > 0 on 3966 of 8640 bars = 45.9%; last vfi +4.844 (smoothed +5.881)
- zero crosses in the window n = 310; last 5 (raw vfi sign change; close move over the next 12 bars):
  - 2026-11-07 00:15Z  vfi -0.518 -> +2.328 (up)  next-12-bar move +0.08%
  - 2026-11-07 00:30Z  vfi +2.328 -> -0.671 (down)  next-12-bar move -0.16%
  - 2026-11-07 01:15Z  vfi -1.620 -> +0.114 (up)  next-12-bar move -0.05%
  - 2026-11-07 04:00Z  vfi +0.929 -> -1.207 (down)  next-12-bar move +0.20%
  - 2026-11-07 06:15Z  vfi -0.057 -> +1.150 (up)  next-12-bar move +0.02%
- Friday 2026-11-06 15:00Z sweep bar (15m open time; high 75819.5 low 74810.0 close 75809.1 volume 7360.4): vfi -20.963, smoothed -19.774
- the 20 bars before it, then the sweep bar (open time, close, raw vfi, change vs the previous bar):
  - 2026-11-06 10:00Z  close 76144.6  vfi -16.892  -0.281
  - 2026-11-06 10:15Z  close 76138.4  vfi -17.947  -1.055
  - 2026-11-06 10:30Z  close 76195.0  vfi -17.748  +0.199
  - 2026-11-06 10:45Z  close 76026.3  vfi -17.816  -0.068
  - 2026-11-06 11:00Z  close 75958.3  vfi -18.095  -0.279
  - 2026-11-06 11:15Z  close 76084.5  vfi -17.874  +0.221
  - 2026-11-06 11:30Z  close 76132.5  vfi -17.602  +0.271
  - 2026-11-06 11:45Z  close 76116.9  vfi -18.090  -0.488
  - 2026-11-06 12:00Z  close 76095.6  vfi -18.803  -0.713
  - 2026-11-06 12:15Z  close 76308.9  vfi -17.962  +0.841
  - 2026-11-06 12:30Z  close 76188.4  vfi -17.913  +0.049
  - 2026-11-06 12:45Z  close 76006.2  vfi -18.000  -0.087
  - 2026-11-06 13:00Z  close 75880.2  vfi -20.103  -2.102
  - 2026-11-06 13:15Z  close 76014.7  vfi -19.254  +0.849
  - 2026-11-06 13:30Z  close 75778.3  vfi -21.311  -2.057
  - 2026-11-06 13:45Z  close 75864.7  vfi -20.008  +1.303
  - 2026-11-06 14:00Z  close 75569.1  vfi -21.437  -1.429
  - 2026-11-06 14:15Z  close 75599.7  vfi -21.691  -0.254
  - 2026-11-06 14:30Z  close 75714.4  vfi -19.338  +2.353
  - 2026-11-06 14:45Z  close 75511.4  vfi -19.021  +0.317
  - 2026-11-06 15:00Z  close 75809.1  vfi -20.963  -1.942  <- sweep bar
- over those 20 bars vfi went -16.892 -> -19.021 (change -2.129); it fell on 10 of the 19 steps (n = 19, descriptive, no verdict)
