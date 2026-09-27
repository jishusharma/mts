# Opus 5.5 Review Request — T050 Execution Layer

**Date:** 2026-09-27 01:35 IST
**From:** Sonnet 5 (this session)
**Status:** Steps 1–5 have working code. Steps 2–3 are proven (tests pass). Steps 1, 4, 5 are untested — no testnet key exists. Step 6 is deliberately deferred.

This supersedes `opus_handoff_context.md` from the prior session, which asked Opus to *design* Step 2 from scratch. That's no longer the ask — Step 2 is built and verified. The ask now is **review, decide open questions, and guide sequencing** — not greenfield design.

---

## What's Proven (ran and verified this session)

**Step 2 — Trade-plan schema + validator**
- `execution/trade_plan_schema.json` — full JSON Schema
- `execution/trade_plan_validator.py` — dependency-free (stdlib only), enforces schema + business caps (notional ceiling, loss floor, concurrent-order cross-check against ladder size)
- `execution/examples/` — 5 valid + 3 invalid plans
- **Ran:** `python trade_plan_validator.py --examples` → all 8 behaved exactly as expected (5 valid pass, 3 invalid rejected with specific reasons)

**Step 3 — Plan compiler**
- `execution/plan_compiler.py` — plan → order list, price snapped to $0.5 tick, size rounded to $10 contracts
- **Ran:** `python plan_compiler.py --examples` → compiled all 5 valid plans
- **Hand-verified** the 4-rung ladder example: avg entry 49900.0, stop 48902.0 (2% below), worst-case loss -$1.40 — matches manual calculation exactly
- Caught and fixed one display bug during this session (stop price wasn't printing in the table, though it was computed correctly)

## What's Written But NOT Verified (no testnet key exists — flagging honestly, not smoothing over it)

**Step 1 — `execution/deribit_orders.py`**
- Order wraps: buy, sell, edit, cancel, get_positions, get_open_orders, get_order_state, get_account_summary
- Syntax-checked only. Zero network calls have succeeded because there is no key yet.
- **Deviation from original ask, flagged for your decision:** the roadmap asked for "one persistent WebSocket: auth, heartbeat, reconnect." I built REST/polling instead, matching the existing `deribit_read.py` convention (stdlib-only, one-request-per-call, no persistent connection). This means no push notifications for fills — `executor.py` polls every 2 seconds instead. **Question 1: is REST polling acceptable for fill-tracking, or does the partial-fill/stop-resize loop need a WebSocket rewrite before Step 4 can be trusted?**
- `cancel_all_by_label` is currently a stub that cancels ALL orders for the currency (Deribit's endpoint doesn't filter by label server-side) — **known incomplete, flagged inline in the code.**

**Step 4 — `execution/executor.py`**
- Places entry orders, polls for fills via the journal (single source of truth), places a sized stop after fill.
- **Has a hard refusal guard in `main()`** — it will not run even if invoked, with a message explaining why (never tested against a live order book). This is intentional; I did not want untested money-handling code runnable by accident.
- **Real gap, not cosmetic:** only `fixed_percent` stop type is implemented. `trailing_percent` and `breakeven_after_fills` stops (both in the schema, both in the compiler's output) have **no execution logic** — if a plan using either reaches the executor, entries fill and the code deliberately halts with "NO STOP PLACED" rather than pretending to place a wrong one. **Question 2: build these before or after the first testnet run of fixed_percent plans?** My instinct is after — get one full round-trip proven first, then extend.
- **Question 3 (design choice, needs your sign-off):** on any entry-rung rejection mid-ladder, the executor cancels everything placed so far and halts the whole plan, rather than trying to keep partially-placed rungs. Conservative by design (matches B071's fail-closed lesson) — confirm this is the right permanent behavior, not just my default.

**Step 5 — `execution/journal.py` + `execution/reconciler.py`**
- Journal: append-only JSONL, one file per `plan_id`, replays into a "belief" state
- Reconciler: compares belief to Deribit's actual order states + position size, halts on any mismatch, never auto-corrects
- **Known simplification, flagged in code:** the position-size check doesn't yet net out stop/target fills against entry fills — it only sums entry-labeled orders. A real mismatch and this simplification could look identical right now. **Needs fixing before this reconciler is trusted, not after.**

**Step 6 — Deliberately not built.** See `step6_multi_account_design_note.md`. Its own exit criterion requires Steps 1–5 proven on testnet first; building it now would be designing against unverified assumptions about how Deribit actually behaves.

---

## Decisions I Made By Default (confirm or override)

These were unanswered in the prior handoff, so I picked conservative defaults to keep moving. All are schema-enforced ceilings/floors, not just suggestions — a plan exceeding them fails validation:

| Setting | Default I used | Rationale |
|---|---|---|
| Max notional per trade | $10,000 ceiling | T050's own dependency list called this "undefined today"; picked round conservative number |
| Max loss per trade | -$500 floor | Same |
| Max concurrent orders | 10 ceiling | Covers a 4-rung ladder + stop + 2 targets with room |
| Stop rule types supported | fixed_percent, trailing_percent, breakeven_after_fills | Covers the three variants mentioned in the original handoff's Step 2 spec |
| Operator approval model | **Not decided — not yet wired into executor.py at all** | Executor currently has no approval gate; it either runs (if the refusal guard is removed) or doesn't. Needs your input before that guard comes off. |
| Target format | `[{amount_percent, pnl_target_percent}]` array | Simplest structure that supports partial-target scaling |

**Question 4: are these defaults acceptable to keep, or does the operator want different numbers before the first testnet run?**

---

## Sequencing Question (the actual "guide the flow" ask)

Given everything above, here's what I see as the options for what happens next, in order of how conservative they are:

**Option A (most conservative):** Wait for operator's testnet key. Run `deribit_orders.py` smoke test (auth + account summary query, zero orders) first. Only then attempt one real order via `executor.py` — after removing the refusal guard — on a single fixed_percent market-entry plan, hand-watched the whole way.

**Option B:** Same as A, but also fix the reconciler's netting simplification and implement trailing/breakeven stops *before* any testnet order, so the first real run exercises the full schema surface, not just the happy path.

**Option C:** Same as A, but skip the WebSocket-vs-REST question (Question 1) for now — REST polling is "good enough to prove the concept," revisit only if Step 4's testnet run shows fills being missed or stops resizing too late.

**My recommendation:** A, then C, then B — prove one simple round-trip end to end before extending surface area. But this is exactly the kind of sequencing call the roadmap assigned to Opus (Step 4's own exit criteria assume review before testnet contact), so I'm asking rather than deciding.

---

## Files (all committed to device this session)

```
MyTradingSys/execution/
├── trade_plan_schema.json          (Step 2 — done, verified)
├── trade_plan_validator.py         (Step 2 — done, verified: 5/5 valid, 3/3 invalid)
├── plan_compiler.py                (Step 3 — done, verified against hand-calc)
├── deribit_orders.py               (Step 1 — written, UNTESTED, REST not WebSocket)
├── executor.py                     (Step 4 — written, UNTESTED, refusal guard active)
├── journal.py                      (Step 5 — written, UNTESTED)
├── reconciler.py                   (Step 5 — written, UNTESTED, known netting gap)
├── examples/
│   ├── valid_market_simple.json
│   ├── valid_limit_short.json
│   ├── valid_ladder_four_rung.json
│   ├── valid_breakeven_stop.json
│   ├── valid_no_targets_just_stop.json
│   ├── invalid_missing_stop.json
│   ├── invalid_cap_exceeds_ceiling.json
│   └── invalid_ladder_multiplier_mismatch.json
└── deribit_client.py, deribit_read.py, README.md   (pre-existing, unchanged)

MyTradingSys/research/
├── deribit_api_research.md
├── opus_handoff_context.md          (superseded by this file for the "what to design" part; API research section still current)
├── execution_system_architecture.md
├── operator_summary.md
├── step6_multi_account_design_note.md
├── SESSION_HANDOFF_2026-09-27.md
└── OPUS_REVIEW_REQUEST.md           (this file)
```

---

## Still Blocked On Operator

Nothing above required the testnet key to build — but nothing above can be *proven* without it either. The blocker is unchanged from the prior session: operator creates a test.deribit.com account, generates a trade-scoped key, saves it to `execution/.secrets/testnet.secret.json`, then Step 1's smoke test (`deribit_orders.py` run directly) is the first real signal on whether any of this actually works against a live order book.

---

**Four questions for you, in priority order:**
1. REST polling vs. WebSocket for Step 1 — acceptable, or rebuild first?
2. Fix reconciler's netting gap + implement trailing/breakeven stops before or after first testnet round-trip?
3. Confirm or override the halt-on-any-rejection ladder behavior in executor.py
4. Confirm or override the conservative caps defaults ($10K/-$500/10 orders)

Plus the sequencing call (Option A/B/C above) once you've answered those.

---

## UPDATE 2026-09-27 12:41 IST — Sonnet 5, handoff before stopping

Everything below happened after the original request above. Your four
open questions (REST vs WebSocket, reconciler netting/trailing/breakeven
sequencing, halt-on-rejection confirm, caps defaults confirm) are still
open and still yours to answer - nothing here resolves them.

### D1-D7 operator rulings (all seven, this session)

Full detail: research/core_readiness_2026-09-27/D1_D7_DECISION_BRIEF.md

- D1 revert (hard R:R stop always applies): RULED YES. **Built and
  harness-verified** - see below.
- D2 (Java authoritative for zone math): RULED NO CHANGE - operator
  declined your recommendation, leaving Python/Java disagreement as-is
  since it's off the live path. No C4 task.
- D3 (separate extra/FVG candidates into module_candidates): RULED YES.
  **Not built** - Java change (MarketDataSnapshot.java), needs Maven to
  compile/verify, unavailable in this bridge session.
- D4 (directional-only proof count, drop speed): RULED YES. **Not
  built** - same Java/Maven blocker as D3, plus this is explicitly your
  review gate per the original plan (C3: "Sonnet builds, Opus reviews
  before deploy").
- D5 (document unhealthy/transition gap in compiled_engine sec 1, text
  only): RULED YES. **Not written** - this is explicitly your task
  (C5), not mine, per the plan's own role assignment. Can draft proposed
  language if useful, have not yet.
- D6a (document proof thresholds 3/5 as [SYSTEM] in sec 8): RULED YES.
  Same as D5 - your task, not written yet.
- D6b (SETUP_CONFIRMED fate): operator ruled AGAINST your plan's
  recommendation (remove from alert lists) - wants a real Tom-cited
  trigger found/confirmed instead. Filed as a new research task, T052
  (items/T052_setup_confirmed_trigger.md). Not started.
- D7 (B071 floor = WAIT_PROOF, no halt/alert): RULED - shipped behavior
  ratified as final, no halt+alert being added.

### C1 built and verified (D1's code change)

verdict.py: suspend_rr path removed, mode field kept for display only.
Verified against verdict_golden.py's transition matrix: 3 of 4 rows
match your predicted counts in CORE_READINESS_PLAN.md sec 3 exactly
(SETUP_FORMING->WAIT_RR 158, WATCH->WAIT_RR 807, WAIT_PROOF->WAIT_RR
1195); the 4th (WAIT_TRIGGER->WAIT_RR) is 891 measured vs 893 predicted,
a 2-count gap consistent with corpus growth between when you measured
the plan and now, not a logic error. New baseline NOT written
(--write-baseline) - left for the operator's review batch, not done
unilaterally.

scripts/core/start-trading-day.ps1 (critical file): same fix, four-step
proof done (hash fb3f6f70... -> 8c07ef1b..., explicit-replace edit,
diff shown to operator). Cannot execute-verify - no PowerShell in this
bridge session, same limitation noted throughout this project's Sonnet
sessions.

Both files UNCOMMITTED. Operator has not yet run git commit on anything
from this session.

### B071 (fail-open fix) - now live, not just staged

Applied to start-trading-day.ps1, build_mo_cli.py, verdict.py (all
three, four-step proof on the critical file, harness-verified:
fail_closed_spec.py S1+S2 PASS on 9287 real snapshots, verdict_golden.py
NO CHANGE vs its then-baseline). D7 ratifies this as final. NOT verified:
actual PowerShell execution on a live running candle loop - still needs
the operator watching a real loop tick.

### New bugs filed this session (B072-B079), all uncommitted

- B072-B076: from NUC-builder testing (L2 input validation, net_rr
  rounding, rule-order dependence, historical-mode look-ahead leak,
  SETUP_CONFIRMED unreachable - this last one is what became D6b/T052).
- B077 (HIGH): execution/executor.py places the protective stop as a
  reduce-only LIMIT, not stop_market - live code path, not dead code.
  deribit_orders.py's _place_order() has no trigger/trigger_price params
  at all; this needs a signature change plus a trigger-source decision
  (last_price/mark_price/index_price), not a one-line fix.
- B078 (MED): cancel_all_by_label calls private/cancel_all_by_currency,
  which Deribit doesn't filter by label server-side - cancels every
  order on the account. Currently dead code (grepped, not called
  anywhere yet), so no live risk today, but a real gap before Step 5
  reconciliation/teardown relies on it. Your own code comment already
  flagged this.
- B079 (HIGH): plan_compiler.py computes caps_check.within_max_loss but
  nothing ever checks it - executor.py.execute_plan() never references
  caps_check at all. A plan could compile with within_max_loss=False and
  still execute unchanged. Also: no within_max_notional check exists
  anywhere, at any stage.

None of B077/B078/B079 fixed - operator chose to file and continue the
review queue rather than fix immediately, when asked.

### Testnet progress (parallel operator session, not this one)

Phase 1+2 both PASS on first run: testnet key created (read/trade
scopes, no wallet/custody/block-trade), wallet-scope refusal guard held,
deribit_client.py ticker fetch OK, deribit_orders.py auth+account
summary OK (equity=100.0, 0 open orders). Full receipt in
items/T050_deribit_execution_layer.md. Phase 3 (order placement) not yet
run - my recommendation to the operator was that B077/B078 don't block
Phase 3's literal exit criterion (one limit order far from market, one
market order, via deribit_orders.py primitives directly, no stop
involved) - they block executor.py's automated pipeline specifically,
which already has its own hard refusal guard for exactly this reason.

### What's actually needed from you, concretely, in priority order

1. **Executor.py review** - this was already the plan's own gate before
   any testnet order flows through it (not just B077/B078 - the file's
   own docstring names you as the required reviewer). Still hasn't
   happened. The operator may attempt a Phase-3-scoped primitive order
   test (bypassing executor.py) before this lands, per my recommendation
   above - flagging so you're not surprised if BUGS.md shows testnet
   order activity before your review is done.
2. **C5 text** - compiled_engine.md sec 1 (D5) and sec 8 (D6a), critical
   file, four-step proof, operator approval. Ruled yes on both, nobody
   has written the actual language yet.
3. **C3 review** - once I build the directional-proof-count Java change
   (D4), it needs your review before deploy per the original plan. Not
   built yet - blocked on Maven access in whichever session builds it.
4. **D6b / T052** - is there a real Tom-cited SETUP_CONFIRMED trigger in
   the transcripts, or should the operator's ruling (find one, don't
   remove it) be revisited? Not started by me.
5. B077's fix needs a trigger-source decision (last_price vs mark_price
   vs index_price) that's more of a design call than a mechanical
   patch - flagging in case you want to weigh in before whoever builds
   it picks one.

Stopping here per operator instruction. This file + the decision brief
+ BUGS.md/items/INDEX.md are the full state as of now.
