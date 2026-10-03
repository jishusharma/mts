# MTS-2026-10-03-2051Z-APP-ANA-btc-candle-patterns
surface: APP | role: ANA | model: claude-sonnet-5-5 | branch: fast-track | lanes: none (no subagents, no NUC) | status: open
host: JIS-NB (Claude Win App, Code tab) | account: not captured | predecessor: none (no earlier -APP-ANA record) | started: 2026-10-03 20:51Z

Surface (SURFACE_POLICY section 1/1b): APP desktop. No CLI fallback needed: every step ran as file read/write, stdlib Python scripts
and public web lookups. No live process was touched, no file under execution/ or layers/alerts/ was edited, no HALT, no trade.

## Task (operator, verbatim summary, 2026-10-03)
Thorough research on BTC candlestick-pattern trades: assess the operator's example rule (long when price rises through the previous
daily open, exit when the daily closes below the previous daily close), survey which candle signals are worth testing on BTC, define
verifiable backtests for each. Deliver: method note per playbook Part I, source-tier plan per sub-question, findings tagged
Tier | Method quality | Confidence, backtest feasibility vs current MTS and Fabio functions with a file map, surface named, BUGS row if a defect
surfaces, high-level roadmap.

## Deliverable
`MyTradingSys/research/candle_patterns_2026-10-04/` (index: CANDLE_PATTERNS_RESEARCH_2026-10-04.md). Pre-registration committed before any result.

## Log
- Boot docs read: STATUS.md, SURFACE_POLICY.md, LESSONS_LEARNED.md (to line 200), playbook Part I, BACKTEST_PROTOCOL.md.
- Data fetched with the repo's own `fetch_binance_archive.py` (public, SHA256-checked): fundingRate 2020-01..2025-08, 1d klines 2025-09..2026-09-26.
