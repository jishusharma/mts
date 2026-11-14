# RESULT: hourly RSI extreme + confirming candle (edge-rsi-extreme-confirm-1113)

**Verdict: FAIL.** 0 of 384 pre-registered cells PASS; 0 ROBUST. BH 10% significant cells: 0 on VALIDATION, 0 on DEV.
Regime mix: BTC close vs 200d SMA (bull >+5%, bear <-5%): DEV bull 57% / bear 34% / range 9%; VALIDATION bull 62% / bear 11% / range 27%; RECENT bull 36% / bear 54% / range 10%.
Pooled universe: BTC, ETH, SOL, XRP, DOGE, BNB, ADA, LINK, LTC, AVAX (Bybit linear 1h, from listing). Fees 2 x BINANCE_TAKER from fees.py, Bybit funding, net R per trade, day-clustered.
Cells with VALIDATION n>=30: 177 of 384; with VALIDATION mean>0: 26; DEV n>=30 and mean>0: 25.
Cells with n < 30 in a split are UNDERPOWERED (T=10 has ~28 pooled trades in DEV across all buckets).

## Best DEV cells (n>=30): win rate, MAE (R), placebo p, then VALIDATION and RECENT
| side | T | bucket | stop | exit | DEV_n | DEV_mean_r | DEV_win | DEV_mae | DEV_plac_p | VAL_n | VAL_mean_r | RECENT_n | RECENT_mean_r |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| long | 20 | 0 | pct1 | time24 | 62 | 0.284 | 0.161 | 2.06 | 0.136 | 29 | -0.061 | 39 | -0.486 |
| long | 20 | 0 | atr025 | tgt2r | 58 | 0.166 | 0.466 | 1.052 | 0.098 | 22 | 0.202 | 36 | -0.299 |
| long | 15 | 2 | atr100 | time24 | 46 | 0.161 | 0.522 | 0.763 | 0.119 | 16 | -0.233 | 18 | 0.155 |
| long | 20 | 0 | low_pct1 | tgt2r | 55 | 0.149 | 0.473 | 1.006 | 0.147 | 20 | 0.32 | 36 | -0.332 |
| long | 20 | 0 | pct1 | rsi50 | 62 | 0.126 | 0.161 | 2.06 | 0.163 | 29 | -0.247 | 39 | -0.487 |
| long | 20 | 0 | atr100 | tgt2r | 54 | 0.119 | 0.537 | 0.794 | 0.204 | 18 | 0.463 | 35 | -0.247 |
| long | 15 | 2 | atr100 | tgt2r | 46 | 0.115 | 0.522 | 0.761 | 0.082 | 16 | 0.135 | 18 | 0.153 |
| long | 20 | 1 | atr025 | time24 | 199 | 0.077 | 0.387 | 1.166 | 0.114 | 79 | 0.196 | 89 | -0.042 |
| long | 20 | 1 | low_pct1 | time24 | 192 | 0.071 | 0.458 | 1.03 | 0.115 | 78 | 0.167 | 85 | -0.026 |
| long | 15 | 2 | pct1 | tgt2r | 53 | 0.067 | 0.396 | 1.351 | 0.075 | 18 | -0.264 | 20 | -0.183 |

## Which stop works best (daily bucket pooled, descriptive, mean net R averaged over T)
| side | stop | exit | DEV_mean_r | VAL_mean_r | RECENT_mean_r |
|---|---|---|---|---|---|
| long | atr025 | rsi50 | -0.078 | 0.033 | -0.139 |
| long | atr025 | tgt2r | -0.055 | 0.033 | -0.153 |
| long | atr025 | time24 | -0.034 | 0.065 | -0.184 |
| long | atr100 | rsi50 | -0.047 | 0.133 | -0.076 |
| long | atr100 | tgt2r | -0.023 | 0.162 | -0.053 |
| long | atr100 | time24 | -0.015 | 0.125 | -0.066 |
| long | low_pct1 | rsi50 | -0.055 | 0.19 | -0.144 |
| long | low_pct1 | tgt2r | -0.008 | 0.228 | -0.156 |
| long | low_pct1 | time24 | -0.012 | 0.203 | -0.178 |
| long | pct1 | rsi50 | -0.426 | -0.203 | -0.263 |
| long | pct1 | tgt2r | -0.215 | -0.299 | -0.262 |
| long | pct1 | time24 | -0.338 | -0.189 | -0.36 |
| short | atr025 | rsi50 | -0.226 | -0.226 | 0.069 |
| short | atr025 | tgt2r | -0.172 | -0.228 | -0.012 |
| short | atr025 | time24 | -0.252 | -0.204 | 0.049 |
| short | atr100 | rsi50 | -0.202 | -0.179 | 0.023 |
| short | atr100 | tgt2r | -0.175 | -0.165 | 0.099 |
| short | atr100 | time24 | -0.221 | -0.162 | 0.033 |
| short | low_pct1 | rsi50 | -0.177 | -0.252 | 0.063 |
| short | low_pct1 | tgt2r | -0.151 | -0.201 | 0.117 |
| short | low_pct1 | time24 | -0.199 | -0.214 | 0.086 |
| short | pct1 | rsi50 | -0.482 | -0.47 | 0.357 |
| short | pct1 | tgt2r | -0.332 | -0.38 | 0.055 |
| short | pct1 | time24 | -0.491 | -0.439 | 0.395 |

## By threshold T, long, daily bucket pooled
| T | DEV_n | DEV_mean_r | VAL_n | VAL_mean_r | RECENT_n | RECENT_mean_r |
|---|---|---|---|---|---|---|
| 10 | 27.75 | -0.087 | 6.0 | 0.365 | 10.75 | -0.444 |
| 15 | 137.583 | -0.099 | 56.75 | 0.18 | 61.0 | -0.115 |
| 20 | 604.083 | -0.099 | 219.917 | -0.143 | 257.75 | -0.041 |
| 25 | 1849.667 | -0.151 | 612.083 | -0.242 | 792.25 | -0.078 |

## BTC alone, long T=15, bucket pooled (small n; descriptive)
| stop | exit | DEV_btc_n | DEV_btc_mean_r | VAL_btc_n | VAL_btc_mean_r | RECENT_btc_n | RECENT_btc_mean_r |
|---|---|---|---|---|---|---|---|
| atr025 | tgt2r | 22 | -0.075 | 3 | -0.505 | 5 | -0.337 |
| atr025 | rsi50 | 22 | -0.051 | 3 | -0.612 | 5 | -0.937 |
| atr025 | time24 | 22 | 0.003 | 3 | -0.505 | 5 | -0.937 |
| atr100 | tgt2r | 21 | 0.218 | 3 | 0.491 | 5 | -0.781 |
| atr100 | rsi50 | 21 | 0.174 | 3 | 0.596 | 5 | -0.781 |
| atr100 | time24 | 21 | 0.326 | 3 | 0.946 | 5 | -0.781 |
| pct1 | tgt2r | 24 | -0.107 | 3 | -0.1 | 6 | -0.597 |
| pct1 | rsi50 | 24 | -0.365 | 3 | 0.2 | 6 | -1.097 |
| pct1 | time24 | 24 | -0.225 | 3 | 0.497 | 6 | -1.097 |
| low_pct1 | tgt2r | 21 | 0.215 | 3 | 0.547 | 5 | -0.8 |
| low_pct1 | rsi50 | 21 | 0.138 | 3 | 0.49 | 5 | -0.8 |
| low_pct1 | time24 | 21 | 0.281 | 3 | 0.812 | 5 | -0.8 |

Full per-cell table: cells.csv (bucket=-1 rows are the pooled-bucket descriptive view, not in BH).
Limitations: no slippage term; placebo trades are not position-constrained; stop-first on same-bar touches; short daily buckets mirrored (OURS).
Best next test: none close. The one positive pocket (T=25, daily RSI<30, VALIDATION about +0.3R, n 32-51) is negative in DEV and RECENT.
