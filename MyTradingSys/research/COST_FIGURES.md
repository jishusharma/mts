# Round-trip cost figures (table only, no code changed)

Card: fee-figure-unify. Counts are `grep -rl` over non-test `.py` under MyTradingSys on trunk e6ef9091f.

## Finding

The three "disagreeing" figures share one fee and differ only in the slippage added on top. Fee per round trip is 0.10 % in all three (taker 5 bp in + 5 bp out, Binance USDT-M default tier). The totals differ by slippage: 0 bp (fees.py), 2 bp (trade_costs.py), 4 bp (research_kit.py). Nothing here is a fee conflict; the conflict is that slippage is unnamed in two of the three places.

| # | Figure | Value | file:line | Fee part | Slip part | SOURCED / OURS | Callers (grep) |
|---|---|---|---|---|---|---|---|
| 1 | `BINANCE_TAKER` | 0.0005 per side = 0.10 % RT | backtest/fees.py:36 | 5 bp x 2 | none | SOURCED (Binance fee schedule, docstring fees.py:12-13) | 33 non-test files (fabio/run_backtest.py:41 as `FEE_ROUND_TRIP = 2 * _BT`, vp_pivot_probe.py, c26 phase1/phase3, eagle_eyes, cowen event study) |
| 2 | `BINANCE_MAKER` | 0.0002 per side = 0.04 % RT | backtest/fees.py:37 | 2 bp x 2 | none | SOURCED (same) | vp_pivot_probe.py:25, 241 and others |
| 3 | `net_return` defaults `fee_rt=0.0010`, `slip_rt=0.0002` | 0.12 % RT | backtest/layers/positioning/trade_costs.py:51 | 10 bp | 2 bp | fee SOURCED (FORMULAS.md s13, line 352); slip OURS (internal "SCALPING FEE FLOOR", FORMULAS.md s13 line 353) | 3 non-test code files: bigtrade/fires_kline.py:130, layers/run_t055.py:107, research/loose_code/oi_divergence_v2_2026-10-10.py |
| 4 | `TAKER_RT_PCT` | 0.14 % RT | backtest/research_kit.py:21 | 10 bp | 4 bp (2 + 2) | SOURCED to gross_effect_screen_2026-10-15/PRE_REG.md s.1 "Primary round-trip cost C" (research_kit.py:12-14) | research_kit.taker_cost_r (:156), research/context_factors_pit_2026-10-16/counts.py:35,76,183,226 |
| 5 | `MAKER_IN_RT_PCT` | 0.09 % RT | backtest/research_kit.py:22 | 2 + 5 bp | 2 bp | SOURCED (PRE_REG "Secondary cost readout C_m") | research_kit.maker_in_cost_r (:160), counts.py:183,226 |
| 6 | Deribit `DERIBIT_TAKER` | 0.0005 per side | backtest/fees.py:32 | 5 bp x 2 | none | SOURCED | fees.py FEES_* dicts (:48-49); testnet path |

Not figures but related: bt_engine.py:12 and FORMULAS.md s17 (line 409-413) both point at fees.py; the Java constant is pinned to fees.py by tests/test_b070_fee_parity.py.

## Recommendation (one canonical set, for a reviewer ACCEPT before any code moves)

Canonical pair, fee only, in fees.py: taker 0.0005 / maker 0.0002 per side (already there). Add one named slippage constant next to it (suggest `SLIP_RT_STRESS = (0.0, 0.0002, 0.0004)` as three labelled stress levels, OURS) so every study states fee-net at a named slippage instead of a bare total. Mapping that keeps all published numbers valid:

- "fee only" (0.10 %): fees.py users, unchanged.
- "fee + 2 bp" (0.12 %): trade_costs.py defaults, unchanged.
- "fee + 4 bp" (0.14 %): research_kit TAKER_RT_PCT, unchanged, but derive it as `2*BINANCE_TAKER*100 + 0.04` instead of a literal.

Callers that would move if a single total were forced instead: the 33 fees.py studies (to 0.12 or 0.14) and the 2 research_kit callers. Every one changes fee-net decision numbers, so each needs its own IMPORTANT card plus re-run. Recommended: do not force one total; derive research_kit and trade_costs defaults from fees.py (no value change), add the named slippage levels, and only then retire literals. Follow-up cards are filed through the builder's Noticed: line.
