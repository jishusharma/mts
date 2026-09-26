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

## Files

deribit_client.py - phase 1: public (unauthenticated) read-only client.
No credentials used or required. Fetches BTC-PERPETUAL ticker from
test.deribit.com to prove the network path and client shape before any
key exists.
