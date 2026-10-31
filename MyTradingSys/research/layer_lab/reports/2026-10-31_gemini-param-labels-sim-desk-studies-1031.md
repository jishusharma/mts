# Layer Lab Report: Parameter Labels Audit of Sim Desk Studies

- **Task**: `gemini-param-labels-sim-desk-studies-1031`
- **Lane**: `CODEX`
- **Scope**: `MyTradingSys/research/sim_desk/studies/` (`rsi.py`, `levels.py`, `krown.py`, `wavetrend.py`, `pitchfork.py`, `cowen_bmsb.py`, `_bars.py`)
- **Date**: 2026-10-31
- **Auditor**: Gemini Flash worker (Antigravity JIS-NUC)

---

## 1. Executive Summary

This audit establishes the explicit provenance (`SOURCED` vs `OURS`) for every configuration parameter, default value, and execution threshold across the 6 simulation desk studies and their shared bar harness:
1. `rsi.py` (Malkan 40/60 bounce)
2. `levels.py` (CryptoCred daily level touches)
3. `krown.py` (Krown S5 MA cross, S8 squeeze breakout, S4 coil)
4. `wavetrend.py` (LazyBear WaveTrend oscillator cross)
5. `pitchfork.py` (Andrews / Schiff / Modified Schiff median lines)
6. `cowen_bmsb.py` (Cowen Bull Market Support Band)
7. `_bars.py` (Shared data loader, fees, slippage defaults)

- **Total Parameters / Constants Audited**: 68
- **Provenance Breakdown**:
  - `SOURCED`: 22 (trader rules, technical formulas, and literature citations)
  - `OURS`: 46 (execution fees, slippage model, bar horizons, timeout thresholds, date windows, tolerance bands)
  - `NOT_IN_DATA`: 0
- **Primary Deliverable**: `MyTradingSys/research/gemini_audits_2026-10-31/sim_desk_studies_param_labels.md`

---

## 2. Methodology & Findings Summary

1. **RSI 40/60 (`rsi.py`)**:
   - `SOURCED`: RSI 14 (`WEB_RESEARCH.md:35`), daily timeframe (`WEB_RESEARCH.md:116-120`), entry on breakout above/below signal bar (`WEB_RESEARCH.md:117`), exit at RSI 60/40 level (`WEB_RESEARCH.md:128,152`).
   - `OURS`: 2.0 RSI tolerance band, 20-bar lookback for trend/regime, 100-bar max holding period, Binance fee/slippage defaults.

2. **Price Levels (`levels.py`)**:
   - `SOURCED`: E1 5m RSI filter (`levels_confluence_2026-10-14/ladder.py`), K5 stop past extreme of the day (CryptoCred price action).
   - `OURS`: S2 scale variant, stop buffer (0.05%), 2.0R fixed target, Binance fee/slippage defaults.

3. **Krown Studies (`krown.py`)**:
   - `SOURCED`: S5 21/55 EMA cross on 200 SMA side (`KROWN_RULES.csv:KR-M02`), S8 BBWP basis 7 / lookback 100 (`KR-Q01`), low <= 30 (`KR-Q02`), break >= 50 (`KR-Q02`).
   - `OURS`: Stop past 10 bars extreme, 4h timeframe, 2.0R target (trader gives no exit rule KR-X01), S4 coil parameters (range 20, coil 0.7).

4. **WaveTrend (`wavetrend.py`)**:
   - `SOURCED`: WT parameters 10/21/0.015 and bands 53/60 (LazyBear Pine script), both sides (LazyBear), 3-bar extreme stop and 1.5R target (TrendCrypto2022, `EXTERNAL_SETUPS.md:24`).
   - `OURS`: 1h default timeframe, 100-bar max hold, warmup 200 bars, fee/slippage defaults.

5. **Pitchfork (`pitchfork.py`)**:
   - `SOURCED`: Modified Schiff 50% price shift (Dologa 2007), Andrews 80% median line return rule (`RESEARCH_PITCHFORK_LAYER.md:28-56`), Hagopian failure rule.
   - `OURS`: ZigZag confirmation delay (4 bars 4h, 3 bars 1d), swing threshold (3% 4h, 4% 1d), 70% TPO Value Area filter, 1.5% stop offset, 60-bar max hold.

6. **Cowen BMSB (`cowen_bmsb.py`)**:
   - `SOURCED`: 20-week SMA and 21-week EMA of completed weeks (`extract_bekghgecip8.md:W2,W6`), bounce setup, 50-day SMA fakeout (`COWEN_LEVELS_2026-10-31.md`).
   - `OURS`: Completed week boundary filter (anti-lookahead), 2 daily closes exit rule, 2.0x ATR14 stop distance, 3% catchdown gap, 30-day max hold.

Noticed: Every simulation desk study cleanly separates core trader hypotheses from internal execution scaffolding and fee models.
