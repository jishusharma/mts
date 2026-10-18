# MTS Research Papers Series

This directory contains formal quantitative and domain research papers establishing the foundational methodologies, mathematical proofs, and empirical studies utilized across the MyTradingSys (MTS) architecture.

---

## Index of Papers

| Paper | Title | Focus Areas |
|-------|-------|-------------|
| [01_MASTERS_PITCHFORK_FOUNDATIONS.md](01_MASTERS_PITCHFORK_FOUNDATIONS.md) | **Foundational Median Line Analysis & Pitchfork Methodologies** | Synthesis of master traders (Dr. Alan Andrews, Jerome Schiff, Timothy Morge, Patrick Mikula, Dr. Mircea Dologa), Newton's 3rd Law, Babson Action-Reaction cycles, Five core rules, 80% median line reach theorem, Hagopian failure, and Pitchfork variants (Standard, Schiff, Modified Schiff, Inside). |
| [02_PITCHFORK_APPLICATION_ON_BTC.md](02_PITCHFORK_APPLICATION_ON_BTC.md) | **Quantitative & Empirical Application of Pitchfork and Median Line Dynamics to Bitcoin (BTC)** | Market microstructure, linear vs. logarithmic pitchfork geometry, objective ATR-based pivot detection, empirical regime statistics, Hagopian liquidation cascades, order flow (CVD, absorption) & Volume Profile confluence, and fee economics. |

---

## Architecture Integration

These papers directly inform the **Pitchfork Layer Family** in MTS:
- **Specification:** `MyTradingSys/research/pitchfork_2026-10-19/RESEARCH_PITCHFORK_LAYER.md`
- **Module Implementation:** `MyTradingSys/backtest/layers/pitchfork/pitchfork_detector.py`
- **Unit Verification:** `MyTradingSys/backtest/layers/pitchfork/test_pitchfork_detector.py`
- **System Registration:** `MyTradingSys/system/layer_index.json` & `MyTradingSys/system/layer_map.json`
