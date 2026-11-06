# us_prep.py spec (card us-session-prep-1106, decision d-us-session-prep-1106)
T0 script, no LLM. Phases: P1 09:00Z, P2 13:15Z, P3 14:45Z, P4 21:15Z (scoring). Output MyTradingSys/runtime/us_prep/<date>_<phase>.md + .json (git-ignored).
- macro: NQ, ES, VIX, DXY, US10Y, Kospi, Nikkei from Yahoo; thresholds reused from premarket_risk.js.
- BTC levels: prior-day H/L/C, volume value area + POC (50 USD bins, 70%), Asia 00-08Z and London 08-13Z H/L, day VWAP, BB(20,2) on 15m/1h/4h/1d. Klines from data-api.binance.vision (fapi.binance.com times out from JIS-NB).
- funding, OI 24h, liquidation clusters: only where reachable (fetch on the NUC); else UNKNOWN. Never guess.
- econ calendar + earnings for the day from a public source; UNKNOWN if none.
- P4 scorer: reads the 4 phase jsons + the session's actual H/L/close, writes HIT/MISS per scenario (scenarios come from scenario_ledger.py).
- Tests: fixture day 2026-11-05 (Kospi -5.3%, NQ -0.6%, BTC 80.9k to 75.2k) and UNKNOWN fail-closed; both fail before the module exists.
- The brief is Context, never a signal.
