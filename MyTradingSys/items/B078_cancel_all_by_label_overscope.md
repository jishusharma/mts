# B078 - CANCEL_ALL_BY_LABEL CANCELS EVERY ORDER ON THE CURRENCY, NOT JUST THE LABEL

Opened: 2026-09-27 by session Claude Sonnet 5 (core readiness review, continuing CORE_READINESS_PLAN.md).
Severity: MED (not yet called anywhere, so no live risk today; becomes HIGH the moment teardown/reconciliation wires it in).
Status: CLOSED. Receipt: 5e387a1 (full receipt in the BUGS.md B078 row).

## DESCRIPTION

execution/deribit_orders.py's cancel_all_by_label(token, label, currency)
calls private/cancel_all_by_currency with type="all" and does not pass or
filter by label at all - Deribit's API does not support server-side
label filtering on that endpoint. The function name promises label-scoped
cancellation; the implementation cancels every open order for the currency,
across all plans/subaccounts. The function's own docstring already flags
this: "flagged for Opus/Sonnet to fix before step 4 relies on label-scoped
teardown."

## CURRENT EXPOSURE

Grepped execution/*.py and execution/examples/*.py: cancel_all_by_label is
not called anywhere yet. Dead code today - no live risk until something
wires it in.

## REQUIRED FIX

Fetch open orders (get_open_orders), filter client-side by label, then
call cancel(order_id) individually per matching order. Remove or rename the
current cancel_all_by_currency-based implementation so nothing can call it
under the false assumption that it is label-scoped.

## BLOCKS

- T050 Phase 4/5 (reconciliation, teardown of one plan's orders without
  touching other plans/subaccounts once step 6 multi-account work lands).

## UPDATES

2026-09-27: Found during deribit_api_research.md.new review, alongside
B077. Filed per operator decision to continue the review queue rather than
fix immediately.
