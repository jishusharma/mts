# Layer Lab Report: Parameter Labels Audit of Layer Modules

- **Task**: `gemini-param-labels-layer-modules-1031`
- **Lane**: `CODEX`
- **Module Scope**: `wavetrend`, `rsi`, `krown`, `positioning`, `turn_of_candle`
- **Date**: 2026-10-31
- **Auditor**: Gemini Flash worker (Antigravity JIS-NUC)

---

## 1. Executive Summary

This report covers the systematic labelling audit of all tunable constants and parameter defaults across the five backtest layer modules:
1. `MyTradingSys/backtest/layers/wavetrend`
2. `MyTradingSys/backtest/layers/rsi`
3. `MyTradingSys/backtest/layers/krown`
4. `MyTradingSys/backtest/layers/positioning`
5. `MyTradingSys/backtest/layers/turn_of_candle`

Every number is verified and labelled either `SOURCED` (with an analyst quote, publication path, and line) or `OURS` (internal engineering default / grid-searched IS parameter). Any unsourced trader claim is flagged as `NOT_IN_DATA`.

- **Total Parameters / Constants Audited**: 85
  - `wavetrend`: 9
  - `rsi`: 33
  - `krown`: 30
  - `positioning`: 8
  - `turn_of_candle`: 5
- **Label Breakdown**:
  - `SOURCED`: 43
  - `OURS`: 42
  - `UNLABELLED`: 0
- **Primary Deliverable**: [LAYER_PARAM_LABELS.md](file:///F:/MTS/gq/gemini-param-labels-layer-modules-1031/MyTradingSys/research/gemini_burn_2026-10-31/LAYER_PARAM_LABELS.md)

---

## 2. Findings by Module

### 2.1. Wavetrend (`layers/wavetrend`)
- Parameters: `N1=10`, `N2=21`, `SMA_N=4`, `K=0.015`, `OB1=60.0`, `OB2=53.0`, `typical price divisor=3.0` are `SOURCED` from LazyBear's WaveTrend Oscillator script (`Crosses:14-21`; `FORMULAS.md:20`).
- Constants: `WARMUP=200` (EMA stabilization mask) and `D_TOL=1e-9` (floating-point flat window tolerance) are `OURS` (`PARITY_CONTRACT.md:3`).

### 2.2. RSI (`layers/rsi`)
- Standard RSI & MAs: `period=14`, `length=14`, levels `[70, 50, 30]` are `SOURCED` (`FORMULAS.md:1`; Wilder 1978).
- Malkan 40/60 Regime & Divergence: `lo=40`, `hi=60` are `SOURCED` (Malkansview `WEB_RESEARCH.md` MLK-R1 / MLK-S1 / MLK-S2). Regular divergence `min_bars=3`, `max_bars=10`, `min_rsi_diff=0.0` are `SOURCED` (`extract_Wvq1TZh8aF0.md:13`, `extract_cQ-y1oULkBw.md:15`). Reverse divergence levels `prd_min_rsi=60.0`, `nrd_max_rsi=40.0` and windows `5..14` are cited from `GbXnw_tNMtw_raw.txt:379,460`.
- Internal / Harness Choices: `regime_lookback=20`, `event_tolerance=2.0`, `krown_hidden_bars (3..10)`, `STOP_PCT=0.01`, `TARGET_PCT=0.02`, `MAX_BARS=100`, `PRIMARY_H=10`, `T_MIN=2.0` are `OURS`.

### 2.3. Krown (`layers/krown`)
- Sourced Rules: `zone_min_turns=2` (KR-Z02), `zone_max=5` (KR-Z03), `zone_mature_tests=3` (KR-Z13), `vol_sma=20` (KR-V01), `vol_mult=2` (KR-V02), `vol_half=0.5` (KR-V10), `bbwp_basis=7` (KR-Q01), `bbwp_lookback=100` (KR-Q01), `bbwp_high=85` (KR-Q02), `bbwp_confirm=50` (KR-Q02), `confirm_horizon=3` (KR-C03), `crows_bars=3` (KR-C11), `ma_fast=21` (KR-M01), `ma_slow=55` (KR-M01), `ma_long=200` (KR-M01), `ma_leash=5` (KR-M06), `leash_n=3` (KR-M06), `rsi_bull=60` / `rsi_bear=40` (KR-S03), `tops_need=3` (KR-P01), `s1_vol_mult=2` (KR-V02) all cite `KROWN_LAYER_SPEC.md` and `KROWN_RULES.csv`.
- Structural / Implementation Choices: `zone_k=3`, `zone_lookback=250`, `swing_tol=0.01`, `bbwp_low=30` (from 25-35 range), candle thresholds (`hammer_wick=0.6`, `hammer_close_pos=0.7`, `doji_body=0.1`), MACD parameters (`12/26/9`), range/coil thresholds (`range_n=20`, `range_width_max=0.25`, `range_edge=0.2`, `coil_recent=5`, `coil_max=0.7`), context latencies and baseline windows are `OURS`.

### 2.4. Positioning (`layers/positioning`)
- Sourced: Cumulative CVD delta formula `2 * tbv - v` (`FORMULAS.md:360`) and Binance perpetual round-trip fee `0.0010` (`FORMULAS.md:345`).
- Internal / Grids: Funding percentiles `0.95 / 0.05`, funding lookback `90`, CVD lookback `20`, and slippage hurdle `0.0002` (2 bps) are `OURS` (`FORMULAS.md:345-369`).

### 2.5. Turn of Candle (`layers/turn_of_candle`)
- Sourced: 15-minute quarter period and turn minute 0 are `SOURCED` from Shanaev, Vasenin, Stepanov (*Heliyon*, PMC10015199; `FORMULAS.md:16`).
- Internal: `lead_minutes=1` and `side="long"` are `OURS` (grid-searched IS; `FORMULAS.md:16`).

---

## 3. Verification Commands
- `python scripts/dev/tasks.py check`
- `python scripts/dev/tasks.py lint`
