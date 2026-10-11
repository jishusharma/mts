# MyTradingSys/execution/

Exchange execution layer. New module per PROJECT_VISION.md doctrine: Tom's
rules are core; this is a module, switchable, never gating core behavior.
MTS's existing candle-close read/decide loop is unchanged by anything here.

T050 (MyTradingSys/items/T050_deribit_execution_layer.md) is the phased plan.
T048 (satellite framework) is the exchange-agnostic goal this feeds later.

## .secrets/

Gitignored (see repo .gitignore). API keys live here as plain JSON files,
never in a script, never in an item doc, never pasted into a session. No
AI session should read this directory by default - if a task genuinely
needs a key, the operator supplies it explicitly in that turn, not by
pointing an agent at this folder.

Expected shape once a key exists, testnet.secret.json:
{
  "client_id": "...",
  "client_secret": "...",
  "env": "test"
}

## Operator contracts

- execution/HALT: manual brake, and also written automatically by executor fail_closed and position_manager flatten_halt, and by kill_switch --confirm KILL before anything else; nothing trades until an operator deletes it
- execution/HALT_DAILY_LOSS: written by daily_loss_monitor on breach, on unreadable state, and after 3 consecutive monitor failures; blocks if its date is today, future, malformed, or the file is unreadable; a valid past date only warns
- plan_id must match [A-Za-z0-9_-]{1,24}
- Testnet suites refuse to start while either HALT file exists
- Offline gate: python scripts/dev/run_all_tests.py (use --quick to skip Maven + backtest)
