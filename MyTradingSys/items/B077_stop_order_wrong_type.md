# B077 - STOP ORDER PLACED AS REDUCE-ONLY LIMIT, NOT STOP_MARKET

Opened: 2026-09-27 by session Claude Sonnet 5 (core readiness review, continuing CORE_READINESS_PLAN.md).
Severity: HIGH (stop-loss does not function as a stop; would fill instantly for a long, per plan headline).
Status: CLOSED. Receipt: 5e387a1 (full receipt in the BUGS.md B077 row).

## DESCRIPTION

execution/executor.py lines 137-143: after entry fills, the protective stop
is placed via do.sell(..., "limit", price=stop_spec["price"], reduce_only=True)
(or do.buy(...) for the short case) - a plain reduce-only LIMIT order, not a
stop_market order. A reduce-only LIMIT at the stop price does not wait for
price to reach it the way a real stop does; depending on book state at
placement time it can fill immediately or never trigger as intended.

## ROOT CAUSE

execution/deribit_orders.py's _place_order() (and its buy()/sell() wrappers)
only accept instrument_name, amount, type, price, label, reduce_only. There
is no trigger or trigger_price parameter, which Deribit's stop_market order
type requires, along with a choice of trigger source (last_price, mark_price,
or index_price). The function cannot place a real stop order at all as
currently written - this is a missing capability, not a one-line type-string
swap.

## REQUIRED FIX

1. Add trigger and trigger_price params to _place_order()/buy()/sell() in
   deribit_orders.py.
2. Decide trigger source (last_price vs mark_price vs index_price) - operator
   or Opus decision, affects behavior during fast moves/wicks.
3. Change executor.py's stop placement call to type="stop_market" with the
   new trigger params instead of type="limit".
4. Verify on testnet: place a stop, move price through it (or simulate),
   confirm it fires as a market order at trigger, not before.

## BLOCKS

- T050 Phase 3 (order placement testnet) and Phase 4 (reconciliation) -
  a stop that doesn't behave like a stop makes both phases unsafe to trust.
- Any live trading gate (T050 Phase 6).

## UPDATES

2026-09-27: Found during deribit_api_research.md.new review - the doc fix
(error codes) was applied, but checking the code it documents surfaced this
still-unfixed bug, matching CORE_READINESS_PLAN.md's original headline
finding ("executor places the stop as a reduce-only LIMIT ... must be
stop_market"). Not yet fixed - operator chose to file and continue the
review queue rather than fix immediately.
