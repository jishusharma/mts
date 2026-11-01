# Round-Trip Cost Figures in the MTS Codebase (`COST_FIGURES.md`)

Audit and reconciliation report for coexisting round-trip cost figures across the backtest infrastructure and research studies (card `fee-figure-unify`).

## Summary of Coexisting Cost Figures

Three distinct round-trip cost figures currently coexist in the codebase for BTCUSDT perpetual trading:
1. **0.10% (10 bps)** in `MyTradingSys/backtest/fees.py`: Pure exchange fee only ($2 \times 5\text{ bps}$ Binance VIP0 taker), zero slippage.
2. **0.12% (12 bps)** in `MyTradingSys/backtest/layers/positioning/trade_costs.py`: Exchange fee ($10\text{ bps}$) + asymmetric 1-sided slippage ($2\text{ bps}$).
3. **0.14% (14 bps)** in `MyTradingSys/backtest/research_kit.py`: Exchange fee ($10\text{ bps}$) + symmetric two-sided market slippage ($2 \times 2\text{ bps} = 4\text{ bps}$).

## Cost Figure Comparison Table

| Figure / Constant | File & Line | Nominal Value | Breakdown (Fee + Slip) | Label | Callers (Grep Hits) | Typical Callers & Research Consumers |
|---|---|---|---|---|---|---|
| `BINANCE_TAKER * 2` | `MyTradingSys/backtest/fees.py:36` | `0.10%` (10 bps) | 10 bps fee + 0 bps slip | **SOURCED** (Binance VIP0 tier, `T055b:22`) | 109 files, 175 hits (79 in `.py`) | Core exchange fee module (`fees.py`), C26 Phase 1-3 roadmap (`phase1_ladder_look.py:17`, `phase3_dev.py:45`), Cowen study (`run_event_study.py:21`), VP pivot probe (`vp_pivot_probe.py:237`), Deribit parity test (`test_b070_fee_parity.py:19`). |
| `trade_costs.net_return` (`fee_rt + slip_rt`) | `MyTradingSys/backtest/layers/positioning/trade_costs.py:51` | `0.12%` (12 bps) | 10 bps fee + 2 bps slip | **OURS** (FORMULAS s13, T055 candidates C1-C3) | 62 files, 143 hits (15 in `.py`) | T055 candidates (`funding_cvd_fade.py`, `run_t055.py:9,107`, `test_run_t055.py`), BigTrade fires (`fires_kline.py:130-131`), funding calculation (`bt_engine.py:12`). |
| `TAKER_RT_PCT` | `MyTradingSys/backtest/research_kit.py:21` | `0.14%` (14 bps) | 10 bps fee + 4 bps slip | **OURS** (`gross_effect_screen_2026-10-15/PRE_REG.md:1`) | 11 files, 22 hits (12 in `.py`) | Shared research kit (`research_kit.py:157`), Context factors study (`counts.py:35,76,226`), Rumers power table (`power_table.py:16,28`), Kurisko review (`dir-kurisko_2026-10-18.json:39`). |
| `MAKER_IN_RT_PCT` | `MyTradingSys/backtest/research_kit.py:22` | `0.09%` (9 bps) | 7 bps fee + 2 bps slip | **OURS** (`gross_effect_screen_2026-10-15/PRE_REG.md:1`) | 6 files, 10 hits (5 in `.py`) | Secondary maker-entry / taker-exit cost readout in `research_kit.py`, `counts.py:183,226`. |

## Root Cause of Divergence

The three figures represent three distinct cost accounting conventions that arose at different project stages:
1. **Pure Fee Floor (`0.10%`)**: Established in `backtest/fees.py` as Bug B081 single source of truth for exchange-levied transaction fees. It reflects pure exchange cost without estimating market execution quality.
2. **Asymmetric Slippage (`0.12%`)**: Defined in `trade_costs.py` for T055 candidate evaluation where a single 2 bps slippage penalty (`slip_rt = 0.0002`) was applied alongside 10 bps fees.
3. **Symmetric Slippage (`0.14%`)**: Formalized in `research_kit.py` for MDE power screens and modern pre-registrations where both entry and exit legs incur 2 bps market slippage ($2 \times (5\text{ bps fee} + 2\text{ bps slip}) = 14\text{ bps}$).

## Recommended Canonical Pair

We recommend adopting a single canonical cost standard across all research and backtest layers:

1. **Canonical Taker Round-Trip Cost ($C_{\text{taker}} = 0.14\% = 14\text{ bps}$)**:
   - Primary default for all market-entry / market-exit strategies.
   - Composition: $2 \times 0.0005$ VIP0 taker fee ($10\text{ bps}$) $+ 2 \times 0.0002$ two-sided market slippage ($4\text{ bps}$).
2. **Canonical Maker-In / Taker-Out Round-Trip Cost ($C_{\text{maker}} = 0.09\% = 9\text{ bps}$)**:
   - Secondary default for passive limit-order entries with market-order stops/exits.
   - Composition: $1 \times 0.0002$ VIP0 maker fee ($2\text{ bps}$) $+ 1 \times 0.0005$ VIP0 taker fee ($5\text{ bps}$) $+ 1 \times 0.0002$ exit slippage ($2\text{ bps}$).
3. **Pure Fee Floor ($0.10\% = 10\text{ bps}$)**:
   - Kept in `backtest/fees.py` strictly as the exchange fee lower-bound (`FEES_ALL_TAKER`), explicitly documented as excluding slippage.

### Impact of Moving `trade_costs.py` to the Canonical Standard
- `trade_costs.py:51` currently specifies `slip_rt: float = 0.0002`.
- Updating `slip_rt` to `0.0004` (4 bps) will align `trade_costs.py` with `research_kit.TAKER_RT_PCT` ($0.14\%$), ensuring that every module scoring trades net of slippage uses the identical $0.14\%$ hurdle.
- Affected callers: `run_t055.py` and `fires_kline.py` will experience a minor $0.02\%$ ($2\text{ bps}$) increase in execution drag, strengthening realism without breaking existing fee architecture.

Noticed: `trade_costs.py` default `slip_rt = 0.0002` applies only one leg of slippage for all-market orders; follow-up card `update-trade-costs-default-slip-rt-0004` should adjust `slip_rt` to `0.0004` to unify `trade_costs.py` with `research_kit.TAKER_RT_PCT = 0.14%`.
