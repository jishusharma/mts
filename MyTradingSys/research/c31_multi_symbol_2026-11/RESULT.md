# C31 multi-symbol: daily upper-BB-edge short in a 50-day downtrend, BTC + ETH USD-M, DEV (2026-11-05)

**Verdict: UNDERPOWERED.** Pooled n=17, +0.71 R fee-net (sd 1.89, t 1.55); the repo power gate needs n=1451. No edge claim.
ETH adds 3 trades, all stopped out (-1.06 R each). The BTC lead stays a 2022-23 bear-market trade.

Regime mix: BTC DEV days bull 46 % / bear 39 % / range 14 %; ETH bull 47 % / bear 37 % / range 16 % (close vs rising/falling SMA50, OURS).
All 17 trades fall in 2022 (10) and 2023 (7); none in 2024 H1 (bull).

Context: PRE_REG.md (frozen before the run). Rule A of `eagle_eyes_picture_2026-10-28/c31_halves.py`, unchanged; USD-M futures 1m
from F:/MTS/data/tom_raw (BTCUSDT, ETHUSDT: the only symbols present), DEV [2022-01-01, 2024-07-01), loader refuses later bars.
Fee-net = taker both sides from fees.py + 2 bps slip RT (OURS), divided by the stop distance. Script `study.py`, numbers in `summary.json`.

| Symbol | n | to target | gross R | fee-net R | sd R | cost R | by year |
|---|---|---|---|---|---|---|---|
| BTCUSDT (reproduction) | 14 | 71 % | +1.17 | +1.09 | 1.88 | 0.08 | 2022: 9, 2023: 5 |
| ETHUSDT | 3 | 0 % | -1.00 | -1.06 | 0.02 | 0.06 | 2022: 1, 2023: 2 |
| POOL | 17 | 59 % | +0.79 | +0.71 | 1.89 | 0.08 | 2022: 10, 2023: 7 |

BTC reproduction: futures DEV row n=14, +1.09 R fee-net = the shipped spot 2022-23 half exactly (n=14, +1.09 R; the shipped n=15 total
adds 1 trade in 2025 H1, outside DEV).

## Power
`prereg_gate.py --n 17 --sd 1.893 --cost 0.075 --m auto --new-cells 1`: m=221, z_holm 3.69, MDE 2.08 R + cost 0.08 = 2.15 R vs the
0.30 R plausible-gross cap: exit 1 (BLOCK). n needed = 1451. At ~6 trades a year over two symbols that is centuries of daily data; even
the source's looser bar (one-sided 0.05, no Holm; +0.30 R needs n~230) is out of reach with 2 symbols.

## Conclusion
Decision: UNDERPOWERED, park. More USD-M symbols only matter if they add ~100+ trend-down edge trades; with 2 symbols over 2.5 DEV
years the rule fires 17 times. ETH's 0 of 3 is weak evidence against generality, not a test. No live or testnet use.
