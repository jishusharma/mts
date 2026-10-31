# BLOCKED — live aid indicators vs FORMULAS.md

## Verdict

BLOCKED — the fixture’s requested trailing bars are outside the permitted DEV data window. The task explicitly asks for the last 60 rows of `fixture_klines.json`, but the fixture rows inspected from its tail have open timestamps in October 2026 (for example `1793077140000` ms). The run constraint permits only DEV bars opened before 2024-07-01. Running the requested hand calculation or Node comparison on those rows would violate that constraint. No indicator verdict is claimed, and no code or fixture data was changed.

## What was checked

- `MyTradingSys/tools/live_aid/fixture_klines.json` — tail rows; timestamp example `1793077140000` ms, which is 2026-10-27 UTC.
- `MyTradingSys/tools/live_aid/live_aid_indicators.js:1-7,34-87,107-137` — documented default parameters and RSI, Bollinger, ATR, daily VWAP and WaveTrend functions. Node was not run against the fixture.
- `MyTradingSys/backtest/layers/FORMULAS.md:10-56,331-350,516-553` — Wilder RSI definition; core ATR definition; WaveTrend and Bollinger definitions. The task’s request for the trailing 60 fixture bars cannot be satisfied within the allowed data window.

## Findings

| Severity | File:line | Result | Evidence | Proposed fix |
|---|---|---|---|---|
| MED | `MyTradingSys/tools/live_aid/fixture_klines.json` (tail rows) | NOT_IN_DATA for an allowed audit | Tail bar timestamp `1793077140000` ms is later than the permitted 2024-07-01 cutoff. Consequently the last-60-bar RSI, BB and WaveTrend values were not computed, and no SAME/DIFF comparison is available. | Supply a fixture whose requested bars are DEV bars opened before 2024-07-01, or explicitly revise the data-window rule for this card. |

## Parameter provenance (as documented; values not evaluated)

| Parameter | Label | Evidence |
|---|---|---|
| RSI length 14 | SOURCED | `live_aid_indicators.js:2` identifies the operator chart setup as SOURCED. |
| Bollinger length 20, multiplier 2 | SOURCED | `live_aid_indicators.js:2`; `FORMULAS.md:554-558` calls the standard TradingView setting SOURCED. |
| ATR length 14 | SOURCED | `live_aid_indicators.js:2`. |
| VWAP price `hlc3`, UTC-day anchor 00:00 | SOURCED | `live_aid_indicators.js:2,76-87`. |
| WaveTrend periods 10/10/21/4 and multiplier 0.015 | SOURCED | Formula source at `FORMULAS.md:520-526`. |
| WaveTrend EMA seeding / warmup 200 / gap and flat-window reset | OURS | `FORMULAS.md:524-527`; implementation comment at `live_aid_indicators.js:107-110`. |

## Follow-up

No follow-up card created. Safest non-destructive resolution is to provide an eligible pre-cutoff fixture; alternatively the run constraint needs an explicit update before using this fixture. No changes were made outside this report.

Noticed: The requested fixture tail falls after the permitted DEV cutoff, so a same-input math audit needs eligible fixture data or an explicit change to the run constraint.
