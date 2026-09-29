# Testnet subaccounts - one trade slot per layer family (2026-09-29)

Deribit nets one BTC-PERPETUAL position per account, so each account = one concurrent trade.
Routing (MyTradingSys/execution/auto_trader_config.json, first matching prefix wins):

| Signal source | Account | Secret file Jishu writes |
|---|---|---|
| tom, smoke | main (jishu) | existing testnet secret |
| layer:fabio:* | jishu_1 | .secrets/testnet_jishu_1.secret.json |
| layer:rsi:rsi_events:15m | jishu_2 | .secrets/testnet_jishu_2.secret.json |
| other layer:rsi:* (1h, malkan) | jishu_3 | .secrets/testnet_jishu_3.secret.json |
| every other layer (cryptocred, session, funding, tick, turn_of_candle...) | jishu_4 | .secrets/testnet_jishu_4.secret.json |

A missing secret file = that family falls back to the main slot (as before). Nothing breaks if you do only some.

## Jishu steps (test.deribit.com only, ~15 min)
1. Fund each subaccount: main -> jishu_1..4, e.g. 5 BTC each (Subaccounts page -> transfer icon). Code mode does not move funds.
2. For each subaccount: switch to it -> API -> Add new key: scopes trade:read_write, account:read, wallet:read (NO withdraw).
3. Write each file yourself (same format as your testnet secret):
   {"env": "test", "client_id": "...", "client_secret": "..."}   <- copy "env" value from your existing testnet secret
4. Restart the auto-trader (Ctrl+C in its window, then):  python -m MyTradingSys.execution.auto_trader
5. DONE: auto_trades.jsonl shows trade_attempt lines for layer sources while another trade is open.
Kill one account:  python MyTradingSys/execution/kill_switch.py --confirm KILL --account jishu_1

Known limits (testnet only): the daily-loss monitor watches the main account; subaccount losses are capped per
trade by stop + risk guard (per account). Mainnet stays single-account (named accounts are refused on mainnet).
