# Output of run_ext.py (Fabio Model C price-only stand-in (ours), pre-DEV window 2020-01-02..2022-03-31)

Best third by filter: +0.430 R (range +0.028..+0.869) vs random third: -0.047 R -> PASSED

Holm placebo p 0.047 (m = 2), BH q 0.023

| layer reading | trades | win % | average R after fees |
|---|---|---|---|
| BBWP (1h): not available | 2 | 100.0 | +2.573 |
| BBWP (1h): compression, 30 or below | 117 | 27.4 | -0.070 |
| BBWP (1h): normal, 30 to 85 | 300 | 30.7 | -0.072 |
| BBWP (1h): expansion, 85 or above | 90 | 24.4 | -0.203 |
| D1 trend: not available | 34 | 29.4 | +0.196 |
| D1 trend: up (close above 50-day average) | 284 | 29.6 | -0.116 |
| D1 trend: down (close below 50-day average) | 191 | 28.3 | -0.087 |
| Cowen band (daily close): not available | 91 | 24.2 | -0.257 |
| Cowen band (daily close): above the band | 299 | 30.4 | -0.109 |
| Cowen band (daily close): inside the band | 14 | 28.6 | +0.110 |
| Cowen band (daily close): below the band | 105 | 29.5 | +0.109 |
| Funding sign: positive | 455 | 27.5 | -0.122 |
| Funding sign: negative | 54 | 42.6 | +0.236 |
| Session (UTC): US, 13-21 | 509 | 29.1 | -0.084 |
| RSI 14 (1h): middle, 40 to 60 | 287 | 31.4 | -0.001 |
| RSI 14 (1h): high, 60 or above | 142 | 21.1 | -0.359 |
| RSI 14 (1h): low, 40 or below | 80 | 35.0 | +0.104 |
| WaveTrend (1h): not available | 5 | 40.0 | +0.328 |
| WaveTrend (1h): middle | 397 | 29.2 | -0.070 |
| WaveTrend (1h): overbought | 74 | 24.3 | -0.161 |
| WaveTrend (1h): oversold | 33 | 36.4 | -0.145 |
| Relative volume (1h): middle third | 169 | 32.0 | +0.173 |
| Relative volume (1h): high third | 170 | 30.6 | +0.022 |
| Relative volume (1h): low third | 170 | 24.7 | -0.447 |

