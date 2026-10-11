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
