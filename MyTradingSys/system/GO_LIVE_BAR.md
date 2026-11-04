# GO-LIVE BAR (T086) - nothing goes to real money until every line below is true

Accepted by the operator on the Control Room page, decision D06-gate, 2026-10-09 ("Accept this bar", no edits).
This is the only definition. Changing a number needs a new operator decision on the page; no session edits it alone.

## The bar (all must hold, measured on testnet, for 30 consecutive days)
1. Sample: at least 200 closed testnet trades, all from configs that passed the walk-forward backtest
   (out-of-sample net R above zero with its 95 % interval above zero, fees included, holdout read once).
   Trades from a parked or blocked layer (trade_blocklist, trade_blocklist_parked) do not count.
2. Net after fees: total net P&L above zero, using the exchange's real fills and fees.
3. Profit factor above 1.2.
4. Time-outs: under 5 % of exits are the time exit (today 97 %: T085 must fix this first).
5. Uptime: the stack is up more than 95 % of the 30 days (T080-T086 road, decision D04).
6. Held for 30 days: the five numbers above must stay true for the whole window; one failing day restarts the clock.

## Revision 2026-11-04 (d-s1-defaults-1104)
Operator signed S1; D3 (research/v1_plan_2026-10-20/D3_GO_LIVE_BAR_REVIEW.md) revises the bar. Where this block and items 1-6 differ, this block wins.
- Window: a rolling 30-day window with at most 1 day failing uptime replaces "one failing day restarts the clock"; P&L and PF are read over the whole window.
- Time-outs: item 4 leaves the live bar and becomes a per-layer promotion condition (time-exit share declared in the layer's pre-registration, measured on DEV).
- Sample: 200 closed trades or 60 days, whichever comes first, with at least 30 closed trades per promoted config (M5).
- M1 Restart safety: after any restart or reconnect every accumulator backfills or marks itself INVALID, and the trader fails closed.
- M2 Settlement blindness: daily-loss cap verified against the exchange ledger once per day, tested; the cap sees every account it protects.
- M3 Stop parity: the exchange stop equals the ledger stop, including after a bracket amend; 0 parity violations in the 30-day window.
- M4 Uptime is defined on the mainnet host and measured by a heartbeat file, not by a reviver that is itself a scheduled task.
- M5 Per-config minimum: at least 30 closed trades per promoted config inside the 200.
- M6 Kill-switch drill: one deliberate HALT and one deliberate restart during the 30 days, expected state written before each (EXPECT) and compared after (RESULT).
- M7 Mainnet first step written now: tiny fixed size, an experiment stop (for example 20 trades or -5 R), and trade_blocklist as the only way back.

## Where it is measured
- Trades: runtime_data auto_trades ledger (`trade_ledger.jsonl`), per source, per account.
- Walk-forward status of a config: its backtest report under research/ with the BT-TUNED label.
- Uptime: scripts/dev/refresh_klines + supervisor heartbeat (supervisor_log.txt), health_notes on the Control Room page.

## Status today (2026-10-09)
Not met: no config has a positive out-of-sample net R after fees (Tom gross -0.15 R before fees; only rsi 1h reached targets, 3 trades);
time-exit share 97 %; uptime ~81 % over the last 120 h (F-BT-19). The Control Room page shows this bar under Stage 5.

## Rules that stay regardless
Testnet only (Deribit test) until the operator signs a separate real-money decision on the page after the bar is met.
Builders never enable mainnet, never touch keys.
