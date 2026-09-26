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

OPEN. Phase 1 scaffolding started 2026-09-26 (see UPDATES). Next action:
operator generates a testnet key pair and a placeholder max-notional
number; then phase 2.

## UPDATES

2026-09-26: Filed. MyTradingSys/execution/ created. .gitignore updated for
a credentials path that does not exist yet. Phase 1 public-endpoint script
written; see repo for result.
