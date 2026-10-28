# Fabio dedicated testnet slot

Fabio signals (source `layer:fabio:*`) get their own Deribit TESTNET account so RSI/Tom trades no longer block them.
Busy-check is per account; HALT / HALT_DAILY_LOSS / AUTO_PAUSE stay global. Routing config: `accounts` in
auto_trader_config.json (default `{"layer:fabio:": "fabio"}`).

## Operator steps (testnet only)
1. On https://test.deribit.com create a subaccount (Account > Subaccounts), fund it with testnet BTC.
2. In that subaccount create an API key with scopes trade + read ONLY (no withdraw, no account write).
3. Write `MyTradingSys/execution/.secrets/testnet_fabio.secret.json` yourself, same format as
   `testnet.secret.json` (client_id / client_secret), with `"env": "test"`. It is gitignored. A file with
   any other env is refused; named accounts are refused on mainnet.
4. Restart the auto-trader (the running one keeps the old shared-slot behaviour until restarted):
   `python -m MyTradingSys.execution.auto_trader`   (same flags as your current run; stop old one with Ctrl+C first)
   If the file is missing the trader logs `fabio_account_missing` once and shares the default slot as before.

## Verify the first Fabio fill
- `grep fabio MyTradingSys/execution/auto_trades.jsonl | tail`: expect `trade_attempt` with `"account": "fabio"`,
  `"outcome": "entered"` even while an RSI trade is open (no `skipped_busy` with account fabio unless a Fabio trade is open).
- Confirm on test.deribit.com that the position appears in the fabio subaccount, not the main one.
- Manager log: `journal/auto_manager_logs/<plan_id>.log`.

## Notes
- Mechanism: env var `MTS_ACCOUNT=fabio` is set for new_plan / executor / position_manager subprocesses;
  `deribit_orders._load_secret` picks `.secrets/testnet_fabio.secret.json`.
- kill_switch.py: use `python kill_switch.py --confirm KILL --account fabio` (sets the account for that run only). Do NOT set
  `$env:MTS_ACCOUNT` in your shell: a stale value breaks mainnet commands (the mainnet kill switch now ignores it with a warning,
  but executor/position_manager/daily_loss_monitor `--mainnet` still refuse). deribit_read.py still uses the default account.
