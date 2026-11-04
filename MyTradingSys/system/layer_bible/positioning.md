# Layer Bible: positioning / order flow (family `positioning`) | STUB 2026-11-04: operator rules and evidence pointers only, no runtime yet
One source of truth for OI / CVD / net delta / liquidation reading. Everything else is secondary. No `layer_state.py positioning` exists; until it does, a state answer is "not computed".

## Definition
Not yet consolidated. Pointers: `backtest/layers/FORMULAS.md` (CVD and VWAP sections), `research/coinglass_field_guide_2026-11-01`, `research/oi_side_2026-10-30`.

## Operator rules
- 2026-11-04 ~14:05Z, voice (shot 91f00baca11d, CoinGlass 30m Binance perp, his drawn levels; relayed by the coordinator), verbatim: "these lines provide you some guidelines to understand ... which levels are hit, from which level to which level they move ... how the OI, CVD, net delta ... are changing with price ... liquidations, profit taking, shorts, longs coming out of their positions ... perhaps this gives you some idea on how to use them effectively." His levels, as drawn: price 81,953 / 80,114 / 78,853 / 78,776 / 78,204 / 77,441 / 76,444 / 76,270; OI 98.2K / 95.1K / 92.6K; CVD -21.4K / -23.4K / -28.6K; net delta -4.5K / -7.5K / -10.4K. Illustration, not parameters.

## Findings (as reported, trust UNCHECKED by Lab_Guy)
- OI with price never calls direction: 48-54 % hit rates, DEV 2022-25 n=35,963, the meaning flips by year: `research/oi_side_2026-10-30`.
- CVD divergence hit rate equals the base rate: `research/coinglass_field_guide_2026-11-01` Q8.

## Open
- Study queued: `oi-retest-fewer-positions-1104` (design `research/oi_retest_2026-11-04/SPEC.md`, C2, awaiting a non-Claude spec review). CVD and net delta levels are NOT_IN_DATA in `F:/MTS/data/binance_metrics` (needs aggTrades).
