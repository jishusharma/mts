# Deribit API Research & Execution System Requirements

**Compiled by:** Haiku 4.5  
**Date:** 2026-09-27  
**For:** Step 1–4 (Session Client, Trade-Plan Spec, Plan Compiler, Executor)

---

## 1. Deribit API Fundamentals

### Endpoints
- **Testnet Base:** `https://test.deribit.com/api/v2` (separate account/environment)
- **Production Base:** `https://www.deribit.com/api/v2` (live funds)
- **WebSocket Testnet:** `wss://test.deribit.com/ws/api/v2`
- **WebSocket Production:** `wss://www.deribit.com/ws/api/v2`

### Authentication (All Private Endpoints)
1. **Initial Token:** POST `/public/auth`
   - Method: OAuth2 client_credentials
   - Params: `client_id`, `client_secret`, `grant_type=client_credentials`
   - Returns: `access_token`, `expires_in` (seconds)
2. **Token Lifecycle:**
   - Error 13009 = token expired; refresh immediately
   - Refresh before expiry to avoid mid-trade failures
   - Each key pair must be generated per API client (trade-only scope, no withdraw)

### Order Placement (WebSocket Preferred for Latency)
```
Method: private/buy or private/sell
Required Params:
  - instrument_name: "BTC-PERPETUAL" (for this phase)
  - amount: notional size in contracts
  - type: "market" | "limit"
  - price: (limit orders only)
  
Optional:
  - label: user-assigned label (e.g., "ladder_rung_1", "stop_order")
  - reduce_only: boolean (reduces position, not adding)
  - post_only: boolean (maker-only, rejects if takes liquidity)
```

**Response Structure:**
```json
{
  "order_id": 12345,
  "order_state": "open" | "filled" | "rejected" | "cancelled" | "untriggered",
  "filled_amount": 0,
  "amount": 10,
  "price": 50000,
  "label": "my_label",
  "creation_timestamp": <unix_ms>,
  "last_update_timestamp": <unix_ms>
}
```

---

## 2. Order State Machine

| State | Meaning | Final? | Notes |
|-------|---------|--------|-------|
| **open** | Resting on book | No | May have `filled_amount` > 0 (partial) |
| **filled** | 100% filled | Yes | `filled_amount == amount` |
| **partially_filled** | Implied state | No | `0 < filled_amount < amount`; query for latest |
| **rejected** | Declined by exchange | Yes | Insufficient funds, invalid price/size, etc. |
| **cancelled** | User/system cancelled | Yes | May have `filled_amount` > 0 |
| **untriggered** | Conditional order waiting | No | Linked orders (OTO/OCO) not yet live |

**Key:** Query order by `order_id` to get current state and `filled_amount` at any time.

---

## 3. Critical Error Codes & Handling

| Code | Category | Handling |
|------|----------|----------|
| **10002** | qty_too_low | STOP: halts trading immediately; check order size |
| **10009** | not_enough_funds | STOP: halts trading immediately; check balance |
| **10028** | Rate limited | RETRY: exponential backoff (1s, 2s, 4s, …) |
| **10047** | Portfolio queue full | RETRY: 5-second timeout; retry once |
| **11005** | amount_too_large | STOP: halts trading immediately; check position/order cap |
| **13009** | unauthorized | REFRESH: get new token via /public/auth |
| **11006** | post_only_reject | REJECT: adjust price/type; do NOT retry |
| **11007** | reduce_only_reject | REJECT: do NOT retry |
| **11008** | Order already filled | INFO: log; order is done |

Note: BTC-PERPETUAL order amount is USD notional, in multiples of 10.

---

## 4. Partial Fill Handling

**Scenario:** Ladder order with 4 rungs; each rung 10 BTC at different prices.
- Rung 1 (price $50K, amount 10) → placed, status = "open", filled_amount = 0
- Market moves; rung 1 partially fills: filled_amount = 3
- Rung 2 (price $49.8K, amount 10) → placed
- After 30 sec: rung 1 fully filled (10/10); rung 2 partially (7/10)

**Executor Must:**
1. Track `filled_amount` per order
2. Emit fills incrementally (each query detects cumulative change)
3. Adjust server-side stop (`/private/edit`) after each fill (step 4)
4. Log every state transition with timestamp

---

## 5. Reconciliation (MTS Belief vs Deribit Actual)

**Query Points:**
- `/private/get_account_summary` → balance, available_funds, open_orders count
- `/private/get_position?instrument_name=BTC-PERPETUAL` → current_size, average_price, unrealized_pnl
- `/private/get_open_orders?instrument_name=BTC-PERPETUAL` → list of open orders with state + filled_amount

**Mismatch Detection:**
1. After every action (place, cancel, edit), query positions
2. Compare MTS belief (accumulated fills) to Deribit actual
3. On mismatch: HALT, log full state, alert operator
4. **NEVER guess or assume; always query ground truth**

---

## 6. Failure Mode Requirements

### Network Drop Mid-Order
- Order may or may not reach Deribit
- Retry: GET `/private/get_open_orders` → if not there, place again
- If already there: skip retry

### Partial Fill + Executor Crash
- On restart: query all orders, resume tracking fills
- Resume ladder if primary still has resting rungs

### Exchange Rejection (insufficient funds, etc.)
- Log order_id, rejected reason, params
- Alert operator; do NOT auto-retry
- Executor must halt

### Rate Limit / Network Timeout
- Exponential backoff up to 30 seconds
- If persistent: HALT after 3 retries

---

## 7. WebSocket Session Lifecycle (For Step 1 Builder)

1. **Connect:** Open persistent WebSocket to testnet endpoint
2. **Authenticate:** Send `{"jsonrpc":"2.0","method":"public/auth","params":{...},"id":1}`
3. **Heartbeat:** Exchange expects heartbeat every 30 seconds (method: `public/heartbeat`)
4. **Listen:** Subscribe to fills via `private/subscribe` (order events)
5. **Reconnect:** On disconnect, rebuild connection and re-subscribe (orders persist server-side)

NOTE: method names in this section are unverified against current Deribit docs; confirm before relying on them.

**Expected Heartbeat Response:**
```json
{"jsonrpc":"2.0","result":true,"id":123}
```

---

## 8. Constraints for MTS Integration

- **One position at a time** (today; satellites will change this in step 7)
- **BTC-PERPETUAL only** (phase 1)
- **Testnet only until step 8** (mainnet gate)
- **Labels on all orders** (for filtering, cancel-on-disconnect)
- **No linked orders yet** (OTO/OCO deferred; step 7 may explore)
- **Reduce-only stops** (after each fill; step 4)

---

## 9. Research Sources

- [Deribit API Quickstart](https://docs.deribit.com/articles/deribit-quickstart)
- [Deribit Error Codes Reference](https://docs.deribit.com/articles/errors)
- [Deribit Order Management Best Practices](https://docs.deribit.com/articles/order-management-best-practices)
- [AlgoTrading101 Deribit API Guide](https://algotrading101.com/learn/deribit-api-guide/)
- [Go-Deribit v3 Package (Reference Implementation)](https://pkg.go.dev/github.com/scancel/go-deribit/v3)

---

## 10. Gaps & Clarifications for Opus 5.5

Before Opus designs the trade-plan spec and executor, these need decided:

1. **Max Notional Per Trade:** What's the conservative starting number? (e.g., $10K, $100K?)
2. **Max Loss Per Trade:** Hard cap on realized loss before auto-halt? (e.g., -$500?)
3. **Concurrent Orders:** How many open orders at once? (e.g., max 10 for ladder + stop?)
4. **Ladder Size:** Max rungs per ladder? Multiplier list format?
5. **Stop Logic:** Fixed %-below-entry? Trailing? Breakeven after N fills?
6. **Fill Reporting:** Real-time PnL updates to operator? How often?
7. **Operator Interaction:** Manual trade approval before executor sends, or autonomous within caps?

These drive the trade-plan schema design and cap validation.

---

**Ready for Opus 5.5 to:**
1. Design trade-plan JSON schema (with cap fields)
2. Build validator logic (reject cap-breaking plans)
3. Create 5 valid + 3 invalid examples
4. Define the interaction model (approval vs. autonomous)
