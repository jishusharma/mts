FOUND 21 | DIFF 1 | NOT_IN_DATA 4
# Blind re-read of c31_multi_symbol_2026-11 RESULT.md against summary.json and study.py (2026-11-06)

Method: the host has no F:/MTS/data/tom_raw klines (and `fees` is not importable from here), so study.py cannot be re-run: every number is matched to summary.json, or recomputed from summary.json arithmetic (n-weighted pooling, t = mean/(sd/sqrt n)). study.py supplies the formulas (RT_DRAG = 2 x BINANCE_TAKER x 1.2 with BINANCE_TAKER = 0.0005 in backtest/fees.py line 36; cost_R = RT_DRAG/stop distance, so gross - net must equal cost_R). RESULT.md was read after the recomputation.

| # | Quoted number | Source line / recomputation | Status |
|---|---|---|---|
| 1 | Pooled n = 17 | summary.json POOL.n 17; 14 + 3 | FOUND |
| 2 | Pooled fee-net +0.71 R | POOL.net_R 0.711; recompute (14 x 1.09 + 3 x -1.059)/17 = 0.7108 | FOUND |
| 3 | Pooled sd 1.89 | POOL.sd_R 1.893; recompute from the two groups 1.8926 | FOUND |
| 4 | Pooled t 1.55 | POOL.t 1.55; recompute 0.7108/(1.8926/sqrt 17) = 1.548 | FOUND |
| 5 | Pooled gross +0.79 R | POOL.gross_R 0.786; recompute 0.7862 | FOUND |
| 6 | Pooled cost 0.08 R (and 0.075 in the gate call) | POOL.cost_R 0.075; recompute 0.0755; gross - net = 0.075 | FOUND |
| 7 | Pooled to target 59 % | POOL.tgt_pct 59; BTC 71 % of 14 = 10 hits of 17 = 58.8 % | FOUND |
| 8 | BTC n 14, to target 71 %, gross +1.17, net +1.09, sd 1.88, cost 0.08 | BTCUSDT.n 14, tgt_pct 71, gross_R 1.169, net_R 1.09, sd_R 1.879, cost_R 0.079 | FOUND |
| 9 | ETH n 3, to target 0 %, gross -1.00, net -1.06, sd 0.02, cost 0.06 | ETHUSDT.n 3, tgt_pct 0, gross_R -1.0, net_R -1.059, sd_R 0.023, cost_R 0.059 | FOUND |
| 10 | ETH adds 3 trades, all stopped out (-1.06 R each) | tgt_pct 0 and gross exactly -1.0 with sd 0.023 is consistent with 3 stops (sim() gives -1.0 gross on a stop); per-trade exits are not stored | NOT_IN_DATA (inferred, consistent) |
| 11 | By year BTC 2022: 9, 2023: 5; ETH 1 and 2; POOL 10 and 7 | summary.json years blocks, identical; 9+1 = 10, 5+2 = 7 | FOUND |
| 12 | "All 17 trades in 2022 (10) and 2023 (7); none in 2024 H1" | only keys 2022 and 2023 exist in every years block; sum 17 | FOUND |
| 13 | BTC regime mix 46 / 39 / 14 % | BTCUSDT.regime_mix bull 46, bear 39, range 14 (sums to 99, rounding) | FOUND |
| 14 | ETH regime mix 47 / 37 / 16 % | ETHUSDT.regime_mix 47 / 37 / 16 | FOUND |
| 15 | Gate m = 221 | summary.json gate.out "m 221" | FOUND |
| 16 | Gate z_holm 3.69 | gate.out "z_holm 3.688" | FOUND |
| 17 | MDE 2.08 R + cost 0.08 = 2.15 R | gate.out "MDE 2.079 R + cost 0.075 = 2.154" | FOUND |
| 18 | n needed = 1451, exit 1 (BLOCK) | gate.out "n needed 1451", gate.exit 1, verdict UNDERPOWERED | FOUND |
| 19 | Gate call parameters --n 17 --sd 1.893 --cost 0.075 --m auto --new-cells 1 | study.py main(): p['n'], p['sd_R'], p['cost_R'], '--m auto', '--new-cells 1' (values equal summary.json POOL) | FOUND |
| 20 | DEV window [2022-01-01, 2024-07-01), loader refuses later bars | study.py load() raises if end > DEV_END and if a bar >= DEV_END is loaded; DEV_END from splits (value not in the file) | FOUND (mechanism); date value NOT_IN_DATA |
| 21 | Cost = taker both sides + 2 bps slip RT over stop distance | study.py RT_DRAG = 2 x BINANCE_TAKER x 1.2 (0.0012 with taker 0.0005); gross - net per symbol equals cost_R (0.079, 0.059) | FOUND |
| 22 | Days: 912 per symbol (not quoted) | summary.json days 912 for both, consistent with 2.5 DEV years | FOUND |
| 23 | "At ~6 trades a year over two symbols" | 17 trades over the 2.5 DEV years = 6.8 per year, about 7 | DIFF (minor, ~7 not ~6) |
| 24 | BTC reproduction = shipped spot 2022-23 half n = 14, +1.09 R exactly | shipped result is in eagle_eyes_picture_2026-10-28, outside this card's scope; futures side 14 / 1.09 FOUND in summary.json | NOT_IN_DATA (shipped side) |
| 25 | Looser source bar needs n ~ 230 | not computed in summary.json or study.py | NOT_IN_DATA |
| 26 | Klines from F:/MTS/data/tom_raw, trade-by-trade re-run | files absent on this host | NOT_IN_DATA |

Reading: every number summary.json holds is reproduced in RESULT.md; pooling arithmetic and t check out independently. Verdict UNDERPOWERED stands.
