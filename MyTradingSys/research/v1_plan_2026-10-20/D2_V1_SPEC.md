# D2. MTS v1 product spec (one page; proposal for operator sign-off)

## Purpose
MTS v1 trades one instrument (BTCUSDT perpetual) from signals that passed a fee-net out-of-sample test, on Deribit testnet
until the GO-LIVE BAR holds, then on mainnet at a size the operator signs. Money decisions are made by deterministic code.
Models (Claude, GPT, Gemini, DeepSeek) build, review and read; they never decide a trade.

## In scope (v1)
1. Platform core: data feeds (Binance klines, aggTrades, order flow; Java feed), snapshot and state files, the auto-trader
   with brackets and brakes, position manager, daily-loss monitor, kill switch and HALT, trade ledger, outcome labeler,
   CI-gated deploy to the live tree, read-only live mirror.
2. Exactly two research layers in flight at a time (D4), each run through the pre-registration template, DEV then one
   VALIDATION read, then promotion into `promoted_setups.json` only on a fee-net OOS pass with its confidence interval above zero.
3. CBP as a module: analyst calls arrive through the versioned queue contract and become CANDIDATE_UNTESTED rows; they trade
   only after the same promotion as any layer (D5).
4. Resource safety in code: one ship gate per machine, bounded step limits, process-tree kill, a jam check that exits non-zero
   (unjam branch), a WIP limit enforced by `tasks.py` (max 2 research layers active).
5. One work list (cards), one dispatcher (a human-started coordinator), two pages (D8).

## Out of scope (v1, explicitly)
Options, any market other than BTC perp (DAX chain stays parked, q11), a local LLM assistant, tick-delta layer, new analyst
sources beyond those already in `analysts.json`, confluence between layers before each passed on its own, mainnet.

## Core vs module (the boundary)
Core owns: market data, state, risk limits, order placement, ledger, promotion registry, HALT. Modules (layers, CBP, later
options) produce proposals only. A module may never write to the live tree, place an order, or edit the promotion registry.
Core reads a module through one versioned contract and ignores anything that fails it.

## Module contract (what every module must meet)
- Signal v1 (JSON): `source` (layer id or `cbp:<analyst>`), `instrument`, `side`, `entry_trigger`, `stop` (number or null),
  `target` (number, level, or null), `expires_at` (UTC), `evidence` (file:line or video id), `backtest_id` (layer_map key or
  null), `order_eligible` (false until promoted; core sets it, never the module). Schema file: `MyTradingSys/queue/cbp_contract_v1.schema.json`
  today; v1 promotes it to the one schema for all sources.
- Every parameter labelled SOURCED or OURS (PROJECT_VISION 2026-10-13).
- Pre-registration answered (12 items, `backtest/PRE_REG_TEMPLATE.md`) before any outcome read; one VALIDATION read; the holdout read once.
- Tests that fail on the old code; fail-closed on missing data.

## Non-functional needs
- Uptime: the stack up 95 % of days on the host that will run mainnet (today JIS-NB), measured by the heartbeat and reported daily.
- Resource limits in code: at most 1 code gate per machine at a time, step limit 30 min, gate bound 90 min, python
  processes under 6 per CPU (`traffic.py jam` thresholds).
- Restart safety: every accumulator (session CVD, VWAP volume) backfills or marks state INVALID (fail closed) after a restart
  or reconnect; a test per live file for restart, reset, non-trade balance move and API error (CLAUDE.md).
- Safety: daily loss cap, kill switch and HALT stay in deterministic code; a halt blocks risk-adding orders, never the protective stop.
- Cost: bookkeeping commits under 30 % of trunk commits (STATUS.md cap); coordinator boot under 25 lines of facts.

## Acceptance
v1 is accepted when the GO-LIVE BAR (`system/GO_LIVE_BAR.md`, D06-gate 2026-10-09) holds for 30 days with the changes the
operator picks from D3, and every promoted config traces to a pre-registered, VALIDATION-passed report. Mainnet remains a
separate signed decision.
