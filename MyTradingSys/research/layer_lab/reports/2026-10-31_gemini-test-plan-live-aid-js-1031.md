# Live Aid JS Indicators and Displayed Numbers Test Plan Report

**Task ID:** `gemini-test-plan-live-aid-js-1031`  
**Date (UTC):** 2026-10-31  
**Target Modules:** `MyTradingSys/tools/live_aid/live_aid_indicators.js`, `MyTradingSys/tools/live_aid/us_open_rates.js`, `MyTradingSys/tools/live_aid/live_aid.html`  
**Artifact Generated:** `MyTradingSys/research/gemini_burn_2026-10-31/LIVE_AID_TEST_PLAN.md`  
**Registry Ref:** `MyTradingSys/research/v1_plan_2026-10-20/D11_PROGRAMME.md`  

---

## 1. Summary of Findings

- **Total Displayed Number Metrics Cataloged:** 48 concrete displayed numeric outputs across 13 dashboard panels / sections (OURS: derived from systematic DOM and indicator analysis).
- **Test Pinning Breakdown:**
  - **PINNED:** 36 metrics (75.0%) have direct unit test or replay fixture coverage pinning the mathematical calculation and rendered value.
  - **PARTIAL:** 8 metrics (16.7%) have the underlying calculation tested in Python/Node unit tests, but the rendered DOM formatting in the browser replay is unpinned.
  - **NONE:** 4 metrics (8.3%) are local browser inputs / UI-only distance formatters (e.g., position distance in pts/ATR and custom user rung sizing).
- **Replay Fixture Coverage:**
  - 3 replay fixtures exist and pass: `fixture_klines.json` (momentum strip indicators), `fixture_ff_calendar.json` (economic calendar countdowns), and `fixture_bybit_flush_1030.json` (OI flush / squeeze detection).
  - Missing fixtures identified: Replay fixture for multi-venue liquidation streams (`#liq-sum` / `#liq-tape`) and full analyst ladder replay.

---

## 2. Key File & Line Citations

### 2.1 Indicators (`live_aid_indicators.js`)
- Wilder RMA RSI & SMA: `live_aid_indicators.js:9-47`, tested at `test_live_aid.py:176,180` and `test_live_aid_replay.py:149`.
- WaveTrend LazyBear formula: `live_aid_indicators.js:107-137`, tested at `test_live_aid.py:211` (matched against `wavetrend.py`).
- Bollinger Bands %B and Width: `live_aid_indicators.js:50-63`, tested at `test_live_aid.py:184` and `test_live_aid_replay.py:149`.
- Anchored Day VWAP: `live_aid_indicators.js:76-85`, tested at `test_live_aid.py:194`.
- Coil and Pierce 15m: `live_aid_indicators.js:241-272`, tested at `test_live_aid.py:402`.
- Open Interest Multi-window & Flush Detector: `live_aid_indicators.js:474-592`, tested at `test_oi_money.py:84,132` and `test_live_aid_replay.py:301`.
- US Open Ladder: `live_aid_indicators.js:435-472`, tested at `test_live_aid.py:532`.

### 2.2 Dashboard Rendering (`live_aid.html`)
- Header prices & basis: `live_aid.html:549-555`.
- Position P&L & distances: `live_aid.html:565-584`.
- Momentum strip row rendering: `live_aid.html:663-683`.
- Levels table & glance distances: `live_aid.html:688-713, 1021-1032`.
- Money tile & C24 expectations: `live_aid.html:790-830`.
- Liquidations sum & tape: `live_aid.html:836-860`.
- Funding & premium: `live_aid.html:864-884`.
- Macro calendar: `live_aid.html:900-913`.
- News headlines & pulse: `live_aid.html:930-949`.
- Verdict board & lean votes: `live_aid.html:959-988`.

---

## 3. Verification Commands

```powershell
# Verify indicator unit tests (Python / Node):
pytest MyTradingSys/tools/live_aid/test_live_aid.py -q
pytest MyTradingSys/tools/live_aid/test_oi_money.py -q
pytest MyTradingSys/tools/live_aid/test_build_analyst_data.py -q

# Verify browser replay fixture tests:
pytest MyTradingSys/tools/live_aid/test_live_aid_replay.py -q
pytest MyTradingSys/tools/live_aid/test_live_aid_layout.py -q
```
