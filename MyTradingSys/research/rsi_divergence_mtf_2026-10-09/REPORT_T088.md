# T089 RSI divergence on every timeframe (+ T091 operator long-range column)

Data: BTCUSDT 1m 2022-01-01 .. 2026-10-07, resampled per registry. RSI 14. Fees: one taker round trip 0.10% deducted from every event (fees.py). Primary horizon 10 bars; verdict needs >= 300 events, net > 0, t >= 2.0, gross above same-side drift, net > 0 in half the years. Malkan column = sourced 3-10 bar rule; operator column = T091 11-60 bar non-adjacent idea (NO-SOURCE).

| TF | Column | Kind | Events | n@h | Gross | Drift (side) | Net | t | Hit net | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| 4m | malkan | bullish | 7097 | 7097 | +0.002% | +0.002% | -0.098% | -17.68 | 37.3% | no edge |
| 4m | malkan | bearish | 7393 | 7393 | -0.006% | -0.002% | -0.106% | -19.90 | 36.5% | no edge |
| 4m | operator | bullish | 4270 | 4270 | -0.003% | +0.002% | -0.103% | -14.21 | 37.7% | no edge |
| 4m | operator | bearish | 4545 | 4545 | +0.000% | -0.002% | -0.100% | -15.05 | 38.0% | no edge |
| 3h | malkan | bullish | 168 | 168 | +0.184% | +0.084% | +0.084% | 0.30 | 53.6% | insufficient n |
| 3h | malkan | bearish | 208 | 208 | -0.411% | -0.084% | -0.511% | -2.30 | 47.6% | insufficient n |
| 3h | operator | bullish | 94 | 94 | +0.238% | +0.084% | +0.138% | 0.48 | 56.4% | insufficient n |
| 3h | operator | bearish | 106 | 106 | -0.046% | -0.084% | -0.146% | -0.53 | 45.3% | insufficient n |
| 7h | malkan | bullish | 70 | 70 | -0.147% | +0.171% | -0.247% | -0.51 | 50.0% | insufficient n |
| 7h | malkan | bearish | 113 | 113 | -0.295% | -0.171% | -0.395% | -0.97 | 46.9% | insufficient n |
| 7h | operator | bullish | 46 | 46 | +1.191% | +0.171% | +1.091% | 2.11 | 69.6% | insufficient n |
| 7h | operator | bearish | 56 | 56 | -0.284% | -0.171% | -0.384% | -1.03 | 46.4% | insufficient n |
| 7h_epoch | malkan | bullish | 56 | 56 | +0.392% | +0.201% | +0.292% | 0.43 | 58.9% | insufficient n |
| 7h_epoch | malkan | bearish | 104 | 104 | -0.712% | -0.201% | -0.812% | -1.74 | 38.5% | insufficient n |
| 7h_epoch | operator | bullish | 41 | 41 | +0.565% | +0.201% | +0.465% | 0.72 | 56.1% | insufficient n |
| 7h_epoch | operator | bearish | 45 | 44 | -0.350% | -0.201% | -0.450% | -0.77 | 47.7% | insufficient n |

## Net mean at the primary horizon by year (events with >= 30 per cell shown as n/net)

| TF | Column | Kind | 2022 | 2023 | 2024 | 2025 | 2026 |
|---|---|---|---|---|---|---|---|
| 4m | malkan | bullish | 1508/-0.100% | 1398/-0.091% | 1419/-0.091% | 1580/-0.105% | 1192/-0.103% |
| 4m | malkan | bearish | 1469/-0.100% | 1464/-0.121% | 1599/-0.128% | 1629/-0.085% | 1232/-0.092% |
| 4m | operator | bullish | 841/-0.099% | 888/-0.098% | 867/-0.096% | 959/-0.105% | 715/-0.121% |
| 4m | operator | bearish | 908/-0.081% | 871/-0.124% | 983/-0.104% | 1032/-0.093% | 751/-0.097% |
| 3h | malkan | bullish | 39/-0.900% | 39/+0.279% | 34/+0.639% | 26/+0.475% | 30/+0.142% |
| 3h | malkan | bearish | 37/+0.288% | 38/-0.736% | 63/-0.986% | 44/+0.029% | 26/-1.077% |
| 3h | operator | bullish | 21/+0.753% | 20/-0.282% | 14/+0.374% | 24/-0.075% | 15/-0.043% |
| 3h | operator | bearish | 8/+1.021% | 31/-1.180% | 29/+0.751% | 21/-0.233% | 17/-0.230% |
| 7h | malkan | bullish | 20/-1.755% | 13/+1.940% | 9/-0.911% | 16/+0.438% | 12/-0.516% |
| 7h | malkan | bearish | 16/+1.256% | 31/-1.355% | 27/+0.024% | 24/+0.032% | 15/-1.610% |
| 7h | operator | bullish | 10/+1.532% | 11/+1.832% | 8/+1.339% | 9/+0.172% | 8/+0.309% |
| 7h | operator | bearish | 4/+0.593% | 18/-0.092% | 16/+0.024% | 8/-2.006% | 10/-0.658% |
| 7h_epoch | malkan | bullish | 15/-1.896% | 10/+2.434% | 8/+0.250% | 15/+1.361% | 8/-0.241% |
| 7h_epoch | malkan | bearish | 16/+0.446% | 25/-1.319% | 30/-1.187% | 18/-1.008% | 15/-0.320% |
| 7h_epoch | operator | bullish | 14/+1.651% | 8/+0.521% | 5/-0.564% | 11/-0.805% | 3/+1.149% |
| 7h_epoch | operator | bearish | 5/+3.596% | 14/-0.657% | 12/-2.093% | 5/-1.286% | 8/+0.373% |
