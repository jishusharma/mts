# T050 - DERIBIT EXECUTION LAYER (FIRST SLICE OF T048's EXCHANGE-API GOAL)

Register row: MyTradingSys/research/BUGS.md T050.
Opened: 2026-09-26 by session claude-sonnet-5-2026-09-26.
Severity: HIGH. Status: OPEN (design; scaffolding started).

## OPERATOR STATEMENT (verbatim, 2026-09-26)

"We need a plan now to get live asap!"
"the API part - it is simple i believe - my exchange deribit has API support."

## SCOPE VS T048

T048 is the general satellite / multi-position / exchange-agnostic
framework. T050 is the first real exchange integration - Deribit,
the operator's exchange - that T048's abstraction will eventually sit
behind. T050 ships read state and single-position order management well
before T048's satellite/governance layer exists, so capability does not
wait on the full framework. Phase 5 below is where T050 feeds T048.

## CORRECTION TO "IT IS SIMPLE" (validation, not just agreement)

Confirmed 2026-09-26 against Deribit's own docs: authenticating (OAuth2
client_credentials against /public/auth) and placing one order
(private/buy or private/sell, instrument_name=BTC-PERPETUAL, amount, type,
price) is genuinely a handful of lines. That part is simple and true.

What is not simple, and is already called out as owed in T048's own
dependency list:
- Position model. MTS assumes one position at a time today. An execution
  layer must track exchange-side order/position state and reconcile it
  against MTS's belief - a fill MTS did not see, a manual close on the
  exchange UI, a partial fill. That reconciliation is the hard part, not
  the API call.
- Governance limits. Max notional, max concurrent orders, per-instrument
  caps: all undefined today. An execution layer without these is not a
  smaller version of the goal, it is a different and riskier thing.
- Credential handling. API keys need trade-only scope (no withdraw) and a
  storage location outside anything the DSA/AI session pipeline reads or
  writes. Nothing in the current safety model (no-fabrication, four-step
  proof) assumed a credential could leak through a repository file.
- Failure modes. Network drop mid-order, partial fill, exchange rejection,
  rate limiting, clock drift each need a defined MTS behavior, not a
  try/catch that logs and continues.
- Testnet first. Deribit's test.deribit.com is a fully separate
  account/environment. Nothing here touches the live endpoint until
  testnet behavior is proven.

None of this changes the "go ahead" - it changes what "done" means for
phase 1.

## PHASED PLAN

Phase 1. Read-only connectivity, testnet, no credentials. Fetch
  BTC-PERPETUAL ticker via Deribit's public (unauthenticated) endpoint.
  Proves the client shape and desktop network path before any key exists.
  Exit: run twice, an hour apart, both times correct.
Phase 2. Authenticated read-only, testnet. Account summary, current
  position, open orders, using a trade-scoped (no withdraw) testnet key
  stored outside the repo. Exit: matches the Deribit testnet UI.
Phase 3. Order placement, testnet only. Place/query/cancel one limit
  order far from market and one minimal market order. Governance limits
  hardcoded conservative, not yet configurable. Exit: MTS's log and the
  Deribit testnet UI agree at every state transition.
Phase 4. Reconciliation. MTS belief vs Deribit actual, checked on an
  interval and after every action. Mismatch halts and alerts; it does not
  guess. Exit: a manually forced mismatch (close the position by hand on
  testnet) is detected and halts MTS.
Phase 5. Live, single position, operator-gated. Same code path against
  the live endpoint behind an explicit LIVE flag the operator sets,
  starting at minimum size. Feeds into T048's satellite/governance layer
  once proven - satellites are not built before single-position execution
  is.

## DEPENDENCIES (owed from operator)

- Deribit testnet API key pair: trade permission, no withdraw permission.
- A placeholder max-notional number, even a conservative guess, so phase 3
  has a hard ceiling from day one.
- Sign-off on where the key lives: proposed MyTradingSys/execution/.secrets/
  (gitignored, never committed, never read by any AI session's file tools
  by default).

## STATUS

OPEN. Phase 3 (order placement) code written but NOT run against testnet -
no key exists yet. Trade-plan schema/validator/compiler (phase 3's
governance-limits and sizing logic) are built and verified with synthetic
examples, not live orders. Next action: operator generates a testnet key
pair; then execution/deribit_orders.py's smoke test is the first real
network call this code has made.

## UPDATES

2026-09-26: Filed. MyTradingSys/execution/ created. .gitignore updated for
a credentials path that does not exist yet. Phase 1 public-endpoint script
written; see repo for result.

2026-09-27: Trade-plan schema (execution/trade_plan_schema.json) and
validator (execution/trade_plan_validator.py) built and run against 8
synthetic examples (5 valid, 3 invalid) - all behaved as expected. Plan
compiler (execution/plan_compiler.py) built and run against all 5 valid
examples; ladder math hand-verified (4-rung example: avg entry 49900,
stop 48902 at 2% below, worst-case loss -$1.40, matches manual calc).
Order-wrapper functions (execution/deribit_orders.py), executor
(execution/executor.py), journal + reconciler (execution/journal.py,
execution/reconciler.py) written but syntax-checked only - zero network
calls have succeeded because no testnet key exists. executor.py has a
hard refusal guard in main() specifically because it has never touched a
real order book. Full gap list and four questions for Opus 5.5 in
MyTradingSys/research/_archive/loose_2026-10/OPUS_REVIEW_REQUEST.md. Known real gaps (not
cosmetic): trailing_percent and breakeven_after_fills stop types have no
execution logic yet; reconciler's position-size check doesn't net out
stop/target fills against entry fills; cancel_all_by_label is a stub
that cancels ALL orders for the currency (Deribit doesn't filter by
label server-side). Step 6 (multi-account) deliberately not started -
its exit criterion needs steps 1-5 proven on testnet first; see
research/_archive/loose_2026-10/step6_multi_account_design_note.md.

2026-09-27 (parallel operator session, 06:32-06:43Z): Phase 2 crossed.
Testnet API key created at test.deribit.com (client_id iwOlM5A7, Account=read,
Trade=read_write, Wallet=none/Custody=none/Block Trade=none/Block RFQ=none,
no IP whitelist). Secret written directly to execution/.secrets/testnet.secret.json
by the operator on their machine - never pasted into any session, lengths only
verified (client_id=8, client_secret=43, env=test).
Smoke tests, both first-run PASS:
  python MyTradingSys/execution/deribit_client.py (phase 1, no key):
    OK: reached Deribit testnet public API. BTC-PERPETUAL mark_price=84496.54,
    best_bid=84494.0, best_ask=84494.5, state=open, timestamp_ms=1790491372671
    (~2026-09-27T06:43Z).
  python MyTradingSys/execution/deribit_orders.py (phase 2, authenticated):
    AUTH OK. account summary: equity=100.0 available_funds=100.0. open orders: 0.
Proves: network path to testnet works from the operator's machine; client_credentials
auth succeeds with the new key; authenticate()'s wallet-scope refusal guard did not
fire (key scopes correct as generated); account is fresh testnet (100.0 equity,
0 open orders).
NOT yet covered: no orders placed (_place_order/edit/cancel/cancel_all_by_label
unexercised); executor.py, plan_compiler.py, reconciler.py, journal.py not run
end-to-end; deribit_read.py not run.
Next: run deribit_read.py (closes phase 2 formally, read-only, zero risk), then
Phase 3's stated exit criterion - one limit order far from market and one minimal
market order via deribit_orders.py's buy()/sell()/cancel() directly, NOT through
executor.py. This does not require B077 or B078 fixed: Phase 3's exit criterion
has no stop order and no label-scoped cancel in it. B077/B078 remain hard blockers
for executor.py's automated pipeline specifically (which already has its own
hard refusal guard in main() for this reason), not for this primitive-level test.

2026-10-04 (MTS-2026-10-04-1130Z-APP-BLD-t050-phase3): Phase 3 code + offline tests DONE; live order placement NOT run. Added place/amend/get_order_history/reconcile_open/reconcile_filled to deribit_orders.py (buy/sell/edit/cancel already existed; auth + wallet-scope guard reused; place() testnet-only). 8 offline tests in execution/tests/test_deribit_orders_phase3.py, 8/8 error on pre-change code, 8/8 pass after; run_all_tests --quick PASS. Observed testnet (read-only, authenticated): get_open_orders -> 0 orders, get_order_history_by_instrument -> 0 orders (account has no history, so reconcile_filled has no live sample). Not placed: any order, since the live testnet loop (orphan_watchdog HALTs on stray open orders, builders may not open trades) shares this account; supervisor/operator to run the far-limit place/amend/cancel sequence.

## 2026-10-04T11:35Z - phase 3 exit criterion

f088b52 landed place/amend/cancel primitives and 8 offline tests. Phase 3's
exit criterion is a live testnet place/amend/cancel with MTS log and Deribit
UI agreeing at every state transition. Not met: the live testnet loop shares
this account, orphan_watchdog writes a HALT on a stray open order, and builders
may not open trades. The sequence is owed to an operator-run CLI session.
Row stays OPEN.

## 2026-10-04T11:41Z - phase 3 LIVE PASS (exit criterion met)

Operator ran MyTradingSys/execution/testnet/t050_phase3.py from a CLI session.
Both sub-tests passed. Account: test.deribit.com, default account, flat before
and after.

T1a buy limit far below mark: mark=85283.08, min_price=82724.5, tick=0.5,
limit price 82724.5 (3.00% under mark). Order 121807832893 placed open,
listed by get_open_orders, cancelled (order_state=cancelled). Zero open orders
after. Position still 0.

T1b sell market 10: order 121807837545 filled at avg 85280.5. Position size
-10. close_position order 121807838445 filled at avg 85276.5. Position size 0.
Zero open orders at end.

Session transcript: MyTradingSys/research/testnet_status/T050_PHASE3_2026-10-04.md
Exit code 0.
