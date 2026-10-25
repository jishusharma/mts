# MTS Execution System Architecture (Steps 1–8 Roadmap)

**Version:** 0.1  
**Date:** 2026-09-27  
**Status:** Design phase; Haiku research done, Opus design in progress, ready for Sonnet builders

---

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                      MTS EXECUTION PIPELINE                      │
└─────────────────────────────────────────────────────────────────┘

┌──────────────────┐
│  Trade Plan      │  ← Operator provides or system auto-generates
│  (Step 2 spec)   │    (account, instrument, side, entry, stop, caps)
└────────┬─────────┘
         │
         ▼
┌──────────────────────────┐
│  Trade-Plan Validator    │  ← Rejects cap violations, malformed plans
│  (Step 2 validator)      │    (Opus designs; Haiku tests)
└────────┬─────────────────┘
         │ (valid plan)
         ▼
┌──────────────────────────┐
│  Plan Compiler           │  ← Converts plan to order list
│  (Step 3: Sonnet)        │    (entry ladder → [order1, order2, ...])
│  Outputs: order table    │    (targets → [target1, target2, ...])
│           stop price     │    (validates tick & size rounding)
└────────┬─────────────────┘
         │
         ▼
┌──────────────────────────┐
│  Executor                │  ← Sends compiled orders to Deribit
│  (Step 4: Sonnet+Opus)   │    (WebSocket session client from Step 1)
│  · Places orders         │    (tracks fills incrementally)
│  · Tracks fills          │    (resizes stops after each fill)
│  · Resizes stops         │    (halts on error/mismatch)
│  · Logs all intent       │
└────────┬─────────────────┘
         │
         ▼
┌──────────────────────────┐
│  Reconciliation          │  ← MTS belief vs Deribit actual
│  (Step 5: Sonnet)        │    (queries positions after each action)
│  · Compares state        │    (halts on mismatch; never guesses)
│  · Detects mismatches    │    (logs full state for audit)
│  · Halts on error        │
└────────┬─────────────────┘
         │
         ▼
┌──────────────────────────┐
│  Journal & Accounting    │  ← Append-only record of actions
│  (Part of Step 5)        │    (intent → order → fills → final state)
│  · Logs everything       │    (operator can reconstruct any moment)
│  · Immutable record      │
└────────┬─────────────────┘
         │
         ▼
┌──────────────────────────┐
│  Multi-Account Layer     │  ← Scale to 2+ subaccounts
│  (Step 6: Sonnet)        │    (account registry + per-account caps)
│  · Account routing       │    (isolated reconciliation per account)
│  · Per-account caps      │    (test cancel-on-disconnect behavior)
│  · Isolated reconciliation│
└────────┬─────────────────┘
         │
         ▼
┌──────────────────────────┐
│  Satellites/Clusters     │  ← Linked positions (parent→child)
│  (Step 7: Opus+Sonnet)   │    (T048 governance layer)
│  · Parent/child logic    │    (child spawned if parent fills)
│  · Governance gates      │    (each child: own stop, size, account)
│  · Independent stops     │    (manual trigger for now)
└────────┬─────────────────┘
         │
         ▼
┌──────────────────────────┐
│  Mainnet Gate            │  ← Final checklist before go-live
│  (Step 8: Opus review)   │    (B071 fixed, governance set, testnet ✓)
│  · Safety review         │    (operator sets LIVE flag; min position)
│  · Governance validation │
│  · Go-live approval      │
└──────────────────────────┘
```

---

## Parallel Track: Step 1 (Session Client)

Builds independently and feeds into Steps 3–6:

```
┌──────────────────────────┐
│  Session Client (Step 1) │  ← Persistent WebSocket to Deribit
│  (Sonnet; spawn as agent)│    (auth, heartbeat, reconnect logic)
│  · WebSocket connection  │
│  · Auth + token refresh  │
│  · Heartbeat loop        │
│  · Order wraps:          │
│    - buy / sell          │
│    - edit (price/amount) │
│    - cancel (by ID)      │
│    - query (open orders) │
│  · Forced disconnect     │
│    resilience test       │
└────────┬─────────────────┘
         │
         ├──────────► Used by Step 4 (Executor)
         └──────────► Used by Step 5 (Reconciliation)
```

---

## Data Model (Trade Plan)

### Input: Trade Plan (JSON)
```json
{
  "account": "subaccount_1",
  "instrument": "BTC-PERPETUAL",
  "side": "LONG",
  "validity": {
    "start": "2026-09-27T10:00:00Z",
    "end": "2026-09-27T14:00:00Z"
  },
  "entry": {
    "type": "ladder",
    "range": {
      "low": 49800,
      "high": 50200
    },
    "rungs": 4,
    "size_multipliers": [1, 1, 2, 3]
  },
  "base_unit": 10,
  "stop": {
    "type": "fixed_percent",
    "percent_below_entry": 2.0
  },
  "targets": [
    {"amount_percent": 50, "pnl_target_percent": 2.0},
    {"amount_percent": 50, "pnl_target_percent": 5.0}
  ],
  "caps": {
    "max_notional_usd": 10000,
    "max_loss_usd": -500,
    "max_concurrent_orders": 10
  }
}
```

### Step 3 Output: Compiled Order List
```json
{
  "entry_orders": [
    {"rung": 1, "side": "BUY", "price": 50200, "amount": 10, "label": "entry_rung_1"},
    {"rung": 2, "side": "BUY", "price": 50050, "amount": 10, "label": "entry_rung_2"},
    {"rung": 3, "side": "BUY", "price": 49900, "amount": 20, "label": "entry_rung_3"},
    {"rung": 4, "side": "BUY", "price": 49750, "amount": 30, "label": "entry_rung_4"}
  ],
  "stop_order": {
    "side": "SELL",
    "price": 49500,
    "reduce_only": true,
    "amount": 70,
    "label": "stop_order"
  },
  "target_prices": [50500, 51000],
  "entry_avg_if_ladder_fills": 49928.57,
  "max_position_notional": 10500,
  "worst_case_loss": -485
}
```

### Step 4 Output: Execution Journal
```json
{
  "trade_id": "plan_20260927_001",
  "created_at": "2026-09-27T10:05:30Z",
  "orders": [
    {
      "order_id": 12345,
      "label": "entry_rung_1",
      "side": "BUY",
      "price": 50200,
      "amount": 10,
      "filled_amount": 10,
      "filled_price": 50199,
      "order_state": "filled",
      "created_at": "2026-09-27T10:05:31Z",
      "filled_at": "2026-09-27T10:05:45Z"
    },
    {
      "order_id": 12346,
      "label": "entry_rung_2",
      ...
    },
    ...
  ],
  "stop_order": {
    "order_id": 12349,
    "label": "stop_order",
    "current_price": 49500,
    "amount": 70,
    "order_state": "open"
  },
  "position_state": {
    "current_size": 40,
    "avg_entry": 50125,
    "unrealized_pnl": 315,
    "margin_used": 7500
  },
  "last_reconciliation": "2026-09-27T10:15:20Z",
  "mismatch_detected": false
}
```

---

## Step-by-Step Implementation (Who Does What)

| Step | Component | Lead | Focus | Testnet Exit Criteria |
|------|-----------|------|-------|----------------------|
| **1** | Session Client | Sonnet (subagent) | WebSocket auth, order wraps, reconnect | Place/edit/cancel/query far-from-market order; survive forced disconnect |
| **2** | Trade-Plan Spec | Opus | Schema + validator design | 5 valid plans pass; 3 invalid plans rejected |
| **3** | Plan Compiler | Sonnet | Entry ladder, stop, target calc | Compiled order list matches hand-calc on example |
| **4** | Executor | Sonnet (build) Opus (review) | Send orders, track fills, resize stops | Full ladder round trip + partial-fill case; stop always covers |
| **5** | Reconciliation | Sonnet | Compare MTS belief to Deribit actual | Close position by hand on UI; system detects + halts |
| **6** | Multi-Account | Sonnet | Account registry, per-account caps | 2 plans in 2 subaccounts simultaneously |
| **7** | Satellites | Opus (design) Sonnet (build) | Parent→child plans, governance | Parent spawns child; child has independent stop |
| **8** | Mainnet Gate | Opus (review only) | B071 fixed, governance set, testnet ✓ | Initial mainnet position with min size |

---

## Critical Dependencies & Blockers

| Blocker | Status | Unblocks | Action |
|---------|--------|----------|--------|
| **Operator testnet setup** | Pending (user action) | Steps 1–5 (can't test API) | Jishu creates account, API key, runs deribit_client.py + deribit_read.py |
| **B071 (fail-open bug)** | Open (high) | Step 8 mainnet | Must fix before any mainnet order sent |
| **Trade-plan schema** | In progress (Opus) | Step 3 compiler | Opus designs; Haiku validates; Sonnet builds compiler |
| **Step 1 session client** | Ready for Sonnet | Steps 4–5 (need WebSocket) | Spawn Sonnet subagent; builds persistent session |

---

## Testing Strategy

### Testnet Validation (All Steps 1–6)
1. **Step 1:** Place/query/cancel/edit orders; force disconnect → reconnect
2. **Step 2:** Validator tests (5 valid + 3 invalid plans)
3. **Step 3:** Compiler output matches hand-calculated ladder
4. **Step 4:** Execute full ladder (4 rungs); stop order tracks highest fill
5. **Step 5:** Manually close position on Deribit UI → system detects mismatch + halts
6. **Step 6:** 2 simultaneous plans in 2 subaccounts; isolated caps

### Mainnet Readiness (Step 8)
- B071 fixed ✓
- All steps 1–6 testnet ✓
- Governance caps set (max daily loss, max notional, etc.) ✓
- Operator approval on LIVE flag ✓
- Minimum position size (e.g., 1 BTC or $500 notional) ✓

---

## Audit & Compliance

**Immutable Journal (Step 5 output):**
- Every intent logged before action
- Every order state transition timestamped
- Every fill incremented and logged
- Reconciliation results saved
- Operator can reconstruct any moment in time

**No AI Auto-Recovery:**
- On mismatch: halt, log, alert (never guess)
- On error: log, backoff, retry finite times, then halt
- On insufficient funds: halt immediately; don't retry

**Governance Gates (Step 7):**
- Max trade notional
- Max daily loss
- Max concurrent orders
- Per-account caps
- Satellites gated by validation

---

## Timeline

- **Session 1 (today):** Opus designs schema; Haiku docs + research done
- **Session 2:** Operator sets testnet; Sonnet builds Step 1 + Step 3; Haiku validates Step 2
- **Session 3:** Sonnet builds Step 4 (Opus reviews); Step 5 + 6 ready
- **Session 4:** Testnet validation (all steps 1–6 + 7 preliminary)
- **Session 5:** Step 8 mainnet review; operator decides go-live date

---

## File Structure (Execution Layer)

```
MyTradingSys/
├── execution/
│   ├── __init__.py
│   ├── deribit_client.py           (Step 1: session client wrapper)
│   ├── deribit_read.py              (Phase 1: unauthenticated test)
│   ├── trade_plan_schema.json       (Step 2: schema definition)
│   ├── trade_plan_validator.py      (Step 2: validation logic)
│   ├── plan_compiler.py             (Step 3: plan → orders)
│   ├── executor.py                  (Step 4: order placement + fill tracking)
│   ├── reconciler.py                (Step 5: MTS vs Deribit comparison)
│   ├── journal.py                   (Step 5: append-only logging)
│   ├── multi_account.py             (Step 6: account registry + routing)
│   ├── satellites.py                (Step 7: parent/child logic)
│   ├── .secrets/
│   │   └── testnet.secret.json      (API credentials; gitignored)
│   └── examples/
│       ├── valid_plan_1.json        (Step 2 example)
│       ├── valid_plan_2.json
│       ...
│       ├── invalid_plan_1.json
│       └── invalid_plan_2.json
└── research/
    ├── deribit_api_research.md      (Haiku's compilation)
    ├── opus_handoff_context.md      (This handoff)
    └── execution_system_architecture.md (This doc)
```

---

**Ready to proceed. Opus takes it from here on Step 2 design.**
