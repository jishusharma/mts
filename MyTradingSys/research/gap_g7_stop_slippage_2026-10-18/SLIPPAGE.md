# G7 stop-slippage proxy, BTCUSDT (card gap-g7-stop-slippage)

Trust tag: UNCHECKED. Binance USD-M BTCUSDT aggTrades trade-through / latency proxy: no own order size, not Deribit (REPORT G8). DEV days only (all before 2024-07-01); VALIDATION and HOLDOUT not read.

## Method (defaults labelled OURS)

- Stop levels (OURS): every round-100 USD level; an event = one up or down crossing of a level between consecutive trades (reversals and chop at a level each count; events cluster inside a day, hence the day-level bootstrap).
- Slip = adverse signed (price - level) in crossing direction / level, bp. delta 0 = the crossing trade itself (first trade at or beyond the level, tick-bounded optimistic bound). delta 250 / 1000 ms (OURS) = last trade at or before t_cross + delta (a stop-market fills after trigger-to-order latency); signed, reversals kept; events within delta of the last trade of the day are dropped.
- R = slip_bp / 40 at the 0.40 % stop (0.20 / 0.80 % columns in summary.json: R scales 2x / 0.5x).
- Buckets (OURS): terciles of DEV daily range % of BTCUSDT 1m klines (F:/MTS/data/tom_raw, 912 complete days 2022-01-01..2024-06-30; ties go to the higher bucket). Range % spans: low [0.374, 2.71], mid [2.719, 4.497], high [4.504, 20.388].
- Days (OURS): 4 evenly spaced days per tercile (12 days; days.csv holds range %, zip sha256 checked against the Binance .CHECKSUM). Extension rule (events < 500 per bucket -> next 4 days, cap 8): not triggered (every bucket far above 500 events). No aggTrades zip kept; no raw committed.
- Bootstrap (OURS): 1000 day-level resamples, seed 20261030, 2.5-97.5 percentile of the bucket median.

## Result

| bucket | delta ms | n events | n days | median bp | p90 bp | mean bp | share exactly 0 | boot range of median (bp) | median R @0.40% | p90 R @0.40% |
|---|---|---|---|---|---|---|---|---|---|---|
| low | 0 | 7489 | 4 | 0.000 | 0.622 | 0.422 | 83.7% | 0.000 to 0.000 | 0.0000 | 0.0155 |
| low | 250 | 7489 | 4 | 0.000 | 1.295 | 0.121 | 36.5% | 0.000 to 0.000 | 0.0000 | 0.0324 |
| low | 1000 | 7489 | 4 | 0.000 | 2.010 | 0.139 | 28.5% | 0.000 to 0.000 | 0.0000 | 0.0503 |
| mid | 0 | 20186 | 4 | 0.000 | 0.427 | 0.335 | 78.8% | 0.000 to 0.000 | 0.0000 | 0.0107 |
| mid | 250 | 20186 | 4 | 0.000 | 1.541 | 0.052 | 28.0% | 0.000 to 0.000 | 0.0000 | 0.0385 |
| mid | 1000 | 20186 | 4 | 0.000 | 2.536 | 0.120 | 17.5% | 0.000 to 0.000 | 0.0000 | 0.0634 |
| high | 0 | 76102 | 4 | 0.000 | 2.239 | 0.976 | 62.1% | 0.000 to 0.000 | 0.0000 | 0.0560 |
| high | 250 | 76102 | 4 | 0.000 | 3.370 | 0.111 | 13.7% | 0.000 to 0.015 | 0.0000 | 0.0842 |
| high | 1000 | 76102 | 4 | 0.000 | 5.855 | 0.178 | 7.0% | 0.000 to 0.191 | 0.0000 | 0.1464 |

## Reading

- The median is 0.000 bp in every bucket at every delta (bootstrap range of the median 0 to 0.19 bp at most): a typical round-level crossing has no measurable slip at 0.1 USD tick size. The cost sits in the tail and the mean: p90 grows with latency and volatility (0.4 to 2.2 bp at delta 0, 2.0 to 5.9 bp at delta 1000 ms); in R at the 0.40 % stop even the high-volatility p90 at 1 s is 0.146 R.
- Proposed default for a backtest (OURS, UNCHECKED, a proposal only; tom_bt.py and maker_model.py are not edited, adoption is its own C2 card): replace slip=0.0 by the delta-250 ms MEAN slip per bucket (low 0.121 / mid 0.052 / high 0.111 bp), since the median is 0; delta 0 is the optimistic bound; keep the p90 as the stress case.
- Caveats: 12 days only (OURS cap); round-100 levels are a proxy, not real stop placement; trade-through on a liquid venue understates slippage for large size and thin books.
