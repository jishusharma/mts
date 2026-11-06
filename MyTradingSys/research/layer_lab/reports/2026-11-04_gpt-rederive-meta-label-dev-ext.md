MATCH 58 | DIFF 2 | NOT_IN_DATA 0

# GPT re-derive: meta_label_dev_ext_2026-10-31 RESULT.md headline numbers

Method: Sonnet re-derivation (Codex lane stalled). The folder holds no per-trade csv and the 1m perp data is not on this laptop, so the trade-level means, day-block CIs, placebo and AUC cannot be recomputed from prices: those rows are checked as RESULT.md vs numbers.json (transcription) plus arithmetic identities. Everything derivable is recomputed independently from tercile n / mean / sd and the FORMULAS.md fee identity (net = gross - fee; section 18 taker 0.0005 per side): pooled sd, delta_min = sd*sqrt((1.96+0.8416)^2/n), n needed = ceil(7.849*sd^2/0.30^2), best-of-16 luck level sd*sqrt(2 ln 16)/sqrt(n), spreads, weighted means, trade-count sums. Not re-simulated: the trade list itself (needs F:/MTS data).

| # | row | source quote (RESULT.md) | report value | derived | status |
|---|---|---|---|---|---|
| 1 | n filled | 509 filled | 509 | 509 | MATCH |
| 2 | n model = sum terciles | 418 complete-case | 418 | 418 | MATCH |
| 3 | dropped = filled - model | 91 dropped | 91 | 91 | MATCH |
| 4 | n top | 139 | 139 | 139 | MATCH |
| 5 | n middle | 137 | 137 | 137 | MATCH |
| 6 | n bottom | 142 | 142 | 142 | MATCH |
| 7 | top mean net R | +0.430 | 0.43 | 0.43 | MATCH |
| 8 | middle mean net R | -0.355 | -0.355 | -0.355 | MATCH |
| 9 | bottom mean net R | -0.215 | -0.215 | -0.215 | MATCH |
| 10 | spread top-bottom = 0.430-(-0.215) | +0.645 | 0.645 | 0.645 | MATCH |
| 11 | random third = model-sample mean (weighted tercile means) | -0.047 | -0.047 | -0.047 | MATCH |
| 12 | model-sample sd from tercile moments | 2.144 | 2.144 | 2.143 | DIFF |
| 13 | top CI centred (lo+hi)/2 vs mean | +0.028..+0.869 | 0.4296 | 0.4487 | DIFF |
| 14 | top CI lower | +0.028 | 0.028 | 0.028 | MATCH |
| 15 | top CI upper | +0.869 | 0.869 | 0.869 | MATCH |
| 16 | top CI naive iid half-width <= day-block half-width (block wider) | day-block CI | 1 | 1 | MATCH |
| 17 | spread CI lower | +0.114 | 0.114 | 0.114 | MATCH |
| 18 | spread CI upper | +1.194 | 1.194 | 1.194 | MATCH |
| 19 | gross-fee=net top | +0.668/0.238/+0.430 | 0.43 | 0.43 | MATCH |
| 20 | gross-fee=net middle | -0.105/0.251/-0.355 | -0.355 | -0.355 | MATCH |
| 21 | gross-fee=net bottom | +0.030/0.245/-0.215 | -0.215 | -0.215 | MATCH |
| 22 | gross top | +0.668 | 0.668 | 0.668 | MATCH |
| 23 | fee top | 0.238 | 0.238 | 0.238 | MATCH |
| 24 | delta_min = sd*sqrt(7.849/139); (1.96+0.8416)^2=7.849 | 0.509 | 0.509 | 0.509 | MATCH |
| 25 | (1.96+0.8416)^2 | 7.849 | 7.849 | 7.849 | MATCH |
| 26 | n needed for 0.30 R lift = ceil(7.849*sd^2/0.09) | 401 | 401 | 401 | MATCH |
| 27 | luck best-of-16 = sd*sqrt(2 ln16)/sqrt(n_top) | 0.428 | 0.428 | 0.428 | MATCH |
| 28 | placebo p = 7/301 style (+1)/(300+1) | 0.023 | 0.023 | 0.023 | MATCH |
| 29 | Holm m=2 = 2*p | 0.047 | 0.047 | 0.047 | MATCH |
| 30 | BH q (m=2, rank1) = p*2/1 capped by rank2 p | 0.023 | 0.023 | 0.023 | MATCH |
| 31 | placebo real percentile | 98.0th | 98.0 | 98.0 | MATCH |
| 32 | placebo p95 | +0.521 | 0.521 | 0.521 | MATCH |
| 33 | same-sign: 2020 top mean | +0.336 (n 46) | 0.336 | 0.336 | MATCH |
| 34 | same-sign: 2021-22 top mean | +0.476 (n 93) | 0.476 | 0.476 | MATCH |
| 35 | 2020 spread = top - bottom | +0.340 | 0.34 | 0.34 | MATCH |
| 36 | 2021-22 spread = top - bottom | +0.833 | 0.833 | 0.833 | MATCH |
| 37 | n_top 2020+2021-22 = 139 | 46+93 | 139 | 139 | MATCH |
| 38 | pooled n_top with P0 162 | 301 | 301 | 301 | MATCH |
| 39 | week-kfold top mean | +0.056 | 0.056 | 0.056 | MATCH |
| 40 | week-kfold spread = top - bottom | +0.239 | 0.239 | 0.239 | MATCH |
| 41 | OOF AUC | 0.527 | 0.527 | 0.527 | MATCH |
| 42 | top CI 97.5 lower | -0.024 | -0.024 | -0.024 | MATCH |
| 43 | fill check: 509 checked, 0 differ | 0 differ | 0 | 0 | MATCH |
| 44 | numbers.json table rows | 24 rows | 24 | 24 | MATCH |
| 45 | rel volume low third avg R | -0.447 (n 170) | -0.447 | -0.447 | MATCH |
| 46 | rel volume low third n | 170 | 170 | 170 | MATCH |
| 47 | session US n = 509, avg R = mean_all_filled | -0.084 | -0.084 | -0.084 | MATCH |
| 48 | session row avg R | -0.084 | -0.084 | -0.084 | MATCH |
| 49 | BBWP (1h) rows sum to 509 trades | 509 | 509 | 509 | MATCH |
| 50 | BBWP (1h) n-weighted avg R = -0.084 | -0.084 | -0.084 | -0.084 | MATCH |
| 49 | D1 trend rows sum to 509 trades | 509 | 509 | 509 | MATCH |
| 50 | D1 trend n-weighted avg R = -0.084 | -0.084 | -0.084 | -0.084 | MATCH |
| 49 | Cowen band (daily close) rows sum to 509 trades | 509 | 509 | 509 | MATCH |
| 50 | Cowen band (daily close) n-weighted avg R = -0.084 | -0.084 | -0.084 | -0.084 | MATCH |
| 49 | RSI 14 (1h) rows sum to 509 trades | 509 | 509 | 509 | MATCH |
| 50 | RSI 14 (1h) n-weighted avg R = -0.084 | -0.084 | -0.084 | -0.084 | MATCH |
| 49 | WaveTrend (1h) rows sum to 509 trades | 509 | 509 | 509 | MATCH |
| 50 | WaveTrend (1h) n-weighted avg R = -0.084 | -0.084 | -0.084 | -0.084 | MATCH |
| 49 | Funding sign rows sum to 509 trades | 509 | 509 | 509 | MATCH |
| 50 | Funding sign n-weighted avg R = -0.084 | -0.084 | -0.084 | -0.084 | MATCH |

- DIFF: 12 model-sample sd from tercile moments report 2.144 derived 2.143
- DIFF: 13 top CI centred (lo+hi)/2 vs mean report 0.4296 derived 0.4487
- Trade-level rows (top mean +0.430, CIs, placebo p, AUC) are MATCH only as transcription of numbers.json; the trades behind them were not re-simulated here.
- Reading the 2 DIFF rows: row 12 is a rounding gap (derived 2.143 vs 2.144, pooled sd from tercile moments; ddof choice), all dependent numbers (delta_min 0.509, n needed 401) still MATCH. Row 13 is not an error: the day-block CI is asymmetric (centre 0.449 vs mean 0.430), a percentile-type interval is not centred on the mean.
